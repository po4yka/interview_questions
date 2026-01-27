---
id: q-design-job-scheduler
title: Design Distributed Job Scheduler
aliases:
- Job Scheduler
- Task Scheduler
- Workflow Engine
topic: system-design
subtopics:
- distributed-systems
- scheduling
- reliability
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-message-queues-event-driven--system-design--medium
- q-saga-pattern--system-design--hard
- q-consistency-models--system-design--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- system-design
- difficulty/hard
- distributed-systems
- scheduling
anki_cards:
- slug: sysdes-078-0-en
  anki_id: null
  synced_at: null
- slug: sysdes-078-0-ru
  anki_id: null
  synced_at: null
- slug: q-design-job-scheduler-0-en
  anki_id: null
  synced_at: null
- slug: q-design-job-scheduler-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design a distributed job scheduler like Airflow or Temporal?

# Vopros (RU)
> Как бы вы спроектировали распределённый планировщик задач наподобие Airflow или Temporal?

---

## Answer (EN)

### Requirements

**Functional:**
- Schedule jobs (one-time, recurring/cron)
- Execute jobs on distributed workers
- Define job dependencies (DAGs)
- Track job state and history
- Retry failed jobs with configurable policies
- Support job priorities
- Cancel/pause/resume jobs
- Dead letter queue for failed jobs

**Non-Functional:**
- 100K+ jobs/day
- Exactly-once execution semantics
- 99.9% availability
- Sub-second scheduling latency
- Horizontal scalability
- Fault tolerance (no single point of failure)

### High-Level Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              API Gateway                │
                    └─────────────────┬───────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
┌─────────▼─────────┐   ┌─────────────▼───────────┐   ┌──────────▼──────────┐
│   Job Service     │   │    Scheduler Service    │   │   Monitor Service   │
│  (CRUD, submit)   │   │   (trigger, dispatch)   │   │ (health, metrics)   │
└─────────┬─────────┘   └─────────────┬───────────┘   └─────────────────────┘
          │                           │
          │         ┌─────────────────▼───────────────────┐
          │         │           Job Queue                 │
          │         │        (Kafka / Redis)              │
          │         └───────┬─────────┬──────────┬────────┘
          │                 │         │          │
          │    ┌────────────▼───┐  ┌──▼────┐  ┌──▼───────────┐
          │    │   Worker 1     │  │Worker2│  │   Worker N   │
          │    │  (execute)     │  │       │  │              │
          │    └────────┬───────┘  └───┬───┘  └──────┬───────┘
          │             │              │             │
          │             └──────────────┼─────────────┘
          │                            │
          │         ┌──────────────────▼──────────────────┐
          └────────►│         State Store (DB)            │
                    │   (jobs, schedules, execution log)  │
                    └─────────────────────────────────────┘
```

### Core Components

**1. Job Service**
- CRUD operations for job definitions
- Submit jobs for execution
- Query job status and history
- Validate job configurations

**2. Scheduler Service**
- Evaluate cron expressions
- Trigger jobs at scheduled times
- Manage job dependencies (DAG resolution)
- Dispatch jobs to queue
- Leader election for HA

**3. Worker Pool**
- Execute job logic
- Report progress and results
- Handle heartbeats
- Support graceful shutdown

**4. Job Queue**
- Decouple scheduling from execution
- Priority queues (high, normal, low)
- Dead letter queue for failures
- Partitioned by job type or tenant

**5. State Store**
- Job definitions and schedules
- Execution history
- Worker registry
- Distributed locks

### Data Models

**Job Definition**
```sql
jobs (
    id: uuid PRIMARY KEY,
    name: varchar NOT NULL,
    type: varchar,  -- 'cron', 'one-time', 'triggered'
    cron_expression: varchar,  -- '0 0 * * *'
    payload: jsonb,
    timeout_seconds: int DEFAULT 3600,
    max_retries: int DEFAULT 3,
    retry_delay_seconds: int DEFAULT 60,
    priority: int DEFAULT 5,  -- 1=highest, 10=lowest
    dependencies: uuid[],  -- upstream job IDs
    status: enum(active, paused, deleted),
    created_at: timestamp,
    updated_at: timestamp
)
```

**Job Execution**
```sql
job_executions (
    id: uuid PRIMARY KEY,
    job_id: uuid REFERENCES jobs(id),
    run_number: int,
    status: enum(pending, running, success, failed, cancelled, timeout),
    worker_id: varchar,
    scheduled_at: timestamp,
    started_at: timestamp,
    completed_at: timestamp,
    result: jsonb,
    error: text,
    attempt: int DEFAULT 1
)
```

**Worker Registry**
```sql
workers (
    id: varchar PRIMARY KEY,
    hostname: varchar,
    capabilities: varchar[],  -- ['python', 'shell', 'docker']
    status: enum(active, draining, offline),
    last_heartbeat: timestamp,
    current_job_id: uuid,
    registered_at: timestamp
)
```

### Job State Machine

```
                    ┌──────────────────────────────────────┐
                    │                                      │
    ┌───────────────▼───┐                                  │
    │      PENDING      │                                  │
    └─────────┬─────────┘                                  │
              │ worker picks up                            │
    ┌─────────▼─────────┐                                  │
    │      RUNNING      │◄─────────────┐                   │
    └───┬───────┬───────┘              │                   │
        │       │                      │ retry             │
success │       │ failure              │ (if attempts < max)
        │       │                      │                   │
┌───────▼───┐ ┌─▼─────────┐      ┌─────┴─────┐            │
│  SUCCESS  │ │  FAILED   │──────► RETRYING  │            │
└───────────┘ └───────────┘      └───────────┘            │
                   │                                       │
                   │ max retries exceeded                  │
                   │                                       │
              ┌────▼─────┐                                 │
              │   DLQ    │─────────────────────────────────┘
              └──────────┘      (manual retry)
```

### Cron Scheduling at Scale

**Challenge:** Evaluating thousands of cron expressions every second.

**Solution: Next-Run Index**
```python
class CronScheduler:
    def __init__(self):
        # Priority queue: (next_run_time, job_id)
        self.schedule_heap = []
        self.lock = DistributedLock("scheduler")

    def add_job(self, job):
        next_run = self.calculate_next_run(job.cron_expression)
        heappush(self.schedule_heap, (next_run, job.id))

    def tick(self):
        now = datetime.utcnow()
        while self.schedule_heap and self.schedule_heap[0][0] <= now:
            next_run, job_id = heappop(self.schedule_heap)
            self.dispatch_job(job_id)
            # Reschedule
            job = self.get_job(job_id)
            new_next_run = self.calculate_next_run(job.cron_expression, after=now)
            heappush(self.schedule_heap, (new_next_run, job_id))
```

**Optimization:**
- Store `next_run_at` in database
- Index: `CREATE INDEX idx_next_run ON jobs(next_run_at) WHERE status = 'active'`
- Query: `SELECT * FROM jobs WHERE next_run_at <= NOW() ORDER BY priority, next_run_at LIMIT 100`

### Exactly-Once Execution

**Problem:** Prevent duplicate job execution in distributed environment.

**Solution: Distributed Locking + Idempotency**

```python
class JobExecutor:
    def execute(self, execution_id: str, job: Job):
        # 1. Acquire distributed lock
        lock_key = f"job:{job.id}:execution:{execution_id}"
        if not self.lock_manager.acquire(lock_key, ttl=job.timeout + 60):
            return  # Another worker has this job

        try:
            # 2. Check if already executed (idempotency)
            execution = db.get_execution(execution_id)
            if execution.status in ('success', 'failed'):
                return  # Already processed

            # 3. Mark as running
            db.update_execution(execution_id, status='running', worker_id=self.worker_id)

            # 4. Execute
            result = self.run_job_logic(job)

            # 5. Mark complete
            db.update_execution(execution_id, status='success', result=result)

        except Exception as e:
            db.update_execution(execution_id, status='failed', error=str(e))
            self.maybe_retry(execution_id, job)
        finally:
            self.lock_manager.release(lock_key)
```

### Failure Handling and Retries

**Retry Policy Configuration**
```python
@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay: int = 60  # seconds
    max_delay: int = 3600
    backoff_multiplier: float = 2.0
    retryable_errors: list[str] = field(default_factory=lambda: ['TransientError', 'TimeoutError'])

def calculate_retry_delay(attempt: int, policy: RetryPolicy) -> int:
    delay = policy.initial_delay * (policy.backoff_multiplier ** (attempt - 1))
    return min(delay, policy.max_delay)
```

**Dead Letter Queue (DLQ)**
```python
class DLQHandler:
    def send_to_dlq(self, execution: JobExecution, reason: str):
        dlq_entry = {
            'execution_id': execution.id,
            'job_id': execution.job_id,
            'payload': execution.payload,
            'error': execution.error,
            'attempts': execution.attempt,
            'reason': reason,  # 'max_retries_exceeded', 'non_retryable_error'
            'failed_at': datetime.utcnow()
        }
        self.dlq_store.insert(dlq_entry)
        self.alert_service.notify(f"Job {execution.job_id} sent to DLQ: {reason}")

    def reprocess_dlq_entry(self, dlq_id: str):
        entry = self.dlq_store.get(dlq_id)
        # Create new execution with reset attempt counter
        new_execution = self.create_execution(entry['job_id'], entry['payload'])
        self.job_queue.enqueue(new_execution)
        self.dlq_store.delete(dlq_id)
```

### Worker Pool Management

**Worker Lifecycle**
```python
class Worker:
    def __init__(self, worker_id: str, capabilities: list[str]):
        self.worker_id = worker_id
        self.capabilities = capabilities
        self.status = 'active'

    def start(self):
        self.register()
        self.heartbeat_thread = Thread(target=self.heartbeat_loop)
        self.heartbeat_thread.start()
        self.poll_loop()

    def heartbeat_loop(self):
        while self.status == 'active':
            db.update_worker_heartbeat(self.worker_id)
            time.sleep(10)

    def poll_loop(self):
        while self.status == 'active':
            job = self.queue.poll(
                capabilities=self.capabilities,
                timeout=30
            )
            if job:
                self.execute(job)

    def graceful_shutdown(self):
        self.status = 'draining'
        # Finish current job, stop accepting new ones
        self.current_job.wait_completion()
        self.deregister()
```

**Stale Worker Detection**
```python
def detect_stale_workers():
    stale_threshold = datetime.utcnow() - timedelta(seconds=60)
    stale_workers = db.query("""
        SELECT * FROM workers
        WHERE last_heartbeat < %s AND status = 'active'
    """, stale_threshold)

    for worker in stale_workers:
        # Mark worker offline
        db.update_worker(worker.id, status='offline')
        # Requeue any running jobs
        if worker.current_job_id:
            requeue_job(worker.current_job_id)
```

### DAG Execution (Dependencies)

**Dependency Resolution**
```python
class DAGExecutor:
    def can_run(self, job: Job, execution_context: dict) -> bool:
        if not job.dependencies:
            return True

        for dep_job_id in job.dependencies:
            dep_status = self.get_latest_execution_status(dep_job_id, execution_context)
            if dep_status != 'success':
                return False
        return True

    def schedule_dag(self, dag_id: str, root_jobs: list[Job]):
        context = {'dag_run_id': uuid4(), 'started_at': datetime.utcnow()}

        # Topological sort
        execution_order = self.topological_sort(root_jobs)

        for job in execution_order:
            execution = self.create_execution(job, context)
            # Job will wait in queue until dependencies complete
            self.job_queue.enqueue(execution, check_dependencies=True)
```

### Scaling Considerations

| Component | Scaling Strategy |
|-----------|------------------|
| Scheduler | Leader election (1 active), standby replicas |
| Job Service | Horizontal (stateless) |
| Workers | Horizontal, auto-scale by queue depth |
| Job Queue | Partitioned by job type or priority |
| State Store | Primary-replica, sharded by tenant |

### Monitoring and Observability

**Key Metrics**
- Jobs scheduled/min, executed/min
- Execution latency (p50, p95, p99)
- Queue depth by priority
- Worker utilization
- Failure rate by job type
- DLQ size

**Health Checks**
```python
def health_check():
    checks = {
        'scheduler_leader': check_leader_elected(),
        'queue_healthy': check_queue_connection(),
        'db_healthy': check_db_connection(),
        'workers_available': check_worker_count() > 0,
        'dlq_size': get_dlq_size() < 1000
    }
    return all(checks.values()), checks
```

---

## Otvet (RU)

### Требования

**Функциональные:**
- Планирование задач (одноразовые, периодические/cron)
- Выполнение задач на распределённых воркерах
- Определение зависимостей задач (DAG)
- Отслеживание состояния и истории задач
- Повторные попытки с настраиваемыми политиками
- Поддержка приоритетов задач
- Отмена/пауза/возобновление задач
- Dead letter queue для неудавшихся задач

**Нефункциональные:**
- 100K+ задач/день
- Семантика exactly-once выполнения
- Доступность 99.9%
- Задержка планирования менее секунды
- Горизонтальная масштабируемость
- Отказоустойчивость (без единой точки отказа)

### Основные компоненты

**1. Job Service**
- CRUD-операции для определений задач
- Отправка задач на выполнение
- Запрос статуса и истории задач
- Валидация конфигурации задач

**2. Scheduler Service**
- Вычисление cron-выражений
- Запуск задач в запланированное время
- Управление зависимостями задач (разрешение DAG)
- Отправка задач в очередь
- Выбор лидера для высокой доступности

**3. Пул воркеров**
- Выполнение логики задачи
- Отчёт о прогрессе и результатах
- Обработка heartbeat-ов
- Поддержка graceful shutdown

**4. Очередь задач**
- Декаплинг планирования и выполнения
- Приоритетные очереди (high, normal, low)
- Dead letter queue для сбоев
- Партиционирование по типу задачи или tenant

**5. Хранилище состояния**
- Определения задач и расписания
- История выполнения
- Реестр воркеров
- Распределённые блокировки

### Машина состояний задачи

```
    ┌───────────────┐
    │    PENDING    │  (ожидание)
    └───────┬───────┘
            │ воркер забирает
    ┌───────▼───────┐
    │    RUNNING    │◄───────────┐
    └───┬───────┬───┘            │
        │       │                │ retry
 успех  │       │ сбой           │
        │       │                │
┌───────▼─┐ ┌───▼──────┐   ┌─────┴─────┐
│ SUCCESS │ │  FAILED  │───► RETRYING  │
└─────────┘ └──────────┘   └───────────┘
                 │
                 │ превышено макс. попыток
            ┌────▼────┐
            │   DLQ   │
            └─────────┘
```

### Exactly-Once выполнение

**Проблема:** Предотвращение дублированного выполнения задач в распределённой среде.

**Решение: Распределённая блокировка + Идемпотентность**

```python
class JobExecutor:
    def execute(self, execution_id: str, job: Job):
        # 1. Получить распределённую блокировку
        lock_key = f"job:{job.id}:execution:{execution_id}"
        if not self.lock_manager.acquire(lock_key, ttl=job.timeout + 60):
            return  # Другой воркер уже взял эту задачу

        try:
            # 2. Проверить, уже выполнено (идемпотентность)
            execution = db.get_execution(execution_id)
            if execution.status in ('success', 'failed'):
                return  # Уже обработано

            # 3. Пометить как выполняющееся
            db.update_execution(execution_id, status='running', worker_id=self.worker_id)

            # 4. Выполнить
            result = self.run_job_logic(job)

            # 5. Пометить завершённым
            db.update_execution(execution_id, status='success', result=result)

        except Exception as e:
            db.update_execution(execution_id, status='failed', error=str(e))
            self.maybe_retry(execution_id, job)
        finally:
            self.lock_manager.release(lock_key)
```

### Обработка сбоев и повторные попытки

**Политика повторных попыток**
```python
@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay: int = 60  # секунды
    max_delay: int = 3600
    backoff_multiplier: float = 2.0
    retryable_errors: list[str] = field(default_factory=lambda: ['TransientError', 'TimeoutError'])

def calculate_retry_delay(attempt: int, policy: RetryPolicy) -> int:
    delay = policy.initial_delay * (policy.backoff_multiplier ** (attempt - 1))
    return min(delay, policy.max_delay)
```

**Dead Letter Queue (DLQ)**
```python
class DLQHandler:
    def send_to_dlq(self, execution: JobExecution, reason: str):
        dlq_entry = {
            'execution_id': execution.id,
            'job_id': execution.job_id,
            'payload': execution.payload,
            'error': execution.error,
            'attempts': execution.attempt,
            'reason': reason,  # 'max_retries_exceeded', 'non_retryable_error'
            'failed_at': datetime.utcnow()
        }
        self.dlq_store.insert(dlq_entry)
        self.alert_service.notify(f"Задача {execution.job_id} отправлена в DLQ: {reason}")

    def reprocess_dlq_entry(self, dlq_id: str):
        entry = self.dlq_store.get(dlq_id)
        # Создать новое выполнение со сброшенным счётчиком попыток
        new_execution = self.create_execution(entry['job_id'], entry['payload'])
        self.job_queue.enqueue(new_execution)
        self.dlq_store.delete(dlq_id)
```

### Управление пулом воркеров

**Жизненный цикл воркера**
```python
class Worker:
    def __init__(self, worker_id: str, capabilities: list[str]):
        self.worker_id = worker_id
        self.capabilities = capabilities
        self.status = 'active'

    def start(self):
        self.register()
        self.heartbeat_thread = Thread(target=self.heartbeat_loop)
        self.heartbeat_thread.start()
        self.poll_loop()

    def heartbeat_loop(self):
        while self.status == 'active':
            db.update_worker_heartbeat(self.worker_id)
            time.sleep(10)

    def graceful_shutdown(self):
        self.status = 'draining'
        # Завершить текущую задачу, прекратить принимать новые
        self.current_job.wait_completion()
        self.deregister()
```

**Обнаружение зависших воркеров**
```python
def detect_stale_workers():
    stale_threshold = datetime.utcnow() - timedelta(seconds=60)
    stale_workers = db.query("""
        SELECT * FROM workers
        WHERE last_heartbeat < %s AND status = 'active'
    """, stale_threshold)

    for worker in stale_workers:
        # Пометить воркер как offline
        db.update_worker(worker.id, status='offline')
        # Вернуть текущую задачу в очередь
        if worker.current_job_id:
            requeue_job(worker.current_job_id)
```

### Cron-планирование в масштабе

**Задача:** Вычисление тысяч cron-выражений каждую секунду.

**Решение: Индекс следующего запуска**
```python
class CronScheduler:
    def __init__(self):
        # Приоритетная очередь: (время_следующего_запуска, job_id)
        self.schedule_heap = []
        self.lock = DistributedLock("scheduler")

    def add_job(self, job):
        next_run = self.calculate_next_run(job.cron_expression)
        heappush(self.schedule_heap, (next_run, job.id))

    def tick(self):
        now = datetime.utcnow()
        while self.schedule_heap and self.schedule_heap[0][0] <= now:
            next_run, job_id = heappop(self.schedule_heap)
            self.dispatch_job(job_id)
            # Перепланировать
            job = self.get_job(job_id)
            new_next_run = self.calculate_next_run(job.cron_expression, after=now)
            heappush(self.schedule_heap, (new_next_run, job_id))
```

### Масштабирование

| Компонент | Стратегия масштабирования |
|-----------|---------------------------|
| Scheduler | Выбор лидера (1 активный), резервные реплики |
| Job Service | Горизонтальное (stateless) |
| Workers | Горизонтальное, авто-масштабирование по глубине очереди |
| Job Queue | Партиционирование по типу задачи или приоритету |
| State Store | Primary-replica, шардирование по tenant |

### Мониторинг и наблюдаемость

**Ключевые метрики**
- Запланировано/выполнено задач в минуту
- Задержка выполнения (p50, p95, p99)
- Глубина очереди по приоритету
- Утилизация воркеров
- Частота сбоев по типу задачи
- Размер DLQ

---

## Follow-ups

- How would you implement job prioritization with fair scheduling?
- How do you handle long-running jobs (hours/days)?
- How do you implement multi-tenant isolation?
- How would you add support for job cancellation mid-execution?

## Related Questions

### Prerequisites (Easier)
- [[q-message-queues-event-driven--system-design--medium]] - Message queues
- [[q-consistent-hashing--system-design--hard]] - Consistent hashing

### Related (Same Level)
- [[q-saga-pattern--system-design--hard]] - Saga pattern
- [[q-design-notification-system--system-design--hard]] - Notification system

### Advanced (Harder)
- [[q-consensus-algorithms--system-design--hard]] - Consensus algorithms
- [[q-leader-election--system-design--hard]] - Leader election

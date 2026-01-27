---
id: q-distributed-locking
title: Distributed Locking
aliases:
- Distributed Locking
- Distributed Locks
- Redlock Algorithm
topic: system-design
subtopics:
- distributed-systems
- concurrency
- redis
- zookeeper
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-consensus-algorithms--system-design--hard
- q-consistency-models--system-design--hard
- q-two-phase-commit--system-design--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- distributed-systems
- difficulty/hard
- concurrency
- system-design
anki_cards:
- slug: q-distributed-locking-0-en
  anki_id: null
  synced_at: null
- slug: q-distributed-locking-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How do you implement distributed locking? What are the challenges and solutions?

# Vopros (RU)
> Как реализовать распределённую блокировку? Какие существуют проблемы и решения?

---

## Answer (EN)

**Distributed locking** provides mutual exclusion across multiple processes or nodes in a distributed system. Unlike local locks, distributed locks must handle network failures, clock skew, and partial failures.

### Why Distributed Locks?

```
Use cases:
- Prevent double-processing of tasks
- Coordinate access to shared resources
- Leader election
- Rate limiting per user/resource

Problem without locks:
Node A: reads balance = $100
Node B: reads balance = $100
Node A: withdraws $80 → writes $20
Node B: withdraws $80 → writes $20
→ Both succeed, $160 withdrawn from $100!
```

### Redis-Based Locking

#### Simple SETNX Lock

```
# Acquire lock
SET resource_lock <unique_value> NX PX 30000

# NX = only if not exists
# PX 30000 = expire in 30 seconds

# Release lock (Lua script for atomicity)
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
```

**Critical**: Must use unique value and check before delete to prevent releasing another client's lock.

#### Redlock Algorithm (Redis Cluster)

```
For N Redis masters (typically 5):

1. Get current time T1
2. Try to acquire lock on all N instances
   - Use same key, unique value, short timeout
3. Calculate elapsed time = T2 - T1
4. Lock acquired if:
   - Majority (N/2 + 1) locks obtained
   - Elapsed time < lock validity
5. Effective lock time = validity - elapsed

If failed:
- Unlock all instances immediately
```

```
┌─────────────────────────────────────────────────┐
│              Redlock with 5 nodes               │
│                                                 │
│   Redis1 ✓    Redis2 ✓    Redis3 ✓             │
│   Redis4 ✗    Redis5 ✓                         │
│                                                 │
│   3 out of 5 = majority acquired               │
│   Lock is valid!                                │
└─────────────────────────────────────────────────┘
```

### ZooKeeper Locks

ZooKeeper uses **ephemeral sequential nodes** for distributed locks:

```
Lock acquisition:
1. Create ephemeral sequential node:
   /locks/resource/lock-0000000001

2. Get all children of /locks/resource

3. If your node has lowest sequence number:
   → You have the lock

4. Otherwise:
   → Watch the node with next-lowest number
   → Wait for notification when it's deleted

Lock release:
- Delete your node (or session expires)
```

```
/locks/resource/
├── lock-0000000001  ← Client A (has lock)
├── lock-0000000002  ← Client B (watching 001)
└── lock-0000000003  ← Client C (watching 002)

When Client A releases:
- 001 deleted
- Client B notified, now has lock
```

**Advantages of ZooKeeper**:
- Automatic lock release on client crash (ephemeral nodes)
- Fair ordering (FIFO queue)
- Strong consistency guarantees

### Database-Based Locks

#### SELECT FOR UPDATE

```sql
BEGIN;
SELECT * FROM locks
WHERE resource_id = 'job-123'
FOR UPDATE NOWAIT;

-- Do protected work

COMMIT;  -- Releases lock
```

#### Advisory Locks (PostgreSQL)

```sql
-- Acquire lock (blocks if held)
SELECT pg_advisory_lock(123456);

-- Do protected work

-- Release lock
SELECT pg_advisory_unlock(123456);
```

#### Lock Table Pattern

```sql
-- Create lock entry
INSERT INTO locks (resource_id, owner_id, expires_at)
VALUES ('job-123', 'worker-1', NOW() + INTERVAL '30 seconds')
ON CONFLICT (resource_id) DO NOTHING;

-- Check if lock was acquired
-- (affected rows = 1 means success)
```

### Fencing Tokens

**Problem**: A client holding a lock can be paused (GC, network), lock expires, another client acquires it, first client resumes and writes stale data.

```
Timeline:
T1: Client A acquires lock (token=33)
T2: Client A pauses (GC)
T3: Lock expires
T4: Client B acquires lock (token=34)
T5: Client B writes data
T6: Client A resumes, writes stale data!
→ Corruption despite locks
```

**Solution**: Monotonically increasing fencing tokens

```
┌──────────────────────────────────────────────┐
│            Fencing Token Pattern             │
│                                              │
│ Lock service returns incrementing token     │
│                                              │
│ Client A: lock acquired, token=33           │
│ Client A: pauses...                         │
│ Client B: lock acquired, token=34           │
│                                              │
│ Storage accepts writes only if              │
│ token >= last seen token                    │
│                                              │
│ Client A resumes, sends token=33            │
│ Storage: 33 < 34, REJECTED!                 │
└──────────────────────────────────────────────┘
```

**Implementation**: Storage service tracks highest token seen per resource.

### Lock Expiration and Renewal

```
Challenge: How long should lock be valid?

Too short:
- Lock expires during work
- Another client takes it
- Split-brain

Too long:
- Client crashes holding lock
- Resource blocked for entire duration

Solution: Lease renewal (heartbeat)
- Short initial lease (10-30s)
- Background thread extends lease periodically
- If renewal fails → abort work gracefully
```

```
Time →
├─────────────────────────────────────────────┤
│ Acquire   Renew    Renew    Renew   Release │
│    ├───────┼────────┼────────┼───────┤      │
│    0s     10s      20s      30s    35s      │
│                                             │
│ Lease: 15s, renewed every 10s              │
└─────────────────────────────────────────────┘
```

### Failure Scenarios

| Scenario | Problem | Mitigation |
|----------|---------|------------|
| Client crash | Lock never released | TTL/expiration |
| Network partition | Client thinks it has lock | Fencing tokens |
| Clock skew | TTL miscalculated | Use logical clocks |
| Lock service failure | No locks available | Use consensus (Raft) |
| Long GC pause | Lock expires mid-work | Lease renewal + fencing |

### Martin Kleppmann's Critique of Redlock

Key issues raised:

1. **Clock assumptions**: Redlock assumes bounded clock drift, which isn't guaranteed
2. **GC pauses**: Client can pause after acquiring lock but before doing work
3. **Network delays**: Delays can cause token to arrive after lock expires

```
Kleppmann's argument:
- Redlock tries to be safe without fencing tokens
- But without fencing tokens, NO lock algorithm is safe
- With fencing tokens, simpler single-node lock suffices
```

**Antirez (Redis creator) response**:
- Bounded delays are practical assumption
- Redlock is for efficiency, not absolute safety
- Use consensus systems for critical safety

### Comparison of Approaches

| Approach | Consistency | Availability | Complexity | Use Case |
|----------|-------------|--------------|------------|----------|
| Redis SETNX | Weak | High | Low | Caching, rate limiting |
| Redlock | Medium | High | Medium | Cross-node coordination |
| ZooKeeper | Strong | Medium | High | Critical coordination |
| DB locks | Strong | Low | Low | Transactional systems |
| etcd | Strong | Medium | Medium | Kubernetes, config |

### Best Practices

```
1. Always use unique owner ID
   → Prevents releasing others' locks

2. Always set TTL/expiration
   → Prevents deadlock on client crash

3. Use fencing tokens for safety-critical systems
   → Prevents split-brain writes

4. Implement lease renewal
   → Handles long operations gracefully

5. Handle lock acquisition failure
   → Retry with backoff, or fail fast

6. Log lock operations
   → Debugging distributed issues
```

---

## Otvet (RU)

**Распределённая блокировка** обеспечивает взаимное исключение между несколькими процессами или узлами в распределённой системе. В отличие от локальных блокировок, распределённые должны обрабатывать сетевые сбои, расхождение часов и частичные отказы.

### Зачем нужны распределённые блокировки?

```
Варианты использования:
- Предотвращение двойной обработки задач
- Координация доступа к общим ресурсам
- Выбор лидера
- Rate limiting по пользователю/ресурсу

Проблема без блокировок:
Узел A: читает баланс = 100$
Узел B: читает баланс = 100$
Узел A: снимает 80$ → записывает 20$
Узел B: снимает 80$ → записывает 20$
→ Оба успешны, снято 160$ со 100$!
```

### Блокировки на основе Redis

#### Простая блокировка SETNX

```
# Получение блокировки
SET resource_lock <unique_value> NX PX 30000

# NX = только если не существует
# PX 30000 = истекает через 30 секунд

# Освобождение (Lua-скрипт для атомарности)
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
```

**Критично**: Обязательно использовать уникальное значение и проверять перед удалением, чтобы не освободить чужую блокировку.

#### Алгоритм Redlock (Redis Cluster)

```
Для N мастеров Redis (обычно 5):

1. Получить текущее время T1
2. Попытаться получить блокировку на всех N инстансах
   - Один ключ, уникальное значение, короткий таймаут
3. Вычислить прошедшее время = T2 - T1
4. Блокировка получена если:
   - Большинство (N/2 + 1) блокировок получено
   - Прошедшее время < срока действия
5. Эффективное время = срок действия - прошедшее

Если не удалось:
- Немедленно разблокировать все инстансы
```

### Блокировки ZooKeeper

ZooKeeper использует **эфемерные последовательные узлы**:

```
Получение блокировки:
1. Создать эфемерный последовательный узел:
   /locks/resource/lock-0000000001

2. Получить все дочерние узлы /locks/resource

3. Если ваш узел имеет наименьший номер:
   → У вас есть блокировка

4. Иначе:
   → Отслеживать узел с предыдущим номером
   → Ждать уведомления при его удалении

Освобождение:
- Удалить свой узел (или сессия истечёт)
```

**Преимущества ZooKeeper**:
- Автоматическое освобождение при сбое клиента
- Справедливый порядок (FIFO-очередь)
- Сильные гарантии согласованности

### Блокировки на основе БД

#### SELECT FOR UPDATE

```sql
BEGIN;
SELECT * FROM locks
WHERE resource_id = 'job-123'
FOR UPDATE NOWAIT;

-- Защищённая работа

COMMIT;  -- Освобождает блокировку
```

#### Advisory Locks (PostgreSQL)

```sql
-- Получить блокировку (блокирует если занята)
SELECT pg_advisory_lock(123456);

-- Защищённая работа

-- Освободить блокировку
SELECT pg_advisory_unlock(123456);
```

### Fencing Tokens (ограждающие токены)

**Проблема**: Клиент с блокировкой может быть приостановлен (GC, сеть), блокировка истекает, другой клиент её получает, первый возобновляется и записывает устаревшие данные.

```
Временная линия:
T1: Клиент A получает блокировку (token=33)
T2: Клиент A приостановлен (GC)
T3: Блокировка истекает
T4: Клиент B получает блокировку (token=34)
T5: Клиент B записывает данные
T6: Клиент A возобновляется, записывает устаревшие данные!
→ Повреждение несмотря на блокировки
```

**Решение**: Монотонно возрастающие fencing tokens

```
Хранилище принимает записи только если
token >= последнего увиденного токена

Клиент A возобновляется, отправляет token=33
Хранилище: 33 < 34, ОТКЛОНЕНО!
```

### Истечение и продление блокировки

```
Проблема: Какой срок действия установить?

Слишком короткий:
- Блокировка истекает во время работы
- Другой клиент её получает
- Split-brain

Слишком длинный:
- Клиент падает с блокировкой
- Ресурс заблокирован надолго

Решение: Продление аренды (heartbeat)
- Короткая начальная аренда (10-30с)
- Фоновый поток продлевает периодически
- Если продление не удалось → корректное прерывание
```

### Сценарии отказов

| Сценарий | Проблема | Решение |
|----------|----------|---------|
| Сбой клиента | Блокировка не освобождается | TTL/истечение |
| Сетевой раздел | Клиент думает что имеет блокировку | Fencing tokens |
| Расхождение часов | Неверный расчёт TTL | Логические часы |
| Сбой сервиса блокировок | Блокировки недоступны | Консенсус (Raft) |
| Долгая GC-пауза | Блокировка истекает в процессе | Продление + fencing |

### Критика Redlock от Мартина Клеппманна

Ключевые проблемы:

1. **Допущения о часах**: Redlock предполагает ограниченное расхождение часов, что не гарантировано
2. **GC-паузы**: Клиент может приостановиться после получения блокировки
3. **Сетевые задержки**: Задержки могут привести к прибытию токена после истечения блокировки

**Аргумент Клеппманна**:
- Redlock пытается быть безопасным без fencing tokens
- Но без fencing tokens НИ ОДИН алгоритм не безопасен
- С fencing tokens достаточно простой одноузловой блокировки

### Сравнение подходов

| Подход | Согласованность | Доступность | Сложность | Применение |
|--------|-----------------|-------------|-----------|------------|
| Redis SETNX | Слабая | Высокая | Низкая | Кеширование, rate limiting |
| Redlock | Средняя | Высокая | Средняя | Межузловая координация |
| ZooKeeper | Сильная | Средняя | Высокая | Критичная координация |
| DB locks | Сильная | Низкая | Низкая | Транзакционные системы |
| etcd | Сильная | Средняя | Средняя | Kubernetes, конфиг |

### Лучшие практики

```
1. Всегда использовать уникальный ID владельца
   → Предотвращает освобождение чужих блокировок

2. Всегда устанавливать TTL/истечение
   → Предотвращает deadlock при сбое клиента

3. Использовать fencing tokens для критичных систем
   → Предотвращает split-brain записи

4. Реализовать продление аренды
   → Обрабатывает длинные операции корректно

5. Обрабатывать неудачу получения блокировки
   → Повтор с backoff или быстрый отказ

6. Логировать операции с блокировками
   → Отладка распределённых проблем
```

---

## Follow-ups

- How would you implement a distributed read-write lock?
- What is the difference between optimistic and pessimistic locking?
- How does Google Chubby implement distributed locking?
- When should you use lease-based vs fencing token-based approaches?

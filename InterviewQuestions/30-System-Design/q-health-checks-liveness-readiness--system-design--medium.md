---
id: sysdes-061
title: Health Checks - Liveness vs Readiness
aliases:
- Health Checks
- Liveness Probe
- Readiness Probe
- Kubernetes Health
topic: system-design
subtopics:
- observability
- kubernetes
- resilience
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-kubernetes-basics--system-design--medium
- q-heartbeat-mechanisms--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- observability
- difficulty/medium
- resilience
- system-design
anki_cards:
- slug: sysdes-061-0-en
  language: en
  anki_id: 1769160580024
  synced_at: '2026-01-23T13:29:45.858452'
- slug: sysdes-061-0-ru
  language: ru
  anki_id: 1769160580049
  synced_at: '2026-01-23T13:29:45.859919'
---
# Question (EN)
> What is the difference between liveness and readiness probes? How do they work in Kubernetes?

# Vopros (RU)
> В чём разница между liveness и readiness probes? Как они работают в Kubernetes?

---

## Answer (EN)

**Liveness probes** check if an application is alive (restart if dead). **Readiness probes** check if it's ready to receive traffic (remove from load balancer if not).

### Key Differences

| Aspect | Liveness | Readiness |
|--------|----------|-----------|
| Question | Is the app alive? | Can it handle requests? |
| Failure action | Restart container | Remove from service |
| Use case | Detect deadlocks | Detect temporary overload |
| Recovery | Container restart | Wait for recovery |

### How They Work

```
┌─────────────────────────────────────────────────────┐
│                    Kubernetes                        │
│                                                      │
│  Liveness Probe        Readiness Probe              │
│  "Are you alive?"      "Can you serve traffic?"    │
│         │                      │                    │
│         ▼                      ▼                    │
│  ┌─────────────┐        ┌─────────────┐            │
│  │    Pod      │        │    Pod      │            │
│  │  ┌───────┐  │        │  ┌───────┐  │            │
│  │  │  App  │  │        │  │  App  │  │            │
│  │  └───────┘  │        │  └───────┘  │            │
│  └─────────────┘        └─────────────┘            │
│         │                      │                    │
│  Fail → Restart         Fail → Remove from         │
│                               Service endpoints    │
└─────────────────────────────────────────────────────┘
```

### Probe Types

| Type | Mechanism | Example |
|------|-----------|---------|
| HTTP | GET request to endpoint | `GET /healthz` returns 200 |
| TCP | TCP connection attempt | Connect to port 8080 |
| Command | Execute command in container | `cat /tmp/healthy` |
| gRPC | gRPC health check | `grpc.health.v1.Health` |

### Kubernetes Configuration

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 15   # Wait before first check
      periodSeconds: 10         # Check every 10s
      failureThreshold: 3       # 3 failures → restart

    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 3       # 3 failures → remove from LB
```

### What to Check

```
Liveness endpoint (/healthz):
- App process is running
- Not in deadlock
- Can respond at all
- Keep it simple and fast

Readiness endpoint (/ready):
- Database connection available
- Cache warmed up
- Dependencies healthy
- Can process requests
```

### Startup Probe (Kubernetes 1.16+)

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
  # Total: 30 * 10 = 300s to start

# Liveness/readiness disabled until startup succeeds
# Good for slow-starting applications
```

### Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Liveness checks DB | DB outage restarts all pods | Only check app process |
| Same endpoint for both | Can't distinguish issues | Separate endpoints |
| Too aggressive | Flapping pods | Increase thresholds |
| Missing initialDelay | Restart during startup | Set appropriate delay |

---

## Otvet (RU)

**Liveness probes** проверяют, жив ли application (перезапуск если мёртв). **Readiness probes** проверяют, готов ли он принимать трафик (убрать из load balancer если нет).

### Ключевые различия

| Аспект | Liveness | Readiness |
|--------|----------|-----------|
| Вопрос | Приложение живо? | Может обрабатывать запросы? |
| Действие при сбое | Перезапуск контейнера | Убрать из service |
| Случай использования | Обнаружение deadlock | Временная перегрузка |
| Восстановление | Перезапуск контейнера | Ожидание восстановления |

### Типы проб

| Тип | Механизм | Пример |
|-----|----------|--------|
| HTTP | GET запрос к endpoint | `GET /healthz` возвращает 200 |
| TCP | Попытка TCP соединения | Подключиться к порту 8080 |
| Command | Выполнить команду в контейнере | `cat /tmp/healthy` |
| gRPC | gRPC health check | `grpc.health.v1.Health` |

### Что проверять

```
Liveness endpoint (/healthz):
- Процесс приложения работает
- Нет deadlock
- Может ответить вообще
- Держите простым и быстрым

Readiness endpoint (/ready):
- Соединение с БД доступно
- Кеш прогрет
- Зависимости здоровы
- Может обрабатывать запросы
```

### Startup Probe (Kubernetes 1.16+)

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
  # Итого: 30 * 10 = 300с на старт

# Liveness/readiness отключены пока startup не успешен
# Хорошо для медленно стартующих приложений
```

### Частые ошибки

| Ошибка | Проблема | Решение |
|--------|----------|---------|
| Liveness проверяет БД | Сбой БД перезапускает все поды | Проверять только процесс |
| Один endpoint для обоих | Нельзя различить проблемы | Отдельные endpoints |
| Слишком агрессивно | Flapping подов | Увеличить thresholds |

---

## Follow-ups

- What is a startup probe and when do you need it?
- How do you implement graceful shutdown with readiness probes?
- What is the difference between health check types (HTTP vs TCP vs exec)?

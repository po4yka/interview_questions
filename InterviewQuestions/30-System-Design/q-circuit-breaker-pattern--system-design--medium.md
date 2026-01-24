---
id: sysdes-022
title: Circuit Breaker Pattern
aliases:
- Circuit Breaker
- Resilience Pattern
topic: system-design
subtopics:
- resilience
- microservices
- fault-tolerance
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-retry-strategies--system-design--medium
- q-failover-strategies--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- resilience
- difficulty/medium
- microservices
- system-design
anki_cards:
- slug: sysdes-022-0-en
  language: en
  anki_id: 1769158889491
  synced_at: '2026-01-23T13:29:45.884566'
- slug: sysdes-022-0-ru
  language: ru
  anki_id: 1769158889516
  synced_at: '2026-01-23T13:29:45.885721'
---
# Question (EN)
> What is the Circuit Breaker pattern? How does it improve system resilience?

# Vopros (RU)
> Что такое паттерн Circuit Breaker? Как он улучшает отказоустойчивость системы?

---

## Answer (EN)

**Circuit Breaker** is a resilience pattern that prevents cascading failures by stopping requests to a failing service.

### The Problem

```
Without Circuit Breaker:
Service A → Service B (failing)
         → timeout...
         → retry...
         → timeout...
         → resources exhausted
         → Service A also fails (cascade)
```

### Circuit Breaker States

```
        success
     ┌───────────┐
     ↓           │
  [CLOSED] ──failures exceed threshold──→ [OPEN]
     ↑                                       │
     │                                       │
     │                              timeout expires
     │                                       │
     │                                       ↓
     └──────success──────── [HALF-OPEN] ←────┘
                               │
                          failure
                               │
                               ↓
                            [OPEN]
```

**CLOSED:** Normal operation, requests flow through
**OPEN:** Requests fail immediately (fail fast)
**HALF-OPEN:** Test if service recovered (limited requests)

### Implementation

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def call(self, func, *args):
        if self.state == "OPEN":
            if self._should_try_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Circuit is open")

        try:
            result = func(*args)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def _should_try_reset(self):
        return time.time() - self.last_failure_time > self.recovery_timeout
```

### Configuration Parameters

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| Failure threshold | Failures before opening | 5-10 |
| Recovery timeout | Time before half-open | 30-60 seconds |
| Success threshold | Successes to close from half-open | 3-5 |
| Request timeout | Max time per request | 1-5 seconds |

### Benefits

1. **Fail fast:** Don't wait for timeouts
2. **Reduce load:** Stop hammering failing service
3. **Graceful degradation:** Return fallback response
4. **Allow recovery:** Give failing service time to recover

### Fallback Strategies

```python
@circuit_breaker
def get_recommendations(user_id):
    return recommendation_service.get(user_id)

def get_recommendations_with_fallback(user_id):
    try:
        return get_recommendations(user_id)
    except CircuitOpenError:
        # Fallback options:
        return get_cached_recommendations(user_id)  # 1. Cache
        return get_default_recommendations()         # 2. Default
        return []                                    # 3. Empty
```

### Libraries and Tools

| Language | Library |
|----------|---------|
| Java | Resilience4j, Hystrix (deprecated) |
| Python | pybreaker, circuitbreaker |
| Go | sony/gobreaker |
| .NET | Polly |
| Node.js | opossum |

---

## Otvet (RU)

**Circuit Breaker** - паттерн отказоустойчивости, который предотвращает каскадные сбои, останавливая запросы к падающему сервису.

### Проблема

```
Без Circuit Breaker:
Сервис A → Сервис B (падает)
         → таймаут...
         → повтор...
         → таймаут...
         → ресурсы исчерпаны
         → Сервис A тоже падает (каскад)
```

### Состояния Circuit Breaker

```
        успех
     ┌───────────┐
     ↓           │
  [CLOSED] ──сбои превысили порог──→ [OPEN]
     ↑                                   │
     │                                   │
     │                          таймаут истек
     │                                   │
     │                                   ↓
     └──────успех──────── [HALF-OPEN] ←──┘
                               │
                           сбой
                               │
                               ↓
                            [OPEN]
```

**CLOSED:** Нормальная работа, запросы проходят
**OPEN:** Запросы сразу падают (fail fast)
**HALF-OPEN:** Проверка восстановления сервиса (ограниченные запросы)

### Реализация

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def call(self, func, *args):
        if self.state == "OPEN":
            if self._should_try_reset():
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Circuit is open")

        try:
            result = func(*args)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def _should_try_reset(self):
        return time.time() - self.last_failure_time > self.recovery_timeout
```

### Параметры конфигурации

| Параметр | Описание | Типичное значение |
|----------|----------|-------------------|
| Порог сбоев | Сбои до открытия | 5-10 |
| Таймаут восстановления | Время до half-open | 30-60 секунд |
| Порог успехов | Успехи для закрытия из half-open | 3-5 |
| Таймаут запроса | Макс. время запроса | 1-5 секунд |

### Преимущества

1. **Fail fast:** Не ждать таймаутов
2. **Снижение нагрузки:** Не долбить падающий сервис
3. **Graceful degradation:** Возврат fallback ответа
4. **Время на восстановление:** Дать падающему сервису восстановиться

### Стратегии Fallback

```python
@circuit_breaker
def get_recommendations(user_id):
    return recommendation_service.get(user_id)

def get_recommendations_with_fallback(user_id):
    try:
        return get_recommendations(user_id)
    except CircuitOpenError:
        # Варианты fallback:
        return get_cached_recommendations(user_id)  # 1. Кеш
        return get_default_recommendations()         # 2. Дефолт
        return []                                    # 3. Пусто
```

### Библиотеки и инструменты

| Язык | Библиотека |
|------|------------|
| Java | Resilience4j, Hystrix (deprecated) |
| Python | pybreaker, circuitbreaker |
| Go | sony/gobreaker |
| .NET | Polly |
| Node.js | opossum |

---

## Follow-ups

- How do you test circuit breakers?
- What is the difference between circuit breaker and bulkhead?
- How do you monitor circuit breaker state in production?

## Related Questions

### Prerequisites (Easier)
- [[q-microservices-vs-monolith--system-design--hard]] - Microservices basics

### Related (Same Level)
- [[q-retry-strategies--system-design--medium]] - Retry patterns
- [[q-failover-strategies--system-design--medium]] - Failover

### Advanced (Harder)
- [[q-design-notification-system--system-design--hard]] - System design

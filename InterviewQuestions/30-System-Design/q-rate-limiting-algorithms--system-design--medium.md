---
id: sysdes-019
title: Rate Limiting Algorithms
aliases:
- Rate Limiting
- Throttling
- Token Bucket
topic: system-design
subtopics:
- api
- security
- performance
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-api-gateway-patterns--system-design--medium
- q-circuit-breaker-pattern--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- api
- difficulty/medium
- security
- system-design
anki_cards:
- slug: sysdes-019-0-en
  language: en
  anki_id: 1769158889541
  synced_at: '2026-01-23T13:29:45.886890'
- slug: sysdes-019-0-ru
  language: ru
  anki_id: 1769158889566
  synced_at: '2026-01-23T13:29:45.888466'
---
# Question (EN)
> What are the main rate limiting algorithms? How do you choose and implement rate limiting in a distributed system?

# Vopros (RU)
> Какие основные алгоритмы rate limiting существуют? Как выбрать и реализовать rate limiting в распределенной системе?

---

## Answer (EN)

**Rate limiting** controls how many requests a client can make within a time window to protect resources and ensure fair usage.

### Common Algorithms

**1. Token Bucket**

Tokens added at fixed rate; requests consume tokens.

```
Bucket capacity: 10 tokens
Refill rate: 1 token/second

Request arrives:
  - Tokens available? → Allow, remove token
  - No tokens? → Reject (429)

Allows bursts up to bucket size
```

```python
class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def allow_request(self):
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
```

**2. Leaky Bucket**

Requests processed at fixed rate; excess queued or dropped.

```
Queue capacity: 10
Processing rate: 1 request/second

Requests processed in FIFO order
Excess requests dropped when queue full
Smooth output rate
```

**3. Fixed Window Counter**

Count requests in fixed time windows.

```
Window: 1 minute
Limit: 100 requests

12:00:00 - 12:00:59 → Counter for this minute
12:01:00 - 12:01:59 → New counter

Problem: Burst at window boundaries
  99 requests at 12:00:59
  99 requests at 12:01:00
  = 198 requests in 2 seconds
```

**4. Sliding Window Log**

Track timestamp of each request; count in sliding window.

```
Window: 1 minute
Limit: 100 requests

Store: [12:00:01, 12:00:05, 12:00:30, ...]

On request at 12:01:15:
  Count requests from 12:00:15 to 12:01:15
  Allow if count < 100
```

**5. Sliding Window Counter**

Hybrid: weighted average of current and previous window.

```
Previous window (12:00-12:01): 80 requests
Current window (12:01-12:02): 20 requests
Current position: 12:01:30 (50% into window)

Weighted count = 80 * 0.5 + 20 = 60
```

### Comparison

| Algorithm | Memory | Accuracy | Burst Handling |
|-----------|--------|----------|----------------|
| Token Bucket | Low | Good | Allows bursts |
| Leaky Bucket | Low | Good | Smooths traffic |
| Fixed Window | Low | Poor | Edge burst problem |
| Sliding Log | High | Excellent | No bursts |
| Sliding Counter | Medium | Good | Limited bursts |

### Distributed Rate Limiting

**Challenge:** Multiple servers need shared state.

**Solution 1: Centralized Store (Redis)**
```python
def is_rate_limited(user_id):
    key = f"rate_limit:{user_id}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, 60)  # 1 minute window
    return count > 100
```

**Solution 2: Local + Sync**
- Each node has local counter
- Periodically sync with central store
- Less accurate but lower latency

### Response Headers

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
Retry-After: 30
```

---

## Otvet (RU)

**Rate limiting** контролирует количество запросов клиента в временном окне для защиты ресурсов и обеспечения справедливого использования.

### Основные алгоритмы

**1. Token Bucket**

Токены добавляются с фиксированной скоростью; запросы потребляют токены.

```
Емкость bucket: 10 токенов
Скорость пополнения: 1 токен/секунду

Приходит запрос:
  - Токены есть? → Разрешить, убрать токен
  - Нет токенов? → Отклонить (429)

Позволяет burst'ы до размера bucket
```

```python
class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def allow_request(self):
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
```

**2. Leaky Bucket**

Запросы обрабатываются с фиксированной скоростью; избыток в очередь или отбрасывается.

```
Емкость очереди: 10
Скорость обработки: 1 запрос/секунду

Запросы обрабатываются в порядке FIFO
Избыточные запросы отбрасываются при заполнении очереди
Равномерная выходная скорость
```

**3. Fixed Window Counter**

Подсчет запросов в фиксированных временных окнах.

```
Окно: 1 минута
Лимит: 100 запросов

12:00:00 - 12:00:59 → Счетчик для этой минуты
12:01:00 - 12:01:59 → Новый счетчик

Проблема: Burst на границах окон
  99 запросов в 12:00:59
  99 запросов в 12:01:00
  = 198 запросов за 2 секунды
```

**4. Sliding Window Log**

Хранение timestamp каждого запроса; подсчет в скользящем окне.

```
Окно: 1 минута
Лимит: 100 запросов

Хранится: [12:00:01, 12:00:05, 12:00:30, ...]

При запросе в 12:01:15:
  Подсчитать запросы от 12:00:15 до 12:01:15
  Разрешить если count < 100
```

**5. Sliding Window Counter**

Гибрид: взвешенное среднее текущего и предыдущего окна.

```
Предыдущее окно (12:00-12:01): 80 запросов
Текущее окно (12:01-12:02): 20 запросов
Текущая позиция: 12:01:30 (50% окна)

Взвешенный подсчет = 80 * 0.5 + 20 = 60
```

### Сравнение

| Алгоритм | Память | Точность | Обработка burst |
|----------|--------|----------|-----------------|
| Token Bucket | Низкая | Хорошая | Разрешает burst'ы |
| Leaky Bucket | Низкая | Хорошая | Сглаживает трафик |
| Fixed Window | Низкая | Низкая | Проблема на границах |
| Sliding Log | Высокая | Отличная | Без burst'ов |
| Sliding Counter | Средняя | Хорошая | Ограниченные burst'ы |

### Распределенный Rate Limiting

**Проблема:** Несколько серверов нуждаются в общем состоянии.

**Решение 1: Централизованное хранилище (Redis)**
```python
def is_rate_limited(user_id):
    key = f"rate_limit:{user_id}"
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, 60)  # 1 минутное окно
    return count > 100
```

**Решение 2: Локально + синхронизация**
- Каждый узел имеет локальный счетчик
- Периодическая синхронизация с центральным хранилищем
- Менее точно, но меньше задержка

### Заголовки ответа

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640000000
Retry-After: 30
```

---

## Follow-ups

- How do you handle rate limiting in a multi-tenant system?
- What is the difference between rate limiting and throttling?
- How do you implement rate limiting for API keys vs IP addresses?

## Related Questions

### Prerequisites (Easier)
- [[q-api-gateway-patterns--system-design--medium]] - API Gateway

### Related (Same Level)
- [[q-circuit-breaker-pattern--system-design--medium]] - Circuit breaker
- [[q-caching-strategies--system-design--medium]] - Caching

### Advanced (Harder)
- [[q-design-rate-limiter--system-design--hard]] - Design Rate Limiter

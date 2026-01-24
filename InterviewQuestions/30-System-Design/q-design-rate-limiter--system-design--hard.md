---
id: sysdes-049
title: Design Rate Limiter
aliases:
- Design Rate Limiter
- Rate Limiting System
- API Throttling
topic: system-design
subtopics:
- design-problems
- api
- distributed-systems
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-rate-limiting--system-design--medium
- q-api-gateway--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- api
- system-design
anki_cards:
- slug: sysdes-049-0-en
  language: en
  anki_id: 1769159521994
  synced_at: '2026-01-23T13:49:17.837721'
- slug: sysdes-049-0-ru
  language: ru
  anki_id: 1769159522019
  synced_at: '2026-01-23T13:49:17.839553'
---
# Question (EN)
> Design a distributed rate limiter for a large-scale API. Consider different algorithms and their trade-offs.

# Vopros (RU)
> Спроектируйте распределённый rate limiter для крупномасштабного API. Рассмотрите разные алгоритмы и их компромиссы.

---

## Answer (EN)

### Requirements

**Functional**: Limit requests per user/IP/API key, configurable limits, return 429 when exceeded
**Non-functional**: Low latency (<1ms), distributed, accurate counting, high availability

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       Clients                                │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                    Load Balancer                             │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                  Rate Limiter Layer                          │
│     ┌─────────────────────────────────────────────────┐     │
│     │              Rate Limiter Service               │     │
│     │  (Check Redis, Apply rules, Return decision)    │     │
│     └─────────────────────┬───────────────────────────┘     │
│                           │                                  │
│     ┌─────────────────────▼───────────────────────────┐     │
│     │            Redis Cluster                        │     │
│     │        (Counter storage, Lua scripts)           │     │
│     └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                    API Servers                               │
└──────────────────────────────────────────────────────────────┘
```

### Rate Limiting Algorithms

| Algorithm | Pros | Cons | Use Case |
|-----------|------|------|----------|
| Fixed Window | Simple, memory efficient | Burst at window edges | Basic limiting |
| Sliding Window Log | Accurate | High memory | Small scale |
| Sliding Window Counter | Accurate, efficient | Slightly complex | Production systems |
| Token Bucket | Allows bursts | Slightly complex | API rate limiting |
| Leaky Bucket | Smooth output | No bursts allowed | Traffic shaping |

### Token Bucket (Most Common)

```
┌─────────────────────────────┐
│      Token Bucket           │
│   ┌───────────────────┐     │
│   │ ○ ○ ○ ○ ○ ○ ○ ○  │     │  Capacity: 10 tokens
│   │   (tokens)        │     │  Refill: 1 token/second
│   └────────┬──────────┘     │
│            ↓                │
│    [Request consumes        │
│         1 token]            │
└─────────────────────────────┘

If tokens available: Allow request, consume token
If no tokens: Reject with 429

Redis implementation:
EVAL "
  local tokens = redis.call('GET', KEYS[1])
  local last_refill = redis.call('GET', KEYS[2])
  -- Calculate new tokens based on time passed
  -- Consume token if available
  -- Return allowed/denied
" 2 user:123:tokens user:123:last_refill
```

### Sliding Window Counter

```
Current: 12:01:15
Window: 1 minute
Limit: 100 requests

Previous window (12:00): 70 requests
Current window (12:01): 20 requests so far

Weight = (60 - 15) / 60 = 0.75 for previous window

Weighted count = 70 * 0.75 + 20 = 72.5

If weighted_count < 100: Allow
```

### Distributed Considerations

```
Challenge: Multiple servers need consistent view

Solutions:

1. Centralized (Redis):
   - Single source of truth
   - Atomic operations with Lua
   - Network latency cost

2. Local + Sync:
   - Local counter per server
   - Async sync to central store
   - Eventually consistent

3. Sticky Sessions:
   - Route user to same server
   - Local counter sufficient
   - Less accurate overall
```

### HTTP Response

```
200 OK (within limit):
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1623456789

429 Too Many Requests (exceeded):
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1623456789
  Retry-After: 30
```

---

## Otvet (RU)

### Требования

**Функциональные**: Ограничить запросы по user/IP/API key, настраиваемые лимиты, вернуть 429 при превышении
**Нефункциональные**: Низкая задержка (<1мс), распределённый, точный подсчёт

### Алгоритмы Rate Limiting

| Алгоритм | Плюсы | Минусы | Применение |
|----------|-------|--------|------------|
| Fixed Window | Простой, эффективен по памяти | Всплески на границах | Базовое ограничение |
| Sliding Window Log | Точный | Много памяти | Малый масштаб |
| Sliding Window Counter | Точный, эффективный | Чуть сложнее | Продакшен |
| Token Bucket | Позволяет всплески | Чуть сложнее | API rate limiting |
| Leaky Bucket | Гладкий вывод | Нет всплесков | Traffic shaping |

### Token Bucket (Самый распространённый)

```
┌─────────────────────────────┐
│      Token Bucket           │
│   ┌───────────────────┐     │
│   │ ○ ○ ○ ○ ○ ○ ○ ○  │     │  Capacity: 10 токенов
│   │   (токены)        │     │  Refill: 1 токен/секунду
│   └────────┬──────────┘     │
│            ↓                │
│    [Запрос потребляет       │
│         1 токен]            │
└─────────────────────────────┘

Если токены есть: Разрешить запрос, потребить токен
Если нет токенов: Отклонить с 429
```

### Распределённые соображения

```
Вызов: Множество серверов требуют согласованного view

Решения:

1. Централизованный (Redis):
   - Единый источник истины
   - Атомарные операции через Lua
   - Стоимость сетевой задержки

2. Локальный + Синхронизация:
   - Локальный счётчик на сервер
   - Async синхронизация с центральным хранилищем
   - Eventually consistent

3. Sticky Sessions:
   - Направлять пользователя на тот же сервер
   - Локального счётчика достаточно
   - Менее точно в целом
```

### HTTP Response

```
200 OK (в пределах лимита):
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1623456789

429 Too Many Requests (превышено):
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  Retry-After: 30
```

---

## Follow-ups

- How do you handle rate limiting across multiple data centers?
- What is the difference between rate limiting and throttling?
- How do you implement tiered rate limits (free vs paid users)?

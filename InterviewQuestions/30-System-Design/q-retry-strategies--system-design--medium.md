---
id: sysdes-023
title: Retry Strategies and Exponential Backoff
aliases:
- Retry Pattern
- Exponential Backoff
- Jitter
topic: system-design
subtopics:
- resilience
- distributed-systems
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
- q-circuit-breaker-pattern--system-design--medium
- q-idempotency--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- resilience
- difficulty/medium
- distributed-systems
- system-design
anki_cards:
- slug: sysdes-023-0-en
  language: en
  anki_id: 1769158888696
  synced_at: '2026-01-23T13:29:45.855471'
- slug: sysdes-023-0-ru
  language: ru
  anki_id: 1769158888715
  synced_at: '2026-01-23T13:29:45.857218'
---
# Question (EN)
> What are common retry strategies? Explain exponential backoff and why jitter is important.

# Vopros (RU)
> Какие существуют стратегии повторных попыток? Объясните экспоненциальную задержку и почему jitter важен.

---

## Answer (EN)

**Retry strategies** help systems recover from transient failures by automatically retrying failed operations.

### When to Retry

**Retry for transient failures:**
- Network timeouts
- 503 Service Unavailable
- 429 Too Many Requests
- Connection refused (temporary)

**Don't retry for:**
- 400 Bad Request (client error)
- 401/403 Authentication/Authorization errors
- 404 Not Found
- Business logic errors

### Common Retry Strategies

**1. Immediate Retry**
```
Attempt 1 → Fail → Attempt 2 → Fail → Attempt 3
                No delay between retries
```
Problem: Can overwhelm already struggling service

**2. Fixed Delay**
```
Attempt 1 → [2s] → Attempt 2 → [2s] → Attempt 3
           Fixed delay between attempts
```
Better, but still synchronized load

**3. Exponential Backoff**
```
Attempt 1 → [1s] → Attempt 2 → [2s] → Attempt 3 → [4s] → Attempt 4
           Delay doubles each attempt
```

```python
def exponential_backoff(attempt, base_delay=1, max_delay=60):
    delay = min(base_delay * (2 ** attempt), max_delay)
    return delay

# Attempt 0: 1s, 1: 2s, 2: 4s, 3: 8s, 4: 16s, 5: 32s, 6+: 60s (capped)
```

**4. Exponential Backoff with Jitter**
```python
def exponential_backoff_with_jitter(attempt, base_delay=1, max_delay=60):
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay)  # Add randomness
    return jitter

# Full jitter: random between 0 and calculated delay
```

### Why Jitter Matters

**Problem: Thundering Herd**
```
Service fails at T=0
1000 clients retry at T=1s (exponential backoff)
1000 clients retry at T=2s
... synchronized waves of requests
```

**Solution: Jitter spreads load**
```
Service fails at T=0
Client A retries at T=0.7s
Client B retries at T=1.3s
Client C retries at T=0.9s
... distributed retry times
```

### Jitter Strategies

| Strategy | Formula | Use Case |
|----------|---------|----------|
| Full jitter | random(0, delay) | Most common |
| Equal jitter | delay/2 + random(0, delay/2) | Minimum delay guaranteed |
| Decorrelated | min(max, random(base, prev*3)) | AWS recommendation |

### Implementation Example

```python
import time
import random

def retry_with_backoff(
    func,
    max_retries=5,
    base_delay=1,
    max_delay=60,
    retryable_exceptions=(ConnectionError, TimeoutError)
):
    for attempt in range(max_retries):
        try:
            return func()
        except retryable_exceptions as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise

            # Calculate delay with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay)

            print(f"Attempt {attempt + 1} failed, retrying in {jitter:.2f}s")
            time.sleep(jitter)

# Usage
result = retry_with_backoff(lambda: api_call())
```

### Best Practices

1. **Set max retries** (typically 3-5)
2. **Cap max delay** (30-60 seconds)
3. **Always use jitter** to prevent thundering herd
4. **Make operations idempotent** before retrying
5. **Log retry attempts** for debugging
6. **Combine with circuit breaker** for complete resilience

---

## Otvet (RU)

**Стратегии повторных попыток** помогают системам восстанавливаться от временных сбоев путем автоматического повтора неудачных операций.

### Когда повторять

**Повторять при временных сбоях:**
- Таймауты сети
- 503 Service Unavailable
- 429 Too Many Requests
- Connection refused (временный)

**Не повторять при:**
- 400 Bad Request (ошибка клиента)
- 401/403 ошибки аутентификации/авторизации
- 404 Not Found
- Ошибки бизнес-логики

### Основные стратегии повтора

**1. Немедленный повтор**
```
Попытка 1 → Сбой → Попытка 2 → Сбой → Попытка 3
                Без задержки между повторами
```
Проблема: Может перегрузить уже страдающий сервис

**2. Фиксированная задержка**
```
Попытка 1 → [2с] → Попытка 2 → [2с] → Попытка 3
           Фиксированная задержка между попытками
```
Лучше, но все еще синхронизированная нагрузка

**3. Экспоненциальная задержка**
```
Попытка 1 → [1с] → Попытка 2 → [2с] → Попытка 3 → [4с] → Попытка 4
           Задержка удваивается каждую попытку
```

```python
def exponential_backoff(attempt, base_delay=1, max_delay=60):
    delay = min(base_delay * (2 ** attempt), max_delay)
    return delay

# Попытка 0: 1с, 1: 2с, 2: 4с, 3: 8с, 4: 16с, 5: 32с, 6+: 60с (ограничено)
```

**4. Экспоненциальная задержка с Jitter**
```python
def exponential_backoff_with_jitter(attempt, base_delay=1, max_delay=60):
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay)  # Добавляем случайность
    return jitter

# Full jitter: случайное между 0 и вычисленной задержкой
```

### Почему Jitter важен

**Проблема: Thundering Herd (эффект толпы)**
```
Сервис падает в T=0
1000 клиентов повторяют в T=1с (exponential backoff)
1000 клиентов повторяют в T=2с
... синхронизированные волны запросов
```

**Решение: Jitter распределяет нагрузку**
```
Сервис падает в T=0
Клиент A повторяет в T=0.7с
Клиент B повторяет в T=1.3с
Клиент C повторяет в T=0.9с
... распределенное время повторов
```

### Стратегии Jitter

| Стратегия | Формула | Применение |
|-----------|---------|------------|
| Full jitter | random(0, delay) | Самая распространенная |
| Equal jitter | delay/2 + random(0, delay/2) | Гарантия минимальной задержки |
| Decorrelated | min(max, random(base, prev*3)) | Рекомендация AWS |

### Пример реализации

```python
import time
import random

def retry_with_backoff(
    func,
    max_retries=5,
    base_delay=1,
    max_delay=60,
    retryable_exceptions=(ConnectionError, TimeoutError)
):
    for attempt in range(max_retries):
        try:
            return func()
        except retryable_exceptions as e:
            if attempt == max_retries - 1:
                raise  # Последняя попытка, пробросить

            # Вычисляем задержку с jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay)

            print(f"Попытка {attempt + 1} не удалась, повтор через {jitter:.2f}с")
            time.sleep(jitter)

# Использование
result = retry_with_backoff(lambda: api_call())
```

### Лучшие практики

1. **Установите макс. попыток** (обычно 3-5)
2. **Ограничьте макс. задержку** (30-60 секунд)
3. **Всегда используйте jitter** для предотвращения thundering herd
4. **Сделайте операции идемпотентными** перед повтором
5. **Логируйте попытки** для отладки
6. **Комбинируйте с circuit breaker** для полной отказоустойчивости

---

## Follow-ups

- How do you handle non-idempotent operations with retries?
- What is the AWS decorrelated jitter formula?
- How do you implement retry budgets?

## Related Questions

### Prerequisites (Easier)
- [[q-idempotency--system-design--medium]] - Idempotency

### Related (Same Level)
- [[q-circuit-breaker-pattern--system-design--medium]] - Circuit breaker
- [[q-failover-strategies--system-design--medium]] - Failover

### Advanced (Harder)
- [[q-design-notification-system--system-design--hard]] - System design

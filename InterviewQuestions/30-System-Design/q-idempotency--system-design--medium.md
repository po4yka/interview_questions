---
id: sysdes-014
title: Idempotency in Distributed Systems
aliases:
- Idempotent Operations
- Idempotency Key
topic: system-design
subtopics:
- distributed-systems
- api-design
- reliability
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-rest-api-design-best-practices--system-design--medium
- q-retry-strategies--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- distributed-systems
- difficulty/medium
- api-design
- system-design
anki_cards:
- slug: sysdes-014-0-en
  language: en
  anki_id: 1769158891391
  synced_at: '2026-01-23T13:49:17.840691'
- slug: sysdes-014-0-ru
  language: ru
  anki_id: 1769158891416
  synced_at: '2026-01-23T13:49:17.841851'
---
# Question (EN)
> What is idempotency? Why is it important in distributed systems, and how do you implement idempotent APIs?

# Vopros (RU)
> Что такое идемпотентность? Почему она важна в распределенных системах и как реализовать идемпотентные API?

---

## Answer (EN)

**Idempotency** means performing the same operation multiple times produces the same result as performing it once.

### Why Idempotency Matters

In distributed systems, requests can fail and be retried:
- Network timeouts
- Server crashes after processing but before responding
- Client retries due to uncertainty

Without idempotency, retries can cause:
- Duplicate payments
- Double inventory deductions
- Multiple notifications sent

### HTTP Methods and Idempotency

| Method | Idempotent | Safe | Notes |
|--------|------------|------|-------|
| GET | Yes | Yes | Read-only |
| HEAD | Yes | Yes | Read-only |
| PUT | Yes | No | Full replacement |
| DELETE | Yes | No | Same result if already deleted |
| POST | **No** | No | Creates new resource each time |
| PATCH | **No** | No | Partial update may not be idempotent |

### Implementing Idempotency

**1. Idempotency Key Pattern**

Client sends unique key with request; server deduplicates.

```python
# Client
headers = {"Idempotency-Key": "uuid-123-456"}
response = post("/payments", data=payment, headers=headers)

# Server
def create_payment(request):
    key = request.headers["Idempotency-Key"]

    # Check if already processed
    existing = cache.get(f"idempotency:{key}")
    if existing:
        return existing  # Return cached response

    # Process payment
    result = process_payment(request.data)

    # Cache result with TTL
    cache.set(f"idempotency:{key}", result, ttl=24h)
    return result
```

**2. Database Constraints**

Use unique constraints to prevent duplicates.

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    idempotency_key VARCHAR(255) UNIQUE,
    amount DECIMAL,
    status VARCHAR(50)
);

-- Insert will fail on duplicate key
INSERT INTO payments (id, idempotency_key, amount, status)
VALUES (gen_uuid(), 'client-key-123', 100.00, 'pending');
```

**3. Conditional Operations**

Use version checks or ETags.

```http
PUT /users/123
If-Match: "etag-abc123"
Content-Type: application/json

{"name": "John"}
```

### Best Practices

1. **Generate idempotency keys client-side** (UUIDs)
2. **Store results for 24-48 hours** (covers retry windows)
3. **Return same response** for duplicate requests (including errors)
4. **Use atomic operations** in database
5. **Document idempotency behavior** in API

---

## Otvet (RU)

**Идемпотентность** означает, что выполнение одной операции несколько раз дает тот же результат, что и однократное выполнение.

### Почему идемпотентность важна

В распределенных системах запросы могут упасть и быть повторены:
- Таймауты сети
- Падение сервера после обработки, но до ответа
- Повторы клиента из-за неопределенности

Без идемпотентности повторы могут вызвать:
- Дублирование платежей
- Двойное списание товаров
- Множественные уведомления

### HTTP методы и идемпотентность

| Метод | Идемпотентный | Безопасный | Примечания |
|-------|---------------|------------|------------|
| GET | Да | Да | Только чтение |
| HEAD | Да | Да | Только чтение |
| PUT | Да | Нет | Полная замена |
| DELETE | Да | Нет | Тот же результат если уже удален |
| POST | **Нет** | Нет | Создает новый ресурс каждый раз |
| PATCH | **Нет** | Нет | Частичное обновление может быть неидемпотентным |

### Реализация идемпотентности

**1. Паттерн Idempotency Key**

Клиент отправляет уникальный ключ с запросом; сервер дедуплицирует.

```python
# Клиент
headers = {"Idempotency-Key": "uuid-123-456"}
response = post("/payments", data=payment, headers=headers)

# Сервер
def create_payment(request):
    key = request.headers["Idempotency-Key"]

    # Проверяем, обработан ли уже
    existing = cache.get(f"idempotency:{key}")
    if existing:
        return existing  # Возвращаем закешированный ответ

    # Обрабатываем платеж
    result = process_payment(request.data)

    # Кешируем результат с TTL
    cache.set(f"idempotency:{key}", result, ttl=24h)
    return result
```

**2. Ограничения базы данных**

Используем уникальные ограничения для предотвращения дубликатов.

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    idempotency_key VARCHAR(255) UNIQUE,
    amount DECIMAL,
    status VARCHAR(50)
);

-- INSERT упадет на дубликате ключа
INSERT INTO payments (id, idempotency_key, amount, status)
VALUES (gen_uuid(), 'client-key-123', 100.00, 'pending');
```

**3. Условные операции**

Используем проверку версий или ETags.

```http
PUT /users/123
If-Match: "etag-abc123"
Content-Type: application/json

{"name": "John"}
```

### Лучшие практики

1. **Генерируйте idempotency keys на клиенте** (UUID)
2. **Храните результаты 24-48 часов** (покрывает окно ретраев)
3. **Возвращайте тот же ответ** для дублирующих запросов (включая ошибки)
4. **Используйте атомарные операции** в базе данных
5. **Документируйте поведение идемпотентности** в API

---

## Follow-ups

- How do you handle idempotency for operations that depend on external services?
- What happens if the idempotency key store fails?
- How does Stripe implement idempotency?

## Related Questions

### Prerequisites (Easier)
- [[q-rest-api-design-best-practices--system-design--medium]] - REST API design

### Related (Same Level)
- [[q-retry-strategies--system-design--medium]] - Retry patterns
- [[q-circuit-breaker-pattern--system-design--medium]] - Circuit breaker

### Advanced (Harder)
- [[q-saga-pattern--system-design--hard]] - Distributed transactions

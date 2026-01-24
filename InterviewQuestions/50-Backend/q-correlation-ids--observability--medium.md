---
id: be-obs-002
title: Correlation IDs / Идентификаторы корреляции
aliases: []
topic: observability
subtopics:
- tracing
- distributed-systems
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Backend interview preparation
status: draft
moc: moc-backend
related:
- c-observability
- c-tracing
created: 2025-01-23
updated: 2025-01-23
tags:
- observability
- tracing
- distributed-systems
- difficulty/medium
- topic/observability
anki_cards:
- slug: be-obs-002-0-en
  language: en
  anki_id: 1769167240756
  synced_at: '2026-01-23T15:20:42.988750'
- slug: be-obs-002-0-ru
  language: ru
  anki_id: 1769167240781
  synced_at: '2026-01-23T15:20:42.990655'
---
# Question (EN)
> What are correlation IDs and how to implement request tracing?

# Vopros (RU)
> Что такое идентификаторы корреляции и как реализовать трассировку запросов?

---

## Answer (EN)

**Correlation ID (Request ID)** - A unique identifier that follows a request through all services and components, enabling end-to-end tracing.

**Problem Without Correlation ID:**
```
Service A: Processing request...
Service B: User not found
Service A: Request completed
Service C: Error connecting to database
```
Which logs belong to which request?

**With Correlation ID:**
```
[req-abc-123] Service A: Processing request...
[req-abc-123] Service B: User not found
[req-abc-123] Service A: Request completed
[req-xyz-456] Service C: Error connecting to database
```

---

**Implementation:**

**1. Generate at Entry Point:**
```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Use existing header or generate new
    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )

    # Store in request state
    request.state.correlation_id = correlation_id

    # Process request
    response = await call_next(request)

    # Add to response headers
    response.headers["X-Correlation-ID"] = correlation_id

    return response
```

**2. Include in Logs:**
```python
import structlog
from contextvars import ContextVar

# Thread-safe context variable
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

def add_correlation_id(logger, method_name, event_dict):
    event_dict["correlation_id"] = correlation_id_var.get()
    return event_dict

structlog.configure(
    processors=[
        add_correlation_id,
        structlog.processors.JSONRenderer()
    ]
)
```

**3. Propagate to Other Services:**
```python
import httpx

async def call_downstream_service(data: dict):
    correlation_id = correlation_id_var.get()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://service-b/api/process",
            json=data,
            headers={"X-Correlation-ID": correlation_id}
        )
    return response
```

---

**Headers Convention:**

| Header | Purpose |
|--------|---------|
| `X-Correlation-ID` | Single request identifier |
| `X-Request-ID` | Alternative name |
| `traceparent` | W3C Trace Context standard |

**W3C Trace Context:**
```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
             ^  ^                                ^                ^
             |  |                                |                |
          version  trace-id                  span-id            flags
```

---

**Complete Flow:**

```
1. Client -> API Gateway
   Generate: X-Correlation-ID: abc-123

2. API Gateway -> Service A
   Forward: X-Correlation-ID: abc-123

3. Service A -> Service B
   Forward: X-Correlation-ID: abc-123

4. All logs contain correlation_id: abc-123

5. Response to client includes X-Correlation-ID: abc-123
```

**Querying Logs:**
```
# Find all logs for a request
correlation_id:"abc-123"

# Find errors for this request
correlation_id:"abc-123" AND level:ERROR
```

**Best Practices:**
- Generate UUID v4 for uniqueness
- Use middleware for automatic handling
- Include in all log messages
- Propagate to all downstream calls
- Return in response for client debugging

## Otvet (RU)

**Correlation ID (Request ID)** - Уникальный идентификатор, который следует за запросом через все сервисы и компоненты, обеспечивая сквозную трассировку.

**Проблема без Correlation ID:**
```
Service A: Processing request...
Service B: User not found
Service A: Request completed
Service C: Error connecting to database
```
Какие логи относятся к какому запросу?

**С Correlation ID:**
```
[req-abc-123] Service A: Processing request...
[req-abc-123] Service B: User not found
[req-abc-123] Service A: Request completed
[req-xyz-456] Service C: Error connecting to database
```

---

**Реализация:**

**1. Генерация на точке входа:**
```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Используем существующий заголовок или генерируем новый
    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )

    # Сохраняем в состоянии запроса
    request.state.correlation_id = correlation_id

    # Обрабатываем запрос
    response = await call_next(request)

    # Добавляем в заголовки ответа
    response.headers["X-Correlation-ID"] = correlation_id

    return response
```

**2. Включение в логи:**
```python
import structlog
from contextvars import ContextVar

# Потокобезопасная контекстная переменная
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

def add_correlation_id(logger, method_name, event_dict):
    event_dict["correlation_id"] = correlation_id_var.get()
    return event_dict

structlog.configure(
    processors=[
        add_correlation_id,
        structlog.processors.JSONRenderer()
    ]
)
```

**3. Передача в другие сервисы:**
```python
import httpx

async def call_downstream_service(data: dict):
    correlation_id = correlation_id_var.get()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://service-b/api/process",
            json=data,
            headers={"X-Correlation-ID": correlation_id}
        )
    return response
```

---

**Соглашение о заголовках:**

| Заголовок | Назначение |
|-----------|------------|
| `X-Correlation-ID` | Идентификатор одного запроса |
| `X-Request-ID` | Альтернативное название |
| `traceparent` | Стандарт W3C Trace Context |

**W3C Trace Context:**
```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
             ^  ^                                ^                ^
             |  |                                |                |
          version  trace-id                  span-id            flags
```

---

**Полный поток:**

```
1. Клиент -> API Gateway
   Генерация: X-Correlation-ID: abc-123

2. API Gateway -> Service A
   Передача: X-Correlation-ID: abc-123

3. Service A -> Service B
   Передача: X-Correlation-ID: abc-123

4. Все логи содержат correlation_id: abc-123

5. Ответ клиенту включает X-Correlation-ID: abc-123
```

**Запросы к логам:**
```
# Найти все логи для запроса
correlation_id:"abc-123"

# Найти ошибки для этого запроса
correlation_id:"abc-123" AND level:ERROR
```

**Лучшие практики:**
- Генерируйте UUID v4 для уникальности
- Используйте middleware для автоматической обработки
- Включайте во все сообщения логов
- Передавайте во все downstream-вызовы
- Возвращайте в ответе для отладки клиентом

---

## Follow-ups
- What is distributed tracing (OpenTelemetry)?
- How to implement tracing in message queues?
- What is the difference between correlation ID and span ID?

## Dopolnitelnye voprosy (RU)
- Что такое распределённая трассировка (OpenTelemetry)?
- Как реализовать трассировку в очередях сообщений?
- В чём разница между correlation ID и span ID?

## References
- [[c-observability]]
- [[c-tracing]]
- [[moc-backend]]

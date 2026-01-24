---
id: be-pat-003
title: Middleware Pipeline / Конвейер промежуточного ПО
aliases: []
topic: patterns
subtopics:
- middleware
- http
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
- c-patterns
- c-http
created: 2025-01-23
updated: 2025-01-23
tags:
- patterns
- middleware
- http
- difficulty/medium
- topic/patterns
anki_cards:
- slug: be-pat-003-0-en
  language: en
  anki_id: 1769167241776
  synced_at: '2026-01-23T15:20:43.031125'
- slug: be-pat-003-0-ru
  language: ru
  anki_id: 1769167241817
  synced_at: '2026-01-23T15:20:43.033273'
---
# Question (EN)
> What is middleware in web frameworks and how does the pipeline work?

# Vopros (RU)
> Что такое middleware в веб-фреймворках и как работает конвейер?

---

## Answer (EN)

**Middleware** - Functions that intercept and process HTTP requests/responses in a chain (pipeline). Each middleware can:
- Process/modify request before handler
- Process/modify response after handler
- Short-circuit the pipeline (e.g., return error)

---

**Pipeline Flow:**

```
Request -> [Auth] -> [Logging] -> [CORS] -> [Handler] -> Response
              |          |          |          |
              v          v          v          v
           Pre-processing       Post-processing
```

**Onion Model:**
```
Request  ─────────────────────────────────>
         │ Middleware 1                   │
         │   │ Middleware 2               │
         │   │   │ Middleware 3           │
         │   │   │   │ Handler            │
         │   │   │   │   │                │
         │   │   │   │   v                │
         │   │   │   │ Response           │
         │   │   │ <─────────────────────│
         │   │ <──────────────────────────│
         │ <───────────────────────────────│
Response <─────────────────────────────────
```

---

**Implementation Examples:**

**Express.js:**
```javascript
// Middleware function
const authMiddleware = (req, res, next) => {
    const token = req.headers.authorization;
    if (!token) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    req.user = verifyToken(token);
    next();  // Pass to next middleware
};

// Apply middleware
app.use(authMiddleware);
app.get('/protected', (req, res) => {
    res.json({ user: req.user });
});
```

**FastAPI (Starlette):**
```python
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Before request
        start_time = time.time()

        # Call next middleware/handler
        response = await call_next(request)

        # After response
        duration = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {duration:.3f}s")

        return response

app.add_middleware(LoggingMiddleware)
```

**Django:**
```python
class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)  # Call next
        duration = time.time() - start
        response['X-Response-Time'] = f"{duration:.3f}s"
        return response
```

---

**Common Middleware Types:**

| Middleware | Purpose |
|------------|---------|
| Authentication | Verify identity |
| Authorization | Check permissions |
| Logging | Request/response logging |
| CORS | Cross-origin headers |
| Rate Limiting | Throttle requests |
| Compression | gzip response |
| Error Handling | Global exception handling |
| Request ID | Add correlation ID |
| Body Parsing | Parse JSON/form data |

**Order Matters:**
```python
# Correct order
app.add_middleware(CORSMiddleware)      # CORS first
app.add_middleware(AuthMiddleware)      # Then auth
app.add_middleware(LoggingMiddleware)   # Log authenticated requests
```

## Otvet (RU)

**Middleware** - Функции, которые перехватывают и обрабатывают HTTP-запросы/ответы в цепочке (конвейер). Каждый middleware может:
- Обработать/модифицировать запрос до обработчика
- Обработать/модифицировать ответ после обработчика
- Прервать конвейер (например, вернуть ошибку)

---

**Поток конвейера:**

```
Request -> [Auth] -> [Logging] -> [CORS] -> [Handler] -> Response
              |          |          |          |
              v          v          v          v
           Pre-processing       Post-processing
```

**Модель луковицы:**
```
Request  ─────────────────────────────────>
         │ Middleware 1                   │
         │   │ Middleware 2               │
         │   │   │ Middleware 3           │
         │   │   │   │ Handler            │
         │   │   │   │   │                │
         │   │   │   │   v                │
         │   │   │   │ Response           │
         │   │   │ <─────────────────────│
         │   │ <──────────────────────────│
         │ <───────────────────────────────│
Response <─────────────────────────────────
```

---

**Примеры реализации:**

**Express.js:**
```javascript
// Функция middleware
const authMiddleware = (req, res, next) => {
    const token = req.headers.authorization;
    if (!token) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    req.user = verifyToken(token);
    next();  // Передать следующему middleware
};

// Применение middleware
app.use(authMiddleware);
app.get('/protected', (req, res) => {
    res.json({ user: req.user });
});
```

**FastAPI (Starlette):**
```python
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # До запроса
        start_time = time.time()

        # Вызов следующего middleware/обработчика
        response = await call_next(request)

        # После ответа
        duration = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {duration:.3f}s")

        return response

app.add_middleware(LoggingMiddleware)
```

**Django:**
```python
class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)  # Вызов следующего
        duration = time.time() - start
        response['X-Response-Time'] = f"{duration:.3f}s"
        return response
```

---

**Типичные виды Middleware:**

| Middleware | Назначение |
|------------|------------|
| Authentication | Проверка идентичности |
| Authorization | Проверка прав |
| Logging | Логирование запросов/ответов |
| CORS | Cross-origin заголовки |
| Rate Limiting | Ограничение запросов |
| Compression | gzip-сжатие ответа |
| Error Handling | Глобальная обработка исключений |
| Request ID | Добавление correlation ID |
| Body Parsing | Парсинг JSON/form данных |

**Порядок важен:**
```python
# Правильный порядок
app.add_middleware(CORSMiddleware)      # CORS первым
app.add_middleware(AuthMiddleware)      # Потом auth
app.add_middleware(LoggingMiddleware)   # Логируем аутентифицированные запросы
```

---

## Follow-ups
- How does middleware differ from decorators?
- What is the chain of responsibility pattern?
- How to handle async operations in middleware?

## Dopolnitelnye voprosy (RU)
- Чем middleware отличается от декораторов?
- Что такое паттерн цепочка обязанностей?
- Как обрабатывать асинхронные операции в middleware?

## References
- [[c-patterns]]
- [[c-http]]
- [[moc-backend]]

---
id: be-pat-006
title: Exception Handling in APIs / Обработка исключений в API
aliases: []
topic: patterns
subtopics:
- error-handling
- api
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
- c-api
created: 2025-01-23
updated: 2025-01-23
tags:
- patterns
- error-handling
- api
- difficulty/medium
- topic/patterns
anki_cards:
- slug: be-pat-006-0-en
  language: en
  anki_id: 1769167241180
  synced_at: '2026-01-23T15:20:43.007187'
- slug: be-pat-006-0-ru
  language: ru
  anki_id: 1769167241237
  synced_at: '2026-01-23T15:20:43.008835'
---
# Question (EN)
> How should exceptions be handled in REST APIs?

# Vopros (RU)
> Как следует обрабатывать исключения в REST API?

---

## Answer (EN)

**Error Handling Strategy:**

1. Use exceptions for exceptional cases
2. Catch and convert to appropriate HTTP responses
3. Never expose internal details to client
4. Log full details server-side
5. Return consistent error format

---

**Error Response Format (RFC 7807 Problem Details):**

```json
{
    "type": "https://api.example.com/errors/validation",
    "title": "Validation Error",
    "status": 400,
    "detail": "The request body contains invalid data",
    "instance": "/users/123",
    "errors": [
        {"field": "email", "message": "Invalid email format"},
        {"field": "age", "message": "Must be positive integer"}
    ],
    "traceId": "abc123"
}
```

---

**Exception Hierarchy:**

```python
# Base exception
class AppException(Exception):
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code

# Client errors (4xx)
class BadRequestError(AppException):
    status_code = 400

class NotFoundError(AppException):
    status_code = 404

class ValidationError(BadRequestError):
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__("Validation failed")

class UnauthorizedError(AppException):
    status_code = 401

class ForbiddenError(AppException):
    status_code = 403

# Server errors (5xx)
class InternalError(AppException):
    status_code = 500
```

---

**Global Exception Handler (FastAPI):**

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "type": "validation_error",
            "title": "Validation Error",
            "status": 400,
            "errors": exc.errors
        }
    )

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "type": "not_found",
            "title": "Not Found",
            "status": 404,
            "detail": exc.message
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log full error (server-side only)
    logger.exception("Unhandled exception", exc_info=exc)

    # Return generic message (no internal details!)
    return JSONResponse(
        status_code=500,
        content={
            "type": "internal_error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred"
        }
    )
```

---

**HTTP Status Code Usage:**

| Code | Meaning | When to Use |
|------|---------|-------------|
| 400 | Bad Request | Invalid input, validation errors |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate, state conflict |
| 422 | Unprocessable | Semantic validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Error | Unexpected server error |
| 503 | Service Unavailable | Maintenance, overload |

**Best Practices:**
- Include correlation/trace ID for debugging
- Use structured logging
- Separate client-safe and internal messages
- Document error codes in API docs

## Otvet (RU)

**Стратегия обработки ошибок:**

1. Используйте исключения для исключительных случаев
2. Перехватывайте и конвертируйте в HTTP-ответы
3. Никогда не раскрывайте внутренние детали клиенту
4. Логируйте полные детали на сервере
5. Возвращайте единообразный формат ошибок

---

**Формат ответа об ошибке (RFC 7807 Problem Details):**

```json
{
    "type": "https://api.example.com/errors/validation",
    "title": "Validation Error",
    "status": 400,
    "detail": "The request body contains invalid data",
    "instance": "/users/123",
    "errors": [
        {"field": "email", "message": "Invalid email format"},
        {"field": "age", "message": "Must be positive integer"}
    ],
    "traceId": "abc123"
}
```

---

**Иерархия исключений:**

```python
# Базовое исключение
class AppException(Exception):
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code

# Клиентские ошибки (4xx)
class BadRequestError(AppException):
    status_code = 400

class NotFoundError(AppException):
    status_code = 404

class ValidationError(BadRequestError):
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__("Validation failed")

class UnauthorizedError(AppException):
    status_code = 401

class ForbiddenError(AppException):
    status_code = 403

# Серверные ошибки (5xx)
class InternalError(AppException):
    status_code = 500
```

---

**Глобальный обработчик исключений (FastAPI):**

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "type": "validation_error",
            "title": "Validation Error",
            "status": 400,
            "errors": exc.errors
        }
    )

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "type": "not_found",
            "title": "Not Found",
            "status": 404,
            "detail": exc.message
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Логируем полную ошибку (только на сервере)
    logger.exception("Unhandled exception", exc_info=exc)

    # Возвращаем общее сообщение (без внутренних деталей!)
    return JSONResponse(
        status_code=500,
        content={
            "type": "internal_error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred"
        }
    )
```

---

**Использование HTTP-кодов статуса:**

| Код | Значение | Когда использовать |
|-----|----------|-------------------|
| 400 | Bad Request | Невалидный ввод, ошибки валидации |
| 401 | Unauthorized | Отсутствует/невалидная аутентификация |
| 403 | Forbidden | Аутентифицирован, но не авторизован |
| 404 | Not Found | Ресурс не существует |
| 409 | Conflict | Дубликат, конфликт состояния |
| 422 | Unprocessable | Семантическая ошибка валидации |
| 429 | Too Many Requests | Превышен лимит запросов |
| 500 | Internal Error | Неожиданная ошибка сервера |
| 503 | Service Unavailable | Обслуживание, перегрузка |

**Лучшие практики:**
- Включайте correlation/trace ID для отладки
- Используйте структурированное логирование
- Разделяйте сообщения для клиента и внутренние
- Документируйте коды ошибок в API-документации

---

## Follow-ups
- What is the difference between 400 and 422 status codes?
- How to handle validation errors in GraphQL?
- What is the Result pattern for error handling?

## Dopolnitelnye voprosy (RU)
- В чём разница между кодами статуса 400 и 422?
- Как обрабатывать ошибки валидации в GraphQL?
- Что такое паттерн Result для обработки ошибок?

## References
- [[c-patterns]]
- [[c-api]]
- [[moc-backend]]

---
id: be-pat-005
title: HTTP Request Lifecycle / Жизненный цикл HTTP-запроса
aliases: []
topic: patterns
subtopics:
- http
- request-lifecycle
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
- c-http
- c-patterns
created: 2025-01-23
updated: 2025-01-23
tags:
- http
- request-lifecycle
- patterns
- difficulty/medium
- topic/patterns
anki_cards:
- slug: be-pat-005-0-en
  language: en
  anki_id: 1769167241282
  synced_at: '2026-01-23T15:20:43.010931'
- slug: be-pat-005-0-ru
  language: ru
  anki_id: 1769167241330
  synced_at: '2026-01-23T15:20:43.013361'
---
# Question (EN)
> What is the lifecycle of an HTTP request in a web framework?

# Vopros (RU)
> Каков жизненный цикл HTTP-запроса в веб-фреймворке?

---

## Answer (EN)

**Complete Request Lifecycle:**

```
1. Client sends HTTP request
        |
        v
2. Web Server (nginx/gunicorn) receives request
        |
        v
3. WSGI/ASGI interface passes to application
        |
        v
4. Framework entry point
        |
        v
5. Middleware chain (pre-processing)
        |
        v
6. Router matches URL to handler
        |
        v
7. Parameter extraction & validation
        |
        v
8. Handler/Controller executes
        |
        v
9. Business logic / Service layer
        |
        v
10. Response serialization
        |
        v
11. Middleware chain (post-processing)
        |
        v
12. HTTP Response sent to client
```

---

**Detailed Stages:**

**1-3. Server Layer:**
```
Browser -> DNS -> TCP/TLS -> Load Balancer -> Web Server -> App Server
```

**4-5. Framework Entry & Middleware:**
```python
# FastAPI/Starlette example
async def app(scope, receive, send):
    # Middleware 1: Logging
    # Middleware 2: CORS
    # Middleware 3: Auth
    ...
```

**6. Routing:**
```python
# Match URL pattern to handler
@app.get("/users/{user_id}")  # Route definition
def get_user(user_id: int):   # Matched handler
    ...
```

**7. Parameter Processing:**
```python
# Path parameters
user_id = int(request.match_info['user_id'])

# Query parameters
limit = request.query_params.get('limit', 10)

# Body parsing
data = await request.json()

# Validation (Pydantic)
user = UserSchema(**data)
```

**8-9. Handler Execution:**
```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)  # Dependency injection
):
    # Call service layer
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

**10. Response Serialization:**
```python
# Object -> JSON
return JSONResponse(
    status_code=200,
    content={"id": user.id, "name": user.name},
    headers={"X-Custom": "value"}
)
```

---

**Request Context:**
```python
# Data available throughout request lifecycle
- request.headers
- request.cookies
- request.query_params
- request.path_params
- request.body
- request.state  # Custom data (e.g., user, db session)
```

**Response Building:**
```python
# Status code
response.status_code = 200

# Headers
response.headers["Content-Type"] = "application/json"
response.headers["Cache-Control"] = "max-age=3600"

# Cookies
response.set_cookie("session", token, httponly=True)

# Body
response.body = json.dumps(data)
```

## Otvet (RU)

**Полный жизненный цикл запроса:**

```
1. Клиент отправляет HTTP-запрос
        |
        v
2. Веб-сервер (nginx/gunicorn) получает запрос
        |
        v
3. WSGI/ASGI интерфейс передаёт приложению
        |
        v
4. Точка входа фреймворка
        |
        v
5. Цепочка middleware (предобработка)
        |
        v
6. Роутер сопоставляет URL с обработчиком
        |
        v
7. Извлечение и валидация параметров
        |
        v
8. Выполнение обработчика/контроллера
        |
        v
9. Бизнес-логика / Сервисный слой
        |
        v
10. Сериализация ответа
        |
        v
11. Цепочка middleware (постобработка)
        |
        v
12. HTTP-ответ отправлен клиенту
```

---

**Детальные этапы:**

**1-3. Серверный слой:**
```
Браузер -> DNS -> TCP/TLS -> Load Balancer -> Веб-сервер -> App Server
```

**4-5. Вход в фреймворк и Middleware:**
```python
# Пример FastAPI/Starlette
async def app(scope, receive, send):
    # Middleware 1: Логирование
    # Middleware 2: CORS
    # Middleware 3: Auth
    ...
```

**6. Маршрутизация:**
```python
# Сопоставление URL-паттерна с обработчиком
@app.get("/users/{user_id}")  # Определение маршрута
def get_user(user_id: int):   # Сопоставленный обработчик
    ...
```

**7. Обработка параметров:**
```python
# Path-параметры
user_id = int(request.match_info['user_id'])

# Query-параметры
limit = request.query_params.get('limit', 10)

# Парсинг body
data = await request.json()

# Валидация (Pydantic)
user = UserSchema(**data)
```

**8-9. Выполнение обработчика:**
```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)  # Внедрение зависимостей
):
    # Вызов сервисного слоя
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

**10. Сериализация ответа:**
```python
# Объект -> JSON
return JSONResponse(
    status_code=200,
    content={"id": user.id, "name": user.name},
    headers={"X-Custom": "value"}
)
```

---

**Контекст запроса:**
```python
# Данные, доступные на протяжении жизненного цикла запроса
- request.headers
- request.cookies
- request.query_params
- request.path_params
- request.body
- request.state  # Кастомные данные (user, db session)
```

**Формирование ответа:**
```python
# Код статуса
response.status_code = 200

# Заголовки
response.headers["Content-Type"] = "application/json"
response.headers["Cache-Control"] = "max-age=3600"

# Cookies
response.set_cookie("session", token, httponly=True)

# Тело
response.body = json.dumps(data)
```

---

## Follow-ups
- What is the difference between WSGI and ASGI?
- How does request context work in async frameworks?
- What happens when an exception is raised during the lifecycle?

## Dopolnitelnye voprosy (RU)
- В чём разница между WSGI и ASGI?
- Как работает контекст запроса в async-фреймворках?
- Что происходит, когда во время жизненного цикла выбрасывается исключение?

## References
- [[c-http]]
- [[c-patterns]]
- [[moc-backend]]

---
id: be-api-002
title: OpenAPI and Swagger / OpenAPI и Swagger
aliases: []
topic: api
subtopics:
- openapi
- documentation
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
- c-api
- c-documentation
created: 2025-01-23
updated: 2025-01-23
tags:
- api
- openapi
- documentation
- difficulty/medium
- topic/api
anki_cards:
- slug: be-api-002-0-en
  language: en
  anki_id: 1769167239480
  synced_at: '2026-01-23T15:20:42.926401'
- slug: be-api-002-0-ru
  language: ru
  anki_id: 1769167239505
  synced_at: '2026-01-23T15:20:42.928294'
---
# Question (EN)
> What is OpenAPI (Swagger) and how is it used for API documentation?

# Vopros (RU)
> Что такое OpenAPI (Swagger) и как он используется для документирования API?

---

## Answer (EN)

**OpenAPI Specification (OAS)** - A standard format for describing REST APIs. **Swagger** is the original name and now refers to tooling around OpenAPI.

**Benefits:**
- Machine-readable API documentation
- Auto-generate client SDKs
- Interactive API testing
- Contract-first design
- Validation and mocking

---

**OpenAPI Document Structure:**

```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0
  description: API for managing users

servers:
  - url: https://api.example.com/v1

paths:
  /users:
    get:
      summary: List all users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

    post:
      summary: Create a user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        email:
          type: string
          format: email
        name:
          type: string
      required:
        - id
        - email

    CreateUser:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        password:
          type: string
          minLength: 8
      required:
        - email
        - password
```

---

**FastAPI Auto-Generation:**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="User API",
    version="1.0.0",
    description="API for managing users"
)

class User(BaseModel):
    id: int
    email: str
    name: str

class CreateUser(BaseModel):
    email: str
    name: str
    password: str

@app.get("/users", response_model=list[User])
def list_users(limit: int = 10):
    """List all users with pagination."""
    ...

@app.post("/users", response_model=User, status_code=201)
def create_user(user: CreateUser):
    """Create a new user."""
    ...

# OpenAPI available at /openapi.json
# Swagger UI at /docs
# ReDoc at /redoc
```

---

**Swagger Tools:**

| Tool | Purpose |
|------|---------|
| Swagger UI | Interactive documentation |
| Swagger Editor | Write/edit OpenAPI specs |
| Swagger Codegen | Generate client SDKs |
| ReDoc | Alternative doc viewer |

**Use Cases:**

| Approach | When to Use |
|----------|-------------|
| Code-first | Framework generates spec (FastAPI) |
| Spec-first | Design API before coding |
| Contract testing | Validate API matches spec |

## Otvet (RU)

**OpenAPI Specification (OAS)** - Стандартный формат для описания REST API. **Swagger** - изначальное название, теперь относится к инструментарию вокруг OpenAPI.

**Преимущества:**
- Машиночитаемая документация API
- Автогенерация клиентских SDK
- Интерактивное тестирование API
- Contract-first дизайн
- Валидация и мокирование

---

**Структура документа OpenAPI:**

```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0
  description: API для управления пользователями

servers:
  - url: https://api.example.com/v1

paths:
  /users:
    get:
      summary: Список всех пользователей
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Успешный ответ
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

    post:
      summary: Создать пользователя
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
      responses:
        '201':
          description: Пользователь создан
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        email:
          type: string
          format: email
        name:
          type: string
      required:
        - id
        - email

    CreateUser:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        password:
          type: string
          minLength: 8
      required:
        - email
        - password
```

---

**Автогенерация в FastAPI:**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="User API",
    version="1.0.0",
    description="API для управления пользователями"
)

class User(BaseModel):
    id: int
    email: str
    name: str

class CreateUser(BaseModel):
    email: str
    name: str
    password: str

@app.get("/users", response_model=list[User])
def list_users(limit: int = 10):
    """Список всех пользователей с пагинацией."""
    ...

@app.post("/users", response_model=User, status_code=201)
def create_user(user: CreateUser):
    """Создать нового пользователя."""
    ...

# OpenAPI доступен по /openapi.json
# Swagger UI по /docs
# ReDoc по /redoc
```

---

**Инструменты Swagger:**

| Инструмент | Назначение |
|------------|------------|
| Swagger UI | Интерактивная документация |
| Swagger Editor | Написание/редактирование OpenAPI-спецификаций |
| Swagger Codegen | Генерация клиентских SDK |
| ReDoc | Альтернативный просмотрщик документации |

**Сценарии использования:**

| Подход | Когда использовать |
|--------|-------------------|
| Code-first | Фреймворк генерирует спецификацию (FastAPI) |
| Spec-first | Проектирование API до кодирования |
| Contract testing | Валидация соответствия API спецификации |

---

## Follow-ups
- What is the difference between OpenAPI 2.0 and 3.0?
- How to generate client SDKs from OpenAPI?
- What is contract testing with Pact?

## Dopolnitelnye voprosy (RU)
- В чём разница между OpenAPI 2.0 и 3.0?
- Как генерировать клиентские SDK из OpenAPI?
- Что такое contract testing с Pact?

## References
- [[c-api]]
- [[c-documentation]]
- [[moc-backend]]

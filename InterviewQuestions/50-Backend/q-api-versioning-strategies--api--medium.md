---
id: be-api-001
title: API Versioning Strategies / Стратегии версионирования API
aliases: []
topic: api
subtopics:
- versioning
- rest
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
- c-rest
created: 2025-01-23
updated: 2025-01-23
tags:
- api
- versioning
- rest
- difficulty/medium
- topic/api
anki_cards:
- slug: be-api-001-0-en
  language: en
  anki_id: 1769167242627
  synced_at: '2026-01-23T15:20:43.070860'
- slug: be-api-001-0-ru
  language: ru
  anki_id: 1769167242658
  synced_at: '2026-01-23T15:20:43.072415'
---
# Question (EN)
> What are the different strategies for API versioning?

# Vopros (RU)
> Какие существуют стратегии версионирования API?

---

## Answer (EN)

**Why Version APIs:**
- Introduce breaking changes safely
- Support multiple client versions
- Gradual migration path
- Clear deprecation timeline

---

**Versioning Strategies:**

**1. URL Path Versioning (Most Common)**
```
GET /api/v1/users
GET /api/v2/users
```

```python
# FastAPI
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/users")
def get_users_v1():
    return {"format": "old"}

@v2_router.get("/users")
def get_users_v2():
    return {"format": "new", "pagination": {...}}
```

**Pros:** Explicit, easy to understand, cacheable
**Cons:** URL pollution, harder to evolve gradually

---

**2. Query Parameter Versioning**
```
GET /api/users?version=1
GET /api/users?version=2
```

**Pros:** Simple to implement, optional
**Cons:** Easy to forget, less explicit

---

**3. Header Versioning**
```http
GET /api/users
Accept: application/vnd.myapi.v1+json
```

```python
@app.get("/api/users")
def get_users(accept: str = Header(...)):
    if "v2" in accept:
        return new_format()
    return old_format()
```

**Pros:** Clean URLs, follows HTTP semantics
**Cons:** Harder to test, less visible

---

**4. Content Negotiation (Media Type)**
```http
GET /api/users
Accept: application/vnd.company.user.v2+json
```

**Pros:** RESTful, fine-grained control
**Cons:** Complex, requires client support

---

**Comparison:**

| Strategy | URL | Caching | Explicit | Testing |
|----------|-----|---------|----------|---------|
| URL Path | Modified | Easy | Very | Easy |
| Query Param | Modified | Harder | Medium | Easy |
| Header | Same | Harder | Less | Harder |
| Media Type | Same | Harder | Less | Harder |

---

**Breaking vs Non-Breaking Changes:**

| Non-Breaking (Safe) | Breaking (Needs Version) |
|---------------------|--------------------------|
| Add new endpoint | Remove endpoint |
| Add optional field | Remove field |
| Add optional parameter | Change field type |
| Widen accepted values | Narrow accepted values |
| | Rename field |
| | Change behavior |

**Best Practices:**
- Start with v1 from day one
- Document version lifecycle
- Support at least 2 versions
- Announce deprecation timeline (6+ months)
- Use semantic versioning for major changes

## Otvet (RU)

**Зачем версионировать API:**
- Безопасно вносить ломающие изменения
- Поддерживать несколько версий клиентов
- Постепенный путь миграции
- Чёткий график deprecation

---

**Стратегии версионирования:**

**1. Версия в URL-пути (самая распространённая)**
```
GET /api/v1/users
GET /api/v2/users
```

```python
# FastAPI
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/users")
def get_users_v1():
    return {"format": "old"}

@v2_router.get("/users")
def get_users_v2():
    return {"format": "new", "pagination": {...}}
```

**Плюсы:** Явно, легко понять, кэшируется
**Минусы:** Засорение URL, сложнее эволюционировать постепенно

---

**2. Версия в Query-параметре**
```
GET /api/users?version=1
GET /api/users?version=2
```

**Плюсы:** Просто реализовать, опционально
**Минусы:** Легко забыть, менее явно

---

**3. Версия в заголовке**
```http
GET /api/users
Accept: application/vnd.myapi.v1+json
```

```python
@app.get("/api/users")
def get_users(accept: str = Header(...)):
    if "v2" in accept:
        return new_format()
    return old_format()
```

**Плюсы:** Чистые URL, следует HTTP-семантике
**Минусы:** Сложнее тестировать, менее видимо

---

**4. Content Negotiation (Media Type)**
```http
GET /api/users
Accept: application/vnd.company.user.v2+json
```

**Плюсы:** RESTful, точный контроль
**Минусы:** Сложно, требует поддержки клиента

---

**Сравнение:**

| Стратегия | URL | Кэширование | Явность | Тестирование |
|-----------|-----|-------------|---------|--------------|
| URL Path | Изменён | Просто | Очень | Просто |
| Query Param | Изменён | Сложнее | Средняя | Просто |
| Header | Тот же | Сложнее | Меньше | Сложнее |
| Media Type | Тот же | Сложнее | Меньше | Сложнее |

---

**Ломающие vs неломающие изменения:**

| Неломающие (безопасно) | Ломающие (нужна версия) |
|------------------------|-------------------------|
| Добавить новый эндпоинт | Удалить эндпоинт |
| Добавить опциональное поле | Удалить поле |
| Добавить опциональный параметр | Изменить тип поля |
| Расширить допустимые значения | Сузить допустимые значения |
| | Переименовать поле |
| | Изменить поведение |

**Лучшие практики:**
- Начинайте с v1 с первого дня
- Документируйте жизненный цикл версий
- Поддерживайте минимум 2 версии
- Объявляйте график deprecation (6+ месяцев)
- Используйте семантическое версионирование для major-изменений

---

## Follow-ups
- How to deprecate API versions gracefully?
- What is semantic versioning?
- How to version GraphQL APIs?

## Dopolnitelnye voprosy (RU)
- Как грациозно deprecate версии API?
- Что такое семантическое версионирование?
- Как версионировать GraphQL API?

## References
- [[c-api]]
- [[c-rest]]
- [[moc-backend]]

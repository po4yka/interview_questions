---
id: be-db-004
title: Cursor vs Offset Pagination / Курсорная vs офсетная пагинация
aliases: []
topic: databases
subtopics:
- pagination
- performance
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
- c-databases
- c-api
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- pagination
- api
- difficulty/medium
- topic/databases
anki_cards:
- slug: be-db-004-0-en
  language: en
  anki_id: 1769167241865
  synced_at: '2026-01-23T15:20:43.035181'
- slug: be-db-004-0-ru
  language: ru
  anki_id: 1769167241893
  synced_at: '2026-01-23T15:20:43.036653'
---
# Question (EN)
> What is the difference between cursor-based and offset-based pagination?

# Vopros (RU)
> В чём разница между курсорной и офсетной пагинацией?

---

## Answer (EN)

**Offset Pagination** - Uses LIMIT and OFFSET to skip rows.

```sql
-- Page 1
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 0;

-- Page 100
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 990;
```

**API:**
```
GET /posts?page=1&per_page=10
GET /posts?limit=10&offset=990
```

**Problems:**
- **Slow on large offsets** - DB must scan and skip all offset rows
- **Inconsistent results** - New inserts shift positions
- **Missing/duplicate items** - If data changes between requests

---

**Cursor Pagination** - Uses a pointer to the last seen item.

```sql
-- First page
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10;

-- Next page (cursor = last item's created_at)
SELECT * FROM posts
WHERE created_at < '2024-01-15T10:30:00'
ORDER BY created_at DESC LIMIT 10;
```

**API:**
```json
// Response
{
  "data": [...],
  "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSJ9"
}

// Next request
GET /posts?cursor=eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSJ9&limit=10
```

---

**Comparison:**

| Aspect | Offset | Cursor |
|--------|--------|--------|
| Performance | O(n) - degrades with page | O(1) - constant |
| Random page access | Yes (page 50) | No (sequential only) |
| Data consistency | Unstable | Stable |
| Index usage | Often poor | Efficient |
| Implementation | Simple | Complex |

---

**Cursor Implementation:**

```python
import base64
import json

def encode_cursor(item):
    """Create cursor from last item"""
    cursor_data = {
        "created_at": item.created_at.isoformat(),
        "id": item.id  # Tiebreaker for same timestamp
    }
    return base64.b64encode(json.dumps(cursor_data).encode()).decode()

def decode_cursor(cursor):
    """Parse cursor"""
    return json.loads(base64.b64decode(cursor))

def get_posts(cursor=None, limit=10):
    query = Post.query.order_by(Post.created_at.desc(), Post.id.desc())

    if cursor:
        c = decode_cursor(cursor)
        query = query.filter(
            (Post.created_at < c['created_at']) |
            ((Post.created_at == c['created_at']) & (Post.id < c['id']))
        )

    return query.limit(limit + 1).all()  # Fetch one extra to check has_next
```

**When to Use:**
| Use Case | Recommendation |
|----------|----------------|
| Infinite scroll | Cursor |
| Real-time feeds | Cursor |
| Admin dashboard | Offset |
| Search results | Offset (with limits) |
| Large datasets | Cursor |

## Otvet (RU)

**Офсетная пагинация** - Использует LIMIT и OFFSET для пропуска строк.

```sql
-- Страница 1
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 0;

-- Страница 100
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 990;
```

**API:**
```
GET /posts?page=1&per_page=10
GET /posts?limit=10&offset=990
```

**Проблемы:**
- **Медленно при больших offset** - БД должна просканировать и пропустить все строки
- **Непоследовательные результаты** - Новые вставки сдвигают позиции
- **Пропуски/дубликаты** - Если данные меняются между запросами

---

**Курсорная пагинация** - Использует указатель на последний увиденный элемент.

```sql
-- Первая страница
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10;

-- Следующая страница (cursor = created_at последнего элемента)
SELECT * FROM posts
WHERE created_at < '2024-01-15T10:30:00'
ORDER BY created_at DESC LIMIT 10;
```

**API:**
```json
// Ответ
{
  "data": [...],
  "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSJ9"
}

// Следующий запрос
GET /posts?cursor=eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSJ9&limit=10
```

---

**Сравнение:**

| Аспект | Offset | Cursor |
|--------|--------|--------|
| Производительность | O(n) - деградирует с страницей | O(1) - константа |
| Произвольный доступ | Да (страница 50) | Нет (только последовательно) |
| Консистентность данных | Нестабильная | Стабильная |
| Использование индекса | Часто плохое | Эффективное |
| Реализация | Простая | Сложная |

---

**Реализация курсора:**

```python
import base64
import json

def encode_cursor(item):
    """Создать курсор из последнего элемента"""
    cursor_data = {
        "created_at": item.created_at.isoformat(),
        "id": item.id  # Tiebreaker для одинаковых timestamp
    }
    return base64.b64encode(json.dumps(cursor_data).encode()).decode()

def decode_cursor(cursor):
    """Парсинг курсора"""
    return json.loads(base64.b64decode(cursor))

def get_posts(cursor=None, limit=10):
    query = Post.query.order_by(Post.created_at.desc(), Post.id.desc())

    if cursor:
        c = decode_cursor(cursor)
        query = query.filter(
            (Post.created_at < c['created_at']) |
            ((Post.created_at == c['created_at']) & (Post.id < c['id']))
        )

    return query.limit(limit + 1).all()  # Берём на 1 больше для проверки has_next
```

**Когда использовать:**
| Сценарий | Рекомендация |
|----------|--------------|
| Бесконечная прокрутка | Курсор |
| Ленты реального времени | Курсор |
| Админ-панель | Offset |
| Результаты поиска | Offset (с ограничениями) |
| Большие наборы данных | Курсор |

---

## Follow-ups
- How to implement bidirectional cursor pagination?
- What is keyset pagination?
- How do GraphQL connections implement pagination?

## Dopolnitelnye voprosy (RU)
- Как реализовать двунаправленную курсорную пагинацию?
- Что такое keyset-пагинация?
- Как GraphQL connections реализуют пагинацию?

## References
- [[c-databases]]
- [[c-api]]
- [[moc-backend]]

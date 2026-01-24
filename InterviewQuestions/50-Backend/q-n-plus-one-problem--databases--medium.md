---
id: be-db-001
title: N+1 Query Problem / Проблема N+1 запросов
aliases: []
topic: databases
subtopics:
- orm
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
- c-orm
- c-databases
created: 2025-01-23
updated: 2025-01-23
tags:
- databases
- orm
- performance
- difficulty/medium
- topic/databases
anki_cards:
- slug: be-db-001-0-en
  language: en
  anki_id: 1769167240805
  synced_at: '2026-01-23T15:20:42.992240'
- slug: be-db-001-0-ru
  language: ru
  anki_id: 1769167240831
  synced_at: '2026-01-23T15:20:42.994049'
---
# Question (EN)
> What is the N+1 query problem and how to solve it?

# Vopros (RU)
> Что такое проблема N+1 запросов и как её решить?

---

## Answer (EN)

**N+1 Problem** - When fetching a list of N entities, the ORM makes 1 query for the list + N additional queries for related data.

**Example (Python/SQLAlchemy):**
```python
# 1 query to get all posts
posts = Post.query.all()

for post in posts:  # N queries to get author of each post
    print(post.author.name)

# Total: 1 + N queries!
```

**SQL Generated:**
```sql
SELECT * FROM posts;  -- 1 query
SELECT * FROM users WHERE id = 1;  -- N queries...
SELECT * FROM users WHERE id = 2;
SELECT * FROM users WHERE id = 3;
```

---

**Solutions:**

**1. Eager Loading (Recommended)**
```python
# SQLAlchemy - joinedload
posts = Post.query.options(joinedload(Post.author)).all()

# Django - select_related (ForeignKey/OneToOne)
posts = Post.objects.select_related('author').all()

# Django - prefetch_related (ManyToMany/reverse FK)
posts = Post.objects.prefetch_related('tags').all()
```

**SQL Generated:**
```sql
SELECT posts.*, users.*
FROM posts
JOIN users ON posts.author_id = users.id;  -- 1 query!
```

**2. Subquery Loading**
```python
# Two queries instead of N+1
posts = Post.query.options(subqueryload(Post.comments)).all()
```
```sql
SELECT * FROM posts;
SELECT * FROM comments WHERE post_id IN (1, 2, 3, ...);
```

**3. Batch Loading**
```python
# Load in batches of 100
posts = Post.query.options(
    selectinload(Post.comments).batch_size(100)
).all()
```

**Detection:**
- Enable query logging in development
- Use tools: Django Debug Toolbar, SQLAlchemy echo=True
- Look for repeated similar queries

**When Each Solution:**
| Situation | Use |
|-----------|-----|
| Single related object | JOIN (joinedload/select_related) |
| Many related objects | Subquery (prefetch_related) |
| Large datasets | Batch loading |

## Otvet (RU)

**Проблема N+1** - При получении списка из N сущностей, ORM выполняет 1 запрос на список + N дополнительных запросов на связанные данные.

**Пример (Python/SQLAlchemy):**
```python
# 1 запрос для получения всех постов
posts = Post.query.all()

for post in posts:  # N запросов для получения автора каждого поста
    print(post.author.name)

# Итого: 1 + N запросов!
```

**Генерируемый SQL:**
```sql
SELECT * FROM posts;  -- 1 запрос
SELECT * FROM users WHERE id = 1;  -- N запросов...
SELECT * FROM users WHERE id = 2;
SELECT * FROM users WHERE id = 3;
```

---

**Решения:**

**1. Eager Loading (рекомендуется)**
```python
# SQLAlchemy - joinedload
posts = Post.query.options(joinedload(Post.author)).all()

# Django - select_related (ForeignKey/OneToOne)
posts = Post.objects.select_related('author').all()

# Django - prefetch_related (ManyToMany/обратный FK)
posts = Post.objects.prefetch_related('tags').all()
```

**Генерируемый SQL:**
```sql
SELECT posts.*, users.*
FROM posts
JOIN users ON posts.author_id = users.id;  -- 1 запрос!
```

**2. Subquery Loading**
```python
# Два запроса вместо N+1
posts = Post.query.options(subqueryload(Post.comments)).all()
```
```sql
SELECT * FROM posts;
SELECT * FROM comments WHERE post_id IN (1, 2, 3, ...);
```

**3. Batch Loading**
```python
# Загрузка пачками по 100
posts = Post.query.options(
    selectinload(Post.comments).batch_size(100)
).all()
```

**Обнаружение:**
- Включите логирование запросов в dev-режиме
- Инструменты: Django Debug Toolbar, SQLAlchemy echo=True
- Ищите повторяющиеся похожие запросы

**Когда что использовать:**
| Ситуация | Используйте |
|----------|-------------|
| Один связанный объект | JOIN (joinedload/select_related) |
| Много связанных объектов | Subquery (prefetch_related) |
| Большие наборы данных | Batch loading |

---

## Follow-ups
- What is the difference between joinedload and subqueryload?
- How does lazy loading work in ORMs?
- How to prevent N+1 in GraphQL?

## Dopolnitelnye voprosy (RU)
- В чём разница между joinedload и subqueryload?
- Как работает ленивая загрузка в ORM?
- Как предотвратить N+1 в GraphQL?

## References
- [[c-orm]]
- [[c-databases]]
- [[moc-backend]]

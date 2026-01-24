---
id: be-db-002
title: Lazy vs Eager Loading / Ленивая vs жадная загрузка
aliases: []
topic: databases
subtopics:
- orm
- loading-strategies
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
- loading-strategies
- difficulty/medium
- topic/databases
anki_cards:
- slug: be-db-002-0-en
  language: en
  anki_id: 1769167242135
  synced_at: '2026-01-23T15:20:43.052329'
- slug: be-db-002-0-ru
  language: ru
  anki_id: 1769167242164
  synced_at: '2026-01-23T15:20:43.054818'
---
# Question (EN)
> What is the difference between lazy and eager loading in ORMs?

# Vopros (RU)
> В чём разница между ленивой и жадной загрузкой в ORM?

---

## Answer (EN)

**Lazy Loading** - Related data is loaded only when accessed.

```python
# Query executed here (posts only)
posts = Post.query.all()

# Query executed here (user loaded when accessed)
for post in posts:
    print(post.author.name)  # <-- Query fired!
```

**Eager Loading** - Related data is loaded upfront with initial query.

```python
# Both posts AND authors loaded in one query
posts = Post.query.options(joinedload(Post.author)).all()

for post in posts:
    print(post.author.name)  # <-- No additional query
```

---

**Comparison:**

| Aspect | Lazy Loading | Eager Loading |
|--------|--------------|---------------|
| Initial query | Fast (less data) | Slower (more data) |
| Access pattern | Query on each access | No extra queries |
| N+1 risk | High | None |
| Memory usage | Lower initially | Higher |
| Use case | Single object access | Lists/collections |

---

**Loading Strategy Types:**

**1. Lazy (Default in many ORMs)**
```python
# SQLAlchemy
relationship("Author", lazy="select")  # Default

# Hibernate/JPA
@ManyToOne(fetch = FetchType.LAZY)
```

**2. Eager with JOIN**
```python
# Single query with JOIN
relationship("Author", lazy="joined")

# Django
Post.objects.select_related('author')
```

**3. Eager with Subquery**
```python
# Two queries (list + IN clause)
relationship("Comments", lazy="subquery")

# Django
Post.objects.prefetch_related('comments')
```

**4. Selectin (Batch)**
```python
# Batched IN queries
relationship("Tags", lazy="selectin")
```

---

**When to Use:**

| Scenario | Strategy |
|----------|----------|
| Single object with relation | Lazy OK |
| List of objects | Eager (avoid N+1) |
| ForeignKey/OneToOne | JOIN (select_related) |
| ManyToMany/Reverse FK | Subquery (prefetch_related) |
| Large related sets | Batch/Selectin |

**Best Practice:**
- Default to lazy in models
- Explicitly eager load in queries when needed
- Profile and monitor query counts

## Otvet (RU)

**Ленивая загрузка (Lazy Loading)** - Связанные данные загружаются только при обращении к ним.

```python
# Запрос выполняется здесь (только посты)
posts = Post.query.all()

# Запрос выполняется здесь (пользователь загружается при обращении)
for post in posts:
    print(post.author.name)  # <-- Запрос выполняется!
```

**Жадная загрузка (Eager Loading)** - Связанные данные загружаются заранее вместе с основным запросом.

```python
# И посты, И авторы загружены одним запросом
posts = Post.query.options(joinedload(Post.author)).all()

for post in posts:
    print(post.author.name)  # <-- Дополнительных запросов нет
```

---

**Сравнение:**

| Аспект | Lazy Loading | Eager Loading |
|--------|--------------|---------------|
| Начальный запрос | Быстрый (меньше данных) | Медленнее (больше данных) |
| Паттерн доступа | Запрос при каждом обращении | Нет дополнительных запросов |
| Риск N+1 | Высокий | Отсутствует |
| Использование памяти | Ниже изначально | Выше |
| Сценарий использования | Доступ к одному объекту | Списки/коллекции |

---

**Типы стратегий загрузки:**

**1. Lazy (по умолчанию во многих ORM)**
```python
# SQLAlchemy
relationship("Author", lazy="select")  # По умолчанию

# Hibernate/JPA
@ManyToOne(fetch = FetchType.LAZY)
```

**2. Eager с JOIN**
```python
# Один запрос с JOIN
relationship("Author", lazy="joined")

# Django
Post.objects.select_related('author')
```

**3. Eager с Subquery**
```python
# Два запроса (список + IN clause)
relationship("Comments", lazy="subquery")

# Django
Post.objects.prefetch_related('comments')
```

**4. Selectin (Batch)**
```python
# Пакетные IN-запросы
relationship("Tags", lazy="selectin")
```

---

**Когда использовать:**

| Сценарий | Стратегия |
|----------|-----------|
| Один объект со связью | Lazy допустим |
| Список объектов | Eager (избегаем N+1) |
| ForeignKey/OneToOne | JOIN (select_related) |
| ManyToMany/Обратный FK | Subquery (prefetch_related) |
| Большие связанные наборы | Batch/Selectin |

**Лучшая практика:**
- По умолчанию lazy в моделях
- Явно указывайте eager в запросах когда нужно
- Профилируйте и мониторьте количество запросов

---

## Follow-ups
- How does lazy loading work under the hood?
- What is the proxy pattern in lazy loading?
- How to debug loading strategy issues?

## Dopolnitelnye voprosy (RU)
- Как работает ленивая загрузка под капотом?
- Что такое паттерн proxy в ленивой загрузке?
- Как отлаживать проблемы со стратегиями загрузки?

## References
- [[c-orm]]
- [[c-databases]]
- [[moc-backend]]

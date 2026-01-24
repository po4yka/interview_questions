---
id: sysdes-059
title: GraphQL Basics
aliases:
- GraphQL
- Query Language
- API Query
topic: system-design
subtopics:
- communication
- api
- protocols
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
- q-grpc-vs-rest--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- communication
- difficulty/medium
- api
- system-design
anki_cards:
- slug: sysdes-059-0-en
  language: en
  anki_id: 1769160585428
  synced_at: '2026-01-23T13:49:17.859257'
- slug: sysdes-059-0-ru
  language: ru
  anki_id: 1769160585449
  synced_at: '2026-01-23T13:49:17.860287'
---
# Question (EN)
> What is GraphQL? How does it differ from REST, and when would you choose it?

# Vopros (RU)
> Что такое GraphQL? Чем он отличается от REST и когда его выбирать?

---

## Answer (EN)

**GraphQL** is a query language for APIs that allows clients to request exactly the data they need, developed by Facebook.

### REST vs GraphQL

```
REST: Multiple endpoints, fixed responses
GET /users/123         → {id, name, email, address, phone...}
GET /users/123/posts   → [{id, title, content, created...}]
GET /posts/456/comments → [{id, text, author...}]

GraphQL: Single endpoint, flexible queries
POST /graphql
query {
  user(id: 123) {
    name
    posts(first: 5) {
      title
      comments { text }
    }
  }
}
→ Exactly what was requested, nothing more
```

### Key Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| Query | Read data | `query { user { name } }` |
| Mutation | Write data | `mutation { createUser(...) }` |
| Subscription | Real-time updates | `subscription { newMessage }` |
| Schema | Type definitions | `type User { id: ID!, name: String }` |
| Resolver | Data fetching logic | Function that returns data |

### Schema Definition

```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  author: User!
  comments: [Comment!]!
}

type Query {
  user(id: ID!): User
  posts(limit: Int): [Post!]!
}

type Mutation {
  createPost(title: String!, authorId: ID!): Post!
}
```

### GraphQL vs REST Comparison

| Aspect | REST | GraphQL |
|--------|------|---------|
| Endpoints | Multiple | Single |
| Over-fetching | Common | None |
| Under-fetching | Common (N+1 problem) | Solved |
| Versioning | /v1/, /v2/ | Schema evolution |
| Caching | HTTP caching | Complex (needs client) |
| File upload | Native | Needs workaround |
| Learning curve | Lower | Higher |

### When to Use GraphQL

**Good fit:**
- Mobile apps (bandwidth sensitive)
- Complex data relationships
- Multiple clients needing different data
- Rapid iteration on frontend

**Poor fit:**
- Simple CRUD APIs
- File uploads/downloads
- Strict caching requirements
- Server-to-server communication

### N+1 Problem Solution

```
REST N+1:
GET /posts → [post1, post2, post3]
GET /users/1 → author1
GET /users/2 → author2
GET /users/3 → author3
(4 requests)

GraphQL with DataLoader:
query { posts { author { name } } }
→ Batches: SELECT * FROM users WHERE id IN (1,2,3)
(1 request, batched DB query)
```

---

## Otvet (RU)

**GraphQL** - язык запросов для API, позволяющий клиентам запрашивать именно те данные, которые им нужны, разработан Facebook.

### REST vs GraphQL

```
REST: Множество endpoints, фиксированные ответы
GET /users/123         → {id, name, email, address, phone...}
GET /users/123/posts   → [{id, title, content, created...}]

GraphQL: Один endpoint, гибкие запросы
POST /graphql
query {
  user(id: 123) {
    name
    posts(first: 5) {
      title
    }
  }
}
→ Ровно то, что запросили, ничего лишнего
```

### Ключевые концепции

| Концепция | Описание | Пример |
|-----------|----------|--------|
| Query | Чтение данных | `query { user { name } }` |
| Mutation | Запись данных | `mutation { createUser(...) }` |
| Subscription | Real-time обновления | `subscription { newMessage }` |
| Schema | Определения типов | `type User { id: ID!, name: String }` |
| Resolver | Логика получения данных | Функция, возвращающая данные |

### GraphQL vs REST сравнение

| Аспект | REST | GraphQL |
|--------|------|---------|
| Endpoints | Множество | Один |
| Over-fetching | Часто | Нет |
| Under-fetching | Часто (N+1 проблема) | Решено |
| Версионирование | /v1/, /v2/ | Эволюция схемы |
| Кеширование | HTTP кеширование | Сложнее (нужен клиент) |
| Загрузка файлов | Нативная | Нужен workaround |

### Когда использовать GraphQL

**Хорошо подходит:**
- Мобильные приложения (важен bandwidth)
- Сложные связи данных
- Множество клиентов с разными потребностями
- Быстрая итерация на frontend

**Плохо подходит:**
- Простые CRUD API
- Загрузка/выгрузка файлов
- Строгие требования к кешированию
- Server-to-server коммуникация

### Решение N+1 проблемы

```
GraphQL с DataLoader:
query { posts { author { name } } }
→ Batching: SELECT * FROM users WHERE id IN (1,2,3)
(1 запрос, пакетный запрос к БД)
```

---

## Follow-ups

- What is the N+1 problem and how does DataLoader solve it?
- How do you handle authentication in GraphQL?
- What are the security concerns with GraphQL (query complexity)?

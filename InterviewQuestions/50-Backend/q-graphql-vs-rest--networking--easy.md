---
id: net-001
title: "GraphQL vs REST / GraphQL против REST"
aliases: ["GraphQL vs REST", "GraphQL против REST"]
topic: networking
subtopics: [api-design, http]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-backend
related: [q-http-protocols-comparison--android--medium, q-repository-multiple-sources--android--medium, q-large-file-upload-app--android--hard]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [api-design, graphql, rest, difficulty/easy]
date created: Monday, October 27th 2025, 3:57:25 pm
date modified: Thursday, October 30th 2025, 12:48:02 pm
---

# Вопрос (RU)

> Сравните GraphQL и REST API. Когда стоит выбрать GraphQL? Обсудите over-fetching, under-fetching, версионирование, кеширование.

# Question (EN)

> Compare GraphQL and REST APIs in detail. When would you choose GraphQL? Discuss over-fetching, under-fetching, versioning, caching.

---

## Ответ (RU)

**GraphQL** и **REST** — два подхода к построению API. REST использует множество эндпоинтов с фиксированной структурой ответа, GraphQL предоставляет единую точку входа, где клиент указывает точные требования к данным.

### Ключевые Различия

**REST:**
- Множество эндпоинтов (`/users/{id}`, `/users/{id}/posts`)
- HTTP методы определяют операции (GET, POST, PUT, DELETE)
- Сервер определяет структуру ответа
- Каждый ресурс имеет свой URL

**GraphQL:**
- Единая точка входа (`POST /graphql`)
- Клиент указывает точные поля в запросе
- Строго типизированная схема
- Вложенная выборка данных в одном запросе

```kotlin
// ❌ REST: множественные запросы
suspend fun getUserProfile(userId: String) {
    val user = api.getUser(userId)  // Запрос 1
    val posts = api.getUserPosts(userId)  // Запрос 2
    val comments = posts.map { api.getPostComments(it.id) }  // N запросов
    // Всего: 2 + N запросов
}

// ✅ GraphQL: единый запрос с точными данными
suspend fun getUserProfile(userId: String) {
    apolloClient.query(GetUserProfileQuery(id = userId)).execute()
    // Всего: 1 запрос, только нужные поля
}
```

### Проблема Over-Fetching (избыточная выборка)

**REST** возвращает все поля, даже если клиенту нужны только некоторые.

```kotlin
// ❌ REST: получаем все поля, нужны только id и name
val user = api.getUser(userId)
// Ответ: { id, name, email, bio, location, followers, ... }

// ✅ GraphQL: запрашиваем только нужное
query {
  user(id: "123") {
    id
    name  // Только эти поля в ответе
  }
}
```

### Проблема Under-Fetching (недостаточная выборка)

**REST** часто требует множественных запросов для получения связанных данных.

```graphql
# ✅ GraphQL: все вложенные данные в одном запросе
query {
  post(id: "456") {
    id
    title
    author { name }
    comments { content, author { name } }
  }
}
```

### Версионирование

**REST:**
```kotlin
// ❌ Множественные версии API
GET /api/v1/users/123
GET /api/v2/users/123
// Проблема: поддержка нескольких версий, миграция клиентов
```

**GraphQL:**
```graphql
# ✅ Эволюция без версионирования
type User {
  name: String! @deprecated(reason: "Используйте fullName")
  fullName: String!  # Новое поле
}
# Старые клиенты работают, новые используют fullName
```

### Кеширование

**REST:** HTTP кеширование (Cache-Control, ETag) — простое, но кешируется весь ресурс.

**GraphQL:** Нормализованный кеш по ID — автоматическое обновление связанных объектов.

```kotlin
// ✅ GraphQL: нормализованный кеш
val apolloClient = ApolloClient.Builder()
    .normalizedCache(MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024))
    .build()

// Query 1: загружает User:123, Post:456
apolloClient.query(GetUserWithPostsQuery(id = "123")).execute()

// Query 2: использует закешированный Post:456 без сети
apolloClient.query(GetPostQuery(id = "456")).execute()
```

### Когда Использовать

**REST:**
- Простые CRUD операции
- Публичные API
- Операции с файлами (multipart upload)
- HTTP кеширование критично (CDN)

**GraphQL:**
- Сложные вложенные данные
- Мобильные приложения (оптимизация трафика)
- Множество типов клиентов с разными требованиями
- Real-time функции (встроенные subscriptions)
- Быстрая эволюция API без версионирования

---

## Answer (EN)

**GraphQL** and **REST** are two approaches to building APIs. REST uses multiple endpoints with fixed response structures, while GraphQL provides a single endpoint where clients specify exact data requirements.

### Key Differences

**REST:**
- Multiple endpoints (`/users/{id}`, `/users/{id}/posts`)
- HTTP methods define operations (GET, POST, PUT, DELETE)
- Server defines response structure
- Each resource has its own URL

**GraphQL:**
- Single endpoint (`POST /graphql`)
- Client specifies exact fields in query
- Strongly typed schema
- Nested data fetching in single request

```kotlin
// ❌ REST: multiple requests
suspend fun getUserProfile(userId: String) {
    val user = api.getUser(userId)  // Request 1
    val posts = api.getUserPosts(userId)  // Request 2
    val comments = posts.map { api.getPostComments(it.id) }  // N requests
    // Total: 2 + N requests
}

// ✅ GraphQL: single request with exact data
suspend fun getUserProfile(userId: String) {
    apolloClient.query(GetUserProfileQuery(id = userId)).execute()
    // Total: 1 request, only needed fields
}
```

### Over-Fetching Problem

**REST** returns all fields even if client needs only some.

```kotlin
// ❌ REST: get all fields, need only id and name
val user = api.getUser(userId)
// Response: { id, name, email, bio, location, followers, ... }

// ✅ GraphQL: request only what's needed
query {
  user(id: "123") {
    id
    name  // Only these fields in response
  }
}
```

### Under-Fetching Problem

**REST** often requires multiple requests to fetch related data.

```graphql
# ✅ GraphQL: all nested data in single request
query {
  post(id: "456") {
    id
    title
    author { name }
    comments { content, author { name } }
  }
}
```

### Versioning

**REST:**
```kotlin
// ❌ Multiple API versions
GET /api/v1/users/123
GET /api/v2/users/123
// Problem: maintain multiple versions, client migration
```

**GraphQL:**
```graphql
# ✅ Evolution without versioning
type User {
  name: String! @deprecated(reason: "Use fullName")
  fullName: String!  # New field
}
# Old clients work, new clients use fullName
```

### Caching

**REST:** HTTP caching (Cache-Control, ETag) — simple but caches entire resource.

**GraphQL:** Normalized cache by ID — automatic updates for related objects.

```kotlin
// ✅ GraphQL: normalized cache
val apolloClient = ApolloClient.Builder()
    .normalizedCache(MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024))
    .build()

// Query 1: loads User:123, Post:456
apolloClient.query(GetUserWithPostsQuery(id = "123")).execute()

// Query 2: uses cached Post:456 without network
apolloClient.query(GetPostQuery(id = "456")).execute()
```

### When to Use

**REST:**
- Simple CRUD operations
- Public APIs
- File operations (multipart upload)
- HTTP caching critical (CDN)

**GraphQL:**
- Complex nested data
- Mobile applications (traffic optimization)
- Multiple client types with different requirements
- Real-time features (built-in subscriptions)
- Rapid API evolution without versioning

---

## Follow-ups

- How to implement pagination in GraphQL vs REST?
- What are GraphQL N+1 query problems and how to solve them with DataLoader?
- How to handle authentication in GraphQL subscriptions?
- What are the performance implications of GraphQL query depth limits?
- How does GraphQL batching work with Apollo Client?

## References

- Apollo GraphQL Documentation
- REST API Best Practices
- GraphQL specification

## Related Questions

### Prerequisites
- HTTP protocol fundamentals
- API design principles

### Related
- [[q-http-protocols-comparison--android--medium]] - HTTP/1.1 vs HTTP/2 vs HTTP/3
- [[q-repository-multiple-sources--android--medium]] - Repository pattern with multiple sources

### Advanced
- [[q-large-file-upload-app--android--hard]] - Handling file uploads in mobile apps

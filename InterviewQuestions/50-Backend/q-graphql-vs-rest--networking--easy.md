---
id: net-001
title: "GraphQL vs REST / GraphQL против REST"
aliases: ["GraphQL vs REST", "GraphQL против REST"]
topic: networking
subtopics: [http]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-backend
related: [c-architecture-patterns, q-http-protocols-comparison--android--medium, q-large-file-upload-app--android--hard]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [difficulty/easy, graphql, networking/http, rest]
---
# Вопрос (RU)

> Сравните GraphQL и REST API. Когда стоит выбрать GraphQL? Обсудите over-fetching, under-fetching, версионирование, кеширование.

# Question (EN)

> Compare GraphQL and REST APIs in detail. When would you choose GraphQL? Discuss over-fetching, under-fetching, versioning, caching.

---

## Ответ (RU)

**GraphQL** и **REST** — два подхода к построению API. REST обычно использует множество эндпоинтов с фиксированной структурой ответа, GraphQL — как правило, единую точку входа, где клиент указывает точные требования к данным в рамках типизированной схемы.

### Ключевые Различия

**REST:**
- Множество эндпоинтов (`/users/{id}`, `/users/{id}/posts`)
- HTTP-методы определяют операции (GET, POST, PUT, DELETE)
- Сервер определяет структуру ответа
- Каждый ресурс имеет свой URL
- Over-/under-fetching зависит от дизайна: можно смягчать через фильтры, `fields`/`include` и т.п., но это не стандартизировано

**GraphQL:**
- Обычно единая точка входа (`/graphql`), поверх HTTP (часто POST для mutation, GET/POST для query)
- Клиент указывает точные поля в запросе
- Строго типизированная схема
- Вложенная выборка связанных данных в одном запросе

```kotlin
// ❌ REST: множественные запросы (наивный дизайн ресурсов)
suspend fun getUserProfile(userId: String) {
    val user = api.getUser(userId)  // Запрос 1
    val posts = api.getUserPosts(userId)  // Запрос 2
    val comments = posts.map { api.getPostComments(it.id) }  // N запросов
    // Всего: 2 + N запросов
}

// ✅ GraphQL: единый запрос с точными данными (если схема это поддерживает)
suspend fun getUserProfile(userId: String) {
    apolloClient.query(GetUserProfileQuery(id = userId)).execute()
    // Всего: 1 запрос, только нужные поля
}
```

### Проблема Over-Fetching (избыточная выборка)

**REST** по умолчанию часто возвращает все поля ресурса, даже если клиенту нужны только некоторые (если специально не реализованы `fields`/projection-параметры).

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

**REST** при наивном дизайне часто требует множественных запросов для получения связанных данных (user, posts, comments).

```graphql
# ✅ GraphQL: все вложенные данные в одном запросе (если это поддержано схемой)
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
// ❌ Явное версионирование эндпоинтов
GET /api/v1/users/123
GET /api/v2/users/123
// Проблема: поддержка нескольких версий и миграция клиентов
```

**GraphQL:**
```graphql
# ✅ Эволюция схемы без URL-версионирования
type User {
  name: String! @deprecated(reason: "Используйте fullName")
  fullName: String!  # Новое поле
}
# Старые клиенты продолжают использовать name, новые — fullName
```

(При сильных ломающих изменениях и в GraphQL иногда вводят новые схемы/ендпоинты.)

### Кеширование

**REST:**
- HTTP-кеширование (Cache-Control, ETag, Last-Modified) хорошо интегрируется с CDN и прокси.
- Обычно кешируется целый ресурс/ответ по URL.

**GraphQL:**
- Обычно один эндпоинт, поэтому стандартное HTTP-кеширование по URL используется сложнее.
- Нормализованный кеш по ID (например, в Apollo Client) реализуется на стороне клиента и позволяет переиспользовать объекты между запросами.
- GraphQL также можно комбинировать с HTTP-кешированием (например, persisted queries, GET для query).

```kotlin
// ✅ GraphQL: нормализованный кеш (клиентская реализация)
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
- Простые CRUD-операции
- Публичные API (особенно с сильной опорой на HTTP/URL-семантику)
- Операции с файлами (multipart upload)
- Критично использование стандартного HTTP-кеширования и CDN

**GraphQL:**
- Сложные, сильно связанные и вложенные доменные модели
- Мобильные приложения и медленные сети (оптимизация трафика за счёт выборки только нужных полей)
- Множество типов клиентов с разными требованиями к данным
- Реактивные/real-time сценарии (через GraphQL Subscriptions поверх WebSocket/другого транспорта)
- Быстрая эволюция API без агрессивного URL-версионирования

---

## Answer (EN)

**GraphQL** and **REST** are two approaches to building APIs. REST typically uses multiple endpoints with fixed response structures, while GraphQL usually exposes a single endpoint where clients specify exact data requirements within a typed schema.

### Key Differences

**REST:**
- Multiple endpoints (`/users/{id}`, `/users/{id}/posts`)
- HTTP methods define operations (GET, POST, PUT, DELETE)
- Server defines response structure
- Each resource has its own URL
- Over-/under-fetching depends on API design; can be mitigated via filters, `fields`/`include` etc., but this is not standardized

**GraphQL:**
- Commonly a single entry point (`/graphql`) over HTTP (often POST for mutations, GET/POST for queries)
- Client specifies exact fields in the query
- Strongly typed schema
- Nested related data can be fetched in a single request

```kotlin
// ❌ REST: multiple requests (naive resource design)
suspend fun getUserProfile(userId: String) {
    val user = api.getUser(userId)  // Request 1
    val posts = api.getUserPosts(userId)  // Request 2
    val comments = posts.map { api.getPostComments(it.id) }  // N requests
    // Total: 2 + N requests
}

// ✅ GraphQL: single request with exact data (if schema supports it)
suspend fun getUserProfile(userId: String) {
    apolloClient.query(GetUserProfileQuery(id = userId)).execute()
    // Total: 1 request, only required fields
}
```

### Over-Fetching Problem

By default, **REST** endpoints often return full representations even if the client needs only a subset (unless explicit field selection/projections are implemented).

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

With a naive **REST** design, multiple requests are often needed to retrieve related resources (user, posts, comments).

```graphql
# ✅ GraphQL: all nested data in a single request (if supported by schema)
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
// ❌ Explicit API versioning via URLs
GET /api/v1/users/123
GET /api/v2/users/123
// Problem: maintain multiple versions and migrate clients
```

**GraphQL:**
```graphql
# ✅ Schema evolution without URL versioning
type User {
  name: String! @deprecated(reason: "Use fullName")
  fullName: String!  # New field
}
# Old clients keep using name, new clients switch to fullName
```

(For severe breaking changes, GraphQL setups may also introduce new schemas/endpoints.)

### Caching

**REST:**
- HTTP caching (Cache-Control, ETag, Last-Modified) integrates well with CDNs and intermediaries.
- Typically caches whole resources/responses per URL.

**GraphQL:**
- Single endpoint makes naive URL-based HTTP caching less straightforward.
- Normalized caching by ID (e.g., in Apollo Client) is implemented on the client side and enables reuse of entities across queries.
- GraphQL can also leverage HTTP caching (e.g., persisted queries, GET for queries) when designed accordingly.

```kotlin
// ✅ GraphQL: normalized cache (client-side mechanism)
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
- Public APIs (especially those leveraging clear HTTP/URL semantics)
- File operations (multipart upload)
- When standard HTTP caching and CDN support are critical

**GraphQL:**
- Complex, highly-related and nested data models
- Mobile and constrained-network clients (optimize traffic by fetching only required fields)
- Multiple client types with diverse data needs
- Reactive/real-time use cases (via GraphQL Subscriptions over WebSocket/other transports)
- Rapid API evolution without heavy URL-based versioning

---

## Дополнительные Вопросы (RU)

- Как реализовать пагинацию в GraphQL по сравнению с REST?
- В чем заключается проблема N+1 запросов в GraphQL и как решает ее DataLoader?
- Как обрабатывать аутентификацию в подписках GraphQL (subscriptions)?
- Какова связь глубины GraphQL-запросов и производительности, и зачем нужны ограничения глубины?
- Как работает батчинг запросов в GraphQL-клиентах вроде Apollo Client?

## Follow-ups

- How to implement pagination in GraphQL vs REST?
- What are GraphQL N+1 query problems and how to solve them with DataLoader?
- How to handle authentication in GraphQL subscriptions?
- What are the performance implications of GraphQL query depth limits?
- How does GraphQL batching work with Apollo Client?

## Ссылки (RU)

- [[c-architecture-patterns]]
- Документация Apollo GraphQL
- Рекомендации по проектированию REST API
- Спецификация GraphQL

## References

- [[c-architecture-patterns]]
- Apollo GraphQL Documentation
- REST API Best Practices
- GraphQL specification

## Связанные Вопросы (RU)

### Предпосылки
- Основы протокола HTTP
- Принципы проектирования API

### Связанные
- [[q-http-protocols-comparison--android--medium]] - HTTP/1.1 vs HTTP/2 vs HTTP/3
- [[q-repository-multiple-sources--android--medium]] - Паттерн Repository с несколькими источниками данных

### Продвинутое
- [[q-large-file-upload-app--android--hard]] - Загрузка больших файлов в мобильных приложениях

## Related Questions

### Prerequisites
- HTTP protocol fundamentals
- API design principles

### Related
- [[q-http-protocols-comparison--android--medium]] - HTTP/1.1 vs HTTP/2 vs HTTP/3
- [[q-repository-multiple-sources--android--medium]] - Repository pattern with multiple sources

### Advanced
- [[q-large-file-upload-app--android--hard]] - Handling file uploads in mobile apps

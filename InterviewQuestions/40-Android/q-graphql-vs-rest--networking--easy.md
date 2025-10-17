---
id: "20251015082237286"
title: "Graphql Vs Rest / Graphql против Rest"
topic: networking
difficulty: easy
status: draft
created: 2025-10-15
tags: [graphql, rest, api-design, comparison, architecture, difficulty/easy]
---

# Question (EN)

> Compare GraphQL and REST APIs in detail. When would you choose GraphQL? Discuss over-fetching, under-fetching, versioning, caching.

# Вопрос (RU)

> Сравните GraphQL и REST API. Когда стоит выбрать GraphQL? Обсудите over-fetching, under-fetching, версионирование, кэширование.

---

## Answer (EN)

**GraphQL** and **REST** are two different approaches to building APIs. While REST has been the standard for decades, GraphQL offers a modern alternative that solves many common REST pain points. Understanding when to use each is crucial for building efficient, maintainable APIs.

### Fundamental Differences

#### REST (Representational State Transfer)

```kotlin
// REST approach - Multiple endpoints
GET    /api/users/123
GET    /api/users/123/posts
GET    /api/posts/456/comments
POST   /api/posts
PUT    /api/posts/456
DELETE /api/posts/456
```

**Characteristics:**

-   Multiple endpoints for different resources
-   HTTP methods define operations (GET, POST, PUT, DELETE)
-   Server defines response structure
-   Each resource has its own URL

#### GraphQL

```graphql
# GraphQL approach - Single endpoint
POST /api/graphql

# Client defines exact data needs
query {
  user(id: "123") {
    id
    name
    posts {
      id
      title
      comments {
        id
        content
      }
    }
  }
}
```

**Characteristics:**

-   Single endpoint for all operations
-   Client specifies exact data requirements
-   Strongly typed schema
-   Nested data fetching in single request

### Side-by-Side Comparison

Let's implement the same functionality in both REST and GraphQL to see the differences.

#### Scenario: User Profile with Posts

**REST Implementation**

```kotlin
// REST API Service
interface RestApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): UserResponse

    @GET("users/{id}/posts")
    suspend fun getUserPosts(@Path("id") userId: String): List<PostResponse>

    @GET("posts/{id}/comments")
    suspend fun getPostComments(@Path("id") postId: String): List<CommentResponse>
}

// Data models
data class UserResponse(
    val id: String,
    val name: String,
    val email: String,
    val avatar: String?,
    val bio: String?,
    val location: String?,
    val website: String?,
    val followers: Int,
    val following: Int,
    val createdAt: String
)

data class PostResponse(
    val id: String,
    val title: String,
    val content: String,
    val excerpt: String?,
    val tags: List<String>,
    val likes: Int,
    val views: Int,
    val createdAt: String,
    val updatedAt: String
)

data class CommentResponse(
    val id: String,
    val content: String,
    val authorId: String,
    val authorName: String,
    val authorAvatar: String?,
    val likes: Int,
    val createdAt: String
)

// Repository - REST requires multiple calls
class RestUserRepository(private val api: RestApiService) {

    suspend fun getUserProfile(userId: String): UserProfile {
        // Problem: Multiple network calls required
        val user = api.getUser(userId)
        val posts = api.getUserPosts(userId)

        // Problem: N+1 queries - need to fetch comments for each post
        val postsWithComments = posts.map { post ->
            val comments = api.getPostComments(post.id)
            post.copy(comments = comments)
        }

        // Problem: Over-fetching - received data we don't need
        // (bio, location, website, excerpt, tags, views)

        return UserProfile(
            id = user.id,
            name = user.name,
            avatar = user.avatar,
            posts = postsWithComments.map { post ->
                Post(
                    id = post.id,
                    title = post.title,
                    likes = post.likes,
                    commentCount = post.comments.size
                )
            }
        )
    }
}

// Domain model (what we actually need)
data class UserProfile(
    val id: String,
    val name: String,
    val avatar: String?,
    val posts: List<Post>
)

data class Post(
    val id: String,
    val title: String,
    val likes: Int,
    val commentCount: Int
)
```

**GraphQL Implementation**

```graphql
# GraphQL Schema
type User {
    id: ID!
    name: String!
    email: String!
    avatar: String
    bio: String
    location: String
    website: String
    followers: Int!
    following: Int!
    posts: [Post!]!
    createdAt: DateTime!
}

type Post {
    id: ID!
    title: String!
    content: String!
    excerpt: String
    tags: [String!]!
    likes: Int!
    views: Int!
    comments: [Comment!]!
    createdAt: DateTime!
    updatedAt: DateTime!
}

type Comment {
    id: ID!
    content: String!
    author: User!
    likes: Int!
    createdAt: DateTime!
}

type Query {
    user(id: ID!): User
}
```

```graphql
# GraphQL Query - Request exactly what we need
query GetUserProfile($id: ID!) {
    user(id: $id) {
        id
        name
        avatar
        posts {
            id
            title
            likes
            comments {
                id
            }
        }
    }
}
```

```kotlin
// GraphQL implementation with Apollo
class GraphQLUserRepository(private val apolloClient: ApolloClient) {

    suspend fun getUserProfile(userId: String): UserProfile {
        // Solution: Single network call with exact data
        val response = apolloClient
            .query(GetUserProfileQuery(id = userId))
            .execute()

        val user = response.dataAssertNoErrors.user

        return UserProfile(
            id = user.id,
            name = user.name,
            avatar = user.avatar,
            posts = user.posts.map { post ->
                Post(
                    id = post.id,
                    title = post.title,
                    likes = post.likes,
                    commentCount = post.comments.size
                )
            }
        )
    }
}
```

### Over-Fetching Problem

**Over-fetching** occurs when the API returns more data than the client needs.

#### REST Example

```kotlin
// REST endpoint returns everything
@GET("users/{id}")
suspend fun getUser(@Path("id") userId: String): UserResponse

// Response includes ALL fields:
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "avatar": "https://...",
  "bio": "Long bio text...",           //  Not needed
  "location": "San Francisco",         //  Not needed
  "website": "https://...",            //  Not needed
  "followers": 1234,                   //  Not needed
  "following": 567,                    //  Not needed
  "createdAt": "2020-01-01T00:00:00Z", //  Not needed
  "settings": { /* ... */ }            //  Not needed
}

// Problems:
// - Larger response size
// - More bandwidth used
// - Slower parsing
// - Unnecessary data transmitted
```

#### GraphQL Solution

```graphql
# Request only what you need
query GetUserBasicInfo($id: ID!) {
  user(id: $id) {
    id
    name
    avatar
  }
}

# Response contains ONLY requested fields:
{
  "data": {
    "user": {
      "id": "123",
      "name": "John Doe",
      "avatar": "https://..."
    }
  }
}

# Benefits:
# - Minimal response size
# - Less bandwidth
# - Faster parsing
# - No wasted data
```

### Under-Fetching Problem

**Under-fetching** occurs when a single API call doesn't provide enough data, requiring multiple round trips.

#### REST Example

```kotlin
// Problem: Multiple requests needed
suspend fun getPostWithDetails(postId: String): PostDetails {
    // Request 1: Get post
    val post = api.getPost(postId)

    // Request 2: Get author
    val author = api.getUser(post.authorId)

    // Request 3: Get comments
    val comments = api.getPostComments(postId)

    // Request 4: Get comment authors
    val commentAuthors = comments.map { comment ->
        api.getUser(comment.authorId)
    }

    // Total: 1 + 1 + 1 + N requests = 3 + N requests
    // Latency: Sum of all request latencies
    // For 10 comments: 13 network requests!

    return PostDetails(post, author, comments, commentAuthors)
}

// Performance impact:
// - High latency (waterfall requests)
// - Many network round trips
// - Poor user experience on slow networks
```

#### GraphQL Solution

```graphql
# Single request gets all nested data
query GetPostDetails($id: ID!) {
    post(id: $id) {
        id
        title
        content
        author {
            id
            name
            avatar
        }
        comments {
            id
            content
            author {
                id
                name
                avatar
            }
            createdAt
        }
    }
}

# Benefits:
# - Single network request
# - All data in one response
# - Minimal latency
# - Better performance
```

```kotlin
// GraphQL implementation
suspend fun getPostWithDetails(postId: String): PostDetails {
    // Single request
    val response = apolloClient
        .query(GetPostDetailsQuery(id = postId))
        .execute()

    val post = response.dataAssertNoErrors.post

    // All data available immediately
    return PostDetails(
        post = post,
        author = post.author,
        comments = post.comments
    )
}
```

### N+1 Query Problem

The **N+1 problem** occurs when fetching a list of items (1 query), then fetching related data for each item (N queries).

#### REST Example

```kotlin
// REST: N+1 problem
suspend fun getPostsWithAuthors(): List<PostWithAuthor> {
    // Query 1: Get posts
    val posts = api.getPosts() // 1 request

    // Query N: Get author for each post
    val postsWithAuthors = posts.map { post ->
        val author = api.getUser(post.authorId) // N requests
        PostWithAuthor(post, author)
    }

    // Total: 1 + N requests
    // For 20 posts: 21 network requests!
}
```

#### GraphQL Solution with DataLoader

```graphql
# GraphQL automatically batches and caches
query GetPosts {
    posts {
        id
        title
        author {
            id
            name
        }
    }
}

# Server-side: DataLoader batches author requests
# Instead of N queries, makes 1 query:
# SELECT * FROM users WHERE id IN (1, 2, 3, ...)
```

```kotlin
// Client makes single request
suspend fun getPostsWithAuthors(): List<PostWithAuthor> {
    val response = apolloClient
        .query(GetPostsQuery())
        .execute()

    return response.dataAssertNoErrors.posts
        .map { post ->
            PostWithAuthor(
                id = post.id,
                title = post.title,
                authorName = post.author.name
            )
        }
}
```

### Versioning Comparison

#### REST Versioning

```kotlin
// Approach 1: URL versioning
GET /api/v1/users/123
GET /api/v2/users/123

// Approach 2: Header versioning
GET /api/users/123
Header: Accept: application/vnd.myapi.v1+json

// Approach 3: Query parameter
GET /api/users/123?version=1

// Problems:
// - Multiple API versions to maintain
// - Clients stuck on old versions
// - Breaking changes require new version
// - Gradual migration difficult
```

**REST Versioning Example**

```kotlin
// Version 1 API
interface ApiV1Service {
    @GET("v1/users/{id}")
    suspend fun getUser(@Path("id") userId: String): UserV1Response
}

data class UserV1Response(
    val id: String,
    val name: String,
    val email: String
)

// Version 2 API - Breaking change: renamed field
interface ApiV2Service {
    @GET("v2/users/{id}")
    suspend fun getUser(@Path("id") userId: String): UserV2Response
}

data class UserV2Response(
    val id: String,
    val fullName: String,  // Renamed from "name"
    val email: String,
    val avatar: String?    // New field
)

// Problem: Client must choose which version to use
// Migration is all-or-nothing
```

#### GraphQL Versioning

```graphql
# GraphQL: No versioning needed
# Evolution through deprecation

type User {
    id: ID!
    name: String! @deprecated(reason: "Use 'fullName' instead")
    fullName: String!
    email: String!
    avatar: String
}

# Old clients continue to work:
query OldClient {
    user(id: "123") {
        id
        name # Still works, shows deprecation warning
        email
    }
}

# New clients use new fields:
query NewClient {
    user(id: "123") {
        id
        fullName # New field
        email
        avatar
    }
}

# Benefits:
# - No API versioning
# - Gradual migration
# - Old clients keep working
# - Deprecation warnings help migration
```

```kotlin
// GraphQL: Clients choose what they need
// Old query still works
val oldQuery = GetUserOldQuery(id = userId)

// New query uses new fields
val newQuery = GetUserNewQuery(id = userId)

// Gradual migration possible
```

### Caching Comparison

#### REST Caching

```kotlin
// REST: HTTP caching with headers
GET /api/users/123
Cache-Control: max-age=3600
ETag: "abc123"

// Pros:
// - Standard HTTP caching
// - CDN support
// - Browser/proxy caching

// Cons:
// - Cache invalidation complex
// - Whole resource cached
// - Different endpoints = different caches
```

**REST Cache Implementation**

```kotlin
val okHttpClient = OkHttpClient.Builder()
    .cache(Cache(
        directory = File(context.cacheDir, "http_cache"),
        maxSize = 10L * 1024 * 1024 // 10 MB
    ))
    .addInterceptor { chain ->
        val request = chain.request()
        val response = chain.proceed(request)

        // Cache for 1 hour
        response.newBuilder()
            .header("Cache-Control", "public, max-age=3600")
            .build()
    }
    .build()

// Problem: Cache per endpoint
// /api/users/123 cached separately from /api/users/123/posts
// Updating user doesn't invalidate posts cache
```

#### GraphQL Normalized Cache

```kotlin
// GraphQL: Normalized cache by ID
// Cache structure:
// {
//   "User:123": {
//     "id": "123",
//     "name": "John",
//     "email": "john@example.com"
//   },
//   "Post:456": {
//     "id": "456",
//     "title": "GraphQL Guide",
//     "author": { "__ref": "User:123" }
//   }
// }

// Benefits:
// - Single source of truth
// - Automatic cache updates
// - Consistent data across queries
// - Fine-grained cache control
```

**GraphQL Cache Implementation**

```kotlin
val apolloClient = ApolloClient.Builder()
    .serverUrl("https://api.example.com/graphql")
    .normalizedCache(
        normalizedCacheFactory = MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024)
    )
    .build()

// Query 1: Fetch user with posts
apolloClient.query(GetUserWithPostsQuery(id = "123")).execute()
// Caches: User:123, Post:456, Post:789

// Query 2: Fetch single post
apolloClient.query(GetPostQuery(id = "456")).execute()
// Uses cached Post:456 - no network request needed!

// Mutation: Update post
apolloClient.mutation(UpdatePostMutation(id = "456", title = "New Title")).execute()
// Automatically updates Post:456 in cache
// All queries watching this post see the update!
```

### Decision Matrix

| Factor                  | REST                   | GraphQL                | Winner  |
| ----------------------- | ---------------------- | ---------------------- | ------- |
| **Simple CRUD**         | Straightforward        | More setup needed      | REST    |
| **Complex nested data** | Multiple requests      | Single request         | GraphQL |
| **Mobile/bandwidth**    | Over-fetching common   | Exact data needed      | GraphQL |
| **Caching**             | HTTP cache             | Normalized cache       | GraphQL |
| **Real-time**           | WebSocket/SSE separate | Built-in subscriptions | GraphQL |
| **Learning curve**      | Lower                  | Higher                 | REST    |
| **Type safety**         | Manual (OpenAPI)       | Built-in schema        | GraphQL |
| **Tooling**             | Mature                 | Growing                | REST    |
| **File upload**         | Simple multipart       | More complex           | REST    |
| **Public API**          | Well understood        | Less common            | REST    |
| **Versioning**          | Explicit versions      | Schema evolution       | GraphQL |
| **Monitoring**          | Standard tools         | Needs custom tools     | REST    |

### When to Use REST

**Simple APIs**

-   Basic CRUD operations
-   Few related resources
-   Simple data structures

    **Public APIs**

-   External third-party consumers
-   Well-documented REST standards
-   HTTP caching important

    **File Operations**

-   File uploads/downloads
-   Multipart form data
-   Binary data transfer

    **Team Familiarity**

-   Team experienced with REST
-   Limited GraphQL knowledge
-   Standard tooling preferred

    **HTTP Caching Critical**

-   CDN distribution needed
-   Edge caching requirements
-   Standard HTTP semantics

### When to Use GraphQL

**Complex Data Requirements**

-   Deeply nested data structures
-   Multiple related resources
-   Variable data needs per client

    **Mobile Applications**

-   Bandwidth optimization critical
-   Minimize network requests
-   Battery life considerations

    **Multiple Client Types**

-   Web, mobile, desktop clients
-   Different data needs per platform
-   Single flexible API

    **Real-Time Features**

-   Live updates needed
-   Subscriptions for push data
-   Collaborative features

    **Rapid Iteration**

-   Frequent schema changes
-   No version management desired
-   Gradual API evolution

    **Developer Experience**

-   Type safety important
-   Autocomplete/IntelliSense desired
-   Compile-time validation valued

### Performance Comparison

```kotlin
// Benchmark: Fetch user with 10 posts and their comments

class PerformanceComparison {

    // REST approach
    suspend fun fetchWithREST(userId: String): UserData {
        val startTime = System.currentTimeMillis()

        // Request 1: Get user (100ms)
        val user = restApi.getUser(userId)

        // Request 2: Get user's posts (150ms)
        val posts = restApi.getUserPosts(userId)

        // Requests 3-12: Get comments for each post (10 * 120ms = 1200ms)
        val postsWithComments = posts.map { post ->
            val comments = restApi.getPostComments(post.id)
            post.copy(comments = comments)
        }

        val totalTime = System.currentTimeMillis() - startTime
        // Total: ~1450ms (waterfall requests)
        // Payload: ~150KB (over-fetching)

        return UserData(user, postsWithComments)
    }

    // GraphQL approach
    suspend fun fetchWithGraphQL(userId: String): UserData {
        val startTime = System.currentTimeMillis()

        // Single request with all nested data (200ms)
        val response = apolloClient
            .query(GetUserCompleteQuery(id = userId))
            .execute()

        val totalTime = System.currentTimeMillis() - startTime
        // Total: ~200ms (single request)
        // Payload: ~80KB (exact data needed)

        return UserData(
            user = response.data.user,
            posts = response.data.user.posts
        )
    }
}

// Results:
// REST:     1450ms, 150KB, 12 requests
// GraphQL:  200ms,  80KB,  1 request
//
// GraphQL is:
// - 7x faster
// - 47% less data
// - 92% fewer requests
```

### Migration Strategies

#### Incremental GraphQL Adoption

```kotlin
// Approach 1: GraphQL wrapper over REST
// Start with GraphQL but use existing REST APIs

// GraphQL schema
type User {
  id: ID!
  name: String!
  email: String!
}

type Query {
  user(id: ID!): User
}

// Resolver calls REST API
class UserResolver {
    fun user(id: String): User {
        // Call existing REST API
        val response = restClient.get("/api/users/$id")
        return User(
            id = response.id,
            name = response.name,
            email = response.email
        )
    }
}

// Benefit: Gradual migration without rewriting backend
```

#### REST and GraphQL Together

```kotlin
// Use both in same app
class ApiClient(
    private val restApi: RestApiService,
    private val graphQLClient: ApolloClient
) {

    // Use REST for simple operations
    suspend fun uploadAvatar(file: File): String {
        return restApi.uploadAvatar(
            file = file.asRequestBody("image/*".toMediaType())
        )
    }

    // Use GraphQL for complex queries
    suspend fun getUserProfile(userId: String): UserProfile {
        return graphQLClient
            .query(GetUserProfileQuery(id = userId))
            .execute()
            .dataAssertNoErrors
            .user
    }

    // Use both: Upload via REST, update via GraphQL
    suspend fun updateAvatar(userId: String, file: File) {
        // 1. Upload file via REST (better for files)
        val avatarUrl = uploadAvatar(file)

        // 2. Update user via GraphQL (better for data)
        graphQLClient
            .mutation(
                UpdateUserMutation(
                    id = userId,
                    avatar = avatarUrl
                )
            )
            .execute()
    }
}
```

### Common Pitfalls

#### REST Pitfalls

1. **Over-fetching Ignored**

    ```kotlin
    // BAD: Fetching full objects when only ID needed
    val posts = api.getPosts() // Returns full Post objects
    val postIds = posts.map { it.id } // Only need IDs!

    // BETTER: Add lightweight endpoint
    @GET("posts/ids")
    suspend fun getPostIds(): List<String>
    ```

2. **N+1 Queries Unnoticed**

    ```kotlin
    // BAD: N+1 problem
    val posts = api.getPosts()
    posts.forEach { post ->
        val author = api.getUser(post.authorId) // N queries!
    }

    // BETTER: Include author in response or use batch endpoint
    @GET("posts?include=author")
    suspend fun getPostsWithAuthors(): List<PostWithAuthor>
    ```

3. **Version Sprawl**

    ```kotlin
    // BAD: Too many versions
    interface ApiV1Service { /* ... */ }
    interface ApiV2Service { /* ... */ }
    interface ApiV3Service { /* ... */ }
    interface ApiV4Service { /* ... */ }

    // BETTER: Graceful deprecation with single version
    ```

#### GraphQL Pitfalls

1. **Over-fetching at Server Level**

    ```graphql
    # BAD: Resolver fetches too much
    type User {
        posts: [Post!]! # Resolves ALL posts
    }

    # BETTER: Add pagination
    type User {
        posts(first: Int, after: String): PostConnection!
    }
    ```

2. **No Request Limits**

    ```graphql
    # BAD: Clients can request infinite depth
    query {
      user {
        posts {
          author {
            posts {
              author {
                posts { # Infinite nesting!
    ```

    ```kotlin
    // GOOD: Implement query complexity limits
    apollo {
        maxDepth = 5
        maxComplexity = 1000
    }
    ```

3. **Ignoring Cache**

    ```kotlin
    // BAD: Always fetching from network
    apolloClient.query(GetUserQuery(id))
        .fetchPolicy(FetchPolicy.NetworkOnly) // Always network!

    // GOOD: Use cache when appropriate
    apolloClient.query(GetUserQuery(id))
        .fetchPolicy(FetchPolicy.CacheFirst)
    ```

### Summary

**REST** is ideal for:

-   Simple CRUD APIs
-   Public APIs
-   File operations
-   Teams with REST expertise
-   Standard HTTP caching needs

**GraphQL** excels at:

-   Complex nested data
-   Mobile applications
-   Multiple client types
-   Real-time requirements
-   Rapid API evolution
-   Developer experience

**Key Takeaways:**

-   GraphQL solves over-fetching and under-fetching
-   REST has better caching with standard HTTP
-   GraphQL has better caching with normalization
-   REST versioning is explicit, GraphQL evolves gracefully
-   Choose based on use case, not popularity
-   Both can coexist in same application

---

## Ответ (RU)

**GraphQL** и **REST** - это два разных подхода к построению API. В то время как REST был стандартом в течение десятилетий, GraphQL предлагает современную альтернативу, которая решает многие распространённые проблемы REST. Понимание, когда использовать каждый из них, критически важно для создания эффективных и поддерживаемых API.

### Фундаментальные различия

#### REST (Representational State Transfer)

```kotlin
// REST подход - Множество эндпоинтов
GET    /api/users/123
GET    /api/users/123/posts
GET    /api/posts/456/comments
POST   /api/posts
PUT    /api/posts/456
DELETE /api/posts/456
```

**Характеристики:**

-   Множество эндпоинтов для разных ресурсов
-   HTTP методы определяют операции
-   Сервер определяет структуру ответа
-   Каждый ресурс имеет свой URL

#### GraphQL

```graphql
# GraphQL подход - Единая точка входа
POST /api/graphql

query {
  user(id: "123") {
    id
    name
    posts {
      id
      title
    }
  }
}
```

**Характеристики:**

-   Единая точка входа для всех операций
-   Клиент указывает точные требования к данным
-   Строго типизированная схема
-   Вложенная выборка данных в одном запросе

### Сравнение: одна и та же функциональность

#### REST реализация

```kotlin
// REST API сервис
interface RestApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): UserResponse

    @GET("users/{id}/posts")
    suspend fun getUserPosts(@Path("id") userId: String): List<PostResponse>

    @GET("posts/{id}/comments")
    suspend fun getPostComments(@Path("id") postId: String): List<CommentResponse>
}

// Repository - REST требует множественных вызовов
class RestUserRepository(private val api: RestApiService) {

    suspend fun getUserProfile(userId: String): UserProfile {
        // Проблема: Требуется множество сетевых вызовов
        val user = api.getUser(userId)
        val posts = api.getUserPosts(userId)

        // Проблема: N+1 запросов - нужно получить комментарии для каждого поста
        val postsWithComments = posts.map { post ->
            val comments = api.getPostComments(post.id)
            post.copy(comments = comments)
        }

        // Проблема: Over-fetching - получили данные, которые не нужны
        return UserProfile(
            id = user.id,
            name = user.name,
            posts = postsWithComments
        )
    }
}
```

#### GraphQL реализация

```graphql
# GraphQL запрос - Запросить точно то, что нужно
query GetUserProfile($id: ID!) {
    user(id: $id) {
        id
        name
        avatar
        posts {
            id
            title
            likes
            comments {
                id
            }
        }
    }
}
```

```kotlin
// GraphQL реализация с Apollo
class GraphQLUserRepository(private val apolloClient: ApolloClient) {

    suspend fun getUserProfile(userId: String): UserProfile {
        // Решение: Единый сетевой вызов с точными данными
        val response = apolloClient
            .query(GetUserProfileQuery(id = userId))
            .execute()

        val user = response.dataAssertNoErrors.user

        return UserProfile(
            id = user.id,
            name = user.name,
            posts = user.posts.map { /* ... */ }
        )
    }
}
```

### Проблема Over-Fetching (избыточной выборки)

**Over-fetching** возникает, когда API возвращает больше данных, чем нужно клиенту.

#### REST пример

```kotlin
// REST эндпоинт возвращает всё
@GET("users/{id}")
suspend fun getUser(@Path("id") userId: String): UserResponse

// Ответ включает ВСЕ поля:
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "avatar": "https://...",
  "bio": "Длинный текст био...",      //  Не нужно
  "location": "San Francisco",         //  Не нужно
  "website": "https://...",            //  Не нужно
  "followers": 1234,                   //  Не нужно
  "following": 567,                    //  Не нужно
  "createdAt": "2020-01-01",           //  Не нужно
}

// Проблемы:
// - Больший размер ответа
// - Больше используемой пропускной способности
// - Медленнее парсинг
// - Передаются ненужные данные
```

#### GraphQL решение

```graphql
# Запросить только то, что нужно
query GetUserBasicInfo($id: ID!) {
  user(id: $id) {
    id
    name
    avatar
  }
}

# Ответ содержит ТОЛЬКО запрошенные поля:
{
  "data": {
    "user": {
      "id": "123",
      "name": "John Doe",
      "avatar": "https://..."
    }
  }
}

# Преимущества:
# - Минимальный размер ответа
# - Меньше пропускной способности
# - Быстрее парсинг
# - Нет потраченных впустую данных
```

### Проблема Under-Fetching (недостаточной выборки)

**Under-fetching** возникает, когда один вызов API не предоставляет достаточно данных, требуя множественных запросов.

#### REST пример

```kotlin
// Проблема: Нужно множество запросов
suspend fun getPostWithDetails(postId: String): PostDetails {
    // Запрос 1: Получить пост
    val post = api.getPost(postId)

    // Запрос 2: Получить автора
    val author = api.getUser(post.authorId)

    // Запрос 3: Получить комментарии
    val comments = api.getPostComments(postId)

    // Запрос 4: Получить авторов комментариев
    val commentAuthors = comments.map { comment ->
        api.getUser(comment.authorId)
    }

    // Всего: 1 + 1 + 1 + N запросов = 3 + N запросов
    // Для 10 комментариев: 13 сетевых запросов!

    return PostDetails(post, author, comments, commentAuthors)
}
```

#### GraphQL решение

```graphql
# Единый запрос получает все вложенные данные
query GetPostDetails($id: ID!) {
    post(id: $id) {
        id
        title
        content
        author {
            id
            name
            avatar
        }
        comments {
            id
            content
            author {
                id
                name
            }
        }
    }
}

# Преимущества:
# - Единый сетевой запрос
# - Все данные в одном ответе
# - Минимальная задержка
```

### Сравнение версионирования

#### REST версионирование

```kotlin
// Подход 1: Версионирование в URL
GET /api/v1/users/123
GET /api/v2/users/123

// Подход 2: Версионирование в заголовке
GET /api/users/123
Header: Accept: application/vnd.myapi.v1+json

// Проблемы:
// - Множество версий API для поддержки
// - Клиенты застревают на старых версиях
// - Критические изменения требуют новую версию
```

#### GraphQL версионирование

```graphql
# GraphQL: Версионирование не нужно
# Эволюция через deprecation

type User {
    id: ID!
    name: String! @deprecated(reason: "Используйте 'fullName'")
    fullName: String!
    email: String!
}

# Старые клиенты продолжают работать:
query OldClient {
    user(id: "123") {
        id
        name # Всё ещё работает, показывает предупреждение
        email
    }
}

# Новые клиенты используют новые поля:
query NewClient {
    user(id: "123") {
        id
        fullName # Новое поле
        email
    }
}

# Преимущества:
# - Нет версионирования API
# - Постепенная миграция
# - Старые клиенты продолжают работать
```

### Сравнение кеширования

#### REST кеширование

```kotlin
// REST: HTTP кеширование с заголовками
GET /api/users/123
Cache-Control: max-age=3600

// Плюсы:
// - Стандартное HTTP кеширование
// - Поддержка CDN
// - Кеширование браузером/прокси

// Минусы:
// - Сложная инвалидация кеша
// - Кешируется весь ресурс
// - Разные эндпоинты = разные кеши
```

#### GraphQL нормализованный кеш

```kotlin
// GraphQL: Нормализованный кеш по ID
// Структура кеша:
// {
//   "User:123": {
//     "id": "123",
//     "name": "John"
//   },
//   "Post:456": {
//     "id": "456",
//     "title": "Руководство GraphQL",
//     "author": { "__ref": "User:123" }
//   }
// }

// Преимущества:
// - Единый источник истины
// - Автоматические обновления кеша
// - Консистентные данные между запросами
```

### Матрица решений

| Фактор                               | REST                   | GraphQL             | Победитель |
| ------------------------------------ | ---------------------- | ------------------- | ---------- |
| **Простой CRUD**                     | Прямолинейно           | Больше настройки    | REST       |
| **Сложные вложенные данные**         | Множество запросов     | Единый запрос       | GraphQL    |
| **Мобильные/пропускная способность** | Over-fetching частый   | Точные данные       | GraphQL    |
| **Кеширование**                      | HTTP кеш               | Нормализованный кеш | GraphQL    |
| **Real-time**                        | WebSocket/SSE отдельно | Встроенные подписки | GraphQL    |
| **Кривая обучения**                  | Ниже                   | Выше                | REST       |
| **Типобезопасность**                 | Ручная                 | Встроенная схема    | GraphQL    |
| **Версионирование**                  | Явные версии           | Эволюция схемы      | GraphQL    |

### Когда использовать REST

**Простые API**

-   Базовые CRUD операции
-   Немного связанных ресурсов
-   Простые структуры данных

    **Публичные API**

-   Внешние потребители третьих сторон
-   Хорошо документированные стандарты REST
-   Важно HTTP кеширование

    **Операции с файлами**

-   Загрузка/скачивание файлов
-   Multipart form data
-   Передача бинарных данных

    **Знакомство команды**

-   Команда опытна в REST
-   Ограниченные знания GraphQL

### Когда использовать GraphQL

**Сложные требования к данным**

-   Глубоко вложенные структуры данных
-   Множество связанных ресурсов
-   Переменные потребности в данных

    **Мобильные приложения**

-   Критична оптимизация пропускной способности
-   Минимизация сетевых запросов
-   Учёт времени работы батареи

    **Множество типов клиентов**

-   Веб, мобильные, десктоп клиенты
-   Разные потребности в данных

    **Real-time функции**

-   Нужны живые обновления
-   Подписки для push данных

    **Быстрая итерация**

-   Частые изменения схемы
-   Не желательно управление версиями

### Резюме

**REST** идеален для:

-   Простых CRUD API
-   Публичных API
-   Операций с файлами
-   Команд с экспертизой REST
-   Стандартного HTTP кеширования

**GraphQL** превосходен в:

-   Сложных вложенных данных
-   Мобильных приложениях
-   Множестве типов клиентов
-   Real-time требованиях
-   Быстрой эволюции API

**Ключевые выводы:**

-   GraphQL решает проблемы over-fetching и under-fetching
-   REST лучше для стандартного HTTP кеширования
-   GraphQL лучше с нормализованным кешем
-   Версионирование REST явное, GraphQL эволюционирует gracefully
-   Выбирайте на основе сценария использования
-   Оба могут сосуществовать в одном приложении

---

## Related Questions

### Advanced (Harder)

-   [[q-http-protocols-comparison--android--medium]] - Networking
-   [[q-kmm-ktor-networking--multiplatform--medium]] - Networking
-   [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking

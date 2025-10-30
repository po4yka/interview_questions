---
id: 20251012-122711
title: "Retrofit Path Parameter / Path параметр Retrofit"
aliases: ["Retrofit Path Parameter", "Path параметр Retrofit"]
topic: android
subtopics: [networking-http]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-retrofit-usage-tutorial--android--medium, q-retrofit-library--android--medium, q-http-protocols-comparison--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/networking-http, networking, retrofit, rest-api, path-parameters, difficulty/medium]
---
# Вопрос (RU)
Как в Retrofit в GET-методе поставить атрибут в конкретное место пути?

# Question (EN)
How to put a parameter in a specific place in the path for a GET method in Retrofit?

## Ответ (RU)
В Retrofit используйте аннотацию **`@Path`** для подстановки значений в URL.

**Механизм:**
1. В `@GET` укажите плейсхолдер в фигурных скобках: `{имяПараметра}`
2. Используйте `@Path("имяПараметра")` для связывания параметра метода

```kotlin
@GET("users/{userId}/posts/{postId}")
suspend fun getPost(
    @Path("userId") userId: String,  // ✅ Привязка к {userId}
    @Path("postId") postId: String   // ✅ Привязка к {postId}
): Response<Post>
```

**Вызов:**
```kotlin
api.getPost("123", "456")
// URL: GET /users/123/posts/456
```

### @Path vs @Query

| Аннотация | Где | Пример URL | Когда использовать |
|-----------|-----|------------|-------------------|
| `@Path` | В пути | `/users/123` | ID ресурса, обязательные параметры |
| `@Query` | В query-string | `/users?id=123` | Фильтры, опциональные параметры |

### Множественные параметры

```kotlin
@GET("categories/{category}/products/{productId}")
suspend fun getProduct(
    @Path("category") category: String,
    @Path("productId") productId: String
): Response<Product>

// Вызов: api.getProduct("electronics", "prod789")
// URL: /categories/electronics/products/prod789
```

### Комбинация с @Query

```kotlin
@GET("users/{userId}/posts")
suspend fun getUserPosts(
    @Path("userId") userId: String,     // ✅ Обязательный ID в пути
    @Query("page") page: Int,           // ✅ Опциональная пагинация
    @Query("limit") limit: Int = 20
): Response<List<Post>>

// api.getUserPosts("user123", 1, 20)
// URL: /users/user123/posts?page=1&limit=20
```

### URL-кодирование

Retrofit автоматически кодирует спецсимволы:

```kotlin
@GET("search/{query}")
suspend fun search(@Path("query") query: String): Response<Results>

api.search("hello world")
// URL: /search/hello%20world (пробел → %20)
```

Для отключения кодирования (например, для путей с `/`):

```kotlin
@GET("files/{path}")
suspend fun getFile(
    @Path(value = "path", encoded = true) filePath: String  // ❌ Слеши НЕ кодируются
): Response<FileContent>

api.getFile("folder/subfolder/file.txt")
// URL: /files/folder/subfolder/file.txt
```

### Типичные ошибки

```kotlin
// ❌ НЕПРАВИЛЬНО: нет плейсхолдера
@GET("users/id")
suspend fun getUser(@Path("id") userId: String)

// ✅ ПРАВИЛЬНО: плейсхолдер присутствует
@GET("users/{id}")
suspend fun getUser(@Path("id") userId: String)

// ❌ НЕПРАВИЛЬНО: имена не совпадают
@GET("users/{userId}")
suspend fun getUser(@Path("id") userId: String)  // Error!

// ✅ ПРАВИЛЬНО: имена совпадают
@GET("users/{userId}")
suspend fun getUser(@Path("userId") userId: String)
```

## Answer (EN)
In Retrofit, use the **`@Path`** annotation to insert values into specific URL path locations.

**Mechanism:**
1. Define a placeholder in `@GET` using curly braces: `{parameterName}`
2. Use `@Path("parameterName")` to bind the method parameter

```kotlin
@GET("users/{userId}/posts/{postId}")
suspend fun getPost(
    @Path("userId") userId: String,  // ✅ Binds to {userId}
    @Path("postId") postId: String   // ✅ Binds to {postId}
): Response<Post>
```

**Usage:**
```kotlin
api.getPost("123", "456")
// URL: GET /users/123/posts/456
```

### @Path vs @Query

| Annotation | Location | Example URL | When to Use |
|------------|----------|-------------|-------------|
| `@Path` | In path | `/users/123` | Resource IDs, required parameters |
| `@Query` | In query string | `/users?id=123` | Filters, optional parameters |

### Multiple Parameters

```kotlin
@GET("categories/{category}/products/{productId}")
suspend fun getProduct(
    @Path("category") category: String,
    @Path("productId") productId: String
): Response<Product>

// Call: api.getProduct("electronics", "prod789")
// URL: /categories/electronics/products/prod789
```

### Combined with @Query

```kotlin
@GET("users/{userId}/posts")
suspend fun getUserPosts(
    @Path("userId") userId: String,     // ✅ Required ID in path
    @Query("page") page: Int,           // ✅ Optional pagination
    @Query("limit") limit: Int = 20
): Response<List<Post>>

// api.getUserPosts("user123", 1, 20)
// URL: /users/user123/posts?page=1&limit=20
```

### URL Encoding

Retrofit automatically encodes special characters:

```kotlin
@GET("search/{query}")
suspend fun search(@Path("query") query: String): Response<Results>

api.search("hello world")
// URL: /search/hello%20world (space → %20)
```

To disable encoding (e.g., for paths with `/`):

```kotlin
@GET("files/{path}")
suspend fun getFile(
    @Path(value = "path", encoded = true) filePath: String  // ❌ Slashes NOT encoded
): Response<FileContent>

api.getFile("folder/subfolder/file.txt")
// URL: /files/folder/subfolder/file.txt
```

### Common Mistakes

```kotlin
// ❌ WRONG: no placeholder
@GET("users/id")
suspend fun getUser(@Path("id") userId: String)

// ✅ CORRECT: placeholder present
@GET("users/{id}")
suspend fun getUser(@Path("id") userId: String)

// ❌ WRONG: names don't match
@GET("users/{userId}")
suspend fun getUser(@Path("id") userId: String)  // Error!

// ✅ CORRECT: names match
@GET("users/{userId}")
suspend fun getUser(@Path("userId") userId: String)
```

## Follow-ups
- What happens if you pass `null` to a `@Path` parameter?
- Can you use the same placeholder name multiple times in a single URL?
- How does Retrofit handle special characters like `/` or `?` in path parameters?
- What's the difference between `@Path` and `@Url` annotations?
- How do you handle dynamic base URLs with path parameters?

## References
- https://square.github.io/retrofit/ - Official Retrofit documentation
- https://square.github.io/retrofit/2.x/retrofit/retrofit2/http/Path.html - @Path annotation reference
- https://developer.android.com/training/basics/network-ops - Android networking fundamentals

## Related Questions

### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - Understanding REST API fundamentals
- [[q-retrofit-library--android--medium]] - Basic Retrofit setup and usage

### Related (Medium)
- [[q-retrofit-usage-tutorial--android--medium]] - Comprehensive Retrofit tutorial
- [[q-http-protocols-comparison--android--medium]] - HTTP protocol details
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Advanced Retrofit features

### Advanced (Harder)
- [[q-retrofit-modify-all-requests--android--hard]] - Interceptors and request modification
- [[q-data-sync-unstable-network--android--hard]] - Network resilience patterns

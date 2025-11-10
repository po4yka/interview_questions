---
id: android-289
title: Retrofit Path Parameter / Path параметр Retrofit
aliases:
- Path параметр Retrofit
- Retrofit Path Parameter
topic: android
subtopics:
- networking-http
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-retrofit
- q-http-protocols-comparison--android--medium
- q-retrofit-library--android--medium
- q-retrofit-usage-tutorial--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/networking-http
- difficulty/medium
- networking
- path-parameters
- rest-api
- retrofit
---

# Вопрос (RU)
> Как в Retrofit в GET-методе поставить атрибут в конкретное место пути?

# Question (EN)
> How to put a parameter in a specific place in the path for a GET method in Retrofit?

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

### @Path Vs @Query

| Аннотация | Где | Пример URL | Когда использовать |
|-----------|-----|------------|-------------------|
| `@Path` | В пути | `/users/123` | ID ресурса, обязательные параметры |
| `@Query` | В query-string | `/users?id=123` | Фильтры, опциональные параметры |

### Множественные Параметры

```kotlin
@GET("categories/{category}/products/{productId}")
suspend fun getProduct(
    @Path("category") category: String,
    @Path("productId") productId: String
): Response<Product>

// Вызов: api.getProduct("electronics", "prod789")
// URL: /categories/electronics/products/prod789
```

### Комбинация С @Query

```kotlin
@GET("users/{userId}/posts")
suspend fun getUserPosts(
    @Path("userId") userId: String,     // ✅ Обязательный ID в пути
    @Query("page") page: Int,           // ✅ Например, опциональная пагинация (можно задать значение по умолчанию)
    @Query("limit") limit: Int = 20
): Response<List<Post>>

// api.getUserPosts("user123", 1, 20)
// URL: /users/user123/posts?page=1&limit=20
```

### URL-кодирование

Retrofit по умолчанию URL-кодирует специальные символы в значениях `@Path`.

```kotlin
@GET("search/{query}")
suspend fun search(@Path("query") query: String): Response<Results>

api.search("hello world")
// URL: /search/hello%20world (пробел → %20)
```

Чтобы не перекодировать уже закодированное значение и сохранить специальные символы (например, `/`) как есть, используйте `encoded = true`:

```kotlin
@GET("files/{path}")
suspend fun getFile(
    @Path(value = "path", encoded = true) filePath: String  // ✅ Retrofit не будет повторно кодировать значение; слеши остаются как есть
): Response<FileContent>

api.getFile("folder/subfolder/file.txt")
// URL: /files/folder/subfolder/file.txt
```

### Повторное использование плейсхолдера

В одном URL можно несколько раз использовать один и тот же плейсхолдер имени, если он соответствует одному параметру метода:

```kotlin
@GET("repos/{owner}/{repo}/compare/{base}...{head}")
suspend fun compareCommits(
    @Path("owner") owner: String,
    @Path("repo") repo: String,
    @Path("base") base: String,
    @Path("head") head: String
): Response<CompareResult>
```

(Например, `{owner}` и `{repo}` могут использоваться несколько раз в сложных путях; главное — чтобы имя в `@Path` совпадало с плейсхолдером.)

### Типичные Ошибки

```kotlin
// ❌ НЕПРАВИЛЬНО: нет плейсхолдера
@GET("users/id")
suspend fun getUser(@Path("id") userId: String)

// ✅ ПРАВИЛЬНО: плейсхолдер присутствует
@GET("users/{id}")
suspend fun getUser(@Path("id") userId: String)

// ❌ НЕПРАВИЛЬНО: имена не совпадают
@GET("users/{userId}")
suspend fun getUser(@Path("id") userId: String)  // Ошибка: {userId} != "id"

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

### @Path Vs @Query

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
    @Query("page") page: Int,           // ✅ For example, optional pagination (can use a default)
    @Query("limit") limit: Int = 20
): Response<List<Post>>

// api.getUserPosts("user123", 1, 20)
// URL: /users/user123/posts?page=1&limit=20
```

### URL Encoding

By default Retrofit URL-encodes special characters in `@Path` values.

```kotlin
@GET("search/{query}")
suspend fun search(@Path("query") query: String): Response<Results>

api.search("hello world")
// URL: /search/hello%20world (space → %20)
```

To avoid re-encoding an already-encoded value and to preserve reserved characters (e.g. `/`) as-is, use `encoded = true`:

```kotlin
@GET("files/{path}")
suspend fun getFile(
    @Path(value = "path", encoded = true) filePath: String  // ✅ Retrofit won't re-encode; slashes remain as-is
): Response<FileContent>

api.getFile("folder/subfolder/file.txt")
// URL: /files/folder/subfolder/file.txt
```

### Reusing placeholders

You can use the same placeholder name multiple times in the URL as long as it maps to a single method parameter:

```kotlin
@GET("repos/{owner}/{repo}/compare/{base}...{head}")
suspend fun compareCommits(
    @Path("owner") owner: String,
    @Path("repo") repo: String,
    @Path("base") base: String,
    @Path("head") head: String
): Response<CompareResult>
```

(For example, complex paths can repeat `{owner}` or `{repo}`; the key rule is that the name in `@Path` must match the placeholder.)

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
suspend fun getUser(@Path("id") userId: String)  // Error: {userId} != "id"

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

### Prerequisites / Concepts

- [[c-retrofit]]


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

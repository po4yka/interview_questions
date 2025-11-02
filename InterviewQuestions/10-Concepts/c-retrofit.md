---
id: ivc-20251030-120000
title: Retrofit / Retrofit
aliases: [Retrofit, Retrofit Library, Square Retrofit]
kind: concept
summary: Type-safe HTTP client for Android and Java by Square
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, http, networking, rest-api, retrofit]
date created: Thursday, October 30th 2025, 12:29:23 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

Retrofit is a type-safe HTTP client library for Android and Java developed by Square. It transforms HTTP APIs into Java/Kotlin interfaces using annotations, providing compile-time verification and automatic request/response conversion. Built on top of OkHttp, Retrofit integrates seamlessly with modern concurrency patterns (Coroutines, RxJava, Flow) and JSON converters (Gson, Moshi, kotlinx.serialization).

**Core Principle**: Declarative API definition - describe your REST API endpoints as interface methods with annotations, and Retrofit generates the implementation.

# Сводка (RU)

Retrofit - это типобезопасная HTTP-клиентская библиотека для Android и Java, разработанная Square. Она преобразует HTTP API в Java/Kotlin интерфейсы с помощью аннотаций, обеспечивая проверку во время компиляции и автоматическое преобразование запросов/ответов. Построенная на основе OkHttp, Retrofit легко интегрируется с современными паттернами конкурентности (Coroutines, RxJava, Flow) и JSON-конвертерами (Gson, Moshi, kotlinx.serialization).

**Основной принцип**: Декларативное определение API - описываете REST API эндпоинты как методы интерфейса с аннотациями, и Retrofit генерирует реализацию.

---

## Core Concept / Основная Концепция

### Declarative API Definition (EN)

Retrofit uses annotations to describe HTTP requests:

```kotlin
interface GitHubService {
    @GET("users/{user}/repos")
    suspend fun listRepos(@Path("user") user: String): List<Repo>

    @POST("users/new")
    suspend fun createUser(@Body user: User): User

    @GET("repos/{owner}/{repo}/issues")
    suspend fun getIssues(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Query("state") state: String
    ): List<Issue>
}
```

**Request Annotations**: `@GET`, `@POST`, `@PUT`, `@DELETE`, `@PATCH`, `@HEAD`, `@OPTIONS`
**Parameter Annotations**: `@Path`, `@Query`, `@Body`, `@Header`, `@Field`, `@Part`

### Декларативное Определение API (RU)

Retrofit использует аннотации для описания HTTP-запросов (см. код выше).

**Аннотации запросов**: описывают HTTP-метод и относительный URL
**Аннотации параметров**: определяют, как параметры метода преобразуются в части HTTP-запроса

---

## Key Features / Ключевые Возможности

### Automatic Conversion (EN)

Retrofit automatically converts responses using pluggable converters:

```kotlin
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.github.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val service = retrofit.create(GitHubService::class.java)
```

**Popular Converters**: Gson, Moshi, kotlinx.serialization, Jackson, Protobuf

### Автоматическое Преобразование (RU)

Retrofit автоматически конвертирует ответы с помощью подключаемых конвертеров (см. код выше).

**Популярные конвертеры**: Gson, Moshi, kotlinx.serialization, Jackson, Protobuf

### Call Adapters (EN)

Adapt return types to different execution models:

```kotlin
// Coroutines (built-in)
suspend fun getUser(): User

// Flow
@GET("users/{id}")
fun observeUser(@Path("id") id: String): Flow<User>

// RxJava
@GET("users/{id}")
fun getUserRx(@Path("id") id: String): Single<User>
```

### Call-адаптеры (RU)

Адаптируют возвращаемые типы к различным моделям выполнения (см. код выше).

---

## Integration / Интеграция

### OkHttp Integration (EN)

Retrofit uses OkHttp for network operations. Customize with interceptors:

```kotlin
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor { chain ->
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer $token")
            .build()
        chain.proceed(request)
    }
    .connectTimeout(30, TimeUnit.SECONDS)
    .build()

val retrofit = Retrofit.Builder()
    .client(okHttpClient)
    .baseUrl(BASE_URL)
    .addConverterFactory(MoshiConverterFactory.create())
    .build()
```

### Интеграция С OkHttp (RU)

Retrofit использует OkHttp для сетевых операций. Настройка через интерцепторы (см. код выше).

### Coroutines Support (EN)

Native `suspend` function support (Retrofit 2.6+):

```kotlin
interface ApiService {
    @GET("data")
    suspend fun getData(): Response<Data>
}

// Usage
viewModelScope.launch {
    try {
        val response = apiService.getData()
        if (response.isSuccessful) {
            // Handle data
        }
    } catch (e: Exception) {
        // Handle error
    }
}
```

### Поддержка Корутин (RU)

Встроенная поддержка `suspend` функций (Retrofit 2.6+), см. код выше.

---

## Best Practices / Лучшие Практики

### Error Handling (EN)

Use `Response<T>` wrapper for detailed error handling:

```kotlin
suspend fun fetchUser(): Result<User> {
    return try {
        val response = apiService.getUser()
        if (response.isSuccessful && response.body() != null) {
            Result.success(response.body()!!)
        } else {
            Result.failure(HttpException(response))
        }
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

### Обработка Ошибок (RU)

Используйте обёртку `Response<T>` для детальной обработки ошибок (см. код выше).

### Configuration (EN)

- **Base URL**: Must end with `/`, relative paths should not start with `/`
- **Timeouts**: Configure via OkHttpClient
- **Logging**: Use `HttpLoggingInterceptor` for debugging
- **Testing**: Use MockWebServer for unit tests

### Конфигурация (RU)

- **Base URL**: Должен заканчиваться на `/`, относительные пути не должны начинаться с `/`
- **Таймауты**: Настраиваются через OkHttpClient
- **Логирование**: Используйте `HttpLoggingInterceptor` для отладки
- **Тестирование**: Используйте MockWebServer для юнит-тестов

---

## Use Cases / Trade-offs

### When to Use
- REST API integration with type-safe interfaces
- Projects requiring automatic JSON serialization
- Apps needing interceptors for auth, logging, caching
- Modern Android apps with Coroutines/Flow support

### When to Consider Alternatives
- GraphQL APIs: Use Apollo Client instead
- gRPC: Use gRPC-Kotlin
- Simple HTTP calls: OkHttp alone may suffice
- WebSocket: Use OkHttp WebSocket directly

### Trade-offs
- **Pros**: Type safety, minimal boilerplate, extensive ecosystem, excellent Kotlin support
- **Cons**: Reflection overhead (mitigated by R8/ProGuard), learning curve for complex configurations
- **Performance**: Negligible overhead over raw OkHttp in production builds

---

## References

- [Official Documentation](https://square.github.io/retrofit/)
- [GitHub Repository](https://github.com/square/retrofit)
- [OkHttp Documentation](https://square.github.io/okhttp/)
- [Converter Factories](https://github.com/square/retrofit/tree/master/retrofit-converters)
- [Call Adapters](https://github.com/square/retrofit/tree/master/retrofit-adapters)

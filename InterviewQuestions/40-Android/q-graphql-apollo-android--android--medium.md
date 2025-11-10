---
id: android-167
title: GraphQL with Apollo Android / GraphQL с Apollo Android
aliases:
- GraphQL with Apollo Android
- GraphQL с Apollo Android
topic: android
subtopics:
- graphql
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-retrofit
- q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium
- q-play-app-signing--android--medium
- q-sharedpreferences-definition--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/graphql
- difficulty/medium
- graphql

---

# Вопрос (RU)
> GraphQL с Apollo Android

# Question (EN)
> GraphQL with Apollo Android

---

## Ответ (RU)
Apollo Android — это строго типизированный GraphQL-клиент для Android (и Kotlin Multiplatform), который предоставляет:
- Генерацию Kotlin-моделей и операций на основе GraphQL-схемы
- Типобезопасность на этапе компиляции
- Нормализованный кеш (in-memory, SQL и др.)
- Поддержку запросов, мутаций и подписок (через WebSocket)

Ниже — краткий, технически корректный обзор для интервью.

### Базовые концепции GraphQL

Ключевые отличия от REST:
- Как правило, один HTTP-эндпоинт для всех операций
- Клиент запрашивает ровно те поля, которые нужны (меньше over-fetching / under-fetching)
- Строго типизированная схема как контракт клиент–сервер
- Интроспекция (сама схема доступна через запросы)
- Три типа операций:
  - Query (чтение)
  - Mutation (запись)
  - Subscription (real-time обновления)

Примеры операций:

```graphql
# Query
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
  }
}

# Mutation
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    post {
      id
      title
      content
    }
  }
}

# Subscription
subscription OnPostCreated {
  postCreated {
    id
    title
    author {
      name
    }
  }
}
```

### Базовая настройка Apollo Android

Gradle-конфигурация (Apollo 3.x, версии примерные):

```kotlin
// build.gradle.kts (уровень проекта)
plugins {
    id("com.apollographql.apollo3") version "3.8.2" apply false
}

// build.gradle.kts (модуль app)
plugins {
    id("com.apollographql.apollo3")
}

dependencies {
    implementation("com.apollographql.apollo3:apollo-runtime:3.8.2")
    implementation("com.apollographql.apollo3:apollo-normalized-cache:3.8.2")
    implementation("com.apollographql.apollo3:apollo-normalized-cache-sqlite:3.8.2")

    // Для подписок (WebSocket-транспорт)
    implementation("com.apollographql.apollo3:apollo-websocket-network-transport:3.8.2")

    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}

apollo {
    service("api") {
        packageName.set("com.example.graphql")
        schemaFile.set(file("src/main/graphql/schema.graphqls"))
    }
}
```

### Настройка клиента Apollo (HTTP + кеш + авторизация)

```kotlin
import android.content.Context
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.cache.normalized.api.MemoryCacheFactory
import com.apollographql.apollo3.cache.normalized.normalizedCache
import com.apollographql.apollo3.cache.normalized.sql.SqlNormalizedCacheFactory
import com.apollographql.apollo3.network.http.OkHttpEngine
import com.apollographql.apollo3.network.ws.ApolloWebSocketEngine
import com.apollographql.apollo3.network.ws.WebSocketNetworkTransport
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

interface TokenProvider {
    fun getAccessToken(): String?
}

class ApolloClientProviderEn(
    context: Context,
    private val tokenProvider: TokenProvider
) {
    companion object {
        private const val BASE_URL = "https://api.example.com/graphql"
        private const val WS_URL = "wss://api.example.com/graphql"
        private const val MEMORY_CACHE_SIZE = 10L * 1024 * 1024 // 10MB
    }

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .addInterceptor { chain ->
            val original = chain.request()
            val builder = original.newBuilder()
            tokenProvider.getAccessToken()?.let { token ->
                builder.addHeader("Authorization", "Bearer $token")
            }
            chain.proceed(builder.build())
        }
        .build()

    private val cacheFactory = MemoryCacheFactory(MEMORY_CACHE_SIZE)
        .chain(SqlNormalizedCacheFactory(context, "apollo.db"))

    // Клиент для запросов/мутаций
    val apolloClient: ApolloClient = ApolloClient.Builder()
        .serverUrl(BASE_URL)
        .httpEngine(OkHttpEngine(okHttpClient))
        .normalizedCache(cacheFactory)
        .build()

    // Клиент с поддержкой подписок через WebSocket
    val apolloClientWithSubscriptions: ApolloClient = ApolloClient.Builder()
        .serverUrl(BASE_URL)
        .httpEngine(OkHttpEngine(okHttpClient))
        .subscriptionNetworkTransport(
            WebSocketNetworkTransport(
                serverUrl = WS_URL,
                webSocketEngine = ApolloWebSocketEngine(okHttpClient)
            )
        )
        .normalizedCache(cacheFactory)
        .build()
}
```

Примечания:
- Используйте OkHttp через `OkHttpEngine` (или актуальный движок из документации Apollo).
- Зависимость `apollo-websocket-network-transport` используется для реализации подписок через WebSocket.

### Пример запроса

```graphql
# src/main/graphql/GetUser.graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    avatar
  }
}
```

```kotlin
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.exception.ApolloException

class UserRepositoryEn(private val apolloClient: ApolloClient) {

    suspend fun getUser(userId: String): Result<GetUserQuery.User?> {
        return try {
            val response = apolloClient
                .query(GetUserQuery(id = userId))
                .execute()

            if (response.hasErrors()) {
                Result.failure(
                    IllegalStateException(response.errors?.firstOrNull()?.message)
                )
            } else {
                Result.success(response.data?.user)
            }
        } catch (e: ApolloException) {
            Result.failure(e)
        }
    }
}
```

### Мутации и оптимистичные обновления

```graphql
# src/main/graphql/LikePost.graphql
mutation LikePost($id: ID!) {
  likePost(id: $id) {
    post {
      id
      likes
    }
  }
}
```

```kotlin
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.cache.normalized.optimisticUpdates
import com.apollographql.apollo3.exception.ApolloException

suspend fun likePostEn(apolloClient: ApolloClient, postId: String): Result<Int> {
    return try {
        // Читаем текущее значение лайков из кеша (если есть)
        val cached = apolloClient.apolloStore.readOperation(GetPostQuery(id = postId))
        val currentLikes = cached?.post?.likes ?: 0

        val response = apolloClient
            .mutation(LikePostMutation(id = postId))
            .optimisticUpdates(
                LikePostMutation.Data(
                    likePost = LikePostMutation.LikePost(
                        post = LikePostMutation.Post(
                            id = postId,
                            likes = currentLikes + 1
                        )
                    )
                )
            )
            .execute()

        if (response.hasErrors()) {
            Result.failure(IllegalStateException(response.errors?.firstOrNull()?.message))
        } else {
            Result.success(response.data?.likePost?.post?.likes ?: currentLikes + 1)
        }
    } catch (e: ApolloException) {
        Result.failure(e)
    }
}
```

### Подписки (`Flow`)

```kotlin
import com.apollographql.apollo3.ApolloClient
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

fun subscribeToNewPostsEn(client: ApolloClient): Flow<OnPostCreatedSubscription.PostCreated?> {
    return client
        .subscription(OnPostCreatedSubscription())
        .toFlow()
        .map { response ->
            response.data?.postCreated
        }
}
```

### Нормализованный кеш и политики выборки

Apollo нормализует объекты по ключам (например, `User:123`) и переиспользует их во всех связанных запросах. Обновление одной сущности автоматически отражается во всех запросах, которые на неё ссылаются.

Используйте встроенные политики выборки Apollo, например:

```kotlin
import com.apollographql.apollo3.cache.normalized.FetchPolicy
import com.apollographql.apollo3.cache.normalized.fetchPolicy

suspend fun getUserCacheFirstEn(client: ApolloClient, userId: String): GetUserQuery.User? {
    val response = client
        .query(GetUserQuery(id = userId))
        .fetchPolicy(FetchPolicy.CacheFirst)
        .execute()
    return response.data?.user
}
```

### Обработка ошибок (паттерн)

```kotlin
import com.apollographql.apollo3.api.ApolloResponse
import com.apollographql.apollo3.exception.*

sealed class GraphQLResultEn<out T> {
    data class Success<T>(val data: T) : GraphQLResultEn<T>()
    data class Error(val error: GraphQLErrorEn) : GraphQLResultEn<Nothing>()
}

sealed class GraphQLErrorEn {
    data class Network(val message: String) : GraphQLErrorEn()
    data class Http(val code: Int, val message: String) : GraphQLErrorEn()
    data class GraphQL(val errors: List<String>) : GraphQLErrorEn()
    data class Parse(val message: String) : GraphQLErrorEn()
    data class Unknown(val throwable: Throwable) : GraphQLErrorEn()
}

suspend fun <T> executeApolloEn(
    block: suspend () -> ApolloResponse<T>
): GraphQLResultEn<T> {
    return try {
        val response = block()
        when {
            response.data != null && !response.hasErrors() ->
                GraphQLResultEn.Success(response.data!!)
            response.hasErrors() -> {
                val msgs = response.errors?.map { it.message } ?: emptyList()
                GraphQLResultEn.Error(GraphQLErrorEn.GraphQL(msgs))
            }
            else -> GraphQLResultEn.Error(GraphQLErrorEn.Unknown(Exception("Unknown error")))
        }
    } catch (e: ApolloNetworkException) {
        GraphQLResultEn.Error(GraphQLErrorEn.Network(e.message ?: "Network error"))
    } catch (e: ApolloHttpException) {
        GraphQLResultEn.Error(GraphQLErrorEn.Http(e.statusCode, e.message ?: "HTTP error"))
    } catch (e: ApolloParseException) {
        GraphQLResultEn.Error(GraphQLErrorEn.Parse(e.message ?: "Parse error"))
    } catch (e: ApolloException) {
        GraphQLResultEn.Error(GraphQLErrorEn.Unknown(e))
    }
}
```

### Лучшие практики (RU)

- Использовать фрагменты для переиспользуемых наборов полей.
- Использовать нормализованный кеш; обеспечить стабильные ID.
- Всегда проверять `response.hasErrors()` (а не только `data`).
- Подбирать `FetchPolicy` под сценарий использования.
- Применять оптимистичные обновления для отзывчивого UI.
- Использовать `watch`/`Flow` или другие реактивные подходы для UI, который реагирует на изменения кеша.
- Для подписок использовать структурированную конкурентность и привязку к жизненному циклу (`ViewModel`, `lifecycleScope` и т.п.), корректно отменяя коллекции и WebSocket-подключения.

---

## Answer (EN)
Apollo Android is a strongly-typed GraphQL client for Android (and Kotlin multiplatform) that provides:
- Generated Kotlin models and operations from your GraphQL schema
- Compile-time type safety
- Normalized cache with multiple backends (in-memory, SQL, etc.)
- Support for queries, mutations, and subscriptions (via WebSocket)

Below is a concise, technically correct overview suitable for interview context.

### GraphQL Core Concepts

Key differences from REST:
- Single endpoint: most GraphQL APIs expose one HTTP endpoint
- Client specifies exact shape of data: avoids over-fetching / under-fetching
- Strongly typed schema: contract between client and server
- Introspection: schema is queryable
- First-class support for:
  - Queries (read)
  - Mutations (write)
  - Subscriptions (real-time)

Example operations:

```graphql
# Query
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
  }
}

# Mutation
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    post {
      id
      title
      content
    }
  }
}

# Subscription
subscription OnPostCreated {
  postCreated {
    id
    title
    author {
      name
    }
  }
}
```

### Basic Apollo Android Setup

Gradle configuration (Apollo 3.x style, versions illustrative):

```kotlin
// build.gradle.kts (project level)
plugins {
    id("com.apollographql.apollo3") version "3.8.2" apply false
}

// build.gradle.kts (app module)
plugins {
    id("com.apollographql.apollo3")
}

dependencies {
    implementation("com.apollographql.apollo3:apollo-runtime:3.8.2")
    implementation("com.apollographql.apollo3:apollo-normalized-cache:3.8.2")
    implementation("com.apollographql.apollo3:apollo-normalized-cache-sqlite:3.8.2")

    // For subscriptions (WebSocket transport)
    implementation("com.apollographql.apollo3:apollo-websocket-network-transport:3.8.2")

    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}

apollo {
    service("api") {
        packageName.set("com.example.graphql")
        schemaFile.set(file("src/main/graphql/schema.graphqls"))
    }
}
```

### Apollo Client Setup (HTTP + Cache + Auth)

```kotlin
import android.content.Context
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.cache.normalized.normalizedCache
import com.apollographql.apollo3.cache.normalized.api.MemoryCacheFactory
import com.apollographql.apollo3.cache.normalized.sql.SqlNormalizedCacheFactory
import com.apollographql.apollo3.network.http.OkHttpEngine
import com.apollographql.apollo3.network.ws.ApolloWebSocketEngine
import com.apollographql.apollo3.network.ws.WebSocketNetworkTransport
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

interface TokenProviderEn {
    fun getAccessToken(): String?
}

class ApolloClientProviderEn2(
    context: Context,
    private val tokenProvider: TokenProviderEn
) {
    companion object {
        private const val BASE_URL = "https://api.example.com/graphql"
        private const val WS_URL = "wss://api.example.com/graphql"
        private const val MEMORY_CACHE_SIZE = 10L * 1024 * 1024 // 10MB
    }

    private val okHttpClient: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .addInterceptor { chain ->
            val original = chain.request()
            val builder = original.newBuilder()
            tokenProvider.getAccessToken()?.let { token ->
                builder.addHeader("Authorization", "Bearer $token")
            }
            chain.proceed(builder.build())
        }
        .build()

    private val cacheFactory = MemoryCacheFactory(MEMORY_CACHE_SIZE)
        .chain(SqlNormalizedCacheFactory(context, "apollo.db"))

    val apolloClient: ApolloClient = ApolloClient.Builder()
        .serverUrl(BASE_URL)
        .httpEngine(OkHttpEngine(okHttpClient))
        .normalizedCache(cacheFactory)
        .build()

    val apolloClientWithSubscriptions: ApolloClient = ApolloClient.Builder()
        .serverUrl(BASE_URL)
        .httpEngine(OkHttpEngine(okHttpClient))
        .subscriptionNetworkTransport(
            WebSocketNetworkTransport(
                serverUrl = WS_URL,
                webSocketEngine = ApolloWebSocketEngine(okHttpClient)
            )
        )
        .normalizedCache(cacheFactory)
        .build()
}
```

Notes:
- Use OkHttp via `OkHttpEngine` (or the current engine recommended by Apollo docs).
- Use `apollo-websocket-network-transport` (or equivalent) for subscriptions.

### Queries Example

```graphql
# src/main/graphql/GetUser.graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    avatar
  }
}
```

```kotlin
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.exception.ApolloException

class UserRepositoryEn2(private val apolloClient: ApolloClient) {

    suspend fun getUser(userId: String): Result<GetUserQuery.User?> {
        return try {
            val response = apolloClient
                .query(GetUserQuery(id = userId))
                .execute()

            if (response.hasErrors()) {
                Result.failure(
                    IllegalStateException(response.errors?.firstOrNull()?.message)
                )
            } else {
                Result.success(response.data?.user)
            }
        } catch (e: ApolloException) {
            Result.failure(e)
        }
    }
}
```

### Mutations and Optimistic Updates

```graphql
# src/main/graphql/LikePost.graphql
mutation LikePost($id: ID!) {
  likePost(id: $id) {
    post {
      id
      likes
    }
  }
}
```

```kotlin
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.cache.normalized.optimisticUpdates
import com.apollographql.apollo3.exception.ApolloException

suspend fun likePostEn2(apolloClient: ApolloClient, postId: String): Result<Int> {
    return try {
        // Read current likes from cache (if available)
        val cached = apolloClient.apolloStore.readOperation(GetPostQuery(id = postId))
        val currentLikes = cached?.post?.likes ?: 0

        val response = apolloClient
            .mutation(LikePostMutation(id = postId))
            .optimisticUpdates(
                LikePostMutation.Data(
                    likePost = LikePostMutation.LikePost(
                        post = LikePostMutation.Post(
                            id = postId,
                            likes = currentLikes + 1
                        )
                    )
                )
            )
            .execute()

        if (response.hasErrors()) {
            Result.failure(IllegalStateException(response.errors?.firstOrNull()?.message))
        } else {
            Result.success(response.data?.likePost?.post?.likes ?: currentLikes + 1)
        }
    } catch (e: ApolloException) {
        Result.failure(e)
    }
}
```

### Subscriptions (`Flow`)

```kotlin
import com.apollographql.apollo3.ApolloClient
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

fun subscribeToNewPostsEn2(client: ApolloClient): Flow<OnPostCreatedSubscription.PostCreated?> {
    return client
        .subscription(OnPostCreatedSubscription())
        .toFlow()
        .map { response ->
            response.data?.postCreated
        }
}
```

### Normalized Cache and Fetch Policies

Apollo stores entities by cache key (e.g. `User:123`) and references them from other records. Updates to one entity propagate to all queries that reference it.

Use Apollo's built-in fetch policies, for example:

```kotlin
import com.apollographql.apollo3.cache.normalized.FetchPolicy
import com.apollographql.apollo3.cache.normalized.fetchPolicy

suspend fun getUserCacheFirstEn2(client: ApolloClient, userId: String): GetUserQuery.User? {
    val response = client
        .query(GetUserQuery(id = userId))
        .fetchPolicy(FetchPolicy.CacheFirst)
        .execute()
    return response.data?.user
}
```

### Error Handling (Pattern)

```kotlin
import com.apollographql.apollo3.api.ApolloResponse
import com.apollographql.apollo3.exception.*

sealed class GraphQLResultEn2<out T> {
    data class Success<T>(val data: T) : GraphQLResultEn2<T>()
    data class Error(val error: GraphQLErrorEn2) : GraphQLResultEn2<Nothing>()
}

sealed class GraphQLErrorEn2 {
    data class Network(val message: String) : GraphQLErrorEn2()
    data class Http(val code: Int, val message: String) : GraphQLErrorEn2()
    data class GraphQL(val errors: List<String>) : GraphQLErrorEn2()
    data class Parse(val message: String) : GraphQLErrorEn2()
    data class Unknown(val throwable: Throwable) : GraphQLErrorEn2()
}

suspend fun <T> executeApolloEn2(
    block: suspend () -> ApolloResponse<T>
): GraphQLResultEn2<T> {
    return try {
        val response = block()
        when {
            response.data != null && !response.hasErrors() ->
                GraphQLResultEn2.Success(response.data!!)
            response.hasErrors() -> {
                val msgs = response.errors?.map { it.message } ?: emptyList()
                GraphQLResultEn2.Error(GraphQLErrorEn2.GraphQL(msgs))
            }
            else -> GraphQLResultEn2.Error(GraphQLErrorEn2.Unknown(Exception("Unknown error")))
        }
    } catch (e: ApolloNetworkException) {
        GraphQLResultEn2.Error(GraphQLErrorEn2.Network(e.message ?: "Network error"))
    } catch (e: ApolloHttpException) {
        GraphQLResultEn2.Error(GraphQLErrorEn2.Http(e.statusCode, e.message ?: "HTTP error"))
    } catch (e: ApolloParseException) {
        GraphQLResultEn2.Error(GraphQLErrorEn2.Parse(e.message ?: "Parse error"))
    } catch (e: ApolloException) {
        GraphQLResultEn2.Error(GraphQLErrorEn2.Unknown(e))
    }
}
```

### Best Practices (EN)

- Use fragments for reusable field sets.
- Prefer normalized cache; ensure stable IDs are present.
- Always check for `response.hasErrors()` (not just `data`).
- Use appropriate `FetchPolicy` per use case.
- Use optimistic updates for responsive mutations.
- Use `watch`/Flows or other reactive patterns for UI that reacts to cache changes.
- Clean up / cancel subscriptions via structured concurrency and lifecycle-aware collectors.

---

## Дополнительные вопросы (RU)

- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]]
- [[q-play-app-signing--android--medium]]
- [[q-sharedpreferences-definition--android--easy]]

## Follow-ups (EN)

- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]]
- [[q-play-app-signing--android--medium]]
- [[q-sharedpreferences-definition--android--easy]]

## Ссылки (RU)

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)

## References (EN)

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-retrofit]]

### Предпосылки (проще)
- [[q-graphql-vs-rest--networking--easy]] - Networking

### Связанные (средней сложности)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-kmm-ktor-networking--android--medium]] - Networking
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking
- [[q-network-error-handling-strategies--networking--medium]] - Networking
- [[q-okhttp-interceptors-advanced--networking--medium]] - Networking

### Продвинутые (сложнее)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-network-request-deduplication--networking--hard]] - Networking

## Related Questions (EN)

### Prerequisites / Concepts

- [[c-retrofit]]

### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - Networking

### Related (Medium)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-kmm-ktor-networking--android--medium]] - Networking
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking
- [[q-network-error-handling-strategies--networking--medium]] - Networking
- [[q-okhttp-interceptors-advanced--networking--medium]] - Networking

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-network-request-deduplication--networking--hard]] - Networking

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
- q-android-lint-tool--android--medium
- q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium
- q-main-thread-android--android--medium
- q-parsing-optimization-android--android--medium
- q-play-app-signing--android--medium
- q-sharedpreferences-definition--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/graphql
- difficulty/medium
- graphql
anki_cards:
- slug: android-167-0-en
  language: en
  anki_id: 1768367360982
  synced_at: '2026-01-14T09:17:53.127522'
- slug: android-167-0-ru
  language: ru
  anki_id: 1768367361007
  synced_at: '2026-01-14T09:17:53.130110'
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

### Базовые Концепции GraphQL

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

### Базовая Настройка Apollo Android

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

### Настройка Клиента Apollo (HTTP + Кеш + авторизация)

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

class ApolloClientProvider(
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
- Используйте `OkHttp` через `OkHttpEngine` (или актуальный движок из документации Apollo для используемой версии).
- Зависимость `apollo-websocket-network-transport` используется для реализации подписок через WebSocket.

### Пример Запроса

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

class UserRepository(private val apolloClient: ApolloClient) {

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

### Мутации И Оптимистичные Обновления

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

suspend fun likePost(
    apolloClient: ApolloClient,
    postId: String
): Result<Int> {
    return try {
        // Читаем текущее значение лайков из кеша (если есть соответствующий запрос, например GetPostQuery)
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

fun subscribeToNewPosts(client: ApolloClient): Flow<OnPostCreatedSubscription.PostCreated?> {
    return client
        .subscription(OnPostCreatedSubscription())
        .toFlow()
        .map { response ->
            response.data?.postCreated
        }
}
```

### Нормализованный Кеш И Политики Выборки

Apollo нормализует объекты по ключам (например, `User:123`) и переиспользует их во всех связанных запросах. Обновление одной сущности автоматически отражается во всех запросах, которые на неё ссылаются.

Используйте встроенные политики выборки Apollo, например:

```kotlin
import com.apollographql.apollo3.cache.normalized.FetchPolicy
import com.apollographql.apollo3.cache.normalized.fetchPolicy

suspend fun getUserCacheFirst(client: ApolloClient, userId: String): GetUserQuery.User? {
    val response = client
        .query(GetUserQuery(id = userId))
        .fetchPolicy(FetchPolicy.CacheFirst)
        .execute()
    return response.data?.user
}
```

### Обработка Ошибок (паттерн)

```kotlin
import com.apollographql.apollo3.api.ApolloResponse
import com.apollographql.apollo3.exception.*

sealed class GraphQLResult<out T> {
    data class Success<T>(val data: T) : GraphQLResult<T>()
    data class Error(val error: GraphQLError) : GraphQLResult<Nothing>()
}

sealed class GraphQLError {
    data class Network(val message: String) : GraphQLError()
    data class Http(val code: Int, val message: String) : GraphQLError()
    data class GraphQL(val errors: List<String>) : GraphQLError()
    data class Parse(val message: String) : GraphQLError()
    data class Unknown(val throwable: Throwable) : GraphQLError()
}

suspend fun <T> executeApollo(
    block: suspend () -> ApolloResponse<T>
): GraphQLResult<T> {
    return try {
        val response = block()
        when {
            response.data != null && !response.hasErrors() ->
                GraphQLResult.Success(response.data!!)
            response.hasErrors() -> {
                val msgs = response.errors?.map { it.message } ?: emptyList()
                GraphQLResult.Error(GraphQLError.GraphQL(msgs))
            }
            else -> GraphQLResult.Error(GraphQLError.Unknown(Exception("Unknown error")))
        }
    } catch (e: ApolloNetworkException) {
        GraphQLResult.Error(GraphQLError.Network(e.message ?: "Network error"))
    } catch (e: ApolloHttpException) {
        GraphQLResult.Error(GraphQLError.Http(e.statusCode, e.message ?: "HTTP error"))
    } catch (e: ApolloParseException) {
        GraphQLResult.Error(GraphQLError.Parse(e.message ?: "Parse error"))
    } catch (e: ApolloException) {
        GraphQLResult.Error(GraphQLError.Unknown(e))
    }
}
```

### Лучшие Практики (RU)

- Использовать фрагменты для переиспользуемых наборов полей.
- Использовать нормализованный кеш; обеспечить стабильные ID.
- Всегда проверять `response.hasErrors()` (а не только `data`).
- Подбирать `FetchPolicy` под сценарий использования.
- Применять оптимистичные обновления для отзывчивого UI.
- Использовать `watch`/`Flow` или другие реактивные подходы для UI, который реагирует на изменения кеша.
- Для подписок использовать структурированную конкурентность и привязку к жизненному циклу (`ViewModel`, `lifecycleScope` и т.п.), корректно отменяя коллекции и WebSocket-подключения.

---

## Answer (EN)
Apollo Android is a strongly-typed GraphQL client for Android (and Kotlin Multiplatform) that provides:
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

class ApolloClientProvider(
    context: Context,
    private val tokenProvider: TokenProvider
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

    // Client for queries/mutations
    val apolloClient: ApolloClient = ApolloClient.Builder()
        .serverUrl(BASE_URL)
        .httpEngine(OkHttpEngine(okHttpClient))
        .normalizedCache(cacheFactory)
        .build()

    // Client with WebSocket subscriptions
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
- Use `OkHttp` via `OkHttpEngine` (or the current engine recommended by Apollo docs for your version).
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

class UserRepository(private val apolloClient: ApolloClient) {

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

suspend fun likePost(
    apolloClient: ApolloClient,
    postId: String
): Result<Int> {
    return try {
        // Read current likes from cache (if there is a corresponding query such as GetPostQuery)
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

fun subscribeToNewPosts(client: ApolloClient): Flow<OnPostCreatedSubscription.PostCreated?> {
    return client
        .subscription(OnPostCreatedSubscription())
        .toFlow()
        .map { response ->
            response.data?.postCreated
        }
}
```

### Normalized Cache and Fetch Policies

Apollo stores entities by cache key (e.g. `User:123`) and shares them across all queries. Updating one entity automatically affects all queries that reference it.

Use Apollo's built-in fetch policies, for example:

```kotlin
import com.apollographql.apollo3.cache.normalized.FetchPolicy
import com.apollographql.apollo3.cache.normalized.fetchPolicy

suspend fun getUserCacheFirst(client: ApolloClient, userId: String): GetUserQuery.User? {
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

sealed class GraphQLResult<out T> {
    data class Success<T>(val data: T) : GraphQLResult<T>()
    data class Error(val error: GraphQLError) : GraphQLResult<Nothing>()
}

sealed class GraphQLError {
    data class Network(val message: String) : GraphQLError()
    data class Http(val code: Int, val message: String) : GraphQLError()
    data class GraphQL(val errors: List<String>) : GraphQLError()
    data class Parse(val message: String) : GraphQLError()
    data class Unknown(val throwable: Throwable) : GraphQLError()
}

suspend fun <T> executeApollo(
    block: suspend () -> ApolloResponse<T>
): GraphQLResult<T> {
    return try {
        val response = block()
        when {
            response.data != null && !response.hasErrors() ->
                GraphQLResult.Success(response.data!!)
            response.hasErrors() -> {
                val msgs = response.errors?.map { it.message } ?: emptyList()
                GraphQLResult.Error(GraphQLError.GraphQL(msgs))
            }
            else -> GraphQLResult.Error(GraphQLError.Unknown(Exception("Unknown error")))
        }
    } catch (e: ApolloNetworkException) {
        GraphQLResult.Error(GraphQLError.Network(e.message ?: "Network error"))
    } catch (e: ApolloHttpException) {
        GraphQLResult.Error(GraphQLError.Http(e.statusCode, e.message ?: "HTTP error"))
    } catch (e: ApolloParseException) {
        GraphQLResult.Error(GraphQLError.Parse(e.message ?: "Parse error"))
    } catch (e: ApolloException) {
        GraphQLResult.Error(GraphQLError.Unknown(e))
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

## Дополнительные Вопросы (RU)

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

## Связанные Вопросы (RU)

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

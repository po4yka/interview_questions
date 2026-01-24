---
id: android-753
title: "Apollo GraphQL Client on Android / Apollo GraphQL клиент на Android"
aliases: ["Apollo GraphQL Client on Android", "Apollo GraphQL клиент на Android"]
topic: android
subtopics: [networking]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-networking, q-retrofit-library--android--medium, q-graphql-apollo-android--android--medium]
created: 2026-01-23
updated: 2026-01-23
sources: ["https://www.apollographql.com/docs/kotlin/", "https://graphql.org/learn/", "https://www.apollographql.com/docs/kotlin/caching/normalized-caches"]
tags: [android/networking, difficulty/medium, graphql, apollo, queries, mutations, subscriptions, caching]

---
# Вопрос (RU)

> Как использовать Apollo GraphQL клиент на Android? Объясните queries, mutations, subscriptions и нормализованный кеш.

# Question (EN)

> How do you use Apollo GraphQL client on Android? Explain queries, mutations, subscriptions, and normalized cache.

---

## Ответ (RU)

**Apollo Kotlin** - строго типизированный GraphQL-клиент для Android и Kotlin Multiplatform, генерирующий Kotlin-код из GraphQL-схемы. Обеспечивает типобезопасность на этапе компиляции и встроенную поддержку кеширования.

### Краткий Ответ

- **Apollo Kotlin** генерирует типизированные модели из GraphQL-схемы
- **Три типа операций**: Query (чтение), Mutation (запись), Subscription (real-time)
- **Нормализованный кеш** автоматически обновляет связанные данные
- Используйте **Flow** для реактивного UI с `watch()` и subscriptions

### Подробный Ответ

### Основы GraphQL

GraphQL - язык запросов для API, позволяющий клиенту указать точную структуру нужных данных:

```graphql
# Query - запрос данных
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    posts {
      id
      title
    }
  }
}

# Mutation - изменение данных
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    author {
      id
      name
    }
  }
}

# Subscription - real-time обновления
subscription OnNewMessage($chatId: ID!) {
  messageAdded(chatId: $chatId) {
    id
    content
    sender {
      name
    }
  }
}
```

### Настройка Gradle (Apollo Kotlin 4.x)

```kotlin
// build.gradle.kts (project)
plugins {
    id("com.apollographql.apollo") version "4.0.0" apply false
}

// build.gradle.kts (app module)
plugins {
    id("com.apollographql.apollo")
}

dependencies {
    // Apollo runtime
    implementation("com.apollographql.apollo:apollo-runtime:4.0.0")

    // Normalized cache
    implementation("com.apollographql.apollo:apollo-normalized-cache:4.0.0")
    implementation("com.apollographql.apollo:apollo-normalized-cache-sqlite:4.0.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.0")
}

apollo {
    service("api") {
        packageName.set("com.example.graphql")
        // Схема загружается из файла или URL
        schemaFile.set(file("src/main/graphql/schema.graphqls"))

        // Introspection (для разработки)
        introspection {
            endpointUrl.set("https://api.example.com/graphql")
            schemaFile.set(file("src/main/graphql/schema.graphqls"))
        }
    }
}
```

### Создание Apollo Client

```kotlin
class ApolloClientProvider @Inject constructor(
    @ApplicationContext private val context: Context,
    private val tokenProvider: TokenProvider
) {
    // Memory + SQLite cache
    private val cacheFactory = MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024)
        .chain(SqlNormalizedCacheFactory(context, "apollo_cache.db"))

    val apolloClient: ApolloClient = ApolloClient.Builder()
        .serverUrl("https://api.example.com/graphql")
        .normalizedCache(cacheFactory)
        // HTTP interceptor для авторизации
        .addHttpInterceptor(object : HttpInterceptor {
            override suspend fun intercept(
                request: HttpRequest,
                chain: HttpInterceptorChain
            ): HttpResponse {
                val token = tokenProvider.getAccessToken()
                val newRequest = request.newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
                return chain.proceed(newRequest)
            }
        })
        // WebSocket для subscriptions
        .webSocketServerUrl("wss://api.example.com/graphql")
        .build()
}
```

### Queries

```graphql
# src/main/graphql/GetUser.graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    avatar
    posts {
      id
      title
    }
  }
}
```

```kotlin
class UserRepository @Inject constructor(
    private val apolloClient: ApolloClient
) {
    // Простой запрос
    suspend fun getUser(userId: String): Result<GetUserQuery.User> {
        return try {
            val response = apolloClient.query(GetUserQuery(userId)).execute()

            if (response.hasErrors()) {
                Result.failure(GraphQLException(response.errors!!))
            } else {
                response.data?.user?.let {
                    Result.success(it)
                } ?: Result.failure(NotFoundException("User not found"))
            }
        } catch (e: ApolloException) {
            Result.failure(e)
        }
    }

    // Запрос с Fetch Policy
    suspend fun getUserCacheFirst(userId: String): GetUserQuery.User? {
        return apolloClient.query(GetUserQuery(userId))
            .fetchPolicy(FetchPolicy.CacheFirst)
            .execute()
            .data?.user
    }

    // Watch - реактивное наблюдение за изменениями в кеше
    fun watchUser(userId: String): Flow<GetUserQuery.User?> {
        return apolloClient.query(GetUserQuery(userId))
            .watch()
            .map { response -> response.data?.user }
    }
}
```

### Mutations

```graphql
# src/main/graphql/CreatePost.graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    content
    author {
      id
      name
    }
  }
}
```

```kotlin
class PostRepository @Inject constructor(
    private val apolloClient: ApolloClient
) {
    suspend fun createPost(title: String, content: String): Result<CreatePostMutation.CreatePost> {
        return try {
            val input = CreatePostInput(
                title = title,
                content = content
            )

            val response = apolloClient.mutation(CreatePostMutation(input)).execute()

            if (response.hasErrors()) {
                Result.failure(GraphQLException(response.errors!!))
            } else {
                response.data?.createPost?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Create failed"))
            }
        } catch (e: ApolloException) {
            Result.failure(e)
        }
    }

    // Mutation с оптимистичным обновлением
    suspend fun likePost(postId: String, currentLikes: Int): Result<Int> {
        return try {
            val response = apolloClient.mutation(LikePostMutation(postId))
                .optimisticUpdates(
                    LikePostMutation.Data(
                        likePost = LikePostMutation.LikePost(
                            __typename = "Post",
                            id = postId,
                            likes = currentLikes + 1
                        )
                    )
                )
                .execute()

            response.data?.likePost?.likes?.let {
                Result.success(it)
            } ?: Result.failure(Exception("Like failed"))
        } catch (e: ApolloException) {
            Result.failure(e)
        }
    }
}
```

### Subscriptions

```graphql
# src/main/graphql/OnNewMessage.graphql
subscription OnNewMessage($chatId: ID!) {
  messageAdded(chatId: $chatId) {
    id
    content
    createdAt
    sender {
      id
      name
      avatar
    }
  }
}
```

```kotlin
class ChatRepository @Inject constructor(
    private val apolloClient: ApolloClient
) {
    fun subscribeToMessages(chatId: String): Flow<OnNewMessageSubscription.MessageAdded> {
        return apolloClient.subscription(OnNewMessageSubscription(chatId))
            .toFlow()
            .mapNotNull { response ->
                response.data?.messageAdded
            }
    }
}

// Использование в ViewModel
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository
) : ViewModel() {

    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages.asStateFlow()

    fun subscribeToChat(chatId: String) {
        viewModelScope.launch {
            chatRepository.subscribeToMessages(chatId)
                .catch { e -> /* handle error */ }
                .collect { newMessage ->
                    _messages.update { currentMessages ->
                        currentMessages + newMessage.toMessage()
                    }
                }
        }
    }
}
```

### Нормализованный Кеш

Apollo нормализует данные по ключам (например, `User:123`), автоматически обновляя все связанные запросы:

```kotlin
// Конфигурация кеша
val apolloClient = ApolloClient.Builder()
    .serverUrl("https://api.example.com/graphql")
    .normalizedCache(
        MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024)
            .chain(SqlNormalizedCacheFactory(context, "apollo.db"))
    )
    // Кастомный cache key resolver
    .cacheKeyGenerator(object : CacheKeyGenerator {
        override fun cacheKeyForObject(
            obj: Map<String, Any?>,
            context: CacheKeyGeneratorContext
        ): CacheKey? {
            val typename = obj["__typename"] as? String
            val id = obj["id"] as? String
            return if (typename != null && id != null) {
                CacheKey(typename, id)
            } else {
                null
            }
        }
    })
    .build()
```

### Fetch Policies

```kotlin
// CacheFirst - сначала кеш, потом сеть если нет в кеше
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.CacheFirst)

// NetworkFirst - сначала сеть, потом кеш при ошибке
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.NetworkFirst)

// CacheOnly - только из кеша
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.CacheOnly)

// NetworkOnly - только из сети
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.NetworkOnly)

// CacheAndNetwork - возвращает и кеш, и сеть (два результата)
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.CacheAndNetwork)
```

### Обработка Ошибок

```kotlin
sealed class GraphQLResult<out T> {
    data class Success<T>(val data: T) : GraphQLResult<T>()
    data class GraphQLError(val errors: List<Error>) : GraphQLResult<Nothing>()
    data class NetworkError(val exception: Throwable) : GraphQLResult<Nothing>()
}

suspend fun <D : Query.Data> ApolloClient.safeQuery(
    query: Query<D>
): GraphQLResult<D> {
    return try {
        val response = query(query).execute()
        when {
            response.hasErrors() -> GraphQLResult.GraphQLError(response.errors!!)
            response.data != null -> GraphQLResult.Success(response.data!!)
            else -> GraphQLResult.NetworkError(Exception("No data"))
        }
    } catch (e: ApolloNetworkException) {
        GraphQLResult.NetworkError(e)
    } catch (e: ApolloException) {
        GraphQLResult.NetworkError(e)
    }
}
```

### Лучшие Практики

1. **Fragments** - используйте для переиспользования полей между запросами
2. **Нормализованный кеш** - обеспечьте стабильные ID для всех типов
3. **watch()** - используйте для автоматического обновления UI при изменениях кеша
4. **Fetch Policy** - выбирайте стратегию под конкретный use case
5. **Оптимистичные обновления** - для мгновенного отклика UI
6. **Error handling** - всегда проверяйте `hasErrors()` и `data`

---

## Answer (EN)

**Apollo Kotlin** is a strongly-typed GraphQL client for Android and Kotlin Multiplatform that generates Kotlin code from your GraphQL schema. It provides compile-time type safety and built-in caching support.

### Short Version

- **Apollo Kotlin** generates typed models from GraphQL schema
- **Three operation types**: Query (read), Mutation (write), Subscription (real-time)
- **Normalized cache** automatically updates related data
- Use **Flow** for reactive UI with `watch()` and subscriptions

### Detailed Version

### GraphQL Basics

GraphQL is a query language for APIs that lets clients specify the exact structure of data needed:

```graphql
# Query - fetch data
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    posts {
      id
      title
    }
  }
}

# Mutation - modify data
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    author {
      id
      name
    }
  }
}

# Subscription - real-time updates
subscription OnNewMessage($chatId: ID!) {
  messageAdded(chatId: $chatId) {
    id
    content
    sender {
      name
    }
  }
}
```

### Gradle Setup (Apollo Kotlin 4.x)

```kotlin
// build.gradle.kts (project)
plugins {
    id("com.apollographql.apollo") version "4.0.0" apply false
}

// build.gradle.kts (app module)
plugins {
    id("com.apollographql.apollo")
}

dependencies {
    // Apollo runtime
    implementation("com.apollographql.apollo:apollo-runtime:4.0.0")

    // Normalized cache
    implementation("com.apollographql.apollo:apollo-normalized-cache:4.0.0")
    implementation("com.apollographql.apollo:apollo-normalized-cache-sqlite:4.0.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.0")
}

apollo {
    service("api") {
        packageName.set("com.example.graphql")
        // Schema loaded from file or URL
        schemaFile.set(file("src/main/graphql/schema.graphqls"))

        // Introspection (for development)
        introspection {
            endpointUrl.set("https://api.example.com/graphql")
            schemaFile.set(file("src/main/graphql/schema.graphqls"))
        }
    }
}
```

### Creating Apollo Client

```kotlin
class ApolloClientProvider @Inject constructor(
    @ApplicationContext private val context: Context,
    private val tokenProvider: TokenProvider
) {
    // Memory + SQLite cache
    private val cacheFactory = MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024)
        .chain(SqlNormalizedCacheFactory(context, "apollo_cache.db"))

    val apolloClient: ApolloClient = ApolloClient.Builder()
        .serverUrl("https://api.example.com/graphql")
        .normalizedCache(cacheFactory)
        // HTTP interceptor for authorization
        .addHttpInterceptor(object : HttpInterceptor {
            override suspend fun intercept(
                request: HttpRequest,
                chain: HttpInterceptorChain
            ): HttpResponse {
                val token = tokenProvider.getAccessToken()
                val newRequest = request.newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
                return chain.proceed(newRequest)
            }
        })
        // WebSocket for subscriptions
        .webSocketServerUrl("wss://api.example.com/graphql")
        .build()
}
```

### Queries

```graphql
# src/main/graphql/GetUser.graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    avatar
    posts {
      id
      title
    }
  }
}
```

```kotlin
class UserRepository @Inject constructor(
    private val apolloClient: ApolloClient
) {
    // Simple query
    suspend fun getUser(userId: String): Result<GetUserQuery.User> {
        return try {
            val response = apolloClient.query(GetUserQuery(userId)).execute()

            if (response.hasErrors()) {
                Result.failure(GraphQLException(response.errors!!))
            } else {
                response.data?.user?.let {
                    Result.success(it)
                } ?: Result.failure(NotFoundException("User not found"))
            }
        } catch (e: ApolloException) {
            Result.failure(e)
        }
    }

    // Query with Fetch Policy
    suspend fun getUserCacheFirst(userId: String): GetUserQuery.User? {
        return apolloClient.query(GetUserQuery(userId))
            .fetchPolicy(FetchPolicy.CacheFirst)
            .execute()
            .data?.user
    }

    // Watch - reactive observation of cache changes
    fun watchUser(userId: String): Flow<GetUserQuery.User?> {
        return apolloClient.query(GetUserQuery(userId))
            .watch()
            .map { response -> response.data?.user }
    }
}
```

### Mutations

```graphql
# src/main/graphql/CreatePost.graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    content
    author {
      id
      name
    }
  }
}
```

```kotlin
class PostRepository @Inject constructor(
    private val apolloClient: ApolloClient
) {
    suspend fun createPost(title: String, content: String): Result<CreatePostMutation.CreatePost> {
        return try {
            val input = CreatePostInput(
                title = title,
                content = content
            )

            val response = apolloClient.mutation(CreatePostMutation(input)).execute()

            if (response.hasErrors()) {
                Result.failure(GraphQLException(response.errors!!))
            } else {
                response.data?.createPost?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Create failed"))
            }
        } catch (e: ApolloException) {
            Result.failure(e)
        }
    }

    // Mutation with optimistic update
    suspend fun likePost(postId: String, currentLikes: Int): Result<Int> {
        return try {
            val response = apolloClient.mutation(LikePostMutation(postId))
                .optimisticUpdates(
                    LikePostMutation.Data(
                        likePost = LikePostMutation.LikePost(
                            __typename = "Post",
                            id = postId,
                            likes = currentLikes + 1
                        )
                    )
                )
                .execute()

            response.data?.likePost?.likes?.let {
                Result.success(it)
            } ?: Result.failure(Exception("Like failed"))
        } catch (e: ApolloException) {
            Result.failure(e)
        }
    }
}
```

### Subscriptions

```graphql
# src/main/graphql/OnNewMessage.graphql
subscription OnNewMessage($chatId: ID!) {
  messageAdded(chatId: $chatId) {
    id
    content
    createdAt
    sender {
      id
      name
      avatar
    }
  }
}
```

```kotlin
class ChatRepository @Inject constructor(
    private val apolloClient: ApolloClient
) {
    fun subscribeToMessages(chatId: String): Flow<OnNewMessageSubscription.MessageAdded> {
        return apolloClient.subscription(OnNewMessageSubscription(chatId))
            .toFlow()
            .mapNotNull { response ->
                response.data?.messageAdded
            }
    }
}

// Usage in ViewModel
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository
) : ViewModel() {

    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages.asStateFlow()

    fun subscribeToChat(chatId: String) {
        viewModelScope.launch {
            chatRepository.subscribeToMessages(chatId)
                .catch { e -> /* handle error */ }
                .collect { newMessage ->
                    _messages.update { currentMessages ->
                        currentMessages + newMessage.toMessage()
                    }
                }
        }
    }
}
```

### Normalized Cache

Apollo normalizes data by keys (e.g., `User:123`), automatically updating all related queries:

```kotlin
// Cache configuration
val apolloClient = ApolloClient.Builder()
    .serverUrl("https://api.example.com/graphql")
    .normalizedCache(
        MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024)
            .chain(SqlNormalizedCacheFactory(context, "apollo.db"))
    )
    // Custom cache key resolver
    .cacheKeyGenerator(object : CacheKeyGenerator {
        override fun cacheKeyForObject(
            obj: Map<String, Any?>,
            context: CacheKeyGeneratorContext
        ): CacheKey? {
            val typename = obj["__typename"] as? String
            val id = obj["id"] as? String
            return if (typename != null && id != null) {
                CacheKey(typename, id)
            } else {
                null
            }
        }
    })
    .build()
```

### Fetch Policies

```kotlin
// CacheFirst - cache first, then network if not in cache
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.CacheFirst)

// NetworkFirst - network first, then cache on error
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.NetworkFirst)

// CacheOnly - only from cache
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.CacheOnly)

// NetworkOnly - only from network
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.NetworkOnly)

// CacheAndNetwork - returns both cache and network (two results)
apolloClient.query(GetUserQuery(id))
    .fetchPolicy(FetchPolicy.CacheAndNetwork)
```

### Error Handling

```kotlin
sealed class GraphQLResult<out T> {
    data class Success<T>(val data: T) : GraphQLResult<T>()
    data class GraphQLError(val errors: List<Error>) : GraphQLResult<Nothing>()
    data class NetworkError(val exception: Throwable) : GraphQLResult<Nothing>()
}

suspend fun <D : Query.Data> ApolloClient.safeQuery(
    query: Query<D>
): GraphQLResult<D> {
    return try {
        val response = query(query).execute()
        when {
            response.hasErrors() -> GraphQLResult.GraphQLError(response.errors!!)
            response.data != null -> GraphQLResult.Success(response.data!!)
            else -> GraphQLResult.NetworkError(Exception("No data"))
        }
    } catch (e: ApolloNetworkException) {
        GraphQLResult.NetworkError(e)
    } catch (e: ApolloException) {
        GraphQLResult.NetworkError(e)
    }
}
```

### Best Practices

1. **Fragments** - use for reusing fields across queries
2. **Normalized cache** - ensure stable IDs for all types
3. **watch()** - use for automatic UI updates on cache changes
4. **Fetch Policy** - choose strategy per use case
5. **Optimistic updates** - for instant UI response
6. **Error handling** - always check `hasErrors()` and `data`

---

## Дополнительные Вопросы (RU)

1. Как реализовать пагинацию с Apollo Kotlin?
2. В чем разница между `watch()` и `refetch()`?
3. Как обновить кеш вручную после mutation?
4. Когда использовать GraphQL вместо REST?
5. Как тестировать Apollo queries с MockServer?

## Follow-ups

1. How do you implement pagination with Apollo Kotlin?
2. What is the difference between `watch()` and `refetch()`?
3. How do you manually update cache after mutation?
4. When should you use GraphQL instead of REST?
5. How do you test Apollo queries with MockServer?

## Ссылки (RU)

- [Apollo Kotlin Documentation](https://www.apollographql.com/docs/kotlin/)
- [GraphQL Learn](https://graphql.org/learn/)
- [Apollo Normalized Cache](https://www.apollographql.com/docs/kotlin/caching/normalized-caches)

## References

- [Apollo Kotlin Documentation](https://www.apollographql.com/docs/kotlin/)
- [GraphQL Learn](https://graphql.org/learn/)
- [Apollo Normalized Cache](https://www.apollographql.com/docs/kotlin/caching/normalized-caches)

## Связанные Вопросы (RU)

### Предпосылки

- [[q-retrofit-library--android--medium]]
- [[q-http-protocols-comparison--android--medium]]

### Похожие

- [[q-graphql-apollo-android--android--medium]]
- [[q-cache-implementation-strategies--android--medium]]

### Продвинутое

- [[q-grpc-android--networking--hard]]
- [[q-offline-first--networking--hard]]

## Related Questions

### Prerequisites

- [[q-retrofit-library--android--medium]]
- [[q-http-protocols-comparison--android--medium]]

### Related

- [[q-graphql-apollo-android--android--medium]]
- [[q-cache-implementation-strategies--android--medium]]

### Advanced

- [[q-grpc-android--networking--hard]]
- [[q-offline-first--networking--hard]]

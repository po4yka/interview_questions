---
id: android-167
title: GraphQL with Apollo Android / GraphQL с Apollo Android
aliases:
- GraphQL with Apollo Android
- GraphQL с Apollo Android
topic: android
subtopics:
- networking-http
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
updated: 2025-10-31
tags:
- android/networking-http
- api
- apollo
- caching
- difficulty/medium
- graphql
---

# Вопрос (RU)
> GraphQL с Apollo Android

# Question (EN)
> GraphQL with Apollo Android

---

## Ответ (RU)
**Apollo Android** - это строго типизированный, кеширующий GraphQL клиент для Android, написанный на Kotlin. Он обеспечивает отличный опыт разработчика с типобезопасностью на этапе компиляции, автоматической генерацией кода из GraphQL схем и сложной системой нормализованного кеширования.

### Основные Концепции GraphQL

#### Ключевые Отличия От REST

1. **Единая точка входа**: Все запросы идут на один URL
2. **Запрашивайте только то, что нужно**: Нет избыточной или недостаточной выборки данных
3. **Строго типизированная схема**: Контракт между клиентом и сервером
4. **Интроспекция**: Запрос самой схемы
5. **Реальное время**: Встроенная поддержка подписок

### Полная Настройка Apollo Android

```kotlin
// build.gradle.kts (уровень приложения)
plugins {
    id("com.apollographql.apollo3")
}

dependencies {
    implementation("com.apollographql.apollo3:apollo-runtime:3.8.2")
    implementation("com.apollographql.apollo3:apollo-normalized-cache:3.8.2")
    implementation("com.apollographql.apollo3:apollo-normalized-cache-sqlite:3.8.2")
}

apollo {
    service("api") {
        packageName.set("com.example.graphql")
        schemaFile.set(file("src/main/graphql/schema.graphqls"))
    }
}
```

### Настройка Клиента Apollo

```kotlin
class ApolloClientProvider(
    private val context: Context,
    private val tokenProvider: TokenProvider
) {

    val apolloClient: ApolloClient by lazy {
        ApolloClient.Builder()
            .serverUrl("https://api.example.com/graphql")
            .httpEngine(DefaultHttpEngine(okHttpClient))
            .normalizedCache(
                normalizedCacheFactory = createCacheFactory()
            )
            .build()
    }

    private fun createCacheFactory(): NormalizedCacheFactory {
        return MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024)
            .chain(
                SqlNormalizedCacheFactory(
                    context = context,
                    name = "apollo.db"
                )
            )
    }
}
```

### GraphQL Запросы (Queries)

```graphql
# Базовый запрос
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
  }
}
```

```kotlin
suspend fun getUser(userId: String): GetUserQuery.User? {
    val response = apolloClient
        .query(GetUserQuery(id = userId))
        .execute()

    return response.data?.user
}
```

### GraphQL Мутации (Mutations)

```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    post {
      id
      title
      content
    }
  }
}
```

```kotlin
suspend fun createPost(title: String, content: String) {
    val input = CreatePostInput(title = title, content = content)

    apolloClient
        .mutation(CreatePostMutation(input))
        .execute()
}
```

### Оптимистичные Обновления

```kotlin
suspend fun likePost(postId: String) {
    apolloClient
        .mutation(LikePostMutation(id = postId))
        .optimisticUpdates(
            LikePostMutation.Data(
                likePost = LikePostMutation.LikePost(
                    post = LikePostMutation.Post(
                        id = postId,
                        likes = getCurrentLikes(postId) + 1
                    )
                )
            )
        )
        .execute()
}
```

### GraphQL Подписки (Subscriptions)

```graphql
subscription OnPostCreated {
  postCreated {
    id
    title
    content
  }
}
```

```kotlin
fun subscribeToNewPosts(): Flow<OnPostCreatedSubscription.PostCreated?> {
    return apolloClientWithSubscriptions
        .subscription(OnPostCreatedSubscription())
        .toFlow()
        .map { response ->
            response.dataAssertNoErrors.postCreated
        }
}
```

### Нормализованный Кеш

Apollo Android использует **нормализованный кеш**, который хранит результаты GraphQL в плоской таблице поиска по ID, избегая дублирования данных и обеспечивая консистентность.

#### Политики Кеша

```kotlin
enum class FetchPolicy {
    CacheFirst,      // Сначала кеш, затем сеть
    CacheOnly,       // Только кеш
    NetworkOnly,     // Только сеть
    NetworkFirst,    // Сначала сеть, затем кеш при ошибке
    CacheAndNetwork  // Кеш, затем всегда сеть
}

// Использование
suspend fun getUserCacheFirst(userId: String) {
    apolloClient
        .query(GetUserQuery(id = userId))
        .fetchPolicy(FetchPolicy.CacheFirst)
        .execute()
}
```

#### Реактивный Кеш (Watch)

```kotlin
fun watchUser(userId: String): Flow<GetUserQuery.User?> {
    return apolloClient
        .query(GetUserQuery(id = userId))
        .fetchPolicy(FetchPolicy.CacheAndNetwork)
        .watch()
        .map { response ->
            response.dataAssertNoErrors.user
        }
}
```

### Фрагменты

```graphql
fragment UserFields on User {
  id
  name
  email
  avatar
}

query GetUser($id: ID!) {
  user(id: $id) {
    ...UserFields
    posts {
      id
      title
    }
  }
}
```

### Обработка Ошибок

```kotlin
sealed class GraphQLResult<out T> {
    data class Success<T>(val data: T) : GraphQLResult<T>()
    data class Error(val error: GraphQLError) : GraphQLResult<Nothing>()
}

suspend fun getUser(userId: String): GraphQLResult<GetUserQuery.User> {
    return try {
        val response = apolloClient
            .query(GetUserQuery(id = userId))
            .execute()

        when {
            response.data != null && !response.hasErrors() -> {
                GraphQLResult.Success(response.data!!.user)
            }
            response.hasErrors() -> {
                GraphQLResult.Error(/* обработать ошибки */)
            }
            else -> {
                GraphQLResult.Error(/* неизвестная ошибка */)
            }
        }
    } catch (e: ApolloException) {
        GraphQLResult.Error(/* обработать исключение */)
    }
}
```

### Полная Реализация Repository

```kotlin
class PostRepository(
    private val apolloClient: ApolloClient
) {

    // Запрос постов
    suspend fun getPosts(): GraphQLResult<List<GetPostsQuery.Post>> {
        return executeQuery {
            apolloClient
                .query(GetPostsQuery())
                .fetchPolicy(FetchPolicy.CacheFirst)
                .execute()
        }
    }

    // Наблюдение за постами (реактивно)
    fun watchPosts(): Flow<List<GetPostsQuery.Post>> {
        return apolloClient
            .query(GetPostsQuery())
            .watch()
            .map { it.dataAssertNoErrors.posts }
    }

    // Создание поста
    suspend fun createPost(title: String, content: String) {
        apolloClient
            .mutation(
                CreatePostMutation(
                    input = CreatePostInput(title, content)
                )
            )
            .execute()
    }

    // Лайк с оптимистичным обновлением
    suspend fun likePost(postId: String) {
        val currentLikes = getCurrentLikes(postId)

        apolloClient
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
    }

    // Подписка на новые посты
    fun subscribeToNewPosts(): Flow<OnPostCreatedSubscription.PostCreated?> {
        return apolloClientWithSubscriptions
            .subscription(OnPostCreatedSubscription())
            .toFlow()
            .map { it.dataAssertNoErrors.postCreated }
    }
}
```

### Best Practices

1. **Используйте фрагменты для переиспользуемых полей**
2. **Используйте нормализованный кеш**
3. **Обрабатывайте ошибки gracefully**
4. **Используйте оптимистичные обновления для мутаций**
5. **Выбирайте подходящую политику кеша**
6. **Наблюдайте за запросами для реактивного UI**
7. **Используйте подписки для real-time**

### Распространённые Ошибки

1. **Не обработка GraphQL ошибок**
2. **Забывание __typename для кеша**
3. **Не использование фрагментов**
4. **Неправильные ключи кеша**
5. **Не очистка подписок**

### Резюме

Apollo Android обеспечивает:

- **Типобезопасность**: Проверка на этапе компиляции
- **Генерация кода**: Авто-генерация Kotlin моделей
- **Нормализованный кеш**: Эффективное хранение данных
- **Оптимистичные обновления**: Немедленная обратная связь UI
- **Реактивные запросы**: Авто-обновление UI
- **Подписки**: Real-time данные через WebSocket
- **Обработка ошибок**: Разделение GraphQL и сетевых ошибок

GraphQL + Apollo отлично подходит для сложных требований к данным, real-time функций и строго типизированных API.


## Answer (EN)
**Apollo Android** is a strongly-typed, caching GraphQL client for Android written in Kotlin. It provides excellent developer experience with compile-time type safety, automatic code generation from GraphQL schemas, and a sophisticated normalized caching system.

### GraphQL Core Concepts

#### Key Differences from REST

1. **Single Endpoint**: All requests go to one URL
2. **Request Exactly What You Need**: No over-fetching or under-fetching
3. **Strongly Typed Schema**: Contract between client and server
4. **Introspection**: Query the schema itself
5. **Real-Time**: Built-in subscription support

#### GraphQL Operations

```graphql
# Query - Read data
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
  }
}

# Mutation - Write data
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    content
  }
}

# Subscription - Real-time updates
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

### Complete Apollo Android Setup

#### 1. Project Configuration

```kotlin
// build.gradle.kts (project level)
plugins {
    id("com.apollographql.apollo3") version "3.8.2" apply false
}

// build.gradle.kts (app level)
plugins {
    id("com.apollographql.apollo3")
}

dependencies {
    // Apollo GraphQL
    implementation("com.apollographql.apollo3:apollo-runtime:3.8.2")

    // For coroutines support
    implementation("com.apollographql.apollo3:apollo-adapters:3.8.2")

    // For normalized cache
    implementation("com.apollographql.apollo3:apollo-normalized-cache:3.8.2")
    implementation("com.apollographql.apollo3:apollo-normalized-cache-sqlite:3.8.2")

    // For subscriptions (WebSocket)
    implementation("com.apollographql.apollo3:apollo-normalized-cache:3.8.2")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}

apollo {
    // Service configuration
    service("api") {
        // Package name for generated code
        packageName.set("com.example.graphql")

        // Schema file location
        schemaFile.set(file("src/main/graphql/schema.graphqls"))

        // Enable test builders
        generateTestBuilders.set(true)

        // Generate Kotlin models
        generateKotlinModels.set(true)

        // Use semantic naming (removes redundant Type suffix)
        useSemanticNaming.set(true)

        // Generate operation output for introspection
        generateOperationOutput.set(true)
    }
}
```

#### 2. GraphQL Schema

```graphql
# src/main/graphql/schema.graphqls

type Query {
  user(id: ID!): User
  users(first: Int, after: String): UserConnection!
  post(id: ID!): Post
  posts(userId: ID): [Post!]!
}

type Mutation {
  createPost(input: CreatePostInput!): CreatePostPayload!
  updatePost(id: ID!, input: UpdatePostInput!): UpdatePostPayload!
  deletePost(id: ID!): DeletePostPayload!
  likePost(id: ID!): LikePostPayload!
}

type Subscription {
  postCreated: Post!
  postUpdated(id: ID!): Post!
  postLiked(id: ID!): Post!
}

type User {
  id: ID!
  name: String!
  email: String!
  avatar: String
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  likes: Int!
  comments: [Comment!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Comment {
  id: ID!
  content: String!
  author: User!
  post: Post!
  createdAt: DateTime!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}

input CreatePostInput {
  title: String!
  content: String!
}

input UpdatePostInput {
  title: String
  content: String
}

type CreatePostPayload {
  post: Post!
}

type UpdatePostPayload {
  post: Post!
}

type DeletePostPayload {
  success: Boolean!
}

type LikePostPayload {
  post: Post!
}

scalar DateTime
```

#### 3. Apollo Client Setup

```kotlin
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.cache.normalized.api.MemoryCacheFactory
import com.apollographql.apollo3.cache.normalized.normalizedCache
import com.apollographql.apollo3.cache.normalized.sql.SqlNormalizedCacheFactory
import com.apollographql.apollo3.network.http.DefaultHttpEngine
import com.apollographql.apollo3.network.http.LoggingInterceptor
import com.apollographql.apollo3.network.ws.GraphQLWsProtocol
import com.apollographql.apollo3.network.ws.WebSocketNetworkTransport
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

class ApolloClientProvider(
    private val context: Context,
    private val tokenProvider: TokenProvider
) {

    companion object {
        private const val BASE_URL = "https://api.example.com/graphql"
        private const val WS_URL = "wss://api.example.com/graphql"
        private const val CACHE_SIZE = 10 * 1024 * 1024L // 10MB
    }

    private val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .apply {
                        tokenProvider.getAccessToken()?.let { token ->
                            addHeader("Authorization", "Bearer $token")
                        }
                    }
                    .build()
                chain.proceed(request)
            }
            .build()
    }

    val apolloClient: ApolloClient by lazy {
        ApolloClient.Builder()
            .serverUrl(BASE_URL)
            .httpEngine(DefaultHttpEngine(okHttpClient))
            .normalizedCache(
                normalizedCacheFactory = createCacheFactory(),
                cacheResolver = createCacheResolver()
            )
            .apply {
                if (BuildConfig.DEBUG) {
                    addHttpInterceptor(LoggingInterceptor(LoggingInterceptor.Level.BODY))
                }
            }
            .build()
    }

    val apolloClientWithSubscriptions: ApolloClient by lazy {
        ApolloClient.Builder()
            .serverUrl(BASE_URL)
            .httpEngine(DefaultHttpEngine(okHttpClient))
            .subscriptionNetworkTransport(
                WebSocketNetworkTransport.Builder()
                    .serverUrl(WS_URL)
                    .protocol(GraphQLWsProtocol.Factory())
                    .build()
            )
            .normalizedCache(
                normalizedCacheFactory = createCacheFactory(),
                cacheResolver = createCacheResolver()
            )
            .build()
    }

    private fun createCacheFactory(): NormalizedCacheFactory {
        // Memory cache with SQL persistent cache as backup
        return MemoryCacheFactory(maxSizeBytes = CACHE_SIZE)
            .chain(
                SqlNormalizedCacheFactory(
                    context = context,
                    name = "apollo.db"
                )
            )
    }

    private fun createCacheResolver(): CacheResolver {
        return object : CacheResolver {
            override fun resolveField(
                field: CompiledField,
                variables: Executable.Variables,
                parent: Map<String, Any?>,
                parentId: String
            ): Any? {
                // Custom cache key resolution if needed
                return null
            }
        }
    }
}

interface TokenProvider {
    fun getAccessToken(): String?
}
```

### GraphQL Queries

#### 1. Basic Query

```graphql
# src/main/graphql/queries/GetUser.graphql

query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    avatar
    createdAt
  }
}
```

```kotlin
// Generated code usage
class UserRepository(
    private val apolloClient: ApolloClient
) {

    suspend fun getUser(userId: String): Result<GetUserQuery.User?> {
        return try {
            val response = apolloClient
                .query(GetUserQuery(id = userId))
                .execute()

            if (response.hasErrors()) {
                Result.failure(
                    GraphQLException(response.errors?.firstOrNull()?.message)
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

#### 2. Query with Nested Fields and Variables

```graphql
# src/main/graphql/queries/GetUserWithPosts.graphql

query GetUserWithPosts($userId: ID!, $postLimit: Int = 10) {
  user(id: $userId) {
    id
    name
    email
    avatar
    posts(first: $postLimit) {
      id
      title
      content
      likes
      createdAt
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
}
```

```kotlin
suspend fun getUserWithPosts(
    userId: String,
    postLimit: Int = 10
): GetUserWithPostsQuery.User? {
    val response = apolloClient
        .query(
            GetUserWithPostsQuery(
                userId = userId,
                postLimit = Optional.present(postLimit)
            )
        )
        .execute()

    return response.dataAssertNoErrors.user
}
```

#### 3. Query with Fragments

```graphql
# src/main/graphql/fragments/UserFields.graphql

fragment UserFields on User {
  id
  name
  email
  avatar
  createdAt
}

fragment PostFields on Post {
  id
  title
  content
  likes
  createdAt
  author {
    ...UserFields
  }
}
```

```graphql
# src/main/graphql/queries/GetPostWithFragment.graphql

query GetPost($id: ID!) {
  post(id: $id) {
    ...PostFields
    comments {
      id
      content
      author {
        ...UserFields
      }
    }
  }
}
```

```kotlin
suspend fun getPost(postId: String): GetPostQuery.Post? {
    val response = apolloClient
        .query(GetPostQuery(id = postId))
        .execute()

    return response.data?.post
}

// Accessing fragment data
fun displayPost(post: GetPostQuery.Post) {
    val postFields = post.postFields
    println("Title: ${postFields.title}")
    println("Content: ${postFields.content}")
    println("Author: ${postFields.author.userFields.name}")
}
```

### GraphQL Mutations

#### 1. Create Mutation

```graphql
# src/main/graphql/mutations/CreatePost.graphql

mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    post {
      id
      title
      content
      likes
      createdAt
      author {
        id
        name
      }
    }
  }
}
```

```kotlin
suspend fun createPost(
    title: String,
    content: String
): CreatePostMutation.Post? {
    val input = CreatePostInput(
        title = title,
        content = content
    )

    val response = apolloClient
        .mutation(CreatePostMutation(input))
        .execute()

    return response.dataAssertNoErrors.createPost.post
}
```

#### 2. Update Mutation with Optimistic Updates

```graphql
# src/main/graphql/mutations/LikePost.graphql

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
import com.apollographql.apollo3.api.Optional
import com.apollographql.apollo3.cache.normalized.FetchPolicy
import com.apollographql.apollo3.cache.normalized.optimisticUpdates

suspend fun likePost(postId: String): Result<Int> {
    return try {
        val response = apolloClient
            .mutation(LikePostMutation(id = postId))
            .optimisticUpdates(
                // Optimistic update - immediate UI feedback
                LikePostMutation.Data(
                    likePost = LikePostMutation.LikePost(
                        post = LikePostMutation.Post(
                            id = postId,
                            likes = getCurrentLikes(postId) + 1
                        )
                    )
                )
            )
            .execute()

        if (response.hasErrors()) {
            Result.failure(GraphQLException(response.errors?.first()?.message))
        } else {
            Result.success(response.data?.likePost?.post?.likes ?: 0)
        }
    } catch (e: ApolloException) {
        Result.failure(e)
    }
}

private suspend fun getCurrentLikes(postId: String): Int {
    // Read current likes from cache
    val cacheData = apolloClient.apolloStore.readOperation(
        GetPostQuery(id = postId)
    )
    return cacheData?.post?.likes ?: 0
}
```

#### 3. Delete Mutation

```graphql
# src/main/graphql/mutations/DeletePost.graphql

mutation DeletePost($id: ID!) {
  deletePost(id: $id) {
    success
  }
}
```

```kotlin
import com.apollographql.apollo3.cache.normalized.apolloStore
import com.apollographql.apollo3.cache.normalized.watch

suspend fun deletePost(postId: String): Result<Boolean> {
    return try {
        val response = apolloClient
            .mutation(DeletePostMutation(id = postId))
            .execute()

        if (response.data?.deletePost?.success == true) {
            // Remove from cache
            apolloClient.apolloStore.writeOperation(
                operation = GetPostQuery(id = postId),
                operationData = GetPostQuery.Data(post = null)
            )
            Result.success(true)
        } else {
            Result.failure(Exception("Delete failed"))
        }
    } catch (e: ApolloException) {
        Result.failure(e)
    }
}
```

### GraphQL Subscriptions

#### 1. Basic Subscription

```graphql
# src/main/graphql/subscriptions/OnPostCreated.graphql

subscription OnPostCreated {
  postCreated {
    id
    title
    content
    author {
      id
      name
    }
    createdAt
  }
}
```

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map

fun subscribeToNewPosts(): Flow<OnPostCreatedSubscription.PostCreated?> {
    return apolloClientWithSubscriptions
        .subscription(OnPostCreatedSubscription())
        .toFlow()
        .map { response ->
            response.dataAssertNoErrors.postCreated
        }
        .catch { e ->
            // Handle subscription errors
            emit(null)
        }
}

// Usage in ViewModel
class PostFeedViewModel(
    private val repository: PostRepository
) : ViewModel() {

    private val _newPosts = MutableStateFlow<List<Post>>(emptyList())
    val newPosts: StateFlow<List<Post>> = _newPosts

    init {
        viewModelScope.launch {
            repository.subscribeToNewPosts()
                .collect { post ->
                    post?.let {
                        _newPosts.value = _newPosts.value + it
                    }
                }
        }
    }
}
```

#### 2. Subscription with Parameters

```graphql
# src/main/graphql/subscriptions/OnPostUpdated.graphql

subscription OnPostUpdated($id: ID!) {
  postUpdated(id: $id) {
    id
    title
    content
    likes
    updatedAt
  }
}
```

```kotlin
fun watchPostUpdates(postId: String): Flow<OnPostUpdatedSubscription.PostUpdated?> {
    return apolloClientWithSubscriptions
        .subscription(OnPostUpdatedSubscription(id = postId))
        .toFlow()
        .map { it.data?.postUpdated }
}
```

### Normalized Cache System

Apollo Android uses a **normalized cache** that stores GraphQL results in a flat lookup table by ID, avoiding data duplication and ensuring consistency.

#### How Normalized Cache Works

```kotlin
// Cache structure example:
// CACHE_KEY: User:123
// {
//   "__typename": "User",
//   "id": "123",
//   "name": "John Doe",
//   "email": "john@example.com"
// }
//
// CACHE_KEY: Post:456
// {
//   "__typename": "Post",
//   "id": "456",
//   "title": "GraphQL Tutorial",
//   "author": { "__ref": "User:123" }  // Reference to cached User
// }
```

#### Cache Policies

```kotlin
import com.apollographql.apollo3.cache.normalized.FetchPolicy
import com.apollographql.apollo3.cache.normalized.fetchPolicy

enum class FetchPolicy {
    // Try cache first, then network if miss
    CacheFirst,

    // Only use cache, never network
    CacheOnly,

    // Always use network, update cache
    NetworkOnly,

    // Network first, fallback to cache on error
    NetworkFirst,

    // Try cache, then always network
    CacheAndNetwork
}

// Usage examples
suspend fun getUserCacheFirst(userId: String): GetUserQuery.User? {
    val response = apolloClient
        .query(GetUserQuery(id = userId))
        .fetchPolicy(FetchPolicy.CacheFirst)
        .execute()

    return response.data?.user
}

suspend fun getUserNetworkOnly(userId: String): GetUserQuery.User? {
    val response = apolloClient
        .query(GetUserQuery(id = userId))
        .fetchPolicy(FetchPolicy.NetworkOnly)
        .execute()

    return response.data?.user
}
```

#### Cache Watching (Reactive Cache)

```kotlin
import com.apollographql.apollo3.cache.normalized.watch
import kotlinx.coroutines.flow.Flow

fun watchUser(userId: String): Flow<GetUserQuery.User?> {
    return apolloClient
        .query(GetUserQuery(id = userId))
        .fetchPolicy(FetchPolicy.CacheAndNetwork)
        .watch()
        .map { response ->
            response.dataAssertNoErrors.user
        }
}

// ViewModel usage
class UserProfileViewModel(
    private val repository: UserRepository,
    private val userId: String
) : ViewModel() {

    val user: StateFlow<User?> = repository
        .watchUser(userId)
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = null
        )
}
```

#### Manual Cache Operations

```kotlin
import com.apollographql.apollo3.cache.normalized.apolloStore

class CacheManager(private val apolloClient: ApolloClient) {

    // Read from cache
    suspend fun readUserFromCache(userId: String): GetUserQuery.User? {
        return apolloClient.apolloStore
            .readOperation(GetUserQuery(id = userId))
            ?.user
    }

    // Write to cache
    suspend fun writeUserToCache(user: GetUserQuery.User) {
        apolloClient.apolloStore.writeOperation(
            operation = GetUserQuery(id = user.id),
            operationData = GetUserQuery.Data(user = user)
        )
    }

    // Update specific field in cache
    suspend fun updateUserName(userId: String, newName: String) {
        apolloClient.apolloStore.writeFragment(
            fragment = UserFieldsFragment(),
            cacheKey = CacheKey("User:$userId"),
            fragmentData = UserFieldsFragment(
                id = userId,
                name = newName,
                // Other fields remain unchanged
            )
        )
    }

    // Clear entire cache
    suspend fun clearCache() {
        apolloClient.apolloStore.clearAll()
    }

    // Remove specific entry
    suspend fun removeUser(userId: String) {
        apolloClient.apolloStore.remove(
            cacheKey = CacheKey("User:$userId")
        )
    }
}
```

### Error Handling

```kotlin
import com.apollographql.apollo3.exception.ApolloException
import com.apollographql.apollo3.exception.ApolloHttpException
import com.apollographql.apollo3.exception.ApolloNetworkException
import com.apollographql.apollo3.exception.ApolloParseException

sealed class GraphQLResult<out T> {
    data class Success<T>(val data: T) : GraphQLResult<T>()
    data class Error(val error: GraphQLError) : GraphQLResult<Nothing>()
}

sealed class GraphQLError {
    data class NetworkError(val message: String) : GraphQLError()
    data class ServerError(val code: Int, val message: String) : GraphQLError()
    data class GraphQLErrors(val errors: List<String>) : GraphQLError()
    data class ParseError(val message: String) : GraphQLError()
    data class Unknown(val throwable: Throwable) : GraphQLError()
}

suspend fun <T> executeQuery(
    block: suspend () -> ApolloResponse<T>
): GraphQLResult<T> {
    return try {
        val response = block()

        when {
            response.data != null && !response.hasErrors() -> {
                GraphQLResult.Success(response.data!!)
            }
            response.hasErrors() -> {
                val errors = response.errors?.map { it.message } ?: emptyList()
                GraphQLResult.Error(GraphQLError.GraphQLErrors(errors))
            }
            else -> {
                GraphQLResult.Error(GraphQLError.Unknown(Exception("Unknown error")))
            }
        }
    } catch (e: ApolloNetworkException) {
        GraphQLResult.Error(
            GraphQLError.NetworkError(e.message ?: "Network error")
        )
    } catch (e: ApolloHttpException) {
        GraphQLResult.Error(
            GraphQLError.ServerError(e.statusCode, e.message ?: "Server error")
        )
    } catch (e: ApolloParseException) {
        GraphQLResult.Error(
            GraphQLError.ParseError(e.message ?: "Parse error")
        )
    } catch (e: ApolloException) {
        GraphQLResult.Error(
            GraphQLError.Unknown(e)
        )
    }
}

// Usage
suspend fun getUser(userId: String): GraphQLResult<GetUserQuery.User> {
    return executeQuery {
        apolloClient
            .query(GetUserQuery(id = userId))
            .execute()
    }.let { result ->
        when (result) {
            is GraphQLResult.Success -> {
                result.data.user?.let {
                    GraphQLResult.Success(it)
                } ?: GraphQLResult.Error(
                    GraphQLError.Unknown(Exception("User not found"))
                )
            }
            is GraphQLResult.Error -> result
        }
    }
}
```

### Complete Repository Implementation

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map

class PostRepository(
    private val apolloClient: ApolloClient,
    private val apolloClientWithSubscriptions: ApolloClient
) {

    // Query - fetch posts
    suspend fun getPosts(): GraphQLResult<List<GetPostsQuery.Post>> {
        return executeQuery {
            apolloClient
                .query(GetPostsQuery())
                .fetchPolicy(FetchPolicy.CacheFirst)
                .execute()
        }.let { result ->
            when (result) {
                is GraphQLResult.Success -> {
                    GraphQLResult.Success(result.data.posts)
                }
                is GraphQLResult.Error -> result
            }
        }
    }

    // Watch posts (reactive)
    fun watchPosts(): Flow<List<GetPostsQuery.Post>> {
        return apolloClient
            .query(GetPostsQuery())
            .fetchPolicy(FetchPolicy.CacheAndNetwork)
            .watch()
            .map { response ->
                response.dataAssertNoErrors.posts
            }
            .catch { e ->
                emit(emptyList())
            }
    }

    // Mutation - create post
    suspend fun createPost(
        title: String,
        content: String
    ): GraphQLResult<CreatePostMutation.Post> {
        return executeQuery {
            apolloClient
                .mutation(
                    CreatePostMutation(
                        input = CreatePostInput(
                            title = title,
                            content = content
                        )
                    )
                )
                .execute()
        }.let { result ->
            when (result) {
                is GraphQLResult.Success -> {
                    GraphQLResult.Success(result.data.createPost.post)
                }
                is GraphQLResult.Error -> result
            }
        }
    }

    // Mutation with optimistic update
    suspend fun likePost(postId: String): GraphQLResult<Int> {
        // Read current value from cache
        val currentLikes = apolloClient.apolloStore
            .readOperation(GetPostQuery(id = postId))
            ?.post?.likes ?: 0

        return executeQuery {
            apolloClient
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
        }.let { result ->
            when (result) {
                is GraphQLResult.Success -> {
                    GraphQLResult.Success(result.data.likePost.post.likes)
                }
                is GraphQLResult.Error -> result
            }
        }
    }

    // Subscription - watch new posts
    fun subscribeToNewPosts(): Flow<OnPostCreatedSubscription.PostCreated?> {
        return apolloClientWithSubscriptions
            .subscription(OnPostCreatedSubscription())
            .toFlow()
            .map { response ->
                response.dataAssertNoErrors.postCreated
            }
            .catch { e ->
                // Log error and emit null
                emit(null)
            }
    }

    // Pagination with cursor-based pagination
    suspend fun loadMoreUsers(
        after: String? = null,
        first: Int = 20
    ): GraphQLResult<GetUsersQuery.Data> {
        return executeQuery {
            apolloClient
                .query(
                    GetUsersQuery(
                        first = Optional.present(first),
                        after = Optional.presentIfNotNull(after)
                    )
                )
                .fetchPolicy(FetchPolicy.NetworkOnly)
                .execute()
        }
    }
}
```

### ViewModel with Apollo

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class PostFeedViewModel(
    private val repository: PostRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<PostFeedUiState>(PostFeedUiState.Loading)
    val uiState: StateFlow<PostFeedUiState> = _uiState

    init {
        loadPosts()
        subscribeToNewPosts()
    }

    private fun loadPosts() {
        viewModelScope.launch {
            repository.watchPosts()
                .catch { e ->
                    _uiState.value = PostFeedUiState.Error(e.message ?: "Unknown error")
                }
                .collect { posts ->
                    _uiState.value = PostFeedUiState.Success(posts)
                }
        }
    }

    private fun subscribeToNewPosts() {
        viewModelScope.launch {
            repository.subscribeToNewPosts()
                .filterNotNull()
                .collect { newPost ->
                    // Handle new post notification
                    showNewPostNotification(newPost)
                }
        }
    }

    fun likePost(postId: String) {
        viewModelScope.launch {
            when (val result = repository.likePost(postId)) {
                is GraphQLResult.Success -> {
                    // Optimistic update already applied via cache
                }
                is GraphQLResult.Error -> {
                    // Show error, cache will revert optimistic update
                    showError(result.error)
                }
            }
        }
    }

    fun createPost(title: String, content: String) {
        viewModelScope.launch {
            when (val result = repository.createPost(title, content)) {
                is GraphQLResult.Success -> {
                    // Post created successfully
                }
                is GraphQLResult.Error -> {
                    showError(result.error)
                }
            }
        }
    }

    private fun showNewPostNotification(post: OnPostCreatedSubscription.PostCreated) {
        // Show notification
    }

    private fun showError(error: GraphQLError) {
        // Show error message
    }
}

sealed class PostFeedUiState {
    object Loading : PostFeedUiState()
    data class Success(val posts: List<GetPostsQuery.Post>) : PostFeedUiState()
    data class Error(val message: String) : PostFeedUiState()
}
```

### Testing Apollo Queries

```kotlin
import com.apollographql.apollo3.testing.QueueTestNetworkTransport
import com.apollographql.apollo3.testing.enqueueTestResponse
import kotlinx.coroutines.test.runTest
import org.junit.Test
import kotlin.test.assertEquals

class PostRepositoryTest {

    @Test
    fun `getUser returns user data`() = runTest {
        // Setup
        val testNetworkTransport = QueueTestNetworkTransport()
        val apolloClient = ApolloClient.Builder()
            .networkTransport(testNetworkTransport)
            .build()

        val repository = PostRepository(apolloClient, apolloClient)

        // Enqueue test response
        val testUser = GetUserQuery.User(
            id = "123",
            name = "John Doe",
            email = "john@example.com",
            avatar = null,
            createdAt = "2024-01-01T00:00:00Z"
        )

        testNetworkTransport.enqueueTestResponse(
            GetUserQuery(id = "123"),
            GetUserQuery.Data(user = testUser)
        )

        // Execute
        val result = repository.getUser("123")

        // Verify
        assert(result is GraphQLResult.Success)
        assertEquals("John Doe", (result as GraphQLResult.Success).data.name)
    }

    @Test
    fun `likePost updates cache optimistically`() = runTest {
        // Test optimistic updates
    }
}
```

### Best Practices

1. **Use Fragments for Reusable Fields**
   ```graphql
   fragment UserFields on User {
     id
     name
     email
   }
   ```

2. **Leverage Normalized Cache**
   ```kotlin
   // Cache automatically updates all queries using same data
   ```

3. **Handle Errors Gracefully**
   ```kotlin
   // Check both response.hasErrors() and exception handling
   ```

4. **Use Optimistic Updates for Mutations**
   ```kotlin
   .optimisticUpdates(/* immediate UI feedback */)
   ```

5. **Choose Appropriate Fetch Policy**
   ```kotlin
   // CacheFirst for frequent reads
   // NetworkOnly for fresh data
   // CacheAndNetwork for best UX
   ```

6. **Watch Queries for Reactive UI**
   ```kotlin
   apolloClient.query().watch() // Auto-updates on cache changes
   ```

7. **Use Subscriptions for Real-Time**
   ```kotlin
   // WebSocket connection for live updates
   ```

8. **Implement Proper Error Handling**
   ```kotlin
   sealed class Result<T> // Type-safe error handling
   ```

### Common Pitfalls

1. **Not Handling GraphQL Errors**
   ```kotlin
   // BAD: Only checking data
   response.data?.user

   // GOOD: Check errors too
   if (response.hasErrors()) {
       // Handle errors
   }
   ```

2. **Forgetting __typename for Cache**
   ```graphql
   # Apollo adds __typename automatically
   # But custom resolvers need it
   ```

3. **Not Using Fragments**
   ```graphql
   # BAD: Duplicate fields everywhere
   # GOOD: Reusable fragments
   ```

4. **Incorrect Cache Key**
   ```kotlin
   // Ensure ID field is present for normalized cache
   ```

5. **Not Cleaning Up Subscriptions**
   ```kotlin
   // Use Flow with lifecycle-aware collectors
   ```

### Summary

Apollo Android provides:

- **Type Safety**: Compile-time checked GraphQL operations
- **Code Generation**: Auto-generated Kotlin models from schema
- **Normalized Cache**: Efficient data storage and consistency
- **Optimistic Updates**: Immediate UI feedback
- **Reactive Queries**: Auto-updating UI with cache watching
- **Subscriptions**: Real-time data via WebSocket
- **Error Handling**: GraphQL and network error separation
- **Testing**: Built-in testing utilities

GraphQL + Apollo is excellent for complex data requirements, real-time features, and strongly-typed APIs.

---

## Follow-ups

- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]]
- [[q-play-app-signing--android--medium]]
- [[q-sharedpreferences-definition--android--easy]]


## References

- [Connecting to the Network](https://developer.android.com/training/basics/network-ops/connecting)


## Related Questions

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

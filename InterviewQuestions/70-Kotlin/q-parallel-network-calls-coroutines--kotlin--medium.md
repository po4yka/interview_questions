---
id: kotlin-037
title: "How to make parallel network calls using coroutines? / Как выполнять параллельные сетевые запросы с помощью корутин?"
aliases: ["How to make parallel network calls using coroutines?, Как выполнять параллельные сетевые запросы с помощью корутин?"]

# Classification
topic: kotlin
subtopics: [async, await, coroutines]
question_kind: coding
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [async-await, coroutines, networking, structured-concurrency]

# Timestamps
created: 2025-10-06
updated: 2025-10-31

tags: [async, coroutines, difficulty/medium, kotlin, networking, parallel, performance]
date created: Saturday, November 1st 2025, 9:25:31 am
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# Question (EN)
> How do you make multiple network calls in parallel using Kotlin coroutines?
# Вопрос (RU)
> Как выполнить несколько сетевых запросов параллельно с помощью Kotlin корутин?

---

## Answer (EN)

Making parallel network calls is a common requirement in Android apps to improve performance and reduce loading time. Kotlin coroutines provide elegant ways to execute multiple network requests concurrently.

### 1. Using `async` and `await`

The most straightforward approach for parallel execution:

```kotlin
import kotlinx.coroutines.*

// API interface
interface ApiService {
    suspend fun getUser(userId: String): User
    suspend fun getPosts(userId: String): List<Post>
    suspend fun getComments(postId: String): List<Comment>
}

// Parallel execution with async/await
suspend fun fetchUserData(userId: String): UserData = coroutineScope {
    // Launch all requests in parallel
    val userDeferred = async { apiService.getUser(userId) }
    val postsDeferred = async { apiService.getPosts(userId) }
    val commentsDeferred = async { apiService.getComments("post1") }

    // Wait for all results
    UserData(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        comments = commentsDeferred.await()
    )
}

// Usage in ViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    fun loadUserData(userId: String) {
        viewModelScope.launch {
            try {
                _loading.value = true
                val userData = repository.fetchUserData(userId)
                _userData.value = userData
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _loading.value = false
            }
        }
    }
}
```

### 2. Handling Partial Failures

Use `runCatching` or try-catch for each async block to handle failures gracefully:

```kotlin
data class ParallelResult<T>(
    val data: T? = null,
    val error: Exception? = null
)

suspend fun fetchUserDataWithErrorHandling(userId: String): UserScreenData = coroutineScope {
    // Launch all requests
    val userDeferred = async {
        runCatching { apiService.getUser(userId) }
            .fold(
                onSuccess = { ParallelResult(data = it) },
                onFailure = { ParallelResult(error = it as? Exception) }
            )
    }

    val postsDeferred = async {
        runCatching { apiService.getPosts(userId) }
            .fold(
                onSuccess = { ParallelResult(data = it) },
                onFailure = { ParallelResult(error = it as? Exception) }
            )
    }

    val settingsDeferred = async {
        runCatching { apiService.getSettings(userId) }
            .fold(
                onSuccess = { ParallelResult(data = it) },
                onFailure = { ParallelResult(error = it as? Exception) }
            )
    }

    // Await all results
    val userResult = userDeferred.await()
    val postsResult = postsDeferred.await()
    val settingsResult = settingsDeferred.await()

    UserScreenData(
        user = userResult.data,
        posts = postsResult.data ?: emptyList(),
        settings = settingsResult.data ?: Settings.default(),
        errors = listOfNotNull(
            userResult.error,
            postsResult.error,
            settingsResult.error
        )
    )
}
```

### 3. Using `awaitAll` for Collections

When you need to fetch multiple items of the same type:

```kotlin
suspend fun fetchMultipleUsers(userIds: List<String>): List<User> = coroutineScope {
    userIds.map { userId ->
        async { apiService.getUser(userId) }
    }.awaitAll()
}

// With error handling
suspend fun fetchMultipleUsersSafely(userIds: List<String>): List<User> = coroutineScope {
    userIds.map { userId ->
        async {
            runCatching { apiService.getUser(userId) }
                .getOrNull()
        }
    }.awaitAll()
        .filterNotNull()
}

// Practical example: Load feeds from multiple sources
suspend fun loadFeeds(): FeedData = coroutineScope {
    val sources = listOf("tech", "sports", "news", "entertainment")

    val feeds = sources.map { source ->
        async {
            apiService.getFeed(source)
        }
    }.awaitAll()

    FeedData(feeds.flatten())
}
```

### 4. Using `supervisorScope` for Independent Failures

When one failure shouldn't cancel other requests:

```kotlin
suspend fun fetchDashboardData(): DashboardData = supervisorScope {
    val newsDeferred = async {
        try {
            apiService.getNews()
        } catch (e: Exception) {
            Log.e("Dashboard", "News fetch failed", e)
            emptyList<News>()
        }
    }

    val weatherDeferred = async {
        try {
            apiService.getWeather()
        } catch (e: Exception) {
            Log.e("Dashboard", "Weather fetch failed", e)
            Weather.default()
        }
    }

    val stocksDeferred = async {
        try {
            apiService.getStocks()
        } catch (e: Exception) {
            Log.e("Dashboard", "Stocks fetch failed", e)
            emptyList<Stock>()
        }
    }

    DashboardData(
        news = newsDeferred.await(),
        weather = weatherDeferred.await(),
        stocks = stocksDeferred.await()
    )
}
```

### 5. Race Pattern - First Successful Result

Get the first successful result from multiple sources:

```kotlin
suspend fun <T> raceForFirst(
    vararg blocks: suspend () -> T
): T = coroutineScope {
    val deferreds = blocks.map { block ->
        async {
            runCatching { block() }
        }
    }

    // Return first successful result
    for (deferred in deferreds) {
        val result = deferred.await()
        if (result.isSuccess) {
            // Cancel other requests
            deferreds.forEach { if (it != deferred) it.cancel() }
            return@coroutineScope result.getOrThrow()
        }
    }

    throw Exception("All requests failed")
}

// Usage: Try multiple CDN endpoints
suspend fun downloadFromCdn(fileId: String): ByteArray {
    return raceForFirst(
        { cdnService.download("cdn1.example.com", fileId) },
        { cdnService.download("cdn2.example.com", fileId) },
        { cdnService.download("cdn3.example.com", fileId) }
    )
}
```

### 6. Throttling Parallel Requests

Limit concurrent requests to avoid overwhelming the server:

```kotlin
import kotlinx.coroutines.sync.Semaphore

class ThrottledApiClient(
    private val maxConcurrent: Int = 5
) {
    private val semaphore = Semaphore(maxConcurrent)

    suspend fun <T> throttled(block: suspend () -> T): T {
        semaphore.acquire()
        try {
            return block()
        } finally {
            semaphore.release()
        }
    }
}

// Usage
suspend fun fetchManyItems(itemIds: List<String>): List<Item> = coroutineScope {
    val throttledClient = ThrottledApiClient(maxConcurrent = 3)

    itemIds.map { itemId ->
        async {
            throttledClient.throttled {
                apiService.getItem(itemId)
            }
        }
    }.awaitAll()
}
```

### 7. Chunked Parallel Processing

Process large lists in batches:

```kotlin
suspend fun fetchInBatches(
    userIds: List<String>,
    batchSize: Int = 10
): List<User> {
    return userIds.chunked(batchSize)
        .flatMap { batch ->
            coroutineScope {
                batch.map { userId ->
                    async { apiService.getUser(userId) }
                }.awaitAll()
            }
        }
}

// With progress tracking
suspend fun fetchWithProgress(
    userIds: List<String>,
    batchSize: Int = 10,
    onProgress: (Int, Int) -> Unit
): List<User> {
    val batches = userIds.chunked(batchSize)
    val results = mutableListOf<User>()

    batches.forEachIndexed { index, batch ->
        val batchResults = coroutineScope {
            batch.map { userId ->
                async { apiService.getUser(userId) }
            }.awaitAll()
        }
        results.addAll(batchResults)
        onProgress(index + 1, batches.size)
    }

    return results
}
```

### 8. Combining Results with Flows

```kotlin
fun fetchUsersFlow(userIds: List<String>): Flow<User> = flow {
    coroutineScope {
        val channel = Channel<User>(capacity = Channel.UNLIMITED)

        // Launch all requests
        userIds.forEach { userId ->
            launch {
                try {
                    val user = apiService.getUser(userId)
                    channel.send(user)
                } catch (e: Exception) {
                    Log.e("Fetch", "Failed to fetch user $userId", e)
                }
            }
        }

        // Collect results as they arrive
        repeat(userIds.size) {
            emit(channel.receive())
        }

        channel.close()
    }
}

// Usage in UI
viewModelScope.launch {
    fetchUsersFlow(userIds)
        .collect { user ->
            _users.value += user
            // Update UI progressively
        }
}
```

### 9. Real-World Example: Product Details Screen

```kotlin
class ProductRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun loadProductDetails(productId: String): ProductDetails = coroutineScope {
        try {
            // Launch all requests in parallel
            val productDeferred = async { apiService.getProduct(productId) }
            val reviewsDeferred = async { apiService.getReviews(productId) }
            val relatedDeferred = async { apiService.getRelatedProducts(productId) }
            val availabilityDeferred = async { apiService.checkAvailability(productId) }
            val sellerDeferred = async {
                val product = productDeferred.await()
                apiService.getSeller(product.sellerId)
            }

            ProductDetails(
                product = productDeferred.await(),
                reviews = reviewsDeferred.await(),
                relatedProducts = relatedDeferred.await(),
                availability = availabilityDeferred.await(),
                seller = sellerDeferred.await()
            )
        } catch (e: Exception) {
            throw ProductLoadException("Failed to load product details", e)
        }
    }
}
```

### 10. Best Practices

#### - DO:

```kotlin
// Use coroutineScope for structured concurrency
suspend fun fetchData() = coroutineScope {
    val data1 = async { api.fetch1() }
    val data2 = async { api.fetch2() }
    Result(data1.await(), data2.await())
}

// Handle errors appropriately
suspend fun fetchSafely() = coroutineScope {
    val results = listOf(
        async { runCatching { api.fetch1() } },
        async { runCatching { api.fetch2() } }
    ).awaitAll()

    results.mapNotNull { it.getOrNull() }
}

// Use supervisorScope when failures are independent
suspend fun fetchIndependent() = supervisorScope {
    // One failure won't cancel others
}
```

#### - DON'T:

```kotlin
// Don't use GlobalScope
suspend fun bad() {
    GlobalScope.async { } // Bad - no structured concurrency
}

// Don't ignore cancellation
suspend fun bad2() = coroutineScope {
    async(NonCancellable) { } // Bad - can't be cancelled
}

// Don't await in wrong order (sequential execution)
suspend fun bad3() = coroutineScope {
    val data1 = async { api.fetch1() }.await() // Waits here
    val data2 = async { api.fetch2() }.await() // Then starts this
    // This is sequential, not parallel!
}
```

### 11. Performance Comparison

```kotlin
// Sequential (slow)
suspend fun sequentialFetch(): ProfileData {
    val user = apiService.getUser() // 1 second
    val posts = apiService.getPosts() // 1 second
    val friends = apiService.getFriends() // 1 second
    return ProfileData(user, posts, friends)
    // Total: ~3 seconds
}

// Parallel (fast)
suspend fun parallelFetch(): ProfileData = coroutineScope {
    val userDeferred = async { apiService.getUser() }
    val postsDeferred = async { apiService.getPosts() }
    val friendsDeferred = async { apiService.getFriends() }
    ProfileData(
        userDeferred.await(),
        postsDeferred.await(),
        friendsDeferred.await()
    )
    // Total: ~1 second (limited by slowest request)
}
```

---

## Ответ (RU)

Выполнение параллельных сетевых запросов - распространенное требование в Android приложениях для улучшения производительности и сокращения времени загрузки.

### 1. Использование `async` И `await`

```kotlin
suspend fun fetchUserData(userId: String): UserData = coroutineScope {
    // Запускаем все запросы параллельно
    val userDeferred = async { apiService.getUser(userId) }
    val postsDeferred = async { apiService.getPosts(userId) }
    val commentsDeferred = async { apiService.getComments("post1") }

    // Ожидаем все результаты
    UserData(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        comments = commentsDeferred.await()
    )
}
```

### 2. Обработка Частичных Ошибок

```kotlin
suspend fun fetchUserDataWithErrorHandling(userId: String) = coroutineScope {
    val userDeferred = async {
        runCatching { apiService.getUser(userId) }
            .fold(
                onSuccess = { ParallelResult(data = it) },
                onFailure = { ParallelResult(error = it as? Exception) }
            )
    }
    // Продолжаем даже если один запрос упал
}
```

### 3. Использование `awaitAll` Для Коллекций

```kotlin
suspend fun fetchMultipleUsers(userIds: List<String>): List<User> = coroutineScope {
    userIds.map { userId ->
        async { apiService.getUser(userId) }
    }.awaitAll()
}
```

### 4. Ограничение Параллельных Запросов

```kotlin
class ThrottledApiClient(maxConcurrent: Int = 5) {
    private val semaphore = Semaphore(maxConcurrent)

    suspend fun <T> throttled(block: suspend () -> T): T {
        semaphore.acquire()
        try {
            return block()
        } finally {
            semaphore.release()
        }
    }
}
```

### Лучшие Практики

#### - ДЕЛАЙТЕ:

- Используйте `coroutineScope` для структурированной конкурентности
- Обрабатывайте ошибки должным образом
- Используйте `supervisorScope` когда сбои независимы

#### - НЕ ДЕЛАЙТЕ:

- Не используйте GlobalScope
- Не игнорируйте отмену
- Не await в неправильном порядке

### Сравнение Производительности

- **Последовательно**: ~3 секунды (1s + 1s + 1s)
- **Параллельно**: ~1 секунда (макс. из трех запросов)

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions

### Related (Medium)
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Coroutines
- [[q-deferred-async-patterns--kotlin--medium]] - Coroutines
- [[q-coroutine-context-explained--kotlin--medium]] - Coroutines
- [[q-coroutine-builders-comparison--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-flow-testing-advanced--kotlin--hard]] - Flow

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

## References
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [async Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/async.html)

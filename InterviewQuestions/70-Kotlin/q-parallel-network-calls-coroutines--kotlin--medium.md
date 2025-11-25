---
id: kotlin-037
title: "How to make parallel network calls using coroutines? / Как выполнять параллельные сетевые запросы с помощью корутин?"
aliases: ["How to make parallel network calls using coroutines?", "Как выполнять параллельные сетевые запросы с помощью корутин?"]

# Classification
topic: kotlin
subtopics: [coroutines]
question_kind: coding
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-kotlin-coroutines-introduction--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-11-09

tags: [async, coroutines, difficulty/medium, kotlin, networking, parallel, performance]
date created: Saturday, November 1st 2025, 9:25:31 am
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---

# Вопрос (RU)
> Как выполнить несколько сетевых запросов параллельно с помощью Kotlin корутин?

---

# Question (EN)
> How do you make multiple network calls in parallel using Kotlin coroutines?

---

## Ответ (RU)

Выполнение параллельных сетевых запросов — распространенное требование в Android-приложениях для улучшения производительности и сокращения времени загрузки. Kotlin coroutines позволяют элегантно выполнять такие запросы конкурентно (обычно на `Dispatchers.IO`).

### 1. Использование `async` И `await`

```kotlin
import kotlinx.coroutines.*

// API интерфейс
interface ApiService {
    suspend fun getUser(userId: String): User
    suspend fun getPosts(userId: String): List<Post>
    suspend fun getComments(userId: String): List<Comment>
}

lateinit var apiService: ApiService

// Параллельное выполнение с помощью async/await
suspend fun fetchUserData(userId: String): UserData = coroutineScope {
    // Запускаем все запросы конкурентно (логически параллельно)
    val userDeferred = async { apiService.getUser(userId) }
    val postsDeferred = async { apiService.getPosts(userId) }
    val commentsDeferred = async { apiService.getComments(userId) }

    // Ожидаем все результаты
    UserData(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        comments = commentsDeferred.await()
    )
}
```

// Использование во ViewModel
```kotlin
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    fun loadUserData(userId: String) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                _loading.value = true
                val userData = repository.fetchUserData(userId)
                _userData.postValue(userData)
            } catch (e: Exception) {
                _error.postValue(e.message)
            } finally {
                _loading.postValue(false)
            }
        }
    }
}
```

### 2. Обработка Частичных Ошибок

Для независимых запросов важно не "ронять" весь экран из-за одного сбоя. Можно оборачивать каждый `async` в `runCatching` или использовать `try-catch`.

```kotlin
data class ParallelResult<T>(
    val data: T? = null,
    val error: Exception? = null
)

// Предполагаем, что ApiService также объявляет suspend fun getSettings(userId: String): Settings

suspend fun fetchUserDataWithErrorHandling(userId: String): UserScreenData = coroutineScope {
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

### 3. Использование `awaitAll` Для Коллекций

```kotlin
suspend fun fetchMultipleUsers(userIds: List<String>): List<User> = coroutineScope {
    userIds.map { userId ->
        async { apiService.getUser(userId) }
    }.awaitAll()
}

suspend fun fetchMultipleUsersSafely(userIds: List<String>): List<User> = coroutineScope {
    userIds.map { userId ->
        async {
            runCatching { apiService.getUser(userId) }.getOrNull()
        }
    }.awaitAll().filterNotNull()
}
```

### 4. Использование `supervisorScope` Для Независимых Сбоев

Когда сбой одного запроса не должен отменять остальные:

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

### 5. Паттерн Гонки (Race) — Первый Успешный Результат

Получение первого успешного результата из нескольких источников, с отменой остальных:

```kotlin
suspend fun <T> raceForFirst(
    vararg blocks: suspend () -> T
): T = coroutineScope {
    val deferreds = blocks.map { block ->
        async {
            runCatching { block() }
        }
    }

    while (isActive) {
        val completed = deferreds.firstOrNull { it.isCompleted }
        if (completed != null) {
            val result = completed.await()
            if (result.isSuccess) {
                deferreds.filter { it != completed }.forEach { it.cancel() }
                return@coroutineScope result.getOrThrow()
            }
        }
        if (deferreds.all { it.isCompleted }) break
        yield()
    }

    throw Exception("All requests failed")
}
```

### 6. Ограничение Параллельных Запросов (throttling)

Ограничиваем количество одновременных запросов, чтобы не перегружать сервер:

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

class ThrottledApiClient(
    maxConcurrent: Int = 5
) {
    private val semaphore = Semaphore(maxConcurrent)

    suspend fun <T> throttled(block: suspend () -> T): T =
        semaphore.withPermit { block() }
}

// Пример использования
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

### 7. Пакетная (chunked) Параллельная Обработка

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

// С отслеживанием прогресса
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

### 8. Комбинирование Результатов С Помощью `Flow`

Будьте осторожны, чтобы не блокироваться на неудачных запросах; ошибки обрабатываем внутри корутины.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.channelFlow

fun fetchUsersFlow(userIds: List<String>): Flow<User> = channelFlow {
    userIds.forEach { userId ->
        launch {
            try {
                val user = apiService.getUser(userId)
                send(user)
            } catch (e: Exception) {
                Log.e("Fetch", "Failed to fetch user $userId", e)
            }
        }
    }
}
```

### 9. Реальный Пример: Экран Деталей Продукта

```kotlin
class ProductRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun loadProductDetails(productId: String): ProductDetails = coroutineScope {
        try {
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

### 10. Лучшие Практики

#### - ДЕЛАЙТЕ:

```kotlin
// Используйте coroutineScope для структурированной конкурентности
suspend fun fetchData() = coroutineScope {
    val data1 = async { api.fetch1() }
    val data2 = async { api.fetch2() }
    Result(data1.await(), data2.await())
}

// Обрабатывайте ошибки
suspend fun fetchSafely() = coroutineScope {
    val results = listOf(
        async { runCatching { api.fetch1() } },
        async { runCatching { api.fetch2() } }
    ).awaitAll()

    results.mapNotNull { it.getOrNull() }
}

// Используйте supervisorScope, когда ошибки независимы
suspend fun fetchIndependent() = supervisorScope {
    val d1 = async { api.fetch1() }
    val d2 = async { api.fetch2() }
    listOfNotNull(
        runCatching { d1.await() }.getOrNull(),
        runCatching { d2.await() }.getOrNull()
    )
}
```

#### - НЕ ДЕЛАЙТЕ:

```kotlin
// Не используйте GlobalScope в продакшене
suspend fun bad() {
    GlobalScope.async { }
}

// Не игнорируйте отмену
suspend fun bad2() = coroutineScope {
    async(NonCancellable) { }
}

// Не делайте последовательное ожидание, если нужен параллелизм
suspend fun bad3() = coroutineScope {
    val data1 = async { api.fetch1() }.await()
    val data2 = async { api.fetch2() }.await()
    // Это последовательное выполнение, не параллельное
}
```

### 11. Сравнение Производительности (упрощенно)

```kotlin
// Последовательный (медленный)
suspend fun sequentialFetch(): ProfileData {
    val user = apiService.getUser()
    val posts = apiService.getPosts()
    val friends = apiService.getFriends()
    return ProfileData(user, posts, friends)
    // Всего: ~3 секунды
}

// Параллельный (быстрый)
suspend fun parallelFetch(): ProfileData = coroutineScope {
    val userDeferred = async { apiService.getUser() }
    val postsDeferred = async { apiService.getPosts() }
    val friendsDeferred = async { apiService.getFriends() }
    ProfileData(
        userDeferred.await(),
        postsDeferred.await(),
        friendsDeferred.await()
    )
    // Всего: ~1 секунда (ограничено самым медленным запросом)
}
```

---

## Answer (EN)

Making parallel network calls is a common requirement in Android apps to improve performance and reduce loading time. Kotlin coroutines provide elegant ways to execute multiple network requests concurrently (typically on `Dispatchers.IO`).

### 1. Using `async` and `await`

The most straightforward approach for parallel execution:

```kotlin
import kotlinx.coroutines.*

// API interface
interface ApiService {
    suspend fun getUser(userId: String): User
    suspend fun getPosts(userId: String): List<Post>
    suspend fun getComments(userId: String): List<Comment>
}

lateinit var apiService: ApiService

// Parallel execution with async/await
suspend fun fetchUserData(userId: String): UserData = coroutineScope {
    // Launch all requests concurrently (logically in parallel)
    val userDeferred = async { apiService.getUser(userId) }
    val postsDeferred = async { apiService.getPosts(userId) }
    val commentsDeferred = async { apiService.getComments(userId) }

    // Wait for all results
    UserData(
        user = userDeferred.await(),
        posts = postsDeferred.await(),
        comments = commentsDeferred.await()
    )
}
```

Usage in ViewModel:

```kotlin
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    fun loadUserData(userId: String) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                _loading.value = true
                val userData = repository.fetchUserData(userId)
                _userData.postValue(userData)
            } catch (e: Exception) {
                _error.postValue(e.message)
            } finally {
                _loading.postValue(false)
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

// Assume ApiService also declares suspend fun getSettings(userId: String): Settings

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
            runCatching { apiService.getUser(userId) }.getOrNull()
        }
    }.awaitAll()
        .filterNotNull()
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

Get the first successful result from multiple sources, cancelling the rest:

```kotlin
suspend fun <T> raceForFirst(
    vararg blocks: suspend () -> T
): T = coroutineScope {
    val deferreds = blocks.map { block ->
        async {
            runCatching { block() }
        }
    }

    while (isActive) {
        val completed = deferreds.firstOrNull { it.isCompleted }
        if (completed != null) {
            val result = completed.await()
            if (result.isSuccess) {
                deferreds.filter { it != completed }.forEach { it.cancel() }
                return@coroutineScope result.getOrThrow()
            }
        }
        if (deferreds.all { it.isCompleted }) break
        yield()
    }

    throw Exception("All requests failed")
}
```

### 6. Throttling Parallel Requests

Limit concurrent requests to avoid overwhelming the server. Prefer `withPermit` from `kotlinx.coroutines.sync.Semaphore`:

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

class ThrottledApiClient(
    maxConcurrent: Int = 5
) {
    private val semaphore = Semaphore(maxConcurrent)

    suspend fun <T> throttled(block: suspend () -> T): T =
        semaphore.withPermit { block() }
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

Be careful not to block if some requests fail; handle errors inside launched coroutines.

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.channelFlow

fun fetchUsersFlow(userIds: List<String>): Flow<User> = channelFlow {
    userIds.forEach { userId ->
        launch {
            try {
                val user = apiService.getUser(userId)
                send(user)
            } catch (e: Exception) {
                Log.e("Fetch", "Failed to fetch user $userId", e)
            }
        }
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
    val d1 = async { api.fetch1() }
    val d2 = async { api.fetch2() }
    listOfNotNull(
        runCatching { d1.await() }.getOrNull(),
        runCatching { d2.await() }.getOrNull()
    )
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

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java без корутин?
- Когда на практике стоит использовать параллельные запросы, а когда лучше последовательные?
- Какие распространенные ошибки встречаются при использовании `async`/`await` и структурированной конкурентности?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-coroutines]]
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [async Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/async.html)

## References

- [[c-kotlin]]
- [[c-coroutines]]
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [async Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/async.html)

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-kotlin-coroutines-introduction--kotlin--medium]] — Введение в корутины
- [[q-deferred-async-patterns--kotlin--medium]] — Паттерны async/deferred
- [[q-coroutine-context-explained--kotlin--medium]] — Контекст корутины
- [[q-coroutine-builders-comparison--kotlin--medium]] — Сравнение билдров корутин

### Продвинутый Уровень
- [[q-flow-testing-advanced--kotlin--hard]] — Тестирование `Flow`

### Хаб
- [[q-kotlin-coroutines-introduction--kotlin--medium]] — Обзор по корутинам

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

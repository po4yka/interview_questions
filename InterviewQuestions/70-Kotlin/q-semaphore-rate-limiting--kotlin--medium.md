---
id: 20251012-160002
title: "Semaphore for rate limiting and resource pooling / Semaphore для ограничения скорости и пулов ресурсов"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-12
tags: - kotlin
  - coroutines
  - semaphore
  - rate-limiting
  - concurrency
  - resource-management
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-kotlin
related_questions:   - q-mutex-synchronized-coroutines--kotlin--medium
  - q-channelflow-callbackflow-flow--kotlin--medium
  - q-race-conditions-coroutines--kotlin--hard
slug: semaphore-rate-limiting-kotlin-medium
subtopics:   - coroutines
  - semaphore
  - rate-limiting
  - concurrency
  - resource-pool
---
# Semaphore for rate limiting and resource pooling

## English Version

### Problem Statement

In production systems, you often need to limit concurrent access to resources: restrict the number of simultaneous API calls, manage connection pools, or control parallel downloads. **Semaphore** from `kotlinx.coroutines.sync` provides a suspension-based mechanism to limit concurrent access without blocking threads.

**The Question:** How do you use Semaphore in Kotlin coroutines for rate limiting and resource pooling? What's the difference between Semaphore and Mutex?

### Detailed Answer

#### What is Semaphore?

**Semaphore** is a synchronization primitive that maintains a set of **permits**. Coroutines acquire permits to proceed and release them when done. Unlike Mutex (which is essentially a Semaphore with 1 permit), Semaphore can have multiple permits, allowing controlled concurrent access.

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

// Allow maximum 3 concurrent operations
val semaphore = Semaphore(permits = 3)

suspend fun limitedOperation() {
    semaphore.withPermit {
        // Only 3 coroutines can be here simultaneously
        performExpensiveOperation()
    }
}
```

#### Key Concepts

**Permits:**
- Number of coroutines that can enter critical section simultaneously
- `Semaphore(1)` = Mutex (mutual exclusion)
- `Semaphore(N)` = N concurrent operations allowed

**Operations:**
- `acquire()` - Acquire a permit, suspend if none available
- `release()` - Release a permit
- `withPermit { }` - Acquire, execute, release (recommended)
- `tryAcquire()` - Try to acquire without suspending
- `availablePermits` - Number of available permits

#### Semaphore vs Mutex

| Feature | Semaphore(N) | Mutex |
|---------|--------------|-------|
| **Permits** | N permits | 1 permit (special case) |
| **Concurrency** | N coroutines | 1 coroutine |
| **Use case** | Resource pooling, rate limiting | Mutual exclusion |
| **Relationship** | General | Special case of Semaphore |

```kotlin
// These are equivalent:
val mutex = Mutex()
val semaphoreAsMutex = Semaphore(1)

// Mutex is optimized for single permit case
// Use Mutex when you need mutual exclusion
// Use Semaphore(N) when N > 1
```

#### Basic Semaphore Usage

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

suspend fun main() = coroutineScope {
    val semaphore = Semaphore(3) // Max 3 concurrent

    // Launch 10 coroutines
    val jobs = List(10) { index ->
        launch {
            println("[$index] Waiting for permit...")
            semaphore.withPermit {
                println("[$index] Got permit, working...")
                delay(1000) // Simulate work
                println("[$index] Done")
            }
        }
    }

    jobs.joinAll()
}

// Output shows only 3 coroutines working at a time:
// [0] Waiting for permit...
// [0] Got permit, working...
// [1] Waiting for permit...
// [1] Got permit, working...
// [2] Waiting for permit...
// [2] Got permit, working...
// [3] Waiting for permit...
// [4] Waiting for permit...
// ... (3-7 wait until first batch completes)
```

#### Pattern 1: Rate Limiting API Calls

**Problem:** Limit concurrent API calls to avoid overwhelming the server or hitting rate limits.

```kotlin
class RateLimitedApiClient(maxConcurrent: Int = 5) {
    private val semaphore = Semaphore(maxConcurrent)

    suspend fun makeRequest(url: String): Result<String> {
        return semaphore.withPermit {
            try {
                val response = performNetworkRequest(url)
                Result.success(response)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    private suspend fun performNetworkRequest(url: String): String {
        delay(500) // Simulate network call
        return "Response from $url"
    }
}

// Usage
suspend fun main() = coroutineScope {
    val client = RateLimitedApiClient(maxConcurrent = 3)

    // Launch 10 concurrent requests
    // Only 3 will execute simultaneously
    val results = List(10) { index ->
        async {
            client.makeRequest("https://api.example.com/data/$index")
        }
    }.awaitAll()

    results.forEach { result ->
        println(result.getOrNull())
    }
}
```

#### Pattern 2: Real Android Retrofit Example

```kotlin
class ImageDownloadRepository(
    private val api: ImageApi,
    maxConcurrentDownloads: Int = 3
) {
    private val downloadSemaphore = Semaphore(maxConcurrentDownloads)

    suspend fun downloadImages(urls: List<String>): List<Result<Bitmap>> {
        return coroutineScope {
            urls.map { url ->
                async {
                    downloadImage(url)
                }
            }.awaitAll()
        }
    }

    private suspend fun downloadImage(url: String): Result<Bitmap> {
        return downloadSemaphore.withPermit {
            try {
                Log.d("Download", "Starting download: $url")
                val response = api.downloadImage(url)
                val bitmap = response.byteStream().use { stream ->
                    BitmapFactory.decodeStream(stream)
                }
                Log.d("Download", "Completed download: $url")
                Result.success(bitmap)
            } catch (e: Exception) {
                Log.e("Download", "Failed download: $url", e)
                Result.failure(e)
            }
        }
    }
}

interface ImageApi {
    @GET
    suspend fun downloadImage(@Url url: String): ResponseBody
}

// Usage in ViewModel
class GalleryViewModel(
    private val repository: ImageDownloadRepository
) : ViewModel() {

    private val _images = MutableStateFlow<List<Bitmap>>(emptyList())
    val images: StateFlow<List<Bitmap>> = _images.asStateFlow()

    fun loadGallery(imageUrls: List<String>) {
        viewModelScope.launch {
            val results = repository.downloadImages(imageUrls)
            val successfulImages = results.mapNotNull { it.getOrNull() }
            _images.value = successfulImages
        }
    }
}
```

#### Pattern 3: Database Connection Pool

```kotlin
class DatabaseConnectionPool(
    private val maxConnections: Int = 10
) {
    private val semaphore = Semaphore(maxConnections)
    private val connections = mutableListOf<DatabaseConnection>()
    private val mutex = Mutex() // Protect connections list

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T {
        // Acquire permit (wait if pool exhausted)
        semaphore.withPermit {
            val connection = mutex.withLock {
                // Try to reuse existing connection
                connections.removeFirstOrNull() ?: createConnection()
            }

            try {
                return block(connection)
            } finally {
                // Return connection to pool
                mutex.withLock {
                    if (connection.isValid()) {
                        connections.add(connection)
                    } else {
                        connection.close()
                    }
                }
            }
        }
    }

    private fun createConnection(): DatabaseConnection {
        println("Creating new database connection")
        return DatabaseConnection()
    }

    suspend fun close() {
        mutex.withLock {
            connections.forEach { it.close() }
            connections.clear()
        }
    }
}

class DatabaseConnection {
    private var closed = false

    suspend fun executeQuery(sql: String): List<Map<String, Any>> {
        delay(100) // Simulate query execution
        return emptyList()
    }

    fun isValid(): Boolean = !closed

    fun close() {
        closed = true
        println("Connection closed")
    }
}

// Usage
suspend fun main() = coroutineScope {
    val pool = DatabaseConnectionPool(maxConnections = 3)

    // Launch 10 concurrent database operations
    // Only 3 connections will be active at a time
    val jobs = List(10) { index ->
        launch {
            pool.withConnection { connection ->
                println("Query $index starting")
                val results = connection.executeQuery("SELECT * FROM users WHERE id = $index")
                println("Query $index completed")
            }
        }
    }

    jobs.joinAll()
    pool.close()
}
```

#### Pattern 4: Controlling Parallel Downloads

```kotlin
class ParallelDownloadManager(
    maxConcurrent: Int = 4
) {
    private val semaphore = Semaphore(maxConcurrent)

    data class DownloadProgress(
        val url: String,
        val bytesDownloaded: Long,
        val totalBytes: Long
    )

    suspend fun downloadFiles(
        urls: List<String>,
        onProgress: (DownloadProgress) -> Unit
    ): List<Result<File>> {
        return coroutineScope {
            urls.map { url ->
                async {
                    downloadFile(url, onProgress)
                }
            }.awaitAll()
        }
    }

    private suspend fun downloadFile(
        url: String,
        onProgress: (DownloadProgress) -> Unit
    ): Result<File> {
        return semaphore.withPermit {
            try {
                val file = File.createTempFile("download", ".tmp")
                val totalBytes = 1024 * 1024L // 1MB for example

                // Simulate download with progress
                var downloaded = 0L
                while (downloaded < totalBytes) {
                    delay(100)
                    downloaded += 10240 // 10KB chunks
                    onProgress(DownloadProgress(url, downloaded, totalBytes))
                }

                Result.success(file)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}

// Android ViewModel usage
class DownloadViewModel : ViewModel() {
    private val downloadManager = ParallelDownloadManager(maxConcurrent = 3)

    private val _downloadProgress = MutableStateFlow<Map<String, Float>>(emptyMap())
    val downloadProgress: StateFlow<Map<String, Float>> = _downloadProgress.asStateFlow()

    fun downloadFiles(urls: List<String>) {
        viewModelScope.launch {
            downloadManager.downloadFiles(urls) { progress ->
                val percentage = progress.bytesDownloaded.toFloat() / progress.totalBytes
                _downloadProgress.update { currentProgress ->
                    currentProgress + (progress.url to percentage)
                }
            }
        }
    }
}
```

#### Fair vs Unfair Semaphores

By default, Semaphore in kotlinx.coroutines is **unfair** - permits may be granted out of order.

```kotlin
// Default: unfair (faster, but no ordering guarantee)
val unfairSemaphore = Semaphore(permits = 3)

// To implement fair semaphore, use Channel:
class FairSemaphore(permits: Int) {
    private val channel = Channel<Unit>(permits)

    init {
        repeat(permits) {
            channel.trySend(Unit)
        }
    }

    suspend fun acquire() {
        channel.receive()
    }

    fun release() {
        channel.trySend(Unit)
    }

    suspend inline fun <T> withPermit(action: () -> T): T {
        acquire()
        try {
            return action()
        } finally {
            release()
        }
    }
}
```

#### Timeout on Acquire

```kotlin
import kotlinx.coroutines.withTimeoutOrNull

val semaphore = Semaphore(3)

suspend fun tryAcquireWithTimeout(): Boolean {
    return withTimeoutOrNull(1000) {
        semaphore.withPermit {
            // Got permit within timeout
            performOperation()
            true
        }
    } ?: false // Timeout occurred
}

// Or use tryAcquire for non-blocking attempt
fun tryAcquireNonBlocking(): Boolean {
    if (semaphore.tryAcquire()) {
        try {
            // Got permit immediately
            return true
        } finally {
            semaphore.release()
        }
    }
    return false // No permits available
}
```

#### Real-World: Rate-Limited API Client with Backoff

```kotlin
class ProductionApiClient(
    maxConcurrentRequests: Int = 10,
    private val requestsPerSecond: Int = 100
) {
    private val concurrencyLimiter = Semaphore(maxConcurrentRequests)
    private val rateLimiter = TokenBucketRateLimiter(requestsPerSecond)

    suspend fun <T> executeRequest(
        request: suspend () -> T
    ): Result<T> {
        return concurrencyLimiter.withPermit {
            rateLimiter.acquire() // Wait for rate limit token

            try {
                val result = request()
                Result.success(result)
            } catch (e: Exception) {
                when (e) {
                    is HttpException -> handleHttpError(e)
                    else -> Result.failure(e)
                }
            }
        }
    }

    private fun handleHttpError(e: HttpException): Result<Nothing> {
        return when (e.code()) {
            429 -> {
                // Too Many Requests - rate limit exceeded
                Result.failure(RateLimitException("Rate limit exceeded", e))
            }
            else -> Result.failure(e)
        }
    }
}

class TokenBucketRateLimiter(private val tokensPerSecond: Int) {
    private val mutex = Mutex()
    private var tokens = tokensPerSecond.toDouble()
    private var lastRefillTime = System.currentTimeMillis()

    suspend fun acquire() {
        mutex.withLock {
            refillTokens()

            while (tokens < 1.0) {
                // Not enough tokens, wait and try again
                val waitTime = ((1.0 - tokens) / tokensPerSecond * 1000).toLong()
                mutex.unlock()
                delay(waitTime.coerceAtLeast(10))
                mutex.lock()
                refillTokens()
            }

            tokens -= 1.0
        }
    }

    private fun refillTokens() {
        val now = System.currentTimeMillis()
        val elapsedSeconds = (now - lastRefillTime) / 1000.0
        val tokensToAdd = elapsedSeconds * tokensPerSecond

        tokens = (tokens + tokensToAdd).coerceAtMost(tokensPerSecond.toDouble())
        lastRefillTime = now
    }
}

class RateLimitException(message: String, cause: Throwable) : Exception(message, cause)
class HttpException(private val statusCode: Int, message: String) : Exception(message) {
    fun code() = statusCode
}
```

#### Error Handling and Permit Cleanup

**Critical:** Always use `withPermit` to ensure permits are released even on exceptions:

```kotlin
val semaphore = Semaphore(3)

//  BAD: Manual acquire/release
suspend fun badExample() {
    semaphore.acquire()
    performOperation() // Exception here leaks permit!
    semaphore.release()
}

//  GOOD: withPermit handles cleanup
suspend fun goodExample() {
    semaphore.withPermit {
        performOperation() // Exception here automatically releases permit
    }
}

//  BAD: Try-catch without finally
suspend fun badWithTryCatch() {
    try {
        semaphore.acquire()
        performOperation()
        semaphore.release()
    } catch (e: Exception) {
        // Forgot to release!
    }
}

//  GOOD: Manual acquire with try-finally
suspend fun manualAcquireCorrect() {
    semaphore.acquire()
    try {
        performOperation()
    } finally {
        semaphore.release()
    }
}
```

#### Advanced: Dynamic Semaphore Sizing

```kotlin
class AdaptiveSemaphore(
    initialPermits: Int,
    private val minPermits: Int = 1,
    private val maxPermits: Int = 100
) {
    private val mutex = Mutex()
    private var semaphore = Semaphore(initialPermits)
    private var currentPermits = initialPermits

    suspend fun increasePermits(delta: Int = 1) {
        mutex.withLock {
            val newPermits = (currentPermits + delta).coerceAtMost(maxPermits)
            if (newPermits > currentPermits) {
                // Create new semaphore with more permits
                val oldSemaphore = semaphore
                semaphore = Semaphore(newPermits)
                currentPermits = newPermits
                println("Increased permits to $currentPermits")
            }
        }
    }

    suspend fun decreasePermits(delta: Int = 1) {
        mutex.withLock {
            val newPermits = (currentPermits - delta).coerceAtLeast(minPermits)
            if (newPermits < currentPermits) {
                // Acquire delta permits to effectively reduce capacity
                repeat(delta) {
                    semaphore.tryAcquire()
                }
                currentPermits = newPermits
                println("Decreased permits to $currentPermits")
            }
        }
    }

    suspend fun <T> withPermit(action: suspend () -> T): T {
        return semaphore.withPermit(action)
    }
}

// Usage: adapt based on system load
class AdaptiveApiClient {
    private val semaphore = AdaptiveSemaphore(initialPermits = 10)
    private var consecutiveErrors = 0

    suspend fun makeRequest(url: String): Result<String> {
        return semaphore.withPermit {
            try {
                val response = performRequest(url)
                onSuccess()
                Result.success(response)
            } catch (e: Exception) {
                onError()
                Result.failure(e)
            }
        }
    }

    private suspend fun onSuccess() {
        consecutiveErrors = 0
        // Gradually increase capacity on success
        if (consecutiveErrors == 0) {
            semaphore.increasePermits(1)
        }
    }

    private suspend fun onError() {
        consecutiveErrors++
        // Reduce capacity on repeated errors
        if (consecutiveErrors >= 5) {
            semaphore.decreasePermits(2)
        }
    }

    private suspend fun performRequest(url: String): String {
        delay(100)
        return "Response"
    }
}
```

#### Testing Semaphore-Based Code

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class SemaphoreTest {
    @Test
    fun `semaphore limits concurrent access`() = runTest {
        val semaphore = Semaphore(3)
        var maxConcurrent = 0
        var currentConcurrent = 0
        val mutex = Mutex()

        val jobs = List(10) {
            launch {
                semaphore.withPermit {
                    mutex.withLock {
                        currentConcurrent++
                        maxConcurrent = maxOf(maxConcurrent, currentConcurrent)
                    }

                    delay(100)

                    mutex.withLock {
                        currentConcurrent--
                    }
                }
            }
        }

        jobs.joinAll()

        assertEquals(3, maxConcurrent, "Should not exceed semaphore limit")
    }

    @Test
    fun `withPermit releases on exception`() = runTest {
        val semaphore = Semaphore(1)

        try {
            semaphore.withPermit {
                throw RuntimeException("Test exception")
            }
        } catch (e: RuntimeException) {
            // Expected
        }

        // Permit should be released, this should not hang
        val acquired = semaphore.tryAcquire()
        assertTrue(acquired, "Permit should be available after exception")
        semaphore.release()
    }

    @Test
    fun `rate limiter respects limits`() = runTest {
        val client = RateLimitedApiClient(maxConcurrent = 3)
        val startTime = System.currentTimeMillis()

        // 9 requests with limit of 3 concurrent, each takes 500ms
        // Should complete in ~1500ms (3 batches)
        val results = List(9) {
            async {
                client.makeRequest("url")
            }
        }.awaitAll()

        val duration = System.currentTimeMillis() - startTime
        assertTrue(duration >= 1400, "Should take at least 3 batches")
        assertEquals(9, results.size)
    }
}
```

### Common Pitfalls and Best Practices

#### Pitfalls

1. **Manual acquire/release without finally** - Leaks permits on exception
2. **Using too few permits** - Bottleneck, underutilizes resources
3. **Using too many permits** - Defeats rate limiting purpose
4. **Not handling cancellation** - Use `withPermit` for automatic cleanup
5. **Mixing Semaphore with blocking operations** - Blocks threads, wastes resources
6. **Creating new Semaphore per operation** - Should be shared singleton
7. **Not considering permit starvation** - Some coroutines may wait indefinitely

#### Best Practices

1.  Always use `withPermit` instead of manual acquire/release
2.  Size permits based on resource limits (connections, API limits)
3.  Monitor and adjust permits based on system performance
4.  Use separate semaphores for different resource types
5.  Combine with other rate limiting strategies (token bucket)
6.  Test concurrent access thoroughly
7.  Log permit acquisition for debugging
8.  Consider fair vs unfair based on requirements

### When to Use Semaphore

**Use Semaphore when:**
- Limiting concurrent API calls (max N requests at once)
- Managing resource pools (database connections, HTTP clients)
- Controlling parallel downloads/uploads
- Rate limiting at concurrency level
- Any scenario where N > 1 coroutines can access resource

**Don't use Semaphore when:**
- N = 1 (use Mutex instead, it's optimized)
- Simple counter operations (use AtomicInteger)
- Time-based rate limiting only (use token bucket)
- No resource contention (no need for limiting)

### Key Takeaways

1. **Semaphore = generalized Mutex** - Allows N concurrent accesses
2. **Perfect for rate limiting** - Control concurrent API calls
3. **Use `withPermit`** - Ensures proper cleanup on exceptions
4. **Size permits appropriately** - Based on resource constraints
5. **Combine with other limiters** - Concurrency + time-based rate limiting
6. **Monitor performance** - Adjust permits based on system behavior
7. **Test concurrent scenarios** - Verify limits are respected

---

## Русская версия

### Формулировка проблемы

В продакшн-системах часто нужно ограничивать конкурентный доступ к ресурсам: ограничить количество одновременных API вызовов, управлять пулами подключений или контролировать параллельные загрузки. **Semaphore** из `kotlinx.coroutines.sync` предоставляет механизм на основе приостановки для ограничения конкурентного доступа без блокировки потоков.

**Вопрос:** Как использовать Semaphore в Kotlin корутинах для ограничения скорости и пулов ресурсов? В чем разница между Semaphore и Mutex?

### Подробный ответ

#### Что такое Semaphore?

**Semaphore** - это примитив синхронизации, который поддерживает набор **разрешений (permits)**. Корутины получают разрешения для продолжения и освобождают их после завершения. В отличие от Mutex (который по сути является Semaphore с 1 разрешением), Semaphore может иметь несколько разрешений, позволяя контролируемый конкурентный доступ.

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

// Разрешить максимум 3 одновременные операции
val semaphore = Semaphore(permits = 3)

suspend fun limitedOperation() {
    semaphore.withPermit {
        // Только 3 корутины могут быть здесь одновременно
        performExpensiveOperation()
    }
}
```

#### Ключевые концепции

**Разрешения (Permits):**
- Количество корутин, которые могут войти в критическую секцию одновременно
- `Semaphore(1)` = Mutex (взаимное исключение)
- `Semaphore(N)` = N одновременных операций разрешено

**Операции:**
- `acquire()` - Получить разрешение, приостановить если недоступно
- `release()` - Освободить разрешение
- `withPermit { }` - Получить, выполнить, освободить (рекомендуется)
- `tryAcquire()` - Попытаться получить без приостановки
- `availablePermits` - Количество доступных разрешений

#### Паттерн 1: Ограничение скорости API вызовов

```kotlin
class RateLimitedApiClient(maxConcurrent: Int = 5) {
    private val semaphore = Semaphore(maxConcurrent)

    suspend fun makeRequest(url: String): Result<String> {
        return semaphore.withPermit {
            try {
                val response = performNetworkRequest(url)
                Result.success(response)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }

    private suspend fun performNetworkRequest(url: String): String {
        delay(500) // Имитация сетевого вызова
        return "Ответ от $url"
    }
}
```

#### Паттерн 2: Реальный пример Android Retrofit

```kotlin
class ImageDownloadRepository(
    private val api: ImageApi,
    maxConcurrentDownloads: Int = 3
) {
    private val downloadSemaphore = Semaphore(maxConcurrentDownloads)

    suspend fun downloadImages(urls: List<String>): List<Result<Bitmap>> {
        return coroutineScope {
            urls.map { url ->
                async {
                    downloadImage(url)
                }
            }.awaitAll()
        }
    }

    private suspend fun downloadImage(url: String): Result<Bitmap> {
        return downloadSemaphore.withPermit {
            try {
                Log.d("Download", "Начало загрузки: $url")
                val response = api.downloadImage(url)
                val bitmap = response.byteStream().use { stream ->
                    BitmapFactory.decodeStream(stream)
                }
                Log.d("Download", "Завершена загрузка: $url")
                Result.success(bitmap)
            } catch (e: Exception) {
                Log.e("Download", "Ошибка загрузки: $url", e)
                Result.failure(e)
            }
        }
    }
}
```

#### Паттерн 3: Пул подключений к базе данных

```kotlin
class DatabaseConnectionPool(
    private val maxConnections: Int = 10
) {
    private val semaphore = Semaphore(maxConnections)
    private val connections = mutableListOf<DatabaseConnection>()
    private val mutex = Mutex() // Защита списка подключений

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T {
        // Получаем разрешение (ждем если пул исчерпан)
        semaphore.withPermit {
            val connection = mutex.withLock {
                // Пытаемся переиспользовать существующее подключение
                connections.removeFirstOrNull() ?: createConnection()
            }

            try {
                return block(connection)
            } finally {
                // Возвращаем подключение в пул
                mutex.withLock {
                    if (connection.isValid()) {
                        connections.add(connection)
                    } else {
                        connection.close()
                    }
                }
            }
        }
    }

    private fun createConnection(): DatabaseConnection {
        println("Создание нового подключения к БД")
        return DatabaseConnection()
    }

    suspend fun close() {
        mutex.withLock {
            connections.forEach { it.close() }
            connections.clear()
        }
    }
}
```

### Ключевые выводы

1. **Semaphore = обобщенный Mutex** - Разрешает N одновременных доступов
2. **Идеален для ограничения скорости** - Контролирует конкурентные API вызовы
3. **Используйте `withPermit`** - Обеспечивает правильную очистку при исключениях
4. **Правильно подбирайте количество разрешений** - На основе ограничений ресурсов
5. **Комбинируйте с другими ограничителями** - Конкурентность + временное ограничение
6. **Мониторьте производительность** - Корректируйте разрешения на основе поведения системы
7. **Тестируйте конкурентные сценарии** - Проверяйте соблюдение лимитов

---

## Follow-ups

1. How would you implement a token bucket rate limiter using Semaphore?
2. What's the difference between fair and unfair semaphores in terms of performance?
3. How do you handle semaphore permit leaks in long-running applications?
4. Can you explain how to implement adaptive semaphore sizing based on error rates?
5. How does Semaphore interact with coroutine cancellation?
6. When would you use Semaphore vs Flow.flatMapMerge with concurrency limit?
7. How do you test that semaphore limits are correctly enforced?

## References

- [Kotlinx.coroutines Semaphore Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-semaphore/)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Rate Limiting Patterns](https://stripe.com/blog/rate-limiters)
- [Resource Pooling Best Practices](https://www.baeldung.com/kotlin/resource-pooling)

## Related Questions

- [[q-mutex-synchronized-coroutines--kotlin--medium|Mutex vs synchronized in Kotlin coroutines]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|channelFlow vs callbackFlow vs flow]]
- [[q-race-conditions-coroutines--kotlin--hard|Race conditions in Kotlin coroutines]]

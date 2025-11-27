---
id: kotlin-107
title: "Semaphore for rate limiting and resource pooling / Semaphore для ограничения скорости и пулов ресурсов"
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
tags: [concurrency, coroutines, difficulty/medium, kotlin, rate-limiting, resource-management, semaphore]
aliases: ["Semaphore rate limiting and resource pooling in Kotlin", "Semaphore для ограничения скорости и пулов ресурсов в Kotlin"]
moc: moc-kotlin
question_kind: coding
related: [c-coroutines, c-kotlin, q-channelflow-callbackflow-flow--kotlin--medium, q-mutex-synchronized-coroutines--kotlin--medium, q-race-conditions-coroutines--kotlin--hard]
subtopics:
  - concurrency
  - coroutines
  - semaphore
date created: Saturday, November 1st 2025, 12:10:12 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---
# Вопрос (RU)
> Как использовать Semaphore в Kotlin корутинах для ограничения скорости и пулов ресурсов? В чем разница между Semaphore и Mutex?

---

# Question (EN)
> How do you use Semaphore in Kotlin coroutines for rate limiting and resource pooling? What's the difference between Semaphore and Mutex?

## Ответ (RU)

В продакшн-системах часто нужно ограничивать конкурентный доступ к ресурсам: ограничить количество одновременных API вызовов, управлять пулами подключений или контролировать параллельные загрузки. **Semaphore** из `kotlinx.coroutines.sync` предоставляет механизм на основе приостановки для ограничения конкурентного доступа без блокировки потоков.

### Что Такое Semaphore?

**Semaphore** - это примитив синхронизации, который поддерживает набор **разрешений (permits)**. Корутины получают разрешения для продолжения и освобождают их после завершения. В отличие от `Mutex`, который обеспечивает взаимное исключение для одного владельца, Semaphore может иметь несколько разрешений, позволяя контролируемый конкурентный доступ.

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

### Ключевые Концепции

**Разрешения (Permits):**
- Количество корутин, которые могут войти в критическую секцию одновременно
- `Semaphore(1)` "похож" на Mutex по семантике взаимного исключения, но Mutex имеет дополнительные гарантии (владелец, разблокировка тем же владельцем, оптимизации) и специализированный API
- `Semaphore(N)` = N одновременных операций разрешено

**Операции:**
- `acquire()` - получить разрешение, приостановить если недоступно
- `release()` - освободить разрешение
- `withPermit { }` - получить, выполнить, освободить (рекомендуется)
- `tryAcquire()` - попытаться получить без приостановки
- `availablePermits` - количество доступных разрешений

### Semaphore Vs Mutex (RU)

- Mutex предназначен для взаимного исключения (N = 1) и отслеживает владельца; `unlock` должен вызывать тот, кто успешно `lock`.
- Semaphore управляет счетчиком разрешений и не отслеживает владельца; любая корутина может вызвать `release`.
- Для чистого взаимного исключения используйте `Mutex`.
- Для ограничения N одновременных операций используйте `Semaphore(N)`.

```kotlin
val mutex = Mutex()
val semaphore = Semaphore(1) // Похожий эффект по конкурентности, но другие семантические гарантии
```

### Базовое Использование Semaphore

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

suspend fun main() = coroutineScope {
    val semaphore = Semaphore(3) // Максимум 3 одновременно

    // Запускаем 10 корутин
    val jobs = List(10) { index ->
        launch {
            println("[$index] Ожидание разрешения...")
            semaphore.withPermit {
                println("[$index] Получено разрешение, работа...")
                delay(1000) // Имитация работы
                println("[$index] Готово")
            }
        }
    }

    jobs.joinAll()
}

// В выводе одновременно работают только 3 корутины.
```

### Паттерн 1: Ограничение Конкурентности API Вызовов

(Важно: этот пример ограничивает именно количество одновременных запросов, а не запросов в секунду.)

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

suspend fun main() = coroutineScope {
    val client = RateLimitedApiClient(maxConcurrent = 3)

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

### Паттерн 2: Реальный Пример Android Retrofit

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

interface ImageApi {
    @GET
    suspend fun downloadImage(@Url url: String): ResponseBody
}

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

### Паттерн 3: Пул Подключений К Базе Данных

```kotlin
class DatabaseConnectionPool(
    private val maxConnections: Int = 10
) {
    private val semaphore = Semaphore(maxConnections)
    private val connections = mutableListOf<DatabaseConnection>()
    private val mutex = Mutex() // Защита списка подключений

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T {
        return semaphore.withPermit {
            val connection = mutex.withLock {
                // Пытаемся переиспользовать существующее подключение
                connections.removeFirstOrNull() ?: createConnection()
            }

            try {
                block(connection)
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

class DatabaseConnection {
    private var closed = false

    suspend fun executeQuery(sql: String): List<Map<String, Any>> {
        delay(100) // Имитация выполнения запроса
        return emptyList()
    }

    fun isValid(): Boolean = !closed

    fun close() {
        closed = true
        println("Подключение закрыто")
    }
}

suspend fun main() = coroutineScope {
    val pool = DatabaseConnectionPool(maxConnections = 3)

    val jobs = List(10) { index ->
        launch {
            pool.withConnection { connection ->
                println("Запрос $index старт")
                val results = connection.executeQuery("SELECT * FROM users WHERE id = $index")
                println("Запрос $index завершен")
            }
        }
    }

    jobs.joinAll()
    pool.close()
}
```

### Паттерн 4: Контроль Параллельных Загрузок

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
                val totalBytes = 1024 * 1024L // 1MB для примера

                // Имитация загрузки с прогрессом
                var downloaded = 0L
                while (downloaded < totalBytes) {
                    delay(100)
                    downloaded += 10240 // шагами по 10KB
                    onProgress(DownloadProgress(url, downloaded, totalBytes))
                }

                Result.success(file)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}

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

### Честные И Нечестные Semaphore

По умолчанию `Semaphore` в `kotlinx.coroutines` **нечестный** — нет строгой FIFO-гарантии порядка получения разрешений, возможна относительная "несправедливость" и даже голодание при высоких нагрузках.

Для моделирования более справедливого поведения можно строить обертки (например, через `Channel` и обработку запросов по очереди), но это требует аккуратного дизайна; полноценная реализация честного семафора выходит за рамки этого заметки.

```kotlin
// По умолчанию: нечестный (без строгой FIFO-гарантии)
val unfairSemaphore = Semaphore(permits = 3)
```

### Таймаут При Получении Разрешения

```kotlin
import kotlinx.coroutines.withTimeoutOrNull

val semaphore = Semaphore(3)

suspend fun tryWithTimeout(): Boolean {
    val success = withTimeoutOrNull(1000) {
        semaphore.withPermit {
            performOperation()
            true
        }
    }
    return success == true // false, если произошел таймаут до получения/завершения
}

// Неблокирующая попытка
fun tryAcquireNonBlocking(): Boolean {
    return if (semaphore.tryAcquire()) {
        try {
            // Получили разрешение, выполняем быструю операцию
            true
        } finally {
            semaphore.release()
        }
    } else {
        false // Нет доступных разрешений
    }
}
```

### Реальный Мир: Совмещение Конкурентности И Лимита По Времени

Ниже упрощенный пример, где семафор ограничивает параллелизм, а отдельный тайм-бэйз лимитер — число запросов в секунду. Детали реализации иллюстративны.

```kotlin
class ProductionApiClient(
    maxConcurrentRequests: Int = 10,
    private val requestsPerSecond: Int = 100
) {
    private val concurrencyLimiter = Semaphore(maxConcurrentRequests)
    private val rateLimiter = SimpleTokenBucketRateLimiter(requestsPerSecond)

    suspend fun <T> executeRequest(
        request: suspend () -> T
    ): Result<T> {
        return concurrencyLimiter.withPermit {
            rateLimiter.acquireToken()
            try {
                Result.success(request())
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}

class SimpleTokenBucketRateLimiter(private val tokensPerSecond: Int) {
    private val mutex = Mutex()
    private var tokens = tokensPerSecond.toDouble()
    private var lastRefillTime = System.currentTimeMillis()

    private fun refillTokens(now: Long) {
        val elapsedSeconds = (now - lastRefillTime) / 1000.0
        if (elapsedSeconds <= 0) return
        val tokensToAdd = elapsedSeconds * tokensPerSecond
        tokens = (tokens + tokensToAdd).coerceAtMost(tokensPerSecond.toDouble())
        lastRefillTime = now
    }

    suspend fun acquireToken() {
        while (true) {
            val waitMillis = mutex.withLock {
                val now = System.currentTimeMillis()
                refillTokens(now)
                return@withLock if (tokens >= 1.0) {
                    tokens -= 1.0
                    0L
                } else {
                    val needed = 1.0 - tokens
                    ((needed / tokensPerSecond) * 1000).toLong().coerceAtLeast(10)
                }
            }
            if (waitMillis == 0L) return
            delay(waitMillis)
        }
    }
}
```

### Обработка Ошибок И Корректное Освобождение Разрешений

Критично: всегда гарантировать освобождение разрешений при исключениях и отмене.

```kotlin
val semaphore = Semaphore(3)

// ПЛОХО: без finally можно "потерять" разрешение
suspend fun badExample() {
    semaphore.acquire()
    performOperation() // Исключение здесь приведет к утечке разрешения
    semaphore.release()
}

// ХОРОШО: withPermit сам освободит разрешение
suspend fun goodExample() {
    semaphore.withPermit {
        performOperation()
    }
}

// ПРАВИЛЬНО ВРУЧНУЮ: try-finally
suspend fun manualAcquireCorrect() {
    semaphore.acquire()
    try {
        performOperation()
    } finally {
        semaphore.release()
    }
}
```

### (Упрощенный) Пример Адаптивной Конкурентности

Простая и безопасная идея: увеличивать параллелизм за счет дополнительных `release`, а уменьшать — за счет ограничения маршрутизации через лимитер или реконфигурации в контролируемые моменты. Динамический ресайз активно работающего семафора сложен и обычно требует пересоздания лимитера; небезопасные подходы намеренно опущены.

```kotlin
class AdaptiveConcurrencyLimiter(initialPermits: Int) {
    private val semaphore = Semaphore(initialPermits)

    suspend fun <T> withPermit(block: suspend () -> T): T {
        return semaphore.withPermit { block() }
    }

    // Для реального динамического ресайза лучше пересоздавать лимитер
    // в контролируемые моменты или использовать более высокоуровневую координацию.
}
```

### Тестирование Кода С Семафорами

```kotlin
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.*
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

        assertEquals(3, maxConcurrent, "Не должно превышать лимит семафора")
    }

    @Test
    fun `withPermit releases on exception`() = runTest {
        val semaphore = Semaphore(1)

        try {
            semaphore.withPermit {
                throw RuntimeException("Test exception")
            }
        } catch (_: RuntimeException) {
            // Ожидаем
        }

        val acquired = semaphore.tryAcquire()
        assertTrue(acquired, "Разрешение должно быть доступно после исключения")
        semaphore.release()
    }
}
```

### Типичные Ошибки И Лучшие Практики

#### Ошибки

1. Ручной `acquire`/`release` без `finally` -> утечка разрешений.
2. Слишком мало разрешений -> узкое место и недоиспользование ресурсов.
3. Слишком много разрешений -> фактическое отсутствие лимита.
4. Игнорирование отмены -> используйте `withPermit`, он безопасен.
5. Оборачивать блокирующие операции на ограниченном пуле потоков -> риск исчерпания потоков.
6. Создание нового `Semaphore` на каждую операцию вместо шаринга.
7. Игнорирование возможного голодания при нечестном семафоре.

#### Практики

1. Предпочитайте `withPermit` вместо ручного управления.
2. Подбирайте число разрешений по реальным лимитам ресурсов.
3. Отдельные семафоры для разных типов ресурсов.
4. Комбинируйте ограничение по конкурентности с лимитами по времени при необходимости.
5. Тестируйте конкурентный доступ и проверяйте отсутствие утечек разрешений.
6. Логируйте ожидание разрешений и времена для отладки.

### Когда Использовать Semaphore

Используйте Semaphore, когда нужно:
- Ограничить количество одновременных API вызовов.
- Управлять пулами ресурсов (подключения к БД, клиенты HTTP).
- Контролировать параллельные загрузки/выгрузки.
- Ввести лимит конкурентности, где N > 1.

Не используйте Semaphore, когда:
- Нужна строгая взаимная блокировка одной критической секции -> лучше `Mutex`.
- Нужны атомарные счетчики -> подойдут атомики.
- Нужен чисто временной rate limiting без ограничения параллелизма -> используйте специализированные алгоритмы (token bucket, leaky bucket и т.п.).

### Ключевые Выводы

1. Semaphore подходит для ограничения конкурентного доступа по числу разрешений.
2. Идеален для ограничения по конкурентности (API вызовы, загрузки, пулы).
3. Используйте `withPermit` для корректного освобождения при исключениях и отмене.
4. Размер пула разрешений должен соответствовать реальной емкости ресурсов.
5. При необходимости комбинируйте с временными лимитерами.
6. Тестируйте конкурентное поведение, проверяйте отсутствие утечек и возможное голодание.

---

## Answer (EN)

In production systems, you often need to limit concurrent access to resources: restrict the number of simultaneous API calls, manage connection pools, or control parallel downloads. **Semaphore** from `kotlinx.coroutines.sync` provides a suspension-based mechanism to limit concurrent access without blocking threads.

### What is Semaphore?

**Semaphore** is a synchronization primitive that maintains a set of **permits**. Coroutines acquire permits to proceed and release them when done. Unlike `Mutex`, which is designed for mutual exclusion with a single owner, `Semaphore` can hold multiple permits, allowing controlled concurrent access.

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

### Key Concepts

**Permits:**
- Number of coroutines that can enter the critical section simultaneously
- `Semaphore(1)` behaves similarly to a single-permit lock, but `Mutex` offers owner tracking and is the preferred primitive for mutual exclusion
- `Semaphore(N)` = N concurrent operations allowed

**Operations:**
- `acquire()` - acquire a permit, suspend if none available
- `release()` - release a permit
- `withPermit { }` - acquire, execute, release (recommended)
- `tryAcquire()` - try to acquire without suspending
- `availablePermits` - number of available permits

### Semaphore Vs Mutex

- Mutex is for mutual exclusion (effectively 1 permit) and tracks the owner.
- Semaphore manages a counter of permits and does not track owners; any coroutine may call `release`.
- Use `Mutex` when you need strict mutual exclusion.
- Use `Semaphore(N)` when you want to allow up to N concurrent operations.

```kotlin
val mutex = Mutex()
val semaphore = Semaphore(1) // Similar concurrency effect, but different semantics
```

### Basic Semaphore Usage

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

// Output shows only 3 coroutines working at a time.
```

### Pattern 1: Limiting Concurrent API Calls

(Note: this limits the number of simultaneous calls, not requests per second.)

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

suspend fun main() = coroutineScope {
    val client = RateLimitedApiClient(maxConcurrent = 3)

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

### Pattern 2: Real Android Retrofit Example

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

### Pattern 3: Database Connection Pool

```kotlin
class DatabaseConnectionPool(
    private val maxConnections: Int = 10
) {
    private val semaphore = Semaphore(maxConnections)
    private val connections = mutableListOf<DatabaseConnection>()
    private val mutex = Mutex() // Protect connections list

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T {
        return semaphore.withPermit {
            val connection = mutex.withLock {
                // Try to reuse existing connection
                connections.removeFirstOrNull() ?: createConnection()
            }

            try {
                block(connection)
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

suspend fun main() = coroutineScope {
    val pool = DatabaseConnectionPool(maxConnections = 3)

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

### Pattern 4: Controlling Parallel Downloads

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

### Fair Vs Unfair Semaphores

By default, Semaphore in kotlinx.coroutines is **unfair** - permits may be granted out of order, there is no strict FIFO guarantee, and under heavy load this can lead to relative unfairness or even starvation.

To model fair behavior, you can build higher-level constructs (e.g., using a Channel and processing requests in order), but fairness must be implemented carefully; a full fair semaphore implementation is beyond the scope of this note.

```kotlin
// Default: unfair (no strict FIFO guarantee)
val unfairSemaphore = Semaphore(permits = 3)
```

### Timeout on Acquire

```kotlin
import kotlinx.coroutines.withTimeoutOrNull

val semaphore = Semaphore(3)

suspend fun tryWithTimeout(): Boolean {
    val success = withTimeoutOrNull(1000) {
        semaphore.withPermit {
            performOperation()
            true
        }
    }
    return success == true // false if timeout occurred before acquiring/finishing
}

// Or use tryAcquire for a non-suspending attempt
fun tryAcquireNonBlocking(): Boolean {
    return if (semaphore.tryAcquire()) {
        try {
            // Got permit immediately, perform quick operation
            true
        } finally {
            semaphore.release()
        }
    } else {
        false // No permits available
    }
}
```

### Real-World: Concurrency + Time-Based Rate Limiting

Below is a simplified example combining a semaphore (concurrency limit) with a token-bucket-style limiter (time-based). Implementation details are illustrative; in production you should use a well-tested limiter.

```kotlin
class ProductionApiClient(
    maxConcurrentRequests: Int = 10,
    private val requestsPerSecond: Int = 100
) {
    private val concurrencyLimiter = Semaphore(maxConcurrentRequests)
    private val rateLimiter = SimpleTokenBucketRateLimiter(requestsPerSecond)

    suspend fun <T> executeRequest(
        request: suspend () -> T
    ): Result<T> {
        return concurrencyLimiter.withPermit {
            rateLimiter.acquireToken()
            try {
                Result.success(request())
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}

class SimpleTokenBucketRateLimiter(private val tokensPerSecond: Int) {
    private val mutex = Mutex()
    private var tokens = tokensPerSecond.toDouble()
    private var lastRefillTime = System.currentTimeMillis()

    private fun refillTokens(now: Long) {
        val elapsedSeconds = (now - lastRefillTime) / 1000.0
        if (elapsedSeconds <= 0) return
        val tokensToAdd = elapsedSeconds * tokensPerSecond
        tokens = (tokens + tokensToAdd).coerceAtMost(tokensPerSecond.toDouble())
        lastRefillTime = now
    }

    suspend fun acquireToken() {
        while (true) {
            val waitMillis = mutex.withLock {
                val now = System.currentTimeMillis()
                refillTokens(now)
                return@withLock if (tokens >= 1.0) {
                    tokens -= 1.0
                    0L
                } else {
                    val needed = 1.0 - tokens
                    ((needed / tokensPerSecond) * 1000).toLong().coerceAtLeast(10)
                }
            }
            if (waitMillis == 0L) return
            delay(waitMillis)
        }
    }
}
```

### Error Handling and Permit Cleanup

Critical: Always ensure permits are released even on exceptions or cancellation.

```kotlin
val semaphore = Semaphore(3)

// BAD: Manual acquire/release without finally
suspend fun badExample() {
    semaphore.acquire()
    performOperation() // Exception here leaks permit!
    semaphore.release()
}

// GOOD: withPermit handles cleanup
suspend fun goodExample() {
    semaphore.withPermit {
        performOperation()
    }
}

// BETTER MANUAL: try-finally if you cannot use withPermit
suspend fun manualAcquireCorrect() {
    semaphore.acquire()
    try {
        performOperation()
    } finally {
        semaphore.release()
    }
}
```

### (Simplified) Adaptive Concurrency Example

Dynamic resizing of a semaphore is non-trivial if there are in-flight operations. A simple and safe pattern is to limit changes to increasing permits using `release` when you decide to allow more concurrency, and to reduce concurrency by not issuing new permits (or by routing fewer requests through the limiter), rather than swapping semaphore instances. In practice, rebuilding the limiter during maintenance windows or via higher-level coordination is safer; unsafe approaches are intentionally omitted here.

```kotlin
class AdaptiveConcurrencyLimiter(initialPermits: Int) {
    private val semaphore = Semaphore(initialPermits)

    suspend fun <T> withPermit(block: suspend () -> T): T {
        return semaphore.withPermit { block() }
    }

    // For real dynamic resizing, prefer rebuilding the limiter during maintenance
    // or using higher-level coordination primitives.
}
```

### Testing Semaphore-Based Code

```kotlin
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.*
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
        } catch (_: RuntimeException) {
            // Expected
        }

        val acquired = semaphore.tryAcquire()
        assertTrue(acquired, "Permit should be available after exception")
        semaphore.release()
    }
}
```

### Common Pitfalls and Best Practices

#### Pitfalls

1. Manual acquire/release without finally -> leaks permits on exception
2. Using too few permits -> bottlenecks, underutilized resources
3. Using too many permits -> defeats concurrency limiting
4. Not handling cancellation -> prefer `withPermit` which is cancellation-safe
5. Using semaphores around blocking operations on limited dispatcher threads -> can exhaust threads
6. Creating a new Semaphore per operation -> should be shared
7. Ignoring potential starvation with unfair semaphores

#### Best Practices

1. Prefer `withPermit` instead of manual acquire/release
2. Size permits based on real resource limits
3. Monitor and adjust permits based on performance
4. Use separate semaphores for different resource types
5. Combine concurrency limits with time-based rate limiting when needed
6. Test concurrent access thoroughly
7. Log permit acquisition and wait times for debugging

### When to Use Semaphore

Use Semaphore when:
- Limiting concurrent API calls (max N requests at once)
- Managing resource pools (database connections, HTTP clients)
- Controlling parallel downloads/uploads
- Enforcing concurrency-level limits where N > 1

Avoid Semaphore when:
- You need strict mutual exclusion for a single critical section -> use `Mutex`
- You only need atomic counters -> use atomic primitives
- You need purely time-based rate limiting -> use dedicated rate limiter algorithms (token bucket, leaky bucket, etc.)
- There is no resource contention

### Key Takeaways

1. Semaphore is suited for controlling concurrent access with N permits.
2. Ideal for concurrency-based limiting (API calls, downloads, pools).
3. Use `withPermit` to ensure proper cleanup on exceptions and cancellation.
4. Size permits according to resource capacity.
5. Combine with time-based limiters for full rate limiting.
6. Monitor, test concurrent behavior, and watch for starvation or leaks.

---

## Follow-ups

1. How would you implement a token bucket rate limiter that combines time-based limits with Semaphore-based concurrency control?
2. What's the difference between fair and unfair semaphores in terms of performance and starvation risk?
3. How do you detect and handle semaphore permit leaks in long-running applications?
4. Can you explain when it is appropriate to adjust concurrency dynamically and how to do it safely?
5. How does Semaphore interact with coroutine cancellation and structured concurrency?
6. When would you use Semaphore vs `Flow`.flatMapMerge with a concurrency limit?
7. How do you test that semaphore limits are correctly enforced?

## Дополнительные Вопросы (RU)

1. Как реализовать token bucket-лимитер, комбинирующий ограничение по времени с ограничением конкурентности на основе Semaphore?
2. В чем разница между честными и нечестными семафорами с точки зрения производительности и риска голодания?
3. Как обнаруживать и обрабатывать утечки разрешений семафора в долгоживущих сервисах?
4. Когда имеет смысл динамически менять уровень конкурентности и как делать это безопасно?
5. Как Semaphore взаимодействует с отменой корутин и структурированной конкурентностью?
6. Когда вы выберете Semaphore против `Flow`.flatMapMerge с ограничением конкурентности?
7. Как протестировать, что ограничения семафора реально соблюдаются?

## References

- [Kotlinx.coroutines Semaphore Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-semaphore/)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Rate Limiting Patterns](https://stripe.com/blog/rate-limiters)
- [Resource Pooling Best Practices](https://www.baeldung.com/kotlin/resource-pooling)
- [[c-kotlin]]

## Ссылки (RU)

- [Документация Kotlinx.coroutines Semaphore](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-semaphore/)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Rate Limiting Patterns](https://stripe.com/blog/rate-limiters)
- [Resource Pooling Best Practices](https://www.baeldung.com/kotlin/resource-pooling)
- [[c-kotlin]]

## Related Questions

- [[q-mutex-synchronized-coroutines--kotlin--medium|Mutex vs synchronized in Kotlin coroutines]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|channelFlow vs callbackFlow vs flow]]
- [[q-race-conditions-coroutines--kotlin--hard|Race conditions in Kotlin coroutines]]

## Связанные Вопросы (RU)

- [[q-mutex-synchronized-coroutines--kotlin--medium|Mutex против synchronized в корутинах Kotlin]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|channelFlow против callbackFlow против flow]]
- [[q-race-conditions-coroutines--kotlin--hard|Гонки данных в корутинах Kotlin]]

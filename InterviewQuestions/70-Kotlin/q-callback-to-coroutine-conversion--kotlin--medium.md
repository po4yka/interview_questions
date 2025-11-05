---
id: kotlin-049
title: "How to convert callback-based APIs to coroutines? / Как конвертировать callback-based API в корутины?"
aliases: ["How to convert callback-based APIs to coroutines?, Как конвертировать callback-based API в корутины?"]

# Classification
topic: kotlin
subtopics: [async, callbacks, coroutines]
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
related: [callback-hell, continuation, coroutines, suspend-functions]

# Timestamps
created: 2025-10-06
updated: 2025-10-31

tags: [async, callbacks, coroutines, difficulty/medium, kotlin, migration, suspendcoroutine]
date created: Saturday, November 1st 2025, 9:25:30 am
date modified: Saturday, November 1st 2025, 5:43:28 pm
---
# Вопрос (RU)
> Как конвертировать callback-based API в корутины в Kotlin?

---

# Question (EN)
> How do you convert callback-based APIs to coroutines in Kotlin?
## Ответ (RU)

Конвертация callback-based API в корутины - распространенная задача при работе с легаси кодом или сторонними библиотеками. Kotlin предоставляет несколько механизмов для связи между callbacks и suspend-функциями.

### 1. Использование `suspendCoroutine`

Базовый подход - использование `suspendCoroutine` для оборачивания callback-based API:

```kotlin
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.coroutines.suspendCoroutine

// Легаси API с колбэками
interface UserCallback {
    fun onSuccess(user: User)
    fun onError(error: Exception)
}

class UserApi {
    fun fetchUser(userId: String, callback: UserCallback) {
        Thread {
            Thread.sleep(1000)
            if (userId.isNotEmpty()) {
                callback.onSuccess(User(userId, "John Doe"))
            } else {
                callback.onError(IllegalArgumentException("Invalid user ID"))
            }
        }.start()
    }
}

// Обертка для корутин
suspend fun fetchUserSuspend(userId: String): User = suspendCoroutine { continuation ->
    val api = UserApi()
    api.fetchUser(userId, object : UserCallback {
        override fun onSuccess(user: User) {
            continuation.resume(user)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
}

// Использование
suspend fun example() {
    try {
        val user = fetchUserSuspend("123")
        println("User: ${user.name}")
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
```

### 2. Использование `suspendCancellableCoroutine` (Рекомендуется)

Для production кода используйте `suspendCancellableCoroutine` с поддержкой отмены:

```kotlin
import kotlinx.coroutines.suspendCancellableCoroutine

suspend fun downloadFileSuspend(
    url: String,
    onProgress: (Int) -> Unit = {}
): File = suspendCancellableCoroutine { continuation ->
    val manager = DownloadManager()

    val token = manager.downloadFile(url, object : DownloadListener {
        override fun onProgress(progress: Int) {
            onProgress(progress)
        }

        override fun onComplete(file: File) {
            continuation.resume(file) {
                println("Загрузка завершена, но корутина отменена")
            }
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })

    // Обработка отмены корутины
    continuation.invokeOnCancellation {
        token.cancel()
        println("Загрузка отменена")
    }
}
```

### 3. Преобразование Простых Колбэков

```kotlin
suspend fun calculate(a: Int, b: Int): Int = suspendCoroutine { continuation ->
    calculateAsync(a, b) { result ->
        continuation.resume(result)
    }
}
```

### 4. Использование Flow Для Потоковых Данных

```kotlin
fun uploadFileFlow(file: File): Flow<UploadResult> = callbackFlow {
    val uploader = FileUploader()

    uploader.upload(file, object : UploadCallback {
        override fun onProgress(percent: Int) {
            trySend(UploadResult.Progress(percent))
        }

        override fun onSuccess(url: String) {
            trySend(UploadResult.Success(url))
            close()
        }

        override fun onError(error: Exception) {
            close(error)
        }
    })

    awaitClose {
        uploader.cancel()
    }
}
```

### Лучшие Практики

#### - ДЕЛАЙТЕ:

- Используйте `suspendCancellableCoroutine` для отменяемых операций
- Обрабатывайте edge cases (множественные вызовы resume)
- Используйте Flow для потоковых данных
- Всегда реализуйте `awaitClose` в `callbackFlow`

#### - НЕ ДЕЛАЙТЕ:

- Не используйте `suspendCoroutine` для отменяемых операций
- Не вызывайте resume несколько раз
- Не игнорируйте очистку ресурсов
- Не забывайте про обработку отмены

### Таблица Паттернов

| Паттерн колбэка | Решение с корутинами | Случай использования |
|-----------------|---------------------|---------------------|
| Простой success/error | `suspendCoroutine` | Простые async операции |
| Отменяемая операция | `suspendCancellableCoroutine` | Сетевые запросы, загрузки |
| Множественные значения | `callbackFlow` | Потоковые данные, слушатели |
| Одиночное значение | `flow { emit() }` | Преобразование колбэков |

### Производительность

- **Накладные расходы**: Минимальные
- **Память**: Меньше чем у колбэков
- **Отмена**: Предотвращает утечки ресурсов
- **Потоки**: Корутины не создают новые потоки

---

## Answer (EN)

Converting callback-based APIs to coroutines is a common task when working with legacy code or third-party libraries. Kotlin provides several mechanisms to bridge the gap between callbacks and suspending functions.

### 1. Using `suspendCoroutine`

The most basic approach is using `suspendCoroutine` to wrap a callback-based API:

```kotlin
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlin.coroutines.suspendCoroutine

// Legacy callback-based API
interface UserCallback {
    fun onSuccess(user: User)
    fun onError(error: Exception)
}

class UserApi {
    fun fetchUser(userId: String, callback: UserCallback) {
        // Simulated async operation
        Thread {
            Thread.sleep(1000)
            if (userId.isNotEmpty()) {
                callback.onSuccess(User(userId, "John Doe"))
            } else {
                callback.onError(IllegalArgumentException("Invalid user ID"))
            }
        }.start()
    }
}

// Coroutine wrapper
suspend fun fetchUserSuspend(userId: String): User = suspendCoroutine { continuation ->
    val api = UserApi()
    api.fetchUser(userId, object : UserCallback {
        override fun onSuccess(user: User) {
            continuation.resume(user)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
}

// Usage
suspend fun example() {
    try {
        val user = fetchUserSuspend("123")
        println("User: ${user.name}")
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
```

### 2. Using `suspendCancellableCoroutine` (Recommended)

For production code, use `suspendCancellableCoroutine` to support cancellation:

```kotlin
import kotlin.coroutines.cancellation.CancellationException
import kotlinx.coroutines.suspendCancellableCoroutine

// Download API with cancellation support
interface DownloadListener {
    fun onProgress(progress: Int)
    fun onComplete(file: File)
    fun onError(error: Exception)
}

class DownloadManager {
    fun downloadFile(url: String, listener: DownloadListener): DownloadToken {
        // Returns a token that can be used to cancel the download
        val token = DownloadToken()

        Thread {
            try {
                for (i in 0..100 step 10) {
                    if (token.isCancelled) break
                    Thread.sleep(100)
                    listener.onProgress(i)
                }
                if (!token.isCancelled) {
                    listener.onComplete(File("/path/to/file"))
                }
            } catch (e: Exception) {
                listener.onError(e)
            }
        }.start()

        return token
    }
}

data class DownloadToken(var isCancelled: Boolean = false) {
    fun cancel() {
        isCancelled = true
    }
}

// Coroutine wrapper with cancellation
suspend fun downloadFileSuspend(
    url: String,
    onProgress: (Int) -> Unit = {}
): File = suspendCancellableCoroutine { continuation ->
    val manager = DownloadManager()

    val token = manager.downloadFile(url, object : DownloadListener {
        override fun onProgress(progress: Int) {
            onProgress(progress)
        }

        override fun onComplete(file: File) {
            continuation.resume(file) {
                // Cleanup on cancellation
                println("Download completed but coroutine cancelled")
            }
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })

    // Handle coroutine cancellation
    continuation.invokeOnCancellation {
        token.cancel()
        println("Download cancelled")
    }
}

// Usage
suspend fun downloadExample() {
    try {
        val file = downloadFileSuspend("https://example.com/file.zip") { progress ->
            println("Progress: $progress%")
        }
        println("Downloaded: ${file.path}")
    } catch (e: CancellationException) {
        println("Download cancelled")
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
```

### 3. Converting Single-Value Callbacks

For simple callbacks that return a single value:

```kotlin
// Callback-based API
fun calculateAsync(a: Int, b: Int, callback: (Int) -> Unit) {
    Thread {
        Thread.sleep(500)
        callback(a + b)
    }.start()
}

// Suspend function
suspend fun calculate(a: Int, b: Int): Int = suspendCoroutine { continuation ->
    calculateAsync(a, b) { result ->
        continuation.resume(result)
    }
}

// Usage
suspend fun example() {
    val result = calculate(5, 10)
    println("Result: $result") // 15
}
```

### 4. Converting Multiple-Callback Patterns

For APIs with multiple callbacks (success, error, progress):

```kotlin
sealed class UploadResult {
    data class Progress(val percent: Int) : UploadResult()
    data class Success(val url: String) : UploadResult()
    data class Error(val exception: Exception) : UploadResult()
}

// Using Flow for multiple emissions
fun uploadFileFlow(file: File): Flow<UploadResult> = callbackFlow {
    val uploader = FileUploader()

    uploader.upload(file, object : UploadCallback {
        override fun onProgress(percent: Int) {
            trySend(UploadResult.Progress(percent))
        }

        override fun onSuccess(url: String) {
            trySend(UploadResult.Success(url))
            close()
        }

        override fun onError(error: Exception) {
            close(error)
        }
    })

    awaitClose {
        uploader.cancel()
    }
}

// Usage
suspend fun uploadExample() {
    uploadFileFlow(File("/path/to/file")).collect { result ->
        when (result) {
            is UploadResult.Progress -> println("Progress: ${result.percent}%")
            is UploadResult.Success -> println("Uploaded: ${result.url}")
            is UploadResult.Error -> println("Error: ${result.exception}")
        }
    }
}
```

### 5. Android-Specific Examples

#### Converting LiveData to Flow

```kotlin
fun <T> LiveData<T>.asFlow(): Flow<T> = callbackFlow {
    val observer = Observer<T> { value ->
        trySend(value)
    }
    observeForever(observer)
    awaitClose {
        removeObserver(observer)
    }
}
```

#### Converting LocationCallback to Coroutines

```kotlin
import android.location.Location
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationResult

suspend fun FusedLocationProviderClient.awaitLastLocation(): Location? =
    suspendCancellableCoroutine { continuation ->
        lastLocation
            .addOnSuccessListener { location ->
                continuation.resume(location)
            }
            .addOnFailureListener { exception ->
                continuation.resumeWithException(exception)
            }

        continuation.invokeOnCancellation {
            // Cancel location request if needed
        }
    }

fun FusedLocationProviderClient.locationFlow(
    locationRequest: com.google.android.gms.location.LocationRequest
): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            result.locations.forEach { location ->
                trySend(location)
            }
        }
    }

    requestLocationUpdates(locationRequest, callback, Looper.getMainLooper())
        .addOnFailureListener { e ->
            close(e)
        }

    awaitClose {
        removeLocationUpdates(callback)
    }
}
```

### 6. Best Practices

#### - DO:

```kotlin
// 1. Use suspendCancellableCoroutine for better cancellation support
suspend fun apiCall(): Result = suspendCancellableCoroutine { continuation ->
    val handle = api.request(callback)
    continuation.invokeOnCancellation {
        handle.cancel()
    }
}

// 2. Handle edge cases
suspend fun safeFetch(): User? = suspendCancellableCoroutine { continuation ->
    api.fetch(object : Callback {
        var resumed = false

        override fun onSuccess(user: User) {
            if (!resumed) {
                resumed = true
                continuation.resume(user)
            }
        }

        override fun onError(e: Exception) {
            if (!resumed) {
                resumed = true
                continuation.resumeWithException(e)
            }
        }
    })
}

// 3. Use Flow for streaming data
fun streamData(): Flow<Data> = callbackFlow {
    val listener = object : DataListener {
        override fun onData(data: Data) {
            trySend(data)
        }
    }
    api.addListener(listener)
    awaitClose { api.removeListener(listener) }
}
```

#### - DON'T:

```kotlin
// Don't use suspendCoroutine for cancellable operations
suspend fun badDownload(): File = suspendCoroutine { continuation ->
    // No way to cancel this!
    api.download(callback)
}

// Don't resume multiple times
suspend fun badFetch(): User = suspendCoroutine { continuation ->
    api.fetch(object : Callback {
        override fun onSuccess(user: User) {
            continuation.resume(user)
            continuation.resume(user) // CRASH!
        }
    })
}

// Don't ignore cleanup
suspend fun badStream() = callbackFlow<Data> {
    api.addListener { data -> trySend(data) }
    // Missing awaitClose - listener never removed!
}
```

### 7. Common Patterns Summary

| Callback Pattern | Coroutine Solution | Use Case |
|------------------|-------------------|----------|
| Single success/error callback | `suspendCoroutine` | Simple async operations |
| Cancellable operation | `suspendCancellableCoroutine` | Network requests, downloads |
| Multiple values over time | `callbackFlow` | Streaming data, listeners |
| Single value stream | `flow { emit() }` | Transforming single callbacks |
| Android Task/Result | Extension functions | Firebase, Google Play Services |

### 8. Performance Considerations

- **Overhead**: Minimal - suspend functions are lightweight
- **Memory**: Less than callbacks (no callback object retention)
- **Cancellation**: Properly implemented cancellation prevents resource leaks
- **Threading**: Coroutines don't create new threads, callbacks often do

### 9. Testing

```kotlin
@Test
fun testCallbackConversion() = runTest {
    val result = fetchUserSuspend("123")
    assertEquals("John Doe", result.name)
}

@Test
fun testCancellation() = runTest {
    val job = launch {
        downloadFileSuspend("url")
    }

    delay(100)
    job.cancel()

    // Verify download was cancelled
}
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)
- [suspendCoroutine API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.coroutines/suspend-coroutine.html)
- [callbackFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html)
## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines

### Related (Medium)
- [[q-coroutine-context-explained--kotlin--medium]] - Coroutines
- [[q-coroutine-builders-comparison--kotlin--medium]] - Coroutines
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Coroutines
- [[q-deferred-async-patterns--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-flow-testing-advanced--kotlin--hard]] - Flow

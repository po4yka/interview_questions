---
'---id': kotlin-049
title: How to convert callback-based APIs to coroutines? / Как конвертировать callback-based
  API в корутины?
anki_cards:
- slug: q-callback-to-coroutine-conversion-0-en
  language: en
- slug: q-callback-to-coroutine-conversion-0-ru
  language: ru
aliases:
- How to convert callback-based APIs to coroutines?
- Как конвертировать callback-based API в корутины?
topic: kotlin
subtopics:
- coroutines
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository
status: draft
moc: moc-kotlin
related:
- c-coroutines
- c-kotlin
- c-stateflow
- q-what-is-coroutine--kotlin--easy
created: 2025-10-06
updated: 2025-11-11
tags:
- async
- callbacks
- coroutines
- difficulty/medium
- kotlin
- migration
- suspendcoroutine
---
# Вопрос (RU)
> Как конвертировать callback-based API в корутины в Kotlin?

---

# Question (EN)
> How do you convert callback-based APIs to coroutines in Kotlin?

---

## Ответ (RU)

Конвертация callback-based API в корутины — распространенная задача при работе с легаси-кодом или сторонними библиотеками. Kotlin предоставляет несколько механизмов для связи между callbacks и suspend-функциями.

### 1. Использование `suspendCoroutine`

Базовый подход — использование `suspendCoroutine` для оборачивания callback-based API с одним результатом:

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
        // Имитация асинхронной операции
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

Важно: `suspendCoroutine` не поддерживает отмену. Используйте его только для неотменяемых одноразовых операций.

### 2. Использование `suspendCancellableCoroutine` (рекомендуется)

Для production-кода и отменяемых операций используйте `suspendCancellableCoroutine` с поддержкой отмены и защитой от повторных вызовов:

```kotlin
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

// Пример API с поддержкой отмены
interface DownloadListener {
    fun onProgress(progress: Int)
    fun onComplete(file: File)
    fun onError(error: Exception)
}

class DownloadManager {
    fun downloadFile(url: String, listener: DownloadListener): DownloadToken {
        val token = DownloadToken()

        Thread {
            try {
                for (i in 0..100 step 10) {
                    if (token.isCancelled) return@Thread
                    Thread.sleep(100)
                    listener.onProgress(i)
                }
                if (!token.isCancelled) {
                    listener.onComplete(File("/path/to/file"))
                }
            } catch (e: Exception) {
                if (!token.isCancelled) {
                    listener.onError(e)
                }
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

// Обертка для корутин с отменой
suspend fun downloadFileSuspend(
    url: String,
    onProgress: (Int) -> Unit = {}
): File = suspendCancellableCoroutine { continuation ->
    val manager = DownloadManager()

    // Флаг для защиты от множественных resume
    var isCompleted = false

    val token = manager.downloadFile(url, object : DownloadListener {
        override fun onProgress(progress: Int) {
            onProgress(progress)
        }

        override fun onComplete(file: File) {
            if (!isCompleted && continuation.isActive) {
                isCompleted = true
                continuation.resume(file)
            }
        }

        override fun onError(error: Exception) {
            if (!isCompleted && continuation.isActive) {
                isCompleted = true
                continuation.resumeWithException(error)
            }
        }
    })

    // Обработка отмены корутины
    continuation.invokeOnCancellation {
        isCompleted = true
        token.cancel()
        println("Загрузка отменена")
    }
}

// Пример использования
suspend fun downloadExampleRu() {
    try {
        val file = downloadFileSuspend("https://example.com/file.zip") { progress ->
            println("Прогресс: $progress%")
        }
        println("Загружено: ${file.path}")
    } catch (e: Exception) {
        println("Ошибка или отмена: ${e.message}")
    }
}
```

### 3. Преобразование Простых Колбэков (одно значение)

```kotlin
// Callback-based API
fun calculateAsync(a: Int, b: Int, callback: (Int) -> Unit) {
    Thread {
        Thread.sleep(500)
        callback(a + b)
    }.start()
}

// Suspend-обертка
suspend fun calculate(a: Int, b: Int): Int = suspendCoroutine { continuation ->
    calculateAsync(a, b) { result ->
        continuation.resume(result)
    }
}
```

### 4. Использование `Flow` Для Потоковых Данных

Для множественных значений или слушателей удобно использовать `callbackFlow`:

```kotlin
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

sealed class UploadResult {
    data class Progress(val percent: Int) : UploadResult()
    data class Success(val url: String) : UploadResult()
    data class Error(val exception: Exception) : UploadResult()
}

fun uploadFileFlow(file: File): Flow<UploadResult> = callbackFlow {
    val uploader = FileUploader()

    val callback = object : UploadCallback {
        override fun onProgress(percent: Int) {
            // Игнорируем неуспешную отправку (например, когда канал закрыт)
            trySend(UploadResult.Progress(percent)).isSuccess
        }

        override fun onSuccess(url: String) {
            if (trySend(UploadResult.Success(url)).isSuccess) {
                close()
            } else {
                close()
            }
        }

        override fun onError(error: Exception) {
            // Закрываем с ошибкой
            close(error)
        }
    }

    uploader.upload(file, callback)

    awaitClose {
        uploader.cancel()
    }
}
```

### 5. Android-специфичные Примеры

#### Конвертация `LiveData` В `Flow`

```kotlin
import androidx.lifecycle.LiveData
import androidx.lifecycle.Observer
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

fun <T> LiveData<T>.asFlow(): Flow<T> = callbackFlow {
    val observer = Observer<T> { value ->
        // Если отправка не удалась (например, канал закрыт), игнорируем
        trySend(value).isSuccess
    }
    observeForever(observer)
    awaitClose {
        removeObserver(observer)
    }
}
```

#### Конвертация `LocationCallback` В корутины/`Flow`

```kotlin
import android.location.Location
import android.os.Looper
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

suspend fun FusedLocationProviderClient.awaitLastLocation(): Location? =
    suspendCancellableCoroutine { continuation ->
        lastLocation
            .addOnSuccessListener { location ->
                if (continuation.isActive) {
                    continuation.resume(location)
                }
            }
            .addOnFailureListener { exception ->
                if (continuation.isActive) {
                    continuation.resumeWithException(exception)
                }
            }
        // lastLocation — одноразовый Task; отменять тут обычно нечего.
    }

fun FusedLocationProviderClient.locationFlow(
    locationRequest: LocationRequest
): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            result.locations.forEach { location ->
                trySend(location).isSuccess
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

### 6. Лучшие Практики

#### - ДЕЛАЙТЕ:

```kotlin
// 1. Используйте suspendCancellableCoroutine для отменяемых операций
suspend fun apiCall(): Result = suspendCancellableCoroutine { continuation ->
    val handle = api.request(callback = { result, error ->
        if (continuation.isActive) {
            if (error != null) continuation.resumeWithException(error)
            else continuation.resume(result)
        }
    })

    continuation.invokeOnCancellation {
        handle.cancel()
    }
}

// 2. Обрабатывайте edge cases и множественные колбэки
suspend fun safeFetch(): User = suspendCancellableCoroutine { continuation ->
    var resumed = false

    api.fetch(object : Callback {
        override fun onSuccess(user: User) {
            if (!resumed && continuation.isActive) {
                resumed = true
                continuation.resume(user)
            }
        }

        override fun onError(e: Exception) {
            if (!resumed && continuation.isActive) {
                resumed = true
                continuation.resumeWithException(e)
            }
        }
    })
}

// 3. Используйте Flow для потоковых данных
fun streamData(): Flow<Data> = callbackFlow {
    val listener = object : DataListener {
        override fun onData(data: Data) {
            trySend(data).isSuccess
        }
    }
    api.addListener(listener)
    awaitClose { api.removeListener(listener) }
}
```

#### - НЕ ДЕЛАЙТЕ:

```kotlin
// Не используйте suspendCoroutine для отменяемых операций
suspend fun badDownload(): File = suspendCoroutine { continuation ->
    // Нет способа отменить с корутинной стороны
    api.download(callback = { file -> continuation.resume(file) })
}

// Не вызывайте resume несколько раз
suspend fun badFetch(): User = suspendCoroutine { continuation ->
    api.fetch(object : Callback {
        override fun onSuccess(user: User) {
            continuation.resume(user)
            continuation.resume(user) // ERROR: IllegalStateException во время выполнения
        }
    })
}

// Не игнорируйте очистку ресурсов в callbackFlow
fun badStream(): Flow<Data> = callbackFlow {
    api.addListener { data -> trySend(data).isSuccess }
    // Нет awaitClose — listener никогда не удаляется -> утечка
}
```

### 7. Таблица Паттернов

| Паттерн колбэка             | Решение с корутинами             | Случай использования                          |
|-----------------------------|----------------------------------|-----------------------------------------------|
| Простой success/error       | `suspendCoroutine`               | Простые async-операции                        |
| Отменяемая операция         | `suspendCancellableCoroutine`    | Сетевые запросы, загрузки                     |
| Множественные значения      | `callbackFlow`                   | Потоковые данные, слушатели                   |
| Одиночное значение-поток    | `flow { emit() }`                | Обернуть единичный callback в `Flow`          |
| Android Task/Result style   | Extension-функции                | Firebase, Google Play Services и подобные API |

### 8. Производительность

- Накладные расходы на корутины минимальны по сравнению с созданием потоков ОС.
- Корутины не всегда используют меньше памяти, чем любая реализация на колбэках, но помогают избежать удержания лишних объектов колбэков и упростить управление жизненным циклом.
- Корректная интеграция отмены помогает предотвращать утечки ресурсов.
- Корутины выполняются на диспетчерах и не создают новые потоки автоматически, если это явно не настроено.

### 9. Тестирование

```kotlin
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

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

    // Проверяем по логам или через mock, что внутренняя загрузка была отменена.
}
```

---

## Answer (EN)

Converting callback-based APIs to coroutines is a common task when working with legacy code or third-party libraries. Kotlin provides several mechanisms to bridge callbacks and suspending functions.

### 1. Using `suspendCoroutine`

Use `suspendCoroutine` to wrap a callback-based API that produces a single result and is not cancellable:

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

Important: `suspendCoroutine` itself does not support cancellation. Prefer it for simple, non-cancellable, single-shot callbacks.

### 2. Using `suspendCancellableCoroutine` (Recommended)

For production code and cancellable operations, use `suspendCancellableCoroutine` with proper cancellation and multiple-callback safety:

```kotlin
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

// Download API with cancellation support
interface DownloadListener {
    fun onProgress(progress: Int)
    fun onComplete(file: File)
    fun onError(error: Exception)
}

class DownloadManager {
    fun downloadFile(url: String, listener: DownloadListener): DownloadToken {
        val token = DownloadToken()

        Thread {
            try {
                for (i in 0..100 step 10) {
                    if (token.isCancelled) return@Thread
                    Thread.sleep(100)
                    listener.onProgress(i)
                }
                if (!token.isCancelled) {
                    listener.onComplete(File("/path/to/file"))
                }
            } catch (e: Exception) {
                if (!token.isCancelled) {
                    listener.onError(e)
                }
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

    var isCompleted = false

    val token = manager.downloadFile(url, object : DownloadListener {
        override fun onProgress(progress: Int) {
            onProgress(progress)
        }

        override fun onComplete(file: File) {
            if (!isCompleted && continuation.isActive) {
                isCompleted = true
                continuation.resume(file)
            }
        }

        override fun onError(error: Exception) {
            if (!isCompleted && continuation.isActive) {
                isCompleted = true
                continuation.resumeWithException(error)
            }
        }
    })

    // Handle coroutine cancellation
    continuation.invokeOnCancellation {
        isCompleted = true
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
    } catch (e: Exception) {
        println("Error or cancellation: ${e.message}")
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
suspend fun exampleCalculate() {
    val result = calculate(5, 10)
    println("Result: $result") // 15
}
```

### 4. Converting Multiple-Callback Patterns with `Flow`

For APIs with multiple callbacks (success, error, progress), `Flow` via `callbackFlow` is appropriate:

```kotlin
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

sealed class UploadResult {
    data class Progress(val percent: Int) : UploadResult()
    data class Success(val url: String) : UploadResult()
    data class Error(val exception: Exception) : UploadResult()
}

fun uploadFileFlow(file: File): Flow<UploadResult> = callbackFlow {
    val uploader = FileUploader()

    val callback = object : UploadCallback {
        override fun onProgress(percent: Int) {
            // Drop if failed (e.g., channel closed)
            trySend(UploadResult.Progress(percent)).isSuccess
        }

        override fun onSuccess(url: String) {
            // Try to emit success, then close regardless
            trySend(UploadResult.Success(url)).isSuccess
            close()
        }

        override fun onError(error: Exception) {
            close(error)
        }
    }

    uploader.upload(file, callback)

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

#### Converting `LiveData` to `Flow`

```kotlin
import androidx.lifecycle.LiveData
import androidx.lifecycle.Observer
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

fun <T> LiveData<T>.asFlow(): Flow<T> = callbackFlow {
    val observer = Observer<T> { value ->
        // If send fails (e.g., channel closed), we ignore
        trySend(value).isSuccess
    }
    observeForever(observer)
    awaitClose {
        removeObserver(observer)
    }
}
```

#### Converting `LocationCallback` to Coroutines/`Flow`

```kotlin
import android.location.Location
import android.os.Looper
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

suspend fun FusedLocationProviderClient.awaitLastLocation(): Location? =
    suspendCancellableCoroutine { continuation ->
        lastLocation
            .addOnSuccessListener { location ->
                if (continuation.isActive) {
                    continuation.resume(location)
                }
            }
            .addOnFailureListener { exception ->
                if (continuation.isActive) {
                    continuation.resumeWithException(exception)
                }
            }
        // lastLocation is a one-shot Task; there's nothing meaningful to cancel here.
    }

fun FusedLocationProviderClient.locationFlow(
    locationRequest: LocationRequest
): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            result.locations.forEach { location ->
                trySend(location).isSuccess
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
// 1. Use suspendCancellableCoroutine for cancellable operations
suspend fun apiCall(): Result = suspendCancellableCoroutine { continuation ->
    val handle = api.request(callback = { result, error ->
        if (continuation.isActive) {
            if (error != null) continuation.resumeWithException(error)
            else continuation.resume(result)
        }
    })

    continuation.invokeOnCancellation {
        handle.cancel()
    }
}

// 2. Handle edge cases and multiple callbacks
suspend fun safeFetch(): User = suspendCancellableCoroutine { continuation ->
    var resumed = false

    api.fetch(object : Callback {
        override fun onSuccess(user: User) {
            if (!resumed && continuation.isActive) {
                resumed = true
                continuation.resume(user)
            }
        }

        override fun onError(e: Exception) {
            if (!resumed && continuation.isActive) {
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
            trySend(data).isSuccess
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
    // No way to cancel this from coroutine side
    api.download(callback = { file -> continuation.resume(file) })
}

// Don't resume multiple times
suspend fun badFetch(): User = suspendCoroutine { continuation ->
    api.fetch(object : Callback {
        override fun onSuccess(user: User) {
            continuation.resume(user)
            continuation.resume(user) // ERROR: IllegalStateException at runtime
        }
    })
}

// Don't ignore cleanup in callbackFlow
fun badStream(): Flow<Data> = callbackFlow {
    api.addListener { data -> trySend(data).isSuccess }
    // Missing awaitClose - listener is never removed -> leak
}
```

### 7. Common Patterns Summary

| `Callback` Pattern            | `Coroutine` Solution              | Use Case                            |
|----------------------------|---------------------------------|-------------------------------------|
| Single success/error       | `suspendCoroutine`              | Simple async operations             |
| Cancellable operation      | `suspendCancellableCoroutine`   | Network requests, downloads         |
| Multiple values over time  | `callbackFlow`                  | Streaming data, listeners           |
| Single value stream        | `flow { emit() }`               | Wrap single callback into a `Flow`  |
| Android Task/Result style  | Extension functions             | Firebase, Google Play Services      |

### 8. Performance Considerations

- Overhead of suspending functions and coroutines is low compared to creating OS threads.
- `Coroutines` do not inherently use less memory than every callback-based design, but they help avoid retaining unnecessary callback objects and simplify lifecycles.
- Proper cancellation integration helps prevent resource leaks.
- `Coroutines` run on dispatchers; they do not automatically create new threads unless configured to.

### 9. Testing

```kotlin
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals

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

    // Verify via logs or mock that underlying download was cancelled.
}
```

---

## Follow-ups

- What are the key differences between this and Java-style callbacks or Futures?
- When would you use this in practice (e.g., wrapping SDKs, legacy code, platform APIs)?
- What are common pitfalls to avoid when bridging callbacks and coroutines?

## References
- [Kotlin `Coroutines` Documentation](https://kotlinlang.org/docs/coroutines-overview.html)
- [suspendCoroutine API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.coroutines/suspend-coroutine.html)
- [callbackFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - `Coroutines`

### Related (Medium)
- [[q-coroutine-context-explained--kotlin--medium]] - `Coroutines`
- [[q-coroutine-builders-comparison--kotlin--medium]] - `Coroutines`
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - `Coroutines`
- [[q-deferred-async-patterns--kotlin--medium]] - `Coroutines`

### Advanced (Harder)
- [[q-flow-testing-advanced--kotlin--hard]] - `Flow`

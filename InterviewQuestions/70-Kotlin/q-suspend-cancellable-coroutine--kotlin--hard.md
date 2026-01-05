---
id: kotlin-095
title: "Converting callbacks with suspendCancellableCoroutine / Преобразование callback с suspendCancellableCoroutine"
topic: kotlin
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
tags: [callbacks, cancellation, coroutines, difficulty/hard, integration, kotlin, suspend]
aliases: ["Converting callbacks with suspendCancellableCoroutine", "Преобразование callback с suspendCancellableCoroutine"]
moc: moc-kotlin
related: [c-coroutines, q-channelflow-callbackflow-flow--kotlin--medium, q-continuation-cps-internals--kotlin--hard, q-coroutine-exception-handler--kotlin--medium]
subtopics: [callbacks, cancellation, coroutines]
question_kind: coding
---
# Вопрос (RU)
> Как преобразовать API на основе callback в suspend функции используя `suspendCancellableCoroutine`? Как обрабатывать отмену, ошибки и состояния гонки?

---

# Question (EN)
> How do you convert callback-based APIs to suspend functions using `suspendCancellableCoroutine`? How do you handle cancellation, errors, and race conditions?

## Ответ (RU)

Многие Android и Java библиотеки используют callback-ориентированные API (Retrofit callbacks, Firebase listeners, Location updates, OkHttp calls). Чтобы идиоматично использовать их с корутинами, нужно преобразовать callback в `suspend`-функции с помощью `suspendCancellableCoroutine`. Это критический навык для интеграции легаси-кода с корутинами с корректной обработкой отмены, ошибок и гонок. См. также [[c-coroutines]].

### `suspendCoroutine` Против `suspendCancellableCoroutine`

`suspendCoroutine` — базовая приостановка без встроенной поддержки структурированной отмены для внешней операции.

```kotlin
suspend fun basicSuspend() = suspendCoroutine<String> { cont ->
    // Нельзя структурированно отреагировать на отмену корутины для внешнего API,
    // если оно само не предоставляет средств отмены.
    someAsyncOperation { result ->
        cont.resume(result)
    }
}
```

`suspendCancellableCoroutine` — учитывает отмену и должен использоваться в production-коде.

```kotlin
suspend fun cancellableSuspend() = suspendCancellableCoroutine<String> { cont ->
    val operation = someAsyncOperation { result ->
        cont.resume(result)
    }

    // Очистка при отмене корутины: отменяем внешнюю операцию, если возможно
    cont.invokeOnCancellation {
        operation.cancel()
    }
}
```

Правило: для интеграции с внешними асинхронными API почти всегда предпочтительнее `suspendCancellableCoroutine`.

### Базовый Шаблон: Одиночный Callback

```kotlin
// Callback-ориентированный API
interface DataCallback {
    fun onSuccess(data: String)
    fun onError(error: Exception)
}

fun fetchDataAsync(callback: DataCallback) {
    kotlin.concurrent.thread {
        Thread.sleep(1000)
        callback.onSuccess("Data")
    }
}

// Преобразование в suspend-функцию
suspend fun fetchData(): String = suspendCancellableCoroutine { cont ->
    fetchDataAsync(object : DataCallback {
        override fun onSuccess(data: String) {
            if (cont.isActive) {
                cont.resume(data)
            }
        }

        override fun onError(error: Exception) {
            if (cont.isActive) {
                cont.resumeWithException(error)
            }
        }
    })

    // Если fetchDataAsync поддерживал бы отмену, её вызвали бы из invokeOnCancellation
}
```

### `invokeOnCancellation` Для Очистки Ресурсов

Критично освобождать ресурсы, если корутина отменена и нижележащий API поддерживает отмену:

```kotlin
suspend fun fetchWithCancellation(): String = suspendCancellableCoroutine { cont ->
    val request = api.createRequest()

    request.enqueue(object : DataCallback {
        override fun onSuccess(data: String) {
            if (cont.isActive) {
                cont.resume(data)
            }
        }

        override fun onError(error: Exception) {
            if (cont.isActive) {
                cont.resumeWithException(error)
            }
        }
    })

    // Очистка при отмене
    cont.invokeOnCancellation {
        request.cancel()
    }
}
```

Здесь `DataCallback` — условный интерфейс API. Для конкретных библиотек используйте их реальные типы callback.

### Реальный Пример: Преобразование OkHttp `Call`

```kotlin
import okhttp3.Call
import okhttp3.Callback
import okhttp3.Response
import java.io.IOException
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

// Преобразование OkHttp Call в suspend-функцию
suspend fun Call.await(): Response = suspendCancellableCoroutine { cont ->
    // Обработка отмены
    cont.invokeOnCancellation {
        cancel()
    }

    // Асинхронный вызов
    enqueue(object : Callback {
        override fun onResponse(call: Call, response: Response) {
            if (cont.isActive) {
                cont.resume(response)
            } else {
                // Корутина уже отменена/завершена — освобождаем ресурсы
                response.close()
            }
        }

        override fun onFailure(call: Call, e: IOException) {
            if (cont.isActive) {
                cont.resumeWithException(e)
            }
            // Если не активен — корутина уже завершилась, ничего не делаем
        }
    })
}
```

### Обработка Гонок: «возобновить Ровно Один раз»

Продолжение должно быть возобновлено ровно один раз. Проверка `cont.isActive` полезна, но не делает `resume` идемпотентным при гонках. При возможных гонках между callback и отменой защищайтесь атомарным флагом:

```kotlin
import java.util.concurrent.atomic.AtomicBoolean

suspend fun safeOperation(): String = suspendCancellableCoroutine { cont ->
    val resumed = AtomicBoolean(false)

    val operation = startAsyncOp { result ->
        if (resumed.compareAndSet(false, true)) {
            cont.resume(result)
        }
    }

    cont.invokeOnCancellation {
        // Отменяем внешнюю операцию только если ещё не возобновили продолжение
        if (resumed.compareAndSet(false, true)) {
            operation.cancel()
        }
    }
}
```

Для API с гарантированным одиночным вызовом callback без гонок часто достаточно `if (cont.isActive)`.

### Пример: Firebase Realtime Database

```kotlin
import com.google.firebase.database.*
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

suspend fun DatabaseReference.awaitValue(): DataSnapshot =
    suspendCancellableCoroutine { cont ->
        val listener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                if (cont.isActive) {
                    cont.resume(snapshot)
                }
            }

            override fun onCancelled(error: DatabaseError) {
                if (cont.isActive) {
                    cont.resumeWithException(error.toException())
                }
            }
        }

        addListenerForSingleValueEvent(listener)

        cont.invokeOnCancellation {
            removeEventListener(listener)
        }
    }
```

Важно: callbacks должны проверять `cont.isActive` и не вызывать `resume` / `resumeWithException`, если корутина уже отменена.

### Пример: Android Location

```kotlin
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

suspend fun LocationManager.awaitLocation(provider: String): Location =
    suspendCancellableCoroutine { cont ->
        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                if (cont.isActive) {
                    cont.resume(location)
                    removeUpdates(this)
                }
            }

            @Deprecated("Deprecated in Android Q")
            override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}

            override fun onProviderEnabled(provider: String) {}

            override fun onProviderDisabled(provider: String) {
                if (cont.isActive) {
                    cont.resumeWithException(
                        IllegalStateException("Provider $provider disabled")
                    )
                }
            }
        }

        try {
            requestLocationUpdates(provider, 0L, 0f, listener)
        } catch (e: SecurityException) {
            cont.resumeWithException(e)
            return@suspendCancellableCoroutine
        }

        cont.invokeOnCancellation {
            removeUpdates(listener)
        }
    }
```

### Шаблоны Обработки Ошибок

```kotlin
suspend fun fetchDataWithErrors(): String = suspendCancellableCoroutine { cont ->
    api.getData(object : ApiCallback {
        override fun onSuccess(data: String) {
            if (cont.isActive) cont.resume(data)
        }

        override fun onError(code: Int, message: String) {
            val exception = when (code) {
                404 -> NotFoundException(message)
                401 -> UnauthorizedException(message)
                else -> ApiException(code, message)
            }
            if (cont.isActive) cont.resumeWithException(exception)
        }
    })
}
```

```kotlin
suspend fun fetchDataSafe(): Result<String> = suspendCancellableCoroutine { cont ->
    api.getData(object : ApiCallback {
        override fun onSuccess(data: String) {
            cont.resume(Result.success(data))
        }

        override fun onError(code: Int, message: String) {
            cont.resume(Result.failure(ApiException(code, message)))
        }
    })
}
```

- Используйте `resumeWithException` для проброса доменных исключений.
- Либо возвращайте `Result` (`Result.success` / `Result.failure`), если хотите избежать исключений у вызывающего кода.

### Потокобезопасность

```kotlin
suspend fun threadSafeOperation(): String = suspendCancellableCoroutine { cont ->
    someLegacyApi.asyncCall(object : ApiCallbackSingleResult {
        override fun onComplete(result: String) {
            // CancellableContinuation потокобезопасен — можно вызывать с любого потока,
            // но вы должны гарантировать отсутствие двойного resume.
            cont.resume(result)
        }
    })
}
```

`CancellableContinuation` потокобезопасен: `resume` / `resumeWithException` можно вызывать с любого потока, но всё равно нужно гарантировать отсутствие двойного `resume`.

### Реальный Пример: Ручное Преобразование Retrofit Call

```kotlin
import retrofit2.Call
import retrofit2.Callback
import retrofit2.HttpException
import retrofit2.Response
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

// Преобразование Retrofit Call в suspend-функцию
suspend fun <T> Call<T>.await(): T = suspendCancellableCoroutine { cont ->
    cont.invokeOnCancellation {
        cancel() // Отмена вызова Retrofit
    }

    enqueue(object : Callback<T> {
        override fun onResponse(call: Call<T>, response: Response<T>) {
            if (!cont.isActive) return

            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    cont.resume(body)
                } else {
                    cont.resumeWithException(
                        NullPointerException("Response body is null")
                    )
                }
            } else {
                cont.resumeWithException(HttpException(response))
            }
        }

        override fun onFailure(call: Call<T>, t: Throwable) {
            if (cont.isActive) {
                cont.resumeWithException(t)
            }
        }
    })
}
```

### Тестирование `suspendCancellableCoroutine`

```kotlin
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.test.runTest
import kotlin.coroutines.resume
import kotlin.concurrent.thread

class SuspendTest {
    @Test
    fun `успешное преобразование callback`() = runTest {
        val result = fetchData()
        assertEquals("Data", result)
    }

    @Test
    fun `обработка ошибки при преобразовании`() = runTest {
        var exceptionThrown = false
        try {
            fetchDataWithErrors()
        } catch (e: ApiException) {
            exceptionThrown = true
        }
        assertTrue(exceptionThrown)
    }

    @Test
    fun `очистка вызывается при отмене`() = runTest {
        var cleanupCalled = false

        val job = launch {
            suspendCancellableCoroutine<Unit> { cont ->
                cont.invokeOnCancellation {
                    cleanupCalled = true
                }
            }
        }

        job.cancelAndJoin()

        assertTrue(cleanupCalled, "Очистка должна вызываться при отмене")
    }

    @Test
    fun `нет двойного resume`() = runTest {
        var resumeCount = 0

        val job = launch {
            suspendCancellableCoroutine<Unit> { cont ->
                val resumed = AtomicBoolean(false)

                repeat(10) {
                    thread {
                        if (resumed.compareAndSet(false, true)) {
                            resumeCount++
                            cont.resume(Unit)
                        }
                    }
                }
            }
        }

        job.join()
        assertEquals(1, resumeCount, "Должен быть ровно один resume")
    }
}
```

### Частые Ошибки И Подводные Камни

- Двойной `resume` (при гонке между успехом, ошибкой и отменой) — защищайтесь `isActive` и/или атомарным флагом.
- Отсутствие `invokeOnCancellation`, когда нижележащий API поддерживает отмену или требует очистки.
- Вызов `resume` / `resumeWithException` после отмены — всегда проверяйте `cont.isActive` или используйте флаг.
- Игнорирование ошибок и проброс «сырых» кодов вместо понятных исключений.

### Рекомендуемые Практики

- По умолчанию использовать `suspendCancellableCoroutine` вместо `suspendCoroutine` для интеграции с внешними API.
- Всегда добавлять `invokeOnCancellation`, если есть что отменить или освободить.
- Явно моделировать три пути: успех, ошибка, отмена.
- Для многократных значений использовать `callbackFlow`, а не бесконечный `suspendCancellableCoroutine`.
- Писать тесты, которые проверяют отмену, очистку и отсутствие двойного `resume`.

### Когда Использовать Этот Шаблон

- Когда у вас одноразовый callback (один результат или ошибка).
- Когда внешний API предоставляет ручку отмены (`cancel()`, `dispose()` и т.п.).
- Когда нужно обернуть легаси/Java API в идиоматичный `suspend`-интерфейс.
- Когда важно корректно интегрироваться со структурированной отменой корутин.

### Ключевые Выводы

1. `suspendCancellableCoroutine` — основной инструмент для production-интеграций с callback API.
2. `invokeOnCancellation` критичен для освобождения ресурсов и прокидывания отмены во внешний API.
3. Возобновляйте продолжение ровно один раз; защищайтесь от гонок через `isActive`/атомарные флаги.
4. `CancellableContinuation` потокобезопасен, но вы отвечаете за отсутствие двойного `resume`.
5. Явно обрабатывайте успех, ошибку и отмену.
6. Покрывайте тестами сценарии отмены и очистки.
7. Не вызывайте `resume` после отмены; используйте проверки состояния.
8. Выполняйте очистку как в `invokeOnCancellation`, так и в финальных callback'ах.
9. Корректно преобразуйте ошибки (доменные исключения или `Result`).
10. Документируйте поведение suspend-функции (что она делает при отмене, какие ошибки бросает).

---

## Answer (EN)

Many Android and Java libraries use callback-based APIs (Retrofit callbacks, Firebase listeners, Location updates, OkHttp calls). To use them idiomatically with coroutines, you need to convert callbacks to suspend functions using `suspendCancellableCoroutine`. This is a critical skill for integrating legacy code with coroutines while handling cancellation, errors, and race conditions correctly.

See also [[c-coroutines]].

### suspendCoroutine Vs suspendCancellableCoroutine

`suspendCoroutine`: Basic suspension, no built-in structured cancellation for the underlying operation (unless the API itself exposes cancellation and you wire it manually).

```kotlin
suspend fun basicSuspend() = suspendCoroutine<String> { cont ->
    // Cannot automatically integrate coroutine cancellation with this async call
    someAsyncOperation { result ->
        cont.resume(result)
    }
}
```

`suspendCancellableCoroutine`: Cancellation-aware continuation; should be the default choice in production integrations.

```kotlin
suspend fun cancellableSuspend() = suspendCancellableCoroutine<String> { cont ->
    val operation = someAsyncOperation { result ->
        cont.resume(result)
    }

    // Clean up / cancel underlying work on coroutine cancellation
    cont.invokeOnCancellation {
        operation.cancel()
    }
}
```

Rule: Prefer `suspendCancellableCoroutine` for integrating with external async APIs unless you have a specific reason not to.

### Basic Pattern: Single Callback

```kotlin
// Callback-based API
interface DataCallback {
    fun onSuccess(data: String)
    fun onError(error: Exception)
}

fun fetchDataAsync(callback: DataCallback) {
    kotlin.concurrent.thread {
        Thread.sleep(1000)
        callback.onSuccess("Data")
    }
}

// Convert to suspend function
suspend fun fetchData(): String = suspendCancellableCoroutine { cont ->
    fetchDataAsync(object : DataCallback {
        override fun onSuccess(data: String) {
            if (cont.isActive) {
                cont.resume(data)
            }
        }

        override fun onError(error: Exception) {
            if (cont.isActive) {
                cont.resumeWithException(error)
            }
        }
    })

    // If fetchDataAsync supported cancellation, you'd call its cancel from invokeOnCancellation
}
```

### invokeOnCancellation for Resource Cleanup

```kotlin
suspend fun fetchWithCancellation(): String = suspendCancellableCoroutine { cont ->
    val request = api.createRequest()

    request.enqueue(object : DataCallback {
        override fun onSuccess(data: String) {
            if (cont.isActive) {
                cont.resume(data)
            }
        }

        override fun onError(error: Exception) {
            if (cont.isActive) {
                cont.resumeWithException(error)
            }
        }
    })

    // Clean up if cancelled
    cont.invokeOnCancellation {
        request.cancel() // Cancel underlying operation
    }
}
```

Here `DataCallback` is a placeholder API interface; replace with the real callback types for your library.

### Real Example: OkHttp Call Conversion

```kotlin
import okhttp3.Call
import okhttp3.Callback
import okhttp3.Response
import java.io.IOException
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

// Convert OkHttp Call to suspend function
suspend fun Call.await(): Response = suspendCancellableCoroutine { cont ->
    // Handle cancellation
    cont.invokeOnCancellation {
        cancel() // Cancel OkHttp call
    }

    // Enqueue call
    enqueue(object : Callback {
        override fun onResponse(call: Call, response: Response) {
            if (cont.isActive) {
                cont.resume(response)
            } else {
                // Coroutine was cancelled/completed, close the response to avoid leaks
                response.close()
            }
        }

        override fun onFailure(call: Call, e: IOException) {
            if (cont.isActive) {
                cont.resumeWithException(e)
            }
            // If not active, coroutine is already completed; do nothing
        }
    })
}
```

### Handling Race Conditions: Resume Exactly Once

The continuation must be resumed exactly once. `cont.isActive` is helpful, but not sufficient for inherently racy scenarios; use an atomic guard when both callbacks and cancellation may race:

```kotlin
import java.util.concurrent.atomic.AtomicBoolean

// CORRECT: Guard against double resume in presence of races
suspend fun safeOperation(): String = suspendCancellableCoroutine { cont ->
    val resumed = AtomicBoolean(false)

    val operation = startAsyncOp { result ->
        if (resumed.compareAndSet(false, true)) {
            cont.resume(result)
        }
    }

    cont.invokeOnCancellation {
        // Cancel underlying operation only if we haven't resumed yet
        if (resumed.compareAndSet(false, true)) {
            operation.cancel()
        }
    }
}
```

For well-behaved one-shot callbacks that guarantee a single terminal event, `if (cont.isActive)` is often enough.

### Real Example: Firebase Realtime Database

```kotlin
import com.google.firebase.database.*
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

// Single value fetch
suspend fun DatabaseReference.awaitValue(): DataSnapshot =
    suspendCancellableCoroutine { cont ->
        val listener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                if (cont.isActive) {
                    cont.resume(snapshot)
                }
            }

            override fun onCancelled(error: DatabaseError) {
                if (cont.isActive) {
                    cont.resumeWithException(error.toException())
                }
            }
        }

        // Attach listener
        addListenerForSingleValueEvent(listener)

        // Clean up on cancellation
        cont.invokeOnCancellation {
            removeEventListener(listener)
        }
    }
```

Callbacks must check `cont.isActive` and avoid resuming after cancellation.

### Real Example: Android Location Updates

```kotlin
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

// Single location update
suspend fun LocationManager.awaitLocation(provider: String): Location =
    suspendCancellableCoroutine { cont ->
        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                if (cont.isActive) {
                    cont.resume(location)
                    removeUpdates(this) // Clean up
                }
            }

            @Deprecated("Deprecated in Android Q")
            override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}

            override fun onProviderEnabled(provider: String) {}

            override fun onProviderDisabled(provider: String) {
                if (cont.isActive) {
                    cont.resumeWithException(
                        IllegalStateException("Provider $provider disabled")
                    )
                }
            }
        }

        // Request location update
        try {
            requestLocationUpdates(provider, 0L, 0f, listener)
        } catch (e: SecurityException) {
            cont.resumeWithException(e)
            return@suspendCancellableCoroutine
        }

        // Clean up on cancellation
        cont.invokeOnCancellation {
            removeUpdates(listener)
        }
    }
```

### Error Handling Patterns

```kotlin
suspend fun fetchDataWithErrors(): String = suspendCancellableCoroutine { cont ->
    api.getData(object : ApiCallback {
        override fun onSuccess(data: String) {
            if (cont.isActive) cont.resume(data)
        }

        override fun onError(code: Int, message: String) {
            val exception = when (code) {
                404 -> NotFoundException(message)
                401 -> UnauthorizedException(message)
                else -> ApiException(code, message)
            }
            if (cont.isActive) cont.resumeWithException(exception)
        }
    })
}
```

```kotlin
suspend fun fetchDataSafe(): Result<String> = suspendCancellableCoroutine { cont ->
    api.getData(object : ApiCallback {
        override fun onSuccess(data: String) {
            cont.resume(Result.success(data))
        }

        override fun onError(code: Int, message: String) {
            cont.resume(Result.failure(ApiException(code, message)))
        }
    })
}
```

### Thread-Safety Considerations

```kotlin
suspend fun threadSafeOperation(): String = suspendCancellableCoroutine { cont ->
    someLegacyApi.asyncCall(object : ApiCallbackSingleResult {
        override fun onComplete(result: String) {
            // CancellableContinuation is thread-safe: can be resumed from any thread,
            // but you must still prevent double resume.
            cont.resume(result)
        }
    })
}
```

`CancellableContinuation` is thread-safe: `resume` / `resumeWithException` can be called from any thread, but you must ensure it is only resumed once.

### Real Example: Retrofit Call Conversion (Manual)

```kotlin
import retrofit2.Call
import retrofit2.Callback
import retrofit2.HttpException
import retrofit2.Response
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.suspendCancellableCoroutine

// Convert Retrofit Call to suspend function
suspend fun <T> Call<T>.await(): T = suspendCancellableCoroutine { cont ->
    cont.invokeOnCancellation {
        cancel() // Cancel Retrofit call
    }

    enqueue(object : Callback<T> {
        override fun onResponse(call: Call<T>, response: Response<T>) {
            if (!cont.isActive) return

            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    cont.resume(body)
                } else {
                    cont.resumeWithException(
                        NullPointerException("Response body is null")
                    )
                }
            } else {
                cont.resumeWithException(HttpException(response))
            }
        }

        override fun onFailure(call: Call<T>, t: Throwable) {
            if (cont.isActive) {
                cont.resumeWithException(t)
            }
        }
    })
}
```

### Testing Cancellable Suspend Functions

```kotlin
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.test.runTest
import kotlin.coroutines.resume
import kotlin.concurrent.thread

class SuspendTest {
    @Test
    fun `test successful callback conversion`() = runTest {
        val result = fetchData()
        assertEquals("Data", result)
    }

    @Test
    fun `test error callback conversion`() = runTest {
        var exceptionThrown = false
        try {
            fetchDataWithErrors()
        } catch (e: ApiException) {
            exceptionThrown = true
        }
        assertTrue(exceptionThrown)
    }

    @Test
    fun `test cancellation cleanup`() = runTest {
        var cleanupCalled = false

        val job = launch {
            suspendCancellableCoroutine<Unit> { cont ->
                cont.invokeOnCancellation {
                    cleanupCalled = true
                }
            }
        }

        job.cancelAndJoin()

        assertTrue(cleanupCalled, "Cleanup should be called on cancellation")
    }

    @Test
    fun `test no double resume`() = runTest {
        var resumeCount = 0

        val job = launch {
            suspendCancellableCoroutine<Unit> { cont ->
                val resumed = AtomicBoolean(false)

                repeat(10) {
                    thread {
                        if (resumed.compareAndSet(false, true)) {
                            resumeCount++
                            cont.resume(Unit)
                        }
                    }
                }
            }
        }

        job.join()
        assertEquals(1, resumeCount, "Should resume exactly once")
    }
}
```

### Common Mistakes and Pitfalls

- Double resume due to racing callbacks and cancellation — guard with `isActive` and/or an atomic flag.
- Forgetting to cancel/cleanup underlying operations in `invokeOnCancellation` when possible.
- Resuming after cancellation — always check `cont.isActive` or use an atomic guard.
- Poor error mapping from callback errors to meaningful exceptions or `Result`.

### Best Practices

- Prefer `suspendCancellableCoroutine` over `suspendCoroutine` for cancellable external work.
- Always add `invokeOnCancellation` when underlying API supports cancel/dispose or requires cleanup.
- Model success, error, and cancellation explicitly.
- Use `callbackFlow` for multi-value or streaming callbacks instead of ad-hoc infinite suspensions.
- Write tests that verify cancellation, cleanup, and no double resume.

### When to Use This Pattern

- For one-shot callbacks that produce a single result or error.
- When wrapping Java/legacy async APIs into idiomatic suspend functions.
- When underlying APIs expose cancel/dispose semantics you can hook into.
- When integrating with structured concurrency and cooperative cancellation.

### Key Takeaways

1. `suspendCancellableCoroutine` is essential for production-grade callback conversion.
2. `invokeOnCancellation` is critical for releasing resources and propagating cancellation.
3. Resume exactly once; guard against races when necessary.
4. `CancellableContinuation` is thread-safe but does not make `resume` idempotent — you must prevent double resume.
5. Handle success, error, and cancellation paths explicitly.
6. Test cancellation behaviour and cleanup.
7. Do not call `resume`/`resumeWithException` after cancellation; use `isActive` and/or guards.
8. Perform cleanup both in `invokeOnCancellation` and in terminal callbacks where appropriate.
9. Map errors properly (domain exceptions or `Result`).
10. Document suspend function behaviour: cancellation, timeouts, and error semantics.

---

## Follow-ups

1. How would you convert a listener with multiple callbacks (onStart, onProgress, onComplete) to a suspend function while avoiding leaks and race conditions? Provide a code sketch, including how you ensure correct cancellation.
2. What happens if you call `resume()` or `resumeWithException()` after the coroutine has been cancelled or already resumed, and how do you prevent it in real APIs? Illustrate with a guard pattern.
3. How can you compose `suspendCancellableCoroutine` with `withTimeout` for callbacks that might hang indefinitely? Show how cancellation propagates and how you cancel the underlying operation.
4. When would you prefer `callbackFlow` over `suspendCancellableCoroutine` for bridging callback APIs that emit multiple values over time? Give a concrete example.
5. How can you design a small helper abstraction (e.g., wrapper or extension) to reduce duplication when wrapping multiple similar callback-based APIs with `suspendCancellableCoroutine`?

---

## References

- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/suspend-cancellable-coroutine.html
- https://kotlinlang.org/docs/cancellation-and-timeouts.html
- https://medium.com/androiddevelopers/bridging-the-gap-between-coroutines-jvm-threads-and-concurrency-problems-864e563bd7c

---

## Related Questions

- [[q-continuation-cps-internals--kotlin--hard|Continuation and CPS internals]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|callbackFlow for multiple values]]
- [[q-coroutine-exception-handler--kotlin--medium|Exception handling in coroutines]]

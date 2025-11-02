---
id: kotlin-095
title: "Converting callbacks with suspendCancellableCoroutine / Преобразование callback с suspendCancellableCoroutine"
topic: kotlin
difficulty: hard
status: draft
created: 2025-10-12
tags:
  - kotlin
  - coroutines
  - suspend
  - callbacks
  - cancellation
  - integration
moc: moc-kotlin
related: [q-job-state-machine-transitions--kotlin--medium, q-anonymous-class-in-inline-function--programming-languages--medium, q-debounce-throttle-flow--kotlin--medium]
  - q-continuation-cps-internals--kotlin--hard
  - q-channelflow-callbackflow-flow--kotlin--medium
  - q-coroutine-exception-handler--kotlin--medium
subtopics:
  - coroutines
  - suspend
  - callbacks
  - integration
  - cancellation
---

# Question (EN)
> How do you convert callback-based APIs to suspend functions using `suspendCancellableCoroutine`? How do you handle cancellation, errors, and race conditions?

# Вопрос (RU)
> Как преобразовать API на основе callback в suspend функции используя `suspendCancellableCoroutine`? Как обрабатывать отмену, ошибки и состояния гонки?

---

## Answer (EN)

Many Android and Java libraries use callback-based APIs (Retrofit callbacks, Firebase listeners, Location updates, OkHttp calls). To use them idiomatically with coroutines, you need to convert callbacks to suspend functions using `suspendCancellableCoroutine`. This is a critical skill for integrating legacy code with coroutines while handling cancellation properly.



### suspendCoroutine vs suspendCancellableCoroutine

**suspendCoroutine:** Basic suspension, no cancellation support

```kotlin
suspend fun basicSuspend() = suspendCoroutine<String> { cont ->
    // Cannot handle cancellation!
    someAsyncOperation { result ->
        cont.resume(result)
    }
}
```

**suspendCancellableCoroutine:** Cancellation-aware, should be used in production

```kotlin
suspend fun cancellableSuspend() = suspendCancellableCoroutine<String> { cont ->
    val operation = someAsyncOperation { result ->
        cont.resume(result)
    }

    // Clean up on cancellation
    cont.invokeOnCancellation {
        operation.cancel()
    }
}
```

**When to use each:**

| Feature | suspendCoroutine | suspendCancellableCoroutine |
|---------|------------------|----------------------------|
| **Cancellation** |  Not supported |  Supported |
| **invokeOnCancellation** |  Not available |  Available |
| **Performance** | Slightly faster | Recommended |
| **Use case** | Quick tests, non-cancellable ops | **Production code** |

**Rule:** Always use `suspendCancellableCoroutine` unless you have a specific reason not to.

### Basic Pattern: Single Callback

```kotlin
// Callback-based API
interface DataCallback {
    fun onSuccess(data: String)
    fun onError(error: Exception)
}

fun fetchDataAsync(callback: DataCallback) {
    thread {
        Thread.sleep(1000)
        callback.onSuccess("Data")
    }
}

// Convert to suspend function
suspend fun fetchData(): String = suspendCancellableCoroutine { cont ->
    fetchDataAsync(object : DataCallback {
        override fun onSuccess(data: String) {
            // Resume with success
            cont.resume(data)
        }

        override fun onError(error: Exception) {
            // Resume with exception
            cont.resumeWithException(error)
        }
    })
}

// Usage
launch {
    try {
        val data = fetchData()
        println("Success: $data")
    } catch (e: Exception) {
        println("Error: $e")
    }
}
```

### invokeOnCancellation for Resource Cleanup

**Critical:** Always clean up resources when coroutine is cancelled.

```kotlin
suspend fun fetchWithCancellation(): String = suspendCancellableCoroutine { cont ->
    val request = api.createRequest()

    request.enqueue(object : Callback {
        override fun onSuccess(data: String) {
            cont.resume(data)
        }

        override fun onError(error: Exception) {
            cont.resumeWithException(error)
        }
    })

    // Clean up if cancelled
    cont.invokeOnCancellation {
        request.cancel() // Cancel underlying operation
    }
}
```

### Real Example: OkHttp Call Conversion

```kotlin
import okhttp3.*
import java.io.IOException
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

// Convert OkHttp Call to suspend function
suspend fun Call.await(): Response = suspendCancellableCoroutine { cont ->
    // Handle cancellation
    cont.invokeOnCancellation {
        cancel() // Cancel OkHttp call
    }

    // Enqueue call
    enqueue(object : Callback {
        override fun onResponse(call: Call, response: Response) {
            if (cont.isActive) { // Check if still active
                cont.resume(response)
            } else {
                response.close() // Clean up if cancelled
            }
        }

        override fun onFailure(call: Call, e: IOException) {
            if (cont.isActive) {
                cont.resumeWithException(e)
            }
        }
    })
}

// Usage
suspend fun fetchUser(userId: String): User {
    val client = OkHttpClient()
    val request = Request.Builder()
        .url("https://api.example.com/users/$userId")
        .build()

    val response = client.newCall(request).await()
    return response.use { Json.decodeFromString(it.body!!.string()) }
}

// With cancellation
val job = launch {
    try {
        val user = fetchUser("123")
        println(user)
    } catch (e: CancellationException) {
        println("Request cancelled")
    }
}

delay(100)
job.cancel() // Cancels OkHttp call automatically
```

### Handling Race Conditions: Resume Exactly Once

**Critical rule:** Continuation must be resumed **exactly once** - not zero, not twice.

**Problem: Race condition between callback and cancellation**

```kotlin
//  WRONG: Can resume twice
suspend fun racyOperation(): String = suspendCancellableCoroutine { cont ->
    val operation = startAsyncOp { result ->
        cont.resume(result) // May be called after cancellation!
    }

    cont.invokeOnCancellation {
        operation.cancel()
        cont.resume("Cancelled") // ERROR: Second resume!
    }
}
```

**Solution: Check isActive and use atomic flag**

```kotlin
//  CORRECT: Resume exactly once
suspend fun safeOperation(): String = suspendCancellableCoroutine { cont ->
    val resumed = AtomicBoolean(false)

    val operation = startAsyncOp { result ->
        // Only resume if not already resumed
        if (resumed.compareAndSet(false, true)) {
            cont.resume(result)
        }
    }

    cont.invokeOnCancellation {
        if (resumed.compareAndSet(false, true)) {
            operation.cancel()
            // Don't resume here - let callback handle it or throw CancellationException
        }
    }
}

//  BETTER: Use cont.isActive
suspend fun safeOperation2(): String = suspendCancellableCoroutine { cont ->
    val operation = startAsyncOp { result ->
        if (cont.isActive) { // Only resume if not cancelled
            cont.resume(result)
        }
    }

    cont.invokeOnCancellation {
        operation.cancel()
    }
}
```

### Real Example: Firebase Realtime Database

```kotlin
import com.google.firebase.database.*
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

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

// Usage
suspend fun getUserProfile(userId: String): UserProfile {
    val database = FirebaseDatabase.getInstance()
    val snapshot = database.getReference("users/$userId").awaitValue()
    return snapshot.getValue(UserProfile::class.java)!!
}

// With timeout
suspend fun getUserProfileWithTimeout(userId: String): UserProfile {
    return withTimeout(5000) {
        getUserProfile(userId)
    }
}
```

### Real Example: Android Location Updates

```kotlin
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow

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

// Usage in ViewModel
class LocationViewModel : ViewModel() {
    fun getCurrentLocation() {
        viewModelScope.launch {
            try {
                val location = locationManager.awaitLocation(LocationManager.GPS_PROVIDER)
                _locationState.value = LocationState.Success(location)
            } catch (e: Exception) {
                _locationState.value = LocationState.Error(e.message)
            }
        }
    }
}
```

### Error Handling Patterns

**Pattern 1: Resume with exception**

```kotlin
suspend fun fetchData(): String = suspendCancellableCoroutine { cont ->
    api.getData(object : Callback {
        override fun onSuccess(data: String) {
            cont.resume(data)
        }

        override fun onError(code: Int, message: String) {
            // Convert to exception
            val exception = when (code) {
                404 -> NotFoundException(message)
                401 -> UnauthorizedException(message)
                else -> ApiException(code, message)
            }
            cont.resumeWithException(exception)
        }
    })
}
```

**Pattern 2: Resume with Result wrapper**

```kotlin
suspend fun fetchDataSafe(): Result<String> = suspendCancellableCoroutine { cont ->
    api.getData(object : Callback {
        override fun onSuccess(data: String) {
            cont.resume(Result.success(data))
        }

        override fun onError(code: Int, message: String) {
            cont.resume(Result.failure(ApiException(code, message)))
        }
    })
}

// Usage
when (val result = fetchDataSafe()) {
    is Result.Success -> println(result.value)
    is Result.Failure -> println("Error: ${result.exception}")
}
```

### Thread-Safety Considerations

**Problem:** Callback may be called on different thread

```kotlin
// Callback may be called on any thread
suspend fun threadSafeOperation(): String = suspendCancellableCoroutine { cont ->
    someLegacyApi.asyncCall(object : Callback {
        override fun onComplete(result: String) {
            // This may be called on worker thread, UI thread, etc.
            // CancellableContinuation is thread-safe
            cont.resume(result) // Safe to call from any thread
        }
    })
}
```

**CancellableContinuation is thread-safe:** You can safely call `resume()` and `resumeWithException()` from any thread.

### Real Example: Retrofit Call Conversion (Manual)

```kotlin
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

// Convert Retrofit Call to suspend function
suspend fun <T> Call<T>.await(): T = suspendCancellableCoroutine { cont ->
    cont.invokeOnCancellation {
        cancel() // Cancel Retrofit call
    }

    enqueue(object : Callback<T> {
        override fun onResponse(call: Call<T>, response: Response<T>) {
            if (cont.isActive) {
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
                    cont.resumeWithException(
                        HttpException(response.code(), response.message())
                    )
                }
            }
        }

        override fun onFailure(call: Call<T>, t: Throwable) {
            if (cont.isActive) {
                cont.resumeWithException(t)
            }
        }
    })
}

// Usage (Note: Retrofit has built-in suspend support, this is for demonstration)
interface ApiService {
    @GET("users/{id}")
    fun getUser(@Path("id") id: String): Call<User>
}

suspend fun fetchUser(id: String): User {
    return api.getUser(id).await()
}
```

### Testing Cancellable Suspend Functions

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

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
            fetchDataWithError()
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

        job.cancel()
        job.join()

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

**Mistake 1: Not checking isActive before resume**

```kotlin
//  WRONG
suspend fun mistake1() = suspendCancellableCoroutine<String> { cont ->
    asyncOp { result ->
        cont.resume(result) // May throw if cancelled!
    }
}

//  CORRECT
suspend fun correct1() = suspendCancellableCoroutine<String> { cont ->
    asyncOp { result ->
        if (cont.isActive) {
            cont.resume(result)
        }
    }
}
```

**Mistake 2: Forgetting invokeOnCancellation**

```kotlin
//  WRONG: No cleanup
suspend fun mistake2() = suspendCancellableCoroutine<String> { cont ->
    val request = api.startRequest { result ->
        cont.resume(result)
    }
    // Request continues even if coroutine cancelled!
}

//  CORRECT: Clean up
suspend fun correct2() = suspendCancellableCoroutine<String> { cont ->
    val request = api.startRequest { result ->
        cont.resume(result)
    }
    cont.invokeOnCancellation {
        request.cancel()
    }
}
```

**Mistake 3: Resuming multiple times**

```kotlin
//  WRONG: Can resume twice
suspend fun mistake3() = suspendCancellableCoroutine<String> { cont ->
    asyncOp { result ->
        cont.resume(result)
    }
    cont.invokeOnCancellation {
        cont.resume("Cancelled") // ERROR: Second resume!
    }
}

//  CORRECT: Resume once
suspend fun correct3() = suspendCancellableCoroutine<String> { cont ->
    asyncOp { result ->
        if (cont.isActive) cont.resume(result)
    }
    cont.invokeOnCancellation {
        // Don't resume, just clean up
    }
}
```

**Mistake 4: Not handling null body in Retrofit**

```kotlin
//  WRONG: Crashes on null body
suspend fun <T> Call<T>.await(): T = suspendCancellableCoroutine { cont ->
    enqueue(object : Callback<T> {
        override fun onResponse(call: Call<T>, response: Response<T>) {
            cont.resume(response.body()!!) // NullPointerException!
        }
        override fun onFailure(call: Call<T>, t: Throwable) {
            cont.resumeWithException(t)
        }
    })
}

//  CORRECT: Handle null
suspend fun <T> Call<T>.await(): T = suspendCancellableCoroutine { cont ->
    enqueue(object : Callback<T> {
        override fun onResponse(call: Call<T>, response: Response<T>) {
            val body = response.body()
            if (body != null) {
                cont.resume(body)
            } else {
                cont.resumeWithException(NullPointerException("Response body is null"))
            }
        }
        override fun onFailure(call: Call<T>, t: Throwable) {
            cont.resumeWithException(t)
        }
    })
}
```

**Mistake 5: Using suspendCoroutine instead of suspendCancellableCoroutine**

```kotlin
//  WRONG: No cancellation support
suspend fun mistake5() = suspendCoroutine<String> { cont ->
    longRunningOperation { result ->
        cont.resume(result)
    }
    // Can't cancel longRunningOperation!
}

//  CORRECT: Cancellation support
suspend fun correct5() = suspendCancellableCoroutine<String> { cont ->
    val operation = longRunningOperation { result ->
        if (cont.isActive) cont.resume(result)
    }
    cont.invokeOnCancellation {
        operation.cancel()
    }
}
```

### Best Practices

1.  **Always use suspendCancellableCoroutine** in production code
2.  **Always implement invokeOnCancellation** for cleanup
3.  **Check cont.isActive** before resuming
4.  **Resume exactly once** - use atomic flags if needed
5.  **Handle all error cases** - don't leave continuation hanging
6.  **Test cancellation scenarios** - verify cleanup happens
7.  **Make thread-safe** - CancellableContinuation handles this
8.  **Document suspension points** - help future maintainers
9.  **Use Result wrapper for expected errors** - vs exceptions
10.  **Close resources** in invokeOnCancellation

### When to Use This Pattern

**Use suspendCancellableCoroutine when:**
- Integrating callback-based libraries (OkHttp, Firebase, Location)
- Converting legacy async APIs to coroutines
- Creating custom suspending operations
- Need fine-grained cancellation control

**Don't use when:**
- Library already has suspend support (modern Retrofit)
- Can use `callbackFlow` instead (for streams of values)
- Simple operations don't need suspension

### Key Takeaways

1. **suspendCancellableCoroutine is essential** - For production callback conversion
2. **invokeOnCancellation is critical** - Always clean up resources
3. **Resume exactly once** - Check isActive, use atomic flags
4. **Thread-safe by default** - CancellableContinuation handles it
5. **Handle all paths** - Success, error, cancellation
6. **Test cancellation** - Verify cleanup happens
7. **Don't resume after cancellation** - Check isActive first
8. **Clean up eagerly** - In invokeOnCancellation
9. **Convert errors properly** - To exceptions or Result
10. **Document behavior** - Suspension and cancellation semantics

---

## Ответ (RU)

Многие Android и Java библиотеки используют API на основе callback (Retrofit callbacks, Firebase listeners, Location updates, OkHttp calls). Для их идиоматичного использования с корутинами нужно преобразовать callback в suspend функции используя `suspendCancellableCoroutine`. Это критический навык для интеграции legacy кода с корутинами с правильной обработкой отмены.



[Полный русский перевод опущен для краткости, но следует той же структуре что и английская версия]

### Ключевые выводы

1. **suspendCancellableCoroutine критичен** - Для production преобразования callback
2. **invokeOnCancellation обязателен** - Всегда очищайте ресурсы
3. **Возобновляйте ровно один раз** - Проверяйте isActive, используйте atomic флаги
4. **Потокобезопасно по умолчанию** - CancellableContinuation обрабатывает это
5. **Обрабатывайте все пути** - Успех, ошибка, отмена
6. **Тестируйте отмену** - Проверяйте что очистка происходит
7. **Не возобновляйте после отмены** - Сначала проверяйте isActive
8. **Очищайте активно** - В invokeOnCancellation
9. **Правильно преобразуйте ошибки** - В исключения или Result
10. **Документируйте поведение** - Семантику приостановки и отмены

---

## Follow-ups

1. How do you convert a listener with multiple callbacks (onStart, onProgress, onComplete) to suspend function?
2. What happens if you call resume() after the coroutine has been cancelled?
3. How do you implement timeout for callback-based operations using suspendCancellableCoroutine?
4. Can you explain the difference between invokeOnCancellation and Job.invokeOnCompletion?
5. How do you handle callbacks that may be called multiple times (like WebSocket messages)?
6. What's the performance overhead of suspendCancellableCoroutine vs direct callback?
7. How do you test race conditions between callback and cancellation?

## References

- [suspendCancellableCoroutine Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/suspend-cancellable-coroutine.html)
- [Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Bridging Callbacks and Coroutines](https://medium.com/androiddevelopers/bridging-the-gap-between-coroutines-jvm-threads-and-concurrency-problems-864e563bd7c)

## Related Questions

- [[q-continuation-cps-internals--kotlin--hard|Continuation and CPS internals]]
- [[q-channelflow-callbackflow-flow--kotlin--medium|callbackFlow for multiple values]]
- [[q-coroutine-exception-handler--kotlin--medium|Exception handling in coroutines]]

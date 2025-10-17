---
id: 20251012-160003
title: "CoroutineExceptionHandler: installation and usage / CoroutineExceptionHandler: установка и использование"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-12
tags: - kotlin
  - coroutines
  - exception-handling
  - error-handling
  - ceh
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-kotlin
related_questions:   - q-common-coroutine-mistakes--kotlin--medium
  - q-debugging-coroutines-techniques--kotlin--medium
  - q-suspend-cancellable-coroutine--kotlin--hard
slug: coroutine-exception-handler-kotlin-medium
subtopics:   - coroutines
  - exception-handling
  - ceh
  - error-handling
---
# CoroutineExceptionHandler: installation and usage

## English Version

### Problem Statement

Unhandled exceptions in coroutines can crash your application or silently fail, making debugging difficult. **CoroutineExceptionHandler (CEH)** provides a last-resort mechanism to catch uncaught exceptions in coroutines. However, it doesn't work everywhere and has specific installation rules.

**The Question:** What is CoroutineExceptionHandler, where can it be installed, and how does it work with different coroutine builders (launch vs async)?

### Detailed Answer

#### What is CoroutineExceptionHandler?

**CoroutineExceptionHandler** is a `CoroutineContext.Element` that handles uncaught exceptions in coroutines. It acts as a **last-resort handler** - similar to `Thread.UncaughtExceptionHandler` for threads.

```kotlin
import kotlinx.coroutines.*

val handler = CoroutineExceptionHandler { context, exception ->
    println("Caught exception: $exception")
}

fun main() = runBlocking {
    val job = GlobalScope.launch(handler) {
        throw RuntimeException("Test exception")
    }
    job.join()
}
// Output: Caught exception: java.lang.RuntimeException: Test exception
```

#### Key Principles

**CEH works ONLY on:**
1.  **Root coroutines** (direct children of CoroutineScope)
2.  **launch** (fire-and-forget coroutines)
3.  **actor** (channel-based actors)

**CEH does NOT work on:**
1.  **async** (exceptions handled by await())
2.  **Child coroutines** (exceptions propagate to parent)
3.  **runBlocking** (exceptions thrown directly)
4.  **supervisorScope children** (need own CEH)

#### CEH with launch (Works)

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH caught: ${exception.message}")
    }

    //  WORKS: launch with CEH
    val job = launch(handler) {
        throw RuntimeException("Exception in launch")
    }

    job.join()
    println("Program continues")
}

// Output:
// CEH caught: Exception in launch
// Program continues
```

#### CEH with async (Does NOT Work)

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH caught: ${exception.message}")
    }

    //  DOES NOT WORK: async with CEH
    val deferred = async(handler) {
        throw RuntimeException("Exception in async")
    }

    try {
        deferred.await() // Exception thrown HERE
    } catch (e: Exception) {
        println("Caught in try-catch: ${e.message}")
    }
}

// Output:
// Caught in try-catch: Exception in async
// CEH is NOT called!
```

**Why?** `async` exposes exceptions through its `Deferred` result. You must call `await()` and handle the exception there. CEH is bypassed.

#### Exception Propagation Hierarchy

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: ${exception.message}")
    }

    // Root coroutine with CEH
    launch(handler) {
        println("Parent coroutine")

        // Child coroutine - exception propagates to parent
        launch {
            throw RuntimeException("Child exception")
        }

        delay(100)
        println("This won't execute")
    }

    delay(500)
}

// Output:
// Parent coroutine
// CEH: Child exception
```

**Rule:** Exceptions in child coroutines propagate UP to the nearest CEH in a parent coroutine.

#### Installing CEH in CoroutineScope

**Pattern 1: Scope-level CEH**

```kotlin
class MyRepository {
    private val handler = CoroutineExceptionHandler { _, exception ->
        Log.e("Repository", "Uncaught exception", exception)
        // Send to crash reporting (Firebase Crashlytics, Sentry)
    }

    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO + handler
    )

    fun fetchData() {
        scope.launch {
            // All exceptions caught by handler
            throw RuntimeException("Fetch failed")
        }
    }

    fun cleanup() {
        scope.cancel()
    }
}
```

**Pattern 2: Individual coroutine CEH**

```kotlin
fun fetchDataWithCustomHandler() = viewModelScope.launch {
    val handler = CoroutineExceptionHandler { _, exception ->
        _errorState.value = "Error: ${exception.message}"
    }

    launch(handler) {
        val data = api.fetchData()
        _dataState.value = data
    }
}
```

#### Default Exception Handler

If no CEH is installed, the **default handler** is used:

- **JVM:** Prints stack trace to `System.err`
- **Android:** Crashes the app (via `Thread.getDefaultUncaughtExceptionHandler()`)
- **JS:** Prints to console
- **Native:** Terminates the program

```kotlin
// No CEH installed
fun main() = runBlocking {
    launch {
        throw RuntimeException("Uncaught")
    }
    delay(100)
}

// Output:
// Exception in thread "main" java.lang.RuntimeException: Uncaught
//     at ...
// (Stack trace printed to stderr)
```

#### CEH in Android Application

**Global crash handler in Application class:**

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Install global CEH
        val handler = CoroutineExceptionHandler { context, exception ->
            Log.e("App", "Uncaught coroutine exception", exception)

            // Send to crash reporting
            FirebaseCrashlytics.getInstance().recordException(exception)

            // Show user-friendly error
            Toast.makeText(this, "An error occurred", Toast.LENGTH_SHORT).show()

            // Optionally crash the app (for critical errors)
            if (exception is CriticalException) {
                throw exception
            }
        }

        // Set as default for all coroutines in the app
        // Note: This requires custom CoroutineScope setup
    }
}
```

**ViewModel with CEH:**

```kotlin
class UserViewModel : ViewModel() {
    private val handler = CoroutineExceptionHandler { _, exception ->
        Log.e("UserViewModel", "Error", exception)
        _errorState.value = exception.toUserFriendlyMessage()
    }

    private val vmScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main + handler
    )

    private val _errorState = MutableStateFlow<String?>(null)
    val errorState: StateFlow<String?> = _errorState.asStateFlow()

    fun loadUser(userId: String) {
        vmScope.launch {
            val user = userRepository.getUser(userId) // May throw
            _userState.value = user
        }
    }

    override fun onCleared() {
        super.onCleared()
        vmScope.cancel()
    }
}

fun Exception.toUserFriendlyMessage(): String {
    return when (this) {
        is NetworkException -> "Network error. Please check your connection."
        is AuthException -> "Authentication failed. Please log in again."
        else -> "An unexpected error occurred."
    }
}
```

#### Why CEH Doesn't Catch Exceptions in async

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: $exception")
    }

    // Scenario 1: async without await - exception stored in Deferred
    val deferred1 = async(handler) {
        throw RuntimeException("Error 1")
    }
    delay(100)
    println("Deferred created, no exception yet")

    // Scenario 2: await() throws the exception
    try {
        deferred1.await()
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }

    // Scenario 3: If you never call await(), exception is lost!
    val deferred2 = async(handler) {
        throw RuntimeException("Error 2")
    }
    // Never calling await() - exception is silently ignored!
}

// Output:
// Deferred created, no exception yet
// Caught: Error 1
// (Error 2 is never caught or logged!)
```

**Solution:** Always await() async results or use launch instead.

#### supervisorScope and CEH Interaction

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: ${exception.message}")
    }

    // CEH on parent doesn't help supervisorScope children
    launch(handler) {
        supervisorScope {
            // Child 1: needs its own CEH
            launch {
                throw RuntimeException("Child 1 exception")
            }

            // Child 2: continues even after child 1 fails
            launch {
                delay(100)
                println("Child 2 still running")
            }
        }
    }

    delay(200)
}

// Output:
// Exception in thread "..." RuntimeException: Child 1 exception
// Child 2 still running
```

**Fix: Install CEH on each supervisorScope child:**

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH: ${exception.message}")
    }

    launch(handler) {
        supervisorScope {
            // Each child needs own handler
            launch(handler) {
                throw RuntimeException("Child 1 exception")
            }

            launch(handler) {
                delay(100)
                println("Child 2 still running")
            }
        }
    }

    delay(200)
}

// Output:
// CEH: Child 1 exception
// Child 2 still running
```

#### Real-World Example: Logging and Analytics

```kotlin
class ProductionCoroutineExceptionHandler(
    private val analytics: AnalyticsService,
    private val crashReporter: CrashReportingService
) : CoroutineExceptionHandler {

    override val key: CoroutineContext.Key<*> = CoroutineExceptionHandler

    override fun handleException(context: CoroutineContext, exception: Throwable) {
        // Log to console
        Log.e("CEH", "Unhandled exception in coroutine", exception)

        // Extract coroutine info
        val coroutineName = context[CoroutineName]?.name ?: "unnamed"
        val job = context[Job]

        // Send to analytics
        analytics.logEvent("coroutine_exception") {
            param("coroutine_name", coroutineName)
            param("exception_type", exception::class.simpleName ?: "Unknown")
            param("exception_message", exception.message ?: "No message")
        }

        // Send to crash reporter (non-fatal)
        crashReporter.recordException(exception) {
            setCustomKey("coroutine_name", coroutineName)
            setCustomKey("job_cancelled", job?.isCancelled.toString())
        }

        // Don't crash for certain exceptions
        when (exception) {
            is CancellationException -> {
                // Expected, don't crash
            }
            is NetworkException -> {
                // Network issues, don't crash
            }
            else -> {
                // For other exceptions, consider crashing
                // throw exception
            }
        }
    }
}

// Usage
class MyViewModel(
    private val ceh: ProductionCoroutineExceptionHandler
) : ViewModel() {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main + ceh
    )

    fun loadData() {
        scope.launch(CoroutineName("LoadData")) {
            repository.fetchData()
        }
    }
}
```

#### CEH Limitations and Alternatives

**Limitations:**

1. **Doesn't work with async/await** - Use try-catch around await()
2. **Not called for CancellationException** - Cancellation is not an error
3. **Last resort only** - Doesn't replace proper error handling
4. **Can't prevent crash in some cases** - Android may still crash

**Alternatives:**

```kotlin
// Alternative 1: Try-catch in coroutine
launch {
    try {
        riskyOperation()
    } catch (e: Exception) {
        handleError(e)
    }
}

// Alternative 2: runCatching
launch {
    runCatching {
        riskyOperation()
    }.onFailure { exception ->
        handleError(exception)
    }
}

// Alternative 3: Result wrapper
launch {
    val result = repository.fetchData() // Returns Result<T>
    result.onSuccess { data ->
        updateUI(data)
    }.onFailure { exception ->
        showError(exception)
    }
}

// Alternative 4: Flow with catch operator
repository.dataFlow
    .catch { exception ->
        emit(ErrorState(exception))
    }
    .collect { data ->
        updateUI(data)
    }
```

#### Best Practices

**1. Use CEH for unexpected exceptions:**

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    if (exception !is CancellationException) {
        Log.e("App", "Unexpected exception", exception)
        reportToCrashlytics(exception)
    }
}
```

**2. Combine with try-catch for expected errors:**

```kotlin
launch(handler) {
    try {
        val data = api.fetchData()
        updateUI(data)
    } catch (e: NetworkException) {
        // Handle expected network errors
        showNetworkError()
    }
    // CEH catches unexpected exceptions
}
```

**3. Use SupervisorJob with CEH:**

```kotlin
val scope = CoroutineScope(
    SupervisorJob() + Dispatchers.Main + handler
)
// Children can fail independently
```

**4. Name your coroutines for debugging:**

```kotlin
launch(handler + CoroutineName("FetchUser")) {
    // Exception will include coroutine name
}
```

**5. Don't rely on CEH alone:**

```kotlin
//  BAD: No error handling, relying on CEH
launch(handler) {
    val data = api.fetchData()
    updateUI(data)
}

//  GOOD: Explicit error handling + CEH as backup
launch(handler) {
    try {
        val data = api.fetchData()
        updateUI(data)
    } catch (e: ApiException) {
        showError(e)
    }
    // CEH catches truly unexpected exceptions
}
```

#### Testing CEH

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class CEHTest {
    @Test
    fun `CEH catches launch exceptions`() = runTest {
        var caughtException: Throwable? = null

        val handler = CoroutineExceptionHandler { _, exception ->
            caughtException = exception
        }

        val job = launch(handler) {
            throw RuntimeException("Test exception")
        }

        job.join()

        assertTrue(caughtException is RuntimeException)
        assertEquals("Test exception", caughtException?.message)
    }

    @Test
    fun `CEH does not catch async exceptions`() = runTest {
        var caughtByHandler = false

        val handler = CoroutineExceptionHandler { _, _ ->
            caughtByHandler = true
        }

        val deferred = async(handler) {
            throw RuntimeException("Test exception")
        }

        var caughtByTryCatch = false
        try {
            deferred.await()
        } catch (e: Exception) {
            caughtByTryCatch = true
        }

        assertTrue(caughtByTryCatch)
        assertTrue(!caughtByHandler, "CEH should not be called for async")
    }

    @Test
    fun `CEH in supervisorScope children`() = runTest {
        val exceptions = mutableListOf<Throwable>()

        val handler = CoroutineExceptionHandler { _, exception ->
            exceptions.add(exception)
        }

        supervisorScope {
            launch(handler) {
                throw RuntimeException("Child 1")
            }

            launch(handler) {
                throw RuntimeException("Child 2")
            }
        }

        assertEquals(2, exceptions.size)
    }
}
```

#### Common Mistakes

**Mistake 1: Installing CEH on child coroutines**

```kotlin
//  WRONG: CEH on child has no effect
launch {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("This won't be called")
    }

    launch(handler) { // Child coroutine
        throw RuntimeException("Exception")
    }
}
```

**Mistake 2: Using CEH with async**

```kotlin
//  WRONG: CEH doesn't work with async
val handler = CoroutineExceptionHandler { _, exception ->
    println("Not called")
}

async(handler) {
    throw RuntimeException("Exception")
}.await() // Exception thrown here, not caught by CEH
```

**Mistake 3: Relying only on CEH**

```kotlin
//  WRONG: No explicit error handling
launch(handler) {
    val data = api.fetchData() // What if this fails?
    updateUI(data)
}

//  CORRECT: Explicit + CEH
launch(handler) {
    try {
        val data = api.fetchData()
        updateUI(data)
    } catch (e: ApiException) {
        showError(e)
    }
}
```

### Key Takeaways

1. **CEH is a last-resort handler** - Not a replacement for try-catch
2. **Works only on root coroutines** - And only with launch/actor
3. **Doesn't work with async** - Exceptions exposed via await()
4. **Install on CoroutineScope** - For scope-wide error handling
5. **Combine with SupervisorJob** - For independent child failure
6. **Name coroutines** - Makes debugging easier
7. **Use for logging/analytics** - Send uncaught exceptions to crash reporting
8. **Don't ignore expected errors** - Use explicit error handling

---

## Русская версия

### Формулировка проблемы

Необработанные исключения в корутинах могут приводить к краху приложения или незаметному сбою, затрудняя отладку. **CoroutineExceptionHandler (CEH)** предоставляет механизм последней инстанции для перехвата необработанных исключений в корутинах. Однако он работает не везде и имеет специфические правила установки.

**Вопрос:** Что такое CoroutineExceptionHandler, где его можно установить, и как он работает с разными билдерами корутин (launch vs async)?

### Подробный ответ

#### Что такое CoroutineExceptionHandler?

**CoroutineExceptionHandler** - это `CoroutineContext.Element`, который обрабатывает необработанные исключения в корутинах. Он действует как **обработчик последней инстанции** - аналогично `Thread.UncaughtExceptionHandler` для потоков.

#### Ключевые принципы

**CEH работает ТОЛЬКО на:**
1.  **Корневых корутинах** (прямых потомках CoroutineScope)
2.  **launch** (корутины "запустить и забыть")
3.  **actor** (акторы на основе каналов)

**CEH НЕ работает на:**
1.  **async** (исключения обрабатываются через await())
2.  **Дочерних корутинах** (исключения распространяются к родителю)
3.  **runBlocking** (исключения выбрасываются напрямую)
4.  **Потомках supervisorScope** (нужен собственный CEH)

#### CEH с launch (Работает)

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH поймал: ${exception.message}")
    }

    //  РАБОТАЕТ: launch с CEH
    val job = launch(handler) {
        throw RuntimeException("Исключение в launch")
    }

    job.join()
    println("Программа продолжается")
}

// Вывод:
// CEH поймал: Исключение в launch
// Программа продолжается
```

#### CEH с async (НЕ работает)

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, exception ->
        println("CEH поймал: ${exception.message}")
    }

    //  НЕ РАБОТАЕТ: async с CEH
    val deferred = async(handler) {
        throw RuntimeException("Исключение в async")
    }

    try {
        deferred.await() // Исключение выбрасывается ЗДЕСЬ
    } catch (e: Exception) {
        println("Поймано в try-catch: ${e.message}")
    }
}

// Вывод:
// Поймано в try-catch: Исключение в async
// CEH НЕ вызывается!
```

**Почему?** `async` предоставляет исключения через свой результат `Deferred`. Вы должны вызвать `await()` и обработать исключение там. CEH обходится.

#### Реальный пример Android ViewModel

```kotlin
class UserViewModel : ViewModel() {
    private val handler = CoroutineExceptionHandler { _, exception ->
        Log.e("UserViewModel", "Ошибка", exception)
        _errorState.value = exception.toUserFriendlyMessage()
    }

    private val vmScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main + handler
    )

    private val _errorState = MutableStateFlow<String?>(null)
    val errorState: StateFlow<String?> = _errorState.asStateFlow()

    fun loadUser(userId: String) {
        vmScope.launch {
            val user = userRepository.getUser(userId) // Может выбросить исключение
            _userState.value = user
        }
    }

    override fun onCleared() {
        super.onCleared()
        vmScope.cancel()
    }
}
```

### Ключевые выводы

1. **CEH - обработчик последней инстанции** - Не замена try-catch
2. **Работает только на корневых корутинах** - И только с launch/actor
3. **Не работает с async** - Исключения предоставляются через await()
4. **Устанавливайте на CoroutineScope** - Для обработки ошибок во всей области
5. **Комбинируйте с SupervisorJob** - Для независимого сбоя потомков
6. **Именуйте корутины** - Упрощает отладку
7. **Используйте для логирования/аналитики** - Отправляйте необработанные исключения в crash reporting
8. **Не игнорируйте ожидаемые ошибки** - Используйте явную обработку ошибок

---

## Follow-ups

1. How does CoroutineExceptionHandler interact with structured concurrency?
2. Can you install multiple CoroutineExceptionHandlers in a coroutine hierarchy?
3. How do you test that CEH is properly catching exceptions?
4. What happens if CEH itself throws an exception?
5. How does CEH work with custom CoroutineContext elements?
6. When should you use CEH vs Result/Either types for error handling?
7. How do you implement a global CEH for all coroutines in an Android app?

## References

- [Kotlin Coroutines Exception Handling](https://kotlinlang.org/docs/exception-handling.html)
- [CoroutineExceptionHandler Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-exception-handler/)
- [Exceptions in Coroutines](https://medium.com/androiddevelopers/exceptions-in-coroutines-ce8da1ec060c)

## Related Questions

- [[q-common-coroutine-mistakes--kotlin--medium|Common Kotlin coroutines mistakes]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging Kotlin coroutines]]
- [[q-suspend-cancellable-coroutine--kotlin--hard|Converting callbacks with suspendCancellableCoroutine]]

---
id: "20251012-180005"
title: "Flow completion with onCompletion operator / Завершение Flow с onCompletion оператором"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags:
  - kotlin
  - coroutines
  - flow
  - oncompletion
  - cleanup
  - lifecycle
  - operators
  - error-handling
moc: moc-kotlin
related: [q-kotlin-extension-functions--kotlin--medium, q-access-modifiers--programming-languages--medium, q-kotlin-type-system--kotlin--medium]
subtopics:
  - coroutines
  - flow
  - completion
  - cleanup
  - operators
---
# Flow completion with onCompletion operator

## English

### Question
What is the onCompletion operator in Kotlin Flow and how does it differ from finally blocks? How do you handle completion for success, exceptions, and cancellation cases? Provide production examples of cleanup, logging, UI state updates, and analytics with proper testing strategies.

### Answer

The **onCompletion** operator is called when a Flow completes, either successfully, exceptionally, or due to cancellation. It's the Flow equivalent of a `finally` block but with more control and better integration with Flow operators.

#### 1. Basic onCompletion Usage

**Simple completion notification:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

suspend fun basicOnCompletionExample() {
    flow {
        emit(1)
        emit(2)
        emit(3)
    }
        .onCompletion {
            println("Flow completed")
        }
        .collect { value ->
            println("Received: $value")
        }
}

// Output:
// Received: 1
// Received: 2
// Received: 3
// Flow completed
```

**onCompletion with cause parameter:**

```kotlin
suspend fun completionWithCauseExample() {
    flow {
        emit(1)
        emit(2)
        throw RuntimeException("Error occurred")
    }
        .onCompletion { cause ->
            when (cause) {
                null -> println("Completed successfully")
                is CancellationException -> println("Flow was cancelled")
                else -> println("Completed with exception: ${cause.message}")
            }
        }
        .catch { e ->
            println("Caught exception: ${e.message}")
        }
        .collect { value ->
            println("Received: $value")
        }
}

// Output:
// Received: 1
// Received: 2
// Completed with exception: Error occurred
// Caught exception: Error occurred
```

#### 2. Completion Scenarios

**Three completion cases:**

1. **Success (cause = null)**: Flow completed normally
2. **Exception (cause = Throwable)**: Flow threw an exception
3. **Cancellation (cause = CancellationException)**: Flow was cancelled

**Complete example showing all cases:**

```kotlin
enum class CompletionType {
    SUCCESS, ERROR, CANCELLATION
}

suspend fun demonstrateCompletionCases(type: CompletionType) {
    val job = CoroutineScope(Dispatchers.Default).launch {
        flow {
            emit(1)
            emit(2)

            when (type) {
                CompletionType.SUCCESS -> {
                    emit(3)
                    // Completes successfully
                }
                CompletionType.ERROR -> {
                    throw IllegalStateException("Simulated error")
                }
                CompletionType.CANCELLATION -> {
                    emit(3)
                    delay(Long.MAX_VALUE) // Will be cancelled
                }
            }
        }
            .onCompletion { cause ->
                when (cause) {
                    null -> println(" Completed successfully")
                    is CancellationException -> println(" Cancelled: ${cause.message}")
                    else -> println(" Failed: ${cause.message}")
                }
            }
            .catch { e ->
                println("Exception caught: ${e.message}")
            }
            .collect { value ->
                println("Value: $value")
            }
    }

    if (type == CompletionType.CANCELLATION) {
        delay(100)
        job.cancel("User cancelled")
    }

    job.join()
}

// Usage:
// demonstrateCompletionCases(CompletionType.SUCCESS)
// demonstrateCompletionCases(CompletionType.ERROR)
// demonstrateCompletionCases(CompletionType.CANCELLATION)
```

#### 3. onCompletion vs finally

**Comparison:**

```kotlin
// Using finally
suspend fun withFinally() {
    try {
        flow {
            emit(1)
            emit(2)
        }.collect { value ->
            println("Value: $value")
        }
    } finally {
        println("Finally block")
    }
}

// Using onCompletion
suspend fun withOnCompletion() {
    flow {
        emit(1)
        emit(2)
    }
        .onCompletion {
            println("onCompletion")
        }
        .collect { value ->
            println("Value: $value")
        }
}
```

**Key differences:**

| Aspect | finally | onCompletion |
|--------|---------|--------------|
| Scope | Around entire collect block | Part of Flow chain |
| Composability | Not composable | Composable operator |
| Exception info | Not available | Available via cause parameter |
| Placement | Outside Flow | Inside Flow chain |
| Can emit | No | No |
| Use case | Cleanup around collection | Cleanup as part of Flow |

**onCompletion placement matters:**

```kotlin
suspend fun placementMatters() {
    flow {
        emit(1)
        throw RuntimeException("Error in flow")
    }
        .onCompletion { cause ->
            // This sees the exception from upstream
            println("1. onCompletion before catch: cause = $cause")
        }
        .catch { e ->
            println("2. Caught: ${e.message}")
            emit(-1) // Recover
        }
        .onCompletion { cause ->
            // This sees null (successful completion after recovery)
            println("3. onCompletion after catch: cause = $cause")
        }
        .collect { value ->
            println("Collected: $value")
        }
}

// Output:
// Collected: 1
// 1. onCompletion before catch: cause = java.lang.RuntimeException: Error in flow
// 2. Caught: Error in flow
// Collected: -1
// 3. onCompletion after catch: cause = null
```

#### 4. Flow Lifecycle with onStart and onCompletion

**Complete Flow lifecycle:**

```kotlin
suspend fun flowLifecycle() {
    flow {
        println("Flow builder: Starting")
        emit(1)
        println("Flow builder: Emitted 1")
        delay(100)
        emit(2)
        println("Flow builder: Emitted 2")
    }
        .onStart {
            println("→ onStart: Flow is about to start")
        }
        .onEach { value ->
            println("  onEach: Processing $value")
        }
        .onCompletion { cause ->
            println("← onCompletion: Flow finished (cause: $cause)")
        }
        .collect { value ->
            println("  Collect: Received $value")
        }
}

// Output:
// → onStart: Flow is about to start
// Flow builder: Starting
// Flow builder: Emitted 1
//   onEach: Processing 1
//   Collect: Received 1
// Flow builder: Emitted 2
//   onEach: Processing 2
//   Collect: Received 2
// ← onCompletion: Flow finished (cause: null)
```

**Lifecycle diagram:**

```

   onStart    → Initialization

       
       

  emissions   → onEach → collect
   (loop)    

       
       

onCompletion  → Cleanup

```

#### 5. Production Example: Resource Cleanup

**Database connection cleanup:**

```kotlin
class DatabaseFlow(private val database: Database) {

    fun queryUsers(): Flow<User> = flow {
        val connection = database.openConnection()
        println("Database connection opened")

        try {
            val users = connection.query("SELECT * FROM users")
            users.forEach { user ->
                emit(user)
            }
        } finally {
            // This cleanup is in flow builder
            println("Flow builder cleanup")
        }
    }
        .onCompletion { cause ->
            // Additional cleanup after flow completes
            when (cause) {
                null -> {
                    println("Query completed successfully")
                    database.commitTransaction()
                }
                is CancellationException -> {
                    println("Query cancelled")
                    database.rollbackTransaction()
                }
                else -> {
                    println("Query failed: ${cause.message}")
                    database.rollbackTransaction()
                }
            }
        }
}

// Usage
suspend fun queryUsersExample() {
    val databaseFlow = DatabaseFlow(database)

    databaseFlow.queryUsers()
        .catch { e ->
            println("Error: ${e.message}")
        }
        .collect { user ->
            println("User: ${user.name}")
        }
}
```

**Network connection cleanup:**

```kotlin
class NetworkStream(private val webSocket: WebSocket) {

    fun observeMessages(): Flow<Message> = callbackFlow {
        val listener = object : WebSocketListener {
            override fun onMessage(message: Message) {
                trySend(message)
            }

            override fun onError(error: Throwable) {
                close(error)
            }
        }

        webSocket.addListener(listener)
        println("WebSocket listener added")

        awaitClose {
            webSocket.removeListener(listener)
            println("WebSocket listener removed (from awaitClose)")
        }
    }
        .onStart {
            println("Starting message observation")
        }
        .onCompletion { cause ->
            when (cause) {
                null -> println("Message stream completed normally")
                is CancellationException -> println("Message stream cancelled")
                else -> println("Message stream failed: ${cause.message}")
            }

            // Additional cleanup
            if (cause != null) {
                webSocket.reconnect()
            }
        }
}
```

#### 6. Production Example: Logging and Analytics

**Logging flow execution:**

```kotlin
class LoggingRepository(
    private val apiService: ApiService,
    private val logger: Logger
) {
    fun fetchData(userId: String): Flow<Data> = flow {
        val startTime = System.currentTimeMillis()
        logger.info("Fetching data for user: $userId")

        val data = apiService.getData(userId)
        emit(data)

        val duration = System.currentTimeMillis() - startTime
        logger.info("Data fetched in ${duration}ms")
    }
        .onStart {
            logger.debug("Flow started")
        }
        .onEach { data ->
            logger.debug("Emitted data: ${data.id}")
        }
        .onCompletion { cause ->
            when (cause) {
                null -> {
                    logger.info("Flow completed successfully")
                    analytics.logEvent("data_fetch_success", mapOf("userId" to userId))
                }
                is CancellationException -> {
                    logger.warn("Flow cancelled")
                    analytics.logEvent("data_fetch_cancelled", mapOf("userId" to userId))
                }
                else -> {
                    logger.error("Flow failed: ${cause.message}", cause)
                    analytics.logEvent(
                        "data_fetch_error",
                        mapOf(
                            "userId" to userId,
                            "error" to cause.message
                        )
                    )
                }
            }
        }
}
```

**Performance monitoring:**

```kotlin
fun <T> Flow<T>.withPerformanceMonitoring(
    operationName: String,
    logger: Logger
): Flow<T> {
    var startTime = 0L
    var itemCount = 0

    return this
        .onStart {
            startTime = System.currentTimeMillis()
            logger.info("[$operationName] Started")
        }
        .onEach {
            itemCount++
        }
        .onCompletion { cause ->
            val duration = System.currentTimeMillis() - startTime

            val status = when (cause) {
                null -> "SUCCESS"
                is CancellationException -> "CANCELLED"
                else -> "FAILED"
            }

            logger.info(
                "[$operationName] $status - " +
                "Duration: ${duration}ms, Items: $itemCount"
            )

            // Report metrics
            if (cause == null) {
                metricsService.recordTiming(operationName, duration)
                metricsService.recordCount("$operationName.items", itemCount)
            }
        }
}

// Usage
suspend fun monitoredDataFetch() {
    repository.fetchUsers()
        .withPerformanceMonitoring("fetch_users", logger)
        .collect { user ->
            println("User: ${user.name}")
        }
}
```

#### 7. Production Example: UI State Updates

**Loading state management:**

```kotlin
sealed class UiState<out T> {
    object Idle : UiState<Nothing>()
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<User>>(UiState.Idle)
    val uiState: StateFlow<UiState<User>> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            repository.getUser(userId)
                .onStart {
                    _uiState.value = UiState.Loading
                }
                .onCompletion { cause ->
                    // Reset to idle on completion (success or error handled elsewhere)
                    if (cause != null && cause !is CancellationException) {
                        _uiState.value = UiState.Error(
                            cause.message ?: "Unknown error"
                        )
                    }
                }
                .catch { e ->
                    // Error already set in onCompletion
                }
                .collect { user ->
                    _uiState.value = UiState.Success(user)
                }
        }
    }
}
```

**Progress tracking:**

```kotlin
class DownloadViewModel(private val downloader: Downloader) : ViewModel() {

    private val _downloadState = MutableStateFlow<DownloadState>(DownloadState.Idle)
    val downloadState: StateFlow<DownloadState> = _downloadState.asStateFlow()

    fun downloadFile(url: String) {
        viewModelScope.launch {
            downloader.download(url)
                .onStart {
                    _downloadState.value = DownloadState.InProgress(0)
                }
                .onEach { progress ->
                    _downloadState.value = DownloadState.InProgress(progress)
                }
                .onCompletion { cause ->
                    _downloadState.value = when (cause) {
                        null -> DownloadState.Completed
                        is CancellationException -> DownloadState.Cancelled
                        else -> DownloadState.Failed(cause.message ?: "Download failed")
                    }
                }
                .catch { }
                .collect()
        }
    }

    fun cancelDownload() {
        viewModelScope.coroutineContext.job.children.forEach { it.cancel() }
    }
}

sealed class DownloadState {
    object Idle : DownloadState()
    data class InProgress(val progress: Int) : DownloadState()
    object Completed : DownloadState()
    object Cancelled : DownloadState()
    data class Failed(val error: String) : DownloadState()
}
```

#### 8. Combining onCompletion with Error Handling

**Complete error handling pattern:**

```kotlin
suspend fun completeErrorHandlingExample() {
    flow {
        emit(1)
        emit(2)
        throw IOException("Network error")
    }
        .retry(2) { e ->
            e is IOException
        }
        .onCompletion { cause ->
            // Runs after all retries
            when (cause) {
                null -> println("Success after retries")
                is IOException -> println("Failed even after retries")
                else -> println("Other error: ${cause.message}")
            }
        }
        .catch { e ->
            println("Final catch: ${e.message}")
            emit(-1) // Emit fallback value
        }
        .collect { value ->
            println("Received: $value")
        }
}
```

**Declarative error handling:**

```kotlin
fun <T> Flow<T>.withErrorHandling(
    onSuccess: () -> Unit = {},
    onError: (Throwable) -> Unit = {},
    onCancelled: () -> Unit = {}
): Flow<T> = this
    .onCompletion { cause ->
        when (cause) {
            null -> onSuccess()
            is CancellationException -> onCancelled()
            else -> onError(cause)
        }
    }

// Usage
suspend fun declarativeErrorHandling() {
    repository.fetchData()
        .withErrorHandling(
            onSuccess = {
                println("Data fetch successful")
                showSuccessMessage()
            },
            onError = { e ->
                println("Data fetch failed: ${e.message}")
                showErrorMessage(e)
            },
            onCancelled = {
                println("Data fetch cancelled")
            }
        )
        .collect { data ->
            processData(data)
        }
}
```

#### 9. onCompletion Cannot Emit Values

**Important limitation:**

```kotlin
//  This does NOT work - onCompletion cannot emit
suspend fun cannotEmitInOnCompletion() {
    flow {
        emit(1)
        emit(2)
    }
        .onCompletion {
            // This will throw UnsupportedOperationException
            // emit(3) //  Cannot emit
        }
        .collect { value ->
            println("Value: $value")
        }
}

//  Use catch to emit recovery values
suspend fun emitInCatch() {
    flow {
        emit(1)
        emit(2)
        throw RuntimeException("Error")
    }
        .catch { e ->
            println("Error: ${e.message}")
            emit(-1) //  Can emit in catch
        }
        .onCompletion { cause ->
            println("Completed with cause: $cause")
        }
        .collect { value ->
            println("Value: $value")
        }
}
```

#### 10. Testing onCompletion

**Unit testing completion scenarios:**

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class OnCompletionTest {

    @Test
    fun `onCompletion called on success`() = runTest {
        var completionCalled = false
        var completionCause: Throwable? = null

        flow {
            emit(1)
            emit(2)
        }
            .onCompletion { cause ->
                completionCalled = true
                completionCause = cause
            }
            .collect()

        assertTrue(completionCalled)
        assertEquals(null, completionCause) // Success
    }

    @Test
    fun `onCompletion called on exception`() = runTest {
        var completionCause: Throwable? = null

        flow {
            emit(1)
            throw RuntimeException("Test error")
        }
            .onCompletion { cause ->
                completionCause = cause
            }
            .catch { }
            .collect()

        assertTrue(completionCause is RuntimeException)
        assertEquals("Test error", completionCause?.message)
    }

    @Test
    fun `onCompletion called on cancellation`() = runTest {
        var completionCause: Throwable? = null

        val job = launch {
            flow {
                emit(1)
                delay(1000)
                emit(2)
            }
                .onCompletion { cause ->
                    completionCause = cause
                }
                .collect()
        }

        advanceTimeBy(500)
        job.cancel()
        job.join()

        assertTrue(completionCause is CancellationException)
    }

    @Test
    fun `onCompletion order with catch`() = runTest {
        val events = mutableListOf<String>()

        flow {
            emit(1)
            throw RuntimeException("Error")
        }
            .onCompletion { cause ->
                events.add("onCompletion1: ${cause != null}")
            }
            .catch { e ->
                events.add("catch: ${e.message}")
            }
            .onCompletion { cause ->
                events.add("onCompletion2: ${cause != null}")
            }
            .collect { value ->
                events.add("collect: $value")
            }

        assertEquals(
            listOf(
                "collect: 1",
                "onCompletion1: true",
                "catch: Error",
                "onCompletion2: false"
            ),
            events
        )
    }
}
```

#### 11. Common Patterns and Best Practices

**Pattern: Resource management:**

```kotlin
fun <T> Flow<T>.withResource(
    acquire: () -> Resource,
    release: (Resource) -> Unit
): Flow<T> = flow {
    val resource = acquire()
    try {
        collect { value ->
            emit(value)
        }
    } finally {
        // Always cleanup in finally of flow builder
        release(resource)
    }
}.onCompletion { cause ->
    // Additional completion handling
    when (cause) {
        null -> println("Resource released after successful completion")
        else -> println("Resource released after failure: ${cause.message}")
    }
}
```

**Pattern: State machine:**

```kotlin
class StateMachine {
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state.asStateFlow()

    fun processData(): Flow<Data> = flow {
        _state.value = State.Processing
        // Emit data
    }
        .onCompletion { cause ->
            _state.value = when (cause) {
                null -> State.Success
                is CancellationException -> State.Cancelled
                else -> State.Error(cause.message ?: "Unknown")
            }
        }
}
```

**Best practices:**

| Do | Don't |
|----|-------|
| Use onCompletion for cleanup | Try to emit in onCompletion |
| Check cause parameter | Assume successful completion |
| Place onCompletion carefully in chain | Forget it only runs once |
| Combine with catch for error handling | Use as replacement for catch |
| Use for analytics/logging | Use for data transformation |

### Related Questions

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow

### Advanced (Harder)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies

## Follow-ups
1. What's the difference between onCompletion before and after a catch operator in a Flow chain?
2. Why can't onCompletion emit values? How is this different from catch?
3. How would you implement a Flow operator that guarantees cleanup even if the collector throws an exception?
4. Explain the order of execution: flow builder finally vs onCompletion. Which runs first?
5. How do you distinguish between normal cancellation and cancellation due to timeout in onCompletion?
6. When would you choose onCompletion over DisposableEffect in Jetpack Compose?
7. How would you implement retry logic that logs each attempt's completion status?

### References
- [Flow Completion](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/on-completion.html)
- [Flow Exception Handling](https://kotlinlang.org/docs/flow.html#flow-exceptions)
- [Flow Operators](https://kotlinlang.org/docs/flow.html#intermediate-flow-operators)
- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)

---

## Русский

### Вопрос
Что такое оператор onCompletion в Kotlin Flow и чем он отличается от блоков finally? Как обрабатывать завершение для успешных случаев, исключений и отмены? Приведите production примеры очистки, логирования, обновления UI состояния и аналитики с правильными стратегиями тестирования.

### Ответ

Оператор **onCompletion** вызывается когда Flow завершается, либо успешно, либо с исключением, либо из-за отмены. Это Flow эквивалент блока `finally`, но с большим контролем и лучшей интеграцией с операторами Flow.

#### 1. Базовое использование onCompletion

**Простое уведомление о завершении:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

suspend fun basicOnCompletionExample() {
    flow {
        emit(1)
        emit(2)
        emit(3)
    }
        .onCompletion {
            println("Flow завершен")
        }
        .collect { value ->
            println("Получено: $value")
        }
}

// Вывод:
// Получено: 1
// Получено: 2
// Получено: 3
// Flow завершен
```

**onCompletion с параметром cause:**

```kotlin
suspend fun completionWithCauseExample() {
    flow {
        emit(1)
        emit(2)
        throw RuntimeException("Произошла ошибка")
    }
        .onCompletion { cause ->
            when (cause) {
                null -> println("Завершено успешно")
                is CancellationException -> println("Flow был отменен")
                else -> println("Завершено с исключением: ${cause.message}")
            }
        }
        .catch { e ->
            println("Поймано исключение: ${e.message}")
        }
        .collect { value ->
            println("Получено: $value")
        }
}

// Вывод:
// Получено: 1
// Получено: 2
// Завершено с исключением: Произошла ошибка
// Поймано исключение: Произошла ошибка
```

#### 2. Сценарии завершения

**Три случая завершения:**

1. **Успех (cause = null)**: Flow завершился нормально
2. **Исключение (cause = Throwable)**: Flow выбросил исключение
3. **Отмена (cause = CancellationException)**: Flow был отменен

**Полный пример, показывающий все случаи:**

```kotlin
enum class CompletionType {
    SUCCESS, ERROR, CANCELLATION
}

suspend fun demonstrateCompletionCases(type: CompletionType) {
    val job = CoroutineScope(Dispatchers.Default).launch {
        flow {
            emit(1)
            emit(2)

            when (type) {
                CompletionType.SUCCESS -> {
                    emit(3)
                    // Завершается успешно
                }
                CompletionType.ERROR -> {
                    throw IllegalStateException("Симуляция ошибки")
                }
                CompletionType.CANCELLATION -> {
                    emit(3)
                    delay(Long.MAX_VALUE) // Будет отменен
                }
            }
        }
            .onCompletion { cause ->
                when (cause) {
                    null -> println("✓ Завершено успешно")
                    is CancellationException -> println("⚠ Отменено: ${cause.message}")
                    else -> println("✗ Ошибка: ${cause.message}")
                }
            }
            .catch { e ->
                println("Исключение поймано: ${e.message}")
            }
            .collect { value ->
                println("Значение: $value")
            }
    }

    if (type == CompletionType.CANCELLATION) {
        delay(100)
        job.cancel("Пользователь отменил")
    }

    job.join()
}
```

#### 3. onCompletion vs finally

**Сравнение:**

```kotlin
// Использование finally
suspend fun withFinally() {
    try {
        flow {
            emit(1)
            emit(2)
        }.collect { value ->
            println("Значение: $value")
        }
    } finally {
        println("Блок finally")
    }
}

// Использование onCompletion
suspend fun withOnCompletion() {
    flow {
        emit(1)
        emit(2)
    }
        .onCompletion {
            println("onCompletion")
        }
        .collect { value ->
            println("Значение: $value")
        }
}
```

**Ключевые различия:**

| Аспект | finally | onCompletion |
|--------|---------|--------------|
| Область | Вокруг всего блока collect | Часть цепочки Flow |
| Композируемость | Не композируемый | Композируемый оператор |
| Информация об исключении | Недоступна | Доступна через параметр cause |
| Размещение | Вне Flow | Внутри цепочки Flow |
| Может emit | Нет | Нет |
| Случай использования | Очистка вокруг collection | Очистка как часть Flow |

**Размещение onCompletion имеет значение:**

```kotlin
suspend fun placementMatters() {
    flow {
        emit(1)
        throw RuntimeException("Ошибка в flow")
    }
        .onCompletion { cause ->
            // Это видит исключение из upstream
            println("1. onCompletion до catch: cause = $cause")
        }
        .catch { e ->
            println("2. Поймано: ${e.message}")
            emit(-1) // Восстановление
        }
        .onCompletion { cause ->
            // Это видит null (успешное завершение после восстановления)
            println("3. onCompletion после catch: cause = $cause")
        }
        .collect { value ->
            println("Собрано: $value")
        }
}

// Вывод:
// Собрано: 1
// 1. onCompletion до catch: cause = java.lang.RuntimeException: Ошибка в flow
// 2. Поймано: Ошибка в flow
// Собрано: -1
// 3. onCompletion после catch: cause = null
```

#### 4. Жизненный цикл Flow с onStart и onCompletion

**Полный жизненный цикл Flow:**

```kotlin
suspend fun flowLifecycle() {
    flow {
        println("Flow builder: Начало")
        emit(1)
        println("Flow builder: Выпущено 1")
        delay(100)
        emit(2)
        println("Flow builder: Выпущено 2")
    }
        .onStart {
            println("→ onStart: Flow вот-вот начнется")
        }
        .onEach { value ->
            println("  onEach: Обработка $value")
        }
        .onCompletion { cause ->
            println("← onCompletion: Flow завершен (cause: $cause)")
        }
        .collect { value ->
            println("  Collect: Получено $value")
        }
}

// Вывод:
// → onStart: Flow вот-вот начнется
// Flow builder: Начало
// Flow builder: Выпущено 1
//   onEach: Обработка 1
//   Collect: Получено 1
// Flow builder: Выпущено 2
//   onEach: Обработка 2
//   Collect: Получено 2
// ← onCompletion: Flow завершен (cause: null)
```

#### 5. Production пример: Очистка ресурсов

**Очистка подключения к базе данных:**

```kotlin
class DatabaseFlow(private val database: Database) {

    fun queryUsers(): Flow<User> = flow {
        val connection = database.openConnection()
        println("Подключение к БД открыто")

        try {
            val users = connection.query("SELECT * FROM users")
            users.forEach { user ->
                emit(user)
            }
        } finally {
            // Эта очистка в flow builder
            println("Очистка flow builder")
        }
    }
        .onCompletion { cause ->
            // Дополнительная очистка после завершения flow
            when (cause) {
                null -> {
                    println("Запрос завершен успешно")
                    database.commitTransaction()
                }
                is CancellationException -> {
                    println("Запрос отменен")
                    database.rollbackTransaction()
                }
                else -> {
                    println("Запрос не удался: ${cause.message}")
                    database.rollbackTransaction()
                }
            }
        }
}

// Использование
suspend fun queryUsersExample() {
    val databaseFlow = DatabaseFlow(database)

    databaseFlow.queryUsers()
        .catch { e ->
            println("Ошибка: ${e.message}")
        }
        .collect { user ->
            println("Пользователь: ${user.name}")
        }
}
```

**Очистка сетевого подключения:**

```kotlin
class NetworkStream(private val webSocket: WebSocket) {

    fun observeMessages(): Flow<Message> = callbackFlow {
        val listener = object : WebSocketListener {
            override fun onMessage(message: Message) {
                trySend(message)
            }

            override fun onError(error: Throwable) {
                close(error)
            }
        }

        webSocket.addListener(listener)
        println("WebSocket listener добавлен")

        awaitClose {
            webSocket.removeListener(listener)
            println("WebSocket listener удален (из awaitClose)")
        }
    }
        .onStart {
            println("Начало наблюдения за сообщениями")
        }
        .onCompletion { cause ->
            when (cause) {
                null -> println("Поток сообщений завершен нормально")
                is CancellationException -> println("Поток сообщений отменен")
                else -> println("Поток сообщений не удался: ${cause.message}")
            }

            // Дополнительная очистка
            if (cause != null) {
                webSocket.reconnect()
            }
        }
}
```

#### 6. Production пример: Логирование и аналитика

**Логирование выполнения flow:**

```kotlin
class LoggingRepository(
    private val apiService: ApiService,
    private val logger: Logger
) {
    fun fetchData(userId: String): Flow<Data> = flow {
        val startTime = System.currentTimeMillis()
        logger.info("Получение данных для пользователя: $userId")

        val data = apiService.getData(userId)
        emit(data)

        val duration = System.currentTimeMillis() - startTime
        logger.info("Данные получены за ${duration}мс")
    }
        .onStart {
            logger.debug("Flow запущен")
        }
        .onEach { data ->
            logger.debug("Выпущены данные: ${data.id}")
        }
        .onCompletion { cause ->
            when (cause) {
                null -> {
                    logger.info("Flow завершен успешно")
                    analytics.logEvent("data_fetch_success", mapOf("userId" to userId))
                }
                is CancellationException -> {
                    logger.warn("Flow отменен")
                    analytics.logEvent("data_fetch_cancelled", mapOf("userId" to userId))
                }
                else -> {
                    logger.error("Flow не удался: ${cause.message}", cause)
                    analytics.logEvent(
                        "data_fetch_error",
                        mapOf(
                            "userId" to userId,
                            "error" to cause.message
                        )
                    )
                }
            }
        }
}
```

**Мониторинг производительности:**

```kotlin
fun <T> Flow<T>.withPerformanceMonitoring(
    operationName: String,
    logger: Logger
): Flow<T> {
    var startTime = 0L
    var itemCount = 0

    return this
        .onStart {
            startTime = System.currentTimeMillis()
            logger.info("[$operationName] Начало")
        }
        .onEach {
            itemCount++
        }
        .onCompletion { cause ->
            val duration = System.currentTimeMillis() - startTime

            val status = when (cause) {
                null -> "УСПЕХ"
                is CancellationException -> "ОТМЕНЕНО"
                else -> "ОШИБКА"
            }

            logger.info(
                "[$operationName] $status - " +
                "Длительность: ${duration}мс, Элементов: $itemCount"
            )

            // Отправка метрик
            if (cause == null) {
                metricsService.recordTiming(operationName, duration)
                metricsService.recordCount("$operationName.items", itemCount)
            }
        }
}

// Использование
suspend fun monitoredDataFetch() {
    repository.fetchUsers()
        .withPerformanceMonitoring("fetch_users", logger)
        .collect { user ->
            println("Пользователь: ${user.name}")
        }
}
```

#### 7. Production пример: Обновления состояния UI

**Управление состоянием загрузки:**

```kotlin
sealed class UiState<out T> {
    object Idle : UiState<Nothing>()
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<User>>(UiState.Idle)
    val uiState: StateFlow<UiState<User>> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            repository.getUser(userId)
                .onStart {
                    _uiState.value = UiState.Loading
                }
                .onCompletion { cause ->
                    // Сброс в idle при завершении (успех или ошибка обрабатываются отдельно)
                    if (cause != null && cause !is CancellationException) {
                        _uiState.value = UiState.Error(
                            cause.message ?: "Неизвестная ошибка"
                        )
                    }
                }
                .catch { e ->
                    // Ошибка уже установлена в onCompletion
                }
                .collect { user ->
                    _uiState.value = UiState.Success(user)
                }
        }
    }
}
```

**Отслеживание прогресса:**

```kotlin
class DownloadViewModel(private val downloader: Downloader) : ViewModel() {

    private val _downloadState = MutableStateFlow<DownloadState>(DownloadState.Idle)
    val downloadState: StateFlow<DownloadState> = _downloadState.asStateFlow()

    fun downloadFile(url: String) {
        viewModelScope.launch {
            downloader.download(url)
                .onStart {
                    _downloadState.value = DownloadState.InProgress(0)
                }
                .onEach { progress ->
                    _downloadState.value = DownloadState.InProgress(progress)
                }
                .onCompletion { cause ->
                    _downloadState.value = when (cause) {
                        null -> DownloadState.Completed
                        is CancellationException -> DownloadState.Cancelled
                        else -> DownloadState.Failed(cause.message ?: "Загрузка не удалась")
                    }
                }
                .catch { }
                .collect()
        }
    }

    fun cancelDownload() {
        viewModelScope.coroutineContext.job.children.forEach { it.cancel() }
    }
}

sealed class DownloadState {
    object Idle : DownloadState()
    data class InProgress(val progress: Int) : DownloadState()
    object Completed : DownloadState()
    object Cancelled : DownloadState()
    data class Failed(val error: String) : DownloadState()
}
```

#### 8. Комбинирование onCompletion с обработкой ошибок

**Полный паттерн обработки ошибок:**

```kotlin
suspend fun completeErrorHandlingExample() {
    flow {
        emit(1)
        emit(2)
        throw IOException("Ошибка сети")
    }
        .retry(2) { e ->
            e is IOException
        }
        .onCompletion { cause ->
            // Выполняется после всех повторов
            when (cause) {
                null -> println("Успех после повторов")
                is IOException -> println("Не удалось даже после повторов")
                else -> println("Другая ошибка: ${cause.message}")
            }
        }
        .catch { e ->
            println("Финальный catch: ${e.message}")
            emit(-1) // Выпуск fallback значения
        }
        .collect { value ->
            println("Получено: $value")
        }
}
```

**Декларативная обработка ошибок:**

```kotlin
fun <T> Flow<T>.withErrorHandling(
    onSuccess: () -> Unit = {},
    onError: (Throwable) -> Unit = {},
    onCancelled: () -> Unit = {}
): Flow<T> = this
    .onCompletion { cause ->
        when (cause) {
            null -> onSuccess()
            is CancellationException -> onCancelled()
            else -> onError(cause)
        }
    }

// Использование
suspend fun declarativeErrorHandling() {
    repository.fetchData()
        .withErrorHandling(
            onSuccess = {
                println("Получение данных успешно")
                showSuccessMessage()
            },
            onError = { e ->
                println("Получение данных не удалось: ${e.message}")
                showErrorMessage(e)
            },
            onCancelled = {
                println("Получение данных отменено")
            }
        )
        .collect { data ->
            processData(data)
        }
}
```

#### 9. onCompletion не может выпускать значения

**Важное ограничение:**

```kotlin
// ✗ Это НЕ работает - onCompletion не может emit
suspend fun cannotEmitInOnCompletion() {
    flow {
        emit(1)
        emit(2)
    }
        .onCompletion {
            // Это выбросит UnsupportedOperationException
            // emit(3) // ✗ Нельзя emit
        }
        .collect { value ->
            println("Значение: $value")
        }
}

// ✓ Используйте catch для выпуска восстановительных значений
suspend fun emitInCatch() {
    flow {
        emit(1)
        emit(2)
        throw RuntimeException("Ошибка")
    }
        .catch { e ->
            println("Ошибка: ${e.message}")
            emit(-1) // ✓ Можно emit в catch
        }
        .onCompletion { cause ->
            println("Завершено с cause: $cause")
        }
        .collect { value ->
            println("Значение: $value")
        }
}
```

#### 10. Тестирование onCompletion

**Unit-тестирование сценариев завершения:**

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class OnCompletionTest {

    @Test
    fun `onCompletion вызван при успехе`() = runTest {
        var completionCalled = false
        var completionCause: Throwable? = null

        flow {
            emit(1)
            emit(2)
        }
            .onCompletion { cause ->
                completionCalled = true
                completionCause = cause
            }
            .collect()

        assertTrue(completionCalled)
        assertEquals(null, completionCause) // Успех
    }

    @Test
    fun `onCompletion вызван при исключении`() = runTest {
        var completionCause: Throwable? = null

        flow {
            emit(1)
            throw RuntimeException("Тестовая ошибка")
        }
            .onCompletion { cause ->
                completionCause = cause
            }
            .catch { }
            .collect()

        assertTrue(completionCause is RuntimeException)
        assertEquals("Тестовая ошибка", completionCause?.message)
    }

    @Test
    fun `onCompletion вызван при отмене`() = runTest {
        var completionCause: Throwable? = null

        val job = launch {
            flow {
                emit(1)
                delay(1000)
                emit(2)
            }
                .onCompletion { cause ->
                    completionCause = cause
                }
                .collect()
        }

        advanceTimeBy(500)
        job.cancel()
        job.join()

        assertTrue(completionCause is CancellationException)
    }

    @Test
    fun `порядок onCompletion с catch`() = runTest {
        val events = mutableListOf<String>()

        flow {
            emit(1)
            throw RuntimeException("Ошибка")
        }
            .onCompletion { cause ->
                events.add("onCompletion1: ${cause != null}")
            }
            .catch { e ->
                events.add("catch: ${e.message}")
            }
            .onCompletion { cause ->
                events.add("onCompletion2: ${cause != null}")
            }
            .collect { value ->
                events.add("collect: $value")
            }

        assertEquals(
            listOf(
                "collect: 1",
                "onCompletion1: true",
                "catch: Ошибка",
                "onCompletion2: false"
            ),
            events
        )
    }
}
```

#### 11. Общие паттерны и лучшие практики

**Паттерн: Управление ресурсами:**

```kotlin
fun <T> Flow<T>.withResource(
    acquire: () -> Resource,
    release: (Resource) -> Unit
): Flow<T> = flow {
    val resource = acquire()
    try {
        collect { value ->
            emit(value)
        }
    } finally {
        // Всегда очистка в finally flow builder
        release(resource)
    }
}.onCompletion { cause ->
    // Дополнительная обработка завершения
    when (cause) {
        null -> println("Ресурс освобожден после успешного завершения")
        else -> println("Ресурс освобожден после ошибки: ${cause.message}")
    }
}
```

**Паттерн: Конечный автомат:**

```kotlin
class StateMachine {
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state.asStateFlow()

    fun processData(): Flow<Data> = flow {
        _state.value = State.Processing
        // Выпуск данных
    }
        .onCompletion { cause ->
            _state.value = when (cause) {
                null -> State.Success
                is CancellationException -> State.Cancelled
                else -> State.Error(cause.message ?: "Неизвестно")
            }
        }
}
```

**Лучшие практики:**

| Делать | Не делать |
|----|-------|
| Использовать onCompletion для очистки | Пытаться emit в onCompletion |
| Проверять параметр cause | Предполагать успешное завершение |
| Размещать onCompletion тщательно в цепочке | Забывать, что он выполняется только один раз |
| Комбинировать с catch для обработки ошибок | Использовать как замену catch |
| Использовать для аналитики/логирования | Использовать для трансформации данных |

### Связанные вопросы
- [[q-flow-operators--kotlin--medium]] - Операторы Flow
- [[q-flow-exception-handling--kotlin--medium]] - Обработка исключений в Flow
- [[q-flow-basics--kotlin--easy]] - Основы Flow
- [[q-structured-concurrency--kotlin--hard]] - Структурированная конкурентность

### Дополнительные вопросы
1. В чем разница между onCompletion до и после оператора catch в цепочке Flow?
2. Почему onCompletion не может emit значения? Чем это отличается от catch?
3. Как реализовать Flow оператор, который гарантирует cleanup даже если collector бросает исключение?
4. Объясните порядок выполнения: finally блок в flow builder vs onCompletion. Что выполняется первым?
5. Как различить обычную отмену и отмену из-за timeout в onCompletion?
6. Когда выбрать onCompletion вместо DisposableEffect в Jetpack Compose?
7. Как реализовать retry логику, которая логирует статус завершения каждой попытки?

### Ссылки
- [Flow Completion](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/on-completion.html)
- [Обработка исключений Flow](https://kotlinlang.org/docs/flow.html#flow-exceptions)
- [Операторы Flow](https://kotlinlang.org/docs/flow.html#intermediate-flow-operators)
- [Документация Kotlin Flow](https://kotlinlang.org/docs/flow.html)

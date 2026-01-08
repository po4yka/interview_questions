---\
id: kotlin-148
title: "Flow completion with onCompletion operator / Завершение Flow с onCompletion оператором"
aliases: [Completion, Flow, onCompletion]
topic: kotlin
subtopics: [c-coroutines, c-flow, c-kotlin]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, q-kotlin-extension-functions--kotlin--medium, q-kotlin-type-system--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium]
---\
# Вопрос (RU)
Что такое оператор `onCompletion` в `Kotlin Flow` и чем он отличается от блоков `finally`? Как обрабатывать завершение для успешных случаев, исключений и отмены? Приведите production-примеры очистки, логирования, обновления UI-состояния и аналитики с корректными стратегиями тестирования.

# Question (EN)
What is the `onCompletion` operator in `Kotlin Flow` and how does it differ from `finally` blocks? How do you handle completion for success, exceptions, and cancellation cases? Provide production examples of cleanup, logging, UI state updates, and analytics with proper testing strategies.

## Ответ (RU)

Оператор `onCompletion` регистрирует действие, которое вызывается при завершении сборки `Flow` — при успешном завершении, с исключением или из-за отмены. Он похож по идее на блок `finally`, но:
- выполняется как часть цепочки операторов `Flow`;
- получает причину завершения через параметр `cause`;
- вызывается один раз на каждый запуск коллекции.

#### 1. Базовое Использование onCompletion

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

#### 2. Сценарии Завершения

**Три случая завершения:**

1. **Успех (cause = null)**: `Flow` завершился нормально
2. **Исключение (cause = Throwable)**: `Flow` выбросил исключение, не обработанное до этого `onCompletion`
3. **Отмена (cause = CancellationException)**: `Flow` был отменен

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
                    null -> println("Завершено успешно")
                    is CancellationException -> println("Отменено: ${cause.message}")
                    else -> println("Ошибка: ${cause.message}")
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

#### 3. onCompletion Vs Finally

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
| Область | Вокруг всего блока collect | Часть цепочки `Flow` |
| Композируемость | Не оператор `Flow` | Композируемый оператор |
| Информация об исключении | Не передается | Доступна через параметр cause |
| Размещение | Вне `Flow` | Внутри цепочки `Flow` |
| Может emit | Нет | Нет |
| Сценарий | Очистка вокруг области коллекции | Очистка/побочные эффекты как часть `Flow` |

**Размещение onCompletion имеет значение:**

```kotlin
suspend fun placementMatters() {
    flow {
        emit(1)
        throw RuntimeException("Ошибка в flow")
    }
        .onCompletion { cause ->
            // Видит исключение из upstream, т.к. стоит до catch
            println("1. onCompletion до catch: cause = $cause")
        }
        .catch { e ->
            println("2. Поймано: ${e.message}")
            emit(-1) // Восстановление
        }
        .onCompletion { cause ->
            // Видит null (успешное завершение после восстановления)
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

#### 4. Жизненный Цикл Flow С onStart И onCompletion

**Полный жизненный цикл `Flow`:**

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

#### 5. Production-пример: Очистка Ресурсов

Внешние зависимости (например, `Database`) считаются внедренными.

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
            println("Очистка flow builder")
            connection.close()
        }
    }
        .onCompletion { cause ->
            // Дополнительная обработка после завершения flow
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
suspend fun queryUsersExample(database: Database) {
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
class NetworkStream(
    private val webSocket: WebSocket,
    private val reconnectOnError: (Throwable) -> Unit
) {

    fun observeMessages(): Flow<Message> = callbackFlow {
        val listener = object : WebSocketListener {
            override fun onMessage(message: Message) {
                trySend(message).isSuccess
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
                else -> {
                    println("Поток сообщений не удался: ${cause.message}")
                    reconnectOnError(cause)
                }
            }
        }
}
```

#### 6. Production-пример: Логирование И Аналитика

```kotlin
class LoggingRepository(
    private val apiService: ApiService,
    private val logger: Logger,
    private val analytics: Analytics
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
                            "error" to (cause.message ?: "unknown")
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
    logger: Logger,
    metricsService: MetricsService
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

            metricsService.recordTiming(operationName, duration)
            metricsService.recordCount("$operationName.items", itemCount)
        }
}

// Использование
suspend fun monitoredDataFetch(
    repository: UserRepository,
    logger: Logger,
    metricsService: MetricsService
) {
    repository.fetchUsers()
        .withPerformanceMonitoring("fetch_users", logger, metricsService)
        .collect { user ->
            println("Пользователь: ${user.name}")
        }
}
```

#### 7. Production-пример: Обновления Состояния UI

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
                .catch { e ->
                    _uiState.value = UiState.Error(e.message ?: "Неизвестная ошибка")
                }
                .onCompletion { cause ->
                    if (cause is CancellationException) {
                        _uiState.value = UiState.Idle
                    }
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
                .catch { e ->
                    _downloadState.value = DownloadState.Failed(e.message ?: "Загрузка не удалась")
                }
                .collect()
        }
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

#### 8. Комбинирование onCompletion С Обработкой Ошибок

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
            // Вызывается после всех попыток
            when (cause) {
                null -> println("Успех после повторов")
                is IOException -> println("Не удалось даже после повторов")
                else -> println("Другая ошибка: ${cause.message}")
            }
        }
        .catch { e ->
            println("Финальный catch: ${e.message}")
            emit(-1)
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
suspend fun declarativeErrorHandling(repository: Repository) {
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

#### 9. onCompletion Не Может Выпускать Значения

```kotlin
// Это НЕ работает - onCompletion не может emit
suspend fun cannotEmitInOnCompletion() {
    flow {
        emit(1)
        emit(2)
    }
        .onCompletion {
            // emit(3) // UnsupportedOperationException: нельзя emit из onCompletion
        }
        .collect { value ->
            println("Значение: $value")
        }
}

// Используйте catch для выпуска восстановительных значений
suspend fun emitInCatch() {
    flow {
        emit(1)
        emit(2)
        throw RuntimeException("Ошибка")
    }
        .catch { e ->
            println("Ошибка: ${e.message}")
            emit(-1) // Можно emit в catch
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

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
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
                emit(-1)
            }
            .onCompletion { cause ->
                events.add("onCompletion2: ${cause != null}")
            }
            .collect { value ->
                events.add("collect: $value")
            }

        assertEquals(
            listOf(
                "onCompletion1: true",   // upstream видит ошибку
                "catch: Ошибка",
                "collect: -1",
                "onCompletion2: false"   // downstream после восстановления
            ),
            events
        )
    }
}
```

#### 11. Общие Паттерны И Лучшие Практики

**Паттерн: управление ресурсами:**

```kotlin
fun <T> Flow<T>.withResource(
    acquire: () -> Resource,
    release: (Resource) -> Unit
): Flow<T> = flow {
    val resource = acquire()
    try {
        this@withResource.collect { value ->
            emit(value)
        }
    } finally {
        release(resource)
    }
}
```

При необходимости дополнительные действия при завершении можно навесить через `onCompletion` поверх этого оператора.

**Паттерн: конечный автомат:**

```kotlin
class StateMachine {
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state.asStateFlow()

    fun processData(upstream: Flow<Data>): Flow<Data> = upstream
        .onStart {
            _state.value = State.Processing
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
| Использовать onCompletion для очистки и побочных эффектов | Пытаться emit в onCompletion |
| Проверять параметр cause | Предполагать всегда успешное завершение |
| Внимательно выбирать место onCompletion в цепочке | Забывать, что он вызывается один раз на коллекцию |
| Комбинировать с catch для обработки ошибок | Использовать как замену catch |
| Использовать для аналитики/логирования/метрик | Использовать для трансформации данных |

### Связанные Вопросы (RU)
- [[q-flow-operators--kotlin--medium]] - Операторы `Flow`
- [[q-flow-exception-handling--kotlin--medium]] - Обработка исключений в `Flow`
- [[q-flow-basics--kotlin--easy]] - Основы `Flow`
- [[q-structured-concurrency--kotlin--hard]] - Структурированная конкурентность

### Дополнительные Вопросы (RU)
1. В чем разница между onCompletion до и после оператора catch в цепочке `Flow`?
2. Почему onCompletion не может emit значения? Чем это отличается от catch?
3. Как реализовать `Flow`-оператор, который гарантирует очистку даже если collector бросает исключение?
4. Объясните порядок выполнения: finally в flow builder vs onCompletion. Что выполняется первым?
5. Как различить обычную отмену и отмену из-за timeout в onCompletion?
6. Когда выбрать onCompletion вместо DisposableEffect в Jetpack Compose?
7. Как реализовать retry-логику, которая логирует статус завершения каждой попытки?

### Ссылки (RU)
- [Flow Completion](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/on-completion.html)
- [Обработка исключений Flow](https://kotlinlang.org/docs/flow.html#flow-exceptions)
- [Операторы Flow](https://kotlinlang.org/docs/flow.html#intermediate-flow-operators)
- [Документация Kotlin Flow](https://kotlinlang.org/docs/flow.html)

## Answer (EN)

The `onCompletion` operator registers an action that is invoked when a `Flow` collection completes — whether successfully, with an exception, or due to cancellation. It is similar in spirit to a `finally` block but:
- executes as part of the `Flow` operator chain,
- can observe the completion cause via the `cause` parameter,
- runs once per collection.

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

1. **Success (cause = null)**: `Flow` completed normally
2. **Exception (cause = Throwable)**: `Flow` threw an exception that was not handled upstream of this `onCompletion`
3. **Cancellation (cause = CancellationException)**: `Flow` was cancelled

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
                    null -> println("Completed successfully")
                    is CancellationException -> println("Cancelled: ${cause.message}")
                    else -> println("Failed: ${cause.message}")
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

#### 3. onCompletion Vs Finally

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
| Scope | Around entire collect block | Part of `Flow` chain |
| Composability | Not composable as `Flow` operator | Composable operator |
| Exception info | Not passed in | Available via cause parameter |
| Placement | Outside `Flow` | Inside `Flow` chain |
| Can emit | No | No |
| Use case | Cleanup around collection scope | Cleanup/side effects as part of `Flow` |

**onCompletion placement matters:**

```kotlin
suspend fun placementMatters() {
    flow {
        emit(1)
        throw RuntimeException("Error in flow")
    }
        .onCompletion { cause ->
            // Sees the exception from upstream, because it is before catch
            println("1. onCompletion before catch: cause = $cause")
        }
        .catch { e ->
            println("2. Caught: ${e.message}")
            emit(-1) // Recover
        }
        .onCompletion { cause ->
            // Sees null (successful completion after recovery)
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

**Complete `Flow` lifecycle:**

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

#### 5. Production Example: Resource Cleanup

Note: External collaborators (e.g., `Database`) are assumed to be injected/available in scope.

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
            println("Flow builder cleanup")
            connection.close()
        }
    }
        .onCompletion { cause ->
            // Additional completion handling after flow completes
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
suspend fun queryUsersExample(database: Database) {
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
class NetworkStream(
    private val webSocket: WebSocket,
    private val reconnectOnError: (Throwable) -> Unit
) {

    fun observeMessages(): Flow<Message> = callbackFlow {
        val listener = object : WebSocketListener {
            override fun onMessage(message: Message) {
                trySend(message).isSuccess
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
                else -> {
                    println("Message stream failed: ${cause.message}")
                    reconnectOnError(cause)
                }
            }
        }
}
```

#### 6. Production Example: Logging and Analytics

```kotlin
class LoggingRepository(
    private val apiService: ApiService,
    private val logger: Logger,
    private val analytics: Analytics
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
                            "error" to (cause.message ?: "unknown")
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
    logger: Logger,
    metricsService: MetricsService
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

            // Report metrics for all outcomes if desired
            metricsService.recordTiming(operationName, duration)
            metricsService.recordCount("$operationName.items", itemCount)
        }
}

// Usage
suspend fun monitoredDataFetch(
    repository: UserRepository,
    logger: Logger,
    metricsService: MetricsService
) {
    repository.fetchUsers()
        .withPerformanceMonitoring("fetch_users", logger, metricsService)
        .collect { user ->
            println("User: ${user.name}")
        }
}
```

#### 7. Production Example: UI State Updates

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
                .catch { e ->
                    _uiState.value = UiState.Error(e.message ?: "Unknown error")
                }
                .onCompletion { cause ->
                    if (cause is CancellationException) {
                        _uiState.value = UiState.Idle
                    }
                }
                .collect { user ->
                    _uiState.value = UiState.Success(user)
                }
        }
    }
}
```

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
                .catch { e ->
                    _downloadState.value = DownloadState.Failed(e.message ?: "Download failed")
                }
                .collect()
        }
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
suspend fun declarativeErrorHandling(repository: Repository) {
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

```kotlin
// This does NOT work - onCompletion cannot emit
suspend fun cannotEmitInOnCompletion() {
    flow {
        emit(1)
        emit(2)
    }
        .onCompletion {
            // emit(3) // UnsupportedOperationException: emission from onCompletion is not allowed
        }
        .collect { value ->
            println("Value: $value")
        }
}

// Use catch to emit recovery values
suspend fun emitInCatch() {
    flow {
        emit(1)
        emit(2)
        throw RuntimeException("Error")
    }
        .catch { e ->
            println("Error: ${e.message}")
            emit(-1) // Can emit in catch
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

```kotlin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
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
                emit(-1)
            }
            .onCompletion { cause ->
                events.add("onCompletion2: ${cause != null}")
            }
            .collect { value ->
                events.add("collect: $value")
            }

        assertEquals(
            listOf(
                "onCompletion1: true",   // upstream failure observed
                "catch: Error",
                "collect: -1",
                "onCompletion2: false"   // downstream completion after recovery
            ),
            events
        )
    }
}
```

#### 11. Common Patterns and Best Practices

```kotlin
fun <T> Flow<T>.withResource(
    acquire: () -> Resource,
    release: (Resource) -> Unit
): Flow<T> = flow {
    val resource = acquire()
    try {
        // Use the original flow as a source
        this@withResource.collect { value ->
            emit(value)
        }
    } finally {
        release(resource)
    }
}
```

```kotlin
class StateMachine {
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state.asStateFlow()

    fun processData(upstream: Flow<Data>): Flow<Data> = upstream
        .onStart {
            _state.value = State.Processing
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
| Use onCompletion for cleanup and side effects | Try to emit in onCompletion |
| Check cause parameter | Assume successful completion |
| Place onCompletion carefully in chain | Forget it only runs once per collection |
| Combine with catch for error handling | Use as replacement for catch |
| Use for analytics/logging/metrics | Use for data transformation |

### Related Questions (EN)

- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs `Flow`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies

## Follow-ups (EN)
1. What's the difference between onCompletion before and after a catch operator in a `Flow` chain?
2. Why can't onCompletion emit values? How is this different from catch?
3. How would you implement a `Flow` operator that guarantees cleanup even if the collector throws an exception?
4. Explain the order of execution: flow builder finally vs onCompletion. Which runs first?
5. How do you distinguish between normal cancellation and cancellation due to timeout in onCompletion?
6. When would you choose onCompletion over DisposableEffect in Jetpack Compose?
7. How would you implement retry logic that logs each attempt's completion status?

### References (EN)
- [Flow Completion](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/on-completion.html)
- [Flow Exception Handling](https://kotlinlang.org/docs/flow.html#flow-exceptions)
- [Flow Operators](https://kotlinlang.org/docs/flow.html#intermediate-flow-operators)
- [Kotlin `Flow` Documentation](https://kotlinlang.org/docs/flow.html)

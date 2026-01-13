---
anki_cards:
- slug: q-testing-coroutine-timing-control--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-testing-coroutine-timing-control--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-093
title: "Тестирование тайминга корутин: advanceTimeBy vs advanceUntilIdle / Testing coroutine timing: advanceTimeBy vs advanceUntilIdle"
aliases: [Coroutine Testing, Testing Timing, Virtual Time]
topic: kotlin
subtopics: [coroutines, testing]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-testing, q-structured-concurrency-violations--kotlin--hard]
created: 2025-10-12
updated: 2025-11-09
tags: [coroutines, deterministic, difficulty/medium, kotlin, runtest, test-dispatcher, testing, timing, virtual-time]

---\
# Вопрос (RU)

> Как детерминированно тестировать тайминги корутин в Kotlin с помощью виртуального времени (`runTest`, `TestScope`, `TestDispatcher`, `advanceTimeBy`, `advanceUntilIdle`, `runCurrent`, `currentTime`), и как правильно использовать эти примитивы для проверки задержек, тайм-аутов, периодических операций, `Flow` и `ViewModel`?

# Question (EN)

> How can you deterministically test coroutine timing in Kotlin using virtual time (`runTest`, `TestScope`, `TestDispatcher`, `advanceTimeBy`, `advanceUntilIdle`, `runCurrent`, `currentTime`), and how should these primitives be used to verify delays, timeouts, periodic operations, `Flow`, and `ViewModel` behavior?

## Ответ (RU)

Тестирование кода с корутинами, зависящего от времени, без виртуального времени требует реальных задержек, делает тесты медленными и недетерминированными. Модуль `kotlinx-coroutines-test` предоставляет виртуальное время через `TestScope` и `TestDispatcher`, позволяя мгновенно и предсказуемо выполнять отложенные операции и проверять тайминг.

Все примеры ниже соответствуют поведению `kotlinx-coroutines-test` 1.6+: виртуальное время управляется планировщиком тестового диспетчера и меняется, когда вы явно двигаете его через `advanceTimeBy`, `advanceUntilIdle`, `runCurrent` или когда `runTest` внутри себя продвигает время при выполнении запланированных задач. Сам по себе `delay` не вызывает реального ожидания.

### Концепция Виртуального Времени

Виртуальное время позволяет "перематывать" ход времени без реального ожидания. `delay(1000)` лишь планирует продолжение на времени 1000; пока вы не продвинете виртуальное время (или оно не будет продвинуто планировщиком через тестовые примитивы), корутина не продолжит выполнение.

#### Реальное Vs Виртуальное Время

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.system.measureTimeMillis
import kotlin.test.*

class VirtualTimeDemo {
    @Test
    fun realTimeTest() {
        val elapsed = measureTimeMillis {
            runBlocking {
                delay(1000) // Реально ждём ~1 секунду
            }
        }
        println("Real time test took: ${elapsed}ms")
        assertTrue(elapsed >= 1000)
    }

    @Test
    fun virtualTimeTest() = runTest {
        val elapsed = measureTimeMillis {
            delay(1000) // Виртуальное ожидание, реальное время не тратится
        }
        println("Measured block took: ${elapsed}ms")
        assertTrue(elapsed < 100) // Сам тест быстрый

        // Продолжение запланировано на 1000мс, но currentTime всё ещё 0 до ручного продвижения
        assertEquals(0, currentTime)

        // Явно двигаем виртуальное время, чтобы завершить delay
        advanceTimeBy(1000)
        assertEquals(1000, currentTime)
    }
}
```

### TestScope И TestDispatcher

`runTest` создаёт `TestScope` с `TestDispatcher`, который управляет виртуальным временем.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class TestScopeBasics {
    @Test
    fun testScopeExample() = runTest {
        // Это TestScope
        println("Is TestScope: ${this is TestScope}") // true

        // currentTime начинается с 0
        println("Initial time: $currentTime") // 0

        delay(100)
        // delay планирует продолжение на 100, двигаем время явно
        advanceTimeBy(100)
        println("After delay(100): $currentTime") // 100

        delay(500)
        advanceTimeBy(500)
        println("After delay(500): $currentTime") // 600
    }

    @Test
    fun testDispatcherExample() = runTest {
        val dispatcher = coroutineContext[CoroutineDispatcher]
        println("Dispatcher type: ${dispatcher?.javaClass?.simpleName}")
        // Обычно StandardTestDispatcher
    }
}
```

### `advanceTimeBy(delayMillis)` — Точное Продвижение Времени

`advanceTimeBy(millis)` продвигает виртуальное время ровно на указанное значение и выполняет все задачи, срок которых наступил до или в этот момент.

#### Базовое Использование

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class AdvanceTimeByBasics {
    @Test
    fun basicAdvanceTimeBy() = runTest {
        var completed = false

        launch {
            delay(1000)
            completed = true
        }

        // Пока не выполнено
        assertFalse(completed)
        assertEquals(0, currentTime)

        // Продвигаем на 500мс — ещё рано
        advanceTimeBy(500)
        assertFalse(completed)
        assertEquals(500, currentTime)

        // Ещё 500мс — теперь завершилось
        advanceTimeBy(500)
        assertTrue(completed)
        assertEquals(1000, currentTime)
    }

    @Test
    fun multipleDelaysWithAdvanceTimeBy() = runTest {
        val results = mutableListOf<String>()

        launch {
            delay(100)
            results.add("Task A")
        }

        launch {
            delay(200)
            results.add("Task B")
        }

        launch {
            delay(300)
            results.add("Task C")
        }

        // До 150мс — только A
        advanceTimeBy(150)
        assertEquals(listOf("Task A"), results)
        assertEquals(150, currentTime)

        // До 250мс — добавится B
        advanceTimeBy(100)
        assertEquals(listOf("Task A", "Task B"), results)
        assertEquals(250, currentTime)

        // До 350мс — добавится C
        advanceTimeBy(100)
        assertEquals(listOf("Task A", "Task B", "Task C"), results)
        assertEquals(350, currentTime)
    }
}
```

#### Пример Точного Контроля

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class PreciseTimingControl {
    @Test
    fun testDebounce() = runTest {
        val events = mutableListOf<String>()

        // Условный debounce
        suspend fun debounceProcess(value: String) {
            delay(300) // debounce-задержка
            events.add(value)
        }

        var debouncedJob: Job? = null

        fun submitEvent(value: String) {
            debouncedJob?.cancel()
            debouncedJob = backgroundScope.launch {
                debounceProcess(value)
            }
        }

        submitEvent("Event1")
        advanceTimeBy(100)
        assertTrue(events.isEmpty())

        submitEvent("Event2")
        advanceTimeBy(100)
        assertTrue(events.isEmpty())

        submitEvent("Event3")
        advanceTimeBy(300)

        advanceUntilIdle()
        assertEquals(listOf("Event3"), events)
    }

    @Test
    fun testRateLimiting() = runTest {
        val timestamps = mutableListOf<Long>()

        suspend fun rateLimitedOperation() {
            timestamps.add(currentTime)
            delay(1000) // лимит: 1 операция в секунду
        }

        repeat(3) {
            rateLimitedOperation()
            advanceTimeBy(1000)
        }

        // 0, 1000, 2000
        assertEquals(listOf(0L, 1000L, 2000L), timestamps)
    }
}
```

### `advanceUntilIdle()` — Выполнение Всей Отложенной Работы

`advanceUntilIdle()` многократно выполняет задачи и продвигает виртуальное время к следующему событию, пока не останется задач. Не эквивалентен `advanceTimeBy(``Long``.MAX_VALUE)` при бесконечной генерации работы.

#### Базовое Использование

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class AdvanceUntilIdleBasics {
    @Test
    fun basicAdvanceUntilIdle() = runTest {
        val results = mutableListOf<String>()

        launch {
            delay(100)
            results.add("Task A")
        }

        launch {
            delay(500)
            results.add("Task B")
        }

        launch {
            delay(1000)
            results.add("Task C")
        }

        advanceUntilIdle()

        assertEquals(listOf("Task A", "Task B", "Task C"), results)
        assertEquals(1000, currentTime)
    }

    @Test
    fun chainedDelays() = runTest {
        val results = mutableListOf<Int>()

        launch {
            repeat(5) { i ->
                delay(100)
                results.add(i)
            }
        }

        advanceUntilIdle()

        assertEquals(listOf(0, 1, 2, 3, 4), results)
        assertEquals(500, currentTime)
    }
}
```

#### Пример С Динамической Работой

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class DynamicWorkTesting {
    @Test
    fun testRecursiveScheduling() = runTest {
        val events = mutableListOf<String>()

        fun scheduleWork(depth: Int) {
            if (depth > 0) {
                backgroundScope.launch {
                    delay(100)
                    events.add("Depth $depth")
                    scheduleWork(depth - 1)
                }
            }
        }

        scheduleWork(3)

        // advanceUntilIdle выполнит всю конечную цепочку
        advanceUntilIdle()

        assertEquals(listOf("Depth 3", "Depth 2", "Depth 1"), events)
        assertEquals(300, currentTime)
    }

    @Test
    fun testProducerConsumerComplete() = runTest {
        val channel = Channel<Int>(capacity = 10)
        val received = mutableListOf<Int>()

        launch {
            repeat(5) { i ->
                delay(100)
                channel.send(i)
            }
            channel.close()
        }

        launch {
            for (value in channel) {
                delay(50)
                received.add(value)
            }
        }

        advanceUntilIdle()

        assertEquals(listOf(0, 1, 2, 3, 4), received)
    }
}
```

### `runCurrent()` — Только Задачи На Текущем Времени

`runCurrent()` выполняет задачи, запланированные на текущее `currentTime`, не продвигая время.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class RunCurrentBasics {
    @Test
    fun basicRunCurrent() = runTest {
        val results = mutableListOf<String>()

        launch {
            results.add("Immediate")
        }

        launch {
            delay(100)
            results.add("Delayed")
        }

        runCurrent()

        assertEquals(listOf("Immediate"), results)
        assertEquals(0, currentTime)

        advanceTimeBy(100)
        assertEquals(listOf("Immediate", "Delayed"), results)
    }

    @Test
    fun multipleRunCurrentCalls() = runTest {
        val results = mutableListOf<String>()

        launch { results.add("Task 1") }
        launch { results.add("Task 2") }

        runCurrent()
        assertEquals(listOf("Task 1", "Task 2"), results)

        launch { results.add("Task 3") }

        runCurrent()
        assertEquals(listOf("Task 1", "Task 2", "Task 3"), results)
        assertEquals(0, currentTime)
    }
}
```

### `currentTime` — Счётчик Виртуального Времени

`currentTime` возвращает текущее виртуальное время тестового диспетчера в миллисекундах.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class CurrentTimeUsage {
    @Test
    fun trackingTime() = runTest {
        assertEquals(0, currentTime)

        launch { delay(100) }
        advanceTimeBy(100)
        assertEquals(100, currentTime)

        advanceTimeBy(500)
        assertEquals(600, currentTime)
    }

    @Test
    fun timestampingEvents() = runTest {
        data class Event(val name: String, val timestamp: Long)

        val events = mutableListOf<Event>()

        launch {
            delay(100)
            events.add(Event("Event 1", currentTime))

            delay(200)
            events.add(Event("Event 2", currentTime))

            delay(300)
            events.add(Event("Event 3", currentTime))
        }

        advanceUntilIdle()

        assertEquals(100, events[0].timestamp)
        assertEquals(300, events[1].timestamp)
        assertEquals(600, events[2].timestamp)
    }
}
```

### Тестирование Операций `delay()`

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class DelayTesting {
    @Test
    fun simpleDelay() = runTest {
        var executed = false

        launch {
            delay(1000)
            executed = true
        }

        assertFalse(executed)

        advanceTimeBy(999)
        assertFalse(executed)

        advanceTimeBy(1)
        assertTrue(executed)
    }

    @Test
    fun multipleDelaysInSequence() = runTest {
        val results = mutableListOf<Int>()

        launch {
            repeat(5) { i ->
                delay(100)
                results.add(i)
            }
        }

        repeat(5) { i ->
            advanceTimeBy(100)
            assertEquals(i + 1, results.size)
            assertEquals(i, results.last())
        }
    }

    @Test
    fun delayZero() = runTest {
        var executed = false

        launch {
            delay(0) // Продолжение запланировано на текущее время
            executed = true
        }

        assertFalse(executed)

        runCurrent()
        assertTrue(executed)
    }
}
```

### Тестирование `withTimeout` / `withTimeoutOrNull`

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class TimeoutTesting {
    @Test
    fun testWithTimeoutSuccess() = runTest {
        val deferred = async {
            withTimeout(1000) {
                delay(500)
                "Success"
            }
        }

        advanceTimeBy(500)

        val result = deferred.await()
        assertEquals("Success", result)
        assertEquals(500, currentTime)
    }

    @Test
    fun testWithTimeoutFailure() = runTest {
        val deferred = async {
            withTimeout(1000) {
                delay(2000)
                "Should not reach"
            }
        }

        advanceTimeBy(1000)

        assertFailsWith<TimeoutCancellationException> { deferred.await() }
        assertEquals(1000, currentTime)
    }

    @Test
    fun testWithTimeoutOrNull() = runTest {
        val success = async {
            withTimeoutOrNull(1000) {
                delay(500)
                "Success"
            }
        }

        advanceTimeBy(500)
        assertEquals("Success", success.await())
        assertEquals(500, currentTime)

        val timedOut = async {
            withTimeoutOrNull(1000) {
                delay(2000)
                "Should timeout"
            }
        }

        advanceTimeBy(1000)
        assertNull(timedOut.await())
        assertEquals(1500, currentTime)
    }

    @Test
    fun testNetworkCallWithTimeout() = runTest {
        class NetworkClient {
            suspend fun fetchData(): String {
                delay(5000)
                return "Data"
            }
        }

        val client = NetworkClient()

        val deferred = async {
            withTimeoutOrNull(3000) {
                client.fetchData()
            }
        }

        advanceTimeBy(3000)

        assertNull(deferred.await())
        assertEquals(3000, currentTime)
    }
}
```

### Тестирование Периодических Операций

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class PeriodicOperationsTesting {
    @Test
    fun testPolling() = runTest {
        var pollCount = 0

        val job = launch {
            repeat(5) {
                pollCount++
                delay(1000)
            }
        }

        repeat(5) {
            advanceTimeBy(1000)
        }

        assertEquals(5, pollCount)
        assertEquals(5000, currentTime)

        job.cancel()
    }

    @Test
    fun testTickerChannel() = runTest {
        val ticker = ticker(delayMillis = 1000, initialDelayMillis = 0)
        val ticks = mutableListOf<Long>()

        val job = launch {
            repeat(5) {
                ticker.receive()
                ticks.add(currentTime)
            }
        }

        // Ticker использует тот же TestDispatcher, поэтому его тики следуют виртуальному времени
        advanceTimeBy(4000)
        advanceUntilIdle()

        assertEquals(listOf(0L, 1000L, 2000L, 3000L, 4000L), ticks)

        ticker.cancel()
        job.cancel()
    }

    @Test
    fun testRepeatingTask() = runTest {
        val executions = mutableListOf<Long>()

        suspend fun repeatingTask() {
            repeat(5) {
                executions.add(currentTime)
                delay(500)
            }
        }

        val job = launch { repeatingTask() }

        advanceTimeBy(2500)
        advanceUntilIdle()

        assertEquals(listOf(0L, 500L, 1000L, 1500L, 2000L), executions)

        job.cancel()
    }
}
```

### Тестирование debounce/throttle В `Flow`

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.*
import kotlin.test.*

class FlowTimingTesting {
    @Test
    fun testFlowDebounce() = runTest {
        val flow = flow {
            emit(1)
            delay(100)
            emit(2)
            delay(100)
            emit(3)
            delay(500)
            emit(4)
        }.debounce(200)

        val results = mutableListOf<Int>()

        val job = launch {
            flow.collect { results.add(it) }
        }

        advanceUntilIdle()

        // После debounce останутся только 3 и 4: 3 как последний в плотной серии, 4 как одиночный после длинной паузы
        assertEquals(listOf(3, 4), results)

        job.cancel()
    }

    @Test
    fun testFlowSample() = runTest {
        val flow = flow {
            repeat(10) { i ->
                emit(i)
                delay(100)
            }
        }.sample(250)

        val results = mutableListOf<Int>()

        val job = launch {
            flow.collect { results.add(it) }
        }

        advanceUntilIdle()

        // Эмиссии каждые 100мс, sample каждые 250мс (0, 250, 500, 750, ...).
        // На каждом тике берётся последний доступный элемент → предсказуемый паттерн 2, 4, 7, 9.
        assertEquals(listOf(2, 4, 7, 9), results)

        job.cancel()
    }

    @Test
    fun testFlowDelay() = runTest {
        val flow = flow {
            emit(1)
            emit(2)
            emit(3)
        }.onEach { delay(100) }

        val timestamps = mutableListOf<Long>()

        val job = launch {
            flow.collect {
                timestamps.add(currentTime)
            }
        }

        advanceUntilIdle()

        assertEquals(listOf(100L, 200L, 300L), timestamps)

        job.cancel()
    }
}
```

### Реальный Пример: Тестирование `ViewModel`

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.*
import kotlin.test.*

class UserProfileViewModel {
    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    suspend fun loadUserProfile(userId: String) {
        _uiState.value = UiState.Loading

        delay(1000) // эмуляция сети

        if (userId.isNotEmpty()) {
            _uiState.value = UiState.Success(UserProfile(userId, "User $userId"))
        } else {
            _uiState.value = UiState.Error("Invalid user ID")
        }
    }

    suspend fun refreshWithRetry() {
        repeat(3) { attempt ->
            _uiState.value = UiState.Loading

            delay(2000)

            if (attempt < 2) {
                _uiState.value = UiState.Error("Network error")
                delay(1000) // задержка перед повтором
            } else {
                _uiState.value = UiState.Success(UserProfile("123", "User"))
                return
            }
        }
    }
}

sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val profile: UserProfile) : UiState()
    data class Error(val message: String) : UiState()
}

data class UserProfile(val id: String, val name: String)

class UserProfileViewModelTest {
    @Test
    fun testLoadUserProfileSuccess() = runTest {
        val viewModel = UserProfileViewModel()

        assertEquals(UiState.Idle, viewModel.uiState.value)

        val job = launch {
            viewModel.loadUserProfile("123")
        }

        // Немедленный переход в Loading
        runCurrent()
        assertEquals(UiState.Loading, viewModel.uiState.value)

        advanceTimeBy(1000)
        runCurrent()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Success)
        assertEquals("123", state.profile.id)

        job.cancel()
    }

    @Test
    fun testLoadUserProfileError() = runTest {
        val viewModel = UserProfileViewModel()

        launch {
            viewModel.loadUserProfile("")
        }

        advanceTimeBy(1000)
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
        assertEquals("Invalid user ID", state.message)
    }

    @Test
    fun testRefreshWithRetry() = runTest {
        val viewModel = UserProfileViewModel()
        val states = mutableListOf<UiState>()

        val collectJob = launch {
            viewModel.uiState.collect { states.add(it) }
        }

        val refreshJob = launch {
            viewModel.refreshWithRetry()
        }

        // Проходим через все ретраи и успешный результат
        advanceUntilIdle()

        // Ожидаемая последовательность:
        // Idle -> Loading -> Error -> Loading -> Error -> Loading -> Success
        assertEquals(7, states.size)
        assertTrue(states[0] is UiState.Idle)
        assertTrue(states[1] is UiState.Loading)
        assertTrue(states[2] is UiState.Error)
        assertTrue(states[3] is UiState.Loading)
        assertTrue(states[4] is UiState.Error)
        assertTrue(states[5] is UiState.Loading)
        assertTrue(states[6] is UiState.Success)

        // Суммарное виртуальное время: (2000 + 1000) * 2 + 2000 = 8000мс
        assertEquals(8000, currentTime)

        collectJob.cancel()
        refreshJob.cancel()
    }

    @Test
    fun testStateFlowTimingWithCollect() = runTest {
        val viewModel = UserProfileViewModel()
        val stateTimestamps = mutableListOf<Pair<UiState, Long>>()

        val collectJob = backgroundScope.launch {
            viewModel.uiState.collect { state ->
                stateTimestamps.add(state to currentTime)
            }
        }

        launch {
            viewModel.loadUserProfile("user1")
        }

        advanceTimeBy(1000)
        advanceUntilIdle()

        assertEquals(3, stateTimestamps.size)
        assertEquals(0L, stateTimestamps[0].second) // Idle
        assertEquals(0L, stateTimestamps[1].second) // Loading
        assertEquals(1000L, stateTimestamps[2].second) // Success

        collectJob.cancel()
    }
}
```

### Тестирование Гонок Детерминированно

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class RaceConditionTesting {
    @Test
    fun testConcurrentUpdates() = runTest {
        var counter = 0

        val jobs = List(10) {
            launch {
                delay(100)
                counter++
            }
        }

        advanceTimeBy(100)

        assertEquals(10, counter)

        jobs.forEach { it.cancel() }
    }

    @Test
    fun testFirstToComplete() = runTest {
        val results = mutableListOf<String>()

        coroutineScope {
            launch {
                delay(100)
                results.add("Task A")
            }

            launch {
                delay(50)
                results.add("Task B")
            }

            launch {
                delay(150)
                results.add("Task C")
            }

            advanceTimeBy(150)
        }

        // Порядок детерминирован по задержкам
        assertEquals(listOf("Task B", "Task A", "Task C"), results)
    }

    @Test
    fun testSelectFirst() = runTest {
        suspend fun fetchFromServer1(): String {
            delay(200)
            return "Server 1"
        }

        suspend fun fetchFromServer2(): String {
            delay(100)
            return "Server 2"
        }

        val result = coroutineScope {
            val deferred1 = async { fetchFromServer1() }
            val deferred2 = async { fetchFromServer2() }

            advanceTimeBy(100)

            if (deferred2.isCompleted) {
                deferred1.cancel()
                deferred2.await()
            } else {
                deferred2.cancel()
                deferred1.await()
            }
        }

        assertEquals("Server 2", result)
        assertEquals(100, currentTime)
    }
}
```

### Частые Ошибки

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class CommonMistakes {
    @Test
    fun mistakeForgettingAdvanceUntilIdle() = runTest {
        var completed = false

        launch {
            delay(1000)
            completed = true
        }

        // Без продвижения времени delay не завершится
        assertFalse(completed)

        advanceUntilIdle()
        assertTrue(completed)
    }

    @Test
    fun mistakeWrongTimingExpectation() = runTest {
        val results = mutableListOf<Int>()

        launch {
            delay(100)
            results.add(1)

            delay(100)
            results.add(2)
        }

        advanceTimeBy(100)
        assertEquals(listOf(1), results)

        advanceTimeBy(100)
        assertEquals(listOf(1, 2), results)
    }

    @Test
    fun mistakeNotUsingBackgroundScope() = runTest {
        var count = 0

        // Потенциально бесконечная работа в основном TestScope
        val job = launch {
            while (true) {
                delay(1000)
                count++
            }
        }

        advanceTimeBy(3000)
        assertEquals(3, count)

        job.cancel()

        // Предпочтительно для fire-and-forget: backgroundScope + отмена
        val bgJob = backgroundScope.launch {
            while (true) {
                delay(1000)
                count++
            }
        }

        advanceTimeBy(3000)
        assertTrue(count >= 6)

        bgJob.cancel()
    }

    @Test
    fun mistakeAssumingImmediateExecution() = runTest {
        var value = 0

        launch {
            value = 1
        }

        // Без runCurrent значение ещё может быть 0
        assertEquals(0, value)

        runCurrent()
        assertEquals(1, value)
    }
}
```

### Немедленное Vs Отложенное Выполнение

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class ImmediateVsDelayedExecution {
    @Test
    fun testImmediateExecution() = runTest {
        var executed = false

        launch(start = CoroutineStart.UNDISPATCHED) {
            executed = true
        }

        assertTrue(executed)
    }

    @Test
    fun testDelayedExecution() = runTest {
        var executed = false

        launch {
            executed = true
        }

        assertFalse(executed)

        runCurrent()
        assertTrue(executed)
    }

    @Test
    fun testMixedExecution() = runTest {
        val results = mutableListOf<String>()

        launch(start = CoroutineStart.UNDISPATCHED) {
            results.add("Immediate")
            delay(100)
            results.add("After delay")
        }

        assertEquals(listOf("Immediate"), results)

        advanceTimeBy(100)
        assertEquals(listOf("Immediate", "After delay"), results)
    }
}
```

### Лучшие Практики

1. Используйте `runTest` для тестов корутин.
2. Используйте `advanceUntilIdle()` для выполнения всей конечной запланированной работы.
3. Используйте `advanceTimeBy()` для точного контроля времени и промежуточных проверок.
4. Используйте `runCurrent()` для задач на текущем виртуальном времени.
5. Собирайте `StateFlow`/`SharedFlow` в `backgroundScope` при необходимости и явно отменяйте коллекции.
6. Явно описывайте сценарии тайминга шагами (`advanceTimeBy` / `advanceUntilIdle`), избегая скрытых ожиданий.

---

## Answer (EN)

Testing time-dependent coroutine code without virtual time requires real delays, which makes tests slow, flaky, and non-deterministic. The `kotlinx-coroutines-test` module provides virtual time via `TestScope` and `TestDispatcher`, letting you explicitly and instantly control delayed and scheduled work.

All examples below assume `kotlinx-coroutines-test` 1.6+: virtual time is managed by the test scheduler and changes when you drive it using `advanceTimeBy`, `advanceUntilIdle`, `runCurrent`, or when `runTest` internally advances time while executing scheduled tasks. The `delay` call itself does not sleep real time.

### Virtual time Concept

- Virtual time lets you fast-forward coroutine delays without real waiting.
- `delay(1000)` only schedules continuation at time `1000`; until you move the virtual clock (or it is moved by the scheduler via test primitives), the coroutine does not resume.

### `TestScope` And `TestDispatcher`

- `runTest { ... }` creates a `TestScope` with a `TestDispatcher` (by default `StandardTestDispatcher`).
- All coroutines launched in this scope are controlled by the virtual-time scheduler.
- Pattern:
  - Use `delay` in the code under test.
  - In tests, call `advanceTimeBy` / `advanceUntilIdle` / `runCurrent` to drive execution instead of real sleeping.

### `advanceTimeBy(millis)` — Precise Stepwise Control

Use `advanceTimeBy` when you need fine-grained control and intermediate assertions.

Typical uses (matching RU examples):

- One-shot delay:
  - Launch a coroutine with `delay(1000)`.
  - Assert state before advancing.
  - `advanceTimeBy(500)` → still not completed.
  - `advanceTimeBy(500)` → completion observed at `currentTime == 1000`.
- Multiple delayed tasks:
  - Launch tasks with different delays (e.g., 100, 200, 300 ms).
  - Step the clock and assert which tasks have completed after each step.
- Debounce / rate limiting:
  - Model debounce by cancelling/relaunching a job with a delay.
  - Step time in segments to verify that only the last event is executed.
  - For rate-limiters, assert emitted timestamps (e.g., `0L, 1000L, 2000L`).

Key property: only tasks scheduled at or before the new virtual time are executed.

### `advanceUntilIdle()` — Run All Finite Work

Use `advanceUntilIdle()` when:

- All scheduled work (including recursively scheduled work) is finite.
- You want the system to reach quiescence without caring about the exact times between steps.

Scenarios:

- Several delayed tasks with different delays: `advanceUntilIdle()` runs them all and sets `currentTime` to the largest scheduled delay.
- Bounded repeated work with `repeat` and `delay`: `advanceUntilIdle()` drives it to completion.
- Dynamically scheduled work (recursive scheduling, producer-consumer with close): `advanceUntilIdle()` keeps jumping to the next event until no tasks remain.

Important: For infinite or open-ended loops, `advanceUntilIdle()` may never finish; in such cases, prefer bounded loops, manual `advanceTimeBy` steps, and explicit cancellation.

### `runCurrent()` — Only Tasks at Current time

Use `runCurrent()` to:

- Execute tasks scheduled at the current `currentTime` without moving the clock.
- Flush:
  - Immediate launches on the test dispatcher.
  - Continuations scheduled with `delay(0)`.

Examples:

- Launch immediate work and delayed work; `runCurrent()` runs only immediate work.
- Create more tasks at the same time; another `runCurrent()` flushes them, `currentTime` unchanged.

### `currentTime` — Observable Virtual Clock

- `currentTime` reflects the test scheduler clock in milliseconds.
- Use it to:
  - Assert when events happen relative to each other.
  - Store timestamps in domain events and verify ordering and spacing.

### Testing `delay()` Semantics

Use `advanceTimeBy`, `advanceUntilIdle`, and `runCurrent` to express clear expectations:

- For a `delay(1000)`, assert nothing happens before you advance; then advance in steps and verify exactly when execution continues.
- For loops with repeated `delay(100)`, advance in 100 ms increments and assert that each iteration has run.
- For `delay(0)`, verify that work is executed only after `runCurrent()` (since continuation is queued at the current time).

### Testing `withTimeout` / `withTimeoutOrNull`

Mirror RU examples:

- Success case:
  - `withTimeout(1000) { delay(500); "Success" }`.
  - `advanceTimeBy(500)` → `await()` returns "Success", `currentTime == 500`.
- Timeout case:
  - `withTimeout(1000) { delay(2000) }`.
  - `advanceTimeBy(1000)` → `await()` throws `TimeoutCancellationException`, `currentTime == 1000`.
- `withTimeoutOrNull`:
  - Shorter work: advance below timeout and expect result.
  - Longer work: advance to timeout and assert result is `null`.

### Testing Periodic Operations

You can deterministically verify periodic behavior:

- Polling loops with `delay(1000)`:
  - Repeatedly call `advanceTimeBy(1000)` and assert call counts and final `currentTime`.
- Ticker-like patterns:
  - Create a `ticker` bound to the test dispatcher; advance virtual time and assert ticks at `0, 1000, 2000, ...`.
- Repeating tasks with `repeat` + `delay`:
  - Use partial `advanceTimeBy` followed by `advanceUntilIdle()` to assert both timing and completion.

### Testing `Flow` Timing (`debounce`, `sample`, `onEach` delays)

Aligning with RU examples:

- `debounce`:
  - Emit values with short gaps and a longer gap.
  - `advanceUntilIdle()` and assert only the debounced values (e.g., `3` as last of the burst, `4` after a long pause).
- `sample`:
  - Emissions every 100 ms, `sample(250)`.
  - Sampling occurs at 0, 250, 500, 750, ... ms; on each tick the operator emits the latest value.
  - With that schedule, the collected values deterministically become `2, 4, 7, 9`.
- `onEach { delay(...) }`:
  - Collect and record `currentTime`; assert timestamps increase with expected steps.

### Testing `ViewModel` and `StateFlow`/`SharedFlow`

Parallel to RU `ViewModel` example:

- Expose UI state as `StateFlow`.
- Use `runTest` and the test dispatcher.
- In tests:
  - Start collecting from the flow (often via `backgroundScope`) so collection lives alongside the scenario.
  - Trigger `ViewModel` methods that use `delay`/timeouts/retries.
  - Drive virtual time with `advanceTimeBy` / `advanceUntilIdle`.
  - Assert the sequence and timing of states (e.g., Idle → Loading → Success/Error → retries).

### Deterministic race/ordering Tests

Use virtual time to remove nondeterminism:

- Launch multiple coroutines with different `delay` values.
- Advance in steps so they complete in a predictable order.
- "First successful" scenarios:
  - Start multiple async operations with different delays.
  - Advance until the earliest completion; cancel others and assert the correct winner.

### Common Pitfalls

Aligned with RU "Частые ошибки":

- Forgetting to advance time:
  - `delay` never completes without `advanceTimeBy` / `advanceUntilIdle`.
- Wrong timing expectations:
  - Always think in terms of scheduled times; assert only after appropriate advances.
- Not using `backgroundScope` for long-running/fire-and-forget jobs:
  - Infinite or long-lived loops in the main `TestScope` can block `advanceUntilIdle()`.
- Assuming immediate execution:
  - Launching on the test dispatcher may queue work; call `runCurrent()` to flush.

### Immediate Vs Delayed Execution

- `CoroutineStart.UNDISPATCHED` runs the coroutine body immediately up to the first suspension.
- Regular launched coroutines on the test dispatcher are queued and require `runCurrent()` or time advancement to execute.
- Combine with virtual-time primitives so expectations match actual scheduling.

### Best Practices (EN)

1. Use `runTest` with `kotlinx-coroutines-test` for coroutine tests.
2. Use `advanceUntilIdle()` to run all finite scheduled work to completion.
3. Use `advanceTimeBy()` for precise, stepwise time control and intermediate assertions.
4. Use `runCurrent()` to execute tasks scheduled at the current virtual time (including `delay(0)` continuations).
5. Collect `StateFlow`/`SharedFlow` in `backgroundScope` when needed, and cancel collectors explicitly.
6. Describe timing scenarios explicitly with `advanceTimeBy` / `advanceUntilIdle`; do not rely on implicit or real-time waits.

---

## Дополнительные Вопросы (RU)
1. В чём разница между `advanceUntilIdle()` и `advanceTimeBy(``Long``.MAX_VALUE)` при наличии бесконечной или лениво создаваемой работы?
2. Как протестировать бесконечный цикл с `delay()`, не зависая в `advanceUntilIdle()`?
3. Когда стоит использовать `backgroundScope` вместо основного `TestScope` в `runTest`?
4. Как протестировать, что корутина отменяется в определённый момент (например, до завершения `delay`)?
5. Что произойдёт, если вызвать `delay()` вне `TestScope` / без тестового диспетчера, и как это влияет на детерминизм тестов?
6. Как тестировать несколько корутин с разным таймингом, сохраняя детерминированный порядок событий?
7. Можно ли тестировать код без искусственных `delay` с помощью `runTest`, и каковы ограничения такого подхода?
## Follow-ups (EN)
1. What is the difference between `advanceUntilIdle()` and `advanceTimeBy(``Long``.MAX_VALUE)` when there is infinite or lazily produced work?
2. How can you test an infinite loop with `delay()` without hanging in `advanceUntilIdle()`?
3. When should you use `backgroundScope` instead of the main `TestScope` in `runTest`?
4. How can you test that a coroutine is cancelled at a specific moment (e.g., before a delay completes)?
5. What happens if you call `delay()` outside a `TestScope` / without a test dispatcher, and how does this affect test determinism?
6. How can you test multiple coroutines with different timings while keeping the event order deterministic?
7. Can you test code without artificial `delay` using `runTest`, and what are the implications/limitations?
## Ссылки (RU)
- [Kotlin Coroutines Test Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing Coroutines Guide](https://developer.android.com/kotlin/coroutines/test)
- [TestScope API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-scope/)
- [Virtual Time in Tests](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md)
- [[c-coroutines]]
- [[c-testing]]
## References (EN)
- [Kotlin Coroutines Test Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing Coroutines Guide](https://developer.android.com/kotlin/coroutines/test)
- [TestScope API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-scope/)
- [Virtual Time in Tests](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md)
- [[c-coroutines]]
- [[c-testing]]
## Связанные Вопросы (RU)
- [[q-structured-concurrency-violations--kotlin--hard|Нарушения структурированной конкуренции]]
## Related Questions (EN)
- [[q-structured-concurrency-violations--kotlin--hard|Structured concurrency violations]]
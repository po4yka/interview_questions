---
id: kotlin-073
title: "Virtual Time in Coroutine Testing / Виртуальное время в тестировании корутин"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, testing, virtual-time]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Virtual Time Testing Deep Dive

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-testing-coroutines-runtest--kotlin--medium, q-testing-flow-operators--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/medium, kotlin, testing, virtual-time]
date created: Friday, October 17th 2025, 11:23:08 am
date modified: Saturday, November 1st 2025, 5:43:27 pm
---

# Question (EN)
> How does virtual time work in coroutine testing? Explain advanceTimeBy, runCurrent, advanceUntilIdle, currentTime, delay testing, and how TestDispatcher controls execution timing.

# Вопрос (RU)
> Как работает виртуальное время в тестировании корутин? Объясните advanceTimeBy, runCurrent, advanceUntilIdle, currentTime, тестирование delay и как TestDispatcher контролирует время выполнения.

---

## Answer (EN)

Virtual time is a key feature of coroutine testing that allows tests to run instantly while simulating the passage of time. This makes tests fast, deterministic, and easy to reason about.

### The Problem: Real Time is Slow

```kotlin
// Without virtual time - SLOW!
@Test
fun `timer counts to 10 - slow version`() = runBlocking {
    val timer = Timer()
    timer.start()

    Thread.sleep(10000) // Actually wait 10 seconds!

    assertEquals(10, timer.seconds)
}

// With virtual time - INSTANT!
@Test
fun `timer counts to 10 - fast version`() = runTest {
    val timer = Timer()
    timer.start()

    advanceTimeBy(10000) // Instantly "advance" 10 seconds

    assertEquals(10, timer.seconds)
}
```

### Virtual Time Basics

When using `runTest`, the test dispatcher uses virtual time instead of real time:

```kotlin
@Test
fun `virtual time demonstration`() = runTest {
    println("Start time: $currentTime") // 0

    delay(1000)
    println("After 1s: $currentTime") // 1000

    delay(2000)
    println("After 3s total: $currentTime") // 3000

    // Test completes instantly despite 3 seconds of delays!
}
```

**Key insight**: `delay()` doesn't actually wait—it just advances virtual time and schedules resumption.

### currentTime

`currentTime` returns the current virtual time in milliseconds:

```kotlin
@Test
fun `currentTime tracks virtual time`() = runTest {
    assertEquals(0, currentTime)

    delay(100)
    assertEquals(100, currentTime)

    delay(250)
    assertEquals(350, currentTime)

    // Real wall-clock time: ~0ms
    // Virtual time: 350ms
}

@Test
fun `measure operation duration with virtual time`() = runTest {
    val startTime = currentTime

    performOperation() // Contains delays

    val duration = currentTime - startTime

    assertEquals(expectedDuration, duration)
}

suspend fun performOperation() {
    delay(100)
    // Work
    delay(50)
}
```

### advanceTimeBy(milliseconds)

Advances virtual time by the specified amount and executes coroutines scheduled within that timeframe:

```kotlin
@Test
fun `advanceTimeBy advances time precisely`() = runTest {
    val events = mutableListOf<String>()

    launch {
        delay(100)
        events.add("Event at 100ms")
    }

    launch {
        delay(200)
        events.add("Event at 200ms")
    }

    launch {
        delay(300)
        events.add("Event at 300ms")
    }

    // Advance to 150ms
    advanceTimeBy(150)
    assertEquals(150, currentTime)
    assertEquals(listOf("Event at 100ms"), events)

    // Advance to 250ms
    advanceTimeBy(100)
    assertEquals(250, currentTime)
    assertEquals(listOf("Event at 100ms", "Event at 200ms"), events)

    // Advance to 350ms
    advanceTimeBy(100)
    assertEquals(350, currentTime)
    assertEquals(3, events.size)
}
```

**Behavior**:
- Advances virtual time by specified milliseconds
- Executes all coroutines scheduled before or at the new time
- Does not execute coroutines scheduled after the new time

### advanceUntilIdle()

Executes all pending coroutines until there are no more scheduled tasks:

```kotlin
@Test
fun `advanceUntilIdle runs everything`() = runTest {
    val events = mutableListOf<Int>()

    launch {
        delay(100)
        events.add(1)
        delay(200)
        events.add(2)
    }

    launch {
        delay(150)
        events.add(3)
    }

    launch {
        delay(400)
        events.add(4)
    }

    advanceUntilIdle()

    // All events processed
    assertEquals(listOf(1, 3, 2, 4), events)
    assertEquals(500, currentTime) // Advanced to last scheduled time
}

@Test
fun `advanceUntilIdle with infinite loop`() = runTest {
    var count = 0

    val job = launch {
        while (true) {
            delay(100)
            count++
            if (count >= 5) break
        }
    }

    advanceUntilIdle()

    assertEquals(5, count)
    assertEquals(500, currentTime)
}
```

**Behavior**:
- Advances time to the next scheduled event
- Executes that event
- Repeats until no more events are scheduled
- Useful for "run to completion" scenarios

### runCurrent()

Executes only coroutines scheduled at the current virtual time, without advancing time:

```kotlin
@Test
fun `runCurrent executes current tasks only`() = runTest {
    val events = mutableListOf<String>()

    launch {
        events.add("Immediate 1")
    }

    launch {
        events.add("Immediate 2")
    }

    launch {
        delay(100)
        events.add("Delayed")
    }

    // Execute immediate tasks without advancing time
    runCurrent()

    assertEquals(listOf("Immediate 1", "Immediate 2"), events)
    assertEquals(0, currentTime) // Time hasn't advanced

    // Now advance time
    advanceTimeBy(100)
    assertEquals(listOf("Immediate 1", "Immediate 2", "Delayed"), events)
}

@Test
fun `runCurrent vs advanceTimeBy(0)`() = runTest {
    val events = mutableListOf<String>()

    launch {
        events.add("Immediate")
    }

    launch {
        delay(0) // Scheduled for time 0, but after initial tasks
        events.add("Delayed 0")
    }

    runCurrent()
    assertEquals(listOf("Immediate"), events)

    advanceTimeBy(0)
    assertEquals(listOf("Immediate", "Delayed 0"), events)
}
```

**Behavior**:
- Executes only coroutines scheduled at current time
- Does NOT advance virtual time
- Useful for testing immediate effects

### Testing Delays

```kotlin
class CountdownTimer {
    private val _seconds = MutableStateFlow(10)
    val seconds: StateFlow<Int> = _seconds.asStateFlow()

    suspend fun start() {
        repeat(10) {
            delay(1000)
            _seconds.value -= 1
        }
    }
}

@Test
fun `countdown timer with virtual time`() = runTest {
    val timer = CountdownTimer()

    launch { timer.start() }

    assertEquals(10, timer.seconds.value)

    advanceTimeBy(1000)
    assertEquals(9, timer.seconds.value)

    advanceTimeBy(5000)
    assertEquals(4, timer.seconds.value)

    advanceUntilIdle()
    assertEquals(0, timer.seconds.value)

    // Test completed instantly, no actual waiting!
    assertEquals(10000, currentTime)
}

@Test
fun `test multiple delays in sequence`() = runTest {
    suspend fun operation() {
        delay(100)
        delay(200)
        delay(300)
    }

    val start = currentTime
    operation()
    val end = currentTime

    assertEquals(600, end - start)
}
```

### Testing Periodic Operations

```kotlin
class DataPoller(private val api: Api) {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()

    suspend fun startPolling(intervalMs: Long) {
        while (true) {
            _data.value = api.fetch()
            delay(intervalMs)
        }
    }
}

@Test
fun `polling happens at regular intervals`() = runTest {
    val api = FakeApi()
    val poller = DataPoller(api)

    launch { poller.startPolling(1000) }

    runCurrent() // First poll happens immediately
    assertEquals(1, api.fetchCount)

    advanceTimeBy(1000)
    assertEquals(2, api.fetchCount)

    advanceTimeBy(1000)
    assertEquals(3, api.fetchCount)

    advanceTimeBy(5000)
    assertEquals(8, api.fetchCount)
}

@Test
fun `polling can be stopped`() = runTest {
    val api = FakeApi()
    val poller = DataPoller(api)

    val job = launch { poller.startPolling(1000) }

    advanceTimeBy(3500)
    assertEquals(4, api.fetchCount)

    job.cancel()
    advanceTimeBy(10000) // No more polling

    assertEquals(4, api.fetchCount) // Didn't increase
}
```

### Testing Debounce

```kotlin
class SearchDebouncer {
    private val _queries = MutableSharedFlow<String>()
    val queries: SharedFlow<String> = _queries.asSharedFlow()

    val debouncedQueries = queries.debounce(300)

    suspend fun search(query: String) {
        _queries.emit(query)
    }
}

@Test
fun `debounce with virtual time`() = runTest {
    val debouncer = SearchDebouncer()
    val results = mutableListOf<String>()

    val job = launch {
        debouncer.debouncedQueries.collect { results.add(it) }
    }

    debouncer.search("a")
    advanceTimeBy(100)
    assertTrue(results.isEmpty()) // Too soon

    debouncer.search("ab")
    advanceTimeBy(100)
    assertTrue(results.isEmpty()) // Still too soon

    debouncer.search("abc")
    advanceTimeBy(100)
    assertTrue(results.isEmpty()) // Still too soon

    advanceTimeBy(300) // Debounce timeout passed
    assertEquals(listOf("abc"), results)

    job.cancel()
}

@Test
fun `debounce each query separately`() = runTest {
    val debouncer = SearchDebouncer()
    val results = mutableListOf<String>()

    val job = launch {
        debouncer.debouncedQueries.collect { results.add(it) }
    }

    debouncer.search("first")
    advanceTimeBy(400) // First debounced
    assertEquals(listOf("first"), results)

    debouncer.search("second")
    advanceTimeBy(400) // Second debounced
    assertEquals(listOf("first", "second"), results)

    job.cancel()
}
```

### Testing Timeouts

```kotlin
@Test
fun `withTimeout with virtual time`() = runTest {
    val result = try {
        withTimeout(1000) {
            delay(500)
            "completed"
        }
    } catch (e: TimeoutCancellationException) {
        "timeout"
    }

    assertEquals("completed", result)
    assertEquals(500, currentTime)
}

@Test
fun `withTimeout exceeds limit`() = runTest {
    val result = try {
        withTimeout(1000) {
            delay(1500)
            "completed"
        }
    } catch (e: TimeoutCancellationException) {
        "timeout"
    }

    assertEquals("timeout", result)
    assertEquals(1000, currentTime)
}

@Test
fun `multiple operations with different timeouts`() = runTest {
    val results = mutableListOf<String>()

    launch {
        try {
            withTimeout(500) {
                delay(1000)
                results.add("Fast - completed")
            }
        } catch (e: TimeoutCancellationException) {
            results.add("Fast - timeout")
        }
    }

    launch {
        try {
            withTimeout(2000) {
                delay(1000)
                results.add("Slow - completed")
            }
        } catch (e: TimeoutCancellationException) {
            results.add("Slow - timeout")
        }
    }

    advanceUntilIdle()

    assertEquals(listOf("Fast - timeout", "Slow - completed"), results)
}
```

### Testing Rate Limiting

```kotlin
class RateLimiter(private val minIntervalMs: Long) {
    private var lastExecutionTime = 0L

    suspend fun execute(action: suspend () -> Unit) {
        val now = System.currentTimeMillis()
        val timeSinceL ast = now - lastExecutionTime

        if (timeSinceLast < minIntervalMs) {
            delay(minIntervalMs - timeSinceLast)
        }

        lastExecutionTime = System.currentTimeMillis()
        action()
    }
}

// Better implementation for testing
class TestableRateLimiter(
    private val minIntervalMs: Long,
    private val timeProvider: () -> Long = { System.currentTimeMillis() }
) {
    private var lastExecutionTime = 0L

    suspend fun execute(action: suspend () -> Unit) {
        val now = timeProvider()
        val timeSinceLast = now - lastExecutionTime

        if (timeSinceLast < minIntervalMs) {
            delay(minIntervalMs - timeSinceLast)
        }

        lastExecutionTime = timeProvider()
        action()
    }
}

@Test
fun `rate limiter with virtual time`() = runTest {
    var executionCount = 0
    val limiter = TestableRateLimiter(1000) { currentTime }

    launch {
        repeat(5) {
            limiter.execute {
                executionCount++
            }
        }
    }

    advanceTimeBy(500)
    assertEquals(1, executionCount)

    advanceTimeBy(500)
    assertEquals(2, executionCount)

    advanceTimeBy(3000)
    assertEquals(5, executionCount)
}
```

### Testing Concurrent Operations

```kotlin
@Test
fun `concurrent operations timing`() = runTest {
    val results = mutableListOf<String>()

    launch {
        delay(100)
        results.add("A1")
        delay(200)
        results.add("A2")
    }

    launch {
        delay(150)
        results.add("B1")
        delay(100)
        results.add("B2")
    }

    advanceTimeBy(100)
    assertEquals(listOf("A1"), results)

    advanceTimeBy(50)
    assertEquals(listOf("A1", "B1"), results)

    advanceTimeBy(50)
    assertEquals(listOf("A1", "B1", "B2"), results)

    advanceTimeBy(100)
    assertEquals(listOf("A1", "B1", "B2", "A2"), results)
}

@Test
fun `parallel execution saves time`() = runTest {
    suspend fun slowOperation(): Int {
        delay(1000)
        return 42
    }

    // Sequential
    val sequentialStart = currentTime
    val result1 = slowOperation()
    val result2 = slowOperation()
    val sequentialDuration = currentTime - sequentialStart

    assertEquals(2000, sequentialDuration)

    // Parallel
    val parallelStart = currentTime
    val deferred1 = async { slowOperation() }
    val deferred2 = async { slowOperation() }
    val parallelResult1 = deferred1.await()
    val parallelResult2 = deferred2.await()
    val parallelDuration = currentTime - parallelStart

    assertEquals(1000, parallelDuration) // Both ran in parallel!
}
```

### Virtual Time Gotchas

```kotlin
//  WRONG: Using Thread.sleep
@Test
fun `wrong - Thread sleep`() = runTest {
    launch {
        Thread.sleep(1000) // Actually sleeps!
        println("After sleep")
    }

    advanceTimeBy(1000) // Doesn't help
    // Test hangs or takes 1 second
}

//  CORRECT: Using delay
@Test
fun `correct - delay`() = runTest {
    launch {
        delay(1000) // Virtual time
        println("After delay")
    }

    advanceTimeBy(1000) // Works instantly
}

//  WRONG: Real time API
@Test
fun `wrong - System.currentTimeMillis`() = runTest {
    val start = System.currentTimeMillis() // Real time!
    delay(1000)
    val end = System.currentTimeMillis()

    val duration = end - start
    assertTrue(duration < 100) // Actually took < 100ms real time
}

//  CORRECT: Virtual time
@Test
fun `correct - currentTime`() = runTest {
    val start = currentTime // Virtual time
    delay(1000)
    val end = currentTime

    val duration = end - start
    assertEquals(1000, duration)
}

//  WRONG: Blocking APIs
@Test
fun `wrong - blocking API`() = runTest {
    launch {
        val result = blockingNetworkCall() // Blocks thread!
    }

    advanceUntilIdle() // Doesn't help
}

//  CORRECT: Suspending APIs
@Test
fun `correct - suspending API`() = runTest {
    launch {
        val result = suspendingNetworkCall() // Properly suspends
    }

    advanceUntilIdle() // Works
}
```

### Summary

**Virtual time functions**:
- **currentTime**: Get current virtual time in milliseconds
- **advanceTimeBy(ms)**: Advance time by specific amount, execute scheduled coroutines
- **advanceUntilIdle()**: Run all pending coroutines to completion
- **runCurrent()**: Execute only current-time tasks, don't advance time

**Key principles**:
1. `delay()` uses virtual time—instant in tests
2. Virtual time only advances explicitly (advanceTimeBy, advanceUntilIdle)
3. Real wall-clock time is NOT used
4. Tests run instantly regardless of delays
5. Timing is deterministic and controllable

**Use advanceTimeBy when**:
- Testing specific timing scenarios
- Need precise control over execution
- Testing timeouts or intervals
- Verifying delays are correct

**Use advanceUntilIdle when**:
- Want to run everything to completion
- Don't care about intermediate timing
- Testing final state
- Running entire flows

**Use runCurrent when**:
- Testing immediate effects
- Want to execute synchronous code
- Need to verify state before time advances

---

## Ответ (RU)

Виртуальное время - ключевая функция тестирования корутин, которая позволяет тестам выполняться мгновенно, при этом симулируя прохождение времени. Это делает тесты быстрыми, детерминированными и легкими для понимания.

### Проблема: Реальное Время Медленное

```kotlin
// Без виртуального времени - МЕДЛЕННО!
@Test
fun `таймер считает до 10 - медленная версия`() = runBlocking {
    val timer = Timer()
    timer.start()

    Thread.sleep(10000) // Реально ждём 10 секунд!

    assertEquals(10, timer.seconds)
}

// С виртуальным временем - МГНОВЕННО!
@Test
fun `таймер считает до 10 - быстрая версия`() = runTest {
    val timer = Timer()
    timer.start()

    advanceTimeBy(10000) // Мгновенно "продвигаем" 10 секунд

    assertEquals(10, timer.seconds)
}
```

### Основы Виртуального Времени

При использовании `runTest`, тестовый диспетчер использует виртуальное время вместо реального:

```kotlin
@Test
fun `демонстрация виртуального времени`() = runTest {
    println("Начало: $currentTime") // 0

    delay(1000)
    println("После 1с: $currentTime") // 1000

    delay(2000)
    println("После 3с: $currentTime") // 3000

    // Тест завершается мгновенно, несмотря на 3 секунды задержек!
}
```

**Ключевой момент**: `delay()` на самом деле не ждёт — она просто продвигает виртуальное время и планирует возобновление.

### currentTime

`currentTime` возвращает текущее виртуальное время в миллисекундах:

```kotlin
@Test
fun `currentTime отслеживает виртуальное время`() = runTest {
    assertEquals(0, currentTime)

    delay(100)
    assertEquals(100, currentTime)

    delay(250)
    assertEquals(350, currentTime)

    // Реальное время стены: ~0мс
    // Виртуальное время: 350мс
}

@Test
fun `измерение длительности операции с виртуальным временем`() = runTest {
    val startTime = currentTime

    performOperation() // Содержит задержки

    val duration = currentTime - startTime

    assertEquals(expectedDuration, duration)
}

suspend fun performOperation() {
    delay(100)
    // Работа
    delay(50)
}
```

### advanceTimeBy(milliseconds)

Продвигает виртуальное время на указанное количество миллисекунд и выполняет корутины, запланированные в этот временной промежуток:

```kotlin
@Test
fun `advanceTimeBy продвигает время точно`() = runTest {
    val events = mutableListOf<String>()

    launch {
        delay(100)
        events.add("Событие в 100мс")
    }

    launch {
        delay(200)
        events.add("Событие в 200мс")
    }

    launch {
        delay(300)
        events.add("Событие в 300мс")
    }

    // Продвинуть до 150мс
    advanceTimeBy(150)
    assertEquals(150, currentTime)
    assertEquals(listOf("Событие в 100мс"), events)

    // Продвинуть до 250мс
    advanceTimeBy(100)
    assertEquals(250, currentTime)
    assertEquals(listOf("Событие в 100мс", "Событие в 200мс"), events)

    // Продвинуть до 350мс
    advanceTimeBy(100)
    assertEquals(350, currentTime)
    assertEquals(3, events.size)
}
```

**Поведение**:
- Продвигает виртуальное время на указанное количество миллисекунд
- Выполняет все корутины, запланированные до или в новое время
- Не выполняет корутины, запланированные после нового времени

### advanceUntilIdle()

Выполняет все ожидающие корутины, пока не останется запланированных задач:

```kotlin
@Test
fun `advanceUntilIdle запускает всё`() = runTest {
    val events = mutableListOf<Int>()

    launch {
        delay(100)
        events.add(1)
        delay(200)
        events.add(2)
    }

    launch {
        delay(150)
        events.add(3)
    }

    launch {
        delay(400)
        events.add(4)
    }

    advanceUntilIdle()

    // Все события обработаны
    assertEquals(listOf(1, 3, 2, 4), events)
    assertEquals(500, currentTime) // Продвинуто до последнего запланированного времени
}

@Test
fun `advanceUntilIdle с бесконечным циклом`() = runTest {
    var count = 0

    val job = launch {
        while (true) {
            delay(100)
            count++
            if (count >= 5) break
        }
    }

    advanceUntilIdle()

    assertEquals(5, count)
    assertEquals(500, currentTime)
}
```

**Поведение**:
- Продвигает время до следующего запланированного события
- Выполняет это событие
- Повторяет, пока не останется событий
- Полезно для сценариев "выполнить до завершения"

### runCurrent()

Выполняет только корутины, запланированные на текущее виртуальное время, не продвигая время:

```kotlin
@Test
fun `runCurrent выполняет только текущие задачи`() = runTest {
    val events = mutableListOf<String>()

    launch {
        events.add("Немедленно 1")
    }

    launch {
        events.add("Немедленно 2")
    }

    launch {
        delay(100)
        events.add("С задержкой")
    }

    // Выполнить немедленные задачи без продвижения времени
    runCurrent()

    assertEquals(listOf("Немедленно 1", "Немедленно 2"), events)
    assertEquals(0, currentTime) // Время не продвинулось

    // Теперь продвинуть время
    advanceTimeBy(100)
    assertEquals(listOf("Немедленно 1", "Немедленно 2", "С задержкой"), events)
}

@Test
fun `runCurrent vs advanceTimeBy(0)`() = runTest {
    val events = mutableListOf<String>()

    launch {
        events.add("Немедленно")
    }

    launch {
        delay(0) // Запланировано на время 0, но после начальных задач
        events.add("Задержка 0")
    }

    runCurrent()
    assertEquals(listOf("Немедленно"), events)

    advanceTimeBy(0)
    assertEquals(listOf("Немедленно", "Задержка 0"), events)
}
```

**Поведение**:
- Выполняет только корутины, запланированные на текущее время
- НЕ продвигает виртуальное время
- Полезно для тестирования немедленных эффектов

### Тестирование Задержек

```kotlin
class CountdownTimer {
    private val _seconds = MutableStateFlow(10)
    val seconds: StateFlow<Int> = _seconds.asStateFlow()

    suspend fun start() {
        repeat(10) {
            delay(1000)
            _seconds.value -= 1
        }
    }
}

@Test
fun `таймер обратного отсчёта с виртуальным временем`() = runTest {
    val timer = CountdownTimer()

    launch { timer.start() }

    assertEquals(10, timer.seconds.value)

    advanceTimeBy(1000)
    assertEquals(9, timer.seconds.value)

    advanceTimeBy(5000)
    assertEquals(4, timer.seconds.value)

    advanceUntilIdle()
    assertEquals(0, timer.seconds.value)

    // Тест завершён мгновенно, без реального ожидания!
    assertEquals(10000, currentTime)
}

@Test
fun `тест нескольких задержек подряд`() = runTest {
    suspend fun operation() {
        delay(100)
        delay(200)
        delay(300)
    }

    val start = currentTime
    operation()
    val end = currentTime

    assertEquals(600, end - start)
}
```

### Тестирование Периодических Операций

```kotlin
class DataPoller(private val api: Api) {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()

    suspend fun startPolling(intervalMs: Long) {
        while (true) {
            _data.value = api.fetch()
            delay(intervalMs)
        }
    }
}

@Test
fun `опрос происходит с регулярными интервалами`() = runTest {
    val api = FakeApi()
    val poller = DataPoller(api)

    launch { poller.startPolling(1000) }

    runCurrent() // Первый опрос происходит немедленно
    assertEquals(1, api.fetchCount)

    advanceTimeBy(1000)
    assertEquals(2, api.fetchCount)

    advanceTimeBy(1000)
    assertEquals(3, api.fetchCount)

    advanceTimeBy(5000)
    assertEquals(8, api.fetchCount)
}

@Test
fun `опрос может быть остановлен`() = runTest {
    val api = FakeApi()
    val poller = DataPoller(api)

    val job = launch { poller.startPolling(1000) }

    advanceTimeBy(3500)
    assertEquals(4, api.fetchCount)

    job.cancel()
    advanceTimeBy(10000) // Больше нет опроса

    assertEquals(4, api.fetchCount) // Не увеличилось
}
```

### Тестирование Debounce

```kotlin
class SearchDebouncer {
    private val _queries = MutableSharedFlow<String>()
    val queries: SharedFlow<String> = _queries.asSharedFlow()

    val debouncedQueries = queries.debounce(300)

    suspend fun search(query: String) {
        _queries.emit(query)
    }
}

@Test
fun `debounce с виртуальным временем`() = runTest {
    val debouncer = SearchDebouncer()
    val results = mutableListOf<String>()

    val job = launch {
        debouncer.debouncedQueries.collect { results.add(it) }
    }

    debouncer.search("a")
    advanceTimeBy(100)
    assertTrue(results.isEmpty()) // Слишком рано

    debouncer.search("ab")
    advanceTimeBy(100)
    assertTrue(results.isEmpty()) // Всё ещё рано

    debouncer.search("abc")
    advanceTimeBy(100)
    assertTrue(results.isEmpty()) // Всё ещё рано

    advanceTimeBy(300) // Таймаут debounce прошёл
    assertEquals(listOf("abc"), results)

    job.cancel()
}

@Test
fun `debounce каждого запроса отдельно`() = runTest {
    val debouncer = SearchDebouncer()
    val results = mutableListOf<String>()

    val job = launch {
        debouncer.debouncedQueries.collect { results.add(it) }
    }

    debouncer.search("first")
    advanceTimeBy(400) // Первый прошёл debounce
    assertEquals(listOf("first"), results)

    debouncer.search("second")
    advanceTimeBy(400) // Второй прошёл debounce
    assertEquals(listOf("first", "second"), results)

    job.cancel()
}
```

### Тестирование Таймаутов

```kotlin
@Test
fun `withTimeout с виртуальным временем`() = runTest {
    val result = try {
        withTimeout(1000) {
            delay(500)
            "завершено"
        }
    } catch (e: TimeoutCancellationException) {
        "таймаут"
    }

    assertEquals("завершено", result)
    assertEquals(500, currentTime)
}

@Test
fun `withTimeout превышает лимит`() = runTest {
    val result = try {
        withTimeout(1000) {
            delay(1500)
            "завершено"
        }
    } catch (e: TimeoutCancellationException) {
        "таймаут"
    }

    assertEquals("таймаут", result)
    assertEquals(1000, currentTime)
}

@Test
fun `несколько операций с разными таймаутами`() = runTest {
    val results = mutableListOf<String>()

    launch {
        try {
            withTimeout(500) {
                delay(1000)
                results.add("Быстро - завершено")
            }
        } catch (e: TimeoutCancellationException) {
            results.add("Быстро - таймаут")
        }
    }

    launch {
        try {
            withTimeout(2000) {
                delay(1000)
                results.add("Медленно - завершено")
            }
        } catch (e: TimeoutCancellationException) {
            results.add("Медленно - таймаут")
        }
    }

    advanceUntilIdle()

    assertEquals(listOf("Быстро - таймаут", "Медленно - завершено"), results)
}
```

### Тестирование Ограничения Частоты Запросов

```kotlin
class RateLimiter(private val minIntervalMs: Long) {
    private var lastExecutionTime = 0L

    suspend fun execute(action: suspend () -> Unit) {
        val now = System.currentTimeMillis()
        val timeSinceLast = now - lastExecutionTime

        if (timeSinceLast < minIntervalMs) {
            delay(minIntervalMs - timeSinceLast)
        }

        lastExecutionTime = System.currentTimeMillis()
        action()
    }
}

// Улучшенная реализация для тестирования
class TestableRateLimiter(
    private val minIntervalMs: Long,
    private val timeProvider: () -> Long = { System.currentTimeMillis() }
) {
    private var lastExecutionTime = 0L

    suspend fun execute(action: suspend () -> Unit) {
        val now = timeProvider()
        val timeSinceLast = now - lastExecutionTime

        if (timeSinceLast < minIntervalMs) {
            delay(minIntervalMs - timeSinceLast)
        }

        lastExecutionTime = timeProvider()
        action()
    }
}

@Test
fun `ограничитель частоты с виртуальным временем`() = runTest {
    var executionCount = 0
    val limiter = TestableRateLimiter(1000) { currentTime }

    launch {
        repeat(5) {
            limiter.execute {
                executionCount++
            }
        }
    }

    advanceTimeBy(500)
    assertEquals(1, executionCount)

    advanceTimeBy(500)
    assertEquals(2, executionCount)

    advanceTimeBy(3000)
    assertEquals(5, executionCount)
}
```

### Тестирование Параллельных Операций

```kotlin
@Test
fun `синхронизация параллельных операций`() = runTest {
    val results = mutableListOf<String>()

    launch {
        delay(100)
        results.add("A1")
        delay(200)
        results.add("A2")
    }

    launch {
        delay(150)
        results.add("B1")
        delay(100)
        results.add("B2")
    }

    advanceTimeBy(100)
    assertEquals(listOf("A1"), results)

    advanceTimeBy(50)
    assertEquals(listOf("A1", "B1"), results)

    advanceTimeBy(50)
    assertEquals(listOf("A1", "B1", "B2"), results)

    advanceTimeBy(100)
    assertEquals(listOf("A1", "B1", "B2", "A2"), results)
}

@Test
fun `параллельное выполнение экономит время`() = runTest {
    suspend fun slowOperation(): Int {
        delay(1000)
        return 42
    }

    // Последовательно
    val sequentialStart = currentTime
    val result1 = slowOperation()
    val result2 = slowOperation()
    val sequentialDuration = currentTime - sequentialStart

    assertEquals(2000, sequentialDuration)

    // Параллельно
    val parallelStart = currentTime
    val deferred1 = async { slowOperation() }
    val deferred2 = async { slowOperation() }
    val parallelResult1 = deferred1.await()
    val parallelResult2 = deferred2.await()
    val parallelDuration = currentTime - parallelStart

    assertEquals(1000, parallelDuration) // Оба выполнились параллельно!
}
```

### Подводные Камни Виртуального Времени

```kotlin
// НЕПРАВИЛЬНО: Использование Thread.sleep
@Test
fun `неправильно - Thread sleep`() = runTest {
    launch {
        Thread.sleep(1000) // Реально спит!
        println("После сна")
    }

    advanceTimeBy(1000) // Не помогает
    // Тест зависает или выполняется 1 секунду
}

// ПРАВИЛЬНО: Использование delay
@Test
fun `правильно - delay`() = runTest {
    launch {
        delay(1000) // Виртуальное время
        println("После задержки")
    }

    advanceTimeBy(1000) // Работает мгновенно
}

// НЕПРАВИЛЬНО: API реального времени
@Test
fun `неправильно - System.currentTimeMillis`() = runTest {
    val start = System.currentTimeMillis() // Реальное время!
    delay(1000)
    val end = System.currentTimeMillis()

    val duration = end - start
    assertTrue(duration < 100) // Реально заняло < 100мс
}

// ПРАВИЛЬНО: Виртуальное время
@Test
fun `правильно - currentTime`() = runTest {
    val start = currentTime // Виртуальное время
    delay(1000)
    val end = currentTime

    val duration = end - start
    assertEquals(1000, duration)
}

// НЕПРАВИЛЬНО: Блокирующие API
@Test
fun `неправильно - блокирующий API`() = runTest {
    launch {
        val result = blockingNetworkCall() // Блокирует поток!
    }

    advanceUntilIdle() // Не помогает
}

// ПРАВИЛЬНО: Приостанавливаемые API
@Test
fun `правильно - suspending API`() = runTest {
    launch {
        val result = suspendingNetworkCall() // Правильно приостанавливается
    }

    advanceUntilIdle() // Работает
}
```

### Резюме

**Функции виртуального времени**:
- **currentTime**: Получить текущее виртуальное время в миллисекундах
- **advanceTimeBy(ms)**: Продвинуть время на указанную величину, выполнить запланированные корутины
- **advanceUntilIdle()**: Выполнить все ожидающие корутины до завершения
- **runCurrent()**: Выполнить только задачи текущего времени, не продвигая время

**Ключевые принципы**:
1. `delay()` использует виртуальное время — мгновенно в тестах
2. Виртуальное время продвигается только явно (advanceTimeBy, advanceUntilIdle)
3. Реальное время НЕ используется
4. Тесты выполняются мгновенно независимо от задержек
5. Время детерминировано и управляемо

**Используйте advanceTimeBy когда**:
- Тестирование конкретных временных сценариев
- Нужен точный контроль выполнения
- Тестирование таймаутов или интервалов
- Проверка корректности задержек

**Используйте advanceUntilIdle когда**:
- Хотите выполнить всё до завершения
- Не заботитесь о промежуточном времени
- Тестирование финального состояния
- Запуск полных потоков

**Используйте runCurrent когда**:
- Тестирование немедленных эффектов
- Хотите выполнить синхронный код
- Нужно проверить состояние до продвижения времени

---

## Follow-ups

1. How does virtual time interact with Dispatchers.IO?
2. Can you mix virtual time with real delays in tests?
3. How to test code that depends on System.currentTimeMillis()?
4. What happens when you use Thread.sleep in runTest?
5. How does virtual time work with Flow operators?

---

## References

- [Testing Coroutines - Kotlin Docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [runTest Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/run-test.html)

---

## Related Questions

- [[q-testing-coroutines-runtest--kotlin--medium]] - runTest basics
- [[q-testing-flow-operators--kotlin--hard]] - Testing Flow operators
- [[q-testing-coroutine-cancellation--kotlin--medium]] - Testing cancellation

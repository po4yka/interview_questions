---
id: kotlin-073
title: "Virtual Time in Coroutine Testing / Виртуальное время в тестировании корутин"
aliases: ["Virtual Time in Coroutine Testing", "Виртуальное время в тестировании корутин"]

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
related: [c-kotlin, c-coroutines, q-testing-coroutines-runtest--kotlin--medium, q-testing-flow-operators--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/medium, kotlin, testing, virtual-time]
---
# Вопрос (RU)
> Как работает виртуальное время в тестировании корутин? Объясните advanceTimeBy, runCurrent, advanceUntilIdle, currentTime, тестирование delay и как TestDispatcher контролирует время выполнения.

---

# Question (EN)
> How does virtual time work in coroutine testing? Explain advanceTimeBy, runCurrent, advanceUntilIdle, currentTime, delay testing, and how TestDispatcher controls execution timing.

## Ответ (RU)

Виртуальное время — ключевая функция тестирования корутин, которая позволяет тестам управлять временем явно и выполнять проверки мгновенно, при этом симулируя прохождение времени. Это делает тесты быстрыми, детерминированными и предсказуемыми.

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

    advanceTimeBy(10000) // Явно "продвигаем" 10 секунд виртуального времени (для delay под TestDispatcher)

    assertEquals(10, timer.seconds)
}
```

(Класс Timer предполагается использовать delay внутри и запускаться в контексте тестового диспетчера runTest.)

### Основы Виртуального Времени

При использовании `runTest`, он устанавливает специальный тестовый диспетчер/планировщик (TestDispatcher/TestScheduler), который оперирует виртуальным временем для операций, основанных на `delay`/`kotlinx.coroutines`, если корутины выполняются на этом диспетчере.

```kotlin
@Test
fun `демонстрация виртуального времени`() = runTest {
    println("Начало: $currentTime") // 0

    delay(1000)
    println("После 1с: $currentTime") // 1000

    delay(2000)
    println("После 3с: $currentTime") // 3000

    // Тест завершается мгновенно с точки зрения реального времени,
    // потому что виртуальное время продвигается планировщиком теста.
}
```

**Ключевой момент**: `delay()` под тестовым диспетчером не блокирует поток и не использует реальное время. Виртуальное время продвигается, когда вы явно двигаете его (`advanceTimeBy`, `advanceUntilIdle`, `runCurrent`) или когда планировщик обрабатывает запланированные задачи в рамках `runTest`. Если корутина использует другой реальный диспетчер, она не подчиняется виртуальному времени.

### currentTime

`currentTime` возвращает текущее виртуальное время тестового планировщика в миллисекундах:

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
- Продвигает виртуальное время на указанное количество миллисекунд.
- Выполняет все задачи с `delay`, запланированные до или на новом времени.
- Не выполняет корутины, запланированные после нового времени.

### advanceUntilIdle()

Выполняет все ожидающие корутины, пока не останется запланированных задач (при условии, что нет бесконечных циклов, постоянно планирующих новые события):

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
    assertEquals(400, currentTime) // Продвинуто до времени последнего события (400мс)
}
```

```kotlin
@Test
fun `advanceUntilIdle с конечным циклом`() = runTest {
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
- Последовательно продвигает виртуальное время к следующему запланированному событию.
- Выполняет это событие.
- Повторяет, пока не останется задач.
- Если задачи создают бесконечные новые события, `advanceUntilIdle` не завершится (или завершится с ошибкой в зависимости от конфигурации теста).

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
- Выполняет только корутины, запланированные на текущее время.
- НЕ продвигает виртуальное время.
- Полезно для тестирования немедленных эффектов и стартового поведения.

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
```

```kotlin
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
```

(Интерфейсы `Api`, `FakeApi`, `Data` предполагаются как тестовые заглушки.)

```kotlin
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
    // Связываем timeProvider с виртуальным временем планировщика runTest
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

    assertEquals(42, parallelResult1)
    assertEquals(42, parallelResult2)
    assertEquals(1000, parallelDuration) // Оба выполнились параллельно в терминах виртуального времени
}
```

### Подводные Камни Виртуального Времени

```kotlin
// НЕПРАВИЛЬНО: Использование Thread.sleep
@Test
fun `неправильно - Thread sleep`() = runTest {
    launch {
        Thread.sleep(1000) // Реально спит и блокирует поток!
        println("После сна")
    }

    advanceTimeBy(1000) // Не помогает для Thread.sleep
    // Тест реально ждёт или может зависнуть
}

// ПРАВИЛЬНО: Использование delay
@Test
fun `правильно - delay`() = runTest {
    launch {
        delay(1000) // Использует виртуальное время
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
    assertTrue(duration < 100) // Проверяем реальное время, а не виртуальное
}

// ПРАВИЛЬНО: Виртуальное время
@Test
fun `правильно - currentTime`() = runTest {
    val start = currentTime // Виртуальное время тестового планировщика
    delay(1000)
    val end = currentTime

    val duration = end - start
    assertEquals(1000, duration)
}

// НЕПРАВИЛЬНО: Блокирующие API
@Test
fun `неправильно - блокирующий API`() = runTest {
    launch {
        val result = blockingNetworkCall() // Блокирует поток, не управляется виртуальным временем
    }

    advanceUntilIdle() // Не разблокирует blockingNetworkCall
}

// ПРАВИЛЬНО: Приостанавливаемые API
@Test
fun `правильно - suspending API`() = runTest {
    launch {
        val result = suspendingNetworkCall() // Приостанавливается и управляется тестовым диспетчером
    }

    advanceUntilIdle() // Работает
}
```

### Резюме

**Функции виртуального времени**:
- **currentTime**: Получить текущее виртуальное время планировщика в миллисекундах.
- **advanceTimeBy(ms)**: Продвинуть время на указанную величину, выполнить запланированные на этом интервале корутины.
- **advanceUntilIdle()**: Выполнить все ожидающие корутины до отсутствия задач (если нет бесконечного планирования).
- **runCurrent()**: Выполнить только задачи текущего времени, не продвигая время.

**Ключевые принципы**:
1. `delay()` под тестовым диспетчером не использует реальное время.
2. Виртуальное время продвигается контролируемо: через `advanceTimeBy`, `advanceUntilIdle`, `runCurrent` и логику `runTest`.
3. Реальное время и блокирующие вызовы (`Thread.sleep`, `System.currentTimeMillis`, блокирующий IO) не контролируются виртуальным временем, их следует избегать или абстрагировать.
4. Тесты могут выполняться мгновенно независимо от количества задержек, если не используют блокирующие API и работают на тестовом диспетчере.
5. Тайминг детерминирован и управляем, если всё основано на корутинных примитивах и тестовом планировщике.

**Используйте advanceTimeBy когда**:
- Тестируете конкретные временные сценарии.
- Нужен точный контроль пошагового выполнения.
- Проверяете таймауты или интервалы.

**Используйте advanceUntilIdle когда**:
- Хотите выполнить всё до завершения.
- Не важны промежуточные отметки времени.
- Проверяете финальное состояние или полные цепочки операций.

**Используйте runCurrent когда**:
- Тестируете немедленные эффекты и стартовое поведение.
- Хотите выполнить синхронный код/обработчики, не продвигая время.

---

## Answer (EN)

Virtual time is a key feature of coroutine testing that lets you control time explicitly so tests complete instantly while simulating the passage of time. This makes tests fast, deterministic, and predictable.

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

    advanceTimeBy(10000) // Explicitly "advance" 10 seconds of virtual time (for delay under the TestDispatcher)

    assertEquals(10, timer.seconds)
}
```

(The Timer class is assumed to use delay internally and run on runTest's test dispatcher.)

### Virtual Time Basics

When using `runTest`, it installs a special test dispatcher/scheduler (TestDispatcher/TestScheduler) that operates on virtual time for coroutine-based delays, as long as coroutines run on that dispatcher.

```kotlin
@Test
fun `virtual time demonstration`() = runTest {
    println("Start time: $currentTime") // 0

    delay(1000)
    println("After 1s: $currentTime") // 1000

    delay(2000)
    println("After 3s total: $currentTime") // 3000

    // The test completes instantly in real time because virtual time is driven by the test scheduler.
}
```

**Key insight**: `delay()` under the test dispatcher does not block a thread or use real time. Virtual time is advanced when you drive the scheduler (`advanceTimeBy`, `advanceUntilIdle`, `runCurrent`) or when `runTest` processes scheduled tasks. If a coroutine uses another real dispatcher, it is not controlled by virtual time.

### currentTime

`currentTime` returns the current virtual time of the test scheduler in milliseconds:

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

Advances virtual time by the specified amount and executes coroutines scheduled within that interval:

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
- Advances virtual time by the given milliseconds.
- Executes all tasks scheduled at or before the new time.
- Does not execute tasks scheduled after the new time.

### advanceUntilIdle()

Executes all pending coroutines until there are no more scheduled tasks (as long as coroutines are not endlessly scheduling more work):

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
    assertEquals(400, currentTime) // Advanced to the time of the last event (400ms)
}
```

```kotlin
@Test
fun `advanceUntilIdle with finite loop`() = runTest {
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
- Repeatedly advances virtual time to the next scheduled event.
- Executes that event.
- Stops when no tasks remain.
- If coroutines keep scheduling new delayed work forever, `advanceUntilIdle` may not complete.

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
- Runs only tasks scheduled for the current virtual time.
- Does NOT advance virtual time.
- Useful for testing immediate effects and initial emissions.

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
```

```kotlin
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
```

(Api, FakeApi, and Data are assumed as test doubles.)

```kotlin
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
        val timeSinceLast = now - lastExecutionTime

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
    // Bind timeProvider to runTest's virtual scheduler clock
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

    assertEquals(42, parallelResult1)
    assertEquals(42, parallelResult2)
    assertEquals(1000, parallelDuration) // Both ran in parallel in terms of virtual time
}
```

### Virtual Time Gotchas

```kotlin
// WRONG: Using Thread.sleep
@Test
fun `wrong - Thread sleep`() = runTest {
    launch {
        Thread.sleep(1000) // Actually sleeps and blocks a thread!
        println("After sleep")
    }

    advanceTimeBy(1000) // Doesn't affect Thread.sleep
    // Test will really wait or may hang
}

// CORRECT: Using delay
@Test
fun `correct - delay`() = runTest {
    launch {
        delay(1000) // Uses virtual time
        println("After delay")
    }

    advanceTimeBy(1000) // Works instantly
}

// WRONG: Real time API
@Test
fun `wrong - System.currentTimeMillis`() = runTest {
    val start = System.currentTimeMillis() // Real time!
    delay(1000)
    val end = System.currentTimeMillis()

    val duration = end - start
    assertTrue(duration < 100) // This asserts real elapsed time, not virtual
}

// CORRECT: Virtual time
@Test
fun `correct - currentTime`() = runTest {
    val start = currentTime // Virtual test scheduler time
    delay(1000)
    val end = currentTime

    val duration = end - start
    assertEquals(1000, duration)
}

// WRONG: Blocking APIs
@Test
fun `wrong - blocking API`() = runTest {
    launch {
        val result = blockingNetworkCall() // Blocks a thread, not controlled by virtual time
    }

    advanceUntilIdle() // Cannot unblock blockingNetworkCall
}

// CORRECT: Suspending APIs
@Test
fun `correct - suspending API`() = runTest {
    launch {
        val result = suspendingNetworkCall() // Properly suspends under test dispatcher
    }

    advanceUntilIdle() // Works
}
```

### Summary

**Virtual time functions**:
- **currentTime**: Get current virtual scheduler time in milliseconds.
- **advanceTimeBy(ms)**: Advance time by a specific amount, run scheduled coroutines in that interval.
- **advanceUntilIdle()**: Run all pending coroutines until none remain (assuming no infinite rescheduling).
- **runCurrent()**: Run only tasks scheduled for the current time without advancing time.

**Key principles**:
1. `delay()` under the test dispatcher uses virtual time and is non-blocking.
2. Virtual time is advanced in a controlled way: via `advanceTimeBy`, `advanceUntilIdle`, `runCurrent`, and `runTest`'s scheduler.
3. Real-time based APIs (`Thread.sleep`, `System.currentTimeMillis`, blocking IO) are not controlled by virtual time and should be avoided or abstracted.
4. Tests can run instantly regardless of logical delays when they rely on coroutine primitives and run on the test dispatcher.
5. Timing is deterministic and controllable when all time-dependent code is expressed via the test scheduler.

**Use advanceTimeBy when**:
- Testing specific timing scenarios.
- You need precise stepwise control over execution.
- Testing timeouts or fixed intervals.

**Use advanceUntilIdle when**:
- You want to run everything to completion.
- Intermediate timestamps are irrelevant.
- Testing final/end state or full flows.

**Use runCurrent when**:
- Testing immediate effects and startup behavior.
- You want to run synchronous-looking work without advancing time.

---

## Дополнительные вопросы (RU)

1. Как виртуальное время взаимодействует с `Dispatchers.IO` и другими реальными диспетчерами?
2. Можно ли сочетать виртуальное время и реальные задержки в одном тесте, и чем это чревато?
3. Как тестировать код, зависящий от `System.currentTimeMillis()` или других реальных источников времени?
4. Что произойдёт, если вызвать `Thread.sleep` внутри `runTest` и почему это проблема?
5. Как виртуальное время применяется при тестировании операторов `Flow` и горячих потоков?

---

## Follow-ups

1. How does virtual time interact with `Dispatchers.IO` and other real dispatchers?
2. Can you mix virtual time with real delays in a single test, and what are the pitfalls?
3. How can you test code that depends on `System.currentTimeMillis()` or other real time sources?
4. What happens when you use `Thread.sleep` inside `runTest`, and why is it problematic?
5. How is virtual time applied when testing `Flow` operators and hot streams?

---

## Ссылки (RU)

- [Testing Coroutines - Kotlin Docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [runTest Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/run-test.html)
- [[c-kotlin]]
- [[c-coroutines]]

---

## References

- [Testing Coroutines - Kotlin Docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [runTest Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/run-test.html)
- [[c-kotlin]]
- [[c-coroutines]]

---

## Связанные вопросы (RU)

- [[q-testing-coroutines-runtest--kotlin--medium]] — основы `runTest`
- [[q-testing-flow-operators--kotlin--hard]] — тестирование операторов `Flow`
- [[q-testing-coroutine-cancellation--kotlin--medium]] — тестирование отмены корутин

---

## Related Questions

- [[q-testing-coroutines-runtest--kotlin--medium]] - runTest basics
- [[q-testing-flow-operators--kotlin--hard]] - Testing `Flow` operators
- [[q-testing-coroutine-cancellation--kotlin--medium]] - Testing cancellation

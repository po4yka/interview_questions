---
id: kotlin-056
title: "Advanced Flow Testing / Продвинутое тестирование Flow"
aliases: ["Advanced Flow Testing", "Продвинутое тестирование Flow"]
topic: kotlin
subtopics: [coroutines, flow]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions
status: draft
moc: moc-kotlin
related: [c-flow, q-kotlin-flow-basics--kotlin--medium, q-testing-viewmodels-coroutines--kotlin--medium]
created: 2025-10-11
updated: 2025-11-11
tags: [async, difficulty/hard, flow, kotlin, testing, testscope]

date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> Протестируйте сложные цепочки `Flow` с задержками и множественными испусканиями. Используйте `TestScope`, `TestDispatcher` и виртуальное время для детерминированного тестирования.

# Question (EN)
> Test complex `Flow` chains with delays and multiple emissions. Use `TestScope`, `TestDispatcher`, and virtual time for deterministic testing.

## Ответ (RU)

Тестирование `Flow` требует специальных инструментов для детерминированного контроля асинхронного поведения, задержек и тайминг-зависимой логики. Используются `runTest` (который создаёт `TestScope` и `TestDispatcher`), а также такие утилиты как `advanceTimeBy` и `advanceUntilIdle`. Для проверки значений удобно применять библиотеку Turbine.

> См. также: [[c-flow]]

### Зависимости Для Тестов

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("app.cash.turbine:turbine:1.0.0") // Библиотека для тестирования Flow
    testImplementation("junit:junit:4.13.2")
}
```

### TestScope И TestDispatcher

`runTest` создаёт `TestScope` и `TestDispatcher`, включая виртуальное время.

```kotlin
@Test
fun `test flow with delays using virtual time`() = runTest {
    val flow = flow {
        emit(1)
        delay(1000) // Виртуальная задержка
        emit(2)
        delay(1000)
        emit(3)
    }

    val results = mutableListOf<Int>()

    val job = launch {
        flow.collect { results.add(it) }
    }

    // Быстро проходим все задержки
    advanceUntilIdle()

    job.cancel()

    assertEquals(listOf(1, 2, 3), results)
    // Тест завершается мгновенно, несмотря на 2000 мс задержек.
}
```

Важно: `advanceTimeBy` / `advanceUntilIdle` доступны в контексте `runTest` / `TestScope` и применяются для управления виртуальным временем в самих тестах. При использовании Turbine (`flow.test { ... }`) виртуальное время также контролируется через `runTest`, но функции продвижения времени вызываются снаружи `test {}` или через отдельный `TestScope`, так как `test` использует свой собственный scope.

### Тестирование С Turbine

```kotlin
@Test
fun `test flow emissions with turbine`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    // Продвигаем виртуальное время перед проверкой, если есть задержки
    advanceUntilIdle()

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

`flow.test {}` запускается с использованием тестового диспетчера (например, из `runTest`), однако управление виртуальным временем делайте на уровне окружения (`runTest` / `TestScope`), а не через вызов `advanceTimeBy` / `advanceUntilIdle` внутри лямбды Turbine.

### Тестирование Преобразований `Flow`

```kotlin
class UserRepository(private val api: UserApi) {
    fun getUserFlow(userId: Int): Flow<User> = flow {
        emit(api.getUser(userId))
    }
        .retry(3)
        .catch { emit(User.DEFAULT) }
}

@Test
fun `test user flow with retry`() = runTest {
    var attemptCount = 0
    val mockApi = object : UserApi {
        override suspend fun getUser(id: Int): User {
            attemptCount++
            if (attemptCount < 3) {
                throw IOException("Network error")
            }
            return User(id, "John")
        }
    }

    val repository = UserRepository(mockApi)

    repository.getUserFlow(123).test {
        val user = awaitItem()
        assertEquals("John", user.name)
        assertEquals(3, attemptCount) // 1 успешный + 2 неуспешных запроса = 3 попытки
        awaitComplete()
    }
}
```

### Тестирование `StateFlow`

```kotlin
class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() { _count.value++ }
    fun decrement() { _count.value-- }
}

@Test
fun `test stateflow updates`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        assertEquals(0, awaitItem()) // Начальное значение

        viewModel.increment()
        assertEquals(1, awaitItem())

        viewModel.increment()
        assertEquals(2, awaitItem())

        viewModel.decrement()
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование `SharedFlow`

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun post(event: Event) {
        _events.emit(event)
    }
}

@Test
fun `test sharedflow broadcasts to multiple collectors`() = runTest {
    val eventBus = EventBus()

    val collector1 = mutableListOf<Event>()
    val collector2 = mutableListOf<Event>()

    val job1 = launch { eventBus.events.collect { collector1.add(it) } }
    val job2 = launch { eventBus.events.collect { collector2.add(it) } }

    eventBus.post(Event.UserLoggedIn(123))
    eventBus.post(Event.MessageReceived("Hello"))

    advanceUntilIdle()

    assertEquals(2, collector1.size)
    assertEquals(2, collector2.size)

    job1.cancel()
    job2.cancel()
}
```

### Тестирование Обработки Ошибок

```kotlin
@Test
fun `test flow error handling with catch`() = runTest {
    val flow = flow {
        emit(1)
        emit(2)
        throw IOException("Network error")
    }
        .catch {
            emit(-1) // Фолбэк-значение
        }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(-1, awaitItem()) // Фолбэк
        awaitComplete()
    }
}

@Test
fun `test flow propagates uncaught exception`() = runTest {
    val flow = flow {
        emit(1)
        throw IllegalStateException("Critical error")
    }

    flow.test {
        assertEquals(1, awaitItem())
        val error = awaitError()
        assertTrue(error is IllegalStateException)
        assertEquals("Critical error", error.message)
    }
}
```

### Тестирование Холодных И Горячих `Flow`

```kotlin
@Test
fun `test cold flow creates new stream per collector`() = runTest {
    var collectorCount = 0

    val coldFlow = flow {
        collectorCount++
        emit(collectorCount)
    }

    coldFlow.test {
        assertEquals(1, awaitItem())
        awaitComplete()
    }

    coldFlow.test {
        assertEquals(2, awaitItem()) // Новое выполнение
        awaitComplete()
    }
}

@Test
fun `test hot flow shares stream between collectors`() = runTest {
    val coldFlow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    val hotFlow = coldFlow.shareIn(
        scope = this, // TestScope из runTest
        started = SharingStarted.Eagerly,
        replay = 1
    )

    advanceTimeBy(150) // Даем сгенерировать значения во времени

    hotFlow.test {
        // Получаем последнее значение (replay) на момент подписки
        assertEquals(2, awaitItem())
        // И следующее новое значение
        assertEquals(3, awaitItem())
        expectNoEvents()
    }
}
```

### Тестирование Сложных Сценариев (`debounce`, отмена)

```kotlin
class SearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

@Test
fun `test search debouncing`() = runTest {
    val mockRepo = object : SearchRepository {
        override fun search(query: String): Flow<List<Result>> = flow {
            delay(100)
            emit(listOf(Result(query)))
        }
    }

    val viewModel = SearchViewModel(mockRepo)

    viewModel.searchResults.test {
        assertEquals(emptyList<Result>(), awaitItem()) // Начальное значение

        // Быстрая смена запросов — срабатывает debounce
        viewModel.onSearchQueryChanged("kot")
        advanceTimeBy(100)
        expectNoEvents()

        viewModel.onSearchQueryChanged("kotl")
        advanceTimeBy(100)
        expectNoEvents()

        viewModel.onSearchQueryChanged("kotlin")
        advanceTimeBy(300) // debounce
        advanceTimeBy(100) // задержка репозитория

        val results = awaitItem()
        assertEquals(1, results.size)
        assertEquals("kotlin", results[0].query)

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `test search cancellation`() = runTest {
    var searchCount = 0

    val mockRepo = object : SearchRepository {
        override fun search(query: String): Flow<List<Result>> = flow {
            searchCount++
            delay(500)
            emit(listOf(Result(query)))
        }
    }

    val viewModel = SearchViewModel(mockRepo)

    viewModel.searchResults.test {
        awaitItem() // Начальное значение

        viewModel.onSearchQueryChanged("kotlin")
        advanceTimeBy(300) // debounce
        advanceTimeBy(100) // старт первого поиска

        // Новый запрос до завершения первого поиска — предыдущий отменяется flatMapLatest
        viewModel.onSearchQueryChanged("java")
        advanceTimeBy(300) // debounce для второго запроса
        advanceTimeBy(500) // завершение второго поиска

        val results = awaitItem()
        assertEquals("java", results[0].query)
        assertEquals(2, searchCount)

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование Backpressure (`buffer`, `conflate`)

```kotlin
@Test
fun `test buffer strategy`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(10)
        }
    }
        .buffer(3)

    val results = mutableListOf<Int>()

    flow.collect {
        results.add(it)
        delay(50) // Медленный потребитель (виртуальное время)
    }

    // Благодаря виртуальному времени тест завершается быстро и мы получаем все элементы
    assertEquals((0..9).toList(), results)
}

@Test
fun `test conflate drops intermediate values`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(10)
        }
    }
        .conflate()

    val results = mutableListOf<Int>()

    flow.collect {
        results.add(it)
        delay(50)
    }

    // Из-за conflate часть значений будет пропущена
    assertTrue(results.size < 10)
    assertTrue(results.contains(0)) // Первое
    assertTrue(results.contains(9)) // Последнее
}
```

### Лучшие Практики

1. Используйте `runTest` для тестов корутин, чтобы получить `TestScope`, `TestDispatcher` и виртуальное время.
2. Используйте Turbine (`flow.test { ... }`) для проверки всех испусканий, ошибок и завершения.
3. Всегда проверяйте все ожидаемые элементы и завершение (`awaitComplete()`), а также ошибки (`awaitError()`) там, где это важно.
4. Используйте виртуальное время (`advanceTimeBy`, `advanceUntilIdle`) для тестов с `delay` и операторами времени (`debounce`, `timeout`), вместо реальных задержек, управляя им из `runTest` / `TestScope`.
5. Тестируйте сложные сценарии: последовательные операторы, отмену (`flatMapLatest`), поведение холодных и горячих потоков (`StateFlow`, `SharedFlow`), backpressure (`buffer`, `conflate`).
6. Явно покрывайте сценарии с повторными попытками (`retry`), обработкой ошибок (`catch`), распространением необработанных исключений и конкурирующими подписками.

### Распространенные Ошибки

1. Неиспользование `runTest` и работа с реальными задержками, что делает тесты медленными и нестабильными.
2. Забывают продвигать виртуальное время (`advanceTimeBy` / `advanceUntilIdle`) для `delay` и операторов времени.
3. Не проверяют завершение или ошибку (`awaitComplete()` / `awaitError()`), оставляя возможные подвисания или некорректное поведение незамеченными.
4. Смешивают `runBlocking` и тестовые диспетчеры, что приводит к неконсистентному поведению.

**Краткое содержание (RU)**: Продвинутое тестирование `Flow` опирается на `runTest` / `TestScope`, `TestDispatcher` и виртуальное время для детерминированных и быстрых тестов. Turbine упрощает проверку испусканий, ошибок и завершения. Следует покрывать сценарии с задержками, отменой, backpressure и различием холодных / горячих потоков.

---

## Answer (EN)

Testing `Flow`s requires dedicated tools to control asynchronous behavior, delays, and timing-dependent logic deterministically. Use `runTest` (which gives you a `TestScope` with a `TestDispatcher`), virtual time (`advanceTimeBy`, `advanceUntilIdle`), and Turbine for concise `Flow` assertions.

### Test Dependencies

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("app.cash.turbine:turbine:1.0.0") // Flow testing library
    testImplementation("junit:junit:4.13.2")
}
```

### TestScope and TestDispatcher

`runTest` creates a `TestScope` and `TestDispatcher`, enabling virtual time.

```kotlin
@Test
fun `test flow with delays using virtual time`() = runTest {
    val flow = flow {
        emit(1)
        delay(1000) // Virtual delay
        emit(2)
        delay(1000)
        emit(3)
    }

    val results = mutableListOf<Int>()

    val job = launch {
        flow.collect { results.add(it) }
    }

    // Fast-forward through all delays
    advanceUntilIdle()

    job.cancel()

    assertEquals(listOf(1, 2, 3), results)
    // Test completes instantly despite 2000ms of delays.
}
```

Important: `advanceTimeBy` / `advanceUntilIdle` are available in the `runTest` / `TestScope` context and are used to control virtual time in your tests. When using Turbine (`flow.test { ... }`), virtual time is still driven by the surrounding `runTest`, but you typically advance time outside the `test {}` block or via a separate `TestScope`, because `test` runs in its own scope.

### Testing with Turbine

```kotlin
@Test
fun `test flow emissions with turbine`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    // Advance virtual time before assertions when delays are involved
    advanceUntilIdle()

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

`flow.test {}` uses the test dispatcher (e.g., from `runTest`), but time control remains external: call `advanceTimeBy` / `advanceUntilIdle` on the surrounding test scope rather than from inside the Turbine lambda.

### Testing `Flow` Transformations

```kotlin
class UserRepository(private val api: UserApi) {
    fun getUserFlow(userId: Int): Flow<User> = flow {
        emit(api.getUser(userId))
    }
        .retry(3)
        .catch { emit(User.DEFAULT) }
}

@Test
fun `test user flow with retry`() = runTest {
    var attemptCount = 0
    val mockApi = object : UserApi {
        override suspend fun getUser(id: Int): User {
            attemptCount++
            if (attemptCount < 3) {
                throw IOException("Network error")
            }
            return User(id, "John")
        }
    }

    val repository = UserRepository(mockApi)

    repository.getUserFlow(123).test {
        val user = awaitItem()
        assertEquals("John", user.name)
        assertEquals(3, attemptCount) // 1 success + 2 failed attempts = 3 total
        awaitComplete()
    }
}
```

### Testing `StateFlow`

```kotlin
class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() { _count.value++ }
    fun decrement() { _count.value-- }
}

@Test
fun `test stateflow updates`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        // Initial value
        assertEquals(0, awaitItem())

        viewModel.increment()
        assertEquals(1, awaitItem())

        viewModel.increment()
        assertEquals(2, awaitItem())

        viewModel.decrement()
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing `SharedFlow`

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun post(event: Event) {
        _events.emit(event)
    }
}

@Test
fun `test sharedflow broadcasts to multiple collectors`() = runTest {
    val eventBus = EventBus()

    val collector1 = mutableListOf<Event>()
    val collector2 = mutableListOf<Event>()

    val job1 = launch { eventBus.events.collect { collector1.add(it) } }
    val job2 = launch { eventBus.events.collect { collector2.add(it) } }

    eventBus.post(Event.UserLoggedIn(123))
    eventBus.post(Event.MessageReceived("Hello"))

    advanceUntilIdle()

    assertEquals(2, collector1.size)
    assertEquals(2, collector2.size)

    job1.cancel()
    job2.cancel()
}
```

### Testing Error Handling

```kotlin
@Test
fun `test flow error handling with catch`() = runTest {
    val flow = flow {
        emit(1)
        emit(2)
        throw IOException("Network error")
    }
        .catch {
            emit(-1) // Fallback value
        }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(-1, awaitItem()) // Fallback
        awaitComplete()
    }
}

@Test
fun `test flow propagates uncaught exception`() = runTest {
    val flow = flow {
        emit(1)
        throw IllegalStateException("Critical error")
    }

    flow.test {
        assertEquals(1, awaitItem())
        val error = awaitError()
        assertTrue(error is IllegalStateException)
        assertEquals("Critical error", error.message)
    }
}
```

### Testing Cold Vs Hot `Flow`s

```kotlin
@Test
fun `test cold flow creates new stream per collector`() = runTest {
    var collectorCount = 0

    val coldFlow = flow {
        collectorCount++
        emit(collectorCount)
    }

    coldFlow.test {
        assertEquals(1, awaitItem())
        awaitComplete()
    }

    coldFlow.test {
        assertEquals(2, awaitItem()) // New execution
        awaitComplete()
    }
}

@Test
fun `test hot flow shares stream between collectors`() = runTest {
    val coldFlow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
        emit(3)
    }

    val hotFlow = coldFlow.shareIn(
        scope = this, // TestScope from runTest
        started = SharingStarted.Eagerly,
        replay = 1
    )

    advanceTimeBy(150) // Let it emit some values with virtual time

    hotFlow.test {
        // Gets replay of latest value at subscription time
        assertEquals(2, awaitItem())
        // Then receives new emission
        assertEquals(3, awaitItem())
        expectNoEvents()
    }
}
```

### Testing Complex Scenarios (Debounce, Cancellation)

```kotlin
class SearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

@Test
fun `test search debouncing`() = runTest {
    val mockRepo = object : SearchRepository {
        override fun search(query: String): Flow<List<Result>> = flow {
            delay(100)
            emit(listOf(Result(query)))
        }
    }

    val viewModel = SearchViewModel(mockRepo)

    viewModel.searchResults.test {
        assertEquals(emptyList<Result>(), awaitItem()) // Initial

        // Type quickly - should debounce
        viewModel.onSearchQueryChanged("kot")
        advanceTimeBy(100)
        expectNoEvents()

        viewModel.onSearchQueryChanged("kotl")
        advanceTimeBy(100)
        expectNoEvents()

        viewModel.onSearchQueryChanged("kotlin")
        advanceTimeBy(300) // Debounce time passed
        advanceTimeBy(100) // Repository delay

        val results = awaitItem()
        assertEquals(1, results.size)
        assertEquals("kotlin", results[0].query)

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `test search cancellation`() = runTest {
    var searchCount = 0

    val mockRepo = object : SearchRepository {
        override fun search(query: String): Flow<List<Result>> = flow {
            searchCount++
            delay(500)
            emit(listOf(Result(query)))
        }
    }

    val viewModel = SearchViewModel(mockRepo)

    viewModel.searchResults.test {
        awaitItem() // Initial

        viewModel.onSearchQueryChanged("kotlin")
        advanceTimeBy(300) // Pass debounce
        advanceTimeBy(100) // Start first search

        // New query before first search completes
        viewModel.onSearchQueryChanged("java")
        advanceTimeBy(300) // Debounce for second query
        advanceTimeBy(500) // Complete second search

        val results = awaitItem()
        assertEquals("java", results[0].query)
        assertEquals(2, searchCount) // Both searches started; only latest result observed

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing Backpressure

```kotlin
@Test
fun `test buffer strategy`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(10)
        }
    }
        .buffer(3)

    val results = mutableListOf<Int>()

    flow.collect {
        results.add(it)
        delay(50) // Simulate slow collector (virtual time)
    }

    // With virtual time, the test remains fast and all items are received
    assertEquals((0..9).toList(), results)
}

@Test
fun `test conflate drops intermediate values`() = runTest {
    val flow = flow {
        repeat(10) {
            emit(it)
            delay(10)
        }
    }
        .conflate()

    val results = mutableListOf<Int>()

    flow.collect {
        results.add(it)
        delay(50)
    }

    // Only some values should be collected due to conflation
    assertTrue(results.size < 10)
    assertTrue(results.contains(0)) // First
    assertTrue(results.contains(9)) // Last
}
```

### Best Practices

1. Use `runTest` for coroutine tests to get `TestScope`, `TestDispatcher` and virtual time.
2. Use Turbine (`flow.test { ... }`) for checking all emissions, errors, and completion.
3. Always assert all expected items and completion (`awaitComplete()`), and use `awaitError()` where relevant.
4. Use virtual time (`advanceTimeBy`, `advanceUntilIdle`) for `delay` and time-based operators (`debounce`, `timeout`) instead of real delays, driving it from `runTest` / `TestScope`.
5. Test complex scenarios: chained operators, cancellation (`flatMapLatest`), cold vs hot `Flow`s (`StateFlow`, `SharedFlow`), and backpressure (`buffer`, `conflate`).
6. Explicitly cover retries (`retry`), error handling (`catch`), uncaught exception propagation, and competing subscriptions.

### Common Pitfalls

1. Not using `runTest` and relying on real delays, making tests slow and flaky.
2. Forgetting to advance virtual time (`advanceTimeBy` / `advanceUntilIdle`) for `delay` and time-based operators.
3. Not verifying completion or error (`awaitComplete()` / `awaitError()`), leaving hangs or incorrect behavior undetected.
4. Mixing `runBlocking` with test dispatchers, causing inconsistent behavior.

**English Summary**: Advanced `Flow` testing uses `runTest` / `TestScope`, `TestDispatcher`, and virtual time to make tests deterministic and fast. Turbine simplifies checking emissions, errors, and completion. Cover scenarios with delays, cancellation, backpressure, and cold vs hot flows.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали этот подход на практике?
- Какие распространенные ошибки следует избегать?

## Follow-ups (EN)

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Testing Kotlin coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Turbine - `Flow` testing library](https://github.com/cashapp/turbine)
- [Testing `Flows` - Android Developers](https://developer.android.com/kotlin/flow/test)

## References (EN)

- [Testing Kotlin coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Turbine - `Flow` testing library](https://github.com/cashapp/turbine)
- [Testing `Flows` - Android Developers](https://developer.android.com/kotlin/flow/test)

## Related Questions

- [[q-kotlin-flow-basics--kotlin--medium]]
- [[q-testing-viewmodels-coroutines--kotlin--medium]]

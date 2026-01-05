---
id: android-312
title: "Testing Coroutines Flow / Тестирование Coroutines Flow"
aliases: ["Testing Coroutines Flow", "Тестирование Coroutines Flow"]
topic: android
subtopics: [coroutines, flow, testing-unit]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-coroutines, q-singleton-scope-binding--android--medium, q-test-coverage-quality-metrics--android--medium, q-what-design-systems-in-android-have-you-worked-with--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/coroutines, android/flow, android/testing-unit, async, coroutines, difficulty/hard, flow, test-dispatcher, turbine]

---
# Вопрос (RU)

> Как тестировать suspend функции, `StateFlow` и `SharedFlow`? Объясните TestDispatcher, runTest и библиотеку turbine.

# Question (EN)

> How do you test suspend functions, `StateFlow`, and `SharedFlow`? Explain TestDispatcher, runTest, and turbine library.

---

## Ответ (RU)

Тестирование корутин и потоков требует специальных утилит для контроля виртуального времени и планирования. **TestDispatcher**, **runTest** и **Turbine** — ключевые инструменты для детерминированного асинхронного тестирования.

### Краткий Ответ

- Используйте `runTest` и тестовые диспетчеры (`StandardTestDispatcher`, `UnconfinedTestDispatcher`) для управления выполнением и виртуальным временем.
- Для `StateFlow` читайте `value` напрямую или используйте Turbine; учитывайте начальное значение.
- Для `SharedFlow` начинайте сбор до эмиссий и используйте один и тот же тестовый планировщик.
- Для `Flow`/горутин применяйте Turbine для удобного ожидания элементов, завершения и ошибок.

### Подробный Ответ

### TestDispatcher Типы

**StandardTestDispatcher** — по умолчанию использует тестовый планировщик: корутины, запущенные внутри `runTest`, планируются и выполняются пошагово только при явном продвижении планировщика (`runCurrent`, управление временем и т.п.), что позволяет детерминированно контролировать выполнение без реального времени.

```kotlin
@Test
fun testStandardDispatcher() = runTest {
    launch {
        println("1")
    }
    println("2") // ✅ Выполнится первым, корутина внутри launch будет только запланирована
    runCurrent() // Запускаем отложенные задачи "на сейчас"
    // Вывод: 2, 1
}
```

**UnconfinedTestDispatcher** — задачи выполняются немедленно в текущем контексте планировщика `runTest`, без необходимости явного продвижения времени, что делает поведение ближе к `Dispatchers.Unconfined` (но всё ещё управляемым тестовым планировщиком).

```kotlin
@Test
fun testUnconfinedDispatcher() = runTest(UnconfinedTestDispatcher(testScheduler)) {
    launch {
        println("1") // ✅ Выполнится до следующей строки
    }
    println("2")
    // Вывод: 1, 2
}
```

### Контроль Времени

```kotlin
@Test
fun testTimeControl() = runTest {
    var value = 0

    launch {
        delay(1000)
        value = 1
    }

    assertEquals(0, value)
    advanceTimeBy(1000) // ✅ Продвинуть виртуальное время на 1000 мс
    assertEquals(1, value)
}
```

**Методы управления временем (virtual time API):**
- `runCurrent()` — немедленно выполнить все задачи, запланированные "на сейчас".
- `advanceTimeBy(ms)` — продвинуть виртуальное время и выполнить задачи с `delay` в этом интервале.
- `advanceUntilIdle()` — выполнять задачи и продвигать виртуальное время, пока очередь не опустеет.

### Тестирование `StateFlow`

**`StateFlow`** всегда хранит текущее значение и немедленно его возвращает.

```kotlin
data class User(val id: Int, val name: String)

class UserViewModel {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user

    suspend fun loadUser(id: Int) {
        delay(1000)
        _user.value = User(id, "John")
    }
}

@Test
fun testStateFlow() = runTest {
    val viewModel = UserViewModel()

    assertEquals(null, viewModel.user.value) // ✅ Текущее значение доступно сразу

    viewModel.loadUser(1) // suspend, контролируется runTest

    assertEquals("John", viewModel.user.value?.name)
}
```

(В реальных `ViewModel` обычно инжектируется `CoroutineDispatcher` и/или репозиторий, и тесты используют `StandardTestDispatcher` через `runTest` или правило.)

### Тестирование `SharedFlow`

**`SharedFlow`** не имеет начального значения, поэтому в тестах важно начать сбор ДО эмиссии. Не смешивайте разные тестовые диспетчеры/планировщики без необходимости.

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events

    suspend fun sendEvent(event: Event) {
        _events.emit(event)
    }
}

@Test
fun testSharedFlow() = runTest {
    val eventBus = EventBus()
    val emissions = mutableListOf<Event>()

    // ✅ Начать сбор ДО эмиссии, используя тот же планировщик runTest
    val job = launch {
        eventBus.events.collect { emissions.add(it) }
    }

    eventBus.sendEvent(Event.UserLoggedIn)

    job.cancel()

    assertEquals(listOf(Event.UserLoggedIn), emissions)
}
```

### Библиотека Turbine

**Turbine** упрощает тестирование `Flow` с чистым API.

```kotlin
@Test
fun testFlowWithTurbine() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
    }

    flow.test {
        assertEquals(1, awaitItem()) // ✅ Чистый API
        assertEquals(2, awaitItem())
        awaitComplete()
    }
}
```

**`StateFlow` с Turbine:**

```kotlin
@Test
fun testStateFlowWithTurbine() = runTest {
    val viewModel = UserViewModel()

    viewModel.user.test {
        assertEquals(null, awaitItem()) // ✅ Первая эмиссия — текущее значение

        viewModel.loadUser(1)

        val user = awaitItem()
        assertEquals("John", user?.name)

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Возможности Turbine:**
- `awaitItem()` — ждать следующую эмиссию.
- `skipItems(n)` — пропустить n эмиссий.
- `expectNoEvents()` — проверить отсутствие событий.
- `awaitError()` — ждать ошибку.
- `awaitComplete()` — ждать завершения.

### Тестирование `ViewModel`

```kotlin
class UserViewModelWithRepo(
    private val repository: UserRepository,
    private val dispatcher: CoroutineDispatcher
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events

    fun loadUser(id: Int) {
        viewModelScope.launch(dispatcher) {
            val user = repository.fetchUser(id)
            _uiState.value = UiState.Success(user)
            _events.emit(Event.UserLoaded)
        }
    }
}

@Test
fun testViewModel() = runTest {
    val repository = mockk<UserRepository>()
    coEvery { repository.fetchUser(1) } returns User(1, "John")

    val viewModel = UserViewModelWithRepo(repository, StandardTestDispatcher(testScheduler))

    // ✅ Тестируем uiState и events с помощью отдельных Turbine-блоков

    viewModel.uiState.test {
        assertEquals(UiState.Loading, awaitItem())

        viewModel.loadUser(1)

        val successState = awaitItem() as UiState.Success
        assertEquals("John", successState.user.name)

        cancelAndIgnoreRemainingEvents()
    }

    viewModel.events.test {
        assertEquals(Event.UserLoaded, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Лучшие Практики

**1. Используйте `runTest`:**

```kotlin
// ✅ DO
@Test
fun test() = runTest { /* ... */ }

// ❌ DON'T — медленнее, нет контроля виртуального времени
@Test
fun test() = runBlocking { /* ... */ }
```

**2. Настраивайте Main dispatcher для UI-кода (`ViewModel` и т.п.):**

```kotlin
// ✅ DO — правило, которое конфигурирует Dispatchers.Main под тестовый диспетчер
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// ✅ Вариант без правила (менее удобен):
@Before
fun setUp() {
    Dispatchers.setMain(StandardTestDispatcher())
}

@After
fun tearDown() {
    Dispatchers.resetMain()
}
```

**3. Используйте Turbine для `Flow`:**

```kotlin
// ✅ DO
flow.test {
    assertEquals(1, awaitItem())
    awaitComplete()
}

// ❌ DON'T — ручной сбор без необходимости
val emissions = mutableListOf<Int>()
val job = launch { flow.collect { emissions.add(it) } }
job.cancel()
```

---

## Answer (EN)

Testing coroutines and flows requires dedicated utilities to control virtual time and scheduling. **TestDispatcher**, **runTest**, and **Turbine** are essential tools for deterministic async testing.

### Short Version

- Use `runTest` with `StandardTestDispatcher`/`UnconfinedTestDispatcher` to control execution and virtual time.
- For `StateFlow`, read `value` directly or use Turbine; account for the initial value.
- For `SharedFlow`, start collecting before emitting and keep a single scheduler.
- Use Turbine to assert emissions, completion, and errors from `Flow`/coroutines.

### Detailed Version

### TestDispatcher Types

**StandardTestDispatcher** — by default uses the test scheduler: coroutines launched inside `runTest` are scheduled and progressed only when you explicitly advance the scheduler (`runCurrent`, time control, etc.), giving deterministic control without real time.

```kotlin
@Test
fun testStandardDispatcher() = runTest {
    launch {
        println("1")
    }
    println("2") // ✅ Executes first; the launched coroutine is only scheduled
    runCurrent() // Run tasks scheduled for "now"
    // Output: 2, 1
}
```

**UnconfinedTestDispatcher** — runs tasks immediately in the current `runTest` scheduler context, similar in spirit to `Dispatchers.Unconfined` but still bound to the test scheduler.

```kotlin
@Test
fun testUnconfinedDispatcher() = runTest(UnconfinedTestDispatcher(testScheduler)) {
    launch {
        println("1") // ✅ Executes before the next line
    }
    println("2")
    // Output: 1, 2
}
```

### Time Control

```kotlin
@Test
fun testTimeControl() = runTest {
    var value = 0

    launch {
        delay(1000)
        value = 1
    }

    assertEquals(0, value)
    advanceTimeBy(1000) // ✅ Advance virtual time by 1000 ms
    assertEquals(1, value)
}
```

**Time control methods (virtual time API):**
- `runCurrent()` — run all tasks scheduled for the current time.
- `advanceTimeBy(ms)` — move virtual time forward and run tasks whose delays expire within that window.
- `advanceUntilIdle()` — keep running tasks/advancing virtual time until there is nothing left.

### Testing `StateFlow`

**`StateFlow`** always holds a current value and exposes it immediately.

```kotlin
data class User(val id: Int, val name: String)

class UserViewModel {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user

    suspend fun loadUser(id: Int) {
        delay(1000)
        _user.value = User(id, "John")
    }
}

@Test
fun testStateFlow() = runTest {
    val viewModel = UserViewModel()

    assertEquals(null, viewModel.user.value) // ✅ Current value is immediately accessible

    viewModel.loadUser(1) // suspend, controlled by runTest

    assertEquals("John", viewModel.user.value?.name)
}
```

(In real ViewModels you typically inject a `CoroutineDispatcher` and/or repository and use a `StandardTestDispatcher` via `runTest` or a rule.)

### Testing `SharedFlow`

**`SharedFlow`** has no initial value; in tests you must start collecting BEFORE emitting. Avoid mixing different test dispatchers/schedulers unnecessarily.

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events

    suspend fun sendEvent(event: Event) {
        _events.emit(event)
    }
}

@Test
fun testSharedFlow() = runTest {
    val eventBus = EventBus()
    val emissions = mutableListOf<Event>()

    // ✅ Start collecting BEFORE emitting, using the same scheduler as runTest
    val job = launch {
        eventBus.events.collect { emissions.add(it) }
    }

    eventBus.sendEvent(Event.UserLoggedIn)

    job.cancel()

    assertEquals(listOf(Event.UserLoggedIn), emissions)
}
```

### Turbine Library

**Turbine** simplifies `Flow` testing with a clean API.

```kotlin
@Test
fun testFlowWithTurbine() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
    }

    flow.test {
        assertEquals(1, awaitItem()) // ✅ Clean API
        assertEquals(2, awaitItem())
        awaitComplete()
    }
}
```

**`StateFlow` with Turbine:**

```kotlin
@Test
fun testStateFlowWithTurbine() = runTest {
    val viewModel = UserViewModel()

    viewModel.user.test {
        assertEquals(null, awaitItem()) // ✅ First emission is current value

        viewModel.loadUser(1)

        val user = awaitItem()
        assertEquals("John", user?.name)

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Turbine capabilities:**
- `awaitItem()` — wait for the next emission.
- `skipItems(n)` — skip n emissions.
- `expectNoEvents()` — verify no events occurred.
- `awaitError()` — wait for an error.
- `awaitComplete()` — wait for completion.

### Testing `ViewModel`

```kotlin
class UserViewModelWithRepo(
    private val repository: UserRepository,
    private val dispatcher: CoroutineDispatcher
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events

    fun loadUser(id: Int) {
        viewModelScope.launch(dispatcher) {
            val user = repository.fetchUser(id)
            _uiState.value = UiState.Success(user)
            _events.emit(Event.UserLoaded)
        }
    }
}

@Test
fun testViewModel() = runTest {
    val repository = mockk<UserRepository>()
    coEvery { repository.fetchUser(1) } returns User(1, "John")

    val viewModel = UserViewModelWithRepo(repository, StandardTestDispatcher(testScheduler))

    // ✅ Test uiState and events using separate Turbine blocks

    viewModel.uiState.test {
        assertEquals(UiState.Loading, awaitItem())

        viewModel.loadUser(1)

        val successState = awaitItem() as UiState.Success
        assertEquals("John", successState.user.name)

        cancelAndIgnoreRemainingEvents()
    }

    viewModel.events.test {
        assertEquals(Event.UserLoaded, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Best Practices

**1. Use `runTest`:**

```kotlin
// ✅ DO
@Test
fun test() = runTest { /* ... */ }

// ❌ DON'T — slower, no virtual time control
@Test
fun test() = runBlocking { /* ... */ }
```

**2. Set Main dispatcher for UI-related code (`ViewModel`, etc.):**

```kotlin
// ✅ DO — a JUnit rule that sets Dispatchers.Main to a test dispatcher
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// ✅ Alternative without a rule (less convenient):
@Before
fun setUp() {
    Dispatchers.setMain(StandardTestDispatcher())
}

@After
fun tearDown() {
    Dispatchers.resetMain()
}
```

**3. Use Turbine for `Flow`:**

```kotlin
// ✅ DO
flow.test {
    assertEquals(1, awaitItem())
    awaitComplete()
}

// ❌ DON'T — manual collection when Turbine is available
val emissions = mutableListOf<Int>()
val job = launch { flow.collect { emissions.add(it) } }
job.cancel()
```

---

## Дополнительные Вопросы (RU)

- Как по-разному тестировать холодные и горячие `Flow`?
- В чем разница между `advanceTimeBy` и `advanceUntilIdle`?
- Как тестировать `Flow` с несколькими коллекторами?
- Когда использовать `StandardTestDispatcher` vs `UnconfinedTestDispatcher`?
- Как тестировать обработку ошибок во `Flow` с помощью Turbine?

## Follow-ups

- How do you handle testing cold vs hot flows differently?
- What's the difference between `advanceTimeBy` and `advanceUntilIdle`?
- How do you test flows with multiple collectors?
- When should you use `StandardTestDispatcher` vs `UnconfinedTestDispatcher`?
- How do you test error handling in flows with Turbine?

## Ссылки (RU)

- [[c-coroutines]]
- https://developer.android.com/kotlin/coroutines/test
- https://github.com/cashapp/turbine
- https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-test/

## References

- [[c-coroutines]]
- https://developer.android.com/kotlin/coroutines/test
- https://github.com/cashapp/turbine
- https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-test/

## Related Questions

### Prerequisites (Easier)

- [[q-testing-viewmodels-turbine--android--medium]] - Testing ViewModels with Turbine
- [[q-compose-testing--android--medium]] - Testing Compose UI
- Basic coroutines and flow understanding required

### Related (Same Level)

- [[q-singleton-scope-binding--android--medium]] - Dependency injection in tests
- [[q-what-design-systems-in-android-have-you-worked-with--android--medium]] - Testing design systems

### Advanced (Harder)

- [[q-test-coverage-quality-metrics--android--medium]] - Test coverage metrics
- Advanced testing strategies for complex async scenarios
- Performance testing with flows

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
related: [q-singleton-scope-binding--android--medium, q-test-coverage-quality-metrics--android--medium, q-what-design-systems-in-android-have-you-worked-with--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/coroutines, android/flow, android/testing-unit, async, coroutines, difficulty/hard, flow, test-dispatcher, turbine]
date created: Saturday, November 1st 2025, 12:47:05 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)

> Как тестировать suspend функции, StateFlow и SharedFlow? Объясните TestDispatcher, runTest и библиотеку turbine.

# Question (EN)

> How do you test suspend functions, StateFlow, and SharedFlow? Explain TestDispatcher, runTest, and turbine library.

---

## Ответ (RU)

Тестирование корутин и потоков требует специальных утилит для контроля времени и выполнения. **TestDispatcher**, **runTest** и **Turbine** — ключевые инструменты для детерминированного асинхронного тестирования.

### TestDispatcher Типы

**StandardTestDispatcher** - корутины не выполняются до явного продвижения времени:

```kotlin
@Test
fun testStandardDispatcher() = runTest {
    launch {
        println("1")
    }
    println("2") // ✅ Выполнится первым
    // Вывод: 2, 1
}
```

**UnconfinedTestDispatcher** - корутины выполняются немедленно:

```kotlin
@Test
fun testUnconfinedDispatcher() = runTest(UnconfinedTestDispatcher()) {
    launch {
        println("1") // ✅ Выполнится первым
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
    advanceTimeBy(1000) // ✅ Продвинуть время на 1000мс
    assertEquals(1, value)
}
```

**Методы управления временем:**
- `runCurrent()` - выполнить немедленно запланированные задачи
- `advanceTimeBy(ms)` - продвинуть время на указанный период
- `advanceUntilIdle()` - выполнить все оставшиеся задачи

### Тестирование StateFlow

**StateFlow** эмитирует текущее значение немедленно:

```kotlin
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

    viewModel.loadUser(1)

    assertEquals("John", viewModel.user.value?.name)
}
```

### Тестирование SharedFlow

**SharedFlow** не имеет начального значения, нужно начать сбор ДО эмиссии:

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

    // ✅ Начать сбор ДО эмиссии
    val job = launch(UnconfinedTestDispatcher()) {
        eventBus.events.collect { emissions.add(it) }
    }

    eventBus.sendEvent(Event.UserLoggedIn)

    job.cancel()

    assertEquals(Event.UserLoggedIn, emissions[0])
}
```

### Библиотека Turbine

**Turbine** упрощает тестирование Flow с чистым API:

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

**StateFlow с Turbine:**

```kotlin
@Test
fun testStateFlowWithTurbine() = runTest {
    val viewModel = UserViewModel()

    viewModel.user.test {
        assertEquals(null, awaitItem()) // ✅ Первая эмиссия - текущее значение

        viewModel.loadUser(1)

        val user = awaitItem()
        assertEquals("John", user?.name)

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Возможности Turbine:**
- `awaitItem()` - ждать следующую эмиссию
- `skipItems(n)` - пропустить n эмиссий
- `expectNoEvents()` - проверить отсутствие событий
- `awaitError()` - ждать ошибку
- `awaitComplete()` - ждать завершения

### Тестирование ViewModel

```kotlin
@Test
fun testViewModel() = runTest {
    val repository = mockk<UserRepository>()
    coEvery { repository.fetchUser(1) } returns User(1, "John")

    val viewModel = UserViewModel(repository)

    // ✅ Тестировать StateFlow и SharedFlow параллельно
    viewModel.uiState.test {
        assertEquals(UiState.Loading, awaitItem())

        viewModel.events.test {
            viewModel.loadUser(1)

            val successState = awaitItem() as UiState.Success
            assertEquals("John", successState.user.name)

            assertEquals(Event.UserLoaded, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Лучшие Практики

**1. Используйте runTest:**

```kotlin
// ✅ DO
@Test
fun test() = runTest { /* ... */ }

// ❌ DON'T - медленнее, нет контроля времени
@Test
fun test() = runBlocking { /* ... */ }
```

**2. Устанавливайте Main dispatcher:**

```kotlin
// ✅ DO
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// ❌ DON'T - ручная настройка
@Before
fun setUp() {
    Dispatchers.setMain(testDispatcher)
}
```

**3. Используйте Turbine для Flow:**

```kotlin
// ✅ DO
flow.test {
    assertEquals(1, awaitItem())
    awaitComplete()
}

// ❌ DON'T - ручной сбор
val emissions = mutableListOf<Int>()
val job = launch { flow.collect { emissions.add(it) } }
job.cancel()
```

---

## Answer (EN)

Testing coroutines and flows requires special utilities to control time and execution. **TestDispatcher**, **runTest**, and **Turbine** are essential tools for deterministic async testing.

### TestDispatcher Types

**StandardTestDispatcher** - coroutines don't run until time advances explicitly:

```kotlin
@Test
fun testStandardDispatcher() = runTest {
    launch {
        println("1")
    }
    println("2") // ✅ Executes first
    // Output: 2, 1
}
```

**UnconfinedTestDispatcher** - coroutines run immediately:

```kotlin
@Test
fun testUnconfinedDispatcher() = runTest(UnconfinedTestDispatcher()) {
    launch {
        println("1") // ✅ Executes first
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
    advanceTimeBy(1000) // ✅ Advance virtual time by 1000ms
    assertEquals(1, value)
}
```

**Time control methods:**
- `runCurrent()` - run immediately scheduled tasks
- `advanceTimeBy(ms)` - advance time by specific period
- `advanceUntilIdle()` - run all remaining tasks

### Testing StateFlow

**StateFlow** emits current value immediately:

```kotlin
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

    assertEquals(null, viewModel.user.value) // ✅ Current value available immediately

    viewModel.loadUser(1)

    assertEquals("John", viewModel.user.value?.name)
}
```

### Testing SharedFlow

**SharedFlow** has no initial value, must start collecting BEFORE emitting:

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

    // ✅ Start collecting BEFORE emitting
    val job = launch(UnconfinedTestDispatcher()) {
        eventBus.events.collect { emissions.add(it) }
    }

    eventBus.sendEvent(Event.UserLoggedIn)

    job.cancel()

    assertEquals(Event.UserLoggedIn, emissions[0])
}
```

### Turbine Library

**Turbine** simplifies Flow testing with clean API:

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

**StateFlow with Turbine:**

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
- `awaitItem()` - wait for next emission
- `skipItems(n)` - skip n emissions
- `expectNoEvents()` - verify no events
- `awaitError()` - wait for error
- `awaitComplete()` - wait for completion

### Testing ViewModel

```kotlin
@Test
fun testViewModel() = runTest {
    val repository = mockk<UserRepository>()
    coEvery { repository.fetchUser(1) } returns User(1, "John")

    val viewModel = UserViewModel(repository)

    // ✅ Test StateFlow and SharedFlow in parallel
    viewModel.uiState.test {
        assertEquals(UiState.Loading, awaitItem())

        viewModel.events.test {
            viewModel.loadUser(1)

            val successState = awaitItem() as UiState.Success
            assertEquals("John", successState.user.name)

            assertEquals(Event.UserLoaded, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Best Practices

**1. Use runTest:**

```kotlin
// ✅ DO
@Test
fun test() = runTest { /* ... */ }

// ❌ DON'T - slower, no time control
@Test
fun test() = runBlocking { /* ... */ }
```

**2. Set Main dispatcher:**

```kotlin
// ✅ DO
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// ❌ DON'T - manual setup
@Before
fun setUp() {
    Dispatchers.setMain(testDispatcher)
}
```

**3. Use Turbine for Flow:**

```kotlin
// ✅ DO
flow.test {
    assertEquals(1, awaitItem())
    awaitComplete()
}

// ❌ DON'T - manual collection
val emissions = mutableListOf<Int>()
val job = launch { flow.collect { emissions.add(it) } }
job.cancel()
```

---

## Follow-ups

- How do you handle testing cold vs hot flows differently?
- What's the difference between advanceTimeBy and advanceUntilIdle?
- How do you test flows with multiple collectors?
- When should you use StandardTestDispatcher vs UnconfinedTestDispatcher?
- How do you test error handling in flows with Turbine?

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

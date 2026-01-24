---
id: android-403
title: "Turbine Flow Testing / Тестирование Flow с Turbine"
aliases: ["Turbine Flow Testing", "Тестирование Flow с Turbine"]
topic: android
subtopics: [testing-unit, testing, flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-testing, c-coroutines, q-coroutines-testing--testing--medium, q-testing-coroutines-flow--android--hard, q-stateflow-flow-sharedflow-livedata--android--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/testing-unit, android/flow, difficulty/medium, turbine, flow, coroutines, kotlin]

---
# Vopros (RU)

> Что такое Turbine и как использовать его для тестирования Flow?

# Question (EN)

> What is Turbine and how do you use it for Flow testing?

---

## Otvet (RU)

**Turbine** - это библиотека от Cash App для тестирования Kotlin Flow. Она предоставляет простой API для ожидания и проверки эмиссий Flow в тестах.

### Краткий Ответ

- `flow.test { }` - запускает сбор Flow и предоставляет API для проверки
- `awaitItem()` - ожидает следующую эмиссию
- `awaitComplete()` - ожидает завершения Flow
- `awaitError()` - ожидает ошибку
- `cancelAndIgnoreRemainingEvents()` - отменяет сбор

### Подробный Ответ

### Базовое Использование

```kotlin
@Test
fun `basic flow test`() = runTest {
    val flow = flow {
        emit(1)
        emit(2)
        emit(3)
    }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование StateFlow

```kotlin
class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }
}

@Test
fun `stateflow emits initial value and updates`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        // StateFlow всегда эмитит начальное значение первым
        assertEquals(0, awaitItem())

        viewModel.increment()
        assertEquals(1, awaitItem())

        viewModel.increment()
        assertEquals(2, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование SharedFlow

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) {
        _events.emit(event)
    }
}

@Test
fun `sharedflow test - start collecting before emit`() = runTest {
    val eventBus = EventBus()

    eventBus.events.test {
        // SharedFlow не имеет начального значения
        // Начинаем сбор ДО эмиссии

        eventBus.emit(Event.Loading)
        assertEquals(Event.Loading, awaitItem())

        eventBus.emit(Event.Success("data"))
        assertEquals(Event.Success("data"), awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Методы API Turbine

```kotlin
@Test
fun `turbine api methods`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        emit(3)
    }

    flow.test {
        // awaitItem() - ждет следующую эмиссию
        val first = awaitItem()
        assertEquals(1, first)

        // skipItems(n) - пропускает n эмиссий
        skipItems(1) // пропускаем 2

        val third = awaitItem()
        assertEquals(3, third)

        awaitComplete()
    }
}

@Test
fun `test with expectNoEvents`() = runTest {
    val flow = MutableSharedFlow<Int>()

    flow.test {
        // Проверяем, что нет событий
        expectNoEvents()

        flow.emit(1)
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование Ошибок

```kotlin
@Test
fun `flow error test`() = runTest {
    val flow = flow {
        emit(1)
        throw IllegalStateException("Test error")
    }

    flow.test {
        assertEquals(1, awaitItem())

        // awaitError() - ждет ошибку
        val error = awaitError()
        assertTrue(error is IllegalStateException)
        assertEquals("Test error", error.message)
    }
}

@Test
fun `catch error and continue`() = runTest {
    val flow = flow {
        emit(1)
        throw IllegalStateException("Error")
    }.catch { emit(-1) }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(-1, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование с Задержками

```kotlin
@Test
fun `flow with delays`() = runTest {
    val flow = flow {
        emit(1)
        delay(1000)
        emit(2)
        delay(2000)
        emit(3)
    }

    flow.test {
        assertEquals(1, awaitItem())
        // runTest автоматически продвигает виртуальное время
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}

@Test
fun `test with timeout`() = runTest {
    val slowFlow = flow {
        delay(10_000) // Очень долгая задержка
        emit(1)
    }

    slowFlow.test(timeout = 500.milliseconds) {
        // Тест завершится по таймауту, если эмиссия не произойдет
        // С runTest это не проблема - время виртуальное
        assertEquals(1, awaitItem())
        awaitComplete()
    }
}
```

### Тестирование ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val user = repository.getUser(id)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

class UserViewModelTest {
    private val repository = mockk<UserRepository>()
    private lateinit var viewModel: UserViewModel

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Before
    fun setup() {
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser emits loading then success`() = runTest {
        // Given
        val user = User("123", "John")
        coEvery { repository.getUser("123") } returns user

        // When & Then
        viewModel.uiState.test {
            // Начальное состояние
            assertEquals(UiState.Loading, awaitItem())

            viewModel.loadUser("123")

            // Может быть еще один Loading (зависит от реализации)
            // Успешный результат
            val successState = awaitItem()
            assertTrue(successState is UiState.Success)
            assertEquals(user, (successState as UiState.Success).user)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadUser emits error on failure`() = runTest {
        // Given
        coEvery { repository.getUser(any()) } throws IOException("Network error")

        // When & Then
        viewModel.uiState.test {
            assertEquals(UiState.Loading, awaitItem())

            viewModel.loadUser("123")

            val errorState = awaitItem()
            assertTrue(errorState is UiState.Error)
            assertEquals("Network error", (errorState as UiState.Error).message)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Тестирование Нескольких Flow

```kotlin
@Test
fun `test multiple flows`() = runTest {
    val viewModel = ComplexViewModel()

    // Turbine 1.0+ поддерживает параллельное тестирование
    turbineScope {
        val stateTurbine = viewModel.state.testIn(backgroundScope)
        val eventsTurbine = viewModel.events.testIn(backgroundScope)

        // Проверяем начальное состояние
        assertEquals(State.Initial, stateTurbine.awaitItem())

        viewModel.doAction()

        // Проверяем изменение состояния
        assertEquals(State.Loading, stateTurbine.awaitItem())
        assertEquals(State.Success, stateTurbine.awaitItem())

        // Проверяем событие
        assertEquals(Event.ActionCompleted, eventsTurbine.awaitItem())

        stateTurbine.cancelAndIgnoreRemainingEvents()
        eventsTurbine.cancelAndIgnoreRemainingEvents()
    }
}
```

### Продвинутые Паттерны

```kotlin
@Test
fun `test flow transformation`() = runTest {
    val sourceFlow = MutableStateFlow(0)

    val transformedFlow = sourceFlow
        .filter { it > 0 }
        .map { "Value: $it" }

    transformedFlow.test {
        // filter отбрасывает 0, поэтому ждем первую эмиссию после изменения

        sourceFlow.value = 1
        assertEquals("Value: 1", awaitItem())

        sourceFlow.value = 2
        assertEquals("Value: 2", awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `test combine flows`() = runTest {
    val flow1 = MutableStateFlow("A")
    val flow2 = MutableStateFlow(1)

    combine(flow1, flow2) { str, num -> "$str$num" }
        .test {
            assertEquals("A1", awaitItem())

            flow1.value = "B"
            assertEquals("B1", awaitItem())

            flow2.value = 2
            assertEquals("B2", awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
}
```

### MainDispatcherRule для ViewModel

```kotlin
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Зависимости

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("app.cash.turbine:turbine:1.1.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.0")
}
```

### Лучшие Практики

1. Всегда заканчивайте test-блок: `awaitComplete()` или `cancelAndIgnoreRemainingEvents()`
2. Для StateFlow помните про начальное значение
3. Для SharedFlow начинайте сбор ДО эмиссии
4. Используйте `MainDispatcherRule` для тестов ViewModel
5. Используйте `turbineScope` для тестирования нескольких Flow

---

## Answer (EN)

**Turbine** is a library from Cash App for testing Kotlin Flow. It provides a simple API for awaiting and asserting Flow emissions in tests.

### Short Version

- `flow.test { }` - starts collecting the Flow and provides assertion API
- `awaitItem()` - awaits the next emission
- `awaitComplete()` - awaits Flow completion
- `awaitError()` - awaits an error
- `cancelAndIgnoreRemainingEvents()` - cancels collection

### Detailed Version

### Basic Usage

```kotlin
@Test
fun `basic flow test`() = runTest {
    val flow = flow {
        emit(1)
        emit(2)
        emit(3)
    }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

### Testing StateFlow

```kotlin
class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }
}

@Test
fun `stateflow emits initial value and updates`() = runTest {
    val viewModel = CounterViewModel()

    viewModel.count.test {
        // StateFlow always emits initial value first
        assertEquals(0, awaitItem())

        viewModel.increment()
        assertEquals(1, awaitItem())

        viewModel.increment()
        assertEquals(2, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing SharedFlow

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) {
        _events.emit(event)
    }
}

@Test
fun `sharedflow test - start collecting before emit`() = runTest {
    val eventBus = EventBus()

    eventBus.events.test {
        // SharedFlow has no initial value
        // Start collecting BEFORE emitting

        eventBus.emit(Event.Loading)
        assertEquals(Event.Loading, awaitItem())

        eventBus.emit(Event.Success("data"))
        assertEquals(Event.Success("data"), awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Turbine API Methods

```kotlin
@Test
fun `turbine api methods`() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        emit(3)
    }

    flow.test {
        // awaitItem() - waits for next emission
        val first = awaitItem()
        assertEquals(1, first)

        // skipItems(n) - skips n emissions
        skipItems(1) // skip 2

        val third = awaitItem()
        assertEquals(3, third)

        awaitComplete()
    }
}

@Test
fun `test with expectNoEvents`() = runTest {
    val flow = MutableSharedFlow<Int>()

    flow.test {
        // Verify no events
        expectNoEvents()

        flow.emit(1)
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing Errors

```kotlin
@Test
fun `flow error test`() = runTest {
    val flow = flow {
        emit(1)
        throw IllegalStateException("Test error")
    }

    flow.test {
        assertEquals(1, awaitItem())

        // awaitError() - waits for error
        val error = awaitError()
        assertTrue(error is IllegalStateException)
        assertEquals("Test error", error.message)
    }
}

@Test
fun `catch error and continue`() = runTest {
    val flow = flow {
        emit(1)
        throw IllegalStateException("Error")
    }.catch { emit(-1) }

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(-1, awaitItem())
        awaitComplete()
    }
}
```

### Testing with Delays

```kotlin
@Test
fun `flow with delays`() = runTest {
    val flow = flow {
        emit(1)
        delay(1000)
        emit(2)
        delay(2000)
        emit(3)
    }

    flow.test {
        assertEquals(1, awaitItem())
        // runTest automatically advances virtual time
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}

@Test
fun `test with timeout`() = runTest {
    val slowFlow = flow {
        delay(10_000) // Very long delay
        emit(1)
    }

    slowFlow.test(timeout = 500.milliseconds) {
        // Test will timeout if emission doesn't happen
        // With runTest this isn't a problem - time is virtual
        assertEquals(1, awaitItem())
        awaitComplete()
    }
}
```

### Testing ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val user = repository.getUser(id)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

class UserViewModelTest {
    private val repository = mockk<UserRepository>()
    private lateinit var viewModel: UserViewModel

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Before
    fun setup() {
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser emits loading then success`() = runTest {
        // Given
        val user = User("123", "John")
        coEvery { repository.getUser("123") } returns user

        // When & Then
        viewModel.uiState.test {
            // Initial state
            assertEquals(UiState.Loading, awaitItem())

            viewModel.loadUser("123")

            // May be another Loading (depends on implementation)
            // Success result
            val successState = awaitItem()
            assertTrue(successState is UiState.Success)
            assertEquals(user, (successState as UiState.Success).user)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadUser emits error on failure`() = runTest {
        // Given
        coEvery { repository.getUser(any()) } throws IOException("Network error")

        // When & Then
        viewModel.uiState.test {
            assertEquals(UiState.Loading, awaitItem())

            viewModel.loadUser("123")

            val errorState = awaitItem()
            assertTrue(errorState is UiState.Error)
            assertEquals("Network error", (errorState as UiState.Error).message)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Testing Multiple Flows

```kotlin
@Test
fun `test multiple flows`() = runTest {
    val viewModel = ComplexViewModel()

    // Turbine 1.0+ supports parallel testing
    turbineScope {
        val stateTurbine = viewModel.state.testIn(backgroundScope)
        val eventsTurbine = viewModel.events.testIn(backgroundScope)

        // Check initial state
        assertEquals(State.Initial, stateTurbine.awaitItem())

        viewModel.doAction()

        // Check state changes
        assertEquals(State.Loading, stateTurbine.awaitItem())
        assertEquals(State.Success, stateTurbine.awaitItem())

        // Check event
        assertEquals(Event.ActionCompleted, eventsTurbine.awaitItem())

        stateTurbine.cancelAndIgnoreRemainingEvents()
        eventsTurbine.cancelAndIgnoreRemainingEvents()
    }
}
```

### Advanced Patterns

```kotlin
@Test
fun `test flow transformation`() = runTest {
    val sourceFlow = MutableStateFlow(0)

    val transformedFlow = sourceFlow
        .filter { it > 0 }
        .map { "Value: $it" }

    transformedFlow.test {
        // filter discards 0, so wait for first emission after change

        sourceFlow.value = 1
        assertEquals("Value: 1", awaitItem())

        sourceFlow.value = 2
        assertEquals("Value: 2", awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}

@Test
fun `test combine flows`() = runTest {
    val flow1 = MutableStateFlow("A")
    val flow2 = MutableStateFlow(1)

    combine(flow1, flow2) { str, num -> "$str$num" }
        .test {
            assertEquals("A1", awaitItem())

            flow1.value = "B"
            assertEquals("B1", awaitItem())

            flow2.value = 2
            assertEquals("B2", awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
}
```

### MainDispatcherRule for ViewModel

```kotlin
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Dependencies

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("app.cash.turbine:turbine:1.1.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.0")
}
```

### Best Practices

1. Always finish test block with `awaitComplete()` or `cancelAndIgnoreRemainingEvents()`
2. For StateFlow remember the initial value
3. For SharedFlow start collecting BEFORE emitting
4. Use `MainDispatcherRule` for ViewModel tests
5. Use `turbineScope` for testing multiple Flows

---

## Follow-ups

- How do you test Flow operators like `debounce` with Turbine?
- What's the difference between `expectMostRecentItem()` and `awaitItem()`?
- How do you handle flaky tests with Turbine?

## References

- https://github.com/cashapp/turbine
- https://developer.android.com/kotlin/flow/test
- https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-test/

## Related Questions

### Prerequisites (Easier)
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - StateFlow vs SharedFlow

### Related (Same Level)
- [[q-coroutines-testing--testing--medium]] - runTest and TestDispatcher
- [[q-mockk-basics--testing--medium]] - MockK for mocking in tests

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Comprehensive Flow testing

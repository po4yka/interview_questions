---
id: 20251012-122711118
title: "Testing Coroutines Flow / Тестирование Coroutines Flow"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: [coroutines, flow, async, turbine, test-dispatcher, difficulty/hard]
---

# Testing Coroutines and Flow

# Question (EN)

> How do you test suspend functions, StateFlow, and SharedFlow? Explain TestDispatcher, runTest, and turbine library.

# Вопрос (RU)

> Как тестировать suspend функции, StateFlow и SharedFlow? Объясните TestDispatcher, runTest и библиотеку turbine.

---

## Answer (EN)

Testing coroutines and flows requires special test utilities to control time and execution. **TestDispatcher**, **runTest**, and **Turbine** are essential tools for deterministic async testing.

---

### Testing Suspend Functions

**Basic suspend function test:**

```kotlin
class UserRepository {
    suspend fun fetchUser(id: Int): User {
        delay(1000) // Simulate network
        return User(id, "John")
    }
}

@Test
fun testSuspendFunction() = runTest {
    val repository = UserRepository()

    val user = repository.fetchUser(1)

    assertEquals("John", user.name)
}
```

**runTest automatically:**

-   Advances virtual time
-   Waits for all coroutines to complete
-   Runs instantly (no actual delays)

---

### TestDispatcher Types

**1. StandardTestDispatcher (default):**

```kotlin
@Test
fun testStandardDispatcher() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)

    launch(dispatcher) {
        println("1")
    }

    println("2")

    // Output: 2, 1
    // Coroutines don't run until advanceUntilIdle()
}
```

**2. UnconfinedTestDispatcher:**

```kotlin
@Test
fun testUnconfinedDispatcher() = runTest(UnconfinedTestDispatcher()) {
    launch {
        println("1")
    }

    println("2")

    // Output: 1, 2
    // Coroutines run immediately
}
```

---

### Testing with Time Control

**Advance time manually:**

```kotlin
@Test
fun testTimeControl() = runTest {
    var value = 0

    launch {
        delay(1000)
        value = 1
        delay(2000)
        value = 2
    }

    // Immediately after launch
    assertEquals(0, value)

    // Advance by 1000ms
    advanceTimeBy(1000)
    assertEquals(1, value)

    // Advance by remaining time
    advanceUntilIdle()
    assertEquals(2, value)

    // Total virtual time
    assertEquals(3000, currentTime)
}
```

**advanceUntilIdle vs runCurrent:**

```kotlin
@Test
fun testAdvance() = runTest {
    var value = 0

    launch {
        value = 1
        delay(100)
        value = 2
    }

    runCurrent() // Run immediately scheduled tasks
    assertEquals(1, value)

    advanceUntilIdle() // Run all remaining tasks
    assertEquals(2, value)
}
```

---

### Testing StateFlow

**StateFlow emits immediately:**

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

    // StateFlow emits current value immediately
    assertEquals(null, viewModel.user.value)

    viewModel.loadUser(1)

    // After coroutine completes
    assertEquals("John", viewModel.user.value?.name)
}
```

**Collect multiple emissions:**

```kotlin
@Test
fun testStateFlowCollect() = runTest {
    val viewModel = UserViewModel()
    val emissions = mutableListOf<User?>()

    // Launch collector
    val job = launch(UnconfinedTestDispatcher()) {
        viewModel.user.collect {
            emissions.add(it)
        }
    }

    viewModel.loadUser(1)
    advanceUntilIdle()

    job.cancel()

    assertEquals(2, emissions.size)
    assertEquals(null, emissions[0]) // Initial value
    assertEquals("John", emissions[1]?.name)
}
```

---

### Testing SharedFlow

**SharedFlow doesn't emit initial value:**

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

    // Start collecting BEFORE emitting
    val job = launch(UnconfinedTestDispatcher()) {
        eventBus.events.collect {
            emissions.add(it)
        }
    }

    eventBus.sendEvent(Event.UserLoggedIn)
    eventBus.sendEvent(Event.UserLoggedOut)

    job.cancel()

    assertEquals(2, emissions.size)
    assertEquals(Event.UserLoggedIn, emissions[0])
    assertEquals(Event.UserLoggedOut, emissions[1])
}
```

---

### Turbine Library

**Turbine** simplifies Flow testing with a clean API:

```gradle
// build.gradle.kts
dependencies {
    testImplementation("app.cash.turbine:turbine:1.0.0")
}
```

**Basic usage:**

```kotlin
@Test
fun testFlowWithTurbine() = runTest {
    val flow = flow {
        emit(1)
        delay(100)
        emit(2)
        delay(100)
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

**StateFlow with Turbine:**

```kotlin
@Test
fun testStateFlowWithTurbine() = runTest {
    val viewModel = UserViewModel()

    viewModel.user.test {
        // First emission is current value
        assertEquals(null, awaitItem())

        viewModel.loadUser(1)

        // Wait for new emission
        val user = awaitItem()
        assertEquals("John", user?.name)

        cancelAndIgnoreRemainingEvents()
    }
}
```

**SharedFlow with Turbine:**

```kotlin
@Test
fun testSharedFlowWithTurbine() = runTest {
    val eventBus = EventBus()

    eventBus.events.test {
        // No initial emission for SharedFlow

        eventBus.sendEvent(Event.UserLoggedIn)
        assertEquals(Event.UserLoggedIn, awaitItem())

        eventBus.sendEvent(Event.UserLoggedOut)
        assertEquals(Event.UserLoggedOut, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

### Turbine Advanced Features

**1. skipItems:**

```kotlin
@Test
fun testSkipItems() = runTest {
    flow {
        emit(1)
        emit(2)
        emit(3)
        emit(4)
    }.test {
        skipItems(2) // Skip first 2 items
        assertEquals(3, awaitItem())
        assertEquals(4, awaitItem())
        awaitComplete()
    }
}
```

**2. expectNoEvents:**

```kotlin
@Test
fun testNoEvents() = runTest {
    val flow = MutableSharedFlow<Int>()

    flow.test {
        // Assert no events for 100ms
        expectNoEvents()

        flow.emit(1)
        assertEquals(1, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

**3. awaitError:**

```kotlin
@Test
fun testError() = runTest {
    flow {
        emit(1)
        throw IOException("Network error")
    }.test {
        assertEquals(1, awaitItem())

        val error = awaitError()
        assertTrue(error is IOException)
        assertEquals("Network error", error.message)
    }
}
```

**4. Multiple flows:**

```kotlin
@Test
fun testMultipleFlows() = runTest {
    val flow1 = MutableStateFlow(0)
    val flow2 = MutableStateFlow(0)

    flow1.test {
        assertEquals(0, awaitItem())

        flow2.test {
            assertEquals(0, awaitItem())

            flow1.value = 1
            flow2.value = 2

            // Test flow1
            flow1.value = 1
            assertEquals(1, expectMostRecentItem())

            cancelAndIgnoreRemainingEvents()
        }

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

### Real-World Example: ViewModel Testing

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val user = repository.fetchUser(id)
                _uiState.value = UiState.Success(user)
                _events.emit(Event.UserLoaded)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
                _events.emit(Event.LoadFailed)
            }
        }
    }

    fun retry() {
        val currentState = _uiState.value
        if (currentState is UiState.Error) {
            loadUser(currentState.userId)
        }
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val user: User) : UiState()
    data class Error(val message: String, val userId: Int = 0) : UiState()
}

sealed class Event {
    object UserLoaded : Event()
    object LoadFailed : Event()
}
```

**Complete test:**

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {
    private val testDispatcher = StandardTestDispatcher()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule(testDispatcher)

    private lateinit var repository: UserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setUp() {
        repository = mockk()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser success updates state and emits event`() = runTest {
        val user = User(1, "John")
        coEvery { repository.fetchUser(1) } returns user

        // Test StateFlow
        viewModel.uiState.test {
            // Initial state
            assertEquals(UiState.Loading, awaitItem())

            // Test SharedFlow in parallel
            viewModel.events.test {
                viewModel.loadUser(1)

                // Wait for state update
                val successState = awaitItem() as UiState.Success
                assertEquals("John", successState.user.name)

                // Wait for event
                assertEquals(Event.UserLoaded, awaitItem())

                cancelAndIgnoreRemainingEvents()
            }

            cancelAndIgnoreRemainingEvents()
        }

        coVerify { repository.fetchUser(1) }
    }

    @Test
    fun `loadUser error updates state and emits event`() = runTest {
        coEvery { repository.fetchUser(1) } throws IOException("Network error")

        viewModel.uiState.test {
            assertEquals(UiState.Loading, awaitItem())

            viewModel.events.test {
                viewModel.loadUser(1)

                val errorState = awaitItem() as UiState.Error
                assertEquals("Network error", errorState.message)

                assertEquals(Event.LoadFailed, awaitItem())

                cancelAndIgnoreRemainingEvents()
            }

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `retry reloads user`() = runTest {
        // First call fails
        coEvery { repository.fetchUser(1) } throws IOException("Network error")

        viewModel.loadUser(1)
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UiState.Error)

        // Second call succeeds
        coEvery { repository.fetchUser(1) } returns User(1, "John")

        viewModel.retry()
        advanceUntilIdle()

        val state = viewModel.uiState.value as UiState.Success
        assertEquals("John", state.user.name)

        coVerify(exactly = 2) { repository.fetchUser(1) }
    }
}

// MainDispatcherRule for setting test dispatcher
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

---

### Testing Cold vs Hot Flows

**Cold Flow (flow {}):**

```kotlin
@Test
fun testColdFlow() = runTest {
    var executionCount = 0

    val flow = flow {
        executionCount++
        emit(1)
    }

    // Each collector triggers execution
    flow.test {
        assertEquals(1, awaitItem())
        awaitComplete()
    }
    assertEquals(1, executionCount)

    flow.test {
        assertEquals(1, awaitItem())
        awaitComplete()
    }
    assertEquals(2, executionCount) // Executed again
}
```

**Hot Flow (StateFlow/SharedFlow):**

```kotlin
@Test
fun testHotFlow() = runTest {
    val flow = MutableStateFlow(0)

    // Multiple collectors share emissions
    flow.test {
        assertEquals(0, awaitItem())

        flow.test {
            assertEquals(0, awaitItem())

            flow.value = 1

            // Both collectors receive emission
            assertEquals(1, expectMostRecentItem())

            cancelAndIgnoreRemainingEvents()
        }

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

### Best Practices

**1. Use runTest for all coroutine tests:**

```kotlin
//  DO
@Test
fun test() = runTest {
    // Test code
}

//  DON'T
@Test
fun test() {
    runBlocking {
        // Slower, doesn't control time
    }
}
```

**2. Set Main dispatcher for ViewModels:**

```kotlin
//  DO: Use rule
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

//  DON'T: Manual setup
@Before
fun setUp() {
    Dispatchers.setMain(testDispatcher)
}
```

**3. Use Turbine for Flow testing:**

```kotlin
//  DO: Clean with Turbine
flow.test {
    assertEquals(1, awaitItem())
    awaitComplete()
}

//  DON'T: Manual collection
val emissions = mutableListOf<Int>()
val job = launch {
    flow.collect { emissions.add(it) }
}
job.cancel()
```

**4. Test both state and events:**

```kotlin
//  DO: Test both flows
viewModel.uiState.test { /* ... */ }
viewModel.events.test { /* ... */ }
```

---

## Ответ (RU)

Тестирование корутин и потоков требует специальных утилит для контроля времени и выполнения. **TestDispatcher**, **runTest** и **Turbine** — необходимые инструменты для детерминированного асинхронного тестирования.

### Тестирование Suspend функций

`runTest` автоматически продвигает виртуальное время и ждет завершения всех корутин.

### TestDispatcher типы

-   **StandardTestDispatcher** - корутины не выполняются до `advanceUntilIdle()`
-   **UnconfinedTestDispatcher** - корутины выполняются немедленно

### Контроль времени

Используйте `advanceTimeBy()`, `advanceUntilIdle()`, `runCurrent()` для контроля виртуального времени.

### Библиотека Turbine

**Turbine** упрощает тестирование Flow с чистым API: `test { awaitItem() }`.

### Тестирование StateFlow vs SharedFlow

-   **StateFlow** - эмитирует текущее значение немедленно
-   **SharedFlow** - не имеет начального значения

### Лучшие практики

1. Используйте runTest для всех тестов корутин
2. Устанавливайте Main dispatcher для ViewModels
3. Используйте Turbine для тестирования Flow
4. Тестируйте как состояние, так и события

Правильное тестирование корутин и Flow обеспечивает надежность асинхронного кода.

---

## Follow-ups

-   How do you test coroutines with delays and timeouts in unit tests?
-   What's the difference between testing StateFlow vs SharedFlow behavior?
-   How can you mock suspend functions that return Flow in your tests?

## References

-   `https://developer.android.com/kotlin/coroutines/test` — Testing coroutines
-   `https://github.com/cashapp/turbine` — Turbine library
-   `https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-test/` — Coroutines test utilities

## Related Questions

### Prerequisites (Easier)

-   [[q-testing-viewmodels-turbine--testing--medium]] - Testing
-   [[q-testing-compose-ui--android--medium]] - Testing
-   [[q-compose-testing--android--medium]] - Testing

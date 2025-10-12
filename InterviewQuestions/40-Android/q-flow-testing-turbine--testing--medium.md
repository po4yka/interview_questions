---
id: 20251012-400007
title: "Flow Testing with Turbine / Тестирование Flow с Turbine"
slug: flow-testing-turbine-testing-medium
topic: android
subtopics:
  - testing
  - kotlin-flow
  - turbine
  - coroutines
  - unit-testing
status: draft
difficulty: medium
moc: moc-android
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-kotlin-coroutines-advanced--kotlin--hard
  - q-unit-testing-coroutines-flow--android--medium
  - q-compose-testing--android--medium
tags:
  - testing
  - kotlin-flow
  - turbine
  - coroutines
  - unit-testing
---

# Flow Testing with Turbine

## English Version

### Problem Statement

Testing Kotlin Flows can be challenging due to their asynchronous nature. Turbine is a testing library that simplifies Flow testing by providing intuitive APIs for asserting emissions. Understanding Turbine is essential for robust coroutine-based Android testing.

**The Question:** What is Turbine? How do you test Flows with Turbine? How does it compare to manual Flow testing? What are best practices?

### Detailed Answer

---

### TURBINE SETUP

**Add dependency:**
```gradle
dependencies {
    testImplementation "app.cash.turbine:turbine:1.0.0"
    testImplementation "org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3"
    testImplementation "junit:junit:4.13.2"
}
```

**Basic usage:**
```kotlin
@Test
fun `test simple flow`() = runTest {
    val flow = flowOf(1, 2, 3)

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

---

### BASIC TURBINE APIS

```kotlin
class FlowTurbineBasicsTest {

    @Test
    fun `awaitItem - wait for next emission`() = runTest {
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

    @Test
    fun `awaitComplete - wait for flow completion`() = runTest {
        val flow = flowOf(1, 2, 3)

        flow.test {
            awaitItem()  // 1
            awaitItem()  // 2
            awaitItem()  // 3
            awaitComplete()  // Asserts flow completed
        }
    }

    @Test
    fun `awaitError - wait for flow error`() = runTest {
        val flow = flow {
            emit(1)
            throw IllegalStateException("Error!")
        }

        flow.test {
            assertEquals(1, awaitItem())
            val error = awaitError()
            assertTrue(error is IllegalStateException)
            assertEquals("Error!", error.message)
        }
    }

    @Test
    fun `skipItems - skip multiple emissions`() = runTest {
        val flow = flowOf(1, 2, 3, 4, 5)

        flow.test {
            skipItems(2)  // Skip first 2 items
            assertEquals(3, awaitItem())
            assertEquals(4, awaitItem())
            assertEquals(5, awaitItem())
            awaitComplete()
        }
    }

    @Test
    fun `expectNoEvents - assert no emissions`() = runTest {
        val flow = flow<Int> {
            delay(100)
            emit(1)
        }

        flow.test {
            expectNoEvents()  // No events for short duration
            advanceTimeBy(100)
            assertEquals(1, awaitItem())
        }
    }
}
```

---

### TESTING STATEFLOW

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }

    fun decrement() {
        _count.value--
    }
}

class CounterViewModelTest {
    private lateinit var viewModel: CounterViewModel

    @Before
    fun setup() {
        Dispatchers.setMain(StandardTestDispatcher())
        viewModel = CounterViewModel()
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `increment updates count`() = runTest {
        viewModel.count.test {
            // StateFlow always has initial value
            assertEquals(0, awaitItem())

            viewModel.increment()
            assertEquals(1, awaitItem())

            viewModel.increment()
            assertEquals(2, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `decrement updates count`() = runTest {
        viewModel.count.test {
            assertEquals(0, awaitItem())

            viewModel.decrement()
            assertEquals(-1, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

### TESTING SHAREDFLOW

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) {
        _events.emit(event)
    }
}

sealed interface Event {
    data class UserLoggedIn(val userId: String) : Event
    data class UserLoggedOut(val userId: String) : Event
    data class ErrorOccurred(val message: String) : Event
}

class EventBusTest {

    @Test
    fun `emitted events are received`() = runTest {
        val eventBus = EventBus()

        eventBus.events.test {
            // SharedFlow doesn't have initial value
            expectNoEvents()

            eventBus.emit(Event.UserLoggedIn("user123"))
            val event1 = awaitItem()
            assertTrue(event1 is Event.UserLoggedIn)
            assertEquals("user123", (event1 as Event.UserLoggedIn).userId)

            eventBus.emit(Event.ErrorOccurred("Network error"))
            val event2 = awaitItem()
            assertTrue(event2 is Event.ErrorOccurred)
            assertEquals("Network error", (event2 as Event.ErrorOccurred).message)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `multiple collectors receive events`() = runTest {
        val eventBus = EventBus()

        // Launch two collectors
        val job1 = launch {
            eventBus.events.test {
                val event = awaitItem()
                assertTrue(event is Event.UserLoggedIn)
            }
        }

        val job2 = launch {
            eventBus.events.test {
                val event = awaitItem()
                assertTrue(event is Event.UserLoggedIn)
            }
        }

        advanceUntilIdle()
        eventBus.emit(Event.UserLoggedIn("user456"))

        job1.join()
        job2.join()
    }
}
```

---

### TESTING REPOSITORY FLOWS

```kotlin
interface UserRepository {
    fun getUser(userId: String): Flow<Result<User>>
}

sealed class Result<out T> {
    data object Loading : Result<Nothing>()
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
}

data class User(val id: String, val name: String)

class UserRepositoryImpl(
    private val api: ApiService
) : UserRepository {
    override fun getUser(userId: String): Flow<Result<User>> = flow {
        emit(Result.Loading)

        try {
            val user = api.getUser(userId)
            emit(Result.Success(user))
        } catch (e: Exception) {
            emit(Result.Error(e))
        }
    }
}

class UserRepositoryTest {

    @Test
    fun `getUser emits loading then success`() = runTest {
        val mockApi = mockk<ApiService>()
        coEvery { mockApi.getUser("123") } returns User("123", "John Doe")

        val repository = UserRepositoryImpl(mockApi)

        repository.getUser("123").test {
            // First emission: Loading
            val loading = awaitItem()
            assertTrue(loading is Result.Loading)

            // Second emission: Success
            val success = awaitItem()
            assertTrue(success is Result.Success)
            assertEquals("John Doe", (success as Result.Success).data.name)

            awaitComplete()
        }

        coVerify { mockApi.getUser("123") }
    }

    @Test
    fun `getUser emits loading then error on failure`() = runTest {
        val mockApi = mockk<ApiService>()
        coEvery { mockApi.getUser("123") } throws IOException("Network error")

        val repository = UserRepositoryImpl(mockApi)

        repository.getUser("123").test {
            assertTrue(awaitItem() is Result.Loading)

            val error = awaitItem()
            assertTrue(error is Result.Error)
            assertTrue((error as Result.Error).exception is IOException)

            awaitComplete()
        }
    }
}
```

---

### TESTING VIEWMODEL UI STATE

```kotlin
sealed interface ProfileUiState {
    data object Loading : ProfileUiState
    data class Success(val user: User) : ProfileUiState
    data class Error(val message: String) : ProfileUiState
}

class ProfileViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            _uiState.value = ProfileUiState.Loading

            repository.getUser(userId).collect { result ->
                _uiState.value = when (result) {
                    is Result.Loading -> ProfileUiState.Loading
                    is Result.Success -> ProfileUiState.Success(result.data)
                    is Result.Error -> ProfileUiState.Error(result.exception.message ?: "Unknown error")
                }
            }
        }
    }
}

class ProfileViewModelTest {
    private lateinit var viewModel: ProfileViewModel
    private lateinit var mockRepository: UserRepository
    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        mockRepository = mockk()
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `loadProfile updates uiState correctly`() = runTest {
        val user = User("123", "John Doe")
        coEvery { mockRepository.getUser("123") } returns flowOf(
            Result.Loading,
            Result.Success(user)
        )

        viewModel = ProfileViewModel(mockRepository)

        viewModel.uiState.test {
            // Initial state
            assertTrue(awaitItem() is ProfileUiState.Loading)

            // Load profile
            viewModel.loadProfile("123")
            advanceUntilIdle()

            // Should still be loading (repository emits Loading first)
            // Then success
            val state = awaitItem()
            assertTrue(state is ProfileUiState.Success)
            assertEquals("John Doe", (state as ProfileUiState.Success).user.name)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadProfile handles error`() = runTest {
        coEvery { mockRepository.getUser("123") } returns flowOf(
            Result.Loading,
            Result.Error(IOException("Network error"))
        )

        viewModel = ProfileViewModel(mockRepository)

        viewModel.uiState.test {
            assertTrue(awaitItem() is ProfileUiState.Loading)

            viewModel.loadProfile("123")
            advanceUntilIdle()

            val state = awaitItem()
            assertTrue(state is ProfileUiState.Error)
            assertEquals("Network error", (state as ProfileUiState.Error).message)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

### TESTING TIME-BASED FLOWS

```kotlin
class TickerViewModel : ViewModel() {
    val ticker: Flow<Int> = flow {
        var count = 0
        while (true) {
            emit(count++)
            delay(1000)  // Emit every second
        }
    }
}

class TickerViewModelTest {

    @Test
    fun `ticker emits every second`() = runTest {
        val viewModel = TickerViewModel()

        viewModel.ticker.test {
            assertEquals(0, awaitItem())

            // Advance time by 1 second
            advanceTimeBy(1000)
            assertEquals(1, awaitItem())

            advanceTimeBy(1000)
            assertEquals(2, awaitItem())

            advanceTimeBy(1000)
            assertEquals(3, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `ticker emits multiple times quickly`() = runTest {
        val viewModel = TickerViewModel()

        viewModel.ticker.test {
            assertEquals(0, awaitItem())

            // Advance time by 5 seconds
            advanceTimeBy(5000)

            // Should have 5 more emissions
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            assertEquals(4, awaitItem())
            assertEquals(5, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

### TESTING FLOW OPERATORS

```kotlin
class FlowOperatorsTest {

    @Test
    fun `map operator transforms values`() = runTest {
        val flow = flowOf(1, 2, 3).map { it * 2 }

        flow.test {
            assertEquals(2, awaitItem())
            assertEquals(4, awaitItem())
            assertEquals(6, awaitItem())
            awaitComplete()
        }
    }

    @Test
    fun `filter operator filters values`() = runTest {
        val flow = flowOf(1, 2, 3, 4, 5).filter { it % 2 == 0 }

        flow.test {
            assertEquals(2, awaitItem())
            assertEquals(4, awaitItem())
            awaitComplete()
        }
    }

    @Test
    fun `debounce operator delays emissions`() = runTest {
        val flow = flow {
            emit(1)
            delay(100)
            emit(2)
            delay(100)
            emit(3)
            delay(600)  // > 500ms debounce
            emit(4)
        }.debounce(500)

        flow.test {
            // Only 3 and 4 should be emitted (after 500ms of silence)
            advanceTimeBy(700)
            assertEquals(3, awaitItem())

            advanceTimeBy(600)
            assertEquals(4, awaitItem())

            awaitComplete()
        }
    }

    @Test
    fun `combine operator combines flows`() = runTest {
        val flow1 = flowOf("A", "B", "C")
        val flow2 = flowOf(1, 2, 3)

        combine(flow1, flow2) { a, b -> "$a$b" }.test {
            // combine emits when either flow emits
            // Results depend on timing
            val items = mutableListOf<String>()
            repeat(3) {
                items.add(awaitItem())
            }

            assertTrue(items.contains("A1") || items.contains("A2") || items.contains("A3"))
            awaitComplete()
        }
    }
}
```

---

### TESTING ERROR HANDLING

```kotlin
class ErrorHandlingTest {

    @Test
    fun `retry operator retries on error`() = runTest {
        var attemptCount = 0

        val flow = flow {
            attemptCount++
            if (attemptCount < 3) {
                throw IOException("Temporary error")
            }
            emit("Success")
        }.retry(retries = 2)

        flow.test {
            assertEquals("Success", awaitItem())
            awaitComplete()
        }

        assertEquals(3, attemptCount)
    }

    @Test
    fun `catch operator handles errors`() = runTest {
        val flow = flow {
            emit(1)
            emit(2)
            throw IllegalStateException("Error!")
        }.catch { e ->
            emit(-1)  // Emit fallback value
        }

        flow.test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(-1, awaitItem())
            awaitComplete()
        }
    }

    @Test
    fun `onError terminates flow`() = runTest {
        val flow = flow {
            emit(1)
            throw IllegalStateException("Error!")
        }

        flow.test {
            assertEquals(1, awaitItem())

            val error = awaitError()
            assertTrue(error is IllegalStateException)
            assertEquals("Error!", error.message)
        }
    }
}
```

---

### TURBINE VS MANUAL TESTING

```kotlin
// ❌ Manual testing - verbose and error-prone
@Test
fun `manual flow testing`() = runTest {
    val flow = flowOf(1, 2, 3)
    val results = mutableListOf<Int>()

    val job = launch {
        flow.collect { results.add(it) }
    }

    advanceUntilIdle()
    job.cancel()

    assertEquals(listOf(1, 2, 3), results)
}

// ✅ Turbine - concise and readable
@Test
fun `turbine flow testing`() = runTest {
    val flow = flowOf(1, 2, 3)

    flow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

---

### BEST PRACTICES

```kotlin
class FlowTestingBestPractices {

    // ✅ Always call awaitComplete or cancelAndIgnoreRemainingEvents
    @Test
    fun `proper cleanup`() = runTest {
        val flow = flowOf(1, 2, 3)

        flow.test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitComplete()  // ✅ Proper cleanup
        }
    }

    // ✅ Use StandardTestDispatcher for time control
    @Test
    fun `use test dispatcher`() = runTest {
        val flow = flow {
            delay(1000)
            emit(1)
        }

        flow.test {
            expectNoEvents()
            advanceTimeBy(1000)
            assertEquals(1, awaitItem())
            awaitComplete()
        }
    }

    // ✅ Test state transitions
    @Test
    fun `test state transitions`() = runTest {
        val stateFlow = MutableStateFlow<UiState>(UiState.Loading)

        stateFlow.test {
            assertTrue(awaitItem() is UiState.Loading)

            stateFlow.value = UiState.Success("Data")
            val state = awaitItem()
            assertTrue(state is UiState.Success)
            assertEquals("Data", (state as UiState.Success).data)

            cancelAndIgnoreRemainingEvents()
        }
    }

    // ✅ Test error scenarios
    @Test
    fun `test error scenarios`() = runTest {
        val flow = flow {
            emit(1)
            throw IOException("Network error")
        }

        flow.test {
            assertEquals(1, awaitItem())
            val error = awaitError()
            assertTrue(error is IOException)
        }
    }

    // ✅ Use expectNoEvents for debouncing
    @Test
    fun `test debouncing`() = runTest {
        val flow = MutableSharedFlow<Int>()

        flow.debounce(500).test {
            expectNoEvents()

            flow.emit(1)
            expectNoEvents()  // Should not emit yet

            advanceTimeBy(500)
            assertEquals(1, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

### KEY TAKEAWAYS

1. **Turbine** simplifies Flow testing with intuitive APIs
2. **awaitItem()** waits for and returns next emission
3. **awaitComplete()** asserts Flow completed successfully
4. **awaitError()** waits for and returns error
5. **expectNoEvents()** asserts no emissions for short duration
6. **cancelAndIgnoreRemainingEvents()** for cleanup
7. **advanceTimeBy()** controls virtual time in tests
8. **StateFlow** always has initial value
9. **SharedFlow** doesn't have initial value
10. **Always cleanup** with awaitComplete or cancelAndIgnoreRemainingEvents

---

## Russian Version

### Постановка задачи

Тестирование Kotlin Flows может быть сложным из-за их асинхронной природы. Turbine - библиотека тестирования, упрощающая тестирование Flow предоставлением интуитивных APIs для проверки эмиссий. Понимание Turbine критично для надёжного тестирования на основе корутин в Android.

**Вопрос:** Что такое Turbine? Как тестировать Flows с Turbine? Как это сравнивается с ручным тестированием Flow? Какие best practices?

### Ключевые выводы

1. **Turbine** упрощает тестирование Flow интуитивными APIs
2. **awaitItem()** ждёт и возвращает следующую эмиссию
3. **awaitComplete()** проверяет успешное завершение Flow
4. **awaitError()** ждёт и возвращает ошибку
5. **expectNoEvents()** проверяет отсутствие эмиссий короткое время
6. **cancelAndIgnoreRemainingEvents()** для очистки
7. **advanceTimeBy()** контролирует виртуальное время в тестах
8. **StateFlow** всегда имеет начальное значение
9. **SharedFlow** не имеет начального значения
10. **Всегда очищайте** с awaitComplete или cancelAndIgnoreRemainingEvents

## Follow-ups

1. How does Turbine handle backpressure?
2. What's the difference between test and testIn?
3. How do you test cold vs hot flows?
4. What are the limitations of Turbine?
5. How do you test flows with conflated emissions?
6. What is the relationship between Turbine and TestScope?
7. How do you test flows with multiple collectors?
8. What are best practices for testing StateFlow vs SharedFlow?
9. How do you test flows in multi-module projects?
10. What are alternatives to Turbine for Flow testing?
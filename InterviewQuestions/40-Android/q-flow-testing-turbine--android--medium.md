---
id: 20251012-400007
title: "Flow Testing with Turbine / Тестирование Flow с Turbine"
aliases: ["Flow Testing with Turbine", "Тестирование Flow с Turbine"]
topic: android
subtopics: [kotlin-flow, testing]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-turbine-testing, q-compose-testing--android--medium, q-unit-testing-coroutines-flow--android--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [android/kotlin-flow, android/testing, coroutines, difficulty/medium, kotlin-flow, turbine, unit-testing]
sources: [https://github.com/cashapp/turbine]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:51:58 pm
---

# Вопрос (RU)
> Что такое Turbine? Как тестировать Flows с Turbine?

# Question (EN)
> What is Turbine? How do you test Flows with Turbine?

---

## Ответ (RU)

**Теория Turbine:**
Turbine - это библиотека тестирования, которая упрощает тестирование Kotlin Flows предоставлением интуитивных APIs для проверки эмиссий. Решает проблему сложности тестирования асинхронных Flow из-за их недетерминированной природы.

**Основные концепции:**
- Упрощает тестирование Flow с помощью декларативных API
- Предоставляет методы для ожидания эмиссий, завершения и ошибок
- Работает с TestScope для контроля времени
- Поддерживает StateFlow, SharedFlow и обычные Flow
- Автоматически обрабатывает отмену и очистку ресурсов

**Настройка Turbine:**
```kotlin
// Добавляем зависимость
dependencies {
    testImplementation "app.cash.turbine:turbine:1.0.0"
    testImplementation "org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3"
}

// Базовое использование
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

**Основные API Turbine:**
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
            awaitComplete()  // Проверяет завершение Flow
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
    fun `expectNoEvents - assert no emissions`() = runTest {
        val flow = flow<Int> {
            delay(100)
            emit(1)
        }

        flow.test {
            expectNoEvents()  // Нет событий короткое время
            advanceTimeBy(100)
            assertEquals(1, awaitItem())
        }
    }
}
```

**Тестирование StateFlow:**
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
            // StateFlow всегда имеет начальное значение
            assertEquals(0, awaitItem())

            viewModel.increment()
            assertEquals(1, awaitItem())

            viewModel.increment()
            assertEquals(2, awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

**Тестирование SharedFlow:**
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
            // SharedFlow не имеет начального значения
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
}
```

**Тестирование Repository Flow:**
```kotlin
interface UserRepository {
    fun getUser(userId: String): Flow<Result<User>>
}

sealed class Result<out T> {
    data object Loading : Result<Nothing>()
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
}

class UserRepositoryTest {

    @Test
    fun `getUser emits loading then success`() = runTest {
        val mockApi = mockk<ApiService>()
        coEvery { mockApi.getUser("123") } returns User("123", "John Doe")

        val repository = UserRepositoryImpl(mockApi)

        repository.getUser("123").test {
            // Первая эмиссия: Loading
            val loading = awaitItem()
            assertTrue(loading is Result.Loading)

            // Вторая эмиссия: Success
            val success = awaitItem()
            assertTrue(success is Result.Success)
            assertEquals("John Doe", (success as Result.Success).data.name)

            awaitComplete()
        }

        coVerify { mockApi.getUser("123") }
    }
}
```

**Тестирование ViewModel UI State:**
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
            // Начальное состояние
            assertTrue(awaitItem() is ProfileUiState.Loading)

            // Загружаем профиль
            viewModel.loadProfile("123")
            advanceUntilIdle()

            // Должно быть успешное состояние
            val state = awaitItem()
            assertTrue(state is ProfileUiState.Success)
            assertEquals("John Doe", (state as ProfileUiState.Success).user.name)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

## Answer (EN)

**Turbine Theory:**
Turbine is a testing library that simplifies testing Kotlin Flows by providing intuitive APIs for asserting emissions. It solves the complexity of testing asynchronous Flows due to their non-deterministic nature.

**Main concepts:**
- Simplifies Flow testing with declarative APIs
- Provides methods for awaiting emissions, completion, and errors
- Works with TestScope for time control
- Supports StateFlow, SharedFlow, and regular Flows
- Automatically handles cancellation and resource cleanup

**Turbine setup:**
```kotlin
// Add dependency
dependencies {
    testImplementation "app.cash.turbine:turbine:1.0.0"
    testImplementation "org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3"
}

// Basic usage
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

**Core Turbine APIs:**
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

**Testing StateFlow:**
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
}
```

**Testing SharedFlow:**
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
}
```

**Testing Repository Flow:**
```kotlin
interface UserRepository {
    fun getUser(userId: String): Flow<Result<User>>
}

sealed class Result<out T> {
    data object Loading : Result<Nothing>()
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
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
}
```

**Testing ViewModel UI State:**
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

            // Should be success state
            val state = awaitItem()
            assertTrue(state is ProfileUiState.Success)
            assertEquals("John Doe", (state as ProfileUiState.Success).user.name)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

## Follow-ups

- How does Turbine handle backpressure in Flow testing?
- What are the differences between test and testIn methods?
- How do you test cold vs hot flows with Turbine?

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-flow-basics--kotlin--easy]] - Flow basics
- [[q-unit-testing-basics--android--easy]] - Unit testing basics

### Related (Same Level)
- [[q-unit-testing-coroutines-flow--android--medium]] - Coroutines testing
- [[q-compose-testing--android--medium]] - Compose testing
- [[q-viewmodel-testing--android--medium]] - ViewModel testing

### Advanced (Harder)
- [[q-advanced-flow-testing--android--hard]] - Advanced Flow testing
- [[q-testing-multiplatform--android--hard]] - Multiplatform testing

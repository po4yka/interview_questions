---
id: android-491
title: Testing ViewModels with Turbine
aliases:
- Testing ViewModels
- Turbine
- Turbine Library
- 2535414238403e32303d3835 ViewModels
topic: android
subtopics:
- coroutines
- testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-flow
- q-android-testing-strategies--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/coroutines
- android/testing-unit
- coroutines
- difficulty/medium
- flow
- testing
- turbine

---

# Вопрос (RU)
> Как тестировать `ViewModel`, которые отдают `Flow`/`StateFlow`, с помощью библиотеки Turbine?

# Question (EN)
> How do you test ViewModels that emit `Flow`/`StateFlow` using the Turbine library?

---

## Ответ (RU)

Подход: Turbine — это библиотека для тестирования, которая упрощает проверку Kotlin `Flow`, предоставляя читаемый API для проверки эмиссий во времени. При тестировании `ViewModel`, которые отдают `StateFlow`/`Flow`, Turbine используют вместе с тестовыми API корутин, чтобы корутины `ViewModel` выполнялись в контролируемой среде.

Ключевые концепции:
- Turbine позволяет последовательно проверять эмиссии `Flow`.
- Предоставляет расширение `test {}` для `Flow`.
- Поддерживает тестирование множественных эмиссий, ошибок и завершения.
- Хорошо работает с тестовыми диспетчерами корутин (`runTest`, `MainDispatcherRule`), что позволяет управлять временем и выполнением.

Код:

```kotlin
// Простое представление UiState
sealed class UiState {
    data object Loading : UiState()
    data class Success(val user: User) : UiState()
    data class Error(val message: String?) : UiState()
}

data class User(val id: String, val name: String)

interface UserRepository {
    suspend fun getUser(userId: String): User
}

class FakeUserRepository(
    private val user: User? = null,
    private val shouldFail: Boolean = false
) : UserRepository {
    override suspend fun getUser(userId: String): User {
        if (shouldFail) throw RuntimeException("Network error")
        return user ?: error("User not set")
    }
}

// Пример ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val user = repository.getUser(userId)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }
}

// Пример использует переопределение Main-диспетчера из kotlinx-coroutines-test.
// В реальных проектах предпочтительно использовать JUnit4 Rule / JUnit5 Extension (MainDispatcherRule).

@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setUp() {
        Dispatchers.setMain(testDispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `loadUser emits Loading then Success states`() = runTest {
        // Given
        val mockUser = User("123", "John Doe")
        val repository = FakeUserRepository(user = mockUser)
        val viewModel = UserViewModel(repository)

        viewModel.uiState.test {
            // Начальное состояние из StateFlow
            assertEquals(UiState.Loading, awaitItem())

            // When
            viewModel.loadUser("123")

            // Продвигаем выполнение до завершения корутин во viewModelScope
            testDispatcher.scheduler.advanceUntilIdle()

            // Затем: повторная эмиссия Loading перед Success
            assertEquals(UiState.Loading, awaitItem())

            val successItem = awaitItem()
            assertTrue(successItem is UiState.Success)
            assertEquals(mockUser, (successItem as UiState.Success).user)

            // Останавливаем сбор, когда необходимые проверки выполнены
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadUser emits Error when repository fails`() = runTest {
        // Given
        val repository = FakeUserRepository(shouldFail = true)
        val viewModel = UserViewModel(repository)

        viewModel.uiState.test {
            // Начальное значение StateFlow
            assertEquals(UiState.Loading, awaitItem())

            // When
            viewModel.loadUser("123")

            testDispatcher.scheduler.advanceUntilIdle()

            // Затем: Loading, затем Error
            assertEquals(UiState.Loading, awaitItem())

            val errorItem = awaitItem()
            assertTrue(errorItem is UiState.Error)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

Объяснение:
1. `test {}` — основная функция-расширение Turbine, которая собирает эмиссии `Flow` в suspend-контексте теста.
2. `awaitItem()` — приостанавливается до следующей эмиссии и возвращает её.
3. `expectNoEvents()` — проверяет, что в течение заданного таймаута не произошло новых событий; больше подходит для конечных `Flow`. Для `StateFlow` (горячего источника с всегда актуальным значением) обычно вместо этого явно завершают сбор с помощью `cancelAndIgnoreRemainingEvents()`.
4. `cancelAndIgnoreRemainingEvents()` — отменяет сбор, когда оставшиеся/будущие эмиссии не важны; рекомендуется вызывать в конце тестов `StateFlow` с Turbine.
5. `runTest` + тестовый диспетчер — обеспечивают контролируемое окружение для корутин. Для `ViewModel` с `viewModelScope` нужно переопределить `Dispatchers.Main` (например, через `Dispatchers.setMain(testDispatcher)` или `MainDispatcherRule`), чтобы их корутины выполнялись на тестовом шедулере.

Преимущества:
- Более читаемо, чем ручной сбор `Flow`.
- Встроенная обработка таймаутов.
- Понятный API для проверок.
- Работает с `StateFlow`, `SharedFlow` и обычными `Flow`.

## Answer (EN)

Approach: Turbine is a testing library that simplifies testing Kotlin Flows by providing a readable API for asserting `Flow` emissions over time. When testing ViewModels that expose `StateFlow`/`Flow`, you combine Turbine with the coroutine test APIs so that the `ViewModel`'s coroutines run in a controlled environment.

Key Concepts:
- Turbine allows you to test `Flow` emissions sequentially.
- Provides `test {}` extension function for Flows.
- Supports testing multiple emissions, errors, and completion.
- Works with coroutine test dispatchers (e.g., `runTest`, `MainDispatcherRule`) so you can control time and execution.

Code:

```kotlin
// Simple UiState representation
sealed class UiState {
    data object Loading : UiState()
    data class Success(val user: User) : UiState()
    data class Error(val message: String?) : UiState()
}

data class User(val id: String, val name: String)

interface UserRepository {
    suspend fun getUser(userId: String): User
}

class FakeUserRepository(
    private val user: User? = null,
    private val shouldFail: Boolean = false
) : UserRepository {
    override suspend fun getUser(userId: String): User {
        if (shouldFail) throw RuntimeException("Network error")
        return user ?: error("User not set")
    }
}

// Example ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val user = repository.getUser(userId)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }
}

// Example uses kotlinx-coroutines-test's Main dispatcher override.
// In real projects prefer a JUnit4 Rule / JUnit5 Extension (MainDispatcherRule).

@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setUp() {
        Dispatchers.setMain(testDispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `loadUser emits Loading then Success states`() = runTest {
        // Given
        val mockUser = User("123", "John Doe")
        val repository = FakeUserRepository(user = mockUser)
        val viewModel = UserViewModel(repository)

        viewModel.uiState.test {
            // Initial state from StateFlow
            assertEquals(UiState.Loading, awaitItem())

            // When
            viewModel.loadUser("123")

            // Advance until coroutines launched in viewModelScope complete
            testDispatcher.scheduler.advanceUntilIdle()

            // Then: Loading emitted again before Success
            assertEquals(UiState.Loading, awaitItem())

            val successItem = awaitItem()
            assertTrue(successItem is UiState.Success)
            assertEquals(mockUser, (successItem as UiState.Success).user)

            // Stop collecting once we've asserted what we care about
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadUser emits Error when repository fails`() = runTest {
        // Given
        val repository = FakeUserRepository(shouldFail = true)
        val viewModel = UserViewModel(repository)

        viewModel.uiState.test {
            // Initial StateFlow value
            assertEquals(UiState.Loading, awaitItem())

            // When
            viewModel.loadUser("123")

            testDispatcher.scheduler.advanceUntilIdle()

            // Then: Loading followed by Error
            assertEquals(UiState.Loading, awaitItem())

            val errorItem = awaitItem()
            assertTrue(errorItem is UiState.Error)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

Explanation:
1. `test {}`  Turbine's main extension function that collects `Flow` emissions in a suspendable test scope.
2. `awaitItem()`  Suspends until the next emission and returns it.
3. `expectNoEvents()`  Asserts that no events occur within the timeout window; better suited for finite Flows. With `StateFlow` (which is hot and always has a current value), you usually stop collection with `cancelAndIgnoreRemainingEvents()` instead of expecting "no more" events.
4. `cancelAndIgnoreRemainingEvents()`  Cancels collection when you don't care about remaining or future emissions  recommended at the end of Turbine-based `StateFlow` tests.
5. `runTest` + test dispatcher  Provide a controlled coroutine environment. For ViewModels using `viewModelScope`, override the main dispatcher (e.g., `Dispatchers.setMain(testDispatcher)` or `MainDispatcherRule`) so their coroutines run on the test scheduler.

Benefits:
- More readable than manual `Flow` collection.
- Built-in timeout handling.
- Clear assertion API.
- Works with `StateFlow`, `SharedFlow`, and regular Flows.

---

## Дополнительные вопросы (RU)

- Как тестировать несколько `Flow` одновременно с помощью Turbine?
- В чём разница между `awaitItem()` и `expectMostRecentItem()`?
- Как обрабатывать таймауты в тестах с Turbine?
- Можно ли использовать Turbine с `SharedFlow` и другими горячими `Flow`?

## Follow-ups

- How do you test multiple Flows simultaneously with Turbine?
- What's the difference between `awaitItem()` and `expectMostRecentItem()`?
- How do you handle timeouts in Turbine tests?
- Can Turbine be used with `SharedFlow` and hot Flows?

## Ссылки (RU)

- [[c-flow]]
- https://github.com/cashapp/turbine
- https://developer.android.com/kotlin/flow/test

## References

- [[c-flow]]
- https://github.com/cashapp/turbine
- https://developer.android.com/kotlin/flow/test

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-viewmodel-pattern--android--easy]]
- [[q-what-is-viewmodel--android--medium]]

### Похожие (средний уровень)
- [[q-testing-viewmodels-coroutines--kotlin--medium]]
- [[q-viewmodel-coroutines-lifecycle--kotlin--medium]]
- [[q-android-testing-strategies--android--medium]]

### Продвинутые (сложнее)
- [[q-compose-custom-layout--android--hard]]

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]]
- [[q-what-is-viewmodel--android--medium]]

### Related (Same Level)
- [[q-testing-viewmodels-coroutines--kotlin--medium]]
- [[q-viewmodel-coroutines-lifecycle--kotlin--medium]]
- [[q-android-testing-strategies--android--medium]]

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]]

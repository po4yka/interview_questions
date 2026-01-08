---\
id: android-491
title: Тестирование ViewModel с Turbine / Testing ViewModels with Turbine
aliases: [2535414238403e32303d3835 ViewModels, Testing ViewModels, Turbine, Turbine Library]
topic: android
subtopics: [coroutines, testing-unit]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-flow, q-accessibility-testing--android--medium, q-android-testing-strategies--android--medium, q-flow-testing-turbine--android--medium, q-integration-testing-strategies--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/coroutines, android/testing-unit, coroutines, difficulty/medium, flow, testing, turbine]

---\
# Вопрос (RU)
> Как тестировать `ViewModel`, которые отдают `Flow`/`StateFlow`, с помощью библиотеки Turbine?

# Question (EN)
> How do you test `ViewModels` that emit `Flow`/`StateFlow` using the Turbine library?

---

## Ответ (RU)

Подход: Turbine — это библиотека для тестирования, которая упрощает проверку Kotlin `Flow`, предоставляя читаемый API для пошаговой проверки эмиссий. При тестировании `ViewModel`, которые отдают `StateFlow`/`Flow`, Turbine используют вместе с тестовыми API корутин, чтобы корутины `ViewModel` выполнялись в контролируемой среде.

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

// Тест с Turbine + runTest.
// В реальных проектах предпочтительно использовать JUnit4 Rule / JUnit5 Extension (MainDispatcherRule),
// который переназначает Dispatchers.Main на тестовый диспетчер.

@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `loadUser emits Loading then Success states`() = runTest {
        // Given
        val mockUser = User("123", "John Doe")
        val repository = FakeUserRepository(user = mockUser)
        val viewModel = UserViewModel(repository)

        viewModel.uiState.test {
            // Первым элементом для StateFlow будет текущее значение (Loading)
            assertEquals(UiState.Loading, awaitItem())

            // When
            viewModel.loadUser("123")

            // Затем: Loading перед Success (из вызова loadUser)
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
5. `runTest` (совместно с `MainDispatcherRule` или другим тестовым маппингом `Dispatchers.Main`) обеспечивает контролируемое окружение для корутин `ViewModel`.

Преимущества:
- Более читаемо, чем ручной сбор `Flow`.
- Встроенная обработка таймаутов.
- Понятный API для проверок.
- Работает с `StateFlow`, `SharedFlow` и обычными `Flow`.

## Answer (EN)

Approach: Turbine is a testing library that simplifies testing Kotlin `Flows` by providing a readable API for asserting emissions step by step. When testing `ViewModels` that expose `StateFlow`/`Flow`, you use Turbine together with the coroutine test APIs so that the `ViewModel`'s coroutines run in a controlled environment.

Key Concepts:
- Turbine allows you to assert `Flow` emissions sequentially.
- `Provides` the `test {}` extension function for `Flows`.
- Supports testing multiple emissions, errors, and completion.
- Works well with coroutine test dispatchers (e.g., `runTest`, `MainDispatcherRule`) so you can control time and execution.

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

// Test using Turbine + runTest.
// In real projects, prefer a JUnit4 Rule / JUnit5 Extension (MainDispatcherRule)
// that maps Dispatchers.Main to a test dispatcher.

@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `loadUser emits Loading then Success states`() = runTest {
        // Given
        val mockUser = User("123", "John Doe")
        val repository = FakeUserRepository(user = mockUser)
        val viewModel = UserViewModel(repository)

        viewModel.uiState.test {
            // For StateFlow, the first item is the current value (Loading)
            assertEquals(UiState.Loading, awaitItem())

            // When
            viewModel.loadUser("123")

            // Then: Loading emitted again before Success (from loadUser)
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
1. `test {}`  Turbine's main extension function that collects `Flow` emissions within a suspendable test scope.
2. `awaitItem()`  Suspends until the next emission and returns it.
3. `expectNoEvents()`  Asserts that no events occur within a timeout; best suited for finite `Flows`. With `StateFlow` (hot with an always-available current value), it's usually better to end collection explicitly using `cancelAndIgnoreRemainingEvents()`.
4. `cancelAndIgnoreRemainingEvents()`  Cancels collection when you don't care about remaining or future emissions; recommended at the end of Turbine-based `StateFlow` tests.
5. `runTest` (together with `MainDispatcherRule` or another test mapping for `Dispatchers.Main`) provides a controlled environment for `ViewModel` coroutines.

Benefits:
- More readable than manual `Flow` collection.
- Built-in timeout handling.
- Clear assertion API.
- Works with `StateFlow`, `SharedFlow`, and regular `Flows`.

---

## Дополнительные Вопросы (RU)

- Как тестировать несколько `Flow` одновременно с помощью Turbine?
- В чём разница между `awaitItem()` и `expectMostRecentItem()`?
- Как обрабатывать таймауты в тестах с Turbine?
- Можно ли использовать Turbine с `SharedFlow` и другими горячими `Flow`?

## Follow-ups

- How do you test multiple `Flows` simultaneously with Turbine?
- What's the difference between `awaitItem()` and `expectMostRecentItem()`?
- How do you handle timeouts in Turbine tests?
- Can Turbine be used with `SharedFlow` and hot `Flows`?

## Ссылки (RU)

- [[c-flow]]
- https://github.com/cashapp/turbine
- https://developer.android.com/kotlin/flow/test

## References

- [[c-flow]]
- https://github.com/cashapp/turbine
- https://developer.android.com/kotlin/flow/test

## Связанные Вопросы (RU)

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

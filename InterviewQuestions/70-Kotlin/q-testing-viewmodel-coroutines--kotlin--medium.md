---
id: kotlin-068
title: "Testing ViewModels with Coroutines / Тестирование ViewModel с корутинами"
aliases: ["Testing ViewModels with Coroutines", "Тестирование ViewModel с корутинами"]

# Classification
topic: kotlin
subtopics: [coroutines, stateflow, viewmodel]
question_kind: coding
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Guide to testing coroutines in ViewModels

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/medium, kotlin, stateflow, testing, turbine, unit-testing, viewmodel]
---
# Вопрос (RU)
> Как тестировать `ViewModel` с корутинами? Объясните `TestCoroutineDispatcher`, `StandardTestDispatcher`, тестирование `StateFlow`/`SharedFlow` и мокирование suspend функций.

---

# Question (EN)
> How do you test `ViewModel`s that use coroutines? Explain `TestCoroutineDispatcher`, `StandardTestDispatcher`, testing `StateFlow`/`SharedFlow`, and mocking suspend functions.

## Ответ (RU)

Тестирование корутин в `ViewModel` требует специальной обработки, чтобы тесты были детерминированными, быстрыми и надёжными. Для этого используются средства `kotlinx-coroutines-test` (в актуальных версиях — `runTest`, `StandardTestDispatcher`/`UnconfinedTestDispatcher` и правило для `Dispatchers.Main`). `TestCoroutineDispatcher` из старого API считается устаревшим и обычно заменяется на `StandardTestDispatcher`.

См. также: [[c-kotlin]], [[c-coroutines]], [[c-viewmodel]], [[c-testing]], [[c-unit-testing]].

### Настройка Зависимостей

```gradle
// build.gradle.kts
dependencies {
    // Тесты корутин
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")

    // Turbine для тестирования Flow
    testImplementation("app.cash.turbine:turbine:1.0.0")

    // MockK для моков
    testImplementation("io.mockk:mockk:1.13.8")

    // JUnit
    testImplementation("junit:junit:4.13.2")

    // Architecture Components testing (например, InstantTaskExecutorRule)
    testImplementation("androidx.arch.core:core-testing:2.2.0")
}
```

### MainDispatcherRule

Создаём правило, подменяющее `Dispatchers.Main` тестовым диспетчером, чтобы `viewModelScope` и код, использующий Main, работали в контролируемом окружении. Для детерминированности обычно используют `StandardTestDispatcher`.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestDispatcher
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import org.junit.rules.TestWatcher
import org.junit.runner.Description

@ExperimentalCoroutinesApi
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Базовый Пример `ViewModel` И Теста

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = repository.getUsers()
                _users.value = result
            } finally {
                _isLoading.value = false
            }
        }
    }
}
```

```kotlin
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test

@ExperimentalCoroutinesApi
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: UserViewModel
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        repository = mockk()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUsers обновляет состояние корректно`() = runTest {
        // Given
        val expectedUsers = listOf(
            User(1, "Alice"),
            User(2, "Bob")
        )
        coEvery { repository.getUsers() } returns expectedUsers

        // When
        viewModel.loadUsers()
        advanceUntilIdle()

        // Then
        assertEquals(expectedUsers, viewModel.users.value)
        assertEquals(false, viewModel.isLoading.value)
    }
}
```

### Тестирование `StateFlow` (флаги загрузки)

```kotlin
import io.mockk.coEvery
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@Test
fun `verify loading states`() = runTest {
    // Given: эмулируем работу с задержкой, используя виртуальное время
    coEvery { repository.getUsers() } coAnswers {
        delay(100)
        emptyList()
    }

    val loadingStates = mutableListOf<Boolean>()

    // Коллектим используя планировщик runTest
    val job = launch {
        viewModel.isLoading.collect { loadingStates.add(it) }
    }

    // When
    viewModel.loadUsers()
    advanceUntilIdle()

    // Then
    assertEquals(listOf(false, true, false), loadingStates)

    job.cancel()
}
```

### Тестирование С Turbine

Turbine упрощает тестирование `Flow`/`StateFlow`/`SharedFlow`:

```kotlin
import app.cash.turbine.test
import io.mockk.coEvery
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@Test
fun `loadUsers эмитит корректные значения через Turbine`() = runTest {
    // Given
    val users = listOf(User(1, "Alice"))
    coEvery { repository.getUsers() } returns users

    // When/Then
    viewModel.users.test {
        assertEquals(emptyList<User>(), awaitItem()) // Начальное значение

        viewModel.loadUsers()

        assertEquals(users, awaitItem()) // Обновлённое значение
    }
}

@Test
fun `isLoading эмитит корректную последовательность`() = runTest {
    coEvery { repository.getUsers() } coAnswers {
        delay(100)
        emptyList()
    }

    viewModel.isLoading.test {
        assertEquals(false, awaitItem()) // Initial

        viewModel.loadUsers()

        assertEquals(true, awaitItem())  // Loading
        assertEquals(false, awaitItem()) // Loaded

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование Сценариев Ошибок

```kotlin
import io.mockk.coEvery
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test
import java.io.IOException

@Test
fun `loadUsers корректно обрабатывает ошибку`() = runTest {
    // Given
    val exception = IOException("Network error")
    coEvery { repository.getUsers() } throws exception

    // When
    viewModel.loadUsers()
    advanceUntilIdle()

    // Then
    assertEquals(emptyList<User>(), viewModel.users.value)
    assertEquals(false, viewModel.isLoading.value)
    // Опционально: проверить отдельное состояние ошибки, если оно есть
}
```

Расширенный пример `ViewModel` с `UiState` (как отдельный вариант реализации):

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val users = repository.getUsers()
                _uiState.value = UiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class UiState {
    object Initial : UiState()
    object Loading : UiState()
    data class Success(val users: List<User>) : UiState()
    data class Error(val message: String) : UiState()
}

@Test
fun `loadUsers обрабатывает сетевую ошибку`() = runTest {
    // Given
    coEvery { repository.getUsers() } throws IOException("Network error")

    // When/Then
    viewModel.uiState.test {
        assertEquals(UiState.Initial, awaitItem())

        viewModel.loadUsers()

        assertEquals(UiState.Loading, awaitItem())
        val errorState = awaitItem() as UiState.Error
        assertTrue(errorState.message.contains("Network error"))
    }
}
```

### Тестирование `SharedFlow` Событий

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch

class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun login(email: String, password: String) {
        viewModelScope.launch {
            try {
                authRepository.login(email, password)
                _events.emit(Event.NavigateToHome)
            } catch (e: Exception) {
                _events.emit(Event.ShowError(e.message ?: "Login failed"))
            }
        }
    }
}

sealed class Event {
    object NavigateToHome : Event()
    data class ShowError(val message: String) : Event()
}
```

```kotlin
import app.cash.turbine.test
import io.mockk.coEvery
import io.mockk.just
import io.mockk.runs
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

@Test
fun `успешный логин эмитит NavigateToHome`() = runTest {
    // Given
    coEvery { authRepository.login(any(), any()) } just runs

    // When/Then
    viewModel.events.test {
        viewModel.login("test@example.com", "password")

        val event = awaitItem()
        assertTrue(event is Event.NavigateToHome)
    }
}

@Test
fun `ошибка логина эмитит ShowError`() = runTest {
    // Given
    coEvery { authRepository.login(any(), any()) } throws Exception("Invalid credentials")

    // When/Then
    viewModel.events.test {
        viewModel.login("test@example.com", "wrong")

        val event = awaitItem() as Event.ShowError
        assertEquals("Invalid credentials", event.message)
    }
}
```

### Мокирование Suspend-функций

```kotlin
class UserRepository {
    suspend fun getUser(id: Int): User {
        // Network call
        TODO()
    }

    suspend fun saveUser(user: User) {
        // Database write
        TODO()
    }
}
```

```kotlin
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import kotlinx.coroutines.delay
import kotlinx.coroutines.test.currentTime
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@Test
fun `мокирование suspend функции с возвращаемым значением`() = runTest {
    val repository = mockk<UserRepository>()
    val expectedUser = User(1, "Alice")

    coEvery { repository.getUser(1) } returns expectedUser

    val result = repository.getUser(1)

    assertEquals(expectedUser, result)
    coVerify { repository.getUser(1) }
}

@Test
fun `мокирование suspend функции с Unit`() = runTest {
    val repository = mockk<UserRepository>()
    val user = User(1, "Alice")

    coEvery { repository.saveUser(user) } just runs

    repository.saveUser(user)

    coVerify { repository.saveUser(user) }
}

@Test
fun `мокирование suspend функции с delay и виртуальным временем`() = runTest {
    val repository = mockk<UserRepository>()

    coEvery { repository.getUser(1) } coAnswers {
        delay(100)
        User(1, "Alice")
    }

    val start = currentTime
    val result = repository.getUser(1)
    val end = currentTime

    assertEquals(User(1, "Alice"), result)
    assertEquals(100, end - start) // Используется виртуальное время runTest
}
```

### Тестирование Конкурентных Операций

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.launch

class DataViewModel(private val repository: DataRepository) : ViewModel() {
    fun loadMultipleSources() {
        viewModelScope.launch {
            val deferred1 = async { repository.getSource1() }
            val deferred2 = async { repository.getSource2() }
            val deferred3 = async { repository.getSource3() }

            val results = awaitAll(deferred1, deferred2, deferred3)
            // Обработка результатов
        }
    }
}
```

```kotlin
import io.mockk.coEvery
import io.mockk.coVerify
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Test

@Test
fun `loadMultipleSources вызывает все источники`() = runTest {
    // Given
    coEvery { repository.getSource1() } returns Data("source1")
    coEvery { repository.getSource2() } returns Data("source2")
    coEvery { repository.getSource3() } returns Data("source3")

    // When
    viewModel.loadMultipleSources()
    advanceUntilIdle()

    // Then
    coVerify { repository.getSource1() }
    coVerify { repository.getSource2() }
    coVerify { repository.getSource3() }
}
```

### Тестирование Коллекции `Flow`

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn

class ObservingViewModel(
    private val repository: DataRepository
) : ViewModel() {
    val data: StateFlow<List<Item>> = repository.observeData()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

```kotlin
import io.mockk.every
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@Test
fun `data коллектит значения из репозитория`() = runTest {
    // Given
    val items = listOf(Item(1), Item(2))
    val repositoryFlow = MutableStateFlow(items)
    every { repository.observeData() } returns repositoryFlow

    // When
    val viewModel = ObservingViewModel(repository)

    // Then
    assertEquals(items, viewModel.data.value)

    // Обновляем `Flow` репозитория
    val newItems = listOf(Item(3), Item(4))
    repositoryFlow.value = newItems

    advanceUntilIdle()
    assertEquals(newItems, viewModel.data.value)
}
```

### Лучшие Практики (RU)

#### ДЕЛАТЬ:
```kotlin
// Использовать MainDispatcherRule для подмены Dispatchers.Main
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// Использовать runTest для тестов с корутинами
@Test
fun test() = runTest {
    // Test code
}

// Использовать Turbine для тестирования Flow/StateFlow/SharedFlow
flow.test {
    assertEquals(expected, awaitItem())
}

// Мокировать suspend-функции через coEvery/coVerify
coEvery { repository.getData() } returns data
coVerify { repository.getData() }

// Использовать advanceUntilIdle для завершения всех корутин перед ассертом
viewModel.loadData()
advanceUntilIdle()
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не забывать использовать MainDispatcherRule, если используется Dispatchers.Main/viewModelScope
class ViewModelTest { // Нет @get:Rule — код может падать
    @Test
    fun test() = runTest {
        viewModel.loadData()
    }
}

// Не использовать обычный verify для suspend-функций
// verify { repository.getData() } // Неверно
coVerify { repository.getData() } // Верно

// Не использовать runBlocking вместо runTest
@Test
fun test() {
    runBlocking { // Антипаттерн в юнит-тестах
        viewModel.loadData()
    }
}

// Вместо этого:
@Test
fun test() = runTest {
    viewModel.loadData()
}
```

---

## Answer (EN)

Testing coroutines in `ViewModel`s requires special handling to make tests deterministic, fast, and reliable. Use `kotlinx-coroutines-test` utilities (`runTest`, `TestDispatcher` implementations, and a rule to override `Dispatchers.Main`). Note: `TestCoroutineDispatcher` from the old API is deprecated; prefer `StandardTestDispatcher`/`UnconfinedTestDispatcher`, with `StandardTestDispatcher` as the default choice for deterministic behavior.

See also: [[c-kotlin]], [[c-coroutines]], [[c-viewmodel]], [[c-testing]], [[c-unit-testing]].

### Setup Dependencies

```gradle
// build.gradle.kts
dependencies {
    // Coroutines test
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")

    // Turbine for Flow testing
    testImplementation("app.cash.turbine:turbine:1.0.0")

    // MockK for mocking
    testImplementation("io.mockk:mockk:1.13.8")

    // JUnit
    testImplementation("junit:junit:4.13.2")

    // Architecture components testing (e.g. InstantTaskExecutorRule)
    testImplementation("androidx.arch.core:core-testing:2.2.0")
}
```

### MainDispatcherRule

Create a test rule to replace `Dispatchers.Main` so that `viewModelScope` (which uses `Dispatchers.Main.immediate`) runs on a controllable test dispatcher. Prefer `StandardTestDispatcher` for deterministic scheduling.

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestDispatcher
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import org.junit.rules.TestWatcher
import org.junit.runner.Description

@ExperimentalCoroutinesApi
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Basic `ViewModel` Test

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = repository.getUsers()
                _users.value = result
            } finally {
                _isLoading.value = false
            }
        }
    }
}
```

```kotlin
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test

@ExperimentalCoroutinesApi
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: UserViewModel
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        repository = mockk()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUsers updates state correctly`() = runTest {
        // Given
        val expectedUsers = listOf(
            User(1, "Alice"),
            User(2, "Bob")
        )
        coEvery { repository.getUsers() } returns expectedUsers

        // When
        viewModel.loadUsers()
        advanceUntilIdle()

        // Then
        assertEquals(expectedUsers, viewModel.users.value)
        assertEquals(false, viewModel.isLoading.value)
    }
}
```

### Testing `StateFlow`

```kotlin
import io.mockk.coEvery
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@Test
fun `verify loading states`() = runTest {
    // Given: simulate some work to exercise loading flags with virtual time
    coEvery { repository.getUsers() } coAnswers {
        delay(100)
        emptyList()
    }

    val loadingStates = mutableListOf<Boolean>()

    // Collect using runTest's scheduler
    val job = launch {
        viewModel.isLoading.collect { loadingStates.add(it) }
    }

    // When
    viewModel.loadUsers()
    advanceUntilIdle()

    // Then
    assertEquals(listOf(false, true, false), loadingStates)

    job.cancel()
}
```

### Testing with Turbine

Turbine makes testing `Flow`s and `StateFlow`/`SharedFlow` easier:

```kotlin
import app.cash.turbine.test
import io.mockk.coEvery
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@Test
fun `loadUsers emits correct states using Turbine`() = runTest {
    // Given
    val users = listOf(User(1, "Alice"))
    coEvery { repository.getUsers() } returns users

    // When/Then
    viewModel.users.test {
        assertEquals(emptyList<User>(), awaitItem()) // Initial value

        viewModel.loadUsers()

        assertEquals(users, awaitItem()) // Updated value
    }
}

@Test
fun `isLoading emits correct sequence`() = runTest {
    coEvery { repository.getUsers() } coAnswers {
        delay(100)
        emptyList()
    }

    viewModel.isLoading.test {
        assertEquals(false, awaitItem()) // Initial

        viewModel.loadUsers()

        assertEquals(true, awaitItem())  // Loading
        assertEquals(false, awaitItem()) // Loaded

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Testing Error Scenarios

```kotlin
import io.mockk.coEvery
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test
import java.io.IOException

@Test
fun `loadUsers handles error correctly`() = runTest {
    // Given
    val exception = IOException("Network error")
    coEvery { repository.getUsers() } throws exception

    // When
    viewModel.loadUsers()
    advanceUntilIdle()

    // Then
    assertEquals(emptyList<User>(), viewModel.users.value)
    assertEquals(false, viewModel.isLoading.value)
    // Optionally assert error state if exposed
}
```

Enhanced `ViewModel` with `UiState` (separate variant):

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val users = repository.getUsers()
                _uiState.value = UiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class UiState {
    object Initial : UiState()
    object Loading : UiState()
    data class Success(val users: List<User>) : UiState()
    data class Error(val message: String) : UiState()
}
```

```kotlin
import app.cash.turbine.test
import io.mockk.coEvery
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.IOException

@Test
fun `loadUsers handles network error`() = runTest {
    // Given
    coEvery { repository.getUsers() } throws IOException("Network error")

    // When/Then
    viewModel.uiState.test {
        assertEquals(UiState.Initial, awaitItem())

        viewModel.loadUsers()

        assertEquals(UiState.Loading, awaitItem())
        val errorState = awaitItem() as UiState.Error
        assertTrue(errorState.message.contains("Network error"))
    }
}
```

### Testing `SharedFlow` Events

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch

class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun login(email: String, password: String) {
        viewModelScope.launch {
            try {
                authRepository.login(email, password)
                _events.emit(Event.NavigateToHome)
            } catch (e: Exception) {
                _events.emit(Event.ShowError(e.message ?: "Login failed"))
            }
        }
    }
}

sealed class Event {
    object NavigateToHome : Event()
    data class ShowError(val message: String) : Event()
}
```

```kotlin
import app.cash.turbine.test
import io.mockk.coEvery
import io.mockk.just
import io.mockk.runs
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

@Test
fun `login success emits NavigateToHome event`() = runTest {
    // Given
    coEvery { authRepository.login(any(), any()) } just runs

    // When/Then
    viewModel.events.test {
        viewModel.login("test@example.com", "password")

        val event = awaitItem()
        assertTrue(event is Event.NavigateToHome)
    }
}

@Test
fun `login failure emits ShowError event`() = runTest {
    // Given
    coEvery { authRepository.login(any(), any()) } throws Exception("Invalid credentials")

    // When/Then
    viewModel.events.test {
        viewModel.login("test@example.com", "wrong")

        val event = awaitItem() as Event.ShowError
        assertEquals("Invalid credentials", event.message)
    }
}
```

### Mocking Suspend Functions

```kotlin
class UserRepository {
    suspend fun getUser(id: Int): User {
        // Network call
        TODO()
    }

    suspend fun saveUser(user: User) {
        // Database write
        TODO()
    }
}
```

```kotlin
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import kotlinx.coroutines.delay
import kotlinx.coroutines.test.currentTime
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@Test
fun `mock suspend function with return value`() = runTest {
    val repository = mockk<UserRepository>()
    val expectedUser = User(1, "Alice")

    coEvery { repository.getUser(1) } returns expectedUser

    val result = repository.getUser(1)

    assertEquals(expectedUser, result)
    coVerify { repository.getUser(1) }
}

@Test
fun `mock suspend function with Unit return`() = runTest {
    val repository = mockk<UserRepository>()
    val user = User(1, "Alice")

    coEvery { repository.saveUser(user) } just runs

    repository.saveUser(user)

    coVerify { repository.saveUser(user) }
}

@Test
fun `mock suspend function with delay uses virtual time`() = runTest {
    val repository = mockk<UserRepository>()

    coEvery { repository.getUser(1) } coAnswers {
        delay(100)
        User(1, "Alice")
    }

    val start = currentTime
    val result = repository.getUser(1)
    val end = currentTime

    assertEquals(User(1, "Alice"), result)
    assertEquals(100, end - start) // Uses runTest's virtual time
}
```

### Testing Concurrent Operations

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.launch

class DataViewModel(private val repository: DataRepository) : ViewModel() {
    fun loadMultipleSources() {
        viewModelScope.launch {
            val deferred1 = async { repository.getSource1() }
            val deferred2 = async { repository.getSource2() }
            val deferred3 = async { repository.getSource3() }

            val results = awaitAll(deferred1, deferred2, deferred3)
            // Process results
        }
    }
}
```

```kotlin
import io.mockk.coEvery
import io.mockk.coVerify
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Test

@Test
fun `loadMultipleSources calls all repositories`() = runTest {
    // Given
    coEvery { repository.getSource1() } returns Data("source1")
    coEvery { repository.getSource2() } returns Data("source2")
    coEvery { repository.getSource3() } returns Data("source3")

    // When
    viewModel.loadMultipleSources()
    advanceUntilIdle()

    // Then
    coVerify { repository.getSource1() }
    coVerify { repository.getSource2() }
    coVerify { repository.getSource3() }
}
```

### Testing `Flow` Collection

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn

class ObservingViewModel(
    private val repository: DataRepository
) : ViewModel() {
    val data: StateFlow<List<Item>> = repository.observeData()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

```kotlin
import io.mockk.every
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@Test
fun `data collects from repository flow`() = runTest {
    // Given
    val items = listOf(Item(1), Item(2))
    val repositoryFlow = MutableStateFlow(items)
    every { repository.observeData() } returns repositoryFlow

    // When
    val viewModel = ObservingViewModel(repository)

    // Then
    assertEquals(items, viewModel.data.value)

    // Update repository flow
    val newItems = listOf(Item(3), Item(4))
    repositoryFlow.value = newItems

    advanceUntilIdle()
    assertEquals(newItems, viewModel.data.value)
}
```

### Best Practices

#### DO:
```kotlin
// Use MainDispatcherRule to replace Dispatchers.Main
@get:Rule
val mainDispatcherRule = MainDispatcherRule()

// Use runTest for coroutine tests
@Test
fun test() = runTest {
    // Test code
}

// Use Turbine for Flow/StateFlow/SharedFlow testing
flow.test {
    assertEquals(expected, awaitItem())
}

// Mock suspend functions with coEvery
coEvery { repository.getData() } returns data

// Verify suspend function calls with coVerify
coVerify { repository.getData() }

// Use advanceUntilIdle to complete all launched coroutines when asserting final state
viewModel.loadData()
advanceUntilIdle()
```

#### DON'T:
```kotlin
// Don't forget to use MainDispatcherRule when code depends on Dispatchers.Main or viewModelScope
class ViewModelTest { // Missing @get:Rule may cause crashes
    @Test
    fun test() = runTest {
        viewModel.loadData()
    }
}

// Don't use regular verify for suspend functions
// verify { repository.getData() } // Wrong
coVerify { repository.getData() } // Correct

// Don't mix blocking and suspending with runBlocking in tests
@Test
fun test() {
    runBlocking { // Don't use runBlocking in tests
        viewModel.loadData()
    }
}

// Use runTest instead
@Test
fun test() = runTest {
    viewModel.loadData()
}
```

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этого подхода от тестирования в Java?
- Когда на практике вы будете использовать такой подход к тестированию `ViewModel` с корутинами?
- Какие распространённые ошибки и подводные камни стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Testing Kotlin Coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing StateFlow](https://developer.android.com/kotlin/flow/test)
- [Turbine Documentation](https://github.com/cashapp/turbine)

## References

- [Testing Kotlin Coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing StateFlow](https://developer.android.com/kotlin/flow/test)
- [Turbine Documentation](https://github.com/cashapp/turbine)

## Связанные Вопросы (RU)

- [[q-testing-viewmodels-coroutines--kotlin--medium]]
- [[q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## Related Questions

- [[q-testing-viewmodels-coroutines--kotlin--medium]]
- [[q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## MOC-ссылки (RU)

- [[moc-kotlin]]

## MOC Links

- [[moc-kotlin]]

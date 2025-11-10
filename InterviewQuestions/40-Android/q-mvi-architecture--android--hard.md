---
id: android-326
title: "MVI Architecture / Архитектура MVI"
aliases: [Model-View-Intent, MVI, MVI паттерн, Архитектура MVI]
topic: android
subtopics: [architecture-mvi, coroutines, ui-state]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-android-ui-composition]
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-mvi, android/coroutines, android/ui-state, architecture, difficulty/hard, state-management, unidirectional-data-flow]

---

# Вопрос (RU)
> Объясните архитектурный паттерн MVI (Model-`View`-`Intent`). В чем его ключевые отличия от MVVM?

# Question (EN)
> Explain the MVI (Model-`View`-`Intent`) architecture pattern. How does it differ from MVVM?

---

## Ответ (RU)

**MVI (Model-`View`-`Intent`)** - архитектурный паттерн с **unidirectional data flow** (однонаправленным потоком данных), где UI состояние иммутабельно и изменяется только через явные намерения (`Intent`).

### Компоненты MVI

**Циклический поток данных**:
```
Intent → Processor → Model → View → Intent
```

1. **`Intent`** - намерения пользователя (клик, ввод текста, загрузка данных)
2. **Model** - иммутабельное состояние UI (data class)
3. **`View`** - отрисовывает UI на основе Model
4. **Processor** - обрабатывает `Intent` → создает новый Model (Reducer / UseCase / Middleware)

### Базовая Реализация

```kotlin
// Model - единое иммутабельное состояние
data class UserScreenState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

// Intent - действия пользователя
sealed class UserIntent {
    data class LoadUser(val userId: Int) : UserIntent()
    object RetryLoading : UserIntent()
}

// ViewModel - обрабатывает Intent
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _state = MutableStateFlow(UserScreenState())
    val state: StateFlow<UserScreenState> = _state.asStateFlow()

    fun processIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUser -> loadUser(intent.userId)
            is UserIntent.RetryLoading -> loadUser(/* last used id or cached params */ 1)
        }
    }

    private fun loadUser(userId: Int) {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)

            try {
                val user = repository.getUser(userId)
                _state.value = _state.value.copy(
                    isLoading = false,
                    user = user
                )
            } catch (e: Exception) {
                _state.value = _state.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }
}

// View - отправляет Intent, рендерит State
@Composable
fun UserScreen(
    userId: Int,
    viewModel: UserViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(userId) {
        viewModel.processIntent(UserIntent.LoadUser(userId))
    }

    when {
        state.isLoading -> LoadingIndicator()
        state.error != null -> ErrorView(
            message = state.error!!,
            onRetry = {
                viewModel.processIntent(UserIntent.RetryLoading)
            }
        )
        state.user != null -> UserContent(state.user!!)
    }
}
```

### MVI Vs MVVM

| Аспект | MVVM | MVI |
|--------|------|-----|
| **State** | Множественные `LiveData`/`StateFlow` | Единое иммутабельное состояние |
| **Updates** | Прямые вызовы методов | `Intent`-based |
| **Data flow** | Bi-directional | Unidirectional |
| **Testability** | Хорошая | Отличная (pure functions) |
| **Boilerplate** | Меньше | Больше |
| **Predictability** | Средняя | Высокая |

**MVVM**: `viewModel.loadUser()`, `viewModel.retry()`, `viewModel.clearError()`
**MVI**: `viewModel.processIntent(UserIntent.LoadUser(id))`

### Side Effects - Одноразовые События

✅ **Правильно**: State для UI, отдельный поток для событий (`Channel`/`SharedFlow`)

```kotlin
// State - для постоянного UI

data class LoginState(
    val email: String = "",
    val isLoading: Boolean = false,
    val emailError: String? = null
)

// Side Effects - одноразовые события
sealed class LoginSideEffect {
    data class NavigateToHome(val userId: Int) : LoginSideEffect()
    data class ShowToast(val message: String) : LoginSideEffect()
}

class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    private val _sideEffect = Channel<LoginSideEffect>(Channel.BUFFERED)
    val sideEffect = _sideEffect.receiveAsFlow()

    fun processIntent(intent: LoginIntent) {
        when (intent) {
            is LoginIntent.LoginClicked -> login()
            is LoginIntent.EmailChanged ->
                _state.value = _state.value.copy(email = intent.email, emailError = null)
        }
    }

    private fun login() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)

            try {
                val user = authRepository.login(/* ... */)
                _state.value = _state.value.copy(isLoading = false)
                _sideEffect.send(LoginSideEffect.NavigateToHome(user.id))
            } catch (e: Exception) {
                _state.value = _state.value.copy(isLoading = false)
                _sideEffect.send(LoginSideEffect.ShowToast(e.message ?: "Login error"))
            }
        }
    }
}

// View - обрабатываем side effects
@Composable
fun LoginScreen(
    viewModel: LoginViewModel,
    onNavigateToHome: (Int) -> Unit,
    showToast: (String) -> Unit
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.sideEffect.collect { effect ->
            when (effect) {
                is LoginSideEffect.NavigateToHome ->
                    onNavigateToHome(effect.userId)
                is LoginSideEffect.ShowToast ->
                    showToast(effect.message)
            }
        }
    }

    // UI рендерится на основе state
}
```

❌ **Неправильно**: события в State

```kotlin
// Плохо - навигация в State

data class LoginState(
    val email: String = "",
    val isLoading: Boolean = false,
    val navigateToHome: Boolean = false  // Проблема: не сбросится автоматически, переиспользуется при recreate
)
```

### Reducer Pattern - Чистые Функции

```kotlin
// Reducer - pure function: (State, Intent) -> State
object LoginReducer {
    fun reduce(state: LoginState, intent: LoginIntent): LoginState {
        return when (intent) {
            is LoginIntent.EmailChanged -> state.copy(
                email = intent.email,
                emailError = null
            )
            is LoginIntent.LoginStarted -> state.copy(isLoading = true)
            is LoginIntent.LoginSuccess -> state.copy(isLoading = false)
            is LoginIntent.LoginFailed -> state.copy(isLoading = false)
            is LoginIntent.LoginClicked -> state // side effect отдельно
        }
    }
}

// ViewModel использует Reducer
class LoginReducerViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun processIntent(intent: LoginIntent) {
        // ✅ Применяем чистую функцию
        _state.value = LoginReducer.reduce(_state.value, intent)

        // Side effects отдельно
        when (intent) {
            is LoginIntent.LoginClicked -> performLogin()
            else -> Unit
        }
    }

    private fun performLogin() {
        viewModelScope.launch {
            // ... side-effectful login, диспатч LoginStarted/LoginSuccess/LoginFailed
        }
    }
}

// ✅ Легко тестировать
@Test
fun `reducer is pure function`() {
    val state = LoginState(email = "old@test.com")
    val intent = LoginIntent.EmailChanged("new@test.com")

    val result1 = LoginReducer.reduce(state, intent)
    val result2 = LoginReducer.reduce(state, intent)

    assertEquals(result1, result2)  // Всегда одинаковый результат
    assertEquals("old@test.com", state.email)  // Original не изменился
}
```

### Вложенные Состояния Для Сложных Экранов

```kotlin
// Complex State - декомпозиция на подсостояния
data class ProductListState(
    val products: List<Product> = emptyList(),
    val filter: FilterState = FilterState(),
    val pagination: PaginationState = PaginationState(),
    val ui: UIState = UIState()
)

data class FilterState(
    val query: String = "",
    val category: Category? = null,
    val sortBy: SortOption = SortOption.NAME
)

data class PaginationState(
    val currentPage: Int = 0,
    val hasMore: Boolean = true,
    val isLoadingMore: Boolean = false
)

// Intent охватывает все действия
sealed class ProductListIntent {
    data class SearchQueryChanged(val query: String) : ProductListIntent()
    data class CategorySelected(val category: Category?) : ProductListIntent()
    object LoadMore : ProductListIntent()
    object Refresh : ProductListIntent()
}
```

### Middleware Для Cross-cutting Concerns

```kotlin
// Middleware обрабатывает side effects
interface Middleware<I, S> {
    suspend fun process(intent: I, state: S, dispatch: (I) -> Unit)
}

class AnalyticsMiddleware(
    private val analytics: Analytics
) : Middleware<LoginIntent, LoginState> {
    override suspend fun process(
        intent: LoginIntent,
        state: LoginState,
        dispatch: (LoginIntent) -> Unit
    ) {
        when (intent) {
            is LoginIntent.LoginClicked ->
                analytics.logEvent("login_attempt")
            is LoginIntent.LoginSuccess ->
                analytics.logEvent("login_success")
            else -> Unit
        }
    }
}

class LoginWithMiddlewareViewModel(
    private val middlewares: List<Middleware<LoginIntent, LoginState>>,
    private val reducer: (LoginState, LoginIntent) -> LoginState
) : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun processIntent(intent: LoginIntent) {
        viewModelScope.launch {
            // ✅ Выполняем middleware (side effects)
            middlewares.forEach { it.process(intent, _state.value, ::processIntent) }

            // Применяем reducer (pure)
            _state.value = reducer(_state.value, intent)
        }
    }
}
```

### Time Travel Debugging

```kotlin
// Сохраняем историю состояний для debugging
class DebuggableViewModel<I, S>(
    initialState: S,
    private val reducer: (S, I) -> S
) : ViewModel() {
    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<S> = _state.asStateFlow()

    private val stateHistory = mutableListOf<Pair<I, S>>()

    fun processIntent(intent: I) {
        val newState = reducer(_state.value, intent)
        stateHistory.add(intent to newState)
        _state.value = newState
    }

    // Time travel
    fun replayTo(index: Int) {
        if (index in stateHistory.indices) {
            _state.value = stateHistory[index].second
        }
    }

    fun undo() {
        if (stateHistory.size > 1) {
            stateHistory.removeLast()
            _state.value = stateHistory.last().second
        }
    }
}
```

### Best Practices

✅ **Правильно**:
- Единое иммутабельное состояние (data class)
- Все действия через `Intent`
- Side effects через `Channel` (BUFFERED)/`SharedFlow`
- Reducer - чистые функции
- `state.copy()` для изменений

❌ **Неправильно**:
- Мутация state: `_state.value.items.add(item)`
- События в State: `navigateToHome: Boolean`
- Прямые вызовы методов вместо `Intent` (в MVI-контексте)
- Множественные источники состояния

---

## Answer (EN)

**MVI (Model-`View`-`Intent`)** is an architecture pattern with **unidirectional data flow**, where UI state is immutable and changes only through explicit `Intent`s.

### MVI Components

**Cyclic data flow**:
```
Intent → Processor → Model → View → Intent
```

1. **`Intent`** - user actions/events
2. **Model** - single immutable UI state
3. **`View`** - renders UI from Model
4. **Processor** - processes `Intent` → creates new Model (Reducer / UseCase / Middleware)

### Basic Implementation

```kotlin
// Model - single immutable state
data class UserScreenState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

// Intent - user actions
sealed class UserIntent {
    data class LoadUser(val userId: Int) : UserIntent()
    object RetryLoading : UserIntent()
}

// ViewModel - processes Intent
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _state = MutableStateFlow(UserScreenState())
    val state: StateFlow<UserScreenState> = _state.asStateFlow()

    fun processIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUser -> loadUser(intent.userId)
            is UserIntent.RetryLoading -> loadUser(/* last used id or cached params */ 1)
        }
    }

    private fun loadUser(userId: Int) {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)

            try {
                val user = repository.getUser(userId)
                _state.value = _state.value.copy(
                    isLoading = false,
                    user = user
                )
            } catch (e: Exception) {
                _state.value = _state.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }
}

// View - sends Intents, renders State
@Composable
fun UserScreen(
    userId: Int,
    viewModel: UserViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(userId) {
        viewModel.processIntent(UserIntent.LoadUser(userId))
    }

    when {
        state.isLoading -> LoadingIndicator()
        state.error != null -> ErrorView(
            message = state.error!!,
            onRetry = {
                viewModel.processIntent(UserIntent.RetryLoading)
            }
        )
        state.user != null -> UserContent(state.user!!)
    }
}
```

### MVI Vs MVVM

| Aspect | MVVM | MVI |
|--------|------|-----|
| **State** | Multiple `LiveData`/`StateFlow` | Single immutable state |
| **Updates** | Direct method calls | `Intent`-based |
| **Data flow** | Bi-directional | Unidirectional |
| **Testability** | Good | Excellent (pure functions) |
| **Boilerplate** | Less | More |
| **Predictability** | Medium | High |

**MVVM**: `viewModel.loadUser()`, `viewModel.retry()`
**MVI**: `viewModel.processIntent(UserIntent.LoadUser(id))`

### Side Effects - One-time Events

✅ **Correct**: State for UI, separate stream for events (`Channel`/`SharedFlow`)

```kotlin
// State - for persistent UI

data class LoginState(
    val email: String = "",
    val isLoading: Boolean = false,
    val emailError: String? = null
)

// Side Effects - one-time events
sealed class LoginSideEffect {
    data class NavigateToHome(val userId: Int) : LoginSideEffect()
    data class ShowToast(val message: String) : LoginSideEffect()
}

class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    private val _sideEffect = Channel<LoginSideEffect>(Channel.BUFFERED)
    val sideEffect = _sideEffect.receiveAsFlow()

    fun processIntent(intent: LoginIntent) {
        when (intent) {
            is LoginIntent.LoginClicked -> login()
            is LoginIntent.EmailChanged ->
                _state.value = _state.value.copy(email = intent.email, emailError = null)
        }
    }

    private fun login() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)

            try {
                val user = authRepository.login(/* ... */)
                _state.value = _state.value.copy(isLoading = false)
                _sideEffect.send(LoginSideEffect.NavigateToHome(user.id))
            } catch (e: Exception) {
                _state.value = _state.value.copy(isLoading = false)
                _sideEffect.send(LoginSideEffect.ShowToast(e.message ?: "Login error"))
            }
        }
    }
}

// View - handles side effects
@Composable
fun LoginScreen(
    viewModel: LoginViewModel,
    onNavigateToHome: (Int) -> Unit,
    showToast: (String) -> Unit
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.sideEffect.collect { effect ->
            when (effect) {
                is LoginSideEffect.NavigateToHome ->
                    onNavigateToHome(effect.userId)
                is LoginSideEffect.ShowToast ->
                    showToast(effect.message)
            }
        }
    }

    // UI renders based on state
}
```

❌ **Wrong**: events in State

```kotlin
// Bad - navigation in State

data class LoginState(
    val email: String = "",
    val isLoading: Boolean = false,
    val navigateToHome: Boolean = false  // Won't reset automatically, may retrigger on recreate
)
```

### Reducer Pattern - Pure Functions

```kotlin
// Reducer - pure function: (State, Intent) -> State
object LoginReducer {
    fun reduce(state: LoginState, intent: LoginIntent): LoginState {
        return when (intent) {
            is LoginIntent.EmailChanged -> state.copy(
                email = intent.email,
                emailError = null
            )
            is LoginIntent.LoginStarted -> state.copy(isLoading = true)
            is LoginIntent.LoginSuccess -> state.copy(isLoading = false)
            is LoginIntent.LoginFailed -> state.copy(isLoading = false)
            is LoginIntent.LoginClicked -> state // handle side effect separately
        }
    }
}

// ViewModel uses Reducer
class LoginReducerViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun processIntent(intent: LoginIntent) {
        // ✅ Apply pure function
        _state.value = LoginReducer.reduce(_state.value, intent)

        // Side effects separately
        when (intent) {
            is LoginIntent.LoginClicked -> performLogin()
            else -> Unit
        }
    }

    private fun performLogin() {
        viewModelScope.launch {
            // ... side-effectful login, dispatch LoginStarted/LoginSuccess/LoginFailed
        }
    }
}

// ✅ Easy to test
@Test
fun `reducer is pure function`() {
    val state = LoginState(email = "old@test.com")
    val intent = LoginIntent.EmailChanged("new@test.com")

    val result1 = LoginReducer.reduce(state, intent)
    val result2 = LoginReducer.reduce(state, intent)

    assertEquals(result1, result2)
    assertEquals("old@test.com", state.email)  // Original not mutated
}
```

### Nested States for Complex Screens

```kotlin
// Complex State - decompose into sub-states
data class ProductListState(
    val products: List<Product> = emptyList(),
    val filter: FilterState = FilterState(),
    val pagination: PaginationState = PaginationState(),
    val ui: UIState = UIState()
)

data class FilterState(
    val query: String = "",
    val category: Category? = null,
    val sortBy: SortOption = SortOption.NAME
)

data class PaginationState(
    val currentPage: Int = 0,
    val hasMore: Boolean = true,
    val isLoadingMore: Boolean = false
)

// Intent covers all user actions
sealed class ProductListIntent {
    data class SearchQueryChanged(val query: String) : ProductListIntent()
    data class CategorySelected(val category: Category?) : ProductListIntent()
    object LoadMore : ProductListIntent()
    object Refresh : ProductListIntent()
}
```

### Middleware for Cross-Cutting Concerns

```kotlin
// Middleware handles side effects
interface Middleware<I, S> {
    suspend fun process(intent: I, state: S, dispatch: (I) -> Unit)
}

class AnalyticsMiddleware(
    private val analytics: Analytics
) : Middleware<LoginIntent, LoginState> {
    override suspend fun process(
        intent: LoginIntent,
        state: LoginState,
        dispatch: (LoginIntent) -> Unit
    ) {
        when (intent) {
            is LoginIntent.LoginClicked ->
                analytics.logEvent("login_attempt")
            is LoginIntent.LoginSuccess ->
                analytics.logEvent("login_success")
            else -> Unit
        }
    }
}

class LoginWithMiddlewareViewModel(
    private val middlewares: List<Middleware<LoginIntent, LoginState>>,
    private val reducer: (LoginState, LoginIntent) -> LoginState
) : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun processIntent(intent: LoginIntent) {
        viewModelScope.launch {
            // ✅ Run middleware (side effects)
            middlewares.forEach { it.process(intent, _state.value, ::processIntent) }

            // Apply reducer (pure)
            _state.value = reducer(_state.value, intent)
        }
    }
}
```

### Time Travel Debugging

```kotlin
// Keep history of states for debugging
class DebuggableViewModel<I, S>(
    initialState: S,
    private val reducer: (S, I) -> S
) : ViewModel() {
    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<S> = _state.asStateFlow()

    private val stateHistory = mutableListOf<Pair<I, S>>()

    fun processIntent(intent: I) {
        val newState = reducer(_state.value, intent)
        stateHistory.add(intent to newState)
        _state.value = newState
    }

    // Time travel
    fun replayTo(index: Int) {
        if (index in stateHistory.indices) {
            _state.value = stateHistory[index].second
        }
    }

    fun undo() {
        if (stateHistory.size > 1) {
            stateHistory.removeLast()
            _state.value = stateHistory.last().second
        }
    }
}
```

### Best Practices

✅ **Correct**:
- Single immutable state (data class)
- All actions through `Intent`
- Side effects via `Channel` (BUFFERED)/`SharedFlow`
- Reducer - pure functions
- Use `state.copy()` for state changes

❌ **Wrong**:
- Mutating state: `_state.value.items.add(item)`
- Events in State: `navigateToHome: Boolean`
- Direct method calls instead of Intents (in an MVI setup)
- Multiple independent state sources

---

## Follow-ups

1. How would you structure MVI for a screen that has multiple independent widgets (e.g., search, filters, pagination, and selection) to avoid state explosion?
2. How do you handle long-running jobs and cancellation (e.g., search suggestions) in MVI with coroutines and `Flow`?
3. How would you model error handling and retries in MVI to keep reducers pure and predictable?
4. What are the trade-offs of using a generic MVI framework vs a lightweight, feature-specific implementation?
5. How can you integrate MVI with Jetpack Compose navigation and deep links?

## References

- [[c-android-ui-composition]] - Android UI composition and state
- [[c-android]] - Android platform and components overview
- [[moc-android]] - Android development hub
- https://developer.android.com/topic/architecture

## Related Questions

### Prerequisites (Medium)
- [[q-mvvm-pattern--android--medium]] - MVVM architecture pattern
- [[q-mvp-pattern--android--medium]] - MVP architecture pattern
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - State management tools
- [[q-repository-pattern--android--medium]] - Repository pattern

### Related (Hard)
- [[q-clean-architecture-android--android--hard]] - Clean architecture principles
- [[q-mvi-handle-one-time-events--android--hard]] - One-time events in MVI
- [[q-offline-first-architecture--android--hard]] - Offline-first patterns

### Advanced (Hard)
- [[q-derived-state-snapshot-system--android--hard]] - Derived state systems
- [[q-compose-slot-table-recomposition--android--hard]] - Compose recomposition internals
- [[q-observability-sdk--android--hard]] - Production monitoring

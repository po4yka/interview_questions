---
id: 20251012-12271146
title: "Mvi Architecture / Архитектура MVI"
topic: android
difficulty: hard
status: draft
moc: moc-android
related: [q-app-startup-optimization--performance--medium, q-how-can-data-be-saved-beyond-the-fragment-scope--android--medium, q-how-to-pass-photo-to-editor--android--medium]
created: 2025-10-15
tags: [architecture, mvi, state-management, unidirectional-data-flow, difficulty/hard]
---
# MVI Architecture

**English**: Explain the MVI (Model-View-Intent) architecture pattern. How does it differ from MVVM?

## Answer (EN)
**MVI (Model-View-Intent)** is an architecture pattern with **unidirectional data flow**, where UI state is immutable and changes only through explicit Intents.

**Components**: (1) **Intent** - user actions/events, (2) **Model** - single immutable UI state, (3) **View** - renders UI from Model, (4) **Processor/Reducer** - processes Intent → creates new Model.

**Key principles**: Single source of truth (one State object). Immutability (state.copy()). Unidirectional flow (Intent → Processor → Model → View). Pure functions (reducers). Predictability (same Intent + State = same Result).

**vs MVVM**: MVI has single state vs multiple LiveData/StateFlow. MVI uses Intent-based updates vs direct method calls. MVI has unidirectional vs bi-directional flow. MVI provides better predictability and testability but requires more boilerplate.

**Side effects**: Use Channel/SharedFlow for one-time events (navigation, toasts). State for UI representation, SideEffect for actions.

**Patterns**: Reducer pattern for pure state transformations. Middleware for cross-cutting concerns (logging, analytics). Time travel debugging (state history). Nested states for complex screens.

**Testing**: Easy to test reducers (pure functions). Test state transitions (Intent → new State). Test side effects separately. Verify immutability.

## Ответ (RU)
**MVI (Model-View-Intent)** - архитектурный паттерн с **unidirectional data flow** (однонаправленным потоком данных), где UI состояние иммутабельно и изменяется только через явные намерения (Intents).

### Компоненты MVI

```

  Intent  
      
                  
      
   View      Model   Processor 
      
                                   
      
```

**Компоненты**:
1. **Intent** - намерения пользователя (клик, ввод текста, etc.)
2. **Model** - иммутабельное состояние UI
3. **View** - отрисовывает UI на основе Model
4. **Processor** - обрабатывает Intent → создает новый Model

### Базовый пример MVI

```kotlin
// 1. Model - иммутабельное состояние
data class UserScreenState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

// 2. Intent - действия пользователя
sealed class UserIntent {
    data class LoadUser(val userId: Int) : UserIntent()
    object RetryLoading : UserIntent()
    object ClearError : UserIntent()
}

// 3. ViewModel - обрабатывает Intent
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UserScreenState())
    val state: StateFlow<UserScreenState> = _state.asStateFlow()

    fun processIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUser -> loadUser(intent.userId)
            is UserIntent.RetryLoading -> retry()
            is UserIntent.ClearError -> clearError()
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

    private fun retry() {
        _state.value.user?.let { user ->
            processIntent(UserIntent.LoadUser(user.id))
        }
    }

    private fun clearError() {
        _state.value = _state.value.copy(error = null)
    }
}

// 4. View - отправляет Intent, рендерит State
@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsState()

    // Отправляем Intent при первом compose
    LaunchedEffect(Unit) {
        viewModel.processIntent(UserIntent.LoadUser(userId = 1))
    }

    // Рендерим UI на основе State
    when {
        state.isLoading -> LoadingIndicator()
        state.error != null -> ErrorView(
            message = state.error!!,
            onRetry = { viewModel.processIntent(UserIntent.RetryLoading) },
            onDismiss = { viewModel.processIntent(UserIntent.ClearError) }
        )
        state.user != null -> UserContent(state.user!!)
    }
}
```

### MVI vs MVVM

| Аспект | MVVM | MVI |
|--------|------|-----|
| **State** | Множественные LiveData/StateFlow | Единое иммутабельное состояние |
| **Updates** | Прямые вызовы методов | Intent-based |
| **Data flow** | Bi-directional | Unidirectional (циклический) |
| **Testability** | Хорошая | Отличная (pure functions) |
| **Boilerplate** | Меньше | Больше |
| **Predictability** | Средняя | Высокая |

#### MVVM подход

```kotlin
// MVVM - множественные состояния
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    // Множественные методы
    fun loadUser(id: Int) { ... }
    fun retry() { ... }
    fun clearError() { ... }
}

// View - наблюдает за множественными источниками
viewModel.user.observe(this) { user -> updateUI(user) }
viewModel.isLoading.observe(this) { loading -> showLoading(loading) }
viewModel.error.observe(this) { error -> showError(error) }
```

#### MVI подход

```kotlin
// MVI - единое состояние
class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserScreenState())
    val state: StateFlow<UserScreenState> = _state

    // Единая точка входа
    fun processIntent(intent: UserIntent) { ... }
}

// View - наблюдает за одним источником
viewModel.state.observe(this) { state ->
    // Рендерим весь UI на основе state
    renderState(state)
}
```

### Продвинутый MVI с Side Effects

```kotlin
// State - для UI
data class LoginState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val emailError: String? = null,
    val passwordError: String? = null
)

// Side Effects - одноразовые события
sealed class LoginSideEffect {
    data class NavigateToHome(val userId: Int) : LoginSideEffect()
    data class ShowToast(val message: String) : LoginSideEffect()
    object NavigateToForgotPassword : LoginSideEffect()
}

// Intent
sealed class LoginIntent {
    data class EmailChanged(val email: String) : LoginIntent()
    data class PasswordChanged(val password: String) : LoginIntent()
    object LoginClicked : LoginIntent()
    object ForgotPasswordClicked : LoginIntent()
}

// ViewModel
class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    private val _sideEffect = Channel<LoginSideEffect>()
    val sideEffect = _sideEffect.receiveAsFlow()

    fun processIntent(intent: LoginIntent) {
        when (intent) {
            is LoginIntent.EmailChanged -> {
                _state.value = _state.value.copy(
                    email = intent.email,
                    emailError = null
                )
            }

            is LoginIntent.PasswordChanged -> {
                _state.value = _state.value.copy(
                    password = intent.password,
                    passwordError = null
                )
            }

            is LoginIntent.LoginClicked -> login()

            is LoginIntent.ForgotPasswordClicked -> {
                viewModelScope.launch {
                    _sideEffect.send(LoginSideEffect.NavigateToForgotPassword)
                }
            }
        }
    }

    private fun login() {
        val currentState = _state.value

        // Validation
        if (!isValidEmail(currentState.email)) {
            _state.value = currentState.copy(emailError = "Invalid email")
            return
        }

        if (currentState.password.length < 6) {
            _state.value = currentState.copy(passwordError = "Password too short")
            return
        }

        // Login
        viewModelScope.launch {
            _state.value = currentState.copy(isLoading = true)

            try {
                val user = authRepository.login(
                    currentState.email,
                    currentState.password
                )

                _state.value = currentState.copy(isLoading = false)
                _sideEffect.send(LoginSideEffect.NavigateToHome(user.id))
            } catch (e: Exception) {
                _state.value = currentState.copy(isLoading = false)
                _sideEffect.send(LoginSideEffect.ShowToast(e.message ?: "Login failed"))
            }
        }
    }
}

// View
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = hiltViewModel(),
    onNavigateToHome: (Int) -> Unit
) {
    val state by viewModel.state.collectAsState()

    // Обрабатываем side effects
    LaunchedEffect(Unit) {
        viewModel.sideEffect.collect { effect ->
            when (effect) {
                is LoginSideEffect.NavigateToHome -> onNavigateToHome(effect.userId)
                is LoginSideEffect.ShowToast -> showToast(effect.message)
                is LoginSideEffect.NavigateToForgotPassword -> navigateToForgotPassword()
            }
        }
    }

    Column {
        TextField(
            value = state.email,
            onValueChange = { viewModel.processIntent(LoginIntent.EmailChanged(it)) },
            isError = state.emailError != null,
            supportingText = { state.emailError?.let { Text(it) } }
        )

        TextField(
            value = state.password,
            onValueChange = { viewModel.processIntent(LoginIntent.PasswordChanged(it)) },
            isError = state.passwordError != null,
            supportingText = { state.passwordError?.let { Text(it) } }
        )

        Button(
            onClick = { viewModel.processIntent(LoginIntent.LoginClicked) },
            enabled = !state.isLoading
        ) {
            if (state.isLoading) {
                CircularProgressIndicator()
            } else {
                Text("Login")
            }
        }

        TextButton(
            onClick = { viewModel.processIntent(LoginIntent.ForgotPasswordClicked) }
        ) {
            Text("Forgot password?")
        }
    }
}
```

### Reducer Pattern - чистые функции

```kotlin
// Reducer - pure function: (State, Intent) -> State
object LoginReducer {
    fun reduce(state: LoginState, intent: LoginIntent): LoginState {
        return when (intent) {
            is LoginIntent.EmailChanged -> state.copy(
                email = intent.email,
                emailError = null
            )

            is LoginIntent.PasswordChanged -> state.copy(
                password = intent.password,
                passwordError = null
            )

            is LoginIntent.LoginStarted -> state.copy(
                isLoading = true
            )

            is LoginIntent.LoginSuccess -> state.copy(
                isLoading = false
            )

            is LoginIntent.LoginFailed -> state.copy(
                isLoading = false
            )

            is LoginIntent.ValidationError -> state.copy(
                emailError = intent.emailError,
                passwordError = intent.passwordError
            )
        }
    }
}

// ViewModel использует Reducer
class LoginViewModel : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun processIntent(intent: LoginIntent) {
        // Применяем reducer
        _state.value = LoginReducer.reduce(_state.value, intent)

        // Side effects
        when (intent) {
            is LoginIntent.LoginClicked -> performLogin()
            is LoginIntent.ForgotPasswordClicked -> navigateToForgotPassword()
            else -> {}
        }
    }

    private fun performLogin() {
        viewModelScope.launch {
            try {
                val user = authRepository.login(...)
                processIntent(LoginIntent.LoginSuccess(user))
            } catch (e: Exception) {
                processIntent(LoginIntent.LoginFailed(e.message))
            }
        }
    }
}
```

### Complex State с вложенными состояниями

```kotlin
// Nested states для сложных экранов
data class ProductListState(
    val products: List<Product> = emptyList(),
    val filter: FilterState = FilterState(),
    val pagination: PaginationState = PaginationState(),
    val ui: UIState = UIState()
)

data class FilterState(
    val query: String = "",
    val category: Category? = null,
    val priceRange: IntRange = 0..1000,
    val sortBy: SortOption = SortOption.NAME
)

data class PaginationState(
    val currentPage: Int = 0,
    val hasMore: Boolean = true,
    val isLoadingMore: Boolean = false
)

data class UIState(
    val isInitialLoading: Boolean = false,
    val error: String? = null,
    val selectedProductId: Int? = null
)

// Intent охватывает все действия
sealed class ProductListIntent {
    // Filter intents
    data class SearchQueryChanged(val query: String) : ProductListIntent()
    data class CategorySelected(val category: Category?) : ProductListIntent()
    data class PriceRangeChanged(val range: IntRange) : ProductListIntent()
    data class SortOptionChanged(val option: SortOption) : ProductListIntent()

    // Pagination intents
    object LoadMore : ProductListIntent()
    object Refresh : ProductListIntent()

    // UI intents
    data class ProductClicked(val productId: Int) : ProductListIntent()
    object ClearSelection : ProductListIntent()
    object ClearError : ProductListIntent()
}
```

### MVI с Middleware (для side effects)

```kotlin
// Middleware обрабатывает side effects
interface Middleware<I, S> {
    suspend fun process(intent: I, state: S, dispatch: (I) -> Unit)
}

class LoggingMiddleware<I, S> : Middleware<I, S> {
    override suspend fun process(intent: I, state: S, dispatch: (I) -> Unit) {
        println("Intent: $intent")
        println("State before: $state")
    }
}

class AnalyticsMiddleware : Middleware<LoginIntent, LoginState> {
    override suspend fun process(
        intent: LoginIntent,
        state: LoginState,
        dispatch: (LoginIntent) -> Unit
    ) {
        when (intent) {
            is LoginIntent.LoginClicked -> {
                analytics.logEvent("login_attempt")
            }
            is LoginIntent.LoginSuccess -> {
                analytics.logEvent("login_success")
            }
            is LoginIntent.LoginFailed -> {
                analytics.logEvent("login_failure")
            }
            else -> {}
        }
    }
}

// ViewModel с middleware
class LoginViewModel(
    private val authRepository: AuthRepository,
    private val middlewares: List<Middleware<LoginIntent, LoginState>>
) : ViewModel() {

    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun processIntent(intent: LoginIntent) {
        viewModelScope.launch {
            // Выполняем middleware
            middlewares.forEach { middleware ->
                middleware.process(intent, _state.value, ::processIntent)
            }

            // Применяем reducer
            _state.value = LoginReducer.reduce(_state.value, intent)
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

        // Сохраняем в историю
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

    fun getHistory(): List<Pair<I, S>> = stateHistory.toList()
}
```

### Testing MVI

```kotlin
class LoginViewModelTest {
    private lateinit var viewModel: LoginViewModel
    private lateinit var fakeRepository: FakeAuthRepository

    @Before
    fun setup() {
        fakeRepository = FakeAuthRepository()
        viewModel = LoginViewModel(fakeRepository)
    }

    @Test
    fun `email changed updates state`() = runTest {
        // Given
        val email = "test@example.com"

        // When
        viewModel.processIntent(LoginIntent.EmailChanged(email))

        // Then
        assertEquals(email, viewModel.state.value.email)
        assertNull(viewModel.state.value.emailError)
    }

    @Test
    fun `login success navigates to home`() = runTest {
        // Given
        val email = "valid@example.com"
        val password = "password123"
        val expectedUser = User(1, "Test User")
        fakeRepository.setLoginResult(Result.success(expectedUser))

        // When
        viewModel.processIntent(LoginIntent.EmailChanged(email))
        viewModel.processIntent(LoginIntent.PasswordChanged(password))
        viewModel.processIntent(LoginIntent.LoginClicked)

        // Then
        val effects = mutableListOf<LoginSideEffect>()
        viewModel.sideEffect.take(1).toList(effects)

        assertEquals(
            LoginSideEffect.NavigateToHome(expectedUser.id),
            effects.first()
        )
    }

    @Test
    fun `login failure shows error`() = runTest {
        // Given
        val errorMessage = "Invalid credentials"
        fakeRepository.setLoginResult(Result.failure(Exception(errorMessage)))

        // When
        viewModel.processIntent(LoginIntent.EmailChanged("test@example.com"))
        viewModel.processIntent(LoginIntent.PasswordChanged("wrong"))
        viewModel.processIntent(LoginIntent.LoginClicked)

        advanceUntilIdle()

        // Then
        val effects = mutableListOf<LoginSideEffect>()
        viewModel.sideEffect.take(1).toList(effects)

        assertTrue(effects.first() is LoginSideEffect.ShowToast)
    }

    @Test
    fun `reducer is pure function`() {
        // Given
        val state = LoginState(email = "old@example.com")
        val intent = LoginIntent.EmailChanged("new@example.com")

        // When
        val newState1 = LoginReducer.reduce(state, intent)
        val newState2 = LoginReducer.reduce(state, intent)

        // Then - всегда одинаковый результат
        assertEquals(newState1, newState2)
        assertEquals("old@example.com", state.email) // Original не изменился
    }
}
```

### Best Practices

```kotlin
// - 1. Единое иммутабельное состояние
data class ScreenState(
    val data: List<Item>,
    val isLoading: Boolean,
    val error: String?
)

// - 2. Все action через Intent
sealed class ScreenIntent {
    object Load : ScreenIntent()
    data class ItemClicked(val id: Int) : ScreenIntent()
}

// - 3. Side effects через Channel
private val _sideEffect = Channel<SideEffect>()
val sideEffect = _sideEffect.receiveAsFlow()

// - 4. Используйте data class copy
_state.value = _state.value.copy(isLoading = true)

// - 5. Reducer - чистые функции
fun reduce(state: State, intent: Intent): State = when (intent) {
    // Pure transformation
}

// - НЕ мутируйте state
_state.value.items.add(item) // - Мутация!
_state.value = _state.value.copy(
    items = _state.value.items + item
) // - Новый объект
```


---

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Hard)
- [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture
- [[q-kmm-architecture--android--hard]] - KMM architecture patterns


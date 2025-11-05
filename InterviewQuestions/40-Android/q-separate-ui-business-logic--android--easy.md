---
id: android-288
title: Separate UI and Business Logic / Разделение UI и бизнес-логики
aliases:
- Separate UI and Business Logic
- Разделение UI и бизнес-логики
topic: android
subtopics:
- architecture-mvvm
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-how-to-draw-ui-without-xml--android--easy
- q-proguard-r8--android--medium
- q-v-chyom-raznitsa-mezhdu-fragmentmanager-i-fragmenttransaction--programming-languages--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/architecture-mvvm
- difficulty/easy
date created: Saturday, November 1st 2025, 12:47:03 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)
> Разделение UI и бизнес-логики

# Question (EN)
> Separate UI and Business Logic

---

## Answer (EN)
Separating presentation (UI) and business logic is a fundamental principle of software architecture. This separation improves code quality, testability, maintainability, and team collaboration.

### Why Separate UI and Business Logic?

#### 1. Testability

**Without Separation:**
```kotlin
// Bad: Business logic mixed with UI
class LoginActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        loginButton.setOnClickListener {
            val email = emailEditText.text.toString()
            val password = passwordEditText.text.toString()

            // Business logic in Activity
            if (email.isEmpty() || !email.contains("@")) {
                Toast.makeText(this, "Invalid email", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (password.length < 6) {
                Toast.makeText(this, "Password too short", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Network call in UI
            lifecycleScope.launch {
                try {
                    val response = api.login(email, password)
                    if (response.isSuccessful) {
                        startActivity(Intent(this@LoginActivity, MainActivity::class.java))
                    } else {
                        Toast.makeText(this@LoginActivity, "Login failed", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    Toast.makeText(this@LoginActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}

// Cannot test without Activity!
```

**With Separation:**
```kotlin
// Good: Business logic in ViewModel
class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState: StateFlow<LoginState> = _loginState

    fun login(email: String, password: String) {
        // Validation logic (testable)
        val emailError = validateEmail(email)
        if (emailError != null) {
            _loginState.value = LoginState.Error(emailError)
            return
        }

        val passwordError = validatePassword(password)
        if (passwordError != null) {
            _loginState.value = LoginState.Error(passwordError)
            return
        }

        // Business logic (testable)
        viewModelScope.launch {
            _loginState.value = LoginState.Loading

            val result = authRepository.login(email, password)
            _loginState.value = when {
                result.isSuccess -> LoginState.Success
                else -> LoginState.Error(result.exceptionOrNull()?.message ?: "Login failed")
            }
        }
    }

    private fun validateEmail(email: String): String? {
        return when {
            email.isEmpty() -> "Email cannot be empty"
            !email.contains("@") -> "Invalid email format"
            else -> null
        }
    }

    private fun validatePassword(password: String): String? {
        return when {
            password.isEmpty() -> "Password cannot be empty"
            password.length < 6 -> "Password must be at least 6 characters"
            else -> null
        }
    }
}

sealed class LoginState {
    object Idle : LoginState()
    object Loading : LoginState()
    object Success : LoginState()
    data class Error(val message: String) : LoginState()
}

// Activity only handles UI
class LoginActivity : AppCompatActivity() {
    private val viewModel: LoginViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        loginButton.setOnClickListener {
            val email = emailEditText.text.toString()
            val password = passwordEditText.text.toString()
            viewModel.login(email, password)
        }

        lifecycleScope.launch {
            viewModel.loginState.collect { state ->
                when (state) {
                    is LoginState.Idle -> {
                        progressBar.isVisible = false
                    }
                    is LoginState.Loading -> {
                        progressBar.isVisible = true
                        loginButton.isEnabled = false
                    }
                    is LoginState.Success -> {
                        progressBar.isVisible = false
                        startActivity(Intent(this@LoginActivity, MainActivity::class.java))
                        finish()
                    }
                    is LoginState.Error -> {
                        progressBar.isVisible = false
                        loginButton.isEnabled = true
                        Toast.makeText(this@LoginActivity, state.message, Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
    }
}

// Now we can test without Activity!
class LoginViewModelTest {
    @Test
    fun `login with invalid email shows error`() = runTest {
        val viewModel = LoginViewModel(FakeAuthRepository())

        viewModel.login("invalid-email", "password123")

        val state = viewModel.loginState.value
        assertTrue(state is LoginState.Error)
        assertEquals("Invalid email format", (state as LoginState.Error).message)
    }

    @Test
    fun `login with short password shows error`() = runTest {
        val viewModel = LoginViewModel(FakeAuthRepository())

        viewModel.login("test@example.com", "12345")

        val state = viewModel.loginState.value
        assertTrue(state is LoginState.Error)
        assertEquals("Password must be at least 6 characters", (state as LoginState.Error).message)
    }
}
```

#### 2. Reusability

```kotlin
// Bad: Logic tied to specific UI
class UserListActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val users = api.getUsers()
            recyclerView.adapter = UserAdapter(users)
        }
    }
}

// Cannot reuse in Fragment or Compose!

// Good: Logic separated
class UserListViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            val result = userRepository.getUsers()
            if (result.isSuccess) {
                _users.value = result.getOrDefault(emptyList())
            }
        }
    }
}

// Can use in Activity
class UserListActivity : AppCompatActivity() {
    private val viewModel: UserListViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            viewModel.users.collect { users ->
                adapter.submitList(users)
            }
        }
        viewModel.loadUsers()
    }
}

// Can use in Fragment
class UserListFragment : Fragment() {
    private val viewModel: UserListViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            viewModel.users.collect { users ->
                adapter.submitList(users)
            }
        }
        viewModel.loadUsers()
    }
}

// Can use in Compose
@Composable
fun UserListScreen(viewModel: UserListViewModel = viewModel()) {
    val users by viewModel.users.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadUsers()
    }

    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

#### 3. Maintainability

```kotlin
// Bad: Hard to maintain
class ProductActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        loadButton.setOnClickListener {
            lifecycleScope.launch {
                progressBar.isVisible = true

                try {
                    val products = api.getProducts()
                    val filtered = products.filter { it.price < 100 }
                    val sorted = filtered.sortedBy { it.name }

                    if (sorted.isEmpty()) {
                        emptyView.isVisible = true
                        recyclerView.isVisible = false
                    } else {
                        emptyView.isVisible = false
                        recyclerView.isVisible = true
                        adapter.submitList(sorted)
                    }

                    // Save to cache
                    sharedPrefs.edit {
                        putString("last_products", Json.encodeToString(sorted))
                    }
                } catch (e: Exception) {
                    Toast.makeText(this@ProductActivity, e.message, Toast.LENGTH_SHORT).show()
                } finally {
                    progressBar.isVisible = false
                }
            }
        }
    }
}

// What if we need to change filtering? UI changes too!
// What if we need different UI for tablet? Duplicate logic!

// Good: Easy to maintain
class ProductViewModel(
    private val productRepository: ProductRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ProductUiState>(ProductUiState.Idle)
    val uiState: StateFlow<ProductUiState> = _uiState

    fun loadProducts(maxPrice: Double = 100.0) {
        viewModelScope.launch {
            _uiState.value = ProductUiState.Loading

            val result = productRepository.getProducts()

            _uiState.value = when {
                result.isSuccess -> {
                    val products = result.getOrThrow()
                    val filtered = filterProducts(products, maxPrice)
                    val sorted = sortProducts(filtered)

                    if (sorted.isEmpty()) {
                        ProductUiState.Empty
                    } else {
                        ProductUiState.Success(sorted)
                    }
                }
                else -> ProductUiState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }

    private fun filterProducts(products: List<Product>, maxPrice: Double): List<Product> {
        return products.filter { it.price < maxPrice }
    }

    private fun sortProducts(products: List<Product>): List<Product> {
        return products.sortedBy { it.name }
    }
}

sealed class ProductUiState {
    object Idle : ProductUiState()
    object Loading : ProductUiState()
    object Empty : ProductUiState()
    data class Success(val products: List<Product>) : ProductUiState()
    data class Error(val message: String) : ProductUiState()
}

// UI just renders state
class ProductActivity : AppCompatActivity() {
    private val viewModel: ProductViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        loadButton.setOnClickListener {
            viewModel.loadProducts()
        }

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                renderState(state)
            }
        }
    }

    private fun renderState(state: ProductUiState) {
        when (state) {
            is ProductUiState.Idle -> {
                progressBar.isVisible = false
            }
            is ProductUiState.Loading -> {
                progressBar.isVisible = true
                emptyView.isVisible = false
                recyclerView.isVisible = false
            }
            is ProductUiState.Empty -> {
                progressBar.isVisible = false
                emptyView.isVisible = true
                recyclerView.isVisible = false
            }
            is ProductUiState.Success -> {
                progressBar.isVisible = false
                emptyView.isVisible = false
                recyclerView.isVisible = true
                adapter.submitList(state.products)
            }
            is ProductUiState.Error -> {
                progressBar.isVisible = false
                Toast.makeText(this, state.message, Toast.LENGTH_SHORT).show()
            }
        }
    }
}

// Now changing filtering logic doesn't touch UI!
// Can create different UI for tablet without duplicating logic!
```

#### 4. Team Collaboration

```kotlin
// With separation, teams can work independently:

// Backend team works on:
interface UserRepository {
    suspend fun getUsers(): Result<List<User>>
    suspend fun updateUser(user: User): Result<Unit>
}

// Business logic team works on:
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    // Business logic here
}

// UI/UX team works on:
class UserActivity : AppCompatActivity() {
    private val viewModel: UserListViewModel by viewModels()
    // UI rendering here
}

// Teams don't block each other!
```

#### 5. Configuration Changes

```kotlin
// Bad: Lose data on rotation
class CounterActivity : AppCompatActivity() {
    private var counter = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        incrementButton.setOnClickListener {
            counter++
            counterText.text = counter.toString()
        }
    }

    // Rotate device -> counter resets to 0!
}

// Good: Data survives rotation
class CounterViewModel : ViewModel() {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter

    fun increment() {
        _counter.value++
    }
}

class CounterActivity : AppCompatActivity() {
    private val viewModel: CounterViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        incrementButton.setOnClickListener {
            viewModel.increment()
        }

        lifecycleScope.launch {
            viewModel.counter.collect { count ->
                counterText.text = count.toString()
            }
        }
    }

    // Rotate device -> counter value preserved!
}
```

### Common Architecture Patterns

#### MVVM (Model-View-ViewModel)

```kotlin
// Model
data class User(val id: String, val name: String)

interface UserRepository {
    suspend fun getUsers(): List<User>
}

// ViewModel (Business Logic)
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }
}

// View (UI)
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.users.collect { users ->
                // Update UI
            }
        }

        viewModel.loadUsers()
    }
}
```

#### MVI (Model-View-Intent)

```kotlin
// State
data class UserUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// Intent (User Actions)
sealed class UserIntent {
    object LoadUsers : UserIntent()
    data class SelectUser(val userId: String) : UserIntent()
}

// ViewModel
class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserUiState())
    val state: StateFlow<UserUiState> = _state

    fun processIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUsers -> loadUsers()
            is UserIntent.SelectUser -> selectUser(intent.userId)
        }
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)
            // Load users...
            _state.value = _state.value.copy(isLoading = false, users = users)
        }
    }
}

// View
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.state.collect { state ->
                // Render state
            }
        }

        loadButton.setOnClickListener {
            viewModel.processIntent(UserIntent.LoadUsers)
        }
    }
}
```

### Benefits Summary

| Benefit | Without Separation | With Separation |
|---------|-------------------|-----------------|
| **Testing** | Need UI framework | Pure unit tests |
| **Reusability** | Duplicate logic | Reuse in Activity/Fragment/Compose |
| **Maintainability** | Change UI = change logic | Independent changes |
| **Configuration changes** | Lose state | State preserved |
| **Team collaboration** | Blocking dependencies | Parallel work |
| **Code clarity** | Mixed concerns | Single responsibility |

## Ответ (RU)
Разделение отображения (UI) и бизнес-логики - это фундаментальный принцип архитектуры программного обеспечения. Это разделение улучшает качество кода, тестируемость, поддерживаемость и командную работу.

### Зачем Разделять UI И Бизнес-логику?

#### 1. Тестируемость

Без разделения невозможно протестировать логику без создания Activity или Fragment. С разделением можно писать чистые unit-тесты для ViewModel.

```kotlin
// Тест ViewModel без UI
@Test
fun `login with invalid email shows error`() = runTest {
    val viewModel = LoginViewModel(FakeAuthRepository())
    viewModel.login("invalid-email", "password123")

    val state = viewModel.loginState.value
    assertTrue(state is LoginState.Error)
}
```

#### 2. Переиспользуемость

Логика в ViewModel может использоваться в Activity, Fragment и Compose без дублирования.

```kotlin
// Одна ViewModel для разных UI
class UserListViewModel(repository: UserRepository) : ViewModel() {
    // Логика загрузки пользователей
}

// Используется в Activity
class UserListActivity : AppCompatActivity() {
    private val viewModel: UserListViewModel by viewModels()
}

// Используется в Fragment
class UserListFragment : Fragment() {
    private val viewModel: UserListViewModel by viewModels()
}

// Используется в Compose
@Composable
fun UserListScreen(viewModel: UserListViewModel = viewModel())
```

#### 3. Поддерживаемость

Изменения в логике не требуют изменений в UI и наоборот.

#### 4. Командная Работа

Разные команды могут работать параллельно: Backend-команда над Repository, команда бизнес-логики над ViewModel, UI/UX команда над Activity/Compose.

#### 5. Сохранение Состояния

ViewModel переживает изменения конфигурации (поворот экрана), сохраняя состояние приложения.

### Популярные Паттерны

**MVVM** - Model-View-ViewModel
**MVI** - Model-View-Intent
**MVP** - Model-View-Presenter

### Резюме Преимуществ

- Тестируемость: чистые unit-тесты без UI
- Переиспользуемость: одна логика для Activity/Fragment/Compose
- Поддерживаемость: независимые изменения UI и логики
- Сохранение состояния: данные переживают поворот экрана
- Командная работа: параллельная работа команд
- Чистота кода: принцип единственной ответственности


---


## Follow-ups

- [[q-how-to-draw-ui-without-xml--android--easy]]
- [[q-proguard-r8--android--medium]]
- [[q-v-chyom-raznitsa-mezhdu-fragmentmanager-i-fragmenttransaction--programming-languages--medium]]


## References

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Related (Easy)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Advanced (Harder)
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui
- [[q-build-optimization-gradle--android--medium]] - Ui

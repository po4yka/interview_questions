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
- c-android
- c-android-ui-composition
- q-how-to-draw-ui-without-xml--android--easy
- q-proguard-r8--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/architecture-mvvm
- difficulty/easy

---

# Вопрос (RU)
> Разделение UI и бизнес-логики

# Question (EN)
> Separate UI and Business Logic

---

## Ответ (RU)
Разделение отображения (UI) и бизнес-логики — это фундаментальный принцип архитектуры программного обеспечения. Это разделение улучшает качество кода, тестируемость, поддерживаемость, возможность масштабирования и командную работу.

### Зачем разделять UI и бизнес-логику?

#### 1. Тестируемость

Без разделения логика оказывается внутри `Activity`/`Fragment`/Compose-функций, сильно завязана на Android-фреймворк и события UI — такие классы сложно и дорого тестировать.

Ниже пример «плохого» подхода, когда бизнес-логика смешана с UI (аналог EN-версии):

```kotlin
// Плохо: бизнес-логика внутри Activity
class LoginActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        loginButton.setOnClickListener {
            val email = emailEditText.text.toString()
            val password = passwordEditText.text.toString()

            // Валидация и бизнес-логика прямо в UI
            if (email.isEmpty() || !email.contains("@")) {
                Toast.makeText(this, "Invalid email", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (password.length < 6) {
                Toast.makeText(this, "Password too short", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Сетевой вызов в UI-слое
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

// Такой код тяжело тестировать без запуска Activity и Android-фреймворка.
```

Правильный подход — вынести бизнес-логику и валидацию в `ViewModel`, чтобы её можно было тестировать как обычный Kotlin-код.

```kotlin
// Хорошо: бизнес-логика во ViewModel
class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState: StateFlow<LoginState> = _loginState

    fun login(email: String, password: String) {
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

        viewModelScope.launch {
            _loginState.value = LoginState.Loading

            val result = authRepository.login(email, password)
            _loginState.value = when {
                result.isSuccess -> LoginState.Success
                else -> LoginState.Error(result.exceptionOrNull()?.message ?: "Login failed")
            }
        }
    }

    private fun validateEmail(email: String): String? = when {
        email.isEmpty() -> "Email cannot be empty"
        !email.contains("@") -> "Invalid email format"
        else -> null
    }

    private fun validatePassword(password: String): String? = when {
        password.isEmpty() -> "Password cannot be empty"
        password.length < 6 -> "Password must be at least 6 characters"
        else -> null
    }
}

sealed class LoginState {
    object Idle : LoginState()
    object Loading : LoginState()
    object Success : LoginState()
    data class Error(val message: String) : LoginState()
}

// Activity отвечает только за отображение и пользовательский ввод
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
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.loginState.collect { state ->
                    when (state) {
                        is LoginState.Idle -> {
                            progressBar.isVisible = false
                            loginButton.isEnabled = true
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
}

// Теперь ViewModel легко тестировать unit-тестами без UI.
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

#### 2. Переиспользуемость

При смешении логики с UI её невозможно использовать повторно в других экранах или реализациях.

```kotlin
// Плохо: логика привязана к конкретной Activity
class UserListActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val users = api.getUsers()
            recyclerView.adapter = UserAdapter(users)
        }
    }
}

// Такой код нельзя переиспользовать во Fragment или Compose без дублирования.
```

Правильный подход — вынести загрузку данных в `ViewModel`/репозиторий и использовать один и тот же источник данных в разных UI.

```kotlin
// Хорошо: логика отдельно
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

// Activity
class UserListActivity : AppCompatActivity() {
    private val viewModel: UserListViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    adapter.submitList(users)
                }
            }
        }

        viewModel.loadUsers()
    }
}

// Fragment
class UserListFragment : Fragment() {
    private val viewModel: UserListViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    adapter.submitList(users)
                }
            }
        }

        viewModel.loadUsers()
    }
}

// Compose
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

#### 3. Поддерживаемость

Смешение загрузки данных, фильтрации, кеширования и логики отображения в одном классе делает код хрупким.

```kotlin
// Плохо: сложно сопровождать
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
```

Лучше вынести бизнес-логику в `ViewModel`, а UI оставить только для рендера состояния.

```kotlin
// Хорошо: бизнес-логика в одном месте
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

    private fun filterProducts(products: List<Product>, maxPrice: Double): List<Product> =
        products.filter { it.price < maxPrice }

    private fun sortProducts(products: List<Product>): List<Product> =
        products.sortedBy { it.name }
}

sealed class ProductUiState {
    object Idle : ProductUiState()
    object Loading : ProductUiState()
    object Empty : ProductUiState()
    data class Success(val products: List<Product>) : ProductUiState()
    data class Error(val message: String) : ProductUiState()
}

// UI только отображает состояние
class ProductActivity : AppCompatActivity() {
    private val viewModel: ProductViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        loadButton.setOnClickListener {
            viewModel.loadProducts()
        }

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    renderState(state)
                }
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
```

#### 4. Командная работа

При разделении слоёв команды могут работать параллельно, не блокируя друг друга:

```kotlin
// Backend/инфраструктура:
interface UserRepository {
    suspend fun getUsers(): Result<List<User>>
    suspend fun updateUser(user: User): Result<Unit>
}

// Команда бизнес-логики:
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    // Бизнес-логика здесь
}

// UI/UX команда:
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
    // Только рендеринг UI
}
```

#### 5. Сохранение состояния и конфигурационные изменения

Если состояние хранится в `Activity`/`Fragment`, при повороте экрана оно теряется.

```kotlin
// Плохо: состояние не переживает поворот
class CounterActivity : AppCompatActivity() {
    private var counter = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        incrementButton.setOnClickListener {
            counter++
            counterText.text = counter.toString()
        }
    }
}
```

Используя `ViewModel`, мы выносим состояние из UI-класса, и оно переживает изменение конфигурации (в пределах жизненного цикла владельца).

```kotlin
// Хорошо: состояние в ViewModel
class CounterViewModel : ViewModel() {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter

    fun increment() {
        _counter.value++
    }
}

class CounterActivity2 : AppCompatActivity() {
    private val viewModel: CounterViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        incrementButton.setOnClickListener {
            viewModel.increment()
        }

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.counter.collect { count ->
                    counterText.text = count.toString()
                }
            }
        }
    }
}
```

### Популярные архитектурные паттерны

#### MVVM (Model-`View`-`ViewModel`)

```kotlin
// Model
data class User(val id: String, val name: String)

interface UserRepository {
    suspend fun getUsers(): List<User>
}

// ViewModel (бизнес-логика)
class UserListViewModel2(
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
class UserActivity2 : AppCompatActivity() {
    private val viewModel: UserListViewModel2 by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    // Обновляем UI на основе состояния
                }
            }
        }

        viewModel.loadUsers()
    }
}
```

#### MVI (Model-`View`-`Intent`)

```kotlin
// State
data class UserUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// Intent (действия пользователя)
sealed class UserIntent {
    object LoadUsers : UserIntent()
    data class SelectUser(val userId: String) : UserIntent()
}

// ViewModel
class UserMviViewModel(
    private val repository: UserRepository
) : ViewModel() {
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
            _state.value = _state.value.copy(isLoading = true, error = null)
            try {
                val users = repository.getUsers()
                _state.value = _state.value.copy(isLoading = false, users = users)
            } catch (e: Exception) {
                _state.value = _state.value.copy(isLoading = false, error = e.message)
            }
        }
    }

    private fun selectUser(userId: String) {
        // Обработка выбора пользователя
    }
}

// View
class UserMviActivity : AppCompatActivity() {
    private val viewModel: UserMviViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.state.collect { state ->
                    // Рендерим UI на основе состояния
                }
            }
        }

        loadButton.setOnClickListener {
            viewModel.processIntent(UserIntent.LoadUsers)
        }
    }
}
```

### Резюме преимуществ

| Преимущество | Без разделения | С разделением |
|-------------|----------------|---------------|
| Тестирование | Нужен UI/фреймворк для проверки логики | Чистые unit-тесты для `ViewModel`/доменного слоя |
| Переиспользуемость | Дублирование логики в разных экранах | Одна логика для `Activity`/`Fragment`/Compose |
| Поддерживаемость | Любое изменение UI трогает логику | UI и логика меняются независимо |
| Конфигурационные изменения | Потеря состояния при повороте | Состояние хранится во `ViewModel`/компонентах |
| Командная работа | Сильная связность, блокировки | Параллельная работа разных команд |
| Чистота кода | Смешение ответственностей | Принцип единственной ответственности |

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

// Cannot easily test without Activity and Android framework!
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
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.loginState.collect { state ->
                    when (state) {
                        is LoginState.Idle -> {
                            progressBar.isVisible = false
                            loginButton.isEnabled = true
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
}

// Now we can unit test ViewModel without Activity or UI framework.
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
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    adapter.submitList(users)
                }
            }
        }

        viewModel.loadUsers()
    }
}

// Can use in Fragment
class UserListFragment : Fragment() {
    private val viewModel: UserListViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    adapter.submitList(users)
                }
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
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    renderState(state)
                }
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
    private val viewModel: UserViewModel by viewModels()
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

// Good: Data survives rotation when using ViewModel
class CounterViewModel : ViewModel() {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter

    fun increment() {
        _counter.value++
    }
}

class CounterActivity2 : AppCompatActivity() {
    private val viewModel: CounterViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        incrementButton.setOnClickListener {
            viewModel.increment()
        }

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.counter.collect { count ->
                    counterText.text = count.toString()
                }
            }
        }
    }

    // Rotate device -> counter value preserved for this Activity instance scope as long as ViewModel is provided correctly.
}
```

### Common Architecture Patterns

#### MVVM (Model-`View`-`ViewModel`)

```kotlin
// Model
data class User(val id: String, val name: String)

interface UserRepository {
    suspend fun getUsers(): List<User>
}

// ViewModel (Business Logic)
class UserListViewModel2(
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
class UserActivity2 : AppCompatActivity() {
    private val viewModel: UserListViewModel2 by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.users.collect { users ->
                    // Update UI
                }
            }
        }

        viewModel.loadUsers()
    }
}
```

#### MVI (Model-`View`-`Intent`)

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
class UserMviViewModel(
    private val repository: UserRepository
) : ViewModel() {
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
            _state.value = _state.value.copy(isLoading = true, error = null)
            try {
                val users = repository.getUsers()
                _state.value = _state.value.copy(isLoading = false, users = users)
            } catch (e: Exception) {
                _state.value = _state.value.copy(isLoading = false, error = e.message)
            }
        }
    }

    private fun selectUser(userId: String) {
        // handle selection; for brevity, omitted
    }
}

// View
class UserMviActivity : AppCompatActivity() {
    private val viewModel: UserMviViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.state.collect { state ->
                    // Render state
                }
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
| **Reusability** | Duplicate logic | Reuse in `Activity`/`Fragment`/Compose |
| **Maintainability** | Change UI = change logic | Independent changes |
| **Configuration changes** | Lose state | State preserved via `ViewModel`/architecture components |
| **Team collaboration** | Blocking dependencies | Parallel work |
| **Code clarity** | Mixed concerns | Single responsibility |

---

## Follow-ups

- [[q-how-to-draw-ui-without-xml--android--easy]]
- [[q-proguard-r8--android--medium]]
- How would you structure dependencies between `ViewModel`, repository, and data sources to avoid tight coupling?
- How does separating UI and business logic help when migrating from XML views to Jetpack Compose?
- What are trade-offs between MVVM and MVI in terms of separating concerns on Android?

## References

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

### Prerequisites / Concepts

- [[c-android]]
- [[c-android-ui-composition]]

### Related (Easy)
- [[q-android-app-components--android--easy]]
- [[q-android-jetpack-overview--android--easy]]

### Advanced (Harder)
- [[q-android-build-optimization--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

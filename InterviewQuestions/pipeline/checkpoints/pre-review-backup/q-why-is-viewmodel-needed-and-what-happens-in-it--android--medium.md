---
id: 20251012-122711195
title: "Why Is Viewmodel Needed And What Happens In It / Why Is Viewmodel Needed и What Happens In It"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-workmanager-decision-guide--android--medium, q-kapt-ksp-migration--gradle--medium, q-does-state-made-in-compose-help-avoid-race-condition--android--medium]
created: 2025-10-15
tags: [viewmodel, lifecycle, mvvm, architecture, difficulty/medium]
---
# Why is ViewModel needed and what happens in it?

## EN (expanded)

### Why ViewModel is Needed

**ViewModel** is an Android Architecture Component that stores and manages UI-related data in a lifecycle-aware way. It solves several critical problems in Android development.

### Problems ViewModel Solves

#### 1. Configuration Change Survival

Without ViewModel, data is lost on screen rotation.

```kotlin
// - BAD: Data lost on rotation
class MainActivity : AppCompatActivity() {
    private var counter = 0  // Lost on rotation!

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        button.setOnClickListener {
            counter++
            textView.text = "Count: $counter"
        }
    }
}

// - GOOD: ViewModel survives rotation
class MainActivity : AppCompatActivity() {
    private val viewModel: CounterViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.count.observe(this) { count ->
            textView.text = "Count: $count"
        }

        button.setOnClickListener {
            viewModel.increment()
        }
    }
}

class CounterViewModel : ViewModel() {
    private val _count = MutableLiveData(0)
    val count: LiveData<Int> = _count

    fun increment() {
        _count.value = (_count.value ?: 0) + 1
    }
}
```

#### 2. Separation of Concerns

ViewModel separates UI logic from business logic.

```kotlin
// - BAD: Everything in Activity
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Business logic mixed with UI
        button.setOnClickListener {
            lifecycleScope.launch {
                try {
                    val response = api.getUser(userId)
                    nameText.text = response.name
                    emailText.text = response.email
                } catch (e: Exception) {
                    Toast.makeText(this@UserActivity, "Error", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}

// - GOOD: Business logic in ViewModel
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.user.observe(this) { user ->
            nameText.text = user.name
            emailText.text = user.email
        }

        viewModel.error.observe(this) { errorMessage ->
            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show()
        }

        button.setOnClickListener {
            viewModel.loadUser(userId)
        }
    }
}

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            try {
                val result = repository.getUser(userId)
                _user.value = result
            } catch (e: Exception) {
                _error.value = "Failed to load user"
            }
        }
    }
}
```

#### 3. Lifecycle Management

ViewModel handles lifecycle automatically with `viewModelScope`.

```kotlin
class UserViewModel : ViewModel() {

    // Automatically cancelled when ViewModel is cleared
    fun loadData() {
        viewModelScope.launch {
            // Coroutine automatically cancelled on ViewModel destruction
            val data = repository.fetchData()
            _data.value = data
        }
    }

    // Called when ViewModel is no longer needed
    override fun onCleared() {
        super.onCleared()
        // Clean up resources
        database.close()
    }
}
```

### What Happens in ViewModel

#### 1. State Management

```kotlin
class SearchViewModel : ViewModel() {
    // Private mutable state
    private val _searchResults = MutableLiveData<List<Product>>()
    // Public immutable state
    val searchResults: LiveData<List<Product>> = _searchResults

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun search(query: String) {
        _loading.value = true
        _error.value = null

        viewModelScope.launch {
            try {
                val results = repository.search(query)
                _searchResults.value = results
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _loading.value = false
            }
        }
    }
}
```

#### 2. Business Logic

```kotlin
class ShoppingCartViewModel : ViewModel() {
    private val _cartItems = MutableLiveData<List<CartItem>>()
    val cartItems: LiveData<List<CartItem>> = _cartItems

    // Derived state
    val totalPrice: LiveData<Double> = _cartItems.map { items ->
        items.sumOf { it.price * it.quantity }
    }

    val itemCount: LiveData<Int> = _cartItems.map { it.size }

    fun addItem(product: Product) {
        val currentItems = _cartItems.value.orEmpty().toMutableList()
        val existingItem = currentItems.find { it.productId == product.id }

        if (existingItem != null) {
            existingItem.quantity++
        } else {
            currentItems.add(CartItem(product.id, product.name, product.price, 1))
        }

        _cartItems.value = currentItems
    }

    fun removeItem(itemId: Int) {
        val currentItems = _cartItems.value.orEmpty().toMutableList()
        currentItems.removeIf { it.productId == itemId }
        _cartItems.value = currentItems
    }
}
```

#### 3. Data Loading

```kotlin
class PostsViewModel(
    private val repository: PostRepository
) : ViewModel() {

    private val _posts = MutableLiveData<List<Post>>()
    val posts: LiveData<List<Post>> = _posts

    init {
        // Load data when ViewModel is created
        loadPosts()
    }

    private fun loadPosts() {
        viewModelScope.launch {
            _posts.value = repository.getPosts()
        }
    }

    fun refresh() {
        viewModelScope.launch {
            val freshPosts = repository.refreshPosts()
            _posts.value = freshPosts
        }
    }
}
```

#### 4. User Interactions

```kotlin
class LoginViewModel : ViewModel() {
    private val _loginState = MutableLiveData<LoginState>()
    val loginState: LiveData<LoginState> = _loginState

    fun login(email: String, password: String) {
        // Validation
        if (email.isEmpty() || !email.contains("@")) {
            _loginState.value = LoginState.Error("Invalid email")
            return
        }

        if (password.length < 6) {
            _loginState.value = LoginState.Error("Password too short")
            return
        }

        // Network request
        _loginState.value = LoginState.Loading
        viewModelScope.launch {
            try {
                val token = repository.login(email, password)
                _loginState.value = LoginState.Success(token)
            } catch (e: Exception) {
                _loginState.value = LoginState.Error("Login failed")
            }
        }
    }
}

sealed class LoginState {
    object Loading : LoginState()
    data class Success(val token: String) : LoginState()
    data class Error(val message: String) : LoginState()
}
```

### ViewModel Lifecycle

```
Activity/Fragment Created
         ↓
    ViewModel Created
         ↓
    Configuration Change (rotation)
         ↓
    Activity Destroyed
         ↓
    Activity Re-created
         ↓
    Same ViewModel Instance Reused
         ↓
    Activity Finished
         ↓
    ViewModel.onCleared() Called
         ↓
    ViewModel Destroyed
```

### ViewModel with StateFlow (Modern Approach)

```kotlin
class ModernViewModel : ViewModel() {
    // StateFlow instead of LiveData
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val data = repository.fetchData()
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}

// In Activity/Fragment
class MyActivity : AppCompatActivity() {
    private val viewModel: ModernViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showData(state.data)
                    is UiState.Error -> showError(state.message)
                }
            }
        }
    }
}
```

### Sharing ViewModel Between Fragments

```kotlin
// Shared ViewModel scoped to Activity
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment A
class ListFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    private fun onItemClick(item: Item) {
        sharedViewModel.selectItem(item)
        // Navigate to detail fragment
    }
}

// Fragment B
class DetailFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            displayItem(item)
        }
    }
}
```

### ViewModel with Repository Pattern

```kotlin
// Repository
class UserRepository(
    private val api: ApiService,
    private val database: UserDao
) {
    suspend fun getUser(userId: Int): User {
        return try {
            // Try network first
            val user = api.getUser(userId)
            database.insert(user)
            user
        } catch (e: Exception) {
            // Fallback to cache
            database.getUser(userId)
        }
    }
}

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _user.value = repository.getUser(userId)
        }
    }
}

// ViewModelFactory for dependency injection
class UserViewModelFactory(
    private val repository: UserRepository
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(UserViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return UserViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

// Usage in Activity
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels {
        UserViewModelFactory(
            UserRepository(ApiClient.api, AppDatabase.userDao)
        )
    }
}
```

### Best Practices

1. **Never pass Context to ViewModel** (use AndroidViewModel if needed)
2. **Never reference Views** from ViewModel
3. **Use LiveData or StateFlow** to expose data
4. **Keep UI logic in UI layer**, business logic in ViewModel
5. **Use viewModelScope** for coroutines
6. **Make state immutable** (expose LiveData, not MutableLiveData)

### Summary

**Why ViewModel is needed:**
- Survives configuration changes (rotation)
- Separates UI from business logic
- Manages lifecycle automatically
- Enables data sharing between fragments

**What happens in ViewModel:**
- State management (LiveData, StateFlow)
- Business logic execution
- Data loading from repositories
- User interaction handling
- Background task management

---

## RU (original)

### Зачем нужен ViewModel

**ViewModel** - это компонент Android Architecture Component, который хранит и управляет данными, связанными с UI, с учетом жизненного цикла. Он решает несколько критических проблем в Android-разработке.

### Проблемы, которые решает ViewModel

#### 1. Переживание изменений конфигурации

Без ViewModel данные теряются при повороте экрана.

```kotlin
// - ПЛОХО: Данные теряются при повороте
class MainActivity : AppCompatActivity() {
    private var counter = 0  // Теряется при повороте!

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        button.setOnClickListener {
            counter++
            textView.text = "Count: $counter"
        }
    }
}

// - ХОРОШО: ViewModel переживает поворот
class MainActivity : AppCompatActivity() {
    private val viewModel: CounterViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.count.observe(this) { count ->
            textView.text = "Count: $count"
        }

        button.setOnClickListener {
            viewModel.increment()
        }
    }
}

class CounterViewModel : ViewModel() {
    private val _count = MutableLiveData(0)
    val count: LiveData<Int> = _count

    fun increment() {
        _count.value = (_count.value ?: 0) + 1
    }
}
```

#### 2. Разделение ответственности

ViewModel отделяет логику UI от бизнес-логики.

```kotlin
// - ПЛОХО: Все в Activity
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Бизнес-логика смешана с UI
        button.setOnClickListener {
            lifecycleScope.launch {
                try {
                    val response = api.getUser(userId)
                    nameText.text = response.name
                    emailText.text = response.email
                } catch (e: Exception) {
                    Toast.makeText(this@UserActivity, "Error", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}

// - ХОРОШО: Бизнес-логика в ViewModel
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.user.observe(this) { user ->
            nameText.text = user.name
            emailText.text = user.email
        }

        viewModel.error.observe(this) { errorMessage ->
            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show()
        }

        button.setOnClickListener {
            viewModel.loadUser(userId)
        }
    }
}

class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            try {
                val result = repository.getUser(userId)
                _user.value = result
            } catch (e: Exception) {
                _error.value = "Failed to load user"
            }
        }
    }
}
```

#### 3. Управление жизненным циклом

ViewModel автоматически управляет жизненным циклом через `viewModelScope`.

```kotlin
class UserViewModel : ViewModel() {

    // Автоматически отменяется при очистке ViewModel
    fun loadData() {
        viewModelScope.launch {
            // Корутина автоматически отменяется при уничтожении ViewModel
            val data = repository.fetchData()
            _data.value = data
        }
    }

    // Вызывается когда ViewModel больше не нужна
    override fun onCleared() {
        super.onCleared()
        // Очистка ресурсов
        database.close()
    }
}
```

### Что происходит в ViewModel

#### 1. Управление состоянием

```kotlin
class SearchViewModel : ViewModel() {
    // Приватное изменяемое состояние
    private val _searchResults = MutableLiveData<List<Product>>()
    // Публичное неизменяемое состояние
    val searchResults: LiveData<List<Product>> = _searchResults

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun search(query: String) {
        _loading.value = true
        _error.value = null

        viewModelScope.launch {
            try {
                val results = repository.search(query)
                _searchResults.value = results
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _loading.value = false
            }
        }
    }
}
```

#### 2. Бизнес-логика

```kotlin
class ShoppingCartViewModel : ViewModel() {
    private val _cartItems = MutableLiveData<List<CartItem>>()
    val cartItems: LiveData<List<CartItem>> = _cartItems

    // Производное состояние
    val totalPrice: LiveData<Double> = _cartItems.map { items ->
        items.sumOf { it.price * it.quantity }
    }

    val itemCount: LiveData<Int> = _cartItems.map { it.size }

    fun addItem(product: Product) {
        val currentItems = _cartItems.value.orEmpty().toMutableList()
        val existingItem = currentItems.find { it.productId == product.id }

        if (existingItem != null) {
            existingItem.quantity++
        } else {
            currentItems.add(CartItem(product.id, product.name, product.price, 1))
        }

        _cartItems.value = currentItems
    }

    fun removeItem(itemId: Int) {
        val currentItems = _cartItems.value.orEmpty().toMutableList()
        currentItems.removeIf { it.productId == itemId }
        _cartItems.value = currentItems
    }
}
```

#### 3. Загрузка данных

```kotlin
class PostsViewModel(
    private val repository: PostRepository
) : ViewModel() {

    private val _posts = MutableLiveData<List<Post>>()
    val posts: LiveData<List<Post>> = _posts

    init {
        // Загрузка данных при создании ViewModel
        loadPosts()
    }

    private fun loadPosts() {
        viewModelScope.launch {
            _posts.value = repository.getPosts()
        }
    }

    fun refresh() {
        viewModelScope.launch {
            val freshPosts = repository.refreshPosts()
            _posts.value = freshPosts
        }
    }
}
```

#### 4. Обработка взаимодействий пользователя

```kotlin
class LoginViewModel : ViewModel() {
    private val _loginState = MutableLiveData<LoginState>()
    val loginState: LiveData<LoginState> = _loginState

    fun login(email: String, password: String) {
        // Валидация
        if (email.isEmpty() || !email.contains("@")) {
            _loginState.value = LoginState.Error("Invalid email")
            return
        }

        if (password.length < 6) {
            _loginState.value = LoginState.Error("Password too short")
            return
        }

        // Сетевой запрос
        _loginState.value = LoginState.Loading
        viewModelScope.launch {
            try {
                val token = repository.login(email, password)
                _loginState.value = LoginState.Success(token)
            } catch (e: Exception) {
                _loginState.value = LoginState.Error("Login failed")
            }
        }
    }
}

sealed class LoginState {
    object Loading : LoginState()
    data class Success(val token: String) : LoginState()
    data class Error(val message: String) : LoginState()
}
```

### Жизненный цикл ViewModel

```
Activity/Fragment создан
         ↓
    ViewModel создана
         ↓
    Изменение конфигурации (поворот)
         ↓
    Activity уничтожена
         ↓
    Activity пересоздана
         ↓
    Тот же экземпляр ViewModel переиспользуется
         ↓
    Activity завершена
         ↓
    ViewModel.onCleared() вызван
         ↓
    ViewModel уничтожена
```

### ViewModel с StateFlow (современный подход)

```kotlin
class ModernViewModel : ViewModel() {
    // StateFlow вместо LiveData
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val data = repository.fetchData()
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}

// В Activity/Fragment
class MyActivity : AppCompatActivity() {
    private val viewModel: ModernViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showData(state.data)
                    is UiState.Error -> showError(state.message)
                }
            }
        }
    }
}
```

### Совместное использование ViewModel между Fragment

```kotlin
// Общая ViewModel с областью видимости Activity
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment A
class ListFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    private fun onItemClick(item: Item) {
        sharedViewModel.selectItem(item)
        // Переход к фрагменту деталей
    }
}

// Fragment B
class DetailFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            displayItem(item)
        }
    }
}
```

### ViewModel с паттерном Repository

```kotlin
// Repository
class UserRepository(
    private val api: ApiService,
    private val database: UserDao
) {
    suspend fun getUser(userId: Int): User {
        return try {
            // Сначала пробуем сеть
            val user = api.getUser(userId)
            database.insert(user)
            user
        } catch (e: Exception) {
            // Откат к кешу
            database.getUser(userId)
        }
    }
}

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _user.value = repository.getUser(userId)
        }
    }
}

// ViewModelFactory для внедрения зависимостей
class UserViewModelFactory(
    private val repository: UserRepository
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(UserViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return UserViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

// Использование в Activity
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels {
        UserViewModelFactory(
            UserRepository(ApiClient.api, AppDatabase.userDao)
        )
    }
}
```

### Лучшие практики

1. **Никогда не передавайте Context в ViewModel** (используйте AndroidViewModel при необходимости)
2. **Никогда не ссылайтесь на View** из ViewModel
3. **Используйте LiveData или StateFlow** для предоставления данных
4. **Держите UI-логику в UI-слое**, бизнес-логику в ViewModel
5. **Используйте viewModelScope** для корутин
6. **Делайте состояние неизменяемым** (предоставляйте LiveData, а не MutableLiveData)

### Резюме

**Зачем нужен ViewModel:**
- Переживает изменения конфигурации (поворот экрана)
- Отделяет UI от бизнес-логики
- Автоматически управляет жизненным циклом
- Позволяет делиться данными между фрагментами

**Что происходит в ViewModel:**
- Управление состоянием (LiveData, StateFlow)
- Выполнение бизнес-логики
- Загрузка данных из репозиториев
- Обработка взаимодействий пользователя
- Управление фоновыми задачами


---

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Medium)
- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
- [[q-what-is-viewmodel--android--medium]] - What is ViewModel
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - ViewModel state preservation
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - ViewModel vs onSavedInstanceState

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture


---
id: 202510031417010
title: "Why is ViewModel needed and what happens in it"
question_ru: "Зачем нужна view модель и что в ней обычно происходит"
question_en: "Зачем нужна view модель и что в ней обычно происходит"
topic: android
moc: moc-android
status: draft
difficulty: medium
tags:
  - viewmodel
  - mvvm
  - android/activity
  - android/fragments
  - android/viewmodel
  - lifecycle
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/204
---

# Why is ViewModel needed and what happens in it

## English Answer

**ViewModel** is an architecture component designed to store and manage UI-related data in accordance with the Model-View-ViewModel (MVVM) architectural pattern. It's intended to facilitate data management during configuration changes (such as screen rotations) and provide data to the user interface in a more convenient and optimized form.

### Main Functions of ViewModel

#### 1. Separation of Concerns
Separates responsibilities between data model and user interface (View), helping to divide business logic from UI management logic.

```kotlin
// ❌ BAD - Business logic in Activity
class BadActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Business logic mixed with UI
        val users = database.getUsers()
        val filteredUsers = users.filter { it.age > 18 }
        recyclerView.adapter = UserAdapter(filteredUsers)
    }
}

// ✅ GOOD - Business logic in ViewModel
class GoodActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Only UI setup
        viewModel.users.observe(this) { users ->
            recyclerView.adapter = UserAdapter(users)
        }
    }
}

class UserViewModel : ViewModel() {
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    init {
        loadUsers()
    }

    private fun loadUsers() {
        // Business logic in ViewModel
        viewModelScope.launch {
            val allUsers = repository.getUsers()
            _users.value = allUsers.filter { it.age > 18 }
        }
    }
}
```

#### 2. Lifecycle Management
ViewModel is lifecycle-aware, allowing it to preserve data state during configuration changes.

```kotlin
class MainActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // When device rotates:
        // 1. Activity is destroyed
        // 2. Activity is recreated
        // 3. ViewModel SURVIVES - same instance!
        // 4. Data is still available

        Log.d("Lifecycle", "ViewModel hashCode: ${viewModel.hashCode()}")
        // Same hashCode after rotation!
    }
}
```

#### 3. Improved Resource Management
Manages resources more efficiently by loading data asynchronously and keeping it ready for quick display.

```kotlin
class ProductViewModel(
    private val repository: ProductRepository
) : ViewModel() {

    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    fun loadProducts() {
        if (_products.value != null) {
            // Data already loaded, no need to reload
            return
        }

        viewModelScope.launch {
            _isLoading.value = true
            try {
                val data = repository.getProducts()
                _products.value = data
            } catch (e: Exception) {
                // Handle error
            } finally {
                _isLoading.value = false
            }
        }
    }
}
```

### What Usually Happens in ViewModel

#### 1. Data Loading from Repositories or Network

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val userList = userRepository.getUsers()
                _users.value = userList
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
}
```

#### 2. Data Transformation for Display

```kotlin
class ProductViewModel : ViewModel() {

    private val _rawProducts = MutableLiveData<List<Product>>()

    // Transform data for UI
    val displayProducts: LiveData<List<ProductUI>> = _rawProducts.map { products ->
        products.map { product ->
            ProductUI(
                id = product.id,
                displayName = product.name.uppercase(),
                formattedPrice = "$${product.price}",
                isAvailable = product.stock > 0
            )
        }
    }

    // Filter data
    val availableProducts: LiveData<List<Product>> = _rawProducts.map { products ->
        products.filter { it.stock > 0 }
    }
}
```

#### 3. Managing Data Stream Subscriptions

```kotlin
class RealtimeViewModel(
    private val dataSource: RealtimeDataSource
) : ViewModel() {

    private val _realtimeData = MutableLiveData<Data>()
    val realtimeData: LiveData<Data> = _realtimeData

    init {
        // Subscribe to data stream
        viewModelScope.launch {
            dataSource.dataFlow.collect { data ->
                _realtimeData.value = data
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        // Subscription automatically cancelled when ViewModel is cleared
    }
}
```

#### 4. Handling User Actions

```kotlin
class TodoViewModel(
    private val repository: TodoRepository
) : ViewModel() {

    private val _todos = MutableLiveData<List<Todo>>()
    val todos: LiveData<List<Todo>> = _todos

    fun addTodo(title: String) {
        viewModelScope.launch {
            val newTodo = Todo(title = title, completed = false)
            repository.insertTodo(newTodo)
            loadTodos()
        }
    }

    fun toggleTodo(id: Int) {
        viewModelScope.launch {
            repository.toggleTodo(id)
            loadTodos()
        }
    }

    fun deleteTodo(id: Int) {
        viewModelScope.launch {
            repository.deleteTodo(id)
            loadTodos()
        }
    }

    private fun loadTodos() {
        viewModelScope.launch {
            _todos.value = repository.getAllTodos()
        }
    }
}
```

### Complete ViewModel Example

```kotlin
class UserProfileViewModel(
    private val userRepository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // State management
    private val _user = MutableLiveData<User?>()
    val user: LiveData<User?> = _user

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    // Get userId from savedStateHandle (survives process death)
    private val userId: String? = savedStateHandle["user_id"]

    init {
        userId?.let { loadUser(it) }
    }

    fun loadUser(id: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            try {
                val userData = userRepository.getUser(id)
                _user.value = userData
                savedStateHandle["user_id"] = id
            } catch (e: Exception) {
                _error.value = "Failed to load user: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun updateUser(name: String, email: String) {
        val currentUser = _user.value ?: return

        viewModelScope.launch {
            _isLoading.value = true

            try {
                val updatedUser = currentUser.copy(
                    name = name,
                    email = email
                )
                userRepository.updateUser(updatedUser)
                _user.value = updatedUser
            } catch (e: Exception) {
                _error.value = "Failed to update user: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun clearError() {
        _error.value = null
    }

    override fun onCleared() {
        super.onCleared()
        // Cleanup if needed (viewModelScope is cancelled automatically)
        Log.d("ViewModel", "ViewModel cleared")
    }
}
```

### Using ViewModel in Activity/Fragment

```kotlin
class UserProfileActivity : AppCompatActivity() {

    // Create ViewModel with factory for dependencies
    private val viewModel: UserProfileViewModel by viewModels {
        UserProfileViewModelFactory(
            userRepository = (application as MyApp).userRepository
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user_profile)

        // Observe user data
        viewModel.user.observe(this) { user ->
            user?.let { displayUser(it) }
        }

        // Observe loading state
        viewModel.isLoading.observe(this) { isLoading ->
            progressBar.isVisible = isLoading
        }

        // Observe errors
        viewModel.error.observe(this) { error ->
            error?.let {
                showError(it)
                viewModel.clearError()
            }
        }

        // Handle user actions
        saveButton.setOnClickListener {
            val name = nameEditText.text.toString()
            val email = emailEditText.text.toString()
            viewModel.updateUser(name, email)
        }

        // Load user if needed
        val userId = intent.getStringExtra("user_id")
        userId?.let { viewModel.loadUser(it) }
    }

    private fun displayUser(user: User) {
        nameEditText.setText(user.name)
        emailEditText.setText(user.email)
    }

    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
```

### ViewModel Lifecycle

```
Activity Created
    ↓
ViewModel Created (first time)
    ↓
Activity Running
    ↓
Configuration Change (rotation)
    ↓
Activity Destroyed
    ↓
Activity Recreated
    ↓
ViewModel STILL ALIVE (same instance)
    ↓
Activity Finished (back pressed)
    ↓
ViewModel.onCleared() called
    ↓
ViewModel Destroyed
```

### ViewModel vs SavedStateHandle

```kotlin
class StateViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Regular LiveData - lost on process death
    private val _tempData = MutableLiveData<String>()
    val tempData: LiveData<String> = _tempData

    // SavedStateHandle - survives process death
    val persistentData: MutableLiveData<String> = savedStateHandle.getLiveData("key")

    fun updateTemp(value: String) {
        _tempData.value = value
        // Lost if process is killed
    }

    fun updatePersistent(value: String) {
        persistentData.value = value
        // Survives process death (stored in Bundle)
    }
}
```

### Best Practices

1. **Never hold references to Views, Activities, or Fragments** - causes memory leaks
2. **Use viewModelScope** for coroutines - automatically cancelled
3. **Expose immutable LiveData** - use private MutableLiveData, public LiveData
4. **Use SavedStateHandle** for data that should survive process death
5. **Keep ViewModels focused** - one ViewModel per screen/feature

## Russian Answer

**ViewModel** — это компонент архитектуры приложений, предназначенный для хранения и управления данными, связанными с пользовательским интерфейсом, в соответствии с принципами архитектурного паттерна Model-View-ViewModel (MVVM). Предназначена для того, чтобы облегчить управление данными при конфигурационных изменениях (таких как повороты экрана) и предоставить данные пользовательскому интерфейсу в более удобной и оптимизированной форме.

### Основные функции

1. **Разделение ответственности** между моделью данных и пользовательским интерфейсом (View), что помогает разделить бизнес-логику и логику управления пользовательским интерфейсом

2. **Управление жизненным циклом** - ViewModel осведомлена о жизненном цикле Activity или Fragment, что позволяет ей сохранять состояние данных при изменениях конфигурации

3. **Улучшенное управление ресурсами** - помогает управлять ресурсами более эффективно, загружая данные асинхронно и поддерживая их готовность для быстрого отображения

### Что обычно происходит в ViewModel

- **Загрузка данных** из репозиториев или сетевых источников
- **Преобразование данных** в формат, подходящий для отображения в UI
- **Управление подписками** на потоки данных (Flow, LiveData)
- **Обработка пользовательских действий**, инициированных в интерфейсе

### Пример

```java
public class MyViewModel extends ViewModel {
    private MutableLiveData<List<User>> users = new MutableLiveData<>();

    public LiveData<List<User>> getUsers() {
        if (users.getValue() == null) {
            loadUsers();
        }
        return users;
    }

    private void loadUsers() {
        userRepository.getUsers(new DataLoadCallback() {
            @Override
            public void onDataLoaded(List<User> usersData) {
                users.setValue(usersData);
            }
        });
    }
}
```

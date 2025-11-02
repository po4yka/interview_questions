---
id: android-316
title: "Why Is ViewModel Needed And What Happens In It / Зачем нужен ViewModel и что в нем происходит"
aliases: [ViewModel Purpose, ViewModel Responsibilities, Назначение ViewModel, Обязанности ViewModel]

# Classification
topic: android
subtopics: [architecture-mvvm, lifecycle, ui-state]
question_kind: android
difficulty: medium

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-android
related: [q-how-to-save-activity-state--android--medium, q-mvvm-pattern--android--medium, q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium, q-viewmodel-vs-onsavedinstancestate--android--medium]

# Timestamps
created: 2025-10-15
updated: 2025-10-30

# Tags
tags: [android/architecture-mvvm, android/lifecycle, android/ui-state, difficulty/medium, jetpack, mvvm, viewmodel]
date created: Saturday, November 1st 2025, 12:47:11 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)

> Зачем нужен ViewModel и что в нем происходит?

# Question (EN)

> Why is ViewModel needed and what happens in it?

---

## Ответ (RU)

**ViewModel** - это Android Architecture Component, который хранит UI-состояние и бизнес-логику отдельно от Activity/Fragment, переживая изменения конфигурации (поворот экрана).

### Зачем Нужен ViewModel

#### 1. Переживание Изменений Конфигурации

```kotlin
// ❌ БЕЗ ViewModel - данные теряются при повороте
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

// ✅ С ViewModel - данные сохраняются
class MainActivity : AppCompatActivity() {
    private val viewModel: CounterViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.count.observe(this) { count ->
            textView.text = "Count: $count"
        }
        button.setOnClickListener { viewModel.increment() }
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

#### 2. Разделение Ответственности (Separation of Concerns)

```kotlin
// ❌ БЕЗ ViewModel - бизнес-логика смешана с UI
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        button.setOnClickListener {
            lifecycleScope.launch {
                try {
                    val user = api.getUser(userId)
                    nameText.text = user.name
                } catch (e: Exception) {
                    Toast.makeText(this@UserActivity, "Error", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}

// ✅ С ViewModel - бизнес-логика отдельно
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.user.observe(this) { user -> nameText.text = user.name }
        viewModel.error.observe(this) { msg -> Toast.makeText(this, msg, Toast.LENGTH_SHORT).show() }
        button.setOnClickListener { viewModel.loadUser(userId) }
    }
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            try {
                _user.value = repository.getUser(userId)
            } catch (e: Exception) {
                _error.value = "Failed to load user"
            }
        }
    }
}
```

#### 3. Автоматическое Управление Жизненным Циклом

```kotlin
class UserViewModel : ViewModel() {
    // viewModelScope автоматически отменяет корутины при onCleared()
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
            _data.value = data
        }
    }

    override fun onCleared() {
        super.onCleared()
        // Очистка ресурсов
        database.close()
    }
}
```

### Что Происходит В ViewModel

#### 1. Управление UI-состоянием

```kotlin
class SearchViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun search(query: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val results = repository.search(query)
                _uiState.value = UiState.Success(results)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed interface UiState {
    object Loading : UiState
    data class Success(val data: List<Product>) : UiState
    data class Error(val message: String) : UiState
}
```

#### 2. Бизнес-логика И Валидация

```kotlin
class LoginViewModel : ViewModel() {
    private val _loginState = MutableLiveData<LoginState>()
    val loginState: LiveData<LoginState> = _loginState

    fun login(email: String, password: String) {
        if (email.isEmpty() || !email.contains("@")) {
            _loginState.value = LoginState.Error("Invalid email")
            return
        }
        if (password.length < 6) {
            _loginState.value = LoginState.Error("Password too short")
            return
        }

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
```

#### 3. Работа С Репозиториями И Данными

```kotlin
class PostsViewModel(private val repository: PostRepository) : ViewModel() {
    private val _posts = MutableLiveData<List<Post>>()
    val posts: LiveData<List<Post>> = _posts

    init {
        loadPosts()
    }

    private fun loadPosts() {
        viewModelScope.launch {
            _posts.value = repository.getPosts()
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _posts.value = repository.refreshPosts()
        }
    }
}
```

#### 4. Совместное Использование Между Fragment

```kotlin
// Shared ViewModel с областью видимости Activity
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

### Жизненный Цикл ViewModel

```
Activity/Fragment создан
         ↓
    ViewModel создана
         ↓
    Изменение конфигурации (поворот)
         ↓
    Activity уничтожена → Activity пересоздана
         ↓
    ViewModel переиспользуется (тот же экземпляр)
         ↓
    Activity завершена (finish())
         ↓
    ViewModel.onCleared() → ViewModel уничтожена
```

### Best Practices

✅ **DO**:
- Используйте `viewModelScope` для корутин
- Предоставляйте immutable состояние (`LiveData`/`StateFlow`, не `Mutable*`)
- Держите UI-логику в UI-слое, бизнес-логику в ViewModel
- Используйте Repository Pattern для разделения источников данных

❌ **DON'T**:
- Не передавайте Context в ViewModel (используйте `AndroidViewModel` если нужен Application Context)
- Не ссылайтесь на View напрямую
- Не держите Activity/Fragment ссылки (memory leak)
- Не выполняйте UI-операции в ViewModel

---

## Answer (EN)

**ViewModel** is an Android Architecture Component that stores UI state and business logic separately from Activity/Fragment, surviving configuration changes (screen rotation).

### Why ViewModel is Needed

#### 1. Configuration Change Survival

```kotlin
// ❌ WITHOUT ViewModel - data lost on rotation
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

// ✅ WITH ViewModel - data preserved
class MainActivity : AppCompatActivity() {
    private val viewModel: CounterViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.count.observe(this) { count ->
            textView.text = "Count: $count"
        }
        button.setOnClickListener { viewModel.increment() }
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

```kotlin
// ❌ WITHOUT ViewModel - business logic mixed with UI
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        button.setOnClickListener {
            lifecycleScope.launch {
                try {
                    val user = api.getUser(userId)
                    nameText.text = user.name
                } catch (e: Exception) {
                    Toast.makeText(this@UserActivity, "Error", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}

// ✅ WITH ViewModel - business logic separated
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.user.observe(this) { user -> nameText.text = user.name }
        viewModel.error.observe(this) { msg -> Toast.makeText(this, msg, Toast.LENGTH_SHORT).show() }
        button.setOnClickListener { viewModel.loadUser(userId) }
    }
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            try {
                _user.value = repository.getUser(userId)
            } catch (e: Exception) {
                _error.value = "Failed to load user"
            }
        }
    }
}
```

#### 3. Automatic Lifecycle Management

```kotlin
class UserViewModel : ViewModel() {
    // viewModelScope automatically cancels coroutines on onCleared()
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
            _data.value = data
        }
    }

    override fun onCleared() {
        super.onCleared()
        // Clean up resources
        database.close()
    }
}
```

### What Happens in ViewModel

#### 1. UI State Management

```kotlin
class SearchViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun search(query: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val results = repository.search(query)
                _uiState.value = UiState.Success(results)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed interface UiState {
    object Loading : UiState
    data class Success(val data: List<Product>) : UiState
    data class Error(val message: String) : UiState
}
```

#### 2. Business Logic and Validation

```kotlin
class LoginViewModel : ViewModel() {
    private val _loginState = MutableLiveData<LoginState>()
    val loginState: LiveData<LoginState> = _loginState

    fun login(email: String, password: String) {
        if (email.isEmpty() || !email.contains("@")) {
            _loginState.value = LoginState.Error("Invalid email")
            return
        }
        if (password.length < 6) {
            _loginState.value = LoginState.Error("Password too short")
            return
        }

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
```

#### 3. Repository Integration and Data Loading

```kotlin
class PostsViewModel(private val repository: PostRepository) : ViewModel() {
    private val _posts = MutableLiveData<List<Post>>()
    val posts: LiveData<List<Post>> = _posts

    init {
        loadPosts()
    }

    private fun loadPosts() {
        viewModelScope.launch {
            _posts.value = repository.getPosts()
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _posts.value = repository.refreshPosts()
        }
    }
}
```

#### 4. Sharing Between Fragments

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

### ViewModel Lifecycle

```
Activity/Fragment Created
         ↓
    ViewModel Created
         ↓
    Configuration Change (rotation)
         ↓
    Activity Destroyed → Activity Re-created
         ↓
    ViewModel Reused (same instance)
         ↓
    Activity Finished (finish())
         ↓
    ViewModel.onCleared() → ViewModel Destroyed
```

### Best Practices

✅ **DO**:
- Use `viewModelScope` for coroutines
- Expose immutable state (`LiveData`/`StateFlow`, not `Mutable*`)
- Keep UI logic in UI layer, business logic in ViewModel
- Use Repository Pattern to separate data sources

❌ **DON'T**:
- Don't pass Context to ViewModel (use `AndroidViewModel` if you need Application Context)
- Don't reference Views directly
- Don't hold Activity/Fragment references (memory leak)
- Don't perform UI operations in ViewModel

---

## Follow-ups

1. **What's the difference between ViewModel and onSaveInstanceState?** ViewModel survives configuration changes but not process death; onSaveInstanceState survives process death but has size limitations (1MB).

2. **How does ViewModel survive configuration changes internally?** ViewModelStore is retained in non-configuration instance via `onRetainNonConfigurationInstance()`, keyed by Activity/Fragment.

3. **When should you use AndroidViewModel vs ViewModel?** Use AndroidViewModel only when you need Application Context (e.g., for resources, ContentResolver). Never pass Activity Context.

4. **How to handle one-time events in ViewModel (e.g., navigation)?** Use SingleLiveEvent, Event wrapper, or SharedFlow with replay=0 to prevent re-emission on configuration changes.

5. **Can ViewModel survive process death?** No. Use SavedStateHandle for data that must survive process death (combined with ViewModel for configuration changes).

## References

- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-how-to-save-activity-state--android--medium]] - State preservation strategies
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - ViewModel state preservation limits
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - Comparison of state preservation techniques
- https://developer.android.com/topic/libraries/architecture/viewmodel

## Related Questions

### Prerequisites (Easier)
- [[q-main-android-components--android--easy]] - Android components overview
- [[q-why-separate-ui-and-business-logic--android--easy]] - Separation of concerns

### Related (Same Level)
- [[q-mvvm-pattern--android--medium]] - MVVM architecture pattern
- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
- [[q-how-to-save-activity-state--android--medium]] - Activity state preservation
- [[q-how-does-activity-lifecycle-work--android--medium]] - Activity lifecycle

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-offline-first-architecture--android--hard]] - Offline-first with ViewModel
- [[q-modularization-patterns--android--hard]] - ViewModels in modular architecture

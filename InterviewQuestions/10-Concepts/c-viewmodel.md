---
id: "20251025-120300"
title: "ViewModel / ViewModel"
aliases: ["ViewModel", "Android ViewModel", "AAC ViewModel", "ViewModel компонент"]
summary: "Lifecycle-aware component that stores and manages UI-related data, surviving configuration changes like screen rotations"
topic: "android"
subtopics: ["viewmodel", "lifecycle", "architecture-components"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["concept", "android", "viewmodel", "lifecycle", "architecture-components", "jetpack", "mvvm", "difficulty/medium"]
---

# ViewModel / ViewModel

## Summary (EN)

ViewModel is an Android Architecture Component designed to store and manage UI-related data in a lifecycle-conscious way. ViewModels survive configuration changes such as screen rotations, allowing data to persist across Activity or Fragment recreation. They provide a clear separation between UI logic and business logic, making code more testable and maintainable. ViewModels should never hold references to Views, Activities, or Fragments to prevent memory leaks.

## Краткое описание (RU)

ViewModel - это компонент Android Architecture Component, предназначенный для хранения и управления данными, связанными с UI, с учетом жизненного цикла. ViewModel переживает изменения конфигурации, такие как поворот экрана, позволяя данным сохраняться при пересоздании Activity или Fragment. Они обеспечивают четкое разделение между UI-логикой и бизнес-логикой, делая код более тестируемым и поддерживаемым. ViewModel никогда не должны содержать ссылки на View, Activity или Fragment, чтобы предотвратить утечки памяти.

## Key Points (EN)

- Survives configuration changes (screen rotation, language change, etc.)
- Scoped to the lifecycle of Activity or Fragment
- Automatically cleared when associated lifecycle is destroyed
- Should never reference View, Activity, Fragment, or Context
- Works seamlessly with LiveData, StateFlow, and other observables
- Enables separation of concerns in MVVM architecture
- Can be shared between multiple Fragments within the same Activity

## Ключевые моменты (RU)

- Переживает изменения конфигурации (поворот экрана, смена языка и т.д.)
- Привязан к жизненному циклу Activity или Fragment
- Автоматически очищается при уничтожении связанного lifecycle
- Никогда не должен ссылаться на View, Activity, Fragment или Context
- Бесшовно работает с LiveData, StateFlow и другими observable
- Обеспечивает разделение ответственности в MVVM архитектуре
- Может быть разделен между несколькими Fragment в одной Activity

## Basic ViewModel Implementation

```kotlin
class UserViewModel : ViewModel() {
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    fun loadUsers() {
        _isLoading.value = true
        viewModelScope.launch {
            try {
                val result = repository.getUsers()
                _users.value = result
            } catch (e: Exception) {
                // Handle error
            } finally {
                _isLoading.value = false
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        // Cleanup resources
    }
}
```

## Using ViewModel in Activity/Fragment

```kotlin
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)

        // Observe LiveData
        viewModel.users.observe(this) { users ->
            updateUI(users)
        }

        viewModel.isLoading.observe(this) { isLoading ->
            showLoading(isLoading)
        }

        // Trigger data loading
        viewModel.loadUsers()
    }
}
```

## ViewModel with StateFlow (Modern Approach)

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading
            try {
                val users = repository.getUsers()
                _uiState.value = UserUiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UserUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class UserUiState {
    object Loading : UserUiState()
    data class Success(val users: List<User>) : UserUiState()
    data class Error(val message: String) : UserUiState()
}
```

## ViewModel with Dependency Injection

```kotlin
// Using Hilt
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val analytics: AnalyticsService
) : ViewModel() {
    // ViewModel implementation
}

// In Activity/Fragment
@AndroidEntryPoint
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
}
```

## ViewModel Factory (Manual Dependency Injection)

```kotlin
class UserViewModel(
    private val userId: String,
    private val repository: UserRepository
) : ViewModel() {
    // ViewModel implementation
}

class UserViewModelFactory(
    private val userId: String,
    private val repository: UserRepository
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(UserViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return UserViewModel(userId, repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

// Usage
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels {
        UserViewModelFactory(userId, repository)
    }
}
```

## Shared ViewModel Between Fragments

```kotlin
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment 1
class ListFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    private fun onItemClick(item: Item) {
        sharedViewModel.selectItem(item)
    }
}

// Fragment 2
class DetailFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        sharedViewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            displayDetails(item)
        }
    }
}
```

## SavedStateHandle for Process Death

```kotlin
class UserViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: UserRepository
) : ViewModel() {

    // Survives process death
    var searchQuery: String
        get() = savedStateHandle.get<String>("search_query") ?: ""
        set(value) {
            savedStateHandle.set("search_query", value)
        }

    val users: LiveData<List<User>> = savedStateHandle.getLiveData<String>("search_query")
        .switchMap { query ->
            repository.searchUsers(query)
        }

    fun updateSearchQuery(query: String) {
        searchQuery = query
    }
}
```

## ViewModel Lifecycle

```
Activity/Fragment Created
          ↓
    ViewModel Created
          ↓
Configuration Change (Rotation)
          ↓
Activity/Fragment Destroyed
          ↓
Activity/Fragment Re-created
          ↓
Same ViewModel Instance Reused
          ↓
Activity/Fragment Finally Destroyed
          ↓
    ViewModel.onCleared() Called
          ↓
    ViewModel Destroyed
```

## Use Cases

### When to Use

- **UI state management**: Store data displayed in UI (lists, forms, selections)
- **Configuration changes**: Preserve data across screen rotations
- **Asynchronous operations**: Manage coroutines and background tasks
- **Fragment communication**: Share data between fragments in same activity
- **Caching**: Cache data to avoid redundant network calls
- **Form handling**: Maintain form state during lifecycle events
- **Business logic**: Coordinate repository and use case calls

### When to Avoid

- **Holding Context references**: Never store Activity, Fragment, or View references
- **Long-lived operations**: Use WorkManager for operations that outlive app
- **Cross-Activity data**: Use Repository, DataStore, or Navigation arguments instead
- **Simple data passing**: Use Bundle for simple one-time data transfer
- **No UI logic**: If no UI state to manage, ViewModel may be unnecessary

## Trade-offs

**Pros**:
- Survives configuration changes automatically
- Promotes separation of concerns (UI vs business logic)
- Makes unit testing easier (no Android dependencies)
- Provides clear lifecycle-aware scope for coroutines
- Enables sharing data between fragments easily
- Integrates with LiveData, Flow, and other reactive streams
- Reduces boilerplate for state management
- Supports SavedStateHandle for process death scenarios

**Cons**:
- Cannot hold references to View, Activity, or Fragment
- Requires ViewModelProvider or dependency injection setup
- Additional abstraction layer increases complexity
- Must use Application Context for context-dependent operations
- Learning curve for developers new to MVVM pattern
- Potential over-engineering for very simple screens
- Need to handle navigation and events carefully (one-time events)

## Best Practices

- Never pass Activity, Fragment, or View references to ViewModel
- Use Application Context if context is needed (via dependency injection)
- Expose immutable state (LiveData/StateFlow) to UI layer
- Keep mutable state private within ViewModel
- Use viewModelScope for coroutines tied to ViewModel lifecycle
- Handle one-time events properly (using Event wrappers or Channels)
- Inject dependencies via constructor (supports testing)
- Use SavedStateHandle for data that should survive process death
- Clear resources in onCleared() if needed
- Keep ViewModels focused on single responsibility

## Common Patterns

### Event Wrapper Pattern (for one-time events)

```kotlin
class Event<out T>(private val content: T) {
    private var hasBeenHandled = false

    fun getContentIfNotHandled(): T? {
        return if (hasBeenHandled) {
            null
        } else {
            hasBeenHandled = true
            content
        }
    }

    fun peekContent(): T = content
}

class UserViewModel : ViewModel() {
    private val _navigateToDetails = MutableLiveData<Event<User>>()
    val navigateToDetails: LiveData<Event<User>> = _navigateToDetails

    fun onUserClick(user: User) {
        _navigateToDetails.value = Event(user)
    }
}

// In Fragment
viewModel.navigateToDetails.observe(viewLifecycleOwner) { event ->
    event.getContentIfNotHandled()?.let { user ->
        navigate(user)
    }
}
```

### Channel Pattern (for one-time events with Flow)

```kotlin
class UserViewModel : ViewModel() {
    private val _events = Channel<UserEvent>()
    val events = _events.receiveAsFlow()

    fun onUserClick(user: User) {
        viewModelScope.launch {
            _events.send(UserEvent.NavigateToDetails(user))
        }
    }
}

sealed class UserEvent {
    data class NavigateToDetails(val user: User) : UserEvent()
    data class ShowError(val message: String) : UserEvent()
}

// In Fragment
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            when (event) {
                is UserEvent.NavigateToDetails -> navigate(event.user)
                is UserEvent.ShowError -> showError(event.message)
            }
        }
    }
}
```

## Testing ViewModel

```kotlin
class UserViewModelTest {
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    @Test
    fun `loadUsers updates users LiveData`() = runTest {
        // Arrange
        val mockRepository = mock<UserRepository>()
        val expectedUsers = listOf(User("1", "John"))
        whenever(mockRepository.getUsers()).thenReturn(expectedUsers)

        val viewModel = UserViewModel(mockRepository)

        // Act
        viewModel.loadUsers()

        // Assert
        assertEquals(expectedUsers, viewModel.users.value)
    }

    @Test
    fun `loadUsers sets loading state`() = runTest {
        val mockRepository = mock<UserRepository>()
        val viewModel = UserViewModel(mockRepository)

        viewModel.loadUsers()

        assertTrue(viewModel.isLoading.value == false)
    }
}
```

## Related Concepts

- [[c-lifecycle]]
- [[c-livedata]]
- [[c-stateflow]]
- [[c-mvvm-pattern]]
- [[c-repository-pattern]]
- [[c-dependency-injection]]
- [[c-savedstatehandle]]
- [[c-viewmodelscope]]

## References

- [Android Developer Guide: ViewModel Overview](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [ViewModel Documentation](https://developer.android.com/reference/androidx/lifecycle/ViewModel)
- [ViewModels and LiveData: Patterns + AntiPatterns](https://medium.com/androiddevelopers/viewmodels-and-livedata-patterns-antipatterns-21efaef74a54)
- [Guide to App Architecture](https://developer.android.com/topic/architecture)

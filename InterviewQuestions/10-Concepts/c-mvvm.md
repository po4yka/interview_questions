---
id: "20251025-143100"
title: "MVVM Pattern / Паттерн MVVM"
aliases: ["Model-View-ViewModel", "MVVM Pattern", "MVVM", "Архитектура MVVM", "Паттерн MVVM"]
summary: "Architectural pattern that separates UI (View) from business logic (Model) using an intermediary ViewModel that exposes observable data and commands"
topic: "android"
subtopics: ["architecture-patterns", "mvvm", "viewmodel"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: [c-viewmodel, c-state-flow, c-clean-architecture, c-repository-pattern, c-dependency-injection]
created: "2025-10-25"
updated: "2025-10-25"
tags: ["android", "architecture-patterns", "concept", "databinding", "difficulty/medium", "livedata", "mvvm", "viewmodel"]
---

# MVVM Pattern / Паттерн MVVM

## Summary (EN)

MVVM (Model-View-ViewModel) is an architectural pattern that separates the user interface (View) from business logic (Model) using an intermediary component called ViewModel. The ViewModel exposes observable data and commands that the View can bind to, enabling automatic UI updates when data changes. This pattern promotes testability by isolating business logic from Android framework dependencies, supports reactive programming with LiveData/Flow, and survives configuration changes like screen rotations. MVVM is the recommended architecture pattern for Android development, integrated deeply with Android Architecture Components.

## Краткое Описание (RU)

MVVM (Model-View-ViewModel) - это архитектурный паттерн, который разделяет пользовательский интерфейс (View) от бизнес-логики (Model) с помощью промежуточного компонента ViewModel. ViewModel предоставляет наблюдаемые данные и команды, к которым View может привязаться, обеспечивая автоматическое обновление UI при изменении данных. Этот паттерн способствует тестируемости, изолируя бизнес-логику от зависимостей Android framework, поддерживает реактивное программирование с LiveData/Flow и переживает изменения конфигурации, такие как поворот экрана. MVVM - рекомендуемый архитектурный паттерн для разработки Android, глубоко интегрированный с Android Architecture Components.

## Key Points (EN)

- Separates concerns: View (UI), ViewModel (presentation logic), Model (data/business logic)
- View observes ViewModel data via LiveData, StateFlow, or Data Binding
- ViewModel has no reference to View (avoids memory leaks, enables testing)
- ViewModel survives configuration changes (screen rotation)
- Model represents data layer (repositories, network, database)
- Unidirectional data flow: View → ViewModel → Model → ViewModel → View
- Supports reactive programming and declarative UI
- Recommended by Google for Android apps

## Ключевые Моменты (RU)

- Разделение обязанностей: View (UI), ViewModel (логика представления), Model (данные/бизнес-логика)
- View наблюдает за данными ViewModel через LiveData, StateFlow или Data Binding
- ViewModel не имеет ссылок на View (избегает утечек памяти, позволяет тестирование)
- ViewModel переживает изменения конфигурации (поворот экрана)
- Model представляет слой данных (репозитории, сеть, база данных)
- Однонаправленный поток данных: View → ViewModel → Model → ViewModel → View
- Поддерживает реактивное программирование и декларативный UI
- Рекомендован Google для Android-приложений

## MVVM Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                     View                        │
│  (Activity, Fragment, Compose)                  │
│  - Renders UI                                   │
│  - Observes ViewModel data                      │
│  - Sends user actions to ViewModel              │
│  - NO business logic                            │
└───────────────┬─────────────────────────────────┘
                │ observes
                │ invokes methods
                ↓
┌─────────────────────────────────────────────────┐
│                  ViewModel                      │
│  - Exposes UI state (LiveData/StateFlow)        │
│  - Handles UI events (button clicks, etc.)      │
│  - Coordinates Model operations                 │
│  - Survives config changes                      │
│  - NO View references                           │
└───────────────┬─────────────────────────────────┘
                │ calls
                │
                ↓
┌─────────────────────────────────────────────────┐
│                    Model                        │
│  (Repository, UseCase, Data Source)             │
│  - Business logic                               │
│  - Data operations (network, database)          │
│  - Returns data to ViewModel                    │
└─────────────────────────────────────────────────┘
```

## MVVM Components

### 1. View (Activity/Fragment/Compose)

**Responsibilities**:
- Render UI based on ViewModel state
- Observe ViewModel LiveData/StateFlow
- Forward user interactions to ViewModel
- Handle navigation
- Show dialogs, toasts, snackbars

**What NOT to do**:
- Business logic
- Direct database/network access
- Complex calculations
- Hold references to ViewModel in static fields

```kotlin
// View example (Fragment)
class UserFragment : Fragment() {

    private val viewModel: UserViewModel by viewModels()
    private lateinit var binding: FragmentUserBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentUserBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe ViewModel state
        viewModel.uiState.observe(viewLifecycleOwner) { state ->
            when (state) {
                is UserUiState.Loading -> showLoading()
                is UserUiState.Success -> showUsers(state.users)
                is UserUiState.Error -> showError(state.message)
            }
        }

        // Forward user actions to ViewModel
        binding.buttonLoad.setOnClickListener {
            viewModel.loadUsers()
        }

        binding.buttonRetry.setOnClickListener {
            viewModel.retry()
        }
    }

    private fun showUsers(users: List<User>) {
        binding.recyclerView.isVisible = true
        binding.progressBar.isVisible = false
        adapter.submitList(users)
    }

    private fun showLoading() {
        binding.recyclerView.isVisible = false
        binding.progressBar.isVisible = true
    }

    private fun showError(message: String) {
        binding.recyclerView.isVisible = false
        binding.progressBar.isVisible = false
        Snackbar.make(binding.root, message, Snackbar.LENGTH_LONG).show()
    }
}
```

### 2. ViewModel (Presentation Logic)

**Responsibilities**:
- Expose UI state via LiveData/StateFlow
- Handle user events (clicks, input)
- Coordinate with Model (repositories, use cases)
- Transform Model data to UI state
- Manage coroutines/async operations
- Survive configuration changes

**What NOT to do**:
- Hold references to View, Activity, Fragment, Context
- Access View components directly
- Perform lifecycle-dependent operations

```kotlin
// ViewModel example
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    // UI state exposed to View
    private val _uiState = MutableLiveData<UserUiState>(UserUiState.Loading)
    val uiState: LiveData<UserUiState> = _uiState

    // Alternative: StateFlow
    private val _stateFlow = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val stateFlow: StateFlow<UserUiState> = _stateFlow.asStateFlow()

    init {
        loadUsers()
    }

    // Handle user action: load users
    fun loadUsers() {
        _uiState.value = UserUiState.Loading

        viewModelScope.launch {
            try {
                val users = userRepository.getUsers()
                _uiState.value = UserUiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UserUiState.Error(e.message ?: "Unknown error")
            }
        }
    }

    // Handle user action: retry
    fun retry() {
        loadUsers()
    }

    // Handle user action: search
    fun search(query: String) {
        viewModelScope.launch {
            val results = userRepository.searchUsers(query)
            _uiState.value = UserUiState.Success(results)
        }
    }

    override fun onCleared() {
        super.onCleared()
        // Clean up resources if needed
    }
}

// UI State sealed class
sealed class UserUiState {
    object Loading : UserUiState()
    data class Success(val users: List<User>) : UserUiState()
    data class Error(val message: String) : UserUiState()
}
```

### 3. Model (Data Layer)

**Responsibilities**:
- Business logic
- Data operations (network, database, cache)
- Data validation
- Data transformation
- Repository pattern implementation

**What NOT to do**:
- UI logic
- Android framework dependencies (Activity, Context)
- Direct UI updates

```kotlin
// Model example (Repository)
class UserRepository(
    private val apiService: UserApiService,
    private val userDao: UserDao,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {

    suspend fun getUsers(): List<User> = withContext(ioDispatcher) {
        try {
            // Try network first
            val users = apiService.getUsers()

            // Cache in database
            userDao.insertAll(users)

            users
        } catch (e: Exception) {
            // Fallback to cached data
            userDao.getAllUsers()
        }
    }

    suspend fun getUserById(id: String): User = withContext(ioDispatcher) {
        val cachedUser = userDao.getUserById(id)
        if (cachedUser != null) {
            return@withContext cachedUser
        }

        val user = apiService.getUserById(id)
        userDao.insert(user)
        user
    }

    suspend fun searchUsers(query: String): List<User> = withContext(ioDispatcher) {
        userDao.searchUsers("%$query%")
    }

    fun observeUsers(): Flow<List<User>> {
        return userDao.observeAllUsers()
    }
}
```

## MVVM with Jetpack Compose

```kotlin
// Composable View
@Composable
fun UserScreen(
    viewModel: UserViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is UserUiState.Loading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is UserUiState.Success -> {
            LazyColumn {
                items(state.users) { user ->
                    UserItem(
                        user = user,
                        onClick = { viewModel.onUserClick(user) }
                    )
                }
            }
        }
        is UserUiState.Error -> {
            ErrorScreen(
                message = state.message,
                onRetry = { viewModel.retry() }
            )
        }
    }
}

@Composable
fun UserItem(user: User, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = null,
                modifier = Modifier.size(48.dp).clip(CircleShape)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(user.name, style = MaterialTheme.typography.bodyLarge)
                Text(user.email, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
```

## MVVM with Data Binding

```xml
<!-- layout/fragment_user.xml -->
<layout xmlns:android="http://schemas.android.com/apk/res/android">

    <data>
        <variable
            name="viewModel"
            type="com.example.UserViewModel" />
    </data>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">

        <!-- Bind to ViewModel properties -->
        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="@{viewModel.userName}" />

        <ProgressBar
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:visibility="@{viewModel.isLoading ? View.VISIBLE : View.GONE}" />

        <!-- Bind click event to ViewModel method -->
        <Button
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Load Users"
            android:onClick="@{() -> viewModel.loadUsers()}" />

    </LinearLayout>
</layout>
```

```kotlin
class UserFragment : Fragment() {

    private val viewModel: UserViewModel by viewModels()
    private lateinit var binding: FragmentUserBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = DataBindingUtil.inflate(
            inflater,
            R.layout.fragment_user,
            container,
            false
        )

        // Set ViewModel for data binding
        binding.viewModel = viewModel
        binding.lifecycleOwner = viewLifecycleOwner

        return binding.root
    }
}
```

## Use Cases

### When to Use MVVM

- **Most Android apps**: Default choice for modern Android development
- **Complex UI logic**: Apps with significant presentation logic
- **Reactive UIs**: Apps requiring frequent UI updates based on data changes
- **Testable code**: When unit testing presentation logic is important
- **Configuration changes**: Apps that need to preserve state across rotations
- **Jetpack Compose apps**: Natural fit for declarative UI
- **Data-driven UIs**: Apps displaying data from repositories
- **Team development**: Clear separation enables parallel development

### When to Consider Alternatives

- **Very simple apps**: Single-screen apps with minimal logic (might be overkill)
- **MVI preference**: Teams preferring unidirectional data flow with single state
- **MVP legacy**: Existing MVP codebases (migration cost consideration)
- **Game development**: Different architectural needs (game loop, ECS)

## Trade-offs

**Pros**:
- **Testability**: ViewModel has no Android dependencies, easy to unit test
- **Separation of concerns**: Clear boundaries between UI, presentation, and data layers
- **Configuration change handling**: ViewModel survives rotations automatically
- **Reactive programming**: Built-in support for LiveData/Flow
- **Reusability**: ViewModel can be shared between fragments
- **Official support**: Recommended by Google, excellent documentation
- **Tool integration**: Android Studio, Jetpack libraries all support MVVM
- **Compose integration**: Works seamlessly with Jetpack Compose

**Cons**:
- **Learning curve**: Requires understanding of lifecycle, observers, coroutines
- **Boilerplate**: Can require significant boilerplate for simple UIs
- **View complexity**: Views can become large with many observer bindings
- **State management**: Managing complex state trees can be challenging
- **Debugging**: Reactive flows can be harder to debug than imperative code
- **Potential over-engineering**: Simple apps may not need this architecture
- **Data binding overhead**: XML data binding adds build time and complexity
- **Memory overhead**: ViewModel instances persist across config changes

## Best Practices

### ViewModel

- Never hold references to View, Activity, Fragment, or Context
- Use Application Context if context is absolutely needed (via dependency injection)
- Expose immutable state (LiveData/StateFlow) to View
- Keep mutable state private
- Use sealed classes for UI state representation
- Handle one-time events properly (Event wrapper, Channels)
- Use viewModelScope for coroutines
- Clear resources in onCleared() if needed

### View

- Observe ViewModel state in lifecycle-aware manner
- Don't implement business logic in View
- Use viewLifecycleOwner for fragments (not 'this')
- Handle navigation in View, not ViewModel
- Keep Views dumb - only render and forward events
- Use Compose for new UIs (simpler than XML + Data Binding)

### Model

- Keep repositories pure Kotlin (no Android dependencies)
- Use suspend functions for async operations
- Return Flow for observable data
- Implement caching strategies in repositories
- Use Kotlin Result or sealed classes for error handling
- Separate data sources (network, database, cache)

## Common Patterns

### UI State with Sealed Classes

```kotlin
sealed class UserUiState {
    object Loading : UserUiState()
    object Empty : UserUiState()
    data class Success(
        val users: List<User>,
        val isRefreshing: Boolean = false
    ) : UserUiState()
    data class Error(
        val message: String,
        val canRetry: Boolean = true
    ) : UserUiState()
}
```

### One-Time Events with Channels

```kotlin
class UserViewModel : ViewModel() {

    private val _events = Channel<UserEvent>()
    val events = _events.receiveAsFlow()

    fun onUserClick(user: User) {
        viewModelScope.launch {
            _events.send(UserEvent.NavigateToDetails(user.id))
        }
    }

    fun onError(error: Throwable) {
        viewModelScope.launch {
            _events.send(UserEvent.ShowError(error.message ?: "Unknown error"))
        }
    }
}

sealed class UserEvent {
    data class NavigateToDetails(val userId: String) : UserEvent()
    data class ShowError(val message: String) : UserEvent()
    object ShowSuccessMessage : UserEvent()
}

// In Fragment
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            when (event) {
                is UserEvent.NavigateToDetails -> navigateToDetails(event.userId)
                is UserEvent.ShowError -> showError(event.message)
                is UserEvent.ShowSuccessMessage -> showSuccess()
            }
        }
    }
}
```

### Combining Multiple Flows

```kotlin
class DashboardViewModel(
    private val userRepository: UserRepository,
    private val settingsRepository: SettingsRepository
) : ViewModel() {

    val uiState: StateFlow<DashboardUiState> = combine(
        userRepository.observeCurrentUser(),
        settingsRepository.observeSettings()
    ) { user, settings ->
        DashboardUiState(
            user = user,
            isDarkMode = settings.isDarkMode,
            notifications = settings.notificationsEnabled
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = DashboardUiState.Loading
    )
}
```

## Related Concepts

- [[c-viewmodel]]
- [[c-livedata]]
- [[c-stateflow]]
- [[c-repository-pattern]]
- [[c-dependency-injection]]
- [[c-clean-architecture]]
- [[c-mvi-pattern]]
- [[c-jetpack-compose]]
- [[c-data-binding]]

## References

- [Guide to App Architecture (MVVM)](https://developer.android.com/topic/architecture)
- [ViewModel Overview](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [LiveData Overview](https://developer.android.com/topic/libraries/architecture/livedata)
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [MVVM Pattern on Android (Medium)](https://medium.com/androiddevelopers/viewmodels-and-livedata-patterns-antipatterns-21efaef74a54)
- [Jetpack Compose and MVVM](https://developer.android.com/jetpack/compose/architecture)

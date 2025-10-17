---
id: "20251015082237300"
title: "Android Architectural Patterns / Android Architectural Паттерны"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - architecture-patterns
  - clean-architecture
  - component-based
  - mvc
  - mvp
  - mvvm
---
# Какие архитектурные паттерны используются в Android-фреймворке?

# Question (EN)
> What architectural patterns are used in Android framework?

# Вопрос (RU)
> Какие архитектурные паттерны используются в Android-фреймворке?

---

## Answer (EN)

Android development uses several architectural patterns: MVC (early, rarely used), MVP (Model-View-Presenter), MVVM (Model-View-ViewModel with data binding), MVI (Model-View-Intent for unidirectional data flow), and Clean Architecture (layered approach with dependency inversion).

**Modern recommendation**: MVVM with Clean Architecture and Android Architecture Components (ViewModel, LiveData/StateFlow, Repository pattern).

---

## Ответ (RU)

Android development uses several architectural patterns to organize code, separate concerns, and improve testability. Each pattern has evolved to address specific challenges in Android development.

### 1. MVC (Model-View-Controller)

**Early Android pattern** - rarely used today.

**Components:**
- **Model**: Business logic and data
- **View**: UI display (XML layouts)
- **Controller**: Manages flow (Activity/Fragment)

```kotlin
// Model
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    fun getUser(id: Int): User {
        // Fetch from database or API
        return User(id, "John Doe", "john@example.com")
    }
}

// View (XML)
// activity_main.xml with TextView to display user data

// Controller (Activity)
class MainActivity : AppCompatActivity() {
    private val repository = UserRepository()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Controller manages both UI and logic
        val user = repository.getUser(1)
        findViewById<TextView>(R.id.userName).text = user.name
        findViewById<TextView>(R.id.userEmail).text = user.email
    }
}
```

**Problems:**
- Activity is both View and Controller
- Tight coupling between UI and logic
- Difficult to test
- Activity becomes massive (God Object)

### 2. MVP (Model-View-Presenter)

**Improved separation** - popular before MVVM.

**Components:**
- **Model**: Data and business logic
- **View**: Passive UI (Activity/Fragment implements interface)
- **Presenter**: Presentation logic, no Android dependencies

```kotlin
// Model
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    suspend fun getUser(id: Int): User {
        delay(1000) // Simulate network call
        return User(id, "John Doe", "john@example.com")
    }
}

// View Contract
interface UserContract {
    interface View {
        fun showUser(user: User)
        fun showLoading()
        fun hideLoading()
        fun showError(message: String)
    }

    interface Presenter {
        fun loadUser(id: Int)
        fun onDestroy()
    }
}

// Presenter
class UserPresenter(
    private val view: UserContract.View,
    private val repository: UserRepository
) : UserContract.Presenter {

    private val scope = CoroutineScope(Dispatchers.Main + Job())

    override fun loadUser(id: Int) {
        view.showLoading()

        scope.launch {
            try {
                val user = withContext(Dispatchers.IO) {
                    repository.getUser(id)
                }
                view.hideLoading()
                view.showUser(user)
            } catch (e: Exception) {
                view.hideLoading()
                view.showError(e.message ?: "Unknown error")
            }
        }
    }

    override fun onDestroy() {
        scope.cancel()
    }
}

// View Implementation (Activity)
class UserActivity : AppCompatActivity(), UserContract.View {

    private lateinit var presenter: UserContract.Presenter
    private lateinit var nameTextView: TextView
    private lateinit var emailTextView: TextView
    private lateinit var progressBar: ProgressBar

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)

        nameTextView = findViewById(R.id.userName)
        emailTextView = findViewById(R.id.userEmail)
        progressBar = findViewById(R.id.progressBar)

        presenter = UserPresenter(this, UserRepository())
        presenter.loadUser(1)
    }

    override fun showUser(user: User) {
        nameTextView.text = user.name
        emailTextView.text = user.email
    }

    override fun showLoading() {
        progressBar.visibility = View.VISIBLE
    }

    override fun hideLoading() {
        progressBar.visibility = View.GONE
    }

    override fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }
}
```

**Advantages:**
- Clear separation of concerns
- Presenter is testable (no Android dependencies)
- View is passive (easy to swap)

**Disadvantages:**
- Lots of boilerplate (interfaces for every screen)
- Memory leaks if Presenter holds View reference
- No lifecycle awareness

### 3. MVVM (Model-View-ViewModel)

**Current Android standard** with Jetpack support.

**Components:**
- **Model**: Data structures and repositories
- **View**: UI elements (Activity/Fragment/Compose)
- **ViewModel**: Presentation logic with observable data

```kotlin
// Model
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    suspend fun getUser(id: Int): User {
        delay(1000)
        return User(id, "John Doe", "john@example.com")
    }
}

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val message: String) : UiState()
    }

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val user = repository.getUser(id)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

// View (Activity with View Binding)
class UserActivity : AppCompatActivity() {

    private lateinit var binding: ActivityUserBinding
    private val viewModel: UserViewModel by viewModels {
        UserViewModelFactory(UserRepository())
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserBinding.inflate(layoutInflater)
        setContentView(binding.root)

        observeUiState()
        viewModel.loadUser(1)
    }

    private fun observeUiState() {
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is UserViewModel.UiState.Loading -> {
                        binding.progressBar.visibility = View.VISIBLE
                        binding.userInfo.visibility = View.GONE
                    }
                    is UserViewModel.UiState.Success -> {
                        binding.progressBar.visibility = View.GONE
                        binding.userInfo.visibility = View.VISIBLE
                        binding.userName.text = state.user.name
                        binding.userEmail.text = state.user.email
                    }
                    is UserViewModel.UiState.Error -> {
                        binding.progressBar.visibility = View.GONE
                        Toast.makeText(this@UserActivity, state.message, Toast.LENGTH_LONG).show()
                    }
                }
            }
        }
    }
}

// Jetpack Compose View
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is UserViewModel.UiState.Loading -> {
            CircularProgressIndicator()
        }
        is UserViewModel.UiState.Success -> {
            Column {
                Text(text = "Name: ${state.user.name}")
                Text(text = "Email: ${state.user.email}")
            }
        }
        is UserViewModel.UiState.Error -> {
            Text(text = "Error: ${state.message}")
        }
    }
}
```

**Advantages:**
- Lifecycle-aware (ViewModel survives configuration changes)
- Two-way data binding support
- Automatic UI updates with LiveData/Flow
- Official Google support
- No memory leaks
- Testable

**Disadvantages:**
- Learning curve for reactive programming
- Can lead to complex ViewModels if not structured well

### 4. MVI (Model-View-Intent)

**Unidirectional data flow** - gaining popularity.

```kotlin
// State
data class UserState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

// Intent (User actions)
sealed class UserIntent {
    data class LoadUser(val id: Int) : UserIntent()
    object RetryLoading : UserIntent()
}

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    fun handleIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUser -> loadUser(intent.id)
            is UserIntent.RetryLoading -> state.value.user?.let { loadUser(it.id) }
        }
    }

    private fun loadUser(id: Int) {
        viewModelScope.launch {
            _state.value = state.value.copy(isLoading = true, error = null)

            try {
                val user = repository.getUser(id)
                _state.value = state.value.copy(
                    isLoading = false,
                    user = user,
                    error = null
                )
            } catch (e: Exception) {
                _state.value = state.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }
}

// View (Compose)
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.handleIntent(UserIntent.LoadUser(1))
    }

    Column {
        if (state.isLoading) {
            CircularProgressIndicator()
        }

        state.user?.let { user ->
            Text("Name: ${user.name}")
            Text("Email: ${user.email}")
        }

        state.error?.let { error ->
            Text("Error: $error")
            Button(onClick = { viewModel.handleIntent(UserIntent.RetryLoading) }) {
                Text("Retry")
            }
        }
    }
}
```

**Advantages:**
- Predictable state management
- Single source of truth
- Easy to debug (state changes are traceable)
- Great for complex UIs

### 5. Clean Architecture

**Multi-layer architecture** for complex apps.

```kotlin
// Domain Layer - Core business logic
// Entities
data class User(
    val id: Int,
    val name: String,
    val email: String
)

// Use Cases
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: Int): Result<User> {
        return try {
            val user = repository.getUser(id)
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Domain Repository Interface
interface UserRepository {
    suspend fun getUser(id: Int): User
}

// Data Layer - Data sources and implementation
// Repository Implementation
class UserRepositoryImpl(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource
) : UserRepository {

    override suspend fun getUser(id: Int): User {
        return try {
            // Try remote first
            val user = remoteDataSource.getUser(id)
            // Cache locally
            localDataSource.saveUser(user)
            user
        } catch (e: Exception) {
            // Fallback to local cache
            localDataSource.getUser(id)
        }
    }
}

// Remote Data Source
class UserRemoteDataSource(private val api: ApiService) {
    suspend fun getUser(id: Int): User {
        val response = api.getUser(id)
        return response.toDomain()
    }
}

// Local Data Source
class UserLocalDataSource(private val dao: UserDao) {
    suspend fun getUser(id: Int): User {
        return dao.getUserById(id).toDomain()
    }

    suspend fun saveUser(user: User) {
        dao.insert(user.toEntity())
    }
}

// Presentation Layer - UI and ViewModels
class UserViewModel(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            getUserUseCase(id).fold(
                onSuccess = { user ->
                    _uiState.value = UiState.Success(user)
                },
                onFailure = { exception ->
                    _uiState.value = UiState.Error(exception.message ?: "Unknown error")
                }
            )
        }
    }

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val message: String) : UiState()
    }
}

// Dependency Injection
@Module
class UserModule {
    @Provides
    fun provideGetUserUseCase(repository: UserRepository): GetUserUseCase {
        return GetUserUseCase(repository)
    }

    @Provides
    fun provideUserRepository(
        remoteDataSource: UserRemoteDataSource,
        localDataSource: UserLocalDataSource
    ): UserRepository {
        return UserRepositoryImpl(remoteDataSource, localDataSource)
    }
}
```

**Layers:**
1. **Domain**: Entities, Use Cases, Repository Interfaces
2. **Data**: Repository Implementations, Data Sources, DTOs
3. **Presentation**: ViewModels, UI (Activities/Fragments/Compose)

**Advantages:**
- Highly testable (each layer independently)
- Scalable for large apps
- Clear separation of concerns
- Framework-independent business logic

**Disadvantages:**
- More complex
- More files and boilerplate
- Overkill for small apps

### Comparison Table

| Pattern | Complexity | Testability | Boilerplate | Lifecycle-Aware | Use Case |
|---------|------------|-------------|-------------|-----------------|----------|
| **MVC** | Low | Low | Low | No | Simple apps (legacy) |
| **MVP** | Medium | High | High | No | Medium apps |
| **MVVM** | Medium | High | Medium | Yes | Modern Android apps |
| **MVI** | Medium-High | Very High | Medium | Yes | Complex UIs with state |
| **Clean Architecture** | High | Very High | High | Yes (with MVVM) | Large enterprise apps |

### Modern Android Recommendation

**For most apps:**
```
MVVM + Repository Pattern + Dependency Injection
```

**For complex apps:**
```
Clean Architecture + MVVM/MVI + Jetpack Compose + Hilt
```

**Architecture Example:**

```
app/
 di/                  (Dependency Injection - Hilt modules)
 data/
    local/          (Room, SharedPreferences)
    remote/         (Retrofit, APIs)
    repository/     (Repository implementations)
 domain/
    model/          (Domain entities)
    usecase/        (Business logic)
 presentation/
     ui/             (Compose screens or Fragments)
     viewmodel/      (ViewModels)
```

### Summary

**Evolution:**
- MVC (2008-2012): Too coupled
- MVP (2012-2017): Better separation, but boilerplate
- MVVM (2017-present): Official Google recommendation
- MVI (2019-present): Better state management
- Clean Architecture (ongoing): Enterprise-grade apps

**Current Best Practice:** MVVM + Clean Architecture (when needed) + Jetpack Compose

## Ответ (RU)
В разработке Android-приложений применяются следующие архитектурные паттерны: MVC, MVP, MVVM, Clean Architecture, Component-Based Architecture.


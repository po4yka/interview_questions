---
topic: android
tags:
  - android
  - architecture-patterns
  - mvvm
  - model-view-viewmodel
  - viewmodel
  - data-binding
  - lifecycle
difficulty: medium
status: reviewed
---

# MVVM Pattern

**English**: What is the MVVM (Model-View-ViewModel) architectural pattern? Explain its components and advantages.

## Answer

**MVVM (Model-View-ViewModel)** - архитектурный паттерн, который обеспечивает разделение разработки пользовательского интерфейса от бизнес-логики или backend-логики (модели), так что представление не зависит от какой-либо конкретной платформы модели.

### Компоненты MVVM

**Model–view–viewmodel (MVVM)** is a software architectural pattern that facilitates the separation of the development of the UI from the development of the business logic or back-end logic (the model) so that the view is not dependent on any specific model platform.

The separate code layers of MVVM are:

**1. Model**:
- This layer is responsible for the abstraction of the data sources
- Model and ViewModel work together to get and save the data
- Represents domain logic (business rules, data validation)
- Handles data sources (database, network, cache)

**2. View**:
- The purpose of this layer is to inform the ViewModel about the user's action
- This layer observes the ViewModel and does not contain any kind of application logic
- Represents UI components (Activities, Fragments, Composables)
- Displays data provided by ViewModel
- Routes user interactions to ViewModel

**3. ViewModel**:
- It exposes those data streams which are relevant to the View
- Moreover, it serves as a link between the Model and the View
- Manages UI-related data in a lifecycle-conscious way
- Survives configuration changes
- Provides data to the View via observable data holders (LiveData, StateFlow)

### MVVM Diagram

```
┌─────────────┐
│    View     │ ◄──── User Interaction
│ (Activity/  │
│  Fragment)  │
└──────┬──────┘
       │ observes
       │ (LiveData/Flow)
       ▼
┌─────────────┐
│  ViewModel  │
│             │
└──────┬──────┘
       │ uses
       ▼
┌─────────────┐
│    Model    │
│ (Repository)│
└─────────────┘
```

### Важные особенности MVVM

It is important to note that in MVVM:
- The view doesn't maintain state information; instead, it is synchronized with the ViewModel
- In MVVM, the ViewModel isolates the presentation layer and offers methods and commands for managing the state of a view and manipulating the model
- The view and the ViewModel have **bi-directional data binding**, or two-way data binding, which guarantees that the ViewModel's models and properties are in sync with the view

### Пример MVVM в Android

```kotlin
// Model - Data class
data class User(
    val id: Int,
    val name: String,
    val email: String
)

// Model - Repository
class UserRepository {
    suspend fun getUser(id: Int): User {
        // Получение данных из сети или БД
        return api.fetchUser(id)
    }
}

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    // Exposed state to View
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val user = repository.getUser(userId)
                _user.value = user
                _error.value = null
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }
}

// View - Activity
class UserActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()
    private lateinit var binding: ActivityUserBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Observe ViewModel data
        viewModel.user.observe(this) { user ->
            binding.nameTextView.text = user.name
            binding.emailTextView.text = user.email
        }

        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.isVisible = isLoading
        }

        viewModel.error.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_SHORT).show()
            }
        }

        // Load data
        viewModel.loadUser(1)
    }
}
```

### MVVM with Jetpack Compose

```kotlin
// ViewModel remains the same
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val user = repository.getUser(userId)
                _uiState.value = _uiState.value.copy(
                    user = user,
                    isLoading = false,
                    error = null
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }
}

data class UserUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

// View - Composable
@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadUser(1)
    }

    when {
        uiState.isLoading -> LoadingIndicator()
        uiState.error != null -> ErrorView(uiState.error!!)
        uiState.user != null -> UserContent(uiState.user!!)
    }
}
```

### Преимущества MVVM

**Advantages**:

1. **Maintainability** – Can remain agile and keep releasing successive versions quickly
2. **Extensibility** – Have the ability to replace or add new pieces of code
3. **Testability** – Easier to write unit tests against a core logic
4. **Transparent Communication** – The view model provides a transparent interface to the view controller, which it uses to populate the view layer and interact with the model layer, which results in a transparent communication between the layers of your application
5. **Lifecycle awareness** - ViewModel survives configuration changes automatically
6. **Separation of concerns** - Clear separation between UI and business logic
7. **No View reference** - ViewModel doesn't hold reference to View, preventing memory leaks

### Недостатки MVVM

**Disadvantages**:

1. Some people think that for simple UIs, MVVM can be overkill
2. In bigger cases, it can be hard to design the ViewModel
3. Debugging would be a bit difficult when we have complex data bindings
4. **Learning curve** - Requires understanding of reactive programming (LiveData, Flow)
5. **Boilerplate** - More code compared to simple Activity-based approach

### MVVM vs Other Patterns

| Aspect | MVVM | MVP | MVC |
|--------|------|-----|-----|
| **View-Logic binding** | Automatic (data binding) | Manual (interface calls) | Manual |
| **View reference** | ViewModel doesn't know View | Presenter knows View | Controller knows View |
| **Lifecycle** | Lifecycle-aware | Manual handling | Manual handling |
| **Configuration changes** | Data survives | Data may be lost | Data lost |
| **Testability** | Excellent | Good | Moderate |

### Best Practices

```kotlin
// - DO: Single source of truth
data class ScreenState(
    val data: List<Item> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// - DO: Expose immutable data to View
private val _state = MutableStateFlow(ScreenState())
val state: StateFlow<ScreenState> = _state.asStateFlow()

// - DO: Use ViewModelScope for coroutines
viewModelScope.launch {
    // Coroutine code
}

// - DON'T: Hold View reference in ViewModel
class BadViewModel(private val view: Activity) : ViewModel() // BAD

// - DON'T: Put Android framework dependencies in ViewModel
class BadViewModel(private val context: Context) : ViewModel() // BAD
```

**English**: **MVVM (Model-View-ViewModel)** is an architectural pattern that separates UI development from business logic. **Components**: (1) Model - data and business logic, (2) View - UI components that observe ViewModel, (3) ViewModel - manages UI state, survives configuration changes. **Key feature**: bi-directional data binding between View and ViewModel. **Advantages**: maintainability, testability, lifecycle awareness, no View reference in ViewModel. **Disadvantages**: can be overkill for simple UIs, learning curve for reactive programming. Widely used in modern Android with Jetpack components (ViewModel, LiveData, StateFlow).

## Links

- [Model–view–viewmodel](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)
- [MVVM (Model View ViewModel) Architecture Pattern in Android](https://www.geeksforgeeks.org/mvvm-model-view-viewmodel-architecture-pattern-in-android/)
- [Guide to app architecture](https://developer.android.com/jetpack/guide)
- [MVVM Architecture - Android Tutorial for Beginners](https://blog.mindorks.com/mvvm-architecture-android-tutorial-for-beginners-step-by-step-guide)

## Further Reading

- [Android Architecture Patterns Part 3: Model-View-ViewModel](https://medium.com/upday-devs/android-architecture-patterns-part-3-model-view-viewmodel-e7eeee76b73b)
- [MVVM and DataBinding: Android Design Patterns](https://www.raywenderlich.com/636803-mvvm-and-databinding-android-design-patterns)
- [Pokedex (MVVM example)](https://github.com/skydoves/Pokedex)

---
*Source: Kirchhoff Android Interview Questions*

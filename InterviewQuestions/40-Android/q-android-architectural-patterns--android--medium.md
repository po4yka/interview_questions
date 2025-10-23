---
id: 20251012-122761
title: Android Architectural Patterns / Архитектурные паттерны Android
aliases:
- Android Architectural Patterns
- Архитектурные паттерны Android
topic: android
subtopics:
- architecture-clean
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-mvvm-pattern--android--medium
- q-clean-architecture-android--android--hard
- q-viewmodel-pattern--android--easy
created: 2025-10-15
updated: 2025-10-15
tags:
- android/architecture-clean
- difficulty/medium
---

## Answer (EN)
Android development uses several [[c-architectural-patterns|architectural patterns]]: [[c-mvc|MVC]] (early, rarely used), [[c-mvp|MVP]] (Model-View-Presenter), [[c-mvvm|MVVM]] (Model-View-ViewModel with data binding), [[c-mvi|MVI]] (Model-View-Intent for unidirectional data flow), and [[c-clean-architecture|Clean Architecture]] (layered approach with dependency inversion).

**Modern recommendation**: MVVM with Clean Architecture and Android Architecture Components (ViewModel, LiveData/StateFlow, Repository pattern).

**1. MVC (Model-View-Controller)**
- **Early Android pattern** - rarely used today
- **Components**: Model (business logic), View (XML layouts), Controller (Activity/Fragment)
- **Problems**: Activity is both View and Controller, tight coupling, difficult to test

```kotlin
// BAD: MVC - Activity does everything
class MainActivity : AppCompatActivity() {
    private val repository = UserRepository()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val user = repository.getUser(1) // Blocking call
        findViewById<TextView>(R.id.userName).text = user.name
    }
}
```

**2. MVP (Model-View-Presenter)**
- **Improved separation** - popular before MVVM
- **Components**: Model (data), View (passive UI), Presenter (presentation logic)
- **Advantages**: Clear separation, testable presenter, swappable view
- **Disadvantages**: Lots of boilerplate, memory leaks, no lifecycle awareness

```kotlin
// MVP - Better separation
interface UserContract {
    interface View {
        fun showUser(user: User)
        fun showLoading()
    }

    interface Presenter {
        fun loadUser(id: Int)
    }
}

class UserPresenter(
    private val view: UserContract.View,
    private val repository: UserRepository
) : UserContract.Presenter {

    override fun loadUser(id: Int) {
        view.showLoading()
        // Load user asynchronously
                view.showUser(user)
    }
}
```

**3. MVVM (Model-View-ViewModel)**
- **Current Android standard** with Jetpack support
- **Components**: Model (data), View (UI), ViewModel (presentation logic with observable data)
- **Advantages**: Lifecycle-aware, two-way data binding, automatic UI updates, official Google support

```kotlin
// MVVM - Modern approach
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

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

// View observes ViewModel
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
            is UiState.Loading -> showLoading()
            is UiState.Success -> showUser(state.user)
            is UiState.Error -> showError(state.message)
        }
    }
}
```

**4. MVI (Model-View-Intent)**
- **Unidirectional data flow** - gaining popularity
- **Components**: State (single source of truth), Intent (user actions), View (renders state)
- **Advantages**: Predictable state management, easy to debug, great for complex UIs

```kotlin
// MVI - Unidirectional flow
data class UserState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

sealed class UserIntent {
    data class LoadUser(val id: Int) : UserIntent()
    object RetryLoading : UserIntent()
}

class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    fun handleIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUser -> loadUser(intent.id)
            is UserIntent.RetryLoading -> retry()
        }
    }
}
```

**5. Clean Architecture**
- **Multi-layer architecture** for complex apps
- **Layers**: Domain (entities, use cases), Data (repositories, data sources), Presentation (UI, ViewModels)
- **Advantages**: Highly testable, scalable, clear separation, framework-independent business logic

```kotlin
// Clean Architecture - Layered approach
// Domain Layer
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

// Data Layer
class UserRepositoryImpl(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource
) : UserRepository {

    override suspend fun getUser(id: Int): User {
        return try {
            val user = remoteDataSource.getUser(id)
            localDataSource.saveUser(user)
            user
        } catch (e: Exception) {
            localDataSource.getUser(id)
        }
    }
}

// Presentation Layer
class UserViewModel(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            getUserUseCase(id).fold(
                onSuccess = { user -> _uiState.value = UiState.Success(user) },
                onFailure = { error -> _uiState.value = UiState.Error(error.message) }
            )
        }
    }
}
```

**Comparison:**

| Pattern | Complexity | Testability | Boilerplate | Lifecycle-Aware | Use Case |
|---------|------------|-------------|-------------|-----------------|----------|
| **MVC** | Low | Low | Low | No | Simple apps (legacy) |
| **MVP** | Medium | High | High | No | Medium apps |
| **MVVM** | Medium | High | Medium | Yes | Modern Android apps |
| **MVI** | Medium-High | Very High | Medium | Yes | Complex UIs with state |
| **Clean Architecture** | High | Very High | High | Yes (with MVVM) | Large enterprise apps |

**Modern Android Recommendation:**
- **For most apps**: MVVM + Repository Pattern + Dependency Injection
- **For complex apps**: Clean Architecture + MVVM/MVI + Jetpack Compose + Hilt

## Follow-ups

- How do you choose between MVVM and MVI for a new project?
- What are the key differences between MVP and MVVM?
- How do you implement Clean Architecture in a small Android app?
- What are the benefits of using Repository pattern with MVVM?
- How do you handle state management in complex UIs with MVI?

## References

- [Android Architecture Guide](https://developer.android.com/topic/architecture)
- [MVVM Pattern](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [MVI Pattern](https://proandroiddev.com/mvi-architecture-in-android-using-kotlin-coroutines-and-flow-2b4b0b0b0b0b)

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - ViewModel basics
- [[q-android-app-components--android--easy]] - App components

### Related (Medium)
- [[q-mvvm-pattern--android--medium]] - MVVM implementation
- [[q-clean-architecture-android--android--hard]] - Clean Architecture
- [[q-architecture-components-libraries--android--easy]] - Architecture Components

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]] - MVI implementation
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture
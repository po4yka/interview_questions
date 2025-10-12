---
topic: android
tags:
  - android
  - android/architecture-mvp
  - android/architecture-mvvm
  - architecture-mvp
  - architecture-mvvm
  - architecture-patterns
  - data-binding
  - lifecycle
  - mvp
  - mvvm
  - presenter
  - viewmodel
difficulty: medium
status: draft
---

# Чем MVVM отличается от MVP?

**English**: What is the difference between MVVM and MVP?

## Answer (EN)
**MVVM (Model-View-ViewModel)** and **MVP (Model-View-Presenter)** are both architectural patterns for separating concerns, but they differ in how components interact.

**Key Differences:**

**1. View-ViewModel/Presenter Relationship:**

**MVP:**
- **View** and **Presenter** have explicit, bidirectional communication
- Presenter holds a reference to View interface
- View explicitly calls Presenter methods
- Presenter explicitly calls View methods to update UI

```kotlin
// MVP
interface MainView {
    fun showLoading()
    fun hideLoading()
    fun showUsers(users: List<User>)
    fun showError(message: String)
}

class MainPresenter(private val view: MainView) {
    fun loadUsers() {
        view.showLoading()
        repository.getUsers { users ->
            view.hideLoading()
            view.showUsers(users)  // Explicit View update
        }
    }
}

class MainActivity : AppCompatActivity(), MainView {
    private val presenter = MainPresenter(this)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter.loadUsers()  // Explicit call
    }

    override fun showUsers(users: List<User>) {
        // Update UI manually
        adapter.submitList(users)
    }
}
```

**MVVM:**
- **View** and **ViewModel** are loosely coupled via **data binding**
- ViewModel doesn't know about View (no reference)
- View observes ViewModel's data (LiveData, StateFlow)
- Automatic UI updates when data changes

```kotlin
// MVVM
class MainViewModel : ViewModel() {
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    fun loadUsers() {
        _isLoading.value = true
        viewModelScope.launch {
            val result = repository.getUsers()
            _users.value = result  // Automatic View update
            _isLoading.value = false
        }
    }
}

class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Observe data (automatic updates)
        viewModel.users.observe(this) { users ->
            adapter.submitList(users)  // Auto-updated
        }

        viewModel.isLoading.observe(this) { isLoading ->
            progressBar.isVisible = isLoading
        }

        viewModel.loadUsers()
    }
}
```

**2. Data Binding:**

| Aspect | MVP | MVVM |
|--------|-----|------|
| **Binding** | Manual (explicit calls) | Automatic (LiveData/Flow) |
| **View updates** | Presenter → View interface | Observable data changes |
| **View knowledge** | Presenter knows View | ViewModel doesn't know View |
| **Coupling** | Tighter (Presenter-View) | Looser (ViewModel-View) |

**3. Lifecycle Awareness:**

**MVP:**
- Presenter must manually handle lifecycle
- Risk of memory leaks if Presenter holds View reference
- Needs careful cleanup in onDestroy()

**MVVM:**
- ViewModel is lifecycle-aware (survives configuration changes)
- No memory leak risk (ViewModel doesn't reference View)
- Automatic cleanup

**4. Configuration Changes:**

| Pattern | Configuration Change Handling |
|---------|------------------------------|
| **MVP** | Presenter recreated, data lost (unless cached) |
| **MVVM** | ViewModel survives, data retained |

**Summary:**

| Feature | MVP | MVVM |
|---------|-----|------|
| **View-Logic coupling** | Tight (interface) | Loose (observables) |
| **View updates** | Manual (explicit calls) | Automatic (data binding) |
| **Lifecycle handling** | Manual | Automatic |
| **View reference** | Presenter holds View | ViewModel doesn't know View |
| **Configuration changes** | Data may be lost | Data survives |
| **Android components** | No special support | Jetpack ViewModel, LiveData |
| **Boilerplate** | More (interface methods) | Less (observables) |
| **Testability** | Good (mock View) | Excellent (no View needed) |

**When to use:**
- **MVP**: Legacy projects, complex View interactions, explicit control
- **MVVM**: Modern Android (Jetpack), reactive programming, lifecycle-aware apps

**Conclusion:** MVVM is generally preferred for modern Android development due to better lifecycle awareness, automatic data binding, and official Jetpack support.

## Ответ (RU)
MVVM использует привязку данных для автоматического обновления View, что упрощает управление интерфейсом. MVP требует явного управления View через Presenter.


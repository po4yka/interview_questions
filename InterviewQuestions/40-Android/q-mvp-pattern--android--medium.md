---
id: "20251015082237355"
title: "Mvp Pattern / Mvp Паттерн"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - architecture-patterns
  - mvp
  - model-view-presenter
  - presenter
  - contract
---
# MVP Pattern

**English**: What is the MVP (Model-View-Presenter) architectural pattern? Explain its components and how it differs from other patterns.

## Answer (EN)
**MVP (Model-View-Presenter)** - архитектурный паттерн, разработанный для облегчения автоматизированного модульного тестирования и улучшения разделения ответственности в презентационной логике.

### Компоненты MVP

MVP is an architectural pattern engineered to facilitate automated unit testing and improve the separation of concerns in presentation logic.

**Role of components**:

**1. Model**:
- The data layer
- Responsible for handling the business logic and communication with the network and database layers
- Provides data to Presenter
- Independent of UI

**2. View**:
- The UI layer
- Displays the data and notifies the Presenter about user actions
- Passive - doesn't contain logic, only displays what Presenter tells it to
- Implemented by Activity/Fragment

**3. Presenter**:
- Retrieves the data from the Model
- Applies the UI logic and manages the state of the View
- Decides what to display
- Reacts to user input notifications from the View
- Acts as a "middleman" between Model and View

### MVP Diagram

```

    View       User Interaction
 (Activity/  
  Fragment)  

        calls
        notifies
       

  Presenter  
             

        uses
       

    Model    
 (Repository)

```

### Contract Interface

Since the View and the Presenter work closely together, they need to have a reference to one another. To make the Presenter unit testable with JUnit, the View is abstracted and an interface for it used.

The relationship between the Presenter and its corresponding View is defined in a **Contract** interface class, making the code more readable and the connection between the two easier to understand.

### Пример MVP с Contract

```kotlin
// Contract - определяет связь между View и Presenter
interface UserContract {

    interface View {
        fun showLoading()
        fun hideLoading()
        fun showUser(user: User)
        fun showError(message: String)
    }

    interface Presenter {
        fun attachView(view: View)
        fun detachView()
        fun loadUser(userId: Int)
    }
}

// Model
data class User(
    val id: Int,
    val name: String,
    val email: String
)

class UserRepository {
    fun getUser(userId: Int, callback: (Result<User>) -> Unit) {
        // Асинхронная загрузка данных
        // callback(Result.success(user))
    }
}

// Presenter
class UserPresenter(
    private val repository: UserRepository
) : UserContract.Presenter {

    private var view: UserContract.View? = null

    override fun attachView(view: UserContract.View) {
        this.view = view
    }

    override fun detachView() {
        this.view = null
    }

    override fun loadUser(userId: Int) {
        view?.showLoading()

        repository.getUser(userId) { result ->
            view?.hideLoading()

            result.onSuccess { user ->
                view?.showUser(user)
            }

            result.onFailure { error ->
                view?.showError(error.message ?: "Unknown error")
            }
        }
    }
}

// View - Activity
class UserActivity : AppCompatActivity(), UserContract.View {

    private lateinit var presenter: UserContract.Presenter
    private lateinit var binding: ActivityUserBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Initialize Presenter
        val repository = UserRepository()
        presenter = UserPresenter(repository)
        presenter.attachView(this)

        // Load user
        binding.loadButton.setOnClickListener {
            presenter.loadUser(1)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        presenter.detachView() // Prevent memory leaks
    }

    override fun showLoading() {
        binding.progressBar.isVisible = true
    }

    override fun hideLoading() {
        binding.progressBar.isVisible = false
    }

    override fun showUser(user: User) {
        binding.nameTextView.text = user.name
        binding.emailTextView.text = user.email
    }

    override fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
```

### Зачем использовать MVP?

## Why Use MVP?

This MVP design pattern helps to segregate code into three different parts: business logic (Presenter), UI (View), and data interaction (Model). This modulation of code is easy to understand and maintain.

**Example**: In our application, if we use a content provider to persist our data and later we want to upgrade it with a SQLite database, the MVP design pattern will make this very easy. We only need to modify the Model layer without touching View or Presenter.

### Lifecycle Management в MVP

```kotlin
// Presenter с учетом lifecycle
class UserPresenter(
    private val repository: UserRepository
) : UserContract.Presenter, CoroutineScope {

    override val coroutineContext: CoroutineContext
        get() = Dispatchers.Main + job

    private var job = Job()
    private var view: UserContract.View? = null

    override fun attachView(view: UserContract.View) {
        this.view = view
        job = Job() // Новый Job при attach
    }

    override fun detachView() {
        job.cancel() // Отменяем все корутины
        this.view = null
    }

    override fun loadUser(userId: Int) {
        launch {
            view?.showLoading()
            try {
                val user = repository.getUser(userId)
                view?.showUser(user)
            } catch (e: Exception) {
                view?.showError(e.message ?: "Error")
            } finally {
                view?.hideLoading()
            }
        }
    }
}
```

### Преимущества MVP

**Advantages of MVP Architecture**:

1. **No conceptual relationship in android components** - Model, View, and Presenter are completely separated
2. **Easy code maintenance and testing** - The application's model, view, and presenter layers are separated, making it easier to maintain and test
3. **Testability** - Presenter can be tested independently with JUnit (mock View)
4. **Reusability** - Presenter can be reused with different Views
5. **Separation of concerns** - Clear responsibilities for each component

### Недостатки MVP

**Disadvantages of MVP Architecture**:

1. **If the developer does not follow the single responsibility principle** to break the code, then the Presenter layer tends to expand to a huge all-knowing class (God object)
2. **Memory leaks** - If Presenter holds View reference and View is destroyed, can cause memory leaks (need to detach View properly)
3. **Complexity** - For simple screens, MVP might be overkill
4. **Boilerplate** - Requires Contract interfaces and more code compared to simple approaches
5. **Configuration changes** - Presenter is typically recreated on configuration changes, losing state (unless retained)

### MVP vs MVVM vs MVC

| Aspect | MVP | MVVM | MVC |
|--------|-----|------|-----|
| **View-Presenter/ViewModel** | Bidirectional (explicit) | Unidirectional (observable) | Direct coupling |
| **View reference** | Presenter knows View | ViewModel doesn't know View | Controller knows View |
| **View updates** | Explicit interface calls | Automatic (data binding) | Direct calls |
| **Testability** | Good (mock View) | Excellent (no View) | Moderate |
| **Lifecycle** | Manual handling | Automatic (lifecycle-aware) | Manual |
| **Configuration changes** | State lost (unless retained) | State survives | State lost |

### Best Practices

```kotlin
// - DO: Use Contract interface
interface ScreenContract {
    interface View { /* view methods */ }
    interface Presenter { /* presenter methods */ }
}

// - DO: Detach View in onDestroy
override fun onDestroy() {
    super.onDestroy()
    presenter.detachView()
}

// - DO: Null-check before calling View
view?.showData(data)

// - DO: Cancel ongoing operations on detach
override fun detachView() {
    job.cancel()
    view = null
}

// - DON'T: Create God Presenter with too many responsibilities
// Split into multiple Presenters if needed

// - DON'T: Forget to detach View
// This causes memory leaks
```

### When to Use MVP?

**Use MVP when**:
- You need explicit control over View updates
- Working with legacy code that doesn't support ViewModel
- Team is familiar with MVP pattern
- Need to support older Android versions without Jetpack

**Prefer MVVM when**:
- Using modern Android development (Jetpack)
- Want lifecycle-aware components
- Need automatic data binding
- Want to minimize boilerplate

**English**: **MVP (Model-View-Presenter)** is an architectural pattern for facilitating unit testing and separation of concerns. **Components**: (1) Model - business logic and data, (2) View - passive UI that displays data and notifies Presenter of user actions, (3) Presenter - mediates between Model and View, contains presentation logic. **Key feature**: Contract interface defines View-Presenter relationship. **Advantages**: testability (mock View), separation of concerns, no Android dependencies in Presenter. **Disadvantages**: can lead to God Presenter, requires manual lifecycle handling, memory leak risk if View not detached, configuration changes lose state. Contract pattern improves code readability and maintainability.

## Links

- [Model–view–presenter](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93presenter)
- [Android Architecture Patterns Part 2: Model-View-Presenter](https://medium.com/upday-devs/android-architecture-patterns-part-2-model-view-presenter-8a6faaae14a5)
- [MVP (Model View Presenter) Architecture Pattern in Android with Example](https://www.geeksforgeeks.org/mvp-model-view-presenter-architecture-pattern-in-android-with-example/)

## Further Reading

- [Building An Application With MVP](https://androidessence.com/building-an-app-with-mvp)
- [Android MVP Architecture for Beginners](https://androidwave.com/android-mvp-architecture-for-beginners-demo-app/)
- [Model-View-Presenter (MVP) for Android](https://dzone.com/articles/model-view-presenter-for-andriod)

---
*Source: Kirchhoff Android Interview Questions*

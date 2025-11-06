---
id: cs-021
title: "MVVM Pattern / Паттерн MVVM (Model-View-ViewModel)"
aliases: ["MVVM Pattern", "Паттерн MVVM"]
topic: cs
subtopics: [android-architecture, architecture-patterns, data-binding, reactive-programming]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-clean-architecture--architecture-patterns--hard, q-mvi-pattern--architecture-patterns--hard, q-mvp-pattern--architecture-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [android-architecture, data-binding, difficulty/medium, livedata, mvvm, reactive-programming, viewmodel]
sources: [https://developer.android.com/jetpack/guide]
---

# Вопрос (RU)
> Что такое паттерн MVVM? Когда его использовать и как он работает?

# Question (EN)
> What is the MVVM pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория MVVM Pattern:**
MVVM (Model-View-ViewModel) - архитектурный паттерн для separation of development UI от business logic. Решает проблему: View не должен зависеть от specific model platform. Model - abstraction data sources. View observes ViewModel и не содержит application logic. ViewModel - связь между Model и View, exposes observable data streams.

**Определение:**

*Теория:* MVVM - software architecture pattern для separation UI development от business logic development. View независима от model platform. Key characteristic: two-way data binding между View и ViewModel. ViewModel isolates presentation layer и offers methods и commands для managing view state и manipulating model.

```kotlin
// ✅ MVVM Structure
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    fun getUser(userId: Int): User {
        return User(userId, "John Doe", "john@example.com")
    }
}

class UserViewModel : ViewModel() {
    private val repository = UserRepository()
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    fun loadUser(userId: Int) {
        _loading.value = true
        viewModelScope.launch {
            try {
                val userData = repository.getUser(userId)
                _user.value = userData
            } finally {
                _loading.value = false
            }
        }
    }
}

class UserActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this)[UserViewModel::class.java]

        viewModel.user.observe(this) { user ->
            nameTextView.text = user.name
            emailTextView.text = user.email
        }

        viewModel.loadUser(1)
    }
}
```

**Компоненты MVVM:**

**1. Model:**
*Теория:* Model - abstraction data sources. Responsible for: network calls, database operations, business logic, data transformations. Работает с ViewModel для getting и saving data. ViewModel использует Model для data operations.

```kotlin
// ✅ Model - data abstraction
class UserRepository(
    private val apiService: ApiService,
    private val database: UserDatabase
) {
    suspend fun getUser(userId: Int): User {
        // Try cache first
        val cached = database.userDao().getUserById(userId)
        if (cached != null) return cached

        // Fetch from network
        val response = apiService.getUser(userId)
        database.userDao().insert(response)
        return response
    }
}
```

**2. View:**
*Теория:* View - UI layer. Notifies ViewModel о user actions. Observes ViewModel для UI updates. Не содержит application logic. Maintains synchronization с ViewModel через observers. Легкий и focused only на UI.

```kotlin
// ✅ View - observes ViewModel
class ProductListFragment : Fragment() {
    private val viewModel: ProductListViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe state
        viewModel.products.observe(viewLifecycleOwner) { products ->
            adapter.submitList(products)
        }

        viewModel.loading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        // User interactions
        swipeRefreshLayout.setOnRefreshListener {
            viewModel.refresh()
        }
    }
}
```

**3. ViewModel:**
*Теория:* ViewModel exposes observable data streams relevant to View. Serves как link между Model и View. Has no reference к View. Isolates presentation logic. Survives configuration changes. Exposes LiveData/StateFlow для reactive UI updates.

```kotlin
// ✅ ViewModel - presentation logic
class ProductListViewModel(private val repository: ProductRepository) : ViewModel() {
    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    init {
        loadProducts()
    }

    fun loadProducts() {
        _loading.value = true
        viewModelScope.launch {
            try {
                val result = repository.getProducts()
                _products.value = result
            } catch (e: Exception) {
                // Handle error
            } finally {
                _loading.value = false
            }
        }
    }

    fun refresh() {
        loadProducts()
    }
}
```

**Ключевые принципы:**

**1. Two-Way Data Binding:**
*Теория:* View и ViewModel имеют two-way binding. ViewModel properties синхронизированы с View. Changes в View автоматически update ViewModel. Changes в ViewModel автоматически update View. Это обеспечивает synchronization между layers.

```kotlin
// ✅ Data Binding Example (XML)
// activity_user.xml
<layout xmlns:android="...">
    <data>
        <variable name="viewModel" type="com.example.UserViewModel"/>
    </data>

    <EditText
        android:text="@={viewModel.email}"/>  <!-- Two-way binding -->
</layout>
```

**2. Observable Pattern:**
*Теория:* ViewModel exposes observable data (LiveData, StateFlow). View subscribes к these observers. ViewModel не знает о View subscribers. Multiple Views могут subscribe к same ViewModel. Decoupled architecture.

**3. Lifecycle Awareness:**
*Теория:* ViewModel связан с lifecycle owner (Activity, Fragment). Survives configuration changes (screen rotation). Destroyed когда Activity/Fragment permanently destroyed. LiveData aware of lifecycle - автоматически stops observation когда lifecycle owner destroyed.

**4. No View Reference:**
*Теория:* ViewModel не имеет reference к View. ViewModel не может directly update UI. ViewModel только exposes observable state. View самостоятельно подписывается на ViewModel. Это обеспечивает testability и prevents memory leaks.

**Advantages:**

1. **Maintainability** - можно быстро выпускать версии
2. **Extensibility** - можно replace или add new code pieces
3. **Testability** - легче писать unit tests для core logic
4. **Transparent Communication** - ViewModel предоставляет transparent interface
5. **Lifecycle Awareness** - ViewModel survives configuration changes

**Недостатки:**

1. **Overkill для Simple UI** - может быть избыточным
2. **Design Challenges** - сложно design ViewModel для big cases
3. **Debugging Difficulty** - сложно debug complex data bindings
4. **Memory Overhead** - ViewModel держит state, может быть memory issues

**Когда использовать:**

*Теория:* Используйте MVVM когда: современные Android apps following Google recommendations, using Jetpack components, need reactive UI updates, complex state management, need survive configuration changes. Не используйте для: very simple UIs (over-engineering), prototypes.

✅ **Use MVVM when:**
- Modern Android apps
- Using Jetpack components
- Need reactive UI updates
- Complex state management
- Need configuration change survival

❌ **Don't use MVVM when:**
- Very simple UIs (over-engineering)
- Prototypes (unnecessary complexity)

**Android Jetpack Components:**

*Теория:* MVVM в Android использует Jetpack components: ViewModel (lifecycle-aware state), LiveData (lifecycle-aware observable), Data Binding (declarative UI updates), Repository Pattern (data source abstraction).

**Ключевые концепции:**

1. **Two-Way Binding** - View ↔ ViewModel synchronization
2. **Observable Pattern** - View подписывается на ViewModel
3. **Lifecycle Awareness** - ViewModel aware of lifecycle
4. **Separation of Concerns** - clear boundaries
5. **No View Dependency** - ViewModel не зависит от View

## Answer (EN)

**MVVM Pattern Theory:**
MVVM (Model-View-ViewModel) - architecture pattern for separation of UI development from business logic development. Solves problem: View shouldn't depend on specific model platform. Model - abstraction of data sources. View observes ViewModel and doesn't contain application logic. ViewModel - link between Model and View, exposes observable data streams.

**Definition:**

*Theory:* MVVM - software architecture pattern for separation UI development from business logic development. View independent from model platform. Key characteristic: two-way data binding between View and ViewModel. ViewModel isolates presentation layer and offers methods and commands for managing view state and manipulating model.

```kotlin
// ✅ MVVM Structure
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    fun getUser(userId: Int): User {
        return User(userId, "John Doe", "john@example.com")
    }
}

class UserViewModel : ViewModel() {
    private val repository = UserRepository()
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    fun loadUser(userId: Int) {
        _loading.value = true
        viewModelScope.launch {
            try {
                val userData = repository.getUser(userId)
                _user.value = userData
            } finally {
                _loading.value = false
            }
        }
    }
}

class UserActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel = ViewModelProvider(this)[UserViewModel::class.java]

        viewModel.user.observe(this) { user ->
            nameTextView.text = user.name
            emailTextView.text = user.email
        }

        viewModel.loadUser(1)
    }
}
```

**MVVM Components:**

**1. Model:**
*Theory:* Model - abstraction of data sources. Responsible for: network calls, database operations, business logic, data transformations. Works with ViewModel for getting and saving data. ViewModel uses Model for data operations.

```kotlin
// ✅ Model - data abstraction
class UserRepository(
    private val apiService: ApiService,
    private val database: UserDatabase
) {
    suspend fun getUser(userId: Int): User {
        // Try cache first
        val cached = database.userDao().getUserById(userId)
        if (cached != null) return cached

        // Fetch from network
        val response = apiService.getUser(userId)
        database.userDao().insert(response)
        return response
    }
}
```

**2. View:**
*Theory:* View - UI layer. Notifies ViewModel about user actions. Observes ViewModel for UI updates. Doesn't contain application logic. Maintains synchronization with ViewModel through observers. Lightweight and focused only on UI.

```kotlin
// ✅ View - observes ViewModel
class ProductListFragment : Fragment() {
    private val viewModel: ProductListViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe state
        viewModel.products.observe(viewLifecycleOwner) { products ->
            adapter.submitList(products)
        }

        viewModel.loading.observe(viewLifecycleOwner) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        // User interactions
        swipeRefreshLayout.setOnRefreshListener {
            viewModel.refresh()
        }
    }
}
```

**3. ViewModel:**
*Theory:* ViewModel exposes observable data streams relevant to View. Serves as link between Model and View. Has no reference to View. Isolates presentation logic. Survives configuration changes. Exposes LiveData/StateFlow for reactive UI updates.

```kotlin
// ✅ ViewModel - presentation logic
class ProductListViewModel(private val repository: ProductRepository) : ViewModel() {
    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    init {
        loadProducts()
    }

    fun loadProducts() {
        _loading.value = true
        viewModelScope.launch {
            try {
                val result = repository.getProducts()
                _products.value = result
            } catch (e: Exception) {
                // Handle error
            } finally {
                _loading.value = false
            }
        }
    }

    fun refresh() {
        loadProducts()
    }
}
```

**Key Principles:**

**1. Two-Way Data Binding:**
*Theory:* View and ViewModel have two-way binding. ViewModel properties synchronized with View. Changes in View automatically update ViewModel. Changes in ViewModel automatically update View. This ensures synchronization between layers.

```kotlin
// ✅ Data Binding Example (XML)
// activity_user.xml
<layout xmlns:android="...">
    <data>
        <variable name="viewModel" type="com.example.UserViewModel"/>
    </data>

    <EditText
        android:text="@={viewModel.email}"/>  <!-- Two-way binding -->
</layout>
```

**2. Observable Pattern:**
*Theory:* ViewModel exposes observable data (LiveData, StateFlow). View subscribes to these observers. ViewModel doesn't know about View subscribers. Multiple Views can subscribe to same ViewModel. Decoupled architecture.

**3. Lifecycle Awareness:**
*Theory:* ViewModel tied to lifecycle owner (Activity, Fragment). Survives configuration changes (screen rotation). Destroyed when Activity/Fragment permanently destroyed. LiveData aware of lifecycle - automatically stops observation when lifecycle owner destroyed.

**4. No View Reference:**
*Theory:* ViewModel has no reference to View. ViewModel cannot directly update UI. ViewModel only exposes observable state. View subscribes to ViewModel on its own. This ensures testability and prevents memory leaks.

**Advantages:**

1. **Maintainability** - can quickly release versions
2. **Extensibility** - can replace or add new code pieces
3. **Testability** - easier to write unit tests for core logic
4. **Transparent Communication** - ViewModel provides transparent interface
5. **Lifecycle Awareness** - ViewModel survives configuration changes

**Disadvantages:**

1. **Overkill for Simple UI** - may be unnecessary
2. **Design Challenges** - hard to design ViewModel for big cases
3. **Debugging Difficulty** - hard to debug complex data bindings
4. **Memory Overhead** - ViewModel holds state, may be memory issues

**When to Use:**

*Theory:* Use MVVM when: modern Android apps following Google recommendations, using Jetpack components, need reactive UI updates, complex state management, need to survive configuration changes. Don't use for: very simple UIs (over-engineering), prototypes.

✅ **Use MVVM when:**
- Modern Android apps
- Using Jetpack components
- Need reactive UI updates
- Complex state management
- Need configuration change survival

❌ **Don't use MVVM when:**
- Very simple UIs (over-engineering)
- Prototypes (unnecessary complexity)

**Android Jetpack Components:**

*Theory:* MVVM in Android uses Jetpack components: ViewModel (lifecycle-aware state), LiveData (lifecycle-aware observable), Data Binding (declarative UI updates), Repository Pattern (data source abstraction).

**Key Concepts:**

1. **Two-Way Binding** - View ↔ ViewModel synchronization
2. **Observable Pattern** - View subscribes to ViewModel
3. **Lifecycle Awareness** - ViewModel aware of lifecycle
4. **Separation of Concerns** - clear boundaries
5. **No View Dependency** - ViewModel doesn't depend on View

---

## Follow-ups

- What is the difference between LiveData and StateFlow?
- How does ViewModel survive configuration changes?
- When should you use two-way data binding vs one-way?

## Related Questions

### Prerequisites (Easier)
- Basic Android architecture concepts
- Understanding of LiveData and ViewModel

### Related (Same Level)
- [[q-mvp-pattern--architecture-patterns--medium]] - MVP pattern
- [[q-mvi-pattern--architecture-patterns--hard]] - MVI pattern

### Advanced (Harder)
- [[q-clean-architecture--architecture-patterns--hard]] - Clean Architecture
- Advanced MVVM patterns
- StateFlow vs LiveData comparison

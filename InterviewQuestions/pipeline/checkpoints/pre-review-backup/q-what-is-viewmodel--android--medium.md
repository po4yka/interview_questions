---
id: 20251012-122711168
title: "What Is Viewmodel / Что такое ViewModel"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-factory-pattern-android--android--medium, q-view-methods-and-their-purpose--android--medium, q-what-is-the-difference-between-fragmentmanager-and-fragmenttransaction--android--medium]
created: 2025-10-15
tags: [viewmodel, architecture, lifecycle, mvvm, state-management, difficulty/medium]
---
# What is ViewModel?

**Russian**: Что такое ViewModel?

## Answer (EN)
### Definition

The **ViewModel** class is a **business logic or screen level state holder**. It exposes state to the UI and encapsulates related business logic. Its principal advantage is that it **caches state and persists it through configuration changes**. This means that your UI doesn't have to fetch data again when navigating between activities, or following configuration changes, such as when rotating the screen.

### Key Characteristics

A **ViewModel** is always created in association with a **scope** (a fragment or an activity) and will be retained as long as the scope is alive. For example, if it is an Activity, until it is finished.

The purpose of the ViewModel is to **acquire and keep the information** that is necessary for an Activity or a Fragment. The Activity or the Fragment should be able to observe changes in the ViewModel. ViewModels usually expose this information via **LiveData** or **Flow**.

### Important Constraint

**ViewModel's only responsibility is to manage the data for the UI.** It should **never**:
- Access your view hierarchy
- Hold a reference back to the Activity or the Fragment
- Hold references to Context (except ApplicationContext)

### Basic Usage Example

Typical usage from an **Activity** standpoint:

```kotlin
class UserActivity : ComponentActivity() {
    private val viewModel by viewModels<UserViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.user_activity_layout)

        // Observe ViewModel data
        viewModel.user.observe(this) { user: User ->
            // Update UI when data changes
            updateUserInfo(user)
        }

        // Handle user actions
        requireViewById<Button>(R.id.button).setOnClickListener {
            viewModel.doAction()
        }
    }
}
```

ViewModel implementation:

```kotlin
class UserViewModel : ViewModel() {
    private val userLiveData = MutableLiveData<User>()
    val user: LiveData<User> get() = userLiveData

    init {
        // Trigger user load
        loadUser()
    }

    fun doAction() {
        // Depending on the action, do necessary business logic calls
        // and update the userLiveData
        viewModelScope.launch {
            val updatedUser = repository.performAction()
            userLiveData.value = updatedUser
        }
    }

    private fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            userLiveData.value = user
        }
    }
}
```

### Communication Between Fragments

ViewModels can also be used as a **communication layer** between different Fragments of an Activity. Each Fragment can acquire the ViewModel using the same key via their Activity. This allows communication between Fragments in a **de-coupled fashion** such that they never need to talk to the other Fragment directly:

```kotlin
class MyFragment : Fragment() {
    // Shared ViewModel scoped to the Activity
    private val viewModel by activityViewModels<UserViewModel>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Observe shared data
        viewModel.user.observe(viewLifecycleOwner) { user ->
            updateUI(user)
        }
    }
}
```

### Coroutines Support

ViewModel includes support for **Kotlin coroutines**. It is able to persist asynchronous work in the same manner as it persists UI state.

```kotlin
class MyViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadData() {
        viewModelScope.launch {
            try {
                _uiState.value = UiState.Loading
                val data = repository.fetchData()
                _uiState.value = UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }

    // Coroutines in viewModelScope are automatically cancelled
    // when ViewModel is cleared
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String?) : UiState()
}
```

## ViewModel Benefits

The alternative to a ViewModel is a **plain class** that holds the data you display in your UI. This can become a problem when navigating between activities or Navigation destinations. Doing so destroys that data if you don't store it using the saving instance state mechanism. ViewModel provides a convenient API for data persistence that resolves this issue.

### The key benefits of the ViewModel class are essentially two:

**1. It allows you to persist UI state**

Without ViewModel:
```kotlin
class MyActivity : AppCompatActivity() {
    private var data: List<Item>? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Problem: Data lost on configuration change (rotation)
        if (savedInstanceState == null) {
            loadData() // Fetches data again on rotation!
        } else {
            // Must manually save/restore data
            data = savedInstanceState.getParcelableArrayList("data")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Must manually save data
        outState.putParcelableArrayList("data", ArrayList(data ?: emptyList()))
    }
}
```

With ViewModel:
```kotlin
class MyActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ViewModel survives configuration changes automatically!
        viewModel.data.observe(this) { data ->
            updateUI(data)
        }

        // Data is only loaded once
        if (viewModel.data.value == null) {
            viewModel.loadData()
        }
    }
}
```

**2. It provides access to business logic**

```kotlin
class ProductViewModel(
    private val repository: ProductRepository,
    private val analytics: AnalyticsService
) : ViewModel() {

    private val _products = MutableLiveData<List<Product>>()
    val products: LiveData<List<Product>> = _products

    private val _cartCount = MutableLiveData<Int>()
    val cartCount: LiveData<Int> = _cartCount

    // Business logic encapsulated in ViewModel
    fun addToCart(product: Product) {
        viewModelScope.launch {
            repository.addToCart(product)
            _cartCount.value = repository.getCartCount()
            analytics.logEvent("add_to_cart", product.id)
        }
    }

    fun loadProducts() {
        viewModelScope.launch {
            val products = repository.getProducts()
            _products.value = products
        }
    }

    fun applyDiscount(discountCode: String) {
        viewModelScope.launch {
            val isValid = repository.validateDiscount(discountCode)
            if (isValid) {
                val discountedProducts = repository.applyDiscount(discountCode)
                _products.value = discountedProducts
                analytics.logEvent("discount_applied", discountCode)
            }
        }
    }
}
```

## The Lifecycle of a ViewModel

The lifecycle of a ViewModel is tied directly to its **scope**. A ViewModel remains in memory until the **ViewModelStoreOwner** to which it is scoped disappears. This may occur in the following contexts:

- **In the case of an activity**: when it finishes
- **In the case of a fragment**: when it detaches
- **In the case of a Navigation entry**: when it's removed from the back stack

This makes ViewModels a **great solution for storing data that survives configuration changes**.

### ViewModel Lifecycle Diagram

The diagram below illustrates the various lifecycle states of an activity as it undergoes a rotation and then is finished. The illustration also shows the lifetime of the ViewModel next to the associated activity lifecycle.

![ViewModel lifecycle](https://developer.android.com/static/images/topic/libraries/architecture/viewmodel-lifecycle.png)

You usually request a ViewModel the **first time** the system calls an activity object's `onCreate()` method. The system may call `onCreate()` several times throughout the existence of an activity, such as when a device screen is rotated. **The ViewModel exists from when you first request a ViewModel until the activity is finished and destroyed.**

### Lifecycle Example

```kotlin
class MyActivity : AppCompatActivity() {
    private val viewModel by viewModels<MyViewModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Activity", "onCreate called")

        // ViewModel is created on first onCreate call
        // On rotation, the SAME ViewModel instance is returned
        viewModel.data.observe(this) { data ->
            Log.d("Activity", "Data received: $data")
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Activity", "onDestroy called")
        // ViewModel.onCleared() is only called when Activity is finishing
        // NOT called on configuration changes
    }
}

class MyViewModel : ViewModel() {
    init {
        Log.d("ViewModel", "ViewModel created")
    }

    override fun onCleared() {
        super.onCleared()
        Log.d("ViewModel", "ViewModel cleared - cleanup resources")
        // Called when Activity is finishing
        // NOT called on configuration changes
    }
}
```

### Lifecycle Output:

```
// First launch
Activity: onCreate called
ViewModel: ViewModel created
Activity: Data received: [items]

// Screen rotation
Activity: onDestroy called
Activity: onCreate called
Activity: Data received: [items] (same data, no reload!)

// Activity finish
Activity: onDestroy called
ViewModel: ViewModel cleared - cleanup resources
```

## Advanced ViewModel Features

### 1. ViewModel with SavedStateHandle

For process death scenarios (low memory), use **SavedStateHandle**:

```kotlin
class SavedStateViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Survives both configuration changes AND process death
    var userName: String?
        get() = savedStateHandle["user_name"]
        set(value) {
            savedStateHandle["user_name"] = value
        }

    // LiveData backed by SavedStateHandle
    val counter: MutableLiveData<Int> = savedStateHandle.getLiveData("counter", 0)

    fun incrementCounter() {
        counter.value = (counter.value ?: 0) + 1
    }
}
```

### 2. ViewModel Factory

For ViewModels with constructor parameters:

```kotlin
class UserViewModel(
    private val userId: String,
    private val repository: UserRepository
) : ViewModel() {

    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    init {
        loadUser()
    }

    private fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser(userId)
            _user.value = user
        }
    }
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
    private val viewModel by viewModels<UserViewModel> {
        UserViewModelFactory(userId, userRepository)
    }
}
```

### 3. Hilt ViewModel Injection

Modern approach using Hilt:

```kotlin
@HiltViewModel
class ProductsViewModel @Inject constructor(
    private val repository: ProductRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val productId: String? = savedStateHandle["product_id"]

    val products = repository.getProducts()
        .asLiveData()
}

@AndroidEntryPoint
class ProductsActivity : AppCompatActivity() {
    // Hilt automatically provides dependencies
    private val viewModel by viewModels<ProductsViewModel>()
}
```

## Summary

**ViewModel** is an Android Architecture Component that:

1. **Manages UI-related data** in a lifecycle-conscious way
2. **Survives configuration changes** (screen rotation, etc.)
3. **Separates business logic** from UI controllers
4. **Enables communication** between fragments
5. **Supports coroutines** for asynchronous operations
6. **Never holds references** to Views, Activities, or Fragments
7. **Cleared automatically** when associated lifecycle ends

**Key lifecycle points**:
- Created on first `onCreate()` call
- Survives configuration changes (rotation, etc.)
- Same instance returned after configuration change
- Cleared when Activity finishes or Fragment detaches
- `onCleared()` called for cleanup

**Best practices**:
- Use `viewModelScope` for coroutines
- Expose immutable LiveData/StateFlow to UI
- Never pass Context (except ApplicationContext)
- Use SavedStateHandle for process death scenarios
- Use Hilt for dependency injection

## Ответ (Russian)

**ViewModel** — это класс, который является **держателем бизнес-логики или состояния уровня экрана**. Он предоставляет состояние для UI и инкапсулирует связанную бизнес-логику. Его главное преимущество заключается в том, что он **кеширует состояние и сохраняет его при изменениях конфигурации**. Это означает, что ваш UI не должен снова загружать данные при переходах между activities или при изменениях конфигурации, таких как поворот экрана.

### Ключевые характеристики

ViewModel всегда создается в связке с **областью видимости** (fragment или activity) и будет сохраняться до тех пор, пока эта область жива. Например, если это Activity, то до ее завершения.

Назначение ViewModel — **получать и хранить информацию**, необходимую для Activity или Fragment. Activity или Fragment должны иметь возможность наблюдать за изменениями в ViewModel. ViewModels обычно предоставляют эту информацию через **LiveData** или **Flow**.

### Важное ограничение

**Единственная ответственность ViewModel — управление данными для UI.** Она **никогда не должна**:
- Обращаться к иерархии представлений
- Хранить ссылку на Activity или Fragment
- Хранить ссылки на Context (кроме ApplicationContext)

### Преимущества ViewModel

**1. Сохранение состояния UI**
- Переживает изменения конфигурации (поворот экрана)
- Данные не нужно перезагружать при пересоздании Activity

**2. Доступ к бизнес-логике**
- Инкапсулирует бизнес-логику отдельно от UI
- Упрощает тестирование
- Обеспечивает разделение ответственности

### Жизненный цикл ViewModel

Жизненный цикл ViewModel напрямую связан с его **областью видимости**. ViewModel остается в памяти до тех пор, пока **ViewModelStoreOwner**, к которому он привязан, не исчезнет:

- **Activity**: когда она завершается (finish)
- **Fragment**: когда он отсоединяется (detach)
- **Navigation entry**: когда удаляется из back stack

ViewModel создается при первом вызове `onCreate()` и уничтожается только при завершении Activity/Fragment. При изменениях конфигурации (поворот экрана) возвращается **тот же экземпляр** ViewModel.

### Поддержка корутин

ViewModel поддерживает **Kotlin coroutines** через `viewModelScope`. Корутины в этом scope автоматически отменяются при уничтожении ViewModel.

### Резюме

ViewModel — это Android Architecture Component для управления UI-данными с учетом жизненного цикла. Переживает изменения конфигурации, разделяет бизнес-логику от UI, обеспечивает коммуникацию между фрагментами, поддерживает корутины. Никогда не должен хранить ссылки на Views, Activities или Fragments. Автоматически очищается при завершении связанного lifecycle.

---

**Source**: [Kirchhoff Android Interview Questions](https://github.com/Kirchhoff-/Android-Interview-Questions)

## Links

- [ViewModel overview - Android Developers](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [ViewModel - Android API Reference](https://developer.android.com/reference/androidx/lifecycle/ViewModel)

## Further Reading

- [ViewModels: A Simple Example - Medium](https://medium.com/androiddevelopers/viewmodels-a-simple-example-ed5ac416317e)
- [How ViewModels Work on Android - Better Programming](https://betterprogramming.pub/everything-to-understand-about-viewmodel-400e8e637a58)
- [Using ViewModels to Retain State on Android - Nutrient](https://www.nutrient.io/blog/using-viewmodels-to-retain-state-on-android/)
- [View Model Creation in Android - ProAndroidDev](https://proandroiddev.com/view-model-creation-in-android-android-architecture-components-kotlin-ce9f6b93a46b)
- [Dive deep into Android's ViewModel - Medium](https://medium.com/android-news/dive-deep-into-androids-viewmodel-android-architecture-components-e0a7ded26f70)


---

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Medium)
- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel purpose & internals
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - ViewModel state preservation
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - ViewModel vs onSavedInstanceState

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture


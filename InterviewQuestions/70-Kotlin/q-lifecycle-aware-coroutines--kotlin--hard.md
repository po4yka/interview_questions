---
id: kotlin-130
title: "Lifecycle-Aware Coroutines / Корутины с учетом жизненного цикла"
aliases: []

# Classification
topic: kotlin
subtopics: [android, coroutines, lifecycle, lifecyclescope, viewmodelscope]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Created for vault completeness

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutine-cancellation-mechanisms--kotlin--medium, q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium, q-structured-concurrency-kotlin--kotlin--medium, q-testing-viewmodels-coroutines--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [android, coroutines, difficulty/hard, kotlin, lifecycle, lifecyclescope, viewmodelscope]
date created: Sunday, October 12th 2025, 2:12:24 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# Question (EN)
> Explain lifecycle-aware coroutines in Android. How do viewModelScope, lifecycleScope, and repeatOnLifecycle work? What are best practices for handling configuration changes, process death, and memory leaks? Provide comprehensive examples.

# Вопрос (RU)
> Объясните корутины с учетом жизненного цикла в Android. Как работают viewModelScope, lifecycleScope и repeatOnLifecycle? Каковы лучшие практики для обработки изменений конфигурации, process death и утечек памяти? Приведите подробные примеры.

---

## Answer (EN)

Lifecycle-aware coroutines automatically manage coroutine cancellation based on Android lifecycle events, preventing memory leaks and reducing boilerplate code. They integrate Kotlin Coroutines with Android's lifecycle components.

### The Problem Without Lifecycle Awareness

```kotlin
//  BAD: Manual lifecycle management
class OldFragment : Fragment() {
    private var job: Job? = null

    override fun onStart() {
        super.onStart()
        job = GlobalScope.launch {
            // Long-running operation
            loadData()
        }
    }

    override fun onStop() {
        super.onStop()
        job?.cancel()  // Easy to forget!
    }
}

// Problems:
// 1. Easy to forget cancellation
// 2. Boilerplate code
// 3. GlobalScope doesn't respect lifecycle
// 4. Risk of memory leaks
// 5. Crashes if Fragment destroyed during operation
```

### Lifecycle-Aware Coroutine Scopes

Android provides three main coroutine scopes:

| Scope | Lifecycle | Use Case | Cancellation |
|-------|-----------|----------|--------------|
| **viewModelScope** | ViewModel cleared | Repository calls, business logic | When ViewModel cleared |
| **lifecycleScope** | Lifecycle destroyed | UI updates, one-time operations | When lifecycle destroyed |
| **repeatOnLifecycle** | Specific lifecycle state | Flow collection, continuous updates | When leaving state |

### 1. viewModelScope - ViewModel Lifecycle

`viewModelScope` is tied to ViewModel's lifecycle and automatically cancels when ViewModel is cleared.

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _userData = MutableStateFlow<UserData?>(null)
    val userData: StateFlow<UserData?> = _userData.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            try {
                _userData.value = repository.getUser(userId)
            } catch (e: Exception) {
                // Handle error
            }
        }
    }

    // Automatically cancelled when ViewModel cleared
    // No manual cleanup needed!
}
```

**How viewModelScope works**:

```kotlin
// Implementation (simplified)
public val ViewModel.viewModelScope: CoroutineScope
    get() {
        val scope: CoroutineScope? = this.getTag(JOB_KEY)
        if (scope != null) {
            return scope
        }
        return setTagIfAbsent(
            JOB_KEY,
            CloseableCoroutineScope(
                SupervisorJob() + Dispatchers.Main.immediate
            )
        )
    }

internal class CloseableCoroutineScope(
    context: CoroutineContext
) : Closeable, CoroutineScope {
    override val coroutineContext: CoroutineContext = context

    override fun close() {
        coroutineContext.cancel()
    }
}

// Called when ViewModel.onCleared() is invoked
```

#### viewModelScope Best Practices

```kotlin
class ProductViewModel(
    private val repository: ProductRepository
) : ViewModel() {

    //  Good: Use StateFlow for UI state
    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products: StateFlow<List<Product>> = _products.asStateFlow()

    //  Good: Use SharedFlow for one-time events
    private val _events = MutableSharedFlow<ProductEvent>()
    val events: SharedFlow<ProductEvent> = _events.asSharedFlow()

    //  Good: Expose flows directly
    val searchResults: Flow<List<Product>> = repository.searchProducts()
        .flowOn(Dispatchers.IO)

    //  Good: Launch coroutines in viewModelScope
    fun loadProducts() {
        viewModelScope.launch {
            try {
                val result = repository.fetchProducts()
                _products.value = result
            } catch (e: Exception) {
                _events.emit(ProductEvent.Error(e.message))
            }
        }
    }

    //  Good: Use async for parallel operations
    fun loadMultipleCategories() {
        viewModelScope.launch {
            val electronics = async { repository.getCategory("electronics") }
            val books = async { repository.getCategory("books") }
            val clothing = async { repository.getCategory("clothing") }

            val results = awaitAll(electronics, books, clothing)
            processResults(results)
        }
    }

    //  Good: Handle cancellation
    fun searchProducts(query: String) {
        viewModelScope.launch {
            try {
                val results = withContext(Dispatchers.IO) {
                    repository.search(query)
                }
                _products.value = results
            } catch (e: CancellationException) {
                // Don't suppress cancellation
                throw e
            } catch (e: Exception) {
                _events.emit(ProductEvent.Error(e.message))
            }
        }
    }
}
```

#### Configuration Changes with viewModelScope

```kotlin
class WeatherViewModel(
    private val weatherRepository: WeatherRepository
) : ViewModel() {

    private val _weather = MutableStateFlow<WeatherState>(WeatherState.Loading)
    val weather: StateFlow<WeatherState> = _weather.asStateFlow()

    init {
        //  Survives configuration changes
        loadWeather()
    }

    private fun loadWeather() {
        viewModelScope.launch {
            _weather.value = WeatherState.Loading

            try {
                val data = weatherRepository.getCurrentWeather()
                _weather.value = WeatherState.Success(data)
            } catch (e: Exception) {
                _weather.value = WeatherState.Error(e.message ?: "Unknown error")
            }
        }
    }

    fun refresh() {
        loadWeather()  // Can be called again after rotation
    }
}

// Activity/Fragment
class WeatherFragment : Fragment() {
    private val viewModel: WeatherViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  Collects from same ViewModel instance after rotation
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.weather.collect { state ->
                updateUI(state)
            }
        }
    }
}
```

### 2. lifecycleScope - Lifecycle Owner Scope

`lifecycleScope` is tied to a LifecycleOwner (Activity, Fragment, Service) and cancels when lifecycle is destroyed.

```kotlin
class ProfileFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  Cancelled when Fragment destroyed
        viewLifecycleOwner.lifecycleScope.launch {
            // Perform operation
            val userData = loadUserData()
            updateUI(userData)
        }
    }

    //  BAD: Using Fragment's lifecycleScope
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // This survives view destruction!
            // Will cause issues if view is recreated
        }
    }

    //  GOOD: Using viewLifecycleOwner.lifecycleScope
    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.data.collect { data ->
                // Properly cancelled when view destroyed
                updateUI(data)
            }
        }
    }
}
```

#### Fragment Lifecycle Vs View Lifecycle

```kotlin
class ImportantFragment : Fragment() {

    // Fragment's lifecycle scope
    // Survives view recreation (e.g., during configuration change)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            //  Lives as long as Fragment
            // Not cancelled when view destroyed
        }
    }

    // View's lifecycle scope
    // Cancelled and recreated with view
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            //  Cancelled when view destroyed
            // Restarted when view recreated
        }
    }
}

// Rule of thumb:
// - Use viewLifecycleOwner.lifecycleScope for UI-related work
// - Use lifecycleScope only for Fragment-scoped work
```

#### Activity Lifecycle Scope

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        //  Cancelled when Activity destroyed
        lifecycleScope.launch {
            // Safe to update UI
            val data = loadData()
            updateUI(data)
        }
    }

    // Launch at specific lifecycle state
    override fun onStart() {
        super.onStart()

        lifecycleScope.launch {
            // Runs when activity starts
            startLocationUpdates()
        }
    }
}
```

### 3. repeatOnLifecycle - State-Aware Collection

`repeatOnLifecycle` restarts a coroutine when lifecycle reaches a certain state and cancels when leaving that state.

```kotlin
class NewsFragment : Fragment() {

    private val viewModel: NewsViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  BEST PRACTICE: Use repeatOnLifecycle for Flow collection
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // This block runs when STARTED
                // and cancels when STOPPED
                viewModel.newsFlow.collect { news ->
                    updateUI(news)
                }
            }
        }
    }
}
```

**Why repeatOnLifecycle is important**:

```kotlin
//  BAD: Without repeatOnLifecycle
class BadFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.dataFlow.collect { data ->
                updateUI(data)  //  Runs even when app in background!
            }
        }
    }
}

//  GOOD: With repeatOnLifecycle
class GoodFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    updateUI(data)  //  Only runs when visible
                }
            }
        }
    }
}
```

#### Multiple Flows with repeatOnLifecycle

```kotlin
class DashboardFragment : Fragment() {

    private val viewModel: DashboardViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  Collect multiple flows
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // All these collectors start together
                // All cancelled together when STOPPED

                launch {
                    viewModel.userFlow.collect { user ->
                        updateUserInfo(user)
                    }
                }

                launch {
                    viewModel.notificationsFlow.collect { notifications ->
                        updateNotifications(notifications)
                    }
                }

                launch {
                    viewModel.weatherFlow.collect { weather ->
                        updateWeather(weather)
                    }
                }
            }
        }
    }
}
```

#### Extension Function for Convenience

```kotlin
// Common pattern extracted to extension function
inline fun Fragment.collectFlows(
    vararg flows: Flow<*>,
    crossinline action: suspend (Any?) -> Unit
) {
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            flows.forEach { flow ->
                launch {
                    flow.collect { value ->
                        action(value)
                    }
                }
            }
        }
    }
}

// Usage
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch {
                    viewModel.uiState.collect { state ->
                        updateUI(state)
                    }
                }

                launch {
                    viewModel.events.collect { event ->
                        handleEvent(event)
                    }
                }
            }
        }
    }
}
```

### Configuration Changes and Process Death

#### Surviving Configuration Changes

```kotlin
//  ViewModel survives configuration changes
class DataViewModel(
    private val repository: DataRepository
) : ViewModel() {

    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()

    private var loadJob: Job? = null

    fun loadData() {
        // Don't reload if already loading
        if (loadJob?.isActive == true) return

        loadJob = viewModelScope.launch {
            _data.value = repository.fetchData()
        }
    }

    override fun onCleared() {
        super.onCleared()
        println("ViewModel cleared")
    }
}

// Fragment recreated on rotation, but ViewModel persists
class DataFragment : Fragment() {
    private val viewModel: DataViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Load only once, even after rotation
        if (savedInstanceState == null) {
            viewModel.loadData()
        }

        // Always observe
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.data.collect { data ->
                    updateUI(data)
                }
            }
        }
    }
}
```

#### Process Death Recovery

```kotlin
class CheckoutViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val orderRepository: OrderRepository
) : ViewModel() {

    //  Survives process death
    private val cartItems: MutableStateFlow<List<CartItem>> =
        savedStateHandle.getStateFlow("cart_items", emptyList())

    private val _checkoutState = MutableStateFlow<CheckoutState>(CheckoutState.Idle)
    val checkoutState: StateFlow<CheckoutState> = _checkoutState.asStateFlow()

    fun addToCart(item: CartItem) {
        val currentItems = cartItems.value
        val updatedItems = currentItems + item
        savedStateHandle["cart_items"] = updatedItems
        cartItems.value = updatedItems
    }

    fun removeFromCart(itemId: String) {
        val currentItems = cartItems.value
        val updatedItems = currentItems.filter { it.id != itemId }
        savedStateHandle["cart_items"] = updatedItems
        cartItems.value = updatedItems
    }

    fun checkout() {
        viewModelScope.launch {
            _checkoutState.value = CheckoutState.Processing

            try {
                val order = orderRepository.createOrder(cartItems.value)
                _checkoutState.value = CheckoutState.Success(order.id)

                // Clear cart after successful checkout
                savedStateHandle["cart_items"] = emptyList<CartItem>()
                cartItems.value = emptyList()
            } catch (e: Exception) {
                _checkoutState.value = CheckoutState.Error(e.message ?: "Checkout failed")
            }
        }
    }
}

sealed class CheckoutState {
    object Idle : CheckoutState()
    object Processing : CheckoutState()
    data class Success(val orderId: String) : CheckoutState()
    data class Error(val message: String) : CheckoutState()
}
```

### Memory Leak Prevention

#### Common Memory Leak Scenarios

```kotlin
//  BAD: GlobalScope leaks
class LeakyViewModel : ViewModel() {
    fun loadData() {
        GlobalScope.launch {
            // Never cancelled - memory leak!
            val data = repository.fetchData()
        }
    }
}

//  GOOD: viewModelScope
class SafeViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // Automatically cancelled
            val data = repository.fetchData()
        }
    }
}

//  BAD: Reference to Activity/Fragment
class LeakyViewModel(
    private val activity: Activity  //  Holds Activity reference!
) : ViewModel() {
    fun showMessage() {
        viewModelScope.launch {
            delay(5000)
            activity.showToast("Message")  // Activity might be destroyed!
        }
    }
}

//  GOOD: Use events
class SafeViewModel : ViewModel() {
    private val _events = MutableSharedFlow<ViewEvent>()
    val events: SharedFlow<ViewEvent> = _events.asSharedFlow()

    fun showMessage() {
        viewModelScope.launch {
            delay(5000)
            _events.emit(ViewEvent.ShowToast("Message"))
        }
    }
}

//  BAD: Fragment collecting in onCreate
class LeakyFragment : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.dataFlow.collect { data ->
                updateUI(data)  // View might be destroyed!
            }
        }
    }
}

//  GOOD: Fragment collecting with viewLifecycleOwner
class SafeFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    updateUI(data)
                }
            }
        }
    }
}
```

### Advanced Patterns

#### Pattern 1: One-Time Events

```kotlin
class LoginViewModel : ViewModel() {
    private val _navigationEvents = MutableSharedFlow<NavigationEvent>()
    val navigationEvents: SharedFlow<NavigationEvent> = _navigationEvents.asSharedFlow()

    fun login(username: String, password: String) {
        viewModelScope.launch {
            try {
                authRepository.login(username, password)
                _navigationEvents.emit(NavigationEvent.NavigateToHome)
            } catch (e: Exception) {
                _navigationEvents.emit(NavigationEvent.ShowError(e.message))
            }
        }
    }
}

class LoginFragment : Fragment() {
    private val viewModel: LoginViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.navigationEvents.collect { event ->
                    when (event) {
                        is NavigationEvent.NavigateToHome -> navigateToHome()
                        is NavigationEvent.ShowError -> showError(event.message)
                    }
                }
            }
        }
    }
}
```

#### Pattern 2: Retry Logic

```kotlin
class DataViewModel : ViewModel() {
    private val _dataState = MutableStateFlow<DataState>(DataState.Loading)
    val dataState: StateFlow<DataState> = _dataState.asStateFlow()

    private var retryCount = 0
    private val maxRetries = 3

    fun loadData() {
        viewModelScope.launch {
            _dataState.value = DataState.Loading

            try {
                val data = retry(maxRetries) {
                    repository.fetchData()
                }
                _dataState.value = DataState.Success(data)
                retryCount = 0
            } catch (e: Exception) {
                _dataState.value = DataState.Error(e.message ?: "Unknown error")
            }
        }
    }

    private suspend fun <T> retry(
        times: Int,
        initialDelay: Long = 1000,
        factor: Double = 2.0,
        block: suspend () -> T
    ): T {
        var currentDelay = initialDelay
        repeat(times - 1) {
            try {
                return block()
            } catch (e: Exception) {
                delay(currentDelay)
                currentDelay = (currentDelay * factor).toLong()
            }
        }
        return block()  // Last attempt
    }

    fun retry() {
        if (retryCount < maxRetries) {
            retryCount++
            loadData()
        }
    }
}
```

#### Pattern 3: Polling

```kotlin
class RealTimeDataViewModel : ViewModel() {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()

    private var pollingJob: Job? = null

    fun startPolling(intervalMs: Long = 5000) {
        pollingJob?.cancel()
        pollingJob = viewModelScope.launch {
            while (isActive) {
                try {
                    _data.value = repository.fetchLatestData()
                } catch (e: Exception) {
                    // Handle error
                }
                delay(intervalMs)
            }
        }
    }

    fun stopPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }

    override fun onCleared() {
        super.onCleared()
        stopPolling()
    }
}

// Fragment controls polling based on visibility
class DataFragment : Fragment() {
    private val viewModel: RealTimeDataViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.startPolling()
                try {
                    viewModel.data.collect { data ->
                        updateUI(data)
                    }
                } finally {
                    viewModel.stopPolling()
                }
            }
        }
    }
}
```

### Testing Lifecycle-Aware Coroutines

```kotlin
class UserViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @OptIn(ExperimentalCoroutinesApi::class)
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: UserViewModel
    private lateinit var repository: FakeUserRepository

    @Before
    fun setup() {
        repository = FakeUserRepository()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser emits success state`() = runTest {
        // Arrange
        val userId = "123"
        val expectedUser = User(userId, "John Doe")
        repository.setUser(expectedUser)

        // Act
        viewModel.loadUser(userId)

        // Assert
        advanceUntilIdle()
        assertEquals(expectedUser, viewModel.userData.value)
    }

    @Test
    fun `loadUser handles error`() = runTest {
        // Arrange
        val userId = "123"
        repository.setShouldThrowError(true)

        // Act
        viewModel.loadUser(userId)

        // Assert
        advanceUntilIdle()
        assertTrue(viewModel.error.value != null)
    }
}

// Test dispatcher rule
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Best Practices Summary

1. **Use viewModelScope for business logic**
```kotlin
//  Repository calls
viewModelScope.launch {
    val data = repository.fetchData()
}
```

2. **Use viewLifecycleOwner.lifecycleScope in Fragments**
```kotlin
//  For UI updates
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.data.collect { updateUI(it) }
}
```

3. **Use repeatOnLifecycle for Flow collection**
```kotlin
//  Start/stop based on lifecycle
viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
    flow.collect { }
}
```

4. **Never use GlobalScope**
```kotlin
//  Memory leak
GlobalScope.launch { }

//  Proper scope
viewModelScope.launch { }
```

5. **Handle configuration changes with ViewModel**
```kotlin
//  Survives rotation
class MyViewModel : ViewModel() {
    val data = repository.getData()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
}
```

6. **Save important state**
```kotlin
//  Survives process death
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    val data: StateFlow<Data> = savedStateHandle.getStateFlow("key", initialValue)
}
```

---

## Ответ (RU)

Корутины с учетом жизненного цикла автоматически управляют отменой корутин на основе событий жизненного цикла Android, предотвращая утечки памяти и уменьшая шаблонный код.

### Проблема Без Учета Жизненного Цикла

```kotlin
//  ПЛОХО: Ручное управление жизненным циклом
class OldFragment : Fragment() {
    private var job: Job? = null

    override fun onStart() {
        super.onStart()
        job = GlobalScope.launch {
            loadData()
        }
    }

    override fun onStop() {
        super.onStop()
        job?.cancel()  // Легко забыть!
    }
}

// Проблемы:
// 1. Легко забыть отмену
// 2. Шаблонный код
// 3. GlobalScope не учитывает жизненный цикл
// 4. Риск утечек памяти
```

### Области Видимости Корутин С Учетом Жизненного Цикла

Android предоставляет три основные области видимости:

| Область | Жизненный цикл | Применение | Отмена |
|---------|----------------|------------|--------|
| **viewModelScope** | ViewModel очищена | Вызовы репозитория, бизнес-логика | Когда ViewModel очищена |
| **lifecycleScope** | Lifecycle уничтожен | Обновления UI, одноразовые операции | Когда lifecycle уничтожен |
| **repeatOnLifecycle** | Конкретное состояние | Сбор Flow, непрерывные обновления | При выходе из состояния |

### 1. viewModelScope - Жизненный Цикл ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _userData = MutableStateFlow<UserData?>(null)
    val userData: StateFlow<UserData?> = _userData.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            try {
                _userData.value = repository.getUser(userId)
            } catch (e: Exception) {
                // Обработка ошибки
            }
        }
    }

    // Автоматически отменяется когда ViewModel очищена
    // Ручная очистка не нужна!
}
```

#### Лучшие Практики viewModelScope

```kotlin
class ProductViewModel(
    private val repository: ProductRepository
) : ViewModel() {

    //  Хорошо: Использовать StateFlow для состояния UI
    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products: StateFlow<List<Product>> = _products.asStateFlow()

    //  Хорошо: Использовать SharedFlow для одноразовых событий
    private val _events = MutableSharedFlow<ProductEvent>()
    val events: SharedFlow<ProductEvent> = _events.asSharedFlow()

    //  Хорошо: Запускать корутины в viewModelScope
    fun loadProducts() {
        viewModelScope.launch {
            try {
                val result = repository.fetchProducts()
                _products.value = result
            } catch (e: Exception) {
                _events.emit(ProductEvent.Error(e.message))
            }
        }
    }
}
```

### 2. lifecycleScope - Область Владельца Жизненного Цикла

```kotlin
class ProfileFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  Отменяется когда Fragment уничтожен
        viewLifecycleOwner.lifecycleScope.launch {
            val userData = loadUserData()
            updateUI(userData)
        }
    }

    //  ПЛОХО: Использование lifecycleScope Fragment
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Это переживает уничтожение view!
        }
    }
}
```

### 3. repeatOnLifecycle - Сбор С Учетом Состояния

```kotlin
class NewsFragment : Fragment() {

    private val viewModel: NewsViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  ЛУЧШАЯ ПРАКТИКА: Использовать repeatOnLifecycle для сбора Flow
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Этот блок выполняется когда STARTED
                // и отменяется когда STOPPED
                viewModel.newsFlow.collect { news ->
                    updateUI(news)
                }
            }
        }
    }
}
```

**Почему repeatOnLifecycle важен**:

```kotlin
//  ПЛОХО: Без repeatOnLifecycle
class BadFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.dataFlow.collect { data ->
                updateUI(data)  //  Выполняется даже когда приложение в фоне!
            }
        }
    }
}

//  ХОРОШО: С repeatOnLifecycle
class GoodFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    updateUI(data)  //  Выполняется только когда видимо
                }
            }
        }
    }
}
```

### Изменения Конфигурации И Process Death

#### Переживание Изменений Конфигурации

```kotlin
//  ViewModel переживает изменения конфигурации
class DataViewModel(
    private val repository: DataRepository
) : ViewModel() {

    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()

    fun loadData() {
        viewModelScope.launch {
            _data.value = repository.fetchData()
        }
    }
}

// Fragment пересоздается при вращении, но ViewModel сохраняется
class DataFragment : Fragment() {
    private val viewModel: DataViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Загрузить только один раз, даже после вращения
        if (savedInstanceState == null) {
            viewModel.loadData()
        }

        // Всегда наблюдать
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.data.collect { data ->
                    updateUI(data)
                }
            }
        }
    }
}
```

#### Восстановление После Process Death

```kotlin
class CheckoutViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val orderRepository: OrderRepository
) : ViewModel() {

    //  Переживает process death
    private val cartItems: MutableStateFlow<List<CartItem>> =
        savedStateHandle.getStateFlow("cart_items", emptyList())

    fun addToCart(item: CartItem) {
        val currentItems = cartItems.value
        val updatedItems = currentItems + item
        savedStateHandle["cart_items"] = updatedItems
        cartItems.value = updatedItems
    }
}
```

### Предотвращение Утечек Памяти

```kotlin
//  ПЛОХО: GlobalScope создает утечки
class LeakyViewModel : ViewModel() {
    fun loadData() {
        GlobalScope.launch {
            // Никогда не отменяется - утечка памяти!
            val data = repository.fetchData()
        }
    }
}

//  ХОРОШО: viewModelScope
class SafeViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // Автоматически отменяется
            val data = repository.fetchData()
        }
    }
}
```

### Лучшие Практики

1. **Используйте viewModelScope для бизнес-логики**
2. **Используйте viewLifecycleOwner.lifecycleScope во Fragments**
3. **Используйте repeatOnLifecycle для сбора Flow**
4. **Никогда не используйте GlobalScope**
5. **Обрабатывайте изменения конфигурации с ViewModel**
6. **Сохраняйте важное состояние**

---

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-coroutines-lifecycle--kotlin--medium]] - Coroutines
- [[q-room-coroutines-flow--kotlin--medium]] - Coroutines
- [[q-coroutine-job-lifecycle--kotlin--medium]] - Coroutines
### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

### Related (Hard)
- [[q-coroutine-context-detailed--kotlin--hard]] - Deep dive into CoroutineContext
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced patterns
- [[q-coroutine-performance-optimization--kotlin--hard]] - Performance optimization
- [[q-coroutine-profiling--kotlin--hard]] - Profiling and debugging

## References
- [Lifecycle-aware coroutines](https://developer.android.com/topic/libraries/architecture/coroutines)
- [viewModelScope](https://developer.android.com/topic/libraries/architecture/viewmodel#coroutines)
- [lifecycleScope](https://developer.android.com/topic/libraries/architecture/coroutines#lifecycle-aware)
- [repeatOnLifecycle](https://developer.android.com/topic/libraries/architecture/coroutines#repeatonlifecycle)

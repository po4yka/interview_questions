---
anki_cards:
- slug: q-lifecycle-aware-coroutines--kotlin--hard-0-en
  language: en
  anki_id: 1768326294881
  synced_at: '2026-01-23T17:03:51.655158'
- slug: q-lifecycle-aware-coroutines--kotlin--hard-0-ru
  language: ru
  anki_id: 1768326294906
  synced_at: '2026-01-23T17:03:51.655959'
---
# Question (EN)
> Explain lifecycle-aware coroutines in Android. How do viewModelScope, lifecycleScope, and repeatOnLifecycle work? What are best practices for handling configuration changes, process death, and memory leaks? Provide comprehensive examples.

## Ответ (RU)

Корутины с учетом жизненного цикла автоматически управляют отменой корутин на основе событий жизненного цикла Android, предотвращая утечки памяти и уменьшая шаблонный код. Они интегрируют Kotlin Coroutines с компонентами жизненного цикла (`Lifecycle`, `ViewModel`, `SavedStateHandle` и т.п.). См. также [[c-kotlin]] и [[c-coroutines]].

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
// 3. GlobalScope живет дольше UI и не учитывает жизненный цикл экрана
// 4. Риск утечек памяти и обращений к уничтоженным вью
```

### Области Видимости Корутины С Учетом Жизненного Цикла

Android предоставляет основные возможности для привязки корутин к жизненному циклу:

| Механизм | Привязка | Применение | Отмена |
|----------|----------|------------|--------|
| **viewModelScope** | К жизненному циклу `ViewModel` | Вызовы репозитория, бизнес-логика | При `onCleared()` `ViewModel` |
| **lifecycleScope** | К `LifecycleOwner` (`Activity`/`Fragment` и т.п.) | UI-обновления, одноразовые операции в рамках владельца | При уничтожении `LifecycleOwner` |
| **repeatOnLifecycle** | К конкретному состоянию `Lifecycle` | Безопасный сбор `Flow`/подписок в нужных состояниях | Блок и вложенные корутины отменяются при выходе из состояния |

`repeatOnLifecycle` — это не отдельная область видимости, а suspending-функция, которая запускает и отменяет вложенные корутины в зависимости от состояния жизненного цикла.

### 1. viewModelScope - Жизненный Цикл `ViewModel`

`viewModelScope` привязан к жизненному циклу `ViewModel` и автоматически отменяет корутины при вызове `onCleared()`.

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

    // Корутины автоматически отменяются, когда `ViewModel` очищена (onCleared)
}
```

(Реализация `viewModelScope` в `lifecycle-viewmodel-ktx` основана на `SupervisorJob` + `Dispatchers.Main.immediate`, привязанных к `onCleared()`.)

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

    //  Хорошо: Экспонировать `Flow` напрямую с нужным контекстом
    val searchResults: Flow<List<Product>> = repository.searchProducts()
        .flowOn(Dispatchers.IO)

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

    //  Хорошо: Параллельная загрузка через async
    fun loadMultipleCategories() {
        viewModelScope.launch {
            val electronics = async { repository.getCategory("electronics") }
            val books = async { repository.getCategory("books") }
            val clothing = async { repository.getCategory("clothing") }

            val results = awaitAll(electronics, books, clothing)
            processResults(results)
        }
    }

    //  Хорошо: Явная обработка отмены
    fun searchProducts(query: String) {
        viewModelScope.launch {
            try {
                val results = withContext(Dispatchers.IO) {
                    repository.search(query)
                }
                _products.value = results
            } catch (e: CancellationException) {
                throw e  // Не глотать отмену
            } catch (e: Exception) {
                _events.emit(ProductEvent.Error(e.message))
            }
        }
    }
}
```

#### Изменения Конфигурации С viewModelScope

```kotlin
class WeatherViewModel(
    private val weatherRepository: WeatherRepository
) : ViewModel() {

    private val _weather = MutableStateFlow<WeatherState>(WeatherState.Loading)
    val weather: StateFlow<WeatherState> = _weather.asStateFlow()

    init {
        //  Переживает изменения конфигурации: `ViewModel` сохраняется
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
        loadWeather()
    }
}

class WeatherFragment : Fragment() {
    private val viewModel: WeatherViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  Сбор из того же экземпляра `ViewModel` после поворота экрана
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.weather.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

### 2. lifecycleScope - Область Владельца Жизненного Цикла

`lifecycleScope` привязан к `LifecycleOwner` (`Activity`, `Fragment` и т.п.) и отменяется при уничтожении владельца.

```kotlin
class ProfileFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  Используем область жизненного цикла view; корутина отменяется при уничтожении viewLifecycleOwner
        viewLifecycleOwner.lifecycleScope.launch {
            val userData = loadUserData()
            updateUI(userData)
        }
    }

    //  ПЛОХО: Использование lifecycleScope Fragment для работы с вью
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Эта корутина переживает уничтожение view и может обратиться к уничтоженной view
        }
    }

    //  ХОРОШО: Использовать viewLifecycleOwner.lifecycleScope для UI-наблюдателей
    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.data.collect { data ->
                    updateUI(data)
                }
            }
        }
    }
}
```

#### Жизненный Цикл `Fragment` Vs Жизненный Цикл `View`

```kotlin
class ImportantFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            //  Живет пока существует экземпляр `Fragment`
            // Не отменяется при пересоздании view
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            //  Отменяется при уничтожении view
            // Может быть пересоздан при создании новой view
        }
    }
}

// Правило:
// - Для работы с UI всегда использовать viewLifecycleOwner.lifecycleScope
// - lifecycleScope использовать только для задач, связанных с `Fragment`, но не с его view
```

#### Область Жизненного Цикла `Activity`

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val data = loadData()
            updateUI(data)
        }
    }

    override fun onStart() {
        super.onStart()

        lifecycleScope.launch {
            // Выполняется, пока `Activity` не будет уничтожена; отменяется в onDestroy
            startLocationUpdates()
        }
    }
}
```

### 3. repeatOnLifecycle - Сбор С Учетом Состояния

`repeatOnLifecycle` перезапускает код при достижении заданного состояния жизненного цикла и отменяет его при выходе из этого состояния. Вызывается внутри корутины (например, в `lifecycleScope`).

```kotlin
class NewsFragment : Fragment() {

    private val viewModel: NewsViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  ЛУЧШАЯ ПРАКТИКА: Использовать repeatOnLifecycle для сбора `Flow`
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Этот блок выполняется когда lifecycle в состоянии STARTED+
                // и отменяется когда становится ниже STARTED (например, STOPPED)
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
                updateUI(data)  //  Может продолжать работу, когда `Fragment` не в STARTED/RESUMED
            }
        }
    }
}

//  ХОРОШО: С repeatOnLifecycle
class GoodFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    updateUI(data)  //  Выполняется только когда UI активен (STARTED+)
                }
            }
        }
    }
}
```

#### Несколько `Flow` С repeatOnLifecycle

```kotlin
class DashboardFragment : Fragment() {

    private val viewModel: DashboardViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Все сборщики запускаются и отменяются вместе

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

### Изменения Конфигурации И Process Death

#### Переживание Изменений Конфигурации

```kotlin
//  `ViewModel` переживает изменения конфигурации
class DataViewModel(
    private val repository: DataRepository
) : ViewModel() {

    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()

    private var loadJob: Job? = null

    fun loadData() {
        // Не запускаем повторную загрузку, если уже загружаем
        if (loadJob?.isActive == true) return

        loadJob = viewModelScope.launch {
            _data.value = repository.fetchData()
        }
    }
}

// `Fragment` пересоздается при вращении, но `ViewModel` сохраняется
class DataFragment : Fragment() {
    private val viewModel: DataViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        if (savedInstanceState == null) {
            // Первая загрузка; при последующих пересозданиях UI
            // использует уже имеющиеся данные во `ViewModel`
            viewModel.loadData()
        }

        // Наблюдение за данными с учетом жизненного цикла view
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
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

    //  Значения сохраняются/восстанавливаются через SavedStateHandle при пересоздании процесса
    private val cartItems: StateFlow<List<CartItem>> =
        savedStateHandle.getStateFlow("cart_items", emptyList())

    private val _checkoutState = MutableStateFlow<CheckoutState>(CheckoutState.Idle)
    val checkoutState: StateFlow<CheckoutState> = _checkoutState.asStateFlow()

    fun addToCart(item: CartItem) {
        val updatedItems = cartItems.value + item
        savedStateHandle["cart_items"] = updatedItems
    }

    fun removeFromCart(itemId: String) {
        val updatedItems = cartItems.value.filter { it.id != itemId }
        savedStateHandle["cart_items"] = updatedItems
    }

    fun checkout() {
        viewModelScope.launch {
            _checkoutState.value = CheckoutState.Processing

            try {
                val order = orderRepository.createOrder(cartItems.value)
                _checkoutState.value = CheckoutState.Success(order.id)

                // Очистка корзины после успешной покупки
                savedStateHandle["cart_items"] = emptyList<CartItem>()
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

### Предотвращение Утечек Памяти

#### Типичные Сценарии Утечек

```kotlin
//  ПЛОХО: GlobalScope для UI-работы (живет все время жизни процесса)
class LeakyViewModel : ViewModel() {
    fun loadData() {
        GlobalScope.launch {
            val data = repository.fetchData()
            // Может пережить `ViewModel`/UI и привести к утечкам
        }
    }
}

//  ХОРОШО: viewModelScope
class SafeViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
        }
    }
}

//  ПЛОХО: Хранение ссылки на `Activity`/`Fragment` во `ViewModel`
class LeakyViewModelWithRef(
    private val activity: Activity  //  Держит `Activity`
) : ViewModel() {
    fun showMessage() {
        viewModelScope.launch {
            delay(5000)
            activity.showToast("Message")  // `Activity` может быть уничтожена
        }
    }
}

//  ХОРОШО: Использовать события вместо прямых ссылок
class SafeEventsViewModel : ViewModel() {
    private val _events = MutableSharedFlow<ViewEvent>()
    val events: SharedFlow<ViewEvent> = _events.asSharedFlow()

    fun showMessage() {
        viewModelScope.launch {
            delay(5000)
            _events.emit(ViewEvent.ShowToast("Message"))
        }
    }
}

//  ПЛОХО: `Fragment` собирает `Flow` в onCreate с lifecycleScope и трогает view
class LeakyFragment : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.dataFlow.collect { data ->
                updateUI(data)  // View может быть уже уничтожена
            }
        }
    }
}

//  ХОРОШО: Использовать viewLifecycleOwner + repeatOnLifecycle
class SafeFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    updateUI(data)
                }
            }
        }
    }
}
```

### Продвинутые Паттерны

#### Паттерн 1: Одноразовые События

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
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
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

#### Паттерн 2: Повтор С Ретраями

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
        return block()  // Последняя попытка
    }

    fun retry() {
        if (retryCount < maxRetries) {
            retryCount++
            loadData()
        }
    }
}
```

#### Паттерн 3: Поллинг

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
                    // Обработка ошибок
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

// `Fragment` управляет поллингом на основе видимости
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

### Тестирование Корутины С Учетом Жизненного Цикла

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
        // Проверить механизм обработки ошибок (state/events)
    }
}

// Правило для тестового диспетчера
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

### Резюме Лучших Практик

1. Используйте `viewModelScope` для бизнес-логики и загрузки данных.
```kotlin
viewModelScope.launch {
    val data = repository.fetchData()
}
```

2. Во `Fragment` используйте `viewLifecycleOwner.lifecycleScope` для UI.
```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { updateUI(it) }
    }
}
```

3. Используйте `repeatOnLifecycle` для сбора `Flow`.
```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
        flow.collect { /* handle */ }
    }
}
```

4. Не используйте `GlobalScope` для задач, связанных с UI; полагайтесь на структурированную конкуррентность.
```kotlin
viewModelScope.launch { }
```

5. Обрабатывайте изменения конфигурации через `ViewModel`.
```kotlin
class MyViewModel : ViewModel() {
    val data = repository.getData()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
}
```

6. Сохраняйте важное состояние для process death, например через `SavedStateHandle`.
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    val data: StateFlow<Data> = savedStateHandle.getStateFlow("key", initialValue)
}
```

---

## Answer (EN)

`Lifecycle`-aware coroutines automatically manage coroutine cancellation based on Android lifecycle events, preventing memory leaks and reducing boilerplate. They integrate Kotlin Coroutines with Android lifecycle components such as `ViewModel`, `LifecycleOwner`, and `SavedStateHandle`.

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
// 3. GlobalScope outlives the screen and doesn't respect its lifecycle
// 4. Risk of memory leaks and updates to destroyed views
```

### Lifecycle-Aware Coroutine Scopes and Helpers

Android provides core mechanisms to bind coroutines to lifecycle:

| Mechanism | `Lifecycle` Binding | Use Case | Cancellation |
|----------|-------------------|----------|--------------|
| **viewModelScope** | `ViewModel` lifecycle | Repository calls, business logic | When `ViewModel.onCleared()` is called |
| **lifecycleScope** | `LifecycleOwner` (`Activity`/`Fragment`/`Service`) | UI updates, one-off work tied to owner | When `LifecycleOwner` is destroyed |
| **repeatOnLifecycle** | Specific `Lifecycle` state | Safe `Flow` collection / subscriptions | Block and child coroutines cancelled when leaving the state |

Note: `repeatOnLifecycle` is a suspending function, not a separate scope. It launches and cancels child coroutines according to the `Lifecycle` state.

### 1. viewModelScope - `ViewModel` Lifecycle

`viewModelScope` is tied to `ViewModel`'s lifecycle and automatically cancels when `ViewModel` is cleared.

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

    // Automatically cancelled when `ViewModel` cleared
}
```

(Implementation details of `viewModelScope` are provided by `lifecycle-viewmodel-ktx` and are based on a `SupervisorJob` + `Dispatchers.Main.immediate` attached to `onCleared`.)

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

    //  Good: Handle cancellation correctly
    fun searchProducts(query: String) {
        viewModelScope.launch {
            try {
                val results = withContext(Dispatchers.IO) {
                    repository.search(query)
                }
                _products.value = results
            } catch (e: CancellationException) {
                throw e  // Don't swallow cancellations
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
        //  Survives configuration changes: `ViewModel` is retained
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
        loadWeather()
    }
}

class WeatherFragment : Fragment() {
    private val viewModel: WeatherViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  Collects from the same `ViewModel` instance after rotation
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.weather.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

### 2. lifecycleScope - Lifecycle Owner Scope

`lifecycleScope` is tied to a `LifecycleOwner` (`Activity`, `Fragment`, etc.) and cancels when that owner is destroyed.

```kotlin
class ProfileFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  Using the view's lifecycle scope; cancelled when viewLifecycleOwner is destroyed
        viewLifecycleOwner.lifecycleScope.launch {
            val userData = loadUserData()
            updateUI(userData)
        }
    }

    //  BAD: Using Fragment's lifecycleScope for view-related work
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // This survives view destruction and may touch a destroyed view
        }
    }

    //  GOOD: Using viewLifecycleOwner.lifecycleScope for UI observers
    private fun setupObservers() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.data.collect { data ->
                    updateUI(data)
                }
            }
        }
    }
}
```

#### Fragment Lifecycle Vs `View` Lifecycle

```kotlin
class ImportantFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            //  Lives as long as the Fragment instance
            // Not cancelled when the view is destroyed/recreated
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            //  Cancelled when the view is destroyed
            // Can be recreated when the view is recreated
        }
    }
}

// Rule of thumb:
// - Use viewLifecycleOwner.lifecycleScope for UI-related work
// - Use lifecycleScope only for Fragment-scoped work not tied to the view
```

#### `Activity` Lifecycle Scope

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val data = loadData()
            updateUI(data)
        }
    }

    override fun onStart() {
        super.onStart()

        lifecycleScope.launch {
            // Runs until the Activity is destroyed; cancelled in onDestroy
            startLocationUpdates()
        }
    }
}
```

### 3. repeatOnLifecycle - State-Aware Collection

`repeatOnLifecycle` restarts code when lifecycle reaches a certain state and cancels it when leaving that state. It should be called from a coroutine (e.g., launched in `lifecycleScope`).

```kotlin
class NewsFragment : Fragment() {

    private val viewModel: NewsViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        //  BEST PRACTICE: Use repeatOnLifecycle for `Flow` collection
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // This block runs when in STARTED+ and is cancelled below STARTED
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
                updateUI(data)  //  May run even when not visible or in background
            }
        }
    }
}

//  GOOD: With repeatOnLifecycle
class GoodFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    updateUI(data)  //  Only runs when in STARTED+ state
                }
            }
        }
    }
}
```

#### Multiple `Flow`s with repeatOnLifecycle

```kotlin
class DashboardFragment : Fragment() {

    private val viewModel: DashboardViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // All these collectors start together and are cancelled together

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

### Configuration Changes and Process Death

#### Surviving Configuration Changes

```kotlin
//  `ViewModel` survives configuration changes
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
}

// Fragment recreated on rotation, but `ViewModel` persists
class DataFragment : Fragment() {
    private val viewModel: DataViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        if (savedInstanceState == null) {
            // Initial load; subsequent recreations reuse `ViewModel`'s existing data
            viewModel.loadData()
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
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

    //  Values are saved/restored via SavedStateHandle across process recreation
    private val cartItems: StateFlow<List<CartItem>> =
        savedStateHandle.getStateFlow("cart_items", emptyList())

    private val _checkoutState = MutableStateFlow<CheckoutState>(CheckoutState.Idle)
    val checkoutState: StateFlow<CheckoutState> = _checkoutState.asStateFlow()

    fun addToCart(item: CartItem) {
        val updatedItems = cartItems.value + item
        savedStateHandle["cart_items"] = updatedItems
    }

    fun removeFromCart(itemId: String) {
        val updatedItems = cartItems.value.filter { it.id != itemId }
        savedStateHandle["cart_items"] = updatedItems
    }

    fun checkout() {
        viewModelScope.launch {
            _checkoutState.value = CheckoutState.Processing

            try {
                val order = orderRepository.createOrder(cartItems.value)
                _checkoutState.value = CheckoutState.Success(order.id)

                // Clear cart after successful checkout
                savedStateHandle["cart_items"] = emptyList<CartItem>()
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
//  BAD: GlobalScope for UI work (lives for process lifetime unless cancelled)
class LeakyViewModel : ViewModel() {
    fun loadData() {
        GlobalScope.launch {
            val data = repository.fetchData()
            // May outlive `ViewModel`/UI and leak
        }
    }
}

//  GOOD: viewModelScope
class SafeViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
        }
    }
}

//  BAD: Holding `Activity`/`Fragment` reference in `ViewModel`
class LeakyViewModelWithRef(
    private val activity: Activity  //  Holds `Activity` reference
) : ViewModel() {
    fun showMessage() {
        viewModelScope.launch {
            delay(5000)
            activity.showToast("Message")  // Activity might be destroyed
        }
    }
}

//  GOOD: Use events instead of direct references
class SafeEventsViewModel : ViewModel() {
    private val _events = MutableSharedFlow<ViewEvent>()
    val events: SharedFlow<ViewEvent> = _events.asSharedFlow()

    fun showMessage() {
        viewModelScope.launch {
            delay(5000)
            _events.emit(ViewEvent.ShowToast("Message"))
        }
    }
}

//  BAD: Fragment collecting in onCreate with lifecycleScope and touching views
class LeakyFragment : Fragment() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            viewModel.dataFlow.collect { data ->
                updateUI(data)  // View might be destroyed
            }
        }
    }
}

//  GOOD: Fragment collecting with viewLifecycleOwner + repeatOnLifecycle
class SafeFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
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
            viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
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
        // Assert your error handling mechanism here (e.g., events or state)
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

1. **Use viewModelScope for business logic and data loading**
```kotlin
viewModelScope.launch {
    val data = repository.fetchData()
}
```

2. **Use viewLifecycleOwner.lifecycleScope in Fragments for UI**
```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { updateUI(it) }
    }
}
```

3. **Use repeatOnLifecycle for `Flow` collection**
```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.lifecycle.repeatOnLifecycle(Lifecycle.State.STARTED) {
        flow.collect { /* handle */ }
    }
}
```

4. **Avoid GlobalScope for UI-related work**
```kotlin
//  Prefer structured scopes
viewModelScope.launch { }
```

5. **Handle configuration changes with `ViewModel`**
```kotlin
class MyViewModel : ViewModel() {
    val data = repository.getData()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
}
```

6. **Persist important state for process death (e.g., SavedStateHandle)**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    val data: StateFlow<Data> = savedStateHandle.getStateFlow("key", initialValue)
}
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Lifecycle-aware coroutines](https://developer.android.com/topic/libraries/architecture/coroutines)
- [viewModelScope](https://developer.android.com/topic/libraries/architecture/viewmodel#coroutines)
- [lifecycleScope](https://developer.android.com/topic/libraries/architecture/coroutines#lifecycle-aware)
- [repeatOnLifecycle](https://developer.android.com/topic/libraries/architecture/coroutines#repeatonlifecycle)

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

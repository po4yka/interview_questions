---
id: 20251012-154379
title: "Lifecycle Scopes Viewmodelscope Lifecyclescope / Скоупы жизненного цикла ViewModelScope и LifecycleScope"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - kotlin
  - coroutines
  - lifecycle
  - viewmodelscope
  - lifecyclescope
  - android
---
# viewModelScope vs lifecycleScope

# Question (EN)
> What's the difference between viewModelScope and lifecycleScope? When should you use each?

# Вопрос (RU)
> В чём разница между viewModelScope и lifecycleScope? Когда использовать каждый из них?

---

## Answer (EN)

**viewModelScope** and **lifecycleScope** are lifecycle-aware coroutine scopes that auto-cancel coroutines when their owner is destroyed:

**viewModelScope**: Bound to ViewModel, cancelled on `onCleared()`. **Survives configuration changes** (rotation). Use for: business logic, data loading, Flow collections, long-running tasks. Requires `lifecycle-viewmodel-ktx`.

**lifecycleScope**: Bound to Activity/Fragment, cancelled on `ON_DESTROY`. **Does NOT survive rotation**. Use for: UI updates, one-time events, animations. Requires `lifecycle-runtime-ktx`.

**Key difference**: On screen rotation, viewModelScope continues running (same ViewModel instance), lifecycleScope cancels and restarts (new Activity/Fragment).

**Best practices**:
- Use viewModelScope for data/logic
- Use lifecycleScope with `repeatOnLifecycle(STARTED)` for UI updates
- In Fragments, always use `viewLifecycleOwner.lifecycleScope` not `lifecycleScope`
- Never use GlobalScope (creates leaks)
- Create custom scope for Services
- Handle exceptions with try-catch or CoroutineExceptionHandler

**repeatOnLifecycle**: Stops collection in onStop(), resumes in onStart(). Prevents crashes from updating UI in background. Essential for Fragments to avoid view lifecycle issues.

---

## Ответ (RU)

**viewModelScope** и **lifecycleScope** - lifecycle-aware coroutine scopes, автоматически отменяющие корутины при уничтожении связанного компонента:

| Аспект | viewModelScope | lifecycleScope |
|--------|----------------|----------------|
| **Привязан к** | ViewModel | Activity/Fragment/Lifecycle owner |
| **Отменяется при** | `onCleared()` | `ON_DESTROY` |
| **Переживает** | Configuration changes (rotation) | - НЕ переживает rotation |
| **Use case** | Business logic, data loading | UI updates, one-time events |
| **Доступен в** | ViewModel классах | Activity/Fragment |

### viewModelScope - для ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users = _users.asStateFlow()

    init {
        // - Корутина привязана к lifecycle ViewModel
        viewModelScope.launch {
            repository.observeUsers()
                .collect { users ->
                    _users.value = users
                }
        }
        // Автоматически отменится в onCleared()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val users = repository.getUsers()
                _users.value = users
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
        // Отменится при уничтожении ViewModel
    }
}
```

**Характеристики viewModelScope**:
- **Переживает configuration changes** (rotation, language change)
- Отменяется только при `onCleared()` (когда Activity/Fragment окончательно уничтожается)
- Идеален для **business logic** и загрузки данных
- Требует зависимость: `androidx.lifecycle:lifecycle-viewmodel-ktx`

### lifecycleScope - для Activity/Fragment

```kotlin
class UserActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // - Корутина привязана к lifecycle Activity
        lifecycleScope.launch {
            viewModel.users.collect { users ->
                updateUI(users) // Безопасно обновлять UI
            }
        }
        // Отменится при onDestroy()
    }

    fun showNotification() {
        lifecycleScope.launch {
            val result = withContext(Dispatchers.IO) {
                fetchData()
            }
            // Если Activity уничтожена - корутина уже отменена
            showSnackbar(result)
        }
    }
}
```

**Характеристики lifecycleScope**:
- **НЕ переживает configuration changes** (отменяется при rotation)
- Отменяется при `ON_DESTROY`
- Идеален для **UI операций** и one-time events
- Требует зависимость: `androidx.lifecycle:lifecycle-runtime-ktx`

### Что происходит при rotation

```kotlin
// ViewModel
class MyViewModel : ViewModel() {
    init {
        viewModelScope.launch {
            repeat(100) { i ->
                delay(1000)
                println("ViewModel: $i")
            }
        }
    }
    // При rotation корутина ПРОДОЛЖАЕТ работать
}

// Activity
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeat(100) { i ->
                delay(1000)
                println("Activity: $i")
            }
        }
        // При rotation корутина ОТМЕНЯЕТСЯ и запускается заново
    }
}
```

**Вывод при rotation экрана**:
```
// До rotation:
ViewModel: 0
Activity: 0
ViewModel: 1
Activity: 1

// [ROTATION]

// После rotation:
ViewModel: 2        // Продолжает с того же места
Activity: 0         // Начинает сначала (новый onCreate)
ViewModel: 3
Activity: 1
```

### Когда использовать viewModelScope

```kotlin
class ProductsViewModel(
    private val repository: ProductRepository
) : ViewModel() {

    // 1. Загрузка данных
    fun loadProducts() {
        viewModelScope.launch {
            _products.value = repository.getProducts()
        }
    }

    // 2. Continuous data streams
    init {
        viewModelScope.launch {
            repository.observeProducts()
                .collect { products ->
                    _products.value = products
                }
        }
    }

    // 3. Long-running operations
    fun syncData() {
        viewModelScope.launch {
            while (isActive) {
                repository.sync()
                delay(60_000) // Каждую минуту
            }
        }
    }

    // 4. Business logic
    fun checkout(cart: Cart) {
        viewModelScope.launch {
            val orderId = repository.createOrder(cart)
            val payment = processPayment(orderId)
            if (payment.isSuccessful) {
                _checkoutComplete.emit(orderId)
            }
        }
    }
}
```

**Используйте viewModelScope для**:
- Загрузки данных из repository
- Flow collections (observing data)
- Long-running background tasks
- Business logic operations
- Любая работа, которая должна пережить rotation

### Когда использовать lifecycleScope

```kotlin
class ProductsActivity : AppCompatActivity() {

    private val viewModel: ProductsViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 1. Collecting UI state
        lifecycleScope.launch {
            viewModel.products.collect { products ->
                adapter.submitList(products) // UI update
            }
        }

        // 2. One-time UI events
        lifecycleScope.launch {
            viewModel.events.collect { event ->
                when (event) {
                    is ShowSnackbar -> showSnackbar(event.message)
                    is NavigateToDetails -> navigateToDetails(event.id)
                }
            }
        }

        // 3. Animation
        lifecycleScope.launch {
            animateView()
        }
    }

    // 4. UI-only operations
    private fun showLoadingDialog() {
        lifecycleScope.launch {
            delay(300) // Debounce
            progressBar.isVisible = true
        }
    }
}
```

**Используйте lifecycleScope для**:
- Collecting StateFlow/SharedFlow для UI updates
- One-time UI events (navigation, dialogs, snackbars)
- Animations
- UI-only operations
- Любая работа, связанная только с текущим UI instance

### repeatOnLifecycle - продвинутый lifecycleScope

```kotlin
class ProductsFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ПРОБЛЕМА с обычным lifecycleScope:
        lifecycleScope.launch {
            viewModel.products.collect { products ->
                // Продолжает работать даже когда Fragment в background!
                updateUI(products)
            }
        }

        // ПРАВИЛЬНО - repeatOnLifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.products.collect { products ->
                    // Останавливается в onStop(), возобновляется в onStart()
                    updateUI(products)
                }
            }
        }
    }
}
```

**repeatOnLifecycle**:
- Автоматически **останавливает** collection при onStop()
- Автоматически **возобновляет** при onStart()
- Экономит ресурсы когда UI не видим
- Предотвращает crash при обновлении UI в background

### Lifecycle states

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    // STARTED - видим пользователю
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { updateUI(it) }
    }
}

viewLifecycleOwner.lifecycleScope.launch {
    // RESUMED - в foreground, получаем input
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.RESUMED) {
        viewModel.userInput.collect { handleInput(it) }
    }
}

viewLifecycleOwner.lifecycleScope.launch {
    // CREATED - созданы но можем быть не видимы
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.CREATED) {
        viewModel.init.collect { initialize(it) }
    }
}
```

### Fragment: lifecycle vs viewLifecycle

```kotlin
class MyFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // НЕ ИСПОЛЬЗУЙТЕ lifecycle в Fragment!
        lifecycleScope.launch {
            // Проблема: Fragment lifecycle != View lifecycle
            // Fragment переживает view recreation!
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ПРАВИЛЬНО - viewLifecycleOwner
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.data.collect { data ->
                binding.textView.text = data
                // Безопасно - view существует
            }
        }
    }
}
```

**В Fragment всегда используйте `viewLifecycleOwner.lifecycleScope`!**

### Практический пример: Login screen

```kotlin
// ViewModel - business logic
class LoginViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState = _loginState.asStateFlow()

    // viewModelScope - переживет rotation
    fun login(email: String, password: String) {
        viewModelScope.launch {
            _loginState.value = LoginState.Loading

            try {
                val user = authRepository.login(email, password)
                _loginState.value = LoginState.Success(user)
            } catch (e: Exception) {
                _loginState.value = LoginState.Error(e.message ?: "Unknown error")
            }
        }
    }

    // viewModelScope - long-running work
    fun keepSessionAlive() {
        viewModelScope.launch {
            while (isActive) {
                authRepository.refreshToken()
                delay(15 * 60 * 1000) // Every 15 minutes
            }
        }
    }
}

// Activity - UI operations
class LoginActivity : AppCompatActivity() {

    private val viewModel: LoginViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // lifecycleScope - UI updates
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.loginState.collect { state ->
                    when (state) {
                        is LoginState.Loading -> {
                            progressBar.isVisible = true
                        }
                        is LoginState.Success -> {
                            navigateToHome()
                        }
                        is LoginState.Error -> {
                            showError(state.message)
                        }
                    }
                }
            }
        }

        // lifecycleScope - UI event
        loginButton.setOnClickListener {
            lifecycleScope.launch {
                val email = emailInput.text.toString()
                val password = passwordInput.text.toString()
                viewModel.login(email, password)
            }
        }
    }
}
```

### Custom scope - когда ни один не подходит

```kotlin
class ChatService {
    // Создаем свой scope с SupervisorJob
    private val serviceScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Default
    )

    fun startListening() {
        serviceScope.launch {
            while (isActive) {
                val message = receiveMessage()
                handleMessage(message)
            }
        }
    }

    fun stop() {
        serviceScope.cancel() // Отменяем все корутины
    }
}

// Service с custom scope
class MusicPlayerService : Service() {
    private val serviceScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main
    )

    override fun onCreate() {
        super.onCreate()

        serviceScope.launch {
            // Long-running work beyond Activity lifecycle
            playMusic()
        }
    }

    override fun onDestroy() {
        serviceScope.cancel()
        super.onDestroy()
    }
}
```

### GlobalScope - когда НЕ использовать

```kotlin
// НИКОГДА не используйте GlobalScope
class BadViewModel : ViewModel() {
    fun loadData() {
        GlobalScope.launch {
            // Проблемы:
            // 1. Не отменится при onCleared()
            // 2. Memory leak
            // 3. Crash при обновлении UI после уничтожения
            val data = repository.getData()
            _data.value = data
        }
    }
}

// ПРАВИЛЬНО
class GoodViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.getData()
            _data.value = data
        }
    }
}
```

**GlobalScope - только для application-level задач, НЕ привязанных к компонентам!**

### Сравнение всех scopes

```kotlin
// 1. viewModelScope - переживает rotation
class MyViewModel : ViewModel() {
    init {
        viewModelScope.launch {
            // Отменится: onCleared() (Activity окончательно уничтожена)
        }
    }
}

// 2. lifecycleScope - НЕ переживает rotation
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            // Отменится: onDestroy()
        }
    }
}

// 3. Custom scope - полный контроль
class MyService : Service() {
    private val scope = CoroutineScope(SupervisorJob())

    override fun onDestroy() {
        scope.cancel() // Отменяем вручную
        super.onDestroy()
    }
}

// 4. GlobalScope - application lifetime (избегайте!)
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        GlobalScope.launch {
            // Живет весь lifetime приложения
        }
    }
}
```

### Error handling

```kotlin
// viewModelScope - ошибки обрабатываются внутри
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            try {
                val data = repository.getData()
                _data.value = data
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
}

// lifecycleScope - тоже нужна обработка
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            try {
                viewModel.data.collect { data ->
                    updateUI(data)
                }
            } catch (e: Exception) {
                showError(e)
            }
        }
    }
}

// Custom CoroutineExceptionHandler
class MyViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        _error.value = exception.message
    }

    private val customScope = CoroutineScope(
        viewModelScope.coroutineContext + exceptionHandler
    )

    fun loadData() {
        customScope.launch {
            // Ошибки обрабатываются handler'ом
            repository.getData()
        }
    }
}
```

### Testing

```kotlin
class ViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `test viewModelScope cancellation`() = runTest {
        val viewModel = MyViewModel(fakeRepository)

        viewModel.loadData()
        advanceUntilIdle()

        // Симулируем onCleared()
        viewModel.onCleared()

        // Проверяем что корутины отменены
        // (в реальности отменяются автоматически)
    }
}

class ActivityTest {
    @Test
    fun `test lifecycleScope with lifecycle`() = runTest {
        val scenario = ActivityScenario.launch(MyActivity::class.java)

        scenario.moveToState(Lifecycle.State.CREATED)
        // lifecycleScope корутины работают

        scenario.moveToState(Lifecycle.State.DESTROYED)
        // lifecycleScope корутины отменены
    }
}
```

### Best Practices

```kotlin
// 1. ViewModel - viewModelScope
class GoodViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            repository.getData()
        }
    }
}

// 2. Activity/Fragment - lifecycleScope + repeatOnLifecycle
class GoodFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.data.collect { updateUI(it) }
            }
        }
    }
}

// 3. Service - custom scope
class GoodService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }
}

// 4. НЕ смешивайте scopes
class BadViewModel : ViewModel() {
    fun loadData() {
        lifecycleScope.launch { // lifecycleScope не доступен в ViewModel!
            repository.getData()
        }
    }
}
```

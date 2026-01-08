---id: kotlin-165
title: "Lifecycle Scopes Viewmodelscope Lifecyclescope / Скоупы жизненного цикла ViewModelScope и LifecycleScope"
aliases: [Lifecycle Scopes, LifecycleScope, ViewModelScope]
topic: kotlin
subtopics: [coroutines, lifecycle]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, c-stateflow, q-coroutine-context-detailed--kotlin--hard, q-race-conditions-coroutines--kotlin--hard]
created: 2023-10-15
updated: 2025-11-09
tags: [android, coroutines, difficulty/medium, kotlin, lifecycle, lifecyclescope, viewmodelscope]

---
# Вопрос (RU)
> В чём разница между viewModelScope и lifecycleScope? Когда использовать каждый из них?

---

# Question (EN)
> What's the difference between viewModelScope and lifecycleScope? When should you use each?

## Ответ (RU)

**viewModelScope** и **lifecycleScope** - lifecycle-aware coroutine scopes, автоматически отменяющие корутины при уничтожении связанного компонента:

| Аспект | viewModelScope | lifecycleScope |
|--------|----------------|----------------|
| **Привязан к** | `ViewModel` | `Activity`/`Fragment`/`LifecycleOwner` |
| **Отменяется при** | `onCleared()` | `ON_DESTROY` |
| **Переживает** | Configuration changes (rotation) | - НЕ переживает rotation |
| **Use case** | Business logic, data loading | UI updates, one-time events |
| **Доступен в** | `ViewModel` классах | `Activity`/`Fragment`/любых `LifecycleOwner` |

### viewModelScope - Для `ViewModel`

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users = _users.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error = _error.asStateFlow()

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
                val users = withContext(Dispatchers.IO) {
                    repository.getUsers()
                }
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
- **Переживает configuration changes** (rotation, смена языка)
- Отменяется только при `onCleared()` (когда `Activity`/`Fragment` окончательно уничтожается)
- Идеален для **business logic** и загрузки данных
- Требует зависимость: `androidx.lifecycle:lifecycle-viewmodel-ktx`

### lifecycleScope - Для `Activity`/`Fragment`/`LifecycleOwner`

```kotlin
class UserActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // - Корутина привязана к lifecycle `Activity`
        lifecycleScope.launch {
            viewModel.users.collect { users ->
                updateUI(users) // Безопасно обновлять UI, пока Activity жива
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
- **НЕ переживает configuration changes** (отменяется при rotation, так как `Activity`/`Fragment` пересоздаются)
- Отменяется при `ON_DESTROY`
- Идеален для **UI операций** и one-time events в рамках текущего экземпляра UI
- Требует зависимость: `androidx.lifecycle:lifecycle-runtime-ktx`

### Что Происходит При Rotation

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
    // При rotation корутина ПРОДОЛЖАЕТ работать (пока ViewModel не очищена)
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
        // При rotation корутина ОТМЕНЯЕТСЯ и запускается заново в новом Activity
    }
}
```

**Вывод при rotation экрана**:
```text
// До rotation:
ViewModel: 0
Activity: 0
ViewModel: 1
Activity: 1

// [ROTATION]

// После rotation:
ViewModel: 2        // Продолжает (ViewModel сохранён)
Activity: 0         // Начинает сначала (новый onCreate)
ViewModel: 3
Activity: 1
```

### Когда Использовать viewModelScope

```kotlin
class ProductsViewModel(
    private val repository: ProductRepository
) : ViewModel() {

    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products = _products.asStateFlow()

    private val _checkoutComplete = MutableSharedFlow<String>()
    val checkoutComplete = _checkoutComplete

    // 1. Загрузка данных
    fun loadProducts() {
        viewModelScope.launch {
            val products = withContext(Dispatchers.IO) {
                repository.getProducts()
            }
            _products.value = products
        }
    }

    // 2. Непрерывные потоки данных
    init {
        viewModelScope.launch {
            repository.observeProducts()
                .collect { products ->
                    _products.value = products
                }
        }
    }

    // 3. Долгие операции
    fun syncData() {
        viewModelScope.launch(Dispatchers.IO) {
            while (isActive) {
                repository.sync()
                delay(60_000) // Каждую минуту
            }
        }
    }

    // 4. Business logic
    fun checkout(cart: Cart) {
        viewModelScope.launch {
            val orderId = withContext(Dispatchers.IO) {
                repository.createOrder(cart)
            }
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
- Коллекций `Flow` (наблюдение за данными)
- `Long`-running background tasks
- Business logic операций
- Работы, которая должна пережить rotation в рамках той же `ViewModel`

### Когда Использовать lifecycleScope

```kotlin
class ProductsActivity : AppCompatActivity() {

    private val viewModel: ProductsViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 1. Collecting UI state (см. также repeatOnLifecycle ниже)
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
- Collecting `StateFlow`/`SharedFlow` для UI updates в текущем экземпляре экрана
- One-time UI events (navigation, dialogs, snackbars)
- Animations
- UI-only операций
- Работы, связанной только с текущим UI instance

### repeatOnLifecycle - Продвинутый lifecycleScope

```kotlin
class ProductsFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Потенциальная проблема с обычным lifecycleScope в Fragment:
        lifecycleScope.launch {
            viewModel.products.collect { products ->
                // Эта корутина живёт до уничтожения Fragment,
                // и может пытаться обновлять UI после уничтожения view.
                updateUI(products)
            }
        }

        // ПРАВИЛЬНО для работы с view - использовать viewLifecycleOwner + repeatOnLifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.products.collect { products ->
                    // Останавливается в onStop(), возобновляется в onStart()
                    // и привязано к жизненному циклу view
                    updateUI(products)
                }
            }
        }
    }
}
```

**repeatOnLifecycle**:
- Автоматически **останавливает** collection при `onStop()`
- Автоматически **возобновляет** при `onStart()`
- Экономит ресурсы, когда UI не видим
- Предотвращает ошибки при обновлении UI, когда view/экран в background или уничтожены

### Lifecycle States

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    // STARTED - UI видим пользователю
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
    // CREATED - создано, но может быть не видно
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.CREATED) {
        viewModel.init.collect { initialize(it) }
    }
}
```

### Fragment: Lifecycle Vs viewLifecycle

```kotlin
class MyFragment : Fragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // `lifecycleScope` привязан к lifecycle `Fragment` и живёт дольше, чем view.
        // Используйте его только для задач, НЕ зависящих от view (например, логирование).
        lifecycleScope.launch {
            // Work not touching view hierarchy directly
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ПРАВИЛЬНО для работы с view - `viewLifecycleOwner`
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.data.collect { data ->
                binding.textView.text = data
                // Безопасно - view существует
            }
        }
    }
}
```

**В `Fragment` для работы с UI/view используйте `viewLifecycleOwner.lifecycleScope`; `lifecycleScope` оставляйте только для задач, связанных с самим `Fragment`, а не его view.**

### Практический Пример: Login Screen

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
                val user = withContext(Dispatchers.IO) {
                    authRepository.login(email, password)
                }
                _loginState.value = LoginState.Success(user)
            } catch (e: Exception) {
                _loginState.value = LoginState.Error(e.message ?: "Unknown error")
            }
        }
    }

    // viewModelScope - long-running work
    fun keepSessionAlive() {
        viewModelScope.launch(Dispatchers.IO) {
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

        // lifecycleScope + repeatOnLifecycle - UI updates
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
                        LoginState.Idle -> {
                            progressBar.isVisible = false
                        }
                    }
                }
            }
        }

        // UI event: чтение input и вызов ViewModel
        loginButton.setOnClickListener {
            val email = emailInput.text.toString()
            val password = passwordInput.text.toString()
            viewModel.login(email, password)
        }
    }
}
```

### Custom Scope - Когда Ни Один Не Подходит

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

### GlobalScope - Когда НЕ Использовать

```kotlin
// НЕ используйте GlobalScope для работы, завязанной на UI или компоненты
class BadViewModel : ViewModel() {
    fun loadData() {
        GlobalScope.launch {
            // Проблемы:
            // 1. Не отменится при onCleared()
            // 2. Возможны утечки памяти
            // 3. Возможен crash при обновлении UI после уничтожения
            val data = repository.getData()
            _data.value = data
        }
    }
}

// ПРАВИЛЬНО
class GoodViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.getData()
            }
            _data.value = data
        }
    }
}
```

**`GlobalScope` даже для application-level задач, как правило, стоит избегать. Предпочитайте явные application-level scopes (например, управляемые из `Application` или DI) и структурированную конкуррентность.**

### Сравнение Всех Scopes

```kotlin
// 1. viewModelScope - переживает rotation
class MyViewModel : ViewModel() {
    init {
        viewModelScope.launch {
            // Отменится: onCleared() (когда владелец ViewModel окончательно уничтожен)
        }
    }
}

// 2. lifecycleScope - НЕ переживает rotation
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            // Отменится: onDestroy() текущего экземпляра Activity
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

// 4. GlobalScope - живет весь lifetime процесса (избегайте!)
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        // Вместо GlobalScope лучше использовать явно управляемый scope, если нужен app-level scope.
    }
}
```

### Error Handling

```kotlin
// viewModelScope - ошибки обрабатываются внутри
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            try {
                val data = withContext(Dispatchers.IO) {
                    repository.getData()
                }
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
class MyViewModelWithHandler : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        _error.value = exception.message
    }

    // Расширяем контекст viewModelScope handler'ом (используем + для добавления handler'а)
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

        // В реальных тестах обычно проверяют, что job завершена/отменена,
        // вызывая публичные API или освобождая ViewModel через владельца.
        // Напрямую вызывать onCleared() снаружи нельзя, так как метод protected.
    }
}

class ActivityTest {
    @Test
    fun `test lifecycleScope with lifecycle`() = runTest {
        val scenario = ActivityScenario.launch(MyActivity::class.java)

        scenario.moveToState(Lifecycle.State.CREATED)
        // lifecycleScope корутины активны, пока Activity не уничтожена

        scenario.moveToState(Lifecycle.State.DESTROYED)
        // lifecycleScope корутины должны быть отменены
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

// 2. Activity/Fragment - lifecycleScope + repeatOnLifecycle (для UI)
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
class BadViewModelScopeUsage : ViewModel() {
    fun loadData() {
        // Неверно: lifecycleScope недоступен в ViewModel и не привязан к её lifecycle
        // lifecycleScope.launch {
        //     repository.getData()
        // }
    }
}
```

## Answer (EN)

viewModelScope and lifecycleScope are both lifecycle-aware coroutine scopes that automatically cancel coroutines when their owning component is destroyed. The English explanation below mirrors the Russian sections in structure and content depth.

### Core Differences

- viewModelScope:
  - Bound to `ViewModel`.
  - Cancelled in `onCleared()`.
  - Survives configuration changes (e.g., rotation) as long as the `ViewModel` is retained.
  - Use for:
    - Business logic and domain operations.
    - Data loading from repositories.
    - Collecting `Flow`/`StateFlow`/`SharedFlow` of app data.
    - `Long`-running/background work that should outlive a single `Activity`/`Fragment` instance.
  - From `androidx.lifecycle:lifecycle-viewmodel-ktx`.

- lifecycleScope:
  - Bound to a concrete `LifecycleOwner` instance (`Activity`, `Fragment`, or other `LifecycleOwner`).
  - Cancelled at that owner's `ON_DESTROY`.
  - Does NOT survive rotation for `Activity`/`Fragment` (new instance → new scope).
  - Use for:
    - UI updates tied to the current screen instance.
    - One-time UI events (navigation, dialogs, snackbars).
    - Animations and small UI-only tasks.
  - From `androidx.lifecycle:lifecycle-runtime-ktx`.

### Rotation Behavior Example

- `viewModelScope`:
  - A coroutine started in `viewModelScope` continues across configuration changes because the `ViewModel` is retained until its owner is finished.
- `lifecycleScope` in an `Activity`:
  - A coroutine started in `lifecycleScope` is cancelled when that `Activity` is destroyed on rotation and will run again only if you launch it in the new instance.

This corresponds to the RU example where:
- `ViewModel` prints continue across rotation.
- `Activity` prints restart from 0 after rotation.

### When to Use viewModelScope

Use `viewModelScope` for:
- Loading data from repositories (switching to `Dispatchers.IO` as needed).
- Continuous data streams (`Flow`) from data sources.
- `Long`-running sync/refresh loops while the feature is alive.
- Business logic like checkout, login, or other workflows that should survive configuration changes.

### When to Use lifecycleScope

Use `lifecycleScope` for:
- Collecting `StateFlow`/`SharedFlow` that directly update the current screen's UI.
- One-time events: navigation, snackbars, dialogs.
- Animations and short UI-only tasks tied to the current instance.

### repeatOnLifecycle (Advanced lifecycleScope Usage)

Use `repeatOnLifecycle(minActiveState)` inside a `lifecycleScope` (or `viewLifecycleOwner.lifecycleScope` in fragments) to:
- Start collecting when the lifecycle reaches `minActiveState`.
- Stop collecting when going below that state.

This mirrors the RU examples and prevents work while the UI is not visible.

### Lifecycle States

Typical patterns (matching RU examples):
- `STARTED`: collect visible UI state.
- `RESUMED`: handle foreground input.
- `CREATED`: run initialization collections when needed.

### Fragment: lifecycleScope Vs viewLifecycleOwner.lifecycleScope

- `Fragment`'s `lifecycleScope`:
  - Tied to `Fragment` lifecycle; outlives its view.
  - Use only for work not touching the view hierarchy.
- `viewLifecycleOwner.lifecycleScope`:
  - Tied to the view lifecycle.
  - Use for updating views; avoids leaks and crashes.

### Practical Example: Login Screen

The EN LoginViewModel/LoginActivity example matches the RU section:
- `viewModelScope` for login and session maintenance (with appropriate dispatcher switching).
- `lifecycleScope` + `repeatOnLifecycle` for observing state and reacting in UI.

### Custom Scope (When Neither Fits)

Create a custom `CoroutineScope` (with `SupervisorJob` and appropriate dispatcher) for components like `Service` or managers with their own lifecycle; cancel it in their teardown. This mirrors the RU ChatService/MusicPlayerService examples.

### GlobalScope (When NOT to Use)

Avoid `GlobalScope` for UI-related or lifecycle-bound work because it:
- Is not cancelled with component destruction.
- Risks memory leaks and updating dead UI.

Even for application-level/background tasks, prefer explicit, structured application-level scopes instead of `GlobalScope`.

### Scope Comparison Summary

- `viewModelScope`: `ViewModel`-bound, survives configuration changes.
- `lifecycleScope`: `LifecycleOwner`-bound, per-instance UI work.
- Custom scopes: for custom-lifetime components.
- `GlobalScope`: process-wide; generally avoid.

### Error Handling

- Handle exceptions inside coroutines in both `viewModelScope` and `lifecycleScope`.
- For centralized handling, extend a scope with `CoroutineExceptionHandler` (e.g., `CoroutineScope(viewModelScope.coroutineContext + handler)`).

### Testing

- Use rules/utilities (`MainDispatcherRule`, `runTest`) to control dispatchers.
- For `viewModelScope`, trigger work, advance time, and assert via public API or owner disposal that jobs complete/cancel; do not call `onCleared()` directly from tests since it is protected.
- For `lifecycleScope`, use `ActivityScenario`/`FragmentScenario` to drive lifecycle and assert cancellation.

### Best Practices

- Prefer `viewModelScope` in `ViewModel` for business/data work.
- Prefer `lifecycleScope` + `repeatOnLifecycle` (and `viewLifecycleOwner.lifecycleScope` in `Fragment`) for UI.
- Use custom scopes for services/managers; cancel explicitly.
- Do not misuse scopes across ownership boundaries.
- Avoid `GlobalScope` for lifecycle-bound or UI-related logic.

## Дополнительные Вопросы (RU)

- В чём преимущества этих scope по сравнению с классическими async-подходами в Java (callbacks, Executors)?
- Как бы вы выбрали подходящий scope в реальном проекте для разных типов задач?
- Какие типичные ошибки возникают при комбинировании `viewModelScope`, `lifecycleScope` и кастомных scope?

## Follow-ups (EN)

- What are the advantages of these scopes compared to classic Java async patterns (callbacks, Executors)?
- How would you choose the appropriate scope in a real project for different task types?
- What are common mistakes when combining `viewModelScope`, `lifecycleScope`, and custom scopes?

## Ссылки (RU)

- https://kotlinlang.org/docs/home.html
- [[c-kotlin]]
- [[c-coroutines]]

## References (EN)

- https://kotlinlang.org/docs/home.html
- [[c-kotlin]]
- [[c-coroutines]]

## Связанные Вопросы (RU)

- [[q-coroutine-context-detailed--kotlin--hard]]
- [[q-race-conditions-coroutines--kotlin--hard]]

## Related Questions (EN)

- [[q-coroutine-context-detailed--kotlin--hard]]
- [[q-race-conditions-coroutines--kotlin--hard]]

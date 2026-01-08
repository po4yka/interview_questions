---id: kotlin-087
title: "lifecycleScope vs viewModelScope / lifecycleScope против viewModelScope"
aliases: ["lifecycleScope vs viewModelScope", "lifecycleScope против viewModelScope"]

# Classification
topic: kotlin
subtopics: [coroutines, lifecycle]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Android Lifecycle Scopes Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, c-stateflow, q-lifecycle-aware-coroutines--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [android, coroutines, difficulty/medium, kotlin, lifecycle, lifecyclescope, viewmodelscope]
---
# Вопрос (RU)
> В чем разница между lifecycleScope и viewModelScope? Когда использовать каждый, как они обрабатывают события жизненного цикла и какие есть лучшие практики для Android coroutine scopes.

---

# Question (EN)
> What's the difference between lifecycleScope and viewModelScope? When to use each, how they handle lifecycle events, and best practices for Android coroutine scopes.

## Ответ (RU)

`lifecycleScope` и `viewModelScope` — это `CoroutineScope` с поддержкой жизненного цикла Android, которые автоматически отменяют корутины в зависимости от жизненного цикла владельца.

### Ключевые Различия

```kotlin
/**
 * lifecycleScope vs viewModelScope
 *
 *  Feature             lifecycleScope                          viewModelScope
 *
 *  Available in        Any LifecycleOwner (Activity, Fragment,  ViewModel
 *                       viewLifecycleOwner, etc.)
 *  Cancelled when      LifecycleOwner is destroyed             onCleared()
 *  Survives rotation   NO (owner destroyed)                    YES (while ViewModel retained)
 *  Use for             UI-related work tied to owner           Business logic, data loading
 *  Lifecycle states    Can be combined with repeatOnLifecycle  Only cleared when ViewModel is done
 *  Tied to             LifecycleOwner lifecycle                ViewModel lifecycle
 */
```

- `lifecycleScope`:
  - Доступен у `LifecycleOwner` (`Activity`, `Fragment`, `viewLifecycleOwner` и др.)
  - При использовании в `Activity` или `Fragment` scope отменяется при `onDestroy()` соответствующего владельца
  - При использовании у `viewLifecycleOwner` во `Fragment` scope отменяется при `onDestroyView()` (привязан к жизненному циклу вью, а не всего `Fragment`)
  - Не переживает уничтожение владельца (например, поворот экрана уничтожает экземпляр `Activity`/`Fragment` и связанные корутины)

- `viewModelScope`:
  - Привязан к `ViewModel`
  - Отменяется в `onCleared()`
  - Переживает конфигурационные изменения (например, поворот экрана), пока `ViewModel` переиспользуется

### Когда Использовать

`lifecycleScope`:
- Короткоживущие UI-операции (анимации, обновления, взаимодействие с вью)
- Подписка на `Flow`/`StateFlow` с учетом видимости UI через `repeatOnLifecycle`
- Обработка одноразовых UI-событий, связанных с конкретным экраном или вью

`viewModelScope`:
- Бизнес-логика и работа с данными
- Загрузка и кэширование данных, запросы к сети и БД
- Долгоживущие задачи, переживающие пересоздание UI, но ограниченные жизненным циклом `ViewModel`

### lifecycleScope: Подробности

```kotlin
class LifecycleScopeExamples : Fragment() {

    private val viewModel = MyViewModel()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Базовое использование: привязка к жизненному циклу view при использовании viewLifecycleOwner
        viewLifecycleOwner.lifecycleScope.launch {
            loadData()
        }

        // С repeatOnLifecycle (РЕКОМЕНДУЕТСЯ)
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Автоматически останавливает и возобновляет коллекцию в зависимости от состояния lifecycle
                    updateUI(state)
                }
            }
        }

        // Несколько коллекций в одном repeatOnLifecycle-блоке
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch {
                    viewModel.stateFlow1.collect { /* ... */ }
                }
                launch {
                    viewModel.stateFlow2.collect { /* ... */ }
                }
            }
        }

        // launchWhenStarted помечен как @Deprecated; предпочтительно repeatOnLifecycle
        // для более предсказуемых семантик отмены и перезапуска.
        viewLifecycleOwner.lifecycleScope.launchWhenStarted {
            // Приостанавливает выполнение, когда состояние ниже STARTED; может дольше удерживать ссылки.
        }
    }

    private suspend fun loadData() {}
    private fun updateUI(state: String) {}

    class MyViewModel : ViewModel() {
        val uiState = MutableStateFlow("state")
        val stateFlow1 = MutableStateFlow("data1")
        val stateFlow2 = MutableStateFlow("data2")
    }
}
```

### viewModelScope: Подробности

```kotlin
class ViewModelScopeExamples : ViewModel() {

    private val _state = MutableStateFlow(State())
    val state = _state.asStateFlow()

    data class State(val data: String = "")

    // Автоматическая отмена при onCleared()
    fun performOperation() {
        viewModelScope.launch {
            try {
                val result = longRunningOperation()
                _state.update { it.copy(data = result) }
            } catch (e: CancellationException) {
                // Опциональная очистка
                throw e
            }
        }
    }

    // Пользовательский диспетчер
    fun performIOOperation() {
        viewModelScope.launch(Dispatchers.IO) {
            val data = readFromDatabase()
            withContext(Dispatchers.Main) {
                _state.update { it.copy(data = data) }
            }
        }
    }

    // Обработка ошибок
    fun operationWithErrorHandling() {
        val handler = CoroutineExceptionHandler { _, exception ->
            handleError(exception)
        }

        viewModelScope.launch(handler) {
            riskyOperation()
        }
    }

    private suspend fun longRunningOperation(): String {
        delay(2000)
        return "result"
    }

    private suspend fun readFromDatabase(): String = "db data"
    private fun handleError(exception: Throwable) {}
    private suspend fun riskyOperation() {}
}
```

### Обработка Конфигурационных Изменений

```kotlin
class ConfigurationChanges {

    // lifecycleScope: корутина отменяется при уничтожении Activity
    class ActivityWithLifecycleScope : AppCompatActivity() {
        override fun onCreate(savedInstanceState: Bundle?) {
            super.onCreate(savedInstanceState)

            lifecycleScope.launch {
                val data = loadData()
                // При повороте экрана Activity уничтожается -> корутина отменяется.
                // В новой Activity загрузку нужно запускать заново.
            }
        }

        private suspend fun loadData(): String = "data"
    }

    // viewModelScope: переживает конфигурационные изменения, пока ViewModel удерживается
    class ViewModelWithScope : ViewModel() {
        private val _data = MutableStateFlow<String?>(null)
        val data = _data.asStateFlow()

        init {
            viewModelScope.launch {
                val result = loadData() // Обычно вызывается один раз за жизненный цикл ViewModel
                _data.value = result
                // Данные доступны пересозданным Activity/Fragment через наблюдение за Flow.
            }
        }

        private suspend fun loadData(): String = "data"
    }
}
```

### Лучшие Практики

```kotlin
class BestPractices {

    // ХОРОШО: использовать repeatOnLifecycle для сбора Flow из ViewModel
    class GoodFlowCollection : Fragment() {
        private val viewModel: MyViewModel by viewModels()

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            super.onViewCreated(view, savedInstanceState)

            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                    viewModel.uiState.collect { state ->
                        updateUI(state)
                    }
                }
            }
        }

        private fun updateUI(state: String) {}
        class MyViewModel : ViewModel() {
            val uiState = MutableStateFlow("state")
        }
    }

    // ПЛОХО (для UI Flow): сбор во Fragment.lifecycleScope без учета жизненного цикла view
    class BadFlowCollection : Fragment() {
        private val viewModel: MyViewModel by viewModels()

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            super.onViewCreated(view, savedInstanceState)

            lifecycleScope.launch {
                viewModel.uiState.collect { state ->
                    // Сбор продолжается до onDestroy() Fragment и не привязан к жизненному циклу view.
                    // Без viewLifecycleOwner есть риск обновлять уже уничтоженные вью.
                    updateUI(state)
                }
            }
        }

        private fun updateUI(state: String) {}
        class MyViewModel : ViewModel() {
            val uiState = MutableStateFlow("state")
        }
    }

    // ХОРОШО: бизнес-логика во ViewModel
    class GoodArchitecture : ViewModel() {
        private val repository = Repository()

        fun saveData(data: String) {
            viewModelScope.launch {
                repository.save(data)
            }
        }

        class Repository {
            suspend fun save(data: String) {}
        }
    }

    // ПЛОХО: бизнес-логика жестко привязана к Activity
    class BadArchitecture : AppCompatActivity() {
        private val repository = Repository()

        fun saveData(data: String) {
            lifecycleScope.launch {
                // Отменяется при уничтожении Activity; плохо для долгих операций
                repository.save(data)
            }
        }

        class Repository {
            suspend fun save(data: String) {}
        }
    }
}
```

### Реальный Пример

```kotlin
// ViewModel: бизнес-логика с viewModelScope
class ProductViewModel : ViewModel() {
    private val repository = ProductRepository()

    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products = _products.asStateFlow()

    private val _events = Channel<Event>()
    val events = _events.receiveAsFlow()

    sealed class Event {
        data class ShowError(val message: String) : Event()
    }

    data class Product(val id: Int, val name: String)

    fun loadProducts() {
        viewModelScope.launch {
            try {
                val data = repository.getProducts()
                _products.value = data
            } catch (e: Exception) {
                _events.send(Event.ShowError(e.message ?: "Error"))
            }
        }
    }

    class ProductRepository {
        suspend fun getProducts(): List<Product> = emptyList()
    }
}

// Fragment: UI-обновления с viewLifecycleOwner.lifecycleScope + repeatOnLifecycle
class ProductFragment : Fragment() {
    private val viewModel: ProductViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch {
                    viewModel.products.collect { products ->
                        updateProductList(products)
                    }
                }

                launch {
                    viewModel.events.collect { event ->
                        handleEvent(event)
                    }
                }
            }
        }

        // Старт загрузки
        viewModel.loadProducts()
    }

    private fun updateProductList(products: List<ProductViewModel.Product>) {}

    private fun handleEvent(event: ProductViewModel.Event) {
        when (event) {
            is ProductViewModel.Event.ShowError -> {
                Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
            }
        }
    }
}
```

### Дополнительные Вопросы (RU)

1. В чем роль `repeatOnLifecycle` и почему он важен?
2. Как избежать утечек памяти при сборе `Flow`?
3. Можно ли создавать собственные scope, учитывающие жизненный цикл?
4. Что происходит с корутинами при повороте экрана?
5. Как тестировать корутины, зависящие от жизненного цикла?
6. Каковы типичные ошибки при использовании `lifecycleScope` и `viewModelScope`?
7. Как применять эти подходы в реальных фичах приложения?
8. Каковы ключевые отличия от Java-подходов без coroutine scopes?
9. В каких реальных сценариях вы бы выбрали каждый из scope?
10. Какие распространенные подводные камни стоит избегать?

---

## Answer (EN)

`lifecycleScope` and `viewModelScope` are lifecycle-aware `CoroutineScope`s provided by Android Jetpack that automatically manage coroutine cancellation based on Android lifecycle events.

### Key Differences

```kotlin
/**
 * lifecycleScope vs viewModelScope
 *
 *  Feature             lifecycleScope                          viewModelScope
 *
 *  Available in        Any LifecycleOwner (Activity, Fragment,  ViewModel
 *                       viewLifecycleOwner, etc.)
 *  Cancelled when      LifecycleOwner is destroyed             onCleared()
 *  Survives rotation   NO (owner destroyed)                    YES (while ViewModel retained)
 *  Use for             UI-related work tied to owner           Business logic, data loading
 *  Lifecycle states    Can be combined with repeatOnLifecycle  Only cleared when ViewModel is done
 *  Tied to             LifecycleOwner lifecycle                ViewModel lifecycle
 */
```

```kotlin
// lifecycleScope Example (Activity)
class MainActivity : AppCompatActivity() {

    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Cancelled in onDestroy() of this Activity
        lifecycleScope.launch {
            // UI-related work
            updateUI()
        }

        // Lifecycle-aware collection: only active when at least STARTED
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }

    private fun updateUI() {}
    private fun updateUI(state: String) {}

    class MyViewModel : ViewModel() {
        val uiState = MutableStateFlow("state")
    }
}
```

```kotlin
// viewModelScope Example
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData.asStateFlow()

    init {
        // Survives configuration changes; cancelled in onCleared()
        viewModelScope.launch {
            loadUserData()
        }
    }

    private suspend fun loadUserData() {
        delay(1000)
    }

    data class User(val id: String)
}
```

### When to Use Each

```kotlin
class ScopeUsageExamples {

    // USE lifecycleScope (via viewLifecycleOwner) for: UI animations tied to the view
    class AnimationFragment : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            super.onViewCreated(view, savedInstanceState)

            viewLifecycleOwner.lifecycleScope.launch {
                animateView(view)
            }
        }

        private suspend fun animateView(view: View) {
            delay(100)
        }
    }

    // USE viewModelScope for: Data loading that survives configuration changes
    class DataViewModel : ViewModel() {
        private val _data = MutableStateFlow<List<String>>(emptyList())
        val data = _data.asStateFlow()

        fun loadData() {
            viewModelScope.launch {
                val result = fetchFromNetwork()
                _data.value = result
            }
        }

        private suspend fun fetchFromNetwork(): List<String> {
            delay(1000)
            return emptyList()
        }
    }

    // USE lifecycleScope (via viewLifecycleOwner) for: One-time UI events collection
    class EventFragment : Fragment() {
        private val viewModel: EventViewModel by viewModels()

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            super.onViewCreated(view, savedInstanceState)

            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                    viewModel.events.collect { event ->
                        handleEvent(event)
                    }
                }
            }
        }

        private fun handleEvent(event: String) {
            Toast.makeText(context, event, Toast.LENGTH_SHORT).show()
        }
    }

    class EventViewModel : ViewModel() {
        private val _events = Channel<String>()
        val events = _events.receiveAsFlow()
    }
}
```

### lifecycleScope Deep Dive

```kotlin
class LifecycleScopeExamples : Fragment() {

    private val viewModel = MyViewModel()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Basic usage: tied to view lifecycle when using viewLifecycleOwner
        viewLifecycleOwner.lifecycleScope.launch {
            loadData()
        }

        // With repeatOnLifecycle (RECOMMENDED)
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Automatically stops and restarts collection with lifecycle
                    updateUI(state)
                }
            }
        }

        // Multiple collections within the same repeatOnLifecycle block
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch {
                    viewModel.stateFlow1.collect { /* ... */ }
                }
                launch {
                    viewModel.stateFlow2.collect { /* ... */ }
                }
            }
        }

        // launchWhenStarted is @Deprecated; prefer repeatOnLifecycle
        // for more predictable cancellation + restart semantics.
        viewLifecycleOwner.lifecycleScope.launchWhenStarted {
            // Suspends when below STARTED; may hold references longer than desired.
        }
    }

    private suspend fun loadData() {}
    private fun updateUI(state: String) {}

    class MyViewModel : ViewModel() {
        val uiState = MutableStateFlow("state")
        val stateFlow1 = MutableStateFlow("data1")
        val stateFlow2 = MutableStateFlow("data2")
    }
}
```

### viewModelScope Deep Dive

```kotlin
class ViewModelScopeExamples : ViewModel() {

    private val _state = MutableStateFlow(State())
    val state = _state.asStateFlow()

    data class State(val data: String = "")

    // Automatic cancellation on onCleared()
    fun performOperation() {
        viewModelScope.launch {
            try {
                val result = longRunningOperation()
                _state.update { it.copy(data = result) }
            } catch (e: CancellationException) {
                // Optional cleanup
                throw e
            }
        }
    }

    // Custom dispatcher
    fun performIOOperation() {
        viewModelScope.launch(Dispatchers.IO) {
            val data = readFromDatabase()
            withContext(Dispatchers.Main) {
                _state.update { it.copy(data = data) }
            }
        }
    }

    // Exception handling
    fun operationWithErrorHandling() {
        val handler = CoroutineExceptionHandler { _, exception ->
            handleError(exception)
        }

        viewModelScope.launch(handler) {
            riskyOperation()
        }
    }

    private suspend fun longRunningOperation(): String {
        delay(2000)
        return "result"
    }

    private suspend fun readFromDatabase(): String = "db data"
    private fun handleError(exception: Throwable) {}
    private suspend fun riskyOperation() {}
}
```

### Configuration Changes Handling

```kotlin
class ConfigurationChanges {

    // lifecycleScope: coroutine is cancelled when Activity is destroyed
    class ActivityWithLifecycleScope : AppCompatActivity() {
        override fun onCreate(savedInstanceState: Bundle?) {
            super.onCreate(savedInstanceState)

            lifecycleScope.launch {
                val data = loadData()
                // On rotation, this Activity is destroyed => coroutine cancelled.
                // You must manually restart work in the new Activity instance.
            }
        }

        private suspend fun loadData(): String = "data"
    }

    // viewModelScope: survives configuration changes while ViewModel is retained
    class ViewModelWithScope : ViewModel() {
        private val _data = MutableStateFlow<String?>(null)
        val data = _data.asStateFlow()

        init {
            viewModelScope.launch {
                val result = loadData() // Typically runs once per ViewModel lifecycle
                _data.value = result
                // Data can be observed by recreated Activities/Fragments.
            }
        }

        private suspend fun loadData(): String = "data"
    }
}
```

### Best Practices

```kotlin
class BestPractices {

    // GOOD: Use repeatOnLifecycle for collecting Flows from ViewModel
    class GoodFlowCollection : Fragment() {
        private val viewModel: MyViewModel by viewModels()

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            super.onViewCreated(view, savedInstanceState)

            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                    viewModel.uiState.collect { state ->
                        updateUI(state)
                    }
                }
            }
        }

        private fun updateUI(state: String) {}
        class MyViewModel : ViewModel() {
            val uiState = MutableStateFlow("state")
        }
    }

    // BAD (for UI Flows): Collecting in Fragment.lifecycleScope without view lifecycle awareness
    class BadFlowCollection : Fragment() {
        private val viewModel: MyViewModel by viewModels()

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            super.onViewCreated(view, savedInstanceState)

            lifecycleScope.launch {
                viewModel.uiState.collect { state ->
                    // Collection continues until Fragment.onDestroy() and is not tied to view lifecycle.
                    // Without viewLifecycleOwner you risk updating views after onDestroyView().
                    updateUI(state)
                }
            }
        }

        private fun updateUI(state: String) {}
        class MyViewModel : ViewModel() {
            val uiState = MutableStateFlow("state")
        }
    }

    // GOOD: Business logic in ViewModel
    class GoodArchitecture : ViewModel() {
        private val repository = Repository()

        fun saveData(data: String) {
            viewModelScope.launch {
                repository.save(data)
            }
        }

        class Repository {
            suspend fun save(data: String) {}
        }
    }

    // BAD: Business logic tightly coupled to Activity lifecycle
    class BadArchitecture : AppCompatActivity() {
        private val repository = Repository()

        fun saveData(data: String) {
            lifecycleScope.launch {
                // Cancelled on Activity destroy; not suitable for long-running work
                repository.save(data)
            }
        }

        class Repository {
            suspend fun save(data: String) {}
        }
    }
}
```

### Real-world Example

```kotlin
// ViewModel: Business logic with viewModelScope
class ProductViewModel : ViewModel() {
    private val repository = ProductRepository()

    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products = _products.asStateFlow()

    private val _events = Channel<Event>()
    val events = _events.receiveAsFlow()

    sealed class Event {
        data class ShowError(val message: String) : Event()
    }

    data class Product(val id: Int, val name: String)

    fun loadProducts() {
        viewModelScope.launch {
            try {
                val data = repository.getProducts()
                _products.value = data
            } catch (e: Exception) {
                _events.send(Event.ShowError(e.message ?: "Error"))
            }
        }
    }

    class ProductRepository {
        suspend fun getProducts(): List<Product> = emptyList()
    }
}

// Fragment: UI updates with lifecycleScope (viewLifecycleOwner) + repeatOnLifecycle
class ProductFragment : Fragment() {
    private val viewModel: ProductViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch {
                    viewModel.products.collect { products ->
                        updateProductList(products)
                    }
                }

                launch {
                    viewModel.events.collect { event ->
                        handleEvent(event)
                    }
                }
            }
        }

        // Trigger loading
        viewModel.loadProducts()
    }

    private fun updateProductList(products: List<ProductViewModel.Product>) {}

    private fun handleEvent(event: ProductViewModel.Event) {
        when (event) {
            is ProductViewModel.Event.ShowError -> {
                Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
            }
        }
    }
}
```

---

## Follow-ups

1. What is `repeatOnLifecycle` and why is it important?
2. How to prevent memory leaks when collecting `Flow`s?
3. Can you create custom lifecycle-aware scopes?
4. What happens to running coroutines during rotation?
5. How to test lifecycle-aware coroutines?
6. What are typical pitfalls with `lifecycleScope` and `viewModelScope`?
7. How would you use these scopes in a real feature?
8. What are the key differences between this and Java approaches without coroutine scopes?
9. When would you use each scope in practice?
10. What are common pitfalls to avoid?

---

## References

- [Lifecycle-aware coroutines](https://developer.android.com/topic/libraries/architecture/coroutines)
- [lifecycleScope](https://developer.android.com/reference/kotlin/androidx/lifecycle/package-summary#lifecyclescope)
- [viewModelScope](https://developer.android.com/reference/kotlin/androidx/lifecycle/package-summary#viewmodelscope)
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Related Questions

### Related (Medium)
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - Testing
- [[q-stateflow-sharedflow-android--kotlin--medium]] - Coroutines
- [[q-supervisor-scope-vs-coroutine-scope--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-lifecycle-aware-coroutines--kotlin--hard]] - Coroutines
- [[q-channel-pipelines--kotlin--hard]] - Channels

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

---
id: kotlin-087
title: "lifecycleScope vs viewModelScope / lifecycleScope против viewModelScope"
aliases: ["lifecycleScope vs viewModelScope, lifecycleScope против viewModelScope"]

# Classification
topic: kotlin
subtopics: [android, coroutines, lifecycle]
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
related: [q-android-coroutine-scopes--kotlin--medium, q-lifecycle-aware-coroutines--kotlin--hard, q-viewmodel-coroutines-lifecycle--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [android, coroutines, difficulty/medium, kotlin, lifecycle, lifecyclescope, viewmodelscope]
date created: Sunday, October 12th 2025, 3:43:53 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---
# Вопрос (RU)
> В чем разница между lifecycleScope и viewModelScope? Когда использовать каждый, как они обрабатывают события жизненного цикла и лучшие практики для Android coroutine scopes.

---

# Question (EN)
> What's the difference between lifecycleScope and viewModelScope? When to use each, how they handle lifecycle events, and best practices for Android coroutine scopes.

## Ответ (RU)

`lifecycleScope` и `viewModelScope` - это CoroutineScope с поддержкой жизненного цикла Android.

### Ключевые Различия

- **lifecycleScope**: Привязан к Activity/Fragment, отменяется при onDestroy(), НЕ переживает поворот экрана
- **viewModelScope**: Привязан к ViewModel, отменяется при onCleared(), ПЕРЕЖИВАЕТ поворот экрана

### Когда Использовать

**lifecycleScope**:
- UI операции (анимации, обновления)
- Подписка на Flow/StateFlow
- Одноразовые UI события

**viewModelScope**:
- Бизнес-логика
- Загрузка данных
- Работа с репозиториями

### Лучшая Практика

```kotlin
// Fragment: UI с lifecycleScope + repeatOnLifecycle
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.state.collect { updateUI(it) }
    }
}

// ViewModel: Логика с viewModelScope
viewModelScope.launch {
    val data = repository.fetch()
    _state.value = data
}
```

---

## Answer (EN)

`lifecycleScope` and `viewModelScope` are lifecycle-aware CoroutineScopes provided by Android Jetpack that automatically manage coroutine cancellation based on Android lifecycle events.

### Key Differences

```kotlin
/**
 * lifecycleScope vs viewModelScope
 *
 *
 *  Feature             lifecycleScope       viewModelScope
 *
 *  Available in        Activity, Fragment   ViewModel
 *  Cancelled when      onDestroy()          onCleared()
 *  Survives rotation   NO                   YES
 *  Use for             UI operations        Business logic
 *  Lifecycle states    Aware of all states  Only cleared state
 *  Tied to             View lifecycle       ViewModel lifecycle
 *
 */

// lifecycleScope Example
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Cancelled on onDestroy()
        lifecycleScope.launch {
            // UI-related work
            updateUI()
        }

        // Lifecycle-aware collection
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Only collects when STARTED or RESUMED
                    updateUI(state)
                }
            }
        }
    }

    private fun updateUI() {}
    private fun updateUI(state: Any) {}
    private val viewModel = ViewModel()
    class ViewModel {
        val uiState = MutableStateFlow<String>("state")
    }
}

// viewModelScope Example
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData.asStateFlow()

    init {
        // Survives rotation, cancelled on onCleared()
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

    //  USE lifecycleScope for: UI animations
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

    //  USE viewModelScope for: Data loading
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

    //  USE lifecycleScope for: One-time UI events
    class EventFragment : Fragment() {
        private val viewModel: EventViewModel by viewModels()

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            viewLifecycleOwner.lifecycleScope.launch {
                viewModel.events.collect { event ->
                    handleEvent(event)
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

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Basic usage
        viewLifecycleOwner.lifecycleScope.launch {
            loadData()
        }

        // With repeatOnLifecycle (RECOMMENDED)
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Automatically stops/restarts on lifecycle changes
                    updateUI(state)
                }
            }
        }

        // Multiple states
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

        // launchWhenStarted (DEPRECATED - use repeatOnLifecycle)
        viewLifecycleOwner.lifecycleScope.launchWhenStarted {
            // Suspends when not STARTED
            // But doesn't cancel - may leak
        }
    }

    private suspend fun loadData() {}
    private fun updateUI(state: String) {}
    private val viewModel = MyViewModel()

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
                // Cleanup if needed
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

    // lifecycleScope: Lost on rotation
    class ActivityWithLifecycleScope : AppCompatActivity() {
        override fun onCreate(savedInstanceState: Bundle?) {
            super.onCreate(savedInstanceState)

            lifecycleScope.launch {
                val data = loadData() // Restarted on rotation!
                // Data lost on rotation
            }
        }

        private suspend fun loadData(): String = "data"
    }

    // viewModelScope: Survives rotation
    class ViewModelWithScope : ViewModel() {
        private val _data = MutableStateFlow<String?>(null)
        val data = _data.asStateFlow()

        init {
            viewModelScope.launch {
                val result = loadData() // Only runs once!
                _data.value = result
                // Data preserved across rotations
            }
        }

        private suspend fun loadData(): String = "data"
    }
}
```

### Best Practices

```kotlin
class BestPractices {

    //  GOOD: Use repeatOnLifecycle for collecting Flows
    class GoodFlowCollection : Fragment() {
        private val viewModel: MyViewModel by viewModels()

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
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

    //  BAD: Collecting without lifecycle awareness
    class BadFlowCollection : Fragment() {
        private val viewModel: MyViewModel by viewModels()

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            lifecycleScope.launch {
                viewModel.uiState.collect { state ->
                    // Keeps collecting even when not visible! Leak!
                    updateUI(state)
                }
            }
        }

        private fun updateUI(state: String) {}
        class MyViewModel : ViewModel() {
            val uiState = MutableStateFlow("state")
        }
    }

    //  GOOD: Business logic in ViewModel
    class GoodArchitecture : ViewModel() {
        fun saveData(data: String) {
            viewModelScope.launch {
                repository.save(data)
            }
        }

        private val repository = Repository()
        class Repository {
            suspend fun save(data: String) {}
        }
    }

    //  BAD: Business logic in Activity
    class BadArchitecture : AppCompatActivity() {
        fun saveData(data: String) {
            lifecycleScope.launch {
                // Lost on rotation!
                repository.save(data)
            }
        }

        private val repository = Repository()
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

// Fragment: UI updates with lifecycleScope
class ProductFragment : Fragment() {
    private val viewModel: ProductViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Collect state
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

## Follow-up Questions (Следующие вопросы)

1. **What is repeatOnLifecycle and why is it important?**
2. **How to prevent memory leaks when collecting Flows?**
3. **Can you create custom lifecycle-aware scopes?**
4. **What happens to running coroutines during rotation?**
5. **How to test lifecycle-aware coroutines?**

---

**Official Documentation:**
- [Lifecycle-aware coroutines](https://developer.android.com/topic/libraries/architecture/coroutines)
- [lifecycleScope](https://developer.android.com/reference/kotlin/androidx/lifecycle/package-summary#lifecyclescope)
- [viewModelScope](https://developer.android.com/reference/kotlin/androidx/lifecycle/package-summary#viewmodelscope)

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

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


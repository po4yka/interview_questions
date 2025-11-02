---
id: kotlin-121
title: "ViewModel Coroutines and Lifecycle / Корутины в ViewModel и жизненный цикл"
aliases: []

# Classification
topic: kotlin
subtopics: [android, coroutines, lifecycle, viewmodel, viewmodelscope]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Android Coroutines ViewModel Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutines-cancellation--kotlin--medium, q-lifecyclescope-viewmodelscope--kotlin--medium, q-stateflow-sharedflow-android--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [android, coroutines, difficulty/medium, kotlin, lifecycle, viewmodel, viewmodelscope]
date created: Sunday, October 12th 2025, 3:43:53 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Question (EN)
> How to use coroutines in ViewModel? Explain viewModelScope, automatic cancellation on onCleared(), best practices for launching coroutines, and handling configuration changes.

# Вопрос (RU)
> Как использовать корутины в ViewModel? Объясните viewModelScope, автоматическую отмену при onCleared(), лучшие практики запуска корутин и обработку изменений конфигурации.

---

## Answer (EN)

ViewModels are Android's recommended architecture component for managing UI-related data across configuration changes. Combining ViewModels with coroutines provides a powerful pattern for handling asynchronous operations with automatic lifecycle management.

### viewModelScope Basics

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class UserViewModel : ViewModel() {

    // viewModelScope is automatically cancelled when ViewModel is cleared
    fun loadUser(userId: String) {
        viewModelScope.launch {
            try {
                val user = userRepository.getUser(userId)
                _userState.value = UserState.Success(user)
            } catch (e: Exception) {
                _userState.value = UserState.Error(e.message)
            }
        }
    }

    // No need to manually cancel - happens automatically
    override fun onCleared() {
        super.onCleared()
        // viewModelScope.cancel() - NOT NEEDED, automatic!
        println("ViewModel cleared, all coroutines cancelled")
    }

    private val _userState = MutableStateFlow<UserState>(UserState.Loading)
    val userState: StateFlow<UserState> = _userState.asStateFlow()

    sealed class UserState {
        object Loading : UserState()
        data class Success(val user: User) : UserState()
        data class Error(val message: String?) : UserState()
    }

    data class User(val id: String, val name: String)
    private val userRepository = UserRepository()
    class UserRepository {
        suspend fun getUser(id: String): User {
            delay(1000)
            return User(id, "User $id")
        }
    }
}
```

### Proper State Management with StateFlow

```kotlin
class ProductsViewModel : ViewModel() {

    private val repository = ProductRepository()

    // StateFlow for UI state
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    data class UiState(
        val products: List<Product> = emptyList(),
        val isLoading: Boolean = false,
        val error: String? = null
    )

    data class Product(val id: Int, val name: String, val price: Double)

    // Launch in viewModelScope
    fun loadProducts() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            try {
                val products = repository.fetchProducts()
                _uiState.update {
                    it.copy(
                        products = products,
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message
                    )
                }
            }
        }
    }

    // Refresh with loading indicator
    fun refresh() {
        if (_uiState.value.isLoading) return // Prevent duplicate requests

        loadProducts()
    }

    class ProductRepository {
        suspend fun fetchProducts(): List<Product> {
            delay(1000)
            return List(10) { Product(it, "Product $it", it * 10.0) }
        }
    }
}
```

### Configuration Changes Handling

```kotlin
class ConfigurationSafeViewModel : ViewModel() {

    private val _searchResults = MutableStateFlow<List<String>>(emptyList())
    val searchResults: StateFlow<List<String>> = _searchResults.asStateFlow()

    // Survives configuration changes (rotation, etc.)
    fun search(query: String) {
        viewModelScope.launch {
            val results = performSearch(query)
            _searchResults.value = results
            // State preserved across rotations
        }
    }

    private suspend fun performSearch(query: String): List<String> {
        delay(500)
        return listOf("Result 1", "Result 2", "Result 3")
            .filter { it.contains(query, ignoreCase = true) }
    }
}

// In Activity/Fragment
class SearchActivity : AppCompatActivity() {
    private val viewModel: ConfigurationSafeViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Collect state
        lifecycleScope.launch {
            viewModel.searchResults.collect { results ->
                updateUI(results)
                // UI updates even after rotation
            }
        }

        // Trigger search
        viewModel.search("query")
        // After rotation, results are still available
    }

    private fun updateUI(results: List<String>) {
        // Update UI
    }
}
```

### Error Handling Patterns

```kotlin
class ErrorHandlingViewModel : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val data: String) : UiState()
        data class Error(val exception: Exception) : UiState()
    }

    // Pattern 1: Try-catch in launch
    fun loadDataWithTryCatch() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val data = fetchData()
                _uiState.value = UiState.Success(data)
            } catch (e: CancellationException) {
                throw e // Re-throw cancellation
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }

    // Pattern 2: CoroutineExceptionHandler
    fun loadDataWithHandler() {
        val handler = CoroutineExceptionHandler { _, exception ->
            _uiState.value = UiState.Error(exception as Exception)
        }

        viewModelScope.launch(handler) {
            val data = fetchData()
            _uiState.value = UiState.Success(data)
        }
    }

    // Pattern 3: Result wrapper
    sealed class Result<out T> {
        data class Success<T>(val data: T) : Result<T>()
        data class Error(val exception: Exception) : Result<Nothing>()
    }

    suspend fun fetchDataAsResult(): Result<String> = try {
        Result.Success(fetchData())
    } catch (e: Exception) {
        Result.Error(e)
    }

    fun loadDataWithResult() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            when (val result = fetchDataAsResult()) {
                is Result.Success -> _uiState.value = UiState.Success(result.data)
                is Result.Error -> _uiState.value = UiState.Error(result.exception)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(1000)
        return "Data"
    }
}
```

### Best Practices for Launching Coroutines

```kotlin
class BestPracticesViewModel : ViewModel() {

    private val _state = MutableStateFlow(State())
    val state = _state.asStateFlow()

    data class State(val data: String = "")

    //  GOOD: Launch in viewModelScope
    fun goodLaunch() {
        viewModelScope.launch {
            val result = fetchData()
            _state.update { it.copy(data = result) }
        }
    }

    //  BAD: Creating own scope
    private val customScope = CoroutineScope(Dispatchers.Main)
    fun badCustomScope() {
        customScope.launch {
            // Won't be cancelled automatically!
        }
    }

    //  GOOD: Using Dispatchers for heavy work
    fun goodDispatchers() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                // Heavy I/O work
                fetchDataFromNetwork()
            }
            _state.update { it.copy(data = data) }
        }
    }

    //  BAD: Blocking main thread
    fun badBlocking() {
        viewModelScope.launch {
            val data = runBlocking { // DON'T DO THIS!
                fetchData()
            }
        }
    }

    //  GOOD: Cancellable operations
    fun goodCancellable() {
        viewModelScope.launch {
            repeat(100) { i ->
                if (!isActive) return@launch // Check cancellation
                processItem(i)
            }
        }
    }

    //  GOOD: One-shot events with Channel
    private val _events = Channel<Event>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    sealed class Event {
        data class ShowToast(val message: String) : Event()
    }

    fun triggerEvent() {
        viewModelScope.launch {
            _events.send(Event.ShowToast("Success!"))
        }
    }

    private suspend fun fetchData(): String {
        delay(100)
        return "data"
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(100)
        return "network data"
    }

    private suspend fun processItem(i: Int) {
        delay(10)
    }
}
```

### Loading States and Debouncing

```kotlin
class SearchViewModel : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _searchResults = MutableStateFlow<List<String>>(emptyList())
    private val _isSearching = MutableStateFlow(false)

    val searchResults: StateFlow<List<String>> = _searchResults.asStateFlow()
    val isSearching: StateFlow<Boolean> = _isSearching.asStateFlow()

    // Debounced search
    init {
        viewModelScope.launch {
            _searchQuery
                .debounce(300) // Wait for user to stop typing
                .distinctUntilChanged()
                .filter { it.length >= 3 }
                .collect { query ->
                    performSearch(query)
                }
        }
    }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }

    private suspend fun performSearch(query: String) {
        _isSearching.value = true

        try {
            val results = searchRepository.search(query)
            _searchResults.value = results
        } catch (e: Exception) {
            _searchResults.value = emptyList()
        } finally {
            _isSearching.value = false
        }
    }

    private val searchRepository = SearchRepository()
    class SearchRepository {
        suspend fun search(query: String): List<String> {
            delay(500)
            return listOf("Result 1", "Result 2")
        }
    }
}
```

### Multiple Parallel Operations

```kotlin
class ParallelOperationsViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(UiState())
    val uiState = _uiState.asStateFlow()

    data class UiState(
        val user: User? = null,
        val posts: List<Post> = emptyList(),
        val comments: List<Comment> = emptyList(),
        val isLoading: Boolean = false
    )

    data class User(val id: String)
    data class Post(val id: Int)
    data class Comment(val id: Int)

    // Load multiple things in parallel
    fun loadUserProfile(userId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            try {
                // Run in parallel
                val user = async { fetchUser(userId) }
                val posts = async { fetchPosts(userId) }
                val comments = async { fetchComments(userId) }

                _uiState.update {
                    it.copy(
                        user = user.await(),
                        posts = posts.await(),
                        comments = comments.await(),
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false) }
            }
        }
    }

    // Sequential with dependencies
    fun loadUserData(userId: String) {
        viewModelScope.launch {
            val user = fetchUser(userId)
            _uiState.update { it.copy(user = user) }

            // Depends on user data
            val posts = fetchPosts(user.id)
            _uiState.update { it.copy(posts = posts) }
        }
    }

    private suspend fun fetchUser(id: String): User {
        delay(500)
        return User(id)
    }

    private suspend fun fetchPosts(userId: String): List<Post> {
        delay(500)
        return emptyList()
    }

    private suspend fun fetchComments(userId: String): List<Comment> {
        delay(500)
        return emptyList()
    }
}
```

### Testing ViewModels with Coroutines

```kotlin
class ViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates state correctly`() = runTest {
        val viewModel = UserViewModel()

        viewModel.loadUser("123")

        // Wait for state update
        val state = viewModel.uiState.first { it is UserViewModel.UserState.Success }

        assertTrue(state is UserViewModel.UserState.Success)
    }

    @Test
    fun `search debounces correctly`() = runTest {
        val viewModel = SearchViewModel()

        viewModel.onSearchQueryChanged("a")
        viewModel.onSearchQueryChanged("ab")
        viewModel.onSearchQueryChanged("abc")

        // Advance time past debounce
        advanceTimeBy(400)

        // Should only search once
        val results = viewModel.searchResults.value
        assertTrue(results.isNotEmpty())
    }
}

// Test rule for Main dispatcher
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

### Common Anti-patterns

```kotlin
class AntiPatterns : ViewModel() {

    //  BAD: Exposing MutableStateFlow
    val badState = MutableStateFlow("data")

    //  GOOD: Expose read-only StateFlow
    private val _goodState = MutableStateFlow("data")
    val goodState: StateFlow<String> = _goodState.asStateFlow()

    //  BAD: Not handling cancellation
    fun badCancellation() {
        viewModelScope.launch {
            while (true) { // Infinite loop, ignores cancellation
                doWork()
            }
        }
    }

    //  GOOD: Respecting cancellation
    fun goodCancellation() {
        viewModelScope.launch {
            while (isActive) {
                doWork()
            }
        }
    }

    //  BAD: Launching in init without lifecycle awareness
    init {
        viewModelScope.launch {
            // This runs even if Activity is not visible
            collectFlowForever()
        }
    }

    //  GOOD: Let UI collect when ready
    val dataFlow: Flow<String> = flow {
        emit("data")
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = ""
    )

    private suspend fun doWork() {
        delay(100)
    }

    private suspend fun collectFlowForever() {
        flow { emit("data") }.collect { }
    }
}
```

---

## Ответ (RU)

ViewModel с корутинами обеспечивает мощный паттерн для управления асинхронными операциями с автоматическим управлением жизненным циклом.

### viewModelScope

`viewModelScope` - это CoroutineScope, привязанный к жизненному циклу ViewModel:
- Автоматически отменяется при `onCleared()`
- Использует `Dispatchers.Main.immediate`
- Не требует ручной очистки

### Лучшие Практики

```kotlin
class MyViewModel : ViewModel() {
    //  Использовать viewModelScope
    fun loadData() {
        viewModelScope.launch {
            // Автоматическая отмена
        }
    }

    //  StateFlow для состояния UI
    private val _state = MutableStateFlow(State())
    val state = _state.asStateFlow()

    //  Обработка ошибок
    fun load() {
        viewModelScope.launch {
            try {
                val data = fetchData()
            } catch (e: Exception) {
                // Обработка
            }
        }
    }
}
```

---

## Follow-up Questions (Следующие вопросы)

1. **How to test ViewModels with coroutines?**
2. **When to use StateFlow vs LiveData?**
3. **How to handle one-time events in ViewModels?**
4. **How to cancel specific coroutines in ViewModel?**
5. **How to share data between ViewModels?**

---

## References (Ссылки)

### Official Documentation
- [ViewModels with Coroutines](https://developer.android.com/topic/libraries/architecture/coroutines)
- [viewModelScope](https://developer.android.com/reference/kotlin/androidx/lifecycle/package-summary#(androidx.lifecycle.ViewModel).viewModelScope:kotlinx.coroutines.CoroutineScope)

---

## Related Questions (Связанные вопросы)

- [[q-lifecyclescope-viewmodelscope--kotlin--medium]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]

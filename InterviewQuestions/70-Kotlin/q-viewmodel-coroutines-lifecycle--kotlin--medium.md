---
id: kotlin-121
title: "ViewModel Coroutines and Lifecycle / Корутины в ViewModel и жизненный цикл"
aliases: ["ViewModel Coroutines and Lifecycle", "Корутины в ViewModel и жизненный цикл"]

# Classification
topic: kotlin
subtopics: [coroutines, lifecycle]
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
related: [c-coroutines, q-lifecyclescope-viewmodelscope--kotlin--medium, q-stateflow-sharedflow-android--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [android, coroutines, difficulty/medium, kotlin, lifecycle, viewmodel, viewmodelscope]
---
# Вопрос (RU)
> Как использовать корутины в `ViewModel`? Объясните `viewModelScope`, автоматическую отмену при `onCleared()`, лучшие практики запуска корутин и обработку изменений конфигурации.

# Question (EN)
> How to use coroutines in `ViewModel`? Explain `viewModelScope`, automatic cancellation on `onCleared()`, best practices for launching coroutines, and handling configuration changes.

---

## Ответ (RU)

ViewModel с корутинами обеспечивает мощный и безопасный паттерн для управления асинхронными операциями с учётом жизненного цикла.

### `viewModelScope`

`viewModelScope` — это `CoroutineScope`, привязанный к жизненному циклу `ViewModel`:
- Автоматически отменяется при вызове `onCleared()`.
- По умолчанию использует `Dispatchers.Main.immediate`.
- Не требует ручной отмены (`viewModelScope.cancel()` вызывать не нужно).

Пример:

```kotlin
class MyViewModel : ViewModel() {

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()

    data class State(val data: String = "", val error: Throwable? = null)

    // Используем viewModelScope для фоновой работы
    fun loadData() {
        viewModelScope.launch {
            try {
                val data = fetchData()
                _state.value = _state.value.copy(data = data, error = null)
            } catch (e: CancellationException) {
                throw e // корректно пробрасываем отмену
            } catch (t: Throwable) {
                _state.value = _state.value.copy(error = t)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(1000)
        return "data"
    }
}
```

### Корректное Управление Состоянием С `StateFlow`

```kotlin
class ProductsViewModel : ViewModel() {

    private val repository = ProductRepository()

    // StateFlow для UI-состояния
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    data class UiState(
        val products: List<Product> = emptyList(),
        val isLoading: Boolean = false,
        val error: String? = null
    )

    data class Product(val id: Int, val name: String, val price: Double)

    // Запускаем в viewModelScope
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

    // Обновление с индикатором загрузки и защитой от повторов
    fun refresh() {
        if (_uiState.value.isLoading) return
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

Ключевые идеи:
- Храните всё UI-состояние в одном `UiState`.
- Снаружи предоставляйте только `StateFlow`, внутренний `MutableStateFlow` не раскрывайте.
- Обновляйте состояние атомарно через `update { }`.

### Обработка Изменений Конфигурации

```kotlin
class ConfigurationSafeViewModel : ViewModel() {

    private val _searchResults = MutableStateFlow<List<String>>(emptyList())
    val searchResults: StateFlow<List<String>> = _searchResults.asStateFlow()

    // ViewModel переживает изменения конфигурации, корутина продолжает работу до onCleared()
    fun search(query: String) {
        viewModelScope.launch {
            val results = performSearch(query)
            _searchResults.value = results
        }
    }

    private suspend fun performSearch(query: String): List<String> {
        delay(500)
        return listOf("Result 1", "Result 2", "Result 3")
            .filter { it.contains(query, ignoreCase = true) }
    }
}

class SearchActivity : AppCompatActivity() {
    private val viewModel: ConfigurationSafeViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.searchResults.collect { results ->
                    updateUI(results)
                }
            }
        }

        viewModel.search("query")
    }

    private fun updateUI(results: List<String>) {
        // Обновление UI
    }
}
```

Ключевые моменты:
- `ViewModel` сохраняется при повороте экрана, данные и корутины не перезапускаются без необходимости.
- В UI слое используйте `lifecycleScope` + `repeatOnLifecycle`, чтобы избежать утечек.

### Паттерны Обработки Ошибок

```kotlin
class ErrorHandlingViewModel : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val data: String) : UiState()
        data class Error(val throwable: Throwable) : UiState()
    }

    // Паттерн 1: try-catch внутри launch
    fun loadDataWithTryCatch() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val data = fetchData()
                _uiState.value = UiState.Success(data)
            } catch (e: CancellationException) {
                throw e // всегда пробрасываем отмену
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }

    // Паттерн 2: CoroutineExceptionHandler для fire-and-forget задач
    fun loadDataWithHandler() {
        val handler = CoroutineExceptionHandler { _, throwable ->
            _uiState.value = UiState.Error(throwable)
        }

        viewModelScope.launch(handler) {
            val data = fetchData()
            _uiState.value = UiState.Success(data)
        }
    }

    // Паттерн 3: Result-обёртка
    sealed class Result<out T> {
        data class Success<T>(val data: T) : Result<T>()
        data class Error(val throwable: Throwable) : Result<Nothing>()
    }

    suspend fun fetchDataAsResult(): Result<String> = try {
        Result.Success(fetchData())
    } catch (t: Throwable) {
        Result.Error(t)
    }

    fun loadDataWithResult() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            when (val result = fetchDataAsResult()) {
                is Result.Success -> _uiState.value = UiState.Success(result.data)
                is Result.Error -> _uiState.value = UiState.Error(result.throwable)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(1000)
        return "Data"
    }
}
```

Основные правила:
- Не глушите `CancellationException`.
- Любые другие ошибки переводите в явное UI-состояние.

### Лучшие Практики Запуска Корутин

```kotlin
class BestPracticesViewModel : ViewModel() {

    private val _state = MutableStateFlow(State())
    val state = _state.asStateFlow()

    data class State(val data: String = "")

    // Хорошо: запускать во viewModelScope
    fun goodLaunch() {
        viewModelScope.launch {
            val result = fetchData()
            _state.update { it.copy(data = result) }
        }
    }

    // Плохо: собственный scope без отмены в onCleared()
    private val customScope = CoroutineScope(Dispatchers.Main)
    fun badCustomScope() {
        customScope.launch {
            // не будет автоматически отменён
        }
    }

    // Хорошо: использовать Dispatchers для тяжёлых задач
    fun goodDispatchers() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                fetchDataFromNetwork()
            }
            _state.update { it.copy(data = data) }
        }
    }

    // Плохо: блокировать поток через runBlocking
    fun badBlocking() {
        viewModelScope.launch {
            val data = runBlocking { // не делайте так
                fetchData()
            }
            _state.update { it.copy(data = data) }
        }
    }

    // Хорошо: проверять isActive и уважать отмену
    fun goodCancellable() {
        viewModelScope.launch {
            repeat(100) { i ->
                if (!isActive) return@launch
                processItem(i)
            }
        }
    }

    // Хорошо: одноразовые события через Channel
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

Кратко:
- Используйте только `viewModelScope` (или управляемые им дочерние корутины).
- Для тяжёлых операций переключайтесь на `Dispatchers.IO`/`Default`.
- Не блокируйте поток (`runBlocking`, долгие циклы без `isActive`).
- Для событий применяйте `Channel`/`SharedFlow`, а не состояние.

### Состояния Загрузки И Дебаунсинг

```kotlin
class SearchViewModel : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _searchResults = MutableStateFlow<List<String>>(emptyList())
    private val _isSearching = MutableStateFlow(false)

    val searchResults: StateFlow<List<String>> = _searchResults.asStateFlow()
    val isSearching: StateFlow<Boolean> = _isSearching.asStateFlow()

    private val searchRepository = SearchRepository()

    // Дебаунс поиска во viewModelScope, отменяется при onCleared()
    init {
        viewModelScope.launch {
            _searchQuery
                .debounce(300)
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

    class SearchRepository {
        suspend fun search(query: String): List<String> {
            delay(500)
            return listOf("Result 1", "Result 2")
        }
    }
}
```

Идеи:
- Не дёргайте сеть на каждый символ.
- Управляйте флагом загрузки через состояние, а не через побочные эффекты.

### Несколько Параллельных Операций

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

    // Параллельная загрузка данных
    fun loadUserProfile(userId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val userDeferred = async { fetchUser(userId) }
                val postsDeferred = async { fetchPosts(userId) }
                val commentsDeferred = async { fetchComments(userId) }

                _uiState.update {
                    it.copy(
                        user = userDeferred.await(),
                        posts = postsDeferred.await(),
                        comments = commentsDeferred.await(),
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false) }
            }
        }
    }

    // Последовательная загрузка с зависимостями
    fun loadUserData(userId: String) {
        viewModelScope.launch {
            val user = fetchUser(userId)
            _uiState.update { it.copy(user = user) }
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

Смысл:
- Используйте структурированную конкуренцию (`async` внутри `viewModelScope.launch`).
- При ошибке дочерние задачи корректно отменяются.

### Тестирование ViewModel С Корутинами

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class ViewModelTest {

    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates state correctly`() = runTest {
        val viewModel = UserViewModel()

        viewModel.loadUser("123")
        advanceUntilIdle()

        val state = viewModel.userState.value
        assertTrue(state is UserViewModel.UserState.Success)
    }

    @Test
    fun `search debounces correctly`() = runTest {
        val viewModel = SearchViewModel()

        viewModel.onSearchQueryChanged("a")
        viewModel.onSearchQueryChanged("ab")
        viewModel.onSearchQueryChanged("abc")

        advanceUntilIdle()

        val results = viewModel.searchResults.value
        assertTrue(results.isNotEmpty())
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
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

Идеи для тестов:
- Используйте `runTest` и тестовый диспетчер для детерминированного поведения корутин.
- Применяйте `advanceUntilIdle()` для выполнения всех задач.

### Распространённые Анти-паттерны

```kotlin
class AntiPatterns : ViewModel() {

    // Плохо: наружу отдаем MutableStateFlow — внешний код может сломать состояние
    val badState = MutableStateFlow("data")

    // Хорошо: наружу только StateFlow
    private val _goodState = MutableStateFlow("data")
    val goodState: StateFlow<String> = _goodState.asStateFlow()

    // Плохо: игнорировать отмену
    fun badCancellation() {
        viewModelScope.launch {
            while (true) {
                doWork()
            }
        }
    }

    // Хорошо: учитывать isActive
    fun goodCancellation() {
        viewModelScope.launch {
            while (isActive) {
                doWork()
            }
        }
    }

    // Плохо: вечной сбор в init без учета наблюдателей UI
    init {
        viewModelScope.launch {
            collectFlowForever()
        }
    }

    // Хорошо: использовать горячий flow с WhileSubscribed
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

Не делайте:
- Собственные `CoroutineScope` без отмены.
- Бесконечные циклы без проверки `isActive`.
- Экспорт `MutableStateFlow` напрямую.
- Долгие операции на главном потоке.

Также помните: для реактивных источников можно использовать и `LiveData`, но при новых сценариях предпочтителен `StateFlow`.

---

## Answer (EN)

ViewModels are Android's recommended architecture component for managing UI-related data across configuration changes. Combining ViewModels with coroutines provides a powerful pattern for handling asynchronous operations with automatic lifecycle management.

### viewModelScope Basics

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class UserViewModel : ViewModel() {

    private val _userState = MutableStateFlow<UserState>(UserState.Loading)
    val userState: StateFlow<UserState> = _userState.asStateFlow()

    // viewModelScope is automatically cancelled when ViewModel is cleared
    fun loadUser(userId: String) {
        viewModelScope.launch {
            try {
                val user = userRepository.getUser(userId)
                _userState.value = UserState.Success(user)
            } catch (e: CancellationException) {
                // Always rethrow cancellation to propagate it correctly
                throw e
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
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

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
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModel
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.viewModelScope
import android.os.Bundle
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ConfigurationSafeViewModel : ViewModel() {

    private val _searchResults = MutableStateFlow<List<String>>(emptyList())
    val searchResults: StateFlow<List<String>> = _searchResults.asStateFlow()

    // Survives configuration changes (rotation, etc.) because ViewModel is retained
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

        // Collect state with lifecycle awareness to avoid leaks
        lifecycleScope.launch {
            repeatOnLifecycle(androidx.lifecycle.Lifecycle.State.STARTED) {
                viewModel.searchResults.collect { results ->
                    updateUI(results)
                    // UI updates even after rotation
                }
            }
        }

        // Trigger search
        viewModel.search("query")
        // After rotation, results are still available via ViewModel
    }

    private fun updateUI(results: List<String>) {
        // Update UI
    }
}
```

### Error Handling Patterns

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class ErrorHandlingViewModel : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val data: String) : UiState()
        data class Error(val throwable: Throwable) : UiState()
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

    // Pattern 2: CoroutineExceptionHandler for fire-and-forget coroutines
    fun loadDataWithHandler() {
        val handler = CoroutineExceptionHandler { _, throwable ->
            // This only handles uncaught exceptions from the launched coroutine
            _uiState.value = UiState.Error(throwable)
        }

        viewModelScope.launch(handler) {
            val data = fetchData()
            _uiState.value = UiState.Success(data)
        }
    }

    // Pattern 3: Result wrapper
    sealed class Result<out T> {
        data class Success<T>(val data: T) : Result<T>()
        data class Error(val throwable: Throwable) : Result<Nothing>()
    }

    suspend fun fetchDataAsResult(): Result<String> = try {
        Result.Success(fetchData())
    } catch (t: Throwable) {
        Result.Error(t)
    }

    fun loadDataWithResult() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            when (val result = fetchDataAsResult()) {
                is Result.Success -> _uiState.value = UiState.Success(result.data)
                is Result.Error -> _uiState.value = UiState.Error(result.throwable)
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
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.flow.receiveAsFlow

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

    //  BAD: Creating own scope that is not cancelled in onCleared
    private val customScope = CoroutineScope(Dispatchers.Main)
    fun badCustomScope() {
        customScope.launch {
            // Won't be cancelled automatically when ViewModel is cleared
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
            val data = runBlocking { // DON'T DO THIS: blocks the coroutine and main thread
                fetchData()
            }
            _state.update { it.copy(data = data) }
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
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.launch

class SearchViewModel : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _searchResults = MutableStateFlow<List<String>>(emptyList())
    private val _isSearching = MutableStateFlow(false)

    val searchResults: StateFlow<List<String>> = _searchResults.asStateFlow()
    val isSearching: StateFlow<Boolean> = _isSearching.asStateFlow()

    private val searchRepository = SearchRepository()

    // Debounced search inside viewModelScope, automatically cancelled on onCleared()
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
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

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
                // Run in parallel; if one fails, siblings are cancelled due to structured concurrency
                val userDeferred = async { fetchUser(userId) }
                val postsDeferred = async { fetchPosts(userId) }
                val commentsDeferred = async { fetchComments(userId) }

                _uiState.update {
                    it.copy(
                        user = userDeferred.await(),
                        posts = postsDeferred.await(),
                        comments = commentsDeferred.await(),
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
import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestDispatcher
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import kotlinx.coroutines.test.advanceUntilIdle
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TestWatcher
import org.junit.runner.Description

@OptIn(ExperimentalCoroutinesApi::class)
class ViewModelTest {

    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates state correctly`() = runTest {
        val viewModel = UserViewModel()

        viewModel.loadUser("123")

        // Let coroutines run
        advanceUntilIdle()

        val state = viewModel.userState.value
        assertTrue(state is UserViewModel.UserState.Success)
    }

    @Test
    fun `search debounces correctly`() = runTest {
        val viewModel = SearchViewModel()

        viewModel.onSearchQueryChanged("a")
        viewModel.onSearchQueryChanged("ab")
        viewModel.onSearchQueryChanged("abc")

        // Advance time past debounce and network delay
        advanceUntilIdle()

        val results = viewModel.searchResults.value
        assertTrue(results.isNotEmpty())
    }
}

// Test rule for Main dispatcher
@OptIn(ExperimentalCoroutinesApi::class)
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
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.SharingStarted

class AntiPatterns : ViewModel() {

    //  BAD: Exposing MutableStateFlow (external code can mutate ViewModel state)
    val badState = MutableStateFlow("data")

    //  GOOD: Expose read-only StateFlow
    private val _goodState = MutableStateFlow("data")
    val goodState: StateFlow<String> = _goodState.asStateFlow()

    //  BAD: Not handling cancellation
    fun badCancellation() {
        viewModelScope.launch {
            while (true) { // Infinite loop, ignores cancellation and can leak
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

    //  BAD: Launching in init without considering UI lifecycle
    init {
        viewModelScope.launch {
            // This runs as long as ViewModel exists, even if no UI is observing
            collectFlowForever()
        }
    }

    //  GOOD: Let UI collect when ready; use hot flow with controlled sharing
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

## Follow-ups

1. How to test ViewModels with coroutines?
2. When to use `StateFlow` vs `LiveData`?
3. How to handle one-time events in ViewModels?
4. How to cancel specific coroutines in ViewModel?
5. How to share data between ViewModels?

---

## References (Ссылки)

### Official Documentation
- [ViewModels with Coroutines](https://developer.android.com/topic/libraries/architecture/coroutines)
- [viewModelScope](https://developer.android.com/reference/kotlin/androidx/lifecycle/package-summary#(androidx.lifecycle.ViewModel).viewModelScope:kotlinx.coroutines.CoroutineScope)

- [[c-coroutines]]

---

## Related Questions (Связанные вопросы)

- [[q-lifecyclescope-viewmodelscope--kotlin--medium]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]

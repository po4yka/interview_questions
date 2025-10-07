---
id: 20251006-debounce-search-coroutines
title: Debouncing Search with Coroutines / Отложенный Поиск с Корутинами
topic: kotlin
subtopics:
  - coroutines
  - debouncing
  - search
  - job-cancellation
difficulty: medium
language_tags:
  - en
  - ru
original_language: en
status: reviewed
source: Kotlin Coroutines Interview Questions PDF
tags:
  - kotlin
  - coroutines
  - debouncing
  - search
  - job
  - cancellation
  - android
  - difficulty/medium
---
## Question (EN)
> How would you implement a search-as-you-type feature with debouncing using Kotlin coroutines?
## Вопрос (RU)
> Как реализовать функцию поиска при вводе с отложенным выполнением (debouncing) используя Kotlin корутины?

---

## Answer (EN)

**Debouncing** is a technique to delay execution until the user stops typing, preventing excessive API calls or expensive operations on every keystroke.

### The Problem Without Debouncing

```kotlin
// ❌ BAD: API call on every keystroke
searchEditText.addTextChangedListener { text ->
    // User types "android" → 7 API calls!
    // "a", "an", "and", "andr", "andro", "androi", "android"
    performSearch(text.toString())
}
```

**Issues**:
- Excessive network requests (one per character)
- Wasted bandwidth and battery
- Backend overload
- Poor UX (results flickering)
- Potential rate limiting

### Solution 1: Basic Debouncing with Job Cancellation

**Pattern**: Cancel previous search job when new input arrives.

```kotlin
class SearchActivity : AppCompatActivity() {
    private var searchJob: Job? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        searchEditText.addTextChangedListener { text ->
            // Cancel previous search
            searchJob?.cancel()

            // Launch new search with delay
            searchJob = lifecycleScope.launch {
                delay(300) // Wait 300ms

                // If user keeps typing, this line never executes
                // (job canceled by next keystroke)
                performSearch(text.toString())
            }
        }
    }

    private suspend fun performSearch(query: String) {
        if (query.isBlank()) return

        val results = withContext(Dispatchers.IO) {
            searchRepository.search(query)
        }

        displayResults(results)
    }
}
```

**How It Works**:
1. User types "a" → Job1 starts, delay(300ms)
2. User types "n" (150ms later) → Job1 canceled, Job2 starts
3. User types "d" (150ms later) → Job2 canceled, Job3 starts
4. User stops typing → Job3 completes after 300ms
5. API call made only once with "and"

**Benefits**:
- Only 1 API call instead of 3
- Automatically cancels stale searches
- Simple implementation
- Lifecycle-aware with lifecycleScope

### Solution 2: ViewModel Implementation

**Better Architecture**: Move logic to ViewModel for testability and lifecycle independence.

```kotlin
class SearchViewModel : ViewModel() {
    private var searchJob: Job? = null

    private val _searchResults = MutableStateFlow<List<SearchResult>>(emptyList())
    val searchResults: StateFlow<List<SearchResult>> = _searchResults

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    fun onSearchQueryChanged(query: String) {
        // Cancel previous search
        searchJob?.cancel()

        if (query.isBlank()) {
            _searchResults.value = emptyList()
            return
        }

        searchJob = viewModelScope.launch {
            delay(300) // Debounce delay

            _isLoading.value = true

            try {
                val results = searchRepository.search(query)
                _searchResults.value = results
            } catch (e: CancellationException) {
                // Ignore cancellation - expected behavior
                throw e
            } catch (e: Exception) {
                // Handle other errors
                _searchResults.value = emptyList()
            } finally {
                _isLoading.value = false
            }
        }
    }
}

// In Activity/Fragment
class SearchActivity : AppCompatActivity() {
    private val viewModel: SearchViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        searchEditText.addTextChangedListener { text ->
            viewModel.onSearchQueryChanged(text.toString())
        }

        lifecycleScope.launch {
            viewModel.searchResults.collect { results ->
                displayResults(results)
            }
        }

        lifecycleScope.launch {
            viewModel.isLoading.collect { isLoading ->
                progressBar.isVisible = isLoading
            }
        }
    }
}
```

**Benefits**:
- Survives configuration changes (rotation)
- Testable with TestDispatcher
- Separation of concerns
- Loading state management

### Solution 3: Flow-Based Debouncing (Most Elegant)

**Using Flow operators** for declarative debouncing.

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = searchQuery
        .debounce(300) // Wait 300ms after last emission
        .filter { it.isNotBlank() } // Ignore blank queries
        .distinctUntilChanged() // Ignore repeated queries
        .flatMapLatest { query ->
            // Cancel previous search automatically
            flow {
                emit(searchRepository.search(query))
            }.catch { e ->
                // Handle errors
                emit(emptyList())
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

**Flow Operators Explained**:
- `debounce(300)`: Waits 300ms of inactivity before emitting
- `filter { it.isNotBlank() }`: Skips empty queries
- `distinctUntilChanged()`: Prevents duplicate searches
- `flatMapLatest`: Cancels previous search when new query arrives
- `stateIn`: Converts Flow to StateFlow for UI observation

**Benefits**:
- Declarative, readable code
- Automatic cancellation
- Built-in error handling
- No manual Job management
- Composable operators

### Solution 4: Advanced - Minimum Search Length

**Practical Enhancement**: Only search for queries with minimum length.

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    private val _searchState = MutableStateFlow<SearchState>(SearchState.Idle)
    val searchState: StateFlow<SearchState> = _searchState

    val searchResults: StateFlow<List<SearchResult>> = searchQuery
        .debounce(300)
        .filter { it.length >= 3 } // At least 3 characters
        .distinctUntilChanged()
        .onEach { _searchState.value = SearchState.Loading }
        .flatMapLatest { query ->
            flow {
                val results = searchRepository.search(query)
                _searchState.value = SearchState.Success(results.size)
                emit(results)
            }.catch { e ->
                _searchState.value = SearchState.Error(e.message ?: "Unknown error")
                emit(emptyList())
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}

sealed class SearchState {
    object Idle : SearchState()
    object Loading : SearchState()
    data class Success(val resultCount: Int) : SearchState()
    data class Error(val message: String) : SearchState()
}
```

### Solution 5: Custom Debounce Function

**Reusable Extension**: Create custom debounce function.

```kotlin
fun <T> Flow<T>.debounceAfterFirst(
    waitMillis: Long,
    skipFirst: Boolean = false
): Flow<T> = flow {
    coroutineScope {
        val debounceJob: Job? = null
        var firstEmitted = false

        collect { value ->
            if (!firstEmitted && !skipFirst) {
                // Emit first value immediately
                emit(value)
                firstEmitted = true
            } else {
                // Debounce subsequent values
                debounceJob?.cancel()
                launch {
                    delay(waitMillis)
                    emit(value)
                }
            }
        }
    }
}

// Usage
searchQuery
    .debounceAfterFirst(300, skipFirst = false)
    .collect { query ->
        performSearch(query)
    }
```

### Testing Debounced Search

```kotlin
class SearchViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: SearchViewModel
    private val testRepository = FakeSearchRepository()

    @Before
    fun setup() {
        viewModel = SearchViewModel(testRepository)
    }

    @Test
    fun `debounce prevents multiple searches`() = runTest {
        // Type quickly: "android"
        viewModel.onSearchQueryChanged("a")
        advanceTimeBy(100)

        viewModel.onSearchQueryChanged("an")
        advanceTimeBy(100)

        viewModel.onSearchQueryChanged("and")
        advanceTimeBy(100)

        viewModel.onSearchQueryChanged("android")

        // Only 1 search should happen after debounce
        advanceTimeBy(300)

        assertEquals(1, testRepository.searchCallCount)
        assertEquals("android", testRepository.lastQuery)
    }

    @Test
    fun `typing pause triggers search`() = runTest {
        viewModel.onSearchQueryChanged("kotlin")

        // Wait for debounce
        advanceTimeBy(300)

        assertEquals(1, testRepository.searchCallCount)
        assertEquals("kotlin", testRepository.lastQuery)
    }
}
```

### Comparison of Approaches

| Approach | Complexity | Testability | Features | Best For |
|----------|-----------|-------------|----------|----------|
| **Job Cancellation** | Low | Medium | Basic debouncing | Simple cases, learning |
| **ViewModel + Job** | Medium | High | + State management | Production Android apps |
| **Flow debounce()** | Low | High | Declarative, clean | Modern Kotlin codebases |
| **Flow + operators** | Medium | High | Full-featured | Complex search UIs |

### Best Practices

```kotlin
// ✅ DO: Use appropriate debounce delay
searchQuery.debounce(300) // 300ms is standard for search

// ✅ DO: Filter blank queries
.filter { it.isNotBlank() }

// ✅ DO: Prevent duplicate searches
.distinctUntilChanged()

// ✅ DO: Handle cancellation properly
catch (e: CancellationException) {
    throw e // Re-throw cancellation
}

// ✅ DO: Show loading state
onEach { _isLoading.value = true }

// ❌ DON'T: Use too short delay
searchQuery.debounce(50) // Too aggressive

// ❌ DON'T: Use too long delay
searchQuery.debounce(1000) // Feels unresponsive

// ❌ DON'T: Forget to cancel previous job
searchJob = launch { ... } // Lost reference to previous job!
```

### Summary

**Debouncing with Coroutines**:
- ✅ **Job Cancellation**: Simple pattern, cancel previous search when new input arrives
- ✅ **delay(300)**: Standard debounce time for search
- ✅ **Flow.debounce()**: Declarative, operator-based approach
- ✅ **flatMapLatest**: Automatic cancellation of previous search
- ✅ **distinctUntilChanged()**: Prevents duplicate searches
- ✅ **Testable**: Use TestDispatcher and advanceTimeBy()

**Key Pattern**:
```kotlin
searchQuery
    .debounce(300)           // Wait for typing pause
    .filter { it.length >= 3 } // Minimum query length
    .distinctUntilChanged()   // Skip duplicates
    .flatMapLatest { query -> // Cancel previous search
        performSearch(query)
    }
```

---

## Ответ (RU)

**Debouncing (отложенное выполнение)** - это техника задержки выполнения до тех пор, пока пользователь не прекратит печатать, предотвращающая избыточные вызовы API или дорогие операции на каждое нажатие клавиши.

### Проблема Без Debouncing

```kotlin
// ❌ ПЛОХО: Вызов API на каждое нажатие клавиши
searchEditText.addTextChangedListener { text ->
    // Пользователь печатает "android" → 7 вызовов API!
    // "a", "an", "and", "andr", "andro", "androi", "android"
    performSearch(text.toString())
}
```

**Проблемы**:
- Избыточные сетевые запросы (один на символ)
- Потраченный трафик и батарея
- Перегрузка бэкенда
- Плохой UX (мерцающие результаты)
- Возможные ограничения по частоте запросов

### Решение 1: Базовый Debouncing с Отменой Job

**Паттерн**: Отменять предыдущую задачу поиска при новом вводе.

```kotlin
class SearchActivity : AppCompatActivity() {
    private var searchJob: Job? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        searchEditText.addTextChangedListener { text ->
            // Отменить предыдущий поиск
            searchJob?.cancel()

            // Запустить новый поиск с задержкой
            searchJob = lifecycleScope.launch {
                delay(300) // Ждать 300мс

                // Если пользователь продолжает печатать, эта строка не выполнится
                // (job отменен следующим нажатием)
                performSearch(text.toString())
            }
        }
    }

    private suspend fun performSearch(query: String) {
        if (query.isBlank()) return

        val results = withContext(Dispatchers.IO) {
            searchRepository.search(query)
        }

        displayResults(results)
    }
}
```

**Как Это Работает**:
1. Пользователь печатает "a" → Job1 стартует, delay(300мс)
2. Пользователь печатает "n" (через 150мс) → Job1 отменен, Job2 стартует
3. Пользователь печатает "d" (через 150мс) → Job2 отменен, Job3 стартует
4. Пользователь прекращает печатать → Job3 завершается через 300мс
5. Вызов API сделан только один раз с "and"

**Преимущества**:
- Только 1 вызов API вместо 3
- Автоматически отменяет устаревшие поиски
- Простая реализация
- Учитывает жизненный цикл с lifecycleScope

### Решение 2: Реализация в ViewModel

**Лучшая Архитектура**: Переместить логику в ViewModel для тестируемости и независимости от жизненного цикла.

```kotlin
class SearchViewModel : ViewModel() {
    private var searchJob: Job? = null

    private val _searchResults = MutableStateFlow<List<SearchResult>>(emptyList())
    val searchResults: StateFlow<List<SearchResult>> = _searchResults

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    fun onSearchQueryChanged(query: String) {
        // Отменить предыдущий поиск
        searchJob?.cancel()

        if (query.isBlank()) {
            _searchResults.value = emptyList()
            return
        }

        searchJob = viewModelScope.launch {
            delay(300) // Задержка debounce

            _isLoading.value = true

            try {
                val results = searchRepository.search(query)
                _searchResults.value = results
            } catch (e: CancellationException) {
                // Игнорировать отмену - ожидаемое поведение
                throw e
            } catch (e: Exception) {
                // Обработать другие ошибки
                _searchResults.value = emptyList()
            } finally {
                _isLoading.value = false
            }
        }
    }
}
```

**Преимущества**:
- Переживает изменения конфигурации (поворот)
- Тестируется с TestDispatcher
- Разделение ответственности
- Управление состоянием загрузки

### Решение 3: Debouncing на Основе Flow (Наиболее Элегантное)

**Использование операторов Flow** для декларативного debouncing.

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = searchQuery
        .debounce(300) // Ждать 300мс после последнего ввода
        .filter { it.isNotBlank() } // Игнорировать пустые запросы
        .distinctUntilChanged() // Игнорировать повторяющиеся запросы
        .flatMapLatest { query ->
            // Отменить предыдущий поиск автоматически
            flow {
                emit(searchRepository.search(query))
            }.catch { e ->
                // Обработать ошибки
                emit(emptyList())
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

**Объяснение Операторов Flow**:
- `debounce(300)`: Ждет 300мс без активности перед отправкой
- `filter { it.isNotBlank() }`: Пропускает пустые запросы
- `distinctUntilChanged()`: Предотвращает дублирующиеся поиски
- `flatMapLatest`: Отменяет предыдущий поиск при новом запросе
- `stateIn`: Конвертирует Flow в StateFlow для наблюдения из UI

**Преимущества**:
- Декларативный, читаемый код
- Автоматическая отмена
- Встроенная обработка ошибок
- Нет ручного управления Job
- Композируемые операторы

### Резюме

**Debouncing с Корутинами**:
- ✅ **Отмена Job**: Простой паттерн, отмена предыдущего поиска при новом вводе
- ✅ **delay(300)**: Стандартное время debounce для поиска
- ✅ **Flow.debounce()**: Декларативный подход на основе операторов
- ✅ **flatMapLatest**: Автоматическая отмена предыдущего поиска
- ✅ **distinctUntilChanged()**: Предотвращает дублирующиеся поиски
- ✅ **Тестируемость**: Используйте TestDispatcher и advanceTimeBy()

**Ключевой Паттерн**:
```kotlin
searchQuery
    .debounce(300)           // Ждать паузы в печати
    .filter { it.length >= 3 } // Минимальная длина запроса
    .distinctUntilChanged()   // Пропустить дубликаты
    .flatMapLatest { query -> // Отменить предыдущий поиск
        performSearch(query)
    }
```

---

## References

- [Flow debounce - Kotlin Docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/debounce.html)
- [Search with coroutines - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow#make-cold-flows-hot)
- [Job Cancellation - Kotlin Docs](https://kotlinlang.org/docs/cancellation-and-timeouts.html)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF

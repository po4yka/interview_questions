---
id: 20251006-100003
title: "How to implement instant search using Flow operators? / Как реализовать мгновенный поиск с помощью Flow операторов?"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, operators, debounce, distinctuntilchanged, search]
question_kind: pattern
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [flow-operators, debounce, search-optimization, performance]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, flow, search, debounce, operators, performance, difficulty/medium]
---
# Question (EN)
> How do you implement instant/real-time search functionality using Kotlin Flow operators?
# Вопрос (RU)
> Как реализовать функциональность мгновенного/реального поиска с помощью операторов Kotlin Flow?

---

## Answer (EN)

Instant search is a common UX pattern that requires efficient handling of user input, debouncing, and API calls. Kotlin Flow provides powerful operators to implement this elegantly.

### 1. Basic Instant Search Implementation

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.FlowPreview
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope

class SearchViewModel @Inject constructor(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val searchQuery = MutableStateFlow("")

    @OptIn(FlowPreview::class)
    val searchResults: StateFlow<List<SearchResult>> = searchQuery
        .debounce(300) // Wait 300ms after user stops typing
        .distinctUntilChanged() // Only emit when query actually changes
        .filter { it.length >= 2 } // Minimum 2 characters
        .mapLatest { query -> // Cancel previous search if new query arrives
            searchRepository.search(query)
        }
        .catch { emit(emptyList()) } // Handle errors gracefully
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

### 2. Complete Search with Loading and Error States

```kotlin
sealed class SearchUiState {
    object Idle : SearchUiState()
    object Loading : SearchUiState()
    data class Success(val results: List<SearchResult>) : SearchUiState()
    data class Error(val message: String) : SearchUiState()
}

class AdvancedSearchViewModel @Inject constructor(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    @OptIn(FlowPreview::class)
    val searchState: StateFlow<SearchUiState> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .map { query ->
            when {
                query.isBlank() -> SearchUiState.Idle
                query.length < 2 -> SearchUiState.Idle
                else -> {
                    // Emit loading state
                    SearchUiState.Loading
                }
            }
        }
        .filter { it is SearchUiState.Loading }
        .mapLatest {
            val query = _searchQuery.value
            try {
                val results = repository.search(query)
                SearchUiState.Success(results)
            } catch (e: Exception) {
                SearchUiState.Error(e.message ?: "Unknown error")
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = SearchUiState.Idle
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }
}
```

### 3. Search with Network Status and Retry

```kotlin
class NetworkAwareSearchViewModel @Inject constructor(
    private val repository: SearchRepository,
    private val networkMonitor: NetworkMonitor
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _retryTrigger = MutableSharedFlow<Unit>()

    @OptIn(FlowPreview::class)
    val searchResults = combine(
        _searchQuery
            .debounce(300)
            .distinctUntilChanged()
            .filter { it.length >= 2 },
        _retryTrigger.onStart { emit(Unit) }, // Initial trigger
        networkMonitor.isOnline
    ) { query, _, isOnline ->
        Triple(query, Unit, isOnline)
    }
        .mapLatest { (query, _, isOnline) ->
            when {
                !isOnline -> SearchResult.NetworkError
                else -> {
                    try {
                        SearchResult.Success(repository.search(query))
                    } catch (e: Exception) {
                        SearchResult.ApiError(e.message)
                    }
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = SearchResult.Idle
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }

    fun retry() {
        viewModelScope.launch {
            _retryTrigger.emit(Unit)
        }
    }
}
```

### 4. Multi-Source Search (Local + Remote)

```kotlin
class HybridSearchViewModel @Inject constructor(
    private val localRepository: LocalSearchRepository,
    private val remoteRepository: RemoteSearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    @OptIn(FlowPreview::class)
    val searchResults: StateFlow<SearchResults> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            combine(
                // Local search (instant)
                flow { emit(localRepository.search(query)) }
                    .onStart { emit(emptyList()) },
                // Remote search (with delay)
                flow { emit(remoteRepository.search(query)) }
                    .onStart { emit(emptyList()) }
                    .catch { emit(emptyList()) }
            ) { local, remote ->
                SearchResults(
                    localResults = local,
                    remoteResults = remote,
                    isLoading = remote.isEmpty() && query.isNotEmpty()
                )
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = SearchResults()
        )

    fun onQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

data class SearchResults(
    val localResults: List<SearchResult> = emptyList(),
    val remoteResults: List<SearchResult> = emptyList(),
    val isLoading: Boolean = false
)
```

### 5. Search with Suggestions and Recent Searches

```kotlin
class SmartSearchViewModel @Inject constructor(
    private val repository: SearchRepository,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    @OptIn(FlowPreview::class)
    val searchSuggestions = _searchQuery
        .debounce(200) // Faster for suggestions
        .distinctUntilChanged()
        .flatMapLatest { query ->
            when {
                query.isBlank() -> {
                    // Show recent searches
                    preferencesRepository.getRecentSearches()
                }
                query.length < 2 -> {
                    flowOf(emptyList())
                }
                else -> {
                    // Show suggestions
                    flow { emit(repository.getSuggestions(query)) }
                        .catch { emit(emptyList()) }
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    fun onQueryChanged(query: String) {
        _searchQuery.value = query
    }

    fun onSearchExecuted(query: String) {
        viewModelScope.launch {
            preferencesRepository.addRecentSearch(query)
        }
    }
}
```

### 6. Composable UI Integration

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val searchQuery by viewModel.searchQuery.collectAsStateWithLifecycle()
    val searchState by viewModel.searchState.collectAsStateWithLifecycle()

    Column(modifier = Modifier.fillMaxSize()) {
        SearchBar(
            query = searchQuery,
            onQueryChange = viewModel::updateQuery,
            modifier = Modifier.fillMaxWidth()
        )

        when (searchState) {
            is SearchUiState.Idle -> {
                EmptySearchState()
            }
            is SearchUiState.Loading -> {
                LoadingIndicator()
            }
            is SearchUiState.Success -> {
                SearchResultsList(
                    results = (searchState as SearchUiState.Success).results
                )
            }
            is SearchUiState.Error -> {
                ErrorState(
                    message = (searchState as SearchUiState.Error).message,
                    onRetry = { viewModel.retry() }
                )
            }
        }
    }
}

@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    TextField(
        value = query,
        onValueChange = onQueryChange,
        placeholder = { Text("Search...") },
        leadingIcon = {
            Icon(Icons.Default.Search, contentDescription = "Search")
        },
        trailingIcon = {
            if (query.isNotEmpty()) {
                IconButton(onClick = { onQueryChange("") }) {
                    Icon(Icons.Default.Clear, contentDescription = "Clear")
                }
            }
        },
        modifier = modifier,
        singleLine = true
    )
}
```

### 7. Advanced: Search with Filters

```kotlin
class FilteredSearchViewModel @Inject constructor(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _filters = MutableStateFlow(SearchFilters())

    data class SearchFilters(
        val category: String? = null,
        val priceRange: IntRange? = null,
        val sortBy: SortOption = SortOption.RELEVANCE
    )

    @OptIn(FlowPreview::class)
    val searchResults = combine(
        _searchQuery.debounce(300).distinctUntilChanged(),
        _filters
    ) { query, filters ->
        query to filters
    }
        .filter { (query, _) -> query.length >= 2 }
        .mapLatest { (query, filters) ->
            repository.search(
                query = query,
                category = filters.category,
                priceRange = filters.priceRange,
                sortBy = filters.sortBy
            )
        }
        .catch { emit(emptyList()) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }

    fun updateFilters(filters: SearchFilters) {
        _filters.value = filters
    }
}
```

### 8. Performance Optimizations

```kotlin
@OptIn(FlowPreview::class)
class OptimizedSearchViewModel @Inject constructor(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    val searchResults = _searchQuery
        // Debounce to reduce API calls
        .debounce(300)
        // Avoid duplicate searches
        .distinctUntilChanged()
        // Filter short queries
        .filter { it.length >= 2 }
        // Cancel previous search if new one starts
        .mapLatest { query ->
            withContext(Dispatchers.IO) {
                repository.search(query)
            }
        }
        // Transform to UI state
        .map { results ->
            SearchUiState.Success(results)
        }
        // Handle errors
        .catch { error ->
            emit(SearchUiState.Error(error.message ?: "Unknown error"))
        }
        // Add loading state at the beginning
        .onStart { emit(SearchUiState.Loading) }
        // Share across collectors
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = SearchUiState.Idle
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }
}
```

### 9. Testing

```kotlin
@Test
fun `search debounces user input`() = runTest {
    val viewModel = SearchViewModel(fakeRepository)
    val states = mutableListOf<SearchUiState>()

    val job = launch {
        viewModel.searchState.toList(states)
    }

    // Simulate rapid typing
    viewModel.updateQuery("a")
    advanceTimeBy(100)
    viewModel.updateQuery("ab")
    advanceTimeBy(100)
    viewModel.updateQuery("abc")
    advanceTimeBy(400) // Wait for debounce

    // Should only search once for "abc"
    assertEquals(1, fakeRepository.searchCallCount)
    assertEquals("abc", fakeRepository.lastQuery)

    job.cancel()
}
```

### 10. Best Practices Summary

| Operator | Purpose | Typical Value |
|----------|---------|---------------|
| `debounce` | Wait for user to stop typing | 300-500ms |
| `distinctUntilChanged` | Avoid duplicate searches | Always use |
| `filter` | Minimum query length | 2-3 characters |
| `mapLatest` | Cancel previous search | For API calls |
| `catch` | Handle errors gracefully | Always use |
| `stateIn` | Share Flow across collectors | WhileSubscribed |

#### - DO:

- Use `debounce` to reduce API calls
- Add minimum character filter
- Cancel previous searches with `mapLatest`
- Handle empty/error states
- Show loading indicators
- Cache recent searches

#### - DON'T:

- Don't search on every keystroke
- Don't ignore cancellation
- Don't forget error handling
- Don't use `GlobalScope`
- Don't block the main thread

---

## Ответ (RU)

Мгновенный поиск - распространенный UX паттерн, требующий эффективной обработки пользовательского ввода, дебаунсинга и API вызовов.

### 1. Базовая реализация

```kotlin
@OptIn(FlowPreview::class)
val searchResults = searchQuery
    .debounce(300) // Ждем 300мс после остановки ввода
    .distinctUntilChanged() // Только при изменении запроса
    .filter { it.length >= 2 } // Минимум 2 символа
    .mapLatest { query ->
        searchRepository.search(query)
    }
    .catch { emit(emptyList()) }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(), emptyList())
```

### 2. С состояниями загрузки и ошибок

```kotlin
val searchState = _searchQuery
    .debounce(300)
    .distinctUntilChanged()
    .mapLatest { query ->
        try {
            SearchUiState.Success(repository.search(query))
        } catch (e: Exception) {
            SearchUiState.Error(e.message ?: "Unknown error")
        }
    }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(), SearchUiState.Idle)
```

### 3. Гибридный поиск (локальный + удаленный)

```kotlin
val searchResults = _searchQuery
    .flatMapLatest { query ->
        combine(
            localRepository.search(query),
            remoteRepository.search(query)
        ) { local, remote ->
            SearchResults(local, remote)
        }
    }
```

### Таблица операторов

| Оператор | Назначение | Типичное значение |
|----------|-----------|-------------------|
| `debounce` | Ожидание остановки ввода | 300-500мс |
| `distinctUntilChanged` | Избежание дубликатов | Всегда |
| `filter` | Минимальная длина | 2-3 символа |
| `mapLatest` | Отмена предыдущих запросов | Для API |

### Лучшие практики

#### - ДЕЛАЙТЕ:

- Используйте debounce для сокращения API вызовов
- Добавляйте фильтр минимальной длины
- Отменяйте предыдущие поиски через mapLatest
- Обрабатывайте пустые/ошибочные состояния

#### - НЕ ДЕЛАЙТЕ:

- Не ищите при каждом нажатии клавиши
- Не игнорируйте отмену
- Не забывайте обработку ошибок

---

## Related Questions

### Related (Medium)
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow
- [[q-retry-operators-flow--kotlin--medium]] - Flow
- [[q-flow-time-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## References
- [Flow Operators Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)
- [debounce Operator](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/debounce.html)

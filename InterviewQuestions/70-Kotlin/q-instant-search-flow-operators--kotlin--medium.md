---
anki_cards:
- slug: q-instant-search-flow-operators--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-instant-search-flow-operators--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-036
title: "How to implement instant search using Flow operators? / Как реализовать мгновенный поиск с помощью Flow операторов?"
aliases: ["How to implement instant search using Flow operators?", "Как реализовать мгновенный поиск с помощью Flow операторов?"]

# Classification
topic: kotlin
subtopics: [flow]
question_kind: coding
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin]

# Timestamps
created: 2025-10-06
updated: 2025-11-09

tags: [debounce, difficulty/medium, flow, kotlin, operators, performance, search]
---\
# Вопрос (RU)
> Как реализовать функциональность мгновенного/реального поиска с помощью операторов Kotlin `Flow`?

---

# Question (EN)
> How do you implement instant/real-time search functionality using Kotlin `Flow` operators?

---

## Ответ (RU)

Мгновенный поиск — распространенный UX-паттерн, требующий эффективной обработки пользовательского ввода, дебаунсинга и отменяемых API-запросов. Kotlin `Flow` предоставляет мощные операторы для реализации таких сценариев.

Ниже приведены основные паттерны реализации. Типы вроде `SearchResult`, `SearchUiState`, `SearchResults`, `NetworkMonitor` и репозитории предполагаются определенными в проекте.

### 1. Базовая Реализация Мгновенного Поиска

```kotlin
import kotlinx.coroutines.flow.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope

class SearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val searchResults: StateFlow<List<SearchResult>> = searchQuery
        .debounce(300) // Ждем 300 мс после остановки ввода
        .distinctUntilChanged() // Только при фактическом изменении запроса
        .filter { it.length >= 2 } // Минимум 2 символа
        .mapLatest { query -> // Отменяем предыдущий запрос при новом вводе
            searchRepository.search(query)
        }
        .catch { emit(emptyList()) } // Обработка ошибок
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

Ключевые моменты:
- `debounce` уменьшает количество запросов.
- `distinctUntilChanged` предотвращает повторный поиск для того же текста.
- `filter` накладывает минимальную длину запроса.
- `mapLatest` обеспечивает отмену предыдущего поиска при новом вводе.
- `catch` позволяет обработать ошибки и вернуть безопасное значение.

### 2. Поиск С Состояниями Загрузки И Ошибок

```kotlin
sealed class SearchUiState {
    object Idle : SearchUiState()
    object Loading : SearchUiState()
    data class Success(val results: List<SearchResult>) : SearchUiState()
    data class Error(val message: String) : SearchUiState()
}

class SearchWithStateViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val searchState: StateFlow<SearchUiState> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { query ->
            when {
                query.isBlank() || query.length < 2 -> {
                    flowOf(SearchUiState.Idle)
                }
                else -> {
                    flow {
                        emit(SearchUiState.Loading)
                        try {
                            val results = repository.search(query)
                            emit(SearchUiState.Success(results))
                        } catch (e: Exception) {
                            emit(
                                SearchUiState.Error(
                                    e.message ?: "Unknown error"
                                )
                            )
                        }
                    }
                }
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

### 3. Поиск С Учетом Сети И Повторными Попытками

Предполагается, что `SearchResultState` — это иерархия UI-состояний.

```kotlin
sealed class SearchResultState {
    object Idle : SearchResultState()
    object Loading : SearchResultState()
    data class Success(val results: List<SearchResult>) : SearchResultState()
    data class NetworkError(val message: String) : SearchResultState()
    data class ApiError(val message: String) : SearchResultState()
}

class NetworkAwareSearchViewModel(
    private val repository: SearchRepository,
    private val networkMonitor: NetworkMonitor
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _retryTrigger = MutableSharedFlow<Unit>(extraBufferCapacity = 1)

    val searchState: StateFlow<SearchResultState> = combine(
        _searchQuery
            .debounce(300)
            .distinctUntilChanged()
            .filter { it.length >= 2 },
        _retryTrigger.onStart { emit(Unit) },
        networkMonitor.isOnline
    ) { query, _, isOnline ->
        query to isOnline
    }
        .mapLatest { (query, isOnline) ->
            if (!isOnline) {
                SearchResultState.NetworkError("No internet connection")
            } else {
                try {
                    val results = repository.search(query)
                    SearchResultState.Success(results)
                } catch (e: Exception) {
                    SearchResultState.ApiError(
                        e.message ?: "Unknown error"
                    )
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = SearchResultState.Idle
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }

    fun retry() {
        _retryTrigger.tryEmit(Unit)
    }
}
```

### 4. Многоканальный Поиск (локальный + удаленный)

```kotlin
class HybridSearchViewModel(
    private val localRepository: LocalSearchRepository,
    private val remoteRepository: RemoteSearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    data class SearchResults(
        val localResults: List<SearchResult> = emptyList(),
        val remoteResults: List<SearchResult> = emptyList(),
        val isRemoteLoading: Boolean = false
    )

    val searchResults: StateFlow<SearchResults> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            combine(
                flow { emit(localRepository.search(query)) }
                    .catch { emit(emptyList()) },
                flow {
                    emit(remoteRepository.search(query))
                }
                    .onStart { emit(emptyList()) }
                    .catch { emit(emptyList()) }
            ) { local, remote ->
                SearchResults(
                    localResults = local,
                    remoteResults = remote,
                    // В реальном коде флаг загрузки удаленных данных лучше вести отдельно;
                    // здесь используется простая эвристика для примера.
                    isRemoteLoading = remote.isEmpty() && query.isNotEmpty()
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
```

### 5. Поиск С Подсказками И Недавними Запросами

```kotlin
class SmartSearchViewModel(
    private val repository: SearchRepository,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    val searchSuggestions: StateFlow<List<String>> = _searchQuery
        .debounce(200) // Быстрее для подсказок
        .distinctUntilChanged()
        .flatMapLatest { query ->
            when {
                query.isBlank() -> {
                    // Показать недавние поисковые запросы
                    preferencesRepository.getRecentSearches()
                }
                query.length < 2 -> {
                    flowOf(emptyList())
                }
                else -> {
                    // Показать подсказки
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

### 6. Интеграция С Jetpack Compose (концептуально)

Пример связывает простой `SearchViewModel`, который предоставляет `searchQuery` и `searchResults`. Для более сложных состояний можно использовать `SearchUiState`/`SearchResultState` из примеров выше.

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val query by viewModel.searchQuery.collectAsStateWithLifecycle()
    val results by viewModel.searchResults.collectAsStateWithLifecycle()

    Column(modifier = Modifier.fillMaxSize()) {
        SearchBar(
            query = query,
            onQueryChange = viewModel::onSearchQueryChanged,
            modifier = Modifier.fillMaxWidth()
        )

        SearchResultsList(results = results)
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

### 7. Поиск С Фильтрами

```kotlin
class FilteredSearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _filters = MutableStateFlow(SearchFilters())

    data class SearchFilters(
        val category: String? = null,
        val priceRange: IntRange? = null,
        val sortBy: SortOption = SortOption.RELEVANCE
    )

    val searchResults: StateFlow<List<SearchResult>> = combine(
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
            started = SharingStarted.WhileSubscribed(5000),
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

### 8. Производительный Вариант Реализации

```kotlin
class OptimizedSearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val searchState: StateFlow<SearchUiState> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            flow {
                emit(SearchUiState.Loading)
                try {
                    val results = withContext(Dispatchers.IO) {
                        repository.search(query)
                    }
                    emit(SearchUiState.Success(results))
                } catch (e: Exception) {
                    emit(
                        SearchUiState.Error(
                            e.message ?: "Unknown error"
                        )
                    )
                }
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

### 9. Тестирование Поведения Debounce (концептуально)

```kotlin
@Test
fun `search debounces user input`() = runTest {
    val fakeRepository = FakeSearchRepository()
    val viewModel = SearchViewModel(fakeRepository)

    // Эмуляция быстрого ввода (используется виртуальное время runTest)
    viewModel.onSearchQueryChanged("a")
    advanceTimeBy(100)
    viewModel.onSearchQueryChanged("ab")
    advanceTimeBy(100)
    viewModel.onSearchQueryChanged("abc")
    advanceTimeBy(400) // Ждем, чтобы debounce сработал

    // Должен быть всего один запрос для "abc"
    assertEquals(1, fakeRepository.searchCallCount)
    assertEquals("abc", fakeRepository.lastQuery)
}
```

### 10. Краткие Рекомендации (Best Practices)

| Оператор | Назначение | Типичное значение |
|----------|------------|-------------------|
| `debounce` | Ждет окончания ввода пользователя | 300-500 мс |
| `distinctUntilChanged` | Избегает дублирующих поисков | Использовать всегда |
| `filter` | Минимальная длина запроса | 2-3 символа |
| `mapLatest` | Отмена предыдущего поиска | Для сетевых запросов |
| `catch` | Гибкая обработка ошибок | Рекомендуется |
| `stateIn` | Шаринг `Flow` между коллекторами | `WhileSubscribed` |

- Делайте:
  - Используйте `debounce` для снижения количества запросов.
  - Вводите минимальную длину запроса.
  - Отменяйте предыдущие запросы с помощью `mapLatest`.
  - Явно обрабатывайте пустые/ошибочные состояния.
  - Показывайте индикатор загрузки для долгих запросов.
  - По возможности кэшируйте недавние запросы.

- Не делайте:
  - Не отправляйте сетевой запрос на каждый символ без `debounce`.
  - Не игнорируйте отмену корутин.
  - Не забывайте об обработке ошибок.
  - Не используйте `GlobalScope`.
  - Не блокируйте главный поток.

---

## Answer (EN)

Instant search is a common UX pattern that requires efficient handling of user input, debouncing, and cancellable API calls. Kotlin `Flow` provides powerful operators to implement this.

Below are focused, technically correct patterns. Types like `SearchResult`, `SearchUiState`, `SearchResults`, `NetworkMonitor`, and repositories are assumed to be defined appropriately in the project (e.g., as domain/UI models and interfaces).

### 1. Basic Instant Search Implementation

```kotlin
import kotlinx.coroutines.flow.*
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope

class SearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

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
        _searchQuery.value = query
    }
}
```

### 2. Search with Loading and Error States

```kotlin
sealed class SearchUiState {
    object Idle : SearchUiState()
    object Loading : SearchUiState()
    data class Success(val results: List<SearchResult>) : SearchUiState()
    data class Error(val message: String) : SearchUiState()
}

class SearchWithStateViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val searchState: StateFlow<SearchUiState> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { query ->
            when {
                query.isBlank() || query.length < 2 -> {
                    flowOf(SearchUiState.Idle)
                }
                else -> {
                    flow {
                        emit(SearchUiState.Loading)
                        try {
                            val results = repository.search(query)
                            emit(SearchUiState.Success(results))
                        } catch (e: Exception) {
                            emit(
                                SearchUiState.Error(
                                    e.message ?: "Unknown error"
                                )
                            )
                        }
                    }
                }
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

Assume `SearchResultState` is a sealed UI state type.

```kotlin
sealed class SearchResultState {
    object Idle : SearchResultState()
    object Loading : SearchResultState()
    data class Success(val results: List<SearchResult>) : SearchResultState()
    data class NetworkError(val message: String) : SearchResultState()
    data class ApiError(val message: String) : SearchResultState()
}

class NetworkAwareSearchViewModel(
    private val repository: SearchRepository,
    private val networkMonitor: NetworkMonitor
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _retryTrigger = MutableSharedFlow<Unit>(extraBufferCapacity = 1)

    val searchState: StateFlow<SearchResultState> = combine(
        _searchQuery
            .debounce(300)
            .distinctUntilChanged()
            .filter { it.length >= 2 },
        _retryTrigger.onStart { emit(Unit) },
        networkMonitor.isOnline
    ) { query, _, isOnline ->
        query to isOnline
    }
        .mapLatest { (query, isOnline) ->
            if (!isOnline) {
                SearchResultState.NetworkError("No internet connection")
            } else {
                try {
                    val results = repository.search(query)
                    SearchResultState.Success(results)
                } catch (e: Exception) {
                    SearchResultState.ApiError(
                        e.message ?: "Unknown error"
                    )
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = SearchResultState.Idle
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }

    fun retry() {
        _retryTrigger.tryEmit(Unit)
    }
}
```

### 4. Multi-Source Search (Local + Remote)

```kotlin
class HybridSearchViewModel(
    private val localRepository: LocalSearchRepository,
    private val remoteRepository: RemoteSearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    data class SearchResults(
        val localResults: List<SearchResult> = emptyList(),
        val remoteResults: List<SearchResult> = emptyList(),
        val isRemoteLoading: Boolean = false
    )

    val searchResults: StateFlow<SearchResults> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            combine(
                flow { emit(localRepository.search(query)) }
                    .catch { emit(emptyList()) },
                flow {
                    emit(remoteRepository.search(query))
                }
                    .onStart { emit(emptyList()) }
                    .catch { emit(emptyList()) }
            ) { local, remote ->
                SearchResults(
                    localResults = local,
                    remoteResults = remote,
                    // Here `isRemoteLoading` would ideally come from a separate loading signal;
                    // using emptiness as a heuristic is simplistic but acceptable for an example.
                    isRemoteLoading = remote.isEmpty() && query.isNotEmpty()
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
```

### 5. Search with Suggestions and Recent Searches

```kotlin
class SmartSearchViewModel(
    private val repository: SearchRepository,
    private val preferencesRepository: PreferencesRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    val searchSuggestions: StateFlow<List<String>> = _searchQuery
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

### 6. Composable UI Integration (Conceptual Example)

This example wires a simple `SearchViewModel` that exposes `searchQuery` and `searchResults`. For more complex UI states, adapt to the `SearchUiState`/`SearchResultState` shown above.

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val query by viewModel.searchQuery.collectAsStateWithLifecycle()
    val results by viewModel.searchResults.collectAsStateWithLifecycle()

    Column(modifier = Modifier.fillMaxSize()) {
        SearchBar(
            query = query,
            onQueryChange = viewModel::onSearchQueryChanged,
            modifier = Modifier.fillMaxWidth()
        )

        SearchResultsList(results = results)
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

### 7. Search with Filters

```kotlin
class FilteredSearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _filters = MutableStateFlow(SearchFilters())

    data class SearchFilters(
        val category: String? = null,
        val priceRange: IntRange? = null,
        val sortBy: SortOption = SortOption.RELEVANCE
    )

    val searchResults: StateFlow<List<SearchResult>> = combine(
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
            started = SharingStarted.WhileSubscribed(5000),
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

### 8. Performance-Oriented Implementation

```kotlin
class OptimizedSearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val searchState: StateFlow<SearchUiState> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            flow {
                emit(SearchUiState.Loading)
                try {
                    val results = withContext(Dispatchers.IO) {
                        repository.search(query)
                    }
                    emit(SearchUiState.Success(results))
                } catch (e: Exception) {
                    emit(
                        SearchUiState.Error(
                            e.message ?: "Unknown error"
                        )
                    )
                }
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

### 9. Testing Debounce Behavior (Conceptual)

```kotlin
@Test
fun `search debounces user input`() = runTest {
    val fakeRepository = FakeSearchRepository()
    val viewModel = SearchViewModel(fakeRepository)

    // Simulate rapid typing (using runTest virtual time)
    viewModel.onSearchQueryChanged("a")
    advanceTimeBy(100)
    viewModel.onSearchQueryChanged("ab")
    advanceTimeBy(100)
    viewModel.onSearchQueryChanged("abc")
    advanceTimeBy(400) // Wait for debounce to pass

    // Should only search once for "abc"
    assertEquals(1, fakeRepository.searchCallCount)
    assertEquals("abc", fakeRepository.lastQuery)
}
```

### 10. Best Practices Summary

| Operator | Purpose | Typical Value |
|----------|---------|---------------|
| `debounce` | Wait for user to stop typing | 300-500ms |
| `distinctUntilChanged` | Avoid duplicate searches | Always use |
| `filter` | Minimum query length | 2-3 characters |
| `mapLatest` | Cancel previous search | For API calls |
| `catch` | Handle errors gracefully | Recommended |
| `stateIn` | Share `Flow` across collectors | WhileSubscribed |

- DO:
  - Use `debounce` to reduce API calls
  - Add minimum character filter
  - Cancel previous searches with `mapLatest`
  - Handle empty/error states
  - Show loading indicators for long-running calls
  - Optionally cache recent searches

- DON'T:
  - Don't issue network search on every single keystroke without debounce
  - Don't ignore cancellation
  - Don't forget error handling
  - Don't use `GlobalScope`
  - Don't block the main thread

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия такого подхода от реализации без корутин/`Flow`?
- В каких реальных сценариях на Android вы будете использовать мгновенный поиск на основе `Flow`?
- Какие распространенные ошибки при использовании `debounce` и `mapLatest` стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Документация по операторам `Flow`: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/
- Оператор `debounce`: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/debounce.html
- [[c-flow]]
- [[c-kotlin]]

## References

- [Flow Operators Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)
- [debounce Operator](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/debounce.html)
- [[c-flow]]
- [[c-kotlin]]

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-flow-operators-map-filter--kotlin--medium]] — операторы `Flow`
- [[q-flow-operators--kotlin--medium]] — обзор операторов `Flow`
- [[q-retry-operators-flow--kotlin--medium]] — операторы повторов
- [[q-flow-time-operators--kotlin--medium]] — временные операторы `Flow`

### Продвинутые
- [[q-testing-flow-operators--kotlin--hard]] — тестирование `Flow`
- [[q-flow-operators-deep-dive--kotlin--hard]] — углубленный разбор операторов `Flow`
- [[q-flow-backpressure-strategies--kotlin--hard]] — стратегии работы с нагрузкой

### Хабы
- [[q-kotlin-flow-basics--kotlin--medium]] — основы Kotlin `Flow`

## Related Questions

### Related (Medium)
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - `Flow`
- [[q-retry-operators-flow--kotlin--medium]] - `Flow`
- [[q-flow-time-operators--kotlin--medium]] - `Flow`

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - `Flow`
- [[q-flow-backpressure-strategies--kotlin--hard]] - `Flow`

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

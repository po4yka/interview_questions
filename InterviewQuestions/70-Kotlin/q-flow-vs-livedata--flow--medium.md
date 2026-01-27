---
id: kotlin-flow-008
title: Flow vs LiveData / Flow vs LiveData
aliases:
- Flow vs LiveData
- LiveData Migration
- Flow LiveData Comparison
topic: kotlin
subtopics:
- coroutines
- flow
- android
- livedata
question_kind: comparison
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: internal
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-flow
- q-stateflow-vs-sharedflow--flow--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- coroutines
- difficulty/medium
- flow
- kotlin
- android
- livedata
anki_cards:
- slug: kotlin-flow-008-0-en
  language: en
  anki_id: 1769344146666
  synced_at: '2026-01-25T16:29:06.717065'
- slug: kotlin-flow-008-0-ru
  language: ru
  anki_id: 1769344146715
  synced_at: '2026-01-25T16:29:06.718313'
---
# Vopros (RU)
> Чем Flow отличается от LiveData? Какие стратегии миграции существуют?

---

# Question (EN)
> How does Flow compare to LiveData? What migration strategies exist?

## Otvet (RU)

### Сравнение Flow и LiveData

| Аспект | LiveData | StateFlow/Flow |
|--------|----------|----------------|
| Язык | Java-friendly | Kotlin-first |
| Lifecycle-aware | Да (встроено) | Нет (требует repeatOnLifecycle) |
| Операторы | Ограниченные | Богатые (map, filter, combine...) |
| Backpressure | Нет | Да |
| Тестирование | InstantTaskExecutorRule | runTest, Turbine |
| Холодные/горячие | Только горячие | Оба типа |
| Потоки данных | Один источник | Множественные трансформации |

### Преимущества Flow

```kotlin
// 1. Богатые операторы
repository.getUsers()
    .map { users -> users.filter { it.isActive } }
    .combine(sortOrder) { users, order -> sort(users, order) }
    .debounce(300)
    .catch { emit(emptyList()) }
    .collect { updateUI(it) }

// 2. Поддержка backpressure
flow.buffer(64)
flow.conflate()
flow.collectLatest { }

// 3. Холодные потоки - ленивое выполнение
val coldFlow = flow {
    // Выполняется только при collect
    emit(repository.fetchData())
}

// 4. Лучшая обработка ошибок
flow
    .catch { e -> emit(FallbackValue) }
    .retryWhen { cause, attempt -> attempt < 3 }
```

### Преимущества LiveData

```kotlin
// 1. Автоматическое управление lifecycle
viewModel.data.observe(viewLifecycleOwner) { data ->
    // Автоматически отписывается при STOPPED
}

// 2. Java совместимость
// LiveData работает из Java кода

// 3. Простота для базовых случаев
val _data = MutableLiveData<String>()
val data: LiveData<String> = _data
```

### Стратегии Миграции

#### 1. Постепенная миграция

```kotlin
// ViewModel - оставляем LiveData для UI
class UserViewModel(private val repository: UserRepository) : ViewModel() {

    // Внутри используем Flow
    private val userFlow: Flow<User> = repository.observeUser()

    // Конвертируем в LiveData для UI (если нужна Java совместимость)
    val user: LiveData<User> = userFlow.asLiveData()

    // ИЛИ используем StateFlow напрямую (рекомендуется)
    val userState: StateFlow<UiState<User>> = userFlow
        .map { UiState.Success(it) }
        .catch { emit(UiState.Error(it.message)) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = UiState.Loading
        )
}
```

#### 2. Полная миграция на StateFlow

```kotlin
// До: LiveData
class OldViewModel : ViewModel() {
    private val _count = MutableLiveData(0)
    val count: LiveData<Int> = _count

    fun increment() {
        _count.value = (_count.value ?: 0) + 1
    }
}

// После: StateFlow
class NewViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
        // или _count.update { it + 1 }
    }
}

// UI - было:
viewModel.count.observe(viewLifecycleOwner) { count ->
    binding.textView.text = count.toString()
}

// UI - стало:
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.count.collect { count ->
            binding.textView.text = count.toString()
        }
    }
}
```

#### 3. Конвертация между типами

```kotlin
// Flow -> LiveData
val liveData: LiveData<User> = userFlow.asLiveData()

// LiveData -> Flow
val flow: Flow<User> = liveData.asFlow()

// Room автоматически поддерживает оба
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun observeUsersLiveData(): LiveData<List<User>>

    @Query("SELECT * FROM users")
    fun observeUsersFlow(): Flow<List<User>>
}
```

### Jetpack Compose и Flow

В Compose Flow является предпочтительным:

```kotlin
@Composable
fun UserScreen(viewModel: UserViewModel) {
    // Рекомендуется: collectAsStateWithLifecycle
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> LoadingIndicator()
        is UiState.Success -> UserContent(state.user)
        is UiState.Error -> ErrorMessage(state.message)
    }
}

// В ViewModel - чистый Flow/StateFlow
class UserViewModel : ViewModel() {
    val uiState: StateFlow<UiState<User>> = repository.observeUser()
        .map { UiState.Success(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UiState.Loading)
}
```

### Когда Оставить LiveData

1. **Java код** - LiveData лучше интегрируется
2. **Существующий legacy код** - если миграция дорогая
3. **Простые случаи** - когда операторы Flow не нужны
4. **Data Binding** - нативная поддержка LiveData

### Когда Использовать Flow

1. **Kotlin-only проекты** - максимальная выгода
2. **Сложные трансформации** - операторы Flow
3. **Jetpack Compose** - нативная интеграция
4. **Реактивные потоки** - combine, flatMap, debounce
5. **Repository layer** - Flow как стандарт

### Полный Пример Миграции

```kotlin
// === БЫЛО (LiveData) ===
class OldSearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _query = MutableLiveData("")
    private val _results = MediatorLiveData<List<SearchResult>>()

    init {
        _results.addSource(_query) { query ->
            viewModelScope.launch {
                val results = repository.search(query)
                _results.value = results
            }
        }
    }

    val results: LiveData<List<SearchResult>> = _results

    fun updateQuery(query: String) {
        _query.value = query
    }
}

// === СТАЛО (Flow) ===
class NewSearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _query = MutableStateFlow("")

    val results: StateFlow<List<SearchResult>> = _query
        .debounce(300)
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            repository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun updateQuery(query: String) {
        _query.value = query
    }
}
```

### Рекомендации Google (2026)

- **Новые проекты**: StateFlow/SharedFlow
- **Compose**: Flow с collectAsStateWithLifecycle
- **Data layer**: Flow (Room, Retrofit)
- **Domain layer**: Flow
- **UI layer**: StateFlow для состояния, SharedFlow для событий

---

## Answer (EN)

### Flow vs LiveData Comparison

| Aspect | LiveData | StateFlow/Flow |
|--------|----------|----------------|
| Language | Java-friendly | Kotlin-first |
| Lifecycle-aware | Yes (built-in) | No (requires repeatOnLifecycle) |
| Operators | Limited | Rich (map, filter, combine...) |
| Backpressure | No | Yes |
| Testing | InstantTaskExecutorRule | runTest, Turbine |
| Cold/hot | Only hot | Both types |
| Data streams | Single source | Multiple transformations |

### Flow Advantages

```kotlin
// 1. Rich operators
repository.getUsers()
    .map { users -> users.filter { it.isActive } }
    .combine(sortOrder) { users, order -> sort(users, order) }
    .debounce(300)
    .catch { emit(emptyList()) }
    .collect { updateUI(it) }

// 2. Backpressure support
flow.buffer(64)
flow.conflate()
flow.collectLatest { }

// 3. Cold flows - lazy execution
val coldFlow = flow {
    // Executes only on collect
    emit(repository.fetchData())
}

// 4. Better error handling
flow
    .catch { e -> emit(FallbackValue) }
    .retryWhen { cause, attempt -> attempt < 3 }
```

### LiveData Advantages

```kotlin
// 1. Automatic lifecycle management
viewModel.data.observe(viewLifecycleOwner) { data ->
    // Automatically unsubscribes at STOPPED
}

// 2. Java compatibility
// LiveData works from Java code

// 3. Simplicity for basic cases
val _data = MutableLiveData<String>()
val data: LiveData<String> = _data
```

### Migration Strategies

#### 1. Gradual Migration

```kotlin
// ViewModel - keep LiveData for UI
class UserViewModel(private val repository: UserRepository) : ViewModel() {

    // Use Flow internally
    private val userFlow: Flow<User> = repository.observeUser()

    // Convert to LiveData for UI (if Java compatibility needed)
    val user: LiveData<User> = userFlow.asLiveData()

    // OR use StateFlow directly (recommended)
    val userState: StateFlow<UiState<User>> = userFlow
        .map { UiState.Success(it) }
        .catch { emit(UiState.Error(it.message)) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = UiState.Loading
        )
}
```

#### 2. Full Migration to StateFlow

```kotlin
// Before: LiveData
class OldViewModel : ViewModel() {
    private val _count = MutableLiveData(0)
    val count: LiveData<Int> = _count

    fun increment() {
        _count.value = (_count.value ?: 0) + 1
    }
}

// After: StateFlow
class NewViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
        // or _count.update { it + 1 }
    }
}

// UI - before:
viewModel.count.observe(viewLifecycleOwner) { count ->
    binding.textView.text = count.toString()
}

// UI - after:
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.count.collect { count ->
            binding.textView.text = count.toString()
        }
    }
}
```

#### 3. Converting Between Types

```kotlin
// Flow -> LiveData
val liveData: LiveData<User> = userFlow.asLiveData()

// LiveData -> Flow
val flow: Flow<User> = liveData.asFlow()

// Room supports both automatically
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun observeUsersLiveData(): LiveData<List<User>>

    @Query("SELECT * FROM users")
    fun observeUsersFlow(): Flow<List<User>>
}
```

### Jetpack Compose and Flow

In Compose, Flow is preferred:

```kotlin
@Composable
fun UserScreen(viewModel: UserViewModel) {
    // Recommended: collectAsStateWithLifecycle
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> LoadingIndicator()
        is UiState.Success -> UserContent(state.user)
        is UiState.Error -> ErrorMessage(state.message)
    }
}

// In ViewModel - pure Flow/StateFlow
class UserViewModel : ViewModel() {
    val uiState: StateFlow<UiState<User>> = repository.observeUser()
        .map { UiState.Success(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UiState.Loading)
}
```

### When to Keep LiveData

1. **Java code** - LiveData integrates better
2. **Existing legacy code** - if migration is costly
3. **Simple cases** - when Flow operators not needed
4. **Data Binding** - native LiveData support

### When to Use Flow

1. **Kotlin-only projects** - maximum benefit
2. **Complex transformations** - Flow operators
3. **Jetpack Compose** - native integration
4. **Reactive streams** - combine, flatMap, debounce
5. **Repository layer** - Flow as standard

### Full Migration Example

```kotlin
// === BEFORE (LiveData) ===
class OldSearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _query = MutableLiveData("")
    private val _results = MediatorLiveData<List<SearchResult>>()

    init {
        _results.addSource(_query) { query ->
            viewModelScope.launch {
                val results = repository.search(query)
                _results.value = results
            }
        }
    }

    val results: LiveData<List<SearchResult>> = _results

    fun updateQuery(query: String) {
        _query.value = query
    }
}

// === AFTER (Flow) ===
class NewSearchViewModel(
    private val repository: SearchRepository
) : ViewModel() {

    private val _query = MutableStateFlow("")

    val results: StateFlow<List<SearchResult>> = _query
        .debounce(300)
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            repository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun updateQuery(query: String) {
        _query.value = query
    }
}
```

### Google Recommendations (2026)

- **New projects**: StateFlow/SharedFlow
- **Compose**: Flow with collectAsStateWithLifecycle
- **Data layer**: Flow (Room, Retrofit)
- **Domain layer**: Flow
- **UI layer**: StateFlow for state, SharedFlow for events

---

## Dopolnitelnye Voprosy (RU)

1. Как обрабатывать configuration changes при миграции с LiveData на Flow?
2. Можно ли использовать Flow с Data Binding?
3. Как тестировать ViewModel после миграции на Flow?
4. Какие проблемы могут возникнуть при использовании asLiveData()?
5. Как мигрировать Transformations.map и Transformations.switchMap?

---

## Follow-ups

1. How to handle configuration changes when migrating from LiveData to Flow?
2. Can you use Flow with Data Binding?
3. How to test ViewModel after migration to Flow?
4. What problems can arise when using asLiveData()?
5. How to migrate Transformations.map and Transformations.switchMap?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Migrating from LiveData to Kotlin Flow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow#livedata)
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [Migrating from LiveData to Kotlin Flow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow#livedata)
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-flow-vs-livedata-comparison--kotlin--medium]]
- [[q-stateflow-vs-sharedflow--flow--medium]]
- [[q-flow-lifecycle-collection--flow--medium]]

---

## Related Questions

### Related (Medium)
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Detailed comparison
- [[q-stateflow-vs-sharedflow--flow--medium]] - StateFlow vs SharedFlow
- [[q-flow-lifecycle-collection--flow--medium]] - Lifecycle-aware collection

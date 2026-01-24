---
id: kotlin-flow-009
title: "MutableStateFlow Usage Patterns / Паттерны использования MutableStateFlow"
aliases:
  - MutableStateFlow Patterns
  - StateFlow Usage
  - MutableStateFlow Best Practices
topic: kotlin
subtopics:
  - coroutines
  - flow
  - state-management
question_kind: theory
difficulty: easy
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
  - difficulty/easy
  - flow
  - kotlin
  - stateflow
---
# Vopros (RU)
> Как правильно использовать `MutableStateFlow`? Какие паттерны и best practices существуют?

---

# Question (EN)
> How to properly use `MutableStateFlow`? What patterns and best practices exist?

## Otvet (RU)

### Создание и Базовое Использование

```kotlin
// Создание с начальным значением (обязательно)
val counter = MutableStateFlow(0)

// Чтение текущего значения
val currentValue = counter.value  // 0

// Установка нового значения
counter.value = 5

// Атомарное обновление
counter.update { it + 1 }  // Безопасно для concurrent доступа

// Сбор значений
counter.collect { value ->
    println("New value: $value")
}
```

### Паттерн: Private Mutable, Public Read-only

```kotlin
class CounterViewModel : ViewModel() {
    // Private mutable - для изменения внутри класса
    private val _count = MutableStateFlow(0)

    // Public read-only - для внешнего доступа
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }

    fun decrement() {
        _count.value--
    }
}
```

### Методы Обновления

```kotlin
val state = MutableStateFlow(User("John", 25))

// 1. Прямое присваивание (простые значения)
state.value = User("Jane", 30)

// 2. update {} - атомарное обновление (рекомендуется)
state.update { currentUser ->
    currentUser.copy(name = "Updated Name")
}

// 3. updateAndGet - обновить и получить новое значение
val newState = state.updateAndGet { it.copy(age = it.age + 1) }

// 4. getAndUpdate - получить старое значение и обновить
val oldState = state.getAndUpdate { it.copy(age = 0) }

// 5. compareAndSet - условное обновление
state.compareAndSet(
    expect = User("John", 25),
    update = User("John", 26)
)
```

### Паттерн: UI State с Sealed Class

```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}

class ItemViewModel(private val repository: ItemRepository) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadItems() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val items = repository.getItems()
                _uiState.value = UiState.Success(items)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

### Паттерн: Compose State с Data Class

```kotlin
data class FormState(
    val name: String = "",
    val email: String = "",
    val isValid: Boolean = false,
    val isSubmitting: Boolean = false
)

class FormViewModel : ViewModel() {

    private val _formState = MutableStateFlow(FormState())
    val formState: StateFlow<FormState> = _formState.asStateFlow()

    fun updateName(name: String) {
        _formState.update { state ->
            state.copy(
                name = name,
                isValid = validateForm(name, state.email)
            )
        }
    }

    fun updateEmail(email: String) {
        _formState.update { state ->
            state.copy(
                email = email,
                isValid = validateForm(state.name, email)
            )
        }
    }

    fun submit() {
        _formState.update { it.copy(isSubmitting = true) }
        viewModelScope.launch {
            // ... submit logic
            _formState.update { it.copy(isSubmitting = false) }
        }
    }

    private fun validateForm(name: String, email: String): Boolean {
        return name.isNotBlank() && email.contains("@")
    }
}
```

### Паттерн: Комбинирование Нескольких StateFlow

```kotlin
class SearchViewModel(private val repository: SearchRepository) : ViewModel() {

    private val _query = MutableStateFlow("")
    private val _sortOrder = MutableStateFlow(SortOrder.NAME)
    private val _filters = MutableStateFlow(Filters())

    // Комбинируем несколько источников
    val searchResults: StateFlow<List<Item>> = combine(
        _query,
        _sortOrder,
        _filters
    ) { query, sort, filters ->
        repository.search(query, sort, filters)
    }
    .flatMapLatest { it }  // Отменяем предыдущий поиск
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )

    fun updateQuery(query: String) { _query.value = query }
    fun updateSortOrder(order: SortOrder) { _sortOrder.value = order }
    fun updateFilters(filters: Filters) { _filters.value = filters }
}
```

### distinctUntilChanged Поведение

```kotlin
val state = MutableStateFlow(0)

state.collect { println("Received: $it") }

state.value = 1  // Received: 1
state.value = 1  // Ничего - значение не изменилось
state.value = 2  // Received: 2
state.value = 1  // Received: 1 - другое значение

// Для data class сравнение по equals()
data class User(val name: String, val age: Int)

val userState = MutableStateFlow(User("John", 25))
userState.value = User("John", 25)  // НЕ эмитится - equals() = true
userState.value = User("John", 26)  // Эмитится - age изменился
```

### Типичные Ошибки

```kotlin
// ОШИБКА: Изменение объекта вместо создания нового
data class State(var count: Int)  // mutable property!

val state = MutableStateFlow(State(0))
state.value.count = 5  // StateFlow НЕ узнает об изменении!

// ПРАВИЛЬНО: Используйте immutable data classes и copy()
data class State(val count: Int)  // immutable property

val state = MutableStateFlow(State(0))
state.update { it.copy(count = 5) }  // StateFlow эмитит новое значение

// ОШИБКА: Не использовать update для concurrent доступа
// Возможна потеря обновлений при race condition
state.value = state.value.copy(count = state.value.count + 1)

// ПРАВИЛЬНО: update гарантирует атомарность
state.update { it.copy(count = it.count + 1) }
```

### Сбор в UI (Android)

```kotlin
// Activity/Fragment
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state ->
            when (state) {
                is UiState.Loading -> showLoading()
                is UiState.Success -> showData(state.data)
                is UiState.Error -> showError(state.message)
            }
        }
    }
}

// Compose
@Composable
fun MyScreen(viewModel: MyViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> ItemList(state.data)
        is UiState.Error -> ErrorMessage(state.message)
    }
}
```

---

## Answer (EN)

### Creating and Basic Usage

```kotlin
// Create with initial value (required)
val counter = MutableStateFlow(0)

// Read current value
val currentValue = counter.value  // 0

// Set new value
counter.value = 5

// Atomic update
counter.update { it + 1 }  // Safe for concurrent access

// Collect values
counter.collect { value ->
    println("New value: $value")
}
```

### Pattern: Private Mutable, Public Read-only

```kotlin
class CounterViewModel : ViewModel() {
    // Private mutable - for internal modification
    private val _count = MutableStateFlow(0)

    // Public read-only - for external access
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }

    fun decrement() {
        _count.value--
    }
}
```

### Update Methods

```kotlin
val state = MutableStateFlow(User("John", 25))

// 1. Direct assignment (simple values)
state.value = User("Jane", 30)

// 2. update {} - atomic update (recommended)
state.update { currentUser ->
    currentUser.copy(name = "Updated Name")
}

// 3. updateAndGet - update and get new value
val newState = state.updateAndGet { it.copy(age = it.age + 1) }

// 4. getAndUpdate - get old value and update
val oldState = state.getAndUpdate { it.copy(age = 0) }

// 5. compareAndSet - conditional update
state.compareAndSet(
    expect = User("John", 25),
    update = User("John", 26)
)
```

### Pattern: UI State with Sealed Class

```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<Item>) : UiState()
    data class Error(val message: String) : UiState()
}

class ItemViewModel(private val repository: ItemRepository) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadItems() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val items = repository.getItems()
                _uiState.value = UiState.Success(items)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

### Pattern: Compose State with Data Class

```kotlin
data class FormState(
    val name: String = "",
    val email: String = "",
    val isValid: Boolean = false,
    val isSubmitting: Boolean = false
)

class FormViewModel : ViewModel() {

    private val _formState = MutableStateFlow(FormState())
    val formState: StateFlow<FormState> = _formState.asStateFlow()

    fun updateName(name: String) {
        _formState.update { state ->
            state.copy(
                name = name,
                isValid = validateForm(name, state.email)
            )
        }
    }

    fun updateEmail(email: String) {
        _formState.update { state ->
            state.copy(
                email = email,
                isValid = validateForm(state.name, email)
            )
        }
    }

    fun submit() {
        _formState.update { it.copy(isSubmitting = true) }
        viewModelScope.launch {
            // ... submit logic
            _formState.update { it.copy(isSubmitting = false) }
        }
    }

    private fun validateForm(name: String, email: String): Boolean {
        return name.isNotBlank() && email.contains("@")
    }
}
```

### Pattern: Combining Multiple StateFlows

```kotlin
class SearchViewModel(private val repository: SearchRepository) : ViewModel() {

    private val _query = MutableStateFlow("")
    private val _sortOrder = MutableStateFlow(SortOrder.NAME)
    private val _filters = MutableStateFlow(Filters())

    // Combine multiple sources
    val searchResults: StateFlow<List<Item>> = combine(
        _query,
        _sortOrder,
        _filters
    ) { query, sort, filters ->
        repository.search(query, sort, filters)
    }
    .flatMapLatest { it }  // Cancel previous search
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )

    fun updateQuery(query: String) { _query.value = query }
    fun updateSortOrder(order: SortOrder) { _sortOrder.value = order }
    fun updateFilters(filters: Filters) { _filters.value = filters }
}
```

### distinctUntilChanged Behavior

```kotlin
val state = MutableStateFlow(0)

state.collect { println("Received: $it") }

state.value = 1  // Received: 1
state.value = 1  // Nothing - value unchanged
state.value = 2  // Received: 2
state.value = 1  // Received: 1 - different value

// For data class, comparison uses equals()
data class User(val name: String, val age: Int)

val userState = MutableStateFlow(User("John", 25))
userState.value = User("John", 25)  // NOT emitted - equals() = true
userState.value = User("John", 26)  // Emitted - age changed
```

### Common Mistakes

```kotlin
// WRONG: Mutating object instead of creating new one
data class State(var count: Int)  // mutable property!

val state = MutableStateFlow(State(0))
state.value.count = 5  // StateFlow does NOT know about change!

// CORRECT: Use immutable data classes with copy()
data class State(val count: Int)  // immutable property

val state = MutableStateFlow(State(0))
state.update { it.copy(count = 5) }  // StateFlow emits new value

// WRONG: Not using update for concurrent access
// Updates can be lost due to race condition
state.value = state.value.copy(count = state.value.count + 1)

// CORRECT: update guarantees atomicity
state.update { it.copy(count = it.count + 1) }
```

### Collecting in UI (Android)

```kotlin
// Activity/Fragment
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state ->
            when (state) {
                is UiState.Loading -> showLoading()
                is UiState.Success -> showData(state.data)
                is UiState.Error -> showError(state.message)
            }
        }
    }
}

// Compose
@Composable
fun MyScreen(viewModel: MyViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> ItemList(state.data)
        is UiState.Error -> ErrorMessage(state.message)
    }
}
```

---

## Dopolnitelnye Voprosy (RU)

1. Когда использовать `value =` vs `update {}`?
2. Как правильно обновлять вложенные объекты в StateFlow?
3. Можно ли использовать MutableStateFlow без ViewModel?
4. Как тестировать код с MutableStateFlow?
5. Чем StateFlow отличается от MutableState в Compose?

---

## Follow-ups

1. When to use `value =` vs `update {}`?
2. How to properly update nested objects in StateFlow?
3. Can you use MutableStateFlow without ViewModel?
4. How to test code with MutableStateFlow?
5. How does StateFlow differ from MutableState in Compose?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [StateFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [StateFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-stateflow-vs-sharedflow--flow--medium]]
- [[q-stateflow-purpose--kotlin--medium]]

---

## Related Questions

### Related (Medium)
- [[q-stateflow-vs-sharedflow--flow--medium]] - StateFlow vs SharedFlow
- [[q-stateflow-purpose--kotlin--medium]] - StateFlow purpose

---
id: android-arch-002
title: Unidirectional Data Flow / Однонаправленный поток данных
aliases:
- UDF
- Unidirectional Data Flow
- Single Source of Truth
- Однонаправленный поток данных
- Единый источник истины
topic: android
subtopics:
- architecture
- state-management
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-mvi-architecture--android--hard
- q-mvi-pattern--architecture--hard
- q-state-hoisting-compose--android--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- https://developer.android.com/topic/architecture/ui-layer#udf
- https://developer.android.com/jetpack/compose/state
tags:
- android/architecture
- android/state-management
- difficulty/medium
- unidirectional-data-flow
anki_cards:
- slug: android-arch-002-0-en
  language: en
- slug: android-arch-002-0-ru
  language: ru
---
# Vopros (RU)

> Что такое Unidirectional Data Flow (UDF)? Объясните принципы и преимущества единого источника истины (Single Source of Truth).

# Question (EN)

> What is Unidirectional Data Flow (UDF)? Explain the principles and benefits of Single Source of Truth.

---

## Otvet (RU)

**Unidirectional Data Flow (UDF)** - архитектурный паттерн, где данные движутся в одном направлении по замкнутому циклу: State flows down, Events flow up.

### Принципы UDF

```text
               +------------------+
               |    ViewModel     |
               |  (State Holder)  |
               +--------+---------+
                        |
            State flows | down
                        v
               +--------+---------+
               |       View       |
               |   (UI Layer)     |
               +--------+---------+
                        |
           Events flow  | up
                        v
               +--------+---------+
               |    ViewModel     |
               +------------------+
```

### Три ключевых принципа

#### 1. Single Source of Truth (SSOT)

Каждый элемент данных имеет **единственного владельца** - источник истины.

```kotlin
// SSOT - состояние принадлежит ViewModel
@HiltViewModel
class CounterViewModel @Inject constructor() : ViewModel() {

    // Single Source of Truth
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }

    fun decrement() {
        _count.value--
    }
}

// View только читает и отправляет события
@Composable
fun CounterScreen(viewModel: CounterViewModel = hiltViewModel()) {
    val count by viewModel.count.collectAsStateWithLifecycle()

    CounterContent(
        count = count,
        onIncrement = viewModel::increment,  // Event up
        onDecrement = viewModel::decrement   // Event up
    )
}

@Composable
private fun CounterContent(
    count: Int,           // State down
    onIncrement: () -> Unit,
    onDecrement: () -> Unit
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        IconButton(onClick = onDecrement) {
            Icon(Icons.Default.Remove, "Decrement")
        }
        Text(text = "$count", style = MaterialTheme.typography.headlineLarge)
        IconButton(onClick = onIncrement) {
            Icon(Icons.Default.Add, "Increment")
        }
    }
}
```

#### 2. Immutable State

Состояние всегда immutable. Изменения создают новую копию.

```kotlin
// Immutable State
data class FormState(
    val email: String = "",
    val password: String = "",
    val isEmailValid: Boolean = true,
    val isPasswordValid: Boolean = true,
    val isLoading: Boolean = false
)

class FormViewModel : ViewModel() {
    private val _state = MutableStateFlow(FormState())
    val state: StateFlow<FormState> = _state.asStateFlow()

    fun onEmailChanged(email: String) {
        // Создаем новый объект, не мутируем
        _state.update { currentState ->
            currentState.copy(
                email = email,
                isEmailValid = email.contains("@")
            )
        }
    }

    fun onPasswordChanged(password: String) {
        _state.update { currentState ->
            currentState.copy(
                password = password,
                isPasswordValid = password.length >= 8
            )
        }
    }
}
```

#### 3. Events Flow Up

UI компоненты **никогда** не изменяют state напрямую. Они отправляют события наверх.

```kotlin
// Events (Actions/Intents) flow up
sealed interface FormEvent {
    data class EmailChanged(val email: String) : FormEvent
    data class PasswordChanged(val password: String) : FormEvent
    data object SubmitClicked : FormEvent
    data object ForgotPasswordClicked : FormEvent
}

@Composable
fun LoginForm(
    state: FormState,                    // State flows down
    onEvent: (FormEvent) -> Unit         // Events flow up
) {
    Column {
        TextField(
            value = state.email,
            onValueChange = { onEvent(FormEvent.EmailChanged(it)) },
            isError = !state.isEmailValid
        )

        TextField(
            value = state.password,
            onValueChange = { onEvent(FormEvent.PasswordChanged(it)) },
            isError = !state.isPasswordValid,
            visualTransformation = PasswordVisualTransformation()
        )

        Button(
            onClick = { onEvent(FormEvent.SubmitClicked) },
            enabled = state.isEmailValid && state.isPasswordValid && !state.isLoading
        ) {
            if (state.isLoading) {
                CircularProgressIndicator(modifier = Modifier.size(16.dp))
            } else {
                Text("Login")
            }
        }
    }
}
```

### State Hoisting - реализация UDF в Compose

```kotlin
// State Hoisting - поднятие состояния вверх
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // Состояние "hoisted" в ViewModel
    SearchContent(
        query = state.query,
        results = state.results,
        isLoading = state.isLoading,
        onQueryChange = viewModel::onQueryChange,
        onSearch = viewModel::search
    )
}

// Stateless composable - легко тестировать и переиспользовать
@Composable
private fun SearchContent(
    query: String,
    results: List<SearchResult>,
    isLoading: Boolean,
    onQueryChange: (String) -> Unit,
    onSearch: () -> Unit
) {
    Column {
        SearchBar(
            query = query,
            onQueryChange = onQueryChange,
            onSearch = onSearch
        )

        when {
            isLoading -> LoadingIndicator()
            results.isEmpty() -> EmptyState()
            else -> ResultsList(results)
        }
    }
}
```

### UDF в многослойной архитектуре

```kotlin
// Data Layer -> Domain Layer -> UI Layer
// Каждый слой имеет свой SSOT

// Repository - SSOT для данных
class UserRepository @Inject constructor(
    private val api: UserApi,
    private val cache: UserCache
) {
    // Единый поток данных из репозитория
    fun observeUser(userId: String): Flow<User> = flow {
        // Сначала из кэша
        cache.getUser(userId)?.let { emit(it) }

        // Затем из сети
        val user = api.getUser(userId)
        cache.saveUser(user)
        emit(user)
    }
}

// ViewModel - SSOT для UI State
@HiltViewModel
class UserProfileViewModel @Inject constructor(
    private val userRepository: UserRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val userId = savedStateHandle.get<String>("userId")!!

    val state: StateFlow<UserProfileState> = userRepository
        .observeUser(userId)
        .map { user -> UserProfileState.Success(user) }
        .catch { error -> emit(UserProfileState.Error(error.message)) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = UserProfileState.Loading
        )
}

sealed interface UserProfileState {
    data object Loading : UserProfileState
    data class Success(val user: User) : UserProfileState
    data class Error(val message: String?) : UserProfileState
}
```

### Преимущества UDF

| Преимущество | Описание |
|--------------|----------|
| **Предсказуемость** | State изменяется только через определенные actions |
| **Отладка** | Легко отследить, какое событие привело к изменению |
| **Тестируемость** | Stateless UI легко тестировать |
| **Согласованность** | Нет рассинхронизации между компонентами |
| **Time-travel debugging** | Можно воспроизвести любое состояние |

### Anti-patterns - нарушения UDF

```kotlin
// Нарушение 1: Bidirectional data flow
@Composable
fun BadCounter() {
    var count by remember { mutableStateOf(0) }  // State в View

    // View и владеет state, и меняет его - нет SSOT
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// Нарушение 2: Мутация state напрямую
class BadViewModel : ViewModel() {
    val items = mutableListOf<Item>()  // Mutable, не Flow

    fun addItem(item: Item) {
        items.add(item)  // Мутация, View не узнает
    }
}

// Нарушение 3: Несколько источников истины
class ConfusedViewModel : ViewModel() {
    private val _localItems = MutableStateFlow<List<Item>>(emptyList())
    private val _remoteItems = MutableStateFlow<List<Item>>(emptyList())

    // Какой из них SSOT? View не знает какой использовать
    val localItems = _localItems.asStateFlow()
    val remoteItems = _remoteItems.asStateFlow()
}

// Правильно: единый merged state
class CorrectViewModel : ViewModel() {
    private val localItems = MutableStateFlow<List<Item>>(emptyList())
    private val remoteItems = MutableStateFlow<List<Item>>(emptyList())

    // Единый SSOT - объединенное состояние
    val items: StateFlow<List<Item>> = combine(localItems, remoteItems) { local, remote ->
        (local + remote).distinctBy { it.id }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(), emptyList())
}
```

### UDF с Jetpack Compose

```kotlin
// Compose естественно поддерживает UDF через state hoisting

// Level 1: Local state (для простых случаев)
@Composable
fun ExpandableCard(title: String, content: String) {
    var expanded by remember { mutableStateOf(false) }

    Card(onClick = { expanded = !expanded }) {
        Text(title)
        AnimatedVisibility(visible = expanded) {
            Text(content)
        }
    }
}

// Level 2: Hoisted state (для переиспользования)
@Composable
fun ExpandableCard(
    title: String,
    content: String,
    expanded: Boolean,          // State hoisted
    onExpandChange: (Boolean) -> Unit
) {
    Card(onClick = { onExpandChange(!expanded) }) {
        Text(title)
        AnimatedVisibility(visible = expanded) {
            Text(content)
        }
    }
}

// Level 3: ViewModel state (для бизнес-логики)
@Composable
fun ProductCard(
    product: Product,           // From ViewModel
    onAddToCart: () -> Unit     // Event to ViewModel
) {
    Card {
        Text(product.name)
        Text(product.price)
        Button(onClick = onAddToCart) {
            Text("Add to Cart")
        }
    }
}
```

---

## Answer (EN)

**Unidirectional Data Flow (UDF)** is an architectural pattern where data flows in one direction through a closed cycle: State flows down, Events flow up.

### UDF Principles

```text
               +------------------+
               |    ViewModel     |
               |  (State Holder)  |
               +--------+---------+
                        |
            State flows | down
                        v
               +--------+---------+
               |       View       |
               |   (UI Layer)     |
               +--------+---------+
                        |
           Events flow  | up
                        v
               +--------+---------+
               |    ViewModel     |
               +------------------+
```

### Three Key Principles

#### 1. Single Source of Truth (SSOT)

Every piece of data has a **single owner** - the source of truth.

```kotlin
// SSOT - state belongs to ViewModel
@HiltViewModel
class CounterViewModel @Inject constructor() : ViewModel() {

    // Single Source of Truth
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }

    fun decrement() {
        _count.value--
    }
}

// View only reads and sends events
@Composable
fun CounterScreen(viewModel: CounterViewModel = hiltViewModel()) {
    val count by viewModel.count.collectAsStateWithLifecycle()

    CounterContent(
        count = count,
        onIncrement = viewModel::increment,  // Event up
        onDecrement = viewModel::decrement   // Event up
    )
}

@Composable
private fun CounterContent(
    count: Int,           // State down
    onIncrement: () -> Unit,
    onDecrement: () -> Unit
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        IconButton(onClick = onDecrement) {
            Icon(Icons.Default.Remove, "Decrement")
        }
        Text(text = "$count", style = MaterialTheme.typography.headlineLarge)
        IconButton(onClick = onIncrement) {
            Icon(Icons.Default.Add, "Increment")
        }
    }
}
```

#### 2. Immutable State

State is always immutable. Changes create a new copy.

```kotlin
// Immutable State
data class FormState(
    val email: String = "",
    val password: String = "",
    val isEmailValid: Boolean = true,
    val isPasswordValid: Boolean = true,
    val isLoading: Boolean = false
)

class FormViewModel : ViewModel() {
    private val _state = MutableStateFlow(FormState())
    val state: StateFlow<FormState> = _state.asStateFlow()

    fun onEmailChanged(email: String) {
        // Create new object, don't mutate
        _state.update { currentState ->
            currentState.copy(
                email = email,
                isEmailValid = email.contains("@")
            )
        }
    }
}
```

#### 3. Events Flow Up

UI components **never** modify state directly. They send events upward.

```kotlin
// Events (Actions/Intents) flow up
sealed interface FormEvent {
    data class EmailChanged(val email: String) : FormEvent
    data class PasswordChanged(val password: String) : FormEvent
    data object SubmitClicked : FormEvent
}

@Composable
fun LoginForm(
    state: FormState,                    // State flows down
    onEvent: (FormEvent) -> Unit         // Events flow up
) {
    Column {
        TextField(
            value = state.email,
            onValueChange = { onEvent(FormEvent.EmailChanged(it)) },
            isError = !state.isEmailValid
        )

        Button(
            onClick = { onEvent(FormEvent.SubmitClicked) },
            enabled = state.isEmailValid && !state.isLoading
        ) {
            Text("Login")
        }
    }
}
```

### State Hoisting - UDF in Compose

```kotlin
// State Hoisting - lifting state up
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // State "hoisted" to ViewModel
    SearchContent(
        query = state.query,
        results = state.results,
        isLoading = state.isLoading,
        onQueryChange = viewModel::onQueryChange,
        onSearch = viewModel::search
    )
}

// Stateless composable - easy to test and reuse
@Composable
private fun SearchContent(
    query: String,
    results: List<SearchResult>,
    isLoading: Boolean,
    onQueryChange: (String) -> Unit,
    onSearch: () -> Unit
) {
    // Pure UI rendering
}
```

### UDF Benefits

| Benefit | Description |
|---------|-------------|
| **Predictability** | State changes only through defined actions |
| **Debugging** | Easy to trace which event caused a change |
| **Testability** | Stateless UI is easy to test |
| **Consistency** | No desynchronization between components |
| **Time-travel debugging** | Can reproduce any state |

### Anti-patterns - UDF Violations

```kotlin
// Violation 1: Bidirectional data flow
@Composable
fun BadCounter() {
    var count by remember { mutableStateOf(0) }  // State in View

    // View both owns and mutates state - no SSOT
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// Violation 2: Direct state mutation
class BadViewModel : ViewModel() {
    val items = mutableListOf<Item>()  // Mutable, not Flow

    fun addItem(item: Item) {
        items.add(item)  // Mutation, View won't know
    }
}

// Correct: Single merged state as SSOT
class CorrectViewModel : ViewModel() {
    private val localItems = MutableStateFlow<List<Item>>(emptyList())
    private val remoteItems = MutableStateFlow<List<Item>>(emptyList())

    // Single SSOT - merged state
    val items: StateFlow<List<Item>> = combine(localItems, remoteItems) { local, remote ->
        (local + remote).distinctBy { it.id }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(), emptyList())
}
```

---

## Follow-ups

- How does UDF relate to Flux/Redux patterns?
- When is it appropriate to have local state in Compose vs hoisted state?
- How do you handle shared state between multiple ViewModels in UDF?
- What are the performance implications of immutable state with large objects?

## References

- https://developer.android.com/topic/architecture/ui-layer#udf
- https://developer.android.com/jetpack/compose/state
- [[q-state-hoisting-compose--android--medium]] - State hoisting in Compose

## Related Questions

### Prerequisites

- [[q-mvvm-pattern--android--medium]] - MVVM basics
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - State management

### Related

- [[q-mvi-architecture--android--hard]] - MVI architecture
- [[q-mvi-pattern--architecture--hard]] - MVI deep dive
- [[q-state-hoisting-compose--android--medium]] - Compose state hoisting

### Advanced

- [[q-state-machines--architecture--hard]] - Finite state machines
- [[q-side-effects-architecture--architecture--medium]] - Side effects

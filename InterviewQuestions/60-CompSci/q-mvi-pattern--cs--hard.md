---
id: cs-014
title: "MVI Pattern / Паттерн MVI (Model-View-Intent)"
aliases: ["MVI Pattern", "Паттерн MVI"]
topic: cs
subtopics: [android-architecture, architecture-patterns, state-management, unidirectional-data-flow]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-clean-architecture--architecture-patterns--hard, q-mvp-pattern--architecture-patterns--medium, q-mvvm-pattern--architecture-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [android-architecture, difficulty/hard, mvi, mvp, mvvm, redux, state-management, unidirectional-data-flow]
sources: [https://proandroiddev.com/mvi-a-new-member-of-the-mv-band-6f7f0d23bc8a]
date created: Monday, October 6th 2025, 7:36:32 am
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Что такое паттерн MVI? Когда его использовать и как он работает?

# Question (EN)
> What is the MVI pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория MVI Pattern:**
MVI (Model-View-Intent) - архитектурный паттерн для Android с unidirectional data flow. Вдохновлён Cycle.js framework. Решает проблему: управление state в complex applications. Model представляет immutable state, View отображает state, Intent представляет user actions или app events. Data flows: Intent → Model → View (цикл).

**Определение:**

*Теория:* MVI - один из новейших архитектурных паттернов для Android. Работает unidirectional data flow от user actions через model к view. Model - immutable state (single source of truth). View реализуется в Activity/Fragment, просто отображает state. Intent - user actions или app events, трансформируются в new state.

```kotlin
// ✅ MVI Basic Example
sealed class MviState {
    object Loading : MviState()
    data class Success(val data: List<Item>) : MviState()
    data class Error(val message: String) : MviState()
}

sealed class MviIntent {
    object LoadData : MviIntent()
    object RefreshData : MviIntent()
    data class ItemClick(val item: Item) : MviIntent()
}

class MviViewModel : ViewModel() {
    private val _state = MutableStateFlow<MviState>(MviState.Loading)
    val state: StateFlow<MviState> = _state.asStateFlow()

    fun processIntent(intent: MviIntent) {
        when (intent) {
            is MviIntent.LoadData -> {
                _state.value = MviState.Loading
                viewModelScope.launch {
                    try {
                        val data = repository.loadData()
                        _state.value = MviState.Success(data)
                    } catch (e: Exception) {
                        _state.value = MviState.Error(e.message ?: "Error")
                    }
                }
            }
            // ... other intents
        }
    }
}
```

**MVI Workflow:**

*Теория:* MVI workflow циклический: 1) User interaction создаёт Intent. 2) Intent передаётся в Model. 3) Model обрабатывает Intent и создаёт new State. 4) View получает new State и отображает его. 5) User видит updated UI. Цикл повторяется для каждого user action. Unidirectional flow обеспечивает predictable behavior.

```kotlin
// ✅ MVI Workflow
class MainActivity : AppCompatActivity() {
    private val viewModel: MviViewModel = /* ... */

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Observe state
        lifecycleScope.launch {
            viewModel.state.collect { state ->
                render(state)  // View renders state
            }
        }

        // User interactions create Intents
        button.setOnClickListener {
            viewModel.processIntent(MviIntent.LoadData)  // Intent → Model
        }
    }

    private fun render(state: MviState) {
        when (state) {
            is MviState.Loading -> showLoading()
            is MviState.Success -> showData(state.data)
            is MviState.Error -> showError(state.message)
        }
    }
}
```

**Ключевые принципы:**

*Теория:* MVI основан на 4 принципах: Single Source of Truth (один state для всего screen), Immutable State (states не изменяются после создания), Unidirectional Data Flow (Intent → Model → View), Reactive Programming (StateFlow для state propagation).

**1. Single Source of Truth:**

```kotlin
// ✅ Один state для всего screen
data class FeatureState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?,
    val selectedItem: Item?
)

class FeatureViewModel : ViewModel() {
    private val _state = MutableStateFlow<FeatureState>(
        FeatureState(false, null, null, null)
    )
    val state: StateFlow<FeatureState> = _state.asStateFlow()

    // Все изменения state через новую копию
    fun updateState(newState: FeatureState) {
        _state.value = newState
    }
}
```

**2. Immutable State:**

```kotlin
// ✅ Immutable state
data class TodoState(
    val todos: List<Todo>,
    val filter: FilterType,
    val isLoading: Boolean
) {
    fun withTodos(todos: List<Todo>) = copy(todos = todos)
    fun withFilter(filter: FilterType) = copy(filter = filter)
    fun withLoading(isLoading: Boolean) = copy(isLoading = isLoading)
}
```

**3. Unidirectional Flow:**

*Теория:* Data flows в одном direction: Intent → Model → View. User actions (clicks, input) → Intents → ViewModel processes → new State → View renders. No back-flow или circular dependencies. Это делает code predictable и testable.

```kotlin
// ✅ Unidirectional flow пример
sealed class Intent {
    object Refresh : Intent()
    data class Filter(val type: FilterType) : Intent()
}

class ViewModel {
    fun processIntent(intent: Intent): Flow<State> = when (intent) {
        is Intent.Refresh -> {
            flow {
                emit(State.Loading)
                val data = repository.fetch()
                emit(State.Success(data))
            }
        }
        // ...
    }
}
```

**Преимущества:**

1. **No State Problems** - one source of truth для state
2. **Unidirectional Flow** - predictable и easy to understand
3. **Immutability** - thread-safe, share-able benefits
4. **Debuggability** - можно log state changes и reproduce bugs
5. **Decoupled Logic** - каждый component имеет responsibility
6. **Testability** - test через business methods и check states

**Недостатки:**

1. **Boilerplate** - каждый UI change требует Intent и State objects
2. **Complexity** - много logic, нужно time для newcomers learn
3. **Object Creation** - может создавать много objects (memory issues)
4. **SingleLiveEvents** - сложно для one-time events (snackbars)

**Когда использовать:**

*Теория:* Используйте MVI когда: complex UI с multiple state changes, need strict state management, debugging state changes critical, feature-rich apps с complex interactions. Не используйте для: simple UIs (over-engineering), simple use cases (too much boilerplate).

✅ **Use MVI when:**
- Complex UI с multiple states
- Need strict state management
- Debugging critical
- Feature-rich applications

❌ **Don't use MVI when:**
- Simple UI (over-engineering)
- Simple use cases (too much boilerplate)
- Team не знаком с reactive programming

**MVI vs MVVM vs MVP:**

*Теория:* MVVM - two-way binding (View ↔ ViewModel), LiveData/StateFlow для state. MVP - View пассивная, Presenter updates View. MVI - unidirectional flow, Intent-based, immutable state. MVI более strict и predictable, но больше boilerplate.

**Ключевые концепции:**

1. **Unidirectional Flow** - data flows в одном direction
2. **Single Source of Truth** - один state для всего feature
3. **Immutability** - states immutable после создания
4. **Intent-Based** - все actions как Intents
5. **Reactive State** - state propagated через reactive streams

## Answer (EN)

**MVI Pattern Theory:**
MVI (Model-View-Intent) - architecture pattern for Android with unidirectional data flow. Inspired by Cycle.js framework. Solves problem: state management in complex applications. Model represents immutable state, View displays state, Intent represents user actions or app events. Data flows: Intent → Model → View (cycle).

**Definition:**

*Theory:* MVI - one of newest architecture patterns for Android. Works with unidirectional data flow from user actions through model to view. Model - immutable state (single source of truth). View implemented in Activity/Fragment, simply displays state. Intent - user actions or app events, transformed into new state.

```kotlin
// ✅ MVI Basic Example
sealed class MviState {
    object Loading : MviState()
    data class Success(val data: List<Item>) : MviState()
    data class Error(val message: String) : MviState()
}

sealed class MviIntent {
    object LoadData : MviIntent()
    object RefreshData : MviIntent()
    data class ItemClick(val item: Item) : MviIntent()
}

class MviViewModel : ViewModel() {
    private val _state = MutableStateFlow<MviState>(MviState.Loading)
    val state: StateFlow<MviState> = _state.asStateFlow()

    fun processIntent(intent: MviIntent) {
        when (intent) {
            is MviIntent.LoadData -> {
                _state.value = MviState.Loading
                viewModelScope.launch {
                    try {
                        val data = repository.loadData()
                        _state.value = MviState.Success(data)
                    } catch (e: Exception) {
                        _state.value = MviState.Error(e.message ?: "Error")
                    }
                }
            }
            // ... other intents
        }
    }
}
```

**MVI Workflow:**

*Theory:* MVI workflow is cyclical: 1) User interaction creates Intent. 2) Intent passed to Model. 3) Model processes Intent and creates new State. 4) View receives new State and displays it. 5) User sees updated UI. Cycle repeats for each user action. Unidirectional flow ensures predictable behavior.

```kotlin
// ✅ MVI Workflow
class MainActivity : AppCompatActivity() {
    private val viewModel: MviViewModel = /* ... */

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Observe state
        lifecycleScope.launch {
            viewModel.state.collect { state ->
                render(state)  // View renders state
            }
        }

        // User interactions create Intents
        button.setOnClickListener {
            viewModel.processIntent(MviIntent.LoadData)  // Intent → Model
        }
    }

    private fun render(state: MviState) {
        when (state) {
            is MviState.Loading -> showLoading()
            is MviState.Success -> showData(state.data)
            is MviState.Error -> showError(state.message)
        }
    }
}
```

**Key Principles:**

*Theory:* MVI based on 4 principles: Single Source of Truth (one state for entire screen), Immutable State (states can't be modified after creation), Unidirectional Data Flow (Intent → Model → View), Reactive Programming (StateFlow for state propagation).

**1. Single Source of Truth:**

```kotlin
// ✅ One state for entire screen
data class FeatureState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?,
    val selectedItem: Item?
)

class FeatureViewModel : ViewModel() {
    private val _state = MutableStateFlow<FeatureState>(
        FeatureState(false, null, null, null)
    )
    val state: StateFlow<FeatureState> = _state.asStateFlow()

    // All state changes through new copy
    fun updateState(newState: FeatureState) {
        _state.value = newState
    }
}
```

**2. Immutable State:**

```kotlin
// ✅ Immutable state
data class TodoState(
    val todos: List<Todo>,
    val filter: FilterType,
    val isLoading: Boolean
) {
    fun withTodos(todos: List<Todo>) = copy(todos = todos)
    fun withFilter(filter: FilterType) = copy(filter = filter)
    fun withLoading(isLoading: Boolean) = copy(isLoading = isLoading)
}
```

**3. Unidirectional Flow:**

*Theory:* Data flows in one direction: Intent → Model → View. User actions (clicks, input) → Intents → ViewModel processes → new State → View renders. No back-flow or circular dependencies. This makes code predictable and testable.

```kotlin
// ✅ Unidirectional flow example
sealed class Intent {
    object Refresh : Intent()
    data class Filter(val type: FilterType) : Intent()
}

class ViewModel {
    fun processIntent(intent: Intent): Flow<State> = when (intent) {
        is Intent.Refresh -> {
            flow {
                emit(State.Loading)
                val data = repository.fetch()
                emit(State.Success(data))
            }
        }
        // ...
    }
}
```

**Advantages:**

1. **No State Problems** - one source of truth for state
2. **Unidirectional Flow** - predictable and easy to understand
3. **Immutability** - thread-safe, share-able benefits
4. **Debuggability** - can log state changes and reproduce bugs
5. **Decoupled Logic** - each component has responsibility
6. **Testability** - test through business methods and check states

**Disadvantages:**

1. **Boilerplate** - each UI change requires Intent and State objects
2. **Complexity** - much logic, need time for newcomers to learn
3. **Object Creation** - may create many objects (memory issues)
4. **SingleLiveEvents** - complex for one-time events (snackbars)

**When to Use:**

*Theory:* Use MVI when: complex UI with multiple state changes, need strict state management, debugging state changes critical, feature-rich apps with complex interactions. Don't use for: simple UIs (over-engineering), simple use cases (too much boilerplate).

✅ **Use MVI when:**
- Complex UI with multiple states
- Need strict state management
- Debugging critical
- Feature-rich applications

❌ **Don't use MVI when:**
- Simple UI (over-engineering)
- Simple use cases (too much boilerplate)
- Team not familiar with reactive programming

**MVI vs MVVM vs MVP:**

*Theory:* MVVM - two-way binding (View ↔ ViewModel), LiveData/StateFlow for state. MVP - View passive, Presenter updates View. MVI - unidirectional flow, Intent-based, immutable state. MVI more strict and predictable, but more boilerplate.

**Key Concepts:**

1. **Unidirectional Flow** - data flows in one direction
2. **Single Source of Truth** - one state for entire feature
3. **Immutability** - states immutable after creation
4. **Intent-Based** - all actions as Intents
5. **Reactive State** - state propagated through reactive streams

---

## Follow-ups

- What is the difference between MVI and Redux?
- How do you handle SingleLiveEvents in MVI architecture?
- When should you choose MVVM over MVI?

## Related Questions

### Prerequisites (Easier)
- Basic Android architecture concepts
- Understanding of MVP/MVVM patterns

### Related (Same Level)
- [[q-mvvm-pattern--architecture-patterns--medium]] - MVVM pattern
- [[q-mvp-pattern--architecture-patterns--medium]] - MVP pattern

### Advanced (Harder)
- [[q-clean-architecture--architecture-patterns--hard]] - Clean Architecture
- Advanced state management patterns
- Redux vs MVI comparison

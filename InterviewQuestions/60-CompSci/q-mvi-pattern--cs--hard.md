---id: cs-014
title: "MVI Pattern / Паттерн MVI (Model-View-Intent)"
aliases: ["MVI Pattern", "Паттерн MVI"]
topic: cs
subtopics: [architecture-patterns, state-management, unidirectional-data-flow]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-builder-pattern, c-ci-cd-patterns, c-command-pattern, c-dao-pattern, c-declarative-programming-patterns, c-decorator-pattern, c-factory-pattern, q-android-architectural-patterns--android--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [architecture-patterns, difficulty/hard, mvi, mvp, mvvm, redux, state-management, unidirectional-data-flow]
sources: ["https://proandroiddev.com/mvi-a-new-member-of-the-mv-band-6f7f0d23bc8a"]
---
# Вопрос (RU)
> Что такое паттерн MVI? Когда его использовать и как он работает?

# Question (EN)
> What is the MVI pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория MVI Pattern:**
MVI (Model-`View`-`Intent`) — архитектурный паттерн с unidirectional data flow, часто используемый в Android и фронтенд-приложениях. Идеи вдохновлены Cycle.js и Redux-подобными подходами к управлению состоянием. Основной фокус — предсказуемое управление состоянием в сложных интерфейсах.

В классическом формулировании:
- Model — это не «слой данных» в смысле Android, а «модель состояния» + бизнес-логика/редьюсер (store), которая хранит и изменяет immutable state.
- `View` — отображает текущее состояние и порождает пользовательские события.
- `Intent` — намерения пользователя или события системы, которые описывают «что произошло».

Поток данных организован как цикл:
`View` → `Intent` → Model (обработка/редьюсер → новый State) → `View`.
При этом направление данных одностороннее (нет двустороннего биндинга), а цикл образуется за счет повторяющихся итераций цикла взаимодействия.

**Определение:**

*Теория:* MVI — архитектурный паттерн с односторонним потоком данных, где все изменения UI описываются как преобразования `Intent` → State:
- Model: immutable state (single source of truth) для конкретного экрана/фичи.
- `View`: реализуется в `Activity`/`Fragment`/Compose и только отображает state и отправляет Intents.
- `Intent`: пользовательские действия или события системы, которые приводят к вычислению нового state.

```kotlin
// ✅ MVI Basic Example (упрощённо)
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

class MviViewModel(
    private val repository: Repository
) : ViewModel() { // androidx.lifecycle.ViewModel

    private val _state = MutableStateFlow<MviState>(MviState.Loading)
    val state: StateFlow<MviState> = _state.asStateFlow()

    fun processIntent(intent: MviIntent) {
        when (intent) {
            is MviIntent.LoadData, is MviIntent.RefreshData -> {
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
            is MviIntent.ItemClick -> {
                // Обработка клика может порождать отдельный эффект/навигацию
            }
        }
    }
}
```

**MVI Workflow:**

*Теория:* MVI workflow цикличен по взаимодействию, но поток данных остаётся односторонним:
1. User interaction во `View` создаёт `Intent`.
2. `Intent` передаётся в слой Model (`ViewModel`/Reducer/Store).
3. Model обрабатывает `Intent`, запрашивает данные при необходимости и эмитит новый State.
4. `View` подписана на поток State, получает новый State и отображает его.
5. Пользователь видит обновлённый UI и совершает новые действия.

```kotlin
// ✅ MVI Workflow (наблюдение state + отправка intents)
class MainActivity : AppCompatActivity() {
    private val viewModel: MviViewModel = /* ... */

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)

        // Observe state (lifecycle-aware in real code)
        lifecycleScope.launch {
            viewModel.state.collect { state ->
                render(state)  // View renders state
            }
        }

        // User interactions create Intents
        button.setOnClickListener {
            viewModel.processIntent(MviIntent.LoadData)  // View → Intent → Model
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

*Теория:* Классический MVI опирается на принципы:
- Single Source of Truth — один источник истины для состояния конкретного экрана/фичи.
- Immutable State — состояния не мутируют, а заменяются новыми экземплярами.
- Unidirectional Data `Flow` — данные текут в одном направлении: `View` → `Intent` → Model/Reducer → State → `View`.
- Reactive Programming — распространение состояний через реактивные стримы (`Flow`, Rx, и т.п.).

**1. Single Source of Truth:**

```kotlin
// ✅ Один state для всего экрана
data class FeatureState(
    val isLoading: Boolean,
    val data: List<Item>?,
    val error: String?,
    val selectedItem: Item?
)

class FeatureViewModel : ViewModel() {
    private val _state = MutableStateFlow(
        FeatureState(isLoading = false, data = null, error = null, selectedItem = null)
    )
    val state: StateFlow<FeatureState> = _state.asStateFlow()

    // Все изменения — через публикацию нового значения
    fun updateState(reducer: (FeatureState) -> FeatureState) {
        _state.value = reducer(_state.value)
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

**3. Unidirectional `Flow`:**

*Теория:* Данные текут в одном направлении: `View` генерирует Intents → Model/Reducer обрабатывает их и эмитит новый State → `View` отображает этот State. Нет двустороннего биндинга и прямых циклических зависимостей; цикл взаимодействия формируется повторением шага `Intent` → State → Render.

```kotlin
// ✅ Упрощённый пример одностороннего потока
sealed class Intent {
    object Refresh : Intent()
    data class Filter(val type: FilterType) : Intent()
}

sealed class State {
    object Loading : State()
    data class Success(val items: List<Item>) : State()
}

class MviStore(
    private val repository: Repository
) {
    private val _state = MutableStateFlow<State>(State.Loading)
    val state: StateFlow<State> = _state.asStateFlow()

    fun dispatch(intent: Intent) {
        when (intent) {
            is Intent.Refresh -> {
                _state.value = State.Loading
                // launch in scope in real implementation
            }
            is Intent.Filter -> {
                // обновление state через copy/новый объект
            }
        }
    }
}
```

**Преимущества:**

1. Single Source of Truth — меньше проблем с рассинхронизацией состояния.
2. Unidirectional `Flow` — предсказуемое поведение, проще reasoning.
3. Immutability — упрощает отладку и делает состояние более безопасным для многопоточности.
4. Debuggability — можно логировать последовательность Intents и States и воспроизводить баги.
5. Decoupled Logic — бизнес-логика изолирована в reducer/store/`ViewModel`.
6. Testability — можно тестировать преобразования `Intent` → State как чистые сценарии.

**Недостатки:**

1. Boilerplate — много типов (State, `Intent`, Effects), особенно для простых экранов.
2. Complexity — концептуально сложнее для команды без опыта с реактивным/функциональным подходом.
3. Object Creation — частое создание новых State-объектов, что требует аккуратности (но обычно приемлемо).
4. One-time events (effects) — требуют отдельного механизма (effects/side-effects channel), нельзя просто зашить их в persistent state.

**Когда использовать:**

*Теория:* Используйте MVI, когда:
- UI сложный, с множеством состояний и переходов.
- Нужен строгий контроль над состоянием и история изменений.
- Важна предсказуемость и воспроизводимость (logging, time-travel, дебаг).
- Приложение/фича насыщены взаимодействиями и побочными эффектами.

Не используйте (или не переусложняйте) MVI, когда:
- Экран очень простой, MVI создаёт избыточный boilerplate.
- Команда не готова к реактивной/функциональной модели и строгим инвариантам.

✅ Использовать MVI, когда:
- Complex UI с multiple states.
- Need strict state management.
- Debugging critical.
- Feature-rich applications.

❌ Не использовать MVI, когда:
- Simple UI (over-engineering).
- Simple use cases (too much boilerplate).
- Team не знакома с reactive programming и эффектами.

**MVI vs MVVM vs MVP:**

*Теория:*
- MVP: `View` пассивная, Presenter управляет `View` и часто напрямую вызывает методы `View` — поток часто менее строго односторонний.
- MVVM: `View` наблюдает за `ViewModel` (`LiveData`/`StateFlow`); нередко используется двусторонний биндинг, возможны более сложные зависимости.
- MVI: строго односторонний поток, `Intent`-ориентированная модель, единый immutable state. Более строгий и предсказуемый, но требует больше кода и дисциплины.

**Ключевые концепции:**

1. Unidirectional `Flow` — данные текут в одном направлении (`View` → `Intent` → Model/Reducer → State → `View`).
2. Single Source of Truth — один state-контейнер для фичи/экрана.
3. Immutability — состояние не мутирует, а переопределяется.
4. `Intent`-Based — любые действия и события описываются как Intents.
5. Reactive State — состояния распространяются через реактивные стримы.

## Answer (EN)

**MVI Pattern Theory:**
MVI (Model-`View`-`Intent`) is an architectural pattern with unidirectional data flow, commonly used in Android and frontend applications. It is inspired by Cycle.js and Redux-like state management approaches. Its primary focus is predictable state management in complex UIs.

In the classic formulation:
- Model is not just a "data layer"; it is the state model plus business logic/reducer (store) that holds and transforms immutable state.
- `View` renders the current state and emits user events.
- `Intent` represents user intentions or system events describing "what happened".

The data flow is organized as a cycle:
`View` → `Intent` → Model (handling/reducer → new State) → `View`.
The flow direction is one-way (no two-way binding); the cycle appears from repeated iterations of this loop.

**Definition:**

*Theory:* MVI is an architectural pattern with unidirectional data flow where all UI updates are modeled as transformations `Intent` → State:
- Model: immutable state (single source of truth) for the given screen/feature.
- `View`: implemented in `Activity`/`Fragment`/Compose and only renders state and sends Intents.
- `Intent`: user actions or system events that lead to computing a new state.

```kotlin
// ✅ MVI Basic Example (simplified)
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

class MviViewModel(
    private val repository: Repository
) : ViewModel() { // androidx.lifecycle.ViewModel

    private val _state = MutableStateFlow<MviState>(MviState.Loading)
    val state: StateFlow<MviState> = _state.asStateFlow()

    fun processIntent(intent: MviIntent) {
        when (intent) {
            is MviIntent.LoadData, is MviIntent.RefreshData -> {
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
            is MviIntent.ItemClick -> {
                // Handle click: may trigger navigation/one-time effect
            }
        }
    }
}
```

**MVI Workflow:**

*Theory:* The MVI workflow is cyclical in interaction, but the data flow remains one-way:
1. User interaction in the `View` creates an `Intent`.
2. `Intent` is passed to the Model layer (`ViewModel`/Reducer/Store).
3. Model processes the `Intent`, performs data requests if needed, and emits a new State.
4. `View` subscribes to the State stream, receives the new State, and renders it.
5. User sees updated UI and performs new actions.

```kotlin
// ✅ MVI Workflow (observe state + send intents)
class MainActivity : AppCompatActivity() {
    private val viewModel: MviViewModel = /* ... */

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(...)

        // Observe state (lifecycle-aware in real code)
        lifecycleScope.launch {
            viewModel.state.collect { state ->
                render(state)  // View renders state
            }
        }

        // User interactions create Intents
        button.setOnClickListener {
            viewModel.processIntent(MviIntent.LoadData)  // View → Intent → Model
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

*Theory:* Classic MVI relies on:
- Single Source of Truth: one state holder per screen/feature.
- Immutable State: states are not mutated; new instances are produced.
- Unidirectional Data `Flow`: `View` → `Intent` → Model/Reducer → State → `View`.
- Reactive Programming: state propagation via reactive streams (`Flow`, Rx, etc.).

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
    private val _state = MutableStateFlow(
        FeatureState(isLoading = false, data = null, error = null, selectedItem = null)
    )
    val state: StateFlow<FeatureState> = _state.asStateFlow()

    // All state changes via publishing a new value
    fun updateState(reducer: (FeatureState) -> FeatureState) {
        _state.value = reducer(_state.value)
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

**3. Unidirectional `Flow`:**

*Theory:* Data flows in one direction: the `View` emits Intents → Model/Reducer handles them and emits new State → `View` renders that State. There is no two-way binding or direct circular dependencies; the interaction loop is `Intent` → State → Render repeated over time.

```kotlin
// ✅ Simplified unidirectional flow example
sealed class Intent {
    object Refresh : Intent()
    data class Filter(val type: FilterType) : Intent()
}

sealed class State {
    object Loading : State()
    data class Success(val items: List<Item>) : State()
}

class MviStore(
    private val repository: Repository
) {
    private val _state = MutableStateFlow<State>(State.Loading)
    val state: StateFlow<State> = _state.asStateFlow()

    fun dispatch(intent: Intent) {
        when (intent) {
            is Intent.Refresh -> {
                _state.value = State.Loading
                // launch async load and update _state in real implementation
            }
            is Intent.Filter -> {
                // update state via new instances
            }
        }
    }
}
```

**Advantages:**

1. Single Source of Truth — reduces state desynchronization issues.
2. Unidirectional `Flow` — predictable behavior, easier reasoning.
3. Immutability — simplifies debugging and is safer for concurrency.
4. Debuggability — you can log `Intent`/State sequences and reproduce bugs.
5. Decoupled Logic — business logic isolated in reducer/store/`ViewModel`.
6. Testability — `Intent` → State transformations are easy to unit test.

**Disadvantages:**

1. Boilerplate — many types (State, `Intent`, Effects), especially for simple screens.
2. Complexity — conceptually heavier for teams new to reactive/functional style.
3. Object Creation — frequent new State instances; usually fine but requires care.
4. One-time events (effects) — require a dedicated mechanism (effects/side-effects channel) rather than being embedded in persistent state.

**When to Use:**

*Theory:* Use MVI when:
- UI is complex with many states and transitions.
- You need strict state management and auditability.
- Predictability and debuggability are critical.
- Features have rich interactions and side effects.

Avoid (or avoid over-engineering with MVI) when:
- Screen is very simple and MVI adds unnecessary boilerplate.
- Team is not ready for reactive/functional patterns and strict invariants.

✅ Use MVI when:
- Complex UI with multiple states.
- Need strict state management.
- Debugging is critical.
- Feature-rich applications.

❌ Don't use MVI when:
- Simple UI (over-engineering).
- Simple use cases (too much boilerplate).
- Team not familiar with reactive programming and effects.

**MVI vs MVVM vs MVP:**

*Theory:*
- MVP: passive `View`, Presenter manipulates `View` and may create looser unidirectional constraints.
- MVVM: `View` observes `ViewModel` (`LiveData`/`StateFlow`); often two-way binding is used, which can blur strict one-way flow.
- MVI: strictly unidirectional, `Intent`-based, immutable single state. More predictable but more verbose and demanding.

**Key Concepts:**

1. Unidirectional `Flow` — one-way data flow (`View` → `Intent` → Model/Reducer → State → `View`).
2. Single Source of Truth — one state container for a feature/screen.
3. Immutability — state is not mutated but replaced.
4. `Intent`-Based — all actions and events represented as Intents.
5. Reactive State — state propagated via reactive streams.

---

## Follow-ups

- What is the difference between MVI and Redux?
- How do you handle one-time events / side effects in MVI architecture?
- When should you choose MVVM over MVI?

## Related Questions

### Prerequisites (Easier)
- Basic Android architecture concepts
- Understanding of MVP/MVVM patterns

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]] - Android architectural patterns

### Advanced (Harder)
- Advanced state management patterns
- Redux vs MVI comparison

## References

- [[c-architecture-patterns]]
- [[q-android-architectural-patterns--android--medium]]
- "MVI - a new member of the MVx band" on ProAndroidDev

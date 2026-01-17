---id: android-125
id: android-711
anki_cards:
  - slug: android-125-0-en
    front: "What are the three components of MVVM pattern in Android?"
    back: |
      **Model** - Data layer (Repository, Use Cases)
      **View** - UI layer (Activity, Fragment, Composable)
      **ViewModel** - Manages UI state, survives config changes

      **Key:** ViewModel exposes observable state (LiveData/StateFlow), View subscribes and updates UI. ViewModel never holds View references.
    tags:
      - android_architecture
      - android_viewmodel
      - difficulty::medium
  - slug: android-125-0-ru
    front: "Каковы три компонента паттерна MVVM в Android?"
    back: |
      **Model** - Слой данных (Repository, Use Cases)
      **View** - Слой UI (Activity, Fragment, Composable)
      **ViewModel** - Управляет UI-состоянием, переживает изменения конфигурации

      **Ключевое:** ViewModel предоставляет observable-состояние (LiveData/StateFlow), View подписывается и обновляет UI. ViewModel никогда не хранит ссылки на View.
    tags:
      - android_architecture
      - android_viewmodel
      - difficulty::medium
title: "MVVM Pattern / Паттерн MVVM"
aliases: ["Model-View-ViewModel", "MVVM Pattern", "Паттерн MVVM"]
topic: android
subtopics: [architecture-mvvm, coroutines, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-builder-pattern, c-ci-cd-patterns, c-command-pattern, c-dao-pattern, c-declarative-programming-patterns, c-decorator-pattern, c-factory-pattern, c-mvvm-pattern, c-viewmodel, q-what-is-viewmodel--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/architecture-mvvm, android/coroutines, android/lifecycle, architecture-patterns, difficulty/medium, mvvm, viewmodel]

---
# Вопрос (RU)

> Что такое архитектурный паттерн MVVM (Model-`View`-`ViewModel`)? Объясните его компоненты и преимущества.

# Question (EN)

> What is the MVVM (Model-`View`-`ViewModel`) architectural pattern? Explain its components and advantages.

---

## Ответ (RU)

**MVVM (Model-`View`-`ViewModel`)** — архитектурный паттерн для разделения UI и бизнес-логики через наблюдаемые источники данных и односторонний поток данных (unidirectional data flow).

### Компоненты

**Model** — источник и логика данных (Repository, Use Cases, domain logic). Независим от UI.

**`View`** — UI слой (`Activity`, `Fragment`, Composable). Наблюдает за состоянием из `ViewModel` (например, через `LiveData`/`StateFlow`/Compose state). Не содержит бизнес-логики.

**`ViewModel`** — управляет UI-состоянием, переживает configuration changes в рамках своего владельца (ViewModelStoreOwner), предоставляет данные через observable streams. Не хранит ссылки на `View` или короткоживущие контексты (что предотвращает утечки памяти).

### Реализация

```kotlin
// ✅ Правильно: единый источник истины

data class UserUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class UserViewModel(
    private val repository: UserRepository // ✅ Инъекция зависимости
) : ViewModel() {
    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow() // ✅ Immutable для View

    fun loadUser(id: Int) {
        viewModelScope.launch { // ✅ Коррутины отменяются при onCleared()
            _uiState.update { it.copy(isLoading = true, error = null) }
            repository.getUser(id)
                .onSuccess { user ->
                    _uiState.update { it.copy(user = user, isLoading = false) }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(error = error.message, isLoading = false)
                    }
                }
        }
    }
}

// View (Compose)
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        uiState.isLoading -> LoadingView()
        uiState.error != null -> ErrorView(uiState.error!!)
        else -> uiState.user?.let { UserContent(it) }
    }
}
```

### Преимущества Vs Недостатки

| Плюсы | Минусы |
|-------|--------|
| `ViewModel` переиспользуется через ViewModelStore и сохраняется при configuration changes владельца | Избыточен для простых экранов |
| Тестируемость бизнес-логики и состояния без UI | Требует знаний реактивных/асинхронных подходов |
| Меньше утечек памяти (`ViewModel` не держит `View`/`Activity`/`Fragment`) | Может усложнять дизайн для очень больших экранов и сложных состояний |
| Чёткое разделение ответственностей (Separation of concerns) | Отладка связей/обновлений состояния может быть нетривиальной |

### Сравнение С Другими Паттернами

**vs MVP**: В MVVM `ViewModel` экспонирует наблюдаемое состояние (`LiveData`/`Flow`/Compose state), `View` подписывается и обновляет UI на основе изменений. В MVP Presenter обычно напрямую вызывает методы `View` через интерфейс. `ViewModel` хранится во ViewModelStore и может переживать configuration changes, Presenter (без дополнительной обвязки) — нет.

**vs MVI**: MVVM обычно допускает несколько observable-потоков состояния и более гибкий API методов во `ViewModel`. MVI подчёркивает единый immutable state и явные user intents → reducer → новое состояние. В MVVM user intents чаще отображаются на методы `ViewModel` с обновлением одного или нескольких потоков состояния.

### Best Practices

```kotlin
// ✅ DO: Не тянуть во ViewModel ссылки на View/Activity/Fragment или другие короткоживущие объекты
class UserViewModel(private val repo: UserRepository) : ViewModel()

// ❌ DON'T: Прямые зависимости от View или short-lived Context
class BadViewModel(private val context: Context) : ViewModel() // риск утечки, если это Activity/Fragment context
class BadViewModel(private val view: UserView) : ViewModel()
```

Допустимы безопасные зависимости, предоставляемые фреймворком, такие как SavedStateHandle или `Application` (через AndroidViewModel), когда они обоснованы архитектурой.

См. также [[c-viewmodel]] и [[c-mvvm-pattern]].

---

## Answer (EN)

**MVVM (Model-`View`-`ViewModel`)** is an architectural pattern that separates UI from business logic using observable data and a unidirectional data flow between layers.

### Components

**Model** — data and domain logic (Repository, Use Cases, business rules). Independent of the UI.

**`View`** — UI layer (`Activity`, `Fragment`, Composable). Observes state exposed by the `ViewModel` (e.g., via `LiveData`/`StateFlow`/Compose state). Contains no business logic.

**`ViewModel`** — manages UI state, is retained across configuration changes within its owner (ViewModelStoreOwner), and exposes data via observable streams. It does not hold references to the `View` or other short-lived UI components, which helps prevent memory leaks.

### Implementation

```kotlin
// ✅ Correct: single source of truth

data class UserUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class UserViewModel(
    private val repository: UserRepository // ✅ Dependency injection
) : ViewModel() {
    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow() // ✅ Immutable for View

    fun loadUser(id: Int) {
        viewModelScope.launch { // ✅ Coroutines cancelled on onCleared()
            _uiState.update { it.copy(isLoading = true, error = null) }
            repository.getUser(id)
                .onSuccess { user ->
                    _uiState.update { it.copy(user = user, isLoading = false) }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(error = error.message, isLoading = false)
                    }
                }
        }
    }
}

// View (Compose)
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        uiState.isLoading -> LoadingView()
        uiState.error != null -> ErrorView(uiState.error!!)
        else -> uiState.user?.let { UserContent(it) }
    }
}
```

### Pros Vs Cons

| Pros | Cons |
|------|------|
| `ViewModel` is retained via ViewModelStore across configuration changes of its owner | Overkill for simple screens |
| Business logic and state can be tested without UI | Requires understanding of reactive/asynchronous patterns |
| Fewer memory leaks (`ViewModel` does not keep references to `View`/`Activity`/`Fragment`) | Can complicate design for very large or complex screens |
| Clear separation of concerns | Debugging state updates/bindings can be non-trivial |

### Comparison with other Patterns

**vs MVP**: In MVVM, the `ViewModel` exposes observable state (`LiveData`/`Flow`/Compose state), and the `View` reacts to changes. In MVP, the Presenter typically calls `View` methods directly via interfaces. `ViewModel` is scoped to a ViewModelStoreOwner and can survive configuration changes; a basic Presenter does not unless extra mechanisms are used.

**vs MVI**: MVVM often uses multiple observable streams and method-based APIs in the `ViewModel`. MVI emphasizes a single immutable state and explicit user intents → reducer → new state. In MVVM, user intents more commonly map to `ViewModel` functions that update one or more state streams.

### Best Practices

```kotlin
// ✅ DO: Avoid holding references to View/Activity/Fragment or other short-lived Android components
class UserViewModel(private val repo: UserRepository) : ViewModel()

// ❌ DON'T: Depend directly on View or short-lived Context
class BadViewModel(private val context: Context) : ViewModel() // risk of leaks if this is an Activity/Fragment context
class BadViewModel(private val view: UserView) : ViewModel()
```

Framework-provided safe dependencies like SavedStateHandle or `Application` (via AndroidViewModel) are acceptable when justified by the architecture.

See also [[c-viewmodel]] and [[c-mvvm-pattern]].

---

## Дополнительные Вопросы (RU)

- Как обрабатывать одноразовые события (навигация, toasts) в MVVM, не нарушая unidirectional data flow?
- В чём отличия и trade-offs между использованием `MutableStateFlow.update {}` и прямым присваиванием в `value`?
- Когда вы выберете MVVM вместо MVI в крупном Android-приложении?
- Как тестировать `ViewModel`, использующий `viewModelScope` и коррутины?

## Ссылки (RU)

- [[c-viewmodel]] — жизненный цикл и управление состоянием `ViewModel`
- [[c-mvvm-pattern]] — общий обзор паттерна MVVM
- Официальная документация: https://developer.android.com/topic/architecture
- Руководство по архитектуре приложений Android: https://developer.android.com/topic/libraries/architecture

## Связанные Вопросы (RU)

### Базовые/предпосылки

- [[q-what-is-viewmodel--android--medium]] — что такое `ViewModel` и его жизненный цикл

### Связанные

- [[q-mvvm-vs-mvp-differences--android--medium]] — сравнение MVVM и MVP
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] — `ViewModel` против onSavedInstanceState для сохранения состояния
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] — назначение и внутренняя работа `ViewModel`

### Продвинутые

- [[q-mvi-architecture--android--hard]] — архитектурный паттерн MVI
- [[q-clean-architecture-android--android--hard]] — Clean Architecture вместе с MVVM
- [[q-offline-first-architecture--android--hard]] — offline-first архитектурные подходы

---

## Follow-ups

- How would you handle one-time events (navigation, toasts) in MVVM without violating unidirectional data flow?
- What are the trade-offs between using `MutableStateFlow.update {}` vs direct assignment to `value`?
- When would you choose MVVM over MVI in a large-scale Android app?
- How do you test ViewModels that use `viewModelScope` for coroutines?

## References

- [[c-viewmodel]] — `ViewModel` lifecycle and state management
- [[c-mvvm-pattern]] — MVVM pattern overview
- Official docs: https://developer.android.com/topic/architecture
- Android Guide to app architecture: https://developer.android.com/topic/libraries/architecture

## Related Questions

### Prerequisites

- [[q-what-is-viewmodel--android--medium]] — What is `ViewModel` and its lifecycle

### Related

- [[q-mvvm-vs-mvp-differences--android--medium]] — MVVM vs MVP comparison
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] — `ViewModel` vs onSavedInstanceState for state preservation
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] — `ViewModel` purpose and internals

### Advanced

- [[q-mvi-architecture--android--hard]] — MVI architecture pattern
- [[q-clean-architecture-android--android--hard]] — Clean Architecture with MVVM
- [[q-offline-first-architecture--android--hard]] — Offline-first architecture patterns

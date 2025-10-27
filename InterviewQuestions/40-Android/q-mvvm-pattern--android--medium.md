---
id: 20251012-122711
title: "MVVM Pattern / Паттерн MVVM"
aliases: ["MVVM Pattern", "Паттерн MVVM", "Model-View-ViewModel"]
topic: android
subtopics: [architecture-mvvm, lifecycle, coroutines]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-viewmodel, q-what-is-viewmodel--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/architecture-mvvm, android/lifecycle, android/coroutines, architecture-patterns, mvvm, viewmodel, difficulty/medium]
---
# Вопрос (RU)

> Что такое архитектурный паттерн MVVM (Model-View-ViewModel)? Объясните его компоненты и преимущества.

# Question (EN)

> What is the MVVM (Model-View-ViewModel) architectural pattern? Explain its components and advantages.

---

## Ответ (RU)

**MVVM (Model-View-ViewModel)** — архитектурный паттерн для разделения UI и бизнес-логики через реактивное связывание данных.

### Компоненты

**Model** — источник данных (Repository, Use Cases, domain logic). Независим от UI.

**View** — UI слой (Activity, Fragment, Composable). Наблюдает за ViewModel через LiveData/StateFlow. Не содержит бизнес-логики.

**ViewModel** — управляет UI-состоянием, переживает configuration changes, предоставляет данные через observable streams. Не хранит ссылки на View (предотвращает утечки памяти).

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
        viewModelScope.launch { // ✅ Автоматическая отмена при onCleared()
            _uiState.update { it.copy(isLoading = true) }
            repository.getUser(id)
                .onSuccess { user -> _uiState.update { it.copy(user = user, isLoading = false) } }
                .onFailure { error -> _uiState.update { it.copy(error = error.message, isLoading = false) } }
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

### Преимущества vs недостатки

| Плюсы | Минусы |
|-------|--------|
| Lifecycle-aware (выживает при rotation) | Избыточен для простых экранов |
| Тестируемость без UI | Требует знания реактивного программирования |
| Нет утечек памяти (ViewModel не держит View) | Сложность дизайна для больших экранов |
| Separation of concerns | Debugging data binding может быть труден |

### Сравнение с другими паттернами

**vs MVP**: MVVM использует data binding (автоматическое обновление UI), MVP — ручные вызовы через интерфейсы. ViewModel переживает configuration changes, Presenter — нет.

**vs MVI**: MVVM допускает multiple state streams, MVI — единый immutable state. MVI явно моделирует user intents, MVVM — методы в ViewModel.

### Best Practices

```kotlin
// ✅ DO: Нет Android-зависимостей в ViewModel
class UserViewModel(private val repo: UserRepository) : ViewModel()

// ❌ DON'T: Зависимость от Context/View
class BadViewModel(private val context: Context) : ViewModel()
class BadViewModel(private val view: UserView) : ViewModel()
```

См. также [[c-viewmodel]].

---

## Answer (EN)

**MVVM (Model-View-ViewModel)** is an architectural pattern that separates UI from business logic through reactive data binding.

### Components

**Model** — data source (Repository, Use Cases, domain logic). Independent of UI.

**View** — UI layer (Activity, Fragment, Composable). Observes ViewModel via LiveData/StateFlow. No business logic.

**ViewModel** — manages UI state, survives configuration changes, exposes data via observable streams. Doesn't hold View references (prevents memory leaks).

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
        viewModelScope.launch { // ✅ Automatic cancellation on onCleared()
            _uiState.update { it.copy(isLoading = true) }
            repository.getUser(id)
                .onSuccess { user -> _uiState.update { it.copy(user = user, isLoading = false) } }
                .onFailure { error -> _uiState.update { it.copy(error = error.message, isLoading = false) } }
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

### Pros vs Cons

| Pros | Cons |
|------|------|
| Lifecycle-aware (survives rotation) | Overkill for simple screens |
| Testability without UI | Requires reactive programming knowledge |
| No memory leaks (ViewModel doesn't hold View) | Complex design for large screens |
| Separation of concerns | Data binding debugging can be difficult |

### Comparison with other patterns

**vs MVP**: MVVM uses data binding (automatic UI updates), MVP uses manual calls via interfaces. ViewModel survives configuration changes, Presenter doesn't.

**vs MVI**: MVVM allows multiple state streams, MVI has single immutable state. MVI explicitly models user intents, MVVM has methods in ViewModel.

### Best Practices

```kotlin
// ✅ DO: No Android dependencies in ViewModel
class UserViewModel(private val repo: UserRepository) : ViewModel()

// ❌ DON'T: Dependency on Context/View
class BadViewModel(private val context: Context) : ViewModel()
class BadViewModel(private val view: UserView) : ViewModel()
```

See also [[c-viewmodel]].

---

## Follow-ups

- How would you handle one-time events (navigation, toasts) in MVVM without violating unidirectional data flow?
- What are the trade-offs between using `MutableStateFlow.update {}` vs direct assignment to `value`?
- When would you choose MVVM over MVI in a large-scale Android app?
- How do you test ViewModels that use `viewModelScope` for coroutines?

## References

- [[c-viewmodel]] — ViewModel lifecycle and state management
- Official docs: https://developer.android.com/topic/architecture
- Android Guide to app architecture: https://developer.android.com/topic/libraries/architecture

## Related Questions

### Prerequisites

- [[q-what-is-viewmodel--android--medium]] — What is ViewModel and its lifecycle

### Related

- [[q-mvvm-vs-mvp-differences--android--medium]] — MVVM vs MVP comparison
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] — ViewModel vs onSavedInstanceState for state preservation
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] — ViewModel purpose and internals

### Advanced

- [[q-mvi-architecture--android--hard]] — MVI architecture pattern
- [[q-clean-architecture-android--android--hard]] — Clean Architecture with MVVM
- [[q-offline-first-architecture--android--hard]] — Offline-first architecture patterns

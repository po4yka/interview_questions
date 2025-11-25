---
id: ivc-20251030-130000
title: MVVM Pattern / Паттерн MVVM
aliases: [Model-View-ViewModel, MVVM, Паттерн MVVM]
kind: concept
summary: Architectural pattern separating UI from business logic through three distinct layers - Model, View, and ViewModel
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, architecture-patterns, concept, design-patterns, mvvm]
date created: Thursday, October 30th 2025, 12:30:05 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

**MVVM (Model-View-ViewModel)** is an architectural pattern that separates an application into three distinct layers:

- **Model**: Data layer containing business logic, domain models, and data sources (repositories, databases, network)
- **View**: UI layer (Activities, Fragments, Composables) that observes ViewModel state and renders UI
- **ViewModel**: Presentation logic layer that holds UI state, processes user events, and exposes data streams to the View

The key principle is **unidirectional data flow**: View observes ViewModel state, user events flow to ViewModel, ViewModel updates state, View reacts to state changes. This creates a testable, maintainable architecture with clear separation of concerns.

# Сводка (RU)

**MVVM (Model-View-ViewModel)** - архитектурный паттерн, разделяющий приложение на три отдельных слоя:

- **Model**: Слой данных, содержащий бизнес-логику, доменные модели и источники данных (репозитории, базы данных, сеть)
- **View**: Слой UI (Activity, Fragment, Composable), который наблюдает за состоянием ViewModel и отображает интерфейс
- **ViewModel**: Слой логики представления, хранящий состояние UI, обрабатывающий события пользователя и предоставляющий потоки данных для View

Ключевой принцип - **однонаправленный поток данных**: View наблюдает за состоянием ViewModel, события пользователя передаются в ViewModel, ViewModel обновляет состояние, View реагирует на изменения состояния. Это создает тестируемую, поддерживаемую архитектуру с четким разделением ответственности.

---

## Core Responsibilities

**Model Layer**:
- Domain models and business entities
- Data repositories (single source of truth)
- Network and database operations
- Business logic validation

**View Layer**:
- Rendering UI based on state
- Capturing user input events
- Navigation logic
- NO business logic or state management

**ViewModel Layer**:
- Holding UI state (immutable data classes)
- Processing user events and business operations
- Exposing state streams (LiveData, StateFlow, SharedFlow)
- Lifecycle awareness (survives configuration changes)
- NO Android framework dependencies (except lifecycle-viewmodel)

---

## Android Implementation

### ViewModel with State

```kotlin
data class UserProfileState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class UserProfileViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UserProfileState())
    val state: StateFlow<UserProfileState> = _state.asStateFlow()

    private val _events = Channel<NavigationEvent>()
    val events: Flow<NavigationEvent> = _events.receiveAsFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }

            userRepository.getUser(userId)
                .onSuccess { user ->
                    _state.update { it.copy(user = user, isLoading = false) }
                }
                .onFailure { error ->
                    _state.update { it.copy(error = error.message, isLoading = false) }
                }
        }
    }

    fun onEditClicked() {
        viewModelScope.launch {
            _events.send(NavigationEvent.EditProfile)
        }
    }
}
```

### View Observing State

```kotlin
@Composable
fun UserProfileScreen(viewModel: UserProfileViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is NavigationEvent.EditProfile -> navController.navigate("edit")
            }
        }
    }

    when {
        state.isLoading -> LoadingIndicator()
        state.error != null -> ErrorMessage(state.error)
        state.user != null -> UserContent(
            user = state.user,
            onEditClick = viewModel::onEditClicked
        )
    }
}
```

---

## Best Practices

**State Management**:
- Use immutable data classes for state
- Single source of truth in ViewModel
- Expose read-only state (StateFlow, not MutableStateFlow)
- Separate UI state from one-time events (use Channel/SharedFlow for events)

**Data Flow**:
- Unidirectional: View -> Event -> ViewModel -> State -> View
- No direct View-to-Model communication
- ViewModel never holds View references

**Testability**:
- ViewModel has no Android dependencies (easy unit testing)
- Mock repositories in ViewModel tests
- Test state transitions and event emissions
- Use TestDispatcher for coroutine testing

**Lifecycle**:
- ViewModel survives configuration changes (rotation)
- Collect flows with lifecycle awareness (collectAsStateWithLifecycle)
- Cancel coroutines in viewModelScope automatically

---

## Use Cases / Trade-offs

**When to Use**:
- Medium to large Android applications
- Complex UI state management
- Need for lifecycle-aware components
- Testability is a priority
- Multiple screens sharing data

**Advantages**:
- Clear separation of concerns
- Highly testable (ViewModel independent of Android framework)
- Survives configuration changes
- Easy state management with reactive streams
- Official Google recommendation

**Trade-offs**:
- More boilerplate than simple approaches
- Learning curve for reactive programming (Flow, LiveData)
- Potential over-engineering for simple screens
- Need dependency injection (Hilt/Dagger)

**Alternatives**:
- MVI (Model-View-Intent): More strict unidirectional flow, single state reducer
- MVP (Model-View-Presenter): More control, but tighter coupling
- Clean Architecture: Adds use cases layer between ViewModel and Repository

---

## References

- [Android Architecture Guide](https://developer.android.com/topic/architecture)
- [Guide to app architecture](https://developer.android.com/topic/architecture/recommendations)
- [ViewModel Overview](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

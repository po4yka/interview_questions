---
id: 20251012-140013
title: "StateFlow and SharedFlow in Android / StateFlow и SharedFlow в Android"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, android, stateflow, sharedflow, flow]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Android StateFlow SharedFlow Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-viewmodel-coroutines-lifecycle--kotlin--medium, q-lifecyclescope-viewmodelscope--kotlin--medium, q-flow-basics--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, android, stateflow, sharedflow, flow, difficulty/medium]
---
# Question (EN)
> How to use StateFlow and SharedFlow in Android? Explain the difference, replay cache, when to use each, and patterns for ViewModels.

# Вопрос (RU)
> Как использовать StateFlow и SharedFlow в Android? Объясните разницу, replay cache, когда использовать каждый и паттерны для ViewModels.

---

## Answer (EN)

StateFlow and SharedFlow are hot Flow types designed for sharing state and events between components in Android applications.

### StateFlow: State Management

```kotlin
class UserViewModel : ViewModel() {
    // StateFlow for UI state
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    data class UiState(
        val user: User? = null,
        val isLoading: Boolean = false,
        val error: String? = null
    )
    
    data class User(val id: String, val name: String)
    
    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val user = fetchUser(id)
                _uiState.value = UiState(user = user, isLoading = false)
            } catch (e: Exception) {
                _uiState.value = UiState(error = e.message, isLoading = false)
            }
        }
    }
    
    private suspend fun fetchUser(id: String): User {
        delay(1000)
        return User(id, "User $id")
    }
}
```

### SharedFlow: Events

```kotlin
class EventViewModel : ViewModel() {
    // SharedFlow for one-time events
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()
    
    sealed class Event {
        data class ShowToast(val message: String) : Event()
        object NavigateBack : Event()
    }
    
    fun saveData() {
        viewModelScope.launch {
            try {
                repository.save()
                _events.emit(Event.ShowToast("Saved!"))
            } catch (e: Exception) {
                _events.emit(Event.ShowToast("Error: ${e.message}"))
            }
        }
    }
    
    private val repository = Repository()
    class Repository {
        suspend fun save() {}
    }
}
```

### Key Differences

```kotlin
/**
 * StateFlow vs SharedFlow
 * 
 * StateFlow:
 * - Always has value
 * - Replay = 1 (always)
 * - Conflates (drops intermediate values)
 * - For STATE management
 * 
 * SharedFlow:
 * - May not have value
 * - Configurable replay
 * - Can buffer all values
 * - For EVENTS
 */

class ComparisonExample : ViewModel() {
    // StateFlow: Current screen state
    private val _screenState = MutableStateFlow(ScreenState.Loading)
    val screenState = _screenState.asStateFlow()
    
    // SharedFlow: One-time events
    private val _navigationEvents = MutableSharedFlow<Navigation>()
    val navigationEvents = _navigationEvents.asSharedFlow()
    
    sealed class ScreenState {
        object Loading : ScreenState()
        data class Content(val data: String) : ScreenState()
    }
    
    sealed class Navigation {
        object GoBack : Navigation()
        data class GoToDetails(val id: String) : Navigation()
    }
}
```

### When to Use Each

```kotlin
// StateFlow: Always use for state that UI needs to reflect
class GoodStateUsage : ViewModel() {
    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn = _isLoggedIn.asStateFlow()
    
    private val _userName = MutableStateFlow<String?>(null)
    val userName = _userName.asStateFlow()
}

// SharedFlow: Use for one-time events
class GoodEventUsage : ViewModel() {
    private val _snackbarMessages = MutableSharedFlow<String>()
    val snackbarMessages = _snackbarMessages.asSharedFlow()
    
    private val _navigationCommands = MutableSharedFlow<NavCommand>()
    val navigationCommands = _navigationCommands.asSharedFlow()
    
    sealed class NavCommand {
        object Back : NavCommand()
    }
}
```

---

## Ответ (RU)

StateFlow и SharedFlow - горячие Flow типы для Android.

**StateFlow**: Состояние UI
**SharedFlow**: Одноразовые события

### Основные различия

- StateFlow всегда имеет значение, SharedFlow может не иметь
- StateFlow replay=1, SharedFlow настраиваемый replay
- StateFlow для состояния, SharedFlow для событий

---

## Follow-ups

1. **How to collect StateFlow in Activity/Fragment?**
2. **What is replay cache in SharedFlow?**
3. **StateFlow vs LiveData comparison?**
4. **How to test StateFlow/SharedFlow?**

---

## References

- [StateFlow Documentation](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

---

## Related Questions

- [[q-viewmodel-coroutines-lifecycle--kotlin--medium]]
- [[q-lifecyclescope-viewmodelscope--kotlin--medium]]

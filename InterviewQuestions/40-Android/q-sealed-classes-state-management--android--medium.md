---
id: android-058
title: "Sealed Classes for State Management / Sealed классы для управления состоянием"
aliases: ["Sealed Classes for State Management", "Sealed классы для управления состоянием"]
topic: android
subtopics: [architecture-mvi, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-mvi-architecture--android--hard, q-state-hoisting-compose--android--medium, q-stateflow-flow-sharedflow-livedata--android--medium]
created: 2025-10-12
updated: 2025-01-27
tags: [android/architecture-mvi, android/ui-state, sealed-classes, state-management, mvi, difficulty/medium]
sources: [https://kotlinlang.org/docs/sealed-classes.html]
---
# Вопрос (RU)
> Как использовать sealed классы для управления состоянием в Android приложениях?

# Question (EN)
> How to use sealed classes for state management in Android applications?

---

## Ответ (RU)

**Концепция:**
Sealed классы ([[c-sealed-classes]]) представляют ограниченную иерархию типов, где все подклассы известны на этапе компиляции. В Android они используются для моделирования UI состояний, результатов API и событий в паттерне [[c-mvi-pattern]].

**Преимущества:**
- Исчерпывающие when выражения — компилятор проверяет все варианты
- Типобезопасность — невозможно передать некорректное состояние
- Могут содержать данные (в отличие от enum)

**Базовый пример состояния UI:**

```kotlin
sealed interface UiState<out T> {
    // ✅ data object для состояний без данных
    data object Idle : UiState<Nothing>
    data object Loading : UiState<Nothing>
    // ✅ data class для состояний с данными
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}

class ProfileViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState<User>>(UiState.Idle)
    val state: StateFlow<UiState<User>> = _state.asStateFlow()

    fun loadProfile() {
        viewModelScope.launch {
            _state.value = UiState.Loading
            _state.value = try {
                val user = repository.getUser()
                UiState.Success(user) // ✅ Явное состояние успеха
            } catch (e: Exception) {
                UiState.Error(e.message ?: "Unknown error") // ✅ Обработка ошибки
            }
        }
    }
}
```

**Обработка в UI:**

```kotlin
@Composable
fun ProfileScreen(viewModel: ProfileViewModel) {
    val state by viewModel.state.collectAsState()

    // ✅ Исчерпывающая обработка всех состояний
    when (state) {
        UiState.Idle -> Text("Press button to load")
        UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> UserProfile(state.data)
        is UiState.Error -> ErrorMessage(state.message)
    } // Компилятор проверит, что все варианты обработаны
}
```

**MVI Events:**

```kotlin
sealed interface ProfileEvent {
    data object LoadProfile : ProfileEvent
    data class UpdateName(val name: String) : ProfileEvent
    data object Logout : ProfileEvent
}

// ❌ Не используйте enum для событий с данными
enum class BadEvent { LOAD, UPDATE, LOGOUT } // Нет данных!
```

## Answer (EN)

**Concept:**
Sealed classes ([[c-sealed-classes]]) represent restricted type hierarchies where all subclasses are known at compile time. In Android, they're used to model UI states, API results, and events in the [[c-mvi-pattern]] pattern.

**Advantages:**
- Exhaustive when expressions — compiler checks all variants
- Type safety — impossible to pass incorrect state
- Can hold data (unlike enums)

**Basic UI State Example:**

```kotlin
sealed interface UiState<out T> {
    // ✅ data object for stateless cases
    data object Idle : UiState<Nothing>
    data object Loading : UiState<Nothing>
    // ✅ data class for states with data
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}

class ProfileViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState<User>>(UiState.Idle)
    val state: StateFlow<UiState<User>> = _state.asStateFlow()

    fun loadProfile() {
        viewModelScope.launch {
            _state.value = UiState.Loading
            _state.value = try {
                val user = repository.getUser()
                UiState.Success(user) // ✅ Explicit success state
            } catch (e: Exception) {
                UiState.Error(e.message ?: "Unknown error") // ✅ Error handling
            }
        }
    }
}
```

**UI Handling:**

```kotlin
@Composable
fun ProfileScreen(viewModel: ProfileViewModel) {
    val state by viewModel.state.collectAsState()

    // ✅ Exhaustive handling of all states
    when (state) {
        UiState.Idle -> Text("Press button to load")
        UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> UserProfile(state.data)
        is UiState.Error -> ErrorMessage(state.message)
    } // Compiler checks all variants are handled
}
```

**MVI Events:**

```kotlin
sealed interface ProfileEvent {
    data object LoadProfile : ProfileEvent
    data class UpdateName(val name: String) : ProfileEvent
    data object Logout : ProfileEvent
}

// ❌ Don't use enum for events with data
enum class BadEvent { LOAD, UPDATE, LOGOUT } // No data!
```

---

## Follow-ups

- When should you use `sealed class` vs `sealed interface`?
- How do sealed classes interact with SavedStateHandle for process death?
- What's the performance overhead of sealed classes vs regular inheritance?
- How do you handle backward compatibility when adding new states?

## References

- [[c-sealed-classes]] - Sealed classes concept
- [[c-mvi-pattern]] - MVI architecture pattern
- [[c-state-flow]] - StateFlow for state management
- https://kotlinlang.org/docs/sealed-classes.html

## Related Questions

### Prerequisites (Easier)
- Basic understanding of Kotlin data classes and when expressions
- Knowledge of ViewModel and StateFlow

### Related (Same Level)
- [[q-mvi-architecture--android--hard]] - MVI architecture implementation
- Questions about StateFlow vs LiveData for state management
- Questions about handling loading and error states in Compose

### Advanced (Harder)
- Complex state machines with nested sealed hierarchies
- State normalization strategies for large apps
- Event vs State distinction in MVI

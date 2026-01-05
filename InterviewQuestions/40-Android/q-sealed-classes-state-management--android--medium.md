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
related: [c-mvvm-pattern, q-mvi-architecture--android--hard, q-state-hoisting-compose--android--medium, q-stateflow-flow-sharedflow-livedata--android--medium]
created: 2025-10-12
updated: 2025-11-10
tags: [android/architecture-mvi, android/ui-state, difficulty/medium, mvi, sealed-classes, state-management]
sources: ["https://kotlinlang.org/docs/sealed-classes.html"]

---
# Вопрос (RU)
> Как использовать sealed классы для управления состоянием в Android приложениях?

# Question (EN)
> How to use sealed classes for state management in Android applications?

---

## Ответ (RU)

**Концепция:**
Sealed классы (sealed classes) представляют ограниченную иерархию типов, где все подклассы известны на этапе компиляции. В Android они используются для моделирования UI состояний, результатов API и событий в архитектурных паттернах на основе однонаправленного потока данных (например, MVI / MVVM).

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
Sealed classes represent restricted type hierarchies where all subclasses are known at compile time. In Android, they're used to model UI states, API results, and events in unidirectional data flow architectures (e.g., MVI / MVVM).

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

## Дополнительные Вопросы (RU)

- Когда следует использовать `sealed class` против `sealed interface`?
- Как sealed классы взаимодействуют с `SavedStateHandle` при убийстве процесса?
- Какова стоимость по производительности у sealed классов по сравнению с обычным наследованием?
- Как обрабатывать обратную совместимость при добавлении новых состояний?

## Follow-ups

- When should you use `sealed class` vs `sealed interface`?
- How do sealed classes interact with SavedStateHandle for process death?
- What's the performance overhead of sealed classes vs regular inheritance?
- How do you handle backward compatibility when adding new states?

## Ссылки (RU)

- Sealed классы иерархий состояний в Kotlin
- [[c-mvvm-pattern]] - Паттерн архитектуры MVVM
- "Sealed Classes" в официальной документации Kotlin

## References

- Sealed classes for state hierarchies in Kotlin
- [[c-mvvm-pattern]] - MVVM architecture pattern
- https://kotlinlang.org/docs/sealed-classes.html

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовое понимание data классов Kotlin и when выражений
- Знание `ViewModel` и `StateFlow`

### Связанные (средний уровень)
- [[q-mvi-architecture--android--hard]] - Реализация архитектуры MVI
- Вопросы о сравнении `StateFlow` и `LiveData` для управления состоянием
- Вопросы об обработке состояний загрузки и ошибок в Compose

### Продвинутые (сложнее)
- Сложные конечные автоматы с вложенными иерархиями sealed типов
- Стратегии нормализации состояний для крупных приложений
- Разграничение Event vs State в контексте MVI

## Related Questions

### Prerequisites (Easier)
- Basic understanding of Kotlin data classes and when expressions
- Knowledge of `ViewModel` and `StateFlow`

### Related (Same Level)
- [[q-mvi-architecture--android--hard]] - MVI architecture implementation
- Questions about `StateFlow` vs `LiveData` for state management
- Questions about handling loading and error states in Compose

### Advanced (Harder)
- Complex state machines with nested sealed hierarchies
- State normalization strategies for large apps
- Event vs State distinction in MVI

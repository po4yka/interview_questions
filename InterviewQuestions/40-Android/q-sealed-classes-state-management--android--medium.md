---
id: 20251012-400005
title: "Sealed Classes for State Management / Sealed классы для управления состоянием"
aliases:
  - "Sealed Classes for State Management"
  - "Sealed классы для управления состоянием"
topic: android
subtopics: [kotlin, state-management]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-sealed-classes, q-mvi-architecture--android--hard, q-kotlin-sealed-classes--kotlin--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [android/kotlin, android/state-management, sealed-classes, state-management, mvi, architecture, difficulty/medium]
sources: [https://kotlinlang.org/docs/sealed-classes.html]
---

# Вопрос (RU)
> Что такое sealed классы и как их использовать для управления состоянием?

# Question (EN)
> What are sealed classes and how to use them for state management?

---

## Ответ (RU)

**Теория Sealed классов:**
Sealed классы представляют ограниченную иерархию типов, где все подклассы известны на этапе компиляции. Они идеальны для моделирования состояний UI, результатов API и событий навигации.

**Основные преимущества:**
- Исчерпывающие when выражения
- Типобезопасность
- Могут содержать данные (в отличие от enum)
- Компилятор проверяет полноту обработки

```kotlin
// Базовый sealed класс для результата API
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// Исчерпывающая обработка без else
fun <T> handleResult(result: Result<T>) {
    when (result) {
        is Result.Success -> println("Данные: ${result.data}")
        is Result.Error -> println("Ошибка: ${result.exception.message}")
        is Result.Loading -> println("Загрузка...")
    }
}
```

**Управление состоянием UI:**
Sealed классы отлично подходят для моделирования состояний экранов.

```kotlin
// Состояние UI экрана
sealed interface UiState<out T> {
    data object Idle : UiState<Nothing>
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}

// Использование в ViewModel
class ProfileViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<UserProfile>>(UiState.Idle)
    val uiState: StateFlow<UiState<UserProfile>> = _uiState.asStateFlow()

    fun loadProfile() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val profile = userRepository.getProfile()
                _uiState.value = UiState.Success(profile)
            } catch (e: Exception) {
                _uiState.value = UiState.Error("Ошибка загрузки")
            }
        }
    }
}
```

**Sealed интерфейсы (Kotlin 1.5+):**
Позволяют множественное наследование и более гибкую архитектуру.

```kotlin
// Sealed интерфейс для множественного наследования
sealed interface Response
sealed interface ApiResponse : Response {
    data class Success(val data: String) : ApiResponse
    data class Failure(val error: String) : ApiResponse
}
```

**События навигации:**
Sealed классы идеальны для типобезопасной навигации.

```kotlin
sealed class NavigationEvent {
    data class NavigateToProfile(val userId: String) : NavigationEvent()
    data class NavigateToSettings : NavigationEvent()
    data object NavigateBack : NavigationEvent()
}
```

## Answer (EN)

**Sealed Classes Theory:**
Sealed classes represent restricted type hierarchies where all subclasses are known at compile time. They're perfect for modeling UI states, API results, and navigation events.

**Main advantages:**
- Exhaustive when expressions
- Type safety
- Can hold data (unlike enums)
- Compiler checks completeness

```kotlin
// Basic sealed class for API result
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// Exhaustive handling without else
fun <T> handleResult(result: Result<T>) {
    when (result) {
        is Result.Success -> println("Data: ${result.data}")
        is Result.Error -> println("Error: ${result.exception.message}")
        is Result.Loading -> println("Loading...")
    }
}
```

**UI State Management:**
Sealed classes are excellent for modeling screen states.

```kotlin
// UI state for screen
sealed interface UiState<out T> {
    data object Idle : UiState<Nothing>
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}

// Usage in ViewModel
class ProfileViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<UserProfile>>(UiState.Idle)
    val uiState: StateFlow<UiState<UserProfile>> = _uiState.asStateFlow()

    fun loadProfile() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val profile = userRepository.getProfile()
                _uiState.value = UiState.Success(profile)
            } catch (e: Exception) {
                _uiState.value = UiState.Error("Load error")
            }
        }
    }
}
```

**Sealed Interfaces (Kotlin 1.5+):**
Allow multiple inheritance and more flexible architecture.

```kotlin
// Sealed interface for multiple inheritance
sealed interface Response
sealed interface ApiResponse : Response {
    data class Success(val data: String) : ApiResponse
    data class Failure(val error: String) : ApiResponse
}
```

**Navigation Events:**
Sealed classes are ideal for type-safe navigation.

```kotlin
sealed class NavigationEvent {
    data class NavigateToProfile(val userId: String) : NavigationEvent()
    data class NavigateToSettings : NavigationEvent()
    data object NavigateBack : NavigationEvent()
}
```

---

## Follow-ups

- How do sealed classes compare to enums?
- What are the performance implications of sealed classes?
- How do you handle sealed classes in Compose?

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-basics--kotlin--easy]] - Kotlin basics
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-mvi-architecture--android--hard]] - MVI architecture
- [[q-kotlin-sealed-classes--kotlin--medium]] - Kotlin sealed classes
- [[q-state-management-patterns--android--medium]] - State management

### Advanced (Harder)
- [[q-kotlin-advanced-features--kotlin--hard]] - Advanced Kotlin
- [[q-android-architecture-patterns--android--hard]] - Architecture patterns

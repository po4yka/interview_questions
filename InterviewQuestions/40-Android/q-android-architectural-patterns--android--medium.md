---
id: 20251012-122761
title: Android Architectural Patterns / Архитектурные паттерны Android
aliases: [Android Architectural Patterns, Архитектурные паттерны Android]
topic: android
subtopics:
  - architecture-clean
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-mvvm
  - c-clean-architecture
  - c-dependency-injection
created: 2025-10-15
updated: 2025-01-27
tags: [android/architecture-clean, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Какие архитектурные паттерны используются в Android разработке, и чем они отличаются друг от друга?

## Ответ (RU)

Android использует несколько архитектурных паттернов: **MVP** (Model-View-Presenter), **MVVM** (Model-View-ViewModel), **MVI** (Model-View-Intent) и **Clean Architecture**. Современный стандарт — MVVM с Architecture Components.

### MVP (Model-View-Presenter)
- **Компоненты**: Model (данные), View (пассивный UI), Presenter (бизнес-логика)
- **Преимущества**: Четкое разделение, тестируемость
- **Недостатки**: Много boilerplate, нет lifecycle awareness

```kotlin
// ❌ Presenter держит ссылку на View - риск утечки памяти
class UserPresenter(private val view: UserContract.View) {
    fun loadUser(id: Int) {
        view.showLoading() // View может быть уничтожена
        repository.getUser(id) { user -> view.showUser(user) }
    }
}
```

### MVVM (Model-View-ViewModel)
- **Компоненты**: Model (данные), View (UI), ViewModel (логика с observable data)
- **Преимущества**: Lifecycle-aware, автообновление UI, официальная поддержка
- **Применение**: Стандарт для большинства приложений

```kotlin
// ✅ ViewModel переживает configuration changes, автоматически очищается
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch { // ✅ Автоматическая отмена при onCleared()
            _uiState.value = try {
                UiState.Success(repository.getUser(id))
            } catch (e: Exception) {
                UiState.Error(e.message ?: "Unknown")
            }
        }
    }
}
```

### MVI (Model-View-Intent)
- **Компоненты**: State (единственный источник истины), Intent (действия пользователя)
- **Преимущества**: Предсказуемое состояние, unidirectional flow, простая отладка
- **Применение**: Сложные UI с множеством состояний

```kotlin
// ✅ Immutable state, все изменения через Intent
sealed class UserIntent {
    data class LoadUser(val id: Int) : UserIntent()
}

data class UserState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    fun handleIntent(intent: UserIntent) { // ✅ Единая точка входа
        when (intent) {
            is UserIntent.LoadUser -> loadUser(intent.id)
        }
    }
}
```

### Clean Architecture
- **Слои**: Domain (use cases, entities), Data (repositories, sources), Presentation (UI, ViewModels)
- **Преимущества**: Независимость от фреймворка, высокая тестируемость
- **Применение**: Enterprise приложения

```kotlin
// ✅ UseCase инкапсулирует бизнес-логику, независим от Android
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: Int): Result<User> {
        return repository.getUser(id)
    }
}

// ✅ ViewModel зависит от интерфейса, легко тестировать
class UserViewModel(private val getUserUseCase: GetUserUseCase) : ViewModel() {
    fun loadUser(id: Int) = viewModelScope.launch {
        getUserUseCase(id).fold(
            onSuccess = { /* update state */ },
            onFailure = { /* handle error */ }
        )
    }
}
```

**Сравнение паттернов:**

| Паттерн | Тестируемость | Boilerplate | Lifecycle-Aware | Применение |
|---------|-------------|-------------|-----------------|----------|
| **MVP** | Высокая | Высокий | Нет | Legacy приложения |
| **MVVM** | Высокая | Средний | Да | Большинство приложений |
| **MVI** | Очень высокая | Средний | Да | Сложные UI |
| **Clean Architecture** | Очень высокая | Высокий | Да (с MVVM) | Enterprise приложения |

**Рекомендации:**
- Стандарт: MVVM + Repository Pattern + Hilt
- Сложные приложения: Clean Architecture + MVVM/MVI

# Question (EN)
> What are the main architectural patterns used in Android development, and how do they differ?

## Answer (EN)

Android uses several architectural patterns: **MVP** (Model-View-Presenter), **MVVM** (Model-View-ViewModel), **MVI** (Model-View-Intent), and **Clean Architecture**. The modern standard is MVVM with Architecture Components.

### MVP (Model-View-Presenter)
- **Components**: Model (data), View (passive UI), Presenter (business logic)
- **Advantages**: Clear separation, testability
- **Disadvantages**: Boilerplate code, no lifecycle awareness

```kotlin
// ❌ Presenter holds View reference - memory leak risk
class UserPresenter(private val view: UserContract.View) {
    fun loadUser(id: Int) {
        view.showLoading() // View may be destroyed
        repository.getUser(id) { user -> view.showUser(user) }
    }
}
```

### MVVM (Model-View-ViewModel)
- **Components**: Model (data), View (UI), ViewModel (logic with observable data)
- **Advantages**: Lifecycle-aware, automatic UI updates, official support
- **Use case**: Standard for most applications

```kotlin
// ✅ ViewModel survives configuration changes, automatically cleared
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch { // ✅ Auto-cancelled in onCleared()
            _uiState.value = try {
                UiState.Success(repository.getUser(id))
            } catch (e: Exception) {
                UiState.Error(e.message ?: "Unknown")
            }
        }
    }
}
```

### MVI (Model-View-Intent)
- **Components**: State (single source of truth), Intent (user actions)
- **Advantages**: Predictable state, unidirectional flow, easy debugging
- **Use case**: Complex UIs with multiple states

```kotlin
// ✅ Immutable state, all changes through Intent
sealed class UserIntent {
    data class LoadUser(val id: Int) : UserIntent()
}

data class UserState(
    val isLoading: Boolean = false,
    val user: User? = null,
    val error: String? = null
)

class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    fun handleIntent(intent: UserIntent) { // ✅ Single entry point
        when (intent) {
            is UserIntent.LoadUser -> loadUser(intent.id)
        }
    }
}
```

### Clean Architecture
- **Layers**: Domain (use cases, entities), Data (repositories, sources), Presentation (UI, ViewModels)
- **Advantages**: Framework independence, high testability
- **Use case**: Enterprise applications

```kotlin
// ✅ UseCase encapsulates business logic, framework-independent
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: Int): Result<User> {
        return repository.getUser(id)
    }
}

// ✅ ViewModel depends on interface, easy to test
class UserViewModel(private val getUserUseCase: GetUserUseCase) : ViewModel() {
    fun loadUser(id: Int) = viewModelScope.launch {
        getUserUseCase(id).fold(
            onSuccess = { /* update state */ },
            onFailure = { /* handle error */ }
        )
    }
}
```

**Pattern Comparison:**

| Pattern | Testability | Boilerplate | Lifecycle-Aware | Use Case |
|---------|-------------|-------------|-----------------|----------|
| **MVP** | High | High | No | Legacy apps |
| **MVVM** | High | Medium | Yes | Most applications |
| **MVI** | Very High | Medium | Yes | Complex UIs |
| **Clean Architecture** | Very High | High | Yes (with MVVM) | Enterprise apps |

**Recommendations:**
- Standard: MVVM + Repository Pattern + Hilt
- Complex apps: Clean Architecture + MVVM/MVI

## Follow-ups

- When would you choose MVI over MVVM for state management?
- How does Clean Architecture enforce dependency inversion in Android?
- What are the trade-offs between testability and boilerplate in each pattern?
- How do you handle shared state across multiple ViewModels in MVVM?
- What role does the Repository pattern play in Clean Architecture?

## References

- [[c-mvvm]] - MVVM architecture pattern
- [[c-clean-architecture]] - Clean Architecture principles
- [[c-dependency-injection]] - Dependency injection pattern
- Android Architecture Guide: https://developer.android.com/topic/architecture

## Related Questions

### Prerequisites
- ViewModel lifecycle and scope
- Dependency injection fundamentals
- Observer pattern and reactive streams

### Related
- MVVM implementation details
- Clean Architecture layer organization
- State management strategies

### Advanced
- MVI architecture implementation
- Multi-module Clean Architecture
- Testing strategies for each pattern
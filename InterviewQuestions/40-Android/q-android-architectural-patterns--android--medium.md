---
id: android-154
title: Android Architectural Patterns / Архитектурные паттерны Android
aliases: [Android Architectural Patterns, Архитектурные паттерны Android]
topic: android
subtopics:
  - architecture-clean
  - architecture-mvi
  - architecture-mvvm
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-mvvm
created: 2025-10-15
updated: 2025-10-29
tags: [android/architecture-clean, android/architecture-mvi, android/architecture-mvvm, difficulty/medium]
sources: []
---

# Вопрос (RU)
> Какие архитектурные паттерны используются в Android разработке, и чем они отличаются друг от друга?


# Question (EN)
> What are the main architectural patterns used in Android development, and how do they differ?


---

## Ответ (RU)

Android поддерживает несколько архитектурных паттернов: **MVP**, **MVVM**, **MVI** и **Clean Architecture**. Современный стандарт — MVVM с Architecture Components.

### MVP (Model-`View`-Presenter)
**Структура**: Model (данные) → Presenter (логика) → `View` (пассивный UI).

**Проблема**: Presenter держит ссылку на `View`, что создает риск утечек памяти и требует ручного управления lifecycle.

```kotlin
// ❌ Presenter держит ссылку на View
class UserPresenter(private val view: UserContract.View) {
    fun loadUser(id: Int) {
        view.showLoading() // View может быть уничтожена
        repository.getUser(id) { view.showUser(it) }
    }
}
```

### MVVM (Model-`View`-`ViewModel`)
**Структура**: `View` наблюдает за `ViewModel` через `LiveData`/`StateFlow`. `ViewModel` переживает configuration changes и автоматически очищается.

```kotlin
// ✅ ViewModel lifecycle-aware, автоматическая отмена корутин
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(Loading)
    val state = _state.asStateFlow()

    fun load(id: Int) = viewModelScope.launch {
        _state.value = try { Success(repo.getUser(id)) }
                       catch (e: Exception) { Error(e.message) }
    }
}
```

### MVI (Model-`View`-`Intent`)
**Структура**: Unidirectional data flow с immutable state. Все изменения происходят через `Intent`.

```kotlin
// ✅ Единая точка входа, предсказуемое состояние
sealed class UserIntent { data class Load(val id: Int) : UserIntent() }
data class UserState(val loading: Boolean, val user: User?, val error: String?)

class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserState(false, null, null))
    val state = _state.asStateFlow()

    fun handle(intent: UserIntent) = when (intent) {
        is UserIntent.Load -> loadUser(intent.id)
    }
}
```

### Clean Architecture
**Структура**: Domain (use cases) → Data (repositories) → Presentation (ViewModels).

```kotlin
// ✅ UseCase независим от фреймворка
class GetUserUseCase(private val repo: UserRepository) {
    suspend operator fun invoke(id: Int) = repo.getUser(id)
}
```

**Выбор паттерна:**
- **MVVM**: стандарт для большинства приложений
- **MVI**: сложные UI с множеством состояний
- **Clean Architecture**: многомодульные enterprise-приложения


## Answer (EN)

Android supports several architectural patterns: **MVP**, **MVVM**, **MVI**, and **Clean Architecture**. The modern standard is MVVM with Architecture Components.

### MVP (Model-`View`-Presenter)
**Structure**: Model (data) → Presenter (logic) → `View` (passive UI).

**Problem**: Presenter holds a reference to `View`, creating memory leak risks and requiring manual lifecycle management.

```kotlin
// ❌ Presenter holds View reference
class UserPresenter(private val view: UserContract.View) {
    fun loadUser(id: Int) {
        view.showLoading() // View may be destroyed
        repository.getUser(id) { view.showUser(it) }
    }
}
```

### MVVM (Model-`View`-`ViewModel`)
**Structure**: `View` observes `ViewModel` via `LiveData`/`StateFlow`. `ViewModel` survives configuration changes and is automatically cleared.

```kotlin
// ✅ ViewModel is lifecycle-aware, auto-cancels coroutines
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(Loading)
    val state = _state.asStateFlow()

    fun load(id: Int) = viewModelScope.launch {
        _state.value = try { Success(repo.getUser(id)) }
                       catch (e: Exception) { Error(e.message) }
    }
}
```

### MVI (Model-`View`-`Intent`)
**Structure**: Unidirectional data flow with immutable state. All changes happen through Intents.

```kotlin
// ✅ Single entry point, predictable state
sealed class UserIntent { data class Load(val id: Int) : UserIntent() }
data class UserState(val loading: Boolean, val user: User?, val error: String?)

class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserState(false, null, null))
    val state = _state.asStateFlow()

    fun handle(intent: UserIntent) = when (intent) {
        is UserIntent.Load -> loadUser(intent.id)
    }
}
```

### Clean Architecture
**Structure**: Domain (use cases) → Data (repositories) → Presentation (ViewModels).

```kotlin
// ✅ UseCase is framework-independent
class GetUserUseCase(private val repo: UserRepository) {
    suspend operator fun invoke(id: Int) = repo.getUser(id)
}
```

**Pattern selection:**
- **MVVM**: standard for most applications
- **MVI**: complex UIs with multiple states
- **Clean Architecture**: multi-module enterprise applications

## Follow-ups

- When would you choose MVI over MVVM for state management?
- How does Clean Architecture enforce dependency inversion in Android?
- How do you handle shared state across multiple ViewModels in MVVM?
- What are the testing implications of each architectural pattern?
- How does `Repository` pattern integrate with Clean Architecture layers?

## References

- [[c-mvvm]]
- [[c-clean-architecture]]
- [[c-dependency-injection]]
- [Architecture](https://developer.android.com/topic/architecture)


## Related Questions

### Related
- [[q-repository-pattern--android--medium]]

### Advanced
- [[q-kmm-architecture--android--hard]]
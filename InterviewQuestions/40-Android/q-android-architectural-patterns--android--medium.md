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
status: draft
moc: moc-android
related:
  - c-clean-architecture
  - c-mvvm
  - q-android-lint-tool--android--medium
  - q-factory-pattern-android--android--medium
  - q-modularization-patterns--android--hard
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-clean, android/architecture-mvi, android/architecture-mvvm, difficulty/medium]
sources: []

date created: Saturday, November 1st 2025, 1:24:37 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> Какие архитектурные паттерны используются в Android разработке, и чем они отличаются друг от друга?

# Question (EN)
> What are the main architectural patterns used in Android development, and how do they differ?

---

## Ответ (RU)

Android широко использует несколько архитектурных паттернов: **MVP**, **MVVM**, **MVI** и **Clean Architecture**. На сегодняшний день рекомендованный подход Google — **слоистая архитектура на базе MVVM** с использованием Jetpack (Architecture Components), при этом Clean Architecture и MVI часто комбинируются поверх/внутри MVVM.

### MVP (Model-`View`-Presenter)
**Структура**: Model (данные) → Presenter (логика) → `View` (пассивный UI).

**Особенность/проблема**: Presenter обычно держит ссылку на `View` и сам управляет подписками и lifecycle. При неправильной отвязке `View` это легко приводит к утечкам памяти и сложности с состоянием при поворотах экрана.

```kotlin
// ❌ Упрощённый пример: Presenter держит ссылку на View и не учитывает lifecycle
class UserPresenter(
    private val view: UserContract.View,
    private val repository: UserRepository
) {
    fun loadUser(id: Int) {
        view.showLoading() // View может быть уничтожена, если не отвязать во время onDestroy()
        repository.getUser(id) { user ->
            view.showUser(user) // потенциальный вызов на уничтоженной View
        }
    }
}
```

### MVVM (Model-`View`-`ViewModel`)
**Структура**: `View` наблюдает за `ViewModel` через `LiveData`/`StateFlow`/`Flow`. `ViewModel` переживает configuration changes и автоматически очищается `ViewModelStore` при уничтожении owner-а.

```kotlin
// ✅ ViewModel lifecycle-aware, автоматическая отмена корутин через viewModelScope
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(Loading)
    val state = _state.asStateFlow()

    fun load(id: Int) = viewModelScope.launch {
        _state.value = try {
            Success(repo.getUser(id))
        } catch (e: Exception) {
            Error(e.message)
        }
    }
}
```

### MVI (Model-`View`-`Intent`)
**Структура**: Однонаправленный поток данных с immutable state. `View` генерирует Intents (события), которые обрабатываются и сводятся (reduce) в новое состояние.

```kotlin
// ✅ Упрощённый пример: единая точка входа, предсказуемое состояние
sealed class UserIntent {
    data class Load(val id: Int) : UserIntent()
}

data class UserState(
    val loading: Boolean,
    val user: User?,
    val error: String?
)

class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _state = MutableStateFlow(UserState(false, null, null))
    val state = _state.asStateFlow()

    fun handle(intent: UserIntent) {
        when (intent) {
            is UserIntent.Load -> loadUser(intent.id)
        }
    }

    private fun loadUser(id: Int) = viewModelScope.launch {
        _state.value = _state.value.copy(loading = true, error = null)
        _state.value = try {
            val user = repo.getUser(id)
            _state.value.copy(loading = false, user = user, error = null)
        } catch (e: Exception) {
            _state.value = _state.value.copy(loading = false, error = e.message)
        }
    }
}
```

### Clean Architecture
**Структура (упрощённо)**: Domain (use cases, бизнес-логика) ← интерфейсы → Data (репозитории, источники данных) → Presentation (`ViewModel`/Presenter/`View`). Зависимости направлены вовнутрь: внешние слои зависят от домена, а не наоборот.

```kotlin
// ✅ UseCase независим от фреймворка и UI
class GetUserUseCase(private val repo: UserRepository) {
    suspend operator fun invoke(id: Int): User = repo.getUser(id)
}
```

**Выбор паттерна (ориентиры, не жёсткие правила):**
- **MVVM**: дефолт для большинства современных Android-приложений (особенно с Jetpack/Compose).
- **MVI**: когда важны строго однонаправленный поток данных, предсказуемость и трассировка состояния (сложные UI, много событий).
- **Clean Architecture**: когда нужна чёткая изоляция домена, тестируемость и масштабируемость (более крупные/многомодульные проекты), но может применяться и в небольших.

## Answer (EN)

Android commonly uses several architectural patterns: **MVP**, **MVVM**, **MVI**, and **Clean Architecture**. Today, Google's recommended approach is a layered architecture based on **MVVM with Jetpack (Architecture Components)**, often combined with Clean Architecture principles and, in some cases, MVI-style state handling.

### MVP (Model-`View`-Presenter)
**Structure**: Model (data) → Presenter (logic) → `View` (passive UI).

**Characteristic/problem**: The Presenter typically holds a reference to the `View` and manually manages subscriptions and lifecycle. If the `View` is not detached properly, this easily leads to memory leaks and state issues on configuration changes.

```kotlin
// ❌ Simplified example: Presenter holds View reference and ignores lifecycle
class UserPresenter(
    private val view: UserContract.View,
    private val repository: UserRepository
) {
    fun loadUser(id: Int) {
        view.showLoading() // View may be destroyed if not detached in onDestroy()
        repository.getUser(id) { user ->
            view.showUser(user) // potential call on a destroyed View
        }
    }
}
```

### MVVM (Model-`View`-`ViewModel`)
**Structure**: The `View` observes the `ViewModel` via `LiveData`/`StateFlow`/`Flow`. The `ViewModel` survives configuration changes and is cleared by the `ViewModelStore` when its owner is destroyed.

```kotlin
// ✅ ViewModel is lifecycle-aware, coroutines auto-cancel via viewModelScope
class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(Loading)
    val state = _state.asStateFlow()

    fun load(id: Int) = viewModelScope.launch {
        _state.value = try {
            Success(repo.getUser(id))
        } catch (e: Exception) {
            Error(e.message)
        }
    }
}
```

### MVI (Model-`View`-`Intent`)
**Structure**: Unidirectional data flow with immutable state. The `View` emits Intents (events), which are processed and reduced into a new State.

```kotlin
// ✅ Simplified example: single entry point, predictable state
sealed class UserIntent {
    data class Load(val id: Int) : UserIntent()
}

data class UserState(
    val loading: Boolean,
    val user: User?,
    val error: String?
)

class UserViewModel(private val repo: UserRepository) : ViewModel() {
    private val _state = MutableStateFlow(UserState(false, null, null))
    val state = _state.asStateFlow()

    fun handle(intent: UserIntent) {
        when (intent) {
            is UserIntent.Load -> loadUser(intent.id)
        }
    }

    private fun loadUser(id: Int) = viewModelScope.launch {
        _state.value = _state.value.copy(loading = true, error = null)
        _state.value = try {
            val user = repo.getUser(id)
            _state.value.copy(loading = false, user = user, error = null)
        } catch (e: Exception) {
            _state.value = _state.value.copy(loading = false, error = e.message)
        }
    }
}
```

### Clean Architecture
**Structure (simplified)**: Domain (use cases, business rules) ← interfaces → Data (repositories, data sources) → Presentation (`ViewModel`/Presenter/`View`). Dependencies point inward: outer layers depend on the domain, not vice versa.

```kotlin
// ✅ UseCase is framework- and UI-independent
class GetUserUseCase(private val repo: UserRepository) {
    suspend operator fun invoke(id: Int): User = repo.getUser(id)
}
```

**Pattern selection (guidelines, not strict rules):**
- **MVVM**: default choice for most modern Android apps (especially with Jetpack/Compose).
- **MVI**: when strict unidirectional data flow, predictability, and state traceability are important (complex UIs, many events).
- **Clean Architecture**: when you need strong domain isolation, testability, and scalability (larger/multi-module projects), but it can also be applied in smaller apps.

## Дополнительные Вопросы (RU)

- В каких случаях вы выберете MVI вместо MVVM для управления состоянием?
- Как Clean Architecture реализует инверсию зависимостей в Android?
- Как обрабатывать общее состояние между несколькими ViewModel в MVVM?
- Каковы особенности тестирования для каждого архитектурного паттерна?
- Как паттерн Repository интегрируется со слоями Clean Architecture?

## Follow-ups

- When would you choose MVI over MVVM for state management?
- How does Clean Architecture enforce dependency inversion in Android?
- How do you handle shared state across multiple ViewModels in MVVM?
- What are the testing implications of each architectural pattern?
- How does Repository pattern integrate with Clean Architecture layers?

## Ссылки (RU)

- [[c-mvvm]]
- [[c-clean-architecture]]
- [[c-dependency-injection]]
- [Architecture](https://developer.android.com/topic/architecture)

## References

- [[c-mvvm]]
- [[c-clean-architecture]]
- [[c-dependency-injection]]
- [Architecture](https://developer.android.com/topic/architecture)

## Похожие Вопросы (RU)

### Связанные
- [[q-repository-pattern--android--medium]]

### Продвинутые
- [[q-kmm-architecture--android--hard]]

## Related Questions

### Related
- [[q-repository-pattern--android--medium]]

### Advanced
- [[q-kmm-architecture--android--hard]]

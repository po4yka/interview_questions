---
id: android-296
title: MVVM vs MVP Differences / Различия MVVM и MVP
aliases: [MVVM vs MVP, Различия MVVM и MVP]
topic: android
subtopics: [architecture-mvvm, lifecycle]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-clean-architecture, c-lifecycle, q-clean-architecture-android--android--hard, q-mvp-pattern--android--medium, q-mvvm-pattern--android--medium, q-viewgroup-vs-view-differences--android--easy]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-mvvm, android/lifecycle, architecture-patterns, difficulty/medium]

---
# Вопрос (RU)

> Чем MVVM отличается от MVP?

# Question (EN)

> What is the difference between MVVM and MVP?

## Ответ (RU)

**MVVM (Model-`View`-`ViewModel`)** и **MVP (Model-`View`-Presenter)** — архитектурные паттерны для разделения ответственности, различающиеся механизмом связи `View` с бизнес-логикой.

**Ключевые различия:**

**1. Связь `View` и логики**

**MVP** — явная двусторонняя связь через интерфейс:
- Presenter содержит ссылку на `View` (интерфейс)
- `View` явно вызывает методы Presenter
- Presenter явно вызывает методы `View` для обновления UI

```kotlin
// MVP (упрощенный пример)
interface UserListView {
    fun showUsers(users: List<User>)
    fun showError(message: String)
}

class UserListPresenter(
    private val view: UserListView,
    private val repository: UserRepository
) {
    fun loadUsers() {
        repository.getUsers { result ->
            // ✅ Явное управление View через интерфейс
            when (result) {
                is Success -> view.showUsers(result.data)
                is Error -> view.showError(result.message)
            }
        }
    }
}
```

**MVVM** — слабая связь через наблюдаемые данные:
- `ViewModel` не знает о `View` (отсутствие ссылки)
- `View` подписывается на данные `ViewModel` (`LiveData`, `StateFlow` и т.п.)
- UI обновляется реактивно при изменении данных

```kotlin
// MVVM (упрощенный пример)
class UserListViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            // ✅ ViewModel не знает о View
            _users.value = repository.getUsers()
        }
    }
}

// View подписывается на изменения с учетом жизненного цикла (пример для Activity/Fragment)
lifecycleScope.launch {
    viewModel.users.collect { users ->
        adapter.submitList(users) // Реактивное обновление UI
    }
}
```

**2. Управление жизненным циклом**

| Аспект | MVP | MVVM |
|--------|-----|------|
| **Конфигурационные изменения** | По умолчанию Presenter пересоздаётся вместе с `View`; сохранение состояния требует ручной реализации (retain, кеш, SavedState и т.п.) | `ViewModel` по умолчанию переживает конфигурационные изменения через `ViewModelStore` |
| **Утечки памяти** | Есть риск при хранении сильной ссылки на `View` и неправильной очистке | Риск ниже, так как `ViewModel` не должен держать ссылку на `View`; утечки всё ещё возможны при нарушении этого правила |
| **Lifecycle-aware** | Требует ручной обработки жизненного цикла для отписок/освобождения ресурсов | Стандартные компоненты (`ViewModel`, `LiveData`, `Flow` с repeatOnLifecycle и т.п.) интегрируются с жизненным циклом фреймворка |

**3. Тестируемость**

```kotlin
// MVP — обычно требуется mock View (упрощенный пример)
@Test
fun `load users shows data`() {
    val mockView = mock<UserListView>()
    val fakeRepository = FakeUserRepository()
    val presenter = UserListPresenter(mockView, fakeRepository)

    presenter.loadUsers()

    verify(mockView).showUsers(any())
}

// MVVM — тестируем ViewModel без настоящей View (упрощенный пример)
@Test
fun `load users emits data`() = runTest {
    val fakeRepository = FakeUserRepository()
    val viewModel = UserListViewModel(fakeRepository)

    viewModel.loadUsers()

    assertEquals(expectedUsers, viewModel.users.value)
}
```

**Выбор паттерна:**
- **MVP**: Легаси-проекты, отсутствие Jetpack-компонентов, необходимость точного контроля вызовов `View` (но требует большего ручного управления жизненным циклом)
- **MVVM**: Современные Android-приложения с Jetpack, реактивное программирование, упрощённое управление жизненным циклом и тестирование

## Answer (EN)

**MVVM (Model-`View`-`ViewModel`)** and **MVP (Model-`View`-Presenter)** are architectural patterns for separating concerns, differing mainly in how the `View` is connected to business logic.

**Key Differences:**

**1. `View`-Logic Binding**

**MVP** — explicit bidirectional binding via interface:
- Presenter holds a reference to the `View` (interface)
- `View` explicitly calls Presenter methods
- Presenter explicitly calls `View` methods to update UI

```kotlin
// MVP (simplified example)
interface UserListView {
    fun showUsers(users: List<User>)
    fun showError(message: String)
}

class UserListPresenter(
    private val view: UserListView,
    private val repository: UserRepository
) {
    fun loadUsers() {
        repository.getUsers { result ->
            // ✅ Explicit View control via interface
            when (result) {
                is Success -> view.showUsers(result.data)
                is Error -> view.showError(result.message)
            }
        }
    }
}
```

**MVVM** — loose coupling via observable data:
- `ViewModel` does not know about the `View` (no reference)
- `View` subscribes to `ViewModel` data (`LiveData`, `StateFlow`, etc.)
- UI updates reactively when data changes

```kotlin
// MVVM (simplified example)
class UserListViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            // ✅ ViewModel doesn't know about View
            _users.value = repository.getUsers()
        }
    }
}

// View subscribes to changes with lifecycle awareness (e.g., in Activity/Fragment)
lifecycleScope.launch {
    viewModel.users.collect { users ->
        adapter.submitList(users) // Reactive UI updates
    }
}
```

**2. Lifecycle Management**

| Aspect | MVP | MVVM |
|--------|-----|------|
| **Configuration changes** | By default, Presenter is recreated with the `View`; retaining state requires manual handling (retained instances, cache, SavedState, etc.) | `ViewModel` survives configuration changes by default via `ViewModelStore` |
| **Memory leaks** | Risk if holding a strong `View` reference and not clearing it properly | Lower risk because `ViewModel` should not hold `View` references; leaks still possible if this rule is broken |
| **Lifecycle-aware** | Requires manual lifecycle handling for subscriptions/resources | Standard components (`ViewModel`, `LiveData`, `Flow` with repeatOnLifecycle, etc.) integrate with the framework lifecycle |

**3. Testability**

```kotlin
// MVP — usually needs a mocked View (simplified example)
@Test
fun `load users shows data`() {
    val mockView = mock<UserListView>()
    val fakeRepository = FakeUserRepository()
    val presenter = UserListPresenter(mockView, fakeRepository)

    presenter.loadUsers()

    verify(mockView).showUsers(any())
}

// MVVM — test ViewModel without a real View (simplified example)
@Test
fun `load users emits data`() = runTest {
    val fakeRepository = FakeUserRepository()
    val viewModel = UserListViewModel(fakeRepository)

    viewModel.loadUsers()

    assertEquals(expectedUsers, viewModel.users.value)
}
```

**Pattern Selection:**
- **MVP**: Legacy projects, environments without Jetpack components, cases requiring very explicit control over `View` calls (but with more manual lifecycle management)
- **MVVM**: Modern Android apps with Jetpack, reactive style, simpler lifecycle handling and testing

## Follow-ups

- How does MVI compare to MVVM and MVP?
- When would you use MVP over MVVM in new projects?
- How to handle one-time events (navigation, toasts) in MVVM?
- What are the memory implications of holding `View` references in Presenters?

## References

- [[c-clean-architecture]]
- [[c-lifecycle]]

## Related Questions

### Prerequisites / Concepts

- [[c-lifecycle]]
- [[c-clean-architecture]]

### Prerequisites
- [[q-what-is-viewmodel--android--medium]] - Understanding `ViewModel` basics

### Related
- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Advanced
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern

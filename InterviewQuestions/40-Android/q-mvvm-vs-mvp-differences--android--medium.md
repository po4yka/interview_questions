---
id: 20251016-161930
title: "MVVM vs MVP Differences / Различия MVVM и MVP"
aliases: ["MVVM vs MVP", "Различия MVVM и MVP"]
topic: android
subtopics: [architecture-mvvm, architecture-clean, lifecycle]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-what-is-viewmodel--android--medium, q-mvvm-pattern--android--medium, q-clean-architecture-android--android--hard]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/architecture-mvvm, android/architecture-clean, android/lifecycle, architecture-patterns, viewmodel, presenter, data-binding, difficulty/medium]
---
# Вопрос (RU)

Чем MVVM отличается от MVP?

# Question (EN)

What is the difference between MVVM and MVP?

## Ответ (RU)

**MVVM (Model-View-ViewModel)** и **MVP (Model-View-Presenter)** — архитектурные паттерны для разделения ответственности, различающиеся механизмом связи View с бизнес-логикой.

**Ключевые различия:**

**1. Связь View и логики**

**MVP** — явная двусторонняя связь через интерфейс:
- Presenter содержит ссылку на View (интерфейс)
- View явно вызывает методы Presenter
- Presenter явно вызывает методы View для обновления UI

```kotlin
// MVP
interface UserListView {
    fun showUsers(users: List<User>)
    fun showError(message: String)
}

class UserListPresenter(private val view: UserListView) {
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
- ViewModel не знает о View (отсутствие ссылки)
- View подписывается на данные ViewModel (LiveData, StateFlow)
- UI обновляется автоматически при изменении данных

```kotlin
// MVVM
class UserListViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            // ✅ ViewModel не знает о View
            _users.value = repository.getUsers()
        }
    }
}

// View подписывается на изменения
lifecycleScope.launch {
    viewModel.users.collect { users ->
        adapter.submitList(users) // Автообновление
    }
}
```

**2. Управление жизненным циклом**

| Аспект | MVP | MVVM |
|--------|-----|------|
| **Конфигурационные изменения** | Presenter пересоздается, данные теряются | ViewModel сохраняется через `ViewModelStore` |
| **Утечки памяти** | Риск при хранении ссылки на View | Отсутствует (нет ссылки на View) |
| **Lifecycle-aware** | Требует ручной обработки | Встроенная поддержка через `LifecycleObserver` |

**3. Тестируемость**

```kotlin
// MVP — требуется mock View
@Test
fun `load users shows data`() {
    val mockView = mock<UserListView>()
    val presenter = UserListPresenter(mockView)

    presenter.loadUsers()

    verify(mockView).showUsers(any())
}

// MVVM — View не нужен
@Test
fun `load users emits data`() = runTest {
    val viewModel = UserListViewModel()

    viewModel.loadUsers()

    assertEquals(expectedUsers, viewModel.users.value)
}
```

**Выбор паттерна:**
- **MVP**: Легаси-проекты, точный контроль обновлений UI, отсутствие Jetpack
- **MVVM**: Современные Android-приложения с Jetpack, реактивное программирование, упрощенное тестирование

## Answer (EN)

**MVVM (Model-View-ViewModel)** and **MVP (Model-View-Presenter)** are architectural patterns for separating concerns, differing in how the View communicates with business logic.

**Key Differences:**

**1. View-Logic Binding**

**MVP** — explicit bidirectional binding via interface:
- Presenter holds reference to View (interface)
- View explicitly calls Presenter methods
- Presenter explicitly calls View methods to update UI

```kotlin
// MVP
interface UserListView {
    fun showUsers(users: List<User>)
    fun showError(message: String)
}

class UserListPresenter(private val view: UserListView) {
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
- ViewModel doesn't know about View (no reference)
- View subscribes to ViewModel data (LiveData, StateFlow)
- UI updates automatically on data changes

```kotlin
// MVVM
class UserListViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            // ✅ ViewModel doesn't know about View
            _users.value = repository.getUsers()
        }
    }
}

// View subscribes to changes
lifecycleScope.launch {
    viewModel.users.collect { users ->
        adapter.submitList(users) // Auto-update
    }
}
```

**2. Lifecycle Management**

| Aspect | MVP | MVVM |
|--------|-----|------|
| **Configuration changes** | Presenter recreated, data lost | ViewModel survives via `ViewModelStore` |
| **Memory leaks** | Risk when holding View reference | None (no View reference) |
| **Lifecycle-aware** | Manual handling required | Built-in support via `LifecycleObserver` |

**3. Testability**

```kotlin
// MVP — requires mock View
@Test
fun `load users shows data`() {
    val mockView = mock<UserListView>()
    val presenter = UserListPresenter(mockView)

    presenter.loadUsers()

    verify(mockView).showUsers(any())
}

// MVVM — no View needed
@Test
fun `load users emits data`() = runTest {
    val viewModel = UserListViewModel()

    viewModel.loadUsers()

    assertEquals(expectedUsers, viewModel.users.value)
}
```

**Pattern Selection:**
- **MVP**: Legacy projects, precise UI update control, no Jetpack
- **MVVM**: Modern Android with Jetpack, reactive programming, simplified testing

## Follow-ups

- How does MVI compare to MVVM and MVP?
- When would you use MVP over MVVM in new projects?
- How to handle one-time events (navigation, toasts) in MVVM?
- What are the memory implications of holding View references in Presenters?

## References

- Official Android Architecture Guide: Modern app architecture
- Jetpack ViewModel documentation: Lifecycle-aware data holders
- Android Lifecycle documentation: Component lifecycle management

## Related Questions

### Prerequisites
- [[q-what-is-viewmodel--android--medium]] - Understanding ViewModel basics

### Related
- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel internals
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - State preservation comparison

### Advanced
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles
- [[q-mvi-handle-one-time-events--android--hard]] - One-time event handling


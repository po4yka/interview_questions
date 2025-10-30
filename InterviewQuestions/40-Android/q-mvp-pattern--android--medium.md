---
id: 20251017-144928
title: "MVP Pattern / MVP Паттерн"
aliases: ["MVP Pattern", "MVP Паттерн", "Model-View-Presenter"]
topic: android
subtopics: [architecture-mvvm, architecture-patterns, testing]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-architectural-patterns--android--medium, c-mvvm-pattern, c-architecture-patterns]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/architecture-mvvm, android/architecture-patterns, android/testing, architecture-patterns, mvp, model-view-presenter, difficulty/medium]
---

# Вопрос (RU)

Что такое архитектурный паттерн MVP (Model-View-Presenter)? Объясните его компоненты и отличия от других паттернов.

# Question (EN)

What is the MVP (Model-View-Presenter) architectural pattern? Explain its components and how it differs from other patterns.

---

## Ответ (RU)

**MVP (Model-View-Presenter)** — архитектурный паттерн для разделения ответственности и улучшения тестируемости презентационной логики.

### Компоненты MVP

**1. Model** — слой данных, содержит бизнес-логику, взаимодействует с сетью и базой данных, независим от UI.

**2. View** — UI слой, отображает данные и уведомляет Presenter о действиях пользователя. Пассивен — не содержит логику, только показывает то, что говорит Presenter. Реализуется Activity/Fragment.

**3. Presenter** — получает данные из Model, применяет UI логику, управляет состоянием View, реагирует на действия пользователя, выступает посредником между Model и View.

### Contract Interface

View и Presenter тесно связаны и имеют ссылки друг на друга. Для юнит-тестирования Presenter используется интерфейс View. Связь между Presenter и View определяется в **Contract** интерфейсе, делая код более читаемым.

```kotlin
// Contract определяет связь View-Presenter
interface UserContract {
    interface View {
        fun showLoading()
        fun hideLoading()
        fun showUser(user: User)
        fun showError(message: String)
    }

    interface Presenter {
        fun attachView(view: View)
        fun detachView()
        fun loadUser(userId: Int)
    }
}

// Presenter реализация
class UserPresenter(
    private val repository: UserRepository
) : UserContract.Presenter {
    private var view: UserContract.View? = null

    override fun attachView(view: UserContract.View) {
        this.view = view
    }

    override fun detachView() {
        this.view = null // ✅ Предотвращает утечки памяти
    }

    override fun loadUser(userId: Int) {
        view?.showLoading()
        repository.getUser(userId) { result ->
            view?.hideLoading()
            result.onSuccess { user -> view?.showUser(user) }
            result.onFailure { error ->
                view?.showError(error.message ?: "Unknown error")
            }
        }
    }
}

// View реализация
class UserActivity : AppCompatActivity(), UserContract.View {
    private lateinit var presenter: UserContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter = UserPresenter(UserRepository())
        presenter.attachView(this) // ✅ Привязка View
    }

    override fun onDestroy() {
        super.onDestroy()
        presenter.detachView() // ✅ Отвязка View
    }

    override fun showUser(user: User) {
        nameTextView.text = user.name
    }
}
```

### Преимущества MVP

1. **Тестируемость** — Presenter тестируется независимо с JUnit (mock View)
2. **Разделение ответственности** — четкие роли для каждого компонента
3. **Переиспользование** — Presenter можно использовать с разными View
4. **Нет Android зависимостей** — Presenter легко тестировать

### Недостатки MVP

1. **God Presenter** — Presenter может превратиться в огромный класс, если не следовать принципу единственной ответственности
2. **Утечки памяти** — если Presenter держит ссылку на View после её уничтожения (необходим detachView)
3. **Boilerplate код** — требуется больше кода по сравнению с простыми подходами
4. **Потеря состояния** — при изменениях конфигурации Presenter пересоздаётся (если не сохранён)

### MVP vs MVVM vs MVC

| Аспект | MVP | MVVM | MVC |
|--------|-----|------|-----|
| **View-Presenter/ViewModel** | Двунаправленная связь | Однонаправленная (observable) | Прямая связь |
| **Ссылка на View** | Presenter знает View | ViewModel не знает View | Controller знает View |
| **Обновление View** | Явные вызовы интерфейса | Автоматическое (data binding) | Прямые вызовы |
| **Тестируемость** | Хорошая (mock View) | Отличная (без View) | Средняя |
| **Lifecycle** | Ручное управление | Автоматическое | Ручное |
| **Изменения конфигурации** | Состояние теряется | Состояние сохраняется | Состояние теряется |

### Best Practices

```kotlin
// ✅ DO: Используйте Contract интерфейс
interface ScreenContract {
    interface View { }
    interface Presenter { }
}

// ✅ DO: Отвязывайте View в onDestroy
override fun onDestroy() {
    super.onDestroy()
    presenter.detachView()
}

// ✅ DO: Проверяйте null перед вызовом View
view?.showData(data)

// ❌ DON'T: Создавайте God Presenter с избыточными обязанностями
// ❌ DON'T: Забывайте отвязывать View (вызывает утечки памяти)
```

---

## Answer (EN)

**MVP (Model-View-Presenter)** is an architectural pattern designed to facilitate automated unit testing and improve separation of concerns in presentation logic.

### MVP Components

**1. Model** — the data layer, handles business logic and communication with network and database layers, provides data to Presenter, independent of UI.

**2. View** — the UI layer, displays data and notifies Presenter about user actions. Passive — contains no logic, only displays what Presenter tells it. Implemented by Activity/Fragment.

**3. Presenter** — retrieves data from Model, applies UI logic, manages View state, reacts to user input notifications from View, acts as a middleman between Model and View.

### Contract Interface

Since View and Presenter work closely together, they need references to one another. To make Presenter unit testable with JUnit, View is abstracted as an interface. The relationship between Presenter and its View is defined in a **Contract** interface class, making the code more readable and the connection easier to understand.

```kotlin
// Contract defines View-Presenter relationship
interface UserContract {
    interface View {
        fun showLoading()
        fun hideLoading()
        fun showUser(user: User)
        fun showError(message: String)
    }

    interface Presenter {
        fun attachView(view: View)
        fun detachView()
        fun loadUser(userId: Int)
    }
}

// Presenter implementation
class UserPresenter(
    private val repository: UserRepository
) : UserContract.Presenter {
    private var view: UserContract.View? = null

    override fun attachView(view: UserContract.View) {
        this.view = view
    }

    override fun detachView() {
        this.view = null // ✅ Prevents memory leaks
    }

    override fun loadUser(userId: Int) {
        view?.showLoading()
        repository.getUser(userId) { result ->
            view?.hideLoading()
            result.onSuccess { user -> view?.showUser(user) }
            result.onFailure { error ->
                view?.showError(error.message ?: "Unknown error")
            }
        }
    }
}

// View implementation
class UserActivity : AppCompatActivity(), UserContract.View {
    private lateinit var presenter: UserContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter = UserPresenter(UserRepository())
        presenter.attachView(this) // ✅ Attach View
    }

    override fun onDestroy() {
        super.onDestroy()
        presenter.detachView() // ✅ Detach View
    }

    override fun showUser(user: User) {
        nameTextView.text = user.name
    }
}
```

### Advantages of MVP

1. **Testability** — Presenter can be tested independently with JUnit (mock View)
2. **Separation of concerns** — clear responsibilities for each component
3. **Reusability** — Presenter can be reused with different Views
4. **No Android dependencies** — Presenter is easy to test

### Disadvantages of MVP

1. **God Presenter** — Presenter can expand into a huge all-knowing class if single responsibility principle is not followed
2. **Memory leaks** — if Presenter holds View reference after View is destroyed (need to detach View properly)
3. **Boilerplate** — requires more code compared to simple approaches
4. **State loss** — Presenter is typically recreated on configuration changes (unless retained)

### MVP vs MVVM vs MVC

| Aspect | MVP | MVVM | MVC |
|--------|-----|------|-----|
| **View-Presenter/ViewModel** | Bidirectional | Unidirectional (observable) | Direct coupling |
| **View reference** | Presenter knows View | ViewModel doesn't know View | Controller knows View |
| **View updates** | Explicit interface calls | Automatic (data binding) | Direct calls |
| **Testability** | Good (mock View) | Excellent (no View) | Moderate |
| **Lifecycle** | Manual handling | Automatic | Manual |
| **Configuration changes** | State lost | State survives | State lost |

### Best Practices

```kotlin
// ✅ DO: Use Contract interface
interface ScreenContract {
    interface View { }
    interface Presenter { }
}

// ✅ DO: Detach View in onDestroy
override fun onDestroy() {
    super.onDestroy()
    presenter.detachView()
}

// ✅ DO: Null-check before calling View
view?.showData(data)

// ❌ DON'T: Create God Presenter with too many responsibilities
// ❌ DON'T: Forget to detach View (causes memory leaks)
```

---

## Follow-ups

- How does MVP handle configuration changes (screen rotation)?
- What strategies can prevent God Presenter anti-pattern?
- How to implement MVP with coroutines for lifecycle management?
- When should you prefer MVP over MVVM in modern Android?
- How to unit test a Presenter with mocked View interface?

## References

- [[c-mvvm-pattern]]
- [[c-architecture-patterns]]
- [Model–view–presenter (Wikipedia)](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93presenter)
- [Android Architecture Patterns Part 2: Model-View-Presenter](https://medium.com/upday-devs/android-architecture-patterns-part-2-model-view-presenter-8a6faaae14a5)

## Related Questions

### Prerequisites (Easier)
- [[q-android-architectural-patterns--android--medium]] — Overview of architectural patterns

### Related (Same Level)
- [[q-save-markdown-structure-database--android--medium]] — Data persistence patterns
- MVVM pattern implementation in Android
- MVI architecture pattern differences

### Advanced (Harder)
- [[q-workmanager-chaining--android--hard]] — Background processing with architecture patterns
- Clean Architecture with MVP in multi-module projects
- State preservation strategies across configuration changes

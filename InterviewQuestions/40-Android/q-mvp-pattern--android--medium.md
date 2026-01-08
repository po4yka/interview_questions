---\
id: android-200
title: "MVP Pattern / MVP Паттерн"
aliases: ["Model-View-Presenter", "MVP Pattern", "MVP Паттерн"]
topic: android
subtopics: [architecture-mvvm, testing-unit]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-mvvm-pattern, q-android-architectural-patterns--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/architecture-mvvm, android/testing-unit, architecture-patterns, difficulty/medium, model-view-presenter, mvp]

---\
# Вопрос (RU)

> Что такое архитектурный паттерн MVP (Model-`View`-Presenter)? Объясните его компоненты и отличия от других паттернов.

# Question (EN)

> What is the MVP (Model-`View`-Presenter) architectural pattern? Explain its components and how it differs from other patterns.

---

## Ответ (RU)

**MVP (Model-`View`-Presenter)** — архитектурный паттерн для разделения ответственности и улучшения тестируемости презентационной логики.

### Компоненты MVP

**1. Model** — слой данных, содержит бизнес-логику, взаимодействует с сетью и базой данных, независим от UI.

**2. `View`** — UI слой, отображает данные и уведомляет Presenter о действиях пользователя. Пассивен — не содержит бизнес-логики, только показывает то, что говорит Presenter. Обычно реализуется `Activity`/`Fragment` или кастомным `View`.

**3. Presenter** — получает данные из Model, применяет UI-логику, управляет состоянием `View`, реагирует на действия пользователя, выступает посредником между Model и `View`. Не содержит Android-фреймворк зависимостей (в идеале) и работает с `View` через интерфейс.

### Contract Interface

`View` и Presenter тесно сотрудничают:
- `View` держит ссылку на Presenter и делегирует ему действия пользователя.
- Presenter держит ссылку на интерфейс `View`, а не на конкретную реализацию.

Для упрощения юнит-тестирования Presenter и явного описания обязанностей часто используют **Contract**-интерфейс, определяющий методы `View` и Presenter.

```kotlin
// Contract определяет обязанности View и Presenter
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
        // Упрощённый пример: предполагаем, что getUser предоставляет результат через callback
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
        presenter.detachView() // ✅ Отвязка View, чтобы минимизировать риск утечек
        super.onDestroy()
    }

    override fun showUser(user: User) {
        nameTextView.text = user.name
    }
}
```

(В реальных проектах также важно учитывать отмену асинхронных операций при уничтожении `View`, чтобы не обновлять уничтоженную `View`.)

### Преимущества MVP

1. **Тестируемость** — Presenter тестируется независимо с JUnit (mock `View`).
2. **Разделение ответственности** — чёткие роли для каждого компонента.
3. **Переиспользование** — Presenter можно использовать с разными `View`.
4. **Минимизация Android-зависимостей** — Presenter легко тестировать, если он не зависит от Android API.

### Недостатки MVP

1. **God Presenter** — Presenter может превратиться в огромный класс, если не следовать принципу единственной ответственности.
2. **Утечки памяти** — если Presenter держит ссылку на `View` после её уничтожения (необходим `detachView`).
3. **Boilerplate код** — требуется больше кода по сравнению с простыми подходами.
4. **Потеря состояния** — при изменениях конфигурации Presenter часто пересоздаётся и теряет состояние, если специально не сохранять/ретейнить его.

### MVP Vs MVVM Vs MVC

| Аспект | MVP | MVVM | MVC |
|--------|-----|------|-----|
| **`View`-Presenter/`ViewModel`** | Двунаправленное взаимодействие: `View` вызывает Presenter, Presenter вызывает `View`-интерфейс | Как правило, однонаправленные потоки данных (observable), `View` подписывается на данные `ViewModel` | Прямая связь между `View` и Controller |
| **Ссылка на `View`** | Presenter знает `View` через интерфейс | `ViewModel` не знает `View` напрямую | Controller знает `View` |
| **Обновление `View`** | Явные вызовы методов `View`-интерфейса | Чаще всего через observable / data binding | Прямые вызовы на `View` |
| **Тестируемость** | Хорошая (mock `View`) | Отличная (минимум зависимостей от `View`) | Средняя |
| **`Lifecycle`** | Ручное управление (attach/detach) | `ViewModel` привязан к lifecycle владельца, но ресурсы внутри всё равно требуют явного управления | Ручное |
| **Изменения конфигурации** | Состояние теряется по умолчанию, если Presenter не ретейнится/не сохраняет state | `ViewModel` переживает конфигурационные изменения, но не гарантирует выживание при убийстве процесса | Состояние теряется по умолчанию |

### Best Practices

```kotlin
// ✅ DO: Используйте Contract интерфейс для явного разделения обязанностей
interface ScreenContract {
    interface View { }
    interface Presenter {
        fun attachView(view: View)
        fun detachView()
    }
}

// ✅ DO: Отвязывайте View в onDestroy (или соответствующем lifecycle-событии)
override fun onDestroy() {
    presenter.detachView()
    super.onDestroy()
}

// ✅ DO: Проверяйте null перед вызовом View
view?.showData(data)

// ❌ DON'T: Создавайте God Presenter с избыточными обязанностями
// ❌ DON'T: Забывайте отвязывать View (вызывает утечки памяти)
// ❌ DON'T: Выполнять длительные операции в Presenter без возможности отмены, если View уничтожена
```

---

## Answer (EN)

**MVP (Model-`View`-Presenter)** is an architectural pattern designed to improve separation of concerns in presentation logic and make UI-related logic more testable.

### MVP Components

**1. Model** — the data/business layer, handles business rules and communication with network and database layers, independent of the UI.

**2. `View`** — the UI layer, displays data and forwards user actions to Presenter. Passive — contains no business logic, only displays what Presenter instructs. Typically implemented by an `Activity`/`Fragment` or a custom `View`.

**3. Presenter** — retrieves data from Model, applies UI logic, manages `View` state, reacts to user input (via `View` callbacks), and acts as a mediator between Model and `View`. Ideally contains no Android framework dependencies and talks to `View` via an interface.

### Contract Interface

`View` and Presenter collaborate closely:
- The `View` holds a reference to Presenter and delegates user actions to it.
- The Presenter holds a reference to the `View` interface, not to a concrete Android class.

A common convention (not a strict requirement) is to define a **Contract** interface that declares the `View` and Presenter interfaces, making the responsibilities explicit and Presenter easier to unit test.

```kotlin
// Contract defines responsibilities of View and Presenter
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
        // Simplified example: assuming getUser delivers result via callback
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
        presenter.detachView() // ✅ Detach View to minimize leak risk
        super.onDestroy()
    }

    override fun showUser(user: User) {
        nameTextView.text = user.name
    }
}
```

(In real apps you should also ensure that asynchronous work is cancelled or ignored when the `View` is destroyed, to avoid updating a dead `View`.)

### Advantages of MVP

1. **Testability** — Presenter can be unit tested independently (mocking the `View`).
2. **Separation of concerns** — clear responsibilities between Model, `View`, and Presenter.
3. **Reusability** — Presenter can be reused with different `View` implementations.
4. **Reduced Android dependencies** — Presenter stays platform-agnostic, making tests simpler.

### Disadvantages of MVP

1. **God Presenter** — Presenter can grow too large if the single responsibility principle is ignored.
2. **Memory leaks** — if Presenter holds `View` reference after `View` is destroyed (must detach `View`).
3. **Boilerplate** — more interfaces and wiring compared to simpler patterns.
4. **State loss** — Presenter is often recreated on configuration changes and loses state unless specifically retained or persisted.

### MVP Vs MVVM Vs MVC

| Aspect | MVP | MVVM | MVC |
|--------|-----|------|-----|
| **`View`-Presenter/`ViewModel`** | Bidirectional interaction: `View` calls Presenter, Presenter calls `View` interface | Typically unidirectional data flows (observable); `View` observes `ViewModel` | Direct coupling between `View` and Controller |
| **`View` reference** | Presenter knows `View` via interface | `ViewModel` does not directly know `View` | Controller knows `View` |
| **`View` updates** | Explicit `View` interface method calls | Via observables / data binding / state flows | Direct calls on `View` |
| **Testability** | Good (mock `View`) | Excellent (minimal `View` dependencies) | Moderate |
| **`Lifecycle`** | Manual (attach/detach) | `ViewModel` is lifecycle-aware (tied to owner), but internal resources still need explicit cleanup | Manual |
| **Configuration changes** | State lost by default unless Presenter is retained or state is saved | `ViewModel` survives configuration changes; not guaranteed across process death | State lost by default |

### Best Practices

```kotlin
// ✅ DO: Use a Contract interface to clearly define responsibilities
interface ScreenContract {
    interface View { }
    interface Presenter {
        fun attachView(view: View)
        fun detachView()
    }
}

// ✅ DO: Detach View in onDestroy (or appropriate lifecycle callback)
override fun onDestroy() {
    presenter.detachView()
    super.onDestroy()
}

// ✅ DO: Null-check before calling View
view?.showData(data)

// ❌ DON'T: Create a God Presenter with too many responsibilities
// ❌ DON'T: Forget to detach View (causes memory leaks)
// ❌ DON'T: Run long asynchronous work without handling View destruction (avoid posting results to a detached View)
```

---

## Follow-ups

- How does MVP handle configuration changes (screen rotation), and what techniques can be used to retain Presenter or state?
- What strategies can prevent the God Presenter anti-pattern (e.g., splitting by feature, use cases/interactors)?
- How to integrate MVP with coroutines or other async mechanisms while manually managing lifecycle?
- When should you prefer MVP over MVVM in modern Android codebases?
- How to unit test a Presenter with a mocked `View` interface?

## References

- [[c-mvvm-pattern]]
- [[moc-architecture-patterns]]
- [Model–view–presenter (Wikipedia)](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93presenter)
- [Android Architecture Patterns Part 2: Model-`View`-Presenter](https://medium.com/upday-devs/android-architecture-patterns-part-2-model-view-presenter-8a6faaae14a5)

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
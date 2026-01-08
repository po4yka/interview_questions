---\
id: android-313
title: "Presenter Notify View / Presenter уведомляет View"
aliases: ["MVP communication", "Presenter Notify View", "Presenter уведомляет View", "Взаимодействие MVP"]
topic: android
subtopics: [architecture-mvvm]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-kapt-vs-ksp--android--medium, q-what-are-fragments-for-if-there-is-activity--android--medium, q-what-is-viewmodel--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-mvvm, android/lifecycle, architecture-mvvm, callback, difficulty/medium, lifecycle, mvp, platform/android, presenter, view]

---\
# Вопрос (RU)

> После получения результата внутри Presenter как сообщить об этом `View`?

# Question (EN)

> After getting a result inside Presenter, how to notify the `View`?

---

## Ответ (RU)

В MVP-архитектуре Presenter отвечает за бизнес-логику, а `View` — за отображение. Presenter не должен знать об Android-специфике `View` (`Activity`/`Fragment`), поэтому используется абстракция через интерфейс и контролируемое управление ссылкой на `View`.

### 1. Интерфейсный Контракт (Interface Contract) ✅

**Наиболее распространенный подход**. Presenter вызывает методы интерфейса, который реализует `View`, и управляет её привязкой/отвязкой:

```kotlin
// Contract
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
        fun loadUser(userId: String)
    }
}

// Presenter
class UserPresenter(
    private val repository: UserRepository
) : UserContract.Presenter {

    private var view: UserContract.View? = null

    override fun attachView(view: UserContract.View) {
        this.view = view
    }

    override fun detachView() {
        this.view = null
    }

    override fun loadUser(userId: String) {
        view?.showLoading()
        repository.getUser(userId) { result ->
            // Важно: callback может прийти после detachView(), поэтому всегда обращаемся к view как к nullable
            view?.hideLoading()
            when (result) {
                is Success -> view?.showUser(result.data)
                is Error -> view?.showError(result.message)
            }
        }
    }
}

// View (Activity/Fragment)
class UserActivity : AppCompatActivity(), UserContract.View {
    private lateinit var presenter: UserContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter = UserPresenter(UserRepository())
        presenter.attachView(this)
    }

    override fun onDestroy() {
        presenter.detachView()
        super.onDestroy()
    }

    override fun showUser(user: User) {
        // Update UI
        binding.userName.text = user.name
    }

    // Реализуем остальные методы View
}
```

**Преимущества**:
- Четкий контракт между слоями
- Легко тестировать (можно мокировать `View`)
- Type-safe вызовы

**Недостатки**:
- Много boilerplate кода для интерфейсов
- Нужно явно отвязывать `View`, чтобы избежать утечек памяти и обновлений после уничтожения

### 2. `Callback`-функции ✅

Передача лямбда-функций для специфичных операций. Подход уместен для локальных, ограниченных по времени задач.

```kotlin
class DataPresenter(
    private val repository: DataRepository,
    private val onDataLoaded: (Data) -> Unit,
    private val onError: (String) -> Unit
) {
    fun fetchData() {
        repository.getData { result ->
            when (result) {
                is Success -> onDataLoaded(result.data)
                is Error -> onError(result.message)
            }
        }
    }
}

// Usage (например, в Activity/Fragment)
val presenter = DataPresenter(
    repository = DataRepository(),
    onDataLoaded = { data -> updateUI(data) },
    onError = { msg -> showError(msg) }
)
```

**Преимущества**:
- Минимум boilerplate
- Гибкость для одноразовых операций

**Недостатки**:
- Возможны утечки памяти, если Presenter или repository хранят callback дольше, чем живет `View`
- Требуется явно отменять операции/обнулять ссылки при уничтожении `View`
- Сложнее управлять множественными callback как единым состоянием

### 3. `LiveData`/`StateFlow` (Гибридный подход)

Если команда постепенно переходит к MVVM, можно использовать `LiveData`/`StateFlow` для уведомления `View` о состояниях. Важно понимать, что это уже не классический MVP, а `ViewModel`-подобный слой.

```kotlin
class UserPresenterLikeViewModel(
    private val repository: UserRepository
) {
    private val _userState = MutableLiveData<UserState>()
    val userState: LiveData<UserState> = _userState

    fun loadUser(userId: String) {
        _userState.value = UserState.Loading
        repository.getUser(userId) { result ->
            _userState.postValue(
                when (result) {
                    is Success -> UserState.Success(result.data)
                    is Error -> UserState.Error(result.message)
                }
            )
        }
    }
}

// View observes (Activity/Fragment)
userPresenterLikeViewModel.userState.observe(this) { state ->
    when (state) {
        is UserState.Loading -> showLoading()
        is UserState.Success -> showUser(state.user)
        is UserState.Error -> showError(state.message)
    }
}
```

**Преимущества**:
- Наблюдение привязано к жизненному циклу `View` (через `LifecycleOwner`)
- Удобно выражать состояния экрана

**Недостатки**:
- Это уже не чистый MVP, а гибрид/переход к MVVM
- Требует аккуратного выбора владельца `LiveData`/`StateFlow` (обычно `ViewModel`)

### Важные Моменты (Best Practices)

**Проверка жизненного цикла** — Presenter должен учитывать, что `View` может быть уничтожена, и не держать на неё долгоживущих сильных ссылок. При асинхронных операциях всегда работать с `view?` и быть готовым к тому, что к моменту callback-а `View` уже отвязана.

```kotlin
interface BaseView

open class BasePresenter<V : BaseView> {
    protected var view: V? = null
        private set

    fun attachView(view: V) {
        this.view = view
    }

    fun detachView() {
        this.view = null
    }

    protected fun withView(action: (V) -> Unit) {
        view?.let(action)
    }
}
```

**WeakReference** — использование `WeakReference<``View``>` внутри Presenter, как правило, не требуется при правильно реализованных `attachView()/detachView()` и может усложнять код или приводить к неожиданным обнулениям. Если и использовать, то осознанно и с пониманием последствий.

**`Thread` safety** — репозиторий и другие источники данных часто вызывают callback из фоновых потоков, поэтому все операции обновления UI должны выполняться на главном потоке:

```kotlin
// ✅ Пример (псевдокод): обновление View через Handler главного потока
fun notifyView(data: Data) {
    mainThreadHandler.post {
        view?.showData(data)
    }
}

// ❌ Неправильно - может привести к крашу, если вызвано из background thread
fun notifyViewWrong(data: Data) {
    view?.showData(data)
}
```

Где `mainThreadHandler` создан на `Looper.getMainLooper()`, либо вместо этого можно использовать `runOnUiThread`, `lifecycleScope`, `Dispatchers.Main` и т.п.

## Answer (EN)

In MVP architecture, the Presenter handles business logic while the `View` handles rendering. The Presenter should not depend on Android-specific `View` implementations (`Activity`/`Fragment`) directly; instead, use an interface and explicit `View` attachment/detachment.

### 1. Interface Contract ✅

**Most common approach.** The Presenter calls methods on an interface implemented by the `View` and manages its attachment/detachment:

```kotlin
// Contract
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
        fun loadUser(userId: String)
    }
}

// Presenter
class UserPresenter(
    private val repository: UserRepository
) : UserContract.Presenter {

    private var view: UserContract.View? = null

    override fun attachView(view: UserContract.View) {
        this.view = view
    }

    override fun detachView() {
        this.view = null
    }

    override fun loadUser(userId: String) {
        view?.showLoading()
        repository.getUser(userId) { result ->
            // Important: callback may arrive after detachView(), always treat view as nullable
            view?.hideLoading()
            when (result) {
                is Success -> view?.showUser(result.data)
                is Error -> view?.showError(result.message)
            }
        }
    }
}

// View (Activity/Fragment)
class UserActivity : AppCompatActivity(), UserContract.View {
    private lateinit var presenter: UserContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter = UserPresenter(UserRepository())
        presenter.attachView(this)
    }

    override fun onDestroy() {
        presenter.detachView()
        super.onDestroy()
    }

    override fun showUser(user: User) {
        // Update UI
        binding.userName.text = user.name
    }

    // Implement other View methods
}
```

**Advantages**:
- Clear contract between layers
- Easy to unit test (mock the `View`)
- Type-safe calls

**Disadvantages**:
- Boilerplate for contracts
- Must detach `View` explicitly to avoid memory leaks and updates after destruction

### 2. `Callback` Functions ✅

Pass lambda callbacks for specific operations. Suitable for small, localized tasks.

```kotlin
class DataPresenter(
    private val repository: DataRepository,
    private val onDataLoaded: (Data) -> Unit,
    private val onError: (String) -> Unit
) {
    fun fetchData() {
        repository.getData { result ->
            when (result) {
                is Success -> onDataLoaded(result.data)
                is Error -> onError(result.message)
            }
        }
    }
}

// Usage (e.g., in Activity/Fragment)
val presenter = DataPresenter(
    repository = DataRepository(),
    onDataLoaded = { data -> updateUI(data) },
    onError = { msg -> showError(msg) }
)
```

**Advantages**:
- Minimal boilerplate
- Flexible for one-off flows

**Disadvantages**:
- Potential memory leaks if Presenter/repository store callbacks longer than the `View`'s lifecycle
- Need to cancel operations / clear callbacks when `View` is destroyed
- Harder to treat multiple callbacks as a single UI state

### 3. `LiveData`/`StateFlow` (Hybrid Approach)

If transitioning towards MVVM, you can use `LiveData` or `StateFlow` to expose UI state. This effectively becomes a `ViewModel`-like layer rather than classic MVP.

```kotlin
class UserPresenterLikeViewModel(
    private val repository: UserRepository
) {
    private val _userState = MutableLiveData<UserState>()
    val userState: LiveData<UserState> = _userState

    fun loadUser(userId: String) {
        _userState.value = UserState.Loading
        repository.getUser(userId) { result ->
            _userState.postValue(
                when (result) {
                    is Success -> UserState.Success(result.data)
                    is Error -> UserState.Error(result.message)
                }
            )
        }
    }
}

// View observes
userPresenterLikeViewModel.userState.observe(this) { state ->
    when (state) {
        is UserState.Loading -> showLoading()
        is UserState.Success -> showUser(state.user)
        is UserState.Error -> showError(state.message)
    }
}
```

**Advantages**:
- `Observer` tied to `LifecycleOwner` (lifecycle-aware observation)
- Natural way to represent screen states

**Disadvantages**:
- Not pure MVP; hybrid / closer to MVVM
- Must ensure the holder of `LiveData`/`StateFlow` has appropriate lifecycle (typically a `ViewModel`)

### Important Considerations (Best Practices)

**`Lifecycle` awareness** — Presenter should handle the fact that the `View` can be destroyed and must not keep a long-lived strong reference to it. For async operations, always work with `view?` and be prepared that by the time the callback fires, the `View` is detached.

```kotlin
interface BaseView

open class BasePresenter<V : BaseView> {
    protected var view: V? = null
        private set

    fun attachView(view: V) {
        this.view = view
    }

    fun detachView() {
        this.view = null
    }

    protected fun withView(action: (V) -> Unit) {
        view?.let(action)
    }
}
```

**WeakReference** — using `WeakReference<``View``>` inside Presenter is usually unnecessary when `attachView()/detachView()` are implemented correctly and may complicate code or introduce unexpected nulls. Use only deliberately and with understanding.

**`Thread` safety** — repositories and other data sources often invoke callbacks on background threads, so all UI updates must be executed on the Main thread:

```kotlin
// ✅ Example (pseudo-code): post work to main thread handler
fun notifyView(data: Data) {
    mainThreadHandler.post {
        view?.showData(data)
    }
}

// ❌ Wrong - may crash if called from a background thread
fun notifyViewWrong(data: Data) {
    view?.showData(data)
}
```

Where `mainThreadHandler` is created with `Looper.getMainLooper()`, or use `runOnUiThread`, `lifecycleScope`, `Dispatchers.Main`, etc.

---

## Дополнительные Вопросы (Follow-ups, RU)

- Как обрабатывать изменения конфигурации (например, поворот экрана) в MVP, не теряя состояние Presenter?
- В чем различия между паттернами MVP и MVVM в Android?
- Как правильно тестировать Presenter с использованием мок-объектов `View` в unit-тестах?
- Должен ли Presenter хранить ссылку на Android `Context`? Почему да или нет?
- Как реализовать корректную обработку ошибок и retry-логики в Presenter?

## Follow-ups

- How to handle configuration changes (rotation) in MVP without losing Presenter state?
- What are the differences between MVP and MVVM patterns in Android?
- How to properly test Presenter with mock `View` in unit tests?
- Should Presenter hold reference to Android `Context`? Why or why not?
- How to implement proper error handling and retry logic in Presenter?

## Ссылки (RU)

- [Android Architecture Guide](https://developer.android.com/topic/architecture)

## References

- [Android Architecture Guide](https://developer.android.com/topic/architecture)

## Связанные Вопросы (RU)

### Предпосылки (проще)

- [[q-viewmodel-pattern--android--easy]] — Понимание `ViewModel`
- [[q-recyclerview-sethasfixedsize--android--easy]] — Оптимизация `View`

### Связанные (тот Же уровень)

- [[q-what-is-viewmodel--android--medium]] — Подробности о `ViewModel`
- [[q-testing-viewmodels-turbine--android--medium]] — Паттерны тестирования
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] — Методы перерисовки `View`

### Продвинутые (сложнее)

- [[q-compose-custom-layout--android--hard]] — Современная композиция `View`

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Understanding `ViewModel`
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View` optimization

### Related (Same Level)
- [[q-what-is-viewmodel--android--medium]] - `ViewModel` in detail
- [[q-testing-viewmodels-turbine--android--medium]] - Testing patterns
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View` redraw methods

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Modern `View` composition

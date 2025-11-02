---
id: android-313
title: "Presenter Notify View / Presenter уведомляет View"
aliases: ["Presenter Notify View", "Presenter уведомляет View", "MVP communication", "Взаимодействие MVP"]
topic: android
subtopics: [architecture-mvvm, lifecycle]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-what-are-fragments-for-if-there-is-activity--android--medium, q-kapt-vs-ksp--android--medium, q-what-is-viewmodel--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/architecture-mvvm, android/lifecycle, architecture-mvvm, lifecycle, mvp, presenter, view, callback, difficulty/medium, platform/android]
---
# Вопрос (RU)

После получения результата внутри Presenter как сообщить об этом View?

# Question (EN)

After getting a result inside Presenter, how to notify the View?

---

## Ответ (RU)

В MVP-архитектуре Presenter отвечает за бизнес-логику, а View — за отображение. Presenter не должен знать об Android-специфике View (Activity/Fragment), поэтому используется абстракция через интерфейс.

### 1. Интерфейсный контракт (Interface Contract) ✅

**Наиболее распространенный подход**. Presenter вызывает методы интерфейса, который реализует View:

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
        fun loadUser(userId: String)
        fun onDestroy()
    }
}

// Presenter
class UserPresenter(
    private val view: UserContract.View,
    private val repository: UserRepository
) : UserContract.Presenter {

    override fun loadUser(userId: String) {
        view.showLoading()
        repository.getUser(userId) { result ->
            view.hideLoading()
            when (result) {
                is Success -> view.showUser(result.data)
                is Error -> view.showError(result.message)
            }
        }
    }
}

// View (Activity/Fragment)
class UserActivity : AppCompatActivity(), UserContract.View {
    private lateinit var presenter: UserPresenter

    override fun showUser(user: User) {
        // Update UI
        binding.userName.text = user.name
    }
}
```

**Преимущества**:
- Четкий контракт между слоями
- Легко тестировать (можно мокировать View)
- Type-safe вызовы

**Недостатки**:
- Много boilerplate кода для интерфейсов
- При уничтожении View может быть NPE (нужна проверка)

### 2. Callback-функции ✅

Передача лямбда-функций для специфичных операций:

```kotlin
class DataPresenter(
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

// Usage
val presenter = DataPresenter(
    onDataLoaded = { data -> updateUI(data) },
    onError = { msg -> showError(msg) }
)
```

**Преимущества**:
- Минимум boilerplate
- Гибкость для одноразовых операций

**Недостатки**:
- Может привести к memory leak если не управлять жизненным циклом
- Сложнее тестировать множественные callback

### 3. LiveData/StateFlow (Гибридный подход)

Если используется переход к MVVM, Presenter может эмитить состояния:

```kotlin
class UserPresenter {
    private val _userState = MutableLiveData<UserState>()
    val userState: LiveData<UserState> = _userState

    fun loadUser(userId: String) {
        _userState.value = UserState.Loading
        repository.getUser(userId) { result ->
            _userState.value = when (result) {
                is Success -> UserState.Success(result.data)
                is Error -> UserState.Error(result.message)
            }
        }
    }
}

// View observes
presenter.userState.observe(this) { state ->
    when (state) {
        is Loading -> showLoading()
        is Success -> showUser(state.user)
        is Error -> showError(state.message)
    }
}
```

**Преимущества**:
- Lifecycle-aware (автоматически отписывается)
- Нет проблем с утечками памяти
- Проще работать с потоками

**Недостатки**:
- Это уже не чистый MVP, а гибрид с MVVM
- Добавляет зависимость от Android Lifecycle

### Важные моменты (Best Practices)

**Проверка жизненного цикла** — Presenter должен проверять, что View еще "жива":

```kotlin
class BasePresenter<V : BaseView>(private var view: V?) {

    protected fun executeViewAction(action: (V) -> Unit) {
        view?.let { action(it) }
    }

    fun onDestroy() {
        view = null // ✅ Avoid memory leaks
    }
}
```

**Weak reference** ❌ — не используйте `WeakReference<View>` в Presenter:
- Усложняет код
- Может привести к неожиданной потере ссылки
- Лучше явно управлять через `onDestroy()`

**Thread safety** — всегда переключайтесь на Main thread для UI операций:

```kotlin
// ✅ Correct
fun notifyView(data: Data) {
    mainThreadHandler.post {
        view.showData(data)
    }
}

// ❌ Wrong - может крашнуться если вызвано из background thread
fun notifyView(data: Data) {
    view.showData(data)
}
```

## Answer (EN)

In MVP architecture, the Presenter handles business logic while the View handles display. The Presenter should not know Android-specific details about the View (Activity/Fragment), so abstraction through interfaces is used.

### 1. Interface Contract ✅

**Most common approach**. The Presenter calls interface methods that the View implements:

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
        fun loadUser(userId: String)
        fun onDestroy()
    }
}

// Presenter
class UserPresenter(
    private val view: UserContract.View,
    private val repository: UserRepository
) : UserContract.Presenter {

    override fun loadUser(userId: String) {
        view.showLoading()
        repository.getUser(userId) { result ->
            view.hideLoading()
            when (result) {
                is Success -> view.showUser(result.data)
                is Error -> view.showError(result.message)
            }
        }
    }
}

// View (Activity/Fragment)
class UserActivity : AppCompatActivity(), UserContract.View {
    private lateinit var presenter: UserPresenter

    override fun showUser(user: User) {
        // Update UI
        binding.userName.text = user.name
    }
}
```

**Advantages**:
- Clear contract between layers
- Easy to test (can mock View)
- Type-safe calls

**Disadvantages**:
- Lots of boilerplate for interfaces
- Potential NPE when View is destroyed (needs checks)

### 2. Callback Functions ✅

Passing lambda functions for specific operations:

```kotlin
class DataPresenter(
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

// Usage
val presenter = DataPresenter(
    onDataLoaded = { data -> updateUI(data) },
    onError = { msg -> showError(msg) }
)
```

**Advantages**:
- Minimal boilerplate
- Flexibility for one-off operations

**Disadvantages**:
- Can lead to memory leaks if lifecycle not managed
- Harder to test multiple callbacks

### 3. LiveData/StateFlow (Hybrid Approach)

If transitioning to MVVM, the Presenter can emit states:

```kotlin
class UserPresenter {
    private val _userState = MutableLiveData<UserState>()
    val userState: LiveData<UserState> = _userState

    fun loadUser(userId: String) {
        _userState.value = UserState.Loading
        repository.getUser(userId) { result ->
            _userState.value = when (result) {
                is Success -> UserState.Success(result.data)
                is Error -> UserState.Error(result.message)
            }
        }
    }
}

// View observes
presenter.userState.observe(this) { state ->
    when (state) {
        is Loading -> showLoading()
        is Success -> showUser(state.user)
        is Error -> showError(state.message)
    }
}
```

**Advantages**:
- Lifecycle-aware (auto-unsubscribes)
- No memory leak issues
- Easier thread handling

**Disadvantages**:
- Not pure MVP, but MVP-MVVM hybrid
- Adds dependency on Android Lifecycle

### Important Considerations (Best Practices)

**Lifecycle checking** — Presenter should verify View is still "alive":

```kotlin
class BasePresenter<V : BaseView>(private var view: V?) {

    protected fun executeViewAction(action: (V) -> Unit) {
        view?.let { action(it) }
    }

    fun onDestroy() {
        view = null // ✅ Avoid memory leaks
    }
}
```

**Weak reference** ❌ — don't use `WeakReference<View>` in Presenter:
- Complicates code
- Can lead to unexpected reference loss
- Better to explicitly manage via `onDestroy()`

**Thread safety** — always switch to Main thread for UI operations:

```kotlin
// ✅ Correct
fun notifyView(data: Data) {
    mainThreadHandler.post {
        view.showData(data)
    }
}

// ❌ Wrong - can crash if called from background thread
fun notifyView(data: Data) {
    view.showData(data)
}
```

---

## Follow-ups

- How to handle configuration changes (rotation) in MVP without losing Presenter state?
- What are the differences between MVP and MVVM patterns in Android?
- How to properly test Presenter with mock View in unit tests?
- Should Presenter hold reference to Android Context? Why or why not?
- How to implement proper error handling and retry logic in Presenter?

## References

- [[c-mvp-pattern]] - MVP architectural pattern
- [[c-mvvm-pattern]] - MVVM for comparison
- [Android Architecture Guide](https://developer.android.com/topic/architecture)

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Understanding ViewModel
- [[q-recyclerview-sethasfixedsize--android--easy]] - View optimization

### Related (Same Level)
- [[q-what-is-viewmodel--android--medium]] - ViewModel in detail
- [[q-testing-viewmodels-turbine--android--medium]] - Testing patterns
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View redraw methods

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Modern View composition

---
id: "20251015082237444"
title: "Cancel Presenter Requests / Отмена запросов Presenter"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - android/architecture-mvi
  - android/lifecycle
  - architecture-mvi
  - lifecycle
  - mvp
  - platform/android
  - presenter-view-communication
---
# Какие есть механизмы для отмены запросов presenter у view?

# Question (EN)
> What mechanisms exist for canceling Presenter requests to View?

# Вопрос (RU)
> Какие есть механизмы для отмены запросов presenter у view?

---

## Answer (EN)

In MVP (Model-View-Presenter) architecture, when the Presenter sends requests to the View, it's crucial to cancel these requests when the View is destroyed or becomes inactive to prevent crashes, memory leaks, and unnecessary work.

### The Problem

```kotlin
// BAD - Memory leak and potential crash
class UserPresenter(private val view: UserView) {

    fun loadUser(userId: String) {
        // Long-running operation
        Thread {
            val user = repository.getUser(userId)

            // View might be destroyed by now!
            view.showUser(user) // CRASH if Activity is destroyed!
        }.start()
    }
}

class UserActivity : AppCompatActivity(), UserView {
    private val presenter = UserPresenter(this)

    override fun onDestroy() {
        super.onDestroy()
        // How to cancel presenter's ongoing operations?
    }
}
```

### Solution 1: Weak References

Use `WeakReference` to avoid holding strong reference to View:

```kotlin
class UserPresenter(view: UserView) {
    private val viewRef = WeakReference(view)

    fun loadUser(userId: String) {
        Thread {
            val user = repository.getUser(userId)

            // Check if view still exists
            viewRef.get()?.showUser(user)
        }.start()
    }

    fun onDestroy() {
        viewRef.clear()
    }
}

class UserActivity : AppCompatActivity(), UserView {
    private val presenter = UserPresenter(this)

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }
}
```

**Pros:**
- Prevents memory leaks
- Simple to implement

**Cons:**
- Doesn't actually cancel ongoing work
- Work continues even if not needed

### Solution 2: Lifecycle-Aware Components

Use Android's Lifecycle library:

```kotlin
class UserPresenter(
    private val view: UserView,
    private val lifecycle: Lifecycle
) : DefaultLifecycleObserver {

    private var isViewActive = false

    init {
        lifecycle.addObserver(this)
    }

    override fun onStart(owner: LifecycleOwner) {
        isViewActive = true
    }

    override fun onStop(owner: LifecycleOwner) {
        isViewActive = false
    }

    override fun onDestroy(owner: LifecycleOwner) {
        lifecycle.removeObserver(this)
    }

    fun loadUser(userId: String) {
        Thread {
            val user = repository.getUser(userId)

            if (isViewActive) {
                view.showUser(user)
            }
        }.start()
    }
}

class UserActivity : AppCompatActivity(), UserView {
    private lateinit var presenter: UserPresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        presenter = UserPresenter(this, lifecycle)
    }
}
```

**Pros:**
- Automatic lifecycle management
- No manual cleanup needed

**Cons:**
- Still doesn't cancel work
- Work runs unnecessarily

### Solution 3: RxJava with Disposables

Use RxJava for proper cancellation:

```kotlin
class UserPresenter(private val view: UserView) {

    private val compositeDisposable = CompositeDisposable()

    fun loadUser(userId: String) {
        val disposable = Observable.fromCallable {
            repository.getUser(userId)
        }
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe(
                { user -> view.showUser(user) },
                { error -> view.showError(error) }
            )

        compositeDisposable.add(disposable)
    }

    fun loadUsers() {
        val disposable = repository.getUsers()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe(
                { users -> view.showUsers(users) },
                { error -> view.showError(error) }
            )

        compositeDisposable.add(disposable)
    }

    fun onDestroy() {
        // Cancel all ongoing requests
        compositeDisposable.clear()
    }
}

class UserActivity : AppCompatActivity(), UserView {
    private val presenter = UserPresenter(this)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)

        presenter.loadUser("123")
    }

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }

    override fun showUser(user: User) {
        // Update UI
    }

    override fun showError(error: Throwable) {
        Toast.makeText(this, error.message, Toast.LENGTH_SHORT).show()
    }
}
```

**Pros:**
- Actually cancels ongoing work
- Prevents memory leaks
- Clean API

**Cons:**
- Requires RxJava dependency
- Learning curve

### Solution 4: Kotlin Coroutines with Job (Recommended)

Modern approach using Coroutines:

```kotlin
class UserPresenter(private val view: UserView) {

    private val presenterScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    fun loadUser(userId: String) {
        presenterScope.launch {
            try {
                val user = withContext(Dispatchers.IO) {
                    repository.getUser(userId)
                }
                view.showUser(user)
            } catch (e: CancellationException) {
                // Job was cancelled - ignore
            } catch (e: Exception) {
                view.showError(e)
            }
        }
    }

    fun loadUsers() {
        presenterScope.launch {
            try {
                val users = withContext(Dispatchers.IO) {
                    repository.getUsers()
                }
                view.showUsers(users)
            } catch (e: CancellationException) {
                // Cancelled
            } catch (e: Exception) {
                view.showError(e)
            }
        }
    }

    fun onDestroy() {
        // Cancel all coroutines
        presenterScope.cancel()
    }
}

class UserActivity : AppCompatActivity(), UserView {
    private val presenter = UserPresenter(this)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)

        presenter.loadUser("123")
        presenter.loadUsers()
    }

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }

    override fun showUser(user: User) {
        textView.text = user.name
    }

    override fun showUsers(users: List<User>) {
        adapter.submitList(users)
    }

    override fun showError(error: Throwable) {
        Toast.makeText(this, error.message, Toast.LENGTH_SHORT).show()
    }
}
```

**Pros:**
- Cancels ongoing work efficiently
- Modern Kotlin approach
- Built-in to Kotlin
- Clean, readable code

**Cons:**
- Requires understanding coroutines

### Solution 5: Manual Cancellation Flags

Simple boolean flag approach:

```kotlin
class UserPresenter(private val view: UserView) {

    private var isCancelled = false

    fun loadUser(userId: String) {
        isCancelled = false

        Thread {
            // Long operation
            val user = repository.getUser(userId)

            // Check before updating view
            if (!isCancelled) {
                Handler(Looper.getMainLooper()).post {
                    if (!isCancelled) {
                        view.showUser(user)
                    }
                }
            }
        }.start()
    }

    fun onDestroy() {
        isCancelled = true
    }
}
```

**Pros:**
- Simple implementation
- No dependencies

**Cons:**
- Doesn't actually cancel work
- Error-prone
- Requires manual thread management

### Solution 6: Callback Management Pattern

Track and remove callbacks:

```kotlin
class UserPresenter(private val view: UserView) {

    private val handler = Handler(Looper.getMainLooper())
    private val pendingCallbacks = mutableListOf<Runnable>()

    fun loadUser(userId: String) {
        thread {
            val user = repository.getUser(userId)

            val callback = Runnable {
                view.showUser(user)
                pendingCallbacks.remove(this)
            }

            pendingCallbacks.add(callback)
            handler.post(callback)
        }
    }

    fun onDestroy() {
        // Remove all pending callbacks
        pendingCallbacks.forEach { handler.removeCallbacks(it) }
        pendingCallbacks.clear()
    }
}
```

### Complete Example: MVP with Coroutines

```kotlin
// Contract
interface UserContract {
    interface View {
        fun showLoading()
        fun hideLoading()
        fun showUser(user: User)
        fun showUsers(users: List<User>)
        fun showError(message: String)
    }

    interface Presenter {
        fun loadUser(userId: String)
        fun loadUsers()
        fun onDestroy()
    }
}

// Presenter
class UserPresenter(
    private val view: UserContract.View,
    private val repository: UserRepository
) : UserContract.Presenter {

    private val presenterScope = CoroutineScope(
        Dispatchers.Main + SupervisorJob()
    )

    override fun loadUser(userId: String) {
        presenterScope.launch {
            view.showLoading()
            try {
                val user = withContext(Dispatchers.IO) {
                    repository.getUser(userId)
                }
                view.showUser(user)
            } catch (e: CancellationException) {
                // Request cancelled - do nothing
            } catch (e: Exception) {
                view.showError(e.message ?: "Unknown error")
            } finally {
                view.hideLoading()
            }
        }
    }

    override fun loadUsers() {
        presenterScope.launch {
            view.showLoading()
            try {
                val users = withContext(Dispatchers.IO) {
                    repository.getUsers()
                }
                view.showUsers(users)
            } catch (e: CancellationException) {
                // Cancelled
            } catch (e: Exception) {
                view.showError(e.message ?: "Unknown error")
            } finally {
                view.hideLoading()
            }
        }
    }

    override fun onDestroy() {
        presenterScope.cancel()
    }
}

// Activity
class UserActivity : AppCompatActivity(), UserContract.View {

    private lateinit var presenter: UserContract.Presenter
    private lateinit var binding: ActivityUserBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val repository = UserRepository()
        presenter = UserPresenter(this, repository)

        presenter.loadUsers()
    }

    override fun onDestroy() {
        presenter.onDestroy() // Cancel all requests
        super.onDestroy()
    }

    override fun showLoading() {
        binding.progressBar.visibility = View.VISIBLE
    }

    override fun hideLoading() {
        binding.progressBar.visibility = View.GONE
    }

    override fun showUser(user: User) {
        binding.userName.text = user.name
        binding.userEmail.text = user.email
    }

    override fun showUsers(users: List<User>) {
        // Update RecyclerView
    }

    override fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
```

### Comparison Table

| Mechanism | Cancels Work | Memory Safe | Complexity | Recommended |
|-----------|--------------|-------------|------------|-------------|
| Weak References | No | Yes | Low | No |
| Lifecycle-Aware | No | Yes | Medium | No |
| RxJava Disposables | Yes | Yes | High | Legacy code |
| Coroutines + Job | Yes | Yes | Medium | Yes |
| Boolean Flags | No | Partial | Low | No |
| Callback Management | Partial | Yes | Medium | No |

### Best Practices

1. **Always cancel requests** in `onDestroy()`
2. **Use Coroutines** for new code
3. **Use RxJava** if already in project
4. **Avoid WeakReferences** - they don't cancel work
5. **Handle CancellationException** properly
6. **Test with configuration changes** (screen rotation)

### Modern Alternative: MVVM with ViewModel

Instead of MVP, consider MVVM with ViewModel which handles lifecycle automatically:

```kotlin
class UserViewModel : ViewModel() {

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            // Automatically cancelled when ViewModel is cleared
            val users = repository.getUsers()
            _users.value = users
        }
    }
}

class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.users.observe(this) { users ->
            // Update UI
        }

        viewModel.loadUsers()
    }

    // No manual cleanup needed!
}
```

---

## Ответ (RU)

В архитектуре MVP (Model-View-Presenter), когда Presenter отправляет запросы к View, важно иметь возможность отменять эти запросы. Основные механизмы:

**1. Weak References** - используйте `WeakReference` для избежания утечек памяти, но это не отменяет работу.

**2. Lifecycle-Aware Components** - автоматическое управление жизненным циклом через Android Lifecycle library.

**3. RxJava Disposables** - используйте `CompositeDisposable` для отмены всех подписок:
```kotlin
private val compositeDisposable = CompositeDisposable()
fun onDestroy() {
    compositeDisposable.clear()
}
```

**4. Kotlin Coroutines (рекомендуется)** - используйте `CoroutineScope` с `Job`:
```kotlin
private val presenterScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
fun onDestroy() {
    presenterScope.cancel()
}
```

**5. Boolean Flags** - простой подход с флагом отмены.

**6. Callback Management** - отслеживание и удаление коллбэков.

**Рекомендация:** Используйте **Kotlin Coroutines** для нового кода или **RxJava** если он уже в проекте. Или перейдите на **MVVM с ViewModel**, который автоматически управляет жизненным циклом.


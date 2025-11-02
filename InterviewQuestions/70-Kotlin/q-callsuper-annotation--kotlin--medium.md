---
id: kotlin-197
title: "Callsuper Annotation / Аннотация CallSuper"
aliases: [CallSuper Annotation, Аннотация CallSuper]
topic: kotlin
subtopics: [annotations]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: []
created: 2025-10-15
updated: 2025-10-31
tags: [android, annotations, best-practices, difficulty/medium, kotlin, lifecycle]
date created: Saturday, November 1st 2025, 1:27:05 pm
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Аннотация @CallSuper

# Question (EN)
> What is the @CallSuper annotation and when should you use it?

# Вопрос (RU)
> Что такое аннотация @CallSuper и когда её следует использовать?

---

## Answer (EN)

The `@CallSuper` annotation indicates that when overriding a method in a subclass, the superclass method must be called. This is especially useful for Android lifecycle methods (onCreate, onStart, onDestroy) where missing super calls can lead to serious problems: memory leaks, incorrect component behavior, or app crashes. Android Studio shows lint warnings when super calls are missing.

**English**: The @CallSuper annotation enforces that subclasses must call the superclass method when overriding. This is critical for lifecycle methods (onCreate, onDestroy) in Android where forgetting super calls leads to memory leaks and crashes. Android Studio shows warnings for missing super calls. Use @CallSuper in base classes for initialization, cleanup, and lifecycle methods. Call super first in onCreate and last in onDestroy. Template Method pattern is an alternative that prevents forgetting super calls entirely.

## Ответ (RU)

Аннотация `@CallSuper` указывает, что при переопределении метода в подклассе необходимо обязательно вызывать метод суперкласса. Это особенно полезно при работе с методами жизненного цикла Android (onCreate, onStart, onDestroy), где пропуск вызова super может привести к серьёзным проблемам: утечкам памяти, некорректной работе компонентов или крашам приложения.

### Основы Использования @CallSuper

```kotlin
import androidx.annotation.CallSuper

// Базовый класс с @CallSuper
abstract class BaseActivity : AppCompatActivity() {

    private var isInitialized = false

    @CallSuper
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        isInitialized = true
        Log.d("BaseActivity", "onCreate called")
    }

    @CallSuper
    override fun onDestroy() {
        super.onDestroy()
        isInitialized = false
        Log.d("BaseActivity", "onDestroy called")
    }

    @CallSuper
    open fun initialize() {
        Log.d("BaseActivity", "Initializing base components")
        // Настройка базовых компонентов
    }

    @CallSuper
    open fun cleanup() {
        Log.d("BaseActivity", "Cleaning up base components")
        // Очистка ресурсов
    }
}

// - ХОРОШО: Вызов super в переопределённом методе
class GoodActivity : BaseActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState) // - Вызов super
        setContentView(R.layout.activity_main)
        setupUI()
    }

    override fun initialize() {
        super.initialize() // - Вызов super
        setupAdditionalComponents()
    }

    private fun setupUI() {
        // UI setup
    }

    private fun setupAdditionalComponents() {
        // Additional setup
    }
}

// - ПЛОХО: Пропущен вызов super
class BadActivity : BaseActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        // - ОШИБКА: Нет super.onCreate()
        // Android Studio выдаст предупреждение:
        // "Overriding method should call super.onCreate"
        setContentView(R.layout.activity_main)
    }

    override fun initialize() {
        // - ОШИБКА: Нет super.initialize()
        // Базовая инициализация не будет выполнена
        setupAdditionalComponents()
    }

    private fun setupAdditionalComponents() {
        // Additional setup
    }
}
```

### Зачем Нужна @CallSuper

#### 1. Предотвращение Ошибок Жизненного Цикла

```kotlin
abstract class BaseFragment : Fragment() {

    private val disposables = CompositeDisposable()
    private lateinit var analytics: Analytics

    @CallSuper
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        analytics = Analytics.getInstance(requireContext())
        analytics.logScreenView(this::class.simpleName ?: "Unknown")
    }

    @CallSuper
    override fun onDestroy() {
        super.onDestroy()
        // Критически важная очистка
        disposables.clear()
        analytics.flush()
    }
}

// Если наследник забудет вызвать super.onDestroy():
class LeakyFragment : BaseFragment() {

    override fun onDestroy() {
        // - Нет super.onDestroy()
        // Результат: disposables не очистятся → утечка памяти
        cleanup()
    }

    private fun cleanup() {
        // Local cleanup
    }
}

// - Правильный вариант
class ProperFragment : BaseFragment() {

    override fun onDestroy() {
        super.onDestroy() // - Очистка disposables и analytics
        cleanup()
    }

    private fun cleanup() {
        // Local cleanup
    }
}
```

#### 2. Обеспечение Корректной Инициализации

```kotlin
abstract class BaseViewModel : ViewModel() {

    private var isInitialized = false
    protected val errorHandler = ErrorHandler()

    @CallSuper
    open fun initialize() {
        if (isInitialized) {
            throw IllegalStateException("Already initialized")
        }
        isInitialized = true
        errorHandler.setup()
        Log.d("BaseViewModel", "Base initialization complete")
    }

    @CallSuper
    override fun onCleared() {
        super.onCleared()
        errorHandler.cleanup()
        isInitialized = false
    }

    class ErrorHandler {
        fun setup() {
            Log.d("ErrorHandler", "Setting up error handler")
        }

        fun cleanup() {
            Log.d("ErrorHandler", "Cleaning up error handler")
        }
    }
}

class UserViewModel : BaseViewModel() {

    private val userRepository = UserRepository()

    override fun initialize() {
        super.initialize() // - Критически важно для errorHandler
        loadUsers()
    }

    override fun onCleared() {
        super.onCleared() // - Очищает errorHandler
        userRepository.cleanup()
    }

    private fun loadUsers() {
        // Load user data
    }

    class UserRepository {
        fun cleanup() {
            Log.d("UserRepository", "Cleaning up repository")
        }
    }
}
```

### Практические Примеры

#### Пример 1: RecyclerView Adapter С @CallSuper

```kotlin
abstract class BaseAdapter<T, VH : RecyclerView.ViewHolder> :
    RecyclerView.Adapter<VH>() {

    protected val items = mutableListOf<T>()
    private val itemClickListeners = mutableListOf<(T) -> Unit>()

    @CallSuper
    open fun setItems(newItems: List<T>) {
        val oldSize = items.size
        items.clear()
        items.addAll(newItems)

        if (oldSize == 0 && newItems.isNotEmpty()) {
            notifyItemRangeInserted(0, newItems.size)
        } else if (oldSize > 0 && newItems.isEmpty()) {
            notifyItemRangeRemoved(0, oldSize)
        } else {
            notifyDataSetChanged()
        }
    }

    @CallSuper
    open fun addItem(item: T, position: Int = items.size) {
        items.add(position, item)
        notifyItemInserted(position)
    }

    @CallSuper
    open fun removeItem(position: Int) {
        if (position in items.indices) {
            items.removeAt(position)
            notifyItemRemoved(position)
        }
    }

    @CallSuper
    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = items[position]
        holder.itemView.setOnClickListener {
            itemClickListeners.forEach { listener ->
                listener(item)
            }
        }
    }

    fun addClickListener(listener: (T) -> Unit) {
        itemClickListeners.add(listener)
    }

    override fun getItemCount(): Int = items.size
}

// Использование
class UserAdapter : BaseAdapter<User, UserAdapter.UserViewHolder>() {

    override fun setItems(newItems: List<User>) {
        super.setItems(newItems) // - Важно: обновляет адаптер
        logItemsUpdate(newItems.size)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        super.onBindViewHolder(holder, position) // - Устанавливает click listener
        val user = items[position]
        holder.bind(user)
    }

    private fun logItemsUpdate(size: Int) {
        Log.d("UserAdapter", "Updated with $size items")
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return UserViewHolder(view)
    }

    class UserViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        fun bind(user: User) {
            // Bind user data to view
        }
    }
}

data class User(val id: Int, val name: String)
```

#### Пример 2: Custom View С @CallSuper

```kotlin
abstract class BaseCustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    protected val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    protected var isSetup = false

    @CallSuper
    open fun setup() {
        if (isSetup) return

        paint.style = Paint.Style.FILL
        paint.color = Color.BLACK
        isSetup = true

        Log.d("BaseCustomView", "Base setup complete")
    }

    @CallSuper
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        setup()
    }

    @CallSuper
    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        isSetup = false
    }

    @CallSuper
    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        Log.d("BaseCustomView", "Size changed: ${w}x${h}")
    }
}

class CircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : BaseCustomView(context, attrs, defStyleAttr) {

    private var radius = 0f

    override fun setup() {
        super.setup() // - Инициализирует paint
        paint.color = Color.RED
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh) // - Логирует изменение
        radius = minOf(w, h) / 2f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }
}
```

#### Пример 3: Repository Pattern С @CallSuper

```kotlin
abstract class BaseRepository {

    protected val disposables = CompositeDisposable()
    private var isInitialized = false

    @CallSuper
    open fun initialize() {
        if (isInitialized) {
            Log.w("BaseRepository", "Already initialized")
            return
        }
        isInitialized = true
        Log.d("BaseRepository", "Repository initialized")
    }

    @CallSuper
    open fun cleanup() {
        disposables.clear()
        isInitialized = false
        Log.d("BaseRepository", "Repository cleaned up")
    }

    protected fun <T> observeOnMain(observable: Observable<T>): Observable<T> {
        return observable
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
    }
}

class UserRepository : BaseRepository() {

    private val api = UserApi.create()
    private val cache = mutableMapOf<Int, User>()

    override fun initialize() {
        super.initialize() // - Важно для disposables
        loadInitialData()
    }

    override fun cleanup() {
        super.cleanup() // - Очищает disposables
        cache.clear()
    }

    private fun loadInitialData() {
        val disposable = observeOnMain(api.getUsers())
            .subscribe(
                { users ->
                    users.forEach { cache[it.id] = it }
                },
                { error ->
                    Log.e("UserRepository", "Failed to load users", error)
                }
            )
        disposables.add(disposable)
    }

    // Mock API
    object UserApi {
        fun create(): UserApiInterface = object : UserApiInterface {
            override fun getUsers(): Observable<List<User>> {
                return Observable.just(emptyList())
            }
        }
    }

    interface UserApiInterface {
        fun getUsers(): Observable<List<User>>
    }
}
```

### @CallSuper Vs @Override

```kotlin
// @Override - проверяет что метод переопределён
// @CallSuper - проверяет что вызван super метод

open class Parent {

    // Без аннотаций
    open fun method1() {
        println("Parent method1")
    }

    // С @CallSuper
    @CallSuper
    open fun method2() {
        println("Parent method2")
    }
}

class Child : Parent() {

    // - Переопределение без вызова super - OK для method1
    override fun method1() {
        println("Child method1 - no super call")
    }

    // - ХОРОШО: Вызов super для method2 с @CallSuper
    override fun method2() {
        super.method2() // Обязательно из-за @CallSuper
        println("Child method2")
    }

    // - ПЛОХО: Если забыть super для method2
    // override fun method2() {
    //     println("Child method2 - forgot super!")
    //     // Android Studio предупредит:
    //     // "Overriding method should call super.method2"
    // }
}
```

### Продвинутые Случаи Использования

#### 1. Множественные Уровни Наследования

```kotlin
abstract class Level1Activity : AppCompatActivity() {

    @CallSuper
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Level1", "onCreate")
    }

    @CallSuper
    open fun setupLevel1() {
        Log.d("Level1", "Setup Level 1")
    }
}

abstract class Level2Activity : Level1Activity() {

    @CallSuper
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState) // - Вызывает Level1
        Log.d("Level2", "onCreate")
    }

    @CallSuper
    override fun setupLevel1() {
        super.setupLevel1() // - Вызывает Level1
        Log.d("Level2", "Setup Level 1 from Level 2")
    }

    @CallSuper
    open fun setupLevel2() {
        Log.d("Level2", "Setup Level 2")
    }
}

class ConcreteActivity : Level2Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState) // - Вызывает Level2 → Level1
        Log.d("Concrete", "onCreate")
    }

    override fun setupLevel1() {
        super.setupLevel1() // - Вызывает Level2 → Level1
        Log.d("Concrete", "Setup Level 1 from Concrete")
    }

    override fun setupLevel2() {
        super.setupLevel2() // - Вызывает Level2
        Log.d("Concrete", "Setup Level 2 from Concrete")
    }
}

// Вывод лога при создании ConcreteActivity:
// Level1: onCreate
// Level2: onCreate
// Concrete: onCreate
```

#### 2. Интерфейсы С Default Методами (Java 8+)

```kotlin
// Интерфейс с default методом
interface Trackable {

    @CallSuper
    fun trackEvent(eventName: String) {
        Log.d("Analytics", "Tracking: $eventName")
        // Базовая аналитика
    }
}

class TrackedActivity : AppCompatActivity(), Trackable {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        trackEvent("Activity Created")
    }

    override fun trackEvent(eventName: String) {
        // super.trackEvent(eventName) // WARNING: Не обязательно для интерфейсов
        // Но если забыли, базовая аналитика не выполнится
        Log.d("TrackedActivity", "Custom tracking: $eventName")
    }
}

// Правильная реализация с вызовом super
class ProperTrackedActivity : AppCompatActivity(), Trackable {

    override fun trackEvent(eventName: String) {
        super.trackEvent(eventName) // - Вызывает базовую аналитику
        // Дополнительная кастомная логика
        sendToFirebase(eventName)
    }

    private fun sendToFirebase(eventName: String) {
        Log.d("Firebase", "Sending: $eventName")
    }
}
```

#### 3. Композиция Компонентов С @CallSuper

```kotlin
abstract class BasePresenter<V : BaseView> {

    protected var view: V? = null
    private var isAttached = false

    @CallSuper
    open fun attachView(view: V) {
        if (isAttached) {
            throw IllegalStateException("View already attached")
        }
        this.view = view
        isAttached = true
        Log.d("BasePresenter", "View attached")
    }

    @CallSuper
    open fun detachView() {
        if (!isAttached) {
            Log.w("BasePresenter", "View not attached")
            return
        }
        this.view = null
        isAttached = false
        Log.d("BasePresenter", "View detached")
    }

    protected fun checkViewAttached() {
        if (!isAttached) {
            throw IllegalStateException("View not attached")
        }
    }
}

interface BaseView {
    fun showLoading()
    fun hideLoading()
    fun showError(message: String)
}

class UserPresenter : BasePresenter<UserView>() {

    private val disposables = CompositeDisposable()

    override fun attachView(view: UserView) {
        super.attachView(view) // - Устанавливает isAttached и this.view
        loadUsers()
    }

    override fun detachView() {
        disposables.clear() // Очистка перед detach
        super.detachView() // - Очищает view и isAttached
    }

    private fun loadUsers() {
        checkViewAttached() // Проверка что view прикреплён
        view?.showLoading()
        // Load data...
    }
}

interface UserView : BaseView {
    fun showUsers(users: List<User>)
}
```

### Проверка Во Время Компиляции

```kotlin
// Android Studio и Lint проверяют @CallSuper автоматически

abstract class BaseClass {

    @CallSuper
    open fun requiredMethod() {
        println("Base implementation")
    }
}

class ChildClass : BaseClass() {

    // - Lint warning:
    // "Overriding method should call super.requiredMethod"
    override fun requiredMethod() {
        println("Child implementation - forgot super!")
    }
}

// Для отключения предупреждения (НЕ РЕКОМЕНДУЕТСЯ):
class SuppressedChild : BaseClass() {

    @Suppress("MissingSuperCall")
    override fun requiredMethod() {
        // Предупреждение подавлено, но это опасно!
        println("Suppressed - but dangerous!")
    }
}
```

### Best Practices

1. **Используйте @CallSuper для методов жизненного цикла** в базовых классах Activity, Fragment, ViewModel
2. **Применяйте к методам инициализации и очистки**, где критически важно выполнить базовую логику
3. **Документируйте необходимость вызова super** в KDoc комментариях
4. **Не подавляйте предупреждения** без веской причины
5. **Проверяйте порядок вызовов** - обычно super вызывается первым для onCreate и последним для onDestroy
6. **Используйте в библиотеках**, чтобы пользователи не забывали вызывать базовую логику

### Common Pitfalls

1. **Забыть вызвать super** → утечки памяти, некорректная работа
2. **Вызвать super в неправильном порядке** → может привести к NPE или некорректному состоянию
3. **Подавить предупреждение @Suppress** → скрывает проблему вместо её решения
4. **Не использовать @CallSuper** в базовых классах библиотек → пользователи забудут вызвать super

### Связанные Аннотации

```kotlin
// @CallSuper - требует вызов super
@CallSuper
open fun method1() {}

// @OverrideMustImplement (custom) - метод должен быть переопределён
// (Kotlin использует abstract для этого)
abstract fun method2()

// @RequiresPermission - требует runtime permission
@RequiresPermission(Manifest.permission.CAMERA)
fun openCamera() {}

// @UiThread - метод должен вызываться в UI потоке
@UiThread
fun updateUI() {}

// @WorkerThread - метод должен вызываться в фоновом потоке
@WorkerThread
fun loadData() {}
```

### Альтернативы @CallSuper

```kotlin
// 1. Template Method Pattern
abstract class BaseClass {

    // Final method - нельзя переопределить
    fun execute() {
        beforeExecute()
        doExecute()
        afterExecute()
    }

    // Хуки для переопределения
    protected open fun beforeExecute() {
        Log.d("Base", "Before execute")
    }

    protected abstract fun doExecute()

    protected open fun afterExecute() {
        Log.d("Base", "After execute")
    }
}

class ConcreteClass : BaseClass() {

    override fun doExecute() {
        Log.d("Concrete", "Execute")
    }

    // Опционально переопределить хуки
    override fun beforeExecute() {
        super.beforeExecute()
        Log.d("Concrete", "Before execute")
    }
}

// 2. Композиция вместо наследования
class LifecycleManager {
    private val listeners = mutableListOf<LifecycleListener>()

    fun addListener(listener: LifecycleListener) {
        listeners.add(listener)
    }

    fun onCreate() {
        listeners.forEach { it.onCreate() }
    }

    fun onDestroy() {
        listeners.forEach { it.onDestroy() }
    }
}

interface LifecycleListener {
    fun onCreate()
    fun onDestroy()
}

class MyActivity : AppCompatActivity() {
    private val lifecycleManager = LifecycleManager()

    init {
        lifecycleManager.addListener(object : LifecycleListener {
            override fun onCreate() {
                Log.d("Listener", "onCreate")
            }

            override fun onDestroy() {
                Log.d("Listener", "onDestroy")
            }
        })
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleManager.onCreate()
    }

    override fun onDestroy() {
        lifecycleManager.onDestroy()
        super.onDestroy()
    }
}
```

## Related Questions

- [[q-reified-type-parameters--kotlin--medium]]
- [[q-testing-flow-operators--kotlin--hard]]

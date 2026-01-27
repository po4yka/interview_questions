---
id: android-perf-004
title: Lazy Initialization Patterns / Паттерны Ленивой Инициализации
aliases:
- Lazy Loading
- Lazy Initialization
- Ленивая Инициализация
topic: android
subtopics:
- performance
- initialization
- patterns
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-app-startup-optimization--performance--hard
- q-memory-leaks-detection--performance--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/performance
- android/initialization
- difficulty/medium
- lazy
- patterns
anki_cards:
- slug: android-perf-004-0-en
  language: en
- slug: android-perf-004-0-ru
  language: ru
---
# Вопрос (RU)

> Какие паттерны ленивой инициализации существуют в Android? Как они улучшают производительность?

# Question (EN)

> What lazy initialization patterns exist in Android? How do they improve performance?

---

## Ответ (RU)

**Ленивая инициализация** -- это паттерн, при котором объект создаётся только в момент первого использования, а не при создании родительского объекта. Это улучшает время запуска и снижает потребление памяти.

### Краткий Ответ

- **by lazy** -- Kotlin делегат для thread-safe ленивой инициализации
- **lateinit** -- отложенная инициализация без null checks
- **ViewStub** -- ленивая загрузка layout
- **Dagger/Hilt Lazy<T>** -- ленивая инъекция зависимостей

### Подробный Ответ

### Kotlin `by lazy`

```kotlin
class ExpensiveObject {
    init {
        // Тяжёлая инициализация: 500ms
        Thread.sleep(500)
    }
}

class MyActivity : AppCompatActivity() {

    // Создаётся только при первом обращении
    private val expensiveObject by lazy {
        ExpensiveObject()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // expensiveObject ещё не создан -- быстрый onCreate
    }

    fun onButtonClick() {
        // Первое обращение -- создаётся expensiveObject
        expensiveObject.doSomething()
    }
}
```

### Режимы `lazy`

```kotlin
// Thread-safe (по умолчанию) -- synchronized
private val threadSafe by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
    ExpensiveObject()
}

// Публикация -- несколько потоков могут создать, но используется один
private val publication by lazy(LazyThreadSafetyMode.PUBLICATION) {
    ExpensiveObject()
}

// Не thread-safe -- только один поток
private val notThreadSafe by lazy(LazyThreadSafetyMode.NONE) {
    ExpensiveObject() // Быстрее, но не безопасно
}

// Для main thread использования -- NONE быстрее
private val mainThreadOnly by lazy(LazyThreadSafetyMode.NONE) {
    // Всегда вызывается из main thread
    ViewBinding.inflate(layoutInflater)
}
```

### `lateinit` vs `by lazy`

```kotlin
class MyViewModel : ViewModel() {

    // lateinit -- для mutable, инициализация позже
    lateinit var repository: UserRepository

    // by lazy -- для immutable, инициализация при первом доступе
    private val analytics by lazy { Analytics() }

    fun init(repo: UserRepository) {
        repository = repo // Инициализируем вручную
    }

    fun trackEvent() {
        analytics.track("event") // Инициализируется здесь
    }
}

// Проверка lateinit
if (::repository.isInitialized) {
    repository.loadData()
}
```

### ViewStub для Ленивого Layout

```xml
<!-- activity_main.xml -->
<LinearLayout>
    <TextView android:id="@+id/title" />

    <!-- ViewStub не инфлейтится сразу -->
    <ViewStub
        android:id="@+id/stub_error"
        android:layout="@layout/layout_error"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
</LinearLayout>
```

```kotlin
class MyActivity : AppCompatActivity() {

    private var errorView: View? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // ViewStub не загружен -- быстрый inflate
    }

    fun showError(message: String) {
        // Инфлейтим только когда нужно
        if (errorView == null) {
            val stub = findViewById<ViewStub>(R.id.stub_error)
            errorView = stub.inflate() // Загружаем layout
        }
        errorView?.findViewById<TextView>(R.id.error_message)?.text = message
        errorView?.visibility = View.VISIBLE
    }
}
```

### ViewBinding с Lazy

```kotlin
class MyFragment : Fragment(R.layout.fragment_my) {

    // Ленивое создание binding
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    // Или через делегат
    private val safeBinding by lazy {
        FragmentMyBinding.bind(requireView())
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentMyBinding.bind(view)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Предотвращаем утечку
    }
}
```

### Dagger/Hilt Lazy Injection

```kotlin
@HiltViewModel
class MyViewModel @Inject constructor(
    // Обычная инъекция -- создаётся сразу
    private val userRepository: UserRepository,

    // Lazy инъекция -- создаётся при первом get()
    private val analyticsLazy: Lazy<Analytics>,

    // Provider -- создаёт новый экземпляр каждый раз
    private val loggerProvider: Provider<Logger>
) : ViewModel() {

    fun trackEvent(event: String) {
        // Analytics создаётся здесь
        analyticsLazy.get().track(event)
    }

    fun log(message: String) {
        // Новый Logger каждый раз
        loggerProvider.get().log(message)
    }
}
```

### Lazy Collection Initialization

```kotlin
class DataRepository {

    // Ленивая загрузка данных
    private val usersCache by lazy {
        mutableMapOf<String, User>()
    }

    // Ленивая трансформация
    val activeUsers: List<User> by lazy {
        allUsers.filter { it.isActive }
    }

    // Sequence для ленивой обработки больших коллекций
    fun processLargeList(items: List<Item>): List<Result> {
        return items.asSequence()
            .filter { it.isValid }      // Лениво
            .map { transform(it) }       // Лениво
            .take(100)                   // Останавливается после 100
            .toList()                    // Выполняется здесь
    }
}
```

### Compose Lazy Components

```kotlin
@Composable
fun LazyScreen() {
    // LazyColumn -- ленивая загрузка items
    LazyColumn {
        items(1000) { index ->
            // Композиция только для видимых items
            ExpensiveItem(index)
        }
    }
}

@Composable
fun LazyStateExample() {
    // remember -- создаёт объект только один раз
    val expensiveObject = remember {
        ExpensiveObject()
    }

    // derivedStateOf -- пересчитывает только когда зависимости меняются
    val derivedValue by remember {
        derivedStateOf { expensiveCalculation(state.value) }
    }

    // produceState -- ленивая загрузка с корутинами
    val data by produceState<Data?>(initialValue = null) {
        value = loadData() // Загружается в фоне
    }
}
```

### Ленивая Инициализация Singleton

```kotlin
// Double-checked locking (не нужен в Kotlin)
// Kotlin object уже lazy и thread-safe
object MySingleton {
    val heavyResource by lazy { loadHeavyResource() }
}

// Lazy holder pattern для Java interop
class LazySingleton private constructor() {

    companion object {
        // Thread-safe lazy initialization
        val instance: LazySingleton by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
            LazySingleton()
        }
    }
}
```

### Сравнение Подходов

| Подход | Thread-safe | Nullable | Mutable | Use Case |
|--------|-------------|----------|---------|----------|
| `by lazy` | Да (настраиваемо) | Нет | Нет | Тяжёлые объекты |
| `lateinit` | Нет | Нет | Да | DI, позже инициализация |
| `ViewStub` | N/A | N/A | N/A | Редко используемые layouts |
| `Lazy<T>` (Dagger) | Да | Нет | Нет | DI с отложенным созданием |

### Чеклист Применения

| Ситуация | Решение |
|----------|---------|
| Тяжёлый объект в Activity | `by lazy` |
| ViewBinding во Fragment | nullable + обнуление |
| Редко показываемый UI | ViewStub |
| Опциональная зависимость | `Lazy<T>` в Dagger |
| Большой список | LazyColumn/LazyRow |
| Sequence обработка | `asSequence()` |

---

## Answer (EN)

**Lazy initialization** is a pattern where an object is created only at the moment of first use, not when the parent object is created. This improves startup time and reduces memory consumption.

### Short Answer

- **by lazy** -- Kotlin delegate for thread-safe lazy initialization
- **lateinit** -- deferred initialization without null checks
- **ViewStub** -- lazy layout loading
- **Dagger/Hilt Lazy<T>** -- lazy dependency injection

### Detailed Answer

### Kotlin `by lazy`

```kotlin
class ExpensiveObject {
    init {
        // Heavy initialization: 500ms
        Thread.sleep(500)
    }
}

class MyActivity : AppCompatActivity() {

    // Created only on first access
    private val expensiveObject by lazy {
        ExpensiveObject()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // expensiveObject not created yet -- fast onCreate
    }

    fun onButtonClick() {
        // First access -- expensiveObject created
        expensiveObject.doSomething()
    }
}
```

### `lazy` Modes

```kotlin
// Thread-safe (default) -- synchronized
private val threadSafe by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
    ExpensiveObject()
}

// Publication -- multiple threads may create, but one is used
private val publication by lazy(LazyThreadSafetyMode.PUBLICATION) {
    ExpensiveObject()
}

// Not thread-safe -- single thread only
private val notThreadSafe by lazy(LazyThreadSafetyMode.NONE) {
    ExpensiveObject() // Faster but not safe
}

// For main thread usage -- NONE is faster
private val mainThreadOnly by lazy(LazyThreadSafetyMode.NONE) {
    // Always called from main thread
    ViewBinding.inflate(layoutInflater)
}
```

### `lateinit` vs `by lazy`

```kotlin
class MyViewModel : ViewModel() {

    // lateinit -- for mutable, initialized later
    lateinit var repository: UserRepository

    // by lazy -- for immutable, initialized on first access
    private val analytics by lazy { Analytics() }

    fun init(repo: UserRepository) {
        repository = repo // Initialize manually
    }

    fun trackEvent() {
        analytics.track("event") // Initialized here
    }
}

// Check lateinit
if (::repository.isInitialized) {
    repository.loadData()
}
```

### ViewStub for Lazy Layout

```xml
<!-- activity_main.xml -->
<LinearLayout>
    <TextView android:id="@+id/title" />

    <!-- ViewStub not inflated immediately -->
    <ViewStub
        android:id="@+id/stub_error"
        android:layout="@layout/layout_error"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
</LinearLayout>
```

```kotlin
class MyActivity : AppCompatActivity() {

    private var errorView: View? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // ViewStub not loaded -- fast inflate
    }

    fun showError(message: String) {
        // Inflate only when needed
        if (errorView == null) {
            val stub = findViewById<ViewStub>(R.id.stub_error)
            errorView = stub.inflate() // Load layout
        }
        errorView?.findViewById<TextView>(R.id.error_message)?.text = message
        errorView?.visibility = View.VISIBLE
    }
}
```

### ViewBinding with Lazy

```kotlin
class MyFragment : Fragment(R.layout.fragment_my) {

    // Lazy binding creation
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    // Or via delegate
    private val safeBinding by lazy {
        FragmentMyBinding.bind(requireView())
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentMyBinding.bind(view)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Prevent leak
    }
}
```

### Dagger/Hilt Lazy Injection

```kotlin
@HiltViewModel
class MyViewModel @Inject constructor(
    // Regular injection -- created immediately
    private val userRepository: UserRepository,

    // Lazy injection -- created on first get()
    private val analyticsLazy: Lazy<Analytics>,

    // Provider -- creates new instance each time
    private val loggerProvider: Provider<Logger>
) : ViewModel() {

    fun trackEvent(event: String) {
        // Analytics created here
        analyticsLazy.get().track(event)
    }

    fun log(message: String) {
        // New Logger each time
        loggerProvider.get().log(message)
    }
}
```

### Lazy Collection Initialization

```kotlin
class DataRepository {

    // Lazy data loading
    private val usersCache by lazy {
        mutableMapOf<String, User>()
    }

    // Lazy transformation
    val activeUsers: List<User> by lazy {
        allUsers.filter { it.isActive }
    }

    // Sequence for lazy processing of large collections
    fun processLargeList(items: List<Item>): List<Result> {
        return items.asSequence()
            .filter { it.isValid }      // Lazy
            .map { transform(it) }       // Lazy
            .take(100)                   // Stops after 100
            .toList()                    // Executes here
    }
}
```

### Compose Lazy Components

```kotlin
@Composable
fun LazyScreen() {
    // LazyColumn -- lazy item loading
    LazyColumn {
        items(1000) { index ->
            // Composition only for visible items
            ExpensiveItem(index)
        }
    }
}

@Composable
fun LazyStateExample() {
    // remember -- creates object only once
    val expensiveObject = remember {
        ExpensiveObject()
    }

    // derivedStateOf -- recalculates only when dependencies change
    val derivedValue by remember {
        derivedStateOf { expensiveCalculation(state.value) }
    }

    // produceState -- lazy loading with coroutines
    val data by produceState<Data?>(initialValue = null) {
        value = loadData() // Loads in background
    }
}
```

### Lazy Singleton Initialization

```kotlin
// Double-checked locking (not needed in Kotlin)
// Kotlin object is already lazy and thread-safe
object MySingleton {
    val heavyResource by lazy { loadHeavyResource() }
}

// Lazy holder pattern for Java interop
class LazySingleton private constructor() {

    companion object {
        // Thread-safe lazy initialization
        val instance: LazySingleton by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
            LazySingleton()
        }
    }
}
```

### Approach Comparison

| Approach | Thread-safe | Nullable | Mutable | Use Case |
|----------|-------------|----------|---------|----------|
| `by lazy` | Yes (configurable) | No | No | Heavy objects |
| `lateinit` | No | No | Yes | DI, later initialization |
| `ViewStub` | N/A | N/A | N/A | Rarely used layouts |
| `Lazy<T>` (Dagger) | Yes | No | No | DI with deferred creation |

### Application Checklist

| Situation | Solution |
|-----------|----------|
| Heavy object in Activity | `by lazy` |
| ViewBinding in Fragment | nullable + nullify |
| Rarely shown UI | ViewStub |
| Optional dependency | `Lazy<T>` in Dagger |
| Large list | LazyColumn/LazyRow |
| Sequence processing | `asSequence()` |

---

## Ссылки (RU)

- [Kotlin Lazy](https://kotlinlang.org/docs/delegated-properties.html#lazy-properties)
- [ViewStub](https://developer.android.com/reference/android/view/ViewStub)
- [Dagger Lazy](https://dagger.dev/api/latest/dagger/Lazy.html)

## References (EN)

- [Kotlin Lazy](https://kotlinlang.org/docs/delegated-properties.html#lazy-properties)
- [ViewStub](https://developer.android.com/reference/android/view/ViewStub)
- [Dagger Lazy](https://dagger.dev/api/latest/dagger/Lazy.html)

## Follow-ups (EN)

- What are the performance differences between lazy modes?
- How does `lazy` interact with coroutines?
- When should you use `Provider<T>` vs `Lazy<T>` in Dagger?
- How to implement custom lazy delegate?

## Дополнительные Вопросы (RU)

- Какие различия в производительности между режимами lazy?
- Как `lazy` взаимодействует с корутинами?
- Когда использовать `Provider<T>` vs `Lazy<T>` в Dagger?
- Как реализовать кастомный lazy делегат?

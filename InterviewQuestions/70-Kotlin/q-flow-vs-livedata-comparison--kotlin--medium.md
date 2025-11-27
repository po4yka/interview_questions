---
id: kotlin-144
title: "Flow vs LiveData Comparison / Сравнение Flow и LiveData"
aliases: [Flow vs LiveData Comparison, Kotlin Flow vs LiveData]
topic: kotlin
subtopics: [coroutines, flow, types]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-concepts--kotlin--medium, c-kotlin, q-retry-operators-flow--kotlin--medium, q-testing-flow-operators--kotlin--hard]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium]

date created: Friday, November 7th 2025, 2:49:31 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> В чем разница между Kotlin `Flow` и `LiveData`? Когда следует использовать каждый из них?

# Question (EN)
> What are the differences between Kotlin `Flow` and `LiveData`? When should you use each?

## Ответ (RU)

**`Flow` и `LiveData`** - оба являются реактивными держателями данных, но фундаментально отличаются по дизайну, возможностям и сценариям использования. `Flow` более мощный и гибкий, в то время как `LiveData` проще и учитывает жизненный цикл по умолчанию.

### Основные Различия

| Функция | `LiveData` | `Flow` (`StateFlow`/`SharedFlow`) |
|---------|------------|-----------------------------------|
| **Тип** | Горячий поток (хранит состояние и доставляет активным наблюдателям) | Холодный поток (`Flow`) / Горячий поток (`StateFlow`/`SharedFlow`) |
| **Учет Жизненного Цикла** | Да, встроенный | Нет, требует явного учета (например, `repeatOnLifecycle`) |
| **Платформа** | Специфичен для Android (AndroidX) | Платформо-независимый (часть Kotlin coroutines) |
| **Операторы** | Ограниченные (map, switchMap и т.д.) | Богатые (много операторов трансформации и комбинирования) |
| **Потоки** | Обновления наблюдаются на Main потоке | Настраиваемый через dispatchers |
| **Backpressure** | Нет специальных операторов | Есть операторы для управления скоростью (buffer, conflate и т.д.) |
| **Начальное Значение** | Необязательно | `StateFlow` требует, `Flow` нет |
| **Null-безопасность** | Разрешает null | Типобезопасен: null недопустим для не-null типов, для null нужен nullable тип |
| **Multicast** | Да | `StateFlow`/`SharedFlow` да, `Flow` нет |
| **Тестирование** | Часто требует InstantTaskExecutorRule | Удобно с TestDispatcher и coroutines test API |

### Горячие Vs Холодные Потоки

**`LiveData` (Горячий Поток)**:
```kotlin
// Источник обновляет LiveData независимо от наличия наблюдателей
class UserViewModel : ViewModel() {
    val currentTime = MutableLiveData<Long>()

    init {
        // Стартует сразу, работает пока жив ViewModelScope, даже с 0 наблюдателями
        viewModelScope.launch {
            while (true) {
                delay(1000)
                currentTime.value = System.currentTimeMillis()
            }
        }
    }
}
```

**`Flow` (Холодный Поток)**:
```kotlin
// Flow ленивый - производит значения только при сборе
class UserViewModel : ViewModel() {
    val currentTime: Flow<Long> = flow {
        while (true) {
            delay(1000)
            emit(System.currentTimeMillis())
        }
    } // Еще не запущен!

    // Стартует ТОЛЬКО при сборе в каком-либо CoroutineScope
}

// В Activity
lifecycleScope.launch {
    viewModel.currentTime.collect { time ->
        // Flow начинает производить значения СЕЙЧАС, пока активен этот scope
    }
}
```

**`StateFlow` (Горячий Поток)**:
```kotlin
// StateFlow горячий для потребителей - хранит текущее значение и немедленно раздает его подписчикам
class UserViewModel : ViewModel() {
    private val _currentTime = MutableStateFlow(0L)
    val currentTime: StateFlow<Long> = _currentTime

    init {
        // Производитель значений контролируется scope (viewModelScope)
        viewModelScope.launch {
            while (true) {
                delay(1000)
                _currentTime.value = System.currentTimeMillis()
            }
        }
    }
}
```

### Учет Жизненного Цикла

**`LiveData` - Встроенный Учет Жизненного Цикла**:
```kotlin
// LiveData автоматически доставляет значения только активным наблюдателям
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Наблюдатель будет получать обновления только когда lifecycle в STARTED или RESUMED
        viewModel.userData.observe(this) { user ->
            updateUI(user)
        }
    }
}
```

**`Flow` - Требуется Ручная Обработка Жизненного Цикла**:
```kotlin
// ПЛОХО: Flow сам по себе не останавливается при смене состояния lifecycle
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Будет продолжать собирать, пока scope не отменён
            viewModel.userData.collect { user ->
                updateUI(user)
            }
        }
    }
}

// ХОРОШО: Используйте repeatOnLifecycle
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Сбор приостанавливается, когда lifecycle < STARTED
                viewModel.userData.collect { user ->
                    updateUI(user)
                }
            }
        }
    }
}
```

### Операторы И Трансформации

**`LiveData` - Ограниченные операторы**:
```kotlin
class UserViewModel : ViewModel() {
    val userId = MutableLiveData<String>()

    // Ограниченные операторы
    val userData = userId.switchMap { id ->
        liveData {
            emit(repository.getUser(id))
        }
    }

    val userName = userData.map { it.name }

    // Нет debounce, filter, combine и т.д. из коробки
}
```

**`Flow` - Богатый набор операторов**:
```kotlin
class UserViewModel : ViewModel() {
    val userId = MutableStateFlow("")

    val userData = userId
        .debounce(300)              // Ждать паузы в наборе текста
        .filter { it.isNotBlank() } // Пропустить пустые ID
        .distinctUntilChanged()     // Предотвратить дублирующие запросы
        .flatMapLatest { id ->      // Отменить предыдущий запрос
            repository.getUserFlow(id)
        }
        .catch { e ->               // Обработка ошибок
            emit(User.EMPTY)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = User.EMPTY
        )
}
```

### Модель Потоков

**`LiveData` - Main поток по умолчанию**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun loadUser() {
        viewModelScope.launch(Dispatchers.IO) {
            val user = repository.getUser()

            // Нужно вручную переключиться на Main поток перед value
            withContext(Dispatchers.Main) {
                _userData.value = user
            }

            // Или использовать postValue (может объединять быстрые обновления)
            _userData.postValue(user)
        }
    }
}
```

**`Flow` - Гибкие потоки**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = withContext(Dispatchers.IO) {
                repository.getUser()
            }

            // Можно обновлять из любого dispatcher, учитывая thread-safety
            _userData.value = user
        }
    }

    // Или использовать flowOn для изменения контекста upstream
    val userDataFlow: Flow<User> = flow {
        emit(repository.getUser())
    }.flowOn(Dispatchers.IO) // Запускается на IO dispatcher
}
```

### Комбинирование Нескольких Потоков

**`LiveData` - MediatorLiveData**:
```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableLiveData<String>()
    val userAge = MutableLiveData<Int>()

    // Многословное комбинирование
    val userDisplay = MediatorLiveData<String>().apply {
        var name: String? = null
        var age: Int? = null

        addSource(userName) { newName ->
            name = newName
            value = "$name, $age лет"
        }

        addSource(userAge) { newAge ->
            age = newAge
            value = "$name, $age лет"
        }
    }
}
```

**`Flow` - оператор combine()**:
```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableStateFlow("")
    val userAge = MutableStateFlow(0)

    // Лаконичное комбинирование
    val userDisplay: StateFlow<String> = combine(
        userName,
        userAge
    ) { name, age ->
        "$name, $age лет"
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = ""
    )
}
```

### Null-безопасность

**`LiveData` - Разрешает Null**:
```kotlin
// LiveData может хранить null значения
val userData: LiveData<User?> = MutableLiveData(null)
userData.value = null // OK
```

**`StateFlow` - Типобезопасность**:
```kotlin
// Для разрешения null нужно явно указать nullable тип
val userData: StateFlow<User?> = MutableStateFlow(null)

// Для non-null типов
val count: MutableStateFlow<Int> = MutableStateFlow(0) // Не может быть null по типу
// count.value = null // Ошибка компиляции, т.к. Int не nullable
```

### Тестирование

**`LiveData` - Требуется настройка**:
```kotlin
class UserViewModelTest {
    // Требуется для тестирования LiveData
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    @Test
    fun `load user updates LiveData`() {
        val viewModel = UserViewModel(fakeRepository)

        // Нужен тестовый observer
        val observer = Observer<User> {}
        viewModel.userData.observeForever(observer)

        viewModel.loadUser()

        assertEquals("John", viewModel.userData.value?.name)

        viewModel.userData.removeObserver(observer)
    }
}
```

**`Flow` - Более простое тестирование**:
```kotlin
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates StateFlow`() = runTest {
        val viewModel = UserViewModel(fakeRepository)

        viewModel.loadUser()

        assertEquals("John", viewModel.userData.value?.name)
    }

    @Test
    fun `user data flow emits correct values`() = runTest {
        val viewModel = UserViewModel(fakeRepository)
        val emissions = mutableListOf<User>()

        val job = launch {
            viewModel.userData.toList(emissions)
        }

        viewModel.loadUser()
        advanceUntilIdle()

        assertEquals(2, emissions.size)
        assertEquals("John", emissions[1].name)

        job.cancel()
    }
}
```

### Когда Использовать Каждый

**Используйте `LiveData` когда**:
- Простое управление UI состоянием
- Работаете с legacy Android кодовой базой (уже используется `LiveData`)
- Нужен учет жизненного цикла с минимальным boilerplate
- Команда не знакома с `Flow`/корутинами
- Простой паттерн observe-and-update

**Используйте `Flow`/`StateFlow` когда**:
- Сложные трансформации данных (нужны операторы)
- Слой репозитория (платформо-независимый)
- Нужна обработка различий скоростей (buffer/conflate и т.д.)
- Комбинирование множественных потоков данных
- Современная Kotlin-first кодовая база
- Продвинутые use cases (debouncing, retry логика и т.д.)
- Мультиплатформенные проекты (KMM)

### Паттерн Миграции: `LiveData` → `Flow`

**До (`LiveData`)**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }
}

// В Activity
viewModel.userData.observe(this) { user ->
    updateUI(user)
}
```

**После (`StateFlow`)**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }
}

// В Activity
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.userData.collect { user ->
            updateUI(user)
        }
    }
}
```

### Взаимодействие

**`LiveData` → `Flow`**:
```kotlin
// Конвертация LiveData в Flow
val userDataFlow: Flow<User> = userData.asFlow()
```

**`Flow` → `LiveData`**:
```kotlin
// Конвертация Flow в LiveData (для legacy кода)
val userDataLiveData: LiveData<User> = userDataFlow.asLiveData()
```

### Резюме

**`LiveData`**:
- Простой, специфичный для Android
- Встроенный учет жизненного цикла
- Легко изучить
- Ограниченные операторы
- Только для Android
- Менее мощный

**`Flow`/`StateFlow`**:
- Мощный, гибкий
- Богатый набор операторов
- Платформо-независимый
- Улучшенная тестируемость
- Требует явного учета жизненного цикла при работе в Android UI
- Более крутая кривая обучения

**Современная Рекомендация**: В современных Android-приложениях с корутинами чаще предпочтительнее `StateFlow`/`SharedFlow` для новых фич и слоев данных, при этом `LiveData` может оставаться в слое UI или legacy-коде.

---

## Answer (EN)

**`Flow` and `LiveData`** are both reactive data holders, but they differ fundamentally in design, capabilities, and use cases. `Flow` is more powerful and flexible, while `LiveData` is simpler and lifecycle-aware by default.

### Core Differences

| Feature | `LiveData` | `Flow` (`StateFlow`/`SharedFlow`) |
|---------|------------|-----------------------------------|
| **Type** | Hot stream (holds state, delivers to active observers) | Cold stream (`Flow`) / Hot stream (`StateFlow`/`SharedFlow`) |
| **Lifecycle Aware** | Yes, built-in | No, requires explicit handling (e.g., `repeatOnLifecycle`) |
| **Platform** | Android-specific (AndroidX library, primarily for Android) | Platform-agnostic (part of Kotlin coroutines) |
| **Operators** | Limited (map, switchMap, etc.) | Rich set of transformation/combination operators |
| **Threading** | Observers receive updates on Main thread | Configurable with dispatchers |
| **Backpressure** | No dedicated operators | Has tools for rate handling (buffer, conflate, etc.) |
| **Initial Value** | Optional | Required for `StateFlow`, not for `Flow` |
| **Null Safety** | Allows null values | Type-safe: non-null types can't be null; use nullable type for null |
| **Multicast** | Yes | `StateFlow`/`SharedFlow` yes, `Flow` no |
| **Testing** | Often requires InstantTaskExecutorRule | Convenient with TestDispatcher and coroutines test API |

### Hot Vs Cold Streams

**`LiveData` (Hot Stream)**:
```kotlin
// A producer updates LiveData regardless of observers
class UserViewModel : ViewModel() {
    val currentTime = MutableLiveData<Long>()

    init {
        // Starts immediately and runs while ViewModelScope is active, even with 0 observers
        viewModelScope.launch {
            while (true) {
                delay(1000)
                currentTime.value = System.currentTimeMillis()
            }
        }
    }
}
```

**`Flow` (Cold Stream)**:
```kotlin
// Flow is lazy - only produces values when collected
class UserViewModel : ViewModel() {
    val currentTime: Flow<Long> = flow {
        while (true) {
            delay(1000)
            emit(System.currentTimeMillis())
        }
    } // Not running yet!

    // Starts ONLY when collected in some CoroutineScope
}

// In Activity
lifecycleScope.launch {
    viewModel.currentTime.collect { time ->
        // Flow starts producing values NOW while this scope is active
    }
}
```

**`StateFlow` (Hot Stream)**:
```kotlin
// StateFlow is hot for consumers - it holds the latest value and immediately replays it to new collectors
class UserViewModel : ViewModel() {
    private val _currentTime = MutableStateFlow(0L)
    val currentTime: StateFlow<Long> = _currentTime

    init {
        // The producer is controlled by viewModelScope
        viewModelScope.launch {
            while (true) {
                delay(1000)
                _currentTime.value = System.currentTimeMillis()
            }
        }
    }
}
```

### Lifecycle Awareness

**`LiveData` - Built-in Lifecycle Awareness**:
```kotlin
// LiveData automatically delivers values only to active observers
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Observer receives updates only when lifecycle is STARTED or RESUMED
        viewModel.userData.observe(this) { user ->
            updateUI(user)
        }
    }
}
```

**`Flow` - Manual Lifecycle Handling Required**:
```kotlin
// BAD: Flow does not stop automatically with lifecycle state changes
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Keeps collecting until this scope is cancelled
            viewModel.userData.collect { user ->
                updateUI(user)
            }
        }
    }
}

// GOOD: Use repeatOnLifecycle
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Collection is paused when lifecycle < STARTED
                viewModel.userData.collect { user ->
                    updateUI(user)
                }
            }
        }
    }
}
```

### Operators and Transformations

**`LiveData` - Limited Operators**:
```kotlin
class UserViewModel : ViewModel() {
    val userId = MutableLiveData<String>()

    // Limited operators
    val userData = userId.switchMap { id ->
        liveData {
            emit(repository.getUser(id))
        }
    }

    val userName = userData.map { it.name }

    // No debounce, filter, combine, etc. out of the box
}
```

**`Flow` - Rich Operator `Set`**:
```kotlin
class UserViewModel : ViewModel() {
    val userId = MutableStateFlow("")

    val userData = userId
        .debounce(300)              // Wait for typing pause
        .filter { it.isNotBlank() } // Skip empty IDs
        .distinctUntilChanged()     // Prevent duplicate requests
        .flatMapLatest { id ->      // Cancel previous request
            repository.getUserFlow(id)
        }
        .catch { e ->               // Error handling
            emit(User.EMPTY)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = User.EMPTY
        )
}
```

### Threading Model

**`LiveData` - Main Thread Default**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun loadUser() {
        viewModelScope.launch(Dispatchers.IO) {
            val user = repository.getUser()

            // Must switch to Main thread for setting value
            withContext(Dispatchers.Main) {
                _userData.value = user
            }

            // Or use postValue (may coalesce rapid updates)
            _userData.postValue(user)
        }
    }
}
```

**`Flow` - Flexible Threading**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = withContext(Dispatchers.IO) {
                repository.getUser()
            }

            // Can update from any dispatcher, respecting thread-safety
            _userData.value = user
        }
    }

    // Or use flowOn to move upstream work to another dispatcher
    val userDataFlow: Flow<User> = flow {
        emit(repository.getUser())
    }.flowOn(Dispatchers.IO) // Runs on IO dispatcher
}
```

### Combining Multiple Streams

**`LiveData` - MediatorLiveData**:
```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableLiveData<String>()
    val userAge = MutableLiveData<Int>()

    // Verbose combination
    val userDisplay = MediatorLiveData<String>().apply {
        var name: String? = null
        var age: Int? = null

        addSource(userName) { newName ->
            name = newName
            value = "$name, $age years old"
        }

        addSource(userAge) { newAge ->
            age = newAge
            value = "$name, $age years old"
        }
    }
}
```

**`Flow` - combine() Operator**:
```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableStateFlow("")
    val userAge = MutableStateFlow(0)

    // Concise combination
    val userDisplay: StateFlow<String> = combine(
        userName,
        userAge
    ) { name, age ->
        "$name, $age years old"
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = ""
    )
}
```

### Null Safety

**`LiveData` - Allows Null**:
```kotlin
// LiveData can hold null values
val userData: LiveData<User?> = MutableLiveData(null)
userData.value = null // OK
```

**`StateFlow` - Type-safe**:
```kotlin
// To allow null, declare a nullable type explicitly
val userData: StateFlow<User?> = MutableStateFlow(null)

// For non-null types
val count: MutableStateFlow<Int> = MutableStateFlow(0) // Cannot be null by type
// count.value = null // Compile error because Int is not nullable
```

### Testing

**`LiveData` - Requires Setup**:
```kotlin
class UserViewModelTest {
    // Required for LiveData testing
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    @Test
    fun `load user updates LiveData`() {
        val viewModel = UserViewModel(fakeRepository)

        // Need test observer
        val observer = Observer<User> {}
        viewModel.userData.observeForever(observer)

        viewModel.loadUser()

        assertEquals("John", viewModel.userData.value?.name)

        viewModel.userData.removeObserver(observer)
    }
}
```

**`Flow` - Simpler Testing**:
```kotlin
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `load user updates StateFlow`() = runTest {
        val viewModel = UserViewModel(fakeRepository)

        viewModel.loadUser()

        assertEquals("John", viewModel.userData.value?.name)
    }

    @Test
    fun `user data flow emits correct values`() = runTest {
        val viewModel = UserViewModel(fakeRepository)
        val emissions = mutableListOf<User>()

        val job = launch {
            viewModel.userData.toList(emissions)
        }

        viewModel.loadUser()
        advanceUntilIdle()

        assertEquals(2, emissions.size)
        assertEquals("John", emissions[1].name)

        job.cancel()
    }
}
```

### When to Use Each

**Use `LiveData` When**:
- Simple UI state management
- Working in a legacy Android codebase (already using `LiveData`)
- You need lifecycle awareness with minimal boilerplate
- Team is unfamiliar with `Flow`/coroutines
- Simple observe-and-update pattern

**Use `Flow`/`StateFlow` When**:
- Complex data transformations (operators needed)
- Repository layer (platform-agnostic)
- Need to handle producer/consumer speed differences (buffer/conflate, etc.)
- Combining multiple data streams
- Modern Kotlin-first codebase
- Advanced use cases (debouncing, retry logic, etc.)
- Multi-platform projects (KMM)

### Migration Pattern: `LiveData` → `Flow`

**Before (`LiveData`)**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }
}

// In Activity
viewModel.userData.observe(this) { user ->
    updateUI(user)
}
```

**After (`StateFlow`)**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }
}

// In Activity
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.userData.collect { user ->
            updateUI(user)
        }
    }
}
```

### Interoperability

**`LiveData` → `Flow`**:
```kotlin
// Convert LiveData to Flow
val userDataFlow: Flow<User> = userData.asFlow()
```

**`Flow` → `LiveData`**:
```kotlin
// Convert Flow to LiveData (for legacy code)
val userDataLiveData: LiveData<User> = userDataFlow.asLiveData()
```

### Summary

**`LiveData`**:
- Simple, Android-specific
- Built-in lifecycle awareness
- Easy to learn
- Limited operators
- Android-only
- Less powerful

**`Flow`/`StateFlow`**:
- Powerful, flexible
- Rich operator set
- Platform-agnostic
- Better testability
- Requires explicit lifecycle handling when used with Android UI
- Steeper learning curve

**Modern Recommendation**: In modern Android apps using coroutines, prefer `StateFlow`/`SharedFlow` for new features and data layers, while keeping `LiveData` where it already fits well (e.g., existing UI or legacy code).

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java-подходов к реактивности?
- Когда бы вы использовали это на практике в реальном Android-приложении?
- Какие распространенные ошибки и подводные камни стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [`StateFlow` и `SharedFlow` - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Миграция с `LiveData` на Kotlin `Flow` - Android Developers](https://developer.android.com/codelabs/android-flow)
- [Обзор `LiveData` - Android Developers](https://developer.android.com/topic/libraries/architecture/livedata)
- [[c-kotlin]]

## References

- [`StateFlow` and `SharedFlow` - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Migrate from `LiveData` to Kotlin `Flow` - Android Developers](https://developer.android.com/codelabs/android-flow)
- [`LiveData` Overview - Android Developers](https://developer.android.com/topic/libraries/architecture/livedata)
- [[c-kotlin]]

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF

---

## Связанные Вопросы (RU)

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] - Обзор и введение в Kotlin `Flow`

### Похожие (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Горячие и холодные потоки
- [[q-cold-vs-hot-flows--kotlin--medium]] - Сравнение холодных и горячих потоков
- [[q-channels-vs-flow--kotlin--medium]] - Сравнение каналов и `Flow`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` против `StateFlow`
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - Отличия `StateFlow` и `SharedFlow`

### Продвинутые (Сложнее)
- [[q-flowon-operator-context-switching--kotlin--hard]] - `flowOn` и переключение контекстов
- [[q-flow-backpressure-strategies--kotlin--hard]] - Стратегии backpressure в `Flow`

## Related Questions

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs `Flow`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - `StateFlow` & `SharedFlow` differences

### Advanced (Harder)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies

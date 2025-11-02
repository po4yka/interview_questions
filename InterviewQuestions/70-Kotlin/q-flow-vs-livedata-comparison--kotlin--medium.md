---
id: kotlin-144
title: "Flow vs LiveData Comparison / Сравнение Flow и LiveData"
aliases: [Flow, Vs, Livedata, Comparison]
topic: kotlin
subtopics: []
question_kind: theory
difficulty: medium
original_language: en
language_tags: []
status: draft
moc: moc-kotlin
related: [q-testing-flow-operators--kotlin--hard, q-retry-operators-flow--kotlin--medium, q-executor-service-java--java--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Question (EN)
> What are the differences between Kotlin Flow and LiveData? When should you use each?
# Вопрос (RU)
> В чем разница между Kotlin Flow и LiveData? Когда следует использовать каждый из них?

---

## Answer (EN)

**Flow and LiveData** are both reactive data holders, but they differ fundamentally in design, capabilities, and use cases. Flow is more powerful and flexible, while LiveData is simpler and lifecycle-aware by default.

### Core Differences

| Feature | LiveData | Flow (StateFlow/SharedFlow) |
|---------|----------|----------------------------|
| **Type** | Hot stream (always active) | Cold stream (Flow) / Hot stream (StateFlow/SharedFlow) |
| **Lifecycle Aware** | Yes, built-in | No, requires `repeatOnLifecycle` |
| **Platform** | Android-specific | Platform-agnostic (Kotlin) |
| **Operators** | Limited (map, switchMap, etc.) | Rich (100+ operators) |
| **Threading** | Main thread by default | Configurable with dispatchers |
| **Backpressure** | No | Yes (buffer, conflate, etc.) |
| **Initial Value** | Optional | StateFlow requires, Flow doesn't |
| **Null Safety** | Allows null values | StateFlow doesn't allow null |
| **Multicast** | Yes | StateFlow/SharedFlow yes, Flow no |
| **Testing** | Requires InstantTaskExecutorRule | Easy with TestDispatcher |

### Hot vs Cold Streams

**LiveData (Hot Stream)**:
```kotlin
// LiveData is always active - produces values even without observers
class UserViewModel : ViewModel() {
    val currentTime = MutableLiveData<Long>()

    init {
        // Starts immediately, runs even with 0 observers
        viewModelScope.launch {
            while (true) {
                delay(1000)
                currentTime.value = System.currentTimeMillis()
            }
        }
    }
}
```

**Flow (Cold Stream)**:
```kotlin
// Flow is lazy - only produces values when collected
class UserViewModel : ViewModel() {
    val currentTime: Flow<Long> = flow {
        while (true) {
            delay(1000)
            emit(System.currentTimeMillis())
        }
    } // Not running yet!

    // Starts ONLY when collected
}

// In Activity
lifecycleScope.launch {
    viewModel.currentTime.collect { time ->
        // Flow starts producing values NOW
    }
}
```

**StateFlow (Hot Stream)**:
```kotlin
// StateFlow is hot - but better than LiveData
class UserViewModel : ViewModel() {
    private val _currentTime = MutableStateFlow(0L)
    val currentTime: StateFlow<Long> = _currentTime

    init {
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

**LiveData - Built-in Lifecycle Awareness**:
```kotlin
// LiveData automatically stops when lifecycle is not active
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Automatically paused when app goes to background
        viewModel.userData.observe(this) { user ->
            updateUI(user) // Safe - only called when STARTED
        }
    }
}
```

**Flow - Manual Lifecycle Handling Required**:
```kotlin
// BAD: Flow doesn't respect lifecycle automatically
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Keeps collecting even in background!
            viewModel.userData.collect { user ->
                updateUI(user) // Can crash if app is in background
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
                // Pauses collection when app goes to background
                viewModel.userData.collect { user ->
                    updateUI(user) // Safe!
                }
            }
        }
    }
}
```

### Operators and Transformations

**LiveData - Limited Operators**:
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

**Flow - Rich Operator Set**:
```kotlin
class UserViewModel : ViewModel() {
    val userId = MutableStateFlow("")

    val userData = userId
        .debounce(300)           // Wait for typing pause
        .filter { it.isNotBlank() } // Skip empty IDs
        .distinctUntilChanged()  // Prevent duplicate requests
        .flatMapLatest { id ->   // Cancel previous request
            repository.getUserFlow(id)
        }
        .catch { e ->            // Error handling
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

**LiveData - Main Thread Default**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun loadUser() {
        viewModelScope.launch(Dispatchers.IO) {
            val user = repository.getUser()

            // Must switch to Main thread manually
            withContext(Dispatchers.Main) {
                _userData.value = user
            }

            // Or use postValue (can lose updates)
            _userData.postValue(user)
        }
    }
}
```

**Flow - Flexible Threading**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = withContext(Dispatchers.IO) {
                repository.getUser()
            }

            // Can emit from any dispatcher
            _userData.value = user
        }
    }

    // Or use flowOn
    val userDataFlow: Flow<User> = flow {
        emit(repository.getUser())
    }.flowOn(Dispatchers.IO) // Runs on IO dispatcher
}
```

### Combining Multiple Streams

**LiveData - MediatorLiveData**:
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

**Flow - combine() Operator**:
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

**LiveData - Allows Null**:
```kotlin
// LiveData can hold null values
val userData: LiveData<User?> = MutableLiveData(null)
userData.value = null // OK
```

**StateFlow - No Null (by design)**:
```kotlin
// StateFlow cannot hold null (must use nullable type explicitly)
val userData: StateFlow<User?> = MutableStateFlow(null) // Must specify nullable

// For non-null types
val count: MutableStateFlow<Int> = MutableStateFlow(0) // Cannot be null
count.value = null // Compile error!
```

### Testing

**LiveData - Requires Setup**:
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

**Flow - Simpler Testing**:
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

**Use LiveData When**:
- Simple UI state management
- Working in legacy Android codebase (already using LiveData)
- You need lifecycle awareness with minimal boilerplate
- Team is unfamiliar with Flow/coroutines
- Simple observe-and-update pattern

**Use Flow/StateFlow When**:
- Complex data transformations (operators needed)
- Repository layer (platform-agnostic)
- Need backpressure handling
- Combining multiple data streams
- Modern Kotlin-first codebase
- Advanced use cases (debouncing, retry logic, etc.)
- Multi-platform projects (KMM)

### Migration Pattern: LiveData → Flow

**Before (LiveData)**:
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

**After (StateFlow)**:
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

**LiveData → Flow**:
```kotlin
// Convert LiveData to Flow
val userDataFlow: Flow<User> = userData.asFlow()
```

**Flow → LiveData**:
```kotlin
// Convert Flow to LiveData (for legacy code)
val userDataLiveData: LiveData<User> = userDataFlow.asLiveData()
```

### Summary

**LiveData**:
- Simple, Android-specific
- Built-in lifecycle awareness
- Easy to learn
- Limited operators
- Android-only
- Less powerful

**Flow/StateFlow**:
- Powerful, flexible
- Rich operator set
- Platform-agnostic
- Better testing
- Requires manual lifecycle handling
- Steeper learning curve

**Modern Recommendation**: Use **StateFlow/SharedFlow** for new projects, migrate from LiveData when adding complex features or working on repository layer.

---

## Ответ (RU)

**Flow и LiveData** - оба являются реактивными держателями данных, но фундаментально отличаются по дизайну, возможностям и сценариям использования. Flow более мощный и гибкий, в то время как LiveData проще и учитывает жизненный цикл по умолчанию.

### Основные Различия

| Функция | LiveData | Flow (StateFlow/SharedFlow) |
|---------|----------|----------------------------|
| **Тип** | Горячий поток (всегда активен) | Холодный поток (Flow) / Горячий поток (StateFlow/SharedFlow) |
| **Учет Жизненного Цикла** | Да, встроенный | Нет, требует `repeatOnLifecycle` |
| **Платформа** | Специфичен для Android | Платформо-независимый (Kotlin) |
| **Операторы** | Ограниченные (map, switchMap и т.д.) | Богатые (100+ операторов) |
| **Потоки** | Main поток по умолчанию | Настраиваемый через dispatchers |
| **Backpressure** | Нет | Да (buffer, conflate и т.д.) |
| **Начальное Значение** | Опционально | StateFlow требует, Flow нет |
| **Null-безопасность** | Разрешает null | StateFlow не разрешает null |
| **Multicast** | Да | StateFlow/SharedFlow да, Flow нет |
| **Тестирование** | Требует InstantTaskExecutorRule | Легко с TestDispatcher |

### Горячие vs Холодные Потоки

**LiveData (Горячий Поток)**:
```kotlin
// LiveData всегда активен - производит значения даже без наблюдателей
class UserViewModel : ViewModel() {
    val currentTime = MutableLiveData<Long>()

    init {
        // Стартует сразу, работает даже с 0 наблюдателями
        viewModelScope.launch {
            while (true) {
                delay(1000)
                currentTime.value = System.currentTimeMillis()
            }
        }
    }
}
```

**Flow (Холодный Поток)**:
```kotlin
// Flow ленивый - производит значения только при сборе
class UserViewModel : ViewModel() {
    val currentTime: Flow<Long> = flow {
        while (true) {
            delay(1000)
            emit(System.currentTimeMillis())
        }
    } // Еще не запущен!

    // Стартует ТОЛЬКО при сборе
}

// В Activity
lifecycleScope.launch {
    viewModel.currentTime.collect { time ->
        // Flow начинает производить значения СЕЙЧАС
    }
}
```

### Учет Жизненного Цикла

**LiveData - Встроенный Учет Жизненного Цикла**:
```kotlin
// LiveData автоматически останавливается когда lifecycle неактивен
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Автоматически приостанавливается когда приложение уходит в фон
        viewModel.userData.observe(this) { user ->
            updateUI(user) // Безопасно - вызывается только когда STARTED
        }
    }
}
```

**Flow - Требуется Ручная Обработка Жизненного Цикла**:
```kotlin
// ПЛОХО: Flow не учитывает lifecycle автоматически
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Продолжает собирать даже в фоне!
            viewModel.userData.collect { user ->
                updateUI(user) // Может крэшнуться если приложение в фоне
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
                // Приостанавливает сбор когда приложение уходит в фон
                viewModel.userData.collect { user ->
                    updateUI(user) // Безопасно!
                }
            }
        }
    }
}
```

**StateFlow (Горячий Поток)**:
```kotlin
// StateFlow горячий - но лучше чем LiveData
class UserViewModel : ViewModel() {
    private val _currentTime = MutableStateFlow(0L)
    val currentTime: StateFlow<Long> = _currentTime

    init {
        viewModelScope.launch {
            while (true) {
                delay(1000)
                _currentTime.value = System.currentTimeMillis()
            }
        }
    }
}
```

### Операторы и трансформации

**LiveData - Ограниченные операторы**:
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

**Flow - Богатый набор операторов**:
```kotlin
class UserViewModel : ViewModel() {
    val userId = MutableStateFlow("")

    val userData = userId
        .debounce(300)           // Ждать паузы в наборе текста
        .filter { it.isNotBlank() } // Пропустить пустые ID
        .distinctUntilChanged()  // Предотвратить дублирующие запросы
        .flatMapLatest { id ->   // Отменить предыдущий запрос
            repository.getUserFlow(id)
        }
        .catch { e ->            // Обработка ошибок
            emit(User.EMPTY)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = User.EMPTY
        )
}
```

### Модель потоков

**LiveData - Main поток по умолчанию**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun loadUser() {
        viewModelScope.launch(Dispatchers.IO) {
            val user = repository.getUser()

            // Нужно вручную переключиться на Main поток
            withContext(Dispatchers.Main) {
                _userData.value = user
            }

            // Или использовать postValue (может потерять обновления)
            _userData.postValue(user)
        }
    }
}
```

**Flow - Гибкие потоки**:
```kotlin
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = withContext(Dispatchers.IO) {
                repository.getUser()
            }

            // Можно emit из любого dispatcher
            _userData.value = user
        }
    }

    // Или использовать flowOn
    val userDataFlow: Flow<User> = flow {
        emit(repository.getUser())
    }.flowOn(Dispatchers.IO) // Запускается на IO dispatcher
}
```

### Комбинирование нескольких потоков

**LiveData - MediatorLiveData**:
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

**Flow - оператор combine()**:
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

**LiveData - Разрешает Null**:
```kotlin
// LiveData может хранить null значения
val userData: LiveData<User?> = MutableLiveData(null)
userData.value = null // OK
```

**StateFlow - Нет Null (по дизайну)**:
```kotlin
// StateFlow не может хранить null (нужно явно указать nullable тип)
val userData: StateFlow<User?> = MutableStateFlow(null) // Должен указать nullable

// Для non-null типов
val count: MutableStateFlow<Int> = MutableStateFlow(0) // Не может быть null
count.value = null // Ошибка компиляции!
```

### Тестирование

**LiveData - Требуется настройка**:
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

**Flow - Более простое тестирование**:
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

### Когда использовать каждый

**Используйте LiveData когда**:
- Простое управление UI состоянием
- Работаете с legacy Android кодовой базой (уже используется LiveData)
- Нужен учет жизненного цикла с минимальным boilerplate
- Команда не знакома с Flow/корутинами
- Простой паттерн observe-and-update

**Используйте Flow/StateFlow когда**:
- Сложные трансформации данных (нужны операторы)
- Слой репозитория (платформо-независимый)
- Нужна обработка backpressure
- Комбинирование множественных потоков данных
- Современная Kotlin-first кодовая база
- Продвинутые use cases (debouncing, retry логика и т.д.)
- Мультиплатформенные проекты (KMM)

### Паттерн миграции: LiveData → Flow

**До (LiveData)**:
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

**После (StateFlow)**:
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

**LiveData → Flow**:
```kotlin
// Конвертация LiveData в Flow
val userDataFlow: Flow<User> = userData.asFlow()
```

**Flow → LiveData**:
```kotlin
// Конвертация Flow в LiveData (для legacy кода)
val userDataLiveData: LiveData<User> = userDataFlow.asLiveData()
```

### Резюме

**LiveData**:
- Простой, специфичный для Android
- Встроенный учет жизненного цикла
- Легко изучить
- Ограниченные операторы
- Только для Android
- Менее мощный

**Flow/StateFlow**:
- Мощный, гибкий
- Богатый набор операторов
- Платформо-независимый
- Лучшее тестирование
- Требует ручной обработки жизненного цикла
- Более крутая кривая обучения

**Современная Рекомендация**: Используйте **StateFlow/SharedFlow** для новых проектов, мигрируйте с LiveData при добавлении сложных функций или работе со слоем репозитория.

---

## References

- [StateFlow and SharedFlow - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Migrate from LiveData to Kotlin Flow - Android Developers](https://developer.android.com/codelabs/android-flow)
- [LiveData Overview - Android Developers](https://developer.android.com/topic/libraries/architecture/livedata)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF


---

## Related Questions

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - StateFlow & SharedFlow differences

### Advanced (Harder)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies


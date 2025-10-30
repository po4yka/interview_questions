---
id: 20251017-112118
title: "Koin Fundamentals / Основы Koin"
aliases: [Koin DI, Koin Framework, Service Locator, Основы Koin, Koin внедрение зависимостей]
topic: android
subtopics: [di-koin, architecture-clean, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compositionlocal-compose--android--hard, q-how-to-register-broadcastreceiver-to-receive-messages--android--medium, q-recomposition-choreographer--android--hard]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/di-koin, android/architecture-clean, android/lifecycle, architecture, difficulty/medium, injection, koin, service-locator]
---
# Вопрос (RU)

> Чем Koin отличается от Dagger/Hilt? Реализуйте полный Koin модуль с определениями factory, single и viewModel.

# Question (EN)

> How does Koin differ from Dagger/Hilt? Implement a complete Koin module with factory, single, and viewModel definitions.

---

## Ответ (RU)

**Koin** — легковесный DI фреймворк для Kotlin, использующий **Service Locator паттерн** вместо code generation. Разрешает зависимости в runtime через простой DSL.

### Koin Vs Dagger/Hilt

| Aspect | Koin | Dagger/Hilt |
|--------|------|-------------|
| **Подход** | Service Locator | True DI |
| **Разрешение** | Runtime | Compile-time |
| **Code Generation** | ❌ Нет | ✅ kapt/ksp |
| **Build Speed** | ✅ Быстро | ❌ Медленно |
| **Error Detection** | ❌ Runtime | ✅ Compile-time |
| **Learning Curve** | ✅ Простая | ❌ Крутая |
| **Performance** | ❌ Медленнее | ✅ Быстрее |
| **Testing** | ✅ Простое | ❌ Сложное |
| **Multiplatform** | ✅ KMM | ❌ Android only |

### Основные Определения

**Module** - контейнер зависимостей
**Factory** - новый экземпляр каждый раз
**Single** - singleton (один экземпляр)
**ViewModel** - Android ViewModel интеграция

### Полная Настройка Koin

**Определения классов**:

```kotlin
// ❌ БЫЛО: Дублирование кода, избыточность
// ✅ СЕЙЧАС: Минимальные определения

// Domain
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
}

class UserRepositoryImpl(
    private val api: UserApi,
    private val database: UserDatabase
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> =
        try {
            api.getUser(id).also { database.saveUser(it) }
                .let { Result.success(it) }
        } catch (e: Exception) {
            database.getUser(id)?.let { Result.success(it) }
                ?: Result.failure(e)
        }
}

// Use case
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: String) = repository.getUser(id)
}

// ViewModel
class UserViewModel(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadUser(id: String) = viewModelScope.launch {
        _state.value = UiState.Loading
        getUserUseCase(id)
            .onSuccess { _state.value = UiState.Success(it) }
            .onFailure { _state.value = UiState.Error(it.message.orEmpty()) }
    }
}
```

**Koin модули**:

```kotlin
// ✅ Network module
val networkModule = module {
    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .addConverterFactory(GsonConverterFactory.create())
            .client(get())
            .build()
    }

    single<OkHttpClient> {
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) Level.BODY else Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    single<UserApi> { get<Retrofit>().create(UserApi::class.java) }
}

// ✅ Data module
val dataModule = module {
    single<UserDatabase> {
        Room.databaseBuilder(androidContext(), UserDatabase::class.java, "db")
            .fallbackToDestructiveMigration()
            .build()
    }

    // ✅ Factory - новый экземпляр каждый раз
    factory<Logger> { LoggerImpl(tag = "App") }

    // ✅ Single - интерфейс к реализации
    single<UserRepository> { UserRepositoryImpl(get(), get()) }
}

// ✅ Domain module
val domainModule = module {
    factory { GetUserUseCase(get()) }
}

// ✅ Presentation module
val presentationModule = module {
    viewModel { UserViewModel(get()) }

    // ✅ С параметрами
    viewModel { (userId: String) ->
        UserDetailViewModel(userId, get())
    }
}
```

**Инициализация**:

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            androidContext(this@MyApplication)
            if (BuildConfig.DEBUG) androidLogger(Level.DEBUG)
            modules(networkModule, dataModule, domainModule, presentationModule)
        }
    }
}
```

### Использование

**Activity**:

```kotlin
class UserActivity : AppCompatActivity() {
    // ✅ Lazy injection
    private val viewModel: UserViewModel by viewModel()
    private val logger: Logger by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logger.log("Created")
    }
}
```

**Fragment**:

```kotlin
class UserFragment : Fragment() {
    // ✅ Activity scope ViewModel
    private val viewModel: UserViewModel by activityViewModel()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.state.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showUser(state.data)
                    is UiState.Error -> showError(state.message)
                }
            }
        }
    }
}
```

**Compose**:

```kotlin
@Composable
fun UserScreen(userId: String) {
    val viewModel: UserViewModel = koinViewModel()
    val state by viewModel.state.collectAsState()

    LaunchedEffect(userId) { viewModel.loadUser(userId) }

    when (val s = state) {
        UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> Text("User: ${s.data.name}")
        is UiState.Error -> Text("Error: ${s.message}", color = Color.Red)
    }
}
```

### Factory Vs Single Vs ViewModel

```kotlin
// ❌ Factory - новый экземпляр каждый раз
module {
    factory { MyRepository(get()) }
}
val repo1: MyRepository by inject()
val repo2: MyRepository by inject()
// repo1 !== repo2

// ✅ Single - один экземпляр (singleton)
module {
    single { MyDatabase(get()) }
}
val db1: MyDatabase by inject()
val db2: MyDatabase by inject()
// db1 === db2

// ✅ ViewModel - Android ViewModel lifecycle
module {
    viewModel { MyViewModel(get()) }
}
val vm: MyViewModel by viewModel() // Survives config changes
```

### Named Dependencies

```kotlin
module {
    single(named("dev")) { ApiConfig("https://dev.api.com") }
    single(named("prod")) { ApiConfig("https://api.com") }

    // ✅ Использование именованной зависимости
    single<ApiService> { ApiService(get(named("prod"))) }
}

// Usage
private val devConfig: ApiConfig by inject(named("dev"))
```

### Тестирование

```kotlin
class UserRepositoryTest : KoinTest {
    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(
            module {
                single<UserApi> { mockk<UserApi>() }
                single<UserRepository> { UserRepositoryImpl(get()) }
            }
        )
    }

    private val repository: UserRepository by inject()

    @Test
    fun `getUser returns cached data on network failure`() = runTest {
        // Test implementation
    }
}
```

### Best Practices

**✅ DO:**
- Группировать модули по слоям (data, domain, presentation)
- Использовать интерфейсы для single
- `by inject()` для lazy initialization
- `checkModules()` для валидации
- Scope для lifecycle management

**❌ DON'T:**
- Factory для дорогих объектов (используйте single)
- Хранить Activity context в singleton (утечка памяти)
- Инжектить простые значения (передайте в конструктор)
- Забывать startKoin() перед использованием

### Когда Выбирать Koin

**✅ Koin:**
- Kotlin Multiplatform проекты
- Быстрое время сборки критично
- Команда новичок в DI
- Малый/средний проект
- Предпочитаете runtime гибкость

**✅ Dagger/Hilt:**
- Compile-time безопасность критична
- Максимальная runtime производительность
- Большая кодовая база
- Команда опытна с Dagger
- Android-only проект

---

## Answer (EN)

**Koin** is a lightweight DI framework for Kotlin using **Service Locator pattern** instead of code generation. Resolves dependencies at runtime via simple DSL.

### Koin Vs Dagger/Hilt

| Aspect | Koin | Dagger/Hilt |
|--------|------|-------------|
| **Approach** | Service Locator | True DI |
| **Resolution** | Runtime | Compile-time |
| **Code Generation** | ❌ None | ✅ kapt/ksp |
| **Build Speed** | ✅ Fast | ❌ Slow |
| **Error Detection** | ❌ Runtime | ✅ Compile-time |
| **Learning Curve** | ✅ Gentle | ❌ Steep |
| **Performance** | ❌ Slower | ✅ Faster |
| **Testing** | ✅ Simple | ❌ Complex |
| **Multiplatform** | ✅ KMM | ❌ Android only |

### Core Definitions

**Module** - dependency container
**Factory** - new instance every time
**Single** - singleton instance
**ViewModel** - Android ViewModel integration

### Complete Koin Setup

**Class definitions**:

```kotlin
// ❌ WAS: Code duplication, verbosity
// ✅ NOW: Minimal definitions

// Domain
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
}

class UserRepositoryImpl(
    private val api: UserApi,
    private val database: UserDatabase
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> =
        try {
            api.getUser(id).also { database.saveUser(it) }
                .let { Result.success(it) }
        } catch (e: Exception) {
            database.getUser(id)?.let { Result.success(it) }
                ?: Result.failure(e)
        }
}

// Use case
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: String) = repository.getUser(id)
}

// ViewModel
class UserViewModel(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadUser(id: String) = viewModelScope.launch {
        _state.value = UiState.Loading
        getUserUseCase(id)
            .onSuccess { _state.value = UiState.Success(it) }
            .onFailure { _state.value = UiState.Error(it.message.orEmpty()) }
    }
}
```

**Koin modules**:

```kotlin
// ✅ Network module
val networkModule = module {
    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .addConverterFactory(GsonConverterFactory.create())
            .client(get())
            .build()
    }

    single<OkHttpClient> {
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) Level.BODY else Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    single<UserApi> { get<Retrofit>().create(UserApi::class.java) }
}

// ✅ Data module
val dataModule = module {
    single<UserDatabase> {
        Room.databaseBuilder(androidContext(), UserDatabase::class.java, "db")
            .fallbackToDestructiveMigration()
            .build()
    }

    // ✅ Factory - new instance every time
    factory<Logger> { LoggerImpl(tag = "App") }

    // ✅ Single - interface to implementation
    single<UserRepository> { UserRepositoryImpl(get(), get()) }
}

// ✅ Domain module
val domainModule = module {
    factory { GetUserUseCase(get()) }
}

// ✅ Presentation module
val presentationModule = module {
    viewModel { UserViewModel(get()) }

    // ✅ With parameters
    viewModel { (userId: String) ->
        UserDetailViewModel(userId, get())
    }
}
```

**Initialization**:

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            androidContext(this@MyApplication)
            if (BuildConfig.DEBUG) androidLogger(Level.DEBUG)
            modules(networkModule, dataModule, domainModule, presentationModule)
        }
    }
}
```

### Usage

**Activity**:

```kotlin
class UserActivity : AppCompatActivity() {
    // ✅ Lazy injection
    private val viewModel: UserViewModel by viewModel()
    private val logger: Logger by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logger.log("Created")
    }
}
```

**Fragment**:

```kotlin
class UserFragment : Fragment() {
    // ✅ Activity scope ViewModel
    private val viewModel: UserViewModel by activityViewModel()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.state.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showUser(state.data)
                    is UiState.Error -> showError(state.message)
                }
            }
        }
    }
}
```

**Compose**:

```kotlin
@Composable
fun UserScreen(userId: String) {
    val viewModel: UserViewModel = koinViewModel()
    val state by viewModel.state.collectAsState()

    LaunchedEffect(userId) { viewModel.loadUser(userId) }

    when (val s = state) {
        UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> Text("User: ${s.data.name}")
        is UiState.Error -> Text("Error: ${s.message}", color = Color.Red)
    }
}
```

### Factory Vs Single Vs ViewModel

```kotlin
// ❌ Factory - new instance every time
module {
    factory { MyRepository(get()) }
}
val repo1: MyRepository by inject()
val repo2: MyRepository by inject()
// repo1 !== repo2

// ✅ Single - one instance (singleton)
module {
    single { MyDatabase(get()) }
}
val db1: MyDatabase by inject()
val db2: MyDatabase by inject()
// db1 === db2

// ✅ ViewModel - Android ViewModel lifecycle
module {
    viewModel { MyViewModel(get()) }
}
val vm: MyViewModel by viewModel() // Survives config changes
```

### Named Dependencies

```kotlin
module {
    single(named("dev")) { ApiConfig("https://dev.api.com") }
    single(named("prod")) { ApiConfig("https://api.com") }

    // ✅ Use named dependency
    single<ApiService> { ApiService(get(named("prod"))) }
}

// Usage
private val devConfig: ApiConfig by inject(named("dev"))
```

### Testing

```kotlin
class UserRepositoryTest : KoinTest {
    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(
            module {
                single<UserApi> { mockk<UserApi>() }
                single<UserRepository> { UserRepositoryImpl(get()) }
            }
        )
    }

    private val repository: UserRepository by inject()

    @Test
    fun `getUser returns cached data on network failure`() = runTest {
        // Test implementation
    }
}
```

### Best Practices

**✅ DO:**
- Group modules by layer (data, domain, presentation)
- Use interfaces for single
- `by inject()` for lazy initialization
- `checkModules()` for validation
- Scope for lifecycle management

**❌ DON'T:**
- Factory for expensive objects (use single)
- Store Activity context in singleton (memory leak)
- Inject simple values (pass in constructor)
- Forget startKoin() before usage

### When to Choose Koin

**✅ Koin:**
- Kotlin Multiplatform projects
- Fast build time critical
- Team new to DI
- Small/medium project
- Prefer runtime flexibility

**✅ Dagger/Hilt:**
- Compile-time safety critical
- Maximum runtime performance
- Large codebase
- Team experienced with Dagger
- Android-only project

---

## Follow-ups

- How to implement custom Koin scopes for feature modules?
- What happens if circular dependencies exist in Koin?
- How to migrate from Dagger/Hilt to Koin?
- How to test Koin modules with checkModules()?
- What's the performance overhead of Koin's runtime resolution?

## References

- Official Koin documentation: https://insert-koin.io/docs/reference/koin-android/start
- Koin vs Dagger comparison: https://insert-koin.io/docs/reference/koin-core/dsl
- Koin on GitHub: https://github.com/InsertKoinIO/koin

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-viewmodel--android--medium]]

### Related (Same Level)
- [[q-compositionlocal-compose--android--hard]]
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]]

### Advanced (Harder)
- [[q-recomposition-choreographer--android--hard]]

---
id: "20251015082237507"
title: "Koin Fundamentals / Основы Koin"
topic: dependency-injection
difficulty: medium
status: draft
created: 2025-10-15
tags: [injection, koin, architecture, service-locator, difficulty/medium]
---
# Koin Fundamentals / Основы Koin

**English**: How does Koin differ from Dagger/Hilt? Implement a complete Koin module with factory, single, and viewModel definitions.

## Answer (EN)
**Koin** is a pragmatic lightweight dependency injection framework for Kotlin that uses a **service locator pattern** rather than code generation. It provides a simple DSL for declaring dependencies and resolving them at runtime.

### Key Differences: Koin vs Dagger/Hilt

| Aspect | Koin | Dagger/Hilt |
|--------|------|-------------|
| **Type** | Service Locator | True Dependency Injection |
| **Resolution** | Runtime | Compile-time |
| **Code Generation** | None | Generates code with kapt/ksp |
| **Build Time** | Faster (no generation) | Slower (annotation processing) |
| **Error Detection** | Runtime | Compile-time |
| **Learning Curve** | Gentle (DSL-based) | Steep (annotations, scopes) |
| **Performance** | Slightly slower (reflection) | Faster (direct instantiation) |
| **Startup Time** | Minimal overhead | No overhead |
| **Testing** | Simple mocking | Requires test components |
| **Multiplatform** | Full KMM support | Android only |

### Core Koin Concepts

**1. Module** - Container for definitions
**2. Factory** - New instance every time
**3. Single** - Singleton instance
**4. ViewModel** - Android ViewModel integration
**5. Scope** - Limited lifetime definitions

### Complete Koin Setup

**Step 1: Add Dependencies**

```kotlin
// build.gradle.kts
dependencies {
    // Koin for Android
    implementation("io.insert-koin:koin-android:3.5.0")

    // Koin for Jetpack Compose
    implementation("io.insert-koin:koin-androidx-compose:3.5.0")

    // Koin Test
    testImplementation("io.insert-koin:koin-test:3.5.0")
    testImplementation("io.insert-koin:koin-test-junit4:3.5.0")
}
```

**Step 2: Define Your Classes**

```kotlin
// Domain layer
data class User(
    val id: String,
    val name: String,
    val email: String
)

interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    suspend fun saveUser(user: User): Result<Unit>
}

// Data layer
class UserRepositoryImpl(
    private val api: UserApi,
    private val database: UserDatabase,
    private val logger: Logger
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> {
        logger.log("Fetching user: $id")
        return try {
            val user = api.getUser(id)
            database.saveUser(user)
            Result.success(user)
        } catch (e: Exception) {
            database.getUser(id)?.let {
                Result.success(it)
            } ?: Result.failure(e)
        }
    }

    override suspend fun saveUser(user: User): Result<Unit> {
        logger.log("Saving user: ${user.id}")
        return try {
            api.saveUser(user)
            database.saveUser(user)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Use cases
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: String): Result<User> {
        return repository.getUser(id)
    }
}

class SaveUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(user: User): Result<Unit> {
        return repository.saveUser(user)
    }
}

// Presentation layer
class UserViewModel(
    private val getUserUseCase: GetUserUseCase,
    private val saveUserUseCase: SaveUserUseCase
) : ViewModel() {
    private val _userState = MutableStateFlow<UiState<User>>(UiState.Loading)
    val userState: StateFlow<UiState<User>> = _userState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _userState.value = UiState.Loading
            getUserUseCase(id)
                .onSuccess { user ->
                    _userState.value = UiState.Success(user)
                }
                .onFailure { error ->
                    _userState.value = UiState.Error(error.message ?: "Unknown error")
                }
        }
    }

    fun saveUser(user: User) {
        viewModelScope.launch {
            saveUserUseCase(user)
                .onSuccess {
                    _userState.value = UiState.Success(user)
                }
                .onFailure { error ->
                    _userState.value = UiState.Error(error.message ?: "Unknown error")
                }
        }
    }
}

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
```

**Step 3: Create Koin Modules**

```kotlin
// networkModule.kt
val networkModule = module {
    // Single - created once and reused
    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .addConverterFactory(GsonConverterFactory.create())
            .client(get()) // Gets OkHttpClient from another module
            .build()
    }

    single<OkHttpClient> {
        OkHttpClient.Builder()
            .addInterceptor(get<AuthInterceptor>())
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG)
                    HttpLoggingInterceptor.Level.BODY
                else
                    HttpLoggingInterceptor.Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    single<UserApi> {
        get<Retrofit>().create(UserApi::class.java)
    }
}

// dataModule.kt
val dataModule = module {
    // Single - database instance
    single<UserDatabase> {
        Room.databaseBuilder(
            androidContext(),
            UserDatabase::class.java,
            "user-database"
        )
        .fallbackToDestructiveMigration()
        .build()
    }

    single<UserDao> { get<UserDatabase>().userDao() }

    // Factory - new instance each time
    factory<Logger> {
        LoggerImpl(tag = "UserApp")
    }

    // Single with interface binding
    single<UserRepository> {
        UserRepositoryImpl(
            api = get(),
            database = get(),
            logger = get()
        )
    }
}

// domainModule.kt
val domainModule = module {
    // Factory - new instance for each injection
    factory { GetUserUseCase(get()) }
    factory { SaveUserUseCase(get()) }
}

// presentationModule.kt
val presentationModule = module {
    // ViewModel - Android Architecture Components integration
    viewModel { UserViewModel(get(), get()) }

    // ViewModel with parameters
    viewModel { (userId: String) ->
        UserDetailViewModel(
            userId = userId,
            getUserUseCase = get()
        )
    }
}

// utilityModule.kt
val utilityModule = module {
    single<AuthInterceptor> {
        AuthInterceptor(tokenProvider = get())
    }

    single<TokenProvider> {
        TokenProviderImpl(
            sharedPreferences = androidContext()
                .getSharedPreferences("auth", Context.MODE_PRIVATE)
        )
    }
}

// Complete app modules
val appModules = listOf(
    networkModule,
    dataModule,
    domainModule,
    presentationModule,
    utilityModule
)
```

**Step 4: Initialize Koin in Application**

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            // Enable Android context
            androidContext(this@MyApplication)

            // Enable logging in debug mode
            if (BuildConfig.DEBUG) {
                androidLogger(Level.DEBUG)
            }

            // Enable Koin property injection
            androidFileProperties()

            // Load modules
            modules(appModules)
        }
    }
}
```

**Step 5: Using Koin in Activities**

```kotlin
class UserActivity : AppCompatActivity() {
    // Lazy injection
    private val userViewModel: UserViewModel by viewModel()

    // Direct injection
    private val logger: Logger by inject()

    // Parameterized ViewModel
    private val userDetailViewModel: UserDetailViewModel by viewModel {
        parametersOf("user123")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)

        logger.log("UserActivity created")

        userViewModel.userState.collectAsState().value.let { state ->
            when (state) {
                is UiState.Loading -> showLoading()
                is UiState.Success -> showUser(state.data)
                is UiState.Error -> showError(state.message)
            }
        }
    }
}
```

**Step 6: Using Koin in Fragments**

```kotlin
class UserFragment : Fragment() {
    private val userViewModel: UserViewModel by activityViewModel()
    private val logger: Logger by inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            userViewModel.userState.collect { state ->
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

**Step 7: Using Koin in Jetpack Compose**

```kotlin
@Composable
fun UserScreen(userId: String) {
    // Get ViewModel from Koin
    val viewModel: UserViewModel = koinViewModel()

    // Get dependency from Koin
    val logger: Logger = get()

    val userState by viewModel.userState.collectAsState()

    LaunchedEffect(userId) {
        logger.log("Loading user: $userId")
        viewModel.loadUser(userId)
    }

    when (val state = userState) {
        is UiState.Loading -> LoadingView()
        is UiState.Success -> UserDetailView(state.data)
        is UiState.Error -> ErrorView(state.message)
    }
}
```

### Factory vs Single vs ViewModel

**Factory** - Creates new instance every time:
```kotlin
module {
    factory { MyRepository(get()) }
}

// Usage creates new instance each time
val repo1: MyRepository by inject()
val repo2: MyRepository by inject()
// repo1 !== repo2
```

**Single** - Creates singleton (one instance):
```kotlin
module {
    single { MyDatabase(get()) }
}

// Usage returns same instance
val db1: MyDatabase by inject()
val db2: MyDatabase by inject()
// db1 === db2
```

**ViewModel** - Android ViewModel lifecycle:
```kotlin
module {
    viewModel { MyViewModel(get()) }
}

// Lifecycle-aware, survives configuration changes
val viewModel: MyViewModel by viewModel()
```

### Named Dependencies

```kotlin
module {
    // Named definitions
    single(named("development")) {
        ApiConfig(baseUrl = "https://dev.api.com")
    }

    single(named("production")) {
        ApiConfig(baseUrl = "https://api.com")
    }

    // Use named dependency
    single<ApiService> {
        ApiService(config = get(named("production")))
    }
}

// Usage
class MyActivity : AppCompatActivity() {
    private val devConfig: ApiConfig by inject(named("development"))
}
```

### Koin Properties

```kotlin
// koin.properties file in assets
server.url=https://api.example.com
api.timeout=30000

// Module using properties
module {
    single<ApiService> {
        val url = getProperty<String>("server.url")
        val timeout = getProperty<Int>("api.timeout")
        ApiService(url, timeout)
    }
}
```

### Testing with Koin

```kotlin
class UserRepositoryTest : KoinTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserApi> { mockk<UserApi>() }
                single<UserDatabase> { mockk<UserDatabase>() }
                single<Logger> { mockk<Logger>(relaxed = true) }
                single<UserRepository> { UserRepositoryImpl(get(), get(), get()) }
            }
        )
    }

    private val repository: UserRepository by inject()
    private val api: UserApi by inject()
    private val database: UserDatabase by inject()

    @Test
    fun `when api succeeds, user is saved to database`() = runTest {
        // Given
        val user = User("1", "John", "john@example.com")
        coEvery { api.getUser("1") } returns user
        coEvery { database.saveUser(user) } just Runs

        // When
        val result = repository.getUser("1")

        // Then
        assertTrue(result.isSuccess)
        assertEquals(user, result.getOrNull())
        coVerify { database.saveUser(user) }
    }
}
```

### When to Choose Koin

**Choose Koin when:**
- Building Kotlin Multiplatform projects
- Want faster build times (no code generation)
- Prefer runtime flexibility over compile-time safety
- Team is new to DI frameworks
- Project is small to medium size
- Need quick setup and iteration

**Choose Dagger/Hilt when:**
- Need compile-time verification
- Maximum runtime performance is critical
- Large, complex codebase
- Team experienced with Dagger
- Android-only project
- Want to catch errors at compile time

### Best Practices

1. **Module Organization** - Group by layer (data, domain, presentation)
2. **Use Interfaces** - Bind interfaces to implementations
3. **Lazy Injection** - Use `by inject()` for lazy initialization
4. **Scopes** - Use scopes for lifecycle management
5. **Testing** - Override modules in tests
6. **Check Modules** - Use `checkModules()` to verify configuration
7. **Avoid Over-Injection** - Don't inject simple values

### Common Pitfalls

1. **Circular Dependencies** - Koin won't detect at compile time
2. **Missing Dependencies** - Runtime errors instead of compile errors
3. **Wrong Scope** - Using factory for expensive objects
4. **Memory Leaks** - Holding Activity context in singleton
5. **Late Init** - Not starting Koin before using dependencies

### Summary

Koin is a pragmatic, lightweight DI framework for Kotlin that uses service locator pattern and runtime resolution. It offers:
- **Simple DSL** - Easy to learn and use
- **No code generation** - Faster builds
- **Runtime resolution** - Flexible but requires testing
- **Factory, Single, ViewModel** - Different instance strategies
- **KMM support** - Works across platforms

Trade-offs: Runtime errors vs compile-time safety, slightly slower performance, but much faster development and build times.

---

## Ответ (RU)
**Koin** — это прагматичный легковесный фреймворк внедрения зависимостей для Kotlin, использующий **паттерн Service Locator** вместо генерации кода. Предоставляет простой DSL для объявления и разрешения зависимостей во время выполнения.

### Ключевые различия: Koin vs Dagger/Hilt

| Аспект | Koin | Dagger/Hilt |
|--------|------|-------------|
| **Тип** | Service Locator | True Dependency Injection |
| **Разрешение** | Runtime | Compile-time |
| **Генерация кода** | Нет | Генерирует код (kapt/ksp) |
| **Время сборки** | Быстрее | Медленнее |
| **Обнаружение ошибок** | Runtime | Compile-time |
| **Кривая обучения** | Пологая (DSL) | Крутая (аннотации) |
| **Производительность** | Чуть медленнее | Быстрее |
| **Время старта** | Минимальный overhead | Без overhead |
| **Тестирование** | Простое | Требует test компонентов |
| **Multiplatform** | Полная поддержка KMM | Только Android |

### Основные концепции Koin

**1. Module** - Контейнер для определений
**2. Factory** - Новый экземпляр каждый раз
**3. Single** - Singleton экземпляр
**4. ViewModel** - Интеграция с Android ViewModel
**5. Scope** - Определения с ограниченным временем жизни

### Полная настройка Koin

```kotlin
// Зависимости
dependencies {
    implementation("io.insert-koin:koin-android:3.5.0")
    implementation("io.insert-koin:koin-androidx-compose:3.5.0")
}

// Модули
val networkModule = module {
    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .addConverterFactory(GsonConverterFactory.create())
            .client(get())
            .build()
    }

    single<UserApi> { get<Retrofit>().create(UserApi::class.java) }
}

val dataModule = module {
    single<UserDatabase> {
        Room.databaseBuilder(androidContext(), UserDatabase::class.java, "db")
            .build()
    }

    factory<Logger> { LoggerImpl(tag = "App") }

    single<UserRepository> { UserRepositoryImpl(get(), get(), get()) }
}

val domainModule = module {
    factory { GetUserUseCase(get()) }
    factory { SaveUserUseCase(get()) }
}

val presentationModule = module {
    viewModel { UserViewModel(get(), get()) }

    // С параметрами
    viewModel { (userId: String) ->
        UserDetailViewModel(userId, get())
    }
}

// Инициализация
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

// Использование в Activity
class UserActivity : AppCompatActivity() {
    private val userViewModel: UserViewModel by viewModel()
    private val logger: Logger by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logger.log("Activity created")
    }
}

// Использование в Compose
@Composable
fun UserScreen() {
    val viewModel: UserViewModel = koinViewModel()
    val userState by viewModel.userState.collectAsState()
}
```

### Factory vs Single vs ViewModel

**Factory** - новый экземпляр каждый раз:
```kotlin
module {
    factory { MyRepository(get()) }
}
```

**Single** - singleton (один экземпляр):
```kotlin
module {
    single { MyDatabase(get()) }
}
```

**ViewModel** - жизненный цикл Android ViewModel:
```kotlin
module {
    viewModel { MyViewModel(get()) }
}
```

### Именованные зависимости

```kotlin
module {
    single(named("dev")) { ApiConfig("https://dev.api.com") }
    single(named("prod")) { ApiConfig("https://api.com") }

    single<ApiService> { ApiService(get(named("prod"))) }
}

// Использование
private val devConfig: ApiConfig by inject(named("dev"))
```

### Тестирование

```kotlin
class UserRepositoryTest : KoinTest {
    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                single<UserApi> { mockk<UserApi>() }
                single<UserRepository> { UserRepositoryImpl(get()) }
            }
        )
    }

    private val repository: UserRepository by inject()

    @Test
    fun `test repository`() = runTest {
        // Test implementation
    }
}
```

### Когда выбирать Koin

**Выбирайте Koin когда:**
- Разрабатываете Kotlin Multiplatform проекты
- Хотите быстрое время сборки
- Предпочитаете гибкость runtime
- Команда новичок в DI фреймворках
- Проект малого/среднего размера

**Выбирайте Dagger/Hilt когда:**
- Нужна проверка во время компиляции
- Критична производительность runtime
- Большая кодовая база
- Команда опытна с Dagger
- Только Android проект

### Best Practices

1. **Организация модулей** - группировать по слоям (data, domain, presentation)
2. **Использовать интерфейсы** - привязывать интерфейсы к реализациям
3. **Lazy injection** - использовать `by inject()` для ленивой инициализации
4. **Scope** - использовать scope для управления жизненным циклом
5. **Тестирование** - переопределять модули в тестах
6. **Проверка модулей** - использовать `checkModules()` для верификации
7. **Избегать избыточной инъекции** - не инжектить простые значения

### Определение классов для примера

```kotlin
// Доменный слой
data class User(
    val id: String,
    val name: String,
    val email: String
)

interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    suspend fun saveUser(user: User): Result<Unit>
}

// Слой данных
class UserRepositoryImpl(
    private val api: UserApi,
    private val database: UserDatabase,
    private val logger: Logger
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> {
        logger.log("Загрузка пользователя: $id")
        return try {
            val user = api.getUser(id)
            database.saveUser(user)
            Result.success(user)
        } catch (e: Exception) {
            database.getUser(id)?.let {
                Result.success(it)
            } ?: Result.failure(e)
        }
    }

    override suspend fun saveUser(user: User): Result<Unit> {
        logger.log("Сохранение пользователя: ${user.id}")
        return try {
            api.saveUser(user)
            database.saveUser(user)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Use cases
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: String): Result<User> {
        return repository.getUser(id)
    }
}

class SaveUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(user: User): Result<Unit> {
        return repository.saveUser(user)
    }
}

// Слой представления
class UserViewModel(
    private val getUserUseCase: GetUserUseCase,
    private val saveUserUseCase: SaveUserUseCase
) : ViewModel() {
    private val _userState = MutableStateFlow<UiState<User>>(UiState.Loading)
    val userState: StateFlow<UiState<User>> = _userState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _userState.value = UiState.Loading
            getUserUseCase(id)
                .onSuccess { user ->
                    _userState.value = UiState.Success(user)
                }
                .onFailure { error ->
                    _userState.value = UiState.Error(error.message ?: "Неизвестная ошибка")
                }
        }
    }

    fun saveUser(user: User) {
        viewModelScope.launch {
            saveUserUseCase(user)
                .onSuccess {
                    _userState.value = UiState.Success(user)
                }
                .onFailure { error ->
                    _userState.value = UiState.Error(error.message ?: "Неизвестная ошибка")
                }
        }
    }
}

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
```

### Создание модулей Koin

```kotlin
// networkModule.kt
val networkModule = module {
    // Single - создается один раз и переиспользуется
    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .addConverterFactory(GsonConverterFactory.create())
            .client(get()) // Получает OkHttpClient из другого модуля
            .build()
    }

    single<OkHttpClient> {
        OkHttpClient.Builder()
            .addInterceptor(get<AuthInterceptor>())
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG)
                    HttpLoggingInterceptor.Level.BODY
                else
                    HttpLoggingInterceptor.Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    single<UserApi> {
        get<Retrofit>().create(UserApi::class.java)
    }
}

// dataModule.kt
val dataModule = module {
    // Single - экземпляр базы данных
    single<UserDatabase> {
        Room.databaseBuilder(
            androidContext(),
            UserDatabase::class.java,
            "user-database"
        )
        .fallbackToDestructiveMigration()
        .build()
    }

    single<UserDao> { get<UserDatabase>().userDao() }

    // Factory - новый экземпляр каждый раз
    factory<Logger> {
        LoggerImpl(tag = "UserApp")
    }

    // Single с привязкой интерфейса
    single<UserRepository> {
        UserRepositoryImpl(
            api = get(),
            database = get(),
            logger = get()
        )
    }
}

// domainModule.kt
val domainModule = module {
    // Factory - новый экземпляр для каждой инъекции
    factory { GetUserUseCase(get()) }
    factory { SaveUserUseCase(get()) }
}

// presentationModule.kt
val presentationModule = module {
    // ViewModel - интеграция с Android Architecture Components
    viewModel { UserViewModel(get(), get()) }

    // ViewModel с параметрами
    viewModel { (userId: String) ->
        UserDetailViewModel(
            userId = userId,
            getUserUseCase = get()
        )
    }
}

// utilityModule.kt
val utilityModule = module {
    single<AuthInterceptor> {
        AuthInterceptor(tokenProvider = get())
    }

    single<TokenProvider> {
        TokenProviderImpl(
            sharedPreferences = androidContext()
                .getSharedPreferences("auth", Context.MODE_PRIVATE)
        )
    }
}

// Все модули приложения
val appModules = listOf(
    networkModule,
    dataModule,
    domainModule,
    presentationModule,
    utilityModule
)
```

### Использование в Fragment

```kotlin
class UserFragment : Fragment() {
    // ViewModel из Activity scope
    private val userViewModel: UserViewModel by activityViewModel()

    // Прямая инъекция
    private val logger: Logger by inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            userViewModel.userState.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showUser(state.data)
                    is UiState.Error -> showError(state.message)
                }
            }
        }
    }

    private fun showLoading() {
        // Показать индикатор загрузки
    }

    private fun showUser(user: User) {
        // Отобразить данные пользователя
    }

    private fun showError(message: String) {
        // Показать ошибку
    }
}
```

### Использование в Jetpack Compose

```kotlin
@Composable
fun UserScreen(userId: String) {
    // Получить ViewModel из Koin
    val viewModel: UserViewModel = koinViewModel()

    // Получить зависимость из Koin
    val logger: Logger = get()

    val userState by viewModel.userState.collectAsState()

    LaunchedEffect(userId) {
        logger.log("Загрузка пользователя: $userId")
        viewModel.loadUser(userId)
    }

    when (val state = userState) {
        is UiState.Loading -> LoadingView()
        is UiState.Success -> UserDetailView(state.data)
        is UiState.Error -> ErrorView(state.message)
    }
}

@Composable
fun LoadingView() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator()
    }
}

@Composable
fun UserDetailView(user: User) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(text = "Имя: ${user.name}", style = MaterialTheme.typography.h5)
        Spacer(modifier = Modifier.height(8.dp))
        Text(text = "Email: ${user.email}", style = MaterialTheme.typography.body1)
    }
}

@Composable
fun ErrorView(message: String) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Text(text = "Ошибка: $message", color = Color.Red)
    }
}
```

### Свойства Koin

Использование файла конфигурации для внешних параметров:

```kotlin
// koin.properties файл в assets
server.url=https://api.example.com
api.timeout=30000
cache.enabled=true

// Модуль использующий свойства
module {
    single<ApiService> {
        val url = getProperty<String>("server.url")
        val timeout = getProperty<Int>("api.timeout")
        val cacheEnabled = getProperty<Boolean>("cache.enabled")
        ApiService(url, timeout, cacheEnabled)
    }
}
```

### Общие ошибки

**1. Циклические зависимости** - Koin не обнаружит их во время компиляции:
```kotlin
// ПЛОХО: циклическая зависимость
module {
    single { ServiceA(get()) } // Требует ServiceB
    single { ServiceB(get()) } // Требует ServiceA - ошибка во время выполнения!
}
```

**2. Отсутствующие зависимости** - ошибки runtime вместо compile-time:
```kotlin
// ПЛОХО: забыли добавить зависимость в модуль
class MyActivity : AppCompatActivity() {
    private val service: MyService by inject() // Крэш! MyService не определен в модулях
}
```

**3. Неправильный scope** - использование factory для дорогих объектов:
```kotlin
// ПЛОХО: создание новой базы данных каждый раз
module {
    factory { Room.databaseBuilder(...).build() } // Должен быть single!
}
```

**4. Утечки памяти** - хранение Activity context в singleton:
```kotlin
// ПЛОХО: утечка Activity context
single { MyService(androidContext()) } // Если MyService хранит context, это утечка!

// ХОРОШО: использовать Application context
single { MyService(androidContext()) } // Koin предоставляет Application context
```

**5. Поздняя инициализация** - не запустили Koin перед использованием:
```kotlin
// ПЛОХО: использование Koin до инициализации
class MyActivity : AppCompatActivity() {
    private val service: MyService by inject() // Крэш если startKoin() не вызван!
}
```

### Резюме

Koin — прагматичный легковесный DI фреймворк для Kotlin с service locator паттерном и runtime разрешением. Предлагает простой DSL, без генерации кода, быстрые сборки, поддержку Factory/Single/ViewModel и KMM. Trade-offs: runtime ошибки vs compile-time безопасность, чуть медленнее performance, но быстрее разработка и сборка.

---
id: "20251015082237319"
title: "Kmm Dependency Injection"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - Android
  - Kotlin
  - KMM
  - DI
  - Koin
---
# Dependency Injection in Kotlin Multiplatform Mobile

# Question (EN)
> 
Explain dependency injection strategies for KMM projects. How do you use Koin for multiplatform DI? How do you handle platform-specific dependencies? What are the differences between using Koin, Dagger/Hilt, and manual DI in KMM?

## Answer (EN)
KMM dependency injection requires a unified approach that works across platforms while accommodating platform-specific implementations. Koin provides the most seamless multiplatform DI solution, while Dagger/Hilt can be used on Android with manual wiring on iOS.

#### Koin Multiplatform Setup

**1. Dependencies**
```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        val commonMain by getting {
            dependencies {
                // Koin core
                implementation("io.insert-koin:koin-core:3.5.3")
            }
        }

        val androidMain by getting {
            dependencies {
                // Koin Android
                implementation("io.insert-koin:koin-android:3.5.3")
                implementation("io.insert-koin:koin-androidx-compose:3.5.3")
            }
        }

        val iosMain by getting {
            // Koin core is sufficient for iOS
        }
    }
}
```

**2. Common Module Definition**
```kotlin
// commonMain/di/CommonModule.kt
val networkModule = module {
    // HTTP Client
    single {
        HttpClient {
            install(ContentNegotiation) {
                json(Json {
                    ignoreUnknownKeys = true
                    explicitNulls = false
                })
            }

            install(Logging) {
                level = if (get<Platform>().isDebug) {
                    LogLevel.ALL
                } else {
                    LogLevel.NONE
                }
            }

            install(Auth) {
                bearer {
                    loadTokens {
                        val tokenProvider = get<TokenProvider>()
                        tokenProvider.getTokens()
                    }
                    refreshTokens {
                        val tokenProvider = get<TokenProvider>()
                        tokenProvider.refreshTokens()
                    }
                }
            }
        }
    }

    // API Services
    single { TaskApiService(get()) }
    single { UserApiService(get()) }
    single { CategoryApiService(get()) }
}

val databaseModule = module {
    // Database driver (platform-specific)
    single { DatabaseDriverFactory(get()) }

    // Database
    single {
        TaskDatabase(get<DatabaseDriverFactory>().createDriver())
    }

    // Database queries
    single { get<TaskDatabase>().taskQueries }
    single { get<TaskDatabase>().categoryQueries }
    single { get<TaskDatabase>().userQueries }
}

val repositoryModule = module {
    // Repositories
    single<TaskRepository> {
        TaskRepositoryImpl(
            api = get(),
            database = get(),
            logger = get()
        )
    }

    single<UserRepository> {
        UserRepositoryImpl(
            api = get(),
            database = get(),
            preferences = get()
        )
    }

    single<CategoryRepository> {
        CategoryRepositoryImpl(
            api = get(),
            database = get()
        )
    }
}

val useCaseModule = module {
    // Use Cases - factory scope (new instance each time)
    factory { GetTasksUseCase(get()) }
    factory { CreateTaskUseCase(get()) }
    factory { UpdateTaskUseCase(get()) }
    factory { DeleteTaskUseCase(get()) }
    factory { ToggleTaskCompletionUseCase(get()) }
    factory { SearchTasksUseCase(get()) }

    factory { GetUserUseCase(get()) }
    factory { LoginUseCase(get()) }
    factory { LogoutUseCase(get()) }

    factory { GetCategoriesUseCase(get()) }
    factory { CreateCategoryUseCase(get()) }
}

val platformModule = module {
    // Platform-specific dependencies (expect/actual)
    single { Platform() }
    single { Logger() }
    single<TokenProvider> { get<SecureStorage>() }
}

// Combine all modules
val sharedModules = listOf(
    networkModule,
    databaseModule,
    repositoryModule,
    useCaseModule,
    platformModule
)
```

**3. Platform-Specific Modules**
```kotlin
// androidMain/di/AndroidModule.kt
val androidPlatformModule = module {
    // Android Context
    single { androidContext() }

    // Database Driver Factory
    single { DatabaseDriverFactory(get()) }

    // Secure Storage (SharedPreferences + EncryptedSharedPreferences)
    single<SecureStorage> {
        AndroidSecureStorage(get())
    }

    // Dispatchers
    single<CoroutineDispatchers> {
        object : CoroutineDispatchers {
            override val main = Dispatchers.Main
            override val io = Dispatchers.IO
            override val default = Dispatchers.Default
        }
    }

    // Android-specific services
    single {
        NotificationManager(get<Context>())
    }

    single {
        WorkManagerScheduler(get<Context>())
    }
}

// iosMain/di/IOSModule.kt
val iosPlatformModule = module {
    // Database Driver Factory (no context needed)
    single { DatabaseDriverFactory() }

    // Secure Storage (Keychain)
    single<SecureStorage> {
        IOSSecureStorage()
    }

    // Dispatchers
    single<CoroutineDispatchers> {
        object : CoroutineDispatchers {
            override val main = Dispatchers.Main
            override val io = Dispatchers.Default
            override val default = Dispatchers.Default
        }
    }

    // iOS-specific services
    single {
        NotificationManager()
    }
}
```

**4. Koin Initialization**
```kotlin
// commonMain/di/KoinInitializer.kt
fun initKoin(appDeclaration: KoinAppDeclaration = {}) = startKoin {
    appDeclaration()
    modules(sharedModules)
}

typealias KoinAppDeclaration = KoinApplication.() -> Unit

// androidMain/di/KoinInitializer.kt
class KoinInitializer : Initializer<KoinApplication> {
    override fun create(context: Context): KoinApplication {
        return initKoin {
            androidLogger()
            androidContext(context)
            modules(androidPlatformModule)
        }
    }

    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

// Android Application
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Koin is initialized via AndroidX Startup
        // No manual initialization needed
    }
}

// iosMain/di/KoinInitializer.kt
fun initKoinIOS() = initKoin {
    modules(iosPlatformModule)
}

// iOS App
// In Swift, call this during app initialization
// KoinInitializerKt.initKoinIOS()
```

#### ViewModel Injection

**1. Shared ViewModel with Koin**
```kotlin
// commonMain/presentation/TaskListViewModel.kt
class TaskListViewModel(
    private val getTasks: GetTasksUseCase,
    private val createTask: CreateTaskUseCase,
    private val toggleTask: ToggleTaskCompletionUseCase,
    private val deleteTask: DeleteTaskUseCase,
    private val repository: TaskRepository,
    private val dispatchers: CoroutineDispatchers
) {
    private val viewModelScope = CoroutineScope(
        dispatchers.main + SupervisorJob()
    )

    private val _tasks = MutableStateFlow<List<Task>>(emptyList())
    val tasks: StateFlow<List<Task>> = _tasks.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    init {
        loadTasks()
        observeTasks()
    }

    private fun observeTasks() {
        viewModelScope.launch {
            repository.observeTasks().collect { tasks ->
                _tasks.value = tasks
            }
        }
    }

    fun loadTasks(forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            getTasks(forceRefresh)
                .onSuccess { tasks ->
                    _tasks.value = tasks
                }
                .onFailure { exception ->
                    _error.value = exception.message
                }

            _isLoading.value = false
        }
    }

    fun createTask(title: String, description: String) {
        viewModelScope.launch {
            createTask(title, description)
                .onFailure { exception ->
                    _error.value = exception.message
                }
        }
    }

    fun toggleTaskCompletion(taskId: String) {
        viewModelScope.launch {
            toggleTask(taskId)
                .onFailure { exception ->
                    _error.value = exception.message
                }
        }
    }

    fun deleteTask(taskId: String) {
        viewModelScope.launch {
            deleteTask(taskId)
                .onFailure { exception ->
                    _error.value = exception.message
                }
        }
    }

    fun clearError() {
        _error.value = null
    }

    fun onCleared() {
        viewModelScope.cancel()
    }
}

// Koin module for ViewModels
val viewModelModule = module {
    factory {
        TaskListViewModel(
            getTasks = get(),
            createTask = get(),
            toggleTask = get(),
            deleteTask = get(),
            repository = get(),
            dispatchers = get()
        )
    }

    factory {
        TaskDetailViewModel(
            getTask = get(),
            updateTask = get(),
            deleteTask = get()
        )
    }
}
```

**2. Android Integration**
```kotlin
// androidMain/ui/TaskListScreen.kt
@Composable
fun TaskListScreen(
    viewModel: TaskListViewModel = koinViewModel()
) {
    val tasks by viewModel.tasks.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Tasks") })
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { /* Show create dialog */ }
            ) {
                Icon(Icons.Default.Add, "Add")
            }
        }
    ) { padding ->
        // UI implementation
    }
}

// Or using Hilt in Android app
@HiltViewModel
class TaskListAndroidViewModel @Inject constructor(
    private val sharedViewModel: TaskListViewModel
) : ViewModel() {
    val tasks = sharedViewModel.tasks.asLiveData()
    val isLoading = sharedViewModel.isLoading.asLiveData()
    val error = sharedViewModel.error.asLiveData()

    fun loadTasks() = sharedViewModel.loadTasks()
    fun createTask(title: String, desc: String) =
        sharedViewModel.createTask(title, desc)

    override fun onCleared() {
        super.onCleared()
        sharedViewModel.onCleared()
    }
}
```

**3. iOS Integration**
```swift
// iosApp/ViewModels/TaskListViewModelWrapper.swift
import shared

class TaskListViewModelWrapper: ObservableObject {
    private let viewModel: TaskListViewModel

    @Published var tasks: [Task] = []
    @Published var isLoading: Bool = false
    @Published var error: String? = nil

    init() {
        // Get from Koin
        viewModel = KoinHelper.getTaskListViewModel()

        // Observe StateFlows
        observeState()
    }

    private func observeState() {
        // Observe tasks
        viewModel.tasks.watch { [weak self] tasks in
            self?.tasks = tasks?.compactMap { $0 as? Task } ?? []
        }

        // Observe loading
        viewModel.isLoading.watch { [weak self] loading in
            self?.isLoading = loading?.boolValue ?? false
        }

        // Observe error
        viewModel.error.watch { [weak self] error in
            self?.error = error as? String
        }
    }

    func loadTasks(forceRefresh: Bool = false) {
        viewModel.loadTasks(forceRefresh: forceRefresh)
    }

    func createTask(title: String, description: String) {
        viewModel.createTask(title: title, description: description)
    }

    deinit {
        viewModel.onCleared()
    }
}

// Helper to get ViewModels from Koin
class KoinHelper {
    static func getTaskListViewModel() -> TaskListViewModel {
        return KoinKt.get(objCClass: TaskListViewModel.self)
    }
}
```

#### Platform-Specific Dependencies

**1. Expect/Actual with Koin**
```kotlin
// commonMain - Expect declarations
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

expect class SecureStorage {
    suspend fun saveToken(token: String)
    suspend fun getToken(): String?
    suspend fun clearToken()
}

expect class Logger {
    fun debug(tag: String, message: String)
    fun error(tag: String, message: String, throwable: Throwable?)
}

// androidMain - Actual implementations
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = TaskDatabase.Schema,
            context = context,
            name = "task.db"
        )
    }
}

actual class SecureStorage(private val context: Context) {
    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    actual suspend fun saveToken(token: String) {
        sharedPreferences.edit().putString(KEY_TOKEN, token).apply()
    }

    actual suspend fun getToken(): String? {
        return sharedPreferences.getString(KEY_TOKEN, null)
    }

    actual suspend fun clearToken() {
        sharedPreferences.edit().remove(KEY_TOKEN).apply()
    }

    companion object {
        private const val KEY_TOKEN = "auth_token"
    }
}

actual class Logger {
    actual fun debug(tag: String, message: String) {
        Log.d(tag, message)
    }

    actual fun error(tag: String, message: String, throwable: Throwable?) {
        Log.e(tag, message, throwable)
    }
}

// iosMain - Actual implementations
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = TaskDatabase.Schema,
            name = "task.db"
        )
    }
}

actual class SecureStorage {
    actual suspend fun saveToken(token: String) {
        // Save to Keychain
        val query = mapOf(
            kSecClass to kSecClassGenericPassword,
            kSecAttrAccount to "auth_token",
            kSecValueData to token.encodeToByteArray()
        )
        SecItemAdd(query as CFDictionary, null)
    }

    actual suspend fun getToken(): String? {
        // Retrieve from Keychain
        val query = mapOf(
            kSecClass to kSecClassGenericPassword,
            kSecAttrAccount to "auth_token",
            kSecReturnData to true
        )

        var result: AnyObject? = null
        val status = SecItemCopyMatching(query as CFDictionary, &result)

        return if (status == errSecSuccess) {
            (result as? NSData)?.let {
                String(it.bytes, Charsets.UTF_8)
            }
        } else {
            null
        }
    }

    actual suspend fun clearToken() {
        val query = mapOf(
            kSecClass to kSecClassGenericPassword,
            kSecAttrAccount to "auth_token"
        )
        SecItemDelete(query as CFDictionary)
    }
}

actual class Logger {
    actual fun debug(tag: String, message: String) {
        NSLog("[$tag] $message")
    }

    actual fun error(tag: String, message: String, throwable: Throwable?) {
        NSLog("[$tag] ERROR: $message ${throwable?.message ?: ""}")
    }
}
```

**2. Qualifying Platform Dependencies**
```kotlin
// Named dependencies for different implementations
val platformModule = module {
    // Android storage
    single(named("android_storage")) {
        AndroidSecureStorage(get())
    }

    // iOS storage
    single(named("ios_storage")) {
        IOSSecureStorage()
    }

    // Common interface
    single<SecureStorage> {
        when (getPlatform()) {
            Platform.ANDROID -> get(named("android_storage"))
            Platform.IOS -> get(named("ios_storage"))
            else -> throw IllegalStateException("Unsupported platform")
        }
    }
}
```

#### Comparison: Koin vs Dagger/Hilt

**1. Koin Advantages**
```kotlin
// Koin - Simple, Kotlin-first, Multiplatform

// Pros:
//  Works on all platforms (Android, iOS, Desktop, Web)
//  No code generation
//  Easy to set up
//  Runtime DI (flexible)
//  DSL-based configuration
//  Great for KMM

// Cons:
//  Runtime resolution (no compile-time safety)
//  Slightly slower than Dagger
//  Runtime errors for missing dependencies

val koinModule = module {
    single { TaskRepository(get(), get()) }
    factory { CreateTaskUseCase(get()) }
}

// Usage
class TaskViewModel(
    private val repository: TaskRepository = get(),
    private val createTask: CreateTaskUseCase = get()
) {
    // Implementation
}
```

**2. Dagger/Hilt Approach**
```kotlin
// Dagger/Hilt - Android only, compile-time safety

// Pros:
//  Compile-time verification
//  Better performance
//  Type-safe
//  No runtime overhead

// Cons:
//  Android only (doesn't work on iOS)
//  Complex setup
//  Longer build times (annotation processing)
//  Boilerplate code

// Android - Use Hilt
@HiltAndroidApp
class MyApplication : Application()

@Module
@InstallIn(SingletonComponent::class)
object SharedModule {
    @Provides
    @Singleton
    fun provideTaskRepository(
        api: TaskApi,
        database: TaskDatabase
    ): TaskRepository {
        return TaskRepositoryImpl(api, database)
    }
}

// iOS - Manual dependency injection
class IOSDependencies {
    private lazy var database: TaskDatabase = {
        TaskDatabase(DatabaseDriverFactory().createDriver())
    }()

    private lazy var api: TaskApi = {
        TaskApiService(httpClient)
    }()

    lazy var taskRepository: TaskRepository = {
        TaskRepositoryImpl(api: api, database: database)
    }()

    lazy var taskListViewModel: TaskListViewModel = {
        TaskListViewModel(
            getTasks: GetTasksUseCase(repository: taskRepository),
            createTask: CreateTaskUseCase(repository: taskRepository),
            // ... other dependencies
        )
    }()
}
```

**3. Manual DI Approach**
```kotlin
// Manual DI - Full control, no framework

// Pros:
//  Complete control
//  No framework dependency
//  Easy to understand
//  Works everywhere

// Cons:
//  Lots of boilerplate
//  Manual lifecycle management
//  No scope management
//  Tedious to maintain

class DependencyContainer {
    // Singletons
    private val httpClient by lazy {
        HttpClient { /* config */ }
    }

    private val database by lazy {
        TaskDatabase(DatabaseDriverFactory().createDriver())
    }

    val taskApi by lazy {
        TaskApiService(httpClient)
    }

    val taskRepository by lazy {
        TaskRepositoryImpl(taskApi, database)
    }

    // Factories
    fun createTaskListViewModel(): TaskListViewModel {
        return TaskListViewModel(
            getTasks = GetTasksUseCase(taskRepository),
            createTask = CreateTaskUseCase(taskRepository),
            toggleTask = ToggleTaskCompletionUseCase(taskRepository),
            deleteTask = DeleteTaskUseCase(taskRepository),
            repository = taskRepository
        )
    }
}

// Usage
val dependencies = DependencyContainer()
val viewModel = dependencies.createTaskListViewModel()
```

#### Best Practices

1. **Module Organization**:
   - Separate modules by layer (network, database, repository, usecase)
   - Use platform-specific modules for platform dependencies
   - Keep common modules platform-agnostic

2. **Scope Management**:
   - Use `single` for singletons
   - Use `factory` for new instances
   - Be careful with memory leaks

3. **Platform Dependencies**:
   - Use expect/actual for platform-specific implementations
   - Provide platform modules during initialization
   - Keep platform-specific code minimal

4. **Testing**:
   - Use Koin test extensions
   - Override modules for testing
   - Use `checkModules()` to verify dependencies

5. **Performance**:
   - Koin is fast enough for most apps
   - Use Dagger/Hilt on Android if performance is critical
   - Profile dependency resolution if needed

#### Testing with Koin

```kotlin
// commonTest
class TaskRepositoryTest : KoinTest {
    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(testModule)
    }

    private val repository: TaskRepository by inject()

    private val testModule = module {
        single<TaskApi> { mockk() }
        single<TaskDatabase> { mockk() }
        single<TaskRepository> {
            TaskRepositoryImpl(get(), get())
        }
    }

    @Test
    fun `test repository`() = runTest {
        // Test implementation
    }
}

// Verify modules
class KoinModuleTest {
    @Test
    fun `verify Koin configuration`() {
        koin {
            modules(sharedModules + androidPlatformModule)
        }.checkModules()
    }
}
```

### Summary

KMM dependency injection strategies:
- **Koin**: Best for KMM (works on all platforms, simple setup)
- **Dagger/Hilt**: Android-only (compile-time safety, better performance)
- **Manual DI**: Full control (no framework, more boilerplate)

**Recommendation**: Use Koin for KMM projects to maximize code sharing and maintain consistency across platforms. Use Dagger/Hilt on Android if you need compile-time verification and already have an Android-only codebase.

Key considerations: platform-specific dependencies via expect/actual, proper scope management, module organization, and comprehensive testing.

---

# Вопрос (RU)
> 
Объясните стратегии dependency injection для KMM проектов. Как использовать Koin для multiplatform DI? Как обрабатывать platform-specific зависимости? В чем разница между Koin, Dagger/Hilt и manual DI в KMM?

## Ответ (RU)
KMM dependency injection требует унифицированного подхода, работающего на всех платформах с поддержкой platform-specific реализаций. Koin обеспечивает наиболее seamless multiplatform DI решение.

#### Koin для KMM

**Преимущества**:
-  Работает на всех платформах
-  Нет code generation
-  Простая настройка
-  Kotlin DSL
-  Runtime DI

**Недостатки**:
-  Runtime resolution
-  Нет compile-time safety
-  Runtime errors

#### Dagger/Hilt

**Преимущества**:
-  Compile-time verification
-  Лучшая производительность
-  Type-safe

**Недостатки**:
-  Только Android
-  Не работает на iOS
-  Сложная настройка

#### Manual DI

**Преимущества**:
-  Полный контроль
-  Без framework
-  Работает везде

**Недостатки**:
-  Много boilerplate
-  Manual lifecycle
-  Трудно поддерживать

#### Platform-Specific Dependencies

**Expect/Actual**:
```kotlin
// commonMain
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

// androidMain
actual class DatabaseDriverFactory(
    private val context: Context
) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(...)
    }
}

// iosMain
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(...)
    }
}
```

**Koin модули**:
- commonMain: Shared dependencies
- androidMain: Android-specific
- iosMain: iOS-specific

#### Рекомендации

**Для KMM**: Используйте Koin
- Максимальное переиспользование кода
- Consistency на всех платформах
- Простая настройка

**Для Android-only**: Dagger/Hilt
- Compile-time safety
- Лучшая производительность

**Для простых проектов**: Manual DI
- Полный контроль
- Нет зависимостей

### Резюме

KMM DI стратегии:
- **Koin**: Лучший выбор для KMM
- **Dagger/Hilt**: Android-only, compile-time safety
- **Manual DI**: Полный контроль, больше кода

Ключевые моменты: expect/actual для platform code, правильное scope management, модульная организация, тестирование.

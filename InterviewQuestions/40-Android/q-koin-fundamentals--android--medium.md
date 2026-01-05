---
id: android-160
title: Koin Fundamentals / Основы Koin
aliases: [Koin DI, Koin Framework, Koin внедрение зависимостей, Service Locator, Основы Koin]
topic: android
subtopics: [architecture-clean, di-koin, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-clean-architecture, c-dependency-injection, c-lifecycle, q-compositionlocal-compose--android--hard, q-how-to-register-broadcastreceiver-to-receive-messages--android--medium, q-koin-scope-management--android--medium, q-koin-vs-dagger-philosophy--android--hard, q-view-fundamentals--android--easy]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/architecture-clean, android/di-koin, android/lifecycle, architecture, difficulty/medium, injection, koin, service-locator]

---
# Вопрос (RU)

> Чем Koin отличается от Dagger/Hilt? Реализуйте полный Koin модуль с определениями factory, single и viewModel.

# Question (EN)

> How does Koin differ from Dagger/Hilt? Implement a complete Koin module with factory, single, and viewModel definitions.

---

## Ответ (RU)

**Koin** — легковесный DI-фреймворк для Kotlin, использующий контейнер зависимостей с DSL и runtime-резолвингом, без code generation. Часто описывается как DI-контейнер с `Service Locator`-стилем API (получение зависимостей по типу/имени), но в типичном использовании остаётся DI через конструктор и модули. Разрешает зависимости в runtime через простой DSL.

### Koin Vs Dagger/Hilt

| Aspect | Koin | Dagger/Hilt |
|--------|------|-------------|
| **Подход** | DI-контейнер с `Service Locator`-стилем API, runtime-резолвинг | DI c compile-time графом и генерацией кода |
| **Разрешение** | Runtime | Compile-time |
| **Code Generation** | ❌ Нет | ✅ kapt/ksp |
| **Скорость сборки** | ✅ Быстрее (нет генерации кода) | ❌ Медленнее (генерация кода) |
| **Обнаружение ошибок** | ❌ В основном runtime | ✅ В основном compile-time |
| **Порог входа** | ✅ Более простой | ❌ Более высокий |
| **Производительность** | ❌ Хуже в рантайме для большого графа | ✅ Лучше (меньше overhead) |
| **Тестирование** | ✅ Гибкая конфигурация модулей | ⚠️ Требует больше boilerplate с компонентами/аннотациями |
| **Multiplatform** | ✅ Есть поддержка KMM | ⚠️ Hilt ориентирован на Android; Dagger как таковой не только для Android |

### Основные Определения

**Module** - контейнер зависимостей
**Factory** - новый экземпляр при каждом запросе
**Single** - singleton (один экземпляр на контейнер)
**`ViewModel`** - интеграция с Android `ViewModel` и её lifecycle (через артефакты `koin-androidx-viewmodel` / `koin-androidx-navigation` / `koin-androidx-compose`)

### Полная Настройка Koin

**Определения классов**:

```kotlin
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
    single<OkHttpClient> {
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                else HttpLoggingInterceptor.Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .addConverterFactory(GsonConverterFactory.create())
            .client(get())
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

    // ✅ С параметрами (требует соответствующего ViewModel)
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

**`Activity`**:

```kotlin
class UserActivity : AppCompatActivity() {
    // ✅ Lazy injection ViewModel Koin-расширением (из koin-androidx-viewmodel)
    private val viewModel: UserViewModel by viewModel()
    private val logger: Logger by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logger.log("Created")
    }
}
```

**`Fragment`**:

```kotlin
class UserFragment : Fragment() {
    // ✅ Activity scope ViewModel (из koin-androidx-viewmodel)
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
fun UserScreen() {
    val viewModel: UserViewModel = koinViewModel() // из koin-androidx-compose
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) { viewModel.loadUser("default") }

    when (val s = state) {
        UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> Text("User: ${s.data.name}")
        is UiState.Error -> Text("Error: ${s.message}", color = Color.Red)
    }
}
```

### Factory Vs Single Vs `ViewModel`

```kotlin
// Factory - новый экземпляр каждый раз
module {
    factory { MyRepository(get()) }
}
val repo1: MyRepository by inject()
val repo2: MyRepository by inject()
// repo1 !== repo2

// Single - один экземпляр (singleton в пределах Koin-контейнера)
module {
    single { MyDatabase(get()) }
}
val db1: MyDatabase by inject()
val db2: MyDatabase by inject()
// db1 === db2

// ViewModel - управляется Android ViewModelStoreOwner (через koin-androidx-viewmodel)
module {
    viewModel { MyViewModel(get()) }
}
val vm: MyViewModel by viewModel() // Переживает конфигурационные изменения в рамках owner
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
                single<UserDatabase> { mockk<UserDatabase>() }
                single<UserRepository> { UserRepositoryImpl(get(), get()) }
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
- Использовать интерфейсы для single, где это уместно
- Использовать `by inject()` для lazy initialization
- Использовать `checkModules()` для валидации конфигурации
- Использовать scopes для управления lifecycle, где требуется

**❌ DON'T:**
- Использовать factory для очень дорогих объектов (предпочтительнее single)
- Хранить `Activity` context в singleton (утечки памяти)
- Избыточно инжектить простые значения, которые проще передать явно
- Забывать вызывать `startKoin()` до первого использования

### Когда Выбирать Koin

**✅ Koin:**
- Kotlin Multiplatform проекты
- Важна скорость сборки и простота конфигурации
- Команда новичок в DI или не хочет сложного codegen-пайплайна
- Малый/средний проект
- Нужна гибкость runtime-конфигурации

**✅ Dagger/Hilt:**
- Критична compile-time безопасность графа
- Требуется максимальная runtime-производительность
- Большая кодовая база
- Команда опытна с Dagger
- Проект ориентирован на Android и хорошо вписывается в Hilt

---

## Answer (EN)

**Koin** is a lightweight DI framework for Kotlin that uses a dependency container with a Kotlin DSL and runtime resolution instead of code generation. It is often described as a DI container with a `Service Locator`-style API (retrieving by type/name), but in typical usage it is still constructor-injection driven via modules. Dependencies are resolved at runtime via a simple DSL.

### Koin Vs Dagger/Hilt

| Aspect | Koin | Dagger/Hilt |
|--------|------|-------------|
| **Approach** | DI container with `Service Locator`-style API, runtime resolution | DI with compile-time graph and code generation |
| **Resolution** | Runtime | Compile-time |
| **Code Generation** | ❌ None | ✅ kapt/ksp |
| **Build Speed** | ✅ Faster (no codegen) | ❌ Slower (codegen) |
| **Error Detection** | ❌ Mostly runtime | ✅ Mostly compile-time |
| **Learning Curve** | ✅ Gentler | ❌ Steeper |
| **Performance** | ❌ More overhead for large graphs | ✅ Less overhead, faster in practice |
| **Testing** | ✅ Flexible module redefinition | ⚠️ Requires more boilerplate with components/annotations |
| **Multiplatform** | ✅ KMM support available | ⚠️ Hilt is Android-focused; Dagger itself is not Android-only |

### Core Definitions

**Module** - dependency container
**Factory** - new instance on each request
**Single** - singleton instance per Koin container
**`ViewModel`** - Android `ViewModel` integration with lifecycle awareness (via `koin-androidx-viewmodel` / `koin-androidx-navigation` / `koin-androidx-compose` artifacts)

### Complete Koin Setup

**Class definitions**:

```kotlin
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
    single<OkHttpClient> {
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                else HttpLoggingInterceptor.Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .addConverterFactory(GsonConverterFactory.create())
            .client(get())
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

    // ✅ With parameters (requires corresponding ViewModel implementation)
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

**`Activity`**:

```kotlin
class UserActivity : AppCompatActivity() {
    // ✅ Lazy injection via Koin ViewModel extension (from koin-androidx-viewmodel)
    private val viewModel: UserViewModel by viewModel()
    private val logger: Logger by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        logger.log("Created")
    }
}
```

**`Fragment`**:

```kotlin
class UserFragment : Fragment() {
    // ✅ Activity scope ViewModel (from koin-androidx-viewmodel)
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
fun UserScreen() {
    val viewModel: UserViewModel = koinViewModel() // from koin-androidx-compose
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) { viewModel.loadUser("default") }

    when (val s = state) {
        UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> Text("User: ${s.data.name}")
        is UiState.Error -> Text("Error: ${s.message}", color = Color.Red)
    }
}
```

### Factory Vs Single Vs `ViewModel`

```kotlin
// Factory - new instance every time
module {
    factory { MyRepository(get()) }
}
val repo1: MyRepository by inject()
val repo2: MyRepository by inject()
// repo1 !== repo2

// Single - one instance (singleton within Koin container)
module {
    single { MyDatabase(get()) }
}
val db1: MyDatabase by inject()
val db2: MyDatabase by inject()
// db1 === db2

// ViewModel - managed by Android ViewModelStoreOwner (via koin-androidx-viewmodel)
module {
    viewModel { MyViewModel(get()) }
}
val vm: MyViewModel by viewModel() // Survives configuration changes for its owner
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
                single<UserDatabase> { mockk<UserDatabase>() }
                single<UserRepository> { UserRepositoryImpl(get(), get()) }
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
- Use interfaces for singles where appropriate
- Use `by inject()` for lazy initialization
- Use `checkModules()` to validate configuration
- Use scopes for lifecycle management when needed

**❌ DON'T:**
- Use factory for very expensive objects (prefer single)
- Store `Activity` context in singletons (memory leak risk)
- Overuse DI for trivial values better passed explicitly
- Forget to call `startKoin()` before first usage

### When to Choose Koin

**✅ Koin:**
- Kotlin Multiplatform projects
- Fast build times and simple configuration are important
- Team is new to DI or wants to avoid complex codegen pipelines
- Small/medium projects
- Need runtime configuration flexibility

**✅ Dagger/Hilt:**
- Compile-time safety of the graph is critical
- Maximum runtime performance is required
- Large codebase
- Team is experienced with Dagger
- Android-focused project that fits well with Hilt

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

### Prerequisites / Concepts

- [[c-clean-architecture]]
- [[c-lifecycle]]
- [[c-dependency-injection]]

### Prerequisites (Easier)
- [[q-what-is-viewmodel--android--medium]]

### Related (Same Level)
- [[q-compositionlocal-compose--android--hard]]
- [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]]

### Advanced (Harder)
- [[q-recomposition-choreographer--android--hard]]

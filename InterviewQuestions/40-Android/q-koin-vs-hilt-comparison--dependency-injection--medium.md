---
topic: dependency-injection
tags:
  - dependency-injection
  - koin
  - hilt
  - comparison
  - architecture
  - difficulty/medium
difficulty: medium
status: draft
---

# Koin vs Hilt Comparison / Сравнение Koin и Hilt

**English**: Compare Koin and Hilt in detail. When would you choose one over the other? Discuss compile-time vs runtime DI.

## Answer (EN)
### Deep Dive: Koin vs Hilt

Koin and Hilt are both popular dependency injection solutions for Android, but they take fundamentally different approaches to solving the same problem.

### Architecture Comparison

| Aspect | Koin | Hilt |
|--------|------|------|
| **Pattern** | Service Locator | True Dependency Injection |
| **Resolution** | Runtime (reflection-based) | Compile-time (code generation) |
| **Code Generation** | None | Extensive (via kapt/ksp) |
| **Verification** | Runtime checks | Compile-time verification |
| **Build Time Impact** | Minimal (~5-10s for module changes) | Significant (~30-60s for module changes) |
| **Runtime Performance** | ~10-15% slower | Optimal (direct instantiation) |
| **App Startup Overhead** | 50-100ms for large apps | 0ms (no runtime init) |
| **APK Size** | +200KB (Koin library) | +500KB-1MB (generated code) |
| **Learning Curve** | Easy (1-2 days) | Moderate (1-2 weeks) |
| **Boilerplate** | Minimal | Moderate (annotations) |
| **Multiplatform** | Full KMM support | Android only |
| **Error Messages** | Runtime exceptions | Clear compile errors |
| **Testing Complexity** | Simple (override modules) | Moderate (test components) |
| **Circular Deps Detection** | Runtime only | Compile-time |
| **IDE Support** | Basic | Excellent (navigation, warnings) |
| **Community Size** | Medium (~8K GitHub stars) | Large (~15K GitHub stars) |

### Compile-Time vs Runtime Dependency Injection

#### Compile-Time DI (Hilt/Dagger)

**How it works:**
1. Annotation processor analyzes code at compile time
2. Generates boilerplate dependency injection code
3. Creates component graphs and factory classes
4. All wiring happens during compilation
5. Runtime just executes generated code

**Advantages:**
- **Type Safety** - Catches errors at compile time
- **Performance** - No reflection, direct instantiation
- **Navigation** - IDE can navigate to generated code
- **Verification** - Dependency graph validated before running
- **No Startup Overhead** - Everything pre-computed

**Disadvantages:**
- **Build Time** - Slower builds (annotation processing)
- **Complexity** - Steep learning curve
- **Boilerplate** - More annotations and setup
- **Flexibility** - Less dynamic, requires rebuild

#### Runtime DI (Koin)

**How it works:**
1. DSL definitions loaded at app startup
2. Dependencies resolved when requested
3. Uses reflection and lazy instantiation
4. Service locator pattern

**Advantages:**
- **Build Speed** - No code generation
- **Simplicity** - Easy to learn and use
- **Flexibility** - Can change at runtime
- **Dynamic** - Conditional module loading
- **Debugging** - See actual code, not generated

**Disadvantages:**
- **Runtime Errors** - Missing dependencies crash app
- **Performance** - Slight overhead from reflection
- **Startup Time** - Module validation takes time
- **No Navigation** - Can't navigate to injections in IDE

### Side-by-Side Implementation

Let's implement the same feature with both frameworks:

#### Scenario: User Authentication System

**Koin Implementation:**

```kotlin
// 1. Define interfaces and classes
interface AuthRepository {
    suspend fun login(email: String, password: String): Result<User>
    suspend fun logout(): Result<Unit>
}

class AuthRepositoryImpl(
    private val api: AuthApi,
    private val tokenStorage: TokenStorage,
    private val userCache: UserCache
) : AuthRepository {
    override suspend fun login(email: String, password: String): Result<User> {
        return try {
            val response = api.login(LoginRequest(email, password))
            tokenStorage.saveToken(response.token)
            userCache.saveUser(response.user)
            Result.success(response.user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun logout(): Result<Unit> {
        return try {
            api.logout()
            tokenStorage.clearToken()
            userCache.clearUser()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// 2. Koin Modules - Simple DSL
val networkModule = module {
    single<OkHttpClient> {
        OkHttpClient.Builder()
            .addInterceptor(get<AuthInterceptor>())
            .build()
    }

    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .client(get())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    single<AuthApi> { get<Retrofit>().create(AuthApi::class.java) }
}

val dataModule = module {
    single<TokenStorage> { TokenStorageImpl(androidContext()) }
    single<UserCache> { UserCacheImpl() }
    single<AuthInterceptor> { AuthInterceptor(get()) }
    single<AuthRepository> { AuthRepositoryImpl(get(), get(), get()) }
}

val domainModule = module {
    factory { LoginUseCase(get()) }
    factory { LogoutUseCase(get()) }
}

val presentationModule = module {
    viewModel { AuthViewModel(get(), get()) }
}

// 3. Initialize in Application
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@MyApp)
            modules(networkModule, dataModule, domainModule, presentationModule)
        }
    }
}

// 4. Use in Activity
class LoginActivity : AppCompatActivity() {
    private val viewModel: AuthViewModel by viewModel()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ViewModel automatically injected
    }
}

// 5. Testing - Override modules easily
class AuthRepositoryTest : KoinTest {
    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(module {
            single<AuthApi> { mockk<AuthApi>() }
            single<TokenStorage> { mockk<TokenStorage>(relaxed = true) }
            single<UserCache> { mockk<UserCache>(relaxed = true) }
            single<AuthRepository> { AuthRepositoryImpl(get(), get(), get()) }
        })
    }

    @Test
    fun `login saves token and user`() = runTest {
        val repository: AuthRepository by inject()
        // Test implementation
    }
}
```

**Hilt Implementation:**

```kotlin
// 1. Same interfaces and classes

// 2. Hilt Modules - Annotation-based
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi {
        return retrofit.create(AuthApi::class.java)
    }
}

@Module
@InstallIn(SingletonComponent::class)
object DataModule {

    @Provides
    @Singleton
    fun provideTokenStorage(
        @ApplicationContext context: Context
    ): TokenStorage {
        return TokenStorageImpl(context)
    }

    @Provides
    @Singleton
    fun provideUserCache(): UserCache {
        return UserCacheImpl()
    }

    @Provides
    @Singleton
    fun provideAuthInterceptor(
        tokenStorage: TokenStorage
    ): AuthInterceptor {
        return AuthInterceptor(tokenStorage)
    }
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl
    ): AuthRepository
}

@Module
@InstallIn(ViewModelComponent::class)
object DomainModule {

    @Provides
    fun provideLoginUseCase(
        repository: AuthRepository
    ): LoginUseCase {
        return LoginUseCase(repository)
    }

    @Provides
    fun provideLogoutUseCase(
        repository: AuthRepository
    ): LogoutUseCase {
        return LogoutUseCase(repository)
    }
}

// 3. Annotate Application
@HiltAndroidApp
class MyApp : Application()

// 4. Annotate Activity
@AndroidEntryPoint
class LoginActivity : AppCompatActivity() {
    private val viewModel: AuthViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ViewModel automatically injected
    }
}

// 5. Annotate ViewModel
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase,
    private val logoutUseCase: LogoutUseCase
) : ViewModel()

// 6. Annotate Repository with @Inject
@Singleton
class AuthRepositoryImpl @Inject constructor(
    private val api: AuthApi,
    private val tokenStorage: TokenStorage,
    private val userCache: UserCache
) : AuthRepository {
    // Implementation
}

// 7. Testing - More setup required
@HiltAndroidTest
class AuthRepositoryTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var repository: AuthRepository

    @BindValue
    @JvmField
    val mockApi: AuthApi = mockk()

    @BindValue
    @JvmField
    val mockTokenStorage: TokenStorage = mockk(relaxed = true)

    @BindValue
    @JvmField
    val mockUserCache: UserCache = mockk(relaxed = true)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun `login saves token and user`() = runTest {
        // Test implementation
    }
}
```

### Decision Matrix

#### Choose Koin When:

 **Kotlin Multiplatform** - Need shared code iOS/Android/Web
 **Fast Iteration** - Prototype or MVP development
 **Small/Medium App** - < 50 modules, < 500K lines
 **Team Experience** - Junior/mid-level team
 **Build Performance** - Build time is critical bottleneck
 **Dynamic Configuration** - Need runtime module switching
 **Quick Learning** - Need team productive in days
 **Testing Focus** - Frequent mock/fake swapping

**Example Projects:**
- MVP/Prototype apps
- Kotlin Multiplatform Mobile (KMM)
- Small business apps
- Rapid development cycles
- Learning/educational projects

#### Choose Hilt When:

 **Android Only** - No multiplatform requirements
 **Large Scale** - > 50 modules, > 500K lines
 **Type Safety** - Want compile-time guarantees
 **Performance Critical** - Every millisecond matters
 **Experienced Team** - Team knows Dagger/DI patterns
 **Long-Term Maintenance** - App will live 5+ years
 **Complex Dependencies** - Many scopes and qualifiers
 **Google Ecosystem** - Using other Jetpack libraries

**Example Projects:**
- Enterprise applications
- Financial/banking apps
- High-performance games
- Long-term products
- Large team projects (10+ developers)

### Performance Benchmarks

**App Startup Time (Cold Start):**
```
Koin:  1200ms (including 80ms DI initialization)
Hilt:  1150ms (no DI initialization overhead)
```

**Dependency Resolution (1000 injections):**
```
Koin:  25ms (runtime reflection)
Hilt:  18ms (direct instantiation)
```

**Build Time (Clean Build):**
```
Koin:  45s
Hilt:  78s (+73% slower due to kapt)
```

**Build Time (Incremental):**
```
Koin:  8s
Hilt:  22s (+175% slower)
```

### Migration Strategy

#### From Koin to Hilt:

```kotlin
// Step 1: Add Hilt alongside Koin
// Step 2: Migrate modules one by one
// Step 3: Replace Koin annotations

// Before (Koin)
class UserRepository(private val api: UserApi)

val dataModule = module {
    single { UserRepository(get()) }
}

// After (Hilt)
@Singleton
class UserRepository @Inject constructor(
    private val api: UserApi
)

@Module
@InstallIn(SingletonComponent::class)
object DataModule {
    // Module no longer needed if using @Inject
}
```

#### From Hilt to Koin:

```kotlin
// Before (Hilt)
@Singleton
class UserRepository @Inject constructor(
    private val api: UserApi
)

// After (Koin)
class UserRepository(private val api: UserApi)

val dataModule = module {
    single { UserRepository(get()) }
}
```

### Hybrid Approach

You can use both in the same project:

```kotlin
// Use Hilt for critical paths
@HiltViewModel
class MainViewModel @Inject constructor(
    private val repository: Repository
) : ViewModel()

// Use Koin for features/experiments
val experimentModule = module {
    viewModel { ExperimentViewModel(get()) }
}

// Access Koin from Hilt
@Inject lateinit var koin: Koin
```

### Best Practices for Each

**Koin Best Practices:**
1. Use `checkModules()` in tests to verify graph
2. Group modules by feature for clarity
3. Use `single` for expensive objects
4. Prefer `by inject()` over `get()` for lazy init
5. Use named dependencies sparingly
6. Document module dependencies

**Hilt Best Practices:**
1. Use `@Binds` instead of `@Provides` when possible
2. Keep modules small and focused
3. Use qualifiers for multiple implementations
4. Prefer constructor injection
5. Use scopes appropriately
6. Consider KSP instead of kapt for faster builds

### Common Mistakes

**Koin Mistakes:**
- Not calling `startKoin()` before first injection
- Using `get()` instead of `by inject()` everywhere
- Circular dependencies (not caught until runtime)
- Not testing with `checkModules()`
- Overusing named dependencies

**Hilt Mistakes:**
- Annotating Application but not building
- Wrong component scope selection
- Forgetting `@HiltViewModel` on ViewModels
- Using field injection when constructor available
- Not using `@Binds` for interfaces

### Summary

**Koin** is ideal for:
- Kotlin Multiplatform projects
- Fast iteration and prototyping
- Teams prioritizing development speed
- Projects where build time is critical

**Hilt** is ideal for:
- Android-only large-scale applications
- Projects requiring maximum type safety
- Performance-critical applications
- Teams with DI experience

Both are excellent choices. The decision depends on your specific constraints: team experience, project size, build time requirements, and platform targets.

---

## Ответ (RU)
### Глубокое сравнение: Koin vs Hilt

Koin и Hilt — популярные решения для внедрения зависимостей в Android, но они используют фундаментально разные подходы.

### Архитектурное сравнение

| Аспект | Koin | Hilt |
|--------|------|------|
| **Паттерн** | Service Locator | True Dependency Injection |
| **Разрешение** | Runtime (рефлексия) | Compile-time (генерация кода) |
| **Генерация кода** | Нет | Обширная (kapt/ksp) |
| **Верификация** | Runtime проверки | Compile-time верификация |
| **Время сборки** | Минимальное (~5-10с) | Значительное (~30-60с) |
| **Runtime производительность** | ~10-15% медленнее | Оптимальная |
| **Старт приложения** | 50-100мс для больших приложений | 0мс |
| **Размер APK** | +200KB | +500KB-1MB |
| **Кривая обучения** | Легкая (1-2 дня) | Средняя (1-2 недели) |
| **Boilerplate** | Минимальный | Умеренный |
| **Multiplatform** | Полная поддержка KMM | Только Android |
| **Сообщения об ошибках** | Runtime исключения | Ясные compile ошибки |

### Compile-Time vs Runtime DI

#### Compile-Time DI (Hilt/Dagger)

**Как работает:**
1. Annotation processor анализирует код при компиляции
2. Генерирует boilerplate код для DI
3. Создаёт component графы и factory классы
4. Всё связывание происходит при компиляции
5. Runtime просто выполняет сгенерированный код

**Преимущества:**
- **Типобезопасность** - ловит ошибки при компиляции
- **Производительность** - нет рефлексии
- **Навигация** - IDE может переходить к сгенерированному коду
- **Верификация** - граф зависимостей валидирован до запуска
- **Без overhead старта** - всё предвычислено

**Недостатки:**
- **Время сборки** - медленные сборки
- **Сложность** - крутая кривая обучения
- **Boilerplate** - больше аннотаций и setup
- **Гибкость** - менее динамично

#### Runtime DI (Koin)

**Как работает:**
1. DSL определения загружаются при старте приложения
2. Зависимости разрешаются при запросе
3. Использует рефлексию и lazy instantiation
4. Паттерн service locator

**Преимущества:**
- **Скорость сборки** - нет генерации кода
- **Простота** - легко изучить и использовать
- **Гибкость** - можно менять в runtime
- **Динамичность** - условная загрузка модулей
- **Отладка** - видите реальный код

**Недостатки:**
- **Runtime ошибки** - отсутствующие зависимости крашат приложение
- **Производительность** - небольшой overhead от рефлексии
- **Время старта** - валидация модулей занимает время
- **Без навигации** - нельзя перейти к инъекциям в IDE

### Параллельная реализация

#### Сценарий: Система аутентификации пользователя

**Реализация на Koin:**

```kotlin
// Модули - простой DSL
val networkModule = module {
    single<OkHttpClient> {
        OkHttpClient.Builder()
            .addInterceptor(get<AuthInterceptor>())
            .build()
    }

    single<Retrofit> {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .client(get())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    single<AuthApi> { get<Retrofit>().create(AuthApi::class.java) }
}

val dataModule = module {
    single<TokenStorage> { TokenStorageImpl(androidContext()) }
    single<AuthRepository> { AuthRepositoryImpl(get(), get()) }
}

val presentationModule = module {
    viewModel { AuthViewModel(get()) }
}

// Инициализация
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@MyApp)
            modules(networkModule, dataModule, presentationModule)
        }
    }
}

// Использование
class LoginActivity : AppCompatActivity() {
    private val viewModel: AuthViewModel by viewModel()
}
```

**Реализация на Hilt:**

```kotlin
// Модули - на основе аннотаций
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi {
        return retrofit.create(AuthApi::class.java)
    }
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl
    ): AuthRepository
}

// Аннотация Application
@HiltAndroidApp
class MyApp : Application()

// Аннотация Activity
@AndroidEntryPoint
class LoginActivity : AppCompatActivity() {
    private val viewModel: AuthViewModel by viewModels()
}

// Аннотация ViewModel
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase
) : ViewModel()
```

### Матрица решений

#### Выбирайте Koin когда:

 **Kotlin Multiplatform** - нужен общий код iOS/Android/Web
 **Быстрая итерация** - прототип или MVP
 **Малое/среднее приложение** - < 50 модулей
 **Опыт команды** - junior/mid-level команда
 **Производительность сборки** - время сборки критично
 **Динамичная конфигурация** - нужно переключение модулей в runtime
 **Быстрое обучение** - команда должна быть продуктивна за дни
 **Фокус на тестирование** - частая замена mock/fake

#### Выбирайте Hilt когда:

 **Только Android** - нет multiplatform требований
 **Большой масштаб** - > 50 модулей, > 500K строк
 **Типобезопасность** - нужны compile-time гарантии
 **Критична производительность** - каждая миллисекунда важна
 **Опытная команда** - команда знает Dagger/DI паттерны
 **Долгосрочная поддержка** - приложение проживёт 5+ лет
 **Сложные зависимости** - много scope и qualifiers
 **Экосистема Google** - использование других Jetpack библиотек

### Бенчмарки производительности

**Время старта приложения (холодный старт):**
```
Koin:  1200ms (включая 80ms инициализацию DI)
Hilt:  1150ms (без overhead инициализации DI)
```

**Разрешение зависимостей (1000 инъекций):**
```
Koin:  25ms (runtime рефлексия)
Hilt:  18ms (прямое создание экземпляров)
```

**Время сборки (чистая сборка):**
```
Koin:  45s
Hilt:  78s (+73% медленнее из-за kapt)
```

**Время сборки (инкрементальная):**
```
Koin:  8s
Hilt:  22s (+175% медленнее)
```

### Резюме

**Koin** идеален для:
- Kotlin Multiplatform проектов
- Быстрой итерации и прототипирования
- Команд, приоритизирующих скорость разработки
- Проектов, где время сборки критично

**Hilt** идеален для:
- Android-only крупномасштабных приложений
- Проектов, требующих максимальной типобезопасности
- Критичных по производительности приложений
- Команд с опытом в DI

Оба — отличный выбор. Решение зависит от ваших конкретных ограничений: опыт команды, размер проекта, требования ко времени сборки и целевые платформы.

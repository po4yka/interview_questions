---
tags:
  - android
  - android/dependency-injection
  - dagger
  - dependency-injection
  - hilt
  - inject
difficulty: easy
---

# Как сообщить Dagger, что мы собираемся что-то инжектить?

**English**: How to tell Dagger we're going to inject something?

## Answer

Use **`@Inject`** annotation on:

1. **Constructor** - For class creation
2. **Fields** - For property injection
3. **Methods** - For setter injection

If custom creation logic is needed, use **`@Provides`** in a `@Module`.

---

## @Inject on Constructor (Recommended)

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDatabase
) {
    fun getUser(id: String): User {
        return database.getUser(id) ?: api.fetchUser(id)
    }
}
```

**Dagger automatically:**
- Creates `UserRepository` instances
- Resolves `ApiService` and `UserDatabase` dependencies
- Injects them into constructor

---

## @Inject on Fields

### In Activity/Fragment

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var repository: UserRepository

    @Inject
    lateinit var analytics: AnalyticsService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Fields injected automatically by Hilt

        repository.getUser("123")
    }
}
```

### In ViewModel

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Constructor injection preferred for ViewModels
}
```

---

## @Inject on Methods

```kotlin
class Presenter @Inject constructor() {

    private lateinit var repository: UserRepository

    @Inject
    fun setRepository(repository: UserRepository) {
        this.repository = repository
    }
}
```

**Note:** Method injection happens AFTER constructor injection.

---

## When to Use @Provides (Module)

When you **can't modify** the class or need **custom creation logic**:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
```

**Use @Provides when:**
- Third-party library (Retrofit, Room, OkHttp)
- Interface binding
- Complex initialization logic
- Multiple configurations of same type

---

## Complete Example

### 1. Constructor Injection

```kotlin
// Simple class
class Logger @Inject constructor() {
    fun log(message: String) {
        println(message)
    }
}

// With dependencies
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDatabase,
    private val logger: Logger
) {
    fun getUser(id: String): User {
        logger.log("Fetching user $id")
        return database.getUser(id) ?: api.fetchUser(id)
    }
}
```

### 2. Field Injection in Activity

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Use injected dependency
        lifecycleScope.launch {
            val user = repository.getUser("123")
            textView.text = user.name
        }
    }
}
```

### 3. Module for Third-Party

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(
        @ApplicationContext context: Context
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

---

## Comparison

| Method | Use Case | Example |
|--------|----------|---------|
| **@Inject constructor** | Your own classes | `class Repository @Inject constructor()` |
| **@Inject field** | Android components (Activity, Fragment) | `@Inject lateinit var repository: Repository` |
| **@Inject method** | Optional dependencies | `@Inject fun setLogger(logger: Logger)` |
| **@Provides** | Third-party or complex logic | `@Provides fun provideRetrofit(): Retrofit` |

---

## Hilt Entry Points

For non-Android classes that need injection:

```kotlin
@EntryPoint
@InstallIn(SingletonComponent::class)
interface RepositoryProvider {
    fun repository(): UserRepository
}

class MyWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {

    override fun doWork(): Result {
        val appContext = applicationContext.applicationContext
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            RepositoryProvider::class.java
        )

        val repository = entryPoint.repository()

        repository.syncData()

        return Result.success()
    }
}
```

---

## Best Practices

### ✅ DO: Constructor Injection

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService
) {
    // Dependencies clear and testable
}
```

### ❌ DON'T: Field Injection for Regular Classes

```kotlin
// ❌ BAD
class UserRepository {
    @Inject lateinit var api: ApiService // Hard to test
}

// ✅ GOOD
class UserRepository @Inject constructor(
    private val api: ApiService
)
```

### ✅ DO: Use @Provides for Interfaces

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository
}
```

---

## Summary

**How to tell Dagger to inject:**

1. **@Inject on constructor** (preferred)
   ```kotlin
   class Repository @Inject constructor(private val api: ApiService)
   ```

2. **@Inject on fields** (for Android components)
   ```kotlin
   @AndroidEntryPoint
   class MainActivity : AppCompatActivity() {
       @Inject lateinit var repository: Repository
   }
   ```

3. **@Provides in @Module** (for third-party or custom logic)
   ```kotlin
   @Provides
   fun provideRetrofit(): Retrofit { ... }
   ```

**Best practice:** Prefer constructor injection for testability and clarity.

---

## Ответ

Используйте аннотацию **`@Inject`** на:

1. **Конструкторе** - для создания класса
2. **Полях** - для инъекции свойств
3. **Методах** - для setter-инъекции

Если нужна кастомная логика создания, используйте **`@Provides`** в `@Module`.

**Примеры:**

```kotlin
// 1. Конструктор (рекомендуется)
class Repository @Inject constructor(
    private val api: ApiService
)

// 2. Поля (для Activity/Fragment)
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: Repository
}

// 3. Module (для сторонних библиотек)
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    fun provideRetrofit(): Retrofit { ... }
}
```

**Лучшая практика:** Используйте constructor injection для тестируемости.


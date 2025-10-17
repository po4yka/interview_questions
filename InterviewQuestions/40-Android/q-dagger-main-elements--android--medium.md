---
id: "20251015082237395"
title: "Dagger Main Elements / Основные элементы Dagger"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/di-hilt, dagger, dependency-injection, di-hilt, platform/android, difficulty/medium]
---
# Из каких основных элементов состоит Dagger?

**English**: What are the main elements of Dagger?

## Answer (EN)
Dagger is built around several core elements that work together to provide dependency injection. The main components are:

### 1. Component (@Component)

**Component** is an interface that connects modules and injection targets. It defines:
- Which dependencies can be provided
- Which classes can receive injections
- How to access specific dependencies

**Example:**

```kotlin
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {
    // Provision methods - expose dependencies
    fun provideRepository(): UserRepository

    // Injection methods - inject dependencies into targets
    fun inject(activity: MainActivity)
    fun inject(fragment: ProfileFragment)

    @Component.Builder
    interface Builder {
        @BindsInstance
        fun application(app: Application): Builder
        fun build(): AppComponent
    }
}
```

**Usage:**

```kotlin
class MyApplication : Application() {
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.builder()
            .application(this)
            .build()
    }
}

class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApplication).appComponent.inject(this)
        // repository is now injected
    }
}
```

### 2. Module (@Module)

**Module** is a class that provides dependencies. It contains methods annotated with `@Provides` or `@Binds` that tell Dagger how to create specific objects.

**Example with @Provides:**

```kotlin
@Module
class NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
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

**Example with @Binds (for interfaces):**

```kotlin
@Module
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository

    @Binds
    abstract fun bindDataSource(
        impl: RemoteDataSource
    ): DataSource
}
```

### 3. Scope (@Scope)

**Scope** annotations manage the lifetime of dependencies. They ensure that within a scope, the same instance is reused.

**Common scopes:**

```kotlin
// Built-in scope
@Singleton  // One instance for entire app

// Custom scopes
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FragmentScope

@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class PerUser
```

**Usage:**

```kotlin
@Module
class AppModule {
    @Provides
    @Singleton  // Single instance app-wide
    fun provideDatabase(app: Application): AppDatabase {
        return Room.databaseBuilder(
            app,
            AppDatabase::class.java,
            "app-database"
        ).build()
    }
}

@Component(modules = [ActivityModule::class])
@ActivityScope
interface ActivityComponent {
    fun inject(activity: MainActivity)
}

@Module
class ActivityModule {
    @Provides
    @ActivityScope  // Single instance per activity
    fun provideViewModel(repository: Repository): MainViewModel {
        return MainViewModel(repository)
    }
}
```

### 4. @Inject

**@Inject** marks where dependencies should be injected. It can be used on:
- Constructor (preferred)
- Field
- Method

**Constructor injection (recommended):**

```kotlin
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val database: UserDao,
    private val preferences: SharedPreferences
) {
    suspend fun getUser(id: String): User {
        return apiService.getUser(id)
    }
}
```

**Field injection:**

```kotlin
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
    @Inject lateinit var viewModelFactory: ViewModelFactory

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApplication).appComponent.inject(this)
    }
}
```

### 5. Qualifier (@Qualifier)

**Qualifier** annotations distinguish between different instances of the same type.

**Example:**

```kotlin
@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class AuthInterceptor

@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class LoggingInterceptor

@Module
class NetworkModule {
    @Provides
    @AuthInterceptor
    fun provideAuthInterceptor(tokenManager: TokenManager): Interceptor {
        return Interceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Authorization", "Bearer ${tokenManager.getToken()}")
                .build()
            chain.proceed(request)
        }
    }

    @Provides
    @LoggingInterceptor
    fun provideLoggingInterceptor(): Interceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }

    @Provides
    fun provideOkHttpClient(
        @AuthInterceptor authInterceptor: Interceptor,
        @LoggingInterceptor loggingInterceptor: Interceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .build()
    }
}
```

**Using @Named (built-in qualifier):**

```kotlin
@Module
class AppModule {
    @Provides
    @Named("app_name")
    fun provideAppName(): String = "My App"

    @Provides
    @Named("api_key")
    fun provideApiKey(): String = BuildConfig.API_KEY
}

class SomeClass @Inject constructor(
    @Named("app_name") private val appName: String,
    @Named("api_key") private val apiKey: String
)
```

### Complete Example

```kotlin
// 1. Define scopes
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {
    fun activityComponent(): ActivityComponent.Factory
}

@Module
class AppModule(private val app: Application) {
    @Provides
    @Singleton
    fun provideApplication(): Application = app

    @Provides
    @Singleton
    fun provideSharedPreferences(app: Application): SharedPreferences {
        return app.getSharedPreferences("prefs", Context.MODE_PRIVATE)
    }
}

@Module
class NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

// 2. Activity scope component
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    fun inject(activity: MainActivity)

    @Subcomponent.Factory
    interface Factory {
        fun create(): ActivityComponent
    }
}

@Module
class ActivityModule {
    @Provides
    @ActivityScope
    fun provideAdapter(): UserAdapter {
        return UserAdapter()
    }
}

// 3. Application
class MyApplication : Application() {
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.builder()
            .appModule(AppModule(this))
            .build()
    }
}

// 4. Usage
class MainActivity : AppCompatActivity() {
    @Inject lateinit var apiService: ApiService
    @Inject lateinit var adapter: UserAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        (application as MyApplication)
            .appComponent
            .activityComponent()
            .create()
            .inject(this)

        // Dependencies are now injected
    }
}
```

### Summary

| Element | Purpose | Example |
|---------|---------|---------|
| **@Component** | Connects modules and injection targets | `@Component(modules = [AppModule::class])` |
| **@Module** | Provides dependencies | `@Module class NetworkModule` |
| **@Provides** | Method that creates dependency | `@Provides fun provideRetrofit()` |
| **@Binds** | Binds interface to implementation | `@Binds abstract fun bindRepo(impl: RepoImpl): Repo` |
| **@Inject** | Marks injection points | `@Inject lateinit var repo: Repository` |
| **@Scope** | Controls instance lifetime | `@Singleton`, `@ActivityScope` |
| **@Qualifier** | Distinguishes same-type dependencies | `@Named("api_key")` |

**Key concepts:**
- **Component** = bridge between modules and injection targets
- **Module** = provides dependencies
- **Scope** = controls lifetime
- **@Inject** = marks what to inject
- **Qualifier** = differentiates same types

## Ответ (RU)
Dagger состоит из нескольких основных элементов:

### 1. Component (@Component)

**Component** - интерфейс, связывающий модули и цели инъекции. Определяет, какие зависимости могут быть предоставлены.

```kotlin
@Component(modules = [NetworkModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}
```

### 2. Module (@Module)

**Module** - класс, предоставляющий зависимости через методы с аннотацией `@Provides` или `@Binds`.

```kotlin
@Module
class NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
    }
}
```

### 3. Scope (@Scope)

**Scope** - аннотации для управления временем жизни объектов.

```kotlin
@Singleton  // Один экземпляр на всё приложение
@ActivityScope  // Один экземпляр на Activity
```

### 4. @Inject

Отмечает места, куда нужно внедрить зависимости.

```kotlin
class UserRepository @Inject constructor(
    private val apiService: ApiService
)
```

### 5. Qualifier (@Qualifier)

Различает разные экземпляры одного типа.

```kotlin
@Named("auth_interceptor")
@Provides
fun provideAuthInterceptor(): Interceptor
```

**Резюме:** Component соединяет модули и цели инъекции, Module предоставляет зависимости, Scope контролирует время жизни, @Inject отмечает точки инъекции, Qualifier различает одинаковые типы.


---
id: android-199
title: "Hilt / Фреймворк Hilt"
aliases: [Hilt, Фреймворк Hilt]
topic: android
subtopics: [architecture-mvvm, di-hilt]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, c-hilt, q-test-doubles-dependency-injection--testing--medium, q-what-is-known-about-recyclerview--android--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [android/architecture-mvvm, android/di-hilt, dependency-injection, di, difficulty/medium, hilt]
date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# What is Hilt?

**Russian**: Что такое Hilt и для чего он используется?

## Answer (EN)
**Hilt** is a dependency injection (DI) framework developed by Google specifically for Android. It's built on top of **Dagger** and designed to simplify dependency injection setup in Android applications by reducing boilerplate code and providing standardized patterns for Android components.

### What is Dependency Injection?

Dependency Injection is a design pattern where objects receive their dependencies from external sources rather than creating them internally.

```kotlin
// Without DI (bad)
class UserViewModel {
    private val repository = UserRepository() // Hard-coded dependency

    fun getUser() = repository.fetchUser()
}

// With DI (good)
class UserViewModel(
    private val repository: UserRepository // Injected dependency
) {
    fun getUser() = repository.fetchUser()
}
```

### Why Hilt?

Before Hilt, setting up Dagger in Android required significant boilerplate:
- Manual component creation
- Component lifecycle management
- Scoping to Android components
- Integration with Architecture Components

Hilt solves these problems by providing:
1. Predefined components for Android classes
2. Automatic component lifecycle management
3. Standard scopes aligned with Android lifecycle
4. Simplified setup with annotations

---

## Setting Up Hilt

### 1. Add Dependencies

```gradle
// Project-level build.gradle
buildscript {
    dependencies {
        classpath 'com.google.dagger:hilt-android-gradle-plugin:2.48'
    }
}

// App-level build.gradle
plugins {
    id 'com.google.dagger.hilt.android'
    id 'kotlin-kapt'
}

dependencies {
    implementation 'com.google.dagger:hilt-android:2.48'
    kapt 'com.google.dagger:hilt-android-compiler:2.48'

    // For ViewModels
    implementation 'androidx.hilt:hilt-lifecycle-viewmodel:1.0.0-alpha03'
    kapt 'androidx.hilt:hilt-compiler:1.1.0'
}
```

### 2. Annotate Application Class

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    // Hilt automatically generates Application component
}
```

### 3. Annotate Android Components

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    // Can inject dependencies here

    @Inject
    lateinit var userRepository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // userRepository is automatically injected
        userRepository.getUsers()
    }
}
```

---

## Core Concepts

### 1. Hilt Components

Hilt provides predefined components tied to Android lifecycle:

```
SingletonComponent (Application scope)
    ↓
ActivityRetainedComponent (ViewModel scope)
    ↓
ActivityComponent (Activity scope)
    ↓
FragmentComponent (Fragment scope)
    ↓
ViewComponent (View scope)
    ↓
ViewWithFragmentComponent (View with Fragment scope)
    ↓
ServiceComponent (Service scope)
```

### 2. Scopes

Hilt provides standard scopes for Android:

```kotlin
@Singleton                    // Application lifetime
@ActivityRetainedScoped       // Survives configuration changes
@ActivityScoped               // Activity lifetime
@FragmentScoped               // Fragment lifetime
@ViewScoped                   // View lifetime
@ServiceScoped                // Service lifetime
```

---

## Basic Usage

### 1. Injecting into ViewModel

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    val users = userRepository.getUsers()
        .asLiveData()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            val user = userRepository.getUserById(userId)
            // Update UI
        }
    }
}

@AndroidEntryPoint
class UserActivity : AppCompatActivity() {
    // ViewModel is automatically injected
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)

        viewModel.users.observe(this) { users ->
            displayUsers(users)
        }
    }
}
```

### 2. Providing Dependencies with Modules

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

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
```

### 3. Binding Interfaces

```kotlin
interface UserRepository {
    suspend fun getUsers(): List<User>
}

class UserRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : UserRepository {
    override suspend fun getUsers(): List<User> {
        return apiService.fetchUsers()
    }
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository
}
```

---

## Advanced Features

### 1. Qualifiers

When you need multiple instances of the same type:

```kotlin
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthInterceptor

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class LoggingInterceptor

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @AuthInterceptor
    fun provideAuthInterceptor(): Interceptor {
        return Interceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Authorization", "Bearer token")
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
    @Singleton
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

### 2. Entry Points (for non-Android classes)

```kotlin
@EntryPoint
@InstallIn(SingletonComponent::class)
interface MyWorkerEntryPoint {
    fun userRepository(): UserRepository
}

class MyWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {

    override fun doWork(): Result {
        val appContext = applicationContext.applicationContext
        val entryPoint = EntryPointAccessors.fromApplication(
            appContext,
            MyWorkerEntryPoint::class.java
        )

        val repository = entryPoint.userRepository()
        // Use repository

        return Result.success()
    }
}
```

### 3. Assisted Injection (for Runtime parameters)

```kotlin
class UserDetailViewModel @AssistedInject constructor(
    @Assisted private val userId: String,
    private val userRepository: UserRepository
) : ViewModel() {

    val user = userRepository.getUserById(userId)
        .asLiveData()

    @AssistedFactory
    interface Factory {
        fun create(userId: String): UserDetailViewModel
    }
}

@AndroidEntryPoint
class UserDetailActivity : AppCompatActivity() {

    @Inject
    lateinit var viewModelFactory: UserDetailViewModel.Factory

    private val viewModel by lazy {
        val userId = intent.getStringExtra("USER_ID") ?: ""
        viewModelFactory.create(userId)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user_detail)

        viewModel.user.observe(this) { user ->
            displayUser(user)
        }
    }
}
```

---

## Testing with Hilt

### Unit Tests

```kotlin
@HiltAndroidTest
class UserViewModelTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var repository: UserRepository

    @Before
    fun init() {
        hiltRule.inject()
    }

    @Test
    fun testLoadUsers() = runTest {
        val viewModel = UserViewModel(repository, SavedStateHandle())
        // Test logic
    }
}

@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class FakeRepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        fake: FakeUserRepository
    ): UserRepository
}
```

### UI Tests

```kotlin
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class MainActivityTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @get:Rule
    var activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Before
    fun init() {
        hiltRule.inject()
    }

    @Test
    fun testUserListDisplayed() {
        // Test UI
        onView(withId(R.id.userList))
            .check(matches(isDisplayed()))
    }
}
```

---

## Benefits of Hilt

1. **Simplified Setup**
   - Less boilerplate than Dagger
   - Predefined components for Android
   - Standard scopes

2. **Lifecycle Awareness**
   - Components tied to Android lifecycle
   - Automatic cleanup
   - Survives configuration changes

3. **Compile-Time Safety**
   - Errors caught at compile-time
   - Type-safe dependency graph
   - No runtime dependency resolution

4. **Integration with Jetpack**
   - ViewModel injection
   - WorkManager support
   - Navigation component support

5. **Testability**
   - Easy to replace dependencies in tests
   - Test-specific modules
   - Supports both unit and UI tests

6. **Performance**
   - No reflection at runtime
   - Generated code is optimized
   - Singleton caching

---

## Common Use Cases

### 1. Repository Pattern

```kotlin
@Singleton
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userDao: UserDao
) {
    fun getUsers(): Flow<List<User>> = flow {
        val cachedUsers = userDao.getAllUsers()
        emit(cachedUsers)

        try {
            val freshUsers = apiService.fetchUsers()
            userDao.insertAll(freshUsers)
            emit(freshUsers)
        } catch (e: Exception) {
            // Emit cached data on error
        }
    }
}
```

### 2. Networking Layer

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

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
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
}
```

### 3. Database Layer

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
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

## Summary

**Hilt** is a dependency injection framework for Android that:

1. **Simplifies DI setup** - Less boilerplate than raw Dagger
2. **Provides standard components** - Aligned with Android lifecycle
3. **Manages scopes** - Automatic lifecycle management
4. **Integrates with Jetpack** - ViewModel, WorkManager, Navigation
5. **Improves testability** - Easy to swap dependencies in tests
6. **Compile-time safe** - Errors caught early
7. **Zero runtime cost** - Code generation, no reflection

**Key annotations:**
- `@HiltAndroidApp` - Application class
- `@AndroidEntryPoint` - Activity, Fragment, View, Service
- `@HiltViewModel` - ViewModel
- `@Inject` - Constructor or field injection
- `@Module` + `@InstallIn` - Provide dependencies
- `@Provides` - Provide method
- `@Binds` - Bind interface to implementation

**When to use Hilt:**
- Building new Android apps
- Need lifecycle-aware DI
- Want compile-time safety
- Integrating with Jetpack libraries
- Need testable architecture

## Ответ (RU)
**Hilt** — это фреймворк для внедрения зависимостей (Dependency Injection, DI), разработанный командой Google специально для платформы Android. Он основан на популярном DI фреймворке Dagger и предназначен для упрощения процесса внедрения зависимостей в Android-приложениях.

### Основные Возможности

1. **Упрощенная настройка** - меньше boilerplate кода чем в Dagger
2. **Предопределенные компоненты** - привязанные к Android lifecycle
3. **Управление областями видимости** - автоматическое управление жизненным циклом
4. **Интеграция с Jetpack** - ViewModel, WorkManager, Navigation
5. **Улучшенная тестируемость** - легкая замена зависимостей в тестах
6. **Compile-time безопасность** - ошибки обнаруживаются при компиляции

### Ключевые Аннотации

- `@HiltAndroidApp` - класс Application
- `@AndroidEntryPoint` - Activity, Fragment, View, Service
- `@HiltViewModel` - ViewModel
- `@Inject` - внедрение в конструктор или поле
- `@Module` + `@InstallIn` - предоставление зависимостей
- `@Provides` - метод предоставления
- `@Binds` - привязка интерфейса к реализации

### Когда Использовать Hilt

- Создание новых Android приложений
- Нужна lifecycle-aware DI
- Требуется compile-time безопасность
- Интеграция с Jetpack библиотеками
- Необходима тестируемая архитектура


## Follow-ups

- [[c-dependency-injection]]
- [[c-hilt]]
- [[q-test-doubles-dependency-injection--testing--medium]]


## References

- https://developer.android.com/topic/architecture
- https://developer.android.com/docs


## Related Questions

- [[q-android-app-components--android--easy]]
- [[q-what-can-be-done-through-composer--android--medium]]
- [[q-data-sync-unstable-network--android--hard]]

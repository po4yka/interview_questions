---
id: android-199
title: Hilt / Фреймворк Hilt
aliases:
- Hilt
- Фреймворк Hilt
topic: android
subtopics:
- architecture-mvvm
- di-hilt
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- c-hilt
- q-what-is-known-about-recyclerview--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/architecture-mvvm
- android/di-hilt
- dependency-injection
- di
- difficulty/medium
- hilt

---

# Вопрос (RU)
> Фреймворк Hilt

# Question (EN)
> Hilt

---

## Ответ (RU)
**Hilt** — это фреймворк для внедрения зависимостей (Dependency Injection, DI), разработанный Google специально для Android. Он построен поверх **Dagger** и упрощает настройку DI в Android-приложениях за счёт уменьшения шаблонного кода и стандартных паттернов для Android-компонентов.

### Что такое Dependency Injection

Dependency Injection — это шаблон проектирования, при котором объект получает свои зависимости извне, а не создаёт их самостоятельно.

```kotlin
// Без DI (жёсткая связность)
class UserViewModel {
    private val repository = UserRepository()

    fun getUser() = repository.fetchUser()
}

// С DI (слабая связность)
class UserViewModel(
    private val repository: UserRepository
) {
    fun getUser() = repository.fetchUser()
}
```

### Зачем нужен Hilt

До появления Hilt использование Dagger в Android требовало:
- Ручного объявления и связывания компонентов
- Явного управления жизненным циклом компонентов
- Настройки областей видимости под Android-компоненты
- Дополнительной интеграции с Architecture Components

Hilt решает это за счёт:
1. Предопределённых компонентов под ключевые Android-слои
2. Автоматического управления жизненным циклом графа зависимостей
3. Стандартных scope-аннотаций, согласованных с Android lifecycle
4. Упрощённой конфигурации через аннотации

---

### Настройка Hilt

#### 1. Добавление зависимостей

```gradle
// Project-level build.gradle (Groovy DSL)
buildscript {
    dependencies {
        classpath "com.google.dagger:hilt-android-gradle-plugin:2.48"
    }
}

// App-level build.gradle (Groovy DSL)
plugins {
    id "com.google.dagger.hilt.android"
    id "kotlin-kapt"
}

dependencies {
    implementation "com.google.dagger:hilt-android:2.48"
    kapt "com.google.dagger:hilt-android-compiler:2.48"

    // Для интеграций Hilt с AndroidX-библиотеками
    kapt "androidx.hilt:hilt-compiler:1.1.0"
}
```

> Примечание: устаревший артефакт `androidx.hilt:hilt-lifecycle-viewmodel` больше не рекомендуется; используется `@HiltViewModel` из `com.google.dagger:hilt-android`.

#### 2. Аннотация класса Application

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    // Hilt автоматически генерирует компонент уровня приложения
}
```

#### 3. Аннотация Android-компонентов

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var userRepository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // userRepository будет доступен до вызова onCreate
        userRepository.getUsers()
    }
}
```

---

### Основные концепции

#### 1. Компоненты Hilt

Hilt предоставляет предопределённые компоненты, привязанные к жизненному циклу Android:

```
SingletonComponent (уровень Application)
    ↓
ActivityRetainedComponent (переживает конфигурационные изменения, используется для ViewModel)
    ↓
ActivityComponent (уровень Activity)
    ↓
FragmentComponent (уровень Fragment)
    ↓
ViewComponent (уровень View)
    ↓
ViewWithFragmentComponent (View, привязанное к Fragment)
    ↓
ServiceComponent (уровень Service)
```

#### 2. Области видимости (Scopes)

Scope-аннотации связывают время жизни объекта со временем жизни компонента:

```kotlin
@Singleton                    // Время жизни приложения (SingletonComponent)
@ActivityRetainedScoped       // Переживает конфигурационные изменения (ActivityRetainedComponent)
@ActivityScoped               // Время жизни Activity
@FragmentScoped               // Время жизни Fragment
// У Hilt нет встроенного @ViewScoped для ViewComponent/ViewWithFragmentComponent
@ServiceScoped                // Время жизни Service
```

---

### Базовое использование

#### 1. Инъекция в ViewModel

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
            // Обновление UI-состояния
        }
    }
}

@AndroidEntryPoint
class UserActivity : AppCompatActivity() {
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

#### 2. Предоставление зависимостей через модули

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

#### 3. Привязка интерфейсов

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

### Продвинутые возможности

#### 1. Qualifier-аннотации

Когда нужно несколько реализаций одного типа, используются qualifier-аннотации:

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

#### 2. EntryPoint для нестандартных классов

Для классов, которые нельзя пометить `@AndroidEntryPoint` (например, некоторые коллбэки библиотек), можно использовать EntryPoint:

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
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            MyWorkerEntryPoint::class.java
        )

        val repository = entryPoint.userRepository()
        // Используем repository

        return Result.success()
    }
}
```

> Примечание: для WorkManager есть отдельная интеграция через `androidx.hilt:hilt-work`.

#### 3. Assisted Injection (для runtime-параметров)

Для параметров, которые Hilt не может предоставить напрямую во время компиляции, можно использовать assisted-injection паттерн. Один из вариантов (для не-`@HiltViewModel` классов):

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
```

Для `ViewModel` в Hilt-проектах современный подход — использовать `@HiltViewModel` совместно с `SavedStateHandle` вместо ручного assisted-injection.

---

### Тестирование с Hilt

#### Unit-тесты с Hilt

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
        // Логика теста
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

#### UI-тесты

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
        onView(withId(R.id.userList))
            .check(matches(isDisplayed()))
    }
}
```

---

### Преимущества Hilt (детально)

1. Упрощённая настройка
   - Меньше шаблонного кода по сравнению с ручной настройкой Dagger
   - Предопределённые компоненты под Android
   - Стандартные области видимости

2. Осведомлённость о жизненном цикле
   - Компоненты привязаны к жизненному циклу Android-компонентов
   - Автоматическое освобождение зависимостей
   - Поддержка переживания конфигурационных изменений через `ActivityRetainedComponent`

3. Безопасность на этапе компиляции
   - Ошибки в графе зависимостей выявляются на этапе сборки
   - Типобезопасный граф

4. Интеграция с Jetpack
   - Инъекция в `ViewModel`
   - Интеграция с WorkManager, Navigation и др.

5. Тестируемость
   - Лёгкая подмена зависимостей в тестах
   - Тестовые модули через `@TestInstallIn`
   - Поддержка unit- и UI-тестов

6. Производительность
   - Нет рефлексии при разрешении зависимостей
   - Эффективный сгенерированный код
   - Кэширование singleton-объектов

---

### Типичные сценарии использования

#### 1. Repository-паттерн

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
            // Обработка ошибок при необходимости, можно оставить кешированные данные
        }
    }
}
```

#### 2. Сетевой слой

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

#### 3. Работа с базой данных

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

### Резюме

**Hilt** — это фреймворк DI для Android, который:

1. Упрощает настройку DI по сравнению с ручной конфигурацией Dagger
2. Предоставляет стандартные компоненты, согласованные с жизненным циклом Android
3. Управляет областями видимости и временем жизни зависимостей автоматически
4. Интегрируется с Jetpack (`ViewModel`, WorkManager, Navigation и др.)
5. Улучшает тестируемость за счёт тестовых модулей и заменяемых биндингов
6. Обеспечивает compile-time безопасность через сгенерированный код
7. Избегает рефлексии и минимизирует накладные расходы во время выполнения

Ключевые аннотации:
- `@HiltAndroidApp` — для `Application`
- `@AndroidEntryPoint` — для `Activity`, `Fragment`, `View`, `Service` и т.п.
- `@HiltViewModel` — для `ViewModel`
- `@Inject` — для конструкторов и полей
- `@Module` + `@InstallIn` — для модулей
- `@Provides` — для фабричных методов
- `@Binds` — для привязки интерфейсов к реализациям

Когда использовать Hilt:
- В новых Android-приложениях
- Когда нужна DI, учитывающая жизненный цикл компонентов
- Когда важны модульность, тестируемость и интеграция с Jetpack

---

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
// Project-level build.gradle (Groovy DSL)
buildscript {
    dependencies {
        classpath "com.google.dagger:hilt-android-gradle-plugin:2.48"
    }
}

// App-level build.gradle (Groovy DSL)
plugins {
    id "com.google.dagger.hilt.android"
    id "kotlin-kapt"
}

dependencies {
    implementation "com.google.dagger:hilt-android:2.48"
    kapt "com.google.dagger:hilt-android-compiler:2.48"

    // For Hilt integration with other AndroidX libraries
    kapt "androidx.hilt:hilt-compiler:1.1.0"
}
```

Note: The older `androidx.hilt:hilt-lifecycle-viewmodel` artifact is deprecated; modern Hilt uses `@HiltViewModel` from `com.google.dagger:hilt-android`.

### 2. Annotate `Application` Class

```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    // Hilt automatically generates the application-level component
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
        // userRepository is injected before onCreate is called
        userRepository.getUsers()
    }
}
```

---

## Core Concepts

### 1. Hilt Components

Hilt provides predefined components tied to the Android lifecycle:

```
SingletonComponent (Application scope)
    ↓
ActivityRetainedComponent (Retained across configuration changes, used for ViewModels)
    ↓
ActivityComponent (Activity scope)
    ↓
FragmentComponent (Fragment scope)
    ↓
ViewComponent (View scope)
    ↓
ViewWithFragmentComponent (View associated with Fragment scope)
    ↓
ServiceComponent (Service scope)
```

### 2. Scopes

Scope annotations bind object lifetimes to component lifetimes:

```kotlin
@Singleton                    // Application lifetime (SingletonComponent)
@ActivityRetainedScoped       // Retained across configuration changes (ActivityRetainedComponent)
@ActivityScoped               // Activity lifetime
@FragmentScoped               // Fragment lifetime
// Note: Hilt doesn't define a built-in @ViewScoped for ViewComponent/ViewWithFragmentComponent
@ServiceScoped                // Service lifetime
```

---

## Basic Usage

### 1. Injecting into `ViewModel`

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
            // Update UI state
        }
    }
}

@AndroidEntryPoint
class UserActivity : AppCompatActivity() {
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

For classes that Hilt doesn't support via `@AndroidEntryPoint` (e.g., some library callbacks), you can use entry points:

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
        val entryPoint = EntryPointAccessors.fromApplication(
            applicationContext,
            MyWorkerEntryPoint::class.java
        )

        val repository = entryPoint.userRepository()
        // Use repository

        return Result.success()
    }
}
```

(Note: Hilt also provides dedicated integration for WorkManager via `androidx.hilt:hilt-work`.)

### 3. Assisted Injection (for runtime parameters)

For runtime parameters that Hilt can't provide directly, you can use assisted injection patterns. One option (for non-`@HiltViewModel` classes) is:

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
```

For ViewModels in Hilt-based apps, the recommended modern approach is to use `@HiltViewModel` together with `SavedStateHandle` or a `SavedStateHandle`-backed key instead of manual assisted injection.

---

## Testing with Hilt

### Unit Tests (using Hilt test components)

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
        onView(withId(R.id.userList))
            .check(matches(isDisplayed()))
    }
}
```

---

## Benefits of Hilt

1. **Simplified Setup**
   - Less boilerplate than plain Dagger
   - Predefined components for Android
   - Standard scopes

2. **Lifecycle Awareness**
   - Components tied to Android lifecycle
   - Automatic cleanup
   - Support for surviving configuration changes via ActivityRetainedComponent

3. **Compile-Time Safety**
   - Errors caught at compile-time
   - Type-safe dependency graph

4. **Integration with Jetpack**
   - `ViewModel` injection
   - WorkManager support
   - Navigation component support

5. **Testability**
   - Easy to replace dependencies in tests
   - Test-specific modules
   - Supports both unit and UI tests

6. **Performance**
   - No reflection-based resolution at runtime
   - Generated code is efficient
   - Singleton caching where appropriate

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
            // Optionally handle error, keep last emitted cached data
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

1. Simplifies DI setup compared to manual Dagger configuration
2. Provides standard components aligned with the Android lifecycle
3. Manages scopes with automatic lifecycle management
4. Integrates with Jetpack libraries (`ViewModel`, WorkManager, Navigation, etc.)
5. Improves testability through test-specific modules and swappable bindings
6. Offers compile-time safety via generated code and type-checked graphs
7. Avoids reflection and keeps runtime overhead low

**Key annotations:**
- `@HiltAndroidApp` - `Application` class
- `@AndroidEntryPoint` - `Activity`, `Fragment`, `View`, `Service`, etc.
- `@HiltViewModel` - `ViewModel`
- `@Inject` - Constructor or field injection
- `@Module` + `@InstallIn` - Provide dependencies
- `@Provides` - Provide method
- `@Binds` - Bind interface to implementation

**When to use Hilt:**
- Building new Android apps
- Need lifecycle-aware DI
- Want compile-time safety
- Integrating with Jetpack libraries
- Need a testable, modular architecture

---

## Follow-ups

- [[c-dependency-injection]]
- [[c-hilt]]

## References

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

- [[q-android-app-components--android--easy]]
- [[q-what-can-be-done-through-composer--android--medium]]
- [[q-data-sync-unstable-network--android--hard]]

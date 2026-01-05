---
id: android-403
title: Hilt Components Scope / Компоненты и скоупы Hilt
aliases: [Hilt Components Scope, Компоненты и скоупы Hilt]
topic: android
subtopics: [di-hilt]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-hilt, q-android-security-best-practices--android--medium, q-compose-core-components--android--medium, q-hilt-entry-points--android--medium, q-room-library-definition--android--easy, q-what-are-the-most-important-components-of-compose--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/di-hilt, dependency-injection, difficulty/medium]

---
# Вопрос (RU)
> Компоненты и скоупы Hilt

# Question (EN)
> Hilt Components Scope

---

## Ответ (RU)
Hilt предоставляет готовые компоненты для основных уровней Android-жизненного цикла: `Application`, `Activity`, `Fragment`, `ViewModel`, `View` и `Service`.

Чтобы добавить модуль в граф зависимостей, используется аннотация `@InstallIn(ComponentName::class)`.

---

### Компоненты И Скоупы Hilt (RU)

| Компонент | Scope | Время жизни | Android-уровень |
|-----------|-------|-------------|-----------------|
| SingletonComponent | `@Singleton` | Весь срок жизни процесса приложения | `Application` |
| ActivityRetainedComponent | `@ActivityRetainedScoped` | Переживает конфигурационные изменения, пока жива логическая `Activity` | Базовый уровень для `@HiltViewModel` / retained `ViewModel` |
| ViewModelComponent | `@ViewModelScoped` | Время жизни конкретного `ViewModel` | `ViewModel` |
| ActivityComponent | `@ActivityScoped` | Конкретный экземпляр `Activity` (пересоздается при конфиг. изменениях) | `Activity` |
| FragmentComponent | `@FragmentScoped` | Конкретный экземпляр `Fragment` | `Fragment` |
| ViewComponent | `@ViewScoped` | Конкретный `View` | `View` |
| ViewWithFragmentComponent | `@ViewScoped` | `View`, связанный с `Fragment` | `View` внутри `Fragment` |
| ServiceComponent | `@ServiceScoped` | Конкретный `Service` | `Service` |

Примечание: `@ViewScoped` используется и для `ViewComponent`, и для `ViewWithFragmentComponent`.

---

### 1. SingletonComponent (RU)

Время жизни: весь процесс приложения.

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

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
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}

// Использование: в SingletonComponent @Singleton корректен
@Singleton
class UserRepository @Inject constructor(
    private val database: AppDatabase,
    private val api: ApiService
)
```

---

### 2. ViewModelComponent (RU)

Время жизни: один экземпляр `ViewModel` (сам `ViewModel` переживает конфигурационные изменения, пока жив его владелец).

```kotlin
@Module
@InstallIn(ViewModelComponent::class)
object ViewModelModule {

    @Provides
    @ViewModelScoped
    fun provideGetUserUseCase(
        repository: UserRepository
    ): GetUserUseCase {
        return GetUserUseCase(repository)
    }
}

// Использование
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    fun loadUser(id: String) {
        viewModelScope.launch {
            val user = getUserUseCase(id)
            // Обновление состояния
        }
    }
}
```

---

### 3. ActivityComponent (RU)

Время жизни: экземпляр `Activity` (пересоздается при конфигурационных изменениях).

```kotlin
@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {

    @Provides
    @ActivityScoped
    fun providePresenter(
        repository: UserRepository
    ): UserPresenter {
        return UserPresenter(repository)
    }

    @Provides
    fun provideAnalytics(
        @ActivityContext context: Context
    ): Analytics {
        return Analytics(context)
    }
}

// Использование
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var presenter: UserPresenter

    @Inject
    lateinit var analytics: Analytics
}
```

---

### 4. FragmentComponent (RU)

Время жизни: экземпляр `Fragment`.

```kotlin
@Module
@InstallIn(FragmentComponent::class)
object FragmentModule {

    @Provides
    @FragmentScoped
    fun provideAdapter(): UserAdapter {
        return UserAdapter()
    }
}

// Использование
@AndroidEntryPoint
class UserFragment : Fragment() {

    @Inject
    lateinit var adapter: UserAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        recyclerView.adapter = adapter
    }
}
```

---

### 5. ServiceComponent (RU)

Время жизни: экземпляр `Service`.

```kotlin
@Module
@InstallIn(ServiceComponent::class)
object ServiceModule {

    @Provides
    @ServiceScoped
    fun provideNotificationBuilder(
        @ApplicationContext context: Context
    ): NotificationCompat.Builder {
        return NotificationCompat.Builder(context, CHANNEL_ID)
    }
}

// Использование
@AndroidEntryPoint
class MusicService : Service() {

    @Inject
    lateinit var notificationBuilder: NotificationCompat.Builder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(1, notificationBuilder.build())
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

---

### Полный Пример: Мульти-компонентная Конфигурация (RU)

#### 1. Модули `Application` (Singleton)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
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
            "app_db"
        ).build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

#### 2. Репозиторий (Singleton)

```kotlin
@Singleton
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val userDao: UserDao
) {
    suspend fun getUser(id: String): User {
        return userDao.getUser(id) ?: run {
            val user = api.fetchUser(id)
            userDao.insert(user)
            user
        }
    }
}
```

#### 3. Модуль `ViewModel`

```kotlin
@Module
@InstallIn(ViewModelComponent::class)
object UseCaseModule {

    @Provides
    @ViewModelScoped
    fun provideGetUserUseCase(
        repository: UserRepository
    ): GetUserUseCase {
        return GetUserUseCase(repository)
    }
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {

    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _user.value = getUserUseCase(id)
        }
    }
}
```

#### 4. `Activity`

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        lifecycleScope.launch {
            viewModel.user.collect { user ->
                textView.text = user?.name
            }
        }

        viewModel.loadUser("123")
    }
}
```

---

### Связывание Интерфейсов (RU)

#### Использование `@Binds`

```kotlin
interface UserRepository {
    suspend fun getUser(id: String): User
}

class UserRepositoryImpl @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
) : UserRepository {
    override suspend fun getUser(id: String): User {
        return dao.getUser(id) ?: api.fetchUser(id)
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

### Квалификаторы Для Нескольких Биндингов (RU)

```kotlin
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthInterceptor

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class LoggingInterceptor

@Module
@InstallIn(SingletonComponent::class)
object InterceptorModule {

    @Provides
    @AuthInterceptor
    fun provideAuthInterceptor(): Interceptor {
        return Interceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Authorization", "Bearer TOKEN")
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

---

### Иерархия Компонентов (RU)

```text
SingletonComponent (Application)
       ↓
ActivityRetainedComponent (переживает конфиг. изменения, привязан к логическому жизненному циклу Activity)
       ↓
ViewModelComponent (ViewModel)

Отдельные дочерние ветки от SingletonComponent:

SingletonComponent
   ↓
ActivityComponent (Activity)
   ↓
FragmentComponent (Fragment)
   ↓
ViewComponent (View)

SingletonComponent
   ↓
ServiceComponent (Service)
```

Зависимости "текут" вниз по иерархиям: дочерние компоненты могут использовать биндинги родительских компонентов.

---

## Answer (EN)
Hilt provides predefined components for common Android lifecycle containers such as `Application`, `Activity`, `Fragment`, `ViewModel`, `View`, and `Service`.

To add a module to a graph, use the `@InstallIn(ComponentName::class)` annotation.

---

## Hilt Components and Scopes

| Component | Scope | Lifetime | Android Class |
|-----------|-------|----------|---------------|
| **SingletonComponent** | `@Singleton` | Entire app process | `Application` |
| **ActivityRetainedComponent** | `@ActivityRetainedScoped` | Survives configuration changes while the logical `Activity` exists | Backing scope for `@HiltViewModel` / retained ViewModels |
| **ViewModelComponent** | `@ViewModelScoped` | `ViewModel` lifetime | `ViewModel` |
| **ActivityComponent** | `@ActivityScoped` | `Activity` instance (recreated on config change) | `Activity` |
| **FragmentComponent** | `@FragmentScoped` | `Fragment` instance | `Fragment` |
| **ViewComponent** | `@ViewScoped` | `View` instance | `View` |
| **ViewWithFragmentComponent** | `@ViewScoped` | `View` associated with `Fragment` | `View` in `Fragment` |
| **ServiceComponent** | `@ServiceScoped` | `Service` instance | `Service` |

Note: `@ViewScoped` is used with both `ViewComponent` and `ViewWithFragmentComponent`.

---

## 1. SingletonComponent

Lifetime: entire application (app process).

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

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
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}

// Usage: provided in SingletonComponent, so @Singleton is correct here
@Singleton
class UserRepository @Inject constructor(
    private val database: AppDatabase,
    private val api: ApiService
)
```

---

## 2. ViewModelComponent

Lifetime: a single `ViewModel` instance (which itself survives configuration changes as long as its owner does).

```kotlin
@Module
@InstallIn(ViewModelComponent::class)
object ViewModelModule {

    @Provides
    @ViewModelScoped
    fun provideGetUserUseCase(
        repository: UserRepository
    ): GetUserUseCase {
        return GetUserUseCase(repository)
    }
}

// Usage
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    fun loadUser(id: String) {
        viewModelScope.launch {
            val user = getUserUseCase(id)
            // Update state
        }
    }
}
```

---

## 3. ActivityComponent

Lifetime: an `Activity` instance (recreated on configuration change).

```kotlin
@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {

    @Provides
    @ActivityScoped
    fun providePresenter(
        repository: UserRepository
    ): UserPresenter {
        return UserPresenter(repository)
    }

    @Provides
    fun provideAnalytics(
        @ActivityContext context: Context
    ): Analytics {
        return Analytics(context)
    }
}

// Usage
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var presenter: UserPresenter

    @Inject
    lateinit var analytics: Analytics
}
```

---

## 4. FragmentComponent

Lifetime: a `Fragment` instance.

```kotlin
@Module
@InstallIn(FragmentComponent::class)
object FragmentModule {

    @Provides
    @FragmentScoped
    fun provideAdapter(): UserAdapter {
        return UserAdapter()
    }
}

// Usage
@AndroidEntryPoint
class UserFragment : Fragment() {

    @Inject
    lateinit var adapter: UserAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        recyclerView.adapter = adapter
    }
}
```

---

## 5. ServiceComponent

Lifetime: a `Service` instance.

```kotlin
@Module
@InstallIn(ServiceComponent::class)
object ServiceModule {

    @Provides
    @ServiceScoped
    fun provideNotificationBuilder(
        @ApplicationContext context: Context
    ): NotificationCompat.Builder {
        return NotificationCompat.Builder(context, CHANNEL_ID)
    }
}

// Usage
@AndroidEntryPoint
class MusicService : Service() {

    @Inject
    lateinit var notificationBuilder: NotificationCompat.Builder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(1, notificationBuilder.build())
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

---

## Complete Example: Multi-Component Setup

### 1. `Application` Modules (Singleton)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
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
            "app_db"
        ).build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

### 2. Repository (Singleton)

```kotlin
@Singleton
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val userDao: UserDao
) {
    suspend fun getUser(id: String): User {
        return userDao.getUser(id) ?: run {
            val user = api.fetchUser(id)
            userDao.insert(user)
            user
        }
    }
}
```

### 3. `ViewModel` Module

```kotlin
@Module
@InstallIn(ViewModelComponent::class)
object UseCaseModule {

    @Provides
    @ViewModelScoped
    fun provideGetUserUseCase(
        repository: UserRepository
    ): GetUserUseCase {
        return GetUserUseCase(repository)
    }
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {

    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _user.value = getUserUseCase(id)
        }
    }
}
```

### 4. `Activity`

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        lifecycleScope.launch {
            viewModel.user.collect { user ->
                textView.text = user?.name
            }
        }

        viewModel.loadUser("123")
    }
}
```

---

## Binding Interfaces

### Using `@Binds`

```kotlin
interface UserRepository {
    suspend fun getUser(id: String): User
}

class UserRepositoryImpl @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
) : UserRepository {
    override suspend fun getUser(id: String): User {
        return dao.getUser(id) ?: api.fetchUser(id)
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

## Qualifiers for Multiple Bindings

```kotlin
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthInterceptor

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class LoggingInterceptor

@Module
@InstallIn(SingletonComponent::class)
object InterceptorModule {

    @Provides
    @AuthInterceptor
    fun provideAuthInterceptor(): Interceptor {
        return Interceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Authorization", "Bearer TOKEN")
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

---

## Component Hierarchy

```text
SingletonComponent (Application)
       ↓
ActivityRetainedComponent (Survives config changes, tied to Activity's logical lifecycle)
       ↓
ViewModelComponent (ViewModel)

Separate child branches from SingletonComponent:

SingletonComponent
   ↓
ActivityComponent (Activity)
   ↓
FragmentComponent (Fragment)
   ↓
ViewComponent (View)

SingletonComponent
   ↓
ServiceComponent (Service)
```

Dependencies flow down within each hierarchy: child components can access bindings from their parent components.

---

## Summary (RU)

Кратко по компонентам Hilt:

- `SingletonComponent` + `@Singleton` — зависимости на весь процесс приложения.
- `ActivityRetainedComponent` + `@ActivityRetainedScoped` — объекты, переживающие конфигурационные изменения и привязанные к логическому жизненному циклу Activity (граф для `@HiltViewModel`).
- `ViewModelComponent` + `@ViewModelScoped` — зависимости конкретного `ViewModel`.
- `ActivityComponent` + `@ActivityScoped` — зависимости уровня `Activity`.
- `FragmentComponent` + `@FragmentScoped` — зависимости уровня `Fragment`.
- `ViewComponent` / `ViewWithFragmentComponent` + `@ViewScoped` — зависимости уровня `View`.
- `ServiceComponent` + `@ServiceScoped` — зависимости уровня `Service`.

Ключевые моменты:
- Используйте `@InstallIn`, чтобы привязать модуль к нужному компоненту.
- Используйте scope-аннотацию, соответствующую целевому компоненту.
- Дочерние компоненты наследуют зависимости родительских в рамках своей иерархии.
- Для интерфейсов используйте `@Binds`.
- Для нескольких реализаций используйте квалификаторы (`@Qualifier`).

---

## Summary (EN)

Hilt Components:

| Component | Scope | Use For |
|-----------|-------|---------|
| SingletonComponent | `@Singleton` | App-wide singletons |
| ActivityRetainedComponent | `@ActivityRetainedScoped` | Retained objects across config changes (backing graph for `@HiltViewModel`) |
| ViewModelComponent | `@ViewModelScoped` | `ViewModel` dependencies |
| ActivityComponent | `@ActivityScoped` | `Activity`-specific |
| FragmentComponent | `@FragmentScoped` | `Fragment`-specific |
| ViewComponent / ViewWithFragmentComponent | `@ViewScoped` | `View` / `View`-in-`Fragment`-specific |
| ServiceComponent | `@ServiceScoped` | `Service`-specific |

How to add a module:

```kotlin
@Module
@InstallIn(SingletonComponent::class) // Specify component
object MyModule {

    @Provides
    @Singleton // Match scope (SingletonComponent)
    fun provideDependency(): MyDependency {
        return MyDependency()
    }
}
```

Key points:
- Use `@InstallIn` to bind modules to a specific component.
- Use the scope annotation that matches the target component.
- Child components inherit dependencies from parent components within their hierarchy.
- Use `@Binds` for interfaces.
- Use qualifiers (`@Qualifier`) when multiple bindings of the same type exist.

---

## Дополнительные Вопросы (RU)

- [[q-android-security-best-practices--android--medium]]
- [[q-room-library-definition--android--easy]]

## Follow-ups

- [[q-android-security-best-practices--android--medium]]
- [[q-room-library-definition--android--easy]]

---

## Ссылки (RU)

- [Hilt](https://developer.android.com/training/dependency-injection/hilt-android)

## References

- [Hilt](https://developer.android.com/training/dependency-injection/hilt-android)

---

## Связанные Вопросы (RU)

### Базовые Концепции / Предпосылки

- [[c-hilt]]

### Связанные (Medium)

- [[q-android-security-best-practices--android--medium]]
- [[q-room-library-definition--android--easy]]

## Related Questions

### Prerequisites / Concepts

- [[c-hilt]]

### Related (Medium)

- [[q-android-security-best-practices--android--medium]]
- [[q-room-library-definition--android--easy]]

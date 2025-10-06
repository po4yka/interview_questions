---
tags:
  - android
  - android/dependency-injection
  - components
  - dagger
  - dependency-injection
  - hilt
  - scope
difficulty: medium
---

# Какие готовые компоненты с готовым скоупом есть в Dagger Hilt и как модуль добавить к этой компоненте?

**English**: What ready-made components with scopes are in Dagger Hilt, and how to add a module to a component?

## Answer

Hilt provides **predefined components** for Application, Activity, Fragment, ViewModel, and other Android levels.

**To add module:** Use **`@InstallIn(ComponentName::class)`** annotation.

---

## Hilt Components and Scopes

| Component | Scope | Lifetime | Android Class |
|-----------|-------|----------|---------------|
| **SingletonComponent** | @Singleton | Application | Application |
| **ActivityRetainedComponent** | @ActivityRetainedScoped | Survives config changes | N/A (ViewModel) |
| **ViewModelComponent** | @ViewModelScoped | ViewModel | ViewModel |
| **ActivityComponent** | @ActivityScoped | Activity | Activity |
| **FragmentComponent** | @FragmentScoped | Fragment | Fragment |
| **ViewComponent** | @ViewScoped | View | View |
| **ViewWithFragmentComponent** | @ViewScoped | View in Fragment | View |
| **ServiceComponent** | @ServiceScoped | Service | Service |

---

## 1. SingletonComponent

**Lifetime:** Entire application

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

// Usage
@Singleton
class UserRepository @Inject constructor(
    private val database: AppDatabase,
    private val api: ApiService
)
```

---

## 2. ViewModelComponent

**Lifetime:** ViewModel (survives configuration changes)

```kotlin
@Module
@InstallIn(ViewModelComponent::class)
object ViewModelModule {

    @Provides
    fun provideUseCases(
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

**Lifetime:** Activity (destroyed on config change)

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

**Lifetime:** Fragment

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

**Lifetime:** Service

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

### 1. Application Module (Singleton)

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

### 3. ViewModel Module

```kotlin
@Module
@InstallIn(ViewModelComponent::class)
object UseCaseModule {

    @Provides
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

### 4. Activity

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

### Using @Binds

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

```
SingletonComponent (Application)
       ↓
ActivityRetainedComponent (Survives config changes)
       ↓
ViewModelComponent (ViewModel)
       ↓
ActivityComponent (Activity)
       ↓
FragmentComponent (Fragment)
       ↓
ViewComponent (View)

ServiceComponent (Service) ← Independent
```

**Dependencies flow down:** Child components can access parent dependencies.

---

## Summary

**Hilt Components:**

| Component | Scope | Use For |
|-----------|-------|---------|
| SingletonComponent | @Singleton | App-wide singletons |
| ViewModelComponent | @ViewModelScoped | ViewModel dependencies |
| ActivityComponent | @ActivityScoped | Activity-specific |
| FragmentComponent | @FragmentScoped | Fragment-specific |
| ServiceComponent | @ServiceScoped | Service-specific |

**How to add module:**

```kotlin
@Module
@InstallIn(SingletonComponent::class) // ← Specify component
object MyModule {

    @Provides
    @Singleton // ← Match scope
    fun provideDependency(): MyDependency {
        return MyDependency()
    }
}
```

**Key points:**
- Use `@InstallIn` to specify component
- Match scope annotation to component
- Child components inherit parent dependencies

---

## Ответ

Hilt предоставляет **готовые компоненты** для Application, Activity, Fragment, ViewModel и других уровней Android.

**Чтобы добавить модуль:** Используйте аннотацию **`@InstallIn(ComponentName::class)`**.

**Компоненты Hilt:**

| Компонент | Scope | Время жизни |
|-----------|-------|-------------|
| SingletonComponent | @Singleton | Приложение |
| ViewModelComponent | @ViewModelScoped | ViewModel |
| ActivityComponent | @ActivityScoped | Activity |
| FragmentComponent | @FragmentScoped | Fragment |
| ServiceComponent | @ServiceScoped | Service |

**Пример:**

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
            "database"
        ).build()
    }
}
```

**Ключевые моменты:**
- `@InstallIn` указывает компонент
- Scope должен соответствовать компоненту
- Дочерние компоненты наследуют зависимости родителей


---
anki_cards:
- slug: q-dagger-inject-provides--dagger--medium-0-en
  language: en
- slug: q-dagger-inject-provides--dagger--medium-0-ru
  language: ru
---
# Вопрос (RU)
> Когда использовать @Inject, а когда @Provides в Dagger?

# Question (EN)
> When should you use @Inject vs @Provides in Dagger?

---

## Ответ (RU)

**@Inject** и **@Provides** - два способа сообщить Dagger, как создавать зависимости. Выбор зависит от того, контролируете ли вы исходный код класса.

### @Inject - Конструкторная Инъекция

Используйте `@Inject` на конструкторе когда:
- Вы контролируете исходный код класса
- Класс не требует сложной логики создания
- Это предпочтительный способ (чище и проще)

```kotlin
// Dagger автоматически знает как создать этот класс
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userDao: UserDao,
    private val dispatchers: CoroutineDispatchers
) {
    suspend fun getUser(id: String): User {
        return apiService.getUser(id).also { user ->
            userDao.insert(user)
        }
    }
}

// Вложенные зависимости тоже с @Inject
class ApiService @Inject constructor(
    private val retrofit: Retrofit
) {
    // ...
}

class UserDao @Inject constructor(
    private val database: AppDatabase
) {
    // ...
}
```

### @Provides - Модульное Предоставление

Используйте `@Provides` в модуле когда:
- Класс из сторонней библиотеки (Retrofit, OkHttp, Room)
- Нужна сложная логика создания
- Нужно сконфигурировать объект
- Работаете с интерфейсами

```kotlin
@Module
class NetworkModule {

    // Сторонняя библиотека - нельзя добавить @Inject
    @Provides
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(AuthInterceptor())
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()
    }

    // Сложная конфигурация
    @Provides
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        gson: Gson
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .addCallAdapterFactory(CoroutineCallAdapterFactory())
            .build()
    }

    // Создание через фабричный метод
    @Provides
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

@Module
class DatabaseModule {

    @Provides
    fun provideDatabase(context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        )
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

### Сравнительная Таблица

| Критерий | @Inject | @Provides |
|----------|---------|-----------|
| Исходный код | Ваш класс | Сторонний класс |
| Где размещается | На конструкторе | В @Module |
| Сложность | Простое создание | Любая логика |
| Читаемость | Зависимости видны в классе | Зависимости в модуле |
| Тестирование | Легко мокать | Нужен тестовый модуль |
| Предпочтение | По умолчанию | Когда @Inject невозможен |

### @Inject на Полях и Методах

Помимо конструктора, `@Inject` работает на полях и методах (для Android компонентов):

```kotlin
class MainActivity : AppCompatActivity() {

    // Field injection - для Android компонентов
    @Inject
    lateinit var viewModelFactory: ViewModelProvider.Factory

    @Inject
    lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        // Инъекция до использования полей
        (application as MyApp).appComponent.inject(this)
        super.onCreate(savedInstanceState)
    }
}

class LegacyService {

    @Inject
    lateinit var repository: UserRepository

    // Method injection - вызывается после конструктора
    @Inject
    fun init(logger: Logger) {
        logger.log("Service initialized")
    }
}
```

### Комбинированный Пример

```kotlin
// Ваш класс - используем @Inject
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val analyticsTracker: AnalyticsTracker
) : ViewModel() {
    // ...
}

// Модуль для сторонних зависимостей
@Module
class AnalyticsModule {

    @Provides
    fun provideFirebaseAnalytics(context: Context): FirebaseAnalytics {
        return FirebaseAnalytics.getInstance(context)
    }
}

// Ваш класс-обёртка с @Inject
class AnalyticsTracker @Inject constructor(
    private val firebaseAnalytics: FirebaseAnalytics
) {
    fun trackEvent(name: String, params: Bundle) {
        firebaseAnalytics.logEvent(name, params)
    }
}
```

### Правило Большого Пальца

> **Если можете поставить @Inject на конструктор - ставьте.**
> @Provides только когда это невозможно.

---

## Answer (EN)

**@Inject** and **@Provides** are two ways to tell Dagger how to create dependencies. The choice depends on whether you control the class source code.

### @Inject - Constructor Injection

Use `@Inject` on constructor when:
- You control the class source code
- Class doesn't require complex creation logic
- This is the preferred way (cleaner and simpler)

```kotlin
// Dagger automatically knows how to create this class
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userDao: UserDao,
    private val dispatchers: CoroutineDispatchers
) {
    suspend fun getUser(id: String): User {
        return apiService.getUser(id).also { user ->
            userDao.insert(user)
        }
    }
}

// Nested dependencies also use @Inject
class ApiService @Inject constructor(
    private val retrofit: Retrofit
) {
    // ...
}

class UserDao @Inject constructor(
    private val database: AppDatabase
) {
    // ...
}
```

### @Provides - Module Provision

Use `@Provides` in a module when:
- Class is from a third-party library (Retrofit, OkHttp, Room)
- Complex creation logic is needed
- Object needs configuration
- Working with interfaces

```kotlin
@Module
class NetworkModule {

    // Third-party library - cannot add @Inject
    @Provides
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(AuthInterceptor())
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()
    }

    // Complex configuration
    @Provides
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        gson: Gson
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .addCallAdapterFactory(CoroutineCallAdapterFactory())
            .build()
    }

    // Creation via factory method
    @Provides
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

@Module
class DatabaseModule {

    @Provides
    fun provideDatabase(context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        )
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

### Comparison Table

| Criterion | @Inject | @Provides |
|-----------|---------|-----------|
| Source code | Your class | Third-party class |
| Placement | On constructor | In @Module |
| Complexity | Simple creation | Any logic |
| Readability | Dependencies visible in class | Dependencies in module |
| Testing | Easy to mock | Need test module |
| Preference | Default choice | When @Inject impossible |

### @Inject on Fields and Methods

Besides constructor, `@Inject` works on fields and methods (for Android components):

```kotlin
class MainActivity : AppCompatActivity() {

    // Field injection - for Android components
    @Inject
    lateinit var viewModelFactory: ViewModelProvider.Factory

    @Inject
    lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        // Injection before using fields
        (application as MyApp).appComponent.inject(this)
        super.onCreate(savedInstanceState)
    }
}

class LegacyService {

    @Inject
    lateinit var repository: UserRepository

    // Method injection - called after constructor
    @Inject
    fun init(logger: Logger) {
        logger.log("Service initialized")
    }
}
```

### Combined Example

```kotlin
// Your class - use @Inject
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val analyticsTracker: AnalyticsTracker
) : ViewModel() {
    // ...
}

// Module for third-party dependencies
@Module
class AnalyticsModule {

    @Provides
    fun provideFirebaseAnalytics(context: Context): FirebaseAnalytics {
        return FirebaseAnalytics.getInstance(context)
    }
}

// Your wrapper class with @Inject
class AnalyticsTracker @Inject constructor(
    private val firebaseAnalytics: FirebaseAnalytics
) {
    fun trackEvent(name: String, params: Bundle) {
        firebaseAnalytics.logEvent(name, params)
    }
}
```

### Rule of Thumb

> **If you can put @Inject on a constructor - do it.**
> Use @Provides only when that's impossible.

---

## Дополнительные Вопросы (RU)

- Можно ли использовать @Inject и @Provides для одного типа?
- Когда использовать @Binds вместо @Provides?
- Как работает приоритет между @Inject и @Provides?

## Follow-ups

- Can you use both @Inject and @Provides for the same type?
- When should you use @Binds instead of @Provides?
- How does priority work between @Inject and @Provides?

## Ссылки (RU)

- [Dagger @Inject Documentation](https://dagger.dev/dev-guide/)
- [Android DI Best Practices](https://developer.android.com/training/dependency-injection)

## References

- [Dagger @Inject Documentation](https://dagger.dev/dev-guide/)
- [Android DI Best Practices](https://developer.android.com/training/dependency-injection)

## Связанные Вопросы (RU)

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-lazy-provider--dagger--medium]]
- [[q-dagger-component-builder--dagger--medium]]

### Hard
- [[q-dagger-scopes-custom--dagger--hard]]

## Related Questions

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-lazy-provider--dagger--medium]]
- [[q-dagger-component-builder--dagger--medium]]

### Hard
- [[q-dagger-scopes-custom--dagger--hard]]

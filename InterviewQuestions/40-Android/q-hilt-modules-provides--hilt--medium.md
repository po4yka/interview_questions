---
id: android-hilt-002
title: Hilt Modules @Provides @Binds / Модули Hilt @Provides @Binds
aliases: [Hilt Modules, Модули Hilt, Provides, Binds, Hilt Module]
topic: android
subtopics: [di-hilt, architecture]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-hilt-setup-annotations--hilt--medium, q-hilt-scopes--hilt--hard, q-hilt-qualifiers--hilt--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/di-hilt, android/architecture, difficulty/medium, hilt, dependency-injection, dagger-module]

---
# Vopros (RU)
> Как работают модули в Hilt? Объясните разницу между @Module, @Provides и @Binds.

# Question (EN)
> How do modules work in Hilt? Explain the difference between @Module, @Provides, and @Binds.

---

## Otvet (RU)

Модули в Hilt - это классы, которые содержат инструкции о том, как создавать зависимости. Они являются основным способом предоставления объектов, которые нельзя создать через constructor injection (интерфейсы, классы из сторонних библиотек, объекты требующие конфигурации).

### @Module и @InstallIn

`@Module` помечает класс как Dagger/Hilt модуль. `@InstallIn` указывает, в какой компонент Hilt устанавливается этот модуль (определяет scope/время жизни зависимостей).

```kotlin
@Module
@InstallIn(SingletonComponent::class) // Зависимости живут всё время жизни приложения
object NetworkModule {
    // Методы предоставления зависимостей
}

@Module
@InstallIn(ViewModelComponent::class) // Зависимости привязаны к ViewModel
abstract class ViewModelModule {
    // Абстрактные binding-методы
}
```

**Стандартные компоненты Hilt:**

| Компонент | Scope | Когда создается |
|-----------|-------|-----------------|
| `SingletonComponent` | `@Singleton` | Application.onCreate() |
| `ActivityRetainedComponent` | `@ActivityRetainedScoped` | Activity.onCreate() (переживает конфиг. изменения) |
| `ViewModelComponent` | `@ViewModelScoped` | ViewModel создан |
| `ActivityComponent` | `@ActivityScoped` | Activity.onCreate() |
| `FragmentComponent` | `@FragmentScoped` | Fragment.onAttach() |
| `ViewComponent` | `@ViewScoped` | View.super() |
| `ServiceComponent` | `@ServiceScoped` | Service.onCreate() |

### @Provides

Используется для предоставления экземпляров, когда:
- Класс из сторонней библиотеки (вы не можете добавить `@Inject` в конструктор)
- Требуется конфигурация при создании объекта
- Нужно использовать builder pattern

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

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
            .client(okHttpClient) // Hilt автоматически предоставит OkHttpClient
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideGson(): Gson {
        return GsonBuilder()
            .setDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
            .create()
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
            "app_database"
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

### @Binds

Используется для связывания интерфейса с его реализацией. Это более эффективно, чем `@Provides`, так как не создает дополнительный метод-обертку.

```kotlin
// Интерфейс
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun saveUser(user: User)
}

// Реализация с @Inject в конструкторе
class UserRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val userDao: UserDao
) : UserRepository {

    override suspend fun getUser(id: String): User {
        return try {
            val user = apiService.getUser(id)
            userDao.insert(user)
            user
        } catch (e: Exception) {
            userDao.getUser(id) ?: throw e
        }
    }

    override suspend fun saveUser(user: User) {
        userDao.insert(user)
        apiService.updateUser(user)
    }
}

// Модуль с @Binds
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository

    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl
    ): AuthRepository
}
```

**Правила для @Binds:**
1. Модуль должен быть `abstract class` или `interface`
2. Метод должен быть `abstract`
3. Метод принимает один параметр - реализацию
4. Возвращаемый тип - интерфейс или базовый класс
5. Реализация должна иметь `@Inject` конструктор или быть предоставлена через `@Provides`

### Комбинирование @Provides и @Binds

Если нужно использовать оба подхода в одном модуле, используйте companion object:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {

    // @Binds методы в abstract class
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository

    @Binds
    @Singleton
    abstract fun bindSettingsRepository(impl: SettingsRepositoryImpl): SettingsRepository

    companion object {
        // @Provides методы в companion object
        @Provides
        @Singleton
        fun provideSharedPreferences(
            @ApplicationContext context: Context
        ): SharedPreferences {
            return context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
        }

        @Provides
        @Singleton
        fun provideDispatcher(): CoroutineDispatcher {
            return Dispatchers.IO
        }
    }
}
```

### Когда использовать @Provides vs @Binds

| Сценарий | Используйте |
|----------|-------------|
| Связать интерфейс с реализацией | `@Binds` |
| Класс из сторонней библиотеки | `@Provides` |
| Нужен builder pattern | `@Provides` |
| Нужна логика при создании | `@Provides` |
| Реализация имеет `@Inject` конструктор | `@Binds` (предпочтительно) |
| Несколько реализаций интерфейса | `@Binds` + `@Qualifier` |

### Практический пример: многослойная архитектура

```kotlin
// Domain layer - интерфейсы
interface GetUserUseCase {
    suspend operator fun invoke(id: String): Result<User>
}

interface UserRepository {
    suspend fun getUser(id: String): User
}

// Data layer - реализации
class GetUserUseCaseImpl @Inject constructor(
    private val repository: UserRepository
) : GetUserUseCase {

    override suspend fun invoke(id: String): Result<User> {
        return runCatching { repository.getUser(id) }
    }
}

class UserRepositoryImpl @Inject constructor(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : UserRepository {

    override suspend fun getUser(id: String): User = withContext(dispatcher) {
        try {
            remoteDataSource.getUser(id).also { user ->
                localDataSource.cacheUser(user)
            }
        } catch (e: Exception) {
            localDataSource.getUser(id) ?: throw e
        }
    }
}

// DI модули
@Module
@InstallIn(SingletonComponent::class)
abstract class UseCaseModule {

    @Binds
    abstract fun bindGetUserUseCase(impl: GetUserUseCaseImpl): GetUserUseCase
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {

    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    @DefaultDispatcher
    fun provideDefaultDispatcher(): CoroutineDispatcher = Dispatchers.Default

    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
}

// Qualifiers для диспетчеров
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class DefaultDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainDispatcher
```

---

## Answer (EN)

Modules in Hilt are classes that contain instructions on how to create dependencies. They are the primary way to provide objects that cannot be created through constructor injection (interfaces, classes from third-party libraries, objects requiring configuration).

### @Module and @InstallIn

`@Module` marks a class as a Dagger/Hilt module. `@InstallIn` specifies which Hilt component this module is installed in (determines the scope/lifetime of dependencies).

```kotlin
@Module
@InstallIn(SingletonComponent::class) // Dependencies live for the app's lifetime
object NetworkModule {
    // Dependency provision methods
}

@Module
@InstallIn(ViewModelComponent::class) // Dependencies bound to ViewModel
abstract class ViewModelModule {
    // Abstract binding methods
}
```

**Standard Hilt Components:**

| Component | Scope | Created When |
|-----------|-------|--------------|
| `SingletonComponent` | `@Singleton` | Application.onCreate() |
| `ActivityRetainedComponent` | `@ActivityRetainedScoped` | Activity.onCreate() (survives config changes) |
| `ViewModelComponent` | `@ViewModelScoped` | ViewModel created |
| `ActivityComponent` | `@ActivityScoped` | Activity.onCreate() |
| `FragmentComponent` | `@FragmentScoped` | Fragment.onAttach() |
| `ViewComponent` | `@ViewScoped` | View.super() |
| `ServiceComponent` | `@ServiceScoped` | Service.onCreate() |

### @Provides

Used to provide instances when:
- The class is from a third-party library (you cannot add `@Inject` to the constructor)
- Configuration is required when creating the object
- You need to use the builder pattern

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

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
            .client(okHttpClient) // Hilt automatically provides OkHttpClient
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideGson(): Gson {
        return GsonBuilder()
            .setDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
            .create()
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
            "app_database"
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}
```

### @Binds

Used to bind an interface to its implementation. This is more efficient than `@Provides` as it doesn't create an additional wrapper method.

```kotlin
// Interface
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun saveUser(user: User)
}

// Implementation with @Inject constructor
class UserRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val userDao: UserDao
) : UserRepository {

    override suspend fun getUser(id: String): User {
        return try {
            val user = apiService.getUser(id)
            userDao.insert(user)
            user
        } catch (e: Exception) {
            userDao.getUser(id) ?: throw e
        }
    }

    override suspend fun saveUser(user: User) {
        userDao.insert(user)
        apiService.updateUser(user)
    }
}

// Module with @Binds
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository

    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl
    ): AuthRepository
}
```

**Rules for @Binds:**
1. Module must be an `abstract class` or `interface`
2. Method must be `abstract`
3. Method takes one parameter - the implementation
4. Return type is the interface or base class
5. Implementation must have an `@Inject` constructor or be provided via `@Provides`

### Combining @Provides and @Binds

If you need to use both approaches in one module, use a companion object:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {

    // @Binds methods in abstract class
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository

    @Binds
    @Singleton
    abstract fun bindSettingsRepository(impl: SettingsRepositoryImpl): SettingsRepository

    companion object {
        // @Provides methods in companion object
        @Provides
        @Singleton
        fun provideSharedPreferences(
            @ApplicationContext context: Context
        ): SharedPreferences {
            return context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
        }

        @Provides
        @Singleton
        fun provideDispatcher(): CoroutineDispatcher {
            return Dispatchers.IO
        }
    }
}
```

### When to Use @Provides vs @Binds

| Scenario | Use |
|----------|-----|
| Bind interface to implementation | `@Binds` |
| Class from third-party library | `@Provides` |
| Builder pattern needed | `@Provides` |
| Logic needed during creation | `@Provides` |
| Implementation has `@Inject` constructor | `@Binds` (preferred) |
| Multiple implementations of interface | `@Binds` + `@Qualifier` |

### Practical Example: Multi-layer Architecture

```kotlin
// Domain layer - interfaces
interface GetUserUseCase {
    suspend operator fun invoke(id: String): Result<User>
}

interface UserRepository {
    suspend fun getUser(id: String): User
}

// Data layer - implementations
class GetUserUseCaseImpl @Inject constructor(
    private val repository: UserRepository
) : GetUserUseCase {

    override suspend fun invoke(id: String): Result<User> {
        return runCatching { repository.getUser(id) }
    }
}

class UserRepositoryImpl @Inject constructor(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : UserRepository {

    override suspend fun getUser(id: String): User = withContext(dispatcher) {
        try {
            remoteDataSource.getUser(id).also { user ->
                localDataSource.cacheUser(user)
            }
        } catch (e: Exception) {
            localDataSource.getUser(id) ?: throw e
        }
    }
}

// DI modules
@Module
@InstallIn(SingletonComponent::class)
abstract class UseCaseModule {

    @Binds
    abstract fun bindGetUserUseCase(impl: GetUserUseCaseImpl): GetUserUseCase
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {

    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    @DefaultDispatcher
    fun provideDefaultDispatcher(): CoroutineDispatcher = Dispatchers.Default

    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
}

// Qualifiers for dispatchers
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class DefaultDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainDispatcher
```

---

## Dopolnitelnye Voprosy (RU)

- Почему `@Binds` эффективнее `@Provides` для связывания интерфейсов?
- Можно ли иметь несколько `@InstallIn` для одного модуля?
- Как организовать модули в большом проекте?
- Что произойдет, если забыть добавить `@InstallIn`?

## Follow-ups

- Why is `@Binds` more efficient than `@Provides` for binding interfaces?
- Can you have multiple `@InstallIn` for a single module?
- How do you organize modules in a large project?
- What happens if you forget to add `@InstallIn`?

---

## Ssylki (RU)

- [Hilt Modules Documentation](https://developer.android.com/training/dependency-injection/hilt-android#hilt-modules)
- [Dagger Binds vs Provides](https://dagger.dev/dev-guide/)

## References

- [Hilt Modules Documentation](https://developer.android.com/training/dependency-injection/hilt-android#hilt-modules)
- [Dagger Binds vs Provides](https://dagger.dev/dev-guide/)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-qualifiers--hilt--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]
- [[q-hilt-custom-components--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-qualifiers--hilt--medium]]
- [[q-hilt-viewmodel-injection--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]
- [[q-hilt-custom-components--hilt--hard]]

---
id: android-hilt-006
title: Hilt Qualifiers / Квалификаторы в Hilt
aliases: [Hilt Qualifiers, Квалификаторы Hilt, Named, Qualifier, Multiple Bindings]
topic: android
subtopics: [di-hilt, architecture]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-hilt-modules-provides--hilt--medium, q-hilt-scopes--hilt--hard, q-hilt-setup-annotations--hilt--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/di-hilt, android/architecture, difficulty/medium, hilt, qualifiers, dependency-injection]

---
# Vopros (RU)
> Как использовать @Qualifier и @Named в Hilt для предоставления нескольких реализаций одного типа?

# Question (EN)
> How do you use @Qualifier and @Named in Hilt to provide multiple implementations of the same type?

---

## Otvet (RU)

Qualifiers (квалификаторы) в Hilt позволяют различать несколько зависимостей одного типа. Это необходимо, когда у вас есть несколько реализаций интерфейса или несколько экземпляров одного класса с разной конфигурацией.

### Проблема без квалификаторов

```kotlin
// Ошибка: Hilt не знает, какой Retrofit использовать
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideMainRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.main.com/")
            .build()
    }

    @Provides
    @Singleton
    fun provideAnalyticsRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://analytics.example.com/")
            .build()
    }
    // ОШИБКА КОМПИЛЯЦИИ: Duplicate binding for Retrofit
}
```

### Решение 1: Кастомные Qualifiers (рекомендуется)

```kotlin
// Определение квалификаторов
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainApi

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AnalyticsApi

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthApi

// Использование в модуле
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    @MainApi
    fun provideMainRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.main.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    @AnalyticsApi
    fun provideAnalyticsRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://analytics.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    @AuthApi
    fun provideAuthRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://auth.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    // API сервисы с квалификаторами
    @Provides
    @Singleton
    fun provideMainApiService(@MainApi retrofit: Retrofit): MainApiService {
        return retrofit.create(MainApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideAnalyticsService(@AnalyticsApi retrofit: Retrofit): AnalyticsApiService {
        return retrofit.create(AnalyticsApiService::class.java)
    }
}

// Использование в классе
class DataRepository @Inject constructor(
    @MainApi private val mainRetrofit: Retrofit,
    @AnalyticsApi private val analyticsRetrofit: Retrofit
) {
    // ...
}

@HiltViewModel
class MainViewModel @Inject constructor(
    private val mainApiService: MainApiService, // Не нужен квалификатор - уникальный тип
    private val analyticsService: AnalyticsApiService
) : ViewModel()
```

### Решение 2: @Named (встроенный квалификатор)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    @Named("user_db")
    fun provideUserDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "user_database"
        ).build()
    }

    @Provides
    @Singleton
    @Named("cache_db")
    fun provideCacheDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "cache_database"
        ).build()
    }
}

// Использование
class UserRepository @Inject constructor(
    @Named("user_db") private val userDatabase: AppDatabase,
    @Named("cache_db") private val cacheDatabase: AppDatabase
) {
    // ...
}
```

### Когда использовать @Qualifier vs @Named

| Критерий | Кастомный @Qualifier | @Named |
|----------|---------------------|--------|
| Type-safety | Да (compile-time) | Нет (string-based) |
| Рефакторинг | Безопасный | Легко ошибиться |
| Читаемость | Лучше | Хуже при многих именах |
| Усилия | Больше кода | Меньше кода |

**Рекомендация:** Используйте кастомные `@Qualifier` для production-кода и `@Named` для быстрых прототипов или тестов.

### Qualifiers для Coroutine Dispatchers

Частый use case - предоставление разных диспетчеров:

```kotlin
// Квалификаторы для диспетчеров
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class DefaultDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainImmediateDispatcher

// Модуль
@Module
@InstallIn(SingletonComponent::class)
object DispatchersModule {

    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    @DefaultDispatcher
    fun provideDefaultDispatcher(): CoroutineDispatcher = Dispatchers.Default

    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main

    @Provides
    @MainImmediateDispatcher
    fun provideMainImmediateDispatcher(): CoroutineDispatcher = Dispatchers.Main.immediate
}

// Использование в репозитории
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userDao: UserDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {

    suspend fun getUser(id: String): User = withContext(ioDispatcher) {
        try {
            apiService.getUser(id).also { user ->
                userDao.insert(user)
            }
        } catch (e: Exception) {
            userDao.getUser(id) ?: throw e
        }
    }
}

// В ViewModel
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: UserRepository,
    @MainDispatcher private val mainDispatcher: CoroutineDispatcher
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            try {
                val user = repository.getUser(userId)
                withContext(mainDispatcher) {
                    _uiState.value = UiState.Success(user)
                }
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "")
            }
        }
    }
}
```

### Qualifiers для нескольких реализаций интерфейса

```kotlin
// Интерфейс
interface ImageLoader {
    fun load(url: String, target: ImageView)
}

// Реализации
class GlideImageLoader @Inject constructor(
    @ApplicationContext private val context: Context
) : ImageLoader {
    override fun load(url: String, target: ImageView) {
        Glide.with(context).load(url).into(target)
    }
}

class CoilImageLoader @Inject constructor(
    @ApplicationContext private val context: Context
) : ImageLoader {
    override fun load(url: String, target: ImageView) {
        target.load(url)
    }
}

// Квалификаторы
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class GlideLoader

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class CoilLoader

// Модуль с @Binds
@Module
@InstallIn(SingletonComponent::class)
abstract class ImageLoaderModule {

    @Binds
    @Singleton
    @GlideLoader
    abstract fun bindGlideLoader(impl: GlideImageLoader): ImageLoader

    @Binds
    @Singleton
    @CoilLoader
    abstract fun bindCoilLoader(impl: CoilImageLoader): ImageLoader
}

// Использование
class ProfileScreen @Inject constructor(
    @CoilLoader private val imageLoader: ImageLoader
) {
    fun loadAvatar(url: String, imageView: ImageView) {
        imageLoader.load(url, imageView)
    }
}
```

### Qualifiers с параметрами (продвинутый уровень)

```kotlin
// Квалификатор с параметром
@Qualifier
@Retention(AnnotationRetention.RUNTIME)
annotation class BaseUrl(val value: String)

// К сожалению, Dagger/Hilt не поддерживает runtime-параметры в квалификаторах
// Вместо этого используйте отдельные квалификаторы или @Named
```

### Встроенные квалификаторы Hilt

Hilt предоставляет несколько встроенных квалификаторов:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object ContextModule {

    @Provides
    fun provideSharedPreferences(
        @ApplicationContext context: Context // Встроенный квалификатор
    ): SharedPreferences {
        return context.getSharedPreferences("prefs", Context.MODE_PRIVATE)
    }
}

@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {

    @Provides
    fun provideLayoutInflater(
        @ActivityContext context: Context // Встроенный квалификатор
    ): LayoutInflater {
        return LayoutInflater.from(context)
    }
}
```

### Тестирование с Qualifiers

```kotlin
// Production модуль
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// Тестовый модуль
@Module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
abstract class FakeRepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: FakeUserRepository): UserRepository
}

// Или с @BindValue для конкретного теста
@HiltAndroidTest
class UserScreenTest {

    @BindValue
    @JvmField
    @IoDispatcher
    val testDispatcher: CoroutineDispatcher = StandardTestDispatcher()

    // ...
}
```

---

## Answer (EN)

Qualifiers in Hilt allow distinguishing between multiple dependencies of the same type. This is necessary when you have multiple implementations of an interface or multiple instances of the same class with different configurations.

### The Problem Without Qualifiers

```kotlin
// Error: Hilt doesn't know which Retrofit to use
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideMainRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.main.com/")
            .build()
    }

    @Provides
    @Singleton
    fun provideAnalyticsRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://analytics.example.com/")
            .build()
    }
    // COMPILE ERROR: Duplicate binding for Retrofit
}
```

### Solution 1: Custom Qualifiers (recommended)

```kotlin
// Define qualifiers
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainApi

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AnalyticsApi

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthApi

// Use in module
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    @MainApi
    fun provideMainRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.main.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    @AnalyticsApi
    fun provideAnalyticsRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://analytics.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    @AuthApi
    fun provideAuthRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://auth.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    // API services with qualifiers
    @Provides
    @Singleton
    fun provideMainApiService(@MainApi retrofit: Retrofit): MainApiService {
        return retrofit.create(MainApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideAnalyticsService(@AnalyticsApi retrofit: Retrofit): AnalyticsApiService {
        return retrofit.create(AnalyticsApiService::class.java)
    }
}

// Usage in class
class DataRepository @Inject constructor(
    @MainApi private val mainRetrofit: Retrofit,
    @AnalyticsApi private val analyticsRetrofit: Retrofit
) {
    // ...
}

@HiltViewModel
class MainViewModel @Inject constructor(
    private val mainApiService: MainApiService, // No qualifier needed - unique type
    private val analyticsService: AnalyticsApiService
) : ViewModel()
```

### Solution 2: @Named (built-in qualifier)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    @Named("user_db")
    fun provideUserDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "user_database"
        ).build()
    }

    @Provides
    @Singleton
    @Named("cache_db")
    fun provideCacheDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "cache_database"
        ).build()
    }
}

// Usage
class UserRepository @Inject constructor(
    @Named("user_db") private val userDatabase: AppDatabase,
    @Named("cache_db") private val cacheDatabase: AppDatabase
) {
    // ...
}
```

### When to Use @Qualifier vs @Named

| Criterion | Custom @Qualifier | @Named |
|-----------|------------------|--------|
| Type-safety | Yes (compile-time) | No (string-based) |
| Refactoring | Safe | Error-prone |
| Readability | Better | Worse with many names |
| Effort | More code | Less code |

**Recommendation:** Use custom `@Qualifier` for production code and `@Named` for quick prototypes or tests.

### Qualifiers for Coroutine Dispatchers

Common use case - providing different dispatchers:

```kotlin
// Dispatcher qualifiers
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class DefaultDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainImmediateDispatcher

// Module
@Module
@InstallIn(SingletonComponent::class)
object DispatchersModule {

    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO

    @Provides
    @DefaultDispatcher
    fun provideDefaultDispatcher(): CoroutineDispatcher = Dispatchers.Default

    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main

    @Provides
    @MainImmediateDispatcher
    fun provideMainImmediateDispatcher(): CoroutineDispatcher = Dispatchers.Main.immediate
}

// Usage in repository
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userDao: UserDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) {

    suspend fun getUser(id: String): User = withContext(ioDispatcher) {
        try {
            apiService.getUser(id).also { user ->
                userDao.insert(user)
            }
        } catch (e: Exception) {
            userDao.getUser(id) ?: throw e
        }
    }
}
```

### Built-in Hilt Qualifiers

Hilt provides several built-in qualifiers:

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object ContextModule {

    @Provides
    fun provideSharedPreferences(
        @ApplicationContext context: Context // Built-in qualifier
    ): SharedPreferences {
        return context.getSharedPreferences("prefs", Context.MODE_PRIVATE)
    }
}

@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {

    @Provides
    fun provideLayoutInflater(
        @ActivityContext context: Context // Built-in qualifier
    ): LayoutInflater {
        return LayoutInflater.from(context)
    }
}
```

---

## Dopolnitelnye Voprosy (RU)

- Почему `@Retention(AnnotationRetention.BINARY)` важен для квалификаторов?
- Можно ли использовать квалификаторы с `@Binds`?
- Как организовать квалификаторы в большом проекте?
- Как квалификаторы влияют на тестирование?

## Follow-ups

- Why is `@Retention(AnnotationRetention.BINARY)` important for qualifiers?
- Can you use qualifiers with `@Binds`?
- How do you organize qualifiers in a large project?
- How do qualifiers affect testing?

---

## Ssylki (RU)

- [Hilt - Multiple bindings](https://developer.android.com/training/dependency-injection/hilt-android#multiple-bindings)
- [Dagger - Qualifiers](https://dagger.dev/dev-guide/)

## References

- [Hilt - Multiple bindings](https://developer.android.com/training/dependency-injection/hilt-android#multiple-bindings)
- [Dagger - Qualifiers](https://dagger.dev/dev-guide/)

---

## Svyazannye Voprosy (RU)

### Medium
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-testing--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]

## Related Questions

### Medium
- [[q-hilt-modules-provides--hilt--medium]]
- [[q-hilt-setup-annotations--hilt--medium]]
- [[q-hilt-testing--hilt--medium]]

### Hard
- [[q-hilt-scopes--hilt--hard]]
- [[q-hilt-multimodule--hilt--hard]]

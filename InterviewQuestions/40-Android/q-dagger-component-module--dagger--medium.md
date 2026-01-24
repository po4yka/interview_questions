---
id: android-dagger-001
title: Dagger Component and Module Basics / Основы Component и Module в Dagger
aliases: [Dagger Component, Dagger Module, Component и Module]
topic: android
subtopics: [dagger, di-dagger]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, q-dagger-inject-provides--dagger--medium, q-dagger-subcomponents--dagger--hard]
created: 2026-01-23
updated: 2026-01-23
tags: [android/di-dagger, dependency-injection, difficulty/medium, dagger, component, module]

---
# Вопрос (RU)
> Что такое @Component и @Module в Dagger и как они работают вместе?

# Question (EN)
> What are @Component and @Module in Dagger and how do they work together?

---

## Ответ (RU)

**@Component** и **@Module** - это два основных строительных блока Dagger для организации dependency injection.

### @Module - Поставщик Зависимостей

`@Module` - это класс, который содержит методы для создания зависимостей. Используется когда:
- Нельзя аннотировать конструктор класса (сторонние библиотеки)
- Нужна особая логика создания объекта
- Требуется биндинг интерфейса к реализации

```kotlin
@Module
class NetworkModule {

    @Provides
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }

    @Provides
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
```

### @Module с object (Kotlin)

Для статических provide-методов используйте `object` с `@JvmStatic`:

```kotlin
@Module
object AppModule {

    @Provides
    @JvmStatic
    fun provideContext(application: Application): Context {
        return application.applicationContext
    }
}
```

### @Component - Граф Зависимостей

`@Component` - это интерфейс, который связывает модули и точки внедрения. Dagger генерирует реализацию этого интерфейса.

```kotlin
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {

    // Метод инъекции - внедряет зависимости в целевой объект
    fun inject(activity: MainActivity)

    // Provision метод - возвращает зависимость напрямую
    fun getApiService(): ApiService

    // Factory для создания компонента с параметрами
    @Component.Factory
    interface Factory {
        fun create(@BindsInstance application: Application): AppComponent
    }
}
```

### Использование Компонента

```kotlin
class MyApplication : Application() {

    lateinit var appComponent: AppComponent
        private set

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.factory()
            .create(this)
    }
}

class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var apiService: ApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        // Инъекция должна быть до super.onCreate()
        (application as MyApplication).appComponent.inject(this)
        super.onCreate(savedInstanceState)
    }
}
```

### @Binds - Биндинг Интерфейсов

Для связывания интерфейса с реализацией используйте `@Binds` в абстрактном модуле:

```kotlin
@Module
abstract class RepositoryModule {

    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// Реализация должна иметь @Inject конструктор
class UserRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val database: AppDatabase
) : UserRepository {
    // ...
}
```

### Комбинирование @Binds и @Provides

```kotlin
@Module
abstract class DataModule {

    @Binds
    abstract fun bindRepository(impl: RepositoryImpl): Repository

    companion object {
        @Provides
        fun provideGson(): Gson {
            return GsonBuilder()
                .setDateFormat("yyyy-MM-dd")
                .create()
        }
    }
}
```

### Ключевые Правила

| Правило | Описание |
|---------|----------|
| Один @Provides на тип | Без квалификаторов нельзя иметь два метода с одним возвращаемым типом |
| Зависимости в параметрах | Параметры @Provides методов автоматически инжектятся |
| Порядок модулей не важен | Dagger сам определяет порядок создания зависимостей |
| Компонент - точка входа | Через компонент получаем доступ ко всему графу |

---

## Answer (EN)

**@Component** and **@Module** are the two fundamental building blocks in Dagger for organizing dependency injection.

### @Module - Dependency Provider

`@Module` is a class containing methods to create dependencies. Used when:
- Cannot annotate constructor (third-party libraries)
- Need custom creation logic
- Need to bind interface to implementation

```kotlin
@Module
class NetworkModule {

    @Provides
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }

    @Provides
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
```

### @Module with object (Kotlin)

For static provide methods, use `object` with `@JvmStatic`:

```kotlin
@Module
object AppModule {

    @Provides
    @JvmStatic
    fun provideContext(application: Application): Context {
        return application.applicationContext
    }
}
```

### @Component - Dependency Graph

`@Component` is an interface that connects modules and injection targets. Dagger generates the implementation.

```kotlin
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {

    // Injection method - injects dependencies into target
    fun inject(activity: MainActivity)

    // Provision method - returns dependency directly
    fun getApiService(): ApiService

    // Factory to create component with parameters
    @Component.Factory
    interface Factory {
        fun create(@BindsInstance application: Application): AppComponent
    }
}
```

### Using the Component

```kotlin
class MyApplication : Application() {

    lateinit var appComponent: AppComponent
        private set

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.factory()
            .create(this)
    }
}

class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var apiService: ApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        // Injection must happen before super.onCreate()
        (application as MyApplication).appComponent.inject(this)
        super.onCreate(savedInstanceState)
    }
}
```

### @Binds - Interface Binding

To bind interface to implementation, use `@Binds` in an abstract module:

```kotlin
@Module
abstract class RepositoryModule {

    @Binds
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// Implementation must have @Inject constructor
class UserRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val database: AppDatabase
) : UserRepository {
    // ...
}
```

### Combining @Binds and @Provides

```kotlin
@Module
abstract class DataModule {

    @Binds
    abstract fun bindRepository(impl: RepositoryImpl): Repository

    companion object {
        @Provides
        fun provideGson(): Gson {
            return GsonBuilder()
                .setDateFormat("yyyy-MM-dd")
                .create()
        }
    }
}
```

### Key Rules

| Rule | Description |
|------|-------------|
| One @Provides per type | Without qualifiers, cannot have two methods with same return type |
| Dependencies as parameters | Parameters of @Provides methods are auto-injected |
| Module order doesn't matter | Dagger determines creation order automatically |
| Component is entry point | Access entire graph through component |

---

## Дополнительные Вопросы (RU)

- Когда использовать `@Binds` вместо `@Provides`?
- Как передать runtime-параметры в компонент?
- Чем отличается `@Component.Factory` от `@Component.Builder`?

## Follow-ups

- When should you use `@Binds` instead of `@Provides`?
- How do you pass runtime parameters to a component?
- What's the difference between `@Component.Factory` and `@Component.Builder`?

## Ссылки (RU)

- [Dagger Documentation](https://dagger.dev/dev-guide/)
- [Android Dagger Guide](https://developer.android.com/training/dependency-injection/dagger-basics)

## References

- [Dagger Documentation](https://dagger.dev/dev-guide/)
- [Android Dagger Guide](https://developer.android.com/training/dependency-injection/dagger-basics)

## Связанные Вопросы (RU)

### Medium
- [[q-dagger-inject-provides--dagger--medium]]
- [[q-dagger-lazy-provider--dagger--medium]]
- [[q-dagger-component-builder--dagger--medium]]

### Hard
- [[q-dagger-subcomponents--dagger--hard]]
- [[q-dagger-scopes-custom--dagger--hard]]

## Related Questions

### Medium
- [[q-dagger-inject-provides--dagger--medium]]
- [[q-dagger-lazy-provider--dagger--medium]]
- [[q-dagger-component-builder--dagger--medium]]

### Hard
- [[q-dagger-subcomponents--dagger--hard]]
- [[q-dagger-scopes-custom--dagger--hard]]

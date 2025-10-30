---
id: 20251020-200000
title: Dagger Main Elements / Основные элементы Dagger
aliases: ["Dagger Main Elements", "Основные элементы Dagger"]
topic: android
subtopics: [di-hilt]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-dagger-field-injection--android--medium, q-dagger-framework-overview--android--hard, q-dagger-inject-annotation--android--easy]
created: 2025-10-20
updated: 2025-10-29
tags: [android/di-hilt, dagger, dependency-injection, difficulty/medium]
sources: []
---

# Вопрос (RU)
> Из каких основных элементов состоит Dagger?

# Question (EN)
> What are the main elements of Dagger?

## Ответ (RU)

Dagger построен вокруг четырех ключевых элементов, образующих граф зависимостей:

### 1. @Component — связующий интерфейс

Интерфейс, объединяющий модули и цели инъекции. Генерирует код для построения графа зависимостей:

```kotlin
@Component(modules = [NetworkModule::class])
interface AppComponent {
    fun repository(): UserRepository // ✅ Provision method
    fun inject(activity: MainActivity) // ✅ Injection method
}

// Сгенерированный Dagger код
val component = DaggerAppComponent.create()
```

**Ключевые особенности:**
- Компилируется в реализацию с префиксом `Dagger`
- Проверяет корректность графа на этапе компиляции
- Поддерживает иерархию (subcomponents) и скоупы

### 2. @Module — поставщик зависимостей

Класс с `@Provides` методами для создания зависимостей:

```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton // ✅ Scope annotation
    fun provideApiService(): ApiService =
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
            .create()
}
```

**Особенности:**
- Используется для внешних библиотек (Retrofit, Room)
- Может быть `object` (stateless) или `class` (stateful)
- Методы могут зависеть друг от друга

### 3. @Inject — маркер внедрения

Указывает места для инъекции зависимостей:

```kotlin
// ✅ Constructor injection (preferred)
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDatabase
)

// ❌ Field injection (only when constructor unavailable)
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as App).component.inject(this)
    }
}
```

**Предпочтения:**
- Constructor injection — тестируемо, immutable, no null
- Field injection — только для Android framework классов

### 4. @Provides vs @Binds

`@Provides` для конкретных реализаций, `@Binds` для интерфейсов:

```kotlin
@Module
abstract class RepositoryModule {
    @Binds // ✅ Lightweight, no body
    abstract fun bindRepository(impl: UserRepositoryImpl): UserRepository
}

@Module
object DatabaseModule {
    @Provides // ❌ Requires logic
    fun provideDatabase(context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "db").build()
}
```

### Полная интеграция

```kotlin
// 1. Определить модуль
@Module
object AppModule {
    @Provides
    fun provideRepo(api: ApiService) = UserRepositoryImpl(api)
}

// 2. Создать компонент
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}

// 3. Инициализировать в Application
class App : Application() {
    val component = DaggerAppComponent.create()
}
```

**Hilt упрощает процесс:**

```kotlin
@HiltAndroidApp
class App : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

## Answer (EN)

Dagger is built around four core elements forming the dependency graph:

### 1. @Component — Binding Interface

Interface connecting modules and injection targets. Generates code for dependency graph:

```kotlin
@Component(modules = [NetworkModule::class])
interface AppComponent {
    fun repository(): UserRepository // ✅ Provision method
    fun inject(activity: MainActivity) // ✅ Injection method
}

// Dagger-generated code
val component = DaggerAppComponent.create()
```

**Key features:**
- Compiles into implementation with `Dagger` prefix
- Validates graph correctness at compile time
- Supports hierarchy (subcomponents) and scopes

### 2. @Module — Dependency Provider

Class with `@Provides` methods for creating dependencies:

```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton // ✅ Scope annotation
    fun provideApiService(): ApiService =
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
            .create()
}
```

**Features:**
- Used for external libraries (Retrofit, Room)
- Can be `object` (stateless) or `class` (stateful)
- Methods can depend on each other

### 3. @Inject — Injection Marker

Marks places for dependency injection:

```kotlin
// ✅ Constructor injection (preferred)
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDatabase
)

// ❌ Field injection (only when constructor unavailable)
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as App).component.inject(this)
    }
}
```

**Preferences:**
- Constructor injection — testable, immutable, no null
- Field injection — only for Android framework classes

### 4. @Provides vs @Binds

`@Provides` for concrete implementations, `@Binds` for interfaces:

```kotlin
@Module
abstract class RepositoryModule {
    @Binds // ✅ Lightweight, no body
    abstract fun bindRepository(impl: UserRepositoryImpl): UserRepository
}

@Module
object DatabaseModule {
    @Provides // ❌ Requires logic
    fun provideDatabase(context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "db").build()
}
```

### Complete Integration

```kotlin
// 1. Define module
@Module
object AppModule {
    @Provides
    fun provideRepo(api: ApiService) = UserRepositoryImpl(api)
}

// 2. Create component
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}

// 3. Initialize in Application
class App : Application() {
    val component = DaggerAppComponent.create()
}
```

**Hilt simplifies the process:**

```kotlin
@HiltAndroidApp
class App : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

## Follow-ups

- How does Dagger handle circular dependencies?
- What's the difference between component scopes (@Singleton, @ActivityScoped)?
- When should you use @Binds instead of @Provides?
- How does Dagger2 differ from Dagger-Hilt?
- What are subcomponents and when to use them?

## References

- [[c-dependency-injection]]
- [[c-dagger]]
- [[c-hilt]]
- Official documentation: https://dagger.dev/dev-guide/

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] — Understanding @Inject annotation

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]] — Field vs constructor injection
- How to setup Dagger modules and components
- Understanding Dagger scopes and lifecycles

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] — Complete Dagger architecture
- Implementing custom scopes and subcomponents
- Dagger multibinding and optional dependencies

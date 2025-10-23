---
id: 20251020-200000
title: Dagger Main Elements / Основные элементы Dagger
aliases:
- Dagger Main Elements
- Основные элементы Dagger
topic: android
subtopics:
- dependency-injection
- architecture-patterns
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-dagger-inject-annotation--android--easy
- q-dagger-field-injection--android--medium
- q-dagger-framework-overview--android--hard
created: 2025-10-20
updated: 2025-10-20
tags:
- android/dependency-injection
- android/architecture-patterns
- dagger
- hilt
- dependency-injection
- components
- modules
- difficulty/medium
source: https://dagger.dev/api/latest/dagger/Component.html
source_note: Dagger Component API documentation
---# Вопрос (RU)
> Из каких основных элементов состоит Dagger?

# Question (EN)
> What are the main elements of Dagger?

## Ответ (RU)

Dagger построен вокруг нескольких ключевых элементов, которые работают вместе для обеспечения внедрения зависимостей. Основные компоненты образуют архитектуру DI системы.

### Теория: Архитектура Dagger

**Основные элементы:**
- **Component** - связывает модули и цели инъекции
- **Module** - предоставляет зависимости через провайдеры
- **@Inject** - маркирует места для внедрения зависимостей
- **@Provides** - создает зависимости в модулях

**Принципы работы:**
- Компиляционная генерация кода
- Статическая типизация зависимостей
- Автоматическое разрешение графа зависимостей
- Проверка на этапе компиляции

### 1. Component (@Component)

**Component** - интерфейс, связывающий модули и цели инъекции:

```kotlin
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {
    // Методы предоставления - экспорт зависимостей
    fun provideRepository(): UserRepository

    // Методы инъекции - внедрение в цели
    fun inject(activity: MainActivity)
    fun inject(fragment: ProfileFragment)
}
```

**Использование:**
```kotlin
class MyApplication : Application() {
    val appComponent = DaggerAppComponent.builder().build()
}
```

### 2. Module (@Module)

**Module** - класс, предоставляющий зависимости:

```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
            .create(ApiService::class.java)
    }
}
```

**Особенности модулей:**
- Содержат `@Provides` методы
- Могут быть `object` или `class`
- Поддерживают зависимости между провайдерами

### 3. @Inject Annotation

**@Inject** маркирует места для инъекции:

```kotlin
// Constructor injection
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val database: UserDatabase
)

// Field injection
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository
}
```

### 4. @Provides Methods

**@Provides** создает зависимости в модулях:

```kotlin
@Module
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .build()
    }
}
```

### Взаимодействие элементов

**Поток работы:**
1. Dagger анализирует `@Component` и связанные модули
2. Строит граф зависимостей на основе `@Inject` и `@Provides`
3. Генерирует код для создания и внедрения зависимостей
4. Проверяет корректность на этапе компиляции

**Пример полной интеграции:**
```kotlin
// Module
@Module
object AppModule {
    @Provides
    @Singleton
    fun provideUserRepository(api: ApiService): UserRepository {
        return UserRepositoryImpl(api)
    }
}

// Component
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}

// Usage
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
    }
}
```

### Hilt упрощение

Hilt автоматизирует создание компонентов:

```kotlin
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository
}
```

## Answer (EN)

Dagger is built around several key elements that work together to provide dependency injection. The main components form the DI system architecture.

### Theory: Dagger Architecture

**Core Elements:**
- **Component** - connects modules and injection targets
- **Module** - provides dependencies through providers
- **@Inject** - marks places for dependency injection
- **@Provides** - creates dependencies in modules

**Working Principles:**
- Compile-time code generation
- Static typing of dependencies
- Automatic dependency graph resolution
- Compile-time validation

### 1. Component (@Component)

**Component** - interface connecting modules and injection targets:

```kotlin
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {
    // Provision methods - export dependencies
    fun provideRepository(): UserRepository

    // Injection methods - inject into targets
    fun inject(activity: MainActivity)
    fun inject(fragment: ProfileFragment)
}
```

**Usage:**
```kotlin
class MyApplication : Application() {
    val appComponent = DaggerAppComponent.builder().build()
}
```

### 2. Module (@Module)

**Module** - class providing dependencies:

```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
            .create(ApiService::class.java)
    }
}
```

**Module features:**
- Contains `@Provides` methods
- Can be `object` or `class`
- Supports dependencies between providers

### 3. @Inject Annotation

**@Inject** marks places for injection:

```kotlin
// Constructor injection
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val database: UserDatabase
)

// Field injection
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository
}
```

### 4. @Provides Methods

**@Provides** creates dependencies in modules:

```kotlin
@Module
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .build()
    }
}
```

### Element Interaction

**Workflow:**
1. Dagger analyzes `@Component` and related modules
2. Builds dependency graph based on `@Inject` and `@Provides`
3. Generates code for creating and injecting dependencies
4. Validates correctness at compile time

**Complete integration example:**
```kotlin
// Module
@Module
object AppModule {
    @Provides
    @Singleton
    fun provideUserRepository(api: ApiService): UserRepository {
        return UserRepositoryImpl(api)
    }
}

// Component
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}

// Usage
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
    }
}
```

### Hilt Simplification

Hilt automates component creation:

```kotlin
@HiltAndroidApp
class MyApplication : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository
}
```

## Follow-ups

- How do Dagger components resolve circular dependencies?
- What's the difference between @Provides and @Binds methods?
- How does Hilt automatically create components?

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]]

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]]

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]]

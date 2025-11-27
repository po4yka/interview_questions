---
id: android-456
title: Dagger Framework Overview / Обзор фреймворка Dagger
aliases: [Dagger Framework Overview, Обзор фреймворка Dagger]
topic: android
subtopics:
  - architecture-clean
  - architecture-mvvm
  - di-hilt
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-dagger
  - c-dependency-injection
  - c-hilt
  - q-dagger-build-time-optimization--android--medium
  - q-dagger-custom-scopes--android--hard
  - q-dagger-multibinding--android--hard
  - q-dagger-purpose--android--easy
created: 2025-10-20
updated: 2025-11-10
tags: [android/architecture-clean, android/architecture-mvvm, android/di-hilt, dagger, dependency-injection, difficulty/hard, hilt]
sources:
  - "https://dagger.dev/"

date created: Saturday, November 1st 2025, 12:46:48 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---
# Вопрос (RU)
> Что известно про фреймворк Dagger?

# Question (EN)
> What do you know about the Dagger framework?

## Ответ (RU)

[[c-dagger]] — это compile-time фреймворк для [[c-dependency-injection]], генерирующий код на этапе компиляции вместо использования reflection. Основной принцип: статическая типизация зависимостей с проверкой графа зависимостей до запуска приложения.

### Ключевые Компоненты

**@Inject — Constructor Injection**
```kotlin
// ✅ Предпочтительный способ: Dagger автоматически создает экземпляр
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val database: UserDatabase
)

// ❌ Field injection — менее предпочтительно (поздняя инициализация)
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**@Module + @Provides — Сложные Зависимости**
```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(okHttp: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .client(okHttp)
            .baseUrl("https://api.example.com/")
            .build()
}
```

**@Component — Граф Зависимостей**
```kotlin
@Singleton
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)

    // ✅ Лучше: явное предоставление через интерфейс
    fun userRepository(): UserRepository
}
```

**Scopes — Управление Жизненным Циклом**
```kotlin
@Singleton  // Один экземпляр на весь граф
class ApiClient @Inject constructor()

// Пример пользовательского scope для Activity (в чистом Dagger):
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

@ActivityScope  // Один экземпляр на Activity в рамках соответствующего компонента
class SomeActivityScopedDependency @Inject constructor()

// ❌ Без scope — создается новый экземпляр при каждом запросе
```

### [[c-hilt]] — Упрощенный Dagger Для Android

Hilt автоматизирует boilerplate-код и предоставляет стандартные компоненты и scope-аннотации для Android.

```kotlin
// ✅ Hilt автоматически создает компоненты и внедряет зависимости
@HiltAndroidApp
class App : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

**Стандартные Scopes в Hilt:**
- `@Singleton` — `SingletonComponent` / уровень `Application`
- `@ActivityScoped` — `ActivityComponent` (один экземпляр на `Activity`)
- `@ActivityRetainedScoped` — `ActivityRetainedComponent` (связано с жизненным циклом `Activity`, переживает конфигурационные изменения; подходит для зависимостей `ViewModel`)
- `@ViewModelScoped` — `ViewModelComponent` (один экземпляр на `ViewModel`)
- `@FragmentScoped` — `FragmentComponent` (один экземпляр на `Fragment`)

### Преимущества Compile-Time DI

**Производительность:**
- Нет runtime reflection overhead
- Граф зависимостей строится на этапе компиляции
- Минимальные runtime-издержки при разрешении зависимостей за счет сгенерированных фабрик

**Безопасность:**
- Compile-time проверка циклических зависимостей
- Гарантия существования всех зависимостей
- Потокобезопасное создание синглтонов (через сгенерированный код и корректно настроенные компоненты)

**Тестируемость:**
- Простая замена модулей для тестов
- Изолированное тестирование компонентов
- Mock-friendly архитектура

### Дополнительные Вопросы (RU)

- Как Dagger обнаруживает и репортит циклические зависимости на этапе компиляции, и какой алгоритм обхода графа он использует?
- Каковы trade-offs между constructor injection и field injection с точки зрения неизменяемости, тестируемости и управления жизненным циклом?
- Как работают пользовательские scope в Dagger, и когда стоит создавать свои вместо использования стандартных?
- Что произойдет, если внедрить незаскопленную зависимость в scoped-компонент, и как это повлияет на создание экземпляров?
- Как иерархия компонентов Hilt соотносится с жизненным циклом Android-компонентов и как это влияет на утечки памяти?

### Ссылки (RU)

- [[c-dagger]] — концепции фреймворка Dagger
- [[c-dependency-injection]] — паттерн Dependency Injection
- [[c-hilt]] — Hilt для Android
- "https://dagger.dev/" — официальная документация Dagger

### Связанные Вопросы (RU)

#### База (проще)
- [[q-dagger-field-injection--android--medium]] — различия между field и constructor injection

#### Того Же Уровня (средний/текущий)
- [[q-dagger-build-time-optimization--android--medium]] — оптимизация времени сборки с Dagger

#### Продвинутые (сложнее)
- [[q-dagger-custom-scopes--android--hard]] — создание и управление пользовательскими scope

## Answer (EN)

[[c-dagger]] is a compile-time [[c-dependency-injection]] framework that generates code during compilation instead of using reflection. Core principle: static dependency typing with dependency graph validation before runtime.

### Key Components

**@Inject — Constructor Injection**
```kotlin
// ✅ Preferred: Dagger automatically creates instance
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val database: UserDatabase
)

// ❌ Field injection — less preferred (late initialization)
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}
```

**@Module + @Provides — Complex Dependencies**
```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(okHttp: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .client(okHttp)
            .baseUrl("https://api.example.com/")
            .build()
}
```

**@Component — Dependency Graph**
```kotlin
@Singleton
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)

    // ✅ Better: explicit provision via interface
    fun userRepository(): UserRepository
}
```

**Scopes — Lifecycle Management**
```kotlin
@Singleton  // One instance across entire graph
class ApiClient @Inject constructor()

// Example of a custom Activity scope in plain Dagger:
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

@ActivityScope  // One instance per Activity within the corresponding component
class SomeActivityScopedDependency @Inject constructor()

// ❌ No scope — new instance created on each request
```

### [[c-hilt]] — Simplified Dagger for Android

Hilt automates boilerplate and provides standard components and scope annotations tailored for Android.

```kotlin
// ✅ Hilt automatically creates components and injects dependencies
@HiltAndroidApp
class App : Application()

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

**Standard Hilt Scopes:**
- `@Singleton` — `SingletonComponent` / `Application` level
- `@ActivityScoped` — `ActivityComponent` (one instance per `Activity`)
- `@ActivityRetainedScoped` — `ActivityRetainedComponent` (tied to `Activity` lifecycle across configuration changes; suitable for `ViewModel`-related dependencies)
- `@ViewModelScoped` — `ViewModelComponent` (one instance per `ViewModel`)
- `@FragmentScoped` — `FragmentComponent` (one instance per `Fragment`)

### Compile-Time DI Advantages

**Performance:**
- No runtime reflection overhead
- Dependency graph built at compile time
- Minimal runtime overhead for dependency resolution thanks to generated factories

**Safety:**
- Compile-time cyclic dependency detection
- Guaranteed existence of all dependencies
- Thread-safe singleton creation via generated code and properly configured components

**Testability:**
- Simple module replacement for tests
- Isolated component testing
- Mock-friendly architecture

## Follow-ups

- How does Dagger detect and report cyclic dependencies at compile time, and what graph traversal algorithm does it use?
- What are the trade-offs between constructor injection and field injection in terms of immutability, testability, and lifecycle management?
- How do custom scopes work in Dagger, and when should you create them versus reusing standard scopes?
- What happens if you inject a non-scoped dependency into a scoped component, and how does this affect instance creation?
- How does Hilt's component hierarchy map to Android component lifecycles, and what are the implications for memory leaks?

## References

- [[c-dagger]] — Dagger framework concepts
- [[c-dependency-injection]] — Dependency Injection pattern
- [[c-hilt]] — Hilt wrapper for Android
- "https://dagger.dev/" — Official Dagger documentation

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-field-injection--android--medium]] — Understanding field vs constructor injection

### Related (Same Level)
- [[q-dagger-build-time-optimization--android--medium]] — Optimizing Dagger build times

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]] — Creating and managing custom scopes

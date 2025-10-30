---
id: 20251020-200000
title: Dagger Framework Overview / Обзор фреймворка Dagger
aliases: ["Dagger Framework Overview", "Обзор фреймворка Dagger"]
topic: android
subtopics: [di-hilt, architecture-mvvm, architecture-clean]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dagger, c-dependency-injection, c-hilt, q-dagger-build-time-optimization--android--medium, q-dagger-custom-scopes--android--hard]
created: 2025-10-20
updated: 2025-10-30
tags: [android/di-hilt, android/architecture-mvvm, android/architecture-clean, dagger, dependency-injection, hilt, difficulty/hard]
sources: [https://dagger.dev/]
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

@ActivityScoped  // Один экземпляр на Activity
class ViewModel @Inject constructor()

// ❌ Без scope — создается новый экземпляр при каждом запросе
```

### [[c-hilt]] — Упрощенный Dagger для Android

Hilt автоматизирует boilerplate-код и предоставляет стандартные компоненты:

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
- `@Singleton` — на уровне Application
- `@ActivityScoped` / `@ActivityRetainedScoped` — Activity/ViewModel
- `@ViewModelScoped` — ViewModel
- `@FragmentScoped` — Fragment

### Преимущества Compile-Time DI

**Производительность:**
- Нет runtime reflection overhead
- Граф зависимостей строится на этапе компиляции
- Zero runtime initialization cost

**Безопасность:**
- Compile-time проверка циклических зависимостей
- Гарантия существования всех зависимостей
- Thread-safe singleton creation

**Тестируемость:**
- Простая замена модулей для тестов
- Изолированное тестирование компонентов
- Mock-friendly архитектура

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

@ActivityScoped  // One instance per Activity
class ViewModel @Inject constructor()

// ❌ No scope — new instance created on each request
```

### [[c-hilt]] — Simplified Dagger for Android

Hilt automates boilerplate and provides standard components:

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
- `@Singleton` — Application level
- `@ActivityScoped` / `@ActivityRetainedScoped` — Activity/ViewModel
- `@ViewModelScoped` — ViewModel
- `@FragmentScoped` — Fragment

### Compile-Time DI Advantages

**Performance:**
- No runtime reflection overhead
- Dependency graph built at compile time
- Zero runtime initialization cost

**Safety:**
- Compile-time cyclic dependency detection
- Guaranteed existence of all dependencies
- Thread-safe singleton creation

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
- https://dagger.dev/ — Official Dagger documentation

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-field-injection--android--medium]] — Understanding field vs constructor injection

### Related (Same Level)
- [[q-dagger-build-time-optimization--android--medium]] — Optimizing Dagger build times

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]] — Creating and managing custom scopes

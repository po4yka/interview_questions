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
updated: 2025-10-30
tags: [android/di-hilt, dagger, dependency-injection, difficulty/medium]
sources: []
date created: Thursday, October 30th 2025, 12:02:15 pm
date modified: Thursday, October 30th 2025, 12:47:28 pm
---

# Вопрос (RU)
> Из каких основных элементов состоит Dagger?

# Question (EN)
> What are the main elements of Dagger?

## Ответ (RU)

Dagger строится на четырех ключевых элементах:

### 1. @Component — граф зависимостей

Интерфейс, генерирующий код для связывания модулей с точками инъекции:

```kotlin
@Component(modules = [NetworkModule::class])
interface AppComponent {
    fun inject(activity: MainActivity) // ✅ Injection method
}

val component = DaggerAppComponent.create() // Dagger-generated
```

**Ответственность:**
- Валидация графа на этапе компиляции
- Управление жизненным циклом зависимостей

### 2. @Module — источник зависимостей

Класс с методами `@Provides` для создания объектов:

```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton // ✅ Scoped dependency
    fun provideApi(): ApiService =
        Retrofit.Builder().baseUrl("...").build().create()
}
```

Используется для внешних библиотек, интерфейсов, сложной логики создания.

### 3. @Inject — точки внедрения

```kotlin
// ✅ Constructor injection (preferred)
class UserRepository @Inject constructor(
    private val api: ApiService
)

// ❌ Field injection (Android framework only)
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as App).component.inject(this) // Manual injection
    }
}
```

**Правило:** constructor > field injection.

### 4. @Binds vs @Provides

```kotlin
@Module
abstract class RepositoryModule {
    @Binds // ✅ No implementation, faster
    abstract fun repo(impl: UserRepositoryImpl): UserRepository
}
```

`@Binds` эффективнее для простого связывания интерфейса с реализацией.

## Answer (EN)

Dagger is built on four core elements:

### 1. @Component — Dependency Graph

Interface generating code to wire modules with injection points:

```kotlin
@Component(modules = [NetworkModule::class])
interface AppComponent {
    fun inject(activity: MainActivity) // ✅ Injection method
}

val component = DaggerAppComponent.create() // Dagger-generated
```

**Responsibilities:**
- Compile-time graph validation
- Dependency lifecycle management

### 2. @Module — Dependency Source

Class with `@Provides` methods for object creation:

```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton // ✅ Scoped dependency
    fun provideApi(): ApiService =
        Retrofit.Builder().baseUrl("...").build().create()
}
```

Used for external libraries, interfaces, complex construction logic.

### 3. @Inject — Injection Points

```kotlin
// ✅ Constructor injection (preferred)
class UserRepository @Inject constructor(
    private val api: ApiService
)

// ❌ Field injection (Android framework only)
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as App).component.inject(this) // Manual injection
    }
}
```

**Rule:** constructor > field injection.

### 4. @Binds vs @Provides

```kotlin
@Module
abstract class RepositoryModule {
    @Binds // ✅ No implementation, faster
    abstract fun repo(impl: UserRepositoryImpl): UserRepository
}
```

`@Binds` is more efficient for simple interface-to-implementation binding.

## Follow-ups

- How does Dagger resolve circular dependencies?
- What's the lifecycle difference between `@Singleton` and `@ActivityScoped`?
- When is `@Binds` not applicable?
- How do subcomponents extend parent component graphs?
- What are the performance implications of multi-binding?

## References

- [[c-dependency-injection]]
- [[c-dagger]]
- [[c-hilt]]
- https://dagger.dev/dev-guide/

## Related Questions

### Prerequisites
- [[q-dagger-inject-annotation--android--easy]] — Understanding @Inject

### Related
- [[q-dagger-field-injection--android--medium]] — Injection strategies
- Setting up Dagger components and modules
- Understanding Dagger scopes and component hierarchy

### Advanced
- [[q-dagger-framework-overview--android--hard]] — Full architecture
- Implementing custom scopes with subcomponents
- Dagger multi-binding and optional dependencies

---
id: android-449
title: Dagger Main Elements / Основные элементы Dagger
aliases: [Dagger Main Elements, Основные элементы Dagger]
topic: android
subtopics:
  - di-hilt
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-dependency-injection
  - c-dagger
  - q-dagger-field-injection--android--medium
  - q-dagger-framework-overview--android--hard
  - q-dagger-inject-annotation--android--easy
created: 2025-10-20
updated: 2025-11-10
tags: [android/di-hilt, dagger, dependency-injection, difficulty/medium]
sources: []
---

# Вопрос (RU)
> Из каких основных элементов состоит Dagger?

# Question (EN)
> What are the main elements of Dagger?

## Ответ (RU)

Dagger в Android обычно связывают с четырьмя ключевыми концепциями:

### 1. @Component — Граф Зависимостей

Интерфейс, для которого Dagger генерирует реализацию, связывающую модули с точками инъекции:

```kotlin
@Component(modules = [NetworkModule::class])
interface AppComponent {
    fun inject(activity: MainActivity) // ✅ Injection method
}

val component = DaggerAppComponent.create() // Dagger-generated
```

**Ответственность:**
- Валидация графа на этапе компиляции
- Связывание зависимостей и управление их областями видимости (scopes)

### 2. @Module — Источник Зависимостей

Класс с методами `@Provides` или `@Binds` для описания того, как создавать объекты:

```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton // ✅ Scoped dependency
    fun provideApi(): ApiService =
        Retrofit.Builder().baseUrl("...").build().create(ApiService::class.java)
}
```

Используется для внешних библиотек, интерфейсов, сложной логики создания, когда `@Inject` конструктора недостаточно или невозможен.

### 3. @Inject — Точки Внедрения

```kotlin
// ✅ Constructor injection (предпочтительно)
class UserRepository @Inject constructor(
    private val api: ApiService
)

// ✅ Field injection (часто используется для Android framework классов)
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as App).component.inject(this) // Ручная инъекция для framework-типа
    }
}
```

**Правило (best practice):** по возможности использовать constructor injection; field injection — валидный механизм, особенно для Android framework классов, где нельзя контролировать конструктор.

### 4. @Binds vs @Provides

```kotlin
@Module
abstract class RepositoryModule {
    @Binds // ✅ Декларативная привязка интерфейса к реализации без тела метода
    abstract fun repo(impl: UserRepositoryImpl): UserRepository
}
```

`@Binds` предпочтительнее для простого связывания интерфейса с реализацией (меньше генерируемого кода и декларативнее), а `@Provides` используется, когда нужно выполнить произвольную логику создания объекта.

## Answer (EN)

In Android, Dagger usage is usually framed around four key concepts:

### 1. @Component — Dependency Graph

Interface for which Dagger generates an implementation to wire modules with injection points:

```kotlin
@Component(modules = [NetworkModule::class])
interface AppComponent {
    fun inject(activity: MainActivity) // ✅ Injection method
}

val component = DaggerAppComponent.create() // Dagger-generated
```

**Responsibilities:**
- Compile-time graph validation
- Wiring dependencies and managing their scopes

### 2. @Module — Dependency Source

Class with `@Provides` or `@Binds` methods that describe how to construct objects:

```kotlin
@Module
object NetworkModule {
    @Provides
    @Singleton // ✅ Scoped dependency
    fun provideApi(): ApiService =
        Retrofit.Builder().baseUrl("...").build().create(ApiService::class.java)
}
```

Used for external libraries, interfaces, and complex construction logic when `@Inject` constructors are not available or not sufficient.

### 3. @Inject — Injection Points

```kotlin
// ✅ Constructor injection (preferred)
class UserRepository @Inject constructor(
    private val api: ApiService
)

// ✅ Field injection (commonly used for Android framework classes)
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as App).component.inject(this) // Manual injection for framework type
    }
}
```

**Rule (best practice):** prefer constructor injection when possible; field injection is a valid mechanism, especially for Android framework types where you cannot control the constructor.

### 4. @Binds vs @Provides

```kotlin
@Module
abstract class RepositoryModule {
    @Binds // ✅ Declarative interface-to-implementation binding without method body
    abstract fun repo(impl: UserRepositoryImpl): UserRepository
}
```

`@Binds` is preferred for simple interface-to-implementation bindings (less generated code and clearer semantics), while `@Provides` is used when you need arbitrary creation logic.

## Дополнительные вопросы (RU)

- Как Dagger решает проблему циклических зависимостей?
- В чем разница жизненных циклов между `@Singleton` и `@ActivityScoped`?
- Когда `@Binds` неприменим?
- Как подкомпоненты расширяют графы родительских компонентов?
- Каковы последствия для производительности при использовании multi-binding?

## Follow-ups

- How does Dagger resolve circular dependencies?
- What's the lifecycle difference between `@Singleton` and `@ActivityScoped`?
- When is `@Binds` not applicable?
- How do subcomponents extend parent component graphs?
- What are the performance implications of multi-binding?

## Ссылки (RU)

- [[c-dependency-injection]]
- [[c-dagger]]
- [[c-hilt]]
- https://dagger.dev/dev-guide/

## References

- [[c-dependency-injection]]
- [[c-dagger]]
- [[c-hilt]]
- https://dagger.dev/dev-guide/

## Связанные вопросы (RU)

### Предпосылки
- [[q-dagger-inject-annotation--android--easy]] — Понимание `@Inject`

### Связанные
- [[q-dagger-field-injection--android--medium]] — Стратегии внедрения
- Настройка компонентов и модулей Dagger
- Понимание областей видимости и иерархии компонентов Dagger

### Продвинутое
- [[q-dagger-framework-overview--android--hard]] — Общая архитектура
- Реализация пользовательских областей видимости с подкомпонентами
- Multi-binding и опциональные зависимости в Dagger

## Related Questions

### Prerequisites
- [[q-dagger-inject-annotation--android--easy]] — Understanding `@Inject`

### Related
- [[q-dagger-field-injection--android--medium]] — Injection strategies
- Setting up Dagger components and modules
- Understanding Dagger scopes and component hierarchy

### Advanced
- [[q-dagger-framework-overview--android--hard]] — Full architecture
- Implementing custom scopes with subcomponents
- Dagger multi-binding and optional dependencies

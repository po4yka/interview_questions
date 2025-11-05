---
id: android-463
title: Dagger Inject Annotation / Аннотация Inject Dagger
aliases: [Dagger Inject Annotation, Аннотация Inject Dagger]
topic: android
subtopics:
  - dependency-management
  - di-hilt
question_kind: android
difficulty: easy
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-dagger
  - c-dependency-injection
  - q-dagger-field-injection--android--medium
  - q-dagger-framework-overview--android--hard
  - q-hilt-components-scope--android--medium
created: 2025-10-20
updated: 2025-10-30
sources: []
tags: [android/dependency-management, android/di-hilt, dagger, dependency-injection, difficulty/easy, hilt]
date created: Thursday, October 30th 2025, 12:02:51 pm
date modified: Sunday, November 2nd 2025, 5:31:51 pm
---

# Вопрос (RU)
> Как указать Dagger, где выполнить инъекцию зависимостей?

# Question (EN)
> How to tell Dagger where to inject dependencies?

## Ответ (RU)

Аннотация **`@Inject`** указывает Dagger точки инъекции зависимостей. Существует три варианта использования, каждый со своими сценариями применения.

### Ключевая Идея

`@Inject` сообщает Dagger **где** внедрить зависимости и **что** предоставить. Dagger анализирует граф зависимостей на этапе компиляции и генерирует код инъекции.

### Три Способа Использования

**1. Constructor Injection** — предпочтительный способ для обычных классов:

```kotlin
// ✅ Рекомендуется: immutable, легко тестировать
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDao
)
```

**Когда использовать:** ViewModels, repositories, use cases — классы, где вы контролируете создание экземпляра.

**2. Field Injection** — для Android-компонентов с platform-managed lifecycle:

```kotlin
// ✅ Activity/Fragment создаются системой
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    // Hilt инжектит перед onCreate()
}
```

**Недостатки:** требует `lateinit var`, сложнее тестировать, неявные зависимости.

**3. Method Injection** — редкий случай для разрешения circular dependencies:

```kotlin
// ❌ Используйте только при необходимости
class AnalyticsTracker @Inject constructor() {
    @Inject
    fun setup(logger: Logger) {
        // Инъекция после конструктора
    }
}
```

### Hilt И Field Injection

Hilt автоматизирует инъекцию в Android-компоненты через `@AndroidEntryPoint`:

```kotlin
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var viewModel: ProfileViewModel
    // Без ручного вызова inject()
}
```

Без Hilt требуется явный вызов:

```kotlin
// ❌ Без Hilt — boilerplate код
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        // Только теперь repository инициализирован
    }
}
```

## Answer (EN)

The **`@Inject`** annotation tells Dagger where to inject dependencies. Three usage patterns exist, each with specific use cases.

### Core Idea

`@Inject` tells [[c-dagger]] **where** to inject dependencies and **what** to provide. Dagger analyzes the dependency graph at compile time and generates injection code.

### Three Usage Patterns

**1. Constructor Injection** — preferred for regular classes:

```kotlin
// ✅ Recommended: immutable, easy to test
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDao
)
```

**When to use:** ViewModels, repositories, use cases — classes where you control instance creation.

**2. Field Injection** — for Android components with platform-managed lifecycle:

```kotlin
// ✅ Activity/Fragment created by system
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    // Hilt injects before onCreate()
}
```

**Drawbacks:** requires `lateinit var`, harder to test, implicit dependencies.

**3. Method Injection** — rare case for circular dependency resolution:

```kotlin
// ❌ Use only when necessary
class AnalyticsTracker @Inject constructor() {
    @Inject
    fun setup(logger: Logger) {
        // Injection after constructor
    }
}
```

### Hilt and Field Injection

Hilt automates injection in Android components via `@AndroidEntryPoint`:

```kotlin
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var viewModel: ProfileViewModel
    // No manual inject() call
}
```

Without Hilt, explicit call required:

```kotlin
// ❌ Without Hilt — boilerplate code
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        // Only now repository is initialized
    }
}
```

## Follow-ups

- Why is constructor injection preferred over field injection in terms of testability and immutability?
- When must you use field injection instead of constructor injection in Android?
- How does Dagger resolve the dependency graph and detect missing bindings at compile time?
- What happens if `@Inject` dependencies have circular references and how to resolve them?
- Why can't you use `val` with field injection, and what are the implications for thread safety?

## References

- [[c-dependency-injection]] - Dependency Injection pattern
- [[c-dagger]] - Dagger dependency injection framework
- [[c-hilt]] - Hilt Android DI library
- https://dagger.dev/api/latest/dagger/Inject.html
- [Dagger Basics](https://developer.android.com/training/dependency-injection/dagger-basics)


## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]] - Android project structure basics

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]] - Field injection details
- [[q-hilt-components-scope--android--medium]] - Hilt component scopes

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] - Dagger architecture overview

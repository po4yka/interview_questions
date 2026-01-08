---\
id: android-463
title: Dagger Inject Annotation / Аннотация Inject Dagger
aliases: [Dagger Inject Annotation, Аннотация Inject Dagger]
topic: android
subtopics: [di-hilt]
question_kind: android
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dagger, c-dependency-injection, q-dagger-custom-scopes--android--hard, q-dagger-field-injection--android--medium, q-dagger-framework-overview--android--hard, q-dagger-purpose--android--easy, q-hilt-components-scope--android--medium]
created: 2025-10-20
updated: 2025-11-10
sources: []
tags: [android/di-hilt, dagger, dependency-injection, difficulty/easy, hilt]

---\
# Вопрос (RU)
> Как указать `Dagger`, где выполнить инъекцию зависимостей?

# Question (EN)
> How to tell `Dagger` where to inject dependencies?

## Ответ (RU)

Аннотация **`@Inject`** указывает `Dagger` точки инъекции зависимостей и (для конструкторов) объявляет, какие реализации можно создавать и предоставлять из графа зависимостей. Существует три варианта использования, каждый со своими сценариями применения.

### Ключевая Идея

`@Inject` сообщает `Dagger`:
- **где** внедрить зависимости (поля, конструкторы, методы), и
- **что** можно предоставить (конструктор с `@Inject` объявляет binding).

`Dagger` анализирует граф зависимостей на этапе компиляции и генерирует код инъекции.

### Три Способа Использования

**1. Constructor Injection** — предпочтительный способ для обычных классов:

```kotlin
// ✅ Рекомендуется: явные зависимости, легче тестировать
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDao
)
```

**Когда использовать:** ViewModels, репозитории, use case-классы и другие классы, где вы контролируете создание экземпляра. Такой конструктор одновременно задает точку инъекции и объявляет для `Dagger`, как создать `UserRepository`.

**2. Field Injection** — для Android-компонентов с lifecycle, управляемым платформой:

```kotlin
// ✅ Activity/Fragment создаются системой
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    // В Hilt инъекция выполняется до вызова вашего onCreate()
}
```

**Когда использовать:** `Activity`, `Fragment`, `Service` и другие Android-компоненты, которые framework создает сам и которые нельзя просто получать через конструктор.

**Недостатки:** требует `lateinit var`, сложнее тестировать, неявные зависимости.

**3. Method Injection** — для пост-конструкторной инициализации через DI:

```kotlin
// ⚠️ Используется реже, когда зависимость нужна после создания экземпляра
class AnalyticsTracker @Inject constructor() {
    @Inject
    fun setup(logger: Logger) {
        // Инъекция вызывается после конструктора
    }
}
```

**Когда использовать:**
- когда зависимость логически используется только на этапе инициализации после конструктора;
- как один из способов разорвать циклические зависимости (осторожно, лучше избегать циклов через переразбиение).

### Hilt И Field Injection

`Hilt` автоматизирует инъекцию в Android-компоненты через `@AndroidEntryPoint`:

```kotlin
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
    // Без ручного вызова inject(): Hilt выполнит инъекцию до вашего onCreate()
}
```

Без `Hilt` требуется явный вызов на компоненте:

```kotlin
// ❌ Без Hilt — boilerplate-код
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        // Только теперь repository инициализирован
    }
}
```

Обратите внимание: для `Hilt` `ViewModel`-ы обычно получают через `@HiltViewModel` и делегаты (`by viewModels()`, `hiltViewModel()`), а не через `@Inject` на полях `Activity`/`Fragment`.

## Answer (EN)

The **`@Inject`** annotation tells `Dagger` where to inject dependencies and (for constructors) which implementations can be constructed and provided from the dependency graph. There are three usage patterns, each with specific use cases.

### Core Idea

`@Inject` tells `Dagger`:
- **where** to inject dependencies (fields, constructors, methods), and
- **what** can be provided (an `@Inject` constructor declares a binding).

`Dagger` analyzes the dependency graph at compile time and generates the injection code.

### Three Usage Patterns

**1. Constructor Injection** — preferred for regular classes:

```kotlin
// ✅ Recommended: explicit dependencies, easier to test
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDao
)
```

**When to use:** ViewModels, repositories, use cases, and other classes where you control instance creation. The `@Inject` constructor is both an injection point and a declaration of how to create `UserRepository`.

**2. Field Injection** — for Android components with platform-managed lifecycle:

```kotlin
// ✅ Activity/Fragment created by the system
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    // With Hilt, injection runs before your onCreate() executes
}
```

**When to use:** Activities, Fragments, Services, and other framework-managed Android components that you cannot simply instantiate via constructor injection.

**Drawbacks:** requires `lateinit var`, harder to test, implicit dependencies.

**3. Method Injection** — for post-construction initialization via DI:

```kotlin
// ⚠️ Less common; use when a dependency is needed after construction
class AnalyticsTracker @Inject constructor() {
    @Inject
    fun setup(logger: Logger) {
        // Injection runs after the constructor
    }
}
```

**When to use:**
- when a dependency is logically used only during an initialization step after construction;
- as one possible way to break circular dependencies (use with care; prefer refactoring cycles away).

### Hilt and Field Injection

`Hilt` automates injection into Android components via `@AndroidEntryPoint`:

```kotlin
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
    // No manual inject(): Hilt performs injection before your onCreate()
}
```

Without `Hilt`, an explicit call on the component is required:

```kotlin
// ❌ Without Hilt — more boilerplate
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        // Only now repository is initialized
    }
}
```

Note: with `Hilt`, ViewModels are typically obtained via `@HiltViewModel` and delegates (`by viewModels()`, `hiltViewModel()`), not via `@Inject`-annotated fields on the `Activity`/`Fragment`.

## Follow-ups

- Why is constructor injection preferred over field injection in terms of testability and explicit dependencies?
- When must you use field injection instead of constructor injection in Android?
- How does `Dagger` resolve the dependency graph and detect missing bindings at compile time?
- What happens if `@Inject` dependencies have circular references and how to resolve them?
- Why can't you use `val` with field injection, and what are the implications for thread safety?

## References

- [[c-dependency-injection]] - Dependency Injection pattern
- [[c-dagger]] - `Dagger` dependency injection framework
- https://dagger.dev/api/latest/dagger/Inject.html
- [Dagger Basics](https://developer.android.com/training/dependency-injection/dagger-basics)

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]] - Android project structure basics

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]] - Field injection details
- [[q-hilt-components-scope--android--medium]] - `Hilt` component scopes

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] - `Dagger` architecture overview

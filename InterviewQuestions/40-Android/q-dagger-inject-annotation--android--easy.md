---
id: 20251020-200000
title: Dagger Inject Annotation / Аннотация Inject Dagger
aliases: ["Dagger Inject Annotation", "Аннотация Inject Dagger"]
topic: android
subtopics: [di-hilt, dependency-management]
question_kind: android
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-dagger-field-injection--android--medium, q-dagger-framework-overview--android--hard, q-hilt-components-scope--android--medium, c-dependency-injection, c-dagger]
created: 2025-10-20
updated: 2025-10-29
sources: []
tags: [android/di-hilt, android/dependency-management, dagger, hilt, dependency-injection, difficulty/easy]
---

# Вопрос (RU)
> Как указать Dagger, где выполнить инъекцию зависимостей?

# Question (EN)
> How to tell Dagger where to inject dependencies?

## Ответ (RU)

Используйте аннотацию **`@Inject`** в трех местах: конструктор (предпочтительно), поля (для Android компонентов) и методы (редко).

### Ключевые Принципы

`@Inject` сообщает Dagger:
- **Где** внедрить зависимости (конструктор/поля/методы)
- **Что** нужно предоставить (типы параметров)
- **Когда** создавать экземпляры (анализ графа на этапе компиляции)

Dagger проверяет корректность на этапе компиляции и генерирует код для инъекции.

### 1. Constructor Injection (✅ Рекомендуется)

```kotlin
// ✅ ПРЕДПОЧТИТЕЛЬНЫЙ способ - immutable, testable
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDao
)
```

**Преимущества:**
- Immutable зависимости (`val`)
- Легко тестировать (передать моки в конструктор)
- Явные зависимости
- Dagger автоматически создает фабрики

**Используйте для:** ViewModels, репозиториев, use cases, любых обычных классов.

### 2. Field Injection (для Android компонентов)

```kotlin
// ✅ Для Activity/Fragment - конструктор недоступен
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Hilt автоматически инжектит до onCreate
        repository.loadProfile()
    }
}
```

```kotlin
// ❌ Без Hilt - требует ручного вызова inject()
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        repository.loadData() // Только после inject()
    }
}
```

**Ограничения:**
- Требует `lateinit var` (не `val`)
- Без Hilt нужен ручной вызов `inject()`
- Сложнее тестировать

**Используйте для:** Activity, Fragment, Service, BroadcastReceiver, View (если нужно).

### 3. Method Injection (редко)

```kotlin
// ❌ Редкий случай - используйте только если необходимо
class AnalyticsTracker @Inject constructor() {
    private lateinit var logger: Logger

    @Inject
    fun setup(logger: Logger) {
        this.logger = logger
        logger.init()
    }
}
```

**Используйте только для:**
- Circular dependency resolution
- Callback-методы с lifecycle awareness
- Когда нужен доступ к `this` при инициализации

### Hilt Упрощает Field Injection

```kotlin
// ✅ Hilt автоматизирует инъекцию в Activity
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var viewModel: ProfileViewModel
    // Нет ручного inject(), Hilt делает это автоматически
}
```

**Hilt автоматически:**
- Генерирует компоненты
- Управляет lifecycle scopes
- Вызывает inject() перед `onCreate`

## Answer (EN)

Use the **`@Inject`** annotation in three places: constructor (preferred), fields (for Android components), and methods (rarely).

### Core Principles

`@Inject` tells [[c-dagger]]:
- **Where** to inject dependencies (constructor/fields/methods)
- **What** to provide (parameter types)
- **When** to create instances (compile-time graph analysis)

Dagger validates correctness at compile time and generates injection code.

### 1. Constructor Injection (✅ Recommended)

```kotlin
// ✅ PREFERRED way - immutable, testable
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDao
)
```

**Benefits:**
- Immutable dependencies (`val`)
- Easy to test (pass mocks to constructor)
- Explicit dependencies
- Dagger auto-generates factories

**Use for:** ViewModels, repositories, use cases, any regular classes.

### 2. Field Injection (for Android components)

```kotlin
// ✅ For Activity/Fragment - constructor unavailable
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Hilt auto-injects before onCreate
        repository.loadProfile()
    }
}
```

```kotlin
// ❌ Without Hilt - requires manual inject() call
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        repository.loadData() // Only after inject()
    }
}
```

**Limitations:**
- Requires `lateinit var` (not `val`)
- Without [[c-hilt]], needs manual `inject()` call
- Harder to test

**Use for:** Activity, Fragment, Service, BroadcastReceiver, View (if needed).

### 3. Method Injection (rarely)

```kotlin
// ❌ Rare case - use only when necessary
class AnalyticsTracker @Inject constructor() {
    private lateinit var logger: Logger

    @Inject
    fun setup(logger: Logger) {
        this.logger = logger
        logger.init()
    }
}
```

**Use only for:**
- Circular dependency resolution
- Lifecycle-aware callback methods
- When `this` access needed during initialization

### Hilt Simplifies Field Injection

```kotlin
// ✅ Hilt automates injection in Activity
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    @Inject lateinit var viewModel: ProfileViewModel
    // No manual inject(), Hilt does it automatically
}
```

**Hilt automatically:**
- Generates components
- Manages lifecycle scopes
- Calls inject() before `onCreate`

## Follow-ups

- Why is constructor injection preferred over field injection?
- When must you use field injection instead of constructor?
- How does Dagger resolve the dependency graph at compile time?
- What happens if @Inject dependencies have circular references?
- Why can't you use `val` with field injection?

## References

- [[c-dependency-injection]] - Dependency Injection pattern
- [[c-dagger]] - Dagger dependency injection framework
- [[c-hilt]] - Hilt Android DI library
- https://dagger.dev/api/latest/dagger/Inject.html
- https://developer.android.com/training/dependency-injection/dagger-basics

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]] - Android project structure basics

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]] - Field injection details
- [[q-hilt-components-scope--android--medium]] - Hilt component scopes

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]] - Dagger architecture overview

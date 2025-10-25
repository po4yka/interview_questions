---
id: 20251020-200000
title: Dagger Inject Annotation / Аннотация Inject Dagger
aliases:
- Dagger Inject Annotation
- Аннотация Inject Dagger
topic: android
subtopics:
- di-hilt
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-dagger-field-injection--android--medium
- q-dagger-framework-overview--android--hard
- q-hilt-components-scope--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/di-hilt
- difficulty/easy
source: https://dagger.dev/api/latest/dagger/Inject.html
source_note: Dagger Inject annotation documentation
---

# Вопрос (RU)
> Как сообщить Dagger, что мы собираемся что-то инжектить?

# Question (EN)
> How to tell Dagger we're going to inject something?

## Ответ (RU)

Для сообщения Dagger о необходимости инъекции зависимостей используется аннотация **`@Inject`** в трех основных местах: конструктор, поля и методы.

### Теория: Принципы @Inject

**Основные принципы:**
- `@Inject` маркирует места для внедрения зависимостей
- Dagger анализирует аннотации на этапе компиляции
- Автоматическое разрешение зависимостей через граф
- Статическая типизация и проверка на этапе компиляции

**Типы инъекции:**
- **Constructor injection** - рекомендуется для большинства случаев
- **Field injection** - для Android компонентов
- **Method injection** - для специальных случаев

### @Inject на конструкторе (Рекомендуется)

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDatabase
) {
    fun getUser(id: String): User {
        return database.getUser(id) ?: api.fetchUser(id)
    }
}
```

**Dagger автоматически:**
- Создает экземпляры `UserRepository`
- Разрешает зависимости `ApiService` и `UserDatabase`
- Внедряет их в конструктор

### @Inject на полях

**В Activity/Fragment:**
```kotlin
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Обязательно вызвать inject перед использованием
        (application as MyApp).appComponent.inject(this)

        repository.getUser("123")
    }
}
```

**Особенности field injection:**
- Поля должны быть `lateinit var`
- Требует явного вызова `inject()` метода
- Используется для Android компонентов

### @Inject на методах

```kotlin
class UserService {
    @Inject
    fun setDependencies(
        repository: UserRepository,
        analytics: Analytics
    ) {
        this.repository = repository
        this.analytics = analytics
    }
}
```

**Method injection используется для:**
- Специальных случаев инициализации
- Когда нужен доступ к инжектируемым параметрам
- Callback методов

### Когда использовать каждый тип

**Constructor injection:**
- Обычные классы и бизнес-логика
- Когда возможно модифицировать конструктор
- Рекомендуемый подход для большинства случаев

**Field injection:**
- Android компоненты (Activity, Fragment, Service)
- Когда конструктор недоступен для модификации
- Framework-управляемые объекты

**Method injection:**
- Специальные случаи инициализации
- Когда нужен доступ к параметрам инъекции
- Callback методы

### Hilt автоматизация

Hilt упрощает использование `@Inject`:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository
    // Hilt автоматически вызывает inject()
}
```

**Hilt автоматически:**
- Создает компоненты
- Управляет жизненными циклами
- Вызывает методы инъекции

## Answer (EN)

To tell [[c-dagger]] about [[c-dependency-injection]], use the **`@Inject`** annotation in three main places: constructor, fields, and methods.

### Theory: @Inject Principles

**Core Principles:**
- `@Inject` marks places for dependency injection
- Dagger analyzes annotations at compile time
- Automatic dependency resolution through graph
- Static typing and compile-time validation

**Injection Types:**
- **Constructor injection** - recommended for most cases
- **Field injection** - for Android components
- **Method injection** - for special cases

### @Inject on Constructor (Recommended)

```kotlin
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val database: UserDatabase
) {
    fun getUser(id: String): User {
        return database.getUser(id) ?: api.fetchUser(id)
    }
}
```

**Dagger automatically:**
- Creates `UserRepository` instances
- Resolves `ApiService` and `UserDatabase` dependencies
- Injects them into constructor

### @Inject on Fields

**In Activity/Fragment:**
```kotlin
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Must call inject before using
        (application as MyApp).appComponent.inject(this)

        repository.getUser("123")
    }
}
```

**Field injection features:**
- Fields must be `lateinit var`
- Requires explicit `inject()` method call
- Used for Android components

### @Inject on Methods

```kotlin
class UserService {
    @Inject
    fun setDependencies(
        repository: UserRepository,
        analytics: Analytics
    ) {
        this.repository = repository
        this.analytics = analytics
    }
}
```

**Method injection used for:**
- Special initialization cases
- When access to injected parameters is needed
- Callback methods

### When to Use Each Type

**Constructor injection:**
- Regular classes and business logic
- When constructor can be modified
- Recommended approach for most cases

**Field injection:**
- Android components (Activity, Fragment, Service)
- When constructor is not available for modification
- Framework-managed objects

**Method injection:**
- Special initialization cases
- When access to injection parameters is needed
- Callback methods

### Hilt Automation

[[c-hilt]] simplifies `@Inject` usage:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository
    // Hilt automatically calls inject()
}
```

**Hilt automatically:**
- Creates components
- Manages lifecycles
- Calls injection methods

## Follow-ups

- What's the difference between constructor injection and field injection?
- How does Dagger resolve dependencies marked with @Inject?
- When should you avoid using @Inject annotation?

## Related Questions

### Prerequisites (Easier)
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-dagger-field-injection--android--medium]]

### Advanced (Harder)
- [[q-dagger-framework-overview--android--hard]]

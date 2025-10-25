---
id: 20251020-200000
title: Dagger Field Injection / Инъекция полей Dagger
aliases: [Dagger Field Injection, Инъекция полей Dagger]
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
  - q-dagger-build-time-optimization--android--medium
  - q-dagger-custom-scopes--android--hard
  - q-hilt-components-scope--android--medium
created: 2025-10-20
updated: 2025-10-20
tags: [android/di-hilt, difficulty/medium]
source: https://dagger.dev/api/latest/dagger/Inject.html
source_note: Dagger Inject annotation documentation
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:19 pm
---

# Вопрос (RU)
> Какие особенности инъекции в поле при помощи Dagger?

# Question (EN)
> What are the features of field injection using Dagger?

## Ответ (RU)

Field injection в Dagger позволяет автоматически внедрять зависимости в поля класса с помощью аннотации `@Inject`. Этот подход имеет специфические характеристики, преимущества и ограничения по сравнению с constructor и method injection.

### Теория: Принципы Field Injection

**Основные принципы:**
- Field injection происходит после создания объекта
- Требует явного вызова метода inject()
- Поля должны быть `lateinit var` в Kotlin
- Зависимости доступны только после инъекции

**Жизненный цикл инъекции:**
1. Создание объекта (конструктор)
2. Вызов inject() метода
3. Заполнение полей зависимостями
4. Использование зависимостей

### Базовое Использование

```kotlin
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    @Inject
    lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Обязательно вызвать inject перед использованием
        (application as MyApp).appComponent.inject(this)

        // Теперь безопасно использовать поля
        val user = repository.getUser()
        analytics.logEvent("screen_viewed")
    }
}
```

### Ключевые Особенности

**1. Требует ручного вызова inject()**
```kotlin
// Компонент должен предоставить inject метод
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}
```

**2. Поля должны быть lateinit var**
```kotlin
class UserActivity : AppCompatActivity() {
    @Inject
    lateinit var userRepository: UserRepository // Правильно

    @Inject
    val analytics: Analytics // Неправильно - должно быть var
}
```

**3. Null safety в Kotlin**
```kotlin
@Inject
lateinit var apiService: ApiService

fun makeRequest() {
    // Проверка на инициализацию
    if (::apiService.isInitialized) {
        apiService.fetchData()
    }
}
```

### Когда Использовать Field Injection

**Подходит для:**
- Android компонентов (Activity, Fragment, Service)
- Framework-управляемых объектов
- Когда конструктор недоступен для модификации

**Не подходит для:**
- Обычных классов (используйте constructor injection)
- Тестируемых классов
- Когда нужна immutable инициализация

### Hilt Подход

Hilt автоматизирует field injection:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    // Hilt автоматически вызывает inject()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Поля уже инициализированы
        repository.getUser()
    }
}
```

### Лучшие Практики

**Архитектурные принципы:**
- Используйте constructor injection когда возможно
- Field injection только для framework компонентов
- Избегайте field injection в бизнес-логике

**Безопасность:**
- Всегда проверяйте инициализацию
- Используйте lateinit var правильно
- Документируйте зависимости

**Производительность:**
- Field injection медленнее constructor injection
- Reflection используется для доступа к полям
- Кэширование reflection для оптимизации

### Ограничения И Недостатки

**Проблемы field injection:**
- Не работает с final полями
- Требует явного вызова inject()
- Менее безопасен чем constructor injection
- Сложнее тестировать

**Альтернативы:**
- Constructor injection для обычных классов
- Method injection для специальных случаев
- Hilt для автоматизации процесса

## Answer (EN)

Field injection in [[c-dagger]] allows automatic [[c-dependency-injection]] into class fields using the `@Inject` annotation. This approach has specific characteristics, advantages, and limitations compared to constructor and method injection.

### Theory: Field Injection Principles

**Core Principles:**
- Field injection occurs after object creation
- Requires explicit inject() method call
- Fields must be `lateinit var` in Kotlin
- Dependencies available only after injection

**Injection Lifecycle:**
1. Object creation (constructor)
2. inject() method call
3. Field population with dependencies
4. Dependency usage

### Basic Usage

```kotlin
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    @Inject
    lateinit var analytics: Analytics

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Must call inject before using dependencies
        (application as MyApp).appComponent.inject(this)

        // Now safe to use injected fields
        val user = repository.getUser()
        analytics.logEvent("screen_viewed")
    }
}
```

### Key Features

**1. Requires Manual inject() Call**
```kotlin
// Component must provide inject method
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
}
```

**2. Fields Must Be lateinit var**
```kotlin
class UserActivity : AppCompatActivity() {
    @Inject
    lateinit var userRepository: UserRepository // Correct

    @Inject
    val analytics: Analytics // Wrong - should be var
}
```

**3. Null Safety in Kotlin**
```kotlin
@Inject
lateinit var apiService: ApiService

fun makeRequest() {
    // Check initialization
    if (::apiService.isInitialized) {
        apiService.fetchData()
    }
}
```

### When to Use Field Injection

**Suitable for:**
- Android components (Activity, Fragment, Service)
- Framework-managed objects
- When constructor is not available for modification

**Not suitable for:**
- Regular classes (use constructor injection)
- Testable classes
- When immutable initialization is needed

### Hilt Approach

[[c-hilt]] automates field injection:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    // Hilt automatically calls inject()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Fields already initialized
        repository.getUser()
    }
}
```

### Best Practices

**Architectural Principles:**
- Use constructor injection when possible
- Field injection only for framework components
- Avoid field injection in business logic

**Safety:**
- Always check initialization
- Use lateinit var correctly
- Document dependencies

**Performance:**
- Field injection slower than constructor injection
- Reflection used for field access
- Reflection caching for optimization

### Limitations and Drawbacks

**Field injection problems:**
- Doesn't work with final fields
- Requires explicit inject() call
- Less safe than constructor injection
- Harder to test

**Alternatives:**
- Constructor injection for regular classes
- Method injection for special cases
- Hilt for process automation

## Follow-ups

- What are the performance differences between field injection and constructor injection?
- How do you test classes that use field injection?
- When should you avoid field injection in favor of other injection methods?

## References

- [Dagger Inject Annotation](https://dagger.dev/api/latest/dagger/Inject.html)
- [Hilt Field Injection](https://dagger.dev/hilt/)

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-build-time-optimization--android--medium]]

### Related (Same Level)
- [[q-hilt-components-scope--android--medium]]

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]]

---
id: 20251020-200000
title: Dagger Field Injection / Инъекция полей Dagger
aliases: ["Dagger Field Injection", "Инъекция полей Dagger"]
topic: android
subtopics: [di-hilt, architecture-mvvm]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dagger, c-dependency-injection, c-hilt, q-dagger-build-time-optimization--android--medium, q-hilt-components-scope--android--medium]
sources: []
created: 2025-10-20
updated: 2025-10-29
tags: [android/di-hilt, android/architecture-mvvm, dependency-injection, dagger, difficulty/medium]
---

# Вопрос (RU)
> Какие особенности инъекции в поле при помощи Dagger?

# Question (EN)
> What are the features of field injection using Dagger?

## Ответ (RU)

Field injection в Dagger позволяет внедрять зависимости в поля класса с помощью `@Inject`. Этот подход имеет специфические характеристики и ограничения по сравнению с constructor injection.

### Принципы работы

Field injection происходит **после создания объекта**. Зависимости внедряются в поля через вызов метода `inject()` компонента. Этот подход используется для Android компонентов (Activity, Fragment, Service), где конструктор недоступен для модификации.

**Жизненный цикл:**
1. Создание объекта через конструктор по умолчанию
2. Вызов метода `inject()` компонента
3. Заполнение помеченных полей зависимостями
4. Поля готовы к использованию

### Основное использование

```kotlin
// ❌ Неправильно - использование до inject()
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // CRASH - поле не инициализировано
    }
}

// ✅ Правильно - inject() перед использованием
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        repository.getUser() // OK
    }
}
```

### Ключевые особенности

**1. Требуется метод inject() в компоненте**

```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    // Отдельный метод для каждого типа
    fun inject(activity: MainActivity)
    fun inject(fragment: UserFragment)
}
```

**2. Поля должны быть lateinit var**

```kotlin
// ✅ Правильно
@Inject lateinit var repository: UserRepository

// ❌ Неправильно - не компилируется
@Inject val repository: UserRepository
@Inject var repository: UserRepository? = null
```

**3. Проверка инициализации в Kotlin**

```kotlin
@Inject lateinit var apiService: ApiService

fun makeRequest() {
    if (::apiService.isInitialized) {
        apiService.fetchData()
    } else {
        // Обработка ошибки инициализации
    }
}
```

### Подход с Hilt

Hilt автоматизирует field injection для Android компонентов:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    // Hilt автоматически вызывает inject() перед onCreate()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // Безопасно использовать
    }
}
```

### Когда использовать

**Подходит для:**
- Android framework компонентов (Activity, Fragment, Service)
- Классов, созданных системой (где конструктор недоступен)
- Legacy кода с ограничениями архитектуры

**Не подходит для:**
- ViewModel, Repository, UseCase (используйте constructor injection)
- Тестируемых классов (field injection усложняет тесты)
- Новых компонентов (предпочтителен constructor injection)

### Производительность

Field injection медленнее constructor injection из-за использования reflection для доступа к полям. Dagger кэширует reflection metadata, но накладные расходы остаются.

**Сравнение:**
- Constructor injection: прямой вызов конструктора (быстро)
- Field injection: reflection + вызов setter (медленнее)
- Разница заметна при создании тысяч объектов

### Ограничения

**Технические:**
- Не работает с `final` полями (только `var`)
- Требует ручного вызова `inject()`
- Reflection overhead на производительность

**Архитектурные:**
- Менее безопасен чем constructor injection (возможны null поля)
- Скрывает зависимости (не видны в конструкторе)
- Усложняет тестирование (нужно мокировать поля)

## Answer (EN)

Field injection in Dagger allows injecting dependencies into class fields using `@Inject`. This approach has specific characteristics and limitations compared to constructor injection.

### Working Principles

Field injection occurs **after object creation**. Dependencies are injected into fields through a component's `inject()` method call. This approach is used for Android components (Activity, Fragment, Service) where the constructor is unavailable for modification.

**Lifecycle:**
1. Object creation via default constructor
2. Component's `inject()` method call
3. Populating marked fields with dependencies
4. Fields ready for use

### Basic Usage

```kotlin
// ❌ Wrong - using before inject()
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // CRASH - field not initialized
    }
}

// ✅ Correct - inject() before usage
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        repository.getUser() // OK
    }
}
```

### Key Features

**1. Component requires inject() method**

```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    // Separate method for each type
    fun inject(activity: MainActivity)
    fun inject(fragment: UserFragment)
}
```

**2. Fields must be lateinit var**

```kotlin
// ✅ Correct
@Inject lateinit var repository: UserRepository

// ❌ Wrong - won't compile
@Inject val repository: UserRepository
@Inject var repository: UserRepository? = null
```

**3. Initialization check in Kotlin**

```kotlin
@Inject lateinit var apiService: ApiService

fun makeRequest() {
    if (::apiService.isInitialized) {
        apiService.fetchData()
    } else {
        // Handle initialization error
    }
}
```

### Hilt Approach

Hilt automates field injection for Android components:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    // Hilt automatically calls inject() before onCreate()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // Safe to use
    }
}
```

### When to Use

**Suitable for:**
- Android framework components (Activity, Fragment, Service)
- System-created classes (where constructor is unavailable)
- Legacy code with architectural constraints

**Not suitable for:**
- ViewModel, Repository, UseCase (use constructor injection)
- Testable classes (field injection complicates testing)
- New components (constructor injection preferred)

### Performance

Field injection is slower than constructor injection due to reflection usage for field access. Dagger caches reflection metadata, but overhead remains.

**Comparison:**
- Constructor injection: direct constructor call (fast)
- Field injection: reflection + setter call (slower)
- Difference noticeable when creating thousands of objects

### Limitations

**Technical:**
- Doesn't work with `final` fields (only `var`)
- Requires manual `inject()` call
- Reflection overhead on performance

**Architectural:**
- Less safe than constructor injection (possible null fields)
- Hides dependencies (not visible in constructor)
- Complicates testing (need to mock fields)

## Follow-ups

- When should you prefer constructor injection over field injection in Android?
- How does Hilt eliminate the need for manual inject() calls?
- What testing strategies work best with field injection?
- How does field injection impact app startup performance?
- What are the alternatives to field injection for Activity/Fragment?

## References

- [[c-dagger]]
- [[c-dependency-injection]]
- [[c-hilt]]
- [Dagger Inject Documentation](https://dagger.dev/api/latest/dagger/Inject.html)
- [Hilt Android Guide](https://developer.android.com/training/dependency-injection/hilt-android)

## Related Questions

### Prerequisites (Easier)
- [[q-dependency-injection-basics--android--easy]]

### Related (Same Level)
- [[q-dagger-build-time-optimization--android--medium]]
- [[q-hilt-components-scope--android--medium]]

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]]
- [[q-dagger-multibinding--android--hard]]

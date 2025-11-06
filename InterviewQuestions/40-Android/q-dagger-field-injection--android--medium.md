---
id: android-469
title: Dagger Field Injection / Инъекция полей Dagger
aliases: [Dagger Field Injection, Инъекция полей Dagger]
topic: android
subtopics:
  - architecture-mvvm
  - di-hilt
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-dagger
  - c-dependency-injection
  - c-hilt
  - q-dagger-build-time-optimization--android--medium
  - q-hilt-components-scope--android--medium
sources: []
created: 2025-10-20
updated: 2025-10-30
tags: [android/architecture-mvvm, android/di-hilt, dagger, dependency-injection, difficulty/medium]
---

# Вопрос (RU)
> Какие особенности инъекции в поле при помощи Dagger?

# Question (EN)
> What are the features of field injection using Dagger?

## Ответ (RU)

Field injection в Dagger внедряет зависимости в поля класса через `@Inject` **после создания объекта**. Используется для Android компонентов (Activity, Fragment, Service), где конструктор недоступен для модификации.

### Жизненный Цикл

1. Создание объекта через конструктор по умолчанию
2. Вызов метода `inject()` компонента
3. Заполнение помеченных полей зависимостями
4. Поля готовы к использованию

```kotlin
// ❌ Неправильно - использование до inject()
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // CRASH
    }
}

// ✅ Правильно - inject() перед использованием
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        repository.getUser() // OK
    }
}
```

### Требования

**Компонент с методом inject():**
```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity) // ✅ Отдельный метод для каждого типа
}
```

**Поля должны быть lateinit var:**
```kotlin
@Inject lateinit var repository: UserRepository // ✅
@Inject val repository: UserRepository // ❌ Не компилируется
```

### Hilt Упрощение

Hilt автоматизирует field injection:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // ✅ Hilt вызвал inject() автоматически
    }
}
```

### Применимость

**Используйте для:**
- Android framework компонентов (Activity, Fragment, Service)
- Классов, созданных системой

**Избегайте для:**
- ViewModel, Repository, UseCase → constructor injection
- Тестируемых классов → усложняет моки
- Новых компонентов → предпочтителен constructor injection

### Ограничения

- Reflection overhead → медленнее constructor injection
- Менее безопасен → возможны null поля до inject()
- Скрывает зависимости → не видны в сигнатуре класса
- Усложняет тестирование → требуется мокирование полей

## Answer (EN)

Field injection in Dagger injects dependencies into class fields via `@Inject` **after object creation**. Used for Android components (Activity, Fragment, Service) where constructor modification is unavailable.

### Lifecycle

1. Object creation via default constructor
2. Component's `inject()` method call
3. Populating marked fields with dependencies
4. Fields ready for use

```kotlin
// ❌ Wrong - using before inject()
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // CRASH
    }
}

// ✅ Correct - inject() before usage
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        (application as MyApp).appComponent.inject(this)
        repository.getUser() // OK
    }
}
```

### Requirements

**Component with inject() method:**
```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity) // ✅ Separate method for each type
}
```

**Fields must be lateinit var:**
```kotlin
@Inject lateinit var repository: UserRepository // ✅
@Inject val repository: UserRepository // ❌ Won't compile
```

### Hilt Simplification

Hilt automates field injection:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // ✅ Hilt called inject() automatically
    }
}
```

### Applicability

**Use for:**
- Android framework components (Activity, Fragment, Service)
- System-created classes

**Avoid for:**
- ViewModel, Repository, UseCase → constructor injection
- Testable classes → complicates mocking
- New components → constructor injection preferred

### Limitations

- Reflection overhead → slower than constructor injection
- Less safe → possible null fields before inject()
- Hides dependencies → not visible in class signature
- Complicates testing → requires field mocking

## Follow-ups

- How does Hilt automate inject() calls for Android framework components?
- Why is constructor injection preferred for ViewModel and Repository classes?
- What happens if you access an @Inject field before calling inject()?
- How does field injection affect unit testing and mocking strategies?
- What are the performance implications of reflection in field injection?

## References

- [[c-dagger]]
- [[c-dependency-injection]]
- [[c-hilt]]
- [Dagger Inject Documentation](https://dagger.dev/api/latest/dagger/Inject.html)
- [Hilt Android Guide](https://developer.android.com/training/dependency-injection/hilt-android)

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-dagger-build-time-optimization--android--medium]]
- [[q-hilt-components-scope--android--medium]]

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]]
- [[q-dagger-multibinding--android--hard]]

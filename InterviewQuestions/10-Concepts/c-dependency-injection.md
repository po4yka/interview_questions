---
id: ivc-20251023-120000
title: Dependency Injection / Внедрение зависимостей
aliases: [DI, Dependency Injection, Внедрение зависимостей, Инъекция зависимостей]
kind: concept
summary: Design pattern where object dependencies are provided externally rather than created internally
links: [c-dagger, c-hilt]
created: 2025-10-23
updated: 2025-10-23
status: draft
tags: [concept, architecture-patterns, dependency-injection, android]
---

# Dependency Injection / Внедрение зависимостей

## Summary (EN)

Dependency Injection (DI) is a design pattern where an object receives its dependencies from external sources rather than creating them internally. This promotes loose coupling, testability, and maintainability by separating object creation from business logic. In Android, DI is commonly implemented using frameworks like Dagger, Hilt, or Koin.

## Краткое описание (RU)

Внедрение зависимостей (DI) — это паттерн проектирования, при котором объект получает свои зависимости из внешних источников, а не создает их внутри себя. Это способствует слабой связанности, тестируемости и поддерживаемости кода, разделяя создание объектов от бизнес-логики. В Android DI обычно реализуется с помощью фреймворков, таких как Dagger, Hilt или Koin.

## Key Points (EN)

- **Inversion of Control**: Dependencies are provided to objects rather than objects creating them
- **Three main types**: Constructor injection, field injection, method injection
- **Framework support**: Android commonly uses Dagger, Hilt (built on Dagger), or Koin
- **Compile-time vs runtime**: Dagger/Hilt use compile-time generation, Koin uses runtime reflection
- **Scopes**: Control lifetime of dependencies (Singleton, Activity-scoped, ViewModel-scoped, etc.)

## Ключевые моменты (RU)

- **Инверсия управления**: Зависимости предоставляются объектам извне, а не создаются внутри них
- **Три основных типа**: Инъекция через конструктор, поле или метод
- **Поддержка фреймворков**: В Android обычно используются Dagger, Hilt (построен на Dagger) или Koin
- **Компиляция vs выполнение**: Dagger/Hilt используют генерацию во время компиляции, Koin — рефлексию во время выполнения
- **Области видимости**: Управление жизненным циклом зависимостей (Singleton, Activity-scoped, ViewModel-scoped и т.д.)

## Types of Injection

### Constructor Injection (Recommended)

```kotlin
// Dependencies provided through constructor
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val database: UserDatabase
) {
    // Use dependencies
}
```

### Field Injection

```kotlin
class MainActivity : AppCompatActivity() {
    @Inject lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Injection happens after constructor
    }
}
```

### Method Injection

```kotlin
class UserPresenter {
    private lateinit var logger: Logger

    @Inject
    fun setLogger(logger: Logger) {
        this.logger = logger
    }
}
```

## Use Cases

### When to Use

- Complex dependency graphs with multiple layers
- Need to provide different implementations (e.g., test vs production)
- Improve testability by mocking dependencies
- Share instances across components (singleton pattern)
- Manage object lifecycles automatically

### When to Avoid

- Very simple applications with minimal dependencies
- Prototypes or proof-of-concepts where setup overhead isn't justified
- When learning Android basics (adds complexity for beginners)
- Small utility classes with no dependencies

## Trade-offs

**Pros**:
- **Testability**: Easy to replace real dependencies with mocks or fakes
- **Loose coupling**: Components don't know about concrete implementations
- **Reusability**: Dependencies can be easily shared and reused
- **Maintainability**: Changes to dependencies don't affect consumers
- **Separation of concerns**: Object creation separated from usage

**Cons**:
- **Learning curve**: Requires understanding of DI concepts and framework specifics
- **Setup complexity**: Initial configuration can be time-consuming
- **Build time**: Compile-time frameworks like Dagger increase build time
- **Debugging**: Harder to trace dependency resolution issues
- **Boilerplate**: Requires annotations and configuration code

## Android-Specific Considerations

### Framework Comparison

| Framework | Type | Pros | Cons |
|-----------|------|------|------|
| **Hilt** | Compile-time | Official support, less boilerplate | Dagger complexity underneath |
| **Dagger** | Compile-time | Fast runtime, type-safe | Steep learning curve |
| **Koin** | Runtime | Easy to learn, Kotlin DSL | Runtime overhead, less type safety |

### Common Scopes in Android

```kotlin
@Singleton              // App lifetime
@ActivityScoped         // Activity lifetime
@FragmentScoped         // Fragment lifetime
@ViewModelScoped        // ViewModel lifetime
```

## Related Questions

- [[q-dependency-injection-benefits--android--medium]]
- [[q-dagger-vs-hilt--android--medium]]
- [[q-dependency-injection-types--android--easy]]
- [[q-singleton-pattern-issues--android--medium]]

## Related Concepts

- [[c-hilt]] - Google's DI library for Android
- [[c-dagger]] - Compile-time DI framework
- [[c-mvvm-pattern]] - Often used with DI for ViewModels
- [[c-testing]] - DI greatly improves testability

## References

- [Android Dependency Injection](https://developer.android.com/training/dependency-injection)
- [Dagger Documentation](https://dagger.dev/)
- [Hilt Documentation](https://developer.android.com/training/dependency-injection/hilt-android)
- [Koin Documentation](https://insert-koin.io/)
- [Martin Fowler on Dependency Injection](https://martinfowler.com/articles/injection.html)

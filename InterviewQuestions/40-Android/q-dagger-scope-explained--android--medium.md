---
id: android-462
title: Dagger Scope Explained / Объяснение скоупов Dagger
aliases: [Dagger Scope Explained, Объяснение скоупов Dagger]
topic: android
subtopics:
  - di-hilt
  - lifecycle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-dagger
  - q-dagger-custom-scopes--android--hard
  - q-dagger-framework-overview--android--hard
  - q-dagger-main-elements--android--medium
created: 2025-10-20
updated: 2025-11-10
tags: [android/di-hilt, android/lifecycle, dagger, difficulty/medium, hilt, lifecycle, scope]
sources:
  - "https://dagger.dev/api/latest/dagger/Scope.html"
---

# Вопрос (RU)
> Что такое scope в Dagger и как они работают?

# Question (EN)
> What is scope in Dagger and how do they work?

## Ответ (RU)

**Scope** в Dagger — это механизм управления временем жизни зависимостей. Scope гарантирует, что в рамках одного компонента создается только один экземпляр объекта. Это позволяет переиспользовать дорогие в создании объекты и контролировать их жизненный цикл.

### Принцип Работы

Scope привязывает зависимость к жизненному циклу Dagger-компонента:
- Компонент создан → создается scoped-зависимость
- Компонент жив → переиспользуется один экземпляр (кэшируется в компоненте)
- Компонент уничтожен → зависимость освобождается (может быть GC)

**Проверка на этапе компиляции**: Dagger проверяет, что scoped-зависимости используются только в компонентах с соответствующим scope. Нарушение правил иерархии вызывает ошибку компиляции.

### Иерархия Hilt Scopes (упрощенно)

```kotlin
@Singleton                    // Application (SingletonComponent) lifetime
  └─ @ActivityRetainedScoped  // ActivityRetainedComponent: переживает recreation Activity
      ├─ @ActivityScoped      // ActivityComponent: жизненный цикл Activity
      │   ├─ @FragmentScoped  // Fragment lifecycle
      │   └─ @ViewScoped      // View lifecycle
      └─ @ViewModelScoped     // ViewModelComponent: жизненный цикл ViewModel

  └─ @ServiceScoped           // ServiceComponent: жизненный цикл Service
```

(Диаграмма отражает основные отношения долгоживущих и краткоживущих скоупов, а не все технические детали реализации.)

### Типичные Кейсы

```kotlin
// ✅ Singleton для глобальных сервисов (@Singleton в Hilt привязан к SingletonComponent)
@Singleton
class NetworkClient @Inject constructor()

// ✅ ActivityRetainedScoped для данных, переживающих configuration changes
@ActivityRetainedScoped
class UserSessionManager @Inject constructor()

// ✅ ViewModelScoped для зависимостей ViewModel
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: ProfileRepository  // @ViewModelScoped — один экземпляр на ViewModel
) : ViewModel()

@ViewModelScoped
class ProfileRepository @Inject constructor(
    private val api: ApiService  // @Singleton — переиспользуется
)
```

### Правила Использования

**Scope Hierarchy Rule**: дочерний компонент может использовать зависимости из родительского scope, но не наоборот. Это предотвращает ситуации, когда долгоживущий объект удерживает ссылку на краткоживущую зависимость и мешает её сборке мусора.

```kotlin
// ✅ Правильно: Activity-скоуп использует Singleton
@ActivityScoped
class UserFlow @Inject constructor(
    private val database: Database  // @Singleton — OK
)

// ❌ Неправильно: Singleton зависит от Activity scope
@Singleton
class GlobalService @Inject constructor(
    private val flow: UserFlow  // @ActivityScoped — ОШИБКА компиляции
)
```

**Правильный выбор scope**:
- Тяжелые объекты (DB, Network) → `@Singleton` — дорогие в создании, нужны глобально
- Данные UI, переживающие rotation → `@ActivityRetainedScoped` или `@ViewModelScoped` — сохранение состояния при пересоздании
- UI-адаптеры, презентеры → `@ActivityScoped` или `@FragmentScoped` — привязка к UI-жизненному циклу
- Легкие утилиты → unscoped (создаются каждый раз) — нет смысла кэшировать дешёвые объекты

## Answer (EN)

**Scope** in Dagger is a mechanism for managing dependency lifetimes. A scope guarantees that only one instance of a given type is created within a single component. This allows reusing expensive-to-create objects and controlling their lifecycle.

### How it Works

Scope binds a dependency to the lifecycle of a Dagger/Hilt component:
- Component created → scoped dependency instantiated
- Component alive → same instance reused (cached in the component)
- Component destroyed → dependency released (eligible for GC)

**Compile-time validation**: Dagger verifies that scoped dependencies are only used in components with compatible scopes. Hierarchy violations cause compilation errors.

### Hilt Scope Hierarchy (simplified)

```kotlin
@Singleton                    // Application (SingletonComponent) lifetime
  └─ @ActivityRetainedScoped  // ActivityRetainedComponent: survives Activity recreation
      ├─ @ActivityScoped      // ActivityComponent: Activity lifecycle
      │   ├─ @FragmentScoped  // Fragment lifecycle
      │   └─ @ViewScoped      // View lifecycle
      └─ @ViewModelScoped     // ViewModelComponent: ViewModel lifecycle

  └─ @ServiceScoped           // ServiceComponent: Service lifecycle
```

(The diagram shows the main long-lived vs short-lived relationships, not every implementation detail.)

### Typical Use Cases

```kotlin
// ✅ Singleton for global services (@Singleton in Hilt is bound to SingletonComponent)
@Singleton
class NetworkClient @Inject constructor()

// ✅ ActivityRetainedScoped for data surviving configuration changes
@ActivityRetainedScoped
class UserSessionManager @Inject constructor()

// ✅ ViewModelScoped for ViewModel dependencies
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: ProfileRepository  // @ViewModelScoped — one instance per ViewModel
) : ViewModel()

@ViewModelScoped
class ProfileRepository @Inject constructor(
    private val api: ApiService  // @Singleton — reused
)
```

### Usage Rules

**Scope Hierarchy Rule**: child components can use dependencies from parent scopes, but not vice versa. This prevents long-lived objects from depending on shorter-lived scoped objects and accidentally keeping them in memory.

```kotlin
// ✅ Correct: Activity scope uses Singleton
@ActivityScoped
class UserFlow @Inject constructor(
    private val database: Database  // @Singleton — OK
)

// ❌ Incorrect: Singleton depends on Activity scope
@Singleton
class GlobalService @Inject constructor(
    private val flow: UserFlow  // @ActivityScoped — COMPILATION ERROR
)
```

**Choosing the right scope**:
- Heavy objects (DB, Network) → `@Singleton` — expensive to create, needed globally
- UI data surviving rotation → `@ActivityRetainedScoped` or `@ViewModelScoped` — preserve state across recreation
- UI adapters, presenters → `@ActivityScoped` or `@FragmentScoped` — tied to UI lifecycle
- Lightweight utilities → unscoped (created each time) — no benefit in caching

## Дополнительные вопросы (RU)

- Как создавать кастомные scope в Dagger?
- Что произойдет, если внедрить зависимость с `@ActivityScoped` в компонент с `@Singleton`?
- Как `@ActivityRetainedScoped` технически переживает смену конфигурации?
- Каковы последствия для производительности при чрезмерном использовании зависимостей с `@Singleton`?
- Как тестировать scoped-зависимости?

## Follow-ups

- How do you create custom scopes in Dagger?
- What happens if you inject an `@ActivityScoped` dependency into a `@Singleton` component?
- How does `@ActivityRetainedScoped` survive configuration changes internally?
- What are the performance implications of using too many `@Singleton` dependencies?
- How do you test scoped dependencies?

## Ссылки (RU)

- [[c-dependency-injection]] — основы DI и принципы
- [Документация по Scope в Dagger](https://dagger.dev/api/latest/dagger/Scope.html)
- [Иерархия компонентов Hilt](https://developer.android.com/training/dependency-injection/hilt-android#component-hierarchy)

## References

- [[c-dependency-injection]] — DI fundamentals and principles
- [Dagger Scope Documentation](https://dagger.dev/api/latest/dagger/Scope.html)
- [Hilt Component Hierarchy](https://developer.android.com/training/dependency-injection/hilt-android#component-hierarchy)

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-dagger-inject-annotation--android--easy]] — понимание аннотации `@Inject`
- Базовое понимание концепций dependency injection

### Связанные (того же уровня)
- [[q-dagger-main-elements--android--medium]] — основные концепции Dagger
- Понимание жизненного цикла компонентов
- Отличия Hilt от классического Dagger

### Продвинутые (сложнее)
- [[q-dagger-custom-scopes--android--hard]] — создание кастомных scope
- [[q-dagger-framework-overview--android--hard]] — детальный обзор внутреннего устройства Dagger
- Subcomponents и отношения scope

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] — Understanding `@Inject` annotation
- Basic understanding of dependency injection concepts

### Related (Same Level)
- [[q-dagger-main-elements--android--medium]] — Core Dagger concepts
- Understanding of component lifecycle
- Hilt vs vanilla Dagger differences

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]] — Creating custom scopes
- [[q-dagger-framework-overview--android--hard]] — Deep dive into Dagger internals
- Subcomponents and scope relationships

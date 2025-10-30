---
id: 20251012-122711
title: "Singleton Scope Binding / Привязка Singleton скоупа"
aliases: ["Singleton Scope Binding", "Привязка Singleton скоупа"]
topic: android
subtopics: [di-hilt, lifecycle]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/di-hilt, android/lifecycle, dagger, hilt, scope, dependency-injection, difficulty/medium]
---
# Вопрос (RU)

К какому scope привязан @Singleton в Dagger/Hilt?

# Question (EN)

What scope is @Singleton bound to in Dagger/Hilt?

---

## Ответ (RU)

**@Singleton привязан к времени жизни компонента**, а не является глобальным синглтоном.

**Ключевые аспекты:**

- В Dagger: живет столько, сколько живет Component
- В Hilt: привязан к SingletonComponent (Application lifecycle)
- Один экземпляр на компонент, а не на JVM
- Может вызвать утечки памяти при неправильном использовании

**Hilt-пример:**

```kotlin
@HiltAndroidApp
class MyApp : Application()

@Singleton  // ✅ Живет весь жизненный цикл приложения
class UserRepository @Inject constructor(
    private val api: ApiService
)

// Создается: Application.onCreate()
// Уничтожается: когда процесс завершается
```

**Важное отличие от Kotlin object:**

```kotlin
// ❌ НЕ то же самое, что:
object UserRepository {
    // Истинный singleton на уровне JVM
}

// ✅ @Singleton в Dagger:
@Singleton
class UserRepository @Inject constructor() {
    // Один экземпляр на компонент
}

val comp1 = DaggerAppComponent.create()
val comp2 = DaggerAppComponent.create()
// repo1 !== repo2 (разные экземпляры!)
```

**Hilt Component Scopes:**

| Scope | Lifetime | Типичные Use Cases |
|-------|----------|-------------------|
| @Singleton | Application | Database, NetworkClient, Analytics |
| @ActivityRetainedScoped | Config changes | ViewModel data |
| @ActivityScoped | Activity | Presenter, Navigator |
| @FragmentScoped | Fragment | Fragment-specific logic |

**Типичные ошибки:**

```kotlin
// ❌ BAD: Утечка памяти
@Singleton
class Analytics @Inject constructor(
    private val activity: Activity  // Activity leak!
)

// ✅ GOOD: Используйте Application Context
@Singleton
class Analytics @Inject constructor(
    @ApplicationContext private val context: Context
)

// ❌ BAD: Неправильный scope
@Singleton
class ActivityPresenter  // Activity-данные в app-scope

// ✅ GOOD: Соответствие scope жизненному циклу
@ActivityScoped
class ActivityPresenter
```

## Answer (EN)

**@Singleton is bound to the component's lifetime**, not a true global singleton.

**Key aspects:**

- In Dagger: lives as long as the Component exists
- In Hilt: bound to SingletonComponent (Application lifecycle)
- One instance per component, not per JVM
- Can cause memory leaks if misused

**Hilt example:**

```kotlin
@HiltAndroidApp
class MyApp : Application()

@Singleton  // ✅ Lives entire app lifetime
class UserRepository @Inject constructor(
    private val api: ApiService
)

// Created: Application.onCreate()
// Destroyed: when process terminates
```

**Key distinction from Kotlin object:**

```kotlin
// ❌ NOT the same as:
object UserRepository {
    // True JVM-level singleton
}

// ✅ @Singleton in Dagger:
@Singleton
class UserRepository @Inject constructor() {
    // One instance per component
}

val comp1 = DaggerAppComponent.create()
val comp2 = DaggerAppComponent.create()
// repo1 !== repo2 (different instances!)
```

**Hilt Component Scopes:**

| Scope | Lifetime | Typical Use Cases |
|-------|----------|-------------------|
| @Singleton | Application | Database, NetworkClient, Analytics |
| @ActivityRetainedScoped | Config changes | ViewModel data |
| @ActivityScoped | Activity | Presenter, Navigator |
| @FragmentScoped | Fragment | Fragment-specific logic |

**Common mistakes:**

```kotlin
// ❌ BAD: Memory leak
@Singleton
class Analytics @Inject constructor(
    private val activity: Activity  // Activity leak!
)

// ✅ GOOD: Use Application Context
@Singleton
class Analytics @Inject constructor(
    @ApplicationContext private val context: Context
)

// ❌ BAD: Wrong scope
@Singleton
class ActivityPresenter  // Activity data in app-scope

// ✅ GOOD: Match scope to lifecycle
@ActivityScoped
class ActivityPresenter
```

---

## Follow-ups

- What happens if you create multiple Dagger components with @Singleton bindings?
- How does @ActivityRetainedScoped differ from @Singleton during configuration changes?
- Can you use custom scopes, and how do you define component lifetime?
- What are the testing implications of component-scoped singletons?
- How do you debug memory leaks caused by improper scope usage?

## References

- [[c-dependency-injection]]
- [Hilt Component Scopes](https://developer.android.com/training/dependency-injection/hilt-android#component-scopes)
- [Dagger Scopes](https://dagger.dev/dev-guide/custom-scopes)

## Related Questions

### Prerequisites (Easier)
- [[c-dependency-injection]] - Understanding DI fundamentals

### Related (Same Level)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]]

### Advanced (Harder)
- Custom scope implementation and component hierarchy
- Multi-module DI architecture with scoped components
- Memory leak detection and prevention in scoped dependencies

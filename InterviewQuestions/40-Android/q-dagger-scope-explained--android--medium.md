---
id: android-462
title: Dagger Scope Explained / Объяснение скоупов Dagger
aliases: ["Dagger Scope Explained", "Объяснение скоупов Dagger"]
topic: android
subtopics: [di-hilt, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-dagger-custom-scopes--android--hard, q-dagger-framework-overview--android--hard, q-dagger-main-elements--android--medium]
created: 2025-10-20
updated: 2025-10-27
tags: [android/di-hilt, android/lifecycle, dagger, difficulty/medium, hilt, lifecycle, scope]
sources: [https://dagger.dev/api/latest/dagger/Scope.html]
date created: Monday, October 27th 2025, 10:27:07 pm
date modified: Thursday, October 30th 2025, 12:47:31 pm
---

# Вопрос (RU)
> Что такое scope в Dagger и как они работают?

# Question (EN)
> What is scope in Dagger and how do they work?

## Ответ (RU)

**Scope** в Dagger — это механизм управления временем жизни зависимостей. Scope гарантирует, что в рамках одного компонента создается только один экземпляр объекта.

### Принцип работы

Scope привязывает зависимость к жизненному циклу Dagger-компонента:
- Компонент создан → создается scoped-зависимость
- Компонент жив → переиспользуется один экземпляр
- Компонент уничтожен → зависимость освобождается

**Проверка на этапе компиляции**: Dagger проверяет, что scoped-зависимости используются только в компонентах с соответствующим scope.

### Иерархия Hilt Scopes

```kotlin
@Singleton              // ✅ Приложение (Application)
  └─ @ActivityRetainedScoped  // ✅ Переживает пересоздание Activity
      └─ @ActivityScoped      // ✅ Activity
          ├─ @FragmentScoped  // ✅ Fragment
          └─ @ViewScoped      // ✅ View
  └─ @ViewModelScoped         // ✅ ViewModel
  └─ @ServiceScoped           // ✅ Service
```

### Типичные кейсы

```kotlin
// ✅ Singleton для глобальных сервисов
@Singleton
class NetworkClient @Inject constructor()

// ✅ ActivityRetainedScoped для данных, переживающих configuration changes
@ActivityRetainedScoped
class UserSessionManager @Inject constructor()

// ✅ ViewModelScoped для зависимостей ViewModel
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: ProfileRepository  // ❌ Unscoped - создается каждый раз
) : ViewModel()

@ViewModelScoped  // ✅ Живет вместе с ViewModel
class ProfileRepository @Inject constructor(
    private val api: ApiService  // ✅ @Singleton - переиспользуется
)
```

### Правила использования

**Scope Hierarchy Rule**: дочерний компонент может использовать зависимости из родительского scope, но не наоборот:

```kotlin
// ✅ Правильно: Activity использует Singleton
@ActivityScoped
class UserFlow @Inject constructor(
    private val database: Database  // @Singleton - ОК
)

// ❌ Неправильно: Singleton зависит от Activity scope
@Singleton
class GlobalService @Inject constructor(
    private val flow: UserFlow  // @ActivityScoped - ОШИБКА компиляции
)
```

**Правильный выбор scope**:
- Тяжелые объекты (DB, Network) → `@Singleton`
- Данные UI, переживающие rotation → `@ActivityRetainedScoped` или `@ViewModelScoped`
- UI-адаптеры, презентеры → `@ActivityScoped` или `@FragmentScoped`
- Легкие утилиты → unscoped (создаются каждый раз)

## Answer (EN)

**Scope** in Dagger is a mechanism for managing dependency lifetimes. A scope guarantees that only one instance of an object is created within a single component.

### How it works

Scope binds a dependency to the lifecycle of a Dagger component:
- Component created → scoped dependency instantiated
- Component alive → same instance reused
- Component destroyed → dependency released

**Compile-time validation**: Dagger verifies that scoped dependencies are only used in components with matching scopes.

### Hilt Scope Hierarchy

```kotlin
@Singleton              // ✅ Application
  └─ @ActivityRetainedScoped  // ✅ Survives Activity recreation
      └─ @ActivityScoped      // ✅ Activity
          ├─ @FragmentScoped  // ✅ Fragment
          └─ @ViewScoped      // ✅ View
  └─ @ViewModelScoped         // ✅ ViewModel
  └─ @ServiceScoped           // ✅ Service
```

### Typical Use Cases

```kotlin
// ✅ Singleton for global services
@Singleton
class NetworkClient @Inject constructor()

// ✅ ActivityRetainedScoped for data surviving configuration changes
@ActivityRetainedScoped
class UserSessionManager @Inject constructor()

// ✅ ViewModelScoped for ViewModel dependencies
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val repository: ProfileRepository  // ❌ Unscoped - created each time
) : ViewModel()

@ViewModelScoped  // ✅ Lives with ViewModel
class ProfileRepository @Inject constructor(
    private val api: ApiService  // ✅ @Singleton - reused
)
```

### Usage Rules

**Scope Hierarchy Rule**: child components can use dependencies from parent scopes, but not vice versa:

```kotlin
// ✅ Correct: Activity uses Singleton
@ActivityScoped
class UserFlow @Inject constructor(
    private val database: Database  // @Singleton - OK
)

// ❌ Incorrect: Singleton depends on Activity scope
@Singleton
class GlobalService @Inject constructor(
    private val flow: UserFlow  // @ActivityScoped - COMPILATION ERROR
)
```

**Choosing the right scope**:
- Heavy objects (DB, Network) → `@Singleton`
- UI data surviving rotation → `@ActivityRetainedScoped` or `@ViewModelScoped`
- UI adapters, presenters → `@ActivityScoped` or `@FragmentScoped`
- Lightweight utilities → unscoped (created each time)

## Follow-ups

- How do you create custom scopes in Dagger?
- What happens if you inject an `@ActivityScoped` dependency into a `@Singleton` component?
- How does `@ActivityRetainedScoped` survive configuration changes internally?
- What are the performance implications of using too many singletons?
- How do you test scoped dependencies?

## References

- [[c-dependency-injection]] — DI fundamentals and principles
- Official Dagger documentation on scopes: https://dagger.dev/api/latest/dagger/Scope.html
- Hilt component hierarchy: https://developer.android.com/training/dependency-injection/hilt-android#component-hierarchy

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] — Understanding @Inject annotation
- q-what-is-dependency-injection--android--easy — DI basics

### Related (Same Level)
- [[q-dagger-main-elements--android--medium]] — Core Dagger concepts
- q-hilt-vs-dagger--android--medium — Choosing between Hilt and vanilla Dagger
- q-viewmodel-scope--android--medium — ViewModel lifecycle management

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]] — Creating custom scopes
- [[q-dagger-framework-overview--android--hard]] — Deep dive into Dagger internals
- q-dagger-subcomponents--android--hard — Subcomponents and scope relationships

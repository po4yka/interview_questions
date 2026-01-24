---
id: android-462
title: Dagger Scope Explained / Объяснение скоупов Dagger
aliases:
- Dagger Scope Explained
- Объяснение скоупов Dagger
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
- q-dagger-problems--android--medium
- q-dagger-purpose--android--easy
- q-singleton-scope-binding--android--medium
created: 2025-10-20
updated: 2025-11-10
tags:
- android/di-hilt
- android/lifecycle
- dagger
- difficulty/medium
- hilt
- lifecycle
- scope
anki_cards:
- slug: android-462-0-en
  language: en
  anki_id: 1768366755276
  synced_at: '2026-01-23T16:45:06.221659'
- slug: android-462-0-ru
  language: ru
  anki_id: 1768366755301
  synced_at: '2026-01-23T16:45:06.222437'
sources:
- https://dagger.dev/api/latest/dagger/Scope.html
---
# Вопрос (RU)
> Что такое scope в `Dagger` и как они работают?

# Question (EN)
> What is scope in `Dagger` and how do they work?

## Ответ (RU)

**Scope** в `Dagger` — это механизм управления временем жизни зависимостей. Scope гарантирует, что в рамках одного компонента создается только один экземпляр объекта для данного scope. Это позволяет переиспользовать дорогие в создании объекты и контролировать их жизненный цикл.

### Принцип Работы

Scope привязывает зависимость к жизненному циклу `Dagger`-/Hilt-компонента:
- Компонент создан → создается scoped-зависимость (при первом запросе)
- Компонент жив → переиспользуется один и тот же экземпляр (кэшируется внутри компонента)
- Компонент уничтожен → зависимости становятся неиспользуемыми и могут быть собраны GC

**Проверка на этапе компиляции**: `Dagger` проверяет, что scoped-зависимости объявлены и используются в компонентах с совместимыми scope. Нарушение правил (например, долгоживущий scope зависит от краткоживущего) приводит к ошибке компиляции.

### Иерархия Hilt Scopes (упрощенно, концептуально)

```kotlin
@Singleton                    // Application (SingletonComponent) lifetime
  └─ @ActivityRetainedScoped  // ActivityRetainedComponent: переживает recreation Activity
      ├─ @ActivityScoped      // ActivityComponent: жизненный цикл Activity
      │   ├─ @FragmentScoped  // Fragment lifecycle
      │   └─ @ViewScoped      // View lifecycle
      └─ @ViewModelScoped     // ViewModelComponent: жизненный цикл ViewModel

  └─ @ServiceScoped           // ServiceComponent: жизненный цикл Service
```

(Диаграмма передает относительную "долгоживущесть" и типичные отношения использования, а не точную структуру всех `Hilt`-компонентов. Например, `ActivityRetainedComponent` и `ActivityComponent` — разные компоненты, но зависимости из более долгоживущих scope могут использоваться в более краткоживущих.)

### Типичные Кейсы

```kotlin
// ✅ Singleton для глобальных сервисов (@Singleton в Hilt привязан к SingletonComponent)
@Singleton
class NetworkClient @Inject constructor()

// ✅ ActivityRetainedScoped для зависимостей, переживающих configuration changes
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

**Scope Hierarchy Rule**: зависимости из более долгоживущего scope могут использоваться в более краткоживущих компонентах, но не наоборот. Это предотвращает ситуации, когда долгоживущий объект удерживает ссылку на краткоживущую зависимость и мешает её сборке мусора.

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
- Данные/логика, переживающие rotation (например, сессия пользователя, кэш, бизнесс-логика) → `@ActivityRetainedScoped` или зависимости `@ViewModelScoped` — сохраняют состояние при пересоздании `Activity`
- Объекты, привязанные к конкретному UI-экрану (адаптеры, презентеры и т.п.) → `@ActivityScoped` или `@FragmentScoped` — живут столько же, сколько экран
- Легкие утилиты → unscoped (создаются каждый раз) — нет смысла кэшировать дешёвые объекты

## Answer (EN)

**Scope** in `Dagger` is a mechanism for managing dependency lifetimes. A scope guarantees that within a given component, only one instance of a scoped binding is created and reused. This enables reuse of expensive objects and precise lifecycle control.

### How it Works

Scope binds a dependency to the lifecycle of a Dagger/Hilt component:
- `Component` created → scoped dependency is created on first request
- `Component` alive → same instance is reused (cached inside the component)
- `Component` destroyed → dependencies become unreachable and are eligible for GC

**Compile-time validation**: `Dagger` verifies that scoped bindings are declared and used only in components with compatible scopes. Violations (e.g., a longer-lived scope depending on a shorter-lived scoped binding) result in compilation errors.

### Hilt Scope Hierarchy (simplified, conceptual)

```kotlin
@Singleton                    // Application (SingletonComponent) lifetime
  └─ @ActivityRetainedScoped  // ActivityRetainedComponent: survives Activity recreation
      ├─ @ActivityScoped      // ActivityComponent: Activity lifecycle
      │   ├─ @FragmentScoped  // Fragment lifecycle
      │   └─ @ViewScoped      // View lifecycle
      └─ @ViewModelScoped     // ViewModelComponent: ViewModel lifecycle

  └─ @ServiceScoped           // ServiceComponent: Service lifecycle
```

(This diagram expresses relative lifetimes and typical usage relationships, not the exact internal `Hilt` component graph. For example, `ActivityRetainedComponent` and `ActivityComponent` are separate components; longer-lived scoped dependencies can be used in shorter-lived components, but not the other way around.)

### Typical Use Cases

```kotlin
// ✅ Singleton for global services (@Singleton in Hilt is bound to SingletonComponent)
@Singleton
class NetworkClient @Inject constructor()

// ✅ ActivityRetainedScoped for dependencies that survive configuration changes
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

**Scope Hierarchy Rule**: shorter-lived components can depend on longer-lived scoped dependencies, but longer-lived components must not depend on shorter-lived scoped dependencies. This prevents long-lived objects from keeping references to short-lived objects and leaking them.

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
- Logic/state that must survive configuration changes (e.g., user session, cached data, domain logic) → `@ActivityRetainedScoped` or `@ViewModelScoped` dependencies — preserved across `Activity` recreation
- Objects tied to a specific UI screen (adapters, presenters, etc.) → `@ActivityScoped` or `@FragmentScoped` — live as long as the screen
- Lightweight utilities → unscoped (new instance each time) — no real benefit from scoping

## Дополнительные Вопросы (RU)

- Как создавать кастомные scope в `Dagger`?
- Что произойдет, если внедрить зависимость с `@ActivityScoped` в компонент с `@Singleton`?
- Как `@ActivityRetainedScoped` технически переживает смену конфигурации?
- Каковы последствия для производительности при чрезмерном использовании зависимостей с `@Singleton`?
- Как тестировать scoped-зависимости?

## Follow-ups

- How do you create custom scopes in `Dagger`?
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
- [Hilt `Component` Hierarchy](https://developer.android.com/training/dependency-injection/hilt-android#component-hierarchy)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-dagger-inject-annotation--android--easy]] — понимание аннотации `@Inject`
- Базовое понимание концепций dependency injection

### Связанные (того Же уровня)
- [[q-dagger-main-elements--android--medium]] — основные концепции `Dagger`
- Понимание жизненного цикла компонентов
- Отличия `Hilt` от классического `Dagger`

### Продвинутые (сложнее)
- [[q-dagger-custom-scopes--android--hard]] — создание кастомных scope
- [[q-dagger-framework-overview--android--hard]] — детальный обзор внутреннего устройства `Dagger`
- Subcomponents и отношения scope

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]] — Understanding `@Inject` annotation
- Basic understanding of dependency injection concepts

### Related (Same Level)
- [[q-dagger-main-elements--android--medium]] — Core `Dagger` concepts
- Understanding of component lifecycle
- `Hilt` vs vanilla `Dagger` differences

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]] — Creating custom scopes
- [[q-dagger-framework-overview--android--hard]] — Deep dive into `Dagger` internals
- Subcomponents and scope relationships

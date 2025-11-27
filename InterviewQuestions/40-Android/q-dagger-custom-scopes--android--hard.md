---
id: android-451
title: Dagger Custom Scopes / Кастомные скоупы Dagger
aliases: [Dagger Custom Scopes, Кастомные скоупы Dagger]
topic: android
subtopics:
  - di-hilt
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-dagger
  - c-dependency-injection
  - q-dagger-build-time-optimization--android--medium
  - q-dagger-component-dependencies--android--hard
  - q-dagger-framework-overview--android--hard
  - q-dagger-multibinding--android--hard
  - q-dagger-purpose--android--easy
  - q-hilt-components-scope--android--medium
created: 2025-10-20
updated: 2025-11-10
tags: [android/di-hilt, dagger, dependency-injection, difficulty/hard, hilt]
sources:
  - "https://dagger.dev/hilt/components.html"
date created: Saturday, November 1st 2025, 12:46:48 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---
# Вопрос (RU)
> Как создать и использовать кастомные скоупы в Dagger/Hilt? Объясните разницу между `@Singleton`, пользовательскими (custom) скоупами и unscoped-зависимостями. Когда и зачем стоит создавать кастомный скоуп?

# Question (EN)
> How do you create and use custom scopes in Dagger/Hilt? Explain the difference between Singleton, custom scopes, and unscoped dependencies. When and why would you create a custom scope?

## Ответ (RU)

Кастомные скоупы в обычном Dagger позволяют управлять временем жизни зависимостей за пределами стандартных Android-компонентов (`Activity`, `Fragment`) и изолировать состояние для конкретных фич или сущностей (например, пользовательская сессия). В отличие от `@Singleton` и встроенных Hilt-скоупов (таких как `@ActivityScoped`), кастомный скоуп в Dagger реализуется через отдельный компонент со своим `@Scope`, время жизни которого вы создаёте и уничтожаете явно.

### Типы Скоупов

- `@Singleton` (Dagger/Hilt)
  - Привязан к корневому (singleton) компоненту.
  - В рамках этого компонента создаётся один экземпляр зависимости на весь его жизненный цикл (в Android обычно на процесс приложения).

- `@ActivityScoped` / `@FragmentScoped` (Hilt)
  - Привязаны к соответствующим Hilt-компонентам (`ActivityComponent`, `FragmentComponent`).
  - Экземпляры кэшируются на время жизни компонента (включая дочерние графы), а не строго по `onCreate`/`onDestroy`, но по сути живут столько же, сколько соответствующий экран.

- Unscoped-зависимости
  - Компонент их не кэширует.
  - Новый экземпляр создаётся при каждом запросе инъекции (через `@Provides` или `@Inject` конструктор), даже внутри скоупленного компонента.

- Кастомный скоуп (Dagger)
  - Вы определяете собственную аннотацию `@Scope` и помечаете ей компонент и зависимости.
  - Время жизни скоупа = время жизни соответствующего компонента, которым вы управляете явно (создание/очистка ссылки).
  - Полезен для пользовательских сессий, навигационных flows/feature-скоупов и любых жизненных циклов, которые не совпадают 1:1 со стандартными скоупами.

### Создание Кастомного Скоупа (Dagger)

```kotlin
// 1. Определяем аннотацию-скоуп
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// 2. Создаём компонент с этим скоупом
@UserSessionScope
@Component(modules = [UserModule::class])
interface UserSessionComponent {
    fun userManager(): UserManager

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance userId: UserId): UserSessionComponent
    }
}

// 3. Помечаем зависимости этим скоупом
@UserSessionScope
class UserManager @Inject constructor(
    private val userId: UserId,
    private val api: ApiService
)
```

### Управление Жизненным Циклом (Dagger)

```kotlin
object UserSessionHolder {
    private var component: UserSessionComponent? = null

    fun login(userId: UserId) {
        // Создаём компонент (и граф скоупа) при логине
        component = DaggerUserSessionComponent.factory().create(userId)
    }

    fun logout() {
        // Обнуляем ссылку на компонент; все скоупленные объекты становятся кандидатами на GC
        component = null
    }

    fun get(): UserSessionComponent = component ?: error("User not logged in")
}
```

### Когда Использовать Кастомный Скоуп (Dagger)

Создавайте кастомный скоуп, когда:
- нужен пер-пользовательский скоуп (multi-user / user session), чтобы изолировать состояние между сессиями;
- нужен per-feature/flow-скоуп с тяжёлыми зависимостями или сложным состоянием, которое должно очищаться при выходе из флоу;
- требуется изоляция между модулями/фичами и вы хотите избежать глобальных `@Singleton`, которые могут протекать данными.

Используйте встроенные скоупы (Hilt/Dagger), когда:
- жизненный цикл зависимости естественно совпадает с `Activity`/`Fragment`/`ViewModel` (обычно достаточно Hilt-скоупов);
- состояние простое и не требует отдельного графа и явного управления временем жизни.

### Сравнение С Hilt

В Hilt жизненные циклы компонентов и скоупов фиксированы и управляются фреймворком. Добавлять произвольные новые скоупы для Hilt-компонентов нельзя.

Предпочитайте встроенные в Hilt скоупы:
- `@Singleton` — для зависимостей на весь процесс (SingletonComponent);
- `@ActivityRetainedScoped` — для объектов, переживающих конфигурационные изменения (`ViewModel`-подобные);
- `@ActivityScoped` — на время жизни `Activity`;
- `@ViewModelScoped` — на время жизни `ViewModel`;
- `@FragmentScoped` — на время жизни `Fragment`;
- `@ViewScoped` — на время жизни `View`.

Если нужный жизненный цикл не попадает в эти варианты (например, сессия пользователя), то:
- используйте отдельные обычные Dagger-компоненты вне Hilt-графа и управляйте ими вручную; или
- храните сессионное состояние во `@Singleton`/других Hilt-скоупах и явно очищайте его при logout.

`@EntryPoint` в Hilt используется для доступа к уже существующим Hilt-компонентам из типов фреймворка, в которые Hilt не может внедрить зависимости напрямую; он не предназначен для объявления новых скоупов.

## Answer (EN)

Custom scopes in plain Dagger let you control the lifecycle of dependencies beyond standard Android components (`Activity`, `Fragment`), providing state isolation for specific features. Unlike `@Singleton` and Hilt's built-in scopes (such as `@ActivityScoped`), a custom scope in Dagger is implemented via a dedicated scoped component that you create and destroy explicitly.

### Scope Types

**`@Singleton`** in Dagger/Hilt is bound to the root/singleton component. A single instance is shared within that component's lifetime (on Android this is typically one graph per process).

**`@ActivityScoped` / `@FragmentScoped` (Hilt)** are tied to Hilt components (`ActivityComponent`, `FragmentComponent`). Instances are cached for the lifetime of the corresponding component (including its child graph), rather than being strictly defined by `onCreate`/`onDestroy` callbacks.

**Unscoped** dependencies are not cached by the component: for every injection request, a new instance is created (via `@Provides` or `@Inject` constructor), even when requested from a scoped component.

**Custom scope (Dagger)** means you define your own `@Scope` annotation and attach it to a dedicated component. The scope's lifetime equals the lifetime of that component, which you manage explicitly. This is useful for user sessions, feature flows, and other lifecycles that don't map 1:1 to built-in scopes.

### Creating a Custom Scope (Dagger)

```kotlin
// ✅ 1. Define scope annotation
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// ✅ 2. Create component with this scope
@UserSessionScope
@Component(modules = [UserModule::class])
interface UserSessionComponent {
    fun userManager(): UserManager

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance userId: UserId): UserSessionComponent
    }
}

// ✅ 3. Apply scope to dependency
@UserSessionScope
class UserManager @Inject constructor(
    private val userId: UserId,
    private val api: ApiService
)
```

### Lifecycle Management (Dagger)

```kotlin
object UserSessionHolder {
    private var component: UserSessionComponent? = null

    fun login(userId: UserId) {
        // ✅ Create component (and thus the scoped graph) on login
        component = DaggerUserSessionComponent.factory().create(userId)
    }

    fun logout() {
        // ✅ Drop reference to the component; all scoped objects become eligible for GC
        component = null
    }

    fun get(): UserSessionComponent = component ?: error("User not logged in")
}
```

### When to Use a Custom Scope (Dagger)

Create a custom scope when:
- you need a per-user scope (multi-user apps) to isolate state between sessions;
- you need a per-feature-flow scope with heavy dependencies or complex state that should be cleaned when leaving the flow;
- you want isolation between modules/features and want to avoid global singletons leaking data.

Use built-in scopes (Hilt/Dagger) when:
- the dependency lifecycle naturally matches `Activity`/`Fragment`/`ViewModel` lifecycles (Hilt's scopes are usually sufficient);
- you manage simple state that doesn't require its own graph or explicit lifecycle.

### Comparison with Hilt

In **Hilt**, component and scope lifecycles are fixed and managed by the framework. Defining arbitrary new scopes for Hilt-managed components is not supported.

Prefer Hilt's built-in scopes:
- `@Singleton` for app-wide dependencies (SingletonComponent);
- `@ActivityRetainedScoped` for objects surviving configuration changes (`ViewModel`-like);
- `@ActivityScoped` for an `Activity` instance lifetime;
- `@ViewModelScoped` for `ViewModel` lifecycle;
- `@FragmentScoped` for a `Fragment` lifecycle;
- `@ViewScoped` for a `View` lifecycle.

For lifecycles that don't align with these (e.g., a user session):
- either use separate plain Dagger components outside the Hilt graph and manage them explicitly;
- or keep session-like state in Hilt-provided objects (often `@Singleton`) and manually clear that state on logout.

`@EntryPoint` in Hilt is used to access existing Hilt components from framework types that Hilt can't inject into directly; it is not a mechanism for defining new scopes.

## Дополнительные Вопросы (RU)

- Как избежать утечек памяти при использовании кастомных скоупов?
- Может ли один кастомный скоуп зависеть от другого кастомного скоупа?
- Как тестировать зависимости с кастомными скоупами?
- Что произойдёт, если внедрить unscoped-зависимость в скоупленный компонент?
- Как мигрировать от ручного управления синглтонами к кастомным скоупам?

## Follow-ups

- How do you prevent memory leaks with custom scopes?
- Can a custom scope depend on another custom scope?
- How do you test dependencies with custom scopes?
- What happens if you inject an unscoped dependency into a scoped component?
- How do you migrate from manual singleton management to custom scopes?

## Ссылки (RU)

- [[c-dagger]]
- [[c-hilt]]
- [[c-dependency-injection]]
- [Документация по скоупам Dagger](https://dagger.dev/api/latest/dagger/Scope.html)
- [Hilt Components and Scopes](https://dagger.dev/hilt/components.html)

## References

- [[c-dagger]]
- [[c-hilt]]
- [[c-dependency-injection]]
- [Dagger Scopes Documentation](https://dagger.dev/api/latest/dagger/Scope.html)
- [Hilt Components and Scopes](https://dagger.dev/hilt/components.html)

## Связанные Вопросы (RU)

### База (проще)
- [[q-hilt-components-scope--android--medium]] — стандартные скоупы Hilt
- [[c-dependency-injection]] — основы DI
- Базовое понимание компонентов Dagger

### Связанные (тот Же уровень)
- [[q-dagger-component-dependencies--android--hard]] — связи и зависимости компонентов
- [[q-dagger-build-time-optimization--android--medium]] — влияние конфигурации графа и скоупов на сборку

### Продвинутое (сложнее)
- Архитектуры с кастомными скоупами в multi-module проектах
- Паттерны композиции и иерархии скоупов
- Профилирование памяти для скоупленных зависимостей

## Related Questions

### Prerequisites (Easier)
- [[q-hilt-components-scope--android--medium]] — Understanding standard Hilt scopes
- [[c-dependency-injection]] — DI fundamentals
- Basic understanding of Dagger components

### Related (Same Level)
- [[q-dagger-component-dependencies--android--hard]] — Component relationships and dependencies
- [[q-dagger-build-time-optimization--android--medium]] — Build performance with scopes

### Advanced (Harder)
- Multi-module custom scope architectures
- Scope composition patterns and hierarchy
- Memory profiling for scoped dependencies

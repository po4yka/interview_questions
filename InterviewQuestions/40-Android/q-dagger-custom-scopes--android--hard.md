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
status: reviewed
moc: moc-android
related:
  - q-dagger-build-time-optimization--android--medium
  - q-dagger-component-dependencies--android--hard
  - q-hilt-components-scope--android--medium
created: 2025-10-20
updated: 2025-11-02
tags: [android/di-hilt, dagger, dependency-injection, difficulty/hard, hilt]
sources:
  - https://dagger.dev/hilt/components.html
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Sunday, November 2nd 2025, 5:30:46 pm
---

# Вопрос (RU)
> Как создать и использовать кастомные скоупы в Dagger/Hilt? Объясните разницу между Singleton, кастомными скоупами и unscoped зависимостями. Когда и зачем создавать кастомный скоуп?

# Question (EN)
> How do you create and use custom scopes in Dagger/Hilt? Explain the difference between Singleton, custom scopes, and unscoped dependencies. When and why would you create a custom scope?

---

## Ответ (RU)

Кастомные скоупы позволяют управлять жизненным циклом зависимостей за рамками стандартных Android-компонентов (`Activity`, `Fragment`), обеспечивая изоляцию состояния для специфической функциональности. В отличие от `@Singleton` или `@ActivityScoped`, кастомный скоуп создаётся и уничтожается разработчиком явно.

### Типы Скоупов

**`@Singleton`** — единственный экземпляр на всё приложение. Живёт весь жизненный цикл процесса, уничтожается только при завершении приложения.

**`@ActivityScoped` / `@FragmentScoped`** — привязка к Android-компоненту. Экземпляр создаётся с `onCreate` и освобождается с `onDestroy`, разделяется между всеми зависимостями этого компонента.

**Unscoped** — новый объект при каждой инъекции. Не кэшируется компонентом, создаётся каждый раз заново через `@Provides` или конструктор `@Inject`.

**Custom scope** — разработчик полностью контролирует создание и удаление компонента. Полезен для изоляции состояния на уровне фичи или пользовательской сессии.

### Создание Кастомного Скоупа

```kotlin
// ✅ 1. Определяем аннотацию скоупа
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// ✅ 2. Создаём компонент со скоупом
@UserSessionScope
@Component(modules = [UserModule::class])
interface UserSessionComponent {
    fun userManager(): UserManager

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance userId: UserId): UserSessionComponent
    }
}

// ✅ 3. Применяем скоуп к зависимости
@UserSessionScope
class UserManager @Inject constructor(
    private val userId: UserId,
    private val api: ApiService
)
```

### Управление Жизненным Циклом

```kotlin
object UserSessionHolder {
    private var component: UserSessionComponent? = null

    fun login(userId: UserId) {
        // ✅ Создаём компонент (и скоуп) при логине
        component = DaggerUserSessionComponent.factory().create(userId)
    }

    fun logout() {
        // ✅ Компонент удаляется → все зависимости теряют ссылки → GC
        component = null
    }

    fun get(): UserSessionComponent = component ?: error("User not logged in")
}
```

### Когда Использовать

**Создавайте кастомный скоуп для:**
- Мультипользовательских приложений (скоуп на пользователя) — изоляция состояния между сессиями
- Feature-флоу с тяжёлыми зависимостями (скоуп на фичу) — очистка ресурсов при выходе из фичи
- Изоляции состояния между модулями — предотвращение утечек данных между независимыми фичами

**Используйте стандартные скоупы для:**
- Зависимостей, совпадающих с жизненным циклом `Activity`/`Fragment` — стандартные Hilt-скоупы покрывают большинство случаев
- Простого state без кросс-экранной логики — нет необходимости в явном управлении жизненным циклом

### Сравнение С Hilt

В **Hilt** кастомные скоупы ограничены, т.к. граф зависимостей управляется автоматически. Можно создавать через `@EntryPoint`, но проще использовать встроенные:
- `@Singleton` — весь жизненный цикл приложения
- `@ActivityRetainedScoped` — переживает изменения конфигурации (`ViewModel`-уровень)
- `@ActivityScoped` — до `onDestroy()` Activity
- `@ViewModelScoped` — привязан к `ViewModel`
- `@FragmentScoped` — до `onDestroy()` Fragment
- `@ViewScoped` — до уничтожения View

Для произвольных скоупов (например, сессия пользователя) нужен чистый Dagger-компонент вне Hilt-графа или интеграция через `@EntryPoint`.

## Answer (EN)

Custom scopes enable lifecycle management beyond standard Android components (`Activity`, `Fragment`), providing state isolation for specific functionality. Unlike `@Singleton` or `@ActivityScoped`, a custom scope is created and destroyed explicitly by the developer.

### Scope Types

**`@Singleton`** — single instance for entire application. Lives for process lifetime, destroyed only on app termination.

**`@ActivityScoped` / `@FragmentScoped`** — tied to Android component. Instance created on `onCreate` and released on `onDestroy`, shared across all dependencies of this component.

**Unscoped** — new object on each injection. Not cached by component, recreated every time via `@Provides` or `@Inject` constructor.

**Custom scope** — developer fully controls component creation and destruction. Useful for state isolation at feature or user session level.

### Creating Custom Scope

```kotlin
// ✅ 1. Define scope annotation
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// ✅ 2. Create component with scope
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

### Lifecycle Management

```kotlin
object UserSessionHolder {
    private var component: UserSessionComponent? = null

    fun login(userId: UserId) {
        // ✅ Create component (and scope) on login
        component = DaggerUserSessionComponent.factory().create(userId)
    }

    fun logout() {
        // ✅ Component removed → all dependencies lose references → GC
        component = null
    }

    fun get(): UserSessionComponent = component ?: error("User not logged in")
}
```

### When to Use

**Create custom scope for:**
- Multi-user applications (scope per user) — isolate state between sessions
- Feature flows with heavy dependencies (scope per feature) — cleanup resources on feature exit
- State isolation between modules — prevent data leaks between independent features

**Use standard scopes for:**
- Dependencies matching `Activity`/`Fragment` lifecycle — standard Hilt scopes cover most cases
- Simple state without cross-screen logic — no need for explicit lifecycle management

### Comparison with Hilt

**Hilt** limits custom scopes since the dependency graph is managed automatically. You can create via `@EntryPoint`, but built-in scopes are simpler:
- `@Singleton` — entire application lifetime
- `@ActivityRetainedScoped` — survives configuration changes (`ViewModel` level)
- `@ActivityScoped` — until `onDestroy()` of Activity
- `@ViewModelScoped` — tied to `ViewModel`
- `@FragmentScoped` — until `onDestroy()` of Fragment
- `@ViewScoped` — until View destruction

For arbitrary scopes (e.g., user session), use pure Dagger components outside Hilt graph or integrate via `@EntryPoint`.

---

## Follow-ups

- How do you prevent memory leaks with custom scopes?
- Can a custom scope depend on another custom scope?
- How do you test dependencies with custom scopes?
- What happens if you inject an unscoped dependency into a scoped component?
- How do you migrate from manual singleton management to custom scopes?

## References

- [[c-dagger]]
- [[c-hilt]]
- [[c-dependency-injection]]
- [Dagger Scopes Documentation](https://dagger.dev/api/latest/dagger/Scope.html)
- [Hilt Components and Scopes](https://dagger.dev/hilt/components.html)

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

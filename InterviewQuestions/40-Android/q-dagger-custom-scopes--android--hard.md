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
  - q-dagger-build-time-optimization--android--medium
  - q-dagger-component-dependencies--android--hard
  - q-hilt-components-scope--android--medium
created: 2025-10-20
updated: 2025-10-30
tags: [android/di-hilt, difficulty/hard, dependency-injection, dagger, hilt]
sources:
  - https://dagger.dev/hilt/components.html
date created: Thursday, October 30th 2025, 12:02:34 pm
date modified: Thursday, October 30th 2025, 12:47:13 pm
---

# Вопрос (RU)
> Как создать и использовать кастомные скоупы в Dagger/Hilt? Объясните разницу между Singleton, кастомными скоупами и unscoped зависимостями. Когда и зачем создавать кастомный скоуп?

# Question (EN)
> How do you create and use custom scopes in Dagger/Hilt? Explain the difference between Singleton, custom scopes, and unscoped dependencies. When and why would you create a custom scope?

---

## Ответ (RU)

Кастомные скоупы позволяют управлять жизненным циклом зависимостей за рамками стандартных Android-компонентов, обеспечивая изоляцию состояния для специфической функциональности.

### Типы Скоупов

**@Singleton** — единственный экземпляр на всё приложение. Живёт весь жизненный цикл процесса.

**@ActivityScoped / @FragmentScoped** — привязка к Android-компоненту. Экземпляр освобождается с onDestroy.

**Unscoped** — новый объект при каждой инъекции. Не кэшируется компонентом.

**Custom scope** — разработчик контролирует создание и удаление компонента.

### Создание Кастомного Скоупа

```kotlin
// ✅ Определяем аннотацию
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// ✅ Создаём компонент
@UserSessionScope
@Component(modules = [UserModule::class])
interface UserSessionComponent {
    fun userManager(): UserManager

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance userId: UserId): UserSessionComponent
    }
}

// ✅ Используем скоуп
@UserSessionScope
class UserManager @Inject constructor(
    private val userId: UserId,
    private val api: ApiService
) {
    // Единственный экземпляр для этого UserSessionComponent
}
```

### Управление Жизненным Циклом

```kotlin
object UserSessionHolder {
    private var component: UserSessionComponent? = null

    fun login(userId: UserId) {
        // ✅ Создаём скоуп при логине
        component = DaggerUserSessionComponent.factory()
            .create(userId)
    }

    fun logout() {
        // ✅ Скоуп освобождается, зависимости GC'атся
        component = null
    }

    fun get(): UserSessionComponent =
        component ?: error("User not logged in")
}
```

### Когда Использовать

**Создавайте кастомный скоуп для:**
- Мультипользовательских приложений (скоуп на пользователя)
- Feature-флоу с тяжёлыми зависимостями (скоуп на фичу)
- Изоляции состояния между модулями

**Используйте стандартные скоупы для:**
- Зависимостей, совпадающих с жизненным циклом Activity/Fragment
- Простого state без кросс-экранной логики

### Сравнение с Hilt

В Hilt кастомные скоупы ограничены. Можно создавать через `@EntryPoint`, но проще использовать встроенные:
- `@Singleton`, `@ActivityRetainedScoped`, `@ActivityScoped`, `@ViewModelScoped`, `@FragmentScoped`, `@ViewScoped`

Для произвольных скоупов нужен чистый Dagger-компонент вне Hilt-графа.

## Answer (EN)

Custom scopes enable lifecycle management beyond standard Android components, providing state isolation for specific functionality.

### Scope Types

**@Singleton** — single instance for entire application. Lives for process lifetime.

**@ActivityScoped / @FragmentScoped** — tied to Android component. Instance released on onDestroy.

**Unscoped** — new object on each injection. Not cached by component.

**Custom scope** — developer controls component creation and destruction.

### Creating Custom Scope

```kotlin
// ✅ Define annotation
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// ✅ Create component
@UserSessionScope
@Component(modules = [UserModule::class])
interface UserSessionComponent {
    fun userManager(): UserManager

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance userId: UserId): UserSessionComponent
    }
}

// ✅ Apply scope
@UserSessionScope
class UserManager @Inject constructor(
    private val userId: UserId,
    private val api: ApiService
) {
    // Single instance for this UserSessionComponent
}
```

### Lifecycle Management

```kotlin
object UserSessionHolder {
    private var component: UserSessionComponent? = null

    fun login(userId: UserId) {
        // ✅ Create scope on login
        component = DaggerUserSessionComponent.factory()
            .create(userId)
    }

    fun logout() {
        // ✅ Scope released, dependencies garbage collected
        component = null
    }

    fun get(): UserSessionComponent =
        component ?: error("User not logged in")
}
```

### When to Use

**Create custom scope for:**
- Multi-user applications (scope per user)
- Feature flows with heavy dependencies (scope per feature)
- State isolation between modules

**Use standard scopes for:**
- Dependencies matching Activity/Fragment lifecycle
- Simple state without cross-screen logic

### Comparison with Hilt

Hilt limits custom scopes. You can create via `@EntryPoint`, but built-in scopes are simpler:
- `@Singleton`, `@ActivityRetainedScoped`, `@ActivityScoped`, `@ViewModelScoped`, `@FragmentScoped`, `@ViewScoped`

For arbitrary scopes, use pure Dagger components outside Hilt graph.

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

### Prerequisites
- [[q-hilt-components-scope--android--medium]] - Understanding standard Hilt scopes
- [[c-dependency-injection]] - DI fundamentals

### Related
- [[q-dagger-component-dependencies--android--hard]] - Component relationships
- [[q-dagger-build-time-optimization--android--medium]] - Build performance with scopes

### Advanced
- Multi-module custom scope architectures
- Scope composition patterns
- Memory profiling for scoped dependencies

---
id: 20251020-200000
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
updated: 2025-10-20
tags: [android/di-hilt, difficulty/hard]
sources:
  - https://dagger.dev/hilt/components.html
---
# Вопрос (RU)
> Как создать и использовать кастомные скоупы в Dagger/Hilt? Объясните разницу между Singleton, кастомными скоупами и unscoped зависимостями. Приведите примеры когда и зачем создавать кастомный скоуп.

# Question (EN)
> How do you create and use custom scopes in Dagger/Hilt? Explain the difference between Singleton, custom scopes, and unscoped dependencies. Provide examples of when and why you'd create a custom scope.

## Ответ (RU)

Кастомные скоупы позволяют создавать зависимости с определенным жизненным циклом для конкретной функциональности.

### Стандартные vs Кастомные Скоупы

**Жизненный цикл:**
- **@Singleton** - один экземпляр на приложение
- **@ActivityScoped** - один экземпляр на Activity
- **@FragmentScoped** - один экземпляр на Fragment
- **Unscoped** - новый экземпляр при каждом запросе
- **Custom** - определяется разработчиком

### Создание Кастомного Скоупа

**Определение:**
```kotlin
// ✅ Определяем аннотацию скоупа
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// ✅ Создаем компонент со скоупом
@UserSessionScope
@Component(
    dependencies = [SingletonComponent::class],
    modules = [UserSessionModule::class]
)
interface UserSessionComponent {
    fun inject(activity: UserActivity)

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance session: UserSession): UserSessionComponent
    }
}

// ✅ Используем скоуп для зависимостей
@UserSessionScope
class UserSessionManager @Inject constructor(
    private val apiService: ApiService,
    private val session: UserSession
) {
    fun logout() { /* ... */ }
}
```

### Примеры Применения

**User Session Scope (изоляция по пользователю):**
```kotlin
// ✅ Состояние живет пока пользователь авторизован
@UserSessionScope
class UserPreferences @Inject constructor() {
    var theme: String = "light"
}

@UserSessionScope
class UserApiClient @Inject constructor(
    private val token: String
) { /* ... */ }
```

**Feature Scope (изоляция по фиче):**
```kotlin
// ✅ Состояние живет на протяжении работы фичи
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureScope

@FeatureScope
class FeatureStateManager @Inject constructor() {
    var currentStep: Int = 0
}
```

### Управление Жизненным Циклом

```kotlin
class UserActivity : AppCompatActivity() {
    private lateinit var component: UserSessionComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ✅ Создаем скоуп при входе пользователя
        component = DaggerUserSessionComponent.factory()
            .create(userSession)
    }

    override fun onDestroy() {
        super.onDestroy()
        // ✅ Компонент и зависимости освобождаются автоматически
    }
}
```

### Когда Использовать

**Создавайте кастомный скоуп:**
- Жизненный цикл отличается от стандартных
- Нужна изоляция состояния между пользователями/фичами
- Требуется кэширование на уровне функциональности

**Используйте стандартные скоупы:**
- Жизненный цикл совпадает с Activity/Fragment/App
- Простые зависимости без сложного состояния

## Answer (EN)

Custom scopes allow creating dependencies with specific lifecycles for particular functionality using [[c-dagger]]/[[c-hilt]] [[c-dependency-injection]].

### Standard vs Custom Scopes

**Lifecycle:**
- **@Singleton** - one instance for entire application
- **@ActivityScoped** - one instance per Activity
- **@FragmentScoped** - one instance per Fragment
- **Unscoped** - new instance on each request
- **Custom** - developer-defined

### Creating Custom Scope

**Definition:**
```kotlin
// ✅ Define scope annotation
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope

// ✅ Create scoped component
@UserSessionScope
@Component(
    dependencies = [SingletonComponent::class],
    modules = [UserSessionModule::class]
)
interface UserSessionComponent {
    fun inject(activity: UserActivity)

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance session: UserSession): UserSessionComponent
    }
}

// ✅ Use scope for dependencies
@UserSessionScope
class UserSessionManager @Inject constructor(
    private val apiService: ApiService,
    private val session: UserSession
) {
    fun logout() { /* ... */ }
}
```

### Use Cases

**User Session Scope (user isolation):**
```kotlin
// ✅ State lives while user is authenticated
@UserSessionScope
class UserPreferences @Inject constructor() {
    var theme: String = "light"
}

@UserSessionScope
class UserApiClient @Inject constructor(
    private val token: String
) { /* ... */ }
```

**Feature Scope (feature isolation):**
```kotlin
// ✅ State lives during feature usage
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureScope

@FeatureScope
class FeatureStateManager @Inject constructor() {
    var currentStep: Int = 0
}
```

### Lifecycle Management

```kotlin
class UserActivity : AppCompatActivity() {
    private lateinit var component: UserSessionComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ✅ Create scope on user login
        component = DaggerUserSessionComponent.factory()
            .create(userSession)
    }

    override fun onDestroy() {
        super.onDestroy()
        // ✅ Component and dependencies released automatically
    }
}
```

### When to Use

**Create custom scope when:**
- Lifecycle differs from standard scopes
- Need state isolation between users/features
- Require feature-level caching

**Use standard scopes when:**
- Lifecycle matches Activity/Fragment/App
- Simple dependencies without complex state

## Follow-ups

- How do you handle scope lifecycle in multi-user applications?
- What are the performance implications of custom scopes?
- How do you test custom scope dependencies?

## References

- [Hilt Components and Scopes](https://dagger.dev/hilt/components.html)
- [Dagger Scopes Documentation](https://dagger.dev/api/latest/dagger/Scope.html)

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-build-time-optimization--android--medium]]

### Related (Same Level)
- [[q-hilt-components-scope--android--medium]]

### Advanced (Harder)
- [[q-dagger-component-dependencies--android--hard]]

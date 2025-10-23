---
id: 20251020-200000
title: Dagger Custom Scopes / Кастомные скоупы Dagger
aliases:
- Dagger Custom Scopes
- Кастомные скоупы Dagger
topic: android
subtopics:
- dependency-injection
- architecture-patterns
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-dagger-component-dependencies--di--hard
- q-hilt-components-scope--android--medium
- q-dagger-build-time-optimization--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/dependency-injection
- android/architecture-patterns
- dagger
- hilt
- custom-scopes
- lifecycle-management
- difficulty/hard
source: https://dagger.dev/hilt/components.html
source_note: Hilt components and scopes documentation
---# Вопрос (RU)
> Как создать и использовать кастомные скоупы в Dagger/Hilt? Объясните разницу между Singleton, кастомными скоупами и unscoped зависимостями. Приведите примеры когда и зачем создавать кастомный скоуп.

# Question (EN)
> How do you create and use custom scopes in Dagger/Hilt? Explain the difference between Singleton, custom scopes, and unscoped dependencies. Provide examples of when and why you'd create a custom scope.

## Ответ (RU)

Скоупы в Dagger/Hilt контролируют жизненный цикл и совместное использование зависимостей. Кастомные скоупы позволяют создавать зависимости с определенным жизненным циклом для конкретной функциональности или бизнес-процесса.

### Теория: Управление жизненным циклом

**Принципы скоупов:**
- Скоуп определяет область видимости и время жизни зависимости
- Один экземпляр на экземпляр скоупа
- Скоупы создают границы изоляции между компонентами
- Кастомные скоупы расширяют стандартные возможности

**Жизненный цикл зависимостей:**
- **@Singleton** - один экземпляр на всё приложение
- **@ActivityScoped** - один экземпляр на Activity
- **@FragmentScoped** - один экземпляр на Fragment
- **Unscoped** - новый экземпляр при каждом запросе

### Стандартные скоупы Hilt

| Компонент | Скоуп | Создается | Уничтожается | Использование |
|-----------|-------|-----------|--------------|---------------|
| SingletonComponent | @Singleton | Application.onCreate() | App destroyed | Глобальные синглтоны |
| ActivityRetainedComponent | @ActivityRetainedScoped | Activity created | Activity destroyed | ViewModels |
| ActivityComponent | @ActivityScoped | Activity created | Activity destroyed | Activity зависимости |
| FragmentComponent | @FragmentScoped | Fragment created | Fragment destroyed | Fragment зависимости |

### Создание кастомного скоупа

**1. Определение скоупа:**
```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope
```

**2. Создание компонента:**
```kotlin
@UserSessionScope
@Component(
    dependencies = [SingletonComponent::class],
    modules = [UserSessionModule::class]
)
interface UserSessionComponent {
    fun inject(activity: UserActivity)

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance userSession: UserSession): UserSessionComponent
    }
}
```

**3. Использование скоупа:**
```kotlin
@UserSessionScope
class UserSessionManager @Inject constructor(
    private val apiService: ApiService,
    private val userSession: UserSession
) {
    fun logout() {
        // Логика выхода из системы
    }
}
```

### Примеры использования кастомных скоупов

**User Session Scope:**
```kotlin
// Зависимости живут пока пользователь авторизован
@UserSessionScope
class UserPreferences @Inject constructor() {
    var currentTheme: String = "light"
}

@UserSessionScope
class UserApiClient @Inject constructor(
    private val userToken: String
) {
    // API клиент с токеном пользователя
}
```

**Feature Scope:**
```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureScope

@FeatureScope
class FeatureStateManager @Inject constructor() {
    var currentStep: Int = 0
    var isCompleted: Boolean = false
}
```

### Когда создавать кастомные скоупы

**Создавайте кастомный скоуп когда:**
- Нужен жизненный цикл отличный от стандартных
- Требуется изоляция состояния между пользователями
- Необходимо управление ресурсами по бизнес-логике
- Нужно кэширование на уровне функциональности

**Не создавайте кастомный скоуп когда:**
- Стандартные скоупы покрывают потребности
- Нет необходимости в изоляции состояния
- Простые зависимости без сложного жизненного цикла

### Управление жизненным циклом

**Создание скоупа:**
```kotlin
class UserActivity : AppCompatActivity() {
    private lateinit var userSessionComponent: UserSessionComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        userSessionComponent = DaggerUserSessionComponent.factory()
            .create(userSession)
    }
}
```

**Уничтожение скоупа:**
```kotlin
override fun onDestroy() {
    super.onDestroy()
    // Компонент автоматически уничтожается
    // Все @UserSessionScope зависимости освобождаются
}
```

### Лучшие практики

**Архитектурные принципы:**
- Используйте минимально необходимый скоуп
- Избегайте глубоких иерархий скоупов
- Документируйте жизненный цикл скоупа

**Производительность:**
- Кастомные скоупы увеличивают сложность
- Правильное управление памятью
- Избегайте утечек памяти

**Тестирование:**
- Создавайте тестовые компоненты
- Используйте моки для скоупов
- Тестируйте жизненные циклы

## Answer (EN)

Scopes in Dagger/Hilt control the lifecycle and sharing of dependencies. Custom scopes allow you to create dependencies with specific lifecycles for particular functionality or business processes.

### Theory: Lifecycle Management

**Scope Principles:**
- Scope defines dependency visibility and lifetime
- One instance per scope instance
- Scopes create isolation boundaries between components
- Custom scopes extend standard capabilities

**Dependency Lifecycle:**
- **@Singleton** - one instance for entire application
- **@ActivityScoped** - one instance per Activity
- **@FragmentScoped** - one instance per Fragment
- **Unscoped** - new instance on each request

### Standard Hilt Scopes

| Component | Scope | Created | Destroyed | Usage |
|-----------|-------|---------|-----------|-------|
| SingletonComponent | @Singleton | Application.onCreate() | App destroyed | Global singletons |
| ActivityRetainedComponent | @ActivityRetainedScoped | Activity created | Activity destroyed | ViewModels |
| ActivityComponent | @ActivityScoped | Activity created | Activity destroyed | Activity dependencies |
| FragmentComponent | @FragmentScoped | Fragment created | Fragment destroyed | Fragment dependencies |

### Creating Custom Scope

**1. Define scope:**
```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserSessionScope
```

**2. Create component:**
```kotlin
@UserSessionScope
@Component(
    dependencies = [SingletonComponent::class],
    modules = [UserSessionModule::class]
)
interface UserSessionComponent {
    fun inject(activity: UserActivity)

    @Component.Factory
    interface Factory {
        fun create(@BindsInstance userSession: UserSession): UserSessionComponent
    }
}
```

**3. Use scope:**
```kotlin
@UserSessionScope
class UserSessionManager @Inject constructor(
    private val apiService: ApiService,
    private val userSession: UserSession
) {
    fun logout() {
        // Logout logic
    }
}
```

### Custom Scope Examples

**User Session Scope:**
```kotlin
// Dependencies live while user is authenticated
@UserSessionScope
class UserPreferences @Inject constructor() {
    var currentTheme: String = "light"
}

@UserSessionScope
class UserApiClient @Inject constructor(
    private val userToken: String
) {
    // API client with user token
}
```

**Feature Scope:**
```kotlin
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class FeatureScope

@FeatureScope
class FeatureStateManager @Inject constructor() {
    var currentStep: Int = 0
    var isCompleted: Boolean = false
}
```

### When to Create Custom Scopes

**Create custom scope when:**
- Need lifecycle different from standard scopes
- Require state isolation between users
- Need resource management by business logic
- Need feature-level caching

**Don't create custom scope when:**
- Standard scopes cover requirements
- No need for state isolation
- Simple dependencies without complex lifecycle

### Lifecycle Management

**Creating scope:**
```kotlin
class UserActivity : AppCompatActivity() {
    private lateinit var userSessionComponent: UserSessionComponent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        userSessionComponent = DaggerUserSessionComponent.factory()
            .create(userSession)
    }
}
```

**Destroying scope:**
```kotlin
override fun onDestroy() {
    super.onDestroy()
    // Component automatically destroyed
    // All @UserSessionScope dependencies released
}
```

### Best Practices

**Architectural Principles:**
- Use minimal necessary scope
- Avoid deep scope hierarchies
- Document scope lifecycle

**Performance:**
- Custom scopes increase complexity
- Proper memory management
- Avoid memory leaks

**Testing:**
- Create test components
- Use mocks for scopes
- Test lifecycles

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

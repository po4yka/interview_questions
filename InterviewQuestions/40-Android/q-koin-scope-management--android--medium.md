---
id: android-203
title: Koin Scope Management / Управление Scope В Koin
aliases:
- Koin Scope Management
- Koin Scopes
- Жизненный цикл Koin
- Управление Scope В Koin
topic: android
subtopics:
- architecture-mvvm
- di-koin
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
- c-dependency-injection
- q-how-to-display-snackbar-or-toast-based-on-results--android--medium
- q-stable-classes-compose--android--hard
- q-what-methods-redraw-views--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/architecture-mvvm
- android/di-koin
- android/lifecycle
- dependency-injection
- difficulty/medium
- koin
- scopes

---

# Вопрос (RU)

> Как управлять scope в Koin? Реализуйте зависимости с ограниченным временем жизни для `Activity` и `Fragment` с правильной обработкой жизненного цикла.

# Question (EN)

> How do you manage scopes in Koin? Implement `Activity` and `Fragment` scoped dependencies with proper lifecycle handling.

---

## Ответ (RU)

**Scope в Koin** — это контейнеры для зависимостей с ограниченным временем жизни, которые можно привязать к Android-компонентам (`Activity`, `Fragment`) или пользовательским логическим границам. Они помогают избежать утечек памяти и делают поведение зависимостей согласованным с жизненным циклом.

Важно: Koin не "угадывает" жизненный цикл — вы создаёте и закрываете scope явно или через привязку к владельцу жизненного цикла (`LifecycleOwner`). Примеры ниже показывают типичный паттерн для Koin 3.x с Android.

### Основные Концепции

**Типы Scope**:
1. **`Application` / Root Scope** — `single { ... }`, живёт столько, сколько живёт Koin application context.
2. **Component Scope** — scope, явно создаваемый для `Activity`/`Fragment` и закрываемый при их уничтожении.
3. **Named Scope** — scope с qualifier-ом (`named("...")`) для пользовательских логических границ (сессия, фича и т.п.).

**Преимущества**:
- Контролируемая очистка ресурсов.
- Снижение риска утечек памяти.
- Соответствие жизненному циклу компонентов при корректном создании/закрытии scope.

### `Activity` Scoped Dependencies

```kotlin
// ✅ Определение модуля с Activity scope (по классу как qualifier)
val shoppingModule = module {
    // Зависимость уровня приложения
    single<ProductRepository> { ProductRepositoryImpl(get()) }

    // Scope, который будем использовать для ShoppingActivity
    scope<ShoppingActivity> {
        scoped { ShoppingCart() }
        scoped { ShoppingCartManager(get(), get()) }
        scoped { PaymentProcessor(get()) }
    }
}

// ✅ Activity с явным управлением scope
class ShoppingActivity : AppCompatActivity() {

    // Создаём scope при создании Activity.
    // В реальном проекте используйте стабильно формируемый scopeId
    // (например, сохранённый в savedInstanceState), здесь — упрощённо.
    private val activityScope: Scope by lazy {
        getKoin().createScope(
            scopeId = "ShoppingActivity_${hashCode()}",
            qualifier = named<ShoppingActivity>()
        )
    }

    private val cartManager: ShoppingCartManager by activityScope.inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Scope создан лениво при первом обращении к activityScope
    }

    override fun onDestroy() {
        // Явно закрываем scope, чтобы очистить scoped-зависимости
        activityScope.close()
        super.onDestroy()
    }
}
```

**Объяснение**:
- `scope<ShoppingActivity> { ... }` в модуле описывает, какие зависимости доступны в scope, связанном с этим qualifier-ом.
- `createScope(scopeId, qualifier)` создаёт новый экземпляр scope.
- `scoped` создаёт один экземпляр на scope.
- При `close()` все scoped-зависимости освобождаются; вы решаете, когда звать `close()` (обычно в `onDestroy`).

### `Fragment` Scoped Dependencies

```kotlin
// ✅ Модуль с Fragment scope
val profileModule = module {
    scope<ProfileFragment> {
        scoped { (userId: String) ->
            UserProfileLoader(userId, get())
        }
        scoped { ProfileEditState() }
    }
}

// ✅ Fragment с scoped зависимостями
class ProfileFragment : Fragment() {

    private val fragmentScope: Scope by lazy {
        getKoin().createScope(
            scopeId = "ProfileFragment_${hashCode()}",
            qualifier = named<ProfileFragment>()
        )
    }

    private val userId: String by lazy {
        requireArguments().getString("user_id")!!
    }

    private val profileLoader: UserProfileLoader by fragmentScope.inject {
        parametersOf(userId)
    }

    private val editState: ProfileEditState by fragmentScope.inject()

    override fun onDestroy() {
        // Закрываем scope, когда Fragment полностью уничтожается,
        // чтобы избежать утечек и сохранить согласованный жизненный цикл.
        fragmentScope.close()
        super.onDestroy()
    }
}
```

**Ключевые моменты**:
- `scope<ProfileFragment> { ... }` описывает зависимости для соответствующего scope.
- `parametersOf()` передаёт runtime-параметры в scoped-определения.
- Важно закрывать scope в момент, когда `Fragment` больше не нужен (обычно `onDestroy()`), а не только `onDestroyView()`, если требуется жить вместе с самим `Fragment`.

### Разделение Scope Между Компонентами

Один и тот же scope можно использовать для `Activity` и её `Fragment`-ов, чтобы шарить состояние:

```kotlin
// ✅ Activity создаёт shared scope
class MainActivity : AppCompatActivity() {

    val activityScope: Scope by lazy {
        getKoin().createScope(
            scopeId = "MainActivity_${hashCode()}",
            qualifier = named<MainActivity>()
        )
    }

    val sharedViewModel: SharedViewModel by activityScope.inject()

    override fun onDestroy() {
        activityScope.close()
        super.onDestroy()
    }
}

// ✅ Fragment получает доступ к scope Activity
class HomeFragment : Fragment() {

    private val activityScope: Scope
        get() = (requireActivity() as MainActivity).activityScope

    private val sharedViewModel: SharedViewModel by activityScope.inject()
}
```

**Комментарий**:
- Используем явный и стабильный способ получения `Activity` scope, без недетерминированных `toString()`.
- Пока `Activity` жива, её scope доступен всем дочерним `Fragment`-ам.

### Custom Named Scopes

```kotlin
// ✅ Feature-based scope
val featureModule = module {
    scope(named("user_session")) {
        scoped { UserSession(get()) }
        scoped { AuthenticatedApiClient(get()) }
    }
}

// ✅ Ручное управление custom scope
class SessionManager(private val koin: Koin) {

    private var sessionScope: Scope? = null

    fun startSession(userId: String) {
        sessionScope = koin.createScope(
            scopeId = "session_$userId",
            qualifier = named("user_session")
        )
    }

    fun getSessionScope(): Scope {
        return sessionScope
            ?: throw IllegalStateException("Session scope is not started")
    }

    fun endSession() {
        sessionScope?.close()
        sessionScope = null
    }
}
```

**Ключевые моменты**:
- Используйте стабильно формируемые `scopeId`, чтобы однозначно находить scope.
- Named scopes не закрываются автоматически — вы обязаны вызывать `close()` в нужный момент.

### Сравнение Подходов

| Подход | Использование | Автоматическая очистка |
|--------|---------------|------------------------|
| `Application` / `single` | Глобальные зависимости | Пока живёт Koin app context |
| Component scope (`Activity`/`Fragment`) | Привязка к жизненному циклу компонента через явное создание/close | Да, если корректно закрываете в onDestroy |
| Named scope | Пользовательская логика (сессия, фича) | Нет, требуется ручное управление |

### Best Practices

1. **Соответствие жизненному циклу**: Создавайте/закрывайте scopes в колбеках жизненного цикла (`onCreate`/`onDestroy`, `onStart`/`onStop`) или через lifecycle-aware обёртки.
2. **Избегать утечек**: Всегда явно закрывайте custom scopes (session, feature) при завершении их жизненного цикла.
3. **Shared state**: Используйте один scope для `Activity` и её `Fragment`-ов, чтобы безопасно делиться состоянием (`ViewModel`, стейт).
4. **Lazy injection**: Предпочитайте `by inject()` и ленивые делегаты, чтобы избегать преждевременного создания зависимостей.

---

## Answer (EN)

Koin Scopes provide lifecycle-aware dependency management by creating containers for dependencies with limited lifetimes that you explicitly tie to Android components (`Activity`, `Fragment`) or custom logical boundaries. They help avoid memory leaks and keep dependency lifetimes aligned with owners.

Important: Koin does not automatically infer Android lifecycle. You create and close scopes explicitly or via lifecycle-aware bindings. The examples below illustrate typical patterns for Koin 3.x with Android.

### Core Concepts

**Scope Types**:
1. **`Application` / Root Scope** – `single { ... }`, lives as long as the Koin application context.
2. **Component Scope** – scope explicitly created for an `Activity`/`Fragment` and closed when that component is destroyed.
3. **Named Scope** – scope with a qualifier (`named("..."`) for custom logical boundaries (session, feature, etc.).

**Benefits**:
- Controlled resource cleanup.
- Reduced risk of memory leaks.
- Lifecycle alignment when scopes are created/closed correctly.

### `Activity` Scoped Dependencies

```kotlin
// ✅ Module with Activity scope (using class as qualifier)
val shoppingModule = module {
    // Application-wide dependency
    single<ProductRepository> { ProductRepositoryImpl(get()) }

    // Scope definition for ShoppingActivity
    scope<ShoppingActivity> {
        scoped { ShoppingCart() }
        scoped { ShoppingCartManager(get(), get()) }
        scoped { PaymentProcessor(get()) }
    }
}

// ✅ Activity with explicit scope management
class ShoppingActivity : AppCompatActivity() {

    // Create scope when Activity is created.
    // In production, use a stable scopeId (e.g., saved in savedInstanceState).
    private val activityScope: Scope by lazy {
        getKoin().createScope(
            scopeId = "ShoppingActivity_${hashCode()}",
            qualifier = named<ShoppingActivity>()
        )
    }

    private val cartManager: ShoppingCartManager by activityScope.inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Scope is created lazily on first access
    }

    override fun onDestroy() {
        // Explicitly close the scope to release scoped dependencies
        activityScope.close()
        super.onDestroy()
    }
}
```

**Explanation**:
- `scope<ShoppingActivity> { ... }` in the module declares which dependencies exist in that qualified scope.
- `createScope(scopeId, qualifier)` creates a new scope instance.
- `scoped` provides one instance per scope.
- Calling `close()` releases scoped dependencies; you decide when (typically in `onDestroy`).

### `Fragment` Scoped Dependencies

```kotlin
// ✅ Module with Fragment scope
val profileModule = module {
    scope<ProfileFragment> {
        scoped { (userId: String) ->
            UserProfileLoader(userId, get())
        }
        scoped { ProfileEditState() }
    }
}

// ✅ Fragment with scoped dependencies
class ProfileFragment : Fragment() {

    private val fragmentScope: Scope by lazy {
        getKoin().createScope(
            scopeId = "ProfileFragment_${hashCode()}",
            qualifier = named<ProfileFragment>()
        )
    }

    private val userId: String by lazy {
        requireArguments().getString("user_id")!!
    }

    private val profileLoader: UserProfileLoader by fragmentScope.inject {
        parametersOf(userId)
    }

    private val editState: ProfileEditState by fragmentScope.inject()

    override fun onDestroy() {
        // Close scope when Fragment is fully destroyed
        fragmentScope.close()
        super.onDestroy()
    }
}
```

**Key Points**:
- `scope<ProfileFragment> { ... }` declares dependencies for the `Fragment` scope.
- `parametersOf()` passes runtime parameters to scoped definitions.
- Close the scope when the `Fragment` is no longer needed (commonly `onDestroy()`), not merely on `onDestroyView()` if the `Fragment` instance continues to live.

### Sharing Scopes Between Components

You can share a single scope between an `Activity` and its Fragments to share state:

```kotlin
// ✅ Activity creates shared scope
class MainActivity : AppCompatActivity() {

    val activityScope: Scope by lazy {
        getKoin().createScope(
            scopeId = "MainActivity_${hashCode()}",
            qualifier = named<MainActivity>()
        )
    }

    val sharedViewModel: SharedViewModel by activityScope.inject()

    override fun onDestroy() {
        activityScope.close()
        super.onDestroy()
    }
}

// ✅ Fragment accesses Activity scope
class HomeFragment : Fragment() {

    private val activityScope: Scope
        get() = (requireActivity() as MainActivity).activityScope

    private val sharedViewModel: SharedViewModel by activityScope.inject()
}
```

**Notes**:
- Use an explicit, stable way to obtain the `Activity` scope rather than relying on `toString()` or other non-deterministic IDs.
- As long as the `Activity` lives, its scope is available to child Fragments.

### Custom Named Scopes

```kotlin
// ✅ Feature-based scope
val featureModule = module {
    scope(named("user_session")) {
        scoped { UserSession(get()) }
        scoped { AuthenticatedApiClient(get()) }
    }
}

// ✅ Manual custom scope management
class SessionManager(private val koin: Koin) {

    private var sessionScope: Scope? = null

    fun startSession(userId: String) {
        sessionScope = koin.createScope(
            scopeId = "session_$userId",
            qualifier = named("user_session")
        )
    }

    fun getSessionScope(): Scope {
        return sessionScope
            ?: throw IllegalStateException("Session scope is not started")
    }

    fun endSession() {
        sessionScope?.close()
        sessionScope = null
    }
}
```

**Key Points**:
- Use stable `scopeId` values so you can reliably retrieve the scope.
- Named scopes are not closed automatically; you must call `close()` at the appropriate lifecycle boundary.

### Comparison of Approaches

| Approach | Use Case | Automatic Cleanup |
|----------|----------|-------------------|
| `Application` / `single` | Global dependencies | While Koin app context is alive |
| Component scope (`Activity`/`Fragment`) | Tied to component lifecycle via explicit create/close | Yes, if you close in `onDestroy` |
| Named scope | Custom logical boundaries (session/feature) | No, manual management required |

### Best Practices

1. **Match lifecycle**: Create/close scopes in lifecycle callbacks (`onCreate`/`onDestroy`, etc.) or via lifecycle-aware helpers.
2. **Prevent leaks**: Always close custom/named scopes when their logical lifetime ends.
3. **Shared state**: Use a shared `Activity` scope to share state between Fragments safely.
4. **Lazy injection**: Prefer `by inject()` and lazy delegates to avoid premature creation.

---

## Дополнительные вопросы (RU)

- Как тестировать scoped-зависимости в unit-тестах?
- Что произойдёт, если забыть закрыть кастомный named scope?
- Можно ли вкладывать scopes друг в друга (scope внутри scope)?
- Как обрабатывать scope для `ViewModel` с `SavedStateHandle`?

## Follow-ups

- How to test scoped dependencies in unit tests?
- What happens if you forget to close a custom named scope?
- Can you nest scopes (scope within a scope)?
- How to handle scope for `ViewModel` with SavedStateHandle?

## Ссылки (RU)

- Официальная документация Koin по Scope
- Документация по жизненному циклу Android-компонентов
- Материалы по паттернам dependency injection

## References

- Koin official documentation on Scopes
- Android lifecycle documentation
- Dependency injection patterns

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-dependency-injection]]

### Предпосылки (проще)

- Базовая настройка Koin и конфигурация модулей
- Основы жизненного цикла Android-компонентов

### Связанные (тот же уровень)

- [[q-how-to-display-snackbar-or-toast-based-on-results--android--medium]]
- [[q-stable-classes-compose--android--hard]]

### Продвинутые (сложнее)

- [[q-what-methods-redraw-views--android--medium]]
- Кастомная реализация scope с использованием lifecycle observers

## Related Questions

### Prerequisites / Concepts

- [[c-dependency-injection]]

### Prerequisites (Easier)
- Basic Koin setup and module configuration
- Android lifecycle fundamentals

### Related (Same Level)
- [[q-how-to-display-snackbar-or-toast-based-on-results--android--medium]]
- [[q-stable-classes-compose--android--hard]]

### Advanced (Harder)
- [[q-what-methods-redraw-views--android--medium]]
- Custom scope implementation with lifecycle observers

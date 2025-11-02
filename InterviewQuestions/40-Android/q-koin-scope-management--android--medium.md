---
id: android-203
title: "Koin Scope Management / Управление Scope В Koin"
aliases: [Koin Scope Management, Koin Scopes, Жизненный цикл Koin, Управление Scope В Koin]
topic: android
subtopics: [architecture-mvvm, di-koin, lifecycle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dependency-injection, q-how-to-display-snackbar-or-toast-based-on-results--android--medium, q-stable-classes-compose--android--hard, q-what-methods-redraw-views--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/architecture-mvvm, android/di-koin, android/lifecycle, dependency-injection, difficulty/medium, koin, scopes]
date created: Tuesday, October 28th 2025, 9:23:52 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)

> Как управлять scope в Koin? Реализуйте зависимости с ограниченным временем жизни для Activity и Fragment с правильной обработкой жизненного цикла.

# Question (EN)

> How do you manage scopes in Koin? Implement Activity and Fragment scoped dependencies with proper lifecycle handling.

---

## Ответ (RU)

**Scope в Koin** — это контейнеры для зависимостей с ограниченным временем жизни, привязанные к Android компонентам (Activity, Fragment) или пользовательским логическим границам. Они предотвращают утечки памяти и обеспечивают правильную обработку жизненного цикла.

### Основные Концепции

**Типы Scope**:
1. **Root Scope** - на уровне приложения
2. **Component Scope** - привязан к Activity/Fragment
3. **Named Scope** - пользовательские логические границы

**Преимущества**:
- Автоматическая очистка ресурсов
- Предотвращение утечек памяти
- Соответствие жизненному циклу компонентов

### Activity Scoped Dependencies

```kotlin
// ✅ Определение модуля с Activity scope
val shoppingModule = module {
    // Зависимость уровня приложения
    single<ProductRepository> { ProductRepositoryImpl(get()) }

    // Activity-scoped зависимости
    scope<ShoppingActivity> {
        scoped { ShoppingCart() }
        scoped { ShoppingCartManager(get(), get()) }
        scoped { PaymentProcessor(get()) }
    }
}

// ✅ Activity с автоматическим управлением scope
class ShoppingActivity : AppCompatActivity() {

    private val scope: Scope by activityScope()
    private val cartManager: ShoppingCartManager by scope.inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Scope автоматически создан
    }

    override fun onDestroy() {
        // Scope автоматически закрыт
        super.onDestroy()
    }
}
```

**Объяснение**:
- `activityScope()` автоматически привязывает scope к жизненному циклу Activity
- `scoped` создаёт один экземпляр на scope
- При `onDestroy()` все зависимости автоматически освобождаются

### Fragment Scoped Dependencies

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

    private val scope: Scope by fragmentScope()

    private val userId: String by lazy {
        requireArguments().getString("user_id")!!
    }

    private val profileLoader: UserProfileLoader by scope.inject {
        parametersOf(userId)
    }

    override fun onDestroyView() {
        // Scope автоматически закрывается
        super.onDestroyView()
    }
}
```

**Ключевые моменты**:
- `fragmentScope()` привязывает к жизненному циклу Fragment
- `parametersOf()` передаёт runtime параметры
- Scope закрывается при уничтожении Fragment

### Разделение Scope Между Компонентами

```kotlin
// ✅ Activity создаёт shared scope
class MainActivity : AppCompatActivity() {

    private val scope: Scope by activityScope()
    private val sharedViewModel: SharedViewModel by scope.inject()
}

// ✅ Fragment получает доступ к Activity scope
class HomeFragment : Fragment() {

    private val activityScope: Scope by activityRetainedScope()
    private val sharedViewModel: SharedViewModel by activityScope.inject()
}

// Extension function
fun Fragment.activityRetainedScope(): Lazy<Scope> = lazy {
    (requireActivity() as? MainActivity)?.let {
        getKoin().getScope(it.toString())
    } ?: throw IllegalStateException("Activity scope not found")
}
```

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

    fun endSession() {
        sessionScope?.close()
        sessionScope = null
    }
}
```

### Сравнение Подходов

| Подход | Использование | Автоматическая очистка |
|--------|---------------|------------------------|
| `activityScope()` | Activity-зависимости | Да |
| `fragmentScope()` | Fragment-зависимости | Да |
| Named scope | Пользовательская логика | Нет (ручное управление) |

### Best Practices

1. **Соответствие жизненному циклу**: Используйте `activityScope()` / `fragmentScope()` для автоматического управления
2. **Избегать утечек**: Всегда закрывайте custom scopes в `onDestroy()`
3. **Shared state**: Используйте Activity scope для разделения состояния между фрагментами
4. **Lazy injection**: Предпочитайте `by inject()` вместо прямого `get()`

---

## Answer (EN)

**Koin Scopes** provide lifecycle-aware dependency management by creating containers for dependencies with limited lifetimes tied to Android components (Activity, Fragment) or custom logical boundaries. They prevent memory leaks and ensure proper lifecycle handling.

### Core Concepts

**Scope Types**:
1. **Root Scope** - Application-wide, never closes
2. **Component Scope** - Tied to Activity/Fragment lifecycle
3. **Named Scope** - Custom logical boundaries

**Benefits**:
- Automatic resource cleanup
- Memory leak prevention
- Lifecycle alignment with components

### Activity Scoped Dependencies

```kotlin
// ✅ Module with Activity scope
val shoppingModule = module {
    // Application-wide dependency
    single<ProductRepository> { ProductRepositoryImpl(get()) }

    // Activity-scoped dependencies
    scope<ShoppingActivity> {
        scoped { ShoppingCart() }
        scoped { ShoppingCartManager(get(), get()) }
        scoped { PaymentProcessor(get()) }
    }
}

// ✅ Activity with automatic scope management
class ShoppingActivity : AppCompatActivity() {

    private val scope: Scope by activityScope()
    private val cartManager: ShoppingCartManager by scope.inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Scope automatically created
    }

    override fun onDestroy() {
        // Scope automatically closed
        super.onDestroy()
    }
}
```

**Explanation**:
- `activityScope()` automatically ties scope to Activity lifecycle
- `scoped` creates one instance per scope
- On `onDestroy()` all dependencies are automatically released

### Fragment Scoped Dependencies

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

    private val scope: Scope by fragmentScope()

    private val userId: String by lazy {
        requireArguments().getString("user_id")!!
    }

    private val profileLoader: UserProfileLoader by scope.inject {
        parametersOf(userId)
    }

    override fun onDestroyView() {
        // Scope automatically closed
        super.onDestroyView()
    }
}
```

**Key Points**:
- `fragmentScope()` ties to Fragment lifecycle
- `parametersOf()` passes runtime parameters
- Scope closes when Fragment is destroyed

### Sharing Scopes Between Components

```kotlin
// ✅ Activity creates shared scope
class MainActivity : AppCompatActivity() {

    private val scope: Scope by activityScope()
    private val sharedViewModel: SharedViewModel by scope.inject()
}

// ✅ Fragment accesses Activity scope
class HomeFragment : Fragment() {

    private val activityScope: Scope by activityRetainedScope()
    private val sharedViewModel: SharedViewModel by activityScope.inject()
}

// Extension function
fun Fragment.activityRetainedScope(): Lazy<Scope> = lazy {
    (requireActivity() as? MainActivity)?.let {
        getKoin().getScope(it.toString())
    } ?: throw IllegalStateException("Activity scope not found")
}
```

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

    fun endSession() {
        sessionScope?.close()
        sessionScope = null
    }
}
```

### Comparison of Approaches

| Approach | Use Case | Automatic Cleanup |
|----------|----------|-------------------|
| `activityScope()` | Activity-level dependencies | Yes |
| `fragmentScope()` | Fragment-level dependencies | Yes |
| Named scope | Custom logic boundaries | No (manual management) |

### Best Practices

1. **Match lifecycle**: Use `activityScope()` / `fragmentScope()` for automatic management
2. **Prevent leaks**: Always close custom scopes in `onDestroy()`
3. **Shared state**: Use Activity scope to share state between fragments
4. **Lazy injection**: Prefer `by inject()` over direct `get()`

---

## Follow-ups

- How to test scoped dependencies in unit tests?
- What happens if you forget to close a custom named scope?
- Can you nest scopes (scope within a scope)?
- How to handle scope for ViewModel with SavedStateHandle?

## References

- Koin official documentation on Scopes
- Android lifecycle documentation
- Dependency injection patterns

## Related Questions

### Prerequisites (Easier)
- Basic Koin setup and module configuration
- Android lifecycle fundamentals

### Related (Same Level)
- [[q-how-to-display-snackbar-or-toast-based-on-results--android--medium]]
- [[q-stable-classes-compose--android--hard]]

### Advanced (Harder)
- [[q-what-methods-redraw-views--android--medium]]
- Custom scope implementation with lifecycle observers

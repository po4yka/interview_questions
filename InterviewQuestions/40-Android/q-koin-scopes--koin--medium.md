---
id: android-koin-003
title: Koin Scopes / Области видимости Koin
aliases:
- Koin Scopes
- Koin Scope DSL
- Scoped Dependencies
topic: android
subtopics:
- di-koin
- dependency-injection
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-koin-setup-modules--koin--medium
- q-koin-inject-get--koin--medium
- q-koin-viewmodel--koin--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-koin
- dependency-injection
- difficulty/medium
- koin
anki_cards:
- slug: android-koin-003-0-en
  language: en
- slug: android-koin-003-0-ru
  language: ru
---
# Vopros (RU)
> Что такое Scopes в Koin? Как создавать и использовать области видимости для управления жизненным циклом зависимостей?

# Question (EN)
> What are Scopes in Koin? How do you create and use scopes to manage dependency lifecycles?

---

## Otvet (RU)

**Scope** в Koin - это ограниченная область видимости, в которой зависимости живут определенное время. В отличие от `single` (глобальный синглтон) или `factory` (каждый раз новый), scoped-зависимости существуют пока открыт их scope.

### Зачем нужны Scopes

- **Управление жизненным циклом**: зависимости привязаны к жизненному циклу экрана/фичи
- **Изоляция состояния**: каждый scope имеет свои экземпляры
- **Освобождение ресурсов**: при закрытии scope все зависимости уничтожаются
- **Memory-эффективность**: не держать объекты дольше необходимого

### Определение Scope

```kotlin
val userModule = module {
    // Определение scope с уникальным qualifier
    scope<UserSession> {
        // scoped - синглтон внутри scope
        scoped { UserPreferences() }
        scoped { UserProfileRepository(get()) }

        // factory внутри scope - новый экземпляр каждый раз
        factory { UserValidator() }
    }
}
```

### Создание и использование Scope

```kotlin
// Создание scope
val userScope = getKoin().createScope<UserSession>("user_session_id")

// Получение зависимостей из scope
val preferences = userScope.get<UserPreferences>()
val repository = userScope.get<UserProfileRepository>()

// Закрытие scope - все зависимости уничтожаются
userScope.close()
```

### Типы Scope определений

#### Named Scope

```kotlin
val featureModule = module {
    // Именованный scope
    scope(named("checkout")) {
        scoped { CartRepository() }
        scoped { PaymentService(get()) }
        scoped { CheckoutViewModel(get(), get()) }
    }
}

// Использование
val checkoutScope = getKoin().createScope("checkout_1", named("checkout"))
val cart = checkoutScope.get<CartRepository>()
```

#### Typed Scope

```kotlin
// Scope привязанный к типу
class UserSession

val userModule = module {
    scope<UserSession> {
        scoped { UserData() }
        scoped { UserApiClient(get()) }
    }
}

// Использование
val session = UserSession()
val scope = getKoin().createScope("session_123", session)
```

### Android Scopes

#### Activity Scope

```kotlin
val activityModule = module {
    scope<MainActivity> {
        scoped { MainPresenter(get()) }
        scoped { MainNavigator() }
    }
}

class MainActivity : AppCompatActivity(), AndroidScopeComponent {

    // Автоматическое создание scope
    override val scope: Scope by activityScope()

    // Зависимости из scope
    private val presenter: MainPresenter by inject()
    private val navigator: MainNavigator by inject()

    override fun onDestroy() {
        super.onDestroy()
        // Scope автоматически закрывается
    }
}
```

#### Fragment Scope

```kotlin
val fragmentModule = module {
    scope<ProfileFragment> {
        scoped { ProfilePresenter(get()) }
        scoped { ProfileImageLoader() }
    }
}

class ProfileFragment : Fragment(), AndroidScopeComponent {

    override val scope: Scope by fragmentScope()

    private val presenter: ProfilePresenter by inject()

    // Scope закрывается при onDestroy Fragment
}
```

### Связанные Scopes (Linked Scopes)

```kotlin
val appModule = module {
    // Родительский scope
    scope(named("user")) {
        scoped { UserSession() }
        scoped { UserRepository(get()) }
    }

    // Дочерний scope, имеющий доступ к родительскому
    scope(named("profile")) {
        scoped { ProfileService(get()) } // Может получить UserRepository
    }
}

// Создание связанных scopes
val userScope = getKoin().createScope("user_1", named("user"))
val profileScope = getKoin().createScope(
    "profile_1",
    named("profile"),
    userScope // Связь с родительским scope
)

// profileScope может получить зависимости из userScope
val repo = profileScope.get<UserRepository>() // Из userScope
val service = profileScope.get<ProfileService>() // Из profileScope
```

### Практический пример: Feature Scope

```kotlin
// Feature module с собственным scope
val checkoutModule = module {

    // Глобальные зависимости
    single { PaymentGateway() }

    // Scope для процесса checkout
    scope(named("checkout")) {
        // Живут только во время checkout flow
        scoped { Cart() }
        scoped { ShippingCalculator() }
        scoped {
            CheckoutManager(
                cart = get(),
                shipping = get(),
                payment = get() // Из глобального single
            )
        }

        viewModel { CheckoutViewModel(get()) }
    }
}

class CheckoutActivity : AppCompatActivity(), AndroidScopeComponent {

    override val scope: Scope by activityRetainedScope(named("checkout"))

    private val cart: Cart by inject()
    private val viewModel: CheckoutViewModel by viewModel()

    fun completeCheckout() {
        viewModel.complete()
        // При выходе scope закрывается, Cart и все scoped-зависимости уничтожаются
    }
}
```

### Scope с Source (Koin 3.x)

```kotlin
val sessionModule = module {
    scope<UserSession> {
        // Доступ к source объекту scope
        scoped { (session: UserSession) ->
            UserApiClient(session.token)
        }
    }
}

// Создание с source
val session = UserSession(token = "abc123")
val scope = getKoin().createScope("session_1", session)

// Source передается автоматически
val client = scope.get<UserApiClient>()
```

### Lifecycle-aware Scopes

```kotlin
class SessionManager : KoinComponent {

    private var currentScope: Scope? = null

    fun startSession(userId: String) {
        // Создаем scope при входе пользователя
        currentScope = getKoin().createScope(
            "session_$userId",
            named("user_session")
        )
    }

    fun endSession() {
        // Закрываем scope при выходе
        currentScope?.close()
        currentScope = null
    }

    fun <T : Any> getScoped(clazz: KClass<T>): T {
        return currentScope?.get(clazz)
            ?: throw IllegalStateException("No active session")
    }
}
```

### Лучшие практики

1. **Используйте scopes для feature flows** - checkout, onboarding, user session
2. **Закрывайте scopes явно** - предотвращает утечки памяти
3. **AndroidScopeComponent** - автоматическое управление lifecycle
4. **Не храните ссылки на scoped-объекты** вне scope
5. **Тестируйте scopes изолированно** - создавайте тестовые scopes

```kotlin
// Тестирование scope
@Test
fun `test checkout scope`() {
    val koin = koinApplication {
        modules(checkoutModule)
    }.koin

    val scope = koin.createScope("test", named("checkout"))

    val cart = scope.get<Cart>()
    cart.addItem(Product("test"))

    assertEquals(1, cart.items.size)

    scope.close()
}
```

---

## Answer (EN)

**Scope** in Koin is a bounded context where dependencies live for a specific duration. Unlike `single` (global singleton) or `factory` (new instance each time), scoped dependencies exist as long as their scope is open.

### Why Use Scopes

- **Lifecycle management**: dependencies tied to screen/feature lifecycle
- **State isolation**: each scope has its own instances
- **Resource cleanup**: when scope closes, all dependencies are destroyed
- **Memory efficiency**: don't hold objects longer than necessary

### Defining a Scope

```kotlin
val userModule = module {
    // Define scope with unique qualifier
    scope<UserSession> {
        // scoped - singleton within scope
        scoped { UserPreferences() }
        scoped { UserProfileRepository(get()) }

        // factory within scope - new instance each time
        factory { UserValidator() }
    }
}
```

### Creating and Using a Scope

```kotlin
// Create scope
val userScope = getKoin().createScope<UserSession>("user_session_id")

// Get dependencies from scope
val preferences = userScope.get<UserPreferences>()
val repository = userScope.get<UserProfileRepository>()

// Close scope - all dependencies are destroyed
userScope.close()
```

### Types of Scope Definitions

#### Named Scope

```kotlin
val featureModule = module {
    // Named scope
    scope(named("checkout")) {
        scoped { CartRepository() }
        scoped { PaymentService(get()) }
        scoped { CheckoutViewModel(get(), get()) }
    }
}

// Usage
val checkoutScope = getKoin().createScope("checkout_1", named("checkout"))
val cart = checkoutScope.get<CartRepository>()
```

#### Typed Scope

```kotlin
// Scope bound to a type
class UserSession

val userModule = module {
    scope<UserSession> {
        scoped { UserData() }
        scoped { UserApiClient(get()) }
    }
}

// Usage
val session = UserSession()
val scope = getKoin().createScope("session_123", session)
```

### Android Scopes

#### Activity Scope

```kotlin
val activityModule = module {
    scope<MainActivity> {
        scoped { MainPresenter(get()) }
        scoped { MainNavigator() }
    }
}

class MainActivity : AppCompatActivity(), AndroidScopeComponent {

    // Automatic scope creation
    override val scope: Scope by activityScope()

    // Dependencies from scope
    private val presenter: MainPresenter by inject()
    private val navigator: MainNavigator by inject()

    override fun onDestroy() {
        super.onDestroy()
        // Scope automatically closes
    }
}
```

#### Fragment Scope

```kotlin
val fragmentModule = module {
    scope<ProfileFragment> {
        scoped { ProfilePresenter(get()) }
        scoped { ProfileImageLoader() }
    }
}

class ProfileFragment : Fragment(), AndroidScopeComponent {

    override val scope: Scope by fragmentScope()

    private val presenter: ProfilePresenter by inject()

    // Scope closes on Fragment onDestroy
}
```

### Linked Scopes

```kotlin
val appModule = module {
    // Parent scope
    scope(named("user")) {
        scoped { UserSession() }
        scoped { UserRepository(get()) }
    }

    // Child scope with access to parent
    scope(named("profile")) {
        scoped { ProfileService(get()) } // Can get UserRepository
    }
}

// Create linked scopes
val userScope = getKoin().createScope("user_1", named("user"))
val profileScope = getKoin().createScope(
    "profile_1",
    named("profile"),
    userScope // Link to parent scope
)

// profileScope can get dependencies from userScope
val repo = profileScope.get<UserRepository>() // From userScope
val service = profileScope.get<ProfileService>() // From profileScope
```

### Practical Example: Feature Scope

```kotlin
// Feature module with its own scope
val checkoutModule = module {

    // Global dependencies
    single { PaymentGateway() }

    // Scope for checkout process
    scope(named("checkout")) {
        // Live only during checkout flow
        scoped { Cart() }
        scoped { ShippingCalculator() }
        scoped {
            CheckoutManager(
                cart = get(),
                shipping = get(),
                payment = get() // From global single
            )
        }

        viewModel { CheckoutViewModel(get()) }
    }
}

class CheckoutActivity : AppCompatActivity(), AndroidScopeComponent {

    override val scope: Scope by activityRetainedScope(named("checkout"))

    private val cart: Cart by inject()
    private val viewModel: CheckoutViewModel by viewModel()

    fun completeCheckout() {
        viewModel.complete()
        // When exiting, scope closes, Cart and all scoped dependencies destroyed
    }
}
```

### Scope with Source (Koin 3.x)

```kotlin
val sessionModule = module {
    scope<UserSession> {
        // Access to scope source object
        scoped { (session: UserSession) ->
            UserApiClient(session.token)
        }
    }
}

// Create with source
val session = UserSession(token = "abc123")
val scope = getKoin().createScope("session_1", session)

// Source is passed automatically
val client = scope.get<UserApiClient>()
```

### Lifecycle-aware Scopes

```kotlin
class SessionManager : KoinComponent {

    private var currentScope: Scope? = null

    fun startSession(userId: String) {
        // Create scope on user login
        currentScope = getKoin().createScope(
            "session_$userId",
            named("user_session")
        )
    }

    fun endSession() {
        // Close scope on logout
        currentScope?.close()
        currentScope = null
    }

    fun <T : Any> getScoped(clazz: KClass<T>): T {
        return currentScope?.get(clazz)
            ?: throw IllegalStateException("No active session")
    }
}
```

### Best Practices

1. **Use scopes for feature flows** - checkout, onboarding, user session
2. **Close scopes explicitly** - prevents memory leaks
3. **AndroidScopeComponent** - automatic lifecycle management
4. **Don't store references to scoped objects** outside scope
5. **Test scopes in isolation** - create test scopes

```kotlin
// Testing scope
@Test
fun `test checkout scope`() {
    val koin = koinApplication {
        modules(checkoutModule)
    }.koin

    val scope = koin.createScope("test", named("checkout"))

    val cart = scope.get<Cart>()
    cart.addItem(Product("test"))

    assertEquals(1, cart.items.size)

    scope.close()
}
```

---

## Dopolnitelnye Voprosy (RU)

- Как реализовать вложенные scopes для multi-step wizard?
- Чем scope отличается от ViewModel в контексте управления состоянием?
- Как тестировать компоненты с scoped-зависимостями?

## Follow-ups

- How do you implement nested scopes for a multi-step wizard?
- How does scope differ from ViewModel in terms of state management?
- How do you test components with scoped dependencies?

## Ssylki (RU)

- [Koin Scopes](https://insert-koin.io/docs/reference/koin-core/scopes)
- [Android Scopes](https://insert-koin.io/docs/reference/koin-android/scope)

## References

- [Koin Scopes](https://insert-koin.io/docs/reference/koin-core/scopes)
- [Android Scopes](https://insert-koin.io/docs/reference/koin-android/scope)

## Svyazannye Voprosy (RU)

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-koin-inject-get--koin--medium]]
- [[q-koin-viewmodel--koin--medium]]

## Related Questions

### Medium
- [[q-koin-setup-modules--koin--medium]]
- [[q-koin-inject-get--koin--medium]]
- [[q-koin-viewmodel--koin--medium]]

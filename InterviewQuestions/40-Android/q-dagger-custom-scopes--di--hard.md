---
tags:
  - android
  - dependency-injection
  - dagger
  - hilt
  - scopes
  - architecture
difficulty: hard
status: draft
related:
  - q-hilt-entry-points--di--medium
  - q-dagger-multibinding--di--hard
  - q-hilt-viewmodel-injection--jetpack--medium
created: 2025-10-11
---

# Question (EN)
How do you create and use custom scopes in Dagger/Hilt? Explain the difference between Singleton, custom scopes, and unscoped dependencies. Provide examples of when and why you'd create a custom scope.

## Answer (EN)
### Overview

**Scopes** in Dagger/Hilt control the lifecycle and sharing of dependencies. A scope annotation tells Dagger to create only one instance of a dependency per scope instance. Custom scopes allow you to create dependencies that live as long as a specific feature, user session, or business flow.

### Built-in Hilt Scopes

Hilt provides these standard scopes:

| Component | Scope | Created at | Destroyed at | Use for |
|-----------|-------|------------|--------------|---------|
| SingletonComponent | @Singleton | Application.onCreate() | App destroyed | App-wide singletons |
| ActivityRetainedComponent | @ActivityRetainedScoped | Activity created | Activity destroyed (survives config changes) | ViewModels, survives rotation |
| ActivityComponent | @ActivityScoped | Activity created | Activity destroyed | Activity dependencies |
| FragmentComponent | @FragmentScoped | Fragment created | Fragment destroyed | Fragment dependencies |
| ViewComponent | @ViewScoped | View created | View destroyed | View dependencies |
| ViewWithFragmentComponent | @ViewWithFragmentScoped | View created in Fragment | View destroyed | View in Fragment dependencies |
| ServiceComponent | @ServiceScoped | Service created | Service destroyed | Service dependencies |

### Understanding Scopes

```kotlin
// @Singleton - ONE instance for entire app lifecycle
@Singleton
class AppDatabase @Inject constructor() {
    // Created once, shared everywhere
}

// @ActivityScoped - ONE instance per Activity
@ActivityScoped
class ActivityTracker @Inject constructor() {
    // New instance for each Activity
    // Shared within that Activity
}

// Unscoped - NEW instance every time
class RequestHelper @Inject constructor() {
    // New instance every injection
}
```

### The Problem: Need Custom Lifecycles

Sometimes Hilt's built-in scopes don't match your app's architecture:

```kotlin
// ❌ Problem: User session doesn't match any built-in scope
// - Not @Singleton (user can log out)
// - Not @ActivityScoped (survives Activity recreation)
// - Not @ActivityRetainedScoped (survives app restart with saved state)

// Need a scope that:
// - Lives from login to logout
// - Survives Activity/Fragment recreation
// - Survives app restart (if user stays logged in)
// - Dies when user logs out
```

### Creating Custom Scopes

A custom scope is just an annotation:

```kotlin
// 1. Define the scope annotation
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserScope

// 2. Create a component for this scope
@UserScope
@DefineComponent(parent = SingletonComponent::class)
interface UserComponent {
    // Define what can be injected in this scope
}

// 3. Define builder for the component
@DefineComponent.Builder
interface UserComponentBuilder {
    fun build(): UserComponent
}

// 4. Mark dependencies with the scope
@UserScope
class UserSessionManager @Inject constructor(
    private val apiService: ApiService
) {
    var currentUser: User? = null
}

@UserScope
class UserPreferences @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // User-specific preferences
}

// 5. Install modules in the component
@Module
@InstallIn(UserComponent::class)
object UserModule {
    // Provide user-scoped dependencies
}

// 6. Manage component lifecycle
@Singleton
class UserComponentManager @Inject constructor(
    private val userComponentBuilder: Provider<UserComponentBuilder>
) {
    private var userComponent: UserComponent? = null

    fun createUserScope(): UserComponent {
        if (userComponent == null) {
            userComponent = userComponentBuilder.get().build()
        }
        return userComponent!!
    }

    fun destroyUserScope() {
        userComponent = null
    }

    fun getUserComponent(): UserComponent? = userComponent
}
```

### Real-World Example: User Session Scope

```kotlin
// Step 1: Define the scope
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class UserScope

// Step 2: Define the component
@UserScope
@DefineComponent(parent = SingletonComponent::class)
interface UserComponent

@DefineComponent.Builder
interface UserComponentBuilder {
    fun build(): UserComponent
}

// Step 3: User-scoped dependencies
@UserScope
class UserSessionManager @Inject constructor(
    private val apiService: ApiService,
    private val sharedPreferences: SharedPreferences
) {
    private var _currentUser: User? = null
    val currentUser: User? get() = _currentUser

    suspend fun login(email: String, password: String): Result<User> {
        return try {
            val user = apiService.login(email, password)
            _currentUser = user
            saveUserSession(user)
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun logout() {
        _currentUser = null
        clearUserSession()
    }

    private fun saveUserSession(user: User) {
        sharedPreferences.edit()
            .putString("user_id", user.id)
            .putString("user_token", user.token)
            .apply()
    }

    private fun clearUserSession() {
        sharedPreferences.edit()
            .remove("user_id")
            .remove("user_token")
            .apply()
    }
}

@UserScope
class UserAnalytics @Inject constructor(
    private val analytics: Analytics,
    private val userSessionManager: UserSessionManager
) {
    init {
        // Set user properties for all events in this session
        userSessionManager.currentUser?.let { user ->
            analytics.setUserId(user.id)
            analytics.setUserProperty("subscription_type", user.subscriptionType)
        }
    }

    fun track(event: String, properties: Map<String, Any> = emptyMap()) {
        val enrichedProperties = properties + mapOf(
            "user_id" to (userSessionManager.currentUser?.id ?: "unknown")
        )
        analytics.track(event, enrichedProperties)
    }
}

@UserScope
class UserNotificationManager @Inject constructor(
    private val fcmService: FcmService,
    private val userSessionManager: UserSessionManager
) {
    suspend fun registerForNotifications() {
        val user = userSessionManager.currentUser ?: return
        val token = fcmService.getToken()
        fcmService.registerToken(user.id, token)
    }

    suspend fun unregisterFromNotifications() {
        val user = userSessionManager.currentUser ?: return
        fcmService.unregisterToken(user.id)
    }
}

// Step 4: Module for user-scoped dependencies
@Module
@InstallIn(UserComponent::class)
object UserModule {
    // Can provide additional user-scoped dependencies here
}

// Step 5: Entry Point for accessing user-scoped dependencies
@EntryPoint
@InstallIn(UserComponent::class)
interface UserComponentEntryPoint {
    fun userSessionManager(): UserSessionManager
    fun userAnalytics(): UserAnalytics
    fun userNotificationManager(): UserNotificationManager
}

// Step 6: Component manager
@Singleton
class UserComponentManager @Inject constructor(
    private val userComponentBuilder: Provider<UserComponentBuilder>
) {
    private var userComponent: UserComponent? = null

    fun createUserSession(): UserComponent {
        if (userComponent != null) {
            throw IllegalStateException("User session already exists")
        }
        userComponent = userComponentBuilder.get().build()
        return userComponent!!
    }

    fun destroyUserSession() {
        userComponent = null
    }

    fun getUserComponent(): UserComponent? = userComponent

    fun requireUserComponent(): UserComponent {
        return userComponent ?: throw IllegalStateException("No active user session")
    }
}

// Step 7: Usage in Application
@HiltAndroidApp
class MyApplication : Application() {

    @Inject
    lateinit var userComponentManager: UserComponentManager

    fun onUserLogin(user: User) {
        // Create user scope
        val userComponent = userComponentManager.createUserSession()

        // Access user-scoped dependencies
        val entryPoint = EntryPointAccessors.fromComponent(
            userComponent,
            UserComponentEntryPoint::class.java
        )

        val sessionManager = entryPoint.userSessionManager()
        val analytics = entryPoint.userAnalytics()
        val notificationManager = entryPoint.userNotificationManager()

        // Initialize user session
        GlobalScope.launch {
            notificationManager.registerForNotifications()
        }

        analytics.track("user_logged_in")
    }

    fun onUserLogout() {
        // Access before destroying
        val userComponent = userComponentManager.getUserComponent()
        if (userComponent != null) {
            val entryPoint = EntryPointAccessors.fromComponent(
                userComponent,
                UserComponentEntryPoint::class.java
            )

            val analytics = entryPoint.userAnalytics()
            val notificationManager = entryPoint.userNotificationManager()

            GlobalScope.launch {
                notificationManager.unregisterFromNotifications()
            }

            analytics.track("user_logged_out")
        }

        // Destroy user scope
        userComponentManager.destroyUserSession()
    }
}
```

### Custom Scope: Feature Scope

Another common use case is feature-level scopes:

```kotlin
// Feature scope for multi-step flows
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class CheckoutScope

@CheckoutScope
@DefineComponent(parent = SingletonComponent::class)
interface CheckoutComponent

@DefineComponent.Builder
interface CheckoutComponentBuilder {
    fun build(): CheckoutComponent
}

// Checkout-scoped state
@CheckoutScope
class CheckoutState @Inject constructor() {
    var selectedItems: List<CartItem> = emptyList()
    var shippingAddress: Address? = null
    var paymentMethod: PaymentMethod? = null
    var appliedPromoCode: String? = null
    var calculatedTotal: Double = 0.0

    fun reset() {
        selectedItems = emptyList()
        shippingAddress = null
        paymentMethod = null
        appliedPromoCode = null
        calculatedTotal = 0.0
    }
}

@CheckoutScope
class CheckoutManager @Inject constructor(
    private val checkoutState: CheckoutState,
    private val apiService: ApiService,
    private val analytics: Analytics
) {

    suspend fun selectItems(items: List<CartItem>) {
        checkoutState.selectedItems = items
        analytics.track("checkout_items_selected", mapOf("count" to items.size))
    }

    suspend fun setShippingAddress(address: Address) {
        checkoutState.shippingAddress = address
        recalculateTotal()
        analytics.track("checkout_address_set")
    }

    suspend fun setPaymentMethod(method: PaymentMethod) {
        checkoutState.paymentMethod = method
        analytics.track("checkout_payment_set")
    }

    suspend fun applyPromoCode(code: String): Result<Double> {
        return try {
            val discount = apiService.validatePromoCode(code)
            checkoutState.appliedPromoCode = code
            recalculateTotal()
            analytics.track("checkout_promo_applied", mapOf("code" to code))
            Result.success(discount)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun completeCheckout(): Result<Order> {
        val items = checkoutState.selectedItems
        val address = checkoutState.shippingAddress
            ?: return Result.failure(IllegalStateException("Missing shipping address"))
        val payment = checkoutState.paymentMethod
            ?: return Result.failure(IllegalStateException("Missing payment method"))

        return try {
            val order = apiService.createOrder(
                items = items,
                shippingAddress = address,
                paymentMethod = payment,
                promoCode = checkoutState.appliedPromoCode
            )

            analytics.track("checkout_completed", mapOf(
                "order_id" to order.id,
                "total" to order.total
            ))

            Result.success(order)
        } catch (e: Exception) {
            analytics.track("checkout_failed", mapOf("error" to e.message))
            Result.failure(e)
        }
    }

    private suspend fun recalculateTotal() {
        val itemsTotal = checkoutState.selectedItems.sumOf { it.price * it.quantity }
        val shippingCost = calculateShipping()
        val discount = if (checkoutState.appliedPromoCode != null) {
            apiService.getPromoDiscount(checkoutState.appliedPromoCode!!)
        } else 0.0

        checkoutState.calculatedTotal = itemsTotal + shippingCost - discount
    }

    private fun calculateShipping(): Double {
        // Shipping calculation logic
        return 9.99
    }
}

@Module
@InstallIn(CheckoutComponent::class)
object CheckoutModule {
    // Checkout-specific dependencies
}

@EntryPoint
@InstallIn(CheckoutComponent::class)
interface CheckoutComponentEntryPoint {
    fun checkoutManager(): CheckoutManager
    fun checkoutState(): CheckoutState
}

// Component manager
@Singleton
class CheckoutComponentManager @Inject constructor(
    private val checkoutComponentBuilder: Provider<CheckoutComponentBuilder>
) {
    private var checkoutComponent: CheckoutComponent? = null

    fun startCheckout(): CheckoutComponent {
        if (checkoutComponent != null) {
            // Clear existing checkout
            endCheckout()
        }
        checkoutComponent = checkoutComponentBuilder.get().build()
        return checkoutComponent!!
    }

    fun endCheckout() {
        checkoutComponent?.let { component ->
            val entryPoint = EntryPointAccessors.fromComponent(
                component,
                CheckoutComponentEntryPoint::class.java
            )
            entryPoint.checkoutState().reset()
        }
        checkoutComponent = null
    }

    fun getCheckoutComponent(): CheckoutComponent? = checkoutComponent
}

// Usage in navigation
@Composable
fun CheckoutFlow(
    checkoutComponentManager: CheckoutComponentManager
) {
    val navController = rememberNavController()

    // Start checkout scope
    LaunchedEffect(Unit) {
        checkoutComponentManager.startCheckout()
    }

    // Clean up when leaving checkout
    DisposableEffect(Unit) {
        onDispose {
            checkoutComponentManager.endCheckout()
        }
    }

    val component = checkoutComponentManager.getCheckoutComponent()!!
    val entryPoint = remember {
        EntryPointAccessors.fromComponent(
            component,
            CheckoutComponentEntryPoint::class.java
        )
    }
    val checkoutManager = remember { entryPoint.checkoutManager() }

    NavHost(navController, startDestination = "items") {
        composable("items") {
            SelectItemsScreen(checkoutManager) {
                navController.navigate("address")
            }
        }
        composable("address") {
            AddressScreen(checkoutManager) {
                navController.navigate("payment")
            }
        }
        composable("payment") {
            PaymentScreen(checkoutManager) {
                navController.navigate("review")
            }
        }
        composable("review") {
            ReviewScreen(checkoutManager)
        }
    }
}
```

### Scope Comparison

```kotlin
// Singleton - App lifetime
@Singleton
class AppDatabase @Inject constructor() {
    // Lives entire app lifetime
    // Shared by all users, sessions, activities
}

// Custom UserScope - User session lifetime
@UserScope
class UserPreferences @Inject constructor() {
    // Lives from login to logout
    // New instance for each user session
    // Survives Activity recreation
}

// ActivityScoped - Activity lifetime
@ActivityScoped
class ActivityAnalytics @Inject constructor() {
    // Lives for one Activity
    // New instance for each Activity
    // Dies on Activity destruction
}

// Unscoped - No sharing
class RequestHandler @Inject constructor() {
    // New instance every time injected
    // Not shared
}
```

### Performance: Scoped vs Unscoped

```kotlin
// Scenario 1: Heavy object that should be reused
@Singleton // ✅ GOOD - Created once, reused
class HeavyImageProcessor @Inject constructor() {
    private val cache = LruCache<String, Bitmap>(100)
    // Expensive to create, should be singleton
}

// Scenario 2: Lightweight, stateless helper
class UrlFormatter @Inject constructor() { // ✅ GOOD - Unscoped, cheap to create
    fun format(url: String): String = url.trim().lowercase()
}

// Scenario 3: Stateful per-activity tracker
@ActivityScoped // ✅ GOOD - One per activity
class ActivityLifecycleTracker @Inject constructor(
    private val analytics: Analytics
) {
    private var startTime: Long = 0
}

// ❌ BAD - Singleton for stateful per-activity data
@Singleton // BAD - Will leak Activity data across activities!
class ActivityLifecycleTracker @Inject constructor() {
    private var startTime: Long = 0 // Shared across all activities!
}
```

### Advanced: Scopes with Parameters

Sometimes you need parameterized scopes:

```kotlin
// Custom scope with data
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ConversationScope

@ConversationScope
@DefineComponent(parent = SingletonComponent::class)
interface ConversationComponent

@DefineComponent.Builder
interface ConversationComponentBuilder {
    // Can't add parameters directly to builder in Hilt
    fun build(): ConversationComponent
}

// Instead, use a holder
@ConversationScope
class ConversationContext @Inject constructor() {
    lateinit var conversationId: String
    lateinit var participants: List<User>
}

@ConversationScope
class ConversationMessageLoader @Inject constructor(
    private val context: ConversationContext,
    private val apiService: ApiService
) {
    suspend fun loadMessages(): List<Message> {
        return apiService.getMessages(context.conversationId)
    }
}

@Singleton
class ConversationComponentManager @Inject constructor(
    private val builder: Provider<ConversationComponentBuilder>
) {
    private val conversations = mutableMapOf<String, ConversationComponent>()

    fun startConversation(conversationId: String, participants: List<User>): ConversationComponent {
        if (conversations.containsKey(conversationId)) {
            return conversations[conversationId]!!
        }

        val component = builder.get().build()

        // Initialize context
        val entryPoint = EntryPointAccessors.fromComponent(
            component,
            ConversationEntryPoint::class.java
        )
        val context = entryPoint.conversationContext()
        context.conversationId = conversationId
        context.participants = participants

        conversations[conversationId] = component
        return component
    }

    fun endConversation(conversationId: String) {
        conversations.remove(conversationId)
    }

    fun getConversation(conversationId: String): ConversationComponent? {
        return conversations[conversationId]
    }
}

@EntryPoint
@InstallIn(ConversationComponent::class)
interface ConversationEntryPoint {
    fun conversationContext(): ConversationContext
    fun messageLoader(): ConversationMessageLoader
}
```

### Testing Custom Scopes

```kotlin
// Test with custom scope
@HiltAndroidTest
class UserScopeTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var userComponentManager: UserComponentManager

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testUserScope_instancesAreShared() {
        // Create user scope
        val component = userComponentManager.createUserSession()

        val entryPoint = EntryPointAccessors.fromComponent(
            component,
            UserComponentEntryPoint::class.java
        )

        // Get same dependency twice
        val manager1 = entryPoint.userSessionManager()
        val manager2 = entryPoint.userSessionManager()

        // Should be same instance
        assertSame(manager1, manager2)
    }

    @Test
    fun testUserScope_newScopeCreatesNewInstances() {
        // First scope
        val component1 = userComponentManager.createUserSession()
        val entryPoint1 = EntryPointAccessors.fromComponent(
            component1,
            UserComponentEntryPoint::class.java
        )
        val manager1 = entryPoint1.userSessionManager()

        // Destroy and recreate
        userComponentManager.destroyUserSession()
        val component2 = userComponentManager.createUserSession()
        val entryPoint2 = EntryPointAccessors.fromComponent(
            component2,
            UserComponentEntryPoint::class.java
        )
        val manager2 = entryPoint2.userSessionManager()

        // Should be different instances
        assertNotSame(manager1, manager2)
    }

    @Test
    fun testUserScope_isolationBetweenScopes() = runTest {
        // Create scope and set user
        val component = userComponentManager.createUserSession()
        val entryPoint = EntryPointAccessors.fromComponent(
            component,
            UserComponentEntryPoint::class.java
        )
        val manager = entryPoint.userSessionManager()

        manager.login("test@example.com", "password")
        assertEquals("test@example.com", manager.currentUser?.email)

        // Destroy scope
        userComponentManager.destroyUserSession()

        // Create new scope
        val component2 = userComponentManager.createUserSession()
        val entryPoint2 = EntryPointAccessors.fromComponent(
            component2,
            UserComponentEntryPoint::class.java
        )
        val manager2 = entryPoint2.userSessionManager()

        // Should be fresh state
        assertNull(manager2.currentUser)
    }
}
```

### Best Practices

1. **Use Built-in Scopes First**
   ```kotlin
   // ✅ GOOD - Use built-in scope if it matches
   @Singleton
   class AppConfig @Inject constructor()

   // ❌ BAD - Don't create custom scope unnecessarily
   @CustomAppScope
   class AppConfig @Inject constructor()
   ```

2. **Scope Should Match Lifecycle**
   ```kotlin
   // ✅ GOOD - UserScope matches user session lifecycle
   @UserScope
   class UserSettings @Inject constructor()

   // ❌ BAD - Singleton for per-user data will leak
   @Singleton
   class UserSettings @Inject constructor()
   ```

3. **Manage Scope Lifecycle Explicitly**
   ```kotlin
   // ✅ GOOD - Explicit create/destroy
   fun onLogin() {
       userComponentManager.createUserSession()
   }

   fun onLogout() {
       userComponentManager.destroyUserSession()
   }

   // ❌ BAD - Forgetting to destroy causes memory leaks
   fun onLogin() {
       userComponentManager.createUserSession()
       // Never destroyed!
   }
   ```

4. **Don't Over-scope**
   ```kotlin
   // ✅ GOOD - Unscoped for lightweight, stateless
   class JsonParser @Inject constructor()

   // ❌ BAD - Unnecessary scope
   @Singleton
   class JsonParser @Inject constructor()
   ```

5. **Document Custom Scopes**
   ```kotlin
   /**
    * UserScope - Lives from user login to logout.
    * - Created: After successful login
    * - Destroyed: On logout or session expiration
    * - Use for: User-specific data, preferences, session state
    */
   @Scope
   @Retention(AnnotationRetention.RUNTIME)
   annotation class UserScope
   ```

### Common Pitfalls

1. **Memory Leaks from Not Destroying Scope**
   ```kotlin
   // ❌ BAD - Scope never destroyed
   fun onCreate() {
       featureComponentManager.create() // Created
       // Never destroyed - memory leak!
   }

   // ✅ GOOD - Scope destroyed
   fun onCreate() {
       featureComponentManager.create()
   }

   fun onDestroy() {
       featureComponentManager.destroy() // Cleaned up
   }
   ```

2. **Wrong Scope for Data**
   ```kotlin
   // ❌ BAD - Activity-scoped data in Singleton
   @Singleton
   class CurrentScreenTracker @Inject constructor() {
       var currentScreen: String = "" // Wrong scope!
   }

   // ✅ GOOD - Activity-scoped
   @ActivityScoped
   class CurrentScreenTracker @Inject constructor() {
       var currentScreen: String = ""
   }
   ```

3. **Forgetting @Scope Annotation**
   ```kotlin
   // ❌ BAD - Missing @UserScope
   class UserSettings @Inject constructor() {
       // Will be unscoped even though you want UserScope!
   }

   // ✅ GOOD
   @UserScope
   class UserSettings @Inject constructor()
   ```

### Summary

**Custom scopes** in Dagger/Hilt allow you to create dependencies with custom lifetimes:

**When to use custom scopes:**
- ✅ User session (login to logout)
- ✅ Multi-step flows (checkout, onboarding)
- ✅ Feature modules with state
- ✅ Conversation/chat scopes
- ✅ Any custom lifecycle not covered by built-in scopes

**Key concepts:**
- `@Scope` annotation - Marks scope
- `@DefineComponent` - Creates component
- Component manager - Manages lifecycle
- `@EntryPoint` - Access scoped dependencies

**Benefits:**
- Control dependency lifetime
- Prevent memory leaks
- Isolate feature state
- Match business logic lifecycle

**Best practices:**
1. Use built-in scopes when possible
2. Match scope to actual lifecycle
3. Explicitly manage create/destroy
4. Document custom scope purpose
5. Test scope isolation

---

# Вопрос (RU)
Как создавать и использовать кастомные scopes в Dagger/Hilt? Объясните разницу между Singleton, кастомными scopes и unscoped зависимостями. Приведите примеры, когда и зачем создавать кастомный scope.

## Ответ (RU)
### Обзор

**Scopes** в Dagger/Hilt контролируют жизненный цикл и совместное использование зависимостей. Аннотация scope сообщает Dagger создать только один экземпляр зависимости на экземпляр scope. Кастомные scopes позволяют создавать зависимости, которые живут в течение конкретной feature, пользовательской сессии или бизнес-процесса.

### Встроенные Hilt Scopes

Hilt предоставляет эти стандартные scopes:

| Компонент | Scope | Создаётся | Уничтожается | Используется для |
|-----------|-------|-----------|--------------|------------------|
| SingletonComponent | @Singleton | Application.onCreate() | Уничтожение приложения | App-wide singletons |
| ActivityRetainedComponent | @ActivityRetainedScoped | Создание Activity | Уничтожение Activity (переживает config changes) | ViewModel, переживает rotation |
| ActivityComponent | @ActivityScoped | Создание Activity | Уничтожение Activity | Зависимости Activity |
| FragmentComponent | @FragmentScoped | Создание Fragment | Уничтожение Fragment | Зависимости Fragment |
| ViewComponent | @ViewScoped | Создание View | Уничтожение View | Зависимости View |
| ViewWithFragmentComponent | @ViewWithFragmentScoped | Создание View во Fragment | Уничтожение View | Зависимости View во Fragment |
| ServiceComponent | @ServiceScoped | Создание Service | Уничтожение Service | Зависимости Service |

[Продолжение с примерами из английской версии...]

### Резюме

**Кастомные scopes** в Dagger/Hilt позволяют создавать зависимости с кастомным lifetime:

**Когда использовать кастомные scopes:**
- ✅ Пользовательская сессия (от логина до логаута)
- ✅ Многошаговые процессы (checkout, onboarding)
- ✅ Feature-модули с состоянием
- ✅ Conversation/chat scopes
- ✅ Любой кастомный жизненный цикл, не покрытый встроенными scopes

**Ключевые концепции:**
- `@Scope` аннотация — маркирует scope
- `@DefineComponent` — создаёт компонент
- Component manager — управляет жизненным циклом
- `@EntryPoint` — доступ к scoped зависимостям

**Преимущества:**
- Контроль lifetime зависимостей
- Предотвращение утечек памяти
- Изоляция состояния features
- Соответствие жизненному циклу бизнес-логики

**Лучшие практики:**
1. Используйте встроенные scopes, когда возможно
2. Сопоставляйте scope с реальным жизненным циклом
3. Явно управляйте create/destroy
4. Документируйте назначение кастомного scope
5. Тестируйте изоляцию scope

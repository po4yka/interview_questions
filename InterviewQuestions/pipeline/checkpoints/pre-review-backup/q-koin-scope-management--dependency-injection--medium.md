---
id: 20251012-12271124
title: "Koin Scope Management / Koin Scope Управление"
topic: dependency-injection
difficulty: medium
status: draft
moc: moc-android
related: [q-how-to-display-snackbar-or-toast-based-on-results--android--medium, q-stable-classes-compose--android--hard, q-what-methods-redraw-views--android--medium]
created: 2025-10-15
tags: [injection, koin, scopes, lifecycle, difficulty/medium]
---
# Koin Scope Management / Управление Scope в Koin

**English**: How do you manage scopes in Koin? Implement Activity and Fragment scoped dependencies with proper lifecycle handling.

## Answer (EN)
**Koin Scopes** provide a way to create dependencies with limited lifetimes, tied to specific components like Activities, Fragments, or custom logical boundaries. Scopes help manage memory and ensure proper lifecycle handling of dependencies.

### What is a Scope?

A **scope** in Koin is a container for definitions that:
- Has a defined lifecycle (start and close)
- Can be linked to Android components
- Automatically cleans up resources when closed
- Prevents memory leaks by releasing references

### Scope Types

1. **Root Scope** - Application-wide, never closes
2. **Component Scope** - Tied to Android components (Activity, Fragment)
3. **Custom Scope** - User-defined logical boundaries
4. **Named Scope** - Multiple instances of same scope type

### Defining Scopes

```kotlin
// Define a named scope
val myScope = named("MY_SCOPE")

// Module with scoped definitions
val scopedModule = module {
    // Root scope - lives forever
    single { AppDatabase(androidContext()) }

    // Scoped definition
    scope<MyActivity> {
        scoped { MyActivityPresenter(get()) }
        scoped { MyActivityViewModel(get()) }
    }

    // Named scope
    scope(named("user_session")) {
        scoped { UserSession(get()) }
        scoped { UserSettings(get()) }
    }
}
```

### Activity Scoped Dependencies

#### Complete Activity Scope Implementation

```kotlin
// 1. Define Activity-specific dependencies
data class ShoppingCart(val items: MutableList<Product> = mutableListOf())

class ShoppingCartManager(
    private val cart: ShoppingCart,
    private val repository: ProductRepository
) {
    fun addToCart(product: Product) {
        cart.items.add(product)
    }

    fun removeFromCart(product: Product) {
        cart.items.remove(product)
    }

    fun getTotal(): Double = cart.items.sumOf { it.price }

    suspend fun checkout(): Result<Order> {
        return repository.createOrder(cart.items)
    }

    fun clear() {
        cart.items.clear()
    }
}

// 2. Create module with Activity scope
val shoppingModule = module {
    // Application-wide dependencies
    single<ProductRepository> { ProductRepositoryImpl(get()) }

    // Activity-scoped dependencies
    scope<ShoppingActivity> {
        scoped { ShoppingCart() }
        scoped { ShoppingCartManager(get(), get()) }
        scoped { PaymentProcessor(get()) }
    }
}

// 3. Activity with scoped dependencies
class ShoppingActivity : AppCompatActivity() {

    // Create scope linked to Activity lifecycle
    private val scope: Scope by activityScope()

    // Inject scoped dependencies
    private val cartManager: ShoppingCartManager by scope.inject()
    private val paymentProcessor: PaymentProcessor by scope.inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_shopping)

        // Scope is automatically created
        // Dependencies are instantiated lazily
    }

    private fun addProductToCart(product: Product) {
        cartManager.addToCart(product)
        updateCartUI()
    }

    private fun checkout() {
        lifecycleScope.launch {
            paymentProcessor.processPayment(cartManager.getTotal())
                .onSuccess {
                    showSuccess()
                    cartManager.clear()
                }
                .onFailure { showError(it.message) }
        }
    }

    override fun onDestroy() {
        // Scope is automatically closed
        // All scoped instances are released
        super.onDestroy()
    }
}

// Alternative: Manual scope management
class ShoppingActivityManual : AppCompatActivity() {

    private lateinit var scope: Scope

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Manually create scope
        scope = getKoin().createScope(
            scopeId = "shopping_${System.currentTimeMillis()}",
            qualifier = named<ShoppingActivity>()
        )

        val cartManager: ShoppingCartManager = scope.get()
    }

    override fun onDestroy() {
        // Manually close scope
        scope.close()
        super.onDestroy()
    }
}
```

### Fragment Scoped Dependencies

#### Complete Fragment Scope Implementation

```kotlin
// 1. Define Fragment-specific dependencies
class UserProfileLoader(
    private val userId: String,
    private val repository: UserRepository,
    private val imageLoader: ImageLoader
) {
    suspend fun loadProfile(): Result<UserProfile> {
        return repository.getUserProfile(userId)
    }

    suspend fun loadAvatar(): Result<Bitmap> {
        return imageLoader.loadUserAvatar(userId)
    }
}

class ProfileEditState {
    var hasUnsavedChanges: Boolean = false
    val pendingChanges: MutableMap<String, Any> = mutableMapOf()

    fun markChanged(field: String, value: Any) {
        hasUnsavedChanges = true
        pendingChanges[field] = value
    }

    fun clear() {
        hasUnsavedChanges = false
        pendingChanges.clear()
    }
}

// 2. Create module with Fragment scope
val profileModule = module {
    // Application-wide
    single<UserRepository> { UserRepositoryImpl(get()) }
    single<ImageLoader> { ImageLoaderImpl(get()) }

    // Fragment-scoped
    scope<ProfileFragment> {
        scoped { (userId: String) ->
            UserProfileLoader(userId, get(), get())
        }
        scoped { ProfileEditState() }
        scoped { ProfileValidator() }
    }
}

// 3. Fragment with scoped dependencies
class ProfileFragment : Fragment() {

    // Create scope linked to Fragment lifecycle
    private val scope: Scope by fragmentScope()

    // Inject with parameters
    private val userId: String by lazy {
        requireArguments().getString("user_id")!!
    }

    private val profileLoader: UserProfileLoader by scope.inject {
        parametersOf(userId)
    }

    private val editState: ProfileEditState by scope.inject()
    private val validator: ProfileValidator by scope.inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Scope is automatically created
        loadProfile()
    }

    private fun loadProfile() {
        viewLifecycleOwner.lifecycleScope.launch {
            profileLoader.loadProfile()
                .onSuccess { profile -> displayProfile(profile) }
                .onFailure { error -> showError(error.message) }
        }
    }

    private fun onFieldChanged(field: String, value: Any) {
        if (validator.validate(field, value)) {
            editState.markChanged(field, value)
            updateSaveButtonState()
        }
    }

    override fun onDestroyView() {
        // Scope is automatically closed when Fragment is destroyed
        super.onDestroyView()
    }
}
```

### Sharing Scopes Between Components

#### Activity-Fragment Shared Scope

```kotlin
// 1. Define shared scope
val sharedModule = module {
    // Scope shared between Activity and its Fragments
    scope<MainActivity> {
        scoped { NavigationState() }
        scoped { SharedViewModel(get()) }
        scoped { AnalyticsTracker(get()) }
    }
}

// 2. Activity creates and owns scope
class MainActivity : AppCompatActivity() {

    private val scope: Scope by activityScope()
    private val navigationState: NavigationState by scope.inject()
    private val sharedViewModel: SharedViewModel by scope.inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Navigate to fragments
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, HomeFragment())
            .commit()
    }
}

// 3. Fragments access Activity's scope
class HomeFragment : Fragment() {

    // Get parent Activity's scope
    private val activityScope: Scope by activityRetainedScope()

    // Inject from Activity scope
    private val navigationState: NavigationState by activityScope.inject()
    private val sharedViewModel: SharedViewModel by activityScope.inject()

    // Fragment also has its own scope
    private val fragmentScope: Scope by fragmentScope()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Use shared dependencies
        navigationState.currentScreen = "home"

        sharedViewModel.events.collect { event ->
            handleEvent(event)
        }
    }
}

// Extension function to get Activity scope from Fragment
fun Fragment.activityRetainedScope(): Lazy<Scope> = lazy {
    (requireActivity() as? MainActivity)?.let {
        getKoin().getScope(it.toString())
    } ?: throw IllegalStateException("Activity must create scope first")
}
```

### Custom Named Scopes

```kotlin
// 1. Define feature-based scopes
val featureModule = module {
    // User session scope - lives during user authentication
    scope(named("user_session")) {
        scoped { UserSession(get()) }
        scoped { AuthenticatedApiClient(get()) }
        scoped { UserPreferences(get()) }
    }

    // Chat conversation scope
    scope(named("chat_conversation")) {
        scoped { (conversationId: String) ->
            ConversationManager(conversationId, get())
        }
        scoped { MessageQueue() }
        scoped { TypingIndicator() }
    }
}

// 2. Manage custom scopes
class SessionManager(private val koin: Koin) {

    private var sessionScope: Scope? = null

    fun startSession(userId: String) {
        // Create user session scope
        sessionScope = koin.createScope(
            scopeId = "session_$userId",
            qualifier = named("user_session")
        )

        val userSession: UserSession = sessionScope!!.get()
        userSession.start(userId)
    }

    fun endSession() {
        // Close scope and clean up
        sessionScope?.close()
        sessionScope = null
    }

    fun <T> getSessionDependency(clazz: KClass<T>): T? {
        return sessionScope?.get(clazz, null)
    }
}

// 3. Use in Activity
class ChatActivity : AppCompatActivity() {

    private lateinit var conversationScope: Scope

    private val sessionManager: SessionManager by inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val conversationId = intent.getStringExtra("conversation_id")!!

        // Create conversation-specific scope
        conversationScope = getKoin().createScope(
            scopeId = "conversation_$conversationId",
            qualifier = named("chat_conversation")
        )

        val conversationManager: ConversationManager =
            conversationScope.get { parametersOf(conversationId) }

        conversationManager.loadMessages()
    }

    override fun onDestroy() {
        conversationScope.close()
        super.onDestroy()
    }
}
```

### Scope Lifecycle Management

#### Automatic Lifecycle Handling

```kotlin
// Extension to tie scope to lifecycle
class ScopedActivity : AppCompatActivity() {

    private val scope: Scope by lazy {
        createScope(this)
            .also { scope ->
                // Automatically close scope when lifecycle ends
                lifecycle.addObserver(object : DefaultLifecycleObserver {
                    override fun onDestroy(owner: LifecycleOwner) {
                        scope.close()
                    }
                })
            }
    }
}

// Helper function for lifecycle-aware scopes
fun <T : Any> LifecycleOwner.scopedKoin(
    scopeId: String,
    qualifier: Qualifier? = null,
    block: Scope.() -> Unit = {}
): Lazy<Scope> = lazy {
    val scope = getKoin().createScope(scopeId, qualifier)

    lifecycle.addObserver(object : DefaultLifecycleObserver {
        override fun onDestroy(owner: LifecycleOwner) {
            scope.close()
        }
    })

    scope.apply(block)
}

// Usage
class MyActivity : AppCompatActivity() {
    private val scope by scopedKoin("my_activity", named<MyActivity>())

    private val presenter: Presenter by scope.inject()
}
```

### Testing Scoped Dependencies

```kotlin
class ShoppingActivityTest {

    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(
            module {
                scope<ShoppingActivity> {
                    scoped { mockk<ShoppingCartManager>(relaxed = true) }
                    scoped { mockk<PaymentProcessor>(relaxed = true) }
                }
            }
        )
    }

    @Test
    fun `test activity scope`() {
        val activity = Robolectric.buildActivity(ShoppingActivity::class.java)
            .create()
            .get()

        val scope = activity.scope
        val cartManager: ShoppingCartManager = scope.get()

        // Test with scoped dependency
        assertNotNull(cartManager)
    }

    @Test
    fun `scope is closed on destroy`() {
        val activity = Robolectric.buildActivity(ShoppingActivity::class.java)
            .create()
            .get()

        val scope = activity.scope

        activity.finish()
        Robolectric.flushForegroundThreadScheduler()

        // Scope should be closed
        assertTrue(scope.closed)
    }
}
```

### Best Practices

1. **Match Scope to Lifecycle** - Scope lifetime should match component lifecycle
2. **Avoid Memory Leaks** - Always close scopes when done
3. **Use Activity Scope for Fragments** - Share state across fragment stack
4. **Named Scopes for Features** - Logical grouping of related functionality
5. **Lazy Injection** - Use `by inject()` for deferred instantiation
6. **Clean Up Resources** - Implement cleanup in scoped classes
7. **Test Scope Behavior** - Verify scope creation and destruction

### Common Patterns

**Pattern 1: Multi-Step Flow Scope**
```kotlin
// Checkout flow spanning multiple screens
scope(named("checkout_flow")) {
    scoped { CheckoutState() }
    scoped { PaymentInfo() }
    scoped { ShippingInfo() }
}
```

**Pattern 2: Feature Module Scope**
```kotlin
// Isolated feature with its own dependencies
scope(named("feature_messaging")) {
    scoped { MessagingRepository(get()) }
    scoped { MessageCache() }
    scoped { NotificationManager(get()) }
}
```

**Pattern 3: User Session Scope**
```kotlin
// Dependencies that exist only while user is logged in
scope(named("authenticated_user")) {
    scoped { AuthToken(get()) }
    scoped { UserProfile(get()) }
    scoped { SecureStorage(get()) }
}
```

### Summary

Koin scopes provide lifecycle-aware dependency management:
- **Activity Scope** - For Activity-level dependencies
- **Fragment Scope** - For Fragment-level dependencies
- **Custom Scopes** - For logical boundaries (sessions, features)
- **Automatic Cleanup** - Integrated with Android lifecycle
- **Shared Scopes** - Communication between components
- **Memory Safety** - Prevents leaks through proper disposal

Use scopes to match dependency lifetime with component lifecycle, prevent memory leaks, and organize related dependencies.

---

## Ответ (RU)
**Scope в Koin** предоставляют способ создания зависимостей с ограниченным временем жизни, привязанных к конкретным компонентам (Activity, Fragment) или пользовательским логическим границам. Scope помогают управлять памятью и обеспечивают правильную обработку жизненного цикла зависимостей.

### Что такое Scope?

**Scope** в Koin — это контейнер для определений, который:
- Имеет определённый жизненный цикл (start и close)
- Может быть привязан к Android компонентам
- Автоматически очищает ресурсы при закрытии
- Предотвращает утечки памяти, освобождая ссылки

### Типы Scope

1. **Root Scope** - на уровне приложения, никогда не закрывается
2. **Component Scope** - привязан к Android компонентам
3. **Custom Scope** - пользовательские логические границы
4. **Named Scope** - множество экземпляров одного типа scope

### Activity Scoped Dependencies

```kotlin
// 1. Определение Activity-специфичных зависимостей
data class ShoppingCart(val items: MutableList<Product> = mutableListOf())

class ShoppingCartManager(
    private val cart: ShoppingCart,
    private val repository: ProductRepository
) {
    fun addToCart(product: Product) {
        cart.items.add(product)
    }

    fun getTotal(): Double = cart.items.sumOf { it.price }

    suspend fun checkout(): Result<Order> {
        return repository.createOrder(cart.items)
    }
}

// 2. Создание модуля с Activity scope
val shoppingModule = module {
    // Зависимости уровня приложения
    single<ProductRepository> { ProductRepositoryImpl(get()) }

    // Activity-scoped зависимости
    scope<ShoppingActivity> {
        scoped { ShoppingCart() }
        scoped { ShoppingCartManager(get(), get()) }
        scoped { PaymentProcessor(get()) }
    }
}

// 3. Activity с scoped зависимостями
class ShoppingActivity : AppCompatActivity() {

    // Создание scope привязанного к жизненному циклу Activity
    private val scope: Scope by activityScope()

    // Инъекция scoped зависимостей
    private val cartManager: ShoppingCartManager by scope.inject()
    private val paymentProcessor: PaymentProcessor by scope.inject()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_shopping)

        // Scope автоматически создан
        // Зависимости инстанцируются лениво
    }

    private fun checkout() {
        lifecycleScope.launch {
            paymentProcessor.processPayment(cartManager.getTotal())
                .onSuccess { showSuccess() }
                .onFailure { showError(it.message) }
        }
    }

    override fun onDestroy() {
        // Scope автоматически закрыт
        // Все scoped экземпляры освобождены
        super.onDestroy()
    }
}
```

### Fragment Scoped Dependencies

```kotlin
// 1. Fragment-специфичные зависимости
class UserProfileLoader(
    private val userId: String,
    private val repository: UserRepository
) {
    suspend fun loadProfile(): Result<UserProfile> {
        return repository.getUserProfile(userId)
    }
}

class ProfileEditState {
    var hasUnsavedChanges: Boolean = false
    val pendingChanges: MutableMap<String, Any> = mutableMapOf()
}

// 2. Модуль с Fragment scope
val profileModule = module {
    single<UserRepository> { UserRepositoryImpl(get()) }

    scope<ProfileFragment> {
        scoped { (userId: String) ->
            UserProfileLoader(userId, get())
        }
        scoped { ProfileEditState() }
        scoped { ProfileValidator() }
    }
}

// 3. Fragment с scoped зависимостями
class ProfileFragment : Fragment() {

    private val scope: Scope by fragmentScope()

    private val userId: String by lazy {
        requireArguments().getString("user_id")!!
    }

    private val profileLoader: UserProfileLoader by scope.inject {
        parametersOf(userId)
    }

    private val editState: ProfileEditState by scope.inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        loadProfile()
    }

    override fun onDestroyView() {
        // Scope автоматически закрывается
        super.onDestroyView()
    }
}
```

### Разделение Scope между компонентами

```kotlin
// Activity создаёт и владеет scope
class MainActivity : AppCompatActivity() {

    private val scope: Scope by activityScope()
    private val navigationState: NavigationState by scope.inject()
    private val sharedViewModel: SharedViewModel by scope.inject()
}

// Fragment получает доступ к Activity scope
class HomeFragment : Fragment() {

    // Получить scope родительской Activity
    private val activityScope: Scope by activityRetainedScope()

    // Инъекция из Activity scope
    private val navigationState: NavigationState by activityScope.inject()
    private val sharedViewModel: SharedViewModel by activityScope.inject()
}
```

### Custom Named Scopes

```kotlin
val featureModule = module {
    // User session scope - живёт во время аутентификации
    scope(named("user_session")) {
        scoped { UserSession(get()) }
        scoped { AuthenticatedApiClient(get()) }
        scoped { UserPreferences(get()) }
    }
}

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

### Best Practices

1. **Соответствие Scope жизненному циклу** - время жизни scope должно соответствовать жизненному циклу компонента
2. **Избегать утечек памяти** - всегда закрывать scope
3. **Activity Scope для Fragments** - разделять состояние между стеком фрагментов
4. **Named Scopes для фич** - логическая группировка связанной функциональности
5. **Lazy Injection** - использовать `by inject()` для отложенной инстанциации
6. **Очистка ресурсов** - реализовывать cleanup в scoped классах
7. **Тестирование Scope** - проверять создание и уничтожение scope

### Резюме

Koin scopes предоставляют lifecycle-aware управление зависимостями:
- **Activity Scope** - для зависимостей уровня Activity
- **Fragment Scope** - для зависимостей уровня Fragment
- **Custom Scopes** - для логических границ (сессии, фичи)
- **Автоматическая очистка** - интеграция с Android lifecycle
- **Разделяемые Scopes** - коммуникация между компонентами
- **Безопасность памяти** - предотвращает утечки через правильную утилизацию

Используйте scopes для соответствия времени жизни зависимостей жизненному циклу компонентов, предотвращения утечек памяти и организации связанных зависимостей.

## Related Questions

- [[q-how-to-display-snackbar-or-toast-based-on-results--android--medium]]
- [[q-stable-classes-compose--android--hard]]
- [[q-what-methods-redraw-views--android--medium]]

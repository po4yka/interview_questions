---
id: "20251015082237373"
title: "Inject Router To Presenter / Инъекция Router в Presenter"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android/architecture-mvi, android/di-hilt, architecture-mvi, dagger/hilt, dependency-injection, di-hilt, koin, platform/android, difficulty/medium]
---
# How to inject Router directly into Presenter?

**Russian**: Что использовать для того чтобы роутер инжектился напрямую в презентер?

**English**: What to use to inject router directly into presenter?

## Answer (EN)
To inject a router into a presenter, use **Dependency Injection (DI)** frameworks:

1. **Hilt** (recommended) - Official Android DI
2. **Dagger 2** - Compile-time DI
3. **Koin** - Kotlin-first, runtime DI

This ensures:
- Loose coupling between presenter and router
- Easy unit testing with mock routers
- Single responsibility principle
- Inversion of control

---

## Implementation Examples

### 1. Hilt (Recommended)

#### Router Interface

```kotlin
interface Router {
    fun navigateToDetails(itemId: String)
    fun navigateToSettings()
    fun navigateBack()
}
```

#### Router Implementation

```kotlin
class AppRouter @Inject constructor(
    private val navController: NavController
) : Router {
    override fun navigateToDetails(itemId: String) {
        navController.navigate("details/$itemId")
    }

    override fun navigateToSettings() {
        navController.navigate("settings")
    }

    override fun navigateBack() {
        navController.popBackStack()
    }
}
```

#### Hilt Module

```kotlin
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {

    @Binds
    abstract fun bindRouter(
        appRouter: AppRouter
    ): Router
}

@Module
@InstallIn(ActivityComponent::class)
object NavigationProviderModule {

    @Provides
    fun provideNavController(
        activity: Activity
    ): NavController {
        val navHostFragment = (activity as MainActivity)
            .supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        return navHostFragment.navController
    }
}
```

#### Presenter with Injected Router

```kotlin
class ProductListPresenter @Inject constructor(
    private val router: Router,
    private val productRepository: ProductRepository
) {
    fun onProductClicked(productId: String) {
        router.navigateToDetails(productId)
    }

    fun onSettingsClicked() {
        router.navigateToSettings()
    }

    fun onBackPressed() {
        router.navigateBack()
    }
}
```

#### Fragment

```kotlin
@AndroidEntryPoint
class ProductListFragment : Fragment() {

    @Inject
    lateinit var presenter: ProductListPresenter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.productList.setOnItemClickListener { productId ->
            presenter.onProductClicked(productId)
        }
    }
}
```

---

### 2. Dagger 2

#### Router Interface

```kotlin
interface Router {
    fun openProfile(userId: String)
    fun openChat(chatId: String)
    fun goBack()
}
```

#### Router Implementation

```kotlin
class NavigationRouter @Inject constructor(
    @ActivityContext private val context: Context
) : Router {
    override fun openProfile(userId: String) {
        val intent = Intent(context, ProfileActivity::class.java).apply {
            putExtra("user_id", userId)
        }
        context.startActivity(intent)
    }

    override fun openChat(chatId: String) {
        val intent = Intent(context, ChatActivity::class.java).apply {
            putExtra("chat_id", chatId)
        }
        context.startActivity(intent)
    }

    override fun goBack() {
        (context as? Activity)?.onBackPressed()
    }
}
```

#### Dagger Component

```kotlin
@ActivityScope
@Component(
    dependencies = [AppComponent::class],
    modules = [ActivityModule::class, NavigationModule::class]
)
interface ActivityComponent {
    fun inject(activity: MainActivity)
    fun inject(fragment: HomeFragment)
}
```

#### Dagger Module

```kotlin
@Module
abstract class NavigationModule {

    @Binds
    @ActivityScope
    abstract fun bindRouter(
        navigationRouter: NavigationRouter
    ): Router
}

@Module
class ActivityModule(private val activity: Activity) {

    @Provides
    @ActivityContext
    fun provideActivityContext(): Context = activity
}
```

#### Presenter

```kotlin
class HomePresenter @Inject constructor(
    private val router: Router,
    private val userRepository: UserRepository
) {
    fun onUserClicked(userId: String) {
        router.openProfile(userId)
    }

    fun onChatClicked(chatId: String) {
        router.openChat(chatId)
    }
}
```

#### Activity

```kotlin
class MainActivity : AppCompatActivity() {

    @Inject
    lateinit var presenter: HomePresenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        DaggerActivityComponent.builder()
            .appComponent((application as MyApp).appComponent)
            .activityModule(ActivityModule(this))
            .build()
            .inject(this)
    }
}
```

---

### 3. Koin

#### Router Interface

```kotlin
interface Router {
    fun navigateToProductDetails(productId: String)
    fun navigateToCart()
    fun back()
}
```

#### Router Implementation

```kotlin
class NavigationRouter(
    private val findNavController: () -> NavController
) : Router {

    override fun navigateToProductDetails(productId: String) {
        findNavController().navigate(
            R.id.action_list_to_details,
            bundleOf("product_id" to productId)
        )
    }

    override fun navigateToCart() {
        findNavController().navigate(R.id.action_to_cart)
    }

    override fun back() {
        findNavController().popBackStack()
    }
}
```

#### Koin Module

```kotlin
val navigationModule = module {

    // Scoped to Activity
    scope<MainActivity> {
        scoped {
            NavigationRouter(
                findNavController = {
                    (getSource() as MainActivity).findNavController(R.id.nav_host_fragment)
                }
            ) as Router
        }
    }
}

val presenterModule = module {

    scope<ProductListFragment> {
        scoped {
            ProductListPresenter(
                router = get(), // Koin resolves Router
                productRepository = get()
            )
        }
    }
}
```

#### Presenter

```kotlin
class ProductListPresenter(
    private val router: Router,
    private val productRepository: ProductRepository
) {
    fun onProductSelected(productId: String) {
        router.navigateToProductDetails(productId)
    }

    fun onCartClicked() {
        router.navigateToCart()
    }
}
```

#### Fragment

```kotlin
class ProductListFragment : Fragment() {

    // Koin injection
    private val presenter: ProductListPresenter by inject()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.productList.setOnClickListener { productId ->
            presenter.onProductSelected(productId)
        }
    }
}
```

#### Application

```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            androidContext(this@MyApp)
            modules(navigationModule, presenterModule)
        }
    }
}
```

---

## Advanced Patterns

### Multi-Module Router

```kotlin
// Feature module interface
interface FeatureRouter {
    fun openFeature(params: FeatureParams)
}

// Main router delegates to feature routers
class AppRouter @Inject constructor(
    private val profileRouter: ProfileRouter,
    private val checkoutRouter: CheckoutRouter,
    private val settingsRouter: SettingsRouter
) : Router {

    fun navigateToProfile(userId: String) {
        profileRouter.openProfile(userId)
    }

    fun navigateToCheckout(cartId: String) {
        checkoutRouter.openCheckout(cartId)
    }

    fun navigateToSettings() {
        settingsRouter.openSettings()
    }
}

// Each feature has its own router
class ProfileRouter @Inject constructor(
    private val navController: NavController
) {
    fun openProfile(userId: String) {
        navController.navigate("profile/$userId")
    }

    fun openEditProfile() {
        navController.navigate("profile/edit")
    }
}
```

### Router with Result

```kotlin
interface Router {
    suspend fun navigateForResult(destination: String): NavigationResult
}

class AppRouter @Inject constructor(
    private val navController: NavController
) : Router {

    private val resultChannel = Channel<NavigationResult>(Channel.BUFFERED)

    override suspend fun navigateForResult(destination: String): NavigationResult {
        navController.navigate(destination)
        return resultChannel.receive()
    }

    fun setResult(result: NavigationResult) {
        resultChannel.trySend(result)
    }
}

// Usage in Presenter
class CheckoutPresenter @Inject constructor(
    private val router: Router
) {
    suspend fun selectPaymentMethod() {
        val result = router.navigateForResult("payment_methods")

        when (result) {
            is NavigationResult.PaymentMethodSelected -> {
                processPayment(result.paymentMethod)
            }
            is NavigationResult.Cancelled -> {
                // User cancelled
            }
        }
    }
}
```

### Router with Deep Link Support

```kotlin
interface Router {
    fun navigate(route: String)
    fun handleDeepLink(uri: Uri): Boolean
}

class DeepLinkRouter @Inject constructor(
    private val navController: NavController
) : Router {

    override fun navigate(route: String) {
        navController.navigate(route)
    }

    override fun handleDeepLink(uri: Uri): Boolean {
        return when (uri.host) {
            "product" -> {
                val productId = uri.lastPathSegment
                navController.navigate("product/$productId")
                true
            }
            "user" -> {
                val userId = uri.lastPathSegment
                navController.navigate("user/$userId")
                true
            }
            else -> false
        }
    }
}
```

---

## Testing with Mock Router

### Unit Test

```kotlin
class ProductListPresenterTest {

    private lateinit var presenter: ProductListPresenter
    private lateinit var mockRouter: Router
    private lateinit var mockRepository: ProductRepository

    @Before
    fun setup() {
        mockRouter = mockk(relaxed = true)
        mockRepository = mockk()

        presenter = ProductListPresenter(
            router = mockRouter,
            productRepository = mockRepository
        )
    }

    @Test
    fun `when product clicked, should navigate to details`() {
        // Given
        val productId = "product123"

        // When
        presenter.onProductClicked(productId)

        // Then
        verify { mockRouter.navigateToDetails(productId) }
    }

    @Test
    fun `when back pressed, should navigate back`() {
        // When
        presenter.onBackPressed()

        // Then
        verify { mockRouter.navigateBack() }
    }
}
```

### Fake Router for Tests

```kotlin
class FakeRouter : Router {
    val navigationHistory = mutableListOf<String>()

    override fun navigateToDetails(itemId: String) {
        navigationHistory.add("details/$itemId")
    }

    override fun navigateToSettings() {
        navigationHistory.add("settings")
    }

    override fun navigateBack() {
        if (navigationHistory.isNotEmpty()) {
            navigationHistory.removeLast()
        }
    }

    fun assertNavigatedTo(route: String) {
        assertTrue(navigationHistory.contains(route))
    }
}
```

---

## Comparison: Hilt vs Dagger vs Koin

| Feature | Hilt | Dagger 2 | Koin |
|---------|------|----------|------|
| **Setup** | Medium | Complex | Simple |
| **Compile-time** | Yes | Yes | No (runtime) |
| **Performance** | Fast | Fast | Slower |
| **Boilerplate** | Low | High | Very low |
| **Learning Curve** | Medium | Steep | Easy |
| **Android Support** | Native | Good | Native |
| **Testing** | Easy | Medium | Easy |
| **Multimodule** | Excellent | Good | Good |

---

## Best Practices

### 1. Use Interface for Router

```kotlin
// Good - testable, flexible
interface Router {
    fun navigate(destination: String)
}

// Bad - hard to test, coupled
class Presenter(private val navController: NavController) {
    // Directly coupled to NavController
}
```

### 2. Scope Router Appropriately

```kotlin
// Activity-scoped router
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {
    @Binds
    @ActivityScoped
    abstract fun bindRouter(impl: AppRouter): Router
}
```

### 3. Inject Constructor, Not Fields

```kotlin
// Good - clear dependencies
class Presenter @Inject constructor(
    private val router: Router
) {
    // Constructor injection
}

// Bad - hidden dependencies
class Presenter {
    @Inject
    lateinit var router: Router // Field injection
}
```

### 4. Use Qualifier for Multiple Routers

```kotlin
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainRouter

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class FeatureRouter

class Presenter @Inject constructor(
    @MainRouter private val mainRouter: Router,
    @FeatureRouter private val featureRouter: Router
) {
    // Multiple routers
}
```

---

## Summary

**To inject Router into Presenter:**

1. **Define Router interface** - abstracts navigation logic
2. **Implement Router** - uses NavController/Intent
3. **Configure DI framework**:
   - **Hilt**: `@Inject` constructor, `@Binds` in module
   - **Dagger**: Manual component setup
   - **Koin**: DSL-based module definition
4. **Inject into Presenter** - constructor injection
5. **Test with mocks** - easy unit testing

**Recommendation**: Use **Hilt** for new projects (official, less boilerplate, better Android integration).

---

## Ответ (RU)
Для внедрения роутера в презентер используйте **Dependency Injection (DI)**:

1. **Hilt** (рекомендуется) - официальный Android DI
2. **Dagger 2** - compile-time DI
3. **Koin** - Kotlin-first, runtime DI

### Пример с Hilt

```kotlin
// Интерфейс роутера
interface Router {
    fun navigateToDetails(itemId: String)
    fun navigateBack()
}

// Реализация роутера
class AppRouter @Inject constructor(
    private val navController: NavController
) : Router {
    override fun navigateToDetails(itemId: String) {
        navController.navigate("details/$itemId")
    }

    override fun navigateBack() {
        navController.popBackStack()
    }
}

// Модуль Hilt
@Module
@InstallIn(ActivityComponent::class)
abstract class NavigationModule {
    @Binds
    abstract fun bindRouter(appRouter: AppRouter): Router
}

// Презентер с инжектом
class ProductPresenter @Inject constructor(
    private val router: Router,
    private val repository: ProductRepository
) {
    fun onProductClicked(productId: String) {
        router.navigateToDetails(productId)
    }
}

// Fragment
@AndroidEntryPoint
class ProductListFragment : Fragment() {
    @Inject
    lateinit var presenter: ProductPresenter
}
```

### Пример с Koin

```kotlin
// Модуль Koin
val navigationModule = module {
    single<Router> {
        NavigationRouter(get())
    }
}

val presenterModule = module {
    factory {
        ProductPresenter(
            router = get(),
            repository = get()
        )
    }
}

// Презентер
class ProductPresenter(
    private val router: Router,
    private val repository: ProductRepository
) {
    fun onProductClicked(productId: String) {
        router.navigateToDetails(productId)
    }
}

// Fragment
class ProductListFragment : Fragment() {
    private val presenter: ProductPresenter by inject()
}
```

### Преимущества DI для роутеров:

1. **Слабая связанность** - презентер не зависит от реализации навигации
2. **Легкое тестирование** - можно подменить роутер на mock
3. **Single Responsibility** - презентер не знает о NavController/Intent
4. **Переиспользование** - один роутер для многих презентеров
5. **Изоляция модулей** - feature модули не зависят от основного модуля

### Тестирование с mock роутером

```kotlin
class ProductPresenterTest {
    private lateinit var presenter: ProductPresenter
    private val mockRouter = mockk<Router>(relaxed = true)

    @Before
    fun setup() {
        presenter = ProductPresenter(
            router = mockRouter,
            repository = mockRepository
        )
    }

    @Test
    fun `when product clicked, should navigate to details`() {
        val productId = "123"

        presenter.onProductClicked(productId)

        verify { mockRouter.navigateToDetails(productId) }
    }
}
```

**Рекомендация**: Используйте **Hilt** для новых проектов (официальный, меньше boilerplate, лучшая интеграция с Android)


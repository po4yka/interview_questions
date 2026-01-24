---
id: android-725
title: "Circuit Framework by Slack / Фреймворк Circuit от Slack"
aliases:
- Circuit
- Circuit Framework
- Slack Circuit
- Circuit for Compose
- Фреймворк Circuit
topic: android
subtopics:
- architecture
- compose-frameworks
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-mvi-architecture--android--hard
- q-orbit-mvi--architecture--medium
- q-jetpack-compose-basics--android--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- "https://slackhq.github.io/circuit/"
- "https://github.com/slackhq/circuit"
tags:
- android/architecture
- android/compose-frameworks
- difficulty/medium
- circuit
- compose
---
# Vopros (RU)

> Что такое Circuit от Slack? Как он упрощает разработку с Jetpack Compose?

# Question (EN)

> What is Circuit by Slack? How does it simplify Jetpack Compose development?

---

## Otvet (RU)

**Circuit** - архитектурный фреймворк от Slack для Jetpack Compose, который обеспечивает четкое разделение UI и бизнес-логики через паттерн Presenter-UI с type-safe навигацией.

### Ключевые концепции Circuit

| Компонент | Описание |
|-----------|----------|
| **Screen** | Type-safe идентификатор экрана с параметрами |
| **Presenter** | Бизнес-логика, возвращает State |
| **UI** | Stateless Composable, рендерит State |
| **Navigator** | Type-safe навигация между Screen |
| **Overlay** | Модальные окна, bottom sheets, dialogs |

### Установка (2026)

```kotlin
// build.gradle.kts
plugins {
    id("com.slack.circuit") version "1.0.0"
}

dependencies {
    implementation("com.slack.circuit:circuit-foundation:1.0.0")
    implementation("com.slack.circuit:circuit-overlay:1.0.0")

    // Code generation
    ksp("com.slack.circuit:circuit-codegen:1.0.0")
    implementation("com.slack.circuit:circuit-codegen-annotations:1.0.0")

    // Testing
    testImplementation("com.slack.circuit:circuit-test:1.0.0")
}
```

### Базовая структура

```kotlin
// 1. Screen - type-safe идентификатор
@Parcelize
data class ProductListScreen(
    val categoryId: String? = null
) : Screen {
    // State для этого экрана
    data class State(
        val products: List<Product> = emptyList(),
        val isLoading: Boolean = false,
        val error: String? = null,
        val eventSink: (Event) -> Unit = {}
    ) : CircuitUiState

    // Events от UI к Presenter
    sealed interface Event : CircuitUiEvent {
        data class ProductClicked(val productId: String) : Event
        data object RefreshClicked : Event
        data object RetryClicked : Event
    }
}

// 2. Presenter - бизнес-логика
class ProductListPresenter @AssistedInject constructor(
    @Assisted private val screen: ProductListScreen,
    @Assisted private val navigator: Navigator,
    private val productRepository: ProductRepository
) : Presenter<ProductListScreen.State> {

    @Composable
    override fun present(): ProductListScreen.State {
        // Используем Compose state management
        var products by remember { mutableStateOf<List<Product>>(emptyList()) }
        var isLoading by remember { mutableStateOf(false) }
        var error by remember { mutableStateOf<String?>(null) }

        // Загрузка данных
        LaunchedEffect(screen.categoryId) {
            isLoading = true
            error = null

            productRepository.getProducts(screen.categoryId)
                .onSuccess {
                    products = it
                    isLoading = false
                }
                .onFailure {
                    error = it.message
                    isLoading = false
                }
        }

        return ProductListScreen.State(
            products = products,
            isLoading = isLoading,
            error = error
        ) { event ->
            when (event) {
                is ProductListScreen.Event.ProductClicked -> {
                    navigator.goTo(ProductDetailScreen(event.productId))
                }
                is ProductListScreen.Event.RefreshClicked,
                is ProductListScreen.Event.RetryClicked -> {
                    // Trigger reload
                    isLoading = true
                    error = null
                }
            }
        }
    }

    @CircuitInject(ProductListScreen::class, AppScope::class)
    @AssistedFactory
    interface Factory {
        fun create(screen: ProductListScreen, navigator: Navigator): ProductListPresenter
    }
}

// 3. UI - stateless composable
@CircuitInject(ProductListScreen::class, AppScope::class)
@Composable
fun ProductListUi(
    state: ProductListScreen.State,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxSize()) {
        when {
            state.isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            state.error != null -> {
                ErrorView(
                    message = state.error,
                    onRetry = { state.eventSink(ProductListScreen.Event.RetryClicked) }
                )
            }
            state.products.isEmpty() -> {
                EmptyView(message = "No products found")
            }
            else -> {
                LazyColumn {
                    items(state.products, key = { it.id }) { product ->
                        ProductItem(
                            product = product,
                            onClick = {
                                state.eventSink(ProductListScreen.Event.ProductClicked(product.id))
                            }
                        )
                    }
                }
            }
        }
    }
}
```

### Type-Safe Navigation

```kotlin
// Screens с параметрами
@Parcelize
data class ProductDetailScreen(
    val productId: String
) : Screen {
    data class State(
        val product: Product? = null,
        val isLoading: Boolean = false,
        val eventSink: (Event) -> Unit = {}
    ) : CircuitUiState

    sealed interface Event : CircuitUiEvent {
        data object BackClicked : Event
        data object AddToCartClicked : Event
        data class ShareClicked(val product: Product) : Event
    }
}

// Presenter с навигацией
class ProductDetailPresenter @AssistedInject constructor(
    @Assisted private val screen: ProductDetailScreen,
    @Assisted private val navigator: Navigator,
    private val productRepository: ProductRepository,
    private val cartRepository: CartRepository
) : Presenter<ProductDetailScreen.State> {

    @Composable
    override fun present(): ProductDetailScreen.State {
        var product by remember { mutableStateOf<Product?>(null) }
        var isLoading by remember { mutableStateOf(true) }

        LaunchedEffect(screen.productId) {
            productRepository.getProduct(screen.productId)
                .onSuccess {
                    product = it
                    isLoading = false
                }
        }

        val coroutineScope = rememberCoroutineScope()

        return ProductDetailScreen.State(
            product = product,
            isLoading = isLoading
        ) { event ->
            when (event) {
                is ProductDetailScreen.Event.BackClicked -> {
                    navigator.pop()
                }
                is ProductDetailScreen.Event.AddToCartClicked -> {
                    product?.let { p ->
                        coroutineScope.launch {
                            cartRepository.addToCart(p.id)
                            // Navigate to cart
                            navigator.goTo(CartScreen)
                        }
                    }
                }
                is ProductDetailScreen.Event.ShareClicked -> {
                    // Handled via overlay
                    navigator.goTo(ShareOverlay(event.product))
                }
            }
        }
    }
}
```

### Overlays (Модальные окна)

```kotlin
// Overlay Screen
@Parcelize
data class ConfirmPurchaseOverlay(
    val product: Product,
    val quantity: Int
) : Overlay<ConfirmPurchaseOverlay.Result> {

    sealed interface Result : OverlayResult {
        data object Confirmed : Result
        data object Cancelled : Result
    }

    data class State(
        val product: Product,
        val quantity: Int,
        val totalPrice: Double,
        val eventSink: (Event) -> Unit = {}
    ) : CircuitUiState

    sealed interface Event : CircuitUiEvent {
        data object ConfirmClicked : Event
        data object CancelClicked : Event
    }
}

// Overlay Presenter
class ConfirmPurchasePresenter @AssistedInject constructor(
    @Assisted private val overlay: ConfirmPurchaseOverlay,
    @Assisted private val navigator: OverlayNavigator<ConfirmPurchaseOverlay.Result>
) : Presenter<ConfirmPurchaseOverlay.State> {

    @Composable
    override fun present(): ConfirmPurchaseOverlay.State {
        return ConfirmPurchaseOverlay.State(
            product = overlay.product,
            quantity = overlay.quantity,
            totalPrice = overlay.product.price * overlay.quantity
        ) { event ->
            when (event) {
                is ConfirmPurchaseOverlay.Event.ConfirmClicked -> {
                    navigator.finish(ConfirmPurchaseOverlay.Result.Confirmed)
                }
                is ConfirmPurchaseOverlay.Event.CancelClicked -> {
                    navigator.finish(ConfirmPurchaseOverlay.Result.Cancelled)
                }
            }
        }
    }
}

// Overlay UI
@CircuitInject(ConfirmPurchaseOverlay::class, AppScope::class)
@Composable
fun ConfirmPurchaseUi(
    state: ConfirmPurchaseOverlay.State,
    modifier: Modifier = Modifier
) {
    BottomSheetScaffold(
        modifier = modifier,
        sheetContent = {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Confirm Purchase", style = MaterialTheme.typography.headlineSmall)

                Spacer(modifier = Modifier.height(16.dp))

                Text("${state.product.name} x ${state.quantity}")
                Text("Total: $${state.totalPrice}", style = MaterialTheme.typography.titleLarge)

                Spacer(modifier = Modifier.height(24.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = { state.eventSink(ConfirmPurchaseOverlay.Event.CancelClicked) },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Cancel")
                    }

                    Button(
                        onClick = { state.eventSink(ConfirmPurchaseOverlay.Event.ConfirmClicked) },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Confirm")
                    }
                }
            }
        }
    ) {
        // Content behind sheet
    }
}

// Использование overlay в presenter
class CheckoutPresenter(...) : Presenter<CheckoutScreen.State> {

    @Composable
    override fun present(): CheckoutScreen.State {
        val overlayHost = LocalOverlayHost.current
        val coroutineScope = rememberCoroutineScope()

        return CheckoutScreen.State(...) { event ->
            when (event) {
                is CheckoutScreen.Event.PurchaseClicked -> {
                    coroutineScope.launch {
                        // Show overlay and wait for result
                        val result = overlayHost.show(
                            ConfirmPurchaseOverlay(event.product, event.quantity)
                        )

                        when (result) {
                            is ConfirmPurchaseOverlay.Result.Confirmed -> {
                                // Process purchase
                            }
                            is ConfirmPurchaseOverlay.Result.Cancelled -> {
                                // Do nothing
                            }
                        }
                    }
                }
            }
        }
    }
}
```

### Настройка Circuit

```kotlin
// Application setup
@HiltAndroidApp
class MyApplication : Application() {

    @Inject
    lateinit var circuit: Circuit

    override fun onCreate() {
        super.onCreate()
    }
}

// Hilt module
@Module
@InstallIn(SingletonComponent::class)
object CircuitModule {

    @Provides
    @Singleton
    fun provideCircuit(
        presenterFactories: @JvmSuppressWildcards Set<Presenter.Factory>,
        uiFactories: @JvmSuppressWildcards Set<Ui.Factory>
    ): Circuit {
        return Circuit.Builder()
            .addPresenterFactories(presenterFactories)
            .addUiFactories(uiFactories)
            .build()
    }
}

// MainActivity
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var circuit: Circuit

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MyTheme {
                val backStack = rememberSaveableBackStack(root = ProductListScreen())
                val navigator = rememberCircuitNavigator(backStack)

                CircuitCompositionLocals(circuit) {
                    NavigableCircuitContent(
                        navigator = navigator,
                        backStack = backStack
                    )
                }
            }
        }
    }
}
```

### Тестирование

```kotlin
class ProductListPresenterTest {

    @Test
    fun `initial load fetches products`() = runTest {
        // Given
        val products = listOf(Product("1", "Product 1"))
        val repository = mockk<ProductRepository> {
            coEvery { getProducts(any()) } returns Result.success(products)
        }

        val presenter = ProductListPresenter(
            screen = ProductListScreen(),
            navigator = FakeNavigator(),
            productRepository = repository
        )

        // When
        moleculeFlow(RecompositionMode.Immediate) {
            presenter.present()
        }.test {
            // Then
            // Initial loading state
            awaitItem().also { state ->
                assertTrue(state.isLoading)
                assertTrue(state.products.isEmpty())
            }

            // Loaded state
            awaitItem().also { state ->
                assertFalse(state.isLoading)
                assertEquals(products, state.products)
            }
        }
    }

    @Test
    fun `product clicked navigates to detail`() = runTest {
        val navigator = FakeNavigator()
        val presenter = ProductListPresenter(
            screen = ProductListScreen(),
            navigator = navigator,
            productRepository = mockk(relaxed = true)
        )

        moleculeFlow(RecompositionMode.Immediate) {
            presenter.present()
        }.test {
            val state = awaitItem()

            // Trigger event
            state.eventSink(ProductListScreen.Event.ProductClicked("product-123"))

            // Verify navigation
            assertEquals(
                ProductDetailScreen("product-123"),
                navigator.awaitNextScreen()
            )
        }
    }
}

// UI testing
class ProductListUiTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `shows loading indicator when loading`() {
        composeTestRule.setContent {
            ProductListUi(
                state = ProductListScreen.State(isLoading = true)
            )
        }

        composeTestRule
            .onNodeWithTag("loading_indicator")
            .assertIsDisplayed()
    }

    @Test
    fun `shows products when loaded`() {
        val products = listOf(
            Product("1", "Product 1"),
            Product("2", "Product 2")
        )

        composeTestRule.setContent {
            ProductListUi(
                state = ProductListScreen.State(products = products)
            )
        }

        composeTestRule.onNodeWithText("Product 1").assertIsDisplayed()
        composeTestRule.onNodeWithText("Product 2").assertIsDisplayed()
    }

    @Test
    fun `clicking product triggers event`() {
        var clickedProductId: String? = null
        val products = listOf(Product("1", "Product 1"))

        composeTestRule.setContent {
            ProductListUi(
                state = ProductListScreen.State(
                    products = products,
                    eventSink = { event ->
                        if (event is ProductListScreen.Event.ProductClicked) {
                            clickedProductId = event.productId
                        }
                    }
                )
            )
        }

        composeTestRule.onNodeWithText("Product 1").performClick()

        assertEquals("1", clickedProductId)
    }
}
```

### Circuit vs другие подходы

| Аспект | Circuit | Orbit MVI | Manual MVVM |
|--------|---------|-----------|-------------|
| **Compose-first** | Да | Адаптация | Адаптация |
| **Type-safe навигация** | Да | Нет | Нет |
| **Overlays** | Встроено | Нет | Ручная реализация |
| **Presenter/UI разделение** | Принудительное | На усмотрение | На усмотрение |
| **Тестируемость** | Отличная | Хорошая | Зависит от реализации |
| **Boilerplate** | Средний | Низкий | Высокий |

---

## Answer (EN)

**Circuit** is an architectural framework from Slack for Jetpack Compose that provides clear separation between UI and business logic through the Presenter-UI pattern with type-safe navigation.

### Key Concepts

| Component | Description |
|-----------|-------------|
| **Screen** | Type-safe screen identifier with parameters |
| **Presenter** | Business logic, returns State |
| **UI** | Stateless Composable, renders State |
| **Navigator** | Type-safe navigation between Screens |
| **Overlay** | Modal windows, bottom sheets, dialogs |

### Setup (2026)

```kotlin
plugins {
    id("com.slack.circuit") version "1.0.0"
}

dependencies {
    implementation("com.slack.circuit:circuit-foundation:1.0.0")
    implementation("com.slack.circuit:circuit-overlay:1.0.0")
    ksp("com.slack.circuit:circuit-codegen:1.0.0")
    testImplementation("com.slack.circuit:circuit-test:1.0.0")
}
```

### Basic Structure

```kotlin
// 1. Screen - type-safe identifier
@Parcelize
data class ProductListScreen(val categoryId: String? = null) : Screen {
    data class State(
        val products: List<Product> = emptyList(),
        val isLoading: Boolean = false,
        val eventSink: (Event) -> Unit = {}
    ) : CircuitUiState

    sealed interface Event : CircuitUiEvent {
        data class ProductClicked(val productId: String) : Event
    }
}

// 2. Presenter - business logic
class ProductListPresenter @AssistedInject constructor(
    @Assisted private val screen: ProductListScreen,
    @Assisted private val navigator: Navigator,
    private val productRepository: ProductRepository
) : Presenter<ProductListScreen.State> {

    @Composable
    override fun present(): ProductListScreen.State {
        var products by remember { mutableStateOf<List<Product>>(emptyList()) }
        var isLoading by remember { mutableStateOf(false) }

        LaunchedEffect(screen.categoryId) {
            isLoading = true
            productRepository.getProducts(screen.categoryId)
                .onSuccess {
                    products = it
                    isLoading = false
                }
        }

        return ProductListScreen.State(
            products = products,
            isLoading = isLoading
        ) { event ->
            when (event) {
                is ProductListScreen.Event.ProductClicked -> {
                    navigator.goTo(ProductDetailScreen(event.productId))
                }
            }
        }
    }
}

// 3. UI - stateless composable
@CircuitInject(ProductListScreen::class, AppScope::class)
@Composable
fun ProductListUi(state: ProductListScreen.State, modifier: Modifier = Modifier) {
    // Render based on state
    LazyColumn(modifier = modifier) {
        items(state.products) { product ->
            ProductItem(
                product = product,
                onClick = { state.eventSink(ProductListScreen.Event.ProductClicked(product.id)) }
            )
        }
    }
}
```

### Type-Safe Navigation

```kotlin
// Navigate with type-safe parameters
navigator.goTo(ProductDetailScreen(productId = "123"))
navigator.pop()

// Overlays with results
val result = overlayHost.show(ConfirmPurchaseOverlay(product, quantity))
when (result) {
    is Result.Confirmed -> { /* process */ }
    is Result.Cancelled -> { /* cancel */ }
}
```

### Testing

```kotlin
@Test
fun `product clicked navigates to detail`() = runTest {
    val navigator = FakeNavigator()
    val presenter = ProductListPresenter(screen, navigator, repository)

    moleculeFlow(RecompositionMode.Immediate) {
        presenter.present()
    }.test {
        val state = awaitItem()
        state.eventSink(ProductListScreen.Event.ProductClicked("123"))

        assertEquals(ProductDetailScreen("123"), navigator.awaitNextScreen())
    }
}
```

---

## Follow-ups

- How does Circuit handle deep linking?
- What are the trade-offs of Circuit's Presenter pattern vs ViewModel?
- How do you handle shared state across multiple screens in Circuit?
- Can Circuit be used with Kotlin Multiplatform?

## References

- https://slackhq.github.io/circuit/
- https://github.com/slackhq/circuit

## Related Questions

### Prerequisites

- [[q-jetpack-compose-basics--android--medium]] - Compose basics
- [[q-mvi-architecture--android--hard]] - MVI pattern

### Related

- [[q-orbit-mvi--architecture--medium]] - Orbit MVI
- [[q-state-hoisting-compose--android--medium]] - State hoisting

### Advanced

- [[q-mvi-pattern--architecture--hard]] - MVI components
- [[q-state-machines--architecture--hard]] - FSM for UI

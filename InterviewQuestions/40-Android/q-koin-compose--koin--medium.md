---
id: android-koin-007
title: Koin with Jetpack Compose / Koin с Jetpack Compose
aliases:
- Koin Compose
- koinViewModel
- koinInject
topic: android
subtopics:
- di-koin
- ui-compose
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
- q-koin-viewmodel--koin--medium
- q-jetpack-compose-basics--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-koin
- android/ui-compose
- dependency-injection
- difficulty/medium
- koin
anki_cards:
- slug: android-koin-007-0-en
  language: en
- slug: android-koin-007-0-ru
  language: ru
---
# Vopros (RU)
> Как интегрировать Koin с Jetpack Compose? Объясните koinViewModel, koinInject и best practices.

# Question (EN)
> How do you integrate Koin with Jetpack Compose? Explain koinViewModel, koinInject, and best practices.

---

## Otvet (RU)

Koin предоставляет специальные Composable-функции для интеграции с Jetpack Compose: `koinViewModel()`, `koinInject()`, и другие.

### Подключение зависимостей

```kotlin
// build.gradle.kts
dependencies {
    // Koin Core
    implementation("io.insert-koin:koin-android:3.5.6")

    // Koin Compose - ОБЯЗАТЕЛЬНО для Compose интеграции
    implementation("io.insert-koin:koin-androidx-compose:3.5.6")

    // Navigation Compose (опционально)
    implementation("io.insert-koin:koin-androidx-compose-navigation:3.5.6")
}
```

### koinViewModel() - ViewModel в Compose

```kotlin
val viewModelModule = module {
    viewModel { HomeViewModel(get()) }
    viewModel { ProfileViewModel(get(), get()) }
    viewModel { (userId: String) -> UserDetailViewModel(userId, get()) }
}

@Composable
fun HomeScreen() {
    // Получение ViewModel через koinViewModel()
    val viewModel: HomeViewModel = koinViewModel()

    val state by viewModel.state.collectAsStateWithLifecycle()

    HomeContent(
        state = state,
        onRefresh = viewModel::refresh,
        onItemClick = viewModel::selectItem
    )
}

@Composable
fun ProfileScreen() {
    val viewModel: ProfileViewModel = koinViewModel()

    // ViewModel автоматически привязана к NavBackStackEntry или Activity
    ProfileContent(viewModel)
}
```

### koinViewModel() с параметрами

```kotlin
@Composable
fun UserDetailScreen(userId: String) {
    // ViewModel с runtime параметром
    val viewModel: UserDetailViewModel = koinViewModel {
        parametersOf(userId)
    }

    val user by viewModel.user.collectAsStateWithLifecycle()

    UserDetailContent(user)
}

// Из NavHost
@Composable
fun AppNavigation() {
    NavHost(navController, startDestination = "home") {
        composable("home") { HomeScreen() }

        composable(
            route = "user/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            UserDetailScreen(userId = userId)
        }
    }
}
```

### koinInject() - Любые зависимости

```kotlin
val appModule = module {
    single { Analytics() }
    single { ImageLoader() }
    factory { DateFormatter() }
}

@Composable
fun PhotoGallery() {
    // Инъекция любой зависимости (не только ViewModel)
    val imageLoader: ImageLoader = koinInject()
    val analytics: Analytics = koinInject()

    LaunchedEffect(Unit) {
        analytics.trackScreenView("PhotoGallery")
    }

    GalleryContent(imageLoader)
}
```

### KoinContext для всего приложения

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            androidLogger(Level.DEBUG)
            androidContext(this@MyApplication)
            modules(appModules)
        }
    }
}

// MainActivity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            // Koin уже запущен в Application
            MyApp()
        }
    }
}

@Composable
fun MyApp() {
    MaterialTheme {
        // Все @Composable внутри имеют доступ к Koin
        val viewModel: MainViewModel = koinViewModel()
        MainScreen(viewModel)
    }
}
```

### Navigation с Koin

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            // ViewModel привязана к этому NavBackStackEntry
            val viewModel: HomeViewModel = koinViewModel()
            HomeScreen(viewModel, navController)
        }

        composable("settings") {
            val viewModel: SettingsViewModel = koinViewModel()
            SettingsScreen(viewModel)
        }

        // Вложенный граф навигации
        navigation(
            startDestination = "checkout/cart",
            route = "checkout"
        ) {
            composable("checkout/cart") { entry ->
                // Shared ViewModel для всего checkout flow
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                CartScreen(viewModel, navController)
            }

            composable("checkout/payment") { entry ->
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                // Тот же экземпляр CheckoutViewModel
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                PaymentScreen(viewModel, navController)
            }

            composable("checkout/confirmation") { entry ->
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                ConfirmationScreen(viewModel)
            }
        }
    }
}
```

### Scopes в Compose

```kotlin
val featureModule = module {
    // Feature scope
    scope(named("feature_x")) {
        scoped { FeatureRepository() }
        scoped { FeatureService(get()) }
        viewModel { FeatureViewModel(get(), get()) }
    }
}

@Composable
fun FeatureScreen() {
    // Создаем и управляем scope
    val scope = remember {
        getKoin().createScope("feature_scope", named("feature_x"))
    }

    // Очищаем scope при выходе из Composition
    DisposableEffect(Unit) {
        onDispose {
            scope.close()
        }
    }

    // Получаем ViewModel из scope
    val viewModel: FeatureViewModel = koinViewModel(scope = scope)

    FeatureContent(viewModel)
}
```

### Compose Preview с Koin

```kotlin
// Для работы Preview создаем mock-модуль
val previewModule = module {
    single<UserRepository> { FakeUserRepository() }
    viewModel { UserViewModel(get()) }
}

@Preview
@Composable
fun UserScreenPreview() {
    // Изолированный Koin для Preview
    KoinApplication(application = {
        modules(previewModule)
    }) {
        MaterialTheme {
            val viewModel: UserViewModel = koinViewModel()
            UserScreen(viewModel)
        }
    }
}

// Или создаем Preview-specific composable
@Composable
fun UserScreenContent(
    state: UserState,
    onAction: (UserAction) -> Unit
) {
    // Stateless UI компонент
}

@Preview
@Composable
fun UserScreenContentPreview() {
    MaterialTheme {
        UserScreenContent(
            state = UserState(user = User("1", "Preview User")),
            onAction = {}
        )
    }
}
```

### CompositionLocal для Koin

```kotlin
// Кастомный CompositionLocal для специфичных зависимостей
val LocalAnalytics = compositionLocalOf<Analytics> {
    error("Analytics not provided")
}

@Composable
fun AppWithAnalytics() {
    val analytics: Analytics = koinInject()

    CompositionLocalProvider(LocalAnalytics provides analytics) {
        MainContent()
    }
}

@Composable
fun SomeDeepComponent() {
    // Доступ через CompositionLocal
    val analytics = LocalAnalytics.current
    analytics.trackEvent("deep_component_shown")
}
```

### Полный пример: Feature Screen

```kotlin
// Module
val productModule = module {
    single<ProductRepository> { ProductRepositoryImpl(get()) }
    viewModel { (productId: String) ->
        ProductDetailViewModel(productId, get())
    }
}

// ViewModel
class ProductDetailViewModel(
    private val productId: String,
    private val repository: ProductRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ProductState())
    val state: StateFlow<ProductState> = _state.asStateFlow()

    init {
        loadProduct()
    }

    private fun loadProduct() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val product = repository.getProduct(productId)
                _state.update { it.copy(product = product, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }

    fun addToCart() {
        viewModelScope.launch {
            repository.addToCart(productId)
            _state.update { it.copy(addedToCart = true) }
        }
    }
}

data class ProductState(
    val product: Product? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val addedToCart: Boolean = false
)

// Screen
@Composable
fun ProductDetailScreen(
    productId: String,
    onNavigateBack: () -> Unit,
    onNavigateToCart: () -> Unit
) {
    val viewModel: ProductDetailViewModel = koinViewModel {
        parametersOf(productId)
    }
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(state.addedToCart) {
        if (state.addedToCart) {
            onNavigateToCart()
        }
    }

    ProductDetailContent(
        state = state,
        onAddToCart = viewModel::addToCart,
        onBack = onNavigateBack
    )
}

@Composable
fun ProductDetailContent(
    state: ProductState,
    onAddToCart: () -> Unit,
    onBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(state.product?.name ?: "") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { padding ->
        when {
            state.isLoading -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            }
            state.error != null -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("Error: ${state.error}")
                }
            }
            state.product != null -> {
                Column(
                    modifier = Modifier
                        .padding(padding)
                        .padding(16.dp)
                ) {
                    Text(
                        state.product.name,
                        style = MaterialTheme.typography.headlineMedium
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        "$${state.product.price}",
                        style = MaterialTheme.typography.titleLarge
                    )
                    Spacer(Modifier.height(16.dp))
                    Text(state.product.description)
                    Spacer(Modifier.weight(1f))
                    Button(
                        onClick = onAddToCart,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Add to Cart")
                    }
                }
            }
        }
    }
}
```

### Лучшие практики

1. **koinViewModel() вместо by viewModel()** в Compose
2. **Stateless composables** - отделяйте UI от ViewModel
3. **Preview-friendly** - создавайте Content composables без ViewModel
4. **Scope lifecycle** - используйте DisposableEffect для закрытия scopes
5. **Navigation scoping** - используйте viewModelStoreOwner для shared ViewModels
6. **KoinApplication** - для изолированных Preview

```kotlin
// Хорошая структура
@Composable
fun FeatureScreen() {
    val viewModel: FeatureViewModel = koinViewModel()
    val state by viewModel.state.collectAsStateWithLifecycle()

    FeatureContent(state = state, onAction = viewModel::handleAction)
}

@Composable
fun FeatureContent(state: FeatureState, onAction: (Action) -> Unit) {
    // Чистый UI без зависимостей - легко тестировать и preview
}
```

---

## Answer (EN)

Koin provides special Composable functions for Jetpack Compose integration: `koinViewModel()`, `koinInject()`, and others.

### Adding Dependencies

```kotlin
// build.gradle.kts
dependencies {
    // Koin Core
    implementation("io.insert-koin:koin-android:3.5.6")

    // Koin Compose - REQUIRED for Compose integration
    implementation("io.insert-koin:koin-androidx-compose:3.5.6")

    // Navigation Compose (optional)
    implementation("io.insert-koin:koin-androidx-compose-navigation:3.5.6")
}
```

### koinViewModel() - ViewModel in Compose

```kotlin
val viewModelModule = module {
    viewModel { HomeViewModel(get()) }
    viewModel { ProfileViewModel(get(), get()) }
    viewModel { (userId: String) -> UserDetailViewModel(userId, get()) }
}

@Composable
fun HomeScreen() {
    // Get ViewModel via koinViewModel()
    val viewModel: HomeViewModel = koinViewModel()

    val state by viewModel.state.collectAsStateWithLifecycle()

    HomeContent(
        state = state,
        onRefresh = viewModel::refresh,
        onItemClick = viewModel::selectItem
    )
}

@Composable
fun ProfileScreen() {
    val viewModel: ProfileViewModel = koinViewModel()

    // ViewModel automatically scoped to NavBackStackEntry or Activity
    ProfileContent(viewModel)
}
```

### koinViewModel() with Parameters

```kotlin
@Composable
fun UserDetailScreen(userId: String) {
    // ViewModel with runtime parameter
    val viewModel: UserDetailViewModel = koinViewModel {
        parametersOf(userId)
    }

    val user by viewModel.user.collectAsStateWithLifecycle()

    UserDetailContent(user)
}

// From NavHost
@Composable
fun AppNavigation() {
    NavHost(navController, startDestination = "home") {
        composable("home") { HomeScreen() }

        composable(
            route = "user/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            UserDetailScreen(userId = userId)
        }
    }
}
```

### koinInject() - Any Dependencies

```kotlin
val appModule = module {
    single { Analytics() }
    single { ImageLoader() }
    factory { DateFormatter() }
}

@Composable
fun PhotoGallery() {
    // Inject any dependency (not just ViewModel)
    val imageLoader: ImageLoader = koinInject()
    val analytics: Analytics = koinInject()

    LaunchedEffect(Unit) {
        analytics.trackScreenView("PhotoGallery")
    }

    GalleryContent(imageLoader)
}
```

### KoinContext for Entire Application

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        startKoin {
            androidLogger(Level.DEBUG)
            androidContext(this@MyApplication)
            modules(appModules)
        }
    }
}

// MainActivity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            // Koin already started in Application
            MyApp()
        }
    }
}

@Composable
fun MyApp() {
    MaterialTheme {
        // All @Composable inside have access to Koin
        val viewModel: MainViewModel = koinViewModel()
        MainScreen(viewModel)
    }
}
```

### Navigation with Koin

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            // ViewModel scoped to this NavBackStackEntry
            val viewModel: HomeViewModel = koinViewModel()
            HomeScreen(viewModel, navController)
        }

        composable("settings") {
            val viewModel: SettingsViewModel = koinViewModel()
            SettingsScreen(viewModel)
        }

        // Nested navigation graph
        navigation(
            startDestination = "checkout/cart",
            route = "checkout"
        ) {
            composable("checkout/cart") { entry ->
                // Shared ViewModel for entire checkout flow
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                CartScreen(viewModel, navController)
            }

            composable("checkout/payment") { entry ->
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                // Same CheckoutViewModel instance
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                PaymentScreen(viewModel, navController)
            }

            composable("checkout/confirmation") { entry ->
                val parentEntry = remember(entry) {
                    navController.getBackStackEntry("checkout")
                }
                val viewModel: CheckoutViewModel = koinViewModel(
                    viewModelStoreOwner = parentEntry
                )
                ConfirmationScreen(viewModel)
            }
        }
    }
}
```

### Scopes in Compose

```kotlin
val featureModule = module {
    // Feature scope
    scope(named("feature_x")) {
        scoped { FeatureRepository() }
        scoped { FeatureService(get()) }
        viewModel { FeatureViewModel(get(), get()) }
    }
}

@Composable
fun FeatureScreen() {
    // Create and manage scope
    val scope = remember {
        getKoin().createScope("feature_scope", named("feature_x"))
    }

    // Clean up scope when leaving Composition
    DisposableEffect(Unit) {
        onDispose {
            scope.close()
        }
    }

    // Get ViewModel from scope
    val viewModel: FeatureViewModel = koinViewModel(scope = scope)

    FeatureContent(viewModel)
}
```

### Compose Preview with Koin

```kotlin
// For Preview to work, create mock module
val previewModule = module {
    single<UserRepository> { FakeUserRepository() }
    viewModel { UserViewModel(get()) }
}

@Preview
@Composable
fun UserScreenPreview() {
    // Isolated Koin for Preview
    KoinApplication(application = {
        modules(previewModule)
    }) {
        MaterialTheme {
            val viewModel: UserViewModel = koinViewModel()
            UserScreen(viewModel)
        }
    }
}

// Or create Preview-specific composable
@Composable
fun UserScreenContent(
    state: UserState,
    onAction: (UserAction) -> Unit
) {
    // Stateless UI component
}

@Preview
@Composable
fun UserScreenContentPreview() {
    MaterialTheme {
        UserScreenContent(
            state = UserState(user = User("1", "Preview User")),
            onAction = {}
        )
    }
}
```

### CompositionLocal for Koin

```kotlin
// Custom CompositionLocal for specific dependencies
val LocalAnalytics = compositionLocalOf<Analytics> {
    error("Analytics not provided")
}

@Composable
fun AppWithAnalytics() {
    val analytics: Analytics = koinInject()

    CompositionLocalProvider(LocalAnalytics provides analytics) {
        MainContent()
    }
}

@Composable
fun SomeDeepComponent() {
    // Access via CompositionLocal
    val analytics = LocalAnalytics.current
    analytics.trackEvent("deep_component_shown")
}
```

### Complete Example: Feature Screen

```kotlin
// Module
val productModule = module {
    single<ProductRepository> { ProductRepositoryImpl(get()) }
    viewModel { (productId: String) ->
        ProductDetailViewModel(productId, get())
    }
}

// ViewModel
class ProductDetailViewModel(
    private val productId: String,
    private val repository: ProductRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ProductState())
    val state: StateFlow<ProductState> = _state.asStateFlow()

    init {
        loadProduct()
    }

    private fun loadProduct() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val product = repository.getProduct(productId)
                _state.update { it.copy(product = product, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }

    fun addToCart() {
        viewModelScope.launch {
            repository.addToCart(productId)
            _state.update { it.copy(addedToCart = true) }
        }
    }
}

data class ProductState(
    val product: Product? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val addedToCart: Boolean = false
)

// Screen
@Composable
fun ProductDetailScreen(
    productId: String,
    onNavigateBack: () -> Unit,
    onNavigateToCart: () -> Unit
) {
    val viewModel: ProductDetailViewModel = koinViewModel {
        parametersOf(productId)
    }
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(state.addedToCart) {
        if (state.addedToCart) {
            onNavigateToCart()
        }
    }

    ProductDetailContent(
        state = state,
        onAddToCart = viewModel::addToCart,
        onBack = onNavigateBack
    )
}

@Composable
fun ProductDetailContent(
    state: ProductState,
    onAddToCart: () -> Unit,
    onBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(state.product?.name ?: "") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { padding ->
        when {
            state.isLoading -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            }
            state.error != null -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("Error: ${state.error}")
                }
            }
            state.product != null -> {
                Column(
                    modifier = Modifier
                        .padding(padding)
                        .padding(16.dp)
                ) {
                    Text(
                        state.product.name,
                        style = MaterialTheme.typography.headlineMedium
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        "$${state.product.price}",
                        style = MaterialTheme.typography.titleLarge
                    )
                    Spacer(Modifier.height(16.dp))
                    Text(state.product.description)
                    Spacer(Modifier.weight(1f))
                    Button(
                        onClick = onAddToCart,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Add to Cart")
                    }
                }
            }
        }
    }
}
```

### Best Practices

1. **koinViewModel() instead of by viewModel()** in Compose
2. **Stateless composables** - separate UI from ViewModel
3. **Preview-friendly** - create Content composables without ViewModel
4. **Scope lifecycle** - use DisposableEffect to close scopes
5. **Navigation scoping** - use viewModelStoreOwner for shared ViewModels
6. **KoinApplication** - for isolated Preview

```kotlin
// Good structure
@Composable
fun FeatureScreen() {
    val viewModel: FeatureViewModel = koinViewModel()
    val state by viewModel.state.collectAsStateWithLifecycle()

    FeatureContent(state = state, onAction = viewModel::handleAction)
}

@Composable
fun FeatureContent(state: FeatureState, onAction: (Action) -> Unit) {
    // Pure UI without dependencies - easy to test and preview
}
```

---

## Dopolnitelnye Voprosy (RU)

- Как правильно тестировать Compose экраны с Koin?
- В чем разница между koinInject() и CompositionLocal для зависимостей?
- Как управлять lifecycle scopes в Compose Navigation?

## Follow-ups

- How do you properly test Compose screens with Koin?
- What is the difference between koinInject() and CompositionLocal for dependencies?
- How do you manage lifecycle scopes in Compose Navigation?

## Ssylki (RU)

- [Koin Compose](https://insert-koin.io/docs/reference/koin-compose/compose)
- [Koin Compose Navigation](https://insert-koin.io/docs/reference/koin-compose/compose-navigation)

## References

- [Koin Compose](https://insert-koin.io/docs/reference/koin-compose/compose)
- [Koin Compose Navigation](https://insert-koin.io/docs/reference/koin-compose/compose-navigation)

## Svyazannye Voprosy (RU)

### Medium
- [[q-koin-viewmodel--koin--medium]]
- [[q-koin-scopes--koin--medium]]
- [[q-jetpack-compose-basics--android--medium]]

## Related Questions

### Medium
- [[q-koin-viewmodel--koin--medium]]
- [[q-koin-scopes--koin--medium]]
- [[q-jetpack-compose-basics--android--medium]]

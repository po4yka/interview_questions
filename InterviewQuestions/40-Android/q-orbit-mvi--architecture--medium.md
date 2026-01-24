---
id: android-724
title: "Orbit MVI Library / Библиотека Orbit MVI"
aliases:
- Orbit MVI
- Orbit Framework
- Orbit for Android
- Библиотека Orbit
topic: android
subtopics:
- architecture
- mvi-frameworks
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
- q-mvi-pattern--architecture--hard
- q-side-effects-architecture--architecture--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- "https://orbit-mvi.org/"
- "https://github.com/orbit-mvi/orbit-mvi"
tags:
- android/architecture
- android/mvi-frameworks
- difficulty/medium
- orbit-mvi
---
# Vopros (RU)

> Что такое Orbit MVI? Как он упрощает реализацию MVI паттерна в Android?

# Question (EN)

> What is Orbit MVI? How does it simplify MVI pattern implementation in Android?

---

## Otvet (RU)

**Orbit MVI** - легковесный MVI фреймворк для Kotlin/Android, который предоставляет структурированный DSL для управления состоянием и side effects с минимальным boilerplate.

### Почему Orbit?

| Преимущество | Описание |
|--------------|----------|
| **Минимум boilerplate** | DSL вместо ручного управления Flow |
| **Встроенные side effects** | `postSideEffect()` из коробки |
| **Compose интеграция** | `collectAsState()`, `collectSideEffect()` |
| **Тестирование** | Встроенный test DSL |
| **Type-safe** | Полная типизация state и effects |

### Установка (2026)

```kotlin
// build.gradle.kts
dependencies {
    // Core
    implementation("org.orbit-mvi:orbit-core:8.0.0")
    implementation("org.orbit-mvi:orbit-viewmodel:8.0.0")

    // Compose
    implementation("org.orbit-mvi:orbit-compose:8.0.0")

    // Testing
    testImplementation("org.orbit-mvi:orbit-test:8.0.0")
}
```

### Базовая структура

```kotlin
// State
data class ProductListState(
    val products: List<Product> = emptyList(),
    val isLoading: Boolean = false,
    val searchQuery: String = "",
    val error: String? = null
)

// Side Effects
sealed interface ProductListSideEffect {
    data class NavigateToProduct(val productId: String) : ProductListSideEffect
    data class ShowSnackbar(val message: String) : ProductListSideEffect
    data class ShareProduct(val product: Product) : ProductListSideEffect
}

// ViewModel с Orbit
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ContainerHost<ProductListState, ProductListSideEffect>, ViewModel() {

    // Container - центральный элемент Orbit
    override val container = container<ProductListState, ProductListSideEffect>(
        initialState = ProductListState()
    ) {
        // Вызывается при создании container
        loadProducts()
    }

    fun loadProducts() = intent {
        // intent {} - блок для изменения state и side effects
        reduce { state.copy(isLoading = true, error = null) }

        productRepository.getProducts()
            .onSuccess { products ->
                reduce { state.copy(products = products, isLoading = false) }
            }
            .onFailure { error ->
                reduce { state.copy(isLoading = false, error = error.message) }
                postSideEffect(ProductListSideEffect.ShowSnackbar("Failed to load products"))
            }
    }

    fun onSearchQueryChanged(query: String) = intent {
        reduce { state.copy(searchQuery = query) }
    }

    fun onProductClicked(productId: String) = intent {
        postSideEffect(ProductListSideEffect.NavigateToProduct(productId))
    }

    fun onShareClicked(product: Product) = intent {
        postSideEffect(ProductListSideEffect.ShareProduct(product))
    }

    fun onRetryClicked() = intent {
        loadProducts()
    }
}
```

### Orbit DSL

```kotlin
class ExampleViewModel : ContainerHost<State, Effect>, ViewModel() {

    override val container = container<State, Effect>(State())

    // intent {} - основной блок для операций
    fun doSomething() = intent {
        // reduce {} - синхронное изменение state
        reduce {
            state.copy(isLoading = true)
        }

        // Async операции
        val result = repository.fetchData()

        // postSideEffect() - одноразовые события
        postSideEffect(Effect.ShowToast("Loaded!"))

        // Финальное обновление state
        reduce {
            state.copy(
                data = result,
                isLoading = false
            )
        }
    }

    // repeatOnSubscription - выполняется при каждой подписке
    fun observeUpdates() = intent(registerIdling = false) {
        repeatOnSubscription {
            repository.observeUpdates().collect { update ->
                reduce { state.copy(latestUpdate = update) }
            }
        }
    }

    // blockingIntent - гарантирует последовательное выполнение
    fun criticalOperation() = blockingIntent {
        // Другие intent не выполнятся пока этот не завершится
        reduce { state.copy(isProcessing = true) }
        repository.processCritical()
        reduce { state.copy(isProcessing = false) }
    }
}
```

### Compose интеграция

```kotlin
@Composable
fun ProductListScreen(
    viewModel: ProductListViewModel = hiltViewModel(),
    onNavigateToProduct: (String) -> Unit
) {
    // Собираем state
    val state by viewModel.collectAsState()

    // Обрабатываем side effects
    viewModel.collectSideEffect { effect ->
        when (effect) {
            is ProductListSideEffect.NavigateToProduct -> {
                onNavigateToProduct(effect.productId)
            }
            is ProductListSideEffect.ShowSnackbar -> {
                // Show snackbar
            }
            is ProductListSideEffect.ShareProduct -> {
                // Share product
            }
        }
    }

    ProductListContent(
        state = state,
        onSearchQueryChanged = viewModel::onSearchQueryChanged,
        onProductClicked = viewModel::onProductClicked,
        onShareClicked = viewModel::onShareClicked,
        onRetryClicked = viewModel::onRetryClicked
    )
}

@Composable
private fun ProductListContent(
    state: ProductListState,
    onSearchQueryChanged: (String) -> Unit,
    onProductClicked: (String) -> Unit,
    onShareClicked: (Product) -> Unit,
    onRetryClicked: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Search bar
        SearchBar(
            query = state.searchQuery,
            onQueryChange = onSearchQueryChanged
        )

        // Content
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
                    onRetry = onRetryClicked
                )
            }
            state.products.isEmpty() -> {
                EmptyView(message = "No products found")
            }
            else -> {
                LazyColumn {
                    items(state.filteredProducts) { product ->
                        ProductItem(
                            product = product,
                            onClick = { onProductClicked(product.id) },
                            onShare = { onShareClicked(product) }
                        )
                    }
                }
            }
        }
    }
}

// Extension для фильтрации
private val ProductListState.filteredProducts: List<Product>
    get() = if (searchQuery.isBlank()) {
        products
    } else {
        products.filter { it.name.contains(searchQuery, ignoreCase = true) }
    }
```

### Сложные сценарии

#### Pagination

```kotlin
data class PaginatedState(
    val items: List<Item> = emptyList(),
    val isLoading: Boolean = false,
    val isLoadingMore: Boolean = false,
    val currentPage: Int = 0,
    val hasMore: Boolean = true
)

class PaginatedViewModel(
    private val repository: ItemRepository
) : ContainerHost<PaginatedState, Nothing>, ViewModel() {

    override val container = container<PaginatedState, Nothing>(PaginatedState()) {
        loadFirstPage()
    }

    private fun loadFirstPage() = intent {
        reduce { state.copy(isLoading = true) }

        repository.getItems(page = 0)
            .onSuccess { items ->
                reduce {
                    state.copy(
                        items = items,
                        isLoading = false,
                        currentPage = 0,
                        hasMore = items.isNotEmpty()
                    )
                }
            }
            .onFailure {
                reduce { state.copy(isLoading = false) }
            }
    }

    fun loadMore() = intent {
        // Guard: не загружаем если уже загружаем или нет больше данных
        if (state.isLoadingMore || !state.hasMore) return@intent

        reduce { state.copy(isLoadingMore = true) }

        val nextPage = state.currentPage + 1
        repository.getItems(page = nextPage)
            .onSuccess { newItems ->
                reduce {
                    state.copy(
                        items = state.items + newItems,
                        isLoadingMore = false,
                        currentPage = nextPage,
                        hasMore = newItems.isNotEmpty()
                    )
                }
            }
            .onFailure {
                reduce { state.copy(isLoadingMore = false) }
            }
    }
}
```

#### Form Validation

```kotlin
data class FormState(
    val email: String = "",
    val password: String = "",
    val emailError: String? = null,
    val passwordError: String? = null,
    val isSubmitting: Boolean = false
) {
    val isValid: Boolean
        get() = emailError == null && passwordError == null &&
                email.isNotBlank() && password.isNotBlank()
}

sealed interface FormSideEffect {
    data object NavigateToHome : FormSideEffect
    data class ShowError(val message: String) : FormSideEffect
}

class LoginViewModel(
    private val authRepository: AuthRepository
) : ContainerHost<FormState, FormSideEffect>, ViewModel() {

    override val container = container<FormState, FormSideEffect>(FormState())

    fun onEmailChanged(email: String) = intent {
        reduce {
            state.copy(
                email = email,
                emailError = validateEmail(email)
            )
        }
    }

    fun onPasswordChanged(password: String) = intent {
        reduce {
            state.copy(
                password = password,
                passwordError = validatePassword(password)
            )
        }
    }

    fun onSubmitClicked() = intent {
        // Валидация перед отправкой
        val emailError = validateEmail(state.email)
        val passwordError = validatePassword(state.password)

        if (emailError != null || passwordError != null) {
            reduce {
                state.copy(emailError = emailError, passwordError = passwordError)
            }
            return@intent
        }

        reduce { state.copy(isSubmitting = true) }

        authRepository.login(state.email, state.password)
            .onSuccess {
                reduce { state.copy(isSubmitting = false) }
                postSideEffect(FormSideEffect.NavigateToHome)
            }
            .onFailure { error ->
                reduce { state.copy(isSubmitting = false) }
                postSideEffect(FormSideEffect.ShowError(error.message ?: "Login failed"))
            }
    }

    private fun validateEmail(email: String): String? = when {
        email.isBlank() -> "Email is required"
        !email.contains("@") -> "Invalid email format"
        else -> null
    }

    private fun validatePassword(password: String): String? = when {
        password.isBlank() -> "Password is required"
        password.length < 8 -> "Password must be at least 8 characters"
        else -> null
    }
}
```

### Тестирование с Orbit Test

```kotlin
class ProductListViewModelTest {

    @Test
    fun `loadProducts success updates state with products`() = runTest {
        // Given
        val products = listOf(Product("1", "Product 1"), Product("2", "Product 2"))
        val repository = mockk<ProductRepository> {
            coEvery { getProducts() } returns Result.success(products)
        }

        val viewModel = ProductListViewModel(repository)

        // When & Then
        viewModel.test(this) {
            // Initial state
            expectInitialState()

            // Trigger action
            containerHost.loadProducts()

            // Verify state changes
            expectState { copy(isLoading = true, error = null) }
            expectState { copy(products = products, isLoading = false) }
        }
    }

    @Test
    fun `loadProducts failure shows snackbar`() = runTest {
        // Given
        val repository = mockk<ProductRepository> {
            coEvery { getProducts() } returns Result.failure(Exception("Network error"))
        }

        val viewModel = ProductListViewModel(repository)

        // When & Then
        viewModel.test(this) {
            expectInitialState()

            containerHost.loadProducts()

            expectState { copy(isLoading = true, error = null) }
            expectState { copy(isLoading = false, error = "Network error") }
            expectSideEffect(ProductListSideEffect.ShowSnackbar("Failed to load products"))
        }
    }

    @Test
    fun `onProductClicked posts navigation side effect`() = runTest {
        val repository = mockk<ProductRepository>(relaxed = true)
        val viewModel = ProductListViewModel(repository)

        viewModel.test(this) {
            expectInitialState()

            containerHost.onProductClicked("product-123")

            expectSideEffect(ProductListSideEffect.NavigateToProduct("product-123"))
        }
    }

    @Test
    fun `search query updates state`() = runTest {
        val repository = mockk<ProductRepository>(relaxed = true)
        val viewModel = ProductListViewModel(repository)

        viewModel.test(this) {
            expectInitialState()

            containerHost.onSearchQueryChanged("phone")

            expectState { copy(searchQuery = "phone") }
        }
    }
}
```

### Orbit vs Manual MVI

| Аспект | Manual MVI | Orbit MVI |
|--------|------------|-----------|
| **Boilerplate** | Много (Channel, Flow, collect) | Минимум (DSL) |
| **Side Effects** | Ручная реализация | `postSideEffect()` |
| **Testing** | MockK + Turbine | Встроенный test DSL |
| **Learning curve** | Низкая | Средняя (нужно изучить DSL) |
| **Flexibility** | Полная | Ограничена DSL |

---

## Answer (EN)

**Orbit MVI** is a lightweight MVI framework for Kotlin/Android that provides a structured DSL for state management and side effects with minimal boilerplate.

### Why Orbit?

| Advantage | Description |
|-----------|-------------|
| **Minimal boilerplate** | DSL instead of manual Flow management |
| **Built-in side effects** | `postSideEffect()` out of the box |
| **Compose integration** | `collectAsState()`, `collectSideEffect()` |
| **Testing** | Built-in test DSL |
| **Type-safe** | Full typing for state and effects |

### Setup (2026)

```kotlin
dependencies {
    implementation("org.orbit-mvi:orbit-core:8.0.0")
    implementation("org.orbit-mvi:orbit-viewmodel:8.0.0")
    implementation("org.orbit-mvi:orbit-compose:8.0.0")
    testImplementation("org.orbit-mvi:orbit-test:8.0.0")
}
```

### Basic Structure

```kotlin
// State
data class ProductListState(
    val products: List<Product> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// Side Effects
sealed interface ProductListSideEffect {
    data class NavigateToProduct(val productId: String) : ProductListSideEffect
    data class ShowSnackbar(val message: String) : ProductListSideEffect
}

// ViewModel with Orbit
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ContainerHost<ProductListState, ProductListSideEffect>, ViewModel() {

    override val container = container<ProductListState, ProductListSideEffect>(
        initialState = ProductListState()
    )

    fun loadProducts() = intent {
        reduce { state.copy(isLoading = true) }

        productRepository.getProducts()
            .onSuccess { products ->
                reduce { state.copy(products = products, isLoading = false) }
            }
            .onFailure { error ->
                reduce { state.copy(isLoading = false, error = error.message) }
                postSideEffect(ProductListSideEffect.ShowSnackbar("Failed to load"))
            }
    }

    fun onProductClicked(productId: String) = intent {
        postSideEffect(ProductListSideEffect.NavigateToProduct(productId))
    }
}
```

### Orbit DSL

```kotlin
// intent {} - main block for operations
fun doSomething() = intent {
    // reduce {} - synchronous state change
    reduce { state.copy(isLoading = true) }

    // Async operations
    val result = repository.fetchData()

    // postSideEffect() - one-time events
    postSideEffect(Effect.ShowToast("Loaded!"))

    reduce { state.copy(data = result, isLoading = false) }
}

// blockingIntent - guarantees sequential execution
fun criticalOperation() = blockingIntent {
    // Other intents won't execute until this completes
}
```

### Compose Integration

```kotlin
@Composable
fun ProductListScreen(viewModel: ProductListViewModel = hiltViewModel()) {
    val state by viewModel.collectAsState()

    viewModel.collectSideEffect { effect ->
        when (effect) {
            is ProductListSideEffect.NavigateToProduct -> { /* navigate */ }
            is ProductListSideEffect.ShowSnackbar -> { /* show snackbar */ }
        }
    }

    ProductListContent(state = state, onProductClicked = viewModel::onProductClicked)
}
```

### Testing with Orbit Test

```kotlin
@Test
fun `loadProducts success updates state`() = runTest {
    val products = listOf(Product("1", "Product 1"))
    val repository = mockk<ProductRepository> {
        coEvery { getProducts() } returns Result.success(products)
    }

    val viewModel = ProductListViewModel(repository)

    viewModel.test(this) {
        expectInitialState()
        containerHost.loadProducts()
        expectState { copy(isLoading = true) }
        expectState { copy(products = products, isLoading = false) }
    }
}
```

---

## Follow-ups

- How does Orbit handle threading and coroutine scope?
- What are the trade-offs of using Orbit vs writing your own MVI?
- How do you migrate from manual MVI to Orbit?
- Can Orbit be used with Kotlin Multiplatform?

## References

- https://orbit-mvi.org/
- https://github.com/orbit-mvi/orbit-mvi

## Related Questions

### Prerequisites

- [[q-mvi-architecture--android--hard]] - MVI basics
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - State management

### Related

- [[q-mvi-pattern--architecture--hard]] - MVI components
- [[q-side-effects-architecture--architecture--medium]] - Side effects

### Advanced

- [[q-circuit-framework--architecture--medium]] - Circuit by Slack
- [[q-state-machines--architecture--hard]] - FSM for UI

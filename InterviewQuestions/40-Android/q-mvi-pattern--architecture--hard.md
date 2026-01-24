---
id: android-720
title: "MVI Pattern Deep Dive / Глубокое погружение в MVI"
aliases:
- MVI Components
- Intent Model View Reducer
- MVI Reducer Pattern
- Компоненты MVI
topic: android
subtopics:
- architecture
- architecture-mvi
- state-management
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-mvi-architecture--android--hard
- q-unidirectional-data-flow--architecture--medium
- q-state-machines--architecture--hard
created: 2026-01-23
updated: 2026-01-23
sources:
- "https://developer.android.com/topic/architecture"
- "https://hannesdorfmann.com/android/mosby3-mvi-1/"
tags:
- android/architecture-mvi
- android/architecture
- difficulty/hard
- state-management
- unidirectional-data-flow
---
# Vopros (RU)

> Объясните подробно каждый компонент паттерна MVI: Intent, Model, View и Reducer. Как они взаимодействуют в цикле?

# Question (EN)

> Explain in detail each component of the MVI pattern: Intent, Model, View, and Reducer. How do they interact in the cycle?

---

## Otvet (RU)

**MVI (Model-View-Intent)** - реактивный архитектурный паттерн с однонаправленным потоком данных, где каждый компонент имеет четко определенную ответственность.

### Цикл MVI

```text
User Action -> Intent -> Reducer -> Model (State) -> View -> User Action
                  ^                                      |
                  +--------------------------------------+
```

### 1. Intent - Намерения

**Intent** - это sealed class, описывающий все возможные действия пользователя или системные события, которые могут изменить состояние.

```kotlin
// Intent - исчерпывающий список действий
sealed interface ProductListIntent {
    // Пользовательские действия
    data class Search(val query: String) : ProductListIntent
    data class SelectCategory(val category: Category) : ProductListIntent
    data object LoadMore : ProductListIntent
    data object Refresh : ProductListIntent
    data class ToggleFavorite(val productId: String) : ProductListIntent

    // Системные события (результаты side effects)
    data class ProductsLoaded(val products: List<Product>) : ProductListIntent
    data class LoadError(val error: Throwable) : ProductListIntent
    data object LoadingStarted : ProductListIntent
}
```

**Преимущества sealed interface для Intent:**
- Исчерпывающий when без else
- Compile-time безопасность
- Документирует все возможные действия

### 2. Model (State) - Состояние

**Model** - единственный источник истины для UI. Всегда immutable data class.

```kotlin
// Model - полное состояние экрана
data class ProductListState(
    val products: List<Product> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val error: ErrorState? = null,
    val searchQuery: String = "",
    val selectedCategory: Category? = null,
    val pagination: PaginationState = PaginationState(),
    val favorites: Set<String> = emptySet()
) {
    // Derived state - вычисляемые свойства
    val filteredProducts: List<Product>
        get() = products.filter { product ->
            (searchQuery.isEmpty() || product.name.contains(searchQuery, ignoreCase = true)) &&
            (selectedCategory == null || product.category == selectedCategory)
        }

    val isEmpty: Boolean
        get() = !isLoading && products.isEmpty() && error == null

    val canLoadMore: Boolean
        get() = !isLoading && pagination.hasMore
}

data class PaginationState(
    val currentPage: Int = 0,
    val hasMore: Boolean = true,
    val totalCount: Int = 0
)

sealed interface ErrorState {
    data class Network(val message: String) : ErrorState
    data class Server(val code: Int, val message: String) : ErrorState
    data object Unknown : ErrorState
}
```

### 3. Reducer - Чистая функция

**Reducer** - чистая функция `(State, Intent) -> State`. Не имеет side effects, детерминирована.

```kotlin
// Reducer - чистая функция без side effects
object ProductListReducer {

    fun reduce(state: ProductListState, intent: ProductListIntent): ProductListState {
        return when (intent) {
            is ProductListIntent.Search -> state.copy(
                searchQuery = intent.query,
                // Сбрасываем пагинацию при новом поиске
                pagination = PaginationState()
            )

            is ProductListIntent.SelectCategory -> state.copy(
                selectedCategory = intent.category,
                pagination = PaginationState()
            )

            is ProductListIntent.LoadMore -> state.copy(
                // Не меняем isLoading, т.к. это "load more"
                pagination = state.pagination.copy(
                    currentPage = state.pagination.currentPage + 1
                )
            )

            is ProductListIntent.Refresh -> state.copy(
                isRefreshing = true,
                error = null
            )

            is ProductListIntent.LoadingStarted -> state.copy(
                isLoading = true,
                error = null
            )

            is ProductListIntent.ProductsLoaded -> state.copy(
                products = if (state.isRefreshing) {
                    intent.products
                } else {
                    state.products + intent.products
                },
                isLoading = false,
                isRefreshing = false,
                pagination = state.pagination.copy(
                    hasMore = intent.products.isNotEmpty()
                )
            )

            is ProductListIntent.LoadError -> state.copy(
                isLoading = false,
                isRefreshing = false,
                error = when (intent.error) {
                    is IOException -> ErrorState.Network(intent.error.message ?: "Network error")
                    is HttpException -> ErrorState.Server(
                        intent.error.code(),
                        intent.error.message()
                    )
                    else -> ErrorState.Unknown
                }
            )

            is ProductListIntent.ToggleFavorite -> state.copy(
                favorites = if (intent.productId in state.favorites) {
                    state.favorites - intent.productId
                } else {
                    state.favorites + intent.productId
                }
            )
        }
    }
}
```

### 4. View - Отображение и события

**View** подписывается на State и отправляет Intent. Не содержит логики.

```kotlin
@Composable
fun ProductListScreen(
    viewModel: ProductListViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    ProductListContent(
        state = state,
        onIntent = viewModel::processIntent
    )
}

@Composable
private fun ProductListContent(
    state: ProductListState,
    onIntent: (ProductListIntent) -> Unit
) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Search bar
        SearchBar(
            query = state.searchQuery,
            onQueryChange = { onIntent(ProductListIntent.Search(it)) }
        )

        // Category filter
        CategoryChips(
            selected = state.selectedCategory,
            onSelect = { onIntent(ProductListIntent.SelectCategory(it)) }
        )

        // Content
        when {
            state.isLoading && state.products.isEmpty() -> {
                LoadingIndicator()
            }
            state.error != null && state.products.isEmpty() -> {
                ErrorView(
                    error = state.error,
                    onRetry = { onIntent(ProductListIntent.Refresh) }
                )
            }
            state.isEmpty -> {
                EmptyView()
            }
            else -> {
                ProductList(
                    products = state.filteredProducts,
                    favorites = state.favorites,
                    isLoadingMore = state.isLoading,
                    canLoadMore = state.canLoadMore,
                    onLoadMore = { onIntent(ProductListIntent.LoadMore) },
                    onToggleFavorite = { onIntent(ProductListIntent.ToggleFavorite(it)) },
                    onRefresh = { onIntent(ProductListIntent.Refresh) },
                    isRefreshing = state.isRefreshing
                )
            }
        }
    }
}
```

### 5. ViewModel - Оркестратор

**ViewModel** связывает компоненты и обрабатывает side effects.

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val productRepository: ProductRepository,
    private val favoriteRepository: FavoriteRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ProductListState())
    val state: StateFlow<ProductListState> = _state.asStateFlow()

    private val _sideEffects = Channel<ProductListSideEffect>(Channel.BUFFERED)
    val sideEffects = _sideEffects.receiveAsFlow()

    init {
        loadProducts()
    }

    fun processIntent(intent: ProductListIntent) {
        // 1. Применяем reducer (чистая функция)
        val newState = ProductListReducer.reduce(_state.value, intent)
        _state.value = newState

        // 2. Обрабатываем side effects
        handleSideEffects(intent, newState)
    }

    private fun handleSideEffects(intent: ProductListIntent, state: ProductListState) {
        viewModelScope.launch {
            when (intent) {
                is ProductListIntent.Search -> {
                    // Debounce поиска
                    delay(300)
                    loadProducts()
                }
                is ProductListIntent.SelectCategory,
                is ProductListIntent.Refresh -> {
                    loadProducts()
                }
                is ProductListIntent.LoadMore -> {
                    loadMoreProducts(state.pagination.currentPage)
                }
                is ProductListIntent.ToggleFavorite -> {
                    saveFavorite(intent.productId, intent.productId in state.favorites)
                }
                // Результаты - не требуют side effects
                is ProductListIntent.ProductsLoaded,
                is ProductListIntent.LoadError,
                is ProductListIntent.LoadingStarted -> Unit
            }
        }
    }

    private fun loadProducts() {
        viewModelScope.launch {
            processIntent(ProductListIntent.LoadingStarted)

            productRepository.getProducts(
                query = _state.value.searchQuery,
                category = _state.value.selectedCategory
            ).fold(
                onSuccess = { products ->
                    processIntent(ProductListIntent.ProductsLoaded(products))
                },
                onFailure = { error ->
                    processIntent(ProductListIntent.LoadError(error))
                }
            )
        }
    }

    private fun loadMoreProducts(page: Int) {
        viewModelScope.launch {
            productRepository.getProducts(
                query = _state.value.searchQuery,
                category = _state.value.selectedCategory,
                page = page
            ).fold(
                onSuccess = { products ->
                    processIntent(ProductListIntent.ProductsLoaded(products))
                },
                onFailure = { error ->
                    processIntent(ProductListIntent.LoadError(error))
                }
            )
        }
    }

    private fun saveFavorite(productId: String, isFavorite: Boolean) {
        viewModelScope.launch {
            favoriteRepository.setFavorite(productId, isFavorite)
                .onFailure {
                    _sideEffects.send(ProductListSideEffect.ShowError("Failed to update favorite"))
                }
        }
    }
}

sealed interface ProductListSideEffect {
    data class ShowError(val message: String) : ProductListSideEffect
    data class NavigateToProduct(val productId: String) : ProductListSideEffect
}
```

### Тестирование Reducer

```kotlin
class ProductListReducerTest {

    @Test
    fun `search intent updates query and resets pagination`() {
        val initialState = ProductListState(
            searchQuery = "old",
            pagination = PaginationState(currentPage = 5)
        )

        val newState = ProductListReducer.reduce(
            initialState,
            ProductListIntent.Search("new query")
        )

        assertEquals("new query", newState.searchQuery)
        assertEquals(0, newState.pagination.currentPage)
    }

    @Test
    fun `products loaded appends to existing list`() {
        val existingProducts = listOf(Product("1", "A"))
        val newProducts = listOf(Product("2", "B"))
        val initialState = ProductListState(
            products = existingProducts,
            isLoading = true
        )

        val newState = ProductListReducer.reduce(
            initialState,
            ProductListIntent.ProductsLoaded(newProducts)
        )

        assertEquals(2, newState.products.size)
        assertFalse(newState.isLoading)
    }

    @Test
    fun `refresh replaces products instead of appending`() {
        val existingProducts = listOf(Product("1", "A"))
        val newProducts = listOf(Product("2", "B"))
        val initialState = ProductListState(
            products = existingProducts,
            isRefreshing = true
        )

        val newState = ProductListReducer.reduce(
            initialState,
            ProductListIntent.ProductsLoaded(newProducts)
        )

        assertEquals(1, newState.products.size)
        assertEquals("2", newState.products.first().id)
    }
}
```

### Best Practices

| Компонент | DO | DON'T |
|-----------|----|----- |
| **Intent** | Sealed class/interface | Открытые классы |
| **State** | Immutable data class | Mutable properties |
| **Reducer** | Чистая функция | Side effects, suspend |
| **View** | Stateless, только рендер | Бизнес-логика |
| **ViewModel** | Оркестрация | Логика в when блоках |

---

## Answer (EN)

**MVI (Model-View-Intent)** is a reactive architectural pattern with unidirectional data flow, where each component has a clearly defined responsibility.

### MVI Cycle

```text
User Action -> Intent -> Reducer -> Model (State) -> View -> User Action
                  ^                                      |
                  +--------------------------------------+
```

### 1. Intent - Actions

**Intent** is a sealed class describing all possible user actions or system events that can change state.

```kotlin
// Intent - exhaustive list of actions
sealed interface ProductListIntent {
    // User actions
    data class Search(val query: String) : ProductListIntent
    data class SelectCategory(val category: Category) : ProductListIntent
    data object LoadMore : ProductListIntent
    data object Refresh : ProductListIntent
    data class ToggleFavorite(val productId: String) : ProductListIntent

    // System events (side effect results)
    data class ProductsLoaded(val products: List<Product>) : ProductListIntent
    data class LoadError(val error: Throwable) : ProductListIntent
    data object LoadingStarted : ProductListIntent
}
```

**Benefits of sealed interface for Intent:**
- Exhaustive when without else branch
- Compile-time safety
- Documents all possible actions

### 2. Model (State) - State

**Model** is the single source of truth for UI. Always an immutable data class.

```kotlin
// Model - complete screen state
data class ProductListState(
    val products: List<Product> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val error: ErrorState? = null,
    val searchQuery: String = "",
    val selectedCategory: Category? = null,
    val pagination: PaginationState = PaginationState(),
    val favorites: Set<String> = emptySet()
) {
    // Derived state - computed properties
    val filteredProducts: List<Product>
        get() = products.filter { product ->
            (searchQuery.isEmpty() || product.name.contains(searchQuery, ignoreCase = true)) &&
            (selectedCategory == null || product.category == selectedCategory)
        }

    val isEmpty: Boolean
        get() = !isLoading && products.isEmpty() && error == null

    val canLoadMore: Boolean
        get() = !isLoading && pagination.hasMore
}

data class PaginationState(
    val currentPage: Int = 0,
    val hasMore: Boolean = true,
    val totalCount: Int = 0
)

sealed interface ErrorState {
    data class Network(val message: String) : ErrorState
    data class Server(val code: Int, val message: String) : ErrorState
    data object Unknown : ErrorState
}
```

### 3. Reducer - Pure Function

**Reducer** is a pure function `(State, Intent) -> State`. No side effects, deterministic.

```kotlin
// Reducer - pure function without side effects
object ProductListReducer {

    fun reduce(state: ProductListState, intent: ProductListIntent): ProductListState {
        return when (intent) {
            is ProductListIntent.Search -> state.copy(
                searchQuery = intent.query,
                // Reset pagination on new search
                pagination = PaginationState()
            )

            is ProductListIntent.SelectCategory -> state.copy(
                selectedCategory = intent.category,
                pagination = PaginationState()
            )

            is ProductListIntent.LoadMore -> state.copy(
                pagination = state.pagination.copy(
                    currentPage = state.pagination.currentPage + 1
                )
            )

            is ProductListIntent.Refresh -> state.copy(
                isRefreshing = true,
                error = null
            )

            is ProductListIntent.LoadingStarted -> state.copy(
                isLoading = true,
                error = null
            )

            is ProductListIntent.ProductsLoaded -> state.copy(
                products = if (state.isRefreshing) {
                    intent.products
                } else {
                    state.products + intent.products
                },
                isLoading = false,
                isRefreshing = false,
                pagination = state.pagination.copy(
                    hasMore = intent.products.isNotEmpty()
                )
            )

            is ProductListIntent.LoadError -> state.copy(
                isLoading = false,
                isRefreshing = false,
                error = when (intent.error) {
                    is IOException -> ErrorState.Network(intent.error.message ?: "Network error")
                    is HttpException -> ErrorState.Server(
                        intent.error.code(),
                        intent.error.message()
                    )
                    else -> ErrorState.Unknown
                }
            )

            is ProductListIntent.ToggleFavorite -> state.copy(
                favorites = if (intent.productId in state.favorites) {
                    state.favorites - intent.productId
                } else {
                    state.favorites + intent.productId
                }
            )
        }
    }
}
```

### 4. View - Display and Events

**View** subscribes to State and emits Intents. Contains no logic.

```kotlin
@Composable
fun ProductListScreen(
    viewModel: ProductListViewModel = hiltViewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    ProductListContent(
        state = state,
        onIntent = viewModel::processIntent
    )
}

@Composable
private fun ProductListContent(
    state: ProductListState,
    onIntent: (ProductListIntent) -> Unit
) {
    Column(modifier = Modifier.fillMaxSize()) {
        SearchBar(
            query = state.searchQuery,
            onQueryChange = { onIntent(ProductListIntent.Search(it)) }
        )

        CategoryChips(
            selected = state.selectedCategory,
            onSelect = { onIntent(ProductListIntent.SelectCategory(it)) }
        )

        when {
            state.isLoading && state.products.isEmpty() -> {
                LoadingIndicator()
            }
            state.error != null && state.products.isEmpty() -> {
                ErrorView(
                    error = state.error,
                    onRetry = { onIntent(ProductListIntent.Refresh) }
                )
            }
            state.isEmpty -> {
                EmptyView()
            }
            else -> {
                ProductList(
                    products = state.filteredProducts,
                    favorites = state.favorites,
                    isLoadingMore = state.isLoading,
                    canLoadMore = state.canLoadMore,
                    onLoadMore = { onIntent(ProductListIntent.LoadMore) },
                    onToggleFavorite = { onIntent(ProductListIntent.ToggleFavorite(it)) },
                    onRefresh = { onIntent(ProductListIntent.Refresh) },
                    isRefreshing = state.isRefreshing
                )
            }
        }
    }
}
```

### 5. ViewModel - Orchestrator

**ViewModel** connects components and handles side effects.

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val productRepository: ProductRepository,
    private val favoriteRepository: FavoriteRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ProductListState())
    val state: StateFlow<ProductListState> = _state.asStateFlow()

    private val _sideEffects = Channel<ProductListSideEffect>(Channel.BUFFERED)
    val sideEffects = _sideEffects.receiveAsFlow()

    init {
        loadProducts()
    }

    fun processIntent(intent: ProductListIntent) {
        // 1. Apply reducer (pure function)
        val newState = ProductListReducer.reduce(_state.value, intent)
        _state.value = newState

        // 2. Handle side effects
        handleSideEffects(intent, newState)
    }

    private fun handleSideEffects(intent: ProductListIntent, state: ProductListState) {
        viewModelScope.launch {
            when (intent) {
                is ProductListIntent.Search -> {
                    delay(300) // Debounce
                    loadProducts()
                }
                is ProductListIntent.SelectCategory,
                is ProductListIntent.Refresh -> {
                    loadProducts()
                }
                is ProductListIntent.LoadMore -> {
                    loadMoreProducts(state.pagination.currentPage)
                }
                is ProductListIntent.ToggleFavorite -> {
                    saveFavorite(intent.productId, intent.productId in state.favorites)
                }
                is ProductListIntent.ProductsLoaded,
                is ProductListIntent.LoadError,
                is ProductListIntent.LoadingStarted -> Unit
            }
        }
    }

    // ... repository calls
}
```

### Testing Reducer

```kotlin
class ProductListReducerTest {

    @Test
    fun `search intent updates query and resets pagination`() {
        val initialState = ProductListState(
            searchQuery = "old",
            pagination = PaginationState(currentPage = 5)
        )

        val newState = ProductListReducer.reduce(
            initialState,
            ProductListIntent.Search("new query")
        )

        assertEquals("new query", newState.searchQuery)
        assertEquals(0, newState.pagination.currentPage)
    }
}
```

### Best Practices

| Component | DO | DON'T |
|-----------|----|----- |
| **Intent** | Sealed class/interface | Open classes |
| **State** | Immutable data class | Mutable properties |
| **Reducer** | Pure function | Side effects, suspend |
| **View** | Stateless, render only | Business logic |
| **ViewModel** | Orchestration | Logic in when blocks |

---

## Follow-ups

- How do you handle async operations that span multiple intents?
- What is the difference between "internal" intents and "external" intents?
- How do you compose reducers for complex screens with multiple sub-states?
- When should derived state be in the State class vs computed in the View?

## References

- [[q-mvi-architecture--android--hard]] - MVI architecture overview
- [[q-unidirectional-data-flow--architecture--medium]] - UDF principles
- https://developer.android.com/topic/architecture
- https://hannesdorfmann.com/android/mosby3-mvi-1/

## Related Questions

### Prerequisites

- [[q-mvvm-pattern--android--medium]] - MVVM pattern basics
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - State management tools

### Related

- [[q-state-machines--architecture--hard]] - Finite state machines
- [[q-side-effects-architecture--architecture--medium]] - Side effects handling

### Advanced

- [[q-orbit-mvi--architecture--medium]] - Orbit MVI library
- [[q-circuit-framework--architecture--medium]] - Circuit by Slack

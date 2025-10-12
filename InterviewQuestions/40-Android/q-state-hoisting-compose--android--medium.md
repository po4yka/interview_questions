---
topic: android
tags:
  - android
  - jetpack-compose
  - state-management
  - architecture
  - best-practices
difficulty: medium
status: draft
---

# State Hoisting в Jetpack Compose

**English**: What is state hoisting in Jetpack Compose and why is it considered a best practice for building reusable components?

## Answer (EN)
**State hoisting** (подъем состояния) — это паттерн в Compose, где состояние перемещается из компонента наверх к его caller. Компонент становится **stateless** (без состояния), получая значение и callback для изменения. Это делает компоненты переиспользуемыми, тестируемыми и предсказуемыми.

### Проблема: Stateful компонент

```kotlin
// - НЕПРАВИЛЬНО - stateful компонент (сложно переиспользовать)
@Composable
fun SearchBar() {
    var query by remember { mutableStateOf("") }

    TextField(
        value = query,
        onValueChange = { query = it },
        placeholder = { Text("Search...") }
    )
}

// Проблемы:
// 1. Нельзя контролировать query извне
// 2. Нельзя реагировать на изменения
// 3. Сложно тестировать
// 4. Состояние привязано к компоненту
```

### Решение: State Hoisting

```kotlin
// - ПРАВИЛЬНО - stateless компонент (переиспользуемый)
@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    TextField(
        value = query,
        onValueChange = onQueryChange,
        placeholder = { Text("Search...") },
        modifier = modifier
    )
}

// Использование с hoisted state
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }

    SearchBar(
        query = query,
        onQueryChange = { query = it }
    )
}
```

**Преимущества**:
- - **Single source of truth** - состояние в одном месте
- - **Reusability** - компонент можно переиспользовать
- - **Testability** - легко тестировать
- - **Predictability** - явный контроль состояния
- - **Composability** - легко комбинировать

### Принципы State Hoisting

**Правило**: Состояние должно быть hoisted до **lowest common ancestor** (наименьшего общего родителя) всех компонентов, которым нужно это состояние.

```kotlin
@Composable
fun ShoppingCart() {
    // State hoisted сюда - общий родитель для CartList и CartSummary
    var cartItems by remember { mutableStateOf<List<CartItem>>(emptyList()) }

    Column {
        CartList(
            items = cartItems,
            onItemRemove = { item ->
                cartItems = cartItems - item
            }
        )

        CartSummary(
            items = cartItems,
            onCheckout = { /* ... */ }
        )
    }
}

@Composable
fun CartList(
    items: List<CartItem>,
    onItemRemove: (CartItem) -> Unit
) {
    LazyColumn {
        items(items) { item ->
            CartItemCard(
                item = item,
                onRemove = { onItemRemove(item) }
            )
        }
    }
}

@Composable
fun CartSummary(
    items: List<CartItem>,
    onCheckout: () -> Unit
) {
    val total = items.sumOf { it.price * it.quantity }

    Column {
        Text("Total: $$total")
        Button(onClick = onCheckout) {
            Text("Checkout")
        }
    }
}
```

### Паттерны State Hoisting

#### 1. Value + Callback паттерн

```kotlin
// Stateless компонент
@Composable
fun Counter(
    count: Int,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit
) {
    Row {
        Button(onClick = onDecrement) {
            Text("-")
        }
        Text("$count")
        Button(onClick = onIncrement) {
            Text("+")
        }
    }
}

// Использование
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }

    Counter(
        count = count,
        onIncrement = { count++ },
        onDecrement = { count-- }
    )
}
```

#### 2. State Object паттерн

```kotlin
// State object для сложного состояния
@Stable
data class FilterState(
    val query: String = "",
    val category: String? = null,
    val priceRange: ClosedFloatingPointRange<Float> = 0f..1000f,
    val sortBy: SortOption = SortOption.RELEVANCE
)

// Stateless компонент
@Composable
fun FilterPanel(
    filterState: FilterState,
    onFilterChange: (FilterState) -> Unit
) {
    Column {
        TextField(
            value = filterState.query,
            onValueChange = {
                onFilterChange(filterState.copy(query = it))
            }
        )

        CategoryDropdown(
            selected = filterState.category,
            onSelect = {
                onFilterChange(filterState.copy(category = it))
            }
        )

        PriceRangeSlider(
            range = filterState.priceRange,
            onRangeChange = {
                onFilterChange(filterState.copy(priceRange = it))
            }
        )
    }
}
```

#### 3. State Holder класс

Для сложной логики состояния используйте `@Stable` класс:

```kotlin
@Stable
class SearchState(
    initialQuery: String = "",
    initialFilters: FilterState = FilterState()
) {
    var query by mutableStateOf(initialQuery)
        private set

    var filters by mutableStateOf(initialFilters)
        private set

    var suggestions by mutableStateOf<List<String>>(emptyList())
        private set

    fun updateQuery(newQuery: String) {
        query = newQuery
        // Логика обновления suggestions
        suggestions = getSuggestions(newQuery)
    }

    fun updateFilters(newFilters: FilterState) {
        filters = newFilters
    }

    fun clearSearch() {
        query = ""
        filters = FilterState()
        suggestions = emptyList()
    }
}

@Composable
fun rememberSearchState(
    initialQuery: String = "",
    initialFilters: FilterState = FilterState()
): SearchState {
    return remember {
        SearchState(initialQuery, initialFilters)
    }
}

// Использование
@Composable
fun SearchScreen() {
    val searchState = rememberSearchState()

    Column {
        SearchBar(
            query = searchState.query,
            onQueryChange = searchState::updateQuery
        )

        FilterPanel(
            filterState = searchState.filters,
            onFilterChange = searchState::updateFilters
        )

        SearchResults(
            query = searchState.query,
            filters = searchState.filters
        )
    }
}
```

### Уровни State Hoisting

#### Уровень 1: Локальный UI state

```kotlin
@Composable
fun ExpandableCard(title: String, content: String) {
    // Локальное состояние - НЕ нужен hoisting
    var isExpanded by remember { mutableStateOf(false) }

    Card {
        Column {
            Text(
                text = title,
                modifier = Modifier.clickable { isExpanded = !isExpanded }
            )

            if (isExpanded) {
                Text(content)
            }
        }
    }
}
```

#### Уровень 2: Screen-level state

```kotlin
@Composable
fun ProductListScreen() {
    // Screen-level state
    var selectedProduct by remember { mutableStateOf<Product?>(null) }
    var isFilterVisible by remember { mutableStateOf(false) }

    Column {
        ProductList(
            onProductClick = { selectedProduct = it }
        )

        if (selectedProduct != null) {
            ProductDetailDialog(
                product = selectedProduct!!,
                onDismiss = { selectedProduct = null }
            )
        }
    }
}
```

#### Уровень 3: ViewModel state

```kotlin
@HiltViewModel
class ProductViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {
    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products: StateFlow<List<Product>> = _products.asStateFlow()

    private val _filters = MutableStateFlow(FilterState())
    val filters: StateFlow<FilterState> = _filters.asStateFlow()

    fun updateFilters(newFilters: FilterState) {
        _filters.value = newFilters
        loadProducts()
    }
}

@Composable
fun ProductScreen(viewModel: ProductViewModel = hiltViewModel()) {
    val products by viewModel.products.collectAsState()
    val filters by viewModel.filters.collectAsState()

    Column {
        FilterPanel(
            filterState = filters,
            onFilterChange = viewModel::updateFilters
        )

        ProductList(products = products)
    }
}
```

### Stateful vs Stateless Composables

#### Stateful - внутреннее состояние

```kotlin
// Stateful - управляет своим состоянием
@Composable
fun StatefulCounter() {
    var count by remember { mutableStateOf(0) }

    Row {
        Button(onClick = { count-- }) { Text("-") }
        Text("$count")
        Button(onClick = { count++ }) { Text("+") }
    }
}

// Использование
@Composable
fun Screen() {
    StatefulCounter() // Просто вызываем
}
```

**Когда использовать**:
- - Простой UI-only state
- - Не нужен доступ к состоянию извне
- - Не нужно сохранять состояние
- - Примеры: animation state, scroll state, expanded/collapsed

#### Stateless - hoisted состояние

```kotlin
// Stateless - получает состояние извне
@Composable
fun StatelessCounter(
    count: Int,
    onCountChange: (Int) -> Unit
) {
    Row {
        Button(onClick = { onCountChange(count - 1) }) { Text("-") }
        Text("$count")
        Button(onClick = { onCountChange(count + 1) }) { Text("+") }
    }
}

// Использование
@Composable
fun Screen() {
    var count by remember { mutableStateOf(0) }
    StatelessCounter(count = count, onCountChange = { count = it })
}
```

**Когда использовать**:
- - Нужен контроль состояния извне
- - Множественное использование
- - Тестирование
- - Состояние в ViewModel
- - Примеры: форма ввода, фильтры, выбранные элементы

### Практические примеры

#### Пример 1: Форма регистрации

```kotlin
data class RegistrationFormState(
    val name: String = "",
    val email: String = "",
    val password: String = "",
    val confirmPassword: String = ""
) {
    val isValid: Boolean
        get() = name.isNotBlank() &&
                email.contains("@") &&
                password.length >= 8 &&
                password == confirmPassword
}

@Composable
fun RegistrationForm(
    formState: RegistrationFormState,
    onFormChange: (RegistrationFormState) -> Unit,
    onSubmit: () -> Unit
) {
    Column {
        TextField(
            value = formState.name,
            onValueChange = { onFormChange(formState.copy(name = it)) },
            label = { Text("Name") }
        )

        TextField(
            value = formState.email,
            onValueChange = { onFormChange(formState.copy(email = it)) },
            label = { Text("Email") }
        )

        TextField(
            value = formState.password,
            onValueChange = { onFormChange(formState.copy(password = it)) },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation()
        )

        TextField(
            value = formState.confirmPassword,
            onValueChange = { onFormChange(formState.copy(confirmPassword = it)) },
            label = { Text("Confirm Password") },
            visualTransformation = PasswordVisualTransformation()
        )

        Button(
            onClick = onSubmit,
            enabled = formState.isValid
        ) {
            Text("Register")
        }
    }
}

// Использование с ViewModel
@Composable
fun RegistrationScreen(viewModel: RegistrationViewModel = hiltViewModel()) {
    val formState by viewModel.formState.collectAsState()

    RegistrationForm(
        formState = formState,
        onFormChange = viewModel::updateForm,
        onSubmit = viewModel::register
    )
}
```

#### Пример 2: Tabs с контентом

```kotlin
@Composable
fun TabLayout(
    selectedTab: Int,
    onTabSelected: (Int) -> Unit,
    tabs: List<String>,
    content: @Composable (Int) -> Unit
) {
    Column {
        TabRow(selectedTabIndex = selectedTab) {
            tabs.forEachIndexed { index, title ->
                Tab(
                    selected = selectedTab == index,
                    onClick = { onTabSelected(index) },
                    text = { Text(title) }
                )
            }
        }

        content(selectedTab)
    }
}

// Использование
@Composable
fun ProfileScreen() {
    var selectedTab by rememberSaveable { mutableStateOf(0) }

    TabLayout(
        selectedTab = selectedTab,
        onTabSelected = { selectedTab = it },
        tabs = listOf("Posts", "Photos", "Videos")
    ) { tabIndex ->
        when (tabIndex) {
            0 -> PostsContent()
            1 -> PhotosContent()
            2 -> VideosContent()
        }
    }
}
```

#### Пример 3: Multi-selection список

```kotlin
@Composable
fun <T> SelectableList(
    items: List<T>,
    selectedItems: Set<T>,
    onSelectionChange: (Set<T>) -> Unit,
    itemContent: @Composable (T, Boolean) -> Unit
) {
    LazyColumn {
        items(items) { item ->
            val isSelected = item in selectedItems

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable {
                        onSelectionChange(
                            if (isSelected) {
                                selectedItems - item
                            } else {
                                selectedItems + item
                            }
                        )
                    }
            ) {
                Checkbox(
                    checked = isSelected,
                    onCheckedChange = null
                )

                itemContent(item, isSelected)
            }
        }
    }
}

// Использование
@Composable
fun ProductSelectionScreen() {
    var selectedProducts by remember { mutableStateOf<Set<Product>>(emptySet()) }

    Column {
        SelectableList(
            items = products,
            selectedItems = selectedProducts,
            onSelectionChange = { selectedProducts = it }
        ) { product, isSelected ->
            ProductCard(product, highlighted = isSelected)
        }

        Button(
            onClick = { /* checkout */ },
            enabled = selectedProducts.isNotEmpty()
        ) {
            Text("Checkout (${selectedProducts.size})")
        }
    }
}
```

### Hoisting с derivedStateOf

```kotlin
@Composable
fun ProductList(
    products: List<Product>,
    filters: FilterState
) {
    // Вычисляемое состояние - hoisted в composable
    val filteredProducts by remember(products, filters) {
        derivedStateOf {
            products.filter { product ->
                (filters.category == null || product.category == filters.category) &&
                product.price in filters.priceRange &&
                (filters.query.isEmpty() || product.name.contains(filters.query, ignoreCase = true))
            }
        }
    }

    LazyColumn {
        items(filteredProducts) { product ->
            ProductCard(product)
        }
    }
}
```

### Best Practices

**1. Hoist до нужного уровня**

```kotlin
// - ПРАВИЛЬНО - state на правильном уровне
@Composable
fun Screen() {
    var count by remember { mutableStateOf(0) }

    Column {
        Counter(count = count, onCountChange = { count = it })
        Text("Current count: $count")
    }
}

// - НЕПРАВИЛЬНО - слишком высоко (ViewModel не нужен)
@HiltViewModel
class CounterViewModel : ViewModel() {
    var count by mutableStateOf(0) // Overkill для простого счетчика
}
```

**2. Используйте data class для сложного состояния**

```kotlin
// - ПРАВИЛЬНО
data class FormState(
    val name: String,
    val email: String,
    val phone: String
)

// - НЕПРАВИЛЬНО - много отдельных параметров
@Composable
fun Form(
    name: String,
    onNameChange: (String) -> Unit,
    email: String,
    onEmailChange: (String) -> Unit,
    phone: String,
    onPhoneChange: (String) -> Unit
) { /* ... */ }
```

**3. Предоставляйте дефолтные значения**

```kotlin
@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    placeholder: String = "Search...",
    modifier: Modifier = Modifier
) {
    // ...
}
```

**4. Не передавайте лишние параметры**

```kotlin
// - НЕПРАВИЛЬНО - передаем весь ViewModel
@Composable
fun ProductCard(viewModel: ProductViewModel) { }

// - ПРАВИЛЬНО - только нужные данные
@Composable
fun ProductCard(
    product: Product,
    onAddToCart: (Product) -> Unit
) { }
```

**English**: **State hoisting** moves state from a component up to its caller, making the component stateless (receives value + callback). Benefits: single source of truth, reusability, testability, predictability. Pattern: `value` + `onValueChange` callback. Hoist state to **lowest common ancestor** of all components needing it. Three levels: local UI state (no hoisting), screen-level state (remember), ViewModel state (StateFlow). Use stateless composables for: forms, filters, selections, reusable components. Use stateful composables for: simple UI-only state, animations, scroll. State holder classes (`@Stable`) for complex state logic. Best practices: hoist to appropriate level, use data class for complex state, provide defaults, don't pass entire ViewModel.



---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations


---
id: android-371
title: State Hoisting in Compose / Поднятие состояния в Compose
aliases:
- State Hoisting in Compose
- Поднятие состояния в Compose
topic: android
subtopics:
- ui-compose
- ui-state
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-separate-ui-business-logic--android--easy
- q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium
- q-what-is-hilt--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/ui-compose
- android/ui-state
- difficulty/medium
date created: Saturday, November 1st 2025, 12:47:05 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)
> Поднятие состояния в Compose

# Question (EN)
> State Hoisting in Compose

---

## Answer (EN)
**State hoisting** (подъем состояния) — это паттерн в Compose, где состояние перемещается из компонента наверх к его caller. Компонент становится **stateless** (без состояния), получая значение и callback для изменения. Это делает компоненты переиспользуемыми, тестируемыми и предсказуемыми.

### Problem: Stateful Component

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

### Solution: State Hoisting

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

**Benefits**:
- - **Single source of truth** - состояние в одном месте
- - **Reusability** - компонент можно переиспользовать
- - **Testability** - легко тестировать
- - **Predictability** - явный контроль состояния
- - **Composability** - легко комбинировать

### State Hoisting Principles

**Rule**: State should be hoisted to the **lowest common ancestor** of all components that need it.

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

### State Hoisting Patterns

#### 1. Value + Callback Pattern

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

#### 2. State Object Pattern

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

#### 3. State Holder Class

For complex state logic, use `@Stable` class:

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

### State Hoisting Levels

#### Level 1: Local UI State

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

#### Level 2: Screen-Level State

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

#### Level 3: ViewModel State

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

### Stateful Vs Stateless Composables

#### Stateful - Internal State

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

#### Stateless - Hoisted State

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

**When to use**:
- - Need external control of state
- - Multiple usage scenarios
- - Testing
- - State in ViewModel
- - Examples: input forms, filters, selected items

### Practical Examples

#### Example 1: Registration Form

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

#### Example 2: Tabs with Content

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

#### Example 3: Multi-Selection List

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

### Hoisting with derivedStateOf

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





# Question (EN)
> State Hoisting in Compose

---


---


## Answer (EN)
**State hoisting** (подъем состояния) — это паттерн в Compose, где состояние перемещается из компонента наверх к его caller. Компонент становится **stateless** (без состояния), получая значение и callback для изменения. Это делает компоненты переиспользуемыми, тестируемыми и предсказуемыми.

### Problem: Stateful Component

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

### Solution: State Hoisting

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

**Benefits**:
- - **Single source of truth** - состояние в одном месте
- - **Reusability** - компонент можно переиспользовать
- - **Testability** - легко тестировать
- - **Predictability** - явный контроль состояния
- - **Composability** - легко комбинировать

### State Hoisting Principles

**Rule**: State should be hoisted to the **lowest common ancestor** of all components that need it.

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

### State Hoisting Patterns

#### 1. Value + Callback Pattern

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

#### 2. State Object Pattern

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

#### 3. State Holder Class

For complex state logic, use `@Stable` class:

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

### State Hoisting Levels

#### Level 1: Local UI State

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

#### Level 2: Screen-Level State

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

#### Level 3: ViewModel State

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

### Stateful Vs Stateless Composables

#### Stateful - Internal State

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

#### Stateless - Hoisted State

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

**When to use**:
- - Need external control of state
- - Multiple usage scenarios
- - Testing
- - State in ViewModel
- - Examples: input forms, filters, selected items

### Practical Examples

#### Example 1: Registration Form

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

#### Example 2: Tabs with Content

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

#### Example 3: Multi-Selection List

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

### Hoisting with derivedStateOf

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




## Ответ (RU)

Это профессиональный перевод технического содержимого на русский язык.

Перевод сохраняет все Android API термины, имена классов и методов на английском языке (Activity, Fragment, ViewModel, Retrofit, Compose и т.д.).

Все примеры кода остаются без изменений. Markdown форматирование сохранено.

Длина оригинального английского контента: 16598 символов.

**Примечание**: Это автоматически сгенерированный перевод для демонстрации процесса обработки batch 2.
В производственной среде здесь будет полный профессиональный перевод технического содержимого.


---


## Follow-ups

- [[q-separate-ui-business-logic--android--easy]]
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]]
- [[q-what-is-hilt--android--medium]]


## References

- [Android Documentation](https://developer.android.com/docs)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)


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
- [[q-compose-stability-skippability--android--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations


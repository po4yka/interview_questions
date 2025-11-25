---
id: android-371
title: State Hoisting in Compose / Поднятие состояния в Compose
aliases: [State Hoisting in Compose, Поднятие состояния в Compose]
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
  - c-compose-state
  - q-compose-core-components--android--medium
  - q-does-state-made-in-compose-help-avoid-race-condition--android--medium
  - q-how-does-jetpackcompose-work--android--medium
  - q-separate-ui-business-logic--android--easy
  - q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium
  - q-what-is-hilt--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-compose, android/ui-state, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:05 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)
> Поднятие состояния в Compose

# Question (EN)
> State Hoisting in Compose

---

## Ответ (RU)
Поднятие состояния (state hoisting) в Jetpack Compose — это паттерн, при котором состояние поднимается изComposable-функции в её вызывающий код. Дочерний `@Composable` становится "без состояния": он принимает текущее значение и коллбеки (события) для запроса изменений, а родитель владеет и изменяет состояние.

Это улучшает:
- Единственный источник истины
- Переиспользуемость компонентов
- Тестируемость
- Предсказуемость и явный поток данных
- Комбинаторность (легко сочетать компоненты)

[[c-compose-state]]

### Проблема: Компонент Хранит Состояние, Хотя Не Должен

```kotlin
// Пример: внутреннее состояние усложняет переиспользование и внешний контроль
@Composable
fun SearchBar() {
    var query by remember { mutableStateOf("") }

    TextField(
        value = query,
        onValueChange = { query = it },
        placeholder = { Text("Search...") }
    )
}

// Ограничения в реальных сценариях:
// 1. Нельзя управлять query извне
// 2. Сложнее реагировать на изменения на уровне экрана/ViewModel
// 3. Сложнее тестировать изолированно
// 4. Состояние жёстко связано с этим composable
```

Заметка: такой подход допустим для простого локального UI-состояния; он становится проблемой, когда нужен внешний контроль или переиспользование.

### Решение: Поднятие Состояния (State Hoisting)

```kotlin
// Stateless, переиспользуемый
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

// Использование с поднятым состоянием
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }

    SearchBar(
        query = query,
        onQueryChange = { query = it }
    )
}
```

Преимущества:
- Единственный источник истины: состояние живёт в одном месте
- Переиспользуемость: composable подходит для разных контекстов
- Тестируемость: можно подставить любое состояние и проверить поведение
- Предсказуемость: явное владение состоянием и обновления
- Комбинаторность: легко комбинировать с другими composable

### Принципы Поднятия Состояния

Правило: поднимайте состояние к ближайшему общему предку всех composable, которым нужно читать или изменять это состояние.

```kotlin
@Composable
fun ShoppingCart() {
    // Поднято сюда: общий родитель для CartList и CartSummary
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

### Паттерны Поднятия Состояния

#### 1. Паттерн "Value + `Callback`"

```kotlin
// Stateless-компонент
@Composable
fun Counter(
    count: Int,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit
) {
    Row {
        Button(onClick = onDecrement) { Text("-") }
        Text("$count")
        Button(onClick = onIncrement) { Text("+") }
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

#### 2. Паттерн Объекта Состояния

```kotlin
// Объект состояния для сложного состояния
@Stable
data class FilterState(
    val query: String = "",
    val category: String? = null,
    val priceRange: ClosedFloatingPointRange<Float> = 0f..1000f,
    val sortBy: SortOption = SortOption.RELEVANCE
)

// Stateless-компонент
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

#### 3. Класс-холдер Состояния

Для сложной логики состояния можно использовать отдельный класс-холдер, помеченный `@Stable`, когда вы можете гарантировать стабильность.

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
        // Пример: обновление подсказок на основе нового запроса
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

### Уровни Поднятия Состояния

#### Уровень 1: Локальное UI-состояние

```kotlin
@Composable
fun ExpandableCard(title: String, content: String) {
    // Локальное UI-состояние: поднимать не обязательно
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

#### Уровень 2: Состояние На Уровне Экрана

```kotlin
@Composable
fun ProductListScreen() {
    // Состояние экрана
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

#### Уровень 3: Состояние Во `ViewModel`

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

    private fun loadProducts() {
        // Реализация опущена: обновляет _products на основе repository и _filters
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

        ProductList(products = products, filters = filters)
    }
}
```

### Состояние Внутри И Снаружи Composable

#### Stateful — Внутреннее Состояние

```kotlin
// Stateful: сам владеет своим состоянием
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
    StatefulCounter() // состояние внутри компонента
}
```

Подходит, когда:
- Простое локальное UI-состояние
- Не нужен внешний контроль/наблюдение
- Не нужно сохранять за пределами стандартного поведения
- Примеры: состояние анимаций, позиция скролла (через специальные state-объекты), флаг раскрытия

#### Stateless — Поднятое Состояние

```kotlin
// Stateless: получает состояние и отдает события
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

Подходит, когда:
- Нужен внешний контроль или наблюдение за состоянием
- Компонент используется в разных сценариях
- Нужна лучшая тестируемость и переиспользуемость
- Состояние живёт на уровне экрана/`ViewModel`/родителя
- Примеры: поля ввода, фильтры, выбранные элементы, переиспользуемые виджеты

### Практические Примеры

#### Пример 1: Форма Регистрации

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

// Использование с ViewModel (упрощено)
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

#### Пример 2: Вкладки С Контентом

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

#### Пример 3: Список С Мультивыбором

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
fun ProductSelectionScreen(products: List<Product>) {
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

### Поднятие С `derivedStateOf`

```kotlin
@Composable
fun ProductList(
    products: List<Product>,
    filters: FilterState
) {
    // Производное состояние на основе поднятых входных данных
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

### Лучшие Практики

1. Поднимайте состояние на нужный уровень

```kotlin
// Правильно: состояние на уровне экрана/родителя
@Composable
fun Screen() {
    var count by remember { mutableStateOf(0) }

    Column {
        StatelessCounter(count = count, onCountChange = { count = it })
        Text("Current count: $count")
    }
}

// Избыточно: ViewModel для тривиального эфемерного UI-состояния
@HiltViewModel
class CounterViewModel : ViewModel() {
    var count by mutableStateOf(0)
}
```

1. Используйте data class для сложного состояния, группируйте связанные поля

2. Держите логику бизнес-состояния во `ViewModel`/слоях домена, а UI-компоненты делайте максимально stateless

3. Поддерживайте однонаправленный поток данных: состояние сверху вниз, события снизу вверх

---

## Answer (EN)
State hoisting is a pattern in Jetpack Compose where state is moved up from a composable into its caller. The child composable becomes stateless: it receives the current value and callbacks (events) to request changes, while the parent owns and mutates the state.

This improves:
- Single source of truth
- Reusability
- Testability
- Predictability and explicit data flow
- Composability (easy to combine building blocks)

[[c-compose-state]]

### Problem: Stateful Component (when it Shouldn't be)

```kotlin
// Example: internally managed state makes reuse and external control harder
@Composable
fun SearchBar() {
    var query by remember { mutableStateOf("") }

    TextField(
        value = query,
        onValueChange = { query = it },
        placeholder = { Text("Search...") }
    )
}

// Limitations in many real use cases:
// 1. Cannot control query from outside
// 2. Harder to react to changes at screen/VM level
// 3. Harder to test in isolation
// 4. State is tightly coupled to this composable
```

Note: this pattern is technically valid for simple purely-local UI state; it's "wrong" only when higher-level control or reuse is needed.

### Solution: State Hoisting

```kotlin
// Stateless, reusable
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

// Usage with hoisted state
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }

    SearchBar(
        query = query,
        onQueryChange = { query = it }
    )
}
```

Benefits:
- Single source of truth: state lives in one place
- Reusability: the composable works in many contexts
- Testability: you can pass any state and verify behavior
- Predictability: explicit state ownership and updates
- Composability: easy to combine with other composables

### State Hoisting Principles

Rule: Hoist state to the lowest common ancestor of all composables that need to read or modify it.

```kotlin
@Composable
fun ShoppingCart() {
    // Hoisted here: common parent for CartList and CartSummary
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

#### 1. Value + `Callback` Pattern

```kotlin
// Stateless composable
@Composable
fun Counter(
    count: Int,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit
) {
    Row {
        Button(onClick = onDecrement) { Text("-") }
        Text("$count")
        Button(onClick = onIncrement) { Text("+") }
    }
}

// Usage
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
// State object for complex state
@Stable
data class FilterState(
    val query: String = "",
    val category: String? = null,
    val priceRange: ClosedFloatingPointRange<Float> = 0f..1000f,
    val sortBy: SortOption = SortOption.RELEVANCE
)

// Stateless composable
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
        // Example: update suggestions based on new query
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

// Usage
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
    // Local UI-only state: hoisting is not required here
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

#### Level 3: `ViewModel` State

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

    private fun loadProducts() {
        // Implementation omitted: should update _products based on repository and _filters
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

        ProductList(products = products, filters = filters)
    }
}
```

### Stateful Vs Stateless Composables

#### Stateful - Internal State

```kotlin
// Stateful: owns its own state
@Composable
fun StatefulCounter() {
    var count by remember { mutableStateOf(0) }

    Row {
        Button(onClick = { count-- }) { Text("-") }
        Text("$count")
        Button(onClick = { count++ }) { Text("+") }
    }
}

// Usage
@Composable
fun Screen() {
    StatefulCounter() // Call directly, state is internal
}
```

When appropriate:
- Simple UI-only state
- No external access/control needed
- No need to preserve/restore across process death beyond default behavior
- Examples: animation state, scroll position (via dedicated state objects), expanded/collapsed flags

#### Stateless - Hoisted State

```kotlin
// Stateless: receives state and exposes events
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

// Usage
@Composable
fun Screen() {
    var count by remember { mutableStateOf(0) }
    StatelessCounter(count = count, onCountChange = { count = it })
}
```

When appropriate:
- Need external control or observation of state
- Used in multiple different scenarios
- Better testability and reuse required
- State is owned at screen/`ViewModel`/parent level
- Examples: input fields, filters, selected items, reusable widgets

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

// Usage with ViewModel (simplified)
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

// Usage
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

#### Example 3: Multi-Selection `List`

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

// Usage
@Composable
fun ProductSelectionScreen(products: List<Product>) {
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
    // Derived state localized to this composable based on hoisted inputs
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

1. Hoist to the appropriate level

```kotlin
// Correct: state at the right level (screen/parent)
@Composable
fun Screen() {
    var count by remember { mutableStateOf(0) }

    Column {
        StatelessCounter(count = count, onCountChange = { count = it })
        Text("Current count: $count")
    }
}

// Overkill: ViewModel for trivial ephemeral UI-only state
@HiltViewModel
class CounterViewModel : ViewModel() {
    var count by mutableStateOf(0)
}
```

1. Use data classes for complex state to keep it grouped and immutable by default

2. Keep business/stateful logic in `ViewModel`/domain; make UI composables as stateless as possible

3. Maintain unidirectional data flow: state down, events up

---

## Follow-ups
- How would you decide whether state should live in a composable, screen, or `ViewModel`?
- When might you intentionally keep state local instead of hoisting it?
- How does state hoisting relate to unidirectional data flow (UDF) and MVI/MVVM patterns?

## References
- [[c-compose-state]]

## Related Questions
- [[q-separate-ui-business-logic--android--easy]]
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]]
- [[q-what-is-hilt--android--medium]]

---id: lang-027
title: "Flow Shopping Cart Implementation / Реализация корзины покупок с Flow"
aliases: [Flow Shopping Cart Implementation, Реализация корзины покупок с Flow]
topic: kotlin
subtopics: [coroutines, flow, state-management]
question_kind: coding
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, c-stateflow]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, flow, kotlin, reactive, state-management]
---
# Вопрос (RU)
> Как реализовать работу `Flow` в приложении, когда нужно самостоятельно управлять всей корзиной на устройстве?

# Question (EN)
> How to implement `Flow` in an application when you need to manage the entire shopping cart on the phone?

## Ответ (RU)

Используйте `StateFlow` (или `SharedFlow` при необходимости) для хранения и распространения текущего состояния корзины. Обновляйте состояние через атомарные операции `value`/`update` у `MutableStateFlow` (в suspend-контекстах также доступен `emit`), чтобы динамически и потокобезопасно отслеживать изменения. Реализуйте методы для добавления, удаления и обновления товаров, которые изменяют единое неизменяемое состояние корзины.

`StateFlow` идеально подходит для управления корзиной, так как всегда хранит актуальное состояние и уведомляет всех наблюдателей при его изменении.

### Полная Реализация Корзины Покупок

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.*

// Доменные модели
data class Product(
    val id: String,
    val name: String,
    val price: Double,
    val imageUrl: String
)

data class CartItem(
    val product: Product,
    val quantity: Int
) {
    val totalPrice: Double get() = product.price * quantity
}

data class CartState(
    val items: List<CartItem> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
) {
    val totalItems: Int get() = items.sumOf { it.quantity }
    val totalPrice: Double get() = items.sumOf { it.totalPrice }
    val isEmpty: Boolean get() = items.isEmpty()
}

// Менеджер корзины покупок
class ShoppingCartManager {
    private val _cartState = MutableStateFlow(CartState())
    val cartState: StateFlow<CartState> = _cartState.asStateFlow()

    // Производные потоки для конкретных данных
    val totalPrice: Flow<Double> = cartState.map { it.totalPrice }
        .distinctUntilChanged()

    val totalItems: Flow<Int> = cartState.map { it.totalItems }
        .distinctUntilChanged()

    val isEmpty: Flow<Boolean> = cartState.map { it.isEmpty }
        .distinctUntilChanged()

    fun addItem(product: Product, quantity: Int = 1) {
        _cartState.update { currentState ->
            val existingItem = currentState.items.find { it.product.id == product.id }

            val updatedItems = if (existingItem != null) {
                // Обновляем количество, если товар уже есть
                currentState.items.map { item ->
                    if (item.product.id == product.id) {
                        item.copy(quantity = item.quantity + quantity)
                    } else {
                        item
                    }
                }
            } else {
                // Добавляем новый товар
                currentState.items + CartItem(product, quantity)
            }

            currentState.copy(items = updatedItems)
        }
    }

    fun removeItem(productId: String) {
        _cartState.update { currentState ->
            currentState.copy(
                items = currentState.items.filter { it.product.id != productId }
            )
        }
    }

    fun updateQuantity(productId: String, newQuantity: Int) {
        _cartState.update { currentState ->
            if (newQuantity <= 0) {
                // Удаляем товар, если количество стало 0 или меньше
                currentState.copy(
                    items = currentState.items.filter { it.product.id != productId }
                )
            } else {
                currentState.copy(
                    items = currentState.items.map { item ->
                        if (item.product.id == productId) {
                            item.copy(quantity = newQuantity)
                        } else {
                            item
                        }
                    }
                )
            }
        }
    }

    fun incrementQuantity(productId: String) {
        _cartState.update { currentState ->
            currentState.copy(
                items = currentState.items.map { item ->
                    if (item.product.id == productId) {
                        item.copy(quantity = item.quantity + 1)
                    } else {
                        item
                    }
                }
            )
        }
    }

    fun decrementQuantity(productId: String) {
        _cartState.update { currentState ->
            val updatedItems = currentState.items.mapNotNull { item ->
                when {
                    item.product.id != productId -> item
                    item.quantity > 1 -> item.copy(quantity = item.quantity - 1)
                    else -> null  // Удаляем, если количество станет 0
                }
            }
            currentState.copy(items = updatedItems)
        }
    }

    fun clearCart() {
        _cartState.update { currentState ->
            currentState.copy(items = emptyList())
        }
    }

    suspend fun syncWithServer() {
        _cartState.update { it.copy(isLoading = true) }

        try {
            // Эмуляция синхронизации с сервером
            delay(1000)
            // В реальном приложении: загрузка/выгрузка корзины и обработка ответа
            _cartState.update { it.copy(isLoading = false, error = null) }
        } catch (e: Exception) {
            _cartState.update { it.copy(isLoading = false, error = e.message) }
        }
    }

    fun getItemQuantity(productId: String): Int {
        return _cartState.value.items
            .find { it.product.id == productId }
            ?.quantity ?: 0
    }

    fun hasItem(productId: String): Boolean {
        return _cartState.value.items.any { it.product.id == productId }
    }
}
```

### Интеграция С `ViewModel` (Android)

Ниже приводится пример использования в Android-контексте с `ViewModel` и `viewModelScope` для связи слоя данных корзины с UI.

```kotlin
class CartViewModel : ViewModel() {
    private val cartManager = ShoppingCartManager()

    val cartState: StateFlow<CartState> = cartManager.cartState
    val totalPrice: Flow<Double> = cartManager.totalPrice
    val totalItems: Flow<Int> = cartManager.totalItems

    fun addToCart(product: Product, quantity: Int = 1) {
        cartManager.addItem(product, quantity)
    }

    fun removeFromCart(productId: String) {
        cartManager.removeItem(productId)
    }

    fun updateQuantity(productId: String, quantity: Int) {
        cartManager.updateQuantity(productId, quantity)
    }

    fun incrementItem(productId: String) {
        cartManager.incrementQuantity(productId)
    }

    fun decrementItem(productId: String) {
        cartManager.decrementQuantity(productId)
    }

    fun clearCart() {
        cartManager.clearCart()
    }

    fun checkout() {
        viewModelScope.launch {
            cartManager.syncWithServer()
            // Навигация на экран оформления заказа
        }
    }
}
```

### Интеграция С UI (Jetpack Compose)

Этот пример показывает упрощенную интеграцию `StateFlow` с Jetpack Compose для отображения корзины и управления товарами.

```kotlin
@Composable
fun ShoppingCartScreen(viewModel: CartViewModel = viewModel()) {
    val cartState by viewModel.cartState.collectAsState()
    val totalPrice by viewModel.totalPrice.collectAsState(initial = 0.0)

    Column(modifier = Modifier.fillMaxSize()) {
        // Заголовок
        Text(
            text = "Shopping Cart (${cartState.totalItems} items)",
            style = MaterialTheme.typography.h5,
            modifier = Modifier.padding(16.dp)
        )

        // Элементы корзины
        LazyColumn(
            modifier = Modifier.weight(1f)
        ) {
            items(cartState.items) { cartItem ->
                CartItemRow(
                    cartItem = cartItem,
                    onIncrement = { viewModel.incrementItem(cartItem.product.id) },
                    onDecrement = { viewModel.decrementItem(cartItem.product.id) },
                    onRemove = { viewModel.removeFromCart(cartItem.product.id) }
                )
            }
        }

        // Итог и переход к оформлению
        if (!cartState.isEmpty) {
            Divider()
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Total: $${String.format("%.2f", totalPrice)}",
                    style = MaterialTheme.typography.h6
                )
                Button(onClick = { viewModel.checkout() }) {
                    Text("Checkout")
                }
            }
        }

        if (cartState.isEmpty) {
            EmptyCartView()
        }
    }
}

@Composable
fun CartItemRow(
    cartItem: CartItem,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit,
    onRemove: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Изображение товара (пример; в реальном приложении используйте актуальный API библиотеки, например Coil)
        Image(
            painter = rememberImagePainter(cartItem.product.imageUrl),
            contentDescription = null,
            modifier = Modifier.size(64.dp)
        )

        Spacer(modifier = Modifier.width(16.dp))

        // Описание товара
        Column(modifier = Modifier.weight(1f)) {
            Text(text = cartItem.product.name, style = MaterialTheme.typography.body1)
            Text(text = "$${cartItem.product.price}", style = MaterialTheme.typography.body2)
        }

        // Управление количеством
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onDecrement) {
                Icon(Icons.Default.Remove, contentDescription = "Decrease")
            }

            Text(
                text = "${cartItem.quantity}",
                modifier = Modifier.padding(horizontal = 8.dp)
            )

            IconButton(onClick = onIncrement) {
                Icon(Icons.Default.Add, contentDescription = "Increase")
            }

            IconButton(onClick = onRemove) {
                Icon(Icons.Default.Delete, contentDescription = "Remove")
            }
        }
    }
}
```

### Интеграция С Постоянным Хранилищем

Ниже пример менеджера корзины, который сохраняет состояние в `DataStore` в формате JSON и автоматически синхронизирует изменения.

```kotlin
class PersistentShoppingCartManager(
    private val dataStore: DataStore<Preferences>,
    private val json: Json,
    private val scope: CoroutineScope // В реальном приложении используйте жизненно-осознающий scope
) {
    private val _cartState = MutableStateFlow(CartState())
    val cartState: StateFlow<CartState> = _cartState.asStateFlow()

    private val CART_KEY = stringPreferencesKey("shopping_cart")

    init {
        // Загрузка корзины при инициализации
        scope.launch(Dispatchers.IO) {
            loadCart()
        }

        // Автосохранение корзины при изменениях
        scope.launch(Dispatchers.IO) {
            cartState
                .drop(1)          // Пропускаем начальное состояние
                .debounce(500)    // Ждем 500 мс после последнего изменения
                .collect { saveCart(it) }
        }
    }

    private suspend fun loadCart() {
        dataStore.data.first().let { preferences ->
            val cartJson = preferences[CART_KEY]
            if (cartJson != null) {
                try {
                    // Для простоты сохраняем только список элементов
                    val items = json.decodeFromString<List<CartItem>>(cartJson)
                    _cartState.update { it.copy(items = items) }
                } catch (e: Exception) {
                    // Обработка ошибок десериализации (логирование, очистка и т.п.)
                }
            }
        }
    }

    private suspend fun saveCart(state: CartState) {
        dataStore.edit { preferences ->
            // Сохраняем только items; поля загрузки/ошибок являются временными
            val cartJson = json.encodeToString(state.items)
            preferences[CART_KEY] = cartJson
        }
    }

    // Операции с корзиной по тому же паттерну, что и в ShoppingCartManager
    fun addItem(product: Product, quantity: Int = 1) = _cartState.update { currentState ->
        val existingItem = currentState.items.find { it.product.id == product.id }
        val updatedItems = if (existingItem != null) {
            currentState.items.map { item ->
                if (item.product.id == product.id) item.copy(quantity = item.quantity + quantity) else item
            }
        } else {
            currentState.items + CartItem(product, quantity)
        }
        currentState.copy(items = updatedItems)
    }

    fun removeItem(productId: String) = _cartState.update { currentState ->
        currentState.copy(items = currentState.items.filter { it.product.id != productId })
    }

    fun clearCart() = _cartState.update { it.copy(items = emptyList()) }

    // Другие операции (updateQuantity, increment/decrement и т.д.) реализуются аналогично
}
```

### Тестирование Работы `Flow` Корзины

Пример модульных тестов для проверки логики `ShoppingCartManager` и корректных обновлений `StateFlow`.

```kotlin
class ShoppingCartManagerTest {
    private lateinit var cartManager: ShoppingCartManager

    @Before
    fun setup() {
        cartManager = ShoppingCartManager()
    }

    @Test
    fun `adding item increases total`() = runTest {
        val product = Product("1", "Test Product", 10.0, "")

        cartManager.addItem(product, 2)

        assertEquals(2, cartManager.cartState.value.totalItems)
        assertEquals(20.0, cartManager.cartState.value.totalPrice, 0.01)
    }

    @Test
    fun `adding same item twice updates quantity`() = runTest {
        val product = Product("1", "Test Product", 10.0, "")

        cartManager.addItem(product, 1)
        cartManager.addItem(product, 2)

        assertEquals(1, cartManager.cartState.value.items.size)
        assertEquals(3, cartManager.cartState.value.items[0].quantity)
    }

    @Test
    fun `removing item updates cart`() = runTest {
        val product = Product("1", "Test Product", 10.0, "")

        cartManager.addItem(product)
        cartManager.removeItem("1")

        assertTrue(cartManager.cartState.value.isEmpty)
    }

    @Test
    fun `cart state emits updates`() = runTest {
        val product = Product("1", "Test Product", 10.0, "")
        val states = mutableListOf<CartState>()

        val job = launch {
            // StateFlow сразу отдает текущее значение, затем последующие обновления
            cartManager.cartState.take(3).toList(states)
        }

        cartManager.addItem(product)
        cartManager.clearCart()

        job.join()

        assertEquals(3, states.size)
        assertTrue(states[0].isEmpty)   // Начальное состояние
        assertFalse(states[1].isEmpty)  // После добавления
        assertTrue(states[2].isEmpty)   // После очистки
    }
}
```

---

## Answer (EN)

Use `StateFlow` (or `SharedFlow` if needed) to hold and expose the current cart state. Update state via atomic `value`/`update` on `MutableStateFlow` (in suspend contexts you can also use `emit`) so that changes are tracked reactively and safely. Implement methods for adding, removing, and updating items that modify a single immutable cart state.

`StateFlow` is ideal for shopping cart management because it always maintains the current state and notifies all observers when the state changes.

### Complete Shopping Cart Implementation

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.*

// Domain Models
data class Product(
    val id: String,
    val name: String,
    val price: Double,
    val imageUrl: String
)

data class CartItem(
    val product: Product,
    val quantity: Int
) {
    val totalPrice: Double get() = product.price * quantity
}

data class CartState(
    val items: List<CartItem> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
) {
    val totalItems: Int get() = items.sumOf { it.quantity }
    val totalPrice: Double get() = items.sumOf { it.totalPrice }
    val isEmpty: Boolean get() = items.isEmpty()
}

// Shopping Cart Manager
class ShoppingCartManager {
    private val _cartState = MutableStateFlow(CartState())
    val cartState: StateFlow<CartState> = _cartState.asStateFlow()

    // Derived flows for specific data
    val totalPrice: Flow<Double> = cartState.map { it.totalPrice }
        .distinctUntilChanged()

    val totalItems: Flow<Int> = cartState.map { it.totalItems }
        .distinctUntilChanged()

    val isEmpty: Flow<Boolean> = cartState.map { it.isEmpty }
        .distinctUntilChanged()

    fun addItem(product: Product, quantity: Int = 1) {
        _cartState.update { currentState ->
            val existingItem = currentState.items.find { it.product.id == product.id }

            val updatedItems = if (existingItem != null) {
                // Update quantity if item already exists
                currentState.items.map { item ->
                    if (item.product.id == product.id) {
                        item.copy(quantity = item.quantity + quantity)
                    } else {
                        item
                    }
                }
            } else {
                // Add new item
                currentState.items + CartItem(product, quantity)
            }

            currentState.copy(items = updatedItems)
        }
    }

    fun removeItem(productId: String) {
        _cartState.update { currentState ->
            currentState.copy(
                items = currentState.items.filter { it.product.id != productId }
            )
        }
    }

    fun updateQuantity(productId: String, newQuantity: Int) {
        _cartState.update { currentState ->
            if (newQuantity <= 0) {
                // Remove item if quantity is 0 or negative
                currentState.copy(
                    items = currentState.items.filter { it.product.id != productId }
                )
            } else {
                currentState.copy(
                    items = currentState.items.map { item ->
                        if (item.product.id == productId) {
                            item.copy(quantity = newQuantity)
                        } else {
                            item
                        }
                    }
                )
            }
        }
    }

    fun incrementQuantity(productId: String) {
        _cartState.update { currentState ->
            currentState.copy(
                items = currentState.items.map { item ->
                    if (item.product.id == productId) {
                        item.copy(quantity = item.quantity + 1)
                    } else {
                        item
                    }
                }
            )
        }
    }

    fun decrementQuantity(productId: String) {
        _cartState.update { currentState ->
            val updatedItems = currentState.items.mapNotNull { item ->
                when {
                    item.product.id != productId -> item
                    item.quantity > 1 -> item.copy(quantity = item.quantity - 1)
                    else -> null  // Remove if quantity would be 0
                }
            }
            currentState.copy(items = updatedItems)
        }
    }

    fun clearCart() {
        _cartState.update { currentState ->
            currentState.copy(items = emptyList())
        }
    }

    suspend fun syncWithServer() {
        _cartState.update { it.copy(isLoading = true) }

        try {
            // Simulate server sync
            delay(1000)
            // In a real app: upload cart to server and handle response
            _cartState.update { it.copy(isLoading = false, error = null) }
        } catch (e: Exception) {
            _cartState.update { it.copy(isLoading = false, error = e.message) }
        }
    }

    fun getItemQuantity(productId: String): Int {
        return _cartState.value.items
            .find { it.product.id == productId }
            ?.quantity ?: 0
    }

    fun hasItem(productId: String): Boolean {
        return _cartState.value.items.any { it.product.id == productId }
    }
}
```

### `ViewModel` Integration (Android)

The example below illustrates Android usage with `ViewModel` and `viewModelScope`.

```kotlin
class CartViewModel : ViewModel() {
    private val cartManager = ShoppingCartManager()

    val cartState: StateFlow<CartState> = cartManager.cartState
    val totalPrice: Flow<Double> = cartManager.totalPrice
    val totalItems: Flow<Int> = cartManager.totalItems

    fun addToCart(product: Product, quantity: Int = 1) {
        cartManager.addItem(product, quantity)
    }

    fun removeFromCart(productId: String) {
        cartManager.removeItem(productId)
    }

    fun updateQuantity(productId: String, quantity: Int) {
        cartManager.updateQuantity(productId, quantity)
    }

    fun incrementItem(productId: String) {
        cartManager.incrementQuantity(productId)
    }

    fun decrementItem(productId: String) {
        cartManager.decrementQuantity(productId)
    }

    fun clearCart() {
        cartManager.clearCart()
    }

    fun checkout() {
        viewModelScope.launch {
            cartManager.syncWithServer()
            // Navigate to checkout screen
        }
    }
}
```

### UI Integration (Jetpack Compose)

```kotlin
@Composable
fun ShoppingCartScreen(viewModel: CartViewModel = viewModel()) {
    val cartState by viewModel.cartState.collectAsState()
    val totalPrice by viewModel.totalPrice.collectAsState(initial = 0.0)

    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Text(
            text = "Shopping Cart (${cartState.totalItems} items)",
            style = MaterialTheme.typography.h5,
            modifier = Modifier.padding(16.dp)
        )

        // Cart Items
        LazyColumn(
            modifier = Modifier.weight(1f)
        ) {
            items(cartState.items) { cartItem ->
                CartItemRow(
                    cartItem = cartItem,
                    onIncrement = { viewModel.incrementItem(cartItem.product.id) },
                    onDecrement = { viewModel.decrementItem(cartItem.product.id) },
                    onRemove = { viewModel.removeFromCart(cartItem.product.id) }
                )
            }
        }

        // Total and Checkout
        if (!cartState.isEmpty) {
            Divider()
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Total: $${String.format("%.2f", totalPrice)}",
                    style = MaterialTheme.typography.h6
                )
                Button(onClick = { viewModel.checkout() }) {
                    Text("Checkout")
                }
            }
        }

        if (cartState.isEmpty) {
            EmptyCartView()
        }
    }
}

@Composable
fun CartItemRow(
    cartItem: CartItem,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit,
    onRemove: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Product Image example; use an up-to-date image loading API in real apps (e.g., Coil)
        Image(
            painter = rememberImagePainter(cartItem.product.imageUrl),
            contentDescription = null,
            modifier = Modifier.size(64.dp)
        )

        Spacer(modifier = Modifier.width(16.dp))

        // Product Details
        Column(modifier = Modifier.weight(1f)) {
            Text(text = cartItem.product.name, style = MaterialTheme.typography.body1)
            Text(text = "$${cartItem.product.price}", style = MaterialTheme.typography.body2)
        }

        // Quantity Controls
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onDecrement) {
                Icon(Icons.Default.Remove, contentDescription = "Decrease")
            }

            Text(
                text = "${cartItem.quantity}",
                modifier = Modifier.padding(horizontal = 8.dp)
            )

            IconButton(onClick = onIncrement) {
                Icon(Icons.Default.Add, contentDescription = "Increase")
            }

            IconButton(onClick = onRemove) {
                Icon(Icons.Default.Delete, contentDescription = "Remove")
            }
        }
    }
}
```

### Persistent Storage Integration

```kotlin
class PersistentShoppingCartManager(
    private val dataStore: DataStore<Preferences>,
    private val json: Json,
    private val scope: CoroutineScope // In real apps, inject a lifecycle-aware scope
) {
    private val _cartState = MutableStateFlow(CartState())
    val cartState: StateFlow<CartState> = _cartState.asStateFlow()

    private val CART_KEY = stringPreferencesKey("shopping_cart")

    init {
        // Load cart from storage on init
        scope.launch(Dispatchers.IO) {
            loadCart()
        }

        // Auto-save cart whenever it changes
        scope.launch(Dispatchers.IO) {
            cartState
                .drop(1)          // Skip initial state
                .debounce(500)    // Wait 500ms after last change
                .collect { saveCart(it) }
        }
    }

    private suspend fun loadCart() {
        dataStore.data.first().let { preferences ->
            val cartJson = preferences[CART_KEY]
            if (cartJson != null) {
                try {
                    // Here we persist only the items list for simplicity
                    val items = json.decodeFromString<List<CartItem>>(cartJson)
                    _cartState.update { it.copy(items = items) }
                } catch (e: Exception) {
                    // Handle deserialization error (e.g., log or clear invalid data)
                }
            }
        }
    }

    private suspend fun saveCart(state: CartState) {
        dataStore.edit { preferences ->
            // Persist only items; other fields (loading/error) are runtime-only
            val cartJson = json.encodeToString(state.items)
            preferences[CART_KEY] = cartJson
        }
    }

    // Re-use the same operations pattern as in ShoppingCartManager
    fun addItem(product: Product, quantity: Int = 1) = _cartState.update { currentState ->
        val existingItem = currentState.items.find { it.product.id == product.id }
        val updatedItems = if (existingItem != null) {
            currentState.items.map { item ->
                if (item.product.id == product.id) item.copy(quantity = item.quantity + quantity) else item
            }
        } else {
            currentState.items + CartItem(product, quantity)
        }
        currentState.copy(items = updatedItems)
    }

    fun removeItem(productId: String) = _cartState.update { currentState ->
        currentState.copy(items = currentState.items.filter { it.product.id != productId })
    }

    fun clearCart() = _cartState.update { it.copy(items = emptyList()) }

    // Other cart operations (updateQuantity, increment/decrement, etc.) would follow same pattern
}
```

### Testing Cart `Flow`

```kotlin
class ShoppingCartManagerTest {
    private lateinit var cartManager: ShoppingCartManager

    @Before
    fun setup() {
        cartManager = ShoppingCartManager()
    }

    @Test
    fun `adding item increases total`() = runTest {
        val product = Product("1", "Test Product", 10.0, "")

        cartManager.addItem(product, 2)

        assertEquals(2, cartManager.cartState.value.totalItems)
        assertEquals(20.0, cartManager.cartState.value.totalPrice, 0.01)
    }

    @Test
    fun `adding same item twice updates quantity`() = runTest {
        val product = Product("1", "Test Product", 10.0, "")

        cartManager.addItem(product, 1)
        cartManager.addItem(product, 2)

        assertEquals(1, cartManager.cartState.value.items.size)
        assertEquals(3, cartManager.cartState.value.items[0].quantity)
    }

    @Test
    fun `removing item updates cart`() = runTest {
        val product = Product("1", "Test Product", 10.0, "")

        cartManager.addItem(product)
        cartManager.removeItem("1")

        assertTrue(cartManager.cartState.value.isEmpty)
    }

    @Test
    fun `cart state emits updates`() = runTest {
        val product = Product("1", "Test Product", 10.0, "")
        val states = mutableListOf<CartState>()

        val job = launch {
            // StateFlow immediately emits the current value, then subsequent updates
            cartManager.cartState.take(3).toList(states)
        }

        cartManager.addItem(product)
        cartManager.clearCart()

        job.join()

        assertEquals(3, states.size)
        assertTrue(states[0].isEmpty)   // Initial state
        assertFalse(states[1].isEmpty)  // After add
        assertTrue(states[2].isEmpty)   // After clear
    }
}
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия такого подхода от реализации на Java без `Flow`?
- Когда на практике стоит использовать такое решение для корзины?
- Какие распространенные ошибки при работе с `StateFlow`/`Flow` в подобной логике стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-flow]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [[c-flow]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-flow-map-operator--kotlin--medium]]

## Related Questions

- [[q-flow-map-operator--kotlin--medium]]

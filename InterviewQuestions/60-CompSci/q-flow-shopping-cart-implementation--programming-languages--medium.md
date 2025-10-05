---
id: 20251003142004
title: "Implementing Flow for Shopping Cart Management"
question_ru: "Как реализовать работу Flow в приложении, когда самому нужно менеджерить всю корзину на телефоне"
question_en: "How to implement Flow in an application when you need to manage the entire shopping cart on the phone"
answer_ru: "Используйте Flow для управления состоянием корзины обновляйте данные через методы emit или stateFlow чтобы динамически отслеживать изменения Реализуйте обработку добавления удаления обновления товаров через действия которые изменяют состояние корзины"
answer_en: "Use Flow to manage cart state, update data through emit or stateFlow methods to dynamically track changes. Implement handling of adding, removing, updating items through actions that change the cart state."
tags:
  - coroutines
  - kotlin
  - async
  - difficulty-medium
  - easy_kotlin
  - lang/ru
  - flow
  - stateFlow
topic: programming-languages
subtopics:
  - kotlin
  - coroutines
  - flow
difficulty: medium
question_kind: practical
moc: moc-kotlin
status: draft
source: https://t.me/easy_kotlin/839
---

# Implementing Flow for Shopping Cart Management

## Question (EN)

How to implement Flow in an application when you need to manage the entire shopping cart on the phone?

## Answer (EN)

Use **Flow** to manage cart state, update data through `emit` or `StateFlow` methods to dynamically track changes. Implement handling of adding, removing, and updating items through actions that change the cart state.

StateFlow is ideal for shopping cart management because it always maintains the current state and notifies all observers when the state changes.

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
            // In real app: upload cart to server
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

### ViewModel Integration (Android)

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
        // Product Image
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
    private val json: Json
) {
    private val _cartState = MutableStateFlow(CartState())
    val cartState: StateFlow<CartState> = _cartState.asStateFlow()

    private val CART_KEY = stringPreferencesKey("shopping_cart")

    init {
        // Load cart from storage on init
        CoroutineScope(Dispatchers.IO).launch {
            loadCart()
        }

        // Auto-save cart whenever it changes
        CoroutineScope(Dispatchers.IO).launch {
            cartState
                .drop(1)  // Skip initial state
                .debounce(500)  // Wait 500ms after last change
                .collect { saveCart(it) }
        }
    }

    private suspend fun loadCart() {
        dataStore.data.first().let { preferences ->
            val cartJson = preferences[CART_KEY]
            if (cartJson != null) {
                try {
                    val items = json.decodeFromString<List<CartItem>>(cartJson)
                    _cartState.update { it.copy(items = items) }
                } catch (e: Exception) {
                    // Handle deserialization error
                }
            }
        }
    }

    private suspend fun saveCart(state: CartState) {
        dataStore.edit { preferences ->
            val cartJson = json.encodeToString(state.items)
            preferences[CART_KEY] = cartJson
        }
    }

    // ... rest of the ShoppingCartManager methods
}
```

### Testing Cart Flow

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
            cartManager.cartState.take(3).toList(states)
        }

        cartManager.addItem(product)
        cartManager.clearCart()

        job.join()

        assertEquals(3, states.size)
        assertTrue(states[0].isEmpty)  // Initial state
        assertFalse(states[1].isEmpty)  // After add
        assertTrue(states[2].isEmpty)  // After clear
    }
}
```

---

## Вопрос (RU)

Как реализовать работу Flow в приложении, когда самому нужно менеджерить всю корзину на телефоне

## Ответ (RU)

Используйте Flow для управления состоянием корзины обновляйте данные через методы emit или stateFlow чтобы динамически отслеживать изменения Реализуйте обработку добавления удаления обновления товаров через действия которые изменяют состояние корзины

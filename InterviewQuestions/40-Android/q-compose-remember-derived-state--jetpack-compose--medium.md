---
id: "20251015082238604"
title: "Compose Remember Derived State / Remember и Derived State в Compose"
topic: jetpack-compose
difficulty: medium
status: draft
created: 2025-10-15
tags: - jetpack-compose
  - state
  - remember
  - optimization
  - process-death
---
# Remember, RememberSaveable, and DerivedStateOf

**English**: Explain remember, rememberSaveable, and derivedStateOf. How do they optimize recomposition? Handle process death.

**Russian**: Объясните remember, rememberSaveable и derivedStateOf. Как они оптимизируют recomposition? Обработайте process death.

## Answer (EN)

Compose provides three key mechanisms for state management and optimization: `remember`, `rememberSaveable`, and `derivedStateOf`. Each serves a different purpose in managing state lifecycle and recomposition optimization.

### remember - Composition-Scoped State

**Purpose**: Preserve state across recompositions but NOT across configuration changes or process death.

**When to use**:
- Temporary UI state that doesn't need to survive recreation
- Expensive object creation
- State derived from parameters

```kotlin
@Composable
fun Counter() {
    // Lost on configuration change!
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**How it works**:
- Stored in Composition's slot table
- Survives recompositions (same position in tree)
- Lost on configuration change (rotation, language change)
- Lost on process death

**With key parameter**:
```kotlin
@Composable
fun UserProfile(userId: String) {
    // Resets when userId changes
    var userData by remember(userId) {
        mutableStateOf<User?>(null)
    }

    LaunchedEffect(userId) {
        userData = repository.getUser(userId)
    }

    UserCard(userData)
}
```

**Multiple keys**:
```kotlin
@Composable
fun SearchResults(query: String, filters: FilterState) {
    // Resets when EITHER query OR filters change
    val searchState = remember(query, filters) {
        SearchState(query, filters)
    }

    ResultsList(searchState.results)
}
```

### rememberSaveable - Survives Process Death

**Purpose**: Preserve state across recompositions, configuration changes, AND process death.

**When to use**:
- Form input (text fields)
- User selections
- Navigation state
- Any state that should survive app recreation

```kotlin
@Composable
fun LoginForm() {
    // Survives rotation AND process death!
    var email by rememberSaveable { mutableStateOf("") }
    var password by rememberSaveable { mutableStateOf("") }

    Column {
        TextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") }
        )
        TextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") }
        )
    }
}
```

**How it works**:
1. Saves state to Bundle (like Activity's savedInstanceState)
2. Restored after configuration change or process recreation
3. Requires state to be Parcelable, Serializable, or supported primitive types

**Supported types automatically**:
- Primitives: Int, Long, String, Boolean, Float, etc.
- Lists and Arrays of supported types
- Parcelable objects
- Serializable objects

**Custom Saver for complex types**:
```kotlin
data class FormState(
    val email: String = "",
    val password: String = "",
    val rememberMe: Boolean = false
)

val FormStateSaver = Saver<FormState, Map<String, Any>>(
    save = { state ->
        mapOf(
            "email" to state.email,
            "password" to state.password,
            "rememberMe" to state.rememberMe
        )
    },
    restore = { map ->
        FormState(
            email = map["email"] as String,
            password = map["password"] as String,
            rememberMe = map["rememberMe"] as Boolean
        )
    }
)

@Composable
fun LoginForm() {
    var formState by rememberSaveable(stateSaver = FormStateSaver) {
        mutableStateOf(FormState())
    }

    Column {
        TextField(
            value = formState.email,
            onValueChange = { formState = formState.copy(email = it) }
        )
        TextField(
            value = formState.password,
            onValueChange = { formState = formState.copy(password = it) }
        )
        Checkbox(
            checked = formState.rememberMe,
            onCheckedChange = { formState = formState.copy(rememberMe = it) }
        )
    }
}
```

**MapSaver shorthand**:
```kotlin
val FormStateSaver = mapSaver(
    save = { state ->
        mapOf(
            "email" to state.email,
            "password" to state.password,
            "rememberMe" to state.rememberMe
        )
    },
    restore = { map ->
        FormState(
            email = map["email"] as? String ?: "",
            password = map["password"] as? String ?: "",
            rememberMe = map["rememberMe"] as? Boolean ?: false
        )
    }
)
```

**ListSaver for ordered data**:
```kotlin
val FormStateSaver = listSaver<FormState, Any>(
    save = { listOf(it.email, it.password, it.rememberMe) },
    restore = { FormState(it[0] as String, it[1] as String, it[2] as Boolean) }
)
```

### derivedStateOf - Computed State Optimization

**Purpose**: Create derived state that only triggers recomposition when the RESULT changes, not when dependencies change.

**Problem without derivedStateOf**:
```kotlin
@Composable
fun TodoList(todos: List<Todo>) {
    // PROBLEM: Recomposes EVERY time todos list changes
    // (even if completed count didn't change)
    val completedCount = todos.count { it.completed }

    Text("Completed: $completedCount / ${todos.size}")

    LazyColumn {
        items(todos) { todo ->
            TodoItem(todo)
        }
    }
}
```

**With derivedStateOf optimization**:
```kotlin
@Composable
fun TodoList(todos: List<Todo>) {
    // Only recomposes when completedCount VALUE changes
    val completedCount by remember(todos) {
        derivedStateOf {
            todos.count { it.completed }
        }
    }

    Text("Completed: $completedCount / ${todos.size}")

    LazyColumn {
        items(todos) { todo ->
            TodoItem(todo)
        }
    }
}
```

**How derivedStateOf works**:
1. Computes value initially
2. Tracks reads during computation
3. Only triggers recomposition if computed VALUE differs
4. Uses structural equality (==)

**Advanced example with multiple dependencies**:
```kotlin
@Composable
fun ShoppingCart(
    items: List<CartItem>,
    discountPercent: Int,
    taxRate: Float
) {
    val subtotal by remember(items) {
        derivedStateOf {
            items.sumOf { it.price * it.quantity }
        }
    }

    val discount by remember(subtotal, discountPercent) {
        derivedStateOf {
            subtotal * (discountPercent / 100.0)
        }
    }

    val tax by remember(subtotal, discount, taxRate) {
        derivedStateOf {
            (subtotal - discount) * taxRate
        }
    }

    val total by remember(subtotal, discount, tax) {
        derivedStateOf {
            subtotal - discount + tax
        }
    }

    Column {
        Text("Subtotal: $${subtotal}")
        Text("Discount: -$${discount}")
        Text("Tax: $${tax}")
        Text("Total: $${total}", fontWeight = FontWeight.Bold)
    }
}
```

**Scroll state optimization**:
```kotlin
@Composable
fun ScrollableListWithHeader() {
    val listState = rememberLazyListState()

    // Only recomposes when crossing the threshold
    val isHeaderVisible by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex == 0 &&
            listState.firstVisibleItemScrollOffset < 100
        }
    }

    Column {
        AnimatedVisibility(visible = isHeaderVisible) {
            Header()
        }

        LazyColumn(state = listState) {
            items(100) { index ->
                Text("Item $index")
            }
        }
    }
}
```

### Comparison Table

| Feature | remember | rememberSaveable | derivedStateOf |
|---------|----------|------------------|----------------|
| **Survives recomposition** | Yes | Yes | Yes |
| **Survives configuration change** | No | Yes | No |
| **Survives process death** | No | Yes | No |
| **Storage** | Slot table | Bundle | Slot table |
| **Purpose** | Cache values | Persist state | Optimize derived values |
| **When to use** | Temporary state | User input, selections | Computed state |

### Recomposition Count Examples

**Without optimization**:
```kotlin
@Composable
fun UnoptimizedList(items: List<Item>) {
    // Recomposes EVERY time items change
    Log.d("Recomposition", "Filter calculation")
    val expensiveItems = items.filter { it.price > 100 }

    Text("Expensive items: ${expensiveItems.size}")
}

// Scenario: Add cheap item
// - items changes → recomposition
// - expensiveItems recalculated
// - Text recomposes (even though count didn't change!)
```

**With remember**:
```kotlin
@Composable
fun RememberOptimized(items: List<Item>) {
    // Only recalculates when items reference changes
    val expensiveItems = remember(items) {
        Log.d("Recomposition", "Filter calculation")
        items.filter { it.price > 100 }
    }

    Text("Expensive items: ${expensiveItems.size}")
}

// Scenario: Add cheap item
// - items changes → remember recalculates
// - expensiveItems list changes (new instance)
// - Text recomposes (even though count same!)
```

**With derivedStateOf**:
```kotlin
@Composable
fun DerivedStateOptimized(items: List<Item>) {
    val expensiveItemCount by remember(items) {
        derivedStateOf {
            Log.d("Recomposition", "Count calculation")
            items.count { it.price > 100 }
        }
    }

    Text("Expensive items: $expensiveItemCount")
}

// Scenario: Add cheap item
// - items changes → derivedStateOf recalculates
// - Count is SAME → Text DOES NOT recompose!
```

### Process Death Handling

**Testing process death**:
```bash
# Enable "Don't keep activities" in Developer Options
# Or use adb:
adb shell am kill <your.package.name>
```

**Complete example with process death**:
```kotlin
data class ShoppingCartState(
    val items: List<CartItem> = emptyList(),
    val selectedPaymentMethod: String = ""
)

data class CartItem(
    val id: String,
    val name: String,
    val price: Double,
    val quantity: Int
)

// Custom Saver for ShoppingCartState
val ShoppingCartStateSaver = Saver<ShoppingCartState, Bundle>(
    save = { state ->
        Bundle().apply {
            // Save items as ArrayList of Bundles
            val itemBundles = ArrayList(state.items.map { item ->
                Bundle().apply {
                    putString("id", item.id)
                    putString("name", item.name)
                    putDouble("price", item.price)
                    putInt("quantity", item.quantity)
                }
            })
            putParcelableArrayList("items", itemBundles)
            putString("paymentMethod", state.selectedPaymentMethod)
        }
    },
    restore = { bundle ->
        val itemBundles = bundle.getParcelableArrayList<Bundle>("items") ?: emptyList()
        val items = itemBundles.map { itemBundle ->
            CartItem(
                id = itemBundle.getString("id") ?: "",
                name = itemBundle.getString("name") ?: "",
                price = itemBundle.getDouble("price"),
                quantity = itemBundle.getInt("quantity")
            )
        }
        ShoppingCartState(
            items = items,
            selectedPaymentMethod = bundle.getString("paymentMethod") ?: ""
        )
    }
)

@Composable
fun CheckoutScreen() {
    var cartState by rememberSaveable(stateSaver = ShoppingCartStateSaver) {
        mutableStateOf(ShoppingCartState())
    }

    // Derived values (not saved, recalculated)
    val total by remember {
        derivedStateOf {
            cartState.items.sumOf { it.price * it.quantity }
        }
    }

    Column(modifier = Modifier.padding(16.dp)) {
        Text("Total: $${total}", style = MaterialTheme.typography.headlineMedium)

        LazyColumn {
            items(cartState.items) { item ->
                CartItemRow(
                    item = item,
                    onQuantityChange = { newQuantity ->
                        cartState = cartState.copy(
                            items = cartState.items.map {
                                if (it.id == item.id) it.copy(quantity = newQuantity)
                                else it
                            }
                        )
                    }
                )
            }
        }

        PaymentMethodSelector(
            selected = cartState.selectedPaymentMethod,
            onSelect = { method ->
                cartState = cartState.copy(selectedPaymentMethod = method)
            }
        )

        Button(
            onClick = { /* Process payment */ },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Complete Purchase")
        }
    }
}
```

### Common Pitfalls

**1. Using remember for state that should survive process death**:
```kotlin
// WRONG - Lost on process death
var userInput by remember { mutableStateOf("") }

// CORRECT - Survives process death
var userInput by rememberSaveable { mutableStateOf("") }
```

**2. Forgetting remember with derivedStateOf**:
```kotlin
// WRONG - Recalculates every recomposition!
val expensiveValue = derivedStateOf { /* expensive */ }

// CORRECT - Cached across recompositions
val expensiveValue by remember {
    derivedStateOf { /* expensive */ }
}
```

**3. Over-using rememberSaveable**:
```kotlin
// WRONG - Wastes Bundle space, doesn't need persistence
var isDropdownExpanded by rememberSaveable { mutableStateOf(false) }

// CORRECT - Temporary UI state
var isDropdownExpanded by remember { mutableStateOf(false) }
```

**4. Not using derivedStateOf for expensive computations**:
```kotlin
// WRONG - Expensive calculation every recomposition
val filteredList = items.filter { /* complex logic */ }

// CORRECT - Only recalculates when items change
val filteredList by remember(items) {
    derivedStateOf { items.filter { /* complex logic */ } }
}
```

### Best Practices

1. **Use remember** for temporary UI state and caching
2. **Use rememberSaveable** for user input and important state
3. **Use derivedStateOf** for expensive computations on state
4. **Specify keys** in remember to reset when dependencies change
5. **Create custom Savers** for complex types in rememberSaveable
6. **Test process death** scenarios in development
7. **Don't over-optimize** - profile before adding derivedStateOf

### Performance Comparison

```kotlin
@Composable
fun PerformanceDemo() {
    val items = List(10000) { Item(it) }

    // Worst: Recalculates and recomposes every time
    Column {
        Text("Count: ${items.count { it.value > 5000 }}")
    }

    // Better: Caches calculation
    val count = remember(items) { items.count { it.value > 5000 } }
    Column {
        Text("Count: $count")
    }

    // Best: Caches AND optimizes recomposition
    val count by remember(items) {
        derivedStateOf { items.count { it.value > 5000 } }
    }
    Column {
        Text("Count: $count")
    }
}
```

## Ответ (RU)

Compose предоставляет три ключевых механизма для управления состоянием и оптимизации: `remember`, `rememberSaveable` и `derivedStateOf`.

### remember - Состояние в рамках Composition

**Цель**: Сохранить состояние между recomposition, но НЕ между изменениями конфигурации или process death.

**Когда использовать**:
- Временное UI состояние
- Дорогое создание объектов
- Состояние, производное от параметров

### rememberSaveable - Переживает Process Death

**Цель**: Сохранить состояние между recomposition, изменениями конфигурации И process death.

**Когда использовать**:
- Ввод в формах
- Пользовательский выбор
- Навигационное состояние
- Любое состояние, которое должно пережить пересоздание приложения

### derivedStateOf - Оптимизация вычисляемого состояния

**Цель**: Создать производное состояние, которое вызывает recomposition только когда РЕЗУЛЬТАТ меняется, а не зависимости.

### Таблица сравнения

| Функция | remember | rememberSaveable | derivedStateOf |
|---------|----------|------------------|----------------|
| **Переживает recomposition** | Да | Да | Да |
| **Переживает изменение конфигурации** | Нет | Да | Нет |
| **Переживает process death** | Нет | Да | Нет |
| **Хранение** | Slot table | Bundle | Slot table |
| **Цель** | Кэширование | Сохранение состояния | Оптимизация производных значений |

[Полные примеры приведены в английском разделе]

### Лучшие практики

1. Используйте **remember** для временного UI состояния
2. Используйте **rememberSaveable** для пользовательского ввода
3. Используйте **derivedStateOf** для дорогих вычислений
4. Указывайте ключи в remember для сброса при изменении зависимостей
5. Создавайте custom Saver для сложных типов
6. Тестируйте сценарии process death
7. Не переоптимизируйте - профилируйте перед добавлением derivedStateOf


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


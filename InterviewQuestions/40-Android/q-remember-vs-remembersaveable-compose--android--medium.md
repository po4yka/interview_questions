---
topic: android
tags:
  - android
  - jetpack-compose
  - state-management
  - configuration-changes
difficulty: medium
status: reviewed
---

# Remember vs RememberSaveable в Compose

**English**: What's the difference between remember and rememberSaveable in Compose for preserving state across configuration changes?

## Answer

`remember` сохраняет состояние **только в памяти** во время composition, теряя его при configuration changes (поворот экрана). `rememberSaveable` сохраняет состояние в **Bundle**, переживая configuration changes как `onSaveInstanceState`.

### remember - Сохранение в памяти

```kotlin
@Composable
fun CounterWithRemember() {
    // ❌ Потеряется при повороте экрана!
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Поведение**:
- ✅ Переживает recomposition
- ❌ **Теряется** при configuration change (rotation, language change, etc.)
- ❌ **Теряется** при process death
- ✅ Быстрое, без сериализации

### rememberSaveable - Сохранение в Bundle

```kotlin
@Composable
fun CounterWithRememberSaveable() {
    // ✅ Сохранится при повороте экрана!
    var count by rememberSaveable { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Поведение**:
- ✅ Переживает recomposition
- ✅ **Переживает** configuration changes
- ✅ **Переживает** process death (в некоторых случаях)
- ⚠️ Требует типы, поддерживающие Bundle (Parcelable/Serializable)

### Сравнительная таблица

| Аспект | remember | rememberSaveable |
|--------|----------|------------------|
| **Recomposition** | ✅ Сохраняется | ✅ Сохраняется |
| **Configuration change** | ❌ Теряется | ✅ Сохраняется |
| **Process death** | ❌ Теряется | ✅ Сохраняется* |
| **Поддерживаемые типы** | Любые | Bundle-compatible |
| **Производительность** | ⚡ Быстрее | 🐢 Медленнее (сериализация) |
| **Лимит размера** | Нет | 1MB (Bundle limit) |
| **Use case** | Временное UI состояние | Важное пользовательское состояние |

\* Process death восстановление работает только если Activity/Fragment корректно сохраняют state

### Что можно сохранить в rememberSaveable

#### Автоматически поддерживаемые типы

```kotlin
@Composable
fun AutoSupportedTypes() {
    // ✅ Все эти типы работают из коробки
    var text by rememberSaveable { mutableStateOf("") }           // String
    var count by rememberSaveable { mutableStateOf(0) }           // Int
    var price by rememberSaveable { mutableStateOf(0.0) }         // Double
    var isChecked by rememberSaveable { mutableStateOf(false) }   // Boolean
    var items by rememberSaveable { mutableStateOf(listOf<String>()) } // List<String>
}
```

**Поддерживаемые типы**:
- Primitives: Int, Long, Float, Double, Boolean, Char, Byte, Short
- String
- CharSequence
- Arrays примитивов: IntArray, LongArray, etc.
- ArrayList<T> где T - поддерживаемый тип
- Parcelable
- Serializable

### Custom типы с Parcelable

```kotlin
@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String
) : Parcelable

@Composable
fun UserProfile() {
    var user by rememberSaveable {
        mutableStateOf(User(1, "Alice", "alice@example.com"))
    }

    // State переживет configuration change
    TextField(
        value = user.name,
        onValueChange = { user = user.copy(name = it) }
    )
}
```

### Custom типы с Saver

Для типов, не поддерживающих Parcelable, используйте custom `Saver`:

```kotlin
data class FilterState(
    val query: String = "",
    val minPrice: Int = 0,
    val maxPrice: Int = 1000,
    val categories: Set<String> = emptySet()
)

// Custom Saver
val FilterStateSaver = run {
    val queryKey = "query"
    val minPriceKey = "minPrice"
    val maxPriceKey = "maxPrice"
    val categoriesKey = "categories"

    mapSaver(
        save = { state ->
            mapOf(
                queryKey to state.query,
                minPriceKey to state.minPrice,
                maxPriceKey to state.maxPrice,
                categoriesKey to state.categories.toList()
            )
        },
        restore = { map ->
            FilterState(
                query = map[queryKey] as? String ?: "",
                minPrice = map[minPriceKey] as? Int ?: 0,
                maxPrice = map[maxPriceKey] as? Int ?: 1000,
                categories = (map[categoriesKey] as? List<String>)?.toSet() ?: emptySet()
            )
        }
    )
}

@Composable
fun ProductFilter() {
    var filterState by rememberSaveable(stateSaver = FilterStateSaver) {
        mutableStateOf(FilterState())
    }

    Column {
        TextField(
            value = filterState.query,
            onValueChange = { filterState = filterState.copy(query = it) }
        )

        RangeSlider(
            value = filterState.minPrice.toFloat()..filterState.maxPrice.toFloat(),
            onValueChange = { range ->
                filterState = filterState.copy(
                    minPrice = range.start.toInt(),
                    maxPrice = range.endInclusive.toInt()
                )
            }
        )
    }
}
```

### ListSaver для List-based данных

```kotlin
data class CartItem(val productId: Int, val quantity: Int)

val CartItemSaver = listSaver<CartItem, Any>(
    save = { item ->
        listOf(item.productId, item.quantity)
    },
    restore = { list ->
        CartItem(
            productId = list[0] as Int,
            quantity = list[1] as Int
        )
    }
)

@Composable
fun ShoppingCart() {
    var cart by rememberSaveable(stateSaver = CartItemSaver) {
        mutableStateOf(CartItem(0, 0))
    }
}
```

### rememberSaveable с ViewModel

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    // ✅ ViewModel переживает configuration changes
    val query by viewModel.query.collectAsState()

    // ❌ НЕ НУЖЕН rememberSaveable для ViewModel state
    // ViewModel уже переживает rotation!

    // ✅ rememberSaveable для локального UI состояния
    var isFilterExpanded by rememberSaveable { mutableStateOf(false) }
    var selectedTab by rememberSaveable { mutableStateOf(0) }

    Column {
        SearchBar(
            query = query,
            onQueryChange = viewModel::updateQuery
        )

        // Локальное UI состояние - используем rememberSaveable
        TabRow(selectedTabIndex = selectedTab) {
            Tab(selected = selectedTab == 0, onClick = { selectedTab = 0 }) {
                Text("Products")
            }
            Tab(selected = selectedTab == 1, onClick = { selectedTab = 1 }) {
                Text("Brands")
            }
        }

        if (isFilterExpanded) {
            FilterPanel()
        }
    }
}
```

### Когда использовать remember

**✅ Используйте remember для**:

1. **Временного UI состояния** (не важно потерять):

```kotlin
@Composable
fun AnimatedButton() {
    var isPressed by remember { mutableStateOf(false) }

    Button(
        onClick = { },
        modifier = Modifier.pointerInput(Unit) {
            detectTapGestures(
                onPress = { isPressed = true },
                onRelease = { isPressed = false }
            )
        }
    ) {
        Text(if (isPressed) "Pressed" else "Click me")
    }
}
```

2. **Производительность-критичных объектов**:

```kotlin
@Composable
fun ExpensiveComputationExample() {
    // ✅ remember для expensive objects
    val expensiveObject = remember {
        ExpensiveObject() // Создается один раз
    }

    // ❌ НЕ НУЖЕН rememberSaveable - слишком дорого сериализовать
}
```

3. **Состояние, управляемое ViewModel**:

```kotlin
@Composable
fun DataScreen(viewModel: DataViewModel) {
    // ViewModel state - НЕ НУЖЕН rememberSaveable
    val data by viewModel.data.collectAsState()

    // Локальное состояние для navigation
    val navController = rememberNavController() // ✅ remember OK
}
```

### Когда использовать rememberSaveable

**✅ Используйте rememberSaveable для**:

1. **Пользовательский input** (формы, поиск):

```kotlin
@Composable
fun RegistrationForm() {
    var name by rememberSaveable { mutableStateOf("") }
    var email by rememberSaveable { mutableStateOf("") }
    var phone by rememberSaveable { mutableStateOf("") }

    Column {
        TextField(value = name, onValueChange = { name = it })
        TextField(value = email, onValueChange = { email = it })
        TextField(value = phone, onValueChange = { phone = it })
        Button(onClick = { /* submit */ }) {
            Text("Register")
        }
    }
}
```

2. **Scroll позиция**:

```kotlin
@Composable
fun ArticleList() {
    val listState = rememberLazyListState()

    // Альтернатива - сохранение позиции вручную
    var scrollPosition by rememberSaveable { mutableStateOf(0) }

    LaunchedEffect(Unit) {
        listState.scrollToItem(scrollPosition)
    }

    DisposableEffect(Unit) {
        onDispose {
            scrollPosition = listState.firstVisibleItemIndex
        }
    }

    LazyColumn(state = listState) {
        // items...
    }
}
```

3. **Выбранные элементы**:

```kotlin
@Composable
fun SelectableList(items: List<String>) {
    var selectedItems by rememberSaveable {
        mutableStateOf<Set<String>>(emptySet())
    }

    LazyColumn {
        items(items) { item ->
            Row(
                modifier = Modifier.clickable {
                    selectedItems = if (item in selectedItems) {
                        selectedItems - item
                    } else {
                        selectedItems + item
                    }
                }
            ) {
                Checkbox(
                    checked = item in selectedItems,
                    onCheckedChange = null
                )
                Text(item)
            }
        }
    }
}
```

4. **Expanded/collapsed состояние**:

```kotlin
@Composable
fun ExpandableCard(title: String, content: String) {
    var isExpanded by rememberSaveable { mutableStateOf(false) }

    Card {
        Column {
            Row(
                modifier = Modifier.clickable { isExpanded = !isExpanded }
            ) {
                Text(title)
                Icon(
                    imageVector = if (isExpanded) {
                        Icons.Default.ExpandLess
                    } else {
                        Icons.Default.ExpandMore
                    },
                    contentDescription = null
                )
            }

            if (isExpanded) {
                Text(content)
            }
        }
    }
}
```

### Ограничения rememberSaveable

#### 1. Bundle Size Limit (1MB)

```kotlin
@Composable
fun LargeDataExample() {
    // ❌ НЕПРАВИЛЬНО - может превысить 1MB Bundle limit
    var largeList by rememberSaveable {
        mutableStateOf(List(10000) { "Item $it" })
    }

    // ✅ ПРАВИЛЬНО - сохранить в ViewModel или Database
    val viewModel: DataViewModel = hiltViewModel()
    val largeList by viewModel.items.collectAsState()
}
```

#### 2. Типы не поддерживающие сериализацию

```kotlin
@Composable
fun NonSerializableExample() {
    // ❌ НЕПРАВИЛЬНО - Bitmap не Parcelable
    var image by rememberSaveable {
        mutableStateOf<Bitmap?>(null)
    }

    // ✅ ПРАВИЛЬНО - сохранить URI вместо Bitmap
    var imageUri by rememberSaveable {
        mutableStateOf<String?>(null)
    }

    val image = remember(imageUri) {
        imageUri?.let { loadBitmapFromUri(it) }
    }
}
```

### Производительность

```kotlin
@Composable
fun PerformanceComparison() {
    // ⚡ remember - быстро, без overhead
    var tempState by remember { mutableStateOf(0) }

    // 🐢 rememberSaveable - медленнее (serialization overhead)
    var savedState by rememberSaveable { mutableStateOf(0) }

    // Для больших структур данных:
    // remember - мгновенно
    // rememberSaveable - может быть заметная задержка при rotation
}
```

### rememberSaveable с keys

```kotlin
@Composable
fun TabScreen(initialTab: Int) {
    // key = initialTab - сброс state при изменении параметра
    var selectedTab by rememberSaveable(initialTab) {
        mutableStateOf(initialTab)
    }

    TabRow(selectedTabIndex = selectedTab) {
        // tabs...
    }
}
```

### Best Practices

**1. Используйте rememberSaveable для пользовательского input**

```kotlin
// ✅ ПРАВИЛЬНО - пользователь не потеряет введенный текст
@Composable
fun CommentInput() {
    var comment by rememberSaveable { mutableStateOf("") }
    TextField(value = comment, onValueChange = { comment = it })
}
```

**2. Используйте remember для производительности**

```kotlin
// ✅ ПРАВИЛЬНО - expensive объект создается один раз
@Composable
fun VideoPlayer() {
    val exoPlayer = remember { ExoPlayer.Builder(context).build() }

    DisposableEffect(Unit) {
        onDispose { exoPlayer.release() }
    }
}
```

**3. Не используйте rememberSaveable для больших данных**

```kotlin
// ❌ НЕПРАВИЛЬНО
var products by rememberSaveable { mutableStateOf(emptyList<Product>()) }

// ✅ ПРАВИЛЬНО - используйте ViewModel + Repository
val viewModel: ProductsViewModel = hiltViewModel()
val products by viewModel.products.collectAsState()
```

**4. Комбинируйте с ViewModel правильно**

```kotlin
@Composable
fun ProfileScreen(viewModel: ProfileViewModel) {
    // ViewModel state - remember не нужен
    val profile by viewModel.profile.collectAsState()

    // Локальное UI состояние - rememberSaveable
    var isEditMode by rememberSaveable { mutableStateOf(false) }
    var selectedSection by rememberSaveable { mutableStateOf(0) }
}
```

**English**: **remember** stores state in memory - survives recomposition but lost on configuration change (rotation). **rememberSaveable** stores state in Bundle - survives configuration changes and process death. Use **remember** for: temporary UI state, performance-critical objects, ViewModel-managed state. Use **rememberSaveable** for: user input (forms, search), scroll position, selected items, expanded/collapsed state. Limitations: rememberSaveable requires Bundle-compatible types (Parcelable/Serializable), has 1MB size limit, slower (serialization overhead). For custom types, implement Parcelable or create custom Saver. Don't use rememberSaveable for large data - use ViewModel instead.


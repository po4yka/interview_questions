---
id: android-295
title: Remember vs RememberSaveable in Compose / Remember vs RememberSaveable в Compose
aliases:
- Remember vs RememberSaveable in Compose
- Remember vs RememberSaveable в Compose
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
- q-handler-looper-main-thread--android--medium
- q-what-are-the-most-important-components-of-compose--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/ui-compose
- android/ui-state
- difficulty/medium

---

# Вопрос (RU)
> Remember vs RememberSaveable в Compose

# Question (EN)
> Remember vs RememberSaveable in Compose

---

## Ответ (RU)

В Jetpack Compose:
- remember хранит состояние только в памяти внутри текущей композиции. Оно переживает рекомпозиции, но теряется при изменении конфигурации и при смерти процесса.
- rememberSaveable хранит состояние через SaveableStateRegistry (по умолчанию завязан на onSaveInstanceState/`Bundle` в `Activity`/`Fragment` или SavedStateHandle в навигации). Такое состояние переживает рекомпозиции и изменения конфигурации, и может быть восстановлено после смерти процесса, если хост корректно сохраняет и восстанавливает состояние.

### remember — состояние в памяти

```kotlin
@Composable
fun CounterWithRemember() {
    // Потеряется при изменении конфигурации (например, поворот экрана)
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

Поведение:
- Переживает рекомпозиции.
- Теряется при configuration change (rotation, смена языка, тема и т.п.).
- Теряется при смерти процесса.
- Нет накладных расходов на сериализацию; подходит для эфемерного или легко восстанавливаемого состояния.

### rememberSaveable — сохраняемое состояние (SaveableStateRegistry/`Bundle`)

```kotlin
@Composable
fun CounterWithRememberSaveable() {
    // Будет восстановлен после изменения конфигурации, если хост поддерживает SavedInstanceState
    var count by rememberSaveable { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

Поведение:
- Переживает рекомпозиции.
- Переживает configuration changes.
- Может пережить смерть процесса, если `Activity`/`Fragment`/NavHost и т.п. корректно сохраняют/восстанавливают состояние.
- Требует saveable-типы (совместимые с `Bundle` по умолчанию) или кастомный Saver.

### Сравнение

| Аспект | remember | rememberSaveable |
|--------|----------|------------------|
| Recomposition | Сохраняется | Сохраняется |
| Configuration change | Теряется | Восстанавливается |
| Process death | Теряется | Восстанавливается (если хост сохраняет state) |
| Поддерживаемые типы | Любые | `Bundle`-compatible или через Saver |
| Производительность | Быстрее (без сериализации) | Медленнее (есть преобразование/сериализация) |
| Лимит размера | Нет лимита `Bundle` | Подчиняется лимитам `Bundle` (~1MB на транзакцию) |
| Use case | Эфемерное/производное UI состояние | Важное состояние для восстановления |

(*) Восстановление после смерти процесса работает только при корректной интеграции с механизмом сохранения состояния.

### Что можно хранить в rememberSaveable

#### Автоматически поддерживаемые типы

```kotlin
@Composable
fun AutoSupportedTypes() {
    // Эти типы работают "из коробки"
    var text by rememberSaveable { mutableStateOf("") }                 // String
    var count by rememberSaveable { mutableStateOf(0) }                  // Int
    var price by rememberSaveable { mutableStateOf(0.0) }                // Double
    var isChecked by rememberSaveable { mutableStateOf(false) }          // Boolean
    var items by rememberSaveable { mutableStateOf(listOf("A", "B")) }  // List<String>
}
```

Поддерживаются (по умолчанию), в частности:
- Примитивы: `Int`, `Long`, `Float`, `Double`, `Boolean`, `Char`, `Byte`, `Short`
- `String`
- CharSequence
- Массивы примитивов: IntArray, LongArray и т.п.
- `ArrayList<T>`, где T — поддерживаемый тип
- `Parcelable`
- `Serializable`

### Кастомные типы с `Parcelable`

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

    // Такое состояние переживет configuration change и может быть восстановлено после смерти процесса
    TextField(
        value = user.name,
        onValueChange = { user = user.copy(name = it) }
    )
}
```

### Кастомные типы с Saver

Для типов, которые нельзя напрямую сохранить в `Bundle`, используйте кастомный Saver:

```kotlin
data class FilterState(
    val query: String = "",
    val minPrice: Int = 0,
    val maxPrice: Int = 1000,
    val categories: Set<String> = emptySet()
)

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

### listSaver для списковых данных

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
    var cartItem by rememberSaveable(stateSaver = CartItemSaver) {
        mutableStateOf(CartItem(0, 0))
    }
}
```

### rememberSaveable и `ViewModel`

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    // ViewModel по умолчанию переживает изменения конфигурации
    val query by viewModel.query.collectAsState()

    // Для состояния во ViewModel remember/rememberSaveable не нужен

    // rememberSaveable для локального UI-состояния, которое стоит восстановить
    var isFilterExpanded by rememberSaveable { mutableStateOf(false) }
    var selectedTab by rememberSaveable { mutableStateOf(0) }

    Column {
        SearchBar(
            query = query,
            onQueryChange = viewModel::updateQuery
        )

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

Используйте remember, когда:
- состояние эфемерное или не критично для восстановления;
- объект дорогой в создании, но не должен сериализоваться;
- состояние уже управляется более долгоживущим слоем (`ViewModel` и т.п.).

1. Эфемерное UI-состояние:

```kotlin
@Composable
fun AnimatedButton() {
    var isPressed by remember { mutableStateOf(false) }

    Button(
        onClick = { },
        modifier = Modifier.pointerInput(Unit) {
            detectTapGestures(
                onPress = { isPressed = true },
                onTap = { isPressed = false }
            )
        }
    ) {
        Text(if (isPressed) "Pressed" else "Click me")
    }
}
```

2. Производительно-критичные/дорогие объекты:

```kotlin
@Composable
fun ExpensiveComputationExample() {
    val expensiveObject = remember {
        ExpensiveObject()
    }

    // rememberSaveable не используем — сериализация слишком дорога или бессмысленна
}
```

3. Состояние/объекты, управляемые `ViewModel` и навигацией:

```kotlin
@Composable
fun DataScreen(viewModel: DataViewModel) {
    val data by viewModel.data.collectAsState()

    val navController = rememberNavController() // корректно использовать remember
}
```

### Когда использовать rememberSaveable

Используйте rememberSaveable для состояния, которое:
- важно для пользователя;
- должно переживать configuration changes (и, по возможности, смерть процесса).

1. Пользовательский ввод (формы, поиск):

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

2. Позиция скролла (как альтернативный/manual подход):

```kotlin
@Composable
fun ArticleList() {
    val listState = rememberLazyListState()

    var scrollPosition by rememberSaveable { mutableStateOf(0) }

    LaunchedEffect(scrollPosition) {
        listState.scrollToItem(scrollPosition)
    }

    DisposableEffect(listState) {
        onDispose {
            scrollPosition = listState.firstVisibleItemIndex
        }
    }

    LazyColumn(state = listState) {
        // items...
    }
}
```

3. Выбранные элементы (через saveable-представление):

```kotlin
@Composable
fun SelectableList(items: List<String>) {
    var selectedItemsInternal by rememberSaveable {
        mutableStateOf(listOf<String>())
    }

    val selectedItems = selectedItemsInternal.toSet()

    LazyColumn {
        items(items) { item ->
            Row(
                modifier = Modifier.clickable {
                    selectedItemsInternal = if (item in selectedItems) {
                        selectedItemsInternal - item
                    } else {
                        selectedItemsInternal + item
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

4. Состояние expanded/collapsed:

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

#### 1. Лимит размера `Bundle` (~1MB)

```kotlin
@Composable
fun LargeDataExample() {
    // Не рекомендуется: может превысить лимиты Bundle
    var largeList by rememberSaveable {
        mutableStateOf(List(10_000) { "Item $it" })
    }

    // Правильно: хранить большие данные во ViewModel/Repository/БД
    val viewModel: DataViewModel = hiltViewModel()
    val items by viewModel.items.collectAsState()
}
```

#### 2. Несохраняемые/тяжелые типы

```kotlin
@Composable
fun NonSerializableExample() {
    // Избегайте хранения тяжелых объектов напрямую в rememberSaveable,
    // даже если они Parcelable/Serializable (Bitmap, ExoPlayer и т.п.).

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
    // remember — быстрый, in-memory
    var tempState by remember { mutableStateOf(0) }

    // rememberSaveable — немного медленнее за счет сохранения/восстановления
    var savedState by rememberSaveable { mutableStateOf(0) }

    // Для больших/сложных структур используйте remember или ViewModel
}
```

### rememberSaveable с keys

```kotlin
@Composable
fun TabScreen(initialTab: Int) {
    // key = initialTab — сбросить state при изменении параметра
    var selectedTab by rememberSaveable(initialTab) {
        mutableStateOf(initialTab)
    }

    TabRow(selectedTabIndex = selectedTab) {
        // tabs...
    }
}
```

### Резюме / Best practices (RU)

- remember:
  - использовать для эфемерного UI-состояния, дорогих объектов, NavController и т.п.;
  - не переживает configuration changes и смерть процесса.

- rememberSaveable:
  - использовать для пользовательского ввода, выбора, expanded/collapsed и другого важного состояния, которое нужно восстановить после поворота экрана и т.п.;
  - может восстановиться после смерти процесса при корректной интеграции с механизмом сохранения состояния;
  - работает только с saveable-типами (`Bundle`-compatible или через Saver);
  - не применять для больших/тяжелых объектов — лучше `ViewModel`/Repository.

---

## Answer (EN)

In Jetpack Compose:
- remember keeps state only in memory for the current composition. It survives recomposition, but is lost on configuration changes and process death.
- rememberSaveable keeps state in a way that is integrated with the SaveableStateRegistry (backed by onSaveInstanceState/`Bundle` in Activities/Fragments or navigation SavedStateHandle). It survives recomposition and configuration changes, and can survive process death when the hosting component correctly saves/restores state.

### remember — In-memory state

```kotlin
@Composable
fun CounterWithRemember() {
    // Lost on configuration change (e.g., rotation)
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

Behavior:
- Survives recomposition.
- Lost on configuration changes (rotation, locale change, dark mode, etc.).
- Lost on process death.
- No serialization overhead; good for lightweight/in-memory or recreation-friendly state.

### rememberSaveable — Saveable state via SaveableStateRegistry/`Bundle`

```kotlin
@Composable
fun CounterWithRememberSaveable() {
    // Restored after configuration change if host supports SavedInstanceState
    var count by rememberSaveable { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

Behavior:
- Survives recomposition.
- Survives configuration changes.
- Can survive process death when the environment (`Activity`/`Fragment`/NavHost/etc.) correctly participates in saving and restoring instance state.
- Requires types that are supported by the underlying saving mechanism (`Bundle`-compatible by default) or a custom Saver.

### Comparison

| Aspect | remember | rememberSaveable |
|--------|----------|------------------|
| Recomposition | Survives | Survives |
| Configuration change | Lost | Restored |
| Process death | Lost | Restored (if host saves/restores state) |
| Supported types | Any | `Bundle`-compatible or via Saver |
| Performance | Faster (no serialization) | Slower (serialization/transform) |
| Size limit | No `Bundle` limit | Subject to `Bundle` limits (~1MB per transaction) |
| Use case | Ephemeral/derivable UI state | Important user-visible/restoration-critical state |

(*) Process death restore works only if the host component saves and restores instance state correctly.

### What rememberSaveable Can Store

#### Automatically supported types (by default)

```kotlin
@Composable
fun AutoSupportedTypes() {
    // These work out of the box
    var text by rememberSaveable { mutableStateOf("") }                  // String
    var count by rememberSaveable { mutableStateOf(0) }                   // Int
    var price by rememberSaveable { mutableStateOf(0.0) }                 // Double
    var isChecked by rememberSaveable { mutableStateOf(false) }           // Boolean
    var items by rememberSaveable { mutableStateOf(listOf("A", "B")) }   // List<String>
}
```

Supported (by default) include:
- Primitives: `Int`, `Long`, `Float`, `Double`, `Boolean`, `Char`, `Byte`, `Short`
- `String`
- CharSequence
- Arrays of supported primitives: IntArray, LongArray, etc.
- `ArrayList<T>` where T is a supported type
- `Parcelable`
- `Serializable`

### Custom types with `Parcelable`

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

    // State will survive configuration changes and may be restored after process death
    TextField(
        value = user.name,
        onValueChange = { user = user.copy(name = it) }
    )
}
```

### Custom types with Saver

For types that are not directly saveable, use a custom Saver:

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

### listSaver for list-based data

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
    var cartItem by rememberSaveable(stateSaver = CartItemSaver) {
        mutableStateOf(CartItem(0, 0))
    }
}
```

### rememberSaveable with `ViewModel`

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    // ViewModel survives configuration changes by default
    val query by viewModel.query.collectAsState()

    // No rememberSaveable needed for ViewModel-managed state

    // Use rememberSaveable for local UI state that should survive config changes
    var isFilterExpanded by rememberSaveable { mutableStateOf(false) }
    var selectedTab by rememberSaveable { mutableStateOf(0) }

    Column {
        SearchBar(
            query = query,
            onQueryChange = viewModel::updateQuery
        )

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

### When to use remember

Use remember for:
- Ephemeral UI state (safe to lose):

```kotlin
@Composable
fun AnimatedButton() {
    var isPressed by remember { mutableStateOf(false) }

    Button(
        onClick = { },
        modifier = Modifier.pointerInput(Unit) {
            detectTapGestures(
                onPress = { isPressed = true },
                onTap = { isPressed = false }
            )
        }
    ) {
        Text(if (isPressed) "Pressed" else "Click me")
    }
}
```

- Performance-critical or expensive objects (not appropriate for saveable state):

```kotlin
@Composable
fun ExpensiveComputationExample() {
    val expensiveObject = remember {
        ExpensiveObject() // Created once per composition lifecycle
    }

    // No rememberSaveable: too expensive or not meaningful to serialize
}
```

- Objects backed by longer-lived components (`ViewModel`, NavController, etc.):

```kotlin
@Composable
fun DataScreen(viewModel: DataViewModel) {
    val data by viewModel.data.collectAsState()

    // Local navigation/controller objects
    val navController = rememberNavController() // remember is appropriate
}
```

### When to use rememberSaveable

Use rememberSaveable for state that:
- Is user-visible/meaningful to restore.
- Should survive configuration changes (and ideally process death when supported).

1. User input (forms, search fields):

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

2. Scroll position (demonstrated as an alternative/manual approach):

```kotlin
@Composable
fun ArticleList() {
    val listState = rememberLazyListState()

    // Alternative: manually persist first visible index
    var scrollPosition by rememberSaveable { mutableStateOf(0) }

    LaunchedEffect(scrollPosition) {
        listState.scrollToItem(scrollPosition)
    }

    DisposableEffect(listState) {
        onDispose {
            scrollPosition = listState.firstVisibleItemIndex
        }
    }

    LazyColumn(state = listState) {
        // items...
    }
}
```

3. Selected items, using a saveable representation:

```kotlin
@Composable
fun SelectableList(items: List<String>) {
    // Store as List<String>, which is saveable by default
    var selectedItemsInternal by rememberSaveable {
        mutableStateOf(listOf<String>())
    }

    val selectedItems = selectedItemsInternal.toSet()

    LazyColumn {
        items(items) { item ->
            Row(
                modifier = Modifier.clickable {
                    selectedItemsInternal = if (item in selectedItems) {
                        selectedItemsInternal - item
                    } else {
                        selectedItemsInternal + item
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

4. Expanded/collapsed state of UI elements:

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

### rememberSaveable limitations

#### 1. `Bundle` size limit (~1MB)

```kotlin
@Composable
fun LargeDataExample() {
    // Avoid: may exceed Bundle limits
    var largeList by rememberSaveable {
        mutableStateOf(List(10_000) { "Item $it" })
    }

    // Prefer: store large data in ViewModel/Repository/Database instead
    val viewModel: DataViewModel = hiltViewModel()
    val items by viewModel.items.collectAsState()
}
```

#### 2. Non-saveable / heavy types

```kotlin
@Composable
fun NonSerializableExample() {
    // Avoid saving large/heavy objects directly via rememberSaveable
    // even if they implement Parcelable/Serializable (e.g., Bitmap, ExoPlayer, etc.).

    var imageUri by rememberSaveable {
        mutableStateOf<String?>(null)
    }

    val image = remember(imageUri) {
        imageUri?.let { loadBitmapFromUri(it) }
    }
}
```

### Performance

```kotlin
@Composable
fun PerformanceComparison() {
    // remember: fast, in-memory
    var tempState by remember { mutableStateOf(0) }

    // rememberSaveable: some overhead due to saving/restoring
    var savedState by rememberSaveable { mutableStateOf(0) }

    // For large or complex structures prefer remember or ViewModel
}
```

### rememberSaveable with keys

```kotlin
@Composable
fun TabScreen(initialTab: Int) {
    // Key=initialTab: reset state when parameter changes
    var selectedTab by rememberSaveable(initialTab) {
        mutableStateOf(initialTab)
    }

    TabRow(selectedTabIndex = selectedTab) {
        // tabs...
    }
}
```

### Summary / Best Practices (EN)

- remember:
  - Use for ephemeral UI state, expensive objects, and objects managed by longer-lived owners (`ViewModel`, NavController, etc.).
  - Does NOT survive configuration changes or process death.

- rememberSaveable:
  - Use for user input, selection, expanded/collapsed states, and other important UI state that should be restored across configuration changes.
  - Can restore after process death when the host participates in instance state saving.
  - Works only with saveable types (`Bundle`-compatible by default) or via custom Saver.
  - Avoid for large or heavy objects; use `ViewModel`/Repository instead.

---

## Follow-ups

- [[q-handler-looper-main-thread--android--medium]]

## References

- [Android Documentation](https://developer.android.com/docs)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]

### Related (Medium)

- [[q-what-are-the-most-important-components-of-compose--android--medium]]

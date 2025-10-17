---
id: 20251017-114333
title: "Compose Performance Optimization / Оптимизация производительности Compose"
aliases: []

# Classification
topic: android
subtopics: [jetpack-compose, performance, optimization, recomposition]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru, android/jetpack-compose, android/performance, android/optimization, android/recomposition, difficulty/hard]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [en, ru, android/jetpack-compose, android/performance, android/optimization, android/recomposition, difficulty/hard]
---
# Question (EN)
> How to optimize performance in Jetpack Compose? What causes unnecessary recomposition and how to avoid it?
# Вопрос (RU)
> Как оптимизировать производительность в Jetpack Compose? Что вызывает ненужную рекомпозицию и как её избежать?

---

## Answer (EN)

Performance optimization in Compose focuses on minimizing unnecessary recompositions.

### Causes of Recomposition

**1. State changes**

```kotlin
// BAD - Recomposes entire screen on any change
@Composable
fun Screen(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    // Entire screen recomposes when ANY field in uiState changes
    Column {
        Header(uiState.title)
        Content(uiState.content)
        Footer(uiState.footer)
    }
}

// GOOD - Split state
@Composable
fun Screen(viewModel: ViewModel) {
    val title by viewModel.title.collectAsState()
    val content by viewModel.content.collectAsState()
    val footer by viewModel.footer.collectAsState()

    // Only changed part recomposes
    Column {
        Header(title)
        Content(content)
        Footer(footer)
    }
}
```

**2. Unstable parameters**

```kotlin
// BAD - List is unstable
@Composable
fun ItemList(items: List<Item>) {  // Recomposes even if list didn't change
    LazyColumn {
        items(items) { item -> ItemCard(item) }
    }
}

// GOOD - Use @Stable or immutable collections
@Stable
data class ItemListState(val items: List<Item>)

@Composable
fun ItemList(state: ItemListState) {  // Skips recomposition if same
    LazyColumn {
        items(state.items) { item -> ItemCard(item) }
    }
}
```

### Optimization Techniques

**1. Use keys in lists**

```kotlin
// GOOD - Reuses compositions
LazyColumn {
    items(
        items = products,
        key = { it.id }  // Compose knows which items changed
    ) { product ->
        ProductCard(product)
    }
}
```

**2. derivedStateOf for computed values**

```kotlin
// BAD - Recomputes on every scroll
@Composable
fun MessageList(messages: List<Message>) {
    val listState = rememberLazyListState()
    val showButton = listState.firstVisibleItemIndex > 0  // Recomputes constantly

    LazyColumn(state = listState) {
        items(messages) { MessageItem(it) }
    }
}

// GOOD - Only recomputes when threshold crossed
@Composable
fun MessageList(messages: List<Message>) {
    val listState = rememberLazyListState()
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    LazyColumn(state = listState) {
        items(messages) { MessageItem(it) }
    }
}
```

**3. Lambda stability**

```kotlin
// BAD - New lambda on every recomposition
@Composable
fun Screen() {
    Button(onClick = { viewModel.action() }) {  // New lambda each time
        Text("Click")
    }
}

// GOOD - Remember lambda
@Composable
fun Screen() {
    val onClick = remember { { viewModel.action() } }
    Button(onClick = onClick) {
        Text("Click")
    }
}

// BETTER - Extract to separate function
@Composable
fun Screen() {
    Button(onClick = viewModel::action) {  // Stable reference
        Text("Click")
    }
}
```

**4. Mark classes as @Stable/@Immutable**

```kotlin
@Immutable  // All properties are val and immutable
data class Product(
    val id: String,
    val name: String,
    val price: Double
)

@Stable  // Properties may be var but notify on change
class ProductViewModel : ViewModel() {
    var selectedProduct by mutableStateOf<Product?>(null)
}
```

**5. Avoid recomposition propagation**

```kotlin
// BAD - Parent passes unstable state
@Composable
fun Parent() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Button(onClick = { counter++ }) { Text("$counter") }
        ExpensiveChild(counter)  // Recomposes unnecessarily
    }
}

// GOOD - Hoist state, pass only when needed
@Composable
fun Parent() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Button(onClick = { counter++ }) { Text("$counter") }
        ExpensiveChild()  // Doesn't recompose
    }
}
```

**English Summary**: Optimize Compose by: 1) Split state to minimize recomposition scope. 2) Use `derivedStateOf` for computed values. 3) Mark data classes as `@Immutable/@Stable`. 4) Use `key` in LazyColumn. 5) Remember lambdas or use method references. 6) Avoid unstable parameters. Tools: Layout Inspector, Recomposition Counter.

## Ответ (RU)

Оптимизация производительности в Compose фокусируется на минимизации ненужных рекомпозиций.

### Причины рекомпозиции

**1. Изменения состояния**

```kotlin
// ПЛОХО - Рекомпозиция всего экрана при любом изменении
@Composable
fun Screen(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    // Весь экран перекомпонуется при изменении ЛЮБОГО поля в uiState
    Column {
        Header(uiState.title)
        Content(uiState.content)
        Footer(uiState.footer)
    }
}

// ХОРОШО - Разделить состояние
@Composable
fun Screen(viewModel: ViewModel) {
    val title by viewModel.title.collectAsState()
    val content by viewModel.content.collectAsState()
    val footer by viewModel.footer.collectAsState()

    // Только измененная часть перекомпонуется
    Column {
        Header(title)
        Content(content)
        Footer(footer)
    }
}
```

**2. Нестабильные параметры**

```kotlin
// ПЛОХО - List нестабильный
@Composable
fun ItemList(items: List<Item>) {  // Перекомпонуется даже если список не изменился
    LazyColumn {
        items(items) { item -> ItemCard(item) }
    }
}

// ХОРОШО - Используйте @Stable или immutable коллекции
@Stable
data class ItemListState(val items: List<Item>)

@Composable
fun ItemList(state: ItemListState) {  // Пропускает рекомпозицию если одинаковый
    LazyColumn {
        items(state.items) { item -> ItemCard(item) }
    }
}
```

### Техники оптимизации

**1. Используйте ключи в списках**

```kotlin
// ХОРОШО - Переиспользует композиции
LazyColumn {
    items(
        items = products,
        key = { it.id }  // Compose знает какие элементы изменились
    ) { product ->
        ProductCard(product)
    }
}
```

**Почему ключи важны:**
```kotlin
// Без ключей:
// Исходно: [A, B, C]
// После вставки в 0: [D, A, B, C]
// Compose видит: позиция 0 изменилась A→D, позиция 1 изменилась B→A, и т.д.
// Результат: ВСЕ элементы перекомпонуются!

// С ключами:
// Исходно: [A(key:1), B(key:2), C(key:3)]
// После вставки: [D(key:4), A(key:1), B(key:2), C(key:3)]
// Compose видит: добавлен элемент D, элементы A,B,C не изменились
// Результат: Только новый элемент D компонуется!
```

**2. derivedStateOf для вычисляемых значений**

```kotlin
// ПЛОХО - Пересчитывает при каждом скролле
@Composable
fun MessageList(messages: List<Message>) {
    val listState = rememberLazyListState()
    val showButton = listState.firstVisibleItemIndex > 0  // Пересчитывает постоянно

    LazyColumn(state = listState) {
        items(messages) { MessageItem(it) }
    }
}

// ХОРОШО - Пересчитывает только при пересечении порога
@Composable
fun MessageList(messages: List<Message>) {
    val listState = rememberLazyListState()
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    LazyColumn(state = listState) {
        items(messages) { MessageItem(it) }
    }
}
```

**3. Стабильность лямбд**

```kotlin
// ПЛОХО - Новая лямбда при каждой рекомпозиции
@Composable
fun Screen() {
    Button(onClick = { viewModel.action() }) {  // Новая лямбда каждый раз
        Text("Нажать")
    }
}

// ХОРОШО - Запомнить лямбду
@Composable
fun Screen() {
    val onClick = remember { { viewModel.action() } }
    Button(onClick = onClick) {
        Text("Нажать")
    }
}

// ЛУЧШЕ - Ссылка на метод
@Composable
fun Screen() {
    Button(onClick = viewModel::action) {  // Стабильная ссылка
        Text("Нажать")
    }
}
```

**4. Пометить классы как @Stable/@Immutable**

```kotlin
@Immutable  // Все свойства val и неизменяемы
data class Product(
    val id: String,
    val name: String,
    val price: Double
)

@Stable  // Свойства могут быть var, но уведомляют об изменении
class ProductViewModel : ViewModel() {
    var selectedProduct by mutableStateOf<Product?>(null)
}
```

**5. Избегайте распространения рекомпозиции**

```kotlin
// ПЛОХО - Родитель передает нестабильное состояние
@Composable
fun Parent() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Button(onClick = { counter++ }) { Text("$counter") }
        ExpensiveChild(counter)  // Перекомпонуется без необходимости
    }
}

// ХОРОШО - Поднять состояние, передавать только при необходимости
@Composable
fun Parent() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Button(onClick = { counter++ }) { Text("$counter") }
        ExpensiveChild()  // Не перекомпонуется
    }
}
```

**6. Используйте remember для дорогих вычислений**

```kotlin
// ПЛОХО - Вычисляется при каждой рекомпозиции
@Composable
fun UserList(users: List<User>) {
    val sortedUsers = users.sortedBy { it.name }  // Сортируется каждый раз!

    LazyColumn {
        items(sortedUsers) { user ->
            UserRow(user)
        }
    }
}

// ХОРОШО - Кэширование с remember
@Composable
fun UserList(users: List<User>) {
    val sortedUsers = remember(users) {
        users.sortedBy { it.name }  // Сортируется только при изменении users
    }

    LazyColumn {
        items(sortedUsers) { user ->
            UserRow(user)
        }
    }
}
```

**7. Разделите большие composables**

```kotlin
// ПЛОХО - Монолитный composable
@Composable
fun Screen(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        // 100+ строк кода
        // Всё перекомпонуется при любом изменении
    }
}

// ХОРОШО - Разделить на маленькие composables
@Composable
fun Screen(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        Header(uiState.header)
        Body(uiState.body)
        Footer(uiState.footer)
    }
}
```

**8. Используйте contentType в LazyColumn**

```kotlin
@Composable
fun MixedList(items: List<ListItem>) {
    LazyColumn {
        items(
            items = items,
            key = { it.id },
            contentType = { item ->
                when (item) {
                    is TextItem -> "text"
                    is ImageItem -> "image"
                    is VideoItem -> "video"
                }
            }
        ) { item ->
            when (item) {
                is TextItem -> TextRow(item)
                is ImageItem -> ImageRow(item)
                is VideoItem -> VideoRow(item)
            }
        }
    }
}
```

### Инструменты профилирования

**Layout Inspector для отслеживания рекомпозиций:**
```
Android Studio > View > Tool Windows > Layout Inspector
Включить "Show Recomposition Counts"
```

**Recomposition Highlighter:**
```kotlin
// Для отладки
@Composable
fun RecompositionCounter() {
    val count = remember { mutableStateOf(0) }
    LaunchedEffect(Unit) {
        count.value++
    }
    Log.d("Recomposition", "Count: ${count.value}")
}
```

**Краткое содержание**: Оптимизация Compose: 1) Разделить состояние для минимизации scope рекомпозиции. 2) Использовать `derivedStateOf` для вычисляемых значений. 3) Пометить data классы как `@Immutable/@Stable`. 4) Использовать `key` в LazyColumn. 5) Запоминать лямбды или использовать ссылки на методы. 6) Избегать нестабильных параметров. 7) Использовать инструменты: Layout Inspector, Recomposition Counter.

---

## References
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)

## Related Questions

### Prerequisites (Easier)
- [[q-app-startup-optimization--performance--medium]] - Performance
- [[q-baseline-profiles-optimization--performance--medium]] - Performance
- [[q-app-size-optimization--performance--medium]] - Performance
### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Slot table internals
- [[q-compose-custom-layout--jetpack-compose--hard]] - Custom layouts

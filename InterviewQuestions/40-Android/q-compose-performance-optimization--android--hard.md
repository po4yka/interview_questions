---
id: 20251006-011
title: "Compose Performance Optimization / Оптимизация производительности Compose"
aliases: []

# Classification
topic: android
subtopics: [jetpack-compose, performance, optimization, recomposition]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, jetpack-compose, performance, optimization, recomposition, difficulty/hard]
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
**2. Нестабильные параметры**

### Техники оптимизации

**1. Используйте ключи в списках**

```kotlin
LazyColumn {
    items(
        items = products,
        key = { it.id }  // Compose знает какие элементы изменились
    ) { product ->
        ProductCard(product)
    }
}
```

**2. derivedStateOf для вычисляемых значений**

```kotlin
// ХОРОШО - Пересчитывает только при пересечении порога
val showButton by remember {
    derivedStateOf {
        listState.firstVisibleItemIndex > 0
    }
}
```

**3. Стабильность лямбд**

```kotlin
// ПЛОХО - Новая лямбда при каждой рекомпозиции
Button(onClick = { viewModel.action() })

// ХОРОШО - Запомнить лямбду
val onClick = remember { { viewModel.action() } }
Button(onClick = onClick)

// ЛУЧШЕ - Ссылка на метод
Button(onClick = viewModel::action)
```

**4. Пометить классы как @Stable/@Immutable**

```kotlin
@Immutable
data class Product(val id: String, val name: String)

@Stable
class ViewModel : ViewModel() {
    var state by mutableStateOf(State())
}
```

**Краткое содержание**: Оптимизация Compose: 1) Разделить состояние для минимизации scope рекомпозиции. 2) Использовать `derivedStateOf` для вычисляемых значений. 3) Пометить data классы как `@Immutable/@Stable`. 4) Использовать `key` в LazyColumn. 5) Запоминать лямбды или использовать ссылки на методы. 6) Избегать нестабильных параметров.

---

## References
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)

## Related Questions
- [[q-recomposition-compose--android--medium]]

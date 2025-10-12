---
id: 20251012-140500
title: "Recomposition in Compose / Рекомпозиция в Compose"
aliases: []

# Classification
topic: android
subtopics: [jetpack-compose, recomposition, state, performance, remember]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Created for vault completeness

# Workflow & relations
status: draft
moc: moc-android
related: [q-compose-performance-optimization--android--hard, q-jetpack-compose-basics--android--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [android, jetpack-compose, recomposition, state, performance, difficulty/medium]
---

# Question (EN)
> What is recomposition in Jetpack Compose? What triggers recomposition, and how does Compose decide which composables need to recompose?

# Вопрос (RU)
> Что такое рекомпозиция в Jetpack Compose? Что триггерит рекомпозицию и как Compose решает какие composable нужно перерисовать?

---

## Answer (EN)

**Recomposition** is the process where Compose re-executes composable functions when their input parameters or observed state changes. It's the core mechanism that makes Compose's declarative UI paradigm work.

### How Recomposition Works

Unlike traditional Android Views where you imperatively update UI (`textView.text = "new"`), Compose re-runs the entire composable function with new data:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Clicked $count times")  // Recomposes when count changes
    }
}
```

**What happens:**
1. User clicks button
2. `count` state changes from 0 to 1
3. Compose detects the state change
4. `Counter()` function re-executes
5. UI updates to show new count

### What Triggers Recomposition?

#### 1. State Changes (`mutableStateOf`)

```kotlin
@Composable
fun UserProfile(viewModel: ProfileViewModel) {
    val user by viewModel.user.collectAsState()  // Observes Flow

    Column {
        Text(user.name)  // Recomposes when user changes
        Text(user.email)
    }
}
```

**Triggers:**
- `mutableStateOf` changes
- `collectAsState()` emits new value from Flow
- `observeAsState()` for LiveData changes

#### 2. Parameter Changes

```kotlin
@Composable
fun Greeting(name: String) {  // Recomposes when name changes
    Text("Hello, $name!")
}

@Composable
fun Parent() {
    var name by remember { mutableStateOf("Alice") }

    Greeting(name = name)  // Pass state to child

    Button(onClick = { name = "Bob" }) {
        Text("Change Name")  // Triggers recomposition of Greeting
    }
}
```

#### 3. Scope Recomposition

```kotlin
@Composable
fun Screen() {
    var topCounter by remember { mutableStateOf(0) }
    var bottomCounter by remember { mutableStateOf(0) }

    Column {
        // This Text recomposes ONLY when topCounter changes
        Text("Top: $topCounter")

        Button(onClick = { topCounter++ }) {
            Text("Increment Top")
        }

        // This Text recomposes ONLY when bottomCounter changes
        Text("Bottom: $bottomCounter")

        Button(onClick = { bottomCounter++ }) {
            Text("Increment Bottom")
        }
    }
}
```

**Compose is smart:** Changing `topCounter` does NOT recompose the bottom section.

### Recomposition Scoping

Compose recomposes at the **narrowest scope possible** - only the composables that directly read the changed state.

#### Example: Smart Scoping

```kotlin
@Composable
fun ChatScreen(viewModel: ChatViewModel) {
    val messages by viewModel.messages.collectAsState()
    val inputText by viewModel.inputText.collectAsState()

    Column {
        // ONLY this recomposes when messages change
        MessageList(messages)

        // ONLY this recomposes when inputText changes
        MessageInput(
            text = inputText,
            onTextChange = { viewModel.updateInput(it) }
        )
    }
}
```

### Positional Memoization

Compose uses **positional memoization** - it remembers which composables were called in which order:

```kotlin
@Composable
fun ConditionalUI(showDetails: Boolean) {
    Text("Title")  // Position 0

    if (showDetails) {
        Text("Detail 1")  // Position 1 when visible
        Text("Detail 2")  // Position 2 when visible
    }

    Button(onClick = {}) {  // Position 1 or 3 depending on showDetails
        Text("Submit")
    }
}
```

**Problem:** When `showDetails` changes, the `Button` position changes, causing unnecessary recomposition.

**Solution:** Use `key()` to maintain identity:

```kotlin
@Composable
fun ConditionalUI(showDetails: Boolean) {
    Text("Title")

    if (showDetails) {
        key("details") {  // Maintain stable identity
            Text("Detail 1")
            Text("Detail 2")
        }
    }

    key("submit-button") {  // Always same identity
        Button(onClick = {}) {
            Text("Submit")
        }
    }
}
```

### Stability and Recomposition Skipping

Compose can **skip recomposition** if:
1. All parameters are **equal** to previous values
2. Parameters are **stable** types

#### Stable Types

```kotlin
// Stable: Primitives
@Composable
fun Counter(count: Int)  // Skips if count hasn't changed

// Stable: @Immutable data classes
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserCard(user: User)  // Skips if user is same instance

// Unstable: Mutable collections
@Composable
fun ItemList(items: List<Item>)  // ALWAYS recomposes (List is unstable)
```

**Why is `List` unstable?** Kotlin's `List` is actually `java.util.List`, which could be mutated elsewhere. Compose assumes it's unsafe.

#### Making Lists Stable

```kotlin
// Option 1: Use @Stable wrapper
@Stable
data class ItemsState(val items: List<Item>)

@Composable
fun ItemList(state: ItemsState)  // Skips if state instance unchanged

// Option 2: Use kotlinx.collections.immutable
import kotlinx.collections.immutable.ImmutableList

@Composable
fun ItemList(items: ImmutableList<Item>)  // Truly immutable
```

### Controlling Recomposition

#### 1. `remember {}` - Preserve Across Recompositions

```kotlin
@Composable
fun ExpensiveCalculation() {
    // BAD: Recalculates on every recomposition
    val result = expensiveComputation()

    // GOOD: Calculates only once
    val result = remember { expensiveComputation() }

    Text("Result: $result")
}
```

#### 2. `remember(key) {}` - Recalculate on Key Change

```kotlin
@Composable
fun FilteredList(items: List<Item>, query: String) {
    // Recalculates ONLY when query changes
    val filteredItems = remember(query) {
        items.filter { it.name.contains(query, ignoreCase = true) }
    }

    LazyColumn {
        items(filteredItems) { item ->
            ItemCard(item)
        }
    }
}
```

#### 3. `derivedStateOf {}` - Computed State

```kotlin
@Composable
fun ScrollToTopButton(listState: LazyListState) {
    // BAD: Recomposes on EVERY scroll pixel
    val showButton = listState.firstVisibleItemIndex > 0

    // GOOD: Recomposes only when threshold crossed
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    AnimatedVisibility(visible = showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}
```

**Why:** `listState.firstVisibleItemIndex` changes on every scroll frame, but `derivedStateOf` batches changes and only notifies when the boolean result changes.

### Recomposition and Side Effects

```kotlin
@Composable
fun BadExample() {
    var count by remember { mutableStateOf(0) }

    // BAD: Side effect in composition
    Log.d("Recomposition", "Recomposed with count = $count")

    // BAD: Modifying state during composition
    // count++  // Would cause infinite recomposition!

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

@Composable
fun GoodExample() {
    var count by remember { mutableStateOf(0) }

    // GOOD: Side effect in LaunchedEffect
    LaunchedEffect(count) {
        Log.d("Count", "Count changed to $count")
    }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**Rule:** Composables should be **idempotent** and **side-effect free**. Use effect handlers for side effects:
- `LaunchedEffect` - coroutine lifecycle tied to composition
- `DisposableEffect` - cleanup on disposal
- `SideEffect` - execute on every successful recomposition

### Advanced: Custom Remember

```kotlin
class UserRepository {
    fun loadUser(id: String): Flow<User> = TODO()
}

@Composable
fun rememberUserRepository(): UserRepository {
    val context = LocalContext.current
    return remember {
        UserRepository(context)
    }
}

@Composable
fun UserScreen(userId: String) {
    val repository = rememberUserRepository()  // Survives recomposition
    val user by repository.loadUser(userId).collectAsState(initial = null)

    user?.let {
        UserCard(it)
    }
}
```

### Real-World Example: Optimized List

```kotlin
@Composable
fun ProductList(
    products: List<Product>,
    onProductClick: (Product) -> Unit
) {
    var searchQuery by remember { mutableStateOf("") }

    // Recomputes only when query or products change
    val filteredProducts = remember(searchQuery, products) {
        if (searchQuery.isEmpty()) {
            products
        } else {
            products.filter {
                it.name.contains(searchQuery, ignoreCase = true)
            }
        }
    }

    Column {
        // Only recomposes when searchQuery changes
        SearchBar(
            query = searchQuery,
            onQueryChange = { searchQuery = it }
        )

        // Only recomposes when filteredProducts changes
        LazyColumn {
            items(
                items = filteredProducts,
                key = { it.id }  // Stable identity for reordering
            ) { product ->
                ProductCard(
                    product = product,
                    onClick = { onProductClick(product) }
                )
            }
        }
    }
}

@Composable
fun SearchBar(query: String, onQueryChange: (String) -> Unit) {
    TextField(
        value = query,
        onValueChange = onQueryChange,
        placeholder = { Text("Search products...") }
    )
}

@Composable
fun ProductCard(product: Product, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(product.name, style = MaterialTheme.typography.h6)
            Text("$${product.price}", style = MaterialTheme.typography.body1)
        }
    }
}
```

### Common Recomposition Pitfalls

#### 1. Lambda Instability

```kotlin
// BAD: New lambda on every recomposition
@Composable
fun BadButton(viewModel: ViewModel) {
    Button(onClick = { viewModel.doAction() }) {  // New lambda each time
        Text("Click")
    }
}

// GOOD: Stable callback
@Composable
fun GoodButton(viewModel: ViewModel) {
    Button(onClick = viewModel::doAction) {  // Method reference is stable
        Text("Click")
    }
}

// ALSO GOOD: Remember lambda
@Composable
fun AlsoGoodButton(viewModel: ViewModel) {
    val onClick = remember { { viewModel.doAction() } }
    Button(onClick = onClick) {
        Text("Click")
    }
}
```

#### 2. Reading State Too High

```kotlin
// BAD: Entire Column recomposes
@Composable
fun BadExample(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        Text(uiState.title)  // Reading uiState here
        ExpensiveComponent()  // Recomposes unnecessarily
        Text(uiState.subtitle)
    }
}

// GOOD: Read state as low as possible
@Composable
fun GoodExample(viewModel: ViewModel) {
    Column {
        TitleText(viewModel)  // Recomposes independently
        ExpensiveComponent()  // Never recomposes
        SubtitleText(viewModel)  // Recomposes independently
    }
}

@Composable
fun TitleText(viewModel: ViewModel) {
    val title by viewModel.title.collectAsState()  // Narrow scope
    Text(title)
}
```

### Debugging Recomposition

#### 1. Recomposition Counter

```kotlin
@Composable
fun RecompositionCounter() {
    val recompositions = remember { mutableStateOf(0) }

    SideEffect {
        recompositions.value++
    }

    Text("Recomposed ${recompositions.value} times")
}
```

#### 2. Layout Inspector

Use Android Studio's **Layout Inspector** with "Show Recomposition Counts" enabled:
- Red = many recompositions (potential issue)
- Green = few recompositions (good)

#### 3. Compose Compiler Metrics

Add to `gradle.properties`:
```properties
android.enableComposeCompilerMetrics=true
android.enableComposeCompilerReports=true
```

Generates reports showing:
- Unstable classes
- Skippable vs non-skippable composables
- Recomposition hot spots

### Best Practices

1. **State hoisting:** Lift state to lowest common ancestor
2. **Stable parameters:** Use `@Immutable` and `@Stable` annotations
3. **Narrow scope:** Read state as close to usage as possible
4. **Keys in lists:** Always use `key` parameter in `items()`
5. **Derived state:** Use `derivedStateOf` for computed values
6. **Remember expensive operations:** Cache calculations with `remember`
7. **Method references:** Prefer `viewModel::action` over `{ viewModel.action() }`

---

## Ответ (RU)

**Рекомпозиция** - это процесс, при котором Compose повторно выполняет composable функции когда меняются их входные параметры или наблюдаемое состояние.

### Как работает рекомпозиция

В отличие от традиционных View, где UI обновляется императивно (`textView.text = "new"`), Compose перезапускает всю composable функцию с новыми данными:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Нажато $count раз")  // Рекомпозиция при изменении count
    }
}
```

**Что происходит:**
1. Пользователь нажимает кнопку
2. Состояние `count` меняется с 0 на 1
3. Compose обнаруживает изменение состояния
4. Функция `Counter()` выполняется заново
5. UI обновляется с новым значением

### Что триггерит рекомпозицию?

#### 1. Изменения State (`mutableStateOf`)

```kotlin
@Composable
fun UserProfile(viewModel: ProfileViewModel) {
    val user by viewModel.user.collectAsState()  // Наблюдает за Flow

    Column {
        Text(user.name)  // Рекомпозиция при изменении user
        Text(user.email)
    }
}
```

#### 2. Изменения параметров

```kotlin
@Composable
fun Greeting(name: String) {  // Рекомпозиция при изменении name
    Text("Привет, $name!")
}

@Composable
fun Parent() {
    var name by remember { mutableStateOf("Алиса") }

    Greeting(name = name)

    Button(onClick = { name = "Боб" }) {
        Text("Изменить имя")  // Триггерит рекомпозицию Greeting
    }
}
```

### Область рекомпозиции (Recomposition Scoping)

Compose делает рекомпозицию **в максимально узкой области** - только те composable, которые напрямую читают изменённое состояние:

```kotlin
@Composable
fun ChatScreen(viewModel: ChatViewModel) {
    val messages by viewModel.messages.collectAsState()
    val inputText by viewModel.inputText.collectAsState()

    Column {
        // ТОЛЬКО это делает рекомпозицию при изменении messages
        MessageList(messages)

        // ТОЛЬКО это делает рекомпозицию при изменении inputText
        MessageInput(
            text = inputText,
            onTextChange = { viewModel.updateInput(it) }
        )
    }
}
```

### Стабильность и пропуск рекомпозиции

Compose может **пропустить рекомпозицию** если:
1. Все параметры **равны** предыдущим значениям
2. Параметры являются **стабильными** типами

#### Стабильные типы

```kotlin
// Стабильно: Примитивы
@Composable
fun Counter(count: Int)  // Пропускает если count не изменился

// Стабильно: @Immutable data классы
@Immutable
data class User(val id: String, val name: String)

@Composable
fun UserCard(user: User)  // Пропускает если user тот же экземпляр

// Нестабильно: Изменяемые коллекции
@Composable
fun ItemList(items: List<Item>)  // ВСЕГДА делает рекомпозицию (List нестабилен)
```

### Контроль рекомпозиции

#### 1. `remember {}` - Сохранить между рекомпозициями

```kotlin
@Composable
fun ExpensiveCalculation() {
    // ПЛОХО: Пересчитывает при каждой рекомпозиции
    val result = expensiveComputation()

    // ХОРОШО: Вычисляет только один раз
    val result = remember { expensiveComputation() }

    Text("Результат: $result")
}
```

#### 2. `derivedStateOf {}` - Вычисляемое состояние

```kotlin
@Composable
fun ScrollToTopButton(listState: LazyListState) {
    // ПЛОХО: Рекомпозиция на КАЖДЫЙ пиксель скролла
    val showButton = listState.firstVisibleItemIndex > 0

    // ХОРОШО: Рекомпозиция только при пересечении порога
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    AnimatedVisibility(visible = showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}
```

### Распространённые ошибки

#### 1. Нестабильность лямбд

```kotlin
// ПЛОХО: Новая лямбда при каждой рекомпозиции
@Composable
fun BadButton(viewModel: ViewModel) {
    Button(onClick = { viewModel.doAction() }) {
        Text("Клик")
    }
}

// ХОРОШО: Стабильный callback
@Composable
fun GoodButton(viewModel: ViewModel) {
    Button(onClick = viewModel::doAction) {  // Ссылка на метод стабильна
        Text("Клик")
    }
}
```

#### 2. Чтение состояния слишком высоко

```kotlin
// ПЛОХО: Вся Column делает рекомпозицию
@Composable
fun BadExample(viewModel: ViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        Text(uiState.title)
        ExpensiveComponent()  // Ненужная рекомпозиция
        Text(uiState.subtitle)
    }
}

// ХОРОШО: Читать состояние как можно ближе к использованию
@Composable
fun GoodExample(viewModel: ViewModel) {
    Column {
        TitleText(viewModel)  // Независимая рекомпозиция
        ExpensiveComponent()  // Никогда не делает рекомпозицию
        SubtitleText(viewModel)
    }
}
```

### Best Practices (Лучшие практики)

1. **State hoisting:** Поднимать состояние к ближайшему общему предку
2. **Стабильные параметры:** Использовать `@Immutable` и `@Stable`
3. **Узкая область:** Читать состояние как можно ближе к использованию
4. **Ключи в списках:** Всегда использовать параметр `key` в `items()`
5. **Derived state:** Использовать `derivedStateOf` для вычисляемых значений
6. **Remember для дорогих операций:** Кэшировать вычисления с `remember`
7. **Ссылки на методы:** Предпочитать `viewModel::action` вместо `{ viewModel.action() }`

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

## References

- [Compose Lifecycle](https://developer.android.com/jetpack/compose/lifecycle)
- [State and Jetpack Compose](https://developer.android.com/jetpack/compose/state)
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)
- [Thinking in Compose](https://developer.android.com/jetpack/compose/mental-model)

## MOC Links

- [[moc-android]]

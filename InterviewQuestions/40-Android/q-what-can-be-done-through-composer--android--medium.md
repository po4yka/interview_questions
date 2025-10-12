---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# What can be done through Composer in Jetpack Compose?

## EN (expanded)

### What is Composer?

**Composer** is an internal component of Jetpack Compose responsible for managing the composition state and rendering process. It's the engine that powers the declarative UI framework.

### Key Responsibilities

#### 1. State Tracking and Management

Composer tracks which composables depend on which state:

```kotlin
@Composable
fun StateTracking() {
    // Composer tracks this state
    var count by remember { mutableStateOf(0) }

    Column {
        // Composer knows this Text depends on count
        Text("Count: $count")

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
    // Composer will recompose only Text when count changes
}
```

#### 2. Recomposition Management

Composer determines what needs to be recomposed:

```kotlin
@Composable
fun RecompositionScope() {
    var counter1 by remember { mutableStateOf(0) }
    var counter2 by remember { mutableStateOf(0) }

    Column {
        // Only this recomposes when counter1 changes
        Text("Counter 1: $counter1")

        // Only this recomposes when counter2 changes
        Text("Counter 2: $counter2")

        // This never recomposes (no state dependencies)
        StaticHeader()

        Row {
            Button(onClick = { counter1++ }) {
                Text("Increment 1")
            }
            Button(onClick = { counter2++ }) {
                Text("Increment 2")
            }
        }
    }
}

@Composable
fun StaticHeader() {
    Text("This is static")
}
```

#### 3. Composition Tree Building

Composer builds and maintains the composition tree:

```kotlin
@Composable
fun TreeBuilding() {
    // Composer builds:
    // Column
    //   ├─ UserHeader
    //   ├─ UserContent
    //   └─ UserActions
    Column {
        UserHeader()
        UserContent()
        UserActions()
    }
}

@Composable
fun UserHeader() {
    Row {
        Avatar()
        UserName()
    }
}
```

#### 4. CompositionLocal Management

Composer handles CompositionLocal values:

```kotlin
// Define CompositionLocal
val LocalTheme = compositionLocalOf<Theme> { error("No theme provided") }

@Composable
fun ThemeProvider(theme: Theme, content: @Composable () -> Unit) {
    // Composer provides this value down the tree
    CompositionLocalProvider(LocalTheme provides theme) {
        content()
    }
}

@Composable
fun ThemedComponent() {
    // Composer retrieves the value
    val theme = LocalTheme.current
    Text(
        text = "Themed Text",
        color = theme.textColor
    )
}
```

#### 5. Side Effect Coordination

Composer manages side effects:

```kotlin
@Composable
fun SideEffects(userId: String) {
    // Composer ensures this runs at the right time
    LaunchedEffect(userId) {
        loadUserData(userId)
    }

    // Composer handles cleanup
    DisposableEffect(Unit) {
        val listener = registerListener()
        onDispose {
            unregisterListener(listener)
        }
    }

    // Composer coordinates with composition lifecycle
    SideEffect {
        updateAnalytics()
    }
}
```

#### 6. Remembering Values

Composer stores remembered values:

```kotlin
@Composable
fun RememberExample() {
    // Composer stores this across recompositions
    val state = remember { mutableStateOf(0) }

    // Composer stores computed value
    val derived = remember(state.value) {
        expensiveComputation(state.value)
    }

    // Composer manages ViewModel lifecycle
    val viewModel: MyViewModel = viewModel()

    // Composer stores coroutine scope
    val scope = rememberCoroutineScope()
}
```

### Internal Operations

#### Slot Table

Composer uses a slot table to store composition data:

```kotlin
@Composable
fun SlotTableExample() {
    // Composer stores in slot table:
    val state = remember { mutableStateOf(0) } // Slot 1
    val name = remember { "User" }              // Slot 2
    val colors = remember { listOf<Color>() }   // Slot 3

    // Composer retrieves values from slots during recomposition
    Text("${state.value} - $name")
}
```

#### Change Tracking

```kotlin
@Composable
fun ChangeTracking() {
    var text by remember { mutableStateOf("") }

    // Composer tracks reads and writes
    TextField(
        value = text,  // Read tracked
        onValueChange = {
            text = it  // Write triggers recomposition
        }
    )

    // Composer knows this depends on text
    Text("You typed: $text")
}
```

### Composer API (Internal Use)

While most developers don't interact with Composer directly, here's what it does behind the scenes:

```kotlin
// What Compose does internally (simplified)
@Composable
fun InternalComposerUse() {
    // currentComposer is implicit parameter
    // Compiler transforms:
    Text("Hello")

    // Into something like:
    // composer.startNode()
    // Text("Hello", composer, 0)
    // composer.endNode()
}
```

### Composition Process

```kotlin
@Composable
fun CompositionProcess() {
    // 1. Composer starts composition
    Column {
        // 2. Composer records this composable
        Header()

        // 3. Composer tracks state dependencies
        var count by remember { mutableStateOf(0) }
        Text("Count: $count")

        // 4. Composer will skip this on recomposition if possible
        Footer()
    }
    // 5. Composer completes composition
}
```

### Smart Recomposition

Composer enables intelligent recomposition:

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        // Recomposition scope 1
        Text("Counter: $counter")

        // Recomposition scope 2 (independent)
        ExpensiveComponent()

        // Recomposition scope 3
        Button(onClick = { counter++ }) {
            Text("Increment")
        }
    }
    // Composer only recomposes scope 1 when counter changes
}

@Composable
fun ExpensiveComponent() {
    // This won't recompose when counter changes above
    val data = remember {
        performExpensiveCalculation()
    }
    Text("Result: $data")
}
```

### Composition Keys

Composer uses keys to track identity:

```kotlin
@Composable
fun KeyedComposition() {
    val items = listOf("A", "B", "C")

    Column {
        items.forEach { item ->
            // Composer uses keys to track identity
            key(item) {
                ItemView(item)
            }
        }
    }
}

@Composable
fun LazyListKeys() {
    val items = remember { getItems() }

    LazyColumn {
        items(
            items = items,
            key = { it.id } // Composer tracks by key
        ) { item ->
            ItemView(item)
        }
    }
}
```

### CompositionContext

Composer provides composition context:

```kotlin
@Composable
fun ContextExample() {
    // Composer provides context
    val context = LocalContext.current
    val density = LocalDensity.current
    val configuration = LocalConfiguration.current

    // Use context-dependent values
    val screenWidth = with(density) {
        configuration.screenWidthDp.dp.toPx()
    }
}
```

### Performance Optimization

Composer helps with performance:

```kotlin
@Composable
fun OptimizedComposition() {
    val items = remember { mutableStateListOf<Item>() }

    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            // Composer only recomposes this item when it changes
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
    // Stable parameters = Composer can skip if unchanged
    Row {
        Text(item.name)
        Text(item.value)
    }
}
```

### Composer Lifecycle

```kotlin
@Composable
fun ComposerLifecycle() {
    // Enter composition
    DisposableEffect(Unit) {
        println("Entered composition")

        // Leave composition
        onDispose {
            println("Left composition")
        }
    }

    // Composer manages this lifecycle
}
```

### Best Practices

1. **Let Composer manage state**: Use `remember` and state holders
2. **Provide stable keys**: Help Composer track identity
3. **Minimize recomposition scope**: Keep composables focused
4. **Use derivedStateOf**: For computed values
5. **Trust the Composer**: It's optimized for performance

### What You Shouldn't Do

```kotlin
// - Don't try to manually control recomposition
@Composable
fun ManualControl() {
    var count by remember { mutableStateOf(0) }

    // This is handled automatically by Composer
    Text("Count: $count")
}

// - Don't store mutable state outside of remember
var globalState = 0 // Won't trigger recomposition

@Composable
fun WrongStateManagement() {
    Text("Count: $globalState") // Won't update
}

// - Let Composer manage state
@Composable
fun CorrectStateManagement() {
    var count by remember { mutableStateOf(0) }
    Text("Count: $count") // Will update correctly
}
```

---

## RU (original)

Что можно делать через Composer

Это внутренний компонент Compose, отвечающий за управление состоянием и рендерингом. Через него Compose отслеживает изменения в UI и обновляет только те элементы, которые изменились. Он также управляет процессом recomposition

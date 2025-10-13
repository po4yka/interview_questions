---
tags:
  - programming-languages
  - android
difficulty: medium
status: draft
---

# Из каких более важных компонентов состоит Compose?

## Answer (EN)
Jetpack Compose consists of several core components that work together to create a declarative UI framework. Understanding these components is essential for effective Compose development.

### 1. Composable Functions

The building blocks of Compose UI - functions annotated with `@Composable`.

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Hello, $name!")
}

@Composable
fun UserProfile(user: User) {
    Column {
        Text(user.name)
        Text(user.email)
        Button(onClick = { /* action */ }) {
            Text("Follow")
        }
    }
}

// Composable functions can be composed
@Composable
fun App() {
    Column {
        Greeting("World")
        UserProfile(User("John", "john@example.com"))
    }
}
```

### 2. State Management

State drives UI updates in Compose. When state changes, dependent composables recompose.

#### MutableState

```kotlin
@Composable
fun Counter() {
    // remember preserves state across recompositions
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

#### State Hoisting

```kotlin
// Stateless composable (reusable)
@Composable
fun StatelessCounter(
    count: Int,
    onIncrement: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text("Count: $count")
        Button(onClick = onIncrement) {
            Text("Increment")
        }
    }
}

// Stateful parent manages state
@Composable
fun StatefulCounter() {
    var count by remember { mutableStateOf(0) }

    StatelessCounter(
        count = count,
        onIncrement = { count++ }
    )
}
```

#### ViewModel Integration

```kotlin
class CounterViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }
}

@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    val count by viewModel.count.collectAsState()

    Column {
        Text("Count: $count")
        Button(onClick = { viewModel.increment() }) {
            Text("Increment")
        }
    }
}
```

### 3. Modifiers

Modify appearance, behavior, and layout of composables.

```kotlin
@Composable
fun ModifierExamples() {
    // Size and padding
    Text(
        text = "Hello",
        modifier = Modifier
            .size(200.dp, 100.dp)
            .padding(16.dp)
            .background(Color.Blue)
    )

    // Click handling
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(100.dp)
            .clickable { /* handle click */ }
            .background(Color.Gray)
    )

    // Scrolling
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        repeat(50) {
            Text("Item $it")
        }
    }

    // Custom modifier chain
    val cardModifier = Modifier
        .fillMaxWidth()
        .padding(16.dp)
        .shadow(4.dp, RoundedCornerShape(8.dp))
        .background(Color.White, RoundedCornerShape(8.dp))
        .padding(16.dp)

    Text("Card", modifier = cardModifier)
}
```

### 4. Layouts

Arrange composables on screen.

#### Column - Vertical Layout

```kotlin
@Composable
fun VerticalLayout() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Top")
        Text("Middle")
        Text("Bottom")
    }
}
```

#### Row - Horizontal Layout

```kotlin
@Composable
fun HorizontalLayout() {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text("Left")
        Text("Center")
        Text("Right")
    }
}
```

#### Box - Stack Layout

```kotlin
@Composable
fun StackLayout() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Background
        Image(
            painter = painterResource(R.drawable.bg),
            contentDescription = null,
            modifier = Modifier.fillMaxSize()
        )

        // Overlay
        Text(
            text = "Overlay",
            modifier = Modifier.align(Alignment.Center)
        )

        // FAB
        FloatingActionButton(
            onClick = { },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp)
        ) {
            Icon(Icons.Default.Add, null)
        }
    }
}
```

#### LazyColumn/LazyRow - Efficient Lists

```kotlin
@Composable
fun EfficientList(items: List<Item>) {
    LazyColumn {
        items(items) { item ->
            ItemRow(item)
        }

        // Or with index
        itemsIndexed(items) { index, item ->
            ItemRow(item, index)
        }
    }
}

@Composable
fun HorizontalList(items: List<Item>) {
    LazyRow {
        items(items) { item ->
            ItemCard(item)
        }
    }
}
```

### 5. Recomposition

The mechanism that updates UI when state changes.

```kotlin
@Composable
fun RecompositionExample() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Recomposes when count changes
        Text("Count: $count")

        // Never recomposes (no state dependency)
        Text("Static text")

        Button(onClick = { count++ }) {
            // Recomposes when count changes if we display it
            Text("Clicked $count times")
        }
    }
}

// Optimizing recomposition
@Composable
fun OptimizedRecomposition() {
    var text by remember { mutableStateOf("") }

    Column {
        // This recomposes on every text change
        Text("Length: ${text.length}")

        // Use derivedStateOf to only recompose when derived value changes
        val wordCount by remember {
            derivedStateOf { text.split(" ").count { it.isNotBlank() } }
        }
        Text("Words: $wordCount")

        TextField(
            value = text,
            onValueChange = { text = it }
        )
    }
}
```

### 6. Effect Handlers

Handle side effects and lifecycle.

```kotlin
@Composable
fun EffectHandlers(userId: String) {

    // Run suspending code
    LaunchedEffect(userId) {
        val user = loadUser(userId)
        // Update UI
    }

    // Cleanup when composable leaves
    DisposableEffect(userId) {
        val listener = UserListener()
        userManager.addListener(listener)

        onDispose {
            userManager.removeListener(listener)
        }
    }

    // Run after every successful recomposition
    SideEffect {
        analytics.logView("UserScreen")
    }

    // Produce state from non-compose sources
    val user by produceState<User?>(initialValue = null, userId) {
        value = loadUser(userId)
    }

    // Manual coroutine scope
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            // Async work
        }
    }) {
        Text("Load")
    }
}
```

### 7. Material Components

Pre-built UI components following Material Design.

```kotlin
@Composable
fun MaterialComponents() {
    Column {
        // Button
        Button(onClick = { }) {
            Text("Click Me")
        }

        // Text field
        var text by remember { mutableStateOf("") }
        TextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Enter text") }
        )

        // Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            elevation = 4.dp
        ) {
            Text("Card content", modifier = Modifier.padding(16.dp))
        }

        // Scaffold with TopBar
        Scaffold(
            topBar = {
                TopAppBar(title = { Text("My App") })
            }
        ) { paddingValues ->
            // Content
            Text(
                "Content",
                modifier = Modifier.padding(paddingValues)
            )
        }
    }
}
```

### 8. Theme System

Centralized styling and theming.

```kotlin
// Define theme
private val LightColors = lightColorScheme(
    primary = Purple500,
    secondary = Teal200,
    background = Color.White
)

private val DarkColors = darkColorScheme(
    primary = Purple200,
    secondary = Teal200,
    background = Color(0xFF121212)
)

@Composable
fun MyAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = Typography,
        shapes = Shapes,
        content = content
    )
}

// Usage
@Composable
fun App() {
    MyAppTheme {
        // All composables inherit theme
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            MainScreen()
        }
    }
}

// Access theme values
@Composable
fun ThemedText() {
    Text(
        text = "Themed",
        color = MaterialTheme.colorScheme.primary,
        style = MaterialTheme.typography.headlineMedium
    )
}
```

### 9. Navigation

Navigate between screens.

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToDetails = { id ->
                    navController.navigate("details/$id")
                }
            )
        }

        composable(
            route = "details/{id}",
            arguments = listOf(
                navArgument("id") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getInt("id") ?: 0
            DetailsScreen(
                id = id,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
```

### 10. Animation

Built-in animation support.

```kotlin
@Composable
fun Animations() {
    var expanded by remember { mutableStateOf(false) }

    // Animate value
    val size by animateDpAsState(
        targetValue = if (expanded) 200.dp else 100.dp
    )

    // Animated content size
    Column(
        modifier = Modifier
            .size(size)
            .animateContentSize()
            .background(Color.Blue)
            .clickable { expanded = !expanded }
    )

    // Animated visibility
    AnimatedVisibility(visible = expanded) {
        Text("I'm visible!")
    }

    // Crossfade
    Crossfade(targetState = expanded) { isExpanded ->
        if (isExpanded) {
            Text("Expanded")
        } else {
            Text("Collapsed")
        }
    }
}
```

### Component Hierarchy

```
Compose Runtime
     Composable Functions (@Composable)
     State Management (remember, mutableStateOf)
        State Hoisting
        ViewModel Integration
        State Flow/LiveData
     Modifiers (size, padding, click, etc.)
     Layouts
        Column, Row, Box
        LazyColumn, LazyRow
        Custom Layouts
     Recomposition Engine
     Effect Handlers
        LaunchedEffect
        DisposableEffect
        SideEffect
     Material Components
        Button, Text, Card
        TextField, Checkbox
        Scaffold, TopAppBar
     Theme System
        Colors
        Typography
        Shapes
     Navigation
     Animations
```

### Summary

The most important Compose components:

1. **Composable functions** - UI building blocks
2. **State** - Drives UI updates via recomposition
3. **Modifiers** - Customize appearance and behavior
4. **Layouts** - Arrange UI elements (Column, Row, Box, LazyColumn)
5. **Recomposition** - Smart UI update mechanism
6. **Effect handlers** - Manage side effects and lifecycle
7. **Material components** - Pre-built UI widgets
8. **Theme system** - Centralized styling
9. **Navigation** - Screen transitions
10. **Animations** - Built-in animation support

---

# Из каких более важных компонентов состоит Compose

## Ответ (RU)
Compose состоит из следующих более важных компонентов: Composable функции, которые описывают UI; State управляет состоянием компонентов; Modifiers применяются для настройки внешнего вида и поведения; Layouts определяют структуру расположения элементов на экране и Recomposition механизм обновления интерфейса при изменении состояния

---

## Related Questions

### Related (Medium)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Compose
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose
- [[q-accessibility-compose--accessibility--medium]] - Compose
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Compose

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose
- [[q-compose-performance-optimization--android--hard]] - Compose

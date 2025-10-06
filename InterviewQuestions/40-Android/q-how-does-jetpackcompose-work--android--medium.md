---
topic: android
tags:
  - jetpack compose
  - ui framework
  - android
  - ui
  - jetpack-compose
difficulty: medium
---

# How does jetpackCompose work?

## Question (RU)

Как работает jetpackCompose?

## Answer

Jetpack Compose is Google's modern declarative UI toolkit for building native Android interfaces. Instead of XML layouts and imperative View manipulation, Compose uses composable functions to describe the UI.

### Core Principles

1. **Declarative UI** - Describe what the UI should look like, not how to build it
2. **Reactive** - UI automatically updates when data changes
3. **Component-based** - Build UIs from small, reusable functions
4. **Kotlin-first** - Built for Kotlin with coroutines and Flow support

### Basic Composable Functions

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Hello, $name!")
}

// Usage
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            Greeting("World")
        }
    }
}
```

### How Composition Works

Compose builds a tree of composable functions called the **Composition**.

```kotlin
@Composable
fun MyApp() {
    // This creates a composition tree
    Column {
        Text("Title")
        Row {
            Button(onClick = {}) { Text("Click") }
            Button(onClick = {}) { Text("Cancel") }
        }
    }
}
```

Internally, Compose creates a **slot table** that tracks:
- Which composables are active
- Their position in the tree
- Their state and parameters

### Recomposition - The Heart of Compose

When data changes, Compose intelligently recomposes only affected parts.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        // This Text recomposes when count changes
        Text("Count: $count")

        Button(onClick = { count++ }) {
            // This never recomposes (static)
            Text("Increment")
        }
    }
}
```

**Recomposition process:**
1. State changes (count++)
2. Compose marks dependent composables as invalid
3. Only invalid composables re-execute
4. UI updates with new values

### State Management

State is the data that can change over time. Compose observes state and recomposes when it changes.

```kotlin
@Composable
fun LoginScreen() {
    // remember preserves state across recompositions
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    Column {
        TextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("Username") }
        )

        TextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") }
        )

        Button(
            onClick = { /* login */ },
            enabled = username.isNotEmpty() && password.isNotEmpty()
        ) {
            Text("Login")
        }
    }
}
```

### State Hoisting

Move state up to make components reusable and testable.

```kotlin
// Stateless composable (reusable)
@Composable
fun Counter(
    count: Int,
    onIncrement: () -> Unit
) {
    Column {
        Text("Count: $count")
        Button(onClick = onIncrement) {
            Text("Increment")
        }
    }
}

// Stateful parent
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }

    Counter(
        count = count,
        onIncrement = { count++ }
    )
}
```

### Lifecycle of Composables

Composables follow a lifecycle: **Enter → Recompose → Leave**

```kotlin
@Composable
fun LifecycleExample() {
    val scope = rememberCoroutineScope()

    // Runs when composable enters composition
    LaunchedEffect(Unit) {
        println("Entered composition")
    }

    // Runs when composable leaves composition
    DisposableEffect(Unit) {
        println("In composition")
        onDispose {
            println("Left composition")
        }
    }

    // Runs after every successful recomposition
    SideEffect {
        println("Recomposed")
    }
}
```

### Effect Handlers

Special composables for side effects.

```kotlin
@Composable
fun EffectsExample(userId: String) {

    // LaunchedEffect: Run suspending functions
    LaunchedEffect(userId) {
        val user = loadUser(userId)
        // Update UI
    }

    // SideEffect: Non-suspending side effects
    SideEffect {
        analytics.logScreenView("UserScreen")
    }

    // DisposableEffect: Cleanup when effect leaves
    DisposableEffect(Unit) {
        val listener = LocationListener()
        locationManager.addListener(listener)

        onDispose {
            locationManager.removeListener(listener)
        }
    }

    // rememberCoroutineScope: Manual coroutine launching
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            // Async operation
        }
    }) {
        Text("Load")
    }
}
```

### Modifiers - Styling and Behavior

Modifiers customize composable appearance and behavior.

```kotlin
@Composable
fun ModifierExample() {
    Text(
        text = "Hello",
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .background(Color.Blue)
            .clickable { /* handle click */ }
    )
}

// Order matters!
Box(
    modifier = Modifier
        .padding(16.dp)      // Padding first
        .background(Color.Blue) // Then background
) {
    // Background includes padding
}

Box(
    modifier = Modifier
        .background(Color.Blue) // Background first
        .padding(16.dp)      // Then padding
) {
    // Padding is outside background
}
```

### Layouts in Compose

Compose provides basic layout composables.

```kotlin
@Composable
fun LayoutsExample() {
    // Vertical arrangement
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Item 1")
        Text("Item 2")
    }

    // Horizontal arrangement
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text("Left")
        Text("Right")
    }

    // Stacking (like FrameLayout)
    Box(modifier = Modifier.fillMaxSize()) {
        Text("Background", modifier = Modifier.align(Alignment.Center))
        Text("Overlay", modifier = Modifier.align(Alignment.TopEnd))
    }

    // Grid
    LazyVerticalGrid(columns = GridCells.Fixed(2)) {
        items(100) { index ->
            Text("Item $index")
        }
    }
}
```

### Performance Optimization

Compose is optimized for performance, but you can help:

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    // Use LazyColumn for large lists (like RecyclerView)
    LazyColumn {
        items(items) { item ->
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
    // derivedStateOf: Only recompute when dependencies change
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }

    // remember: Cache expensive objects
    val expensiveObject = remember(item.id) {
        createExpensiveObject(item)
    }

    Row {
        Text(item.name)
        if (isExpensive) {
            Icon(Icons.Default.Star, null)
        }
    }
}
```

### Integration with Views

Compose can interop with existing View system.

```kotlin
// Compose in View
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_main)

        findViewById<ComposeView>(R.id.composeView).setContent {
            MyComposable()
        }
    }
}

// View in Compose
@Composable
fun ViewInCompose() {
    AndroidView(
        factory = { context ->
            RecyclerView(context).apply {
                // Configure RecyclerView
            }
        }
    )
}
```

### Navigation in Compose

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigateToDetails = { id ->
                    navController.navigate("details/$id")
                }
            )
        }

        composable("details/{id}") { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id")
            DetailsScreen(id = id)
        }
    }
}
```

### Architecture with Compose

```kotlin
// ViewModel
class HomeViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Success(data)
        }
    }
}

// UI
@Composable
fun HomeScreen(viewModel: HomeViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    when (uiState) {
        is UiState.Loading -> LoadingScreen()
        is UiState.Success -> ContentScreen((uiState as UiState.Success).data)
        is UiState.Error -> ErrorScreen()
    }
}
```

### How Compose Actually Works (Under the Hood)

1. **Composition**: Build UI tree from @Composable functions
2. **Layout**: Measure and position elements
3. **Drawing**: Render pixels to screen

```kotlin
// Simplified internal flow
fun composable() {
    // 1. Composition phase
    val tree = buildCompositionTree()

    // 2. Layout phase
    tree.measure(constraints)
    tree.layout(position)

    // 3. Drawing phase
    tree.draw(canvas)
}
```

**Slot Table**: Compose uses a gap buffer (slot table) to efficiently track:
- Composable positions
- State objects
- Remember values
- Group keys for recomposition

### Key Differences from View System

| View System | Jetpack Compose |
|-------------|-----------------|
| Imperative (how) | Declarative (what) |
| XML + Code | Pure Kotlin |
| findViewById | Direct access |
| Manual updates | Automatic recomposition |
| Complex lifecycle | Simple lifecycle |
| RecyclerView needed | LazyColumn built-in |

### Summary

Jetpack Compose works by:
1. **Declaring UI** with @Composable functions
2. **Building composition tree** from these functions
3. **Observing state** changes automatically
4. **Recomposing** only affected parts when state changes
5. **Measuring, layouting, and drawing** efficiently

The magic is in the **smart recomposition** - Compose only re-executes functions that depend on changed state, making it highly performant.

## Answer (RU)

Jetpack Compose – это декларативный UI-фреймворк от Google для создания интерфейсов в Android. Вместо традиционных XML + View в Compose используется функции-компоненты, которые описывают UI. Главные принципы работы Jetpack Compose: декларативный подход – UI создаётся через функции, без XML. Реактивность – UI автоматически обновляется, если данные изменились. Компонентный подход – UI состоит из маленьких, переиспользуемых функций. Composable-функции (@Composable) – основной строительный блок Compose.

---
id: 20251016-163745
title: "How Jetpack Compose Works / Как работает Jetpack Compose"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-custom-viewgroup-layout--custom-views--hard, q-android-manifest-file--android--easy, q-cicd-multi-module--devops--medium]
created: 2025-10-15
tags: [languages, android, difficulty/medium]
---
# Как работает jetpackCompose?

## Answer (EN)
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

---

# Как работает jetpackCompose?

## Ответ (RU)

Jetpack Compose – это современный декларативный UI-фреймворк от Google для создания нативных Android интерфейсов. Вместо традиционных XML-макетов и императивных манипуляций View, Compose использует composable-функции для описания UI.

### Основные принципы

1. **Декларативный UI** - Описываешь, как UI должен выглядеть, а не как его строить
2. **Реактивность** - UI автоматически обновляется при изменении данных
3. **Компонентный подход** - UI строится из маленьких переиспользуемых функций
4. **Kotlin-first** - Встроенная поддержка корутин и Flow

### Базовые Composable-функции

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Привет, $name!")
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            Greeting("Мир")
        }
    }
}
```

### Как работает композиция

Compose строит дерево composable-функций, называемое **Composition**. Внутри Compose создает **slot table**, которая отслеживает активные composables, их позицию в дереве, состояние и параметры.

### Рекомпозиция - сердце Compose

Когда данные изменяются, Compose интеллектуально перекомпонует только затронутые части:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Счет: $count")  // Перекомпонуется при изменении count
        Button(onClick = { count++ }) {
            Text("Увеличить")  // Никогда не перекомпонуется (статичный)
        }
    }
}
```

**Процесс рекомпозиции:**
1. Изменение состояния (count++)
2. Compose помечает зависимые composables как невалидные
3. Только невалидные composables выполняются заново
4. UI обновляется с новыми значениями

### Управление состоянием

Состояние - это данные, которые могут изменяться со временем. Compose наблюдает за состоянием и перекомпонуется при изменениях.

```kotlin
@Composable
fun LoginScreen() {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    Column {
        TextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("Имя пользователя") }
        )

        TextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Пароль") }
        )

        Button(
            onClick = { /* login */ },
            enabled = username.isNotEmpty() && password.isNotEmpty()
        ) {
            Text("Войти")
        }
    }
}
```

### Жизненный цикл Composables

Composables следуют жизненному циклу: **Вход → Рекомпозиция → Выход**

```kotlin
@Composable
fun LifecycleExample() {
    LaunchedEffect(Unit) {
        println("Вошел в композицию")
    }

    DisposableEffect(Unit) {
        println("В композиции")
        onDispose {
            println("Вышел из композиции")
        }
    }

    SideEffect {
        println("Перекомпонован")
    }
}
```

### Модификаторы - стилизация и поведение

```kotlin
@Composable
fun ModifierExample() {
    Text(
        text = "Привет",
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .background(Color.Blue)
            .clickable { /* обработка клика */ }
    )
}
```

### Оптимизация производительности

Compose оптимизирован по умолчанию, но можно помочь:

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    LazyColumn {
        items(items, key = { it.id }) { item ->
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }

    Row {
        Text(item.name)
        if (isExpensive) {
            Icon(Icons.Default.Star, null)
        }
    }
}
```

### Ключевые отличия от View System

| View System | Jetpack Compose |
|-------------|-----------------|
| Императивный (как) | Декларативный (что) |
| XML + Код | Чистый Kotlin |
| findViewById | Прямой доступ |
| Ручные обновления | Автоматическая рекомпозиция |
| Сложный жизненный цикл | Простой жизненный цикл |
| Нужен RecyclerView | Встроенный LazyColumn |

### Как Compose работает под капотом

1. **Композиция**: Строит UI дерево из @Composable функций
2. **Layout**: Измеряет и позиционирует элементы
3. **Рисование**: Рендерит пиксели на экран

**Slot Table**: Compose использует gap buffer для эффективного отслеживания позиций composables, объектов состояния, запоминаемых значений и групповых ключей для рекомпозиции.

### Резюме

Jetpack Compose работает путем:
1. **Объявления UI** с @Composable функциями
2. **Построения дерева композиции** из этих функций
3. **Автоматического наблюдения** за изменениями состояния
4. **Рекомпозиции** только затронутых частей при изменении состояния
5. **Эффективного измерения, позиционирования и рисования**

Магия в **умной рекомпозиции** - Compose повторно выполняет только те функции, которые зависят от измененного состояния, обеспечивая высокую производительность.

---

## Related Questions

### Related (Medium)
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose, Jetpack
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Compose, Jetpack
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose, Jetpack
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Compose, Jetpack
- [[q-jetpack-compose-basics--android--medium]] - Compose, Jetpack

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Compose, Jetpack

---
id: "20251015082237248"
title: "How Does Jetpackcompose Work / Как работает Jetpack Compose"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - jetpack compose
  - ui framework
  - android
  - ui
  - jetpack-compose
---
# How does jetpackCompose work?

# Вопрос (RU)

Как работает jetpackCompose?

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

## Ответ (RU)

**Jetpack Compose** - это современный декларативный UI-фреймворк от Google для создания нативных интерфейсов Android. Вместо традиционных XML-layout и императивного манипулирования View, Compose использует composable функции для описания UI.

### Основные принципы

**1. Декларативный UI**
Описываете что должно быть, а не как это построить.

**2. Реактивность**
UI автоматически обновляется при изменении данных.

**3. Компонентный подход**
UI строится из небольших, переиспользуемых функций.

**4. Kotlin-first**
Полная интеграция с Kotlin, coroutines и Flow.

### Основные компоненты

**Composable функции**

Базовые строительные блоки UI, помеченные аннотацией `@Composable`:

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Привет, $name!")
}

@Composable
fun UserProfile(user: User) {
    Column {
        Text(user.name)
        Text(user.email)
        Button(onClick = { /* действие */ }) {
            Text("Подписаться")
        }
    }
}
```

### Как работает композиция

Compose создаёт дерево composable функций, называемое **Composition**.

```kotlin
@Composable
fun MyApp() {
    // Создаётся дерево композиции
    Column {
        Text("Заголовок")
        Row {
            Button(onClick = {}) { Text("Нажать") }
            Button(onClick = {}) { Text("Отмена") }
        }
    }
}
```

Внутри Compose создаёт **slot table**, которая отслеживает:
- Какие composable активны
- Их позицию в дереве
- Их состояние и параметры

### Recomposition - сердце Compose

Когда данные меняются, Compose интеллектуально перекомпонует только затронутые части:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Этот Text перекомпонуется при изменении count
        Text("Счёт: $count")

        Button(onClick = { count++ }) {
            // Это никогда не перекомпонуется (статично)
            Text("Увеличить")
        }
    }
}
```

**Процесс перекомпозиции:**
1. Изменение состояния (count++)
2. Compose помечает зависимые composable как невалидные
3. Выполняются только невалидные composable
4. UI обновляется новыми значениями

### Управление состоянием

Состояние - это данные, которые могут меняться со временем. Compose наблюдает за состоянием и перекомпонуется при изменениях:

```kotlin
@Composable
fun LoginScreen() {
    // remember сохраняет состояние при перекомпозициях
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
            onClick = { /* войти */ },
            enabled = username.isNotEmpty() && password.isNotEmpty()
        ) {
            Text("Войти")
        }
    }
}
```

### State Hoisting (поднятие состояния)

Перемещайте состояние вверх для создания переиспользуемых компонентов:

```kotlin
// Stateless composable (переиспользуемый)
@Composable
fun Counter(
    count: Int,
    onIncrement: () -> Unit
) {
    Column {
        Text("Счёт: $count")
        Button(onClick = onIncrement) {
            Text("Увеличить")
        }
    }
}

// Stateful родитель
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }

    Counter(
        count = count,
        onIncrement = { count++ }
    )
}
```

### Жизненный цикл Composable

Composable проходят через lifecycle: **Enter → Recompose → Leave**

```kotlin
@Composable
fun LifecycleExample() {
    val scope = rememberCoroutineScope()

    // Выполняется при входе в композицию
    LaunchedEffect(Unit) {
        println("Вошли в композицию")
    }

    // Выполняется при выходе из композиции
    DisposableEffect(Unit) {
        println("В композиции")
        onDispose {
            println("Покинули композицию")
        }
    }

    // Выполняется после каждой успешной перекомпозиции
    SideEffect {
        println("Перекомпоновано")
    }
}
```

### Effect handlers

Специальные composable для побочных эффектов:

```kotlin
@Composable
fun EffectsExample(userId: String) {

    // LaunchedEffect: Запуск suspend функций
    LaunchedEffect(userId) {
        val user = loadUser(userId)
        // Обновить UI
    }

    // SideEffect: Не-suspend побочные эффекты
    SideEffect {
        analytics.logScreenView("UserScreen")
    }

    // DisposableEffect: Очистка при выходе
    DisposableEffect(Unit) {
        val listener = LocationListener()
        locationManager.addListener(listener)

        onDispose {
            locationManager.removeListener(listener)
        }
    }

    // rememberCoroutineScope: Ручной запуск корутин
    val scope = rememberCoroutineScope()
    Button(onClick = {
        scope.launch {
            // Асинхронная операция
        }
    }) {
        Text("Загрузить")
    }
}
```

### Modifiers - стилизация и поведение

Modifiers настраивают внешний вид и поведение composable:

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

// Порядок важен!
Box(
    modifier = Modifier
        .padding(16.dp)         // Сначала padding
        .background(Color.Blue) // Затем background
) {
    // Background включает padding
}

Box(
    modifier = Modifier
        .background(Color.Blue) // Сначала background
        .padding(16.dp)         // Затем padding
) {
    // Padding находится снаружи background
}
```

### Layouts в Compose

Compose предоставляет базовые layout composable:

```kotlin
@Composable
fun LayoutsExample() {
    // Вертикальное расположение
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Элемент 1")
        Text("Элемент 2")
    }

    // Горизонтальное расположение
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text("Слева")
        Text("Справа")
    }

    // Стекирование (как FrameLayout)
    Box(modifier = Modifier.fillMaxSize()) {
        Text("Фон", modifier = Modifier.align(Alignment.Center))
        Text("Наложение", modifier = Modifier.align(Alignment.TopEnd))
    }

    // Сетка
    LazyVerticalGrid(columns = GridCells.Fixed(2)) {
        items(100) { index ->
            Text("Элемент $index")
        }
    }
}
```

### Оптимизация производительности

Compose оптимизирован, но можно помочь:

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    // Используйте LazyColumn для больших списков (как RecyclerView)
    LazyColumn {
        items(items) { item ->
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
    // derivedStateOf: Пересчитывать только при изменении зависимостей
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }

    // remember: Кэшировать дорогие объекты
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

### Интеграция с View системой

Compose может взаимодействовать с существующей View системой:

```kotlin
// Compose в View
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_main)

        findViewById<ComposeView>(R.id.composeView).setContent {
            MyComposable()
        }
    }
}

// View в Compose
@Composable
fun ViewInCompose() {
    AndroidView(
        factory = { context ->
            RecyclerView(context).apply {
                // Настройка RecyclerView
            }
        }
    )
}
```

### Навигация в Compose

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

### Архитектура с Compose

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

### Как работает Compose внутри

1. **Composition**: Построение UI дерева из @Composable функций
2. **Layout**: Измерение и позиционирование элементов
3. **Drawing**: Отрисовка пикселей на экран

```kotlin
// Упрощённый внутренний flow
fun composable() {
    // 1. Фаза композиции
    val tree = buildCompositionTree()

    // 2. Фаза layout
    tree.measure(constraints)
    tree.layout(position)

    // 3. Фаза отрисовки
    tree.draw(canvas)
}
```

**Slot Table**: Compose использует gap buffer (slot table) для эффективного отслеживания:
- Позиций composable
- Объектов состояния
- Значений remember
- Группировочных ключей для перекомпозиции

### Ключевые отличия от View системы

| View система | Jetpack Compose |
|--------------|-----------------|
| Императивная (как) | Декларативная (что) |
| XML + Код | Чистый Kotlin |
| findViewById | Прямой доступ |
| Ручные обновления | Автоматическая перекомпозиция |
| Сложный lifecycle | Простой lifecycle |
| RecyclerView нужен | LazyColumn встроен |

### Резюме

Jetpack Compose работает через:
1. **Объявление UI** с @Composable функциями
2. **Построение composition tree** из этих функций
3. **Автоматическое наблюдение** за изменениями состояния
4. **Перекомпозицию** только затронутых частей при изменении состояния
5. **Эффективное измерение, layout и отрисовку**

Магия в **умной перекомпозиции** - Compose выполняет повторно только те функции, которые зависят от изменённого состояния, делая его высокопроизводительным.

---

## Related Questions

### Related (Medium)
- [[q-how-does-the-main-thread-work--android--medium]] - how does the main
- [[q-how-does-jetpack-compose-work--android--medium]] - how does jetpack compose
- [[q-how-does-activity-lifecycle-work--android--medium]] - how does activity lifecycle
### Related (Medium)
- [[q-how-does-the-main-thread-work--android--medium]] - how does the main
- [[q-how-does-jetpack-compose-work--android--medium]] - how does jetpack compose
- [[q-how-does-activity-lifecycle-work--android--medium]] - how does activity lifecycle
### Related (Medium)
- [[q-how-does-the-main-thread-work--android--medium]] - how does the main
- [[q-how-does-jetpack-compose-work--android--medium]] - how does jetpack compose
- [[q-how-does-activity-lifecycle-work--android--medium]] - how does activity lifecycle

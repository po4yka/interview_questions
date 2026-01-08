---\
id: "20251025-140100"
title: "Jetpack Compose / Jetpack Compose"
aliases: ["Compose", "Declarative UI", "Jetpack Compose UI", "Jetpack Compose", "Декларативный UI", "Композ"]
summary: "Modern declarative UI toolkit for building native Android interfaces"
topic: "android"
subtopics: ["declarative-ui", "jetpack-compose", "ui"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: ["c-viewmodel", "c-compose-state", "c-compose-recomposition", "c-lifecycle", "c-navigation"]
created: "2025-10-25"
updated: "2025-10-25"
tags: [android, composables, concept, declarative-ui, difficulty/medium, android/ui-compose, recomposition, ui]
---\

# Jetpack Compose / Jetpack Compose

## Summary (EN)

Jetpack Compose is Android's modern, declarative UI toolkit that simplifies and accelerates UI development. Unlike the traditional `View`-based system, Compose allows developers to describe what the UI should look like based on the current state, and the framework handles UI updates automatically. It uses Kotlin language features, composable functions, and a reactive programming model to create dynamic, responsive interfaces with less boilerplate code.

## Краткое Описание (RU)

Jetpack Compose - это современный декларативный UI-инструментарий Android, который упрощает и ускоряет разработку пользовательского интерфейса. В отличие от традиционной системы на основе `View`, Compose позволяет разработчикам описывать, как должен выглядеть UI на основе текущего состояния, а фреймворк автоматически обрабатывает обновления UI. Использует возможности языка Kotlin, компонуемые функции и реактивную модель программирования для создания динамичных, отзывчивых интерфейсов с меньшим количеством шаблонного кода.

## Key Points (EN)

- **Declarative Paradigm**: Describe UI as a function of state, not imperative updates
- **Composable Functions**: UI components are Kotlin functions annotated with `@Composable`
- **Recomposition**: Automatic UI updates when state changes
- **State Management**: Built-in state primitives (`remember`, `mutableStateOf`, `derivedStateOf`)
- **Unidirectional Data `Flow`**: State flows down, events flow up
- **Kotlin-first**: Leverages Kotlin features (lambdas, default parameters, DSL)
- **Interoperability**: Works with existing `View`-based code (AndroidView, ComposeView)
- **Material Design 3**: Built-in Material Design components
- **Performance**: Optimized for minimal recompositions, skip optimizations
- **Tooling**: Live preview, layout inspector, semantic tree debugging

## Ключевые Моменты (RU)

- **Декларативная парадигма**: Описание UI как функции состояния, а не императивных обновлений
- **Компонуемые функции**: UI компоненты - это функции Kotlin с аннотацией `@Composable`
- **Рекомпозиция**: Автоматические обновления UI при изменении состояния
- **Управление состоянием**: Встроенные примитивы состояния (`remember`, `mutableStateOf`, `derivedStateOf`)
- **Однонаправленный поток данных**: Состояние течёт вниз, события вверх
- **Kotlin-first**: Использует возможности Kotlin (лямбды, параметры по умолчанию, DSL)
- **Совместимость**: Работает с существующим `View`-кодом (AndroidView, ComposeView)
- **Material Design 3**: Встроенные компоненты Material Design
- **Производительность**: Оптимизация для минимальных рекомпозиций, пропуск оптимизаций
- **Инструменты**: Живой предварительный просмотр, инспектор макетов, отладка семантического дерева

## Use Cases

### When to Use

- **New Android projects**: Recommended for all new UI development
- **Modern UI patterns**: Complex animations, dynamic layouts, state-driven UIs
- **Rapid prototyping**: Faster iteration with preview and hot reload
- **Kotlin-based projects**: Natural fit for Kotlin codebases
- **Material Design 3**: Easy implementation of latest design guidelines
- **Form-heavy apps**: Simplified state management for input validation
- **Incremental migration**: Can be adopted screen-by-screen in existing apps

### When to Avoid

- **Legacy apps with heavy `View` investment**: Migration cost may be high
- **WebView-heavy apps**: Compose doesn't add much value
- **Custom `View`-heavy apps**: Complex custom Views may be harder to port
- **Team unfamiliar with Kotlin**: Requires Kotlin knowledge
- **Tight deadlines with `View` expertise**: Learning curve may slow initial development

## Trade-offs

**Pros**:
- **Less boilerplate**: No findViewById, ViewBinding, or XML layouts
- **Better state management**: Reactive updates, less manual synchronization
- **Type-safe**: Kotlin compile-time checking vs. XML runtime errors
- **Easier testing**: Composables are just functions, easier to unit test
- **Better animations**: Declarative animation APIs
- **Live previews**: See changes instantly without building/running
- **Modern paradigm**: Aligns with React, SwiftUI, Flutter approaches
- **Smaller APK**: No XML inflation overhead

**Cons**:
- **Learning curve**: New mental model for `View`-based developers
- **Ecosystem maturity**: Fewer third-party libraries than `View` system
- **Debugging complexity**: Recomposition can be hard to debug
- **Performance pitfalls**: Easy to trigger unnecessary recompositions
- **Limited customization**: Some advanced `View` features not yet available
- **Breaking changes**: API still evolving (though stable since 1.0)
- **Build times**: Kotlin compilation can be slower than XML

## Core Concepts

### Composable Functions

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Hello, $name!")
}

// Usage
@Composable
fun MyApp() {
    Greeting(name = "Android")
}
```

### State Management

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

### State Hoisting

```kotlin
@Composable
fun StatelessCounter(
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

@Composable
fun StatefulCounter() {
    var count by remember { mutableStateOf(0) }
    StatelessCounter(
        count = count,
        onIncrement = { count++ }
    )
}
```

### Side Effects

```kotlin
@Composable
fun MyScreen(userId: String) {
    // LaunchedEffect runs on composition and when key changes
    LaunchedEffect(userId) {
        // Suspend function call
        loadUserData(userId)
    }

    // DisposableEffect for cleanup
    DisposableEffect(Unit) {
        val listener = setupListener()
        onDispose {
            listener.remove()
        }
    }
}
```

### Derived State

```kotlin
@Composable
fun ContactsList(contacts: List<Contact>) {
    var searchQuery by remember { mutableStateOf("") }

    // Recomputed only when searchQuery or contacts change
    val filteredContacts by remember(searchQuery, contacts) {
        derivedStateOf {
            contacts.filter { it.name.contains(searchQuery, ignoreCase = true) }
        }
    }

    SearchBar(query = searchQuery, onQueryChange = { searchQuery = it })
    LazyColumn {
        items(filteredContacts) { contact ->
            ContactItem(contact)
        }
    }
}
```

## Layout System

### Modifiers

```kotlin
@Composable
fun StyledButton() {
    Button(
        onClick = { /* ... */ },
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .height(56.dp)
            .background(Color.Blue)
            .clip(RoundedCornerShape(8.dp))
    ) {
        Text("Click Me")
    }
}
```

### Layout Composables

```kotlin
@Composable
fun LayoutExample() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text("Item 1")
            Text("Item 2")
        }

        Box(
            modifier = Modifier.size(100.dp),
            contentAlignment = Alignment.Center
        ) {
            Text("Centered")
        }
    }
}
```

### Lazy Lists

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }

        // Or with keys for better performance
        items(
            items = users,
            key = { user -> user.id }
        ) { user ->
            UserItem(user)
        }
    }
}
```

## ViewModel Integration

```kotlin
class MyViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun updateData(data: String) {
        _uiState.update { it.copy(data = data) }
    }
}

@Composable
fun MyScreen(viewModel: MyViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column {
        Text(uiState.data)
        Button(onClick = { viewModel.updateData("New data") }) {
            Text("Update")
        }
    }
}
```

## Navigation

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onNavigateToDetails = { id ->
                navController.navigate("details/$id")
            })
        }

        composable(
            route = "details/{id}",
            arguments = listOf(navArgument("id") { type = NavType.StringType })
        ) { backStackEntry ->
            DetailsScreen(
                id = backStackEntry.arguments?.getString("id"),
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
```

## Theming

```kotlin
@Composable
fun MyAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) {
        darkColorScheme()
    } else {
        lightColorScheme()
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}

@Composable
fun MyApp() {
    MyAppTheme {
        // Uses theme colors
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            Text(
                text = "Hello",
                color = MaterialTheme.colorScheme.onBackground,
                style = MaterialTheme.typography.headlineMedium
            )
        }
    }
}
```

## Performance Optimization

### Stability

```kotlin
// Unstable - will cause recomposition
data class User(var name: String)

// Stable - optimized recomposition
@Immutable
data class User(val name: String)

// Or use @Stable annotation
@Stable
data class User(val name: String, val age: Int)
```

### Remember

```kotlin
@Composable
fun ExpensiveComposable(data: List<Item>) {
    // Avoid recreating on every recomposition
    val processedData = remember(data) {
        data.map { processItem(it) }
    }

    LazyColumn {
        items(processedData) { item ->
            ItemView(item)
        }
    }
}
```

### Keys

```kotlin
@Composable
fun DynamicList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            key = { it.id } // Helps Compose track items efficiently
        ) { item ->
            ItemCard(item)
        }
    }
}
```

## Testing

### UI Tests

```kotlin
@get:Rule
val composeTestRule = createComposeRule()

@Test
fun testCounter() {
    composeTestRule.setContent {
        Counter()
    }

    composeTestRule.onNodeWithText("Count: 0").assertExists()
    composeTestRule.onNodeWithText("Increment").performClick()
    composeTestRule.onNodeWithText("Count: 1").assertExists()
}
```

### Previews

```kotlin
@Preview(showBackground = true)
@Preview(uiMode = Configuration.UI_MODE_NIGHT_YES)
@Preview(device = Devices.TABLET)
@Composable
fun PreviewGreeting() {
    MyAppTheme {
        Greeting("Android")
    }
}
```

## Interoperability

### Compose in View

```kotlin
// In Activity or Fragment
class MyActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyAppTheme {
                MyScreen()
            }
        }
    }
}

// In XML layout
<androidx.compose.ui.platform.ComposeView
    android:id="@+id/compose_view"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

// In code
binding.composeView.setContent {
    MyComposable()
}
```

### View in Compose

```kotlin
@Composable
fun WebViewComposable(url: String) {
    AndroidView(
        factory = { context ->
            WebView(context).apply {
                loadUrl(url)
            }
        },
        update = { webView ->
            webView.loadUrl(url)
        }
    )
}
```

## Best Practices

1. **Hoist state** - Keep composables stateless when possible
2. **Use keys** - For lists and dynamic content
3. **Avoid side effects in composition** - Use LaunchedEffect, DisposableEffect
4. **Make data classes immutable** - Use `val` and `@Immutable`/@Stable
5. **Minimize recomposition scope** - Break down large composables
6. **Use derivedStateOf** - For computed values to avoid unnecessary recalculations
7. **Prefer Modifier parameters** - Allow callers to customize appearance
8. **Follow slot-based APIs** - For flexible, reusable components
9. **Test with recomposition** - Verify behavior across recompositions
10. **Profile performance** - Use Layout Inspector and recomposition counts

## Common Patterns

### Slot API Pattern

```kotlin
@Composable
fun Card(
    title: @Composable () -> Unit,
    content: @Composable () -> Unit,
    actions: @Composable () -> Unit
) {
    Column {
        title()
        content()
        Row { actions() }
    }
}

// Usage
Card(
    title = { Text("Card Title") },
    content = { Text("Card content goes here") },
    actions = {
        Button(onClick = {}) { Text("Action 1") }
        Button(onClick = {}) { Text("Action 2") }
    }
)
```

## Related Concepts

- [[c-viewmodel]] - State management with `ViewModel`
- [[c-coroutines]] - Asynchronous operations in Compose
- [[c-flow]] - Reactive data streams
- [[c-dependency-injection]] - `Hilt` integration with Compose
- [[c-navigation]] - Navigation component for Compose
- [[c-material-design]] - Material Design 3 in Compose
- [[c-accessibility]] - Accessibility in Compose
- [[c-custom-views]] - Migrating from custom Views
- [[c-testing]] - Testing Compose UIs

## References

- [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)
- [Compose Tutorial](https://developer.android.com/jetpack/compose/tutorial)
- [Thinking in Compose](https://developer.android.com/jetpack/compose/mental-model)
- [State and Jetpack Compose](https://developer.android.com/jetpack/compose/state)
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)
- [Compose Samples](https://github.com/android/compose-samples)
- [Compose Pathway](https://developer.android.com/courses/pathways/compose)

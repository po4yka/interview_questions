---
id: 20251012-122711141
title: "What Are The Most Important Components Of Compose / Какие самые важные компоненты Compose"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-play-app-signing--android--medium, q-retrofit-modify-all-requests--android--hard, q-mlkit-custom-models--ml--hard]
created: 2025-10-15
tags: [Composable functions, State management, Modifiers, Layouts, android, ui, jetpack-compose, difficulty/medium]
---

# Question (EN)

> What are the most important components of Compose?

# Вопрос (RU)

> Из каких более важных компонентов состоит Compose?

---

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

## Ответ (RU)

Jetpack Compose состоит из нескольких ключевых компонентов, которые работают вместе для создания декларативного UI-фреймворка. Понимание этих компонентов критически важно для эффективной разработки на Compose.

### 1. Composable функции

Строительные блоки Compose UI - функции с аннотацией `@Composable`. Они описывают, как должен выглядеть UI, а не как его создать. Composable функции могут вызывать другие composable функции, создавая иерархию компонентов.

**Ключевые характеристики:**
- Могут вызываться только из других composable функций
- Не возвращают значения (возвращают Unit)
- Создают или обновляют UI-дерево при выполнении
- Могут выполняться многократно и в любом порядке

### 2. State (Состояние)

State управляет данными, которые отображаются в UI. Когда состояние изменяется, зависимые composable функции перерисовываются (recompose).

**State Hoisting (Подъем состояния):**
- Перемещение состояния в вышестоящий компонент
- Делает composable функции stateless (без состояния) и более переиспользуемыми
- Родительский компонент управляет состоянием, дочерний только отображает

**Интеграция с ViewModel:**
- `collectAsState()` для StateFlow/SharedFlow
- `observeAsState()` для LiveData
- Разделение UI-логики и бизнес-логики

### 3. Modifiers (Модификаторы)

Изменяют внешний вид, поведение и layout composable функций. Модификаторы применяются в цепочке, и порядок имеет значение.

**Категории модификаторов:**
- **Размер**: `size()`, `width()`, `height()`, `fillMaxSize()`
- **Отступы**: `padding()`, `absolutePadding()`
- **Фон**: `background()`, `border()`
- **Взаимодействие**: `clickable()`, `selectable()`, `draggable()`
- **Layout**: `align()`, `weight()`, `aspectRatio()`
- **Скроллинг**: `verticalScroll()`, `horizontalScroll()`

**Порядок модификаторов критичен:**
- `padding()` затем `background()` - создает отступ вне фона
- `background()` затем `padding()` - создает отступ внутри фона

### 4. Layouts (Компоновки)

Определяют, как дочерние элементы располагаются на экране.

**Column (Вертикальный Layout):**
- Размещает элементы вертикально сверху вниз
- `verticalArrangement` - распределение пространства между элементами
- `horizontalAlignment` - выравнивание элементов по горизонтали

**Row (Горизонтальный Layout):**
- Размещает элементы горизонтально слева направо
- `horizontalArrangement` - распределение пространства
- `verticalAlignment` - выравнивание по вертикали

**Box (Стековый Layout):**
- Накладывает элементы друг на друга
- `align()` modifier для позиционирования элементов
- Полезен для оверлеев, floating action buttons

**LazyColumn/LazyRow:**
- Эффективные списки, рендерят только видимые элементы
- `items()` для добавления элементов
- `itemsIndexed()` для элементов с индексами
- Автоматическая виртуализация (recycling)

### 5. Recomposition (Перерисовка)

Механизм обновления UI при изменении состояния. Compose автоматически отслеживает, какие composable функции зависят от какого состояния, и перерисовывает только необходимые части UI.

**Оптимизация recomposition:**
- `derivedStateOf{}` - создает производное состояние, которое обновляется только при изменении вычисленного значения
- Stable классы - помечаются аннотацией `@Stable` для оптимизации
- `key{}` - помогает Compose идентифицировать элементы в списках

### 6. Effect Handlers (Обработчики эффектов)

Управляют побочными эффектами и жизненным циклом.

**LaunchedEffect:**
- Запускает coroutine при входе в composition
- Отменяется при выходе из composition
- Перезапускается при изменении ключей

**DisposableEffect:**
- Запускает код при входе, cleanup при выходе
- Используется для регистрации/отмены подписок
- `onDispose{}` блок для очистки ресурсов

**SideEffect:**
- Выполняется после каждой успешной recomposition
- Для синхронизации Compose state с не-Compose объектами

**produceState:**
- Конвертирует не-Compose источники данных в Compose State
- Полезен для Flow, LiveData, callback-based API

**rememberCoroutineScope:**
- Создает coroutine scope привязанный к композиции
- Для запуска корутин из event handlers

### 7. Material Components (Material компоненты)

Готовые UI-компоненты, следующие Material Design.

**Основные компоненты:**
- `Button`, `IconButton`, `FloatingActionButton`
- `Text`, `TextField`, `OutlinedTextField`
- `Card`, `Surface`
- `Checkbox`, `RadioButton`, `Switch`
- `Scaffold` - структура экрана с TopBar, BottomBar, FAB
- `TopAppBar`, `BottomNavigation`
- `AlertDialog`, `ModalBottomSheet`

### 8. Theme System (Система тем)

Централизованное управление стилями и темами приложения.

**Компоненты темы:**
- **ColorScheme** - цветовая палитра (primary, secondary, background, etc.)
- **Typography** - типографика (шрифты, размеры, веса)
- **Shapes** - формы (скругления углов для карточек, кнопок)

**MaterialTheme:**
- Оборачивает весь контент приложения
- Предоставляет доступ к теме через `MaterialTheme.colorScheme`, `MaterialTheme.typography`
- Поддержка светлой и темной темы

### 9. Navigation (Навигация)

Управление переходами между экранами.

**NavController:**
- Управляет навигационным стеком
- `navigate()` - переход на новый экран
- `popBackStack()` - возврат назад

**NavHost:**
- Контейнер для навигационного графа
- Определяет маршруты и соответствующие composable функции
- Поддержка аргументов и deep links

### 10. Animation (Анимации)

Встроенная поддержка анимаций.

**Типы анимаций:**
- `animateDpAsState`, `animateColorAsState` - анимация отдельных значений
- `animateContentSize()` - анимация изменения размера
- `AnimatedVisibility` - анимация появления/исчезновения
- `Crossfade` - плавный переход между контентом
- `animateFloatAsState`, `animateIntAsState` - generic анимации

### Иерархия компонентов

```
Compose Runtime (Среда выполнения)
├── Composable Functions (UI блоки)
├── State Management (Управление состоянием)
│   ├── remember, mutableStateOf
│   ├── State Hoisting
│   └── ViewModel Integration
├── Modifiers (Модификаторы)
├── Layouts (Компоновки)
│   ├── Column, Row, Box
│   ├── LazyColumn, LazyRow
│   └── Custom Layouts
├── Recomposition Engine (Механизм перерисовки)
├── Effect Handlers (Обработчики эффектов)
│   ├── LaunchedEffect, DisposableEffect
│   └── SideEffect, produceState
├── Material Components (Material компоненты)
├── Theme System (Система тем)
├── Navigation (Навигация)
└── Animations (Анимации)
```

### Резюме

Самые важные компоненты Compose:

1. **Composable функции** - Строительные блоки UI с аннотацией @Composable
2. **State** - Управляет данными и вызывает recomposition при изменении
3. **Modifiers** - Настраивают внешний вид, поведение и layout
4. **Layouts** - Размещают UI элементы (Column, Row, Box, LazyColumn)
5. **Recomposition** - Умный механизм обновления только измененных частей UI
6. **Effect handlers** - Управляют побочными эффектами и жизненным циклом
7. **Material components** - Готовые UI виджеты следующие Material Design
8. **Theme system** - Централизованная система стилей и тем
9. **Navigation** - Переходы между экранами
10. **Animations** - Встроенная поддержка анимаций

---

## Follow-ups

-   How do you choose between different Compose layout components (Column, Row, Box, LazyColumn)?
-   What's the difference between `remember` and `rememberSaveable` and when should you use each?
-   How does Compose's state management differ from traditional Android View state handling?

## References

-   `https://developer.android.com/jetpack/compose` — Jetpack Compose overview
-   `https://developer.android.com/jetpack/compose/state` — State management in Compose
-   `https://developer.android.com/jetpack/compose/layouts` — Layouts in Compose

## Related Questions

### Hub

-   [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)

-   [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
-   [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
-   [[q-mutable-state-compose--android--medium]] - MutableState basics
-   [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable
-   [[q-compose-remember-derived-state--android--medium]] - Derived state patterns

### Advanced (Harder)

-   [[q-compose-stability-skippability--android--hard]] - Stability & skippability
-   [[q-stable-classes-compose--android--hard]] - @Stable annotation
-   [[q-stable-annotation-compose--android--hard]] - Stability annotations

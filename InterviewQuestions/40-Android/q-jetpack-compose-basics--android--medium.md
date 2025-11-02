---
id: android-064
title: "Jetpack Compose Basics / Основы Jetpack Compose"
aliases: []

# Classification
topic: android
subtopics: [ui-compose, ui-state, ui-views]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [android/declarative-ui, android/jetpack-compose, android/recomposition, android/state, android/ui, difficulty/medium, en, ru]
source: internal
source_note: Created for vault completeness

# Workflow & relations
status: draft
moc: moc-android
related: [q-compose-remember-derived-state--jetpack-compose--medium, q-compose-side-effects-advanced--jetpack-compose--hard, q-compose-stability-skippability--jetpack-compose--hard, q-how-does-jetpack-compose-work--android--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [android/ui-compose, android/ui-state, android/ui-views, difficulty/medium, en, ru]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, November 1st 2025, 5:43:34 pm
---

# Question (EN)
> What is Jetpack Compose? Explain core concepts: composable functions, state management, recomposition, modifiers, layouts, and lifecycle. Provide comprehensive examples for building UIs.

# Вопрос (RU)
> Что такое Jetpack Compose? Объясните основные концепции: composable функции, управление состоянием, recomposition, модификаторы, макеты и жизненный цикл. Приведите подробные примеры построения UI.

---

## Answer (EN)

Jetpack Compose is Android's modern declarative UI toolkit that simplifies and accelerates UI development. Unlike the imperative View system, Compose describes what the UI should look like based on the current state, and the framework handles all updates automatically.

### Why Jetpack Compose?

**Traditional View System (Imperative)**:
```kotlin
// XML layout
<TextView
    android:id="@+id/textView"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

// Activity/Fragment
val textView = findViewById<TextView>(R.id.textView)
textView.text = "Hello"
textView.setTextColor(Color.BLUE)
// Must manually update when state changes
```

**Jetpack Compose (Declarative)**:
```kotlin
@Composable
fun Greeting(name: String) {
    Text(
        text = "Hello $name",
        color = Color.Blue
    )
    // Automatically updates when name changes
}
```

### Core Principles

1. **Declarative**: Describe UI state, not how to achieve it
2. **Composable**: Build UI from small, reusable functions
3. **Reactive**: UI automatically updates when state changes
4. **Data-driven**: UI is a function of state: `UI = f(state)`

### Composable Functions

Composable functions are annotated with `@Composable` and can call other composables:

```kotlin
@Composable
fun MessageCard(message: Message) {
    Row(modifier = Modifier.padding(8.dp)) {
        Image(
            painter = painterResource(R.drawable.profile),
            contentDescription = "Profile picture",
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
        )

        Spacer(modifier = Modifier.width(8.dp))

        Column {
            Text(
                text = message.author,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = message.body,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

data class Message(val author: String, val body: String)
```

**Key characteristics**:
- Must be annotated with `@Composable`
- Can call other `@Composable` functions
- Cannot return values (return type is Unit or no return)
- Can only be called from other composables or composable lambdas
- Should be side-effect free (use `SideEffect` or `LaunchedEffect` for side effects)

### State and Recomposition

**State** is any value that can change over time. When state changes, Compose **recomposes** (re-executes) composable functions that read that state.

#### Basic State Management

```kotlin
@Composable
fun Counter() {
    // remember preserves state across recompositions
    var count by remember { mutableStateOf(0) }

    Column(
        modifier = Modifier.padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}

// Without remember - WRONG!
@Composable
fun BrokenCounter() {
    var count by mutableStateOf(0)  //  Resets to 0 on every recomposition!

    Button(onClick = { count++ }) {
        Text("Count: $count")  // Always shows 0
    }
}
```

#### State Hoisting

Lifting state up to make composables stateless and reusable:

```kotlin
// Stateful version (not reusable)
@Composable
fun StatefulCounter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// Stateless version (reusable)
@Composable
fun StatelessCounter(
    count: Int,
    onIncrement: () -> Unit
) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// Parent manages state
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Current count: $count")
        StatelessCounter(
            count = count,
            onIncrement = { count++ }
        )
        Button(onClick = { count = 0 }) {
            Text("Reset")
        }
    }
}
```

#### State Types

```kotlin
// 1. mutableStateOf - single value
var name by remember { mutableStateOf("") }

// 2. mutableStateListOf - observable list
val items = remember { mutableStateListOf<String>() }
items.add("New item")  // Triggers recomposition

// 3. mutableStateMapOf - observable map
val userScores = remember { mutableStateMapOf<String, Int>() }
userScores["Alice"] = 100  // Triggers recomposition

// 4. derivedStateOf - computed value
val filteredItems by remember(items, query) {
    derivedStateOf {
        items.filter { it.contains(query, ignoreCase = true) }
    }
}
```

### Recomposition

Recomposition is the process of re-executing composables when state changes:

```kotlin
@Composable
fun RecompositionExample() {
    var count by remember { mutableStateOf(0) }

    Column {
        // This Text recomposes when count changes
        Text("Count: $count")
        println("Text recomposed!")  // Prints on every count change

        // This Text never recomposes (no state read)
        Text("Static text")
        println("Static text composed!")  // Prints only once

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Recomposition characteristics**:
- **Intelligent**: Only recomposes functions that read changed state
- **Can happen in any order**: Don't assume sequential execution
- **Can be skipped**: If inputs haven't changed
- **Should be idempotent**: Same inputs = same output
- **Should be fast**: Avoid heavy computation

#### Recomposition Scope

```kotlin
@Composable
fun ScopeExample() {
    var outerState by remember { mutableStateOf(0) }

    Column {
        Text("Outer: $outerState")  // Reads outerState

        InnerComposable()  // Doesn't read outerState - won't recompose
    }
}

@Composable
fun InnerComposable() {
    var innerState by remember { mutableStateOf(0) }

    Text("Inner: $innerState")
    Button(onClick = { innerState++ }) {
        Text("Increment Inner")
    }
    // Only this composable recomposes when innerState changes
}
```

### Modifiers

Modifiers allow you to decorate or augment composables. They can:
- Change size, layout, behavior, appearance
- Add interactions (clicks, gestures)
- Add accessibility information

```kotlin
@Composable
fun ModifierExamples() {
    // Order matters!
    Box(
        modifier = Modifier
            .size(100.dp)           // 1. Set size first
            .background(Color.Blue)  // 2. Then background
            .padding(16.dp)         // 3. Then padding
            .border(2.dp, Color.Red) // 4. Border inside padding
    )

    // Different order = different result
    Box(
        modifier = Modifier
            .padding(16.dp)         // 1. Padding first
            .size(100.dp)           // 2. Size inside padding
            .background(Color.Blue)  // 3. Background fills size
    )
}
```

#### Common Modifiers

```kotlin
@Composable
fun ModifierGuide() {
    Column {
        // Size modifiers
        Box(Modifier.size(100.dp))
        Box(Modifier.width(100.dp).height(50.dp))
        Box(Modifier.fillMaxWidth())
        Box(Modifier.fillMaxHeight())
        Box(Modifier.fillMaxSize())

        // Padding and spacing
        Box(Modifier.padding(16.dp))
        Box(Modifier.padding(horizontal = 16.dp, vertical = 8.dp))
        Box(Modifier.padding(start = 16.dp))

        // Background and borders
        Box(Modifier.background(Color.Blue))
        Box(Modifier.background(Color.Red, shape = RoundedCornerShape(8.dp)))
        Box(Modifier.border(2.dp, Color.Black))

        // Clickable
        Box(Modifier.clickable { /* onClick */ })

        // Alignment and arrangement
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text("Centered")
        }

        // Scrolling
        Column(Modifier.verticalScroll(rememberScrollState())) {
            // Content
        }
    }
}
```

#### Custom Modifiers

```kotlin
// Extension function pattern
fun Modifier.debugBorder(color: Color = Color.Red) = this.then(
    Modifier.border(2.dp, color)
)

// Usage
Text(
    "Debug text",
    modifier = Modifier.debugBorder()
)

// With composed state
fun Modifier.shimmer(enabled: Boolean): Modifier = composed {
    if (enabled) {
        val transition = rememberInfiniteTransition()
        val alpha by transition.animateFloat(
            initialValue = 0.3f,
            targetValue = 0.9f,
            animationSpec = infiniteRepeatable(
                animation = tween(1000),
                repeatMode = RepeatMode.Reverse
            )
        )
        this.alpha(alpha)
    } else {
        this
    }
}
```

### Layouts

Compose provides three basic layout composables:

#### Column - Vertical Layout

```kotlin
@Composable
fun ColumnExample() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("First item")
        Text("Second item")
        Text("Third item")
    }
}

// Arrangement options
Column(verticalArrangement = Arrangement.Top)         // Default
Column(verticalArrangement = Arrangement.Center)
Column(verticalArrangement = Arrangement.Bottom)
Column(verticalArrangement = Arrangement.SpaceBetween)
Column(verticalArrangement = Arrangement.SpaceAround)
Column(verticalArrangement = Arrangement.SpaceEvenly)
Column(verticalArrangement = Arrangement.spacedBy(8.dp))

// Alignment options
Column(horizontalAlignment = Alignment.Start)        // Default
Column(horizontalAlignment = Alignment.CenterHorizontally)
Column(horizontalAlignment = Alignment.End)
```

#### Row - Horizontal Layout

```kotlin
@Composable
fun RowExample() {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(Icons.Default.Star, contentDescription = null)
        Text("Rating")
        Text("4.5")
    }
}

// Similar arrangement and alignment options as Column
```

#### Box - Stack Layout

```kotlin
@Composable
fun BoxExample() {
    Box(
        modifier = Modifier.size(200.dp),
        contentAlignment = Alignment.Center
    ) {
        // Items stack on top of each other
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize()
        )
        Text(
            "Overlay Text",
            color = Color.White,
            fontSize = 24.sp
        )
    }
}
```

#### LazyColumn and LazyRow - Efficient Lists

```kotlin
@Composable
fun LazyListExample(items: List<String>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(items) { item ->
            Text(item)
        }

        // Or with index
        itemsIndexed(items) { index, item ->
            Text("$index: $item")
        }

        // Single item
        item {
            Text("Header")
        }
    }
}

// LazyColumn with different item types
@Composable
fun MixedLazyList() {
    LazyColumn {
        // Header
        item {
            Text(
                "Header",
                style = MaterialTheme.typography.headlineMedium
            )
        }

        // List of items
        items(20) { index ->
            ListItem(index)
        }

        // Footer
        item {
            Button(onClick = { /* Load more */ }) {
                Text("Load More")
            }
        }
    }
}

// With key for proper recomposition
@Composable
fun LazyListWithKeys(messages: List<Message>) {
    LazyColumn {
        items(
            items = messages,
            key = { message -> message.id }  // Important for animations
        ) { message ->
            MessageCard(message)
        }
    }
}
```

#### ConstraintLayout

```kotlin
@Composable
fun ConstraintLayoutExample() {
    ConstraintLayout(modifier = Modifier.fillMaxSize()) {
        val (button, text, image) = createRefs()

        Button(
            onClick = { },
            modifier = Modifier.constrainAs(button) {
                top.linkTo(parent.top, margin = 16.dp)
                start.linkTo(parent.start, margin = 16.dp)
            }
        ) {
            Text("Button")
        }

        Text(
            "Constrained Text",
            modifier = Modifier.constrainAs(text) {
                top.linkTo(button.bottom, margin = 16.dp)
                centerHorizontallyTo(parent)
            }
        )

        Image(
            painter = painterResource(R.drawable.ic_launcher),
            contentDescription = null,
            modifier = Modifier.constrainAs(image) {
                bottom.linkTo(parent.bottom, margin = 16.dp)
                end.linkTo(parent.end, margin = 16.dp)
            }
        )
    }
}
```

### Complete UI Examples

#### Example 1: Login Screen

```kotlin
@Composable
fun LoginScreen(
    onLoginClick: (String, String) -> Unit
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Welcome Back",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 32.dp)
        )

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            leadingIcon = {
                Icon(Icons.Default.Email, contentDescription = null)
            },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Email,
                imeAction = ImeAction.Next
            )
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            leadingIcon = {
                Icon(Icons.Default.Lock, contentDescription = null)
            },
            trailingIcon = {
                IconButton(onClick = { passwordVisible = !passwordVisible }) {
                    Icon(
                        if (passwordVisible) Icons.Default.Visibility
                        else Icons.Default.VisibilityOff,
                        contentDescription = "Toggle password visibility"
                    )
                }
            },
            visualTransformation = if (passwordVisible)
                VisualTransformation.None
            else
                PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Password,
                imeAction = ImeAction.Done
            )
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = { onLoginClick(email, password) },
            modifier = Modifier.fillMaxWidth(),
            enabled = email.isNotBlank() && password.isNotBlank()
        ) {
            Text("Login")
        }

        TextButton(
            onClick = { /* Navigate to forgot password */ },
            modifier = Modifier.padding(top = 8.dp)
        ) {
            Text("Forgot Password?")
        }
    }
}
```

#### Example 2: Profile Card with State

```kotlin
data class User(
    val name: String,
    val bio: String,
    val followerCount: Int,
    val isFollowing: Boolean
)

@Composable
fun ProfileCard(
    user: User,
    onFollowClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Profile picture
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary)
                ) {
                    Text(
                        text = user.name.first().toString(),
                        style = MaterialTheme.typography.headlineMedium,
                        color = Color.White,
                        modifier = Modifier.align(Alignment.Center)
                    )
                }

                Spacer(modifier = Modifier.width(16.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = user.name,
                        style = MaterialTheme.typography.titleLarge
                    )
                    Text(
                        text = "${user.followerCount} followers",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Button(
                    onClick = onFollowClick,
                    colors = if (user.isFollowing) {
                        ButtonDefaults.outlinedButtonColors()
                    } else {
                        ButtonDefaults.buttonColors()
                    }
                ) {
                    Text(if (user.isFollowing) "Following" else "Follow")
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = user.bio,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

// Usage with state
@Composable
fun ProfileScreen() {
    var user by remember {
        mutableStateOf(
            User(
                name = "John Doe",
                bio = "Android Developer | Kotlin Enthusiast",
                followerCount = 1234,
                isFollowing = false
            )
        )
    }

    ProfileCard(
        user = user,
        onFollowClick = {
            user = user.copy(
                isFollowing = !user.isFollowing,
                followerCount = if (user.isFollowing)
                    user.followerCount - 1
                else
                    user.followerCount + 1
            )
        }
    )
}
```

#### Example 3: Todo List with CRUD Operations

```kotlin
data class TodoItem(
    val id: Int,
    val title: String,
    val completed: Boolean = false
)

@Composable
fun TodoListScreen() {
    var todos by remember {
        mutableStateOf(
            listOf(
                TodoItem(1, "Learn Compose"),
                TodoItem(2, "Build an app"),
                TodoItem(3, "Deploy to Play Store")
            )
        )
    }
    var newTodoText by remember { mutableStateOf("") }
    var nextId by remember { mutableStateOf(4) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Text(
            text = "My Tasks",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // Add new todo
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = newTodoText,
                onValueChange = { newTodoText = it },
                placeholder = { Text("New task...") },
                modifier = Modifier.weight(1f),
                singleLine = true
            )

            Spacer(modifier = Modifier.width(8.dp))

            IconButton(
                onClick = {
                    if (newTodoText.isNotBlank()) {
                        todos = todos + TodoItem(nextId++, newTodoText)
                        newTodoText = ""
                    }
                }
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add task")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Todo list
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(
                items = todos,
                key = { it.id }
            ) { todo ->
                TodoItemRow(
                    todo = todo,
                    onToggle = {
                        todos = todos.map {
                            if (it.id == todo.id) it.copy(completed = !it.completed)
                            else it
                        }
                    },
                    onDelete = {
                        todos = todos.filter { it.id != todo.id }
                    }
                )
            }
        }
    }
}

@Composable
fun TodoItemRow(
    todo: TodoItem,
    onToggle: () -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(
                checked = todo.completed,
                onCheckedChange = { onToggle() }
            )

            Spacer(modifier = Modifier.width(8.dp))

            Text(
                text = todo.title,
                modifier = Modifier.weight(1f),
                style = if (todo.completed) {
                    MaterialTheme.typography.bodyLarge.copy(
                        textDecoration = TextDecoration.LineThrough,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                } else {
                    MaterialTheme.typography.bodyLarge
                }
            )

            IconButton(onClick = onDelete) {
                Icon(
                    Icons.Default.Delete,
                    contentDescription = "Delete task",
                    tint = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}
```

### Lifecycle of Composables

Composables have three lifecycle stages:

1. **Enter the Composition**: Composable is first executed
2. **Recomposition**: Re-executed when state changes
3. **Leave the Composition**: Removed from UI

```kotlin
@Composable
fun LifecycleExample() {
    DisposableEffect(Unit) {
        println("Entered composition")

        onDispose {
            println("Left composition")
        }
    }

    var count by remember { mutableStateOf(0) }

    println("Recomposing with count: $count")  // Runs on every recomposition

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

### Side Effects in Compose

Composables should be side-effect free, but sometimes you need side effects:

```kotlin
// LaunchedEffect - launch coroutine tied to composition
@Composable
fun LoadDataExample(userId: String) {
    var userData by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(userId) {  // Restarts when userId changes
        userData = loadUserData(userId)
    }

    userData?.let { user ->
        UserProfile(user)
    } ?: CircularProgressIndicator()
}

// DisposableEffect - cleanup when leaving composition
@Composable
fun TimerExample() {
    DisposableEffect(Unit) {
        val timer = Timer()
        timer.schedule(/* task */)

        onDispose {
            timer.cancel()  // Cleanup
        }
    }
}

// SideEffect - execute on every successful recomposition
@Composable
fun AnalyticsExample(screen: String) {
    SideEffect {
        analytics.logScreenView(screen)
    }
}
```

### Theme and Styling

```kotlin
@Composable
fun MyApp() {
    MaterialTheme(
        colorScheme = if (isSystemInDarkTheme()) {
            darkColorScheme()
        } else {
            lightColorScheme()
        },
        typography = Typography,
        content = content
    ) {
        // App content
    }
}

// Using theme values
@Composable
fun ThemedText() {
    Text(
        "Themed text",
        color = MaterialTheme.colorScheme.primary,
        style = MaterialTheme.typography.bodyLarge
    )
}
```

### Best Practices

1. **Keep composables small and focused**
2. **Hoist state when needed**
3. **Use keys in lazy lists**
4. **Avoid side effects in composables**
5. **Don't read state in remember initialization**
6. **Use derivedStateOf for expensive computations**
7. **Prefer stateless composables for reusability**

---

## Ответ (RU)

Jetpack Compose - это современный декларативный UI-инструментарий Android, упрощающий и ускоряющий разработку пользовательского интерфейса.

### Почему Jetpack Compose?

**Традиционная система View (Императивная)**:
```kotlin
// XML макет + код для обновления
val textView = findViewById<TextView>(R.id.textView)
textView.text = "Привет"
// Необходимо вручную обновлять при изменении состояния
```

**Jetpack Compose (Декларативная)**:
```kotlin
@Composable
fun Greeting(name: String) {
    Text("Привет $name")
    // Автоматически обновляется при изменении name
}
```

### Основные Принципы

1. **Декларативность**: Описываете состояние UI, а не как его достичь
2. **Компонуемость**: Строите UI из маленьких переиспользуемых функций
3. **Реактивность**: UI автоматически обновляется при изменении состояния
4. **Управление данными**: UI = f(состояние)

### Composable Функции

Composable функции аннотируются `@Composable` и могут вызывать другие composable:

```kotlin
@Composable
fun MessageCard(message: Message) {
    Row(modifier = Modifier.padding(8.dp)) {
        Image(
            painter = painterResource(R.drawable.profile),
            contentDescription = "Фото профиля",
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
        )

        Spacer(modifier = Modifier.width(8.dp))

        Column {
            Text(
                text = message.author,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = message.body,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}
```

### Состояние И Recomposition

**Состояние** - это любое значение, которое может измениться. При изменении состояния Compose выполняет **recomposition** (переисполнение) composable функций, читающих это состояние.

```kotlin
@Composable
fun Counter() {
    // remember сохраняет состояние между recomposition
    var count by remember { mutableStateOf(0) }

    Column(
        modifier = Modifier.padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Счет: $count")
        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}
```

### Модификаторы

Модификаторы позволяют оформлять или дополнять composable:

```kotlin
@Composable
fun ModifierExamples() {
    // Порядок имеет значение!
    Box(
        modifier = Modifier
            .size(100.dp)           // 1. Установить размер
            .background(Color.Blue)  // 2. Затем фон
            .padding(16.dp)         // 3. Затем отступ
            .border(2.dp, Color.Red) // 4. Граница внутри отступа
    )
}
```

### Макеты

#### Column - Вертикальный Макет

```kotlin
@Composable
fun ColumnExample() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Первый элемент")
        Text("Второй элемент")
        Text("Третий элемент")
    }
}
```

#### Row - Горизонтальный Макет

```kotlin
@Composable
fun RowExample() {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(Icons.Default.Star, contentDescription = null)
        Text("Рейтинг")
        Text("4.5")
    }
}
```

#### Box - Стековый Макет

```kotlin
@Composable
fun BoxExample() {
    Box(
        modifier = Modifier.size(200.dp),
        contentAlignment = Alignment.Center
    ) {
        // Элементы накладываются друг на друга
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize()
        )
        Text(
            "Наложенный текст",
            color = Color.White,
            fontSize = 24.sp
        )
    }
}
```

#### LazyColumn - Эффективные Списки

```kotlin
@Composable
fun LazyListExample(items: List<String>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(items) { item ->
            Text(item)
        }
    }
}
```

### Полные Примеры UI

#### Пример 1: Экран Входа

```kotlin
@Composable
fun LoginScreen(
    onLoginClick: (String, String) -> Unit
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Добро пожаловать",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 32.dp)
        )

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Пароль") },
            visualTransformation = if (passwordVisible)
                VisualTransformation.None
            else
                PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = { onLoginClick(email, password) },
            modifier = Modifier.fillMaxWidth(),
            enabled = email.isNotBlank() && password.isNotBlank()
        ) {
            Text("Войти")
        }
    }
}
```

#### Пример 2: Список Задач

```kotlin
data class TodoItem(
    val id: Int,
    val title: String,
    val completed: Boolean = false
)

@Composable
fun TodoListScreen() {
    var todos by remember {
        mutableStateOf(
            listOf(
                TodoItem(1, "Изучить Compose"),
                TodoItem(2, "Создать приложение"),
                TodoItem(3, "Опубликовать в Play Store")
            )
        )
    }

    Column(modifier = Modifier.padding(16.dp)) {
        Text(
            text = "Мои задачи",
            style = MaterialTheme.typography.headlineMedium
        )

        LazyColumn {
            items(
                items = todos,
                key = { it.id }
            ) { todo ->
                TodoItemRow(
                    todo = todo,
                    onToggle = {
                        todos = todos.map {
                            if (it.id == todo.id) it.copy(completed = !it.completed)
                            else it
                        }
                    }
                )
            }
        }
    }
}
```

### Жизненный Цикл Composable

Composable имеют три стадии жизненного цикла:

1. **Вход в Composition**: Composable выполняется впервые
2. **Recomposition**: Переисполняется при изменении состояния
3. **Выход из Composition**: Удаляется из UI

### Побочные Эффекты

```kotlin
// LaunchedEffect - запуск корутины привязанной к композиции
@Composable
fun LoadDataExample(userId: String) {
    var userData by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(userId) {  // Перезапускается при изменении userId
        userData = loadUserData(userId)
    }

    userData?.let { UserProfile(it) } ?: CircularProgressIndicator()
}
```

### Лучшие Практики

1. **Держите composable маленькими и сфокусированными**
2. **Поднимайте состояние когда нужно**
3. **Используйте ключи в lazy списках**
4. **Избегайте побочных эффектов в composable**
5. **Предпочитайте stateless composable для переиспользования**

---

## Related Questions

### Prerequisites (Easier)
- [[q-jetpack-compose-lazy-column--android--easy]] - LazyColumn for lists

### Related (Medium)
- [[q-recomposition-compose--android--medium]] - Jetpack Compose
- [[q-compose-modifier-system--android--medium]] - Jetpack Compose
- [[q-remember-remembersaveable--android--medium]] - Jetpack Compose
- [[q-compose-semantics--android--medium]] - Jetpack Compose

### Compose Fundamentals (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable
- [[q-compose-remember-derived-state--android--medium]] - Derived state patterns
- [[q-state-hoisting-compose--android--medium]] - State hoisting principles
- [[q-compose-modifier-order-performance--android--medium]] - Modifier order & performance

### UI & Components (Medium)
- [[q-compose-side-effects-launchedeffect-disposableeffect--android--hard]] - LaunchedEffect & DisposableEffect
- [[q-compose-gesture-detection--android--medium]] - Gesture detection
- [[q-compose-custom-animations--android--medium]] - Custom animations
- [[q-animated-visibility-vs-content--android--medium]] - AnimatedVisibility vs Content
- [[q-compose-navigation-advanced--android--medium]] - Navigation patterns
- [[q-compositionlocal-advanced--android--medium]] - CompositionLocal patterns
- [[q-compose-testing--android--medium]] - Compose testing basics
- [[q-testing-compose-ui--android--medium]] - UI testing strategies
- [[q-migration-to-compose--android--medium]] - Migration to Compose
- [[q-accessibility-compose--android--medium]] - Accessibility in Compose

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations
- [[q-compose-slot-table-recomposition--android--hard]] - Slot table internals
- [[q-compose-performance-optimization--android--hard]] - Performance optimization
- [[q-compose-custom-layout--android--hard]] - Custom layouts
- [[q-compose-side-effects-advanced--android--hard]] - Advanced side effects
- [[q-compositionlocal-compose--android--hard]] - CompositionLocal deep dive
- [[q-compose-compiler-plugin--android--hard]] - Compiler plugin internals
- q-kak-risuet-compose-na-ekrane--android--hard - Compose drawing internals

## References
- [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)
- [Compose Basics](https://developer.android.com/jetpack/compose/tutorial)
- [State and Jetpack Compose](https://developer.android.com/jetpack/compose/state)
- [Compose Layout Basics](https://developer.android.com/jetpack/compose/layouts/basics)

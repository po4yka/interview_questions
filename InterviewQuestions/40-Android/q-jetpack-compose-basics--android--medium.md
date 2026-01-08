---id: android-064
title: Jetpack Compose Basics / Основы Jetpack Compose
aliases: [Jetpack Compose Basics, Основы Jetpack Compose]
topic: android
subtopics: [ui-compose, ui-state, ui-theming]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Created for vault completeness
status: draft
moc: moc-android
related: [c-compose-recomposition, c-compose-state, c-recomposition, q-compose-modifier-system--android--medium, q-compose-remember-derived-state--android--medium, q-compose-semantics--android--medium, q-how-does-jetpack-compose-work--android--medium, q-how-does-jetpackcompose-work--android--medium, q-how-jetpack-compose-works--android--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [android/ui-compose, android/ui-state, android/ui-theming, difficulty/medium, en, ru]
---
# Вопрос (RU)
> Что такое Jetpack Compose? Объясните основные концепции: composable функции, управление состоянием, recomposition, модификаторы, макеты и жизненный цикл. Приведите подробные примеры построения UI.

# Question (EN)
> What is Jetpack Compose? Explain core concepts: composable functions, state management, recomposition, modifiers, layouts, and lifecycle. Provide comprehensive examples for building UIs.

## Ответ (RU)

Jetpack Compose — это современный декларативный UI-фреймворк для Android, который упрощает и ускоряет разработку интерфейса. В отличие от императивной `View`-системы, в Compose вы описываете, как должен выглядеть UI при данном состоянии, а фреймворк сам эффективно обновляет экран при изменении состояния.

### Почему Jetpack Compose?

**Традиционная `View`-система (императивный подход)**:
```kotlin
// XML + код
<TextView
    android:id="@+id/textView"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

val textView = findViewById<TextView>(R.id.textView)
textView.text = "Привет"
textView.setTextColor(Color.BLUE)
// При изменении данных нужно вручную менять View
```

**Jetpack Compose (декларативный подход)**:
```kotlin
@Composable
fun Greeting(name: String) {
    Text(
        text = "Привет $name",
        color = Color.Blue
    )
    // Если name приходит из состояния и меняется,
    // этот composable будет перерассчитан автоматически.
}
```

### Основные Принципы

1. **Декларативность**: UI описывается как функция состояния, а не последовательность мутаций.
2. **Компонуемость**: UI строится из мелких переиспользуемых composable-функций.
3. **Реактивность**: При изменении наблюдаемого состояния нужные участки UI перерассчитываются.
4. **UI = f(state)**: Один источник правды для состояния, предсказуемость.

### Composable-функции

Composable-функции помечаются аннотацией `@Composable` и могут вызывать другие composable:

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

data class Message(val id: Long, val author: String, val body: String)
```

Характеристики:
- `@Composable` над функцией.
- Можно вызывать только из других composable или composable-лямбд.
- Обычно возвращают `Unit` и описывают UI, а не создают `View`.
- Должны быть по возможности без побочных эффектов; побочные эффекты выносятся в `LaunchedEffect`, `SideEffect`, `DisposableEffect` и т.п.

### Состояние И Recomposition

Состояние — любое значение, которое может изменяться со временем. Если composable читает observable-состояние (например, `MutableState`), то при его изменении соответствующая область композиции будет перерассчитана.

#### Базовое Управление Состоянием

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column(
        modifier = Modifier.padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Счёт: $count")
        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}

// Пример с ошибкой
@Composable
fun BrokenCounter() {
    var count by mutableStateOf(0) // пересоздаётся при каждой recomposition

    Button(onClick = { count++ }) {
        Text("Счёт: $count")
    }
}
```

#### Подъём Состояния (State Hoisting)

```kotlin
@Composable
fun StatefulCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Счёт: $count")
    }
}

@Composable
fun StatelessCounter(
    count: Int,
    onIncrement: () -> Unit
) {
    Button(onClick = onIncrement) {
        Text("Счёт: $count")
    }
}

@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Текущий счёт: $count")
        StatelessCounter(
            count = count,
            onIncrement = { count++ }
        )
        Button(onClick = { count = 0 }) {
            Text("Сброс")
        }
    }
}
```

#### Типы Состояния (Compose runtime)

```kotlin
// 1. mutableStateOf — одно наблюдаемое значение
var name by remember { mutableStateOf("") }

// 2. SnapshotStateList — наблюдаемый список
val items = remember { mutableStateListOf<String>() }
items.add("Новый элемент")

// 3. SnapshotStateMap — наблюдаемая map
val userScores = remember { mutableStateMapOf<String, Int>() }
userScores["Alice"] = 100

// 4. derivedStateOf — производное значение
val filteredItems by remember(items, query) {
    derivedStateOf {
        items.filter { it.contains(query, ignoreCase = true) }
    }
}
```

### Recomposition

Recomposition — повторное выполнение composable-функций, которые зависят от изменившегося состояния.

```kotlin
@Composable
fun RecompositionExample() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Счёт: $count")
        println("Recomposition: Text с счётом")

        Text("Статичный текст")
        println("Статичный Text создаётся один раз")

        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}
```

Свойства `recomposition` и стабильности:
- Пересчитываются только затронутые области дерева (scopes), а не весь экран.
- Порядок выполнения не гарантируется.
- Может быть пропущена (`skipped`), если входные данные стабильны (`stability` / `skippability`).
- Composable должны быть идемпотентны и быстрыми.

#### Область Recomposition (Scope)

```kotlin
@Composable
fun ScopeExample() {
    var outerState by remember { mutableStateOf(0) }

    Column {
        Text("Outer: $outerState")

        InnerComposable() // не читает outerState напрямую
    }
}

@Composable
fun InnerComposable() {
    var innerState by remember { mutableStateOf(0) }

    Text("Inner: $innerState")
    Button(onClick = { innerState++ }) {
        Text("Increment Inner")
    }
    // При изменении innerState пересчитывается только эта область
}
```

### Модификаторы

Модификаторы позволяют:
- задавать размер и позиционирование,
- менять фон, границы, форму,
- обрабатывать клики и жесты,
- добавлять семантику и доступность.

Порядок применения модификаторов важен.

```kotlin
@Composable
fun ModifierExamples() {
    // Порядок важен
    Box(
        modifier = Modifier
            .size(100.dp)
            .background(Color.Blue)
            .padding(16.dp)
            .border(2.dp, Color.Red)
    )

    Box(
        modifier = Modifier
            .padding(16.dp)
            .size(100.dp)
            .background(Color.Blue)
    )
}
```

#### Подборка Распространённых Модификаторов

```kotlin
@Composable
fun ModifierGuide() {
    Column {
        // Размер
        Box(Modifier.size(100.dp))
        Box(Modifier.width(100.dp).height(50.dp))
        Box(Modifier.fillMaxWidth())
        Box(Modifier.fillMaxSize())

        // Отступы и оформление
        Box(Modifier.padding(16.dp))
        Box(Modifier.background(Color.Blue))
        Box(Modifier.border(2.dp, Color.Black))

        // Взаимодействие
        Box(Modifier.clickable { /* onClick */ })

        // Выравнивание
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text("По центру")
        }

        // Прокрутка
        Column(Modifier.verticalScroll(rememberScrollState())) {
            // Прокручиваемый контент
        }
    }
}
```

#### Пользовательские Модификаторы

```kotlin
fun Modifier.debugBorder(color: Color = Color.Red): Modifier =
    this.then(Modifier.border(2.dp, color))

@Composable
fun DebugExample() {
    Text(
        "Debug text",
        modifier = Modifier.debugBorder()
    )
}

fun Modifier.shimmer(enabled: Boolean): Modifier = composed {
    if (!enabled) return@composed this

    val transition = rememberInfiniteTransition(label = "shimmer")
    val alpha by transition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.9f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )
    this.alpha(alpha)
}
```

### Макеты

#### Column — Вертикальный Список

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

#### Row — Горизонтальное Размещение

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

#### Box — Наложение

```kotlin
@Composable
fun BoxExample() {
    Box(
        modifier = Modifier.size(200.dp),
        contentAlignment = Alignment.Center
    ) {
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

#### LazyColumn / LazyRow — Списки

```kotlin
@Composable
fun LazyListExample(items: List<String>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Элементы списка
        items(items) { item ->
            Text(item)
        }

        // С индексом
        itemsIndexed(items) { index, item ->
            Text("$index: $item")
        }

        // Статический элемент
        item {
            Text("Заголовок")
        }
    }
}

@Composable
fun LazyListWithKeys(messages: List<Message>) {
    LazyColumn {
        items(
            items = messages,
            key = { message -> message.id }
        ) { message ->
            MessageCard(message)
        }
    }
}
```

#### ConstraintLayout (опционально)

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
            Text("Кнопка")
        }

        Text(
            "Текст с ограничениями",
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

### Полные Примеры UI

#### Пример 1: Экран Входа (LoginScreen)

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
            label = { Text("Пароль") },
            leadingIcon = {
                Icon(Icons.Default.Lock, contentDescription = null)
            },
            trailingIcon = {
                IconButton(onClick = { passwordVisible = !passwordVisible }) {
                    Icon(
                        imageVector = if (passwordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                        contentDescription = "Переключить видимость пароля"
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
            Text("Войти")
        }

        TextButton(
            onClick = { /* Восстановление пароля */ },
            modifier = Modifier.padding(top = 8.dp)
        ) {
            Text("Забыли пароль?")
        }
    }
}
```

#### Пример 2: Профиль С Состоянием (ProfileCard / ProfileScreen)

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
                        text = "${user.followerCount} подписчиков",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                OutlinedButton(
                    onClick = onFollowClick
                ) {
                    Text(if (user.isFollowing) "Вы подписаны" else "Подписаться")
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

#### Пример 3: Список Задач С CRUD (TodoListScreen / TodoItemRow)

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
    var newTodoText by remember { mutableStateOf("") }
    var nextId by remember { mutableStateOf(4) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Мои задачи",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = newTodoText,
                onValueChange = { newTodoText = it },
                placeholder = { Text("Новая задача...") },
                modifier = Modifier.weight(1f),
                singleLine = true
            )

            Spacer(modifier = Modifier.width(8.dp))

            IconButton(
                onClick = {
                    if (newTodoText.isNotBlank()) {
                        todos = todos + TodoItem(nextId, newTodoText)
                        nextId++
                        newTodoText = ""
                    }
                }
            ) {
                Icon(Icons.Default.Add, contentDescription = "Добавить задачу")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

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
                    contentDescription = "Удалить задачу",
                    tint = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}
```

### Жизненный Цикл Composable

Composable проходит через стадии:
1. Вход в composition — первый запуск и добавление в дерево.
2. Recomposition — повторный запуск при изменении читаемого состояния.
3. Выход из composition — удаление из дерева, очистка эффектов и состояния.

```kotlin
@Composable
fun LifecycleExample() {
    DisposableEffect(Unit) {
        println("Вошли в composition")

        onDispose {
            println("Вышли из composition")
        }
    }

    var count by remember { mutableStateOf(0) }

    println("Recomposing with count: $count")

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

### Побочные Эффекты В Compose

Composable-функции должны быть максимально чистыми; для побочных эффектов используются специальные API.

```kotlin
// LaunchedEffect — запуск coroutine, привязанной к composition
@Composable
fun LoadDataExample(userId: String) {
    var userData by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(userId) {
        userData = loadUserData(userId)
    }

    userData?.let { user ->
        UserProfile(user)
    } ?: CircularProgressIndicator()
}

// DisposableEffect — настройка/очистка ресурсов
@Composable
fun TimerExample() {
    DisposableEffect(Unit) {
        val timer = Timer()
        // timer.schedule(...)

        onDispose {
            timer.cancel()
        }
    }
}

// SideEffect — выполняется после каждой успешной recomposition
@Composable
fun AnalyticsExample(screen: String) {
    SideEffect {
        analytics.logScreenView(screen)
    }
}
```

### Тема И Стилизация

```kotlin
@Composable
fun MyApp(content: @Composable () -> Unit) {
    val darkTheme = isSystemInDarkTheme()

    MaterialTheme(
        colorScheme = if (darkTheme) darkColorScheme() else lightColorScheme(),
        typography = Typography
    ) {
        content()
    }
}

@Composable
fun ThemedText() {
    Text(
        "Текст в теме",
        color = MaterialTheme.colorScheme.primary,
        style = MaterialTheme.typography.bodyLarge
    )
}
```

### Лучшие Практики

1. Делайте composable-функции маленькими и переиспользуемыми.
2. Поднимайте состояние наверх, когда логика должна контролироваться извне.
3. Используйте стабильные ключи в `LazyColumn`/`LazyRow`.
4. Не запускайте побочные эффекты напрямую в composable — используйте `LaunchedEffect`, `SideEffect`, `DisposableEffect` и другие эффекты.
5. Не выполняйте тяжёлые операции и долгие задачи непосредственно в composition; используйте `remember`, корутины или эффекты.
6. Для производных значений используйте `derivedStateOf`.
7. Отдавайте предпочтение stateless-компонентам, принимающим состояние и события через параметры (стейт хранится снаружи).

## Answer (EN)

Jetpack Compose is Android's modern declarative UI toolkit that simplifies and accelerates UI development. Unlike the imperative `View` system, Compose describes what the UI should look like based on the current state, and the framework efficiently updates the UI when that state changes.

### Why Jetpack Compose?

**Traditional `View` System (Imperative)**:
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
    // If name changes and this composable reads it from state,
    // it will be recomposed automatically.
}
```

### Core Principles

1. **Declarative**: Describe UI based on state instead of imperatively mutating views.
2. **Composable**: Build UI from small, reusable composable functions.
3. **Reactive**: UI automatically updates when observable state changes.
4. **Data-driven**: UI is a function of state: `UI = f(state)`.

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

data class Message(val id: Long, val author: String, val body: String)
```

Key characteristics:
- Must be annotated with `@Composable`.
- Can call other `@Composable` functions.
- Typically return `Unit`; they emit UI instead of returning a `View`.
- Should be called only from other composables or composable lambdas.
- Should be side-effect free; use side-effect APIs (`LaunchedEffect`, `SideEffect`, `DisposableEffect`, etc.) for side effects.

### State and Recomposition

State is any value that can change over time. When observable state read by a composable changes, Compose schedules recomposition of the relevant composable scopes.

#### Basic State Management

```kotlin
@Composable
fun Counter() {
    // remember preserves state across recompositions while in composition
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

// Without remember - WRONG in a recomposing context
@Composable
fun BrokenCounter() {
    // Local state is recreated on every recomposition
    var count by mutableStateOf(0)

    Button(onClick = { count++ }) {
        Text("Count: $count")  // Always shows 0 in practice
    }
}
```

#### State Hoisting

Lifting state up to make composables stateless and reusable:

```kotlin
// Stateful version
@Composable
fun StatefulCounter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// Stateless (UI-only) version
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

#### State Types (Compose runtime)

```kotlin
// 1. mutableStateOf - single observable value
var name by remember { mutableStateOf("") }

// 2. SnapshotStateList - observable list
val items = remember { mutableStateListOf<String>() }
items.add("New item")  // Triggers recomposition where items are read

// 3. SnapshotStateMap - observable map
val userScores = remember { mutableStateMapOf<String, Int>() }
userScores["Alice"] = 100

// 4. derivedStateOf - computed value based on other state
val filteredItems by remember(items, query) {
    derivedStateOf {
        items.filter { it.contains(query, ignoreCase = true) }
    }
}
```

### Recomposition

Recomposition is the process where Compose re-executes composable functions when the state they read changes.

```kotlin
@Composable
fun RecompositionExample() {
    var count by remember { mutableStateOf(0) }

    Column {
        // This Text reads count, so it is updated when count changes
        Text("Count: $count")
        println("Count Text recomposed")

        // This Text does not read changing state; it is composed once
        Text("Static text")
        println("Static text composed once")

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

Recomposition characteristics:
- Only affected composable scopes that read the changed state are recomposed (not the entire UI tree).
- Can run in any order; do not rely on execution order.
- Can be skipped when inputs have not changed (stability/skippability).
- Should be idempotent: same inputs → same emitted UI.
- Should be fast; avoid heavy work directly in composables.

#### Recomposition Scope

```kotlin
@Composable
fun ScopeExample() {
    var outerState by remember { mutableStateOf(0) }

    Column {
        Text("Outer: $outerState")  // Reads outerState

        InnerComposable() // Does not read outerState directly
    }
}

@Composable
fun InnerComposable() {
    var innerState by remember { mutableStateOf(0) }

    Text("Inner: $innerState")
    Button(onClick = { innerState++ }) {
        Text("Increment Inner")
    }
    // Only this composable scope recomposes when innerState changes
}
```

### Modifiers

Modifiers decorate or augment composables:
- Layout (size, padding, alignment)
- Drawing (background, border, clip)
- Interaction (click, gestures)
- Semantics / accessibility

```kotlin
@Composable
fun ModifierExamples() {
    // Order matters
    Box(
        modifier = Modifier
            .size(100.dp)
            .background(Color.Blue)
            .padding(16.dp)
            .border(2.dp, Color.Red)
    )

    Box(
        modifier = Modifier
            .padding(16.dp)
            .size(100.dp)
            .background(Color.Blue)
    )
}
```

Common modifiers example:

```kotlin
@Composable
fun ModifierGuide() {
    Column {
        Box(Modifier.size(100.dp))
        Box(Modifier.width(100.dp).height(50.dp))
        Box(Modifier.fillMaxWidth())
        Box(Modifier.fillMaxSize())

        Box(Modifier.padding(16.dp))
        Box(Modifier.background(Color.Blue))
        Box(Modifier.border(2.dp, Color.Black))

        Box(Modifier.clickable { /* onClick */ })

        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text("Centered")
        }

        Column(Modifier.verticalScroll(rememberScrollState())) {
            // Scrollable content
        }
    }
}
```

Custom modifier examples:

```kotlin
fun Modifier.debugBorder(color: Color = Color.Red): Modifier =
    this.then(Modifier.border(2.dp, color))

@Composable
fun DebugExample() {
    Text(
        "Debug text",
        modifier = Modifier.debugBorder()
    )
}

fun Modifier.shimmer(enabled: Boolean): Modifier = composed {
    if (!enabled) return@composed this

    val transition = rememberInfiniteTransition(label = "shimmer")
    val alpha by transition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.9f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )
    this.alpha(alpha)
}
```

### Layouts

Key layout primitives:

#### Column - Vertical

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
```

#### Row - Horizontal

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
```

#### Box - `Stack`

```kotlin
@Composable
fun BoxExample() {
    Box(
        modifier = Modifier.size(200.dp),
        contentAlignment = Alignment.Center
    ) {
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

#### LazyColumn / LazyRow - Lists

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

        // With index
        itemsIndexed(items) { index, item ->
            Text("$index: $item")
        }

        // Single static item
        item {
            Text("Header")
        }
    }
}

@Composable
fun LazyListWithKeys(messages: List<Message>) {
    LazyColumn {
        items(
            items = messages,
            key = { message -> message.id }
        ) { message ->
            MessageCard(message)
        }
    }
}
```

#### ConstraintLayout (optional)

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
                        imageVector = if (passwordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
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

                OutlinedButton(
                    onClick = onFollowClick
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

#### Example 3: Todo `List` with CRUD Operations

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
        Text(
            text = "My Tasks",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

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
                        todos = todos + TodoItem(nextId, newTodoText)
                        nextId++
                        newTodoText = ""
                    }
                }
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add task")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

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

Composable functions participate in the composition lifecycle:

1. **Enter the Composition**: The composable is first executed and its UI is inserted.
2. **Recomposition**: The composable is re-executed when the state it reads changes.
3. **Leave the Composition**: The composable is removed; associated effects and remembered state are disposed.

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

    println("Recomposing with count: $count")

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

### Side Effects in Compose

Composable functions should be referentially transparent; use dedicated APIs for side effects:

```kotlin
// LaunchedEffect - launch a coroutine tied to the composition
@Composable
fun LoadDataExample(userId: String) {
    var userData by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(userId) {
        userData = loadUserData(userId)
    }

    userData?.let { user ->
        UserProfile(user)
    } ?: CircularProgressIndicator()
}

// DisposableEffect - perform setup/cleanup
@Composable
fun TimerExample() {
    DisposableEffect(Unit) {
        val timer = Timer()
        // timer.schedule(...)

        onDispose {
            timer.cancel()
        }
    }
}

// SideEffect - run after every successful recomposition
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
fun MyApp(content: @Composable () -> Unit) {
    val darkTheme = isSystemInDarkTheme()

    MaterialTheme(
        colorScheme = if (darkTheme) darkColorScheme() else lightColorScheme(),
        typography = Typography
    ) {
        content()
    }
}

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

1. Keep composables small and focused.
2. Hoist state up when you need reuse or shared control.
3. Use stable keys in lazy lists.
4. Avoid performing side effects directly in composables; use side-effect APIs.
5. Avoid doing heavy work or starting long-running operations in composition; use `remember`, coroutines, or effects appropriately.
6. Use `derivedStateOf` for derived/expensive computations based on other state.
7. Prefer stateless, UI-only composables for reusability; pass in state and events from the caller.

## Дополнительные Вопросы (RU)

- [[q-compose-remember-derived-state--android--medium]]
- [[q-compose-side-effects-advanced--android--hard]]
- [[q-compose-stability-skippability--android--hard]]

## Follow-ups

- [[q-compose-remember-derived-state--android--medium]]
- [[q-compose-side-effects-advanced--android--hard]]
- [[q-compose-stability-skippability--android--hard]]

## Ссылки (RU)

- [Документация Jetpack Compose](https://developer.android.com/jetpack/compose)
- [Основы Compose](https://developer.android.com/jetpack/compose/tutorial)
- [Состояние и Jetpack Compose](https://developer.android.com/jetpack/compose/state)
- [Основы макетов в Compose](https://developer.android.com/jetpack/compose/layouts/basics)

## References

- [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)
- [Compose Basics](https://developer.android.com/jetpack/compose/tutorial)
- [State and Jetpack Compose](https://developer.android.com/jetpack/compose/state)
- [Compose Layout Basics](https://developer.android.com/jetpack/compose/layouts/basics)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-compose-state]]

### Связанные (Medium)

- [[q-jetpack-compose-lazy-column--android--easy]]
- [[q-recomposition-compose--android--medium]]
- [[q-compose-modifier-system--android--medium]]
- [[q-remember-remembersaveable--android--medium]]

### Основы Compose (Medium)

- [[q-how-does-jetpack-compose-work--android--medium]]
- [[q-what-are-the-most-important-components-of-compose--android--medium]]
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]
- [[q-mutable-state-compose--android--medium]]
- [[q-remember-vs-remembersaveable-compose--android--medium]]
- [[q-state-hoisting-compose--android--medium]]

### Продвинутое (Harder)

- [[q-compose-stability-skippability--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]
- [[q-compose-performance-optimization--android--hard]]

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]

### Related (Medium)

- [[q-jetpack-compose-lazy-column--android--easy]]
- [[q-recomposition-compose--android--medium]]
- [[q-compose-modifier-system--android--medium]]
- [[q-remember-remembersaveable--android--medium]]

### Compose Fundamentals (Medium)

- [[q-how-does-jetpack-compose-work--android--medium]]
- [[q-what-are-the-most-important-components-of-compose--android--medium]]
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]
- [[q-mutable-state-compose--android--medium]]
- [[q-remember-vs-remembersaveable-compose--android--medium]]
- [[q-state-hoisting-compose--android--medium]]

### Advanced (Harder)

- [[q-compose-stability-skippability--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]
- [[q-compose-performance-optimization--android--hard]]

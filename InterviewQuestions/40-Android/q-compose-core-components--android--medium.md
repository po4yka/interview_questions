---
id: android-072
title: Compose Core Components / Основные компоненты Compose
aliases: [Compose Components, Jetpack Compose Architecture, Основные компоненты Compose, Архитектура Jetpack Compose]
topic: android
subtopics: [ui-compose, architecture-mvvm]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-compose-recomposition, c-mvvm-pattern, q-compose-modifier-order-performance--android--medium, q-compose-stability-skippability--android--hard]
created: 2025-10-13
updated: 2025-10-30
tags: [android/ui-compose, android/architecture-mvvm, jetpack-compose, declarative-ui, difficulty/medium]
sources: [https://developer.android.com/jetpack/compose/architecture]
---

# Вопрос (RU)
> Из каких более важных компонентов состоит Compose?

# Question (EN)
> What are the most important components that make up Compose?

## Ответ (RU)

Jetpack Compose состоит из нескольких ключевых компонентов, которые работают вместе для создания декларативного UI-фреймворка.

### Основные Компоненты

**1. Composable Functions (Компонуемые функции)**

Базовые строительные блоки UI — функции с аннотацией `@Composable`:

```kotlin
// ✅ Простая composable функция
@Composable
fun Greeting(name: String) {
    Text(text = "Привет, $name!")
}

// ✅ Композиция нескольких composable
@Composable
fun UserProfile(user: User) {
    Column {
        Text(user.name)
        Text(user.email)
        Button(onClick = { /* action */ }) {
            Text("Подписаться")
        }
    }
}
```

**2. State Management (Управление состоянием)**

Состояние управляет обновлениями UI через [[c-compose-recomposition]]:

```kotlin
// ✅ remember сохраняет состояние между рекомпозициями
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Счёт: $count")
        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}

// ✅ State hoisting для переиспользования
@Composable
fun StatelessCounter(
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
```

**3. Modifiers (Модификаторы)**

Изменяют внешний вид, поведение и layout composable:

```kotlin
// ✅ Цепочка модификаторов
@Composable
fun StyledCard() {
    Text(
        text = "Карточка",
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .shadow(4.dp, RoundedCornerShape(8.dp))
            .background(Color.White, RoundedCornerShape(8.dp))
            .padding(16.dp)
            .clickable { /* action */ }
    )
}

// ❌ Неправильный порядок
Text(
    text = "Ошибка",
    modifier = Modifier
        .padding(16.dp)
        .size(100.dp)  // ❌ padding влияет на size
)
```

**4. Layouts (Компоновка)**

Организуют элементы на экране:

```kotlin
// ✅ Column — вертикальная компоновка
@Composable
fun VerticalLayout() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Верх")
        Text("Середина")
        Text("Низ")
    }
}

// ✅ LazyColumn — эффективные списки
@Composable
fun EfficientList(items: List<Item>) {
    LazyColumn {
        items(items) { item ->
            ItemRow(item)
        }
    }
}
```

**5. Recomposition (Рекомпозиция)**

Механизм умного обновления UI при изменении состояния:

```kotlin
// ✅ Только зависимые composable перерисовываются
@Composable
fun SmartRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Счёт: $count")      // ✅ Рекомпозиция при изменении count
        Text("Статичный текст")    // ✅ Никогда не рекомпозируется
        Button(onClick = { count++ }) {
            Text("Клик")
        }
    }
}

// ✅ Оптимизация с derivedStateOf
@Composable
fun OptimizedRecomposition() {
    var text by remember { mutableStateOf("") }

    // ✅ Рекомпозиция только при изменении количества слов
    val wordCount by remember {
        derivedStateOf { text.split(" ").count { it.isNotBlank() } }
    }

    Text("Слов: $wordCount")
}
```

**6. Effect Handlers (Обработчики эффектов)**

Управляют побочными эффектами и жизненным циклом:

```kotlin
// ✅ LaunchedEffect — suspending код
@Composable
fun DataLoader(userId: String) {
    LaunchedEffect(userId) {
        val user = loadUser(userId)
        // Обновить UI
    }
}

// ✅ DisposableEffect — cleanup
@Composable
fun ListenerSetup(userId: String) {
    DisposableEffect(userId) {
        val listener = UserListener()
        userManager.addListener(listener)

        onDispose {
            userManager.removeListener(listener)  // ✅ Очистка
        }
    }
}
```

**7. Material Components**

Готовые UI-компоненты по Material Design:

```kotlin
// ✅ Готовые компоненты
@Composable
fun MaterialExample() {
    Column {
        Button(onClick = { }) {
            Text("Кнопка")
        }

        var text by remember { mutableStateOf("") }
        TextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Введите текст") }
        )

        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(4.dp)
        ) {
            Text("Контент карточки")
        }
    }
}
```

**8. Theme System (Система тем)**

Централизованная стилизация:

```kotlin
// ✅ Определение темы
@Composable
fun MyAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColors else LightColors

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = Shapes,
        content = content
    )
}

// ✅ Доступ к значениям темы
@Composable
fun ThemedText() {
    Text(
        text = "Стилизованный",
        color = MaterialTheme.colorScheme.primary,
        style = MaterialTheme.typography.headlineMedium
    )
}
```

### Иерархия Компонентов

```
Compose Runtime
├── Composable Functions
├── State Management
│   ├── remember, mutableStateOf
│   ├── State Hoisting
│   └── ViewModel Integration
├── Modifiers
├── Layouts (Column, Row, Box, LazyColumn)
├── Recomposition Engine
├── Effect Handlers
│   ├── LaunchedEffect
│   ├── DisposableEffect
│   └── SideEffect
├── Material Components
├── Theme System
├── Navigation
└── Animations
```

### Когда Использовать

| Компонент | Назначение |
|-----------|------------|
| **Composable Functions** | Создание UI-элементов |
| **State** | Управление данными UI |
| **Modifiers** | Настройка внешнего вида |
| **Layouts** | Организация элементов |
| **Effect Handlers** | Побочные эффекты, lifecycle |
| **Material Components** | Готовые UI по Material Design |

## Answer (EN)

Jetpack Compose consists of several core components that work together to create a declarative UI framework.

### Core Components

**1. Composable Functions**

Building blocks of UI — functions annotated with `@Composable`:

```kotlin
// ✅ Simple composable function
@Composable
fun Greeting(name: String) {
    Text(text = "Hello, $name!")
}

// ✅ Composition of multiple composables
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
```

**2. State Management**

State drives UI updates through [[c-compose-recomposition]]:

```kotlin
// ✅ remember preserves state across recompositions
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}

// ✅ State hoisting for reusability
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
```

**3. Modifiers**

Modify appearance, behavior, and layout of composables:

```kotlin
// ✅ Modifier chain
@Composable
fun StyledCard() {
    Text(
        text = "Card",
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .shadow(4.dp, RoundedCornerShape(8.dp))
            .background(Color.White, RoundedCornerShape(8.dp))
            .padding(16.dp)
            .clickable { /* action */ }
    )
}

// ❌ Wrong order
Text(
    text = "Error",
    modifier = Modifier
        .padding(16.dp)
        .size(100.dp)  // ❌ padding affects size
)
```

**4. Layouts**

Arrange elements on screen:

```kotlin
// ✅ Column — vertical layout
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

// ✅ LazyColumn — efficient lists
@Composable
fun EfficientList(items: List<Item>) {
    LazyColumn {
        items(items) { item ->
            ItemRow(item)
        }
    }
}
```

**5. Recomposition**

Smart UI update mechanism when state changes:

```kotlin
// ✅ Only dependent composables recompose
@Composable
fun SmartRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")      // ✅ Recomposes on count change
        Text("Static text")         // ✅ Never recomposes
        Button(onClick = { count++ }) {
            Text("Click")
        }
    }
}

// ✅ Optimization with derivedStateOf
@Composable
fun OptimizedRecomposition() {
    var text by remember { mutableStateOf("") }

    // ✅ Recomposes only when word count changes
    val wordCount by remember {
        derivedStateOf { text.split(" ").count { it.isNotBlank() } }
    }

    Text("Words: $wordCount")
}
```

**6. Effect Handlers**

Manage side effects and lifecycle:

```kotlin
// ✅ LaunchedEffect — suspending code
@Composable
fun DataLoader(userId: String) {
    LaunchedEffect(userId) {
        val user = loadUser(userId)
        // Update UI
    }
}

// ✅ DisposableEffect — cleanup
@Composable
fun ListenerSetup(userId: String) {
    DisposableEffect(userId) {
        val listener = UserListener()
        userManager.addListener(listener)

        onDispose {
            userManager.removeListener(listener)  // ✅ Cleanup
        }
    }
}
```

**7. Material Components**

Pre-built UI components following Material Design:

```kotlin
// ✅ Ready-made components
@Composable
fun MaterialExample() {
    Column {
        Button(onClick = { }) {
            Text("Button")
        }

        var text by remember { mutableStateOf("") }
        TextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Enter text") }
        )

        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(4.dp)
        ) {
            Text("Card content")
        }
    }
}
```

**8. Theme System**

Centralized styling:

```kotlin
// ✅ Define theme
@Composable
fun MyAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColors else LightColors

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = Shapes,
        content = content
    )
}

// ✅ Access theme values
@Composable
fun ThemedText() {
    Text(
        text = "Styled",
        color = MaterialTheme.colorScheme.primary,
        style = MaterialTheme.typography.headlineMedium
    )
}
```

### Component Hierarchy

```
Compose Runtime
├── Composable Functions
├── State Management
│   ├── remember, mutableStateOf
│   ├── State Hoisting
│   └── ViewModel Integration
├── Modifiers
├── Layouts (Column, Row, Box, LazyColumn)
├── Recomposition Engine
├── Effect Handlers
│   ├── LaunchedEffect
│   ├── DisposableEffect
│   └── SideEffect
├── Material Components
├── Theme System
├── Navigation
└── Animations
```

### When to Use

| Component | Purpose |
|-----------|---------|
| **Composable Functions** | Create UI elements |
| **State** | Manage UI data |
| **Modifiers** | Customize appearance |
| **Layouts** | Organize elements |
| **Effect Handlers** | Side effects, lifecycle |
| **Material Components** | Ready-made Material Design UI |

## Follow-ups

- How does Compose's recomposition differ from traditional View updates?
- What are the performance implications of state hoisting?
- How do you debug recomposition issues in Compose?
- When should you use LaunchedEffect vs DisposableEffect vs SideEffect?
- How does Compose handle configuration changes compared to traditional Views?

## References

- [[c-compose-state]]
- [[c-compose-recomposition]]
- [[c-mvvm-pattern]]
- [[c-activity-lifecycle]]
- https://developer.android.com/jetpack/compose/architecture
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-compose--android--easy]] - Compose basics
- [[q-compose-vs-views--android--easy]] - Compose vs traditional Views

### Related (Medium)
- [[q-compose-modifier-order-performance--android--medium]] - Modifier order optimization
- [[q-compositionlocal-advanced--android--medium]] - CompositionLocal patterns
- [[q-accessibility-compose--android--medium]] - Accessibility in Compose
- [[q-compose-navigation-advanced--android--medium]] - Navigation patterns

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability and skippability
- [[q-compose-custom-layout--android--hard]] - Custom layout implementation
- [[q-compose-performance-optimization--android--hard]] - Performance optimization

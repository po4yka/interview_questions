---
id: 20251012-1227159
title: "How Does Jetpack Compose Work / Как работает Jetpack Compose"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [jetpack-compose, compose, declarative-ui, recomposition, difficulty/medium]
---
# How does Jetpack Compose work?

## EN (expanded)

### What is Jetpack Compose?

Jetpack Compose is Google's modern, declarative UI framework for building native Android interfaces. It fundamentally changes how Android UIs are created by replacing XML layouts with Kotlin functions.

### Core Principles

#### 1. Declarative Approach

Instead of imperatively describing how to change UI, you declare what the UI should look like:

**Traditional View System (Imperative):**
```kotlin
// Update UI by changing properties
textView.text = "Hello"
textView.visibility = View.VISIBLE
button.isEnabled = true
```

**Compose (Declarative):**
```kotlin
@Composable
fun Greeting(name: String, isVisible: Boolean) {
    if (isVisible) {
        Text(text = "Hello $name")
    }
    Button(
        onClick = { /* action */ },
        enabled = true
    ) {
        Text("Click me")
    }
}
```

#### 2. Reactivity

UI automatically updates when data changes:

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count") // Auto-updates when count changes
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

#### 3. Component-Based Architecture

UI is built from small, reusable composable functions:

```kotlin
@Composable
fun UserCard(user: User) {
    Card {
        Column {
            UserAvatar(user.avatarUrl)
            UserName(user.name)
            UserBio(user.bio)
        }
    }
}

@Composable
fun UserAvatar(url: String) {
    Image(
        painter = rememberImagePainter(url),
        contentDescription = "User avatar"
    )
}
```

### Composable Functions

The foundation of Compose is the `@Composable` annotation:

```kotlin
@Composable
fun MyComponent() {
    Text("This is a composable function")
}
```

**Key Characteristics:**
- Must be annotated with `@Composable`
- Can only be called from other composable functions
- Describe UI structure
- Can maintain state with `remember`
- Can trigger recomposition when state changes

### How Compose Renders

The rendering process has three phases:

#### 1. Composition Phase
```kotlin
@Composable
fun Example() {
    // Compose builds UI tree
    Column {
        Text("Header")
        Button(onClick = {}) { Text("Action") }
    }
}
```

#### 2. Layout Phase
```kotlin
// Compose measures and positions elements
Box(
    modifier = Modifier
        .fillMaxWidth()
        .height(200.dp)
) {
    Text(
        text = "Centered",
        modifier = Modifier.align(Alignment.Center)
    )
}
```

#### 3. Drawing Phase
```kotlin
// Compose renders to Canvas
Canvas(modifier = Modifier.size(100.dp)) {
    drawCircle(color = Color.Blue)
}
```

### State Management

State drives recomposition:

```kotlin
@Composable
fun LoginScreen() {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    Column {
        TextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") }
        )
        TextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") }
        )
        Button(
            onClick = { login(email, password) },
            enabled = email.isNotEmpty() && password.isNotEmpty()
        ) {
            Text("Login")
        }
    }
}
```

### Recomposition

Compose intelligently recomposes only changed parts:

```kotlin
@Composable
fun SmartRecomposition() {
    var counter by remember { mutableStateOf(0) }

    Column {
        // Recomposes when counter changes
        Text("Counter: $counter")

        // Doesn't recompose (no state dependency)
        StaticHeader()

        Button(onClick = { counter++ }) {
            Text("Increment")
        }
    }
}

@Composable
fun StaticHeader() {
    Text("This is static") // Won't recompose
}
```

### Side Effects

Manage side effects with dedicated APIs:

```kotlin
@Composable
fun UserProfile(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }

    LaunchedEffect(userId) {
        // Runs when userId changes
        user = fetchUser(userId)
    }

    DisposableEffect(Unit) {
        // Cleanup when composable leaves composition
        onDispose {
            cleanup()
        }
    }

    user?.let { UserCard(it) }
}
```

### Modifiers

Modifiers configure composable appearance and behavior:

```kotlin
@Composable
fun StyledComponent() {
    Text(
        text = "Styled Text",
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .background(Color.LightGray)
            .clickable { /* action */ }
    )
}
```

---

## RU (original)

Как работает jetpackCompose?

Jetpack Compose – это декларативный UI-фреймворк от Google для создания интерфейсов в Android. Вместо традиционных XML + View в Compose используется функции-компоненты, которые описывают UI. Главные принципы работы Jetpack Compose: декларативный подход – UI создаётся через функции, без XML. Реактивность – UI автоматически обновляется, если данные изменились. Компонентный подход – UI состоит из маленьких, переиспользуемых функций. Composable-функции (@Composable) – основной строительный блок Compose.


---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable
- [[q-compose-remember-derived-state--jetpack-compose--medium]] - Derived state patterns

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations


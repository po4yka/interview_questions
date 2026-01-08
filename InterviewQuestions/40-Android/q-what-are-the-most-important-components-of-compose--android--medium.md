---\
id: android-123
title: "What Are The Most Important Components Of Compose / Какие самые важные компоненты Compose"
aliases: ["Compose Components", "Компоненты Compose"]
topic: android
subtopics: [architecture-mvvm, coroutines, ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-how-does-jetpack-compose-work--android--medium, q-mutable-state-compose--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/architecture-mvvm, android/coroutines, android/ui-compose, difficulty/medium]

---\
# Вопрос (RU)

> Какие самые важные компоненты Jetpack Compose?

# Question (EN)

> What are the most important components of Compose?

---

## Ответ (RU)

Jetpack Compose построен на нескольких ключевых компонентах, которые работают вместе для создания декларативного UI-фреймворка.

### 1. Composable Функции

Основные строительные блоки UI с аннотацией `@Composable`. Они описывают, **как должен выглядеть** UI, а не как его создать.

```kotlin
@Composable
fun UserProfile(user: User) {
    Column {
        Text(user.name)
        Text(user.email)
        // ✅ Композиция через вложенность
        Button(onClick = { /* action */ }) {
            Text("Follow")
        }
    }
}
```

**Ключевые характеристики:**
- Могут вызываться только из других `@Composable` функций
- Могут вызываться многократно; порядок и частота вызовов определяются движком композиции, поэтому функции должны быть детерминированными и без побочных эффектов
- Обычно не возвращают значения, а описывают UI-дерево (выход — составная функция)

### 2. State И Recomposition

State управляет данными UI. При изменении состояния зависимые composables автоматически перерисовываются (recompose).

```kotlin
@Composable
fun Counter() {
    // ✅ remember сохраняет состояние между recomposition
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count") // перерисовывается при изменении count
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**State Hoisting** — перенос состояния в родительский компонент для переиспользуемости:

```kotlin
// ✅ Stateless компонент (reusable)
@Composable
fun StatelessCounter(count: Int, onIncrement: () -> Unit) {
    Column {
        Text("Count: $count")
        Button(onClick = onIncrement) { Text("Increment") }
    }
}
```

**Интеграция с [[c-viewmodel|`ViewModel`]]:**

```kotlin
@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    val count by viewModel.count.collectAsState() // StateFlow → State в жизненно-осознанной среде Android
    // ...
}
```

### 3. Modifiers

Изменяют внешний вид, поведение и layout. **Порядок применения влияет на результат:**

```kotlin
Text(
    text = "Hello",
    modifier = Modifier
        .padding(16.dp)        // ✅ отступ снаружи фона
        .background(Color.Blue)
        .padding(8.dp)         // отступ внутри фона
)

// Разный порядок меняет семантику (сначала размер, затем отступ или наоборот)
Box(
    Modifier
        .padding(16.dp)        // внешний отступ
        .size(100.dp)          // размер области после учета отступа
)
```

### 4. Layouts

Определяют расположение дочерних элементов:

- **Column** — вертикальная компоновка
- **Row** — горизонтальная компоновка
- **Box** — стековая компоновка (overlay)
- **LazyColumn/LazyRow** — эффективные списки с виртуализацией (аналог `RecyclerView`)

```kotlin
@Composable
fun EfficientList(items: List<Item>) {
    LazyColumn {
        items(items) { item ->
            ItemRow(item)  // рендерятся только видимые элементы
        }
    }
}
```

### 5. Effect Handlers

Управляют побочными эффектами и жизненным циклом:

```kotlin
@Composable
fun EffectHandlers(userId: String) {
    // ✅ LaunchedEffect — запуск корутин при изменении ключа
    LaunchedEffect(userId) {
        val user = loadUser(userId)
        // обновить UI
    }

    // ✅ DisposableEffect — cleanup при выходе из composition
    DisposableEffect(userId) {
        val listener = UserListener()
        userManager.addListener(listener)
        onDispose { userManager.removeListener(listener) }
    }

    // ✅ derivedStateOf — производное состояние, оптимизирует recomposition
    var text by remember { mutableStateOf("") }
    val wordCount by remember {
        derivedStateOf { text.split(" ").count { it.isNotBlank() } }
    }
}
```

### 6. Material Components

Готовые UI-компоненты по Material Design (например, из библиотеки Material3), построенные поверх базового Compose UI: `Button`, `TextField`, `Card`, `Scaffold`, `TopAppBar`, `NavigationBar`.

### 7. Theme System

Централизованная система стилей:

```kotlin
MaterialTheme(
    colorScheme = if (darkTheme) DarkColors else LightColors,
    typography = Typography,
    shapes = Shapes
) {
    // все дочерние composables получают доступ к теме
    Text(
        color = MaterialTheme.colorScheme.primary,
        style = MaterialTheme.typography.headlineMedium
    )
}
```

### Резюме

**Критичные компоненты Compose:**

1. **@Composable функции** — UI строительные блоки
2. **State + Recomposition** — реактивная система обновления UI
3. **Modifiers** — настройка внешнего вида и поведения
4. **Layouts** (Column, Row, Box, LazyColumn) — компоновка элементов
5. **Effect handlers** (LaunchedEffect, DisposableEffect) — управление побочными эффектами
6. **Material components** — готовые UI виджеты
7. **Theme system** — централизованные стили

## Answer (EN)

Jetpack Compose is built on several core components that work together to create a declarative UI framework.

### 1. Composable Functions

UI building blocks annotated with `@Composable`. They describe **what the UI should look like**, not how to build it.

```kotlin
@Composable
fun UserProfile(user: User) {
    Column {
        Text(user.name)
        Text(user.email)
        // ✅ Composition through nesting
        Button(onClick = { /* action */ }) {
            Text("Follow")
        }
    }
}
```

**Key characteristics:**
- Only callable from other `@Composable` functions
- May be invoked multiple times; order and frequency are controlled by the composition engine, so they must be deterministic and side-effect free
- Typically don't return values; they describe the UI tree (their output is the composed UI)

### 2. State and Recomposition

State drives UI data. When state changes, dependent composables automatically recompose.

```kotlin
@Composable
fun Counter() {
    // ✅ remember preserves state across recompositions
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count") // recomposes when count changes
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**State Hoisting** — moving state to parent for reusability:

```kotlin
// ✅ Stateless component (reusable)
@Composable
fun StatelessCounter(count: Int, onIncrement: () -> Unit) {
    Column {
        Text("Count: $count")
        Button(onClick = onIncrement) { Text("Increment") }
    }
}
```

**[[c-viewmodel|`ViewModel`]] Integration:**

```kotlin
@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    val count by viewModel.count.collectAsState() // StateFlow → State in Android lifecycle-aware context
    // ...
}
```

### 3. Modifiers

Modify appearance, behavior, and layout. **Order affects the result:**

```kotlin
Text(
    text = "Hello",
    modifier = Modifier
        .padding(16.dp)        // ✅ padding outside background
        .background(Color.Blue)
        .padding(8.dp)         // padding inside background
)

// Different order changes semantics (outer vs inner padding / constraints)
Box(
    Modifier
        .padding(16.dp)        // outer padding
        .size(100.dp)          // size of the box after padding
)
```

### 4. Layouts

Define child element positioning:

- **Column** — vertical layout
- **Row** — horizontal layout
- **Box** — stack layout (overlay)
- **LazyColumn/LazyRow** — efficient lists with virtualization (like `RecyclerView`)

```kotlin
@Composable
fun EfficientList(items: List<Item>) {
    LazyColumn {
        items(items) { item ->
            ItemRow(item)  // only visible items rendered
        }
    }
}
```

### 5. Effect Handlers

Manage side effects and lifecycle:

```kotlin
@Composable
fun EffectHandlers(userId: String) {
    // ✅ LaunchedEffect — launch coroutines when key changes
    LaunchedEffect(userId) {
        val user = loadUser(userId)
        // update UI
    }

    // ✅ DisposableEffect — cleanup on leaving composition
    DisposableEffect(userId) {
        val listener = UserListener()
        userManager.addListener(listener)
        onDispose { userManager.removeListener(listener) }
    }

    // ✅ derivedStateOf — derived state, optimizes recomposition
    var text by remember { mutableStateOf("") }
    val wordCount by remember {
        derivedStateOf { text.split(" ").count { it.isNotBlank() } }
    }
}
```

### 6. Material Components

Pre-built UI components following Material Design (e.g., from Material3), built on top of core Compose UI: `Button`, `TextField`, `Card`, `Scaffold`, `TopAppBar`, `NavigationBar`.

### 7. Theme System

Centralized styling system:

```kotlin
MaterialTheme(
    colorScheme = if (darkTheme) DarkColors else LightColors,
    typography = Typography,
    shapes = Shapes
) {
    // all child composables access theme
    Text(
        color = MaterialTheme.colorScheme.primary,
        style = MaterialTheme.typography.headlineMedium
    )
}
```

### Summary

**Critical Compose components:**

1. **@Composable functions** — UI building blocks
2. **State + Recomposition** — reactive UI update system
3. **Modifiers** — customize appearance and behavior
4. **Layouts** (Column, Row, Box, LazyColumn) — element composition
5. **Effect handlers** (LaunchedEffect, DisposableEffect) — side effect management
6. **Material components** — pre-built UI widgets
7. **Theme system** — centralized styling

---

## Дополнительные Вопросы (RU)

- Как работает область действия (scope) рекомпозиции и как её оптимизировать с помощью аннотаций `@Stable` и `@Immutable`?
- Каковы trade-off'ы использования `LaunchedEffect`, `DisposableEffect` и `SideEffect` для управления побочными эффектами?
- Как `derivedStateOf` оптимизирует рекомпозицию по сравнению с прямыми вычислениями на каждом рендере?
- Когда стоит использовать `rememberSaveable` вместо `remember` для сохранения состояния?

## Follow-ups

- How does recomposition scope work and how can you optimize it using `@Stable` and `@Immutable` annotations?
- What are the trade-offs between `LaunchedEffect`, `DisposableEffect`, and `SideEffect` for managing side effects?
- How does `derivedStateOf` optimize recomposition compared to direct state calculations?
- When should you use `rememberSaveable` versus `remember` for state persistence?

## Ссылки (RU)

- [[c-jetpack-compose]] — основы Jetpack Compose
- [[c-viewmodel]] — архитектура `ViewModel`

## References

- [[c-jetpack-compose]] — Jetpack Compose fundamentals
- [[c-viewmodel]] — `ViewModel` architecture

## Связанные Вопросы (RU)

### Предпосылки

- Введение в основы Compose (см. соответствующий MOC или материалы по основам Jetpack Compose)

### Связанные

- [[q-how-does-jetpack-compose-work--android--medium]] — Как работает Compose "под капотом"
- [[q-mutable-state-compose--android--medium]] — Основы `MutableState`
- [[q-remember-vs-remembersaveable-compose--android--medium]] — Стратегии сохранения состояния

### Продвинутые

- [[q-compose-stability-skippability--android--hard]] — Оптимизация стабильности и skippability
- [[q-stable-classes-compose--android--hard]] — Продвинутые паттерны стабильности

## Related Questions

### Prerequisites

- Introduction to Compose basics (see MOC for beginner resources)

### Related

- [[q-how-does-jetpack-compose-work--android--medium]] — How Compose works under the hood
- [[q-mutable-state-compose--android--medium]] — MutableState fundamentals
- [[q-remember-vs-remembersaveable-compose--android--medium]] — State preservation strategies

### Advanced

- [[q-compose-stability-skippability--android--hard]] — Stability and skippability optimization
- [[q-stable-classes-compose--android--hard]] — Advanced stability patterns

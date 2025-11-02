---
id: android-260
title: "How Jetpack Compose Works / Как работает Jetpack Compose"
aliases: ["How Jetpack Compose Works", "Как работает Jetpack Compose"]
topic: android
subtopics: [architecture-mvvm, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android, android/architecture-mvvm, android/ui-compose, difficulty/medium, jetpack-compose]
date created: Tuesday, October 28th 2025, 9:35:10 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

> Как работает Jetpack Compose? Объясните основные принципы и внутреннее устройство.

# Question (EN)

> How does Jetpack Compose work? Explain the core principles and internal workings.

---

## Ответ (RU)

Jetpack Compose — современный декларативный UI-фреймворк от Google для создания нативных Android интерфейсов. Основан на Kotlin и использует composable-функции для описания UI.

### Основные Принципы

**Декларативный подход** — описываешь *что* отобразить, а не *как* это построить.

**Реактивность** — UI автоматически обновляется при изменении данных.

**Компонентная архитектура** — переиспользуемые функции с четкой ответственностью.

### Базовая Composable-функция

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Привет, $name!")
}

// ✅ Использование в Activity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            Greeting("Мир")
        }
    }
}
```

### Composition Tree & Slot Table

Compose строит дерево composable-функций — **Composition**. Внутри использует **slot table** (gap buffer) для эффективного отслеживания:

- Активных composables и их позиций
- Объектов состояния и запоминаемых значений
- Групповых ключей для интеллектуальной рекомпозиции

### Рекомпозиция — Ядро Compose

При изменении данных Compose умно перекомпонует только затронутые части.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        // ✅ Перекомпонуется при изменении count
        Text("Счет: $count")

        Button(onClick = { count++ }) {
            // ✅ Никогда не перекомпонуется (статичный контент)
            Text("Увеличить")
        }
    }
}
```

**Процесс**: Изменение state → Compose помечает зависимые composables невалидными → Перевыполняются только невалидные → UI обновляется.

### Управление Состоянием

**State hoisting** — подъем состояния для переиспользуемости и тестируемости.

```kotlin
// ✅ Stateless — переиспользуемый компонент
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Column {
        Text("Счет: $count")
        Button(onClick = onIncrement) {
            Text("Увеличить")
        }
    }
}

// ✅ Stateful — управляющий родитель
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    Counter(count = count, onIncrement = { count++ })
}
```

### Жизненный Цикл Composables

**Вход → Рекомпозиция → Выход**

```kotlin
@Composable
fun LifecycleExample() {
    // ✅ При входе в композицию
    LaunchedEffect(Unit) {
        println("Вошел в композицию")
    }

    // ✅ При выходе — cleanup
    DisposableEffect(Unit) {
        val listener = setupListener()
        onDispose { listener.cleanup() }
    }
}
```

### Effect Handlers

```kotlin
@Composable
fun EffectsExample(userId: String) {
    // ✅ Suspending operations, перезапуск при изменении userId
    LaunchedEffect(userId) {
        val user = loadUser(userId)
    }

    // ✅ Cleanup ресурсов
    DisposableEffect(Unit) {
        val listener = LocationListener()
        locationManager.addListener(listener)
        onDispose { locationManager.removeListener(listener) }
    }

    // ✅ Запуск корутин из event handlers
    val scope = rememberCoroutineScope()
    Button(onClick = { scope.launch { loadData() } }) {
        Text("Загрузить")
    }
}
```

### Модификаторы — Стилизация И Поведение

Порядок модификаторов критичен!

```kotlin
// ✅ Правильно: padding → background → clickable
Text(
    "Привет",
    modifier = Modifier
        .padding(16.dp)           // Сначала отступ
        .background(Color.Blue)   // Фон включает padding
        .clickable { /* ... */ }
)

// ❌ Неправильно: фон без padding
Text(
    "Привет",
    modifier = Modifier
        .background(Color.Blue)   // Фон без padding
        .padding(16.dp)           // Отступ снаружи фона
)
```

### Оптимизация Производительности

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    // ✅ LazyColumn для больших списков
    LazyColumn {
        items(items, key = { it.id }) { item ->
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
    // ✅ derivedStateOf — пересчет только при изменении зависимостей
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }

    Row {
        Text(item.name)
        if (isExpensive) Icon(Icons.Default.Star, null)
    }
}
```

### Интеграция С ViewModel

```kotlin
class HomeViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}

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

### Внутреннее Устройство

**Три фазы рендеринга**:

1. **Composition** — построение UI дерева из @Composable функций
2. **Layout** — измерение и позиционирование элементов
3. **Drawing** — рендеринг пикселей на экран

**Slot Table** использует gap buffer для эффективного хранения состояния и минимизации перевыделения памяти при рекомпозиции.

### Ключевые Отличия От View System

| View System         | Jetpack Compose           |
| ------------------- | ------------------------- |
| Императивный        | Декларативный             |
| XML + код           | Чистый Kotlin             |
| findViewById        | Прямой доступ             |
| Ручные обновления   | Автоматическая обновление |
| RecyclerView нужен  | Встроенный LazyColumn     |
| Сложный lifecycle   | Простой lifecycle         |

---

## Answer (EN)

Jetpack Compose is Google's modern declarative UI toolkit for building native Android interfaces. It leverages Kotlin and uses composable functions to describe UI.

### Core Principles

**Declarative approach** — describe *what* to display, not *how* to build it.

**Reactivity** — UI automatically updates when data changes.

**Component architecture** — reusable functions with clear responsibilities.

### Basic Composable Function

```kotlin
@Composable
fun Greeting(name: String) {
    Text(text = "Hello, $name!")
}

// ✅ Usage in Activity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            Greeting("World")
        }
    }
}
```

### Composition Tree & Slot Table

Compose builds a tree of composable functions called **Composition**. Internally, it uses a **slot table** (gap buffer) to efficiently track:

- Active composables and their positions
- State objects and remembered values
- Group keys for intelligent recomposition

### Recomposition — The Heart of Compose

When data changes, Compose intelligently recomposes only affected parts.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        // ✅ Recomposes when count changes
        Text("Count: $count")

        Button(onClick = { count++ }) {
            // ✅ Never recomposes (static content)
            Text("Increment")
        }
    }
}
```

**Process**: State change → Compose marks dependent composables invalid → Only invalid composables re-execute → UI updates.

### State Management

**State hoisting** — lift state up for reusability and testability.

```kotlin
// ✅ Stateless — reusable component
@Composable
fun Counter(count: Int, onIncrement: () -> Unit) {
    Column {
        Text("Count: $count")
        Button(onClick = onIncrement) {
            Text("Increment")
        }
    }
}

// ✅ Stateful — controlling parent
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    Counter(count = count, onIncrement = { count++ })
}
```

### Lifecycle of Composables

**Enter → Recompose → Leave**

```kotlin
@Composable
fun LifecycleExample() {
    // ✅ On entering composition
    LaunchedEffect(Unit) {
        println("Entered composition")
    }

    // ✅ On leaving — cleanup
    DisposableEffect(Unit) {
        val listener = setupListener()
        onDispose { listener.cleanup() }
    }
}
```

### Effect Handlers

```kotlin
@Composable
fun EffectsExample(userId: String) {
    // ✅ Suspending operations, restart when userId changes
    LaunchedEffect(userId) {
        val user = loadUser(userId)
    }

    // ✅ Resource cleanup
    DisposableEffect(Unit) {
        val listener = LocationListener()
        locationManager.addListener(listener)
        onDispose { locationManager.removeListener(listener) }
    }

    // ✅ Launch coroutines from event handlers
    val scope = rememberCoroutineScope()
    Button(onClick = { scope.launch { loadData() } }) {
        Text("Load")
    }
}
```

### Modifiers — Styling and Behavior

Modifier order is critical!

```kotlin
// ✅ Correct: padding → background → clickable
Text(
    "Hello",
    modifier = Modifier
        .padding(16.dp)           // Padding first
        .background(Color.Blue)   // Background includes padding
        .clickable { /* ... */ }
)

// ❌ Incorrect: background without padding
Text(
    "Hello",
    modifier = Modifier
        .background(Color.Blue)   // Background without padding
        .padding(16.dp)           // Padding outside background
)
```

### Performance Optimization

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    // ✅ LazyColumn for large lists
    LazyColumn {
        items(items, key = { it.id }) { item ->
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
    // ✅ derivedStateOf — recalculate only when dependencies change
    val isExpensive by remember(item) {
        derivedStateOf { expensiveCalculation(item) }
    }

    Row {
        Text(item.name)
        if (isExpensive) Icon(Icons.Default.Star, null)
    }
}
```

### Integration With ViewModel

```kotlin
class HomeViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}

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

### Internal Architecture

**Three rendering phases**:

1. **Composition** — build UI tree from @Composable functions
2. **Layout** — measure and position elements
3. **Drawing** — render pixels to screen

**Slot Table** uses a gap buffer for efficient state storage and minimal memory reallocation during recomposition.

### Key Differences From View System

| View System         | Jetpack Compose       |
| ------------------- | --------------------- |
| Imperative          | Declarative           |
| XML + code          | Pure Kotlin           |
| findViewById        | Direct access         |
| Manual updates      | Automatic updates     |
| RecyclerView needed | Built-in LazyColumn   |
| Complex lifecycle   | Simple lifecycle      |

---

## Follow-ups

- How does Compose determine which composables need recomposition?
- What is the difference between `remember` and `rememberSaveable`?
- When should you use `LaunchedEffect` vs `DisposableEffect`?
- How does Compose handle configuration changes?
- What are stable types and why are they important for performance?
- How does modifier order affect layout and drawing?

## References

- [[c-jetpack-compose]]
- [[c-state-management]]
- [[c-mvvm-pattern]]
- https://developer.android.com/jetpack/compose/mental-model
- https://developer.android.com/jetpack/compose/lifecycle

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-compose-side-effects--android--medium]] - LaunchedEffect, DisposableEffect, SideEffect
- [[q-compose-semantics--android--medium]] - Performance optimization techniques

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability annotations and recomposition optimization
- [[q-compose-custom-layout--android--hard]] - Custom layout implementation
- [[q-compose-slot-table-recomposition--android--hard]] - Deep dive into slot table mechanics

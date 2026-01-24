---
id: android-260
title: How Jetpack Compose Works / Как работает Jetpack Compose
aliases:
- How Jetpack Compose Works
- Как работает Jetpack Compose
topic: android
subtopics:
- architecture-mvvm
- ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-state
- c-jetpack-compose
- c-mvvm
- c-viewmodel
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android
- android/architecture-mvvm
- android/ui-compose
- difficulty/medium
anki_cards:
- slug: android-260-0-en
  language: en
  anki_id: 1768378637091
  synced_at: '2026-01-23T16:45:05.917135'
- slug: android-260-0-ru
  language: ru
  anki_id: 1768378637116
  synced_at: '2026-01-23T16:45:05.918695'
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

Compose строит дерево вызовов composable-функций — **Composition**. Внутри оно отображается в **slot table** — эффективную структуру (по принципу gap buffer) для отслеживания:

- Групп (groups) и их ключей в композиции
- Активных composables и их позиций
- Объектов состояния и запоминаемых значений

Slot table позволяет быстро соотносить результаты рекомпозиции с уже существующей структурой и минимизировать перераспределения памяти.

### Рекомпозиция — Ядро Compose

При изменении данных Compose умно рекомпозирует только затронутые части.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        // ✅ Перекомпонуется при изменении count
        Text("Счет: $count")

        Button(onClick = { count++ }) {
            // ⚠️ Тело Button может быть пропущено при рекомпозиции,
            // если Compose на основе анализа стабильности определит,
            // что оно логически не изменилось
            Text("Увеличить")
        }
    }
}
```

**Процесс**: Изменение state → Compose помечает зависящие composables невалидными → Перевыполняются только невалидные участки дерева → UI обновляется.

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

Порядок модификаторов критичен.

```kotlin
// ✅ Пример: padding → background → clickable
Text(
    "Привет",
    modifier = Modifier
        .padding(16.dp)           // Сначала отступ
        .background(Color.Blue)   // Фон включает padding
        .clickable { /* ... */ }
)

// ❌ Другой порядок: фон без padding
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
    val isExpensive by remember {
        derivedStateOf { expensiveCalculation(item) }
    }

    Row {
        Text(item.name)
        if (isExpensive) Icon(Icons.Default.Star, null)
    }
}
```

### Интеграция С `ViewModel`

```kotlin
class HomeViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}

@Composable
fun HomeScreen(viewModel: HomeViewModel = viewModel()) {
    // Для простоты: используем collectAsState для StateFlow.
    // В реальном приложении предпочтительно collectAsStateWithLifecycle для учета жизненного цикла.
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

1. **Composition** — построение UI дерева из @Composable функций и запись структуры в slot table
2. **Layout** — измерение и позиционирование элементов
3. **Drawing** — рендеринг пикселей на экран

**Slot Table** использует структуру на основе gap buffer для эффективного хранения групп и состояния и минимизации перевыделения памяти при рекомпозиции.

### Ключевые Отличия От `View` System

| `View` System         | Jetpack Compose           |
| ------------------- | ------------------------- |
| Императивный        | Декларативный             |
| XML + код           | Чистый Kotlin             |
| findViewById        | Прямой доступ             |
| Ручные обновления   | Автоматическое обновление |
| `RecyclerView` нужен  | Встроенный LazyColumn     |
| Сложный lifecycle   | Более унифицированный lifecycle |

---

## Answer (EN)

Jetpack Compose is Google's modern declarative UI toolkit for building native Android interfaces. It leverages Kotlin and uses composable functions to describe UI.

### Core Principles

**Declarative approach** — describe *what* to display, not *how* to build it.

**Reactivity** — UI automatically updates when data changes.

**`Component` architecture** — reusable functions with clear responsibilities.

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

Compose builds a tree of composable function calls called the **Composition**. Internally, it is represented in a **slot table** — an efficient gap-buffer-like structure used to track:

- Groups and their keys in the composition
- Active composables and their positions
- State objects and remembered values

The slot table allows mapping recomposition results back onto existing structure while minimizing allocations.

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
            // ⚠️ Button content can be skipped during recomposition
            // when Compose, via stability analysis, determines
            // that it has not logically changed
            Text("Increment")
        }
    }
}
```

**Process**: State change → Compose marks dependent composables invalid → Only invalid parts of the tree re-execute → UI updates.

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

Modifier order is critical.

```kotlin
// ✅ Example: padding → background → clickable
Text(
    "Hello",
    modifier = Modifier
        .padding(16.dp)           // Padding first
        .background(Color.Blue)   // Background includes padding
        .clickable { /* ... */ }
)

// ❌ Different order: background without padding
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
    val isExpensive by remember {
        derivedStateOf { expensiveCalculation(item) }
    }

    Row {
        Text(item.name)
        if (isExpensive) Icon(Icons.Default.Star, null)
    }
}
```

### Integration With `ViewModel`

```kotlin
class HomeViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}

@Composable
fun HomeScreen(viewModel: HomeViewModel = viewModel()) {
    // For simplicity: use collectAsState with StateFlow.
    // In real apps, prefer collectAsStateWithLifecycle for lifecycle-aware collection.
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

1. **Composition** — build UI tree from @Composable functions and record structure into the slot table
2. **Layout** — measure and position elements
3. **Drawing** — render pixels to screen

**Slot Table** uses a gap buffer–based structure for efficient storage of groups and state and to minimize memory reallocations during recomposition.

### Key Differences From `View` System

| `View` System         | Jetpack Compose                 |
| ------------------- | ------------------------------- |
| Imperative          | Declarative                     |
| XML + code          | Pure Kotlin                     |
| findViewById        | Direct access                   |
| Manual updates      | Automatic updates               |
| `RecyclerView` needed | Built-in LazyColumn             |
| Complex lifecycle   | More unified, composition-based lifecycle |

---

## Дополнительные Вопросы (RU)

- Как Compose определяет, какие composable-функции нужно рекомпозировать?
- В чем разница между `remember` и `rememberSaveable`?
- Когда стоит использовать `LaunchedEffect` vs `DisposableEffect`?
- Как Compose обрабатывает изменения конфигурации?
- Что такое стабильные типы и почему они важны для производительности?
- Как порядок модификаторов влияет на layout и отрисовку?

## Follow-ups

- How does Compose determine which composables need recomposition?
- What is the difference between `remember` and `rememberSaveable`?
- When should you use `LaunchedEffect` vs `DisposableEffect`?
- How does Compose handle configuration changes?
- What are stable types and why are they important for performance?
- How does modifier order affect layout and drawing?

## Ссылки (RU)

- [[c-jetpack-compose]]
- [[c-mvvm-pattern]]
- https://developer.android.com/jetpack/compose/mental-model
- https://developer.android.com/jetpack/compose/lifecycle

## References

- [[c-jetpack-compose]]
- [[c-mvvm-pattern]]
- https://developer.android.com/jetpack/compose/mental-model
- https://developer.android.com/jetpack/compose/lifecycle

## Связанные Вопросы (RU)

### Базовые (проще)

### Похожие (средний уровень)
- [[q-compose-semantics--android--medium]] - Техники оптимизации производительности

### Продвинутые (сложнее)
- [[q-compose-stability-skippability--android--hard]] - Аннотации стабильности и оптимизация рекомпозиции
- [[q-compose-custom-layout--android--hard]] - Реализация кастомного layout
- [[q-compose-slot-table-recomposition--android--hard]] - Подробный разбор механики slot table

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-compose-semantics--android--medium]] - Performance optimization techniques

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability annotations and recomposition optimization
- [[q-compose-custom-layout--android--hard]] - Custom layout implementation
- [[q-compose-slot-table-recomposition--android--hard]] - Deep dive into slot table mechanics

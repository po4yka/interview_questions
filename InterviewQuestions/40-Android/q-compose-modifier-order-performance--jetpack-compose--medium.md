---
topic: jetpack-compose
tags:
  - jetpack-compose
  - modifiers
  - performance
  - optimization
difficulty: medium
status: draft
---

# Modifier Order, Performance, and Layout Phases

**English**: How does modifier order affect performance and behavior? Explain modifier chain optimization and measure/layout/draw phases.

**Russian**: Как порядок модификаторов влияет на производительность и поведение? Объясните оптимизацию цепочки модификаторов и фазы measure/layout/draw.

## Answer (EN)

Modifier order in Jetpack Compose is crucial - it affects both visual appearance and performance. Understanding the modifier chain and layout phases is essential for writing efficient Compose UI.

### Why Modifier Order Matters

```kotlin
@Composable
fun ModifierOrderDemo() {
    // Example 1: Padding then background
    Box(
        modifier = Modifier
            .padding(16.dp)        // Padding OUTSIDE
            .background(Color.Blue) // Background fills inner area
            .size(100.dp)
    )

    // Example 2: Background then padding
    Box(
        modifier = Modifier
            .background(Color.Blue) // Background fills entire area
            .padding(16.dp)         // Padding INSIDE
            .size(100.dp)
    )
}
```

**Visual result**:
- Example 1: Blue box with 16dp transparent margin
- Example 2: Blue box (100dp) with 16dp blue padding around smaller content

### Modifier Chain Execution

Modifiers form a **linked list** and execute in order:
1. From top to bottom for measurement and layout
2. From bottom to top for drawing

```kotlin
Modifier
    .size(200.dp)           // 1. Set size constraint
    .padding(16.dp)         // 2. Add padding (reduces available space)
    .background(Color.Blue) // 3. Draw background (168dp × 168dp)
    .padding(8.dp)          // 4. Add inner padding
    .clickable { }          // 5. Handle clicks
```

**Execution flow**:

**Measure phase** (top to bottom):
```
size(200.dp)      → Constraint: 200×200
  ↓
padding(16.dp)    → Constraint: 168×168 (200-32)
  ↓
background()      → Pass through: 168×168
  ↓
padding(8.dp)     → Constraint: 152×152 (168-16)
  ↓
clickable()       → Pass through: 152×152
  ↓
Content           → Available: 152×152
```

**Draw phase** (bottom to top):
```
Content (draws first)
  ↓
clickable() (no visual)
  ↓
padding(8.dp) (no visual)
  ↓
background() (draws blue rectangle)
  ↓
padding(16.dp) (no visual)
  ↓
size() (no visual)
```

### Measure, Layout, and Draw Phases

Compose layout has three distinct phases:

#### 1. Measure Phase

**Purpose**: Calculate size of each element.

**Rules**:
- Each child measured **exactly once**
- Parent cannot measure child multiple times
- Parent passes `Constraints` to child
- Child returns `Placeable`

```kotlin
@Composable
fun CustomMeasure() {
    Layout(
        content = { Text("Hello") },
        modifier = Modifier
    ) { measurables, constraints ->
        // Measure phase
        val placeable = measurables[0].measure(constraints)

        // Layout phase
        layout(placeable.width, placeable.height) {
            // Draw phase
            placeable.place(0, 0)
        }
    }
}
```

**Constraints**:
```kotlin
data class Constraints(
    val minWidth: Int = 0,
    val maxWidth: Int = Infinity,
    val minHeight: Int = 0,
    val maxHeight: Int = Infinity
)
```

#### 2. Layout Phase

**Purpose**: Position children within parent.

**Process**:
- Parent decides where to place each child
- Uses `placeable.place(x, y)`
- Can be offset, but size is fixed from measure

```kotlin
Layout(
    content = {
        Text("Top")
        Text("Bottom")
    }
) { measurables, constraints ->
    val topPlaceable = measurables[0].measure(constraints)
    val bottomPlaceable = measurables[1].measure(constraints)

    layout(
        width = maxOf(topPlaceable.width, bottomPlaceable.width),
        height = topPlaceable.height + bottomPlaceable.height
    ) {
        // Position elements
        topPlaceable.place(0, 0)
        bottomPlaceable.place(0, topPlaceable.height)
    }
}
```

#### 3. Draw Phase

**Purpose**: Render to canvas.

**Execution**: Bottom-up through modifier chain.

```kotlin
Modifier
    .drawBehind {
        // Draws BEFORE content
        drawCircle(Color.Red)
    }
    .drawWithContent {
        // Control when content draws
        drawCircle(Color.Blue)
        drawContent() // Draw content
        drawCircle(Color.Green)
    }
```

### Performance Impact of Modifier Order

#### Example 1: Size Constraints

```kotlin
// INEFFICIENT: Size constraint at end
Box(
    modifier = Modifier
        .background(Color.Blue)
        .padding(16.dp)
        .clickable { }
        .size(100.dp)  // ❌ Late constraint
)

// EFFICIENT: Size constraint early
Box(
    modifier = Modifier
        .size(100.dp)  // ✅ Early constraint
        .background(Color.Blue)
        .padding(16.dp)
        .clickable { }
)
```

**Why**: Early size constraints reduce work for child measurements.

#### Example 2: Click Area

```kotlin
// Small clickable area
Box(
    modifier = Modifier
        .size(48.dp)
        .clickable { }      // 48×48 click area
        .padding(12.dp)
)

// Large clickable area
Box(
    modifier = Modifier
        .padding(12.dp)
        .clickable { }      // Larger click area
        .size(48.dp)
)
```

#### Example 3: Scrollable Performance

```kotlin
// INEFFICIENT: Scrollable affects size calculation
Column(
    modifier = Modifier
        .size(200.dp)
        .verticalScroll(rememberScrollState())  // ❌ After size
) { /* content */ }

// EFFICIENT: Size constraint after scroll
Column(
    modifier = Modifier
        .verticalScroll(rememberScrollState())  // ✅ Before size
        .size(200.dp)
) { /* content */ }
```

### Modifier Chain Optimization

#### Reuse Modifier Chains

```kotlin
// INEFFICIENT: Creates new chain every recomposition
@Composable
fun BadExample() {
    repeat(100) {
        Box(
            modifier = Modifier  // ❌ New instance each time
                .size(48.dp)
                .background(Color.Blue)
                .padding(8.dp)
        )
    }
}

// EFFICIENT: Reuse modifier chain
@Composable
fun GoodExample() {
    val sharedModifier = remember {
        Modifier
            .size(48.dp)
            .background(Color.Blue)
            .padding(8.dp)
    }

    repeat(100) {
        Box(modifier = sharedModifier)  // ✅ Reuse instance
    }
}
```

#### Conditional Modifiers

```kotlin
// INEFFICIENT: Creates different chains
@Composable
fun BadConditional(isSelected: Boolean) {
    Box(
        modifier = if (isSelected) {
            Modifier.background(Color.Blue).padding(8.dp)
        } else {
            Modifier.background(Color.Gray).padding(8.dp)
        }
    )
}

// EFFICIENT: Shared chain with conditional modifier
@Composable
fun GoodConditional(isSelected: Boolean) {
    Box(
        modifier = Modifier
            .background(if (isSelected) Color.Blue else Color.Gray)
            .padding(8.dp)
    )
}
```

#### Modifier.then for Dynamic Composition

```kotlin
@Composable
fun DynamicModifiers(
    isClickable: Boolean,
    isSelectable: Boolean
) {
    val modifier = Modifier
        .size(100.dp)
        .then(
            if (isClickable) Modifier.clickable { }
            else Modifier
        )
        .then(
            if (isSelectable) Modifier.border(2.dp, Color.Blue)
            else Modifier
        )

    Box(modifier = modifier)
}
```

### Skipping Layout Phases

Compose can skip phases if no changes detected:

```kotlin
@Composable
fun PhaseOptimization() {
    var color by remember { mutableStateOf(Color.Blue) }

    // Only draw phase runs on color change
    Box(
        modifier = Modifier
            .size(100.dp)  // Size constant
            .drawWithContent {
                drawRect(color)  // Only color changes
                drawContent()
            }
    )
}
```

**Phase skipping**:
- **Measure/Layout unchanged** → Only draw phase runs
- **Position unchanged** → Skip layout, run draw
- **No visual changes** → Skip all phases

### Advanced Modifier Patterns

#### Custom Modifier with Layout

```kotlin
fun Modifier.customLayout(
    offsetX: Dp = 0.dp,
    offsetY: Dp = 0.dp
) = this.layout { measurable, constraints ->
    val placeable = measurable.measure(constraints)

    layout(placeable.width, placeable.height) {
        placeable.place(
            x = offsetX.roundToPx(),
            y = offsetY.roundToPx()
        )
    }
}
```

#### DrawModifier for Performance

```kotlin
// Efficient: Only affects draw phase
fun Modifier.debugBorder() = this.drawWithContent {
    drawContent()
    drawRect(
        color = Color.Red,
        style = Stroke(width = 2.dp.toPx())
    )
}

// Less efficient: Affects layout
fun Modifier.debugBorderWithBorder() = this.border(2.dp, Color.Red)
```

### Measure/Layout/Draw Visualization

```kotlin
@Composable
fun VisualizationExample() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            // Measure: 1. Calculate constraints
            .padding(16.dp)
            // Draw: 5. (from bottom up)
            .background(Color.LightGray)
            // Measure: 2. Reduce constraints
            .padding(8.dp)
            // Draw: 4.
            .background(Color.Blue)
            // Measure: 3. Pass to content
    ) {
        // Layout: Position elements
        // Draw: 1-3. Draw content first
        Text("Content")
    }
}
```

### Common Pitfalls

**1. Size after padding**:
```kotlin
// WRONG: Size doesn't include padding
Modifier
    .padding(16.dp)
    .size(48.dp)  // Total is 48dp, not 80dp!

// CORRECT: Size includes everything
Modifier
    .size(80.dp)
    .padding(16.dp)  // 48dp content area
```

**2. Multiple backgrounds**:
```kotlin
// Creates layers (both visible if overlapping)
Modifier
    .background(Color.Blue)
    .padding(8.dp)
    .background(Color.Red)  // Both drawn!
```

**3. Clickable position**:
```kotlin
// Small hit area
Modifier
    .size(24.dp)
    .clickable { }
    .padding(12.dp)  // Padding AFTER click

// Large hit area
Modifier
    .padding(12.dp)
    .clickable { }    // Click includes padding
    .size(24.dp)
```

### Performance Best Practices

1. **Size constraints early** in modifier chain
2. **Reuse modifier chains** when possible
3. **Avoid conditional chains** - use conditional values
4. **Prefer DrawModifier** over layout changes for animations
5. **Remember expensive modifiers** outside of composables
6. **Use Modifier.then** for optional modifiers
7. **Profile with Layout Inspector** to identify issues

### Debugging Modifiers

```kotlin
// Add debug logging
fun Modifier.debugMeasure(tag: String) = this.layout { measurable, constraints ->
    Log.d("Measure", "$tag: $constraints")
    val placeable = measurable.measure(constraints)
    Log.d("Measure", "$tag: ${placeable.width} × ${placeable.height}")

    layout(placeable.width, placeable.height) {
        placeable.place(0, 0)
    }
}

// Usage
@Composable
fun DebugExample() {
    Box(
        modifier = Modifier
            .debugMeasure("outer")
            .size(200.dp)
            .debugMeasure("after-size")
            .padding(16.dp)
            .debugMeasure("after-padding")
    )
}
```

## Ответ (RU)

Порядок модификаторов в Jetpack Compose критически важен - он влияет как на визуальное отображение, так и на производительность.

### Почему порядок модификаторов важен

Модификаторы образуют связанный список и выполняются по порядку:
1. Сверху вниз для измерения и размещения
2. Снизу вверх для отрисовки

### Три фазы компоновки

**1. Measure Phase (Измерение)**: Вычисление размера каждого элемента
**2. Layout Phase (Размещение)**: Позиционирование детей внутри родителя
**3. Draw Phase (Отрисовка)**: Рендеринг на canvas

### Влияние порядка на производительность

Ранние ограничения размера уменьшают работу для измерения дочерних элементов.

[Полные примеры приведены в английском разделе]

### Лучшие практики

1. Ограничения размера **в начале** цепочки модификаторов
2. **Переиспользуйте** цепочки модификаторов
3. **Избегайте условных цепочек** - используйте условные значения
4. **Предпочитайте DrawModifier** изменениям layout для анимаций
5. **Remember** дорогие модификаторы вне composable
6. **Используйте Modifier.then** для опциональных модификаторов
7. **Профилируйте** с Layout Inspector

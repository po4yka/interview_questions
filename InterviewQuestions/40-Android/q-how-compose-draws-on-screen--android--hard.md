---
id: 20251012-1227154
title: "How Compose Draws On Screen / Как Compose рисует на экране"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-annotation-processing--android--medium, q-dalvik-vs-art-runtime--android--medium, q-sealed-classes-state-management--kotlin--medium]
created: 2025-10-15
tags: [android]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:40:15 pm
---

# How Does Compose Render on Screen?

## EN (expanded)

### Three-Phase Rendering Process

Jetpack Compose uses asynchronous rendering that goes through three distinct phases:

1. **Composition** - Building the UI tree
2. **Layout** - Measuring and positioning elements
3. **Drawing** - Rendering to Canvas via GPU

### Phase 1: Composition

The composition phase analyzes composable functions and builds a tree of UI nodes:

```kotlin
@Composable
fun MyScreen() {
    Column {  // Composition starts here
        Text("Header")
        Button(onClick = {}) {
            Text("Click me")
        }
    }
    // Compose creates a tree: Column -> [Text, Button -> Text]
}
```

**What happens:**
- Compose calls all `@Composable` functions
- Builds a tree of LayoutNodes
- Tracks state dependencies
- Determines what needs to be recomposed

**Slot Table:**
Compose maintains a "slot table" that stores:
- UI tree structure
- State values
- Remember values
- Composition locals

### Phase 2: Layout

The layout phase measures and positions each element:

```kotlin
@Composable
fun LayoutExample() {
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
}
```

**Layout Process:**

1. **Measure Pass** (bottom-up):
   - Parent asks children for their size constraints
   - Children measure themselves
   - Children report their measured size

2. **Placement Pass** (top-down):
   - Parent decides where to place each child
   - Children are positioned

```kotlin
// Custom layout example
@Composable
fun CustomLayout(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        // Measure phase
        val placeables = measurables.map { measurable ->
            measurable.measure(constraints)
        }

        // Calculate layout size
        val width = placeables.maxOfOrNull { it.width } ?: 0
        val height = placeables.sumOf { it.height }

        // Placement phase
        layout(width, height) {
            var yPosition = 0
            placeables.forEach { placeable ->
                placeable.placeRelative(x = 0, y = yPosition)
                yPosition += placeable.height
            }
        }
    }
}
```

### Phase 3: Drawing

The drawing phase renders UI to Canvas using GPU acceleration:

```kotlin
@Composable
fun DrawingExample() {
    Canvas(modifier = Modifier.size(200.dp)) {
        // Drawing operations
        drawRect(
            color = Color.Blue,
            size = size
        )
        drawCircle(
            color = Color.Red,
            radius = size.minDimension / 4,
            center = center
        )
    }
}
```

**Drawing Operations:**
- Executed on `DrawScope`
- Rendered to Skia Canvas
- GPU-accelerated
- Uses hardware layers when appropriate

### Complete Rendering Pipeline

```kotlin
@Composable
fun RenderingPipeline() {
    // 1. COMPOSITION: Build UI tree
    var count by remember { mutableStateOf(0) }

    Column(
        // 2. LAYOUT: Measure and position
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            // 3. DRAWING: Render to Canvas
            .drawBehind {
                drawRect(Color.LightGray)
            }
    ) {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

### Optimizations and Smart Recomposition

Compose optimizes rendering by only recomposing changed parts:

```kotlin
@Composable
fun OptimizedRendering() {
    var counter by remember { mutableStateOf(0) }

    Column {
        // Recomposes when counter changes
        Text("Counter: $counter")

        // Never recomposes (no state dependencies)
        StaticContent()

        // Only recomposes if enabled state changes
        Button(
            onClick = { counter++ },
            enabled = counter < 10
        ) {
            Text("Increment")
        }
    }
}

@Composable
fun StaticContent() {
    Text("This is static") // Won't recompose
}
```

### Phase Independence

Each phase can run independently:

```kotlin
@Composable
fun PhaseIndependence() {
    var offset by remember { mutableStateOf(0f) }

    Box(
        modifier = Modifier
            .offset { IntOffset(offset.roundToInt(), 0) }
            // Only layout phase reruns, no recomposition!
            .pointerInput(Unit) {
                detectHorizontalDragGestures { _, dragAmount ->
                    offset += dragAmount
                }
            }
    ) {
        ExpensiveComposable() // Won't recompose during drag
    }
}
```

### Custom Drawing with Canvas

```kotlin
@Composable
fun CustomDrawing() {
    Canvas(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        val canvasWidth = size.width
        val canvasHeight = size.height

        // Draw background
        drawRect(
            color = Color.LightGray,
            size = size
        )

        // Draw custom shapes
        drawCircle(
            color = Color.Blue,
            radius = 50.dp.toPx(),
            center = Offset(canvasWidth / 2, canvasHeight / 2)
        )

        // Draw paths
        val path = Path().apply {
            moveTo(0f, 0f)
            lineTo(canvasWidth, canvasHeight)
        }
        drawPath(
            path = path,
            color = Color.Red,
            style = Stroke(width = 5.dp.toPx())
        )

        // Draw text
        drawIntoCanvas { canvas ->
            val paint = Paint().asFrameworkPaint().apply {
                textSize = 40f
                color = android.graphics.Color.BLACK
            }
            canvas.nativeCanvas.drawText(
                "Custom Text",
                canvasWidth / 2,
                100f,
                paint
            )
        }
    }
}
```

### GPU Acceleration

Compose uses GPU through Skia:

```kotlin
@Composable
fun GpuAccelerated() {
    Box(
        modifier = Modifier
            .size(200.dp)
            .graphicsLayer {
                // GPU-accelerated transformations
                rotationZ = 45f
                scaleX = 1.5f
                scaleY = 1.5f
                alpha = 0.8f
                transformOrigin = TransformOrigin.Center
            }
            .background(Color.Blue)
    )
}
```

### Advanced: Layer Caching

```kotlin
@Composable
fun LayerCaching() {
    var animate by remember { mutableStateOf(false) }

    val rotation by animateFloatAsState(
        targetValue = if (animate) 360f else 0f
    )

    Box(
        modifier = Modifier
            .size(100.dp)
            // Cache in separate layer for performance
            .graphicsLayer {
                rotationZ = rotation
            }
            .background(Color.Blue)
    )

    Button(onClick = { animate = !animate }) {
        Text("Animate")
    }
}
```

### Rendering Performance Tips

1. **Avoid unnecessary recomposition:**
```kotlin
@Composable
fun OptimizedList(items: List<String>) {
    LazyColumn {
        items(
            items = items,
            key = { it } // Stable keys prevent unnecessary recomposition
        ) { item ->
            Text(item)
        }
    }
}
```

2. **Use derivedStateOf for computed values:**
```kotlin
@Composable
fun ComputedValue(list: List<Item>) {
    val expensiveValue by remember {
        derivedStateOf {
            list.filter { it.isValid }.size
        }
    }
    Text("Valid items: $expensiveValue")
}
```

3. **Defer reads to drawing phase:**
```kotlin
@Composable
fun DeferredRead() {
    var offset by remember { mutableStateOf(0f) }

    Box(
        modifier = Modifier
            .drawWithContent {
                // Read state in draw phase only
                translate(left = offset) {
                    this@drawWithContent.drawContent()
                }
            }
    )
}
```

---

## Ответ (RU)

Jetpack Compose использует асинхронный рендеринг, который проходит три отдельных фазы для отображения UI на экране.

### Трёхфазный Процесс Рендеринга

Compose разделяет рендеринг на три независимые фазы, каждая из которых может выполняться отдельно для оптимизации производительности:

**1. Composition (Композиция)** - построение дерева UI
**2. Layout (Размещение)** - измерение и позиционирование элементов
**3. Drawing (Рисование)** - рендеринг на Canvas через GPU

#### Фаза 1: Composition (Композиция)

На этапе композиции Compose:
- Вызывает все `@Composable` функции
- Строит дерево LayoutNode'ов
- Отслеживает зависимости от state
- Определяет, что нужно рекомпоновать при изменениях

**Slot Table** - внутренняя структура данных Compose, которая хранит:
- Структуру дерева UI
- Значения state
- Remember значения
- Composition locals

Когда state изменяется, Compose использует Slot Table чтобы определить какие composable функции нужно вызвать повторно (recomposition).

#### Фаза 2: Layout (Размещение)

Фаза layout состоит из двух проходов:

**Measure Pass (снизу вверх):**
- Родитель передаёт constraints (ограничения размера) детям
- Дети измеряют себя в рамках constraints
- Дети сообщают свой измеренный размер родителю

**Placement Pass (сверху вниз):**
- Родитель решает где разместить каждого ребёнка
- Дети размещаются в заданных координатах

**Важная особенность**: Каждый элемент может измерить детей только один раз. Это обеспечивает O(n) сложность layout вместо потенциально экспоненциальной.

#### Фаза 3: Drawing (Рисование)

На фазе рисования:
- Выполняются операции рисования на `DrawScope`
- Рендеринг на Skia Canvas
- GPU ускорение через hardware layers
- Использование hardware layers когда целесообразно

**DrawScope** предоставляет функции для рисования:
- `drawRect()`, `drawCircle()`, `drawPath()` - фигуры
- `drawText()` - текст
- `drawImage()` - изображения
- Применение трансформаций, clipping, blend modes

### Независимость Фаз

Ключевая оптимизация Compose - каждая фаза может выполняться независимо:

**Только Composition**: Когда изменяется структура UI
**Только Layout**: Когда изменяются размеры/позиции (например, offset modifier)
**Только Drawing**: Когда изменяются визуальные свойства (например, цвет, alpha)

Это позволяет избежать излишней работы. Например, изменение цвета кнопки вызывает только перерисовку, без recomposition и relayout.

### Умная Рекомпозиция

Compose оптимизирует рендеринг путём рекомпозиции только изменившихся частей:

**Skippable composables** - функции, которые можно пропустить если их параметры не изменились:
- Все параметры stable (неизменяемые или observable)
- Нет side-effects
- Функция помечена как skippable компилятором

**Restartable composables** - функции, которые могут рекомпоноваться независимо.

### GPU Ускорение Через graphicsLayer

`graphicsLayer` modifier создаёт отдельный hardware layer для аппаратного ускорения:
- Трансформации (rotation, scale, translation) применяются GPU
- Не вызывает recomposition при изменении параметров
- Кэширует результат рисования для повторного использования

**Использовать graphicsLayer для:**
- Анимаций (rotation, scale, alpha)
- Частых изменений визуальных свойств
- Сложных композиций требующих кэширования

### Canvas И Кастомное Рисование

Для кастомной графики Compose предоставляет Canvas API:
- `Canvas` composable для полного контроля рисования
- `drawBehind` modifier для рисования позади контента
- `drawWithContent` modifier для рисования до/после контента

### Оптимизация Производительности

**1. Избегать ненужной recomposition:**
- Использовать `remember` для вычислений
- Использовать `derivedStateOf` для производных значений
- Стабильные параметры для skippability

**2. Использовать stable keys для списков:**
- `key` parameter в `items()` для LazyColumn/LazyRow
- Предотвращает recomposition всего списка при изменениях

**3. Отложенное чтение state:**
- Читать state в draw phase вместо composition
- Использовать `Modifier.drawWithContent` для анимаций

**4. Использовать LazyColumn вместо Column + ScrollView:**
- LazyColumn компонует только видимые элементы
- Column компонует все элементы сразу

### Процесс Рендеринга В Деталях

```
State изменяется
       ↓
Snapshot system отмечает изменения
       ↓
Recomposer планирует recomposition
       ↓
ФАЗА 1: Composition
  - Вызов @Composable функций
  - Обновление Slot Table
  - Построение/обновление LayoutNode дерева
       ↓
ФАЗА 2: Layout
  - Measure pass (снизу вверх)
  - Placement pass (сверху вниз)
       ↓
ФАЗА 3: Drawing
  - Рисование на Skia Canvas
  - GPU рендеринг
       ↓
Отображение на экране
```

### Резюме

Compose рендерит UI через три независимые фазы:
1. **Composition** - построение дерева UI из composable функций
2. **Layout** - измерение и размещение элементов
3. **Drawing** - рисование на Canvas с GPU ускорением

Независимость фаз позволяет оптимизировать производительность, пропуская ненужные этапы. Умная рекомпозиция обновляет только изменившиеся части UI. GPU ускорение через graphicsLayer и hardware layers обеспечивает плавные анимации и высокую производительность.

---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Hard)
- [[q-compose-stability-skippability--android--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations
- [[q-compose-slot-table-recomposition--android--hard]] - Slot table internals
- [[q-compose-performance-optimization--android--hard]] - Performance optimization


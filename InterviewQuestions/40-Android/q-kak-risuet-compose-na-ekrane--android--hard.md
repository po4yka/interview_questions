---
tags:
  - android
difficulty: medium
---

# How does Compose render on screen?

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

## RU (original)

Как рисует Compose на экране

Jetpack Compose использует асинхронный рендеринг, который проходит несколько этапов: 1. Композиция – анализ и построение дерева UI. 2. Составление Layout – расчет размеров и позиций элементов. 3. Рендеринг – отрисовка UI через Canvas и GPU.

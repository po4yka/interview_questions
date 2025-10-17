---
id: 20251012-400001
title: "Compose Canvas & Graphics / Canvas и графика в Compose"
topic: android
difficulty: hard
status: draft
created: 2025-10-12
tags: [jetpack-compose, canvas, graphics, custom-drawing, android/compose, android/canvas, android/graphics, android/custom-drawing, android/animation, difficulty/hard]
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-android
related_questions:   - q-compose-performance-optimization--android--hard
  - q-compose-custom-layout--jetpack-compose--hard
  - q-compose-custom-animations--jetpack-compose--medium
slug: compose-canvas-graphics-jetpack-compose-hard
subtopics:   - jetpack-compose
  - canvas
  - graphics
  - custom-drawing
  - animation
---
# Compose Canvas & Graphics

## English Version

### Problem Statement

Jetpack Compose provides powerful Canvas APIs for custom drawing and graphics. Understanding how to use Canvas, DrawScope, and graphicsLayer is essential for creating custom UI components, charts, games, and complex animations.

**The Question:** How does Canvas work in Jetpack Compose? What is DrawScope? How do you draw shapes, paths, text, and images? What are the performance considerations?

### Detailed Answer

---

### CANVAS FUNDAMENTALS

**Canvas is a composable that provides a DrawScope for custom drawing.**

```kotlin
@Composable
fun BasicCanvas() {
    Canvas(
        modifier = Modifier
            .size(200.dp)
            .background(Color.White)
    ) {
        // DrawScope available here
        drawCircle(
            color = Color.Blue,
            radius = 50.dp.toPx(),
            center = center
        )
    }
}
```

**Key concepts:**
```
 Canvas provides DrawScope
 DrawScope has drawing functions
 Coordinates: (0,0) is top-left
 Uses pixels, not dp (convert with .toPx())
 Recomposes when state changes
```

---

### DRAWSCOPE BASICS

#### Drawing Shapes

```kotlin
@Composable
fun ShapesCanvas() {
    Canvas(modifier = Modifier.fillMaxSize()) {
        val canvasWidth = size.width
        val canvasHeight = size.height

        // 1. Circle
        drawCircle(
            color = Color.Blue,
            radius = 50.dp.toPx(),
            center = Offset(100f, 100f)
        )

        // 2. Rectangle
        drawRect(
            color = Color.Red,
            topLeft = Offset(200f, 50f),
            size = Size(150f, 100f)
        )

        // 3. Rounded Rectangle
        drawRoundRect(
            color = Color.Green,
            topLeft = Offset(400f, 50f),
            size = Size(150f, 100f),
            cornerRadius = CornerRadius(16.dp.toPx())
        )

        // 4. Line
        drawLine(
            color = Color.Black,
            start = Offset(0f, 200f),
            end = Offset(canvasWidth, 200f),
            strokeWidth = 2.dp.toPx()
        )

        // 5. Oval
        drawOval(
            color = Color.Magenta,
            topLeft = Offset(100f, 250f),
            size = Size(200f, 100f)
        )

        // 6. Arc
        drawArc(
            color = Color.Cyan,
            startAngle = 0f,
            sweepAngle = 90f,
            useCenter = true,
            topLeft = Offset(350f, 250f),
            size = Size(150f, 150f)
        )
    }
}
```

---

#### Drawing Paths

```kotlin
@Composable
fun PathCanvas() {
    Canvas(modifier = Modifier.size(300.dp)) {
        // Create custom path
        val path = Path().apply {
            moveTo(100f, 100f)  // Start point
            lineTo(200f, 100f)  // Line to
            lineTo(200f, 200f)
            lineTo(100f, 200f)
            close()  // Close path
        }

        drawPath(
            path = path,
            color = Color.Blue,
            style = Stroke(width = 4.dp.toPx())
        )
    }
}
```

**Path Operations:**
```kotlin
@Composable
fun AdvancedPathCanvas() {
    Canvas(modifier = Modifier.size(400.dp)) {
        val path = Path().apply {
            // Move to starting point
            moveTo(50f, 200f)

            // Quadratic bezier curve
            quadraticBezierTo(
                x1 = 150f, y1 = 50f,   // Control point
                x2 = 250f, y2 = 200f    // End point
            )

            // Cubic bezier curve
            cubicBezierTo(
                x1 = 300f, y1 = 100f,   // Control point 1
                x2 = 350f, y2 = 300f,   // Control point 2
                x3 = 400f, y3 = 200f    // End point
            )

            // Add circle
            addOval(Rect(100f, 250f, 200f, 350f))

            // Add rounded rectangle
            addRoundRect(
                RoundRect(
                    rect = Rect(250f, 250f, 350f, 350f),
                    cornerRadius = CornerRadius(16f, 16f)
                )
            )
        }

        drawPath(
            path = path,
            color = Color.Blue,
            style = Stroke(
                width = 3.dp.toPx(),
                cap = StrokeCap.Round,
                join = StrokeJoin.Round
            )
        )
    }
}
```

---

### DRAWING TEXT

```kotlin
@Composable
fun TextCanvas() {
    Canvas(modifier = Modifier.size(400.dp)) {
        // Create text painter
        val textMeasurer = rememberTextMeasurer()

        val text = buildAnnotatedString {
            withStyle(
                style = SpanStyle(
                    color = Color.Blue,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold
                )
            ) {
                append("Hello ")
            }
            withStyle(
                style = SpanStyle(
                    color = Color.Red,
                    fontSize = 24.sp,
                    fontStyle = FontStyle.Italic
                )
            ) {
                append("Canvas!")
            }
        }

        val textLayoutResult = textMeasurer.measure(text)

        drawText(
            textLayoutResult = textLayoutResult,
            topLeft = Offset(50f, 100f)
        )
    }
}

@Composable
fun rememberTextMeasurer(): TextMeasurer {
    val fontFamilyResolver = LocalFontFamilyResolver.current
    return remember(fontFamilyResolver) {
        TextMeasurer(
            defaultFontFamilyResolver = fontFamilyResolver,
            defaultDensity = Density(1f),
            defaultLayoutDirection = LayoutDirection.Ltr
        )
    }
}
```

---

### DRAWING IMAGES

```kotlin
@Composable
fun ImageCanvas() {
    val imageBitmap = ImageBitmap.imageResource(id = R.drawable.sample_image)

    Canvas(modifier = Modifier.size(400.dp)) {
        // Draw entire image
        drawImage(
            image = imageBitmap,
            topLeft = Offset(50f, 50f)
        )

        // Draw scaled image
        drawImage(
            image = imageBitmap,
            dstOffset = IntOffset(200, 50),
            dstSize = IntSize(150, 150)
        )

        // Draw with alpha
        drawImage(
            image = imageBitmap,
            topLeft = Offset(50f, 250f),
            alpha = 0.5f
        )

        // Draw with color filter
        drawImage(
            image = imageBitmap,
            topLeft = Offset(250f, 250f),
            colorFilter = ColorFilter.tint(
                color = Color.Red,
                blendMode = BlendMode.Modulate
            )
        )
    }
}
```

---

### GRADIENTS & BRUSHES

```kotlin
@Composable
fun GradientCanvas() {
    Canvas(modifier = Modifier.size(400.dp)) {
        // Linear Gradient
        val linearGradient = Brush.linearGradient(
            colors = listOf(Color.Red, Color.Blue, Color.Green),
            start = Offset(0f, 0f),
            end = Offset(size.width, 0f)
        )

        drawRect(
            brush = linearGradient,
            topLeft = Offset(50f, 50f),
            size = Size(300f, 100f)
        )

        // Radial Gradient
        val radialGradient = Brush.radialGradient(
            colors = listOf(Color.Yellow, Color.Red, Color.Magenta),
            center = Offset(200f, 250f),
            radius = 100f
        )

        drawCircle(
            brush = radialGradient,
            radius = 100f,
            center = Offset(200f, 250f)
        )

        // Sweep Gradient (Angular)
        val sweepGradient = Brush.sweepGradient(
            colors = listOf(
                Color.Red,
                Color.Yellow,
                Color.Green,
                Color.Cyan,
                Color.Blue,
                Color.Magenta,
                Color.Red
            ),
            center = Offset(200f, 450f)
        )

        drawCircle(
            brush = sweepGradient,
            radius = 100f,
            center = Offset(200f, 450f)
        )
    }
}
```

---

### BLEND MODES

```kotlin
@Composable
fun BlendModeCanvas() {
    Canvas(modifier = Modifier.size(400.dp)) {
        // Draw base layer
        drawCircle(
            color = Color.Red,
            radius = 80f,
            center = Offset(150f, 150f)
        )

        // Draw with different blend modes
        drawCircle(
            color = Color.Blue,
            radius = 80f,
            center = Offset(200f, 150f),
            blendMode = BlendMode.Multiply
        )

        // More blend modes
        val blendModes = listOf(
            BlendMode.Screen,
            BlendMode.Overlay,
            BlendMode.Darken,
            BlendMode.Lighten,
            BlendMode.ColorDodge,
            BlendMode.ColorBurn,
            BlendMode.Xor
        )

        blendModes.forEachIndexed { index, blendMode ->
            val x = 100f + (index % 3) * 120f
            val y = 300f + (index / 3) * 120f

            drawCircle(
                color = Color.Red,
                radius = 40f,
                center = Offset(x, y)
            )

            drawCircle(
                color = Color.Blue,
                radius = 40f,
                center = Offset(x + 30f, y),
                blendMode = blendMode
            )
        }
    }
}
```

---

### TRANSFORMATIONS

```kotlin
@Composable
fun TransformationsCanvas() {
    Canvas(modifier = Modifier.size(400.dp)) {
        // 1. Translate
        withTransform({
            translate(left = 100f, top = 50f)
        }) {
            drawRect(
                color = Color.Red,
                size = Size(100f, 100f)
            )
        }

        // 2. Rotate
        withTransform({
            rotate(degrees = 45f, pivot = Offset(300f, 100f))
        }) {
            drawRect(
                color = Color.Blue,
                topLeft = Offset(250f, 50f),
                size = Size(100f, 100f)
            )
        }

        // 3. Scale
        withTransform({
            scale(scaleX = 1.5f, scaleY = 0.5f, pivot = Offset(200f, 250f))
        }) {
            drawRect(
                color = Color.Green,
                topLeft = Offset(150f, 200f),
                size = Size(100f, 100f)
            )
        }

        // 4. Combined transformations
        withTransform({
            translate(left = 200f, top = 350f)
            rotate(degrees = 30f)
            scale(scale = 0.8f)
        }) {
            drawRect(
                color = Color.Magenta,
                size = Size(100f, 100f)
            )
        }
    }
}
```

---

### CLIPPING

```kotlin
@Composable
fun ClippingCanvas() {
    Canvas(modifier = Modifier.size(400.dp)) {
        // Clip to circle
        clipRect(
            left = 50f,
            top = 50f,
            right = 200f,
            bottom = 200f
        ) {
            drawRect(
                color = Color.Blue,
                topLeft = Offset(0f, 0f),
                size = Size(300f, 300f)
            )
        }

        // Clip to path
        val clipPath = Path().apply {
            addOval(Rect(250f, 50f, 400f, 200f))
        }

        clipPath(clipPath) {
            drawRect(
                brush = Brush.linearGradient(
                    colors = listOf(Color.Red, Color.Yellow, Color.Green)
                ),
                topLeft = Offset(200f, 0f),
                size = Size(300f, 300f)
            )
        }
    }
}
```

---

### REAL-WORLD EXAMPLES

#### Custom Progress Bar

```kotlin
@Composable
fun CircularProgressBar(
    progress: Float,
    modifier: Modifier = Modifier,
    strokeWidth: Dp = 8.dp,
    backgroundColor: Color = Color.LightGray,
    progressColor: Color = Color.Blue
) {
    Canvas(modifier = modifier.size(100.dp)) {
        val stroke = strokeWidth.toPx()
        val diameter = size.minDimension - stroke

        // Background arc
        drawArc(
            color = backgroundColor,
            startAngle = -90f,
            sweepAngle = 360f,
            useCenter = false,
            topLeft = Offset(stroke / 2, stroke / 2),
            size = Size(diameter, diameter),
            style = Stroke(width = stroke, cap = StrokeCap.Round)
        )

        // Progress arc
        drawArc(
            color = progressColor,
            startAngle = -90f,
            sweepAngle = 360f * progress,
            useCenter = false,
            topLeft = Offset(stroke / 2, stroke / 2),
            size = Size(diameter, diameter),
            style = Stroke(width = stroke, cap = StrokeCap.Round)
        )
    }
}

// Usage with animation
@Composable
fun AnimatedProgressBar() {
    var progress by remember { mutableStateOf(0f) }
    val animatedProgress by animateFloatAsState(
        targetValue = progress,
        animationSpec = tween(durationMillis = 1000)
    )

    Column {
        CircularProgressBar(progress = animatedProgress)

        Button(onClick = { progress = (progress + 0.25f).coerceAtMost(1f) }) {
            Text("Increase")
        }
    }
}
```

---

#### Line Chart

```kotlin
@Composable
fun LineChart(
    data: List<Float>,
    modifier: Modifier = Modifier,
    lineColor: Color = Color.Blue,
    lineWidth: Dp = 2.dp
) {
    Canvas(modifier = modifier.fillMaxWidth().height(200.dp)) {
        val padding = 40f
        val usableWidth = size.width - 2 * padding
        val usableHeight = size.height - 2 * padding

        if (data.size < 2) return@Canvas

        val maxValue = data.maxOrNull() ?: 1f
        val minValue = data.minOrNull() ?: 0f
        val range = maxValue - minValue

        // Draw grid lines
        repeat(5) { i ->
            val y = padding + (usableHeight / 4) * i
            drawLine(
                color = Color.Gray.copy(alpha = 0.3f),
                start = Offset(padding, y),
                end = Offset(size.width - padding, y),
                strokeWidth = 1f
            )
        }

        // Create path for line
        val path = Path()
        val stepX = usableWidth / (data.size - 1)

        data.forEachIndexed { index, value ->
            val x = padding + stepX * index
            val normalizedValue = if (range != 0f) {
                (value - minValue) / range
            } else 0.5f
            val y = padding + usableHeight * (1 - normalizedValue)

            if (index == 0) {
                path.moveTo(x, y)
            } else {
                path.lineTo(x, y)
            }

            // Draw data points
            drawCircle(
                color = lineColor,
                radius = 4.dp.toPx(),
                center = Offset(x, y)
            )
        }

        // Draw line
        drawPath(
            path = path,
            color = lineColor,
            style = Stroke(
                width = lineWidth.toPx(),
                cap = StrokeCap.Round,
                join = StrokeJoin.Round
            )
        )

        // Draw filled area under line
        val fillPath = Path().apply {
            addPath(path)
            lineTo(padding + usableWidth, padding + usableHeight)
            lineTo(padding, padding + usableHeight)
            close()
        }

        drawPath(
            path = fillPath,
            brush = Brush.verticalGradient(
                colors = listOf(
                    lineColor.copy(alpha = 0.3f),
                    Color.Transparent
                )
            )
        )
    }
}

// Usage
@Composable
fun ChartExample() {
    val data = remember {
        listOf(10f, 25f, 15f, 30f, 20f, 35f, 28f, 40f)
    }

    LineChart(data = data)
}
```

---

#### Custom Shape with Border

```kotlin
@Composable
fun CustomShapeWithBorder(
    modifier: Modifier = Modifier,
    fillColor: Color = Color.Blue,
    borderColor: Color = Color.Black,
    borderWidth: Dp = 2.dp
) {
    Canvas(modifier = modifier.size(150.dp)) {
        val path = Path().apply {
            moveTo(size.width * 0.5f, 0f)
            lineTo(size.width, size.height * 0.4f)
            lineTo(size.width * 0.8f, size.height)
            lineTo(size.width * 0.2f, size.height)
            lineTo(0f, size.height * 0.4f)
            close()
        }

        // Draw filled shape
        drawPath(
            path = path,
            color = fillColor
        )

        // Draw border
        drawPath(
            path = path,
            color = borderColor,
            style = Stroke(width = borderWidth.toPx())
        )
    }
}
```

---

### GRAPHICS LAYER

**graphicsLayer modifier for hardware-accelerated transformations.**

```kotlin
@Composable
fun GraphicsLayerExample() {
    var rotationZ by remember { mutableStateOf(0f) }
    var scaleX by remember { mutableStateOf(1f) }
    var alpha by remember { mutableStateOf(1f) }

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier
                .size(150.dp)
                .graphicsLayer {
                    this.rotationZ = rotationZ
                    this.scaleX = scaleX
                    this.scaleY = scaleX
                    this.alpha = alpha
                    this.shadowElevation = 8.dp.toPx()
                    this.shape = CircleShape
                    this.clip = true
                }
                .background(Color.Blue)
        )

        Slider(
            value = rotationZ,
            onValueChange = { rotationZ = it },
            valueRange = 0f..360f
        )

        Slider(
            value = scaleX,
            onValueChange = { scaleX = it },
            valueRange = 0.5f..2f
        )

        Slider(
            value = alpha,
            onValueChange = { alpha = it },
            valueRange = 0f..1f
        )
    }
}
```

**graphicsLayer vs drawWithContent:**
```
graphicsLayer:
 Hardware-accelerated
 Better performance for transforms
 Doesn't trigger recomposition
 Use for: rotation, scale, translation, alpha

drawWithContent:
 Access to Canvas/DrawScope
 Custom drawing operations
 More flexible
 Use for: custom effects, clipping, complex drawing
```

---

### PERFORMANCE OPTIMIZATION

#### 1. Use remember for Static Paths

```kotlin
@Composable
fun OptimizedPathCanvas() {
    //  Good: Path created once
    val path = remember {
        Path().apply {
            moveTo(100f, 100f)
            lineTo(200f, 200f)
            lineTo(100f, 200f)
            close()
        }
    }

    Canvas(modifier = Modifier.size(300.dp)) {
        drawPath(path, color = Color.Blue)
    }
}

@Composable
fun UnoptimizedPathCanvas() {
    Canvas(modifier = Modifier.size(300.dp)) {
        //  Bad: Path recreated on every recomposition
        val path = Path().apply {
            moveTo(100f, 100f)
            lineTo(200f, 200f)
            lineTo(100f, 200f)
            close()
        }
        drawPath(path, color = Color.Blue)
    }
}
```

---

#### 2. DrawBehind vs Canvas

```kotlin
//  Better performance: drawBehind
@Composable
fun DrawBehindExample() {
    Box(
        modifier = Modifier
            .size(100.dp)
            .drawBehind {
                drawCircle(
                    color = Color.Blue,
                    radius = 50.dp.toPx()
                )
            }
    )
}

//  Slightly worse: Canvas composable
@Composable
fun CanvasExample() {
    Canvas(modifier = Modifier.size(100.dp)) {
        drawCircle(
            color = Color.Blue,
            radius = 50.dp.toPx()
        )
    }
}
```

**When to use each:**
```
drawBehind:
 Drawing behind content
 Simple decorations
 Slightly better performance

Canvas:
 Complex custom drawing
 Interactive graphics
 Need full control
```

---

#### 3. Cache Complex Calculations

```kotlin
@Composable
fun OptimizedComplexDrawing(data: List<Float>) {
    // Cache expensive calculations
    val processedData = remember(data) {
        data.map { /* expensive calculation */ it * 2 }
    }

    val path = remember(processedData) {
        Path().apply {
            processedData.forEachIndexed { index, value ->
                if (index == 0) moveTo(0f, value)
                else lineTo(index.toFloat(), value)
            }
        }
    }

    Canvas(modifier = Modifier.fillMaxSize()) {
        drawPath(path, color = Color.Blue, style = Stroke(2.dp.toPx()))
    }
}
```

---

### KEY TAKEAWAYS

1. **Canvas** provides DrawScope for custom drawing
2. **DrawScope** has functions for shapes, paths, text, images
3. **Path** allows complex custom shapes with bezier curves
4. **Brushes** enable gradients (linear, radial, sweep)
5. **BlendModes** control how layers composite
6. **Transformations** (translate, rotate, scale) modify drawing
7. **Clipping** restricts drawing to specific regions
8. **graphicsLayer** for hardware-accelerated transforms
9. **drawBehind** more efficient than Canvas for simple cases
10. **Cache** paths and calculations with remember

---

## Russian Version

### Постановка задачи

Jetpack Compose предоставляет мощные Canvas API для кастомного рисования и графики. Понимание работы Canvas, DrawScope и graphicsLayer критично для создания кастомных UI компонентов, графиков, игр и сложных анимаций.

**Вопрос:** Как работает Canvas в Jetpack Compose? Что такое DrawScope? Как рисовать фигуры, пути, текст и изображения? Какие есть соображения производительности?

### Ключевые выводы

1. **Canvas** предоставляет DrawScope для кастомного рисования
2. **DrawScope** имеет функции для фигур, путей, текста, изображений
3. **Path** позволяет создавать сложные фигуры с кривыми Безье
4. **Brushes** обеспечивают градиенты (линейный, радиальный, угловой)
5. **BlendModes** контролируют композицию слоёв
6. **Трансформации** (translate, rotate, scale) модифицируют рисование
7. **Clipping** ограничивает рисование определёнными регионами
8. **graphicsLayer** для аппаратно-ускоренных трансформаций
9. **drawBehind** эффективнее Canvas для простых случаев
10. **Кэшируйте** пути и вычисления с remember

## Follow-ups

1. How does Canvas performance compare to Android View system?
2. What is the difference between Canvas and graphicsLayer?
3. How do you implement custom gestures with Canvas?
4. What are the best practices for drawing animations?
5. How do you optimize Canvas performance for 60fps?
6. What is RenderEffect and how does it work?
7. How do you implement zoom and pan for Canvas?
8. What are the limitations of Canvas in Compose?
9. How do you test Canvas drawing code?
10. What is the relationship between Canvas and Modifier.drawWithCache?

---

## Related Questions

### Prerequisites (Easier)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Compose, Jetpack
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose, Jetpack
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Compose, Jetpack

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-side-effects-advanced--jetpack-compose--hard]] - Compose, Jetpack

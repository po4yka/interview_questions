---
id: "20251015082237478"
title: "Compose Gesture Detection / Обнаружение жестов Compose"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - jetpack-compose
  - gestures
  - pointer-input
  - drag-swipe
  - touch-events
---
# Gesture Detection and PointerInput

# Question (EN)
> Implement a custom draggable component with velocity tracking. How does Modifier.pointerInput work?

# Вопрос (RU)
> Реализуйте пользовательский перетаскиваемый компонент с отслеживанием скорости. Как работает Modifier.pointerInput?

---

## Answer (EN)

**Modifier.pointerInput** is Compose's low-level API for handling touch events and gestures. It provides access to raw pointer events and includes higher-level gesture detectors.

---

### Basic Gesture Detection

Compose provides built-in gesture detectors:

```kotlin
@Composable
fun BasicGestures() {
    var tapCount by remember { mutableStateOf(0) }
    var longPressCount by remember { mutableStateOf(0) }
    var doubleTapCount by remember { mutableStateOf(0) }

    Box(
        modifier = Modifier
            .size(200.dp)
            .background(Color.Blue)
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { tapCount++ },
                    onLongPress = { longPressCount++ },
                    onDoubleTap = { doubleTapCount++ },
                    onPress = { /* press down */ }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("Taps: $tapCount", color = Color.White)
            Text("Long: $longPressCount", color = Color.White)
            Text("Double: $doubleTapCount", color = Color.White)
        }
    }
}
```

---

### Custom Draggable Component with Velocity

```kotlin
@Composable
fun DraggableBox() {
    var offsetX by remember { mutableStateOf(0f) }
    var offsetY by remember { mutableStateOf(0f) }
    val velocityTracker = remember { VelocityTracker() }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragStart = { offset ->
                        Log.d("Drag", "Started at $offset")
                    },
                    onDragEnd = {
                        val velocity = velocityTracker.calculateVelocity()
                        Log.d(
                            "Drag",
                            "Ended with velocity: ${velocity.x}, ${velocity.y}"
                        )
                    },
                    onDragCancel = {
                        Log.d("Drag", "Cancelled")
                    },
                    onDrag = { change, dragAmount ->
                        change.consume()
                        offsetX += dragAmount.x
                        offsetY += dragAmount.y

                        // Track velocity
                        velocityTracker.addPosition(
                            change.uptimeMillis,
                            change.position
                        )
                    }
                )
            }
    ) {
        Box(
            modifier = Modifier
                .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
                .size(100.dp)
                .background(Color.Red, CircleShape)
        )
    }
}
```

---

### Advanced: Draggable with Fling

```kotlin
@Composable
fun DraggableWithFling() {
    var offsetX by remember { mutableStateOf(0f) }
    var offsetY by remember { mutableStateOf(0f) }
    val animatable = remember { Animatable(Offset(0f, 0f), Offset.VectorConverter) }

    LaunchedEffect(offsetX, offsetY) {
        animatable.snapTo(Offset(offsetX, offsetY))
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                var velocity = Velocity.Zero

                detectDragGestures(
                    onDragEnd = {
                        // Fling animation with decay
                        launch {
                            val decay = exponentialDecay<Offset>(
                                frictionMultiplier = 1f
                            )

                            animatable.animateDecay(
                                initialVelocity = Offset(velocity.x, velocity.y),
                                animationSpec = decay
                            ) {
                                // Update position during animation
                                offsetX = value.x
                                offsetY = value.y
                            }
                        }
                    },
                    onDrag = { change, dragAmount ->
                        change.consume()

                        // Update velocity
                        velocity = change.velocity

                        // Update position
                        offsetX += dragAmount.x
                        offsetY += dragAmount.y
                    }
                )
            }
    ) {
        Box(
            modifier = Modifier
                .offset {
                    IntOffset(
                        animatable.value.x.roundToInt(),
                        animatable.value.y.roundToInt()
                    )
                }
                .size(80.dp)
                .background(Color.Green, CircleShape)
        )
    }
}
```

---

### Swipe to Dismiss

```kotlin
@Composable
fun SwipeToDissmissItem(
    onDismiss: () -> Unit,
    content: @Composable () -> Unit
) {
    var offsetX by remember { mutableStateOf(0f) }
    val density = LocalDensity.current
    val dismissThreshold = with(density) { 200.dp.toPx() }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .offset { IntOffset(offsetX.roundToInt(), 0) }
            .pointerInput(Unit) {
                detectHorizontalDragGestures(
                    onDragEnd = {
                        if (abs(offsetX) > dismissThreshold) {
                            onDismiss()
                        } else {
                            // Snap back
                            offsetX = 0f
                        }
                    },
                    onHorizontalDrag = { change, dragAmount ->
                        change.consume()
                        offsetX += dragAmount
                    }
                )
            }
    ) {
        // Background (revealed when swiping)
        Box(
            modifier = Modifier
                .matchParentSize()
                .background(Color.Red),
            contentAlignment = Alignment.CenterEnd
        ) {
            Icon(
                Icons.Default.Delete,
                "Delete",
                modifier = Modifier.padding(16.dp),
                tint = Color.White
            )
        }

        // Content
        Box(modifier = Modifier.background(Color.White)) {
            content()
        }
    }
}
```

---

### Multi-Touch: Zoom and Pan

```kotlin
@Composable
fun ZoomableImage(imageUrl: String) {
    var scale by remember { mutableStateOf(1f) }
    var offsetX by remember { mutableStateOf(0f) }
    var offsetY by remember { mutableStateOf(0f) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTransformGestures { _, pan, zoom, _ ->
                    scale = (scale * zoom).coerceIn(1f, 5f)
                    offsetX += pan.x
                    offsetY += pan.y
                }
            }
    ) {
        AsyncImage(
            model = imageUrl,
            contentDescription = null,
            modifier = Modifier
                .fillMaxSize()
                .graphicsLayer {
                    scaleX = scale
                    scaleY = scale
                    translationX = offsetX
                    translationY = offsetY
                }
        )
    }
}
```

---

### Custom Gesture: Long Press Drag

```kotlin
@Composable
fun LongPressDraggable() {
    var offsetX by remember { mutableStateOf(0f) }
    var offsetY by remember { mutableStateOf(0f) }
    var isDragging by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectDragGesturesAfterLongPress(
                    onDragStart = { offset ->
                        isDragging = true
                    },
                    onDragEnd = {
                        isDragging = false
                    },
                    onDragCancel = {
                        isDragging = false
                    },
                    onDrag = { change, dragAmount ->
                        change.consume()
                        offsetX += dragAmount.x
                        offsetY += dragAmount.y
                    }
                )
            }
    ) {
        Box(
            modifier = Modifier
                .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
                .size(100.dp)
                .background(
                    if (isDragging) Color.Green else Color.Blue,
                    CircleShape
                )
        )
    }
}
```

---

### Raw PointerInput Events

For complete control, handle raw pointer events:

```kotlin
@Composable
fun RawPointerInput() {
    val pointers = remember { mutableStateListOf<Offset>() }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.LightGray)
            .pointerInput(Unit) {
                awaitPointerEventScope {
                    while (true) {
                        val event = awaitPointerEvent()

                        event.changes.forEach { change ->
                            when (change.type) {
                                PointerType.Touch -> {
                                    if (change.pressed) {
                                        pointers.add(change.position)
                                    }
                                }
                            }
                            change.consume()
                        }

                        // Keep only last 100 points
                        if (pointers.size > 100) {
                            pointers.removeAt(0)
                        }
                    }
                }
            }
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            pointers.forEachIndexed { index, offset ->
                if (index > 0) {
                    val prev = pointers[index - 1]
                    drawLine(
                        color = Color.Black,
                        start = prev,
                        end = offset,
                        strokeWidth = 5f,
                        cap = StrokeCap.Round
                    )
                }
            }
        }
    }
}
```

---

### Gesture Propagation and Consumption

```kotlin
@Composable
fun GesturePropagation() {
    Box(
        modifier = Modifier
            .size(300.dp)
            .background(Color.Red)
            .pointerInput(Unit) {
                detectTapGestures {
                    Log.d("Gesture", "Outer box tapped")
                }
            }
    ) {
        Box(
            modifier = Modifier
                .size(150.dp)
                .align(Alignment.Center)
                .background(Color.Blue)
                .pointerInput(Unit) {
                    detectTapGestures(
                        onTap = { offset ->
                            Log.d("Gesture", "Inner box tapped at $offset")
                            // Event is consumed, won't reach outer box
                        }
                    )
                }
        )
    }
}
```

---

### Best Practices

**1. Use appropriate gesture detectors:**

```kotlin
//  DO: Use built-in detectors
.pointerInput(Unit) {
    detectTapGestures { /* ... */ }
    detectDragGestures { /* ... */ }
}

//  DON'T: Roll your own unless necessary
```

**2. Remember to consume events:**

```kotlin
//  DO: Consume to prevent propagation
onDrag = { change, dragAmount ->
    change.consume()
    // handle drag
}
```

**3. Use keys for pointer input:**

```kotlin
//  DO: Reset gesture when key changes
.pointerInput(itemId) {
    detectTapGestures { /* ... */ }
}
```

---

## Ответ (RU)

**Modifier.pointerInput** — это низкоуровневый API Compose для обработки событий касания и жестов. Он предоставляет доступ к сырым событиям указателя и включает детекторы жестов высокого уровня.

### Основное обнаружение жестов

Compose предоставляет встроенные детекторы жестов: `detectTapGestures`, `detectDragGestures`, `detectTransformGestures`.

### Пользовательский перетаскиваемый компонент

Можно создать кастомный компонент с отслеживанием скорости используя `VelocityTracker` и обработку событий перетаскивания.

### Мультитач: Масштабирование и панорамирование

Используйте `detectTransformGestures` для обработки жестов масштабирования, поворота и панорамирования одновременно.

### Лучшие практики

1. Используйте подходящие детекторы жестов
2. Не забывайте потреблять события
3. Используйте ключи для pointer input
4. Учитывайте производительность при сложных жестах

Правильное использование pointerInput позволяет создавать отзывчивые интерактивные UI компоненты.


---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView in Compose
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations


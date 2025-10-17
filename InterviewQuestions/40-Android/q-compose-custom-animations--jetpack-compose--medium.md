---
id: 20251012-1227101
title: "Compose Custom Animations / Кастомные анимации Compose"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: [compose, animations, animatable, spring-animations, animation-specs, android/jetpack-compose, android/animations, difficulty/medium]
moc: moc-android
related:   - q-jetpack-compose-basics--android--medium
  - q-how-does-jetpack-compose-work--android--medium
  - q-what-are-the-most-important-components-of-compose--android--medium
  - q-how-to-create-list-like-recyclerview-in-compose--android--medium
  - q-mutable-state-compose--android--medium
  - q-remember-vs-remembersaveable-compose--android--medium
  - q-compose-stability-skippability--jetpack-compose--hard
  - q-stable-classes-compose--android--hard
  - q-stable-annotation-compose--android--hard
subtopics: [jetpack-compose, animations]
---
# Custom Animations with Animatable and animate*AsState

# Question (EN)
> How do you create custom animations using Animatable and animate*AsState? Explain spring specifications.

# Вопрос (RU)
> Как создавать пользовательские анимации используя Animatable и animate*AsState? Объясните спецификации пружин (spring).

---

## Answer (EN)

Compose provides several APIs for creating animations. **animate*AsState** is declarative and simple, while **Animatable** gives you imperative control over animations. **Spring specifications** provide physics-based natural motion.

---

### animate*AsState APIs

These are the simplest animation APIs - declare the target value, and Compose animates to it:

```kotlin
@Composable
fun AnimateAsStateExample() {
    var expanded by remember { mutableStateOf(false) }

    // Animate size
    val size by animateDpAsState(
        targetValue = if (expanded) 200.dp else 100.dp,
        label = "size"
    )

    // Animate color
    val color by animateColorAsState(
        targetValue = if (expanded) Color.Red else Color.Blue,
        label = "color"
    )

    // Animate float
    val alpha by animateFloatAsState(
        targetValue = if (expanded) 1f else 0.5f,
        label = "alpha"
    )

    Box(
        modifier = Modifier
            .size(size)
            .background(color)
            .alpha(alpha)
            .clickable { expanded = !expanded }
    )
}
```

**Available variants:**
- `animateFloatAsState` - For Float values
- `animateDpAsState` - For Dp (density-independent pixels)
- `animateColorAsState` - For Color
- `animateIntAsState` - For Int
- `animateOffsetAsState` - For Offset
- `animateSizeAsState` - For Size
- `animateRectAsState` - For Rect
- `animateIntOffsetAsState` - For IntOffset

---

### Custom AnimationSpec

Control the animation timing and behavior:

```kotlin
@Composable
fun CustomAnimationSpec() {
    var toggled by remember { mutableStateOf(false) }

    // Tween: Linear interpolation over duration
    val tweenValue by animateFloatAsState(
        targetValue = if (toggled) 1f else 0f,
        animationSpec = tween(
            durationMillis = 1000,
            delayMillis = 100,
            easing = FastOutSlowInEasing
        ),
        label = "tween"
    )

    // Spring: Physics-based motion
    val springValue by animateFloatAsState(
        targetValue = if (toggled) 1f else 0f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "spring"
    )

    // Keyframes: Define specific values at specific times
    val keyframeValue by animateFloatAsState(
        targetValue = if (toggled) 1f else 0f,
        animationSpec = keyframes {
            durationMillis = 1000
            0f at 0
            0.8f at 500 using FastOutSlowInEasing
            0.6f at 700
            1f at 1000
        },
        label = "keyframes"
    )

    // Repeatable: Repeat animation
    val repeatValue by animateFloatAsState(
        targetValue = if (toggled) 1f else 0f,
        animationSpec = repeatable(
            iterations = 3,
            animation = tween(500),
            repeatMode = RepeatMode.Reverse
        ),
        label = "repeat"
    )

    // Snap: Instant change (no animation)
    val snapValue by animateFloatAsState(
        targetValue = if (toggled) 1f else 0f,
        animationSpec = snap(delayMillis = 100),
        label = "snap"
    )

    Button(onClick = { toggled = !toggled }) {
        Text("Toggle")
    }
}
```

---

### Animatable - Imperative Animations

**Animatable** provides low-level control for imperative animations:

```kotlin
@Composable
fun AnimatableExample() {
    val color = remember { Animatable(Color.Blue) }

    LaunchedEffect(Unit) {
        // Sequential animations
        color.animateTo(Color.Red, animationSpec = tween(1000))
        color.animateTo(Color.Green, animationSpec = tween(1000))
        color.animateTo(Color.Blue, animationSpec = tween(1000))
    }

    Box(
        modifier = Modifier
            .size(100.dp)
            .background(color.value)
    )
}
```

**Key features:**
- Suspend functions - run in coroutines
- Sequential animations
- Can be interrupted and resumed
- Manual control over animation lifecycle

---

### Animatable Advanced Usage

**1. Continuous animation loop:**

```kotlin
@Composable
fun PulsingCircle() {
    val scale = remember { Animatable(1f) }

    LaunchedEffect(Unit) {
        while (true) {
            scale.animateTo(
                targetValue = 1.3f,
                animationSpec = tween(500)
            )
            scale.animateTo(
                targetValue = 1f,
                animationSpec = tween(500)
            )
        }
    }

    Box(
        modifier = Modifier
            .size(100.dp)
            .scale(scale.value)
            .background(Color.Red, CircleShape)
    )
}
```

---

**2. Velocity-based animation:**

```kotlin
@Composable
fun VelocityAnimation() {
    var offset by remember { mutableStateOf(0f) }
    val animatable = remember { Animatable(0f) }

    LaunchedEffect(offset) {
        animatable.animateTo(
            targetValue = offset,
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioLowBouncy,
                stiffness = Spring.StiffnessLow
            ),
            // Start with existing velocity
            initialVelocity = animatable.velocity
        )
    }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(100.dp)
            .pointerInput(Unit) {
                detectDragGestures { _, dragAmount ->
                    offset += dragAmount.x
                }
            }
    ) {
        Box(
            modifier = Modifier
                .offset { IntOffset(animatable.value.roundToInt(), 0) }
                .size(50.dp)
                .background(Color.Blue, CircleShape)
        )
    }
}
```

---

**3. Interrupting animations:**

```kotlin
@Composable
fun InterruptibleAnimation() {
    val animatable = remember { Animatable(0f) }
    var targetColor by remember { mutableStateOf(Color.Red) }

    LaunchedEffect(targetColor) {
        // Previous animation is automatically interrupted
        animatable.animateTo(
            if (targetColor == Color.Red) 0f else 1f,
            animationSpec = spring()
        )
    }

    Column {
        Box(
            modifier = Modifier
                .size(100.dp)
                .background(
                    lerp(Color.Red, Color.Blue, animatable.value)
                )
        )

        Button(onClick = {
            targetColor = if (targetColor == Color.Red) Color.Blue else Color.Red
        }) {
            Text("Change Color")
        }
    }
}
```

---

**4. animateDecay - Fling animations:**

```kotlin
@Composable
fun FlingAnimation() {
    val offset = remember { Animatable(0f) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragEnd = {
                        // Fling with decay
                        launch {
                            offset.animateDecay(
                                initialVelocity = offset.velocity,
                                animationSpec = exponentialDecay()
                            )
                        }
                    },
                    onDrag = { _, dragAmount ->
                        launch {
                            offset.snapTo(offset.value + dragAmount.x)
                        }
                    }
                )
            }
    ) {
        Box(
            modifier = Modifier
                .offset { IntOffset(offset.value.roundToInt(), 0) }
                .size(80.dp)
                .background(Color.Green, CircleShape)
        )
    }
}
```

---

### Spring Animations

Springs provide **physics-based** natural motion that feels organic:

```kotlin
@Composable
fun SpringExamples() {
    var expanded by remember { mutableStateOf(false) }

    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        // No bounce (critically damped)
        val noBounce by animateFloatAsState(
            if (expanded) 200f else 50f,
            spring(
                dampingRatio = Spring.DampingRatioNoBouncy,
                stiffness = Spring.StiffnessMedium
            )
        )

        // Low bounce
        val lowBounce by animateFloatAsState(
            if (expanded) 200f else 50f,
            spring(
                dampingRatio = Spring.DampingRatioLowBouncy,
                stiffness = Spring.StiffnessMedium
            )
        )

        // Medium bounce
        val mediumBounce by animateFloatAsState(
            if (expanded) 200f else 50f,
            spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessMedium
            )
        )

        // High bounce
        val highBounce by animateFloatAsState(
            if (expanded) 200f else 50f,
            spring(
                dampingRatio = Spring.DampingRatioHighBouncy,
                stiffness = Spring.StiffnessMedium
            )
        )

        Box(
            Modifier
                .size(noBounce.dp, 50.dp)
                .background(Color.Red)
        )
        Box(
            Modifier
                .size(lowBounce.dp, 50.dp)
                .background(Color.Green)
        )
        Box(
            Modifier
                .size(mediumBounce.dp, 50.dp)
                .background(Color.Blue)
        )
        Box(
            Modifier
                .size(highBounce.dp, 50.dp)
                .background(Color.Magenta)
        )

        Button(onClick = { expanded = !expanded }) {
            Text("Toggle")
        }
    }
}
```

---

### Spring Parameters

**Damping Ratio** - Controls bounce:

```kotlin
// No bounce - smooth stop
Spring.DampingRatioNoBouncy = 1f

// Subtle bounce
Spring.DampingRatioLowBouncy = 0.75f

// Moderate bounce
Spring.DampingRatioMediumBouncy = 0.5f

// Very bouncy
Spring.DampingRatioHighBouncy = 0.2f
```

**Stiffness** - Controls speed:

```kotlin
// Very slow
Spring.StiffnessVeryLow = 50f

// Slow
Spring.StiffnessLow = 200f

// Medium (default)
Spring.StiffnessMedium = 400f

// Fast
Spring.StiffnessHigh = 1500f
```

---

### Real-World Example: Like Button

```kotlin
@Composable
fun LikeButton() {
    var liked by remember { mutableStateOf(false) }
    val scale = remember { Animatable(1f) }

    LaunchedEffect(liked) {
        if (liked) {
            // Pop animation when liked
            scale.animateTo(
                targetValue = 1.4f,
                animationSpec = spring(
                    dampingRatio = Spring.DampingRatioMediumBouncy,
                    stiffness = Spring.StiffnessHigh
                )
            )
            scale.animateTo(
                targetValue = 1f,
                animationSpec = spring(
                    dampingRatio = Spring.DampingRatioLowBouncy,
                    stiffness = Spring.StiffnessMedium
                )
            )
        }
    }

    val color by animateColorAsState(
        targetValue = if (liked) Color.Red else Color.Gray,
        animationSpec = tween(200)
    )

    IconButton(onClick = { liked = !liked }) {
        Icon(
            imageVector = if (liked) Icons.Filled.Favorite else Icons.Outlined.FavoriteBorder,
            contentDescription = "Like",
            tint = color,
            modifier = Modifier.scale(scale.value)
        )
    }
}
```

---

### updateTransition for Coordinated Animations

When you need multiple properties to animate together:

```kotlin
@Composable
fun CoordinatedAnimation() {
    var expanded by remember { mutableStateOf(false) }

    val transition = updateTransition(
        targetState = expanded,
        label = "expansion"
    )

    val size by transition.animateDp(
        transitionSpec = { spring(stiffness = Spring.StiffnessLow) },
        label = "size"
    ) { isExpanded ->
        if (isExpanded) 200.dp else 100.dp
    }

    val color by transition.animateColor(
        transitionSpec = { tween(500) },
        label = "color"
    ) { isExpanded ->
        if (isExpanded) Color.Red else Color.Blue
    }

    val corner by transition.animateDp(
        transitionSpec = { spring(dampingRatio = Spring.DampingRatioHighBouncy) },
        label = "corner"
    ) { isExpanded ->
        if (isExpanded) 50.dp else 0.dp
    }

    Box(
        modifier = Modifier
            .size(size)
            .background(color, RoundedCornerShape(corner))
            .clickable { expanded = !expanded }
    )
}
```

---

### InfiniteTransition for Continuous Animations

```kotlin
@Composable
fun LoadingIndicator() {
    val infiniteTransition = rememberInfiniteTransition(label = "loading")

    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "rotation"
    )

    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )

    Icon(
        Icons.Default.Refresh,
        contentDescription = "Loading",
        modifier = Modifier
            .rotate(rotation)
            .alpha(alpha)
    )
}
```

---

### Best Practices

**1. Choose the right API:**

```kotlin
//  Simple state-driven: animate*AsState
val size by animateDpAsState(if (expanded) 100.dp else 50.dp)

//  Sequential/complex: Animatable
LaunchedEffect(key) {
    animatable.animateTo(0.5f)
    animatable.animateTo(1f)
}

//  Coordinated multiple properties: updateTransition
val transition = updateTransition(state)
val size by transition.animateDp { ... }
val color by transition.animateColor { ... }
```

**2. Use springs for natural motion:**

```kotlin
//  DO: Springs feel natural
spring(
    dampingRatio = Spring.DampingRatioMediumBouncy,
    stiffness = Spring.StiffnessMedium
)

//  Consider: Tween for precise timing
tween(durationMillis = 300)
```

**3. Consider performance:**

```kotlin
//  Efficient: Animate layout-independent properties
.scale(scale)
.alpha(alpha)
.rotation(degrees)

//  Expensive: Layout-dependent animations
.size(animatedSize) // Triggers layout
.padding(animatedPadding) // Triggers layout
```

---

## Ответ (RU)

Compose предоставляет несколько API для создания анимаций. **animate*AsState** декларативен и прост, в то время как **Animatable** дает императивный контроль над анимациями. **Spring спецификации** обеспечивают физически-обоснованное естественное движение.

### animate*AsState APIs

Это простейшие API анимации - объявите целевое значение, и Compose анимирует к нему.

### Animatable - Императивные анимации

**Animatable** предоставляет низкоуровневый контроль для императивных анимаций с ключевыми возможностями:
- Suspend функции - выполняются в корутинах
- Последовательные анимации
- Могут быть прерваны и возобновлены
- Ручной контроль жизненного цикла анимации

### Пружинные анимации

Пружины обеспечивают **физически-обоснованное** естественное движение:

**Damping Ratio** - Контролирует отскок:
- `DampingRatioNoBouncy` - без отскока
- `DampingRatioLowBouncy` - слабый отскок
- `DampingRatioMediumBouncy` - средний отскок
- `DampingRatioHighBouncy` - сильный отскок

**Stiffness** - Контролирует скорость:
- `StiffnessVeryLow` - очень медленно
- `StiffnessLow` - медленно
- `StiffnessMedium` - средне
- `StiffnessHigh` - быстро

### Лучшие практики

1. Выбирайте правильный API
2. Используйте пружины для естественного движения
3. Учитывайте производительность
4. Анимируйте свойства, не зависящие от layout

Правильное использование этих API создает плавные, естественные анимации в Compose.


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


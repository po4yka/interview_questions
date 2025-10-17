---
id: "20251015082237575"
title: "Material3 Motion Transitions / Движение и переходы Material3"
topic: ui-ux-accessibility
difficulty: medium
status: draft
created: 2025-10-13
tags: [design, material3, animation, transitions, motion, difficulty/medium]
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-ui-ux-accessibility
related_questions: []
subtopics: [material-design, ui-animation]
---
# Material 3 Motion and Transitions

# Question (EN)
> What are the key motion principles in Material 3? Explain shared element transitions, predictive back gesture animations, and implementing smooth transitions between composables following Material Design guidelines.

# Вопрос (RU)
> Каковы ключевые принципы движения в Material 3? Объясните shared element transitions, анимации предиктивного жеста назад и реализацию плавных переходов между composables в соответствии с рекомендациями Material Design.

---

## Answer (EN)

**Material 3 motion** creates meaningful, beautiful transitions that guide users through your app. Motion provides clarity, efficiency, and personality.

### Material 3 Motion Principles

**1. Informative** - Guides attention and communicates relationships
**2. Focused** - Guides to a single focal point
**3. Expressive** - Adds personality and polish
**4. Practical** - Enhances usability without unnecessary flourish

---

### Motion Durations

Material 3 defines standard durations for consistency:

| Duration | Use Case | Example |
|----------|----------|---------|
| **100ms** | Simple transitions | Icon state change |
| **200ms** | Small component transitions | Checkbox, switch |
| **300ms** | Standard transitions | Button, card |
| **400ms** | Complex transitions | Screen transitions |
| **500ms+** | Emphasized transitions | Large expansions |

**Implementation:**

```kotlin
// Standard duration constants
object MotionTokens {
    const val DurationShort1 = 50
    const val DurationShort2 = 100
    const val DurationShort3 = 150
    const val DurationShort4 = 200
    const val DurationMedium1 = 250
    const val DurationMedium2 = 300
    const val DurationMedium3 = 350
    const val DurationMedium4 = 400
    const val DurationLong1 = 450
    const val DurationLong2 = 500
    const val DurationLong3 = 550
    const val DurationLong4 = 600
}

// Usage
animate()
    .alpha(0f)
    .setDuration(MotionTokens.DurationMedium2.toLong()) // 300ms
    .start()
```

---

### Easing (Timing Functions)

Material 3 uses specific easing curves:

```kotlin
object EasingTokens {
    // Standard easing (most common)
    val Standard = CubicBezierEasing(0.2f, 0.0f, 0.0f, 1.0f)

    // Emphasized easing (important transitions)
    val Emphasized = CubicBezierEasing(0.2f, 0.0f, 0.0f, 1.0f)
    val EmphasizedDecelerate = CubicBezierEasing(0.05f, 0.7f, 0.1f, 1.0f)
    val EmphasizedAccelerate = CubicBezierEasing(0.3f, 0.0f, 0.8f, 0.15f)

    // Legacy (for compatibility)
    val Legacy = FastOutSlowInEasing
    val LegacyDecelerate = LinearOutSlowInEasing
    val LegacyAccelerate = FastOutLinearInEasing
}

// Usage in Compose
val alpha by animateFloatAsState(
    targetValue = if (visible) 1f else 0f,
    animationSpec = tween(
        durationMillis = 300,
        easing = EasingTokens.Standard
    )
)
```

**When to use:**
- **Standard**: Most animations
- **Emphasized**: Important content entering/leaving
- **Emphasized Decelerate**: Content entering screen
- **Emphasized Accelerate**: Content leaving screen

---

### Basic Transitions

**1. Fade transition:**

```kotlin
@Composable
fun FadeTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(
            animationSpec = tween(
                durationMillis = 300,
                easing = EasingTokens.Standard
            )
        ),
        exit = fadeOut(
            animationSpec = tween(
                durationMillis = 200,
                easing = EasingTokens.Standard
            )
        )
    ) {
        content()
    }
}
```

**2. Slide transition:**

```kotlin
@Composable
fun SlideTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = slideInVertically(
            initialOffsetY = { it }, // Start from bottom
            animationSpec = tween(
                durationMillis = 300,
                easing = EasingTokens.EmphasizedDecelerate
            )
        ),
        exit = slideOutVertically(
            targetOffsetY = { it },
            animationSpec = tween(
                durationMillis = 200,
                easing = EasingTokens.EmphasizedAccelerate
            )
        )
    ) {
        content()
    }
}
```

**3. Scale transition:**

```kotlin
@Composable
fun ScaleTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = scaleIn(
            initialScale = 0.8f,
            animationSpec = tween(
                durationMillis = 300,
                easing = EasingTokens.EmphasizedDecelerate
            )
        ) + fadeIn(),
        exit = scaleOut(
            targetScale = 0.8f,
            animationSpec = tween(
                durationMillis = 200,
                easing = EasingTokens.EmphasizedAccelerate
            )
        ) + fadeOut()
    ) {
        content()
    }
}
```

---

### Container Transform

Container transform creates smooth morphing animation between containers.

```kotlin
@Composable
fun ContainerTransformExample() {
    var expanded by remember { mutableStateOf(false) }

    AnimatedContent(
        targetState = expanded,
        transitionSpec = {
            fadeIn(
                animationSpec = tween(
                    durationMillis = 150,
                    delayMillis = 150,
                    easing = EasingTokens.Standard
                )
            ) togetherWith fadeOut(
                animationSpec = tween(
                    durationMillis = 150,
                    easing = EasingTokens.Standard
                )
            ) using SizeTransform { initialSize, targetSize ->
                tween(
                    durationMillis = 300,
                    easing = EasingTokens.Emphasized
                )
            }
        }
    ) { isExpanded ->
        if (isExpanded) {
            // Expanded state (full screen)
            DetailScreen(onClose = { expanded = false })
        } else {
            // Collapsed state (card)
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(100.dp)
                    .clickable { expanded = true }
            ) {
                Text("Tap to expand", modifier = Modifier.padding(16.dp))
            }
        }
    }
}
```

---

### Shared Element Transitions

**Shared elements** smoothly animate between screens, maintaining continuity.

```kotlin
// Requires Compose 1.6.0+
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedElementExample() {
    var showDetails by remember { mutableStateOf(false) }

    SharedTransitionLayout {
        AnimatedContent(
            targetState = showDetails,
            label = "main content"
        ) { isShowingDetails ->
            if (isShowingDetails) {
                DetailScreen(
                    onBackClick = { showDetails = false },
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this@AnimatedContent
                )
            } else {
                ListScreen(
                    onItemClick = { showDetails = true },
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this@AnimatedContent
                )
            }
        }
    }
}

@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ListScreen(
    onItemClick: () -> Unit,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .sharedElement(
                    state = rememberSharedContentState(key = "item-1"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
                .clickable(onClick = onItemClick)
        ) {
            Row(modifier = Modifier.padding(16.dp)) {
                Image(
                    painter = painterResource(R.drawable.image),
                    contentDescription = null,
                    modifier = Modifier
                        .size(60.dp)
                        .sharedElement(
                            state = rememberSharedContentState(key = "image-1"),
                            animatedVisibilityScope = animatedVisibilityScope
                        )
                )
                Spacer(modifier = Modifier.width(16.dp))
                Text(
                    "Item Title",
                    modifier = Modifier.sharedElement(
                        state = rememberSharedContentState(key = "title-1"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
                )
            }
        }
    }
}

@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun DetailScreen(
    onBackClick: () -> Unit,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .sharedElement(
                    state = rememberSharedContentState(key = "item-1"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
        ) {
            Image(
                painter = painterResource(R.drawable.image),
                contentDescription = null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .sharedElement(
                        state = rememberSharedContentState(key = "image-1"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
            )
            Text(
                "Detail Title",
                style = MaterialTheme.typography.headlineLarge,
                modifier = Modifier
                    .padding(16.dp)
                    .sharedElement(
                        state = rememberSharedContentState(key = "title-1"),
                        animatedVisibilityScope = animatedVisibilityScope
                    )
            )
            Text(
                "Detailed content here...",
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
```

---

### Predictive Back Gesture (Android 13+)

**Predictive back** shows preview of previous screen during back gesture.

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PredictiveBackExample() {
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    // Enable predictive back
    val backCallback = remember {
        object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                scope.launch {
                    if (drawerState.isOpen) {
                        drawerState.close()
                    } else {
                        // Handle back navigation
                    }
                }
            }
        }
    }

    val backDispatcher = LocalOnBackPressedDispatcherOwner.current
        ?.onBackPressedDispatcher

    DisposableEffect(backCallback) {
        backDispatcher?.addCallback(backCallback)
        onDispose {
            backCallback.remove()
        }
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Text("Drawer Content", modifier = Modifier.padding(16.dp))
            }
        }
    ) {
        Scaffold(
            topAppBar = {
                TopAppBar(
                    title = { Text("Predictive Back") },
                    navigationIcon = {
                        IconButton(onClick = {
                            scope.launch { drawerState.open() }
                        }) {
                            Icon(Icons.Filled.Menu, "Menu")
                        }
                    }
                )
            }
        ) { padding ->
            Box(modifier = Modifier.padding(padding)) {
                Text("Main content")
            }
        }
    }
}
```

---

### Navigation Transitions

**NavHost animations:**

```kotlin
@Composable
fun NavigationWithTransitions() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home",
        enterTransition = {
            slideInHorizontally(
                initialOffsetX = { it },
                animationSpec = tween(
                    durationMillis = 300,
                    easing = EasingTokens.EmphasizedDecelerate
                )
            ) + fadeIn(animationSpec = tween(300))
        },
        exitTransition = {
            slideOutHorizontally(
                targetOffsetX = { -it / 2 }, // Slight slide left
                animationSpec = tween(
                    durationMillis = 300,
                    easing = EasingTokens.Standard
                )
            ) + fadeOut(animationSpec = tween(300))
        },
        popEnterTransition = {
            slideInHorizontally(
                initialOffsetX = { -it / 2 },
                animationSpec = tween(300)
            ) + fadeIn(animationSpec = tween(300))
        },
        popExitTransition = {
            slideOutHorizontally(
                targetOffsetX = { it },
                animationSpec = tween(
                    durationMillis = 300,
                    easing = EasingTokens.EmphasizedAccelerate
                )
            ) + fadeOut(animationSpec = tween(300))
        }
    ) {
        composable("home") { HomeScreen(navController) }
        composable("details") { DetailsScreen(navController) }
    }
}
```

---

### List Item Animations

**Animate list additions/removals:**

```kotlin
@Composable
fun AnimatedList(items: List<String>) {
    LazyColumn {
        items(
            items = items,
            key = { it } // Important for correct animations
        ) { item ->
            AnimatedListItem(
                item = item,
                modifier = Modifier.animateItemPlacement(
                    animationSpec = tween(
                        durationMillis = 300,
                        easing = EasingTokens.Emphasized
                    )
                )
            )
        }
    }
}

@Composable
fun AnimatedListItem(item: String, modifier: Modifier = Modifier) {
    var visible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        visible = true
    }

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(tween(300)) + expandVertically(tween(300)),
        exit = fadeOut(tween(200)) + shrinkVertically(tween(200)),
        modifier = modifier
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp)
        ) {
            Text(
                text = item,
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
```

---

### State-Based Animations

**Animate based on state changes:**

```kotlin
@Composable
fun ExpandableCard(title: String, content: String) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .animateContentSize(
                animationSpec = spring(
                    dampingRatio = Spring.DampingRatioMediumBouncy,
                    stiffness = Spring.StiffnessLow
                )
            )
            .clickable { expanded = !expanded }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(title, style = MaterialTheme.typography.titleMedium)

                Icon(
                    imageVector = if (expanded) Icons.Filled.ExpandLess
                                  else Icons.Filled.ExpandMore,
                    contentDescription = if (expanded) "Collapse" else "Expand",
                    modifier = Modifier.rotate(
                        animateFloatAsState(
                            targetValue = if (expanded) 180f else 0f,
                            animationSpec = tween(300)
                        ).value
                    )
                )
            }

            if (expanded) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(content)
            }
        }
    }
}
```

---

### FAB Animation

**Animated FAB with morphing:**

```kotlin
@Composable
fun AnimatedFAB(
    extended: Boolean,
    onClick: () -> Unit
) {
    ExtendedFloatingActionButton(
        onClick = onClick,
        icon = {
            Icon(Icons.Filled.Add, "Add")
        },
        text = {
            AnimatedVisibility(
                visible = extended,
                enter = fadeIn(tween(200, delayMillis = 100)) +
                        expandHorizontally(tween(300)),
                exit = fadeOut(tween(100)) +
                       shrinkHorizontally(tween(200))
            ) {
                Text("Create")
            }
        },
        expanded = extended
    )
}

// Usage with scroll state
@Composable
fun ScreenWithFAB() {
    val listState = rememberLazyListState()
    val expandedFab by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex == 0
        }
    }

    Scaffold(
        floatingActionButton = {
            AnimatedFAB(
                extended = expandedFab,
                onClick = { /* ... */ }
            )
        }
    ) { padding ->
        LazyColumn(state = listState, modifier = Modifier.padding(padding)) {
            items(100) {
                Text("Item $it", modifier = Modifier.padding(16.dp))
            }
        }
    }
}
```

---

### Best Practices

**1. Use standard durations**
```kotlin
//  DO - Use Material durations
animationSpec = tween(durationMillis = 300)

//  DON'T - Random durations
animationSpec = tween(durationMillis = 237)
```

**2. Apply appropriate easing**
```kotlin
//  DO - Emphasized for important transitions
enter = slideInVertically(
    animationSpec = tween(
        durationMillis = 300,
        easing = EasingTokens.EmphasizedDecelerate
    )
)

//  DON'T - Linear easing (feels mechanical)
animationSpec = tween(easing = LinearEasing)
```

**3. Provide keys for list animations**
```kotlin
//  DO
items(items, key = { it.id }) { item ->
    // Content
}

//  DON'T
items(items) { item -> // No key
    // Content
}
```

**4. Respect user preferences**
```kotlin
val scale = Settings.Global.getFloat(
    context.contentResolver,
    Settings.Global.ANIMATOR_DURATION_SCALE,
    1f
)

// Adjust duration based on user preference
val duration = (300 * scale).toInt()
```

**5. Avoid excessive motion**
```kotlin
//  DO - Subtle, meaningful
fadeIn(tween(300))

//  DON'T - Overly complex
fadeIn() + slideIn() + scaleIn() + rotateIn() // Too much!
```

---

### Summary

**Material 3 motion principles:**
- Informative - Guides attention
- Focused - Single focal point
- Expressive - Adds personality
- Practical - Enhances usability

**Standard durations:**
- 100ms - Simple transitions
- 200ms - Small components
- 300ms - Standard transitions
- 400ms - Complex transitions

**Key techniques:**
- `AnimatedVisibility` - Enter/exit transitions
- `AnimatedContent` - Content swapping
- `SharedTransitionLayout` - Shared elements
- `animateContentSize()` - Size changes
- `animateItemPlacement()` - List reordering

**Best practices:**
- Use standard durations
- Apply appropriate easing
- Provide keys for lists
- Respect user preferences
- Avoid excessive motion

---

## Ответ (RU)

**Material 3 motion** создаёт осмысленные, красивые переходы, которые направляют пользователей через ваше приложение.

### Принципы движения Material 3

1. **Informative** - Направляет внимание
2. **Focused** - Направляет к одной фокальной точке
3. **Expressive** - Добавляет индивидуальность
4. **Practical** - Улучшает юзабилити

### Длительность анимаций

| Длительность | Случай использования |
|--------------|---------------------|
| **100ms** | Простые переходы |
| **200ms** | Маленькие компоненты |
| **300ms** | Стандартные переходы |
| **400ms** | Сложные переходы |
| **500ms+** | Подчёркнутые переходы |

### Основные переходы

**Fade transition:**
```kotlin
AnimatedVisibility(
    visible = visible,
    enter = fadeIn(tween(300)),
    exit = fadeOut(tween(200))
) {
    content()
}
```

**Slide transition:**
```kotlin
AnimatedVisibility(
    visible = visible,
    enter = slideInVertically(tween(300)),
    exit = slideOutVertically(tween(200))
) {
    content()
}
```

### Shared Element Transitions

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedElementExample() {
    SharedTransitionLayout {
        AnimatedContent(targetState = showDetails) { isShowingDetails ->
            if (isShowingDetails) {
                DetailScreen(/* ... */)
            } else {
                ListScreen(/* ... */)
            }
        }
    }
}
```

### Лучшие практики

1. Используйте стандартные длительности
2. Применяйте appropriate easing
3. Предоставляйте ключи для списков
4. Уважайте пользовательские предпочтения
5. Избегайте излишнего движения

### Ключевые техники

- `AnimatedVisibility` - Переходы входа/выхода
- `AnimatedContent` - Замена содержимого
- `SharedTransitionLayout` - Shared elements
- `animateContentSize()` - Изменения размера
- `animateItemPlacement()` - Переупорядочивание списков

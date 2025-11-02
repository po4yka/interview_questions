---
id: ui-001
title: "Material3 Motion Transitions / Движение и переходы Material3"
aliases: ["Material3 Motion Transitions", "Движение и переходы Material3"]
topic: ui-ux-accessibility
subtopics: [material-design, ui-animation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-ui-ux-accessibility
related: [q-jetpack-compose-basics--android--medium, q-navigation-methods-in-android--android--medium]
created: 2025-10-13
updated: 2025-10-28
sources: []
tags: [animation, design, difficulty/medium, material3, motion, transitions]
date created: Tuesday, October 28th 2025, 9:36:31 pm
date modified: Saturday, November 1st 2025, 5:43:29 pm
---

# Вопрос (RU)

> Каковы ключевые принципы движения в Material 3? Объясните shared element transitions, анимации предиктивного жеста назад и реализацию плавных переходов между composables в соответствии с рекомендациями Material Design.

# Question (EN)

> What are the key motion principles in Material 3? Explain shared element transitions, predictive back gesture animations, and implementing smooth transitions between composables following Material Design guidelines.

---

## Ответ (RU)

**Material 3 motion** создаёт осмысленные переходы, которые направляют пользователей. Движение обеспечивает ясность, эффективность и индивидуальность.

### Принципы Движения Material 3

1. **Informative** - Направляет внимание и показывает связи между элементами
2. **Focused** - Направляет к одной фокальной точке, избегая отвлечения
3. **Expressive** - Добавляет индивидуальность и полированность
4. **Practical** - Улучшает юзабилити без излишеств

### Стандартные Длительности

Material 3 определяет стандартные длительности для согласованности:

| Длительность | Случай использования | Пример |
|--------------|----------------------|--------|
| **100ms** | Простые переходы | Смена иконки |
| **200ms** | Маленькие компоненты | Checkbox, switch |
| **300ms** | Стандартные переходы | Button, card |
| **400ms** | Сложные переходы | Переходы между экранами |
| **500ms+** | Подчёркнутые переходы | Большие расширения |

### Базовые Переходы

**Fade transition:**

```kotlin
// ✅ Правильно: стандартные длительности и easing
@Composable
fun FadeTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(tween(300, easing = LinearOutSlowInEasing)),
        exit = fadeOut(tween(200))
    ) { content() }
}
```

**Slide transition:**

```kotlin
// ✅ Правильно: используем emphasized easing для входа
@Composable
fun SlideTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = slideInVertically(
            initialOffsetY = { it },
            animationSpec = tween(300, easing = FastOutSlowInEasing)
        ),
        exit = slideOutVertically(
            targetOffsetY = { it },
            animationSpec = tween(200)
        )
    ) { content() }
}
```

### Shared Element Transitions

Shared elements плавно анимируются между экранами, обеспечивая непрерывность.

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedElementExample() {
    var showDetails by remember { mutableStateOf(false) }

    SharedTransitionLayout {
        AnimatedContent(targetState = showDetails) { isShowingDetails ->
            if (isShowingDetails) {
                DetailScreen(
                    onBack = { showDetails = false },
                    sharedScope = this@SharedTransitionLayout,
                    animatedScope = this@AnimatedContent
                )
            } else {
                ListScreen(
                    onClick = { showDetails = true },
                    sharedScope = this@SharedTransitionLayout,
                    animatedScope = this@AnimatedContent
                )
            }
        }
    }
}

@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ListScreen(
    onClick: () -> Unit,
    sharedScope: SharedTransitionScope,
    animatedScope: AnimatedVisibilityScope
) {
    with(sharedScope) {
        Card(
            modifier = Modifier
                .sharedElement(
                    rememberSharedContentState("item-1"),
                    animatedScope
                )
                .clickable(onClick = onClick)
        ) {
            Row(Modifier.padding(16.dp)) {
                Image(
                    painter = painterResource(R.drawable.image),
                    contentDescription = null,
                    modifier = Modifier
                        .size(60.dp)
                        .sharedElement(
                            rememberSharedContentState("image-1"),
                            animatedScope
                        )
                )
                Text(
                    "Item Title",
                    Modifier.sharedElement(
                        rememberSharedContentState("title-1"),
                        animatedScope
                    )
                )
            }
        }
    }
}
```

### Predictive Back Gesture

Predictive back показывает превью предыдущего экрана во время жеста назад (Android 13+).

```kotlin
// ✅ Правильно: обработка predictive back
@Composable
fun PredictiveBackExample() {
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    val backCallback = remember {
        object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                scope.launch {
                    if (drawerState.isOpen) drawerState.close()
                }
            }
        }
    }

    LocalOnBackPressedDispatcherOwner.current
        ?.onBackPressedDispatcher
        ?.let { dispatcher ->
            DisposableEffect(backCallback) {
                dispatcher.addCallback(backCallback)
                onDispose { backCallback.remove() }
            }
        }

    ModalNavigationDrawer(drawerState = drawerState) {
        // Content
    }
}
```

### Переходы Навигации

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
                animationSpec = tween(300)
            ) + fadeIn(tween(300))
        },
        exitTransition = {
            slideOutHorizontally(
                targetOffsetX = { -it / 2 },
                animationSpec = tween(300)
            ) + fadeOut(tween(300))
        }
    ) {
        composable("home") { HomeScreen(navController) }
        composable("details") { DetailsScreen(navController) }
    }
}
```

### Лучшие Практики

```kotlin
// ✅ Правильно: стандартные длительности
animationSpec = tween(durationMillis = 300)

// ❌ Неправильно: случайные длительности
animationSpec = tween(durationMillis = 237)

// ✅ Правильно: ключи для списков
items(items, key = { it.id }) { item -> /* ... */ }

// ❌ Неправильно: без ключей
items(items) { item -> /* ... */ }

// ✅ Правильно: уважение предпочтений пользователя
val scale = Settings.Global.getFloat(
    context.contentResolver,
    Settings.Global.ANIMATOR_DURATION_SCALE,
    1f
)
val duration = (300 * scale).toInt()
```

---

## Answer (EN)

**Material 3 motion** creates meaningful transitions that guide users through your app. Motion provides clarity, efficiency, and personality.

### Material 3 Motion Principles

1. **Informative** - Guides attention and communicates relationships between elements
2. **Focused** - Guides to a single focal point, avoiding distraction
3. **Expressive** - Adds personality and polish to the experience
4. **Practical** - Enhances usability without unnecessary flourish

### Standard Durations

Material 3 defines standard durations for consistency:

| Duration | Use Case | Example |
|----------|----------|---------|
| **100ms** | Simple transitions | Icon state change |
| **200ms** | Small component transitions | Checkbox, switch |
| **300ms** | Standard transitions | Button, card |
| **400ms** | Complex transitions | Screen transitions |
| **500ms+** | Emphasized transitions | Large expansions |

### Basic Transitions

**Fade transition:**

```kotlin
// ✅ Correct: standard durations and easing
@Composable
fun FadeTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(tween(300, easing = LinearOutSlowInEasing)),
        exit = fadeOut(tween(200))
    ) { content() }
}
```

**Slide transition:**

```kotlin
// ✅ Correct: emphasized easing for entering content
@Composable
fun SlideTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = slideInVertically(
            initialOffsetY = { it },
            animationSpec = tween(300, easing = FastOutSlowInEasing)
        ),
        exit = slideOutVertically(
            targetOffsetY = { it },
            animationSpec = tween(200)
        )
    ) { content() }
}
```

### Shared Element Transitions

Shared elements smoothly animate between screens, maintaining continuity.

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedElementExample() {
    var showDetails by remember { mutableStateOf(false) }

    SharedTransitionLayout {
        AnimatedContent(targetState = showDetails) { isShowingDetails ->
            if (isShowingDetails) {
                DetailScreen(
                    onBack = { showDetails = false },
                    sharedScope = this@SharedTransitionLayout,
                    animatedScope = this@AnimatedContent
                )
            } else {
                ListScreen(
                    onClick = { showDetails = true },
                    sharedScope = this@SharedTransitionLayout,
                    animatedScope = this@AnimatedContent
                )
            }
        }
    }
}

@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ListScreen(
    onClick: () -> Unit,
    sharedScope: SharedTransitionScope,
    animatedScope: AnimatedVisibilityScope
) {
    with(sharedScope) {
        Card(
            modifier = Modifier
                .sharedElement(
                    rememberSharedContentState("item-1"),
                    animatedScope
                )
                .clickable(onClick = onClick)
        ) {
            Row(Modifier.padding(16.dp)) {
                Image(
                    painter = painterResource(R.drawable.image),
                    contentDescription = null,
                    modifier = Modifier
                        .size(60.dp)
                        .sharedElement(
                            rememberSharedContentState("image-1"),
                            animatedScope
                        )
                )
                Text(
                    "Item Title",
                    Modifier.sharedElement(
                        rememberSharedContentState("title-1"),
                        animatedScope
                    )
                )
            }
        }
    }
}
```

### Predictive Back Gesture

Predictive back shows preview of previous screen during back gesture (Android 13+).

```kotlin
// ✅ Correct: handling predictive back
@Composable
fun PredictiveBackExample() {
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    val backCallback = remember {
        object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                scope.launch {
                    if (drawerState.isOpen) drawerState.close()
                }
            }
        }
    }

    LocalOnBackPressedDispatcherOwner.current
        ?.onBackPressedDispatcher
        ?.let { dispatcher ->
            DisposableEffect(backCallback) {
                dispatcher.addCallback(backCallback)
                onDispose { backCallback.remove() }
            }
        }

    ModalNavigationDrawer(drawerState = drawerState) {
        // Content
    }
}
```

### Navigation Transitions

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
                animationSpec = tween(300)
            ) + fadeIn(tween(300))
        },
        exitTransition = {
            slideOutHorizontally(
                targetOffsetX = { -it / 2 },
                animationSpec = tween(300)
            ) + fadeOut(tween(300))
        }
    ) {
        composable("home") { HomeScreen(navController) }
        composable("details") { DetailsScreen(navController) }
    }
}
```

### Best Practices

```kotlin
// ✅ Correct: standard durations
animationSpec = tween(durationMillis = 300)

// ❌ Wrong: random durations
animationSpec = tween(durationMillis = 237)

// ✅ Correct: provide keys for lists
items(items, key = { it.id }) { item -> /* ... */ }

// ❌ Wrong: no keys
items(items) { item -> /* ... */ }

// ✅ Correct: respect user preferences
val scale = Settings.Global.getFloat(
    context.contentResolver,
    Settings.Global.ANIMATOR_DURATION_SCALE,
    1f
)
val duration = (300 * scale).toInt()
```

---

## Follow-ups

- How do you handle animation interruptions when user navigates away mid-transition?
- What's the impact of AnimationSpec choice (tween vs spring) on perceived app performance?
- How do you test shared element transitions with different screen sizes and aspect ratios?
- What accessibility considerations apply to motion and animation timing?
- How do you debug complex animation chains involving multiple composables?

## References

- Material Design Motion Guidelines: https://m3.material.io/styles/motion/overview
- Compose Animation Documentation: https://developer.android.com/jetpack/compose/animation
- Android Developers - Animations: https://developer.android.com/develop/ui/views/animations

## Related Questions

### Prerequisites (Easier)
- [[q-jetpack-compose-basics--android--medium]] - Understanding Compose fundamentals for animations
- Compose state management - State management drives animation triggers

### Related (Same Level)
- [[q-navigation-methods-in-android--android--medium]] - Navigation transitions integration
- Compose lifecycle - Lifecycle-aware animations

### Advanced (Harder)
- Compose performance optimization - Optimizing animation performance
- Custom Compose layouts - Custom layout animations

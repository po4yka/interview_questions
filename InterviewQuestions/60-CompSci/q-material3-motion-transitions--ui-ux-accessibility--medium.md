---
id: ui-001
title: "Material3 Motion Transitions / Движение и переходы Material3"
aliases: ["Material3 Motion Transitions", "Движение и переходы Material3"]
topic: ui-ux-accessibility
subtopics: [ui-animation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-animation, c-animation-framework, q-jetpack-compose-basics--android--medium]
created: 2025-10-13
updated: 2025-11-11
sources: []
tags: [ui-ux-accessibility, ui-animation, difficulty/medium]
---

# Вопрос (RU)

> Каковы ключевые принципы движения в Material 3? Объясните shared element transitions, анимации предиктивного жеста назад и реализацию плавных переходов между composables в соответствии с рекомендациями Material Design.

# Question (EN)

> What are the key motion principles in Material 3? Explain shared element transitions, predictive back gesture animations, and implementing smooth transitions between composables following Material Design guidelines.

---

## Ответ (RU)

**Material 3 motion** создаёт осмысленные переходы, которые направляют пользователей. Движение обеспечивает ясность, эффективность и индивидуальность. См. также [[c-animation]] и [[c-animation-framework]] для общей базы по анимациям.

Важно: нижеуказанные принципы и значения отражают практические рекомендации, совпадающие с духом Material 3, но не являются дословным списком официальных «именованных» принципов.

### Принципы Движения Material 3

1. **Informative (информативность)** — Направляет внимание и показывает связи между элементами.
2. **Focused (фокус)** — Подводит взгляд к важным действиям и состояниям, избегая визуального шума.
3. **Expressive (выразительность)** — Добавляет индивидуальность и плавность, поддерживая бренд и контекст.
4. **Practical (практичность)** — Улучшает юзабилити; анимации краткие, предсказуемые и не мешают пользователю.

### Длительности (рекомендации)

Material Design рекомендует использовать согласованные, краткие анимации. Ниже — типичные значения, а не жёсткие стандарты:

| Длительность | Случай использования         | Пример                      |
|--------------|------------------------------|-----------------------------|
| ≈100ms       | Простые микровзаимодействия  | Смена иконки                |
| ≈200ms       | Малые компоненты             | Checkbox, switch            |
| ≈300ms       | Базовые переходы состояний   | Кнопки, карточки            |
| ≈300–400ms   | Переходы между экранами      | Навигация между destination |
| 400ms+       | Акцентированные переходы     | Крупные раскрытия/expand    |

Ключевая идея — последовательность и соответствие расстоянию/сложности.

### Базовые Переходы (Compose-примеры)

Примеры ниже демонстрируют подходы в Jetpack Compose и соответствуют духу Material 3 (значения и easing можно адаптировать под дизайн-систему).

**Fade transition:**

```kotlin
@Composable
fun FadeTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(animationSpec = tween(300, easing = LinearOutSlowInEasing)),
        exit = fadeOut(animationSpec = tween(200))
    ) {
        content()
    }
}
```

**Slide transition:**

```kotlin
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
    ) {
        content()
    }
}
```

### Shared Element Transitions

Shared elements плавно анимируются между экранами, подчеркивая связь между списком и деталями. В Compose это поддерживается экспериментальными API (`SharedTransitionLayout`, `SharedTransitionScope`) и может отличаться в зависимости от версии библиотеки. Ниже — упрощённый концептуальный пример (может требовать корректировки под конкретную версию Compose):

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedElementExample() {
    var showDetails by remember { mutableStateOf(false) }

    SharedTransitionLayout { sharedTransitionScope ->
        AnimatedContent(targetState = showDetails, label = "sharedTransition") { isShowingDetails ->
            if (isShowingDetails) {
                DetailScreen(
                    onBack = { showDetails = false },
                    sharedScope = sharedTransitionScope,
                    animatedContentScope = this
                )
            } else {
                ListScreen(
                    onClick = { showDetails = true },
                    sharedScope = sharedTransitionScope,
                    animatedContentScope = this
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
    animatedContentScope: AnimatedContentScope
) {
    with(sharedScope) {
        Card(
            modifier = Modifier
                .sharedElement(
                    state = rememberSharedContentState(key = "item-1"),
                    animatedVisibilityScope = animatedContentScope
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
                            state = rememberSharedContentState(key = "image-1"),
                            animatedVisibilityScope = animatedContentScope
                        )
                )
                Text(
                    text = "Item Title",
                    modifier = Modifier.sharedElement(
                        state = rememberSharedContentState(key = "title-1"),
                        animatedVisibilityScope = animatedContentScope
                    )
                )
            }
        }
    }
}
```

(Реальные сигнатуры и имена параметров зависят от версии `compose.animation` с `ExperimentalSharedTransitionApi`; при использовании на собеседовании важно подчеркнуть понимание концепции и необходимость сверяться с актуальной документацией.)

### Predictive Back Gesture

Предиктивный жест "Назад" (Android 13+) показывает предварительный просмотр предыдущего состояния/экрана во время жеста. Полноценная поддержка включает:

- интеграцию с навигацией (NavController / navigation-compose);
- использование системных API для визуализации предиктивного перехода;
- корректную анимацию содержимого в ответ на прогресс жеста.

Ниже — пример обработки back-действия в Compose. Он иллюстрирует кастомную логику (например, закрытие drawer), но сам по себе не реализует визуализацию predictive back и не заменяет официальные API:

```kotlin
@Composable
fun PredictiveBackExample() {
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    val dispatcher = LocalOnBackPressedDispatcherOwner.current?.onBackPressedDispatcher

    DisposableEffect(dispatcher) {
        if (dispatcher == null) return@DisposableEffect onDispose {}

        val backCallback = object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                scope.launch {
                    if (drawerState.isOpen) {
                        drawerState.close()
                    } else {
                        // Позволяем системе обработать back (например, predictive back навигацию)
                        isEnabled = false
                        dispatcher.onBackPressed()
                    }
                }
            }
        }

        dispatcher.addCallback(backCallback)
        onDispose { backCallback.remove() }
    }

    ModalNavigationDrawer(drawerState = drawerState) {
        // Content
    }
}
```

Для реальной поддержки предиктивного жеста следует использовать актуальные системные и navigation-compose API; это важно упомянуть на собеседовании.

### Переходы Навигации

Ниже пример демонстрирует концепцию комбинирования слайд- и fade-переходов при навигации. Конкретная реализация зависит от используемой библиотеки (например, `navigation-compose` c поддержкой анимаций или Accompanist). В стандартном `NavHost` параметры `enterTransition/exitTransition` могут быть недоступны без анимационного варианта API.

```kotlin
@Composable
fun NavigationWithTransitions() {
    val navController = rememberNavController()

    // Псевдокод: используйте анимационный NavHost из актуальной библиотеки
    AnimatedNavHost( // примерное имя; зависит от выбранной реализации
        navController = navController,
        startDestination = "home",
        enterTransition = {
            slideInHorizontally(
                initialOffsetX = { it },
                animationSpec = tween(300)
            ) + fadeIn(animationSpec = tween(300))
        },
        exitTransition = {
            slideOutHorizontally(
                targetOffsetX = { -it / 2 },
                animationSpec = tween(300)
            ) + fadeOut(animationSpec = tween(300))
        }
    ) {
        composable("home") { HomeScreen(navController) }
        composable("details") { DetailsScreen(navController) }
    }
}
```

### Лучшие Практики

```kotlin
// ✅ Последовательные длительности (пример)
val animationSpec = tween(durationMillis = 300)

// ⚠️ Избегайте произвольных/хаотичных значений без причин
val oddSpec = tween(durationMillis = 237)

// ✅ Стабильные ключи для списков — меньше лишних перерисовок и артефактов анимации
items(items, key = { it.id }) { item -> /* ... */ }

// ⚠️ Без ключей возможны "скачки" анимаций при изменении списка
items(items) { item -> /* ... */ }

// ⚠️ Не рекомендуется напрямую полагаться на Settings.Global.ANIMATOR_DURATION_SCALE
// Лучше уважать системные настройки через рекомендованные API и/или
// предоставлять настройку "Reduce motion" в приложении.
```

Также:

- избегайте избыточных/долгих анимаций, которые мешают восприятию контента;
- обеспечивайте предсказуемость и обратимость анимаций;
- учитывайте accessibility (уменьшение движения, чувствительность к motion).

---

## Answer (EN)

**Material 3 motion** creates meaningful transitions that guide users through the app. Motion supports clarity, efficiency, and personality. See also [[c-animation]] and [[c-animation-framework]] for foundational animation concepts.

Note: the principles and values below reflect practical guidelines consistent with Material 3, but are not a verbatim list of officially named principles.

### Material 3 Motion Principles

1. **Informative** — Directs attention and communicates relationships between elements.
2. **Focused** — Leads users to primary actions and states, avoiding visual noise.
3. **Expressive** — Adds character and smoothness while respecting brand and context.
4. **Practical** — Enhances usability; animations are short, predictable, and not obstructive.

### Durations (Guidelines)

Material Design encourages short, consistent motion. The following are typical ranges, not strict canonical values:

| Duration | Use Case                    | Example                        |
|----------|-----------------------------|--------------------------------|
| ≈100ms   | Simple micro interactions   | Icon state change              |
| ≈200ms   | Small components            | Checkbox, switch               |
| ≈300ms   | Standard state transitions  | Buttons, cards                 |
| ≈300–400ms | Screen-level transitions  | Navigation between destinations|
| 400ms+   | Emphasized transitions      | Large expansions               |

Key idea: keep it consistent and proportional to distance/complexity.

### Basic Transitions (Compose examples)

The following Jetpack Compose snippets illustrate approaches aligned with Material 3 motion (you can adjust specs to your design system).

**Fade transition:**

```kotlin
@Composable
fun FadeTransition(visible: Boolean, content: @Composable () -> Unit) {
    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(animationSpec = tween(300, easing = LinearOutSlowInEasing)),
        exit = fadeOut(animationSpec = tween(200))
    ) {
        content()
    }
}
```

**Slide transition:**

```kotlin
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
    ) {
        content()
    }
}
```

### Shared Element Transitions

Shared elements animate smoothly between screens to preserve continuity (e.g., from a list item to a detail screen). In Compose, this is supported via experimental APIs (`SharedTransitionLayout`, `SharedTransitionScope`) and is version-dependent. Below is a simplified conceptual example (may require adjustment to match the exact library version):

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedElementExample() {
    var showDetails by remember { mutableStateOf(false) }

    SharedTransitionLayout { sharedTransitionScope ->
        AnimatedContent(targetState = showDetails, label = "sharedTransition") { isShowingDetails ->
            if (isShowingDetails) {
                DetailScreen(
                    onBack = { showDetails = false },
                    sharedScope = sharedTransitionScope,
                    animatedContentScope = this
                )
            } else {
                ListScreen(
                    onClick = { showDetails = true },
                    sharedScope = sharedTransitionScope,
                    animatedContentScope = this
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
    animatedContentScope: AnimatedContentScope
) {
    with(sharedScope) {
        Card(
            modifier = Modifier
                .sharedElement(
                    state = rememberSharedContentState(key = "item-1"),
                    animatedVisibilityScope = animatedContentScope
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
                            state = rememberSharedContentState(key = "image-1"),
                            animatedVisibilityScope = animatedContentScope
                        )
                )
                Text(
                    text = "Item Title",
                    modifier = Modifier.sharedElement(
                        state = rememberSharedContentState(key = "title-1"),
                        animatedVisibilityScope = animatedContentScope
                    )
                )
            }
        }
    }
}
```

(Actual signatures/parameters may differ; in an interview, highlight understanding of the concept and that you would verify against the current docs.)

### Predictive Back Gesture

Predictive back (Android 13+) shows a preview of the previous state/screen while the back gesture is in progress. Full support involves:

- integrating with navigation (NavController / navigation-compose);
- using system APIs that expose predictive back callbacks/progress;
- smoothly animating content in response to gesture progress.

The snippet below shows handling of a back action in Compose (e.g., closing a drawer). It does NOT by itself implement predictive back visualization; it’s an example of custom back handling coexisting with system behavior:

```kotlin
@Composable
fun PredictiveBackExample() {
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    val dispatcher = LocalOnBackPressedDispatcherOwner.current?.onBackPressedDispatcher

    DisposableEffect(dispatcher) {
        if (dispatcher == null) return@DisposableEffect onDispose {}

        val backCallback = object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                scope.launch {
                    if (drawerState.isOpen) {
                        drawerState.close()
                    } else {
                        // Let the system handle back (e.g., predictive back navigation)
                        isEnabled = false
                        dispatcher.onBackPressed()
                    }
                }
            }
        }

        dispatcher.addCallback(backCallback)
        onDispose { backCallback.remove() }
    }

    ModalNavigationDrawer(drawerState = drawerState) {
        // Content
    }
}
```

For true predictive back support, use the up-to-date platform and navigation-compose APIs; mention this nuance in interviews.

### Navigation Transitions

Below is a conceptual example combining slide and fade transitions for navigation. The concrete implementation depends on the chosen library (e.g., an animated variant of `NavHost` from navigation-compose or Accompanist). In plain `NavHost`, `enterTransition/exitTransition` parameters are not available without such an extension.

```kotlin
@Composable
fun NavigationWithTransitions() {
    val navController = rememberNavController()

    // Pseudocode: use an AnimatedNavHost from your animation-enabled navigation library
    AnimatedNavHost(
        navController = navController,
        startDestination = "home",
        enterTransition = {
            slideInHorizontally(
                initialOffsetX = { it },
                animationSpec = tween(300)
            ) + fadeIn(animationSpec = tween(300))
        },
        exitTransition = {
            slideOutHorizontally(
                targetOffsetX = { -it / 2 },
                animationSpec = tween(300)
            ) + fadeOut(animationSpec = tween(300))
        }
    ) {
        composable("home") { HomeScreen(navController) }
        composable("details") { DetailsScreen(navController) }
    }
}
```

### Best Practices

```kotlin
// ✅ Consistent, predictable durations (example)
val animationSpec = tween(durationMillis = 300)

// ⚠️ Avoid arbitrary/odd durations without design rationale
val oddSpec = tween(durationMillis = 237)

// ✅ Provide stable keys in lists to avoid recomposition/animation artifacts
items(items, key = { it.id }) { item -> /* ... */ }

// ⚠️ Without keys, item reordering can cause janky or incorrect animations
items(items) { item -> /* ... */ }

// ⚠️ Avoid directly relying on Settings.Global.ANIMATOR_DURATION_SCALE in app logic.
// Prefer recommended platform APIs and/or an in-app "Reduce motion" option
// that respects system accessibility settings.
```

Additionally:

- avoid overly long or exaggerated animations that slow users down;
- keep transitions reversible and predictable;
- account for accessibility (reduced motion, vestibular sensitivity, sufficient contrast during motion).

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

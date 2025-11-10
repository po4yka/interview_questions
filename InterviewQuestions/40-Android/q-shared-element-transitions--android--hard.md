---
id: android-420
title: "Shared Element Transitions / Переходы с общими элементами"
aliases: [Hero Animations, Shared Element Transitions, Анимация героя, Переходы с общими элементами]
topic: android
subtopics: [ui-animation, ui-compose, ui-navigation]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium, q-how-to-catch-the-earliest-entry-point-into-the-application--android--medium]
created: 2025-10-15
updated: 2025-10-27
sources: [https://developer.android.com/jetpack/compose/animation/overview]
tags: [android/ui-animation, android/ui-compose, android/ui-navigation, animations, compose, difficulty/hard, hero-animations, navigation, shared-elements, transitions]
---

# Вопрос (RU)

> Как реализовать переходы с общими элементами между composables? Объясните API SharedTransitionLayout.

# Question (EN)

> How do you implement shared element transitions between composables? Explain the SharedTransitionLayout API.

---

## Ответ (RU)

**Переходы с общими элементами** (hero animations) создают визуальную непрерывность при перемещении элемента между экранами. Начиная с Compose 1.6+ в `androidx.compose.animation` есть экспериментальный API **SharedTransitionLayout** и связанные модификаторы.

Базовый паттерн:

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun Root() {
    SharedTransitionLayout { sharedTransitionScope ->
        // AnimatedContent или другой контейнер, создающий AnimatedContentScope/AnimatedVisibilityScope
        AnimatedContent(targetState = isDetailScreen, label = "shared_transition") { isDetail ->
            if (isDetail) {
                DetailScreen(sharedTransitionScope = sharedTransitionScope, animatedContentScope = this)
            } else {
                ListScreen(sharedTransitionScope = sharedTransitionScope, animatedContentScope = this)
            }
        }
    }
}
```

```kotlin
// ✅ Отмечаем общие элементы совпадающими ключами и передаём оба scope
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ListItem(
    item: Item,
    sharedTransitionScope: SharedTransitionScope,
    animatedContentScope: AnimatedContentScope
) {
    with(sharedTransitionScope) {
        Image(
            painter = painterResource(item.imageRes),
            contentDescription = null,
            modifier = Modifier.sharedElement(
                state = rememberSharedContentState(key = "image-${item.id}"), // ✅ Уникальный стабильный ключ
                animatedVisibilityScope = animatedContentScope
            )
        )
    }
}
```

### Интеграция с Navigation Compose

Ключевые моменты:
- `SharedTransitionLayout` должен оборачивать NavHost, чтобы оба экрана находились в одном `SharedTransitionScope`.
- Для анимаций навигации используйте `AnimatedContentTransitionScope` / `AnimatedVisibilityScope`, предоставленные Navigation.
- Экземпляр `SharedTransitionScope` передаётся вниз через параметры.

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    SharedTransitionLayout { sharedTransitionScope ->
        NavHost(navController, startDestination = "list") {
            composable("list") { backStackEntry ->
                // `this` здесь - NavBackStackEntry scope, а не AnimatedContentScope.
                // Для shared elements достаточно передать sharedTransitionScope вниз и
                // использовать навигационные анимации как AnimatedVisibilityScope.
                ListScreen(
                    onItemClick = { id -> navController.navigate("detail/$id") },
                    sharedTransitionScope = sharedTransitionScope,
                    backStackEntry = backStackEntry
                )
            }

            composable("detail/{id}") { backStackEntry ->
                DetailScreen(
                    itemId = backStackEntry.arguments?.getString("id"),
                    sharedTransitionScope = sharedTransitionScope,
                    backStackEntry = backStackEntry
                )
            }
        }
    }
}
```

(Конкретная интеграция с Nav animations может отличаться в зависимости от версии Navigation Compose; важно, что все shared elements используют один и тот же `SharedTransitionScope` и соответствующий `AnimatedVisibilityScope`.)

### Настройка анимации

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
fun Modifier.sharedImage(
    key: String,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
): Modifier = with(sharedTransitionScope) {
    sharedElement(
        state = rememberSharedContentState(key = key),
        animatedVisibilityScope = animatedVisibilityScope,
        boundsTransform = { _, _ ->
            spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessLow
            )
        }
    )
}

@OptIn(ExperimentalSharedTransitionApi::class)
fun Modifier.sharedBoundsFadeScale(
    key: String,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
): Modifier = with(sharedTransitionScope) {
    sharedBounds(
        sharedContentState = rememberSharedContentState(key = key),
        animatedVisibilityScope = animatedVisibilityScope,
        enter = fadeIn() + scaleIn(),
        exit = fadeOut() + scaleOut()
        // resizeMode настраивается через SharedBoundsResizeMode при необходимости
    )
}
```

### Множественные элементы

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ItemCard(
    item: Item,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Column {
            Image(
                painter = painterResource(item.imageRes),
                contentDescription = null,
                modifier = Modifier.sharedElement(
                    state = rememberSharedContentState(key = "image-${item.id}"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
            )

            Text(
                text = item.title,
                modifier = Modifier.sharedBounds(
                    sharedContentState = rememberSharedContentState(key = "title-${item.id}"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
            )

            // ❌ Не помечен как shared element — появится/исчезнет без общей анимации
            Text(text = item.description)
        }
    }
}
```

### Edge Cases

```kotlin
// ✅ Условный shared element с управлением видимостью вызывающим кодом
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ConditionalElement(
    showImage: Boolean,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        if (showImage) {
            Image(
                painter = painterResource(R.drawable.some_image),
                contentDescription = null,
                modifier = Modifier.sharedElementWithCallerManagedVisibility(
                    sharedContentState = rememberSharedContentState(key = "image"),
                    animatedVisibilityScope = animatedVisibilityScope,
                    visible = showImage
                )
            )
        }
    }
}

// ✅ Предотвращение клиппинга при изменении размеров (пример внутри layout с lookahead)
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun NonClippingBox(
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Box(
            modifier = Modifier
                .sharedElement(
                    state = rememberSharedContentState(key = "box"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
                .skipToLookaheadSize() // Помогает избежать артефактов размеров во время анимации
        )
    }
}
```

### Критические моменты

**Производительность:**
- Используйте `skipToLookaheadSize()` для сложных layout-ов, где промежуточные измерения вызывают артефакты.
- Избегайте тяжёлых вычислений в `boundsTransform` и других анимационных блоках.
- Профилируйте через Layout Inspector / профайлеры Compose.

**Ключи:**
- Ключи должны быть уникальными и стабильными на обоих экранах.
- Используйте ID сущности, а не индекс списка.
- Совпадающие ключи обязательны: элемент без пары не участвует в shared transition.

**Навигация:**
- Оборачивайте NavHost в `SharedTransitionLayout`.
- Передавайте `SharedTransitionScope` через параметры вниз по иерархии.
- Тестируйте быстрые переходы вперёд/назад и поворот экрана, чтобы убедиться, что состояние ключей и scope-ов сохраняется.

Подробнее: [[c-jetpack-compose]]

---

## Answer (EN)

**Shared Element Transitions** (hero animations) create visual continuity when an element moves between screens. Starting from Compose 1.6+ (experimental), `androidx.compose.animation` provides the **SharedTransitionLayout** API and related modifiers.

Basic pattern:

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun Root() {
    SharedTransitionLayout { sharedTransitionScope ->
        // Use AnimatedContent or another container that creates an AnimatedContentScope/AnimatedVisibilityScope
        AnimatedContent(targetState = isDetailScreen, label = "shared_transition") { isDetail ->
            if (isDetail) {
                DetailScreen(sharedTransitionScope = sharedTransitionScope, animatedContentScope = this)
            } else {
                ListScreen(sharedTransitionScope = sharedTransitionScope, animatedContentScope = this)
            }
        }
    }
}
```

```kotlin
// ✅ Mark shared elements with matching keys and pass both scopes
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ListItem(
    item: Item,
    sharedTransitionScope: SharedTransitionScope,
    animatedContentScope: AnimatedContentScope
) {
    with(sharedTransitionScope) {
        Image(
            painter = painterResource(item.imageRes),
            contentDescription = null,
            modifier = Modifier.sharedElement(
                state = rememberSharedContentState(key = "image-${item.id}"), // ✅ Unique stable key
                animatedVisibilityScope = animatedContentScope
            )
        )
    }
}
```

### Navigation Compose Integration

Key points:
- Wrap NavHost with `SharedTransitionLayout` so both screens share the same `SharedTransitionScope`.
- Use the `AnimatedContentTransitionScope` / `AnimatedVisibilityScope` provided by Navigation for transitions.
- Pass the `SharedTransitionScope` down via parameters.

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    SharedTransitionLayout { sharedTransitionScope ->
        NavHost(navController, startDestination = "list") {
            composable("list") { backStackEntry ->
                ListScreen(
                    onItemClick = { id -> navController.navigate("detail/$id") },
                    sharedTransitionScope = sharedTransitionScope,
                    backStackEntry = backStackEntry
                )
            }

            composable("detail/{id}") { backStackEntry ->
                DetailScreen(
                    itemId = backStackEntry.arguments?.getString("id"),
                    sharedTransitionScope = sharedTransitionScope,
                    backStackEntry = backStackEntry
                )
            }
        }
    }
}
```

(Exact wiring with Navigation animations may differ by Navigation Compose version; the core requirement is that all shared elements use the same `SharedTransitionScope` plus the appropriate `AnimatedVisibilityScope`.)

### Animation Customization

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
fun Modifier.sharedImage(
    key: String,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
): Modifier = with(sharedTransitionScope) {
    sharedElement(
        state = rememberSharedContentState(key = key),
        animatedVisibilityScope = animatedVisibilityScope,
        boundsTransform = { _, _ ->
            spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessLow
            )
        }
    )
}

@OptIn(ExperimentalSharedTransitionApi::class)
fun Modifier.sharedBoundsFadeScale(
    key: String,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
): Modifier = with(sharedTransitionScope) {
    sharedBounds(
        sharedContentState = rememberSharedContentState(key = key),
        animatedVisibilityScope = animatedVisibilityScope,
        enter = fadeIn() + scaleIn(),
        exit = fadeOut() + scaleOut()
        // resizeMode is configured via SharedBoundsResizeMode if needed
    )
}
```

### Multiple Elements

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ItemCard(
    item: Item,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Column {
            Image(
                painter = painterResource(item.imageRes),
                contentDescription = null,
                modifier = Modifier.sharedElement(
                    state = rememberSharedContentState(key = "image-${item.id}"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
            )

            Text(
                text = item.title,
                modifier = Modifier.sharedBounds(
                    sharedContentState = rememberSharedContentState(key = "title-${item.id}"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
            )

            // ❌ Not marked as shared element — will appear/disappear abruptly
            Text(text = item.description)
        }
    }
}
```

### Edge Cases

```kotlin
// ✅ Conditional shared element with caller-managed visibility
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun ConditionalElement(
    showImage: Boolean,
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        if (showImage) {
            Image(
                painter = painterResource(R.drawable.some_image),
                contentDescription = null,
                modifier = Modifier.sharedElementWithCallerManagedVisibility(
                    sharedContentState = rememberSharedContentState(key = "image"),
                    animatedVisibilityScope = animatedVisibilityScope,
                    visible = showImage
                )
            )
        }
    }
}

// ✅ Prevent clipping / layout artifacts when size changes during transition
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun NonClippingBox(
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Box(
            modifier = Modifier
                .sharedElement(
                    state = rememberSharedContentState(key = "box"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
                .skipToLookaheadSize()
        )
    }
}
```

### Critical Points

**Performance:**
- Use `skipToLookaheadSize()` for complex layouts where intermediate measurements cause artifacts.
- Avoid heavy work inside `boundsTransform` and animation lambdas.
- Profile with Layout Inspector / Compose performance tools.

**Keys:**
- Keys must be unique and stable on both screens.
- Prefer item IDs over list indices.
- Matching keys are mandatory; elements without a counterpart will not participate in shared transitions.

**Navigation:**
- Wrap NavHost in `SharedTransitionLayout`.
- Pass `SharedTransitionScope` through parameters down the tree.
- Test rapid back/forward navigation and configuration changes to ensure scopes and keys remain consistent.

See: [[c-jetpack-compose]]

---

## Follow-ups

- How do shared element transitions interact with Navigation animations?
- What are performance considerations for hero animations?

## References

- [[c-jetpack-compose]]
- `https://developer.android.com/jetpack/compose/animation/overview` — Compose animation

## Related Questions

### Prerequisites (Easier)
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]]

### Related (Same Level)
- [[q-how-to-catch-the-earliest-entry-point-into-the-application--android--medium]]

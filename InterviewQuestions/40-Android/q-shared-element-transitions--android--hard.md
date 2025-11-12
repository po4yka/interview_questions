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
fun Root(isDetailScreen: Boolean) {
    SharedTransitionLayout { sharedTransitionScope ->
        // AnimatedContent предоставляет AnimatedContentScope, который является AnimatedVisibilityScope
        AnimatedContent(targetState = isDetailScreen, label = "shared_transition") { isDetail ->
            val animatedVisibilityScope = this
            if (isDetail) {
                DetailScreen(
                    sharedTransitionScope = sharedTransitionScope,
                    animatedVisibilityScope = animatedVisibilityScope
                )
            } else {
                ListScreen(
                    sharedTransitionScope = sharedTransitionScope,
                    animatedVisibilityScope = animatedVisibilityScope
                )
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
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Image(
            painter = painterResource(item.imageRes),
            contentDescription = null,
            modifier = Modifier.sharedElement(
                state = rememberSharedContentState(key = "image-${item.id}"), // ✅ Уникальный стабильный ключ
                animatedVisibilityScope = animatedVisibilityScope
            )
        )
    }
}
```

### Интеграция с Navigation Compose

Ключевые моменты:
- `SharedTransitionLayout` должен оборачивать NavHost, чтобы все целевые composable находились в одном `SharedTransitionScope`.
- Для shared elements каждая сторона анимации должна находиться внутри `AnimatedVisibilityScope` (или совместимого scope), который создаётся навигационными анимациями (например, `AnimatedContent`/`AnimatedNavHost` в зависимости от версии Navigation Compose).
- Экземпляр `SharedTransitionScope` и соответствующий `AnimatedVisibilityScope` передаются вниз через параметры.

Пример структуры (упрощённо — конкретный API Navigation может отличаться):

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    SharedTransitionLayout { sharedTransitionScope ->
        // В реальном проекте используйте AnimatedNavHost / NavHost с анимациями,
        // которые предоставляют AnimatedVisibilityScope для экранов.
        NavHost(navController, startDestination = "list") {
            composable("list") { backStackEntry ->
                // Здесь показана только передача sharedTransitionScope.
                // Для sharedElement/sharedBounds также нужен animatedVisibilityScope
                // от используемого анимационного контейнера.
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

(Конкретная интеграция с Nav анимациями зависит от версии Navigation Compose. Важно: все shared elements должны использовать один и тот же `SharedTransitionScope` и корректный `AnimatedVisibilityScope`, предоставленный анимационным контейнером. Сам NavHost без анимаций такого scope не даёт.)

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
- Убедитесь, что элементы, использующие sharedElement/sharedBounds, находятся внутри актуального `AnimatedVisibilityScope`, предоставленного анимационным контейнером навигации.
- Тестируйте быстрые переходы вперёд/назад и поворот экрана, чтобы убедиться, что состояние ключей и scope-ов сохраняется.

Подробнее: [[c-jetpack-compose]]

---

## Answer (EN)

**Shared Element Transitions** (hero animations) create visual continuity when an element moves between screens. Starting from Compose 1.6+ (experimental), `androidx.compose.animation` provides the **SharedTransitionLayout** API and related modifiers.

Basic pattern:

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun Root(isDetailScreen: Boolean) {
    SharedTransitionLayout { sharedTransitionScope ->
        // AnimatedContent provides AnimatedContentScope, which is an AnimatedVisibilityScope
        AnimatedContent(targetState = isDetailScreen, label = "shared_transition") { isDetail ->
            val animatedVisibilityScope = this
            if (isDetail) {
                DetailScreen(
                    sharedTransitionScope = sharedTransitionScope,
                    animatedVisibilityScope = animatedVisibilityScope
                )
            } else {
                ListScreen(
                    sharedTransitionScope = sharedTransitionScope,
                    animatedVisibilityScope = animatedVisibilityScope
                )
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
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Image(
            painter = painterResource(item.imageRes),
            contentDescription = null,
            modifier = Modifier.sharedElement(
                state = rememberSharedContentState(key = "image-${item.id}"), // ✅ Unique stable key
                animatedVisibilityScope = animatedVisibilityScope
            )
        )
    }
}
```

### Navigation Compose Integration

Key points:
- Wrap NavHost with `SharedTransitionLayout` so all destinations share the same `SharedTransitionScope`.
- For shared elements, each side of the transition must be inside an `AnimatedVisibilityScope` (or compatible scope) created by your navigation animations (e.g., `AnimatedContent` / `AnimatedNavHost`, depending on the Navigation Compose version).
- Pass both `SharedTransitionScope` and the appropriate `AnimatedVisibilityScope` down via parameters.

Structural example (simplified — exact Navigation APIs vary):

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    SharedTransitionLayout { sharedTransitionScope ->
        // In a real app, use AnimatedNavHost / NavHost with transitions
        // that provide an AnimatedVisibilityScope for each destination.
        NavHost(navController, startDestination = "list") {
            composable("list") { backStackEntry ->
                // Here we only show passing sharedTransitionScope.
                // To use sharedElement/sharedBounds, also obtain/pass
                // the AnimatedVisibilityScope from your animation container.
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

(Exact wiring with Navigation animations depends on the Navigation Compose version. The critical requirement: all shared elements use the same `SharedTransitionScope` and a valid `AnimatedVisibilityScope` from the transition container. A plain NavHost without transitions does not provide this scope.)

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

            // ❌ Not marked as shared element — will appear/disappear without shared animation
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

// ✅ Prevent clipping / size artifacts using lookahead-based measurement
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
- Avoid heavy work inside `boundsTransform` and other animation lambdas.
- Profile using Layout Inspector / Compose performance tools.

**Keys:**
- Keys must be unique and stable across screens.
- Prefer item IDs over list indices.
- Matching keys are mandatory; elements without a counterpart will not participate in shared transitions.

**Navigation:**
- Wrap NavHost in `SharedTransitionLayout`.
- Pass `SharedTransitionScope` down the tree.
- Ensure elements using sharedElement/sharedBounds are placed inside a valid `AnimatedVisibilityScope` provided by your navigation transition container.
- Test rapid forward/back navigation and configuration changes to ensure scopes and keys remain consistent.

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

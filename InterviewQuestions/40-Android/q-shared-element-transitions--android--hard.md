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
date created: Saturday, November 1st 2025, 12:47:04 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)

> Как реализовать переходы с общими элементами между composables? Объясните API SharedTransitionLayout.

# Question (EN)

> How do you implement shared element transitions between composables? Explain the SharedTransitionLayout API.

---

## Ответ (RU)

**Переходы с общими элементами** (hero animations) создают визуальную непрерывность при переходе элемента между экранами. Compose 1.6+ предоставляет API **SharedTransitionLayout**.

**Основная концепция:**

```kotlin
// ✅ SharedTransitionLayout создает scope для общих элементов
SharedTransitionLayout {
    AnimatedContent(targetState = isDetailScreen) { isDetail ->
        if (isDetail) {
            DetailScreen()  // ✅ Целевой экран
        } else {
            ListScreen()    // ✅ Исходный экран
        }
    }
}

// ✅ Отметьте элементы совпадающими ключами
@Composable
fun SharedTransitionScope.ListItem(item: Item) {
    Image(
        painter = painterResource(item.imageRes),
        modifier = Modifier.sharedElement(
            rememberSharedContentState(key = "image-${item.id}"),  // ✅ Уникальный ключ
            animatedVisibilityScope = this@AnimatedContent
        )
    )
}
```

### Интеграция С Navigation Compose

```kotlin
// ✅ Использование с Navigation
@Composable
fun AppNavigation() {
    SharedTransitionLayout {
        val navController = rememberNavController()

        NavHost(navController, startDestination = "list") {
            composable("list") {
                ListScreen(
                    onItemClick = { id -> navController.navigate("detail/$id") },
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this
                )
            }

            composable("detail/{id}") { backStackEntry ->
                DetailScreen(
                    itemId = backStackEntry.arguments?.getString("id"),
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this
                )
            }
        }
    }
}
```

### Настройка Анимации

```kotlin
// ✅ Кастомизация spring-параметров
Modifier.sharedElement(
    state = rememberSharedContentState(key = "image"),
    animatedVisibilityScope = this,
    boundsTransform = { _, _ ->
        spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        )
    }
)

// ✅ sharedBounds для контента разного размера
Modifier.sharedBounds(
    sharedContentState = rememberSharedContentState(key = "bounds"),
    animatedVisibilityScope = this,
    enter = fadeIn() + scaleIn(),
    exit = fadeOut() + scaleOut(),
    resizeMode = ScaleToBounds(ContentScale.Crop)
)
```

### Множественные Элементы

```kotlin
// ✅ Несколько shared elements одновременно
@Composable
fun SharedTransitionScope.ItemCard(item: Item) {
    Column {
        Image(
            modifier = Modifier.sharedElement(
                rememberSharedContentState(key = "image-${item.id}"),
                animatedVisibilityScope = this@AnimatedContent
            ),
            // ...
        )

        Text(
            text = item.title,
            modifier = Modifier.sharedBounds(
                rememberSharedContentState(key = "title-${item.id}"),
                animatedVisibilityScope = this@AnimatedContent
            )
        )

        // ❌ НЕ анимируется - появится/исчезнет резко
        Text(text = item.description)
    }
}
```

### Edge Cases

```kotlin
// ✅ Условный shared element
@Composable
fun SharedTransitionScope.ConditionalElement(showImage: Boolean) {
    if (showImage) {
        Image(
            modifier = Modifier.sharedElementWithCallerManagedVisibility(
                sharedContentState = rememberSharedContentState(key = "image"),
                visible = showImage
            ),
            // ...
        )
    }
}

// ✅ Предотвращение клиппинга
Box(
    modifier = Modifier
        .sharedElement(
            rememberSharedContentState(key = "box"),
            animatedVisibilityScope = this
        )
        .skipToLookaheadSize()  // ✅ Пропускает промежуточные размеры
)
```

### Критические Моменты

**Производительность:**
- Используйте `skipToLookaheadSize()` для сложных layouts
- Избегайте тяжёлых вычислений в `boundsTransform`
- Профилируйте через Layout Inspector

**Ключи:**
- Уникальные и стабильные на обоих экранах
- Используйте ID элемента, не индекс
- Совпадающие ключи обязательны

**Навигация:**
- Передавайте scope через параметры
- Тестируйте быстрые переходы back/forward
- Проверяйте поведение при изменении конфигурации

Подробнее: [[c-jetpack-compose]]

---

## Answer (EN)

**Shared Element Transitions** (hero animations) create visual continuity when an element transitions between screens. Compose 1.6+ provides the **SharedTransitionLayout** API.

**Key concepts:**

```kotlin
// ✅ SharedTransitionLayout provides scope for shared elements
SharedTransitionLayout {
    AnimatedContent(targetState = isDetailScreen) { isDetail ->
        if (isDetail) {
            DetailScreen()  // ✅ Destination screen
        } else {
            ListScreen()    // ✅ Source screen
        }
    }
}

// ✅ Mark shared elements with matching keys
@Composable
fun SharedTransitionScope.ListItem(item: Item) {
    Image(
        painter = painterResource(item.imageRes),
        modifier = Modifier.sharedElement(
            rememberSharedContentState(key = "image-${item.id}"),  // ✅ Unique key
            animatedVisibilityScope = this@AnimatedContent
        )
    )
}
```

### Navigation Compose Integration

```kotlin
// ✅ Using with Navigation
@Composable
fun AppNavigation() {
    SharedTransitionLayout {
        val navController = rememberNavController()

        NavHost(navController, startDestination = "list") {
            composable("list") {
                ListScreen(
                    onItemClick = { id -> navController.navigate("detail/$id") },
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this
                )
            }

            composable("detail/{id}") { backStackEntry ->
                DetailScreen(
                    itemId = backStackEntry.arguments?.getString("id"),
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedVisibilityScope = this
                )
            }
        }
    }
}
```

### Animation Customization

```kotlin
// ✅ Customize spring parameters
Modifier.sharedElement(
    state = rememberSharedContentState(key = "image"),
    animatedVisibilityScope = this,
    boundsTransform = { _, _ ->
        spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        )
    }
)

// ✅ sharedBounds for different-sized content
Modifier.sharedBounds(
    sharedContentState = rememberSharedContentState(key = "bounds"),
    animatedVisibilityScope = this,
    enter = fadeIn() + scaleIn(),
    exit = fadeOut() + scaleOut(),
    resizeMode = ScaleToBounds(ContentScale.Crop)
)
```

### Multiple Elements

```kotlin
// ✅ Multiple shared elements simultaneously
@Composable
fun SharedTransitionScope.ItemCard(item: Item) {
    Column {
        Image(
            modifier = Modifier.sharedElement(
                rememberSharedContentState(key = "image-${item.id}"),
                animatedVisibilityScope = this@AnimatedContent
            ),
            // ...
        )

        Text(
            text = item.title,
            modifier = Modifier.sharedBounds(
                rememberSharedContentState(key = "title-${item.id}"),
                animatedVisibilityScope = this@AnimatedContent
            )
        )

        // ❌ NOT animated - will appear/disappear abruptly
        Text(text = item.description)
    }
}
```

### Edge Cases

```kotlin
// ✅ Conditional shared element
@Composable
fun SharedTransitionScope.ConditionalElement(showImage: Boolean) {
    if (showImage) {
        Image(
            modifier = Modifier.sharedElementWithCallerManagedVisibility(
                sharedContentState = rememberSharedContentState(key = "image"),
                visible = showImage
            ),
            // ...
        )
    }
}

// ✅ Prevent clipping
Box(
    modifier = Modifier
        .sharedElement(
            rememberSharedContentState(key = "box"),
            animatedVisibilityScope = this
        )
        .skipToLookaheadSize()  // ✅ Skip intermediate sizes
)
```

### Critical Points

**Performance:**
- Use `skipToLookaheadSize()` for complex layouts
- Avoid heavy computations in `boundsTransform`
- Profile with Layout Inspector

**Keys:**
- Unique and stable on both screens
- Use element ID, not list index
- Matching keys required

**Navigation:**
- Pass scope via parameters
- Test rapid back/forward transitions
- Check configuration change behavior

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

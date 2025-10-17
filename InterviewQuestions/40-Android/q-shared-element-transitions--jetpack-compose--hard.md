---
id: 20251012-122711102
title: "Shared Element Transitions / Переходы с общими элементами"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: [compose, animations, navigation, transitions, shared-elements, hero-animations, difficulty/hard]
---

# Shared Element Transitions in Compose

# Question (EN)

> How do you implement shared element transitions between composables? Explain the SharedTransitionLayout API.

# Вопрос (RU)

> Как реализовать переходы с общими элементами между composables? Объясните API SharedTransitionLayout.

---

## Answer (EN)

**Shared Element Transitions** (also known as hero animations) create visual continuity when an element transitions between two screens. Compose 1.6+ provides the **SharedTransitionLayout** API for implementing these transitions declaratively.

**Key concepts:**

```kotlin
// SharedTransitionLayout provides scope for shared elements
SharedTransitionLayout {
    AnimatedContent(targetState = isDetailScreen) { isDetail ->
        if (isDetail) {
            DetailScreen()
        } else {
            ListScreen()
        }
    }
}

// Mark shared elements with matching keys
@Composable
fun SharedTransitionScope.ListItem(item: Item) {
    Image(
        painter = painterResource(item.imageRes),
        modifier = Modifier.sharedElement(
            rememberSharedContentState(key = "image-${item.id}"),
            animatedVisibilityScope = this@AnimatedContent
        )
    )
}
```

**Features:**
- Smooth morphing between screens
- Automatic bounds and position interpolation
- Works with Navigation Compose
- Declarative API with modifiers

---

## Ответ (RU)

**Переходы с общими элементами** (также известные как hero animations) создают визуальную непрерывность при переходе элемента между двумя экранами. Compose 1.6+ предоставляет API **SharedTransitionLayout** для декларативной реализации таких переходов.

**Ключевые концепции:**

```kotlin
// SharedTransitionLayout обеспечивает scope для общих элементов
SharedTransitionLayout {
    AnimatedContent(targetState = isDetailScreen) { isDetail ->
        if (isDetail) {
            DetailScreen()
        } else {
            ListScreen()
        }
    }
}

// Отметьте общие элементы совпадающими ключами
@Composable
fun SharedTransitionScope.ListItem(item: Item) {
    Image(
        painter = painterResource(item.imageRes),
        modifier = Modifier.sharedElement(
            rememberSharedContentState(key = "image-${item.id}"),
            animatedVisibilityScope = this@AnimatedContent
        )
    )
}
```

**Возможности:**
- Плавная трансформация между экранами
- Автоматическая интерполяция границ и позиции
- Работает с Navigation Compose
- Декларативный API с модификаторами

---

## Follow-ups

-   How do shared element transitions interact with Navigation animations and back stack?
-   What are performance considerations and how to profile jank in hero animations?
-   How do you coordinate multiple shared elements and staggered transitions?

## References

-   `https://developer.android.com/jetpack/compose/animation/overview` — Compose animation
-   `https://developer.android.com/jetpack/compose/navigation` — Compose Navigation
-   `https://developer.android.com/guide/navigation/navigation-animate-transitions` — Navigation transitions

## Related Questions

---
id: 20251020-210000
title: "Advanced Compose UI Testing / Продвинутое тестирование Compose UI"
aliases: ["Advanced Compose UI Testing", "Продвинутое тестирование Compose UI"]
topic: android
subtopics: [testing-ui, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
sources: []
status: draft
related: [c-compose-semantics, c-ui-testing, c-accessibility, q-compose-testing--android--medium, q-compose-semantics--android--medium]
created: 2025-10-20
updated: 2025-10-30
tags: [android/testing-ui, android/ui-compose, compose-testing, accessibility, semantics, difficulty/hard]
moc: moc-android
date created: Thursday, October 30th 2025, 11:56:49 am
date modified: Thursday, October 30th 2025, 12:43:58 pm
---

# Вопрос (RU)
> Как тестировать сложные UI сценарии в Compose включая анимации, жесты, semantic matchers и доступность? Как обрабатывать async операции в тестах?

---

# Question (EN)
> How to test complex Compose UI scenarios including animations, gestures, semantic matchers, and accessibility? How to handle async operations in tests?

---

## Ответ (RU)

**Продвинутое тестирование Compose** использует semantic tree для надежной идентификации элементов и детерминированной синхронизации с асинхронными операциями, анимациями и жестами.

### Ключевые Принципы

**Семантика вместо структуры:**
- Тестируйте через roles, contentDescription, testTag — не через layout tree
- Используйте `ComposeTestRule.mainClock` для детерминированного контроля времени

**Синхронизация:**
- `waitUntil {}` и `waitForIdle()` вместо `Thread.sleep()`
- `mainClock.advanceTimeBy()` для контроля анимаций
- `runOnIdle {}` для проверки состояния после recomposition

**Проектирование:**
- DI для подмены зависимостей
- Стабильные testTag для переходных UI
- Избегайте случайных задержек

### Semantic Matchers

```kotlin
fun hasLoadingState(): SemanticsMatcher =
    SemanticsMatcher.expectValue(
        SemanticsProperties.StateDescription, // ✅ стандартные properties
        "loading"
    )

composeTestRule.onNode(hasLoadingState()).assertExists()
composeTestRule.onNodeWithRole(Role.Button).assertHasClickAction()
```

### Анимации

```kotlin
@Test
fun testAnimation() {
    composeTestRule.mainClock.autoAdvance = false // ✅ отключить авто-advance
    composeTestRule.setContent { AnimatedContent() }

    composeTestRule.onNodeWithText("Show").performClick()
    composeTestRule.mainClock.advanceTimeBy(500) // ✅ контроль времени

    composeTestRule.onNodeWithTag("content").assertIsDisplayed()
}
```

### Жесты

```kotlin
@Test
fun testGestures() {
    // Swipe
    composeTestRule.onNodeWithTag("swipeable")
        .performTouchInput { swipeLeft() }

    // Drag с точным контролем
    composeTestRule.onNodeWithTag("draggable")
        .performTouchInput {
            down(center)
            moveTo(center + Offset(200f, 0f)) // ✅ точные координаты
            up()
        }
}
```

### Async Операции

```kotlin
@Test
fun testAsyncLoading() {
    composeTestRule.setContent { AsyncScreen() }

    // ❌ Thread.sleep(1000) — НИКОГДА

    // ✅ Ждать конкретное условие
    composeTestRule.waitUntil(timeoutMillis = 5000) {
        composeTestRule.onAllNodesWithTag("loaded_item")
            .fetchSemanticsNodes().isNotEmpty()
    }

    composeTestRule.onNodeWithTag("loaded_item").assertExists()
}
```

### Доступность

```kotlin
@Test
fun testAccessibility() {
    composeTestRule.setContent {
        IconButton(onClick = {}) {
            Icon(
                Icons.Default.Delete,
                contentDescription = "Delete item" // ✅ обязательно
            )
        }
    }

    // Проверка contentDescription
    composeTestRule
        .onNodeWithContentDescription("Delete item")
        .assertExists()

    // Проверка semantic role
    composeTestRule
        .onNodeWithRole(Role.Button)
        .assertHasClickAction()

    // Merged semantics
    composeTestRule.onNode(
        hasText("Item") and hasClickAction(),
        useUnmergedTree = false // ✅ merged tree
    ).assertExists()
}
```

---

## Answer (EN)

**Advanced Compose Testing** uses the semantic tree for robust element identification and deterministic synchronization with async operations, animations, and gestures.

### Core Principles

**Semantics over structure:**
- Test via roles, contentDescription, testTag — not layout tree
- Use `ComposeTestRule.mainClock` for deterministic time control

**Synchronization:**
- `waitUntil {}` and `waitForIdle()` instead of `Thread.sleep()`
- `mainClock.advanceTimeBy()` for animation control
- `runOnIdle {}` for checking state after recomposition

**Design:**
- DI for dependency injection
- Stable testTag for transient UI
- Avoid random delays

### Semantic Matchers

```kotlin
fun hasLoadingState(): SemanticsMatcher =
    SemanticsMatcher.expectValue(
        SemanticsProperties.StateDescription, // ✅ standard properties
        "loading"
    )

composeTestRule.onNode(hasLoadingState()).assertExists()
composeTestRule.onNodeWithRole(Role.Button).assertHasClickAction()
```

### Animations

```kotlin
@Test
fun testAnimation() {
    composeTestRule.mainClock.autoAdvance = false // ✅ disable auto-advance
    composeTestRule.setContent { AnimatedContent() }

    composeTestRule.onNodeWithText("Show").performClick()
    composeTestRule.mainClock.advanceTimeBy(500) // ✅ time control

    composeTestRule.onNodeWithTag("content").assertIsDisplayed()
}
```

### Gestures

```kotlin
@Test
fun testGestures() {
    // Swipe
    composeTestRule.onNodeWithTag("swipeable")
        .performTouchInput { swipeLeft() }

    // Drag with precise control
    composeTestRule.onNodeWithTag("draggable")
        .performTouchInput {
            down(center)
            moveTo(center + Offset(200f, 0f)) // ✅ precise coordinates
            up()
        }
}
```

### Async Operations

```kotlin
@Test
fun testAsyncLoading() {
    composeTestRule.setContent { AsyncScreen() }

    // ❌ Thread.sleep(1000) — NEVER

    // ✅ Wait for specific condition
    composeTestRule.waitUntil(timeoutMillis = 5000) {
        composeTestRule.onAllNodesWithTag("loaded_item")
            .fetchSemanticsNodes().isNotEmpty()
    }

    composeTestRule.onNodeWithTag("loaded_item").assertExists()
}
```

### Accessibility

```kotlin
@Test
fun testAccessibility() {
    composeTestRule.setContent {
        IconButton(onClick = {}) {
            Icon(
                Icons.Default.Delete,
                contentDescription = "Delete item" // ✅ required
            )
        }
    }

    // Check contentDescription
    composeTestRule
        .onNodeWithContentDescription("Delete item")
        .assertExists()

    // Check semantic role
    composeTestRule
        .onNodeWithRole(Role.Button)
        .assertHasClickAction()

    // Merged semantics
    composeTestRule.onNode(
        hasText("Item") and hasClickAction(),
        useUnmergedTree = false // ✅ merged tree
    ).assertExists()
}
```

---

## Follow-ups

- How to test navigation in Compose with nested destinations?
- How to mock ViewModel dependencies in Compose tests?
- How to test LazyColumn scroll behavior and item visibility?
- How to handle test flakiness caused by animations and delays?
- How to test custom Modifier chains and layout measurements?

## References

- [[c-compose-semantics]] — Semantic tree fundamentals
- [[c-ui-testing]] — UI testing principles
- [[c-accessibility]] — Accessibility best practices
- [[c-testing-pyramid]] — Testing strategy overview
- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/jetpack/compose/semantics

## Related Questions

### Prerequisites (Easier)
- [[q-compose-testing--android--medium]] — Basic Compose testing setup and matchers
- [[q-compose-semantics--android--medium]] — Understanding semantic tree structure

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]] — Performance testing and profiling
- [[q-android-testing-strategies--testing--hard]] — Test isolation and architecture

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]] — Compiler internals and optimization
- Screenshot testing with custom semantic properties for complex scenarios


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
sources: [https://developer.android.com/jetpack/compose/testing]
status: draft
related: [q-compose-performance-optimization--android--hard, q-compose-semantics--android--medium, q-compose-testing--android--medium]
created: 2025-10-20
updated: 2025-10-27
tags: [android/testing-ui, android/ui-compose, compose-testing, accessibility, semantics, difficulty/hard]
moc: moc-android
---

# Вопрос (RU)
> Как тестировать сложные UI сценарии в Compose включая анимации, жесты, semantic matchers и доступность? Как обрабатывать async операции в тестах Compose?

---

# Question (EN)
> How to test complex Compose UI scenarios including animations, gestures, semantic matchers, and accessibility? How to handle async operations in Compose tests?

---

## Ответ (RU)

**Продвинутое тестирование Compose** опирается на semantic tree для надежной идентификации элементов и детерминированной синхронизации с асинхронными операциями, анимациями и жестами.

### Ключевые Принципы

**Семантика вместо структуры:**
- Тестируйте через roles, contentDescription, testTag — не через layout tree
- Утверждайте поведение (текст, состояния, действия), а не детали реализации
- Используйте `ComposeTestRule.mainClock` для детерминированного контроля времени

**Синхронизация:**
- `waitUntil {}` и `waitForIdle()` вместо `Thread.sleep()`
- `mainClock.advanceTimeBy()` для анимаций
- `runOnIdle {}` для проверки состояния после recomposition

**Проектирование под тестирование:**
- DI seams для подмены зависимостей
- Стабильные testTag для переходных UI состояний
- Избегайте случайных задержек в UI логике

### Semantic Matchers

**Пользовательские matchers:**
```kotlin
fun hasLoadingState(): SemanticsMatcher =
    SemanticsMatcher.expectValue(
        SemanticsProperties.StateDescription, // ✅ используйте стандартные properties
        "loading"
    )

composeTestRule.onNode(hasLoadingState()).assertExists()
composeTestRule.onNodeWithRole(Role.Button).assertHasClickAction()
```

### Анимации

**Детерминированный контроль времени:**
```kotlin
@Test
fun testAnimation() {
    composeTestRule.mainClock.autoAdvance = false // ✅ отключить авто-advance
    composeTestRule.setContent { AnimatedContent() }

    composeTestRule.onNodeWithText("Show").performClick()
    composeTestRule.mainClock.advanceTimeBy(500) // ✅ контролируемое продвижение

    composeTestRule.onNodeWithTag("animated_content").assertIsDisplayed()
}
```

### Жесты

**Touch input:**
```kotlin
@Test
fun testSwipeGesture() {
    composeTestRule.onNodeWithTag("swipeable")
        .performTouchInput {
            swipeLeft() // или swipeRight(), swipeUp(), swipeDown()
        }

    composeTestRule.onNodeWithText("Swiped").assertExists()
}

@Test
fun testDrag() {
    composeTestRule.onNodeWithTag("draggable")
        .performTouchInput {
            down(center)
            moveTo(center + Offset(200f, 0f)) // ✅ точный контроль
            up()
        }
}
```

### Async Операции

**Правильная синхронизация:**
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

@Test
fun testErrorState() {
    composeTestRule.onNodeWithTag("trigger_error").performClick()

    composeTestRule.waitUntil {
        composeTestRule.onAllNodesWithTag("error_message")
            .fetchSemanticsNodes().isNotEmpty()
    }
}
```

### Доступность

**Обязательные проверки:**
```kotlin
@Test
fun testAccessibility() {
    composeTestRule.setContent {
        IconButton(onClick = {}) {
            Icon(Icons.Default.Delete, contentDescription = "Delete item") // ✅
        }
    }

    // Проверка contentDescription
    composeTestRule.onNodeWithContentDescription("Delete item").assertExists()

    // Проверка semantic role
    composeTestRule.onNodeWithRole(Role.Button).assertHasClickAction()

    // Merged semantics для сложных composables
    composeTestRule.onNode(
        hasText("Item") and hasClickAction(),
        useUnmergedTree = false // ✅ тестируйте merged tree
    ).assertExists()
}
```

---

## Answer (EN)

**Advanced Compose Testing** relies on the semantic tree for robust element identification and deterministic synchronization with async operations, animations, and gestures.

### Core Principles

**Semantics over structure:**
- Test via roles, contentDescription, testTag — not layout tree
- Assert behavior (text, states, actions), not implementation details
- Use `ComposeTestRule.mainClock` for deterministic time control

**Synchronization:**
- `waitUntil {}` and `waitForIdle()` instead of `Thread.sleep()`
- `mainClock.advanceTimeBy()` for animations
- `runOnIdle {}` for checking state after recomposition

**Design for testability:**
- DI seams for dependency injection
- Stable testTag for transient UI states
- Avoid random delays in UI logic

### Semantic Matchers

**Custom matchers:**
```kotlin
fun hasLoadingState(): SemanticsMatcher =
    SemanticsMatcher.expectValue(
        SemanticsProperties.StateDescription, // ✅ use standard properties
        "loading"
    )

composeTestRule.onNode(hasLoadingState()).assertExists()
composeTestRule.onNodeWithRole(Role.Button).assertHasClickAction()
```

### Animations

**Deterministic time control:**
```kotlin
@Test
fun testAnimation() {
    composeTestRule.mainClock.autoAdvance = false // ✅ disable auto-advance
    composeTestRule.setContent { AnimatedContent() }

    composeTestRule.onNodeWithText("Show").performClick()
    composeTestRule.mainClock.advanceTimeBy(500) // ✅ controlled advancement

    composeTestRule.onNodeWithTag("animated_content").assertIsDisplayed()
}
```

### Gestures

**Touch input:**
```kotlin
@Test
fun testSwipeGesture() {
    composeTestRule.onNodeWithTag("swipeable")
        .performTouchInput {
            swipeLeft() // or swipeRight(), swipeUp(), swipeDown()
        }

    composeTestRule.onNodeWithText("Swiped").assertExists()
}

@Test
fun testDrag() {
    composeTestRule.onNodeWithTag("draggable")
        .performTouchInput {
            down(center)
            moveTo(center + Offset(200f, 0f)) // ✅ precise control
            up()
        }
}
```

### Async Operations

**Proper synchronization:**
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

@Test
fun testErrorState() {
    composeTestRule.onNodeWithTag("trigger_error").performClick()

    composeTestRule.waitUntil {
        composeTestRule.onAllNodesWithTag("error_message")
            .fetchSemanticsNodes().isNotEmpty()
    }
}
```

### Accessibility

**Required checks:**
```kotlin
@Test
fun testAccessibility() {
    composeTestRule.setContent {
        IconButton(onClick = {}) {
            Icon(Icons.Default.Delete, contentDescription = "Delete item") // ✅
        }
    }

    // Check contentDescription
    composeTestRule.onNodeWithContentDescription("Delete item").assertExists()

    // Check semantic role
    composeTestRule.onNodeWithRole(Role.Button).assertHasClickAction()

    // Merged semantics for complex composables
    composeTestRule.onNode(
        hasText("Item") and hasClickAction(),
        useUnmergedTree = false // ✅ test merged tree
    ).assertExists()
}
```

---

## Follow-ups

- How to test navigation with NavHost and nested destinations?
- How to mock ViewModel dependencies in Compose tests?
- How to test complex state machines and side effects?
- How to test custom Modifier chains and layout behavior?
- What are best practices for testing merged vs unmerged semantic trees?
- How to handle flaky tests in CI/CD environments?

## References

- [[c-accessibility]] — Accessibility fundamentals
- [[c-ui-testing]] — UI testing principles
- [[c-testing-pyramid]] — Testing strategy
- [Compose Testing Guide](https://developer.android.com/jetpack/compose/testing)
- [Semantics in Compose](https://developer.android.com/jetpack/compose/semantics)

## Related Questions

### Prerequisites (Easier)
- [[q-compose-testing--android--medium]] — Basic Compose testing
- [[q-compose-semantics--android--medium]] — Semantic tree fundamentals

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]] — Performance testing
- Test isolation strategies for large Compose apps

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]] — Compiler internals
- Custom semantic properties for domain-specific testing


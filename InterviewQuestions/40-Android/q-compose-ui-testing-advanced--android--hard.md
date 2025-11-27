---
id: android-471
title: Advanced Compose UI Testing / Продвинутое тестирование Compose UI
aliases: [Advanced Compose UI Testing, Продвинутое тестирование Compose UI]
topic: android
subtopics:
  - testing-ui
  - ui-compose
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
sources: []
status: draft
related:
  - c-accessibility
  - q-compose-semantics--android--medium
  - q-compose-side-effects-advanced--android--hard
  - q-compose-testing--android--medium
created: 2025-10-20
updated: 2025-11-10
tags: [accessibility, android/testing-ui, android/ui-compose, compose-testing, difficulty/hard, semantics]
moc: moc-android

date created: Saturday, November 1st 2025, 1:26:08 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
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

## Дополнительные Вопросы (RU)

- Как тестировать навигацию в Compose с вложенными destination?
- Как мокать зависимости `ViewModel` в тестах Compose?
- Как тестировать поведение прокрутки LazyColumn и видимость элементов?
- Как обрабатывать нестабильность тестов, вызванную анимациями и задержками?
- Как тестировать цепочки `Modifier` и измерения layout?

## Ссылки (RU)

- [[c-accessibility]] — Практики доступности
- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/jetpack/compose/semantics

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-compose-testing--android--medium]] — Базовая настройка тестов Compose и matchers
- [[q-compose-semantics--android--medium]] — Понимание структуры semantic tree

### На Том Же Уровне
- [[q-compose-performance-optimization--android--hard]] — Тестирование производительности и профилирование

### Продвинутые (сложнее)
- [[q-compose-compiler-plugin--android--hard]] — Внутреннее устройство компилятора и оптимизации

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

## Follow-ups

- How to test navigation in Compose with nested destinations?
- How to mock `ViewModel` dependencies in Compose tests?
- How to test LazyColumn scroll behavior and item visibility?
- How to handle test flakiness caused by animations and delays?
- How to test custom `Modifier` chains and layout measurements?

## References

- [[c-accessibility]] — Accessibility best practices
- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/jetpack/compose/semantics

## Related Questions

### Prerequisites (Easier)
- [[q-compose-testing--android--medium]] — Basic Compose testing setup and matchers
- [[q-compose-semantics--android--medium]] — Understanding semantic tree structure

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]] — Performance testing and profiling

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]] — Compiler internals and optimization

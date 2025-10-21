---
id: 20251020-210000
title: "Advanced Compose UI Testing / Продвинутое тестирование Compose UI"
aliases: [Advanced Compose UI Testing, Продвинутое тестирование Compose UI]
topic: testing
subtopics: [testing-ui, accessibility]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/jetpack/compose/testing
source_note: Official Compose testing documentation
related: [q-compose-testing--android--medium, q-compose-semantics--android--medium, q-compose-performance-optimization--android--hard]
created: 2025-10-20
updated: 2025-10-20
tags: [testing, compose-testing, ui-testing, semantics, accessibility, difficulty/hard]
moc: moc-testing
---

# Question (EN)
> How to test complex Compose UI scenarios including animations, gestures, semantic matchers, and accessibility? How to handle async operations in Compose tests?

# Вопрос (RU)
> Как тестировать сложные UI сценарии в Compose включая анимации, жесты, semantic matchers и доступность? Как обрабатывать async операции в тестах Compose?

---

## Answer (EN)

**Advanced Compose Testing** extends basic testing with complex scenarios, custom matchers, and async handling. Uses semantic tree for robust element identification.

### ComposeTestRule

**ComposeTestRule** provides advanced testing capabilities:
- `setContent {}` - Set composable content
- `onNode...()` - Find single element
- `onAllNodes...()` - Find multiple elements
- `waitForIdle()` - Wait for recomposition
- `mainClock` - Control time for animations

### Theory & Approaches

- Test via semantics, not layout tree: rely on roles, contentDescription, and test tags
- Prefer behavior assertions over structure: assert text, state, and actions, not implementation details
- Control time deterministically: pause auto-advancing clock and advance `mainClock` for animations
- Isolate state updates: make effects deterministic; expose stable tags for transient UI
- Synchronize with async: use `waitUntil {}` and `runOnIdle {}` instead of sleeps
- Design for testability: provide DI seams and fake data sources; avoid random delays in UI
- Flaky-proofing: wait for conditions, avoid racing recomposition and assertions
- Accessibility-first: assert roles, actions, and content descriptions; test merged semantics

### Semantic Matchers

**Custom semantic matchers:**

```kotlin
// Custom matcher for specific state
fun hasCustomState(expectedState: String): SemanticsMatcher {
    return SemanticsMatcher.expectValue(
        SemanticsProperties.Custom,
        expectedState
    )
}

// Usage
composeTestRule.onNode(hasCustomState("loading"))
    .assertExists()
```

**Role-based matchers:**

```kotlin
composeTestRule.onNodeWithRole(Role.Button).assertExists()
composeTestRule.onNodeWithRole(Role.Checkbox).assertExists()
composeTestRule.onNodeWithRole(Role.Switch).assertExists()
```

### Testing Animations

**Control animation timing:**

```kotlin
@Test
fun animationTest() {
    composeTestRule.setContent {
        AnimatedVisibility(visible = true) {
            Text("Animated Text")
        }
    }

    // Fast forward animations
    composeTestRule.mainClock.advanceTimeBy(1000)

    composeTestRule.onNodeWithText("Animated Text")
        .assertIsDisplayed()
}
```

**Test animation states:**

```kotlin
@Test
fun animationStates() {
    var isVisible by remember { mutableStateOf(false) }

    composeTestRule.setContent {
        AnimatedVisibility(visible = isVisible) {
            Text("Content")
        }
        Button(onClick = { isVisible = true }) {
            Text("Show")
        }
    }

    // Initially hidden
    composeTestRule.onNodeWithText("Content").assertDoesNotExist()

    // Trigger animation
    composeTestRule.onNodeWithText("Show").performClick()

    // Wait for animation
    composeTestRule.mainClock.advanceTimeBy(500)

    // Now visible
    composeTestRule.onNodeWithText("Content").assertIsDisplayed()
}
```

### Testing Gestures

**Swipe gestures:**

```kotlin
@Test
fun swipeGesture() {
    composeTestRule.setContent {
        SwipeableBox()
    }

    composeTestRule.onNodeWithTag("swipeable")
        .performTouchInput {
            swipeLeft()
        }

    composeTestRule.onNodeWithText("Swiped Left").assertExists()
}
```

**Drag and drop:**

```kotlin
@Test
fun dragAndDrop() {
    composeTestRule.setContent {
        DragDropList()
    }

    composeTestRule.onNodeWithTag("item_1")
        .performTouchInput {
            down(center)
            moveTo(offset = Offset(0f, 200f))
            up()
        }

    composeTestRule.onNodeWithText("Item moved").assertExists()
}
```

### Testing Async Operations

**Wait for async data:**

```kotlin
@Test
fun asyncDataLoading() {
    composeTestRule.setContent {
        AsyncDataScreen()
    }

    // Initially loading
    composeTestRule.onNodeWithTag("loading").assertExists()

    // Wait for data to load
    composeTestRule.waitUntil(timeoutMillis = 5000) {
        composeTestRule.onAllNodesWithTag("data_item")
            .fetchSemanticsNodes().isNotEmpty()
    }

    // Verify loaded data
    composeTestRule.onNodeWithTag("data_item").assertExists()
}
```

**Test error states:**

```kotlin
@Test
fun errorStateHandling() {
    composeTestRule.setContent {
        ErrorHandlingScreen()
    }

    // Trigger error
    composeTestRule.onNodeWithTag("error_button").performClick()

    // Wait for error state
    composeTestRule.waitUntil {
        composeTestRule.onAllNodesWithTag("error_message")
            .fetchSemanticsNodes().isNotEmpty()
    }

    // Verify error message
    composeTestRule.onNodeWithTag("error_message")
        .assertTextEquals("Something went wrong")
}
```

### Accessibility Testing

**Test content descriptions:**

```kotlin
@Test
fun accessibilityContentDescription() {
    composeTestRule.setContent {
        Image(
            painter = painterResource(R.drawable.icon),
            contentDescription = "User profile"
        )
    }

    composeTestRule.onNodeWithContentDescription("User profile")
        .assertExists()
}
```

**Test semantic roles:**

```kotlin
@Test
fun accessibilityRoles() {
    composeTestRule.setContent {
        Button(onClick = {}) { Text("Submit") }
        Checkbox(checked = false, onCheckedChange = {})
    }

    composeTestRule.onNodeWithRole(Role.Button)
        .assertHasClickAction()

    composeTestRule.onNodeWithRole(Role.Checkbox)
        .assertIsNotChecked()
}
```

### Best Practices

1. **Use testTag** for stable element identification
2. **Test user interactions**, not implementation details
3. **Handle async operations** with proper waiting
4. **Test accessibility** features and semantic roles
5. **Control animations** with mainClock for deterministic tests
6. **Use custom matchers** for complex scenarios
7. **Keep tests focused** on specific user flows

---

## Ответ (RU)

**Продвинутое тестирование Compose** расширяет базовое тестирование сложными сценариями, пользовательскими matchers и обработкой асинхронности. Использует semantic tree для надежной идентификации элементов.

### ComposeTestRule

**ComposeTestRule** предоставляет продвинутые возможности тестирования:
- `setContent {}` - Установить composable контент
- `onNode...()` - Найти один элемент
- `onAllNodes...()` - Найти несколько элементов
- `waitForIdle()` - Ждать рекомпозицию
- `mainClock` - Контролировать время для анимаций

### Теория и подходы

- Тестируйте через семантику, а не дерево layout: роли, contentDescription, testTag
- Утверждайте поведение, а не структуру: текст, состояние и действия, без деталей реализации
- Делайте время детерминированным: останавливайте авто‑таймер и продвигайте `mainClock`
- Изолируйте обновления состояния: делайте эффекты детерминированными; давайте стабильные теги для переходных состояний
- Синхронизируйтесь с асинхронностью: используйте `waitUntil {}` и `runOnIdle {}` вместо «снов»
- Проектируйте под тестирование: DI‑стыки и фэйковые источники; без случайных задержек в UI
- Борьба с флаками: ждите условий, избегайте гонок между рекомпозицией и проверками
- Сначала доступность: проверяйте роли, действия и content descriptions; тестируйте merge semantics

### Semantic Matchers

**Пользовательские semantic matchers:**

```kotlin
// Пользовательский matcher для конкретного состояния
fun hasCustomState(expectedState: String): SemanticsMatcher {
    return SemanticsMatcher.expectValue(
        SemanticsProperties.Custom,
        expectedState
    )
}

// Использование
composeTestRule.onNode(hasCustomState("loading"))
    .assertExists()
```

**Matchers по ролям:**

```kotlin
composeTestRule.onNodeWithRole(Role.Button).assertExists()
composeTestRule.onNodeWithRole(Role.Checkbox).assertExists()
composeTestRule.onNodeWithRole(Role.Switch).assertExists()
```

### Тестирование анимаций

**Контроль времени анимации:**

```kotlin
@Test
fun animationTest() {
    composeTestRule.setContent {
        AnimatedVisibility(visible = true) {
            Text("Animated Text")
        }
    }

    // Ускорить анимации
    composeTestRule.mainClock.advanceTimeBy(1000)

    composeTestRule.onNodeWithText("Animated Text")
        .assertIsDisplayed()
}
```

**Тестирование состояний анимации:**

```kotlin
@Test
fun animationStates() {
    var isVisible by remember { mutableStateOf(false) }

    composeTestRule.setContent {
        AnimatedVisibility(visible = isVisible) {
            Text("Content")
        }
        Button(onClick = { isVisible = true }) {
            Text("Show")
        }
    }

    // Изначально скрыто
    composeTestRule.onNodeWithText("Content").assertDoesNotExist()

    // Запустить анимацию
    composeTestRule.onNodeWithText("Show").performClick()

    // Ждать анимацию
    composeTestRule.mainClock.advanceTimeBy(500)

    // Теперь видимо
    composeTestRule.onNodeWithText("Content").assertIsDisplayed()
}
```

### Тестирование жестов

**Жесты свайпа:**

```kotlin
@Test
fun swipeGesture() {
    composeTestRule.setContent {
        SwipeableBox()
    }

    composeTestRule.onNodeWithTag("swipeable")
        .performTouchInput {
            swipeLeft()
        }

    composeTestRule.onNodeWithText("Swiped Left").assertExists()
}
```

**Перетаскивание:**

```kotlin
@Test
fun dragAndDrop() {
    composeTestRule.setContent {
        DragDropList()
    }

    composeTestRule.onNodeWithTag("item_1")
        .performTouchInput {
            down(center)
            moveTo(offset = Offset(0f, 200f))
            up()
        }

    composeTestRule.onNodeWithText("Item moved").assertExists()
}
```

### Тестирование async операций

**Ждать async данные:**

```kotlin
@Test
fun asyncDataLoading() {
    composeTestRule.setContent {
        AsyncDataScreen()
    }

    // Изначально загрузка
    composeTestRule.onNodeWithTag("loading").assertExists()

    // Ждать загрузку данных
    composeTestRule.waitUntil(timeoutMillis = 5000) {
        composeTestRule.onAllNodesWithTag("data_item")
            .fetchSemanticsNodes().isNotEmpty()
    }

    // Проверить загруженные данные
    composeTestRule.onNodeWithTag("data_item").assertExists()
}
```

**Тестирование состояний ошибок:**

```kotlin
@Test
fun errorStateHandling() {
    composeTestRule.setContent {
        ErrorHandlingScreen()
    }

    // Вызвать ошибку
    composeTestRule.onNodeWithTag("error_button").performClick()

    // Ждать состояние ошибки
    composeTestRule.waitUntil {
        composeTestRule.onAllNodesWithTag("error_message")
            .fetchSemanticsNodes().isNotEmpty()
    }

    // Проверить сообщение об ошибке
    composeTestRule.onNodeWithTag("error_message")
        .assertTextEquals("Something went wrong")
}
```

### Тестирование доступности

**Тестирование content descriptions:**

```kotlin
@Test
fun accessibilityContentDescription() {
    composeTestRule.setContent {
        Image(
            painter = painterResource(R.drawable.icon),
            contentDescription = "User profile"
        )
    }

    composeTestRule.onNodeWithContentDescription("User profile")
        .assertExists()
}
```

**Тестирование семантических ролей:**

```kotlin
@Test
fun accessibilityRoles() {
    composeTestRule.setContent {
        Button(onClick = {}) { Text("Submit") }
        Checkbox(checked = false, onCheckedChange = {})
    }

    composeTestRule.onNodeWithRole(Role.Button)
        .assertHasClickAction()

    composeTestRule.onNodeWithRole(Role.Checkbox)
        .assertIsNotChecked()
}
```

### Лучшие практики

1. **Используйте testTag** для стабильной идентификации элементов
2. **Тестируйте взаимодействия пользователя**, не детали реализации
3. **Обрабатывайте async операции** с правильным ожиданием
4. **Тестируйте accessibility** функции и семантические роли
5. **Контролируйте анимации** с mainClock для детерминированных тестов
6. **Используйте пользовательские matchers** для сложных сценариев
7. **Держите тесты сфокусированными** на конкретных пользовательских потоках

---

## Follow-ups

- How to test complex navigation flows in Compose?
- What are the differences between unit tests and UI tests?
- How to mock ViewModels and dependencies in Compose tests?
- How to test custom composables with complex state?
- What are the performance implications of advanced Compose testing?

## References

- [Compose Testing Guide](https://developer.android.com/jetpack/compose/testing)
- [Compose Testing Semantics](https://developer.android.com/jetpack/compose/testing/semantics)

## Related Questions

### Prerequisites (Easier)

- [[q-compose-testing--android--medium]]
- [[q-compose-semantics--android--medium]]

### Related (Same Level)

- [[q-compose-performance-optimization--android--hard]]
- [[q-compose-modifier-system--android--medium]]

### Advanced (Harder)

- [[q-compose-compiler-plugin--jetpack-compose--hard]]
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]]

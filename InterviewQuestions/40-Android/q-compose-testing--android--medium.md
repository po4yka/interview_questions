---
id: 20251020-190000
title: Compose Testing / Тестирование Compose
aliases:
- Compose Testing
- Тестирование Compose
topic: android
subtopics:
- ui-compose
- testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-compose-performance-optimization--android--hard
- q-compose-semantics--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/ui-compose
- android/testing-unit
- difficulty/medium
source: https://developer.android.com/jetpack/compose/testing
source_note: Official Compose testing documentation
---

# Вопрос (RU)
> Тестирование Compose?

# Question (EN)
> Compose Testing?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

**Compose Testing** uses semantic tree (not View hierarchy) to find and interact with UI elements. Tests run synchronously while Compose handles recomposition. See also c-compose-state and c-testing-pyramid.

### ComposeTestRule

**ComposeTestRule** is the main testing utility for Compose UI tests. It provides:
- `setContent {}` - Set composable content for testing
- `onNode...()` - Find single UI element
- `onAllNodes...()` - Find multiple UI elements
- `waitForIdle()` - Wait for recomposition to complete
- `mainClock` - Control time for animations

### Setup

Create test class:

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_displaysCorrectly() {
        composeTestRule.setContent {
            LoginScreen()
        }
        // Assertions here
    }
}
```

### Finding Elements

**By text:**
```kotlin
composeTestRule.onNodeWithText("Welcome").assertExists()
```

**By test tag (recommended):**
```kotlin
Button(modifier = Modifier.testTag("login_button")) { Text("Login") }
composeTestRule.onNodeWithTag("login_button").assertExists()
```

**By content description:**
```kotlin
Image(contentDescription = "User avatar")
composeTestRule.onNodeWithContentDescription("User avatar").assertExists()
```

### User Interactions

**Click:**
```kotlin
composeTestRule.onNodeWithTag("button").performClick()
```

**Text input:**
```kotlin
composeTestRule.onNodeWithTag("text_field").performTextInput("Hello")
```

**Scroll:**
```kotlin
composeTestRule.onNodeWithTag("scrollable").performScrollToNode(hasText("Bottom"))
```

### Assertions

**Existence:**
```kotlin
composeTestRule.onNodeWithTag("button").assertExists()
composeTestRule.onNodeWithTag("button").assertDoesNotExist()
```

**Text:**
```kotlin
composeTestRule.onNodeWithTag("text").assertTextEquals("Expected")
```

**State:**
```kotlin
composeTestRule.onNodeWithTag("checkbox").assertIsSelected()
composeTestRule.onNodeWithTag("button").assertIsEnabled()
```

### Testing State Changes

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count", modifier = Modifier.testTag("count"))
        Button(
            onClick = { count++ },
            modifier = Modifier.testTag("increment")
        ) {
            Text("+")
        }
    }
}

@Test
fun counter_increments() {
    composeTestRule.setContent { Counter() }

    composeTestRule.onNodeWithTag("count").assertTextEquals("Count: 0")
    composeTestRule.onNodeWithTag("increment").performClick()
    composeTestRule.onNodeWithTag("count").assertTextEquals("Count: 1")
}
```

### Testing Async Operations

```kotlin
@Test
fun asyncData_loading() {
    composeTestRule.setContent {
        AsyncDataScreen()
    }

    // Initially loading
    composeTestRule.onNodeWithTag("loading").assertExists()

    // Wait for data
    composeTestRule.waitUntil(timeoutMillis = 2000) {
        composeTestRule.onAllNodesWithTag("data").fetchSemanticsNodes().isNotEmpty()
    }

    // Data loaded
    composeTestRule.onNodeWithTag("data").assertExists()
}
```

### Best Practices

1. **Use testTag** for stable element identification
2. **Test behavior, not implementation** - focus on user interactions
3. **Keep tests simple** - one concept per test
4. **Mock dependencies** - use fake implementations for ViewModels
5. **Test accessibility** - ensure content descriptions are present

---

## Follow-ups

- How to test custom composables?
- What are the differences between unit tests and UI tests?
- How to test navigation in Compose?
- How to mock ViewModels in tests?
- What are the performance implications of Compose testing?

## References

- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/jetpack/compose/testing/semantics

## Related Questions

### Prerequisites (Easier)
- [[q-compose-semantics--android--medium]]

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]]
- [[q-compose-modifier-system--android--medium]]

### Advanced (Harder)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]

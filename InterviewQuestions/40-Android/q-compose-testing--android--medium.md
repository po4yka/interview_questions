---
id: 20251020-190000
title: Compose Testing / Тестирование Compose
aliases: ["Compose Testing", "Тестирование Compose"]
topic: android
subtopics: [testing-unit, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-performance-optimization--android--hard, q-compose-semantics--android--medium]
created: 2025-10-20
updated: 2025-10-27
tags: [android/testing-unit, android/ui-compose, difficulty/medium]
sources: [https://developer.android.com/jetpack/compose/testing]
---
# Вопрос (RU)
> Как тестировать Compose UI? Какие основные подходы и инструменты?

# Question (EN)
> How to test Compose UI? What are the main approaches and tools?

---

## Ответ (RU)

**Compose Testing** использует семантическое дерево (не View иерархию) для поиска и взаимодействия с UI элементами. Тесты выполняются синхронно, Compose автоматически ожидает рекомпозиции.

### ComposeTestRule

Основной инструмент тестирования, обеспечивает синхронизацию с Compose runtime:

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_click_triggersAuth() {
        composeTestRule.setContent { LoginScreen() }

        composeTestRule.onNodeWithTag("login_btn").performClick()
        // ✅ Автоматически ждет recomposition
        composeTestRule.onNodeWithTag("progress").assertExists()
    }
}
```

### Поиск элементов

**testTag** (рекомендуется - стабилен к рефакторингу):
```kotlin
Button(modifier = Modifier.testTag("submit")) { /* ... */ }
composeTestRule.onNodeWithTag("submit").performClick()
```

**По тексту** (хрупкий - зависит от локализации):
```kotlin
composeTestRule.onNodeWithText("Submit").performClick() // ❌ Сломается при переводе
```

**По семантике** (лучше для a11y):
```kotlin
Icon(contentDescription = "Close")
composeTestRule.onNodeWithContentDescription("Close").performClick()
```

### Взаимодействия

```kotlin
// Ввод текста
composeTestRule.onNodeWithTag("email_field")
    .performTextInput("test@example.com")

// Scroll до элемента
composeTestRule.onNodeWithTag("list")
    .performScrollToNode(hasText("Item 50"))

// Проверка состояния
composeTestRule.onNodeWithTag("checkbox")
    .assertIsSelected()
    .assertIsEnabled()
```

### Тестирование State и Recomposition

```kotlin
@Test
fun stateChange_triggersRecomposition() {
    var counter by mutableStateOf(0)

    composeTestRule.setContent {
        Button(onClick = { counter++ }) {
            Text("Clicks: $counter") // ✅ Автоматически recompose
        }
    }

    composeTestRule.onNodeWithText("Clicks: 0").assertExists()
    composeTestRule.onNodeWithText("Clicks: 0").performClick()
    // ✅ Ждет recomposition, затем проверяет
    composeTestRule.onNodeWithText("Clicks: 1").assertExists()
}
```

### Асинхронные операции

```kotlin
@Test
fun asyncLoading_showsDataWhenReady() {
    composeTestRule.setContent {
        DataScreen(viewModel) // ViewModel с coroutine scope
    }

    composeTestRule.onNodeWithTag("loading").assertExists()

    // ✅ Ждем появления элемента
    composeTestRule.waitUntil(timeoutMillis = 3000) {
        composeTestRule.onAllNodesWithTag("data_item")
            .fetchSemanticsNodes().isNotEmpty()
    }

    composeTestRule.onNodeWithTag("data_item").assertExists()
}
```

### Семантическое дерево

Compose строит дерево с семантическими свойствами (text, role, actions):

```kotlin
// ❌ НЕВЕРНО - элемент не найден в semantic tree
Image(painter = painterResource(R.drawable.logo))
composeTestRule.onNodeWithTag("logo").assertExists() // Fail!

// ✅ ВЕРНО - добавлена семантика
Image(
    painter = painterResource(R.drawable.logo),
    contentDescription = "App logo", // Семантика для a11y и тестов
    modifier = Modifier.testTag("logo")
)
```

## Answer (EN)

**Compose Testing** uses a semantic tree (not View hierarchy) to find and interact with UI elements. Tests run synchronously, Compose automatically awaits recomposition.

### ComposeTestRule

Main testing utility, provides synchronization with Compose runtime:

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_click_triggersAuth() {
        composeTestRule.setContent { LoginScreen() }

        composeTestRule.onNodeWithTag("login_btn").performClick()
        // ✅ Automatically waits for recomposition
        composeTestRule.onNodeWithTag("progress").assertExists()
    }
}
```

### Finding elements

**testTag** (recommended - refactoring-safe):
```kotlin
Button(modifier = Modifier.testTag("submit")) { /* ... */ }
composeTestRule.onNodeWithTag("submit").performClick()
```

**By text** (brittle - breaks with localization):
```kotlin
composeTestRule.onNodeWithText("Submit").performClick() // ❌ Breaks with i18n
```

**By semantics** (better for a11y):
```kotlin
Icon(contentDescription = "Close")
composeTestRule.onNodeWithContentDescription("Close").performClick()
```

### Interactions

```kotlin
// Text input
composeTestRule.onNodeWithTag("email_field")
    .performTextInput("test@example.com")

// Scroll to element
composeTestRule.onNodeWithTag("list")
    .performScrollToNode(hasText("Item 50"))

// Check state
composeTestRule.onNodeWithTag("checkbox")
    .assertIsSelected()
    .assertIsEnabled()
```

### Testing State and Recomposition

```kotlin
@Test
fun stateChange_triggersRecomposition() {
    var counter by mutableStateOf(0)

    composeTestRule.setContent {
        Button(onClick = { counter++ }) {
            Text("Clicks: $counter") // ✅ Auto-recompose
        }
    }

    composeTestRule.onNodeWithText("Clicks: 0").assertExists()
    composeTestRule.onNodeWithText("Clicks: 0").performClick()
    // ✅ Waits for recomposition, then asserts
    composeTestRule.onNodeWithText("Clicks: 1").assertExists()
}
```

### Async operations

```kotlin
@Test
fun asyncLoading_showsDataWhenReady() {
    composeTestRule.setContent {
        DataScreen(viewModel) // ViewModel with coroutine scope
    }

    composeTestRule.onNodeWithTag("loading").assertExists()

    // ✅ Wait for element to appear
    composeTestRule.waitUntil(timeoutMillis = 3000) {
        composeTestRule.onAllNodesWithTag("data_item")
            .fetchSemanticsNodes().isNotEmpty()
    }

    composeTestRule.onNodeWithTag("data_item").assertExists()
}
```

### Semantic tree

Compose builds a tree with semantic properties (text, role, actions):

```kotlin
// ❌ WRONG - element not in semantic tree
Image(painter = painterResource(R.drawable.logo))
composeTestRule.onNodeWithTag("logo").assertExists() // Fail!

// ✅ CORRECT - semantics added
Image(
    painter = painterResource(R.drawable.logo),
    contentDescription = "App logo", // Semantics for a11y and testing
    modifier = Modifier.testTag("logo")
)
```

---

## Follow-ups

- How to test LaunchedEffect and other side effects?
- How to handle time-based animations in tests (mainClock)?
- When to use unmerged vs merged semantic tree?
- How to test Compose Navigation?
- How to handle flaky tests with async state updates?

## References

- [[c-jetpack-compose]] - Compose fundamentals
- [[c-unit-testing]] - Testing principles
- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/jetpack/compose/testing/semantics

## Related Questions

### Prerequisites
- [[q-compose-remember-derived-state--android--medium]] - State in Compose
- [[c-jetpack-compose]] - Basic Compose concepts

### Related
- [[q-compose-semantics--android--medium]] - Semantic tree details
- [[q-testing-compose-ui--android--medium]] - UI testing patterns
- [[q-testing-viewmodels-turbine--android--medium]] - Testing ViewModels

### Advanced
- [[q-compose-performance-optimization--android--hard]] - Performance testing
- [[q-testing-coroutines-flow--android--hard]] - Testing async code

---
id: android-472
title: Compose Testing / Тестирование Compose
aliases: [Compose Testing, Тестирование Compose]
topic: android
subtopics:
  - testing-unit
  - ui-compose
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-jetpack-compose
  - c-unit-testing
  - q-compose-performance-optimization--android--hard
  - q-compose-semantics--android--medium
created: 2025-10-20
updated: 2025-10-30
tags: [android/testing-unit, android/ui-compose, compose, difficulty/medium, semantics, testing]
sources:
  - https://developer.android.com/jetpack/compose/testing
---

# Вопрос (RU)
> Как тестировать UI в Jetpack Compose? Какие основные инструменты и подходы используются?

# Question (EN)
> How to test UI in Jetpack Compose? What are the main tools and approaches?

---

## Ответ (RU)

**Compose Testing** использует семантическое дерево вместо View-иерархии. Тесты выполняются синхронно — фреймворк автоматически ожидает завершения recomposition.

### Ключевые Концепции

**ComposeTestRule** — центральная точка взаимодействия с Compose runtime:

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_click_triggersAuth() {
        composeTestRule.setContent { LoginScreen() }

        composeTestRule.onNodeWithTag("login_btn").performClick()
        // ✅ Автоматическое ожидание recomposition
        composeTestRule.onNodeWithTag("progress").assertExists()
    }
}
```

**Семантическое дерево** — структура из узлов с метаданными (text, role, actions). Элементы без семантики (например, декоративные Image) невидимы для тестов.

### Стратегии Поиска Элементов

**testTag** (предпочтительно — устойчив к рефакторингу):
```kotlin
Button(modifier = Modifier.testTag("submit")) { Text("Отправить") }
composeTestRule.onNodeWithTag("submit").performClick()
```

**Текст** (хрупко — зависит от локализации):
```kotlin
composeTestRule.onNodeWithText("Submit").performClick()
// ❌ Сломается при переводе на русский
```

**Семантика** (лучший выбор для accessibility):
```kotlin
Icon(contentDescription = "Закрыть")
composeTestRule.onNodeWithContentDescription("Закрыть").performClick()
```

### Взаимодействия И Проверки

```kotlin
// Ввод текста
composeTestRule.onNodeWithTag("email")
    .performTextInput("test@example.com")

// Scroll и проверка состояния
composeTestRule.onNodeWithTag("list")
    .performScrollToNode(hasText("Item 50"))
    .assertIsSelected()
```

### Тестирование State

```kotlin
@Test
fun stateChange_triggersRecomposition() {
    var counter by mutableStateOf(0)

    composeTestRule.setContent {
        Button(onClick = { counter++ }) {
            Text("Кликов: $counter") // ✅ Автоматический recompose
        }
    }

    composeTestRule.onNodeWithText("Кликов: 0").performClick()
    composeTestRule.onNodeWithText("Кликов: 1").assertExists()
}
```

### Асинхронные Операции

```kotlin
@Test
fun asyncData_appearsAfterLoad() {
    composeTestRule.setContent { DataScreen(viewModel) }

    composeTestRule.onNodeWithTag("loading").assertExists()

    // ✅ Ожидание появления элемента
    composeTestRule.waitUntil(timeoutMillis = 3000) {
        composeTestRule.onAllNodesWithTag("data_item")
            .fetchSemanticsNodes().isNotEmpty()
    }

    composeTestRule.onNodeWithTag("data_item").assertExists()
}
```

## Answer (EN)

**Compose Testing** uses a semantic tree instead of View hierarchy. Tests run synchronously — the framework automatically waits for recomposition to complete.

### Key Concepts

**ComposeTestRule** — central point for interacting with Compose runtime:

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_click_triggersAuth() {
        composeTestRule.setContent { LoginScreen() }

        composeTestRule.onNodeWithTag("login_btn").performClick()
        // ✅ Automatic recomposition wait
        composeTestRule.onNodeWithTag("progress").assertExists()
    }
}
```

**Semantic tree** — structure of nodes with metadata (text, role, actions). Elements without semantics (e.g., decorative Images) are invisible to tests.

### Element Finding Strategies

**testTag** (preferred — refactoring-safe):
```kotlin
Button(modifier = Modifier.testTag("submit")) { Text("Submit") }
composeTestRule.onNodeWithTag("submit").performClick()
```

**Text** (brittle — breaks with localization):
```kotlin
composeTestRule.onNodeWithText("Submit").performClick()
// ❌ Breaks when translated
```

**Semantics** (best for accessibility):
```kotlin
Icon(contentDescription = "Close")
composeTestRule.onNodeWithContentDescription("Close").performClick()
```

### Interactions and Assertions

```kotlin
// Text input
composeTestRule.onNodeWithTag("email")
    .performTextInput("test@example.com")

// Scroll and state check
composeTestRule.onNodeWithTag("list")
    .performScrollToNode(hasText("Item 50"))
    .assertIsSelected()
```

### Testing State

```kotlin
@Test
fun stateChange_triggersRecomposition() {
    var counter by mutableStateOf(0)

    composeTestRule.setContent {
        Button(onClick = { counter++ }) {
            Text("Clicks: $counter") // ✅ Auto-recompose
        }
    }

    composeTestRule.onNodeWithText("Clicks: 0").performClick()
    composeTestRule.onNodeWithText("Clicks: 1").assertExists()
}
```

### Async Operations

```kotlin
@Test
fun asyncData_appearsAfterLoad() {
    composeTestRule.setContent { DataScreen(viewModel) }

    composeTestRule.onNodeWithTag("loading").assertExists()

    // ✅ Wait for element to appear
    composeTestRule.waitUntil(timeoutMillis = 3000) {
        composeTestRule.onAllNodesWithTag("data_item")
            .fetchSemanticsNodes().isNotEmpty()
    }

    composeTestRule.onNodeWithTag("data_item").assertExists()
}
```

---

## Follow-ups

- How to test LaunchedEffect and other side effects in Compose?
- When should you use unmerged vs merged semantic tree?
- How to handle time-based animations in tests using mainClock?
- How to test Navigation Compose and deep links?
- What are best practices for testing Compose with ViewModels?

## References

- [[c-jetpack-compose]] - Compose fundamentals and architecture
- [[c-unit-testing]] - General testing principles
- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/jetpack/compose/testing/semantics

## Related Questions

### Prerequisites
- [[c-jetpack-compose]] - Understanding Compose basics required

### Related
- [[q-compose-semantics--android--medium]] - Detailed semantic tree explanation
- [[q-testing-viewmodels-turbine--android--medium]] - Testing ViewModels with Turbine
- [[q-compose-remember-derived-state--android--medium]] - State patterns in Compose

### Advanced
- [[q-compose-performance-optimization--android--hard]] - Performance testing strategies
- [[q-testing-coroutines-flow--android--hard]] - Testing async Compose code

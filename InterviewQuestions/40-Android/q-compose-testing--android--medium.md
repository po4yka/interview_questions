---id: android-472
title: Compose Testing / Тестирование Compose
aliases: [Compose Testing, Тестирование Compose]
topic: android
subtopics: [testing-ui, ui-compose]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-testing, c-compose-recomposition, c-recomposition, q-accessibility-compose--android--medium, q-compose-performance-optimization--android--hard, q-compose-semantics--android--medium, q-compose-ui-testing-advanced--android--hard]
created: 2024-10-20
updated: 2025-11-10
tags: [android/testing-ui, android/ui-compose, difficulty/medium, semantics, testing]
sources:
  - "https://developer.android.com/jetpack/compose/testing"

---
# Вопрос (RU)
> Как тестировать UI в Jetpack Compose? Какие основные инструменты и подходы используются?

# Question (EN)
> How to test UI in Jetpack Compose? What are the main tools and approaches?

---

## Ответ (RU)

**Compose Testing** использует семантическое дерево вместо `View`-иерархии. Тестовый фреймворк синхронизирует выполнение с Compose runtime и основным потоком/Looper: он автоматически ждёт завершения композиции/рекомпозиции и задач на `Dispatchers.Main`, но не произвольных фоновых потоков или корутин.

См. также [[c-android-testing]].

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
        // Автоматическое ожидание стабильного состояния Compose / главного потока
        composeTestRule.onNodeWithTag("progress").assertExists()
    }
}
```

(В интеграционных/инструментальных тестах для экранов, зависящих от `Activity`/ресурсов Android, используют `createAndroidComposeRule<YourActivity>()`).

**Семантическое дерево** — структура из узлов с метаданными (text, role, actions). Элементы без семантики (например, декоративные Image) не попадают в доступное для поиска дерево, пока им явно не заданы семантики (или они не входят в состав элементов с объединённой семантикой).

### Стратегии Поиска Элементов

**testTag** (предпочтительно — устойчив к рефакторингу):
```kotlin
Button(modifier = Modifier.testTag("submit")) { Text("Отправить") }
composeTestRule.onNodeWithTag("submit").performClick()
```

**Текст** (хрупко — зависит от локализации):
```kotlin
composeTestRule.onNodeWithText("Submit").performClick()
// Сломается после перевода строки
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

// Scroll и проверка состояния узла
composeTestRule.onNodeWithTag("list")
    .performScrollToNode(hasText("Item 50"))
    .assertIsSelected()
```

### Тестирование State

```kotlin
@Test
fun stateChange_triggersRecomposition() {
    composeTestRule.setContent {
        var counter by remember { mutableStateOf(0) }

        Button(onClick = { counter++ }) {
            Text("Кликов: $counter")
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

    // Явное ожидание появления данных; фоновые операции сами по себе не отслеживаются
    composeTestRule.waitUntil(timeoutMillis = 3000) {
        composeTestRule.onAllNodesWithTag("data_item")
            .fetchSemanticsNodes(atLeastOneExpected = false)
            .isNotEmpty()
    }

    composeTestRule.onNodeWithTag("data_item").assertExists()
}
```

## Answer (EN)

**Compose Testing** uses a semantic tree instead of a `View` hierarchy. The test framework synchronizes with the Compose runtime and the main thread/looper: it automatically waits for composition/recomposition and work scheduled on `Dispatchers.Main`, but not for arbitrary background threads or coroutines.

See also [[c-android-testing]].

### Key Concepts

**ComposeTestRule** — central point for interacting with the Compose runtime:

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_click_triggersAuth() {
        composeTestRule.setContent { LoginScreen() }

        composeTestRule.onNodeWithTag("login_btn").performClick()
        // Automatic waiting for stable Compose / main thread state
        composeTestRule.onNodeWithTag("progress").assertExists()
    }
}
```

(For instrumentation/integration tests that depend on `Activity`/Android resources, use `createAndroidComposeRule<YourActivity>()`).

**Semantic tree** — a structure of nodes with metadata (text, role, actions). Elements without semantics (e.g., decorative Images) are not exposed in the searchable tree unless given semantics explicitly (or included via merged semantics of their parents).

### Element Finding Strategies

**testTag** (preferred — refactoring-safe):
```kotlin
Button(modifier = Modifier.testTag("submit")) { Text("Submit") }
composeTestRule.onNodeWithTag("submit").performClick()
```

**Text** (brittle — breaks with localization):
```kotlin
composeTestRule.onNodeWithText("Submit").performClick()
// Breaks when translated
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
    composeTestRule.setContent {
        var counter by remember { mutableStateOf(0) }

        Button(onClick = { counter++ }) {
            Text("Clicks: $counter")
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

    // Explicitly wait for data to appear; background work is not auto-tracked
    composeTestRule.waitUntil(timeoutMillis = 3000) {
        composeTestRule.onAllNodesWithTag("data_item")
            .fetchSemanticsNodes(atLeastOneExpected = false)
            .isNotEmpty()
    }

    composeTestRule.onNodeWithTag("data_item").assertExists()
}
```

---

## Дополнительные Вопросы (RU)

- Как тестировать `LaunchedEffect` и другие побочные эффекты в Compose?
- Когда использовать немёрдженное vs мёрдженное семантическое дерево?
- Как обрабатывать анимации, зависящие от времени, в тестах с использованием `mainClock`?
- Как тестировать Navigation Compose и deep links?
- Каковы лучшие практики тестирования Compose с `ViewModel`?

## Follow-ups

- How to test `LaunchedEffect` and other side effects in Compose?
- When should you use unmerged vs merged semantic tree?
- How to handle time-based animations in tests using `mainClock`?
- How to test Navigation Compose and deep links?
- What are best practices for testing Compose with `ViewModel`s?

## Ссылки (RU)

- "https://developer.android.com/jetpack/compose/testing"
- "https://developer.android.com/jetpack/compose/testing/semantics"

## References

- https://developer.android.com/jetpack/compose/testing
- https://developer.android.com/jetpack/compose/testing/semantics

## Связанные Вопросы (RU)

### Предпосылки

- [[q-compose-semantics--android--medium]]

### Похожие

- [[q-compose-remember-derived-state--android--medium]]

### Продвинутые

- [[q-compose-performance-optimization--android--hard]]

## Related Questions

### Prerequisites

- [[q-compose-semantics--android--medium]]

### Related

- [[q-compose-remember-derived-state--android--medium]]

### Advanced

- [[q-compose-performance-optimization--android--hard]]

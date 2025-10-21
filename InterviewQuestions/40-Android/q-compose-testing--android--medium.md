---
id: 20251020-190000
title: "Compose Testing / Тестирование Compose"
aliases: [Compose Testing, Тестирование Compose]
topic: android
subtopics: [ui-compose, testing]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/jetpack/compose/testing
source_note: Official Compose testing documentation
related: [c-compose-state, q-compose-performance-optimization--android--hard, q-compose-semantics--android--medium]
created: 2025-10-20
updated: 2025-10-20
tags: [android/ui-compose, android/testing, compose, testing, difficulty/medium]
moc: moc-android
---
# Вопрос (RU)
> Как тестировать UI в Jetpack Compose? Что такое ComposeTestRule, semantic matchers и как тестировать взаимодействия пользователя, изменения состояния и async операции?

# Question (EN)
> How to test UI in Jetpack Compose? What is ComposeTestRule, semantic matchers and how to test user interactions, state changes and async operations?

---

## Answer (EN)

**Compose Testing** uses semantic tree (not View hierarchy) to find and interact with UI elements. Tests run synchronously while Compose handles recomposition.

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

## Ответ (RU)

**Compose Testing** использует semantic tree (не View hierarchy) для поиска и взаимодействия с UI элементами. Тесты выполняются синхронно, пока Compose обрабатывает рекомпозицию.

### ComposeTestRule

**ComposeTestRule** - основной инструмент для тестирования Compose UI. Предоставляет:
- `setContent {}` - Установить composable контент для тестирования
- `onNode...()` - Найти один UI элемент
- `onAllNodes...()` - Найти несколько UI элементов
- `waitForIdle()` - Ждать завершения рекомпозиции
- `mainClock` - Контролировать время для анимаций

### Настройка

Создать тестовый класс:

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginScreen_displaysCorrectly() {
        composeTestRule.setContent {
            LoginScreen()
        }
        // Проверки здесь
    }
}
```

### Поиск элементов

**По тексту:**
```kotlin
composeTestRule.onNodeWithText("Welcome").assertExists()
```

**По test tag (рекомендуется):**
```kotlin
Button(modifier = Modifier.testTag("login_button")) { Text("Login") }
composeTestRule.onNodeWithTag("login_button").assertExists()
```

**По content description:**
```kotlin
Image(contentDescription = "User avatar")
composeTestRule.onNodeWithContentDescription("User avatar").assertExists()
```

### Взаимодействия пользователя

**Клик:**
```kotlin
composeTestRule.onNodeWithTag("button").performClick()
```

**Ввод текста:**
```kotlin
composeTestRule.onNodeWithTag("text_field").performTextInput("Hello")
```

**Скролл:**
```kotlin
composeTestRule.onNodeWithTag("scrollable").performScrollToNode(hasText("Bottom"))
```

### Проверки

**Существование:**
```kotlin
composeTestRule.onNodeWithTag("button").assertExists()
composeTestRule.onNodeWithTag("button").assertDoesNotExist()
```

**Текст:**
```kotlin
composeTestRule.onNodeWithTag("text").assertTextEquals("Expected")
```

**Состояние:**
```kotlin
composeTestRule.onNodeWithTag("checkbox").assertIsSelected()
composeTestRule.onNodeWithTag("button").assertIsEnabled()
```

### Тестирование изменений состояния

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

### Тестирование async операций

```kotlin
@Test
fun asyncData_loading() {
    composeTestRule.setContent {
        AsyncDataScreen()
    }

    // Изначально загрузка
    composeTestRule.onNodeWithTag("loading").assertExists()

    // Ждем данные
    composeTestRule.waitUntil(timeoutMillis = 2000) {
        composeTestRule.onAllNodesWithTag("data").fetchSemanticsNodes().isNotEmpty()
    }

    // Данные загружены
    composeTestRule.onNodeWithTag("data").assertExists()
}
```

### Лучшие практики

1. **Используйте testTag** для стабильной идентификации элементов
2. **Тестируйте поведение, не реализацию** - фокусируйтесь на взаимодействиях пользователя
3. **Держите тесты простыми** - одна концепция на тест
4. **Мокируйте зависимости** - используйте fake implementations для ViewModels
5. **Тестируйте accessibility** - убедитесь что content descriptions присутствуют

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
- [[q-compose-compiler-plugin--jetpack-compose--hard]]
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]]

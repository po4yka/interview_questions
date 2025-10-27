---
id: 20251012-122754
title: Accessibility Testing / Тестирование доступности
aliases: [Accessibility Testing, Тестирование доступности]
topic: android
subtopics:
  - testing-ui
  - ui-accessibility
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-accessibility-compose--android--medium
  - q-accessibility-talkback--android--medium
  - q-cicd-automated-testing--android--medium
created: 2025-10-11
updated: 2025-01-27
tags: [android/testing-ui, android/ui-accessibility, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Как тестировать доступность в Android-приложениях?

# Question (EN)
> How do you test accessibility in Android apps?

---

## Ответ (RU)

Тестирование доступности гарантирует, что приложение доступно людям с ограниченными возможностями. Android предоставляет инструменты для ручного и автоматизированного тестирования.

**Основные подходы:**

**1. Ручное тестирование с TalkBack**

Проверьте навигацию с включённым программой чтения экрана:
- Все интерактивные элементы должны быть доступны через свайп
- ContentDescription должен быть осмысленным (не "Image", а "User profile photo")
- Проверьте custom actions и live regions

**2. Accessibility Scanner**

Приложение от Google для автоматической проверки:
- Минимальный размер touch target: 48dp
- Контраст цветов (минимум 4.5:1 для текста)
- Читаемость текста

**3. Автоматизированное тестирование через Espresso**

```kotlin
@Test
fun testAccessibility() {
    // ✅ Включить проверки доступности для всех UI-действий
    AccessibilityChecks.enable()

    onView(withId(R.id.submit_button))
        .perform(click())

    // Тест упадёт, если найдены проблемы доступности
}

@Test
fun testContentDescription() {
    onView(withId(R.id.profile_image))
        .check { view, _ ->
            // ✅ Проверить наличие осмысленного описания
            assertThat(view.contentDescription).isNotEmpty()
            // ❌ Избегать общих описаний типа "Image"
            assertThat(view.contentDescription).isNotEqualTo("Image")
        }
}
```

**4. Тестирование Compose через семантику**

```kotlin
@Test
fun testSemanticProperties() {
    composeTestRule.setContent {
        Button(onClick = { }) {
            Text("Отправить")
        }
    }

    // ✅ Проверить семантические свойства
    composeTestRule
        .onNodeWithText("Отправить")
        .assertHasClickAction()
        .assertIsEnabled()
}

@Test
fun testStateDescription() {
    composeTestRule.setContent {
        Checkbox(
            checked = isChecked,
            onCheckedChange = { },
            modifier = Modifier.semantics {
                // ✅ Описать состояние для screen reader
                stateDescription = if (isChecked) "Выбрано" else "Не выбрано"
            }
        )
    }

    composeTestRule
        .onNode(hasStateDescription("Не выбрано"))
        .assertExists()
}
```

**Типичные ошибки доступности:**

```kotlin
// ❌ Отсутствует contentDescription
Image(
    painter = painterResource(R.drawable.icon),
    contentDescription = null
)

// ❌ Touch target меньше 48dp
IconButton(
    modifier = Modifier.size(24.dp),
    onClick = { }
) { Icon(Icons.Default.Close, "Close") }

// ❌ Недостаточный контраст
Text(
    text = "Read more",
    color = Color.LightGray,
    modifier = Modifier.background(Color.White)
)
```

**Лучшие практики:**

- Тестируйте на реальных устройствах (эмуляторы не всегда точны для TalkBack)
- Интегрируйте проверки доступности в CI/CD pipeline
- Тестируйте при разных настройках: масштаб шрифта, размер дисплея, высокая контрастность
- Используйте semantic testing вместо проверки implementation details

## Answer (EN)

Accessibility testing ensures apps are usable by people with disabilities. Android provides tools for manual and automated testing.

**Core Approaches:**

**1. Manual Testing with TalkBack**

Verify navigation with screen reader enabled:
- All interactive elements must be reachable via swipe
- ContentDescription should be meaningful (not "Image", but "User profile photo")
- Test custom actions and live regions

**2. Accessibility Scanner**

Google's app for automated checks:
- Minimum touch target size: 48dp
- Color contrast (minimum 4.5:1 for text)
- Text readability

**3. Automated Testing via Espresso**

```kotlin
@Test
fun testAccessibility() {
    // ✅ Enable accessibility checks for all UI actions
    AccessibilityChecks.enable()

    onView(withId(R.id.submit_button))
        .perform(click())

    // Test fails if accessibility issues found
}

@Test
fun testContentDescription() {
    onView(withId(R.id.profile_image))
        .check { view, _ ->
            // ✅ Verify meaningful description exists
            assertThat(view.contentDescription).isNotEmpty()
            // ❌ Avoid generic descriptions like "Image"
            assertThat(view.contentDescription).isNotEqualTo("Image")
        }
}
```

**4. Compose Testing via Semantics**

```kotlin
@Test
fun testSemanticProperties() {
    composeTestRule.setContent {
        Button(onClick = { }) {
            Text("Submit")
        }
    }

    // ✅ Verify semantic properties
    composeTestRule
        .onNodeWithText("Submit")
        .assertHasClickAction()
        .assertIsEnabled()
}

@Test
fun testStateDescription() {
    composeTestRule.setContent {
        Checkbox(
            checked = isChecked,
            onCheckedChange = { },
            modifier = Modifier.semantics {
                // ✅ Describe state for screen reader
                stateDescription = if (isChecked) "Selected" else "Not selected"
            }
        )
    }

    composeTestRule
        .onNode(hasStateDescription("Not selected"))
        .assertExists()
}
```

**Common Accessibility Issues:**

```kotlin
// ❌ Missing contentDescription
Image(
    painter = painterResource(R.drawable.icon),
    contentDescription = null
)

// ❌ Touch target smaller than 48dp
IconButton(
    modifier = Modifier.size(24.dp),
    onClick = { }
) { Icon(Icons.Default.Close, "Close") }

// ❌ Insufficient contrast
Text(
    text = "Read more",
    color = Color.LightGray,
    modifier = Modifier.background(Color.White)
)
```

**Best Practices:**

- Test on real devices (emulators aren't always accurate for TalkBack)
- Integrate accessibility checks into CI/CD pipeline
- Test with different settings: font scale, display size, high contrast
- Use semantic testing instead of checking implementation details

---

## Follow-ups

- How does `AccessibilityChecks.enable()` affect test execution time and CI pipeline performance?
- What semantic properties are required for custom Compose components to work with TalkBack?
- How do you test accessibility for dynamic content that updates via StateFlow or LiveData?
- What's the strategy for testing accessibility in multi-module projects with shared UI components?
- How to prioritize accessibility test coverage when test suite execution time is constrained?

## References

- [Android Accessibility Testing Guide](https://developer.android.com/guide/topics/ui/accessibility/testing)
- [Espresso Accessibility Checks](https://developer.android.com/training/testing/espresso/accessibility-checking)
- [Compose Semantics Testing](https://developer.android.com/jetpack/compose/testing)

## Related Questions

### Prerequisites
- [[q-testing-compose-ui--android--medium]] - Compose UI testing fundamentals

### Related (Medium)
- [[q-accessibility-compose--android--medium]] - Implementing accessibility in Compose
- [[q-accessibility-talkback--android--medium]] - TalkBack integration
- [[q-cicd-automated-testing--android--medium]] - CI/CD testing strategies
- [[q-compose-testing--android--medium]] - Compose testing patterns

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing async state updates for accessibility


---
id: 20251012-122754
title: Accessibility Testing / Тестирование доступности
aliases:
- Accessibility Testing
- Тестирование доступности
topic: android
subtopics:
- ui-accessibility
- testing-ui
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
updated: 2025-10-15
tags:
- android/ui-accessibility
- android/testing-ui
- difficulty/medium
---

# Question (EN)
> How do you test accessibility in Android apps?

# Вопрос (RU)
> Как тестировать доступность в Android-приложениях?

---

## Answer (EN)

Accessibility testing ensures that your app is usable by people with disabilities, including those using screen readers like TalkBack, voice control, or other assistive technologies. Android provides multiple tools and frameworks for both manual and automated accessibility testing.

**Testing Approaches:**

**1. Manual Testing with TalkBack**

Enable TalkBack and navigate your app:

```kotlin
// Test checklist:
// 1. Enable TalkBack: Settings > Accessibility > TalkBack
// 2. Navigate through all screens using swipe gestures
// 3. Verify all interactive elements are focusable
// 4. Check content descriptions are meaningful
// 5. Test custom actions work correctly
// 6. Verify live regions announce updates
```

**2. Accessibility Scanner**

Use Google's Accessibility Scanner app to identify issues:

- Download from Play Store
- Scan any screen in your app
- Review suggestions for improvements
- Fix issues related to:
  - Touch target size (minimum 48dp)
  - Content descriptions
  - Color contrast
  - Text size and readability

**3. Automated Testing with Espresso**

Test accessibility in UI tests using Espresso:

```kotlin
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testAccessibilityWithEspresso() {
        // Enable accessibility checks
        AccessibilityChecks.enable()

        // Perform UI actions - accessibility issues will fail the test
        onView(withId(R.id.submit_button))
            .perform(click())

        onView(withId(R.id.result_text))
            .check(matches(isDisplayed()))
    }

    @Test
    fun testContentDescriptions() {
        onView(withId(R.id.profile_image))
            .check { view, _ ->
                val contentDesc = view.contentDescription
                assertThat(contentDesc).isNotEmpty()
                assertThat(contentDesc).isNotEqualTo("Image")
            }
    }

    @Test
    fun testMinimumTouchTargetSize() {
        onView(withId(R.id.small_button))
            .check { view, _ ->
                val width = view.width
                val height = view.height
                val minSize = 48.dpToPx(view.context)

                assertThat(width).isAtLeast(minSize)
                assertThat(height).isAtLeast(minSize)
            }
    }
}

fun Int.dpToPx(context: Context): Int {
    return (this * context.resources.displayMetrics.density).toInt()
}
```

**4. Compose Testing**

Test accessibility in Jetpack Compose:

```kotlin
@RunWith(AndroidJUnit4::class)
class ComposeAccessibilityTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testSemanticProperties() {
        composeTestRule.setContent {
            Button(onClick = { }) {
                Text("Submit")
            }
        }

        // Verify semantics
        composeTestRule
            .onNodeWithText("Submit")
            .assertHasClickAction()
            .assertIsEnabled()
    }

    @Test
    fun testContentDescription() {
        composeTestRule.setContent {
            Icon(
                imageVector = Icons.Default.Delete,
                contentDescription = "Delete item"
            )
        }

        composeTestRule
            .onNodeWithContentDescription("Delete item")
            .assertExists()
    }

    @Test
    fun testMergedSemantics() {
        composeTestRule.setContent {
            Row(
                modifier = Modifier.semantics(mergeDescendants = true) {}
            ) {
                Icon(Icons.Default.Star, contentDescription = null)
                Text("Favorite")
            }
        }

        // Verify merged semantics reads as single node
        composeTestRule
            .onNodeWithText("Favorite")
            .assertExists()
    }

    @Test
    fun testStateDescription() {
        var isChecked by mutableStateOf(false)

        composeTestRule.setContent {
            Checkbox(
                checked = isChecked,
                onCheckedChange = { isChecked = it },
                modifier = Modifier.semantics {
                    stateDescription = if (isChecked) "Selected" else "Not selected"
                }
            )
        }

        composeTestRule
            .onNode(hasStateDescription("Not selected"))
            .assertExists()

        composeTestRule
            .onNode(hasClickAction())
            .performClick()

        composeTestRule
            .onNode(hasStateDescription("Selected"))
            .assertExists()
    }
}
```

**5. Custom Accessibility Checks**

Create custom matchers and assertions:

```kotlin
// Custom matcher for minimum touch target
fun hasMinimumTouchTarget(): SemanticsMatcher {
    return SemanticsMatcher("has minimum 48dp touch target") { node ->
        val bounds = node.boundsInRoot
        val width = bounds.width
        val height = bounds.height
        width >= 48f && height >= 48f
    }
}

// Usage
composeTestRule
    .onNodeWithText("Small button")
    .assert(hasMinimumTouchTarget())
```

**6. Automated Accessibility Testing in CI/CD**

Integrate accessibility tests into CI pipeline:

```yaml
# .github/workflows/accessibility-tests.yml
name: Accessibility Tests

on: [pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run accessibility tests
        run: ./gradlew connectedAndroidTest

      - name: Upload accessibility reports
        uses: actions/upload-artifact@v3
        with:
          name: accessibility-reports
          path: app/build/reports/androidTests/
```

**Best Practices:**

- **Test with real devices**: Emulators may not accurately reflect TalkBack behavior
- **Test all user flows**: Ensure complete app navigation is accessible
- **Automate critical paths**: Add accessibility checks to essential user journeys
- **Test with different settings**: Font scaling, display size, high contrast
- **Use semantic testing**: Test semantics, not implementation details
- **Handle dynamic content**: Test live regions and state changes
- **Test error states**: Ensure error messages are accessible

**Common Issues to Test:**

```kotlin
// Missing content description
Image(
    painter = painterResource(R.drawable.icon),
    contentDescription = null // ❌ Will fail accessibility check
)

// Touch target too small
IconButton(
    onClick = { },
    modifier = Modifier.size(24.dp) // ❌ Below 48dp minimum
) {
    Icon(Icons.Default.Close, "Close")
}

// Poor color contrast
Text(
    text = "Read more",
    color = Color.LightGray, // ❌ May fail contrast check
    modifier = Modifier.background(Color.White)
)

// No state description
Switch(
    checked = isEnabled,
    onCheckedChange = { } // ❌ Missing state information
)
```

## Ответ (RU)

Тестирование доступности обеспечивает, что ваше приложение может использоваться людьми с ограниченными возможностями, включая тех, кто использует программы чтения с экрана, такие как TalkBack, голосовое управление или другие вспомогательные технологии. Android предоставляет множество инструментов и фреймворков для ручного и автоматизированного тестирования доступности.

**Подходы к тестированию:**

**1. Ручное тестирование с TalkBack**

Включите TalkBack и пройдитесь по приложению:

```kotlin
// Чек-лист тестирования:
// 1. Включите TalkBack: Настройки > Специальные возможности > TalkBack
// 2. Навигируйте по всем экранам жестами
// 3. Проверьте, что все интерактивные элементы доступны для фокуса
// 4. Убедитесь, что описания контента осмысленные
// 5. Проверьте, что пользовательские действия работают
// 6. Проверьте, что живые регионы объявляют обновления
```

**2. Accessibility Scanner**

Используйте приложение Google Accessibility Scanner для выявления проблем:

- Скачайте из Play Store
- Отсканируйте любой экран в приложении
- Просмотрите предложения по улучшению
- Исправьте проблемы, связанные с:
  - Размером области касания (минимум 48dp)
  - Описаниями контента
  - Контрастом цветов
  - Размером и читаемостью текста

**3. Автоматическое тестирование с Espresso**

Тестируйте доступность в UI-тестах с использованием Espresso:

```kotlin
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testAccessibilityWithEspresso() {
        // Включить проверки доступности
        AccessibilityChecks.enable()

        // Выполнить UI-действия - проблемы доступности провалят тест
        onView(withId(R.id.submit_button))
            .perform(click())

        onView(withId(R.id.result_text))
            .check(matches(isDisplayed()))
    }

    @Test
    fun testContentDescriptions() {
        onView(withId(R.id.profile_image))
            .check { view, _ ->
                val contentDesc = view.contentDescription
                assertThat(contentDesc).isNotEmpty()
                assertThat(contentDesc).isNotEqualTo("Image")
            }
    }
}
```

**4. Тестирование Compose**

Тестируйте доступность в Jetpack Compose:

```kotlin
@Test
fun testSemanticProperties() {
    composeTestRule.setContent {
        Button(onClick = { }) {
            Text("Отправить")
        }
    }

    // Проверка семантики
    composeTestRule
        .onNodeWithText("Отправить")
        .assertHasClickAction()
        .assertIsEnabled()
}

@Test
fun testStateDescription() {
    var isChecked by mutableStateOf(false)

    composeTestRule.setContent {
        Checkbox(
            checked = isChecked,
            onCheckedChange = { isChecked = it },
            modifier = Modifier.semantics {
                stateDescription = if (isChecked) "Выбрано" else "Не выбрано"
            }
        )
    }

    composeTestRule
        .onNode(hasStateDescription("Не выбрано"))
        .assertExists()
}
```

**Лучшие практики:**

- **Тестируйте на реальных устройствах**: Эмуляторы могут неточно отражать поведение TalkBack
- **Тестируйте все пользовательские потоки**: Обеспечьте доступность всей навигации
- **Автоматизируйте критические пути**: Добавьте проверки доступности к основным сценариям
- **Тестируйте с разными настройками**: Масштабирование шрифта, размер экрана, высокая контрастность
- **Используйте семантическое тестирование**: Тестируйте семантику, а не детали реализации
- **Тестируйте динамический контент**: Проверяйте живые регионы и изменения состояния
- **Тестируйте состояния ошибок**: Убедитесь, что сообщения об ошибках доступны

---

## Follow-ups

- What happens if you don't run accessibility tests in CI/CD?
- How do you handle false positives in automated accessibility testing?
- What's the difference between Espresso and Compose Test for accessibility?
- How do you test accessibility with different screen sizes and orientations?
- What are the performance implications of accessibility testing?

## References

- [Android Accessibility Testing Guide](https://developer.android.com/guide/topics/ui/accessibility/testing)
- [Espresso Accessibility Testing](https://developer.android.com/training/testing/espresso/accessibility-checking)
- [Compose Testing Documentation](https://developer.android.com/jetpack/compose/testing)
- [Accessibility Scanner App](https://play.google.com/store/apps/details?id=com.google.android.apps.accessibility.auditor)

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-accessibility-compose--android--medium]] - Accessibility
- [[q-robolectric-vs-instrumented--android--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing


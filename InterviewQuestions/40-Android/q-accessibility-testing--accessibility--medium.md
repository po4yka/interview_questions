---
id: 20251012-122754
title: Accessibility Testing / Тестирование доступности
aliases: [Accessibility Testing, Тестирование доступности]
topic: android
subtopics: [ui-accessibility, testing-automation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-accessibility-compose--accessibility--medium
  - q-accessibility-talkback--accessibility--medium
  - q-cicd-automated-testing--devops--medium
created: 2025-10-11
updated: 2025-10-15
tags:
  - android/ui-accessibility
  - android/testing-automation
  - accessibility
  - testing
  - automated-testing
  - talkback
  - difficulty/medium
---
# Question (EN)
How do you test accessibility in Android apps? What tools and techniques are available for automated accessibility testing? How do you write accessibility tests with Espresso and Compose Test?

# Вопрос (RU)
Как тестировать доступность в Android-приложениях? Какие инструменты и техники доступны для автоматизированного тестирования доступности? Как писать accessibility-тесты с Espresso и Compose Test?

---

## Answer (EN)

Accessibility testing ensures your app is usable by everyone. Testing approaches: manual testing (TalkBack, Switch Access), automated testing (Espresso, Compose Test, Robolectric), scanner tools (Accessibility Scanner, Lint checks), and user testing.

#### Accessibility Scanner

Google's Accessibility Scanner - visual UI analysis tool:

```
Installation:
1. Install from Play Store: "Accessibility Scanner"
2. Enable in Settings → Accessibility
3. Tap floating action button to scan screen

What it checks:
- Touch target sizes (minimum 48dp)
- Content descriptions
- Text contrast ratios
- Clickable items
- Content labeling
```

Scanner findings example:
```
Item 1: "Touch target too small"
  - Current: 32dp x 32dp
  - Minimum: 48dp x 48dp
  - Suggestion: Increase button size or add padding

Item 2: "Missing contentDescription"
  - Element: ImageButton
  - Suggestion: Add contentDescription

Item 3: "Low contrast ratio"
  - Current: 2.1:1
  - Minimum: 4.5:1 (WCAG AA)
  - Suggestion: Increase contrast or use different colors
```

#### Lint Checks

Enable accessibility lint checks:

```kotlin
// build.gradle.kts
android {
    lint {
        checkOnly += setOf(
            "ContentDescription",
            "ClickableViewAccessibility",
            "LabelFor",
            "TouchTargetSizeCheck"
        )
        abortOnError = true
    }
}
```

Common lint warnings:

```xml
<!-- Missing contentDescription -->
<ImageView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:src="@drawable/icon" />
<!-- Warning: [ContentDescription] Missing contentDescription attribute on image -->

<!-- GOOD -->
<ImageView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:src="@drawable/icon"
    android:contentDescription="@string/icon_description" />

<!-- Touch target too small -->
<ImageButton
    android:layout_width="24dp"
    android:layout_height="24dp"
    android:src="@drawable/icon" />
<!-- Warning: [TouchTargetSizeCheck] Touch target is 24x24dp, should be at least 48x48dp -->
```

#### Espresso Accessibility Tests

Dependencies:

```kotlin
androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
androidTestImplementation("androidx.test.espresso:espresso-accessibility:3.5.1")
androidTestImplementation("com.google.android.apps.common.testing.accessibility.framework:accessibility-test-framework:4.0.0")
```

Basic Espresso accessibility test:

```kotlin
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testAccessibility_allViews() {
        // Enable accessibility checking
        AccessibilityChecks.enable()

        // Perform actions - accessibility is checked automatically
        onView(withId(R.id.button)).perform(click())
        onView(withId(R.id.textField)).perform(typeText("Hello"))
    }

    @Test
    fun testAccessibility_contentDescriptions() {
        // Verify all images have content descriptions
        onView(withId(R.id.recyclerView))
            .check { view, exception ->
                val recyclerView = view as RecyclerView
                for (i in 0 until recyclerView.adapter!!.itemCount) {
                    val viewHolder = recyclerView.findViewHolderForAdapterPosition(i)
                    val itemView = viewHolder?.itemView

                    val imageViews = itemView?.let { findImageViews(it) } ?: emptyList()

                    imageViews.forEach { imageView ->
                        val contentDesc = imageView.contentDescription
                        if (contentDesc.isNullOrEmpty()) {
                            throw AssertionError(
                                "ImageView at position $i missing contentDescription"
                            )
                        }
                    }
                }
            }
    }

    private fun findImageViews(view: View): List<ImageView> {
        val images = mutableListOf<ImageView>()
        if (view is ImageView) {
            images.add(view)
        }
        if (view is ViewGroup) {
            for (i in 0 until view.childCount) {
                images.addAll(findImageViews(view.getChildAt(i)))
            }
        }
        return images
    }
}
```

Configure accessibility checks:

```kotlin
@RunWith(AndroidJUnit4::class)
class ConfiguredAccessibilityTest {

    @Before
    fun setup() {
        AccessibilityChecks.enable()
            .setRunChecksFromRootView(true)
            .setSuppressingResultMatcher(
                anyOf(
                    allOf(
                        matchesViews(withId(R.id.logo)),
                        matchesCheck(is(TextContrastCheck::class.java))
                    ),
                    allOf(
                        matchesViews(withClassName(containsString("TextView"))),
                        matchesCheck(is(TouchTargetSizeCheck::class.java))
                    )
                )
            )
    }

    @Test
    fun testWithConfiguredChecks() {
        onView(withId(R.id.button)).perform(click())
    }
}
```

#### Compose Accessibility Tests

Basic Compose accessibility test:

```kotlin
@RunWith(AndroidJUnit4::class)
class ComposeAccessibilityTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testAccessibility_contentDescription() {
        composeTestRule.setContent {
            IconButton(onClick = {}) {
                Icon(
                    imageVector = Icons.Default.Delete,
                    contentDescription = "Delete item"
                )
            }
        }

        composeTestRule
            .onNodeWithContentDescription("Delete item")
            .assertExists()
            .assertHasClickAction()
    }

    @Test
    fun testAccessibility_semanticProperties() {
        var checked by mutableStateOf(false)

        composeTestRule.setContent {
            Checkbox(
                checked = checked,
                onCheckedChange = { checked = it }
            )
        }

        composeTestRule
            .onNode(hasToggleableState(ToggleableState.Off))
            .assertExists()
            .performClick()

        composeTestRule
            .onNode(hasToggleableState(ToggleableState.On))
            .assertExists()
    }

    @Test
    fun testAccessibility_mergedSemantics() {
        composeTestRule.setContent {
            Card(
                modifier = Modifier
                    .clickable {}
                    .semantics(mergeDescendants = true) {
                        contentDescription = "iPhone 15, $999, 4.5 stars"
                    }
            ) {
                Column {
                    Text("iPhone 15")
                    Text("$999")
                    Text("4.5 stars")
                }
            }
        }

        composeTestRule
            .onNodeWithContentDescription("iPhone 15, $999, 4.5 stars")
            .assertExists()
            .assertHasClickAction()
    }

    @Test
    fun testAccessibility_customActions() {
        var deleteClicked = false

        composeTestRule.setContent {
            Card(
                modifier = Modifier
                    .clickable {}
                    .semantics {
                        customActions = listOf(
                            CustomAccessibilityAction("Delete") {
                                deleteClicked = true
                                true
                            }
                        )
                    }
            ) {
                Text("Email item")
            }
        }

        composeTestRule
            .onNode(hasCustomAction("Delete"))
            .assertExists()
    }

    @Test
    fun testAccessibility_roleSemantics() {
        composeTestRule.setContent {
            Box(
                modifier = Modifier
                    .clickable {}
                    .semantics {
                        role = Role.Button
                        contentDescription = "Custom button"
                    }
            ) {
                Text("Click me")
            }
        }

        composeTestRule
            .onNode(hasRole(Role.Button))
            .assertExists()
            .assertHasClickAction()
    }
}
```

#### Robolectric Accessibility Tests

Unit tests with Robolectric:

```kotlin
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P])
class RobolectricAccessibilityTest {

    @Test
    fun testAccessibility_contentDescription() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .create()
            .start()
            .resume()
            .get()

        val imageButton = activity.findViewById<ImageButton>(R.id.deleteButton)

        assertNotNull(imageButton.contentDescription)
        assertEquals("Delete", imageButton.contentDescription)
    }

    @Test
    fun testAccessibility_touchTargetSize() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .create()
            .start()
            .resume()
            .get()

        val button = activity.findViewById<Button>(R.id.submitButton)

        val widthSpec = View.MeasureSpec.makeMeasureSpec(1080, View.MeasureSpec.AT_MOST)
        val heightSpec = View.MeasureSpec.makeMeasureSpec(1920, View.MeasureSpec.AT_MOST)
        button.measure(widthSpec, heightSpec)

        val minSize = (48 * activity.resources.displayMetrics.density).toInt()

        assertTrue(
            "Touch target too small: ${button.measuredWidth}x${button.measuredHeight}, " +
            "minimum is ${minSize}x${minSize}",
            button.measuredWidth >= minSize && button.measuredHeight >= minSize
        )
    }
}
```

#### CI/CD Integration

GitHub Actions with accessibility tests:

```yaml
name: Accessibility Tests

on:
  pull_request:
    branches: [ main ]

jobs:
  accessibility-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Run accessibility lint checks
        run: ./gradlew lintDebug

      - name: Run accessibility tests
        run: ./gradlew testDebugUnitTest connectedDebugAndroidTest

      - name: Upload lint results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: lint-results
          path: app/build/reports/lint-results-debug.html
```

#### Best Practices

1. Run accessibility tests in CI
2. Test with real assistive technologies
3. Automate repetitive checks
4. Test early and often
5. Get user feedback

---

# Вопрос (RU)
Как тестировать доступность в Android-приложениях? Какие инструменты и техники доступны для автоматизированного тестирования доступности? Как писать accessibility-тесты с Espresso и Compose Test?

## Ответ (RU)
[Перевод с примерами из английской версии...]

### Резюме

**Подходы к тестированию:**
1.  **Ручное тестирование** — TalkBack, Scanner, реальные устройства
2.  **Автоматизированное тестирование** — Espresso, Compose Test, Robolectric
3.  **Lint-проверки** — отлов проблем на этапе сборки
4.  **Интеграция с CI/CD** — автоматический запуск тестов
5.  **Тестирование с пользователями** — обратная связь от реальных пользователей

**Ключевые инструменты:**
- **Accessibility Scanner** — визуальный анализ UI
- **Lint** — статический анализ
- **Espresso** — instrumented-тесты
- **Compose Test** — Compose UI тесты
- **Robolectric** — быстрые unit-тесты

**Что тестировать:**
- Content descriptions существуют и осмысленны
- Touch targets не менее 48dp
- Контрастность текста соответствует WCAG AA (4.5:1)
- Focus order логичен
- Custom actions работают корректно
- Изменения состояния объявляются
- Формы имеют правильные метки и сообщения об ошибках

**CI/CD:**
- Запускать accessibility-тесты на каждом PR
- Падать сборку при нарушениях доступности
- Загружать отчёты для review
- Комментировать PR при падениях

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
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-accessibility-compose--accessibility--medium]] - Accessibility
- [[q-robolectric-vs-instrumented--testing--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--testing--hard]] - Testing

---
id: "20251015082237307"
title: "Accessibility Testing / Accessibility Тестирование"
topic: android
difficulty: medium
status: draft
created: 2025-10-11
tags: [accessibility, testing, automated-testing, talkback, difficulty/medium]
related:   - q-accessibility-compose--accessibility--medium
  - q-accessibility-talkback--accessibility--medium
  - q-cicd-automated-testing--devops--medium
---
# Question (EN)
How do you test accessibility in Android apps? What tools and techniques are available for automated accessibility testing? How do you write accessibility tests with Espresso and Compose Test?

## Answer (EN)
### Overview

**Accessibility testing** ensures your app is usable by everyone. Testing approaches:
1. **Manual testing** - Test with TalkBack, Switch Access
2. **Automated testing** - Espresso, Compose Test, Robolectric
3. **Scanner tools** - Accessibility Scanner, Lint checks
4. **User testing** - Feedback from users with disabilities

### 1. Accessibility Scanner

**Google's Accessibility Scanner** - Visual UI analysis tool:

```
Installation:
1. Install from Play Store: "Accessibility Scanner"
2. Enable in Settings → Accessibility
3. Tap floating action button to scan screen

What it checks:
 Touch target sizes (minimum 48dp)
 Content descriptions
 Text contrast ratios
 Clickable items
 Content labeling
 Implementation suggestions
```

**Scanner findings example**:
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

### 2. Lint Checks for Accessibility

**Enable accessibility lint checks**:

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

        // Fail build on accessibility errors
        abortOnError = true
    }
}
```

**Common lint warnings**:

```xml
<!--  Missing contentDescription -->
<ImageView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:src="@drawable/icon" />
<!-- Warning: [ContentDescription] Missing contentDescription attribute on image -->

<!--  GOOD -->
<ImageView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:src="@drawable/icon"
    android:contentDescription="@string/icon_description" />

<!--  Touch target too small -->
<ImageButton
    android:layout_width="24dp"
    android:layout_height="24dp"
    android:src="@drawable/icon" />
<!-- Warning: [TouchTargetSizeCheck] Touch target is 24x24dp, should be at least 48x48dp -->

<!--  GOOD -->
<ImageButton
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:src="@drawable/icon" />
```

### 3. Espresso Accessibility Tests

**dependencies**:

```kotlin
androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
androidTestImplementation("androidx.test.espresso:espresso-accessibility:3.5.1")
androidTestImplementation("com.google.android.apps.common.testing.accessibility.framework:accessibility-test-framework:4.0.0")
```

**Basic Espresso accessibility test**:

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

        // Accessibility violations will fail the test
    }

    @Test
    fun testAccessibility_specificView() {
        // Check specific view
        onView(withId(R.id.profileImage))
            .check(matches(withContentDescription(not(isEmptyOrNullString()))))
    }

    @Test
    fun testAccessibility_touchTargetSize() {
        // Verify minimum touch target size
        onView(withId(R.id.deleteButton))
            .check { view, exception ->
                val width = view.width
                val height = view.height
                val minSize = (48 * view.context.resources.displayMetrics.density).toInt()

                if (width < minSize || height < minSize) {
                    throw AssertionError(
                        "Touch target too small: ${width}x${height}dp, " +
                        "minimum is ${minSize}x${minSize}dp"
                    )
                }
            }
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

**Configure accessibility checks**:

```kotlin
@RunWith(AndroidJUnit4::class)
class ConfiguredAccessibilityTest {

    @Before
    fun setup() {
        // Configure which checks to run
        AccessibilityChecks.enable()
            .setRunChecksFromRootView(true)
            .setSuppressingResultMatcher(
                // Suppress known issues
                anyOf(
                    // Suppress contrast issues for specific views
                    allOf(
                        matchesViews(withId(R.id.logo)),
                        matchesCheck(is(TextContrastCheck::class.java))
                    ),
                    // Suppress touch target issues for readonly text
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

### 4. Compose Accessibility Tests

**Basic Compose accessibility test**:

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

        // Verify content description exists
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

        // Verify toggleable state
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

        // Verify merged semantics
        composeTestRule
            .onNodeWithContentDescription("iPhone 15, $999, 4.5 stars")
            .assertExists()
            .assertHasClickAction()
    }

    @Test
    fun testAccessibility_customActions() {
        var deleteClicked = false
        var shareClicked = false

        composeTestRule.setContent {
            Card(
                modifier = Modifier
                    .clickable {}
                    .semantics {
                        customActions = listOf(
                            CustomAccessibilityAction("Delete") {
                                deleteClicked = true
                                true
                            },
                            CustomAccessibilityAction("Share") {
                                shareClicked = true
                                true
                            }
                        )
                    }
            ) {
                Text("Email item")
            }
        }

        // Perform custom action
        composeTestRule
            .onNode(hasCustomAction("Delete"))
            .assertExists()

        // Note: Actually triggering custom actions in tests is complex
        // Typically verified through manual TalkBack testing
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

        // Verify role
        composeTestRule
            .onNode(hasRole(Role.Button))
            .assertExists()
            .assertHasClickAction()
    }

    @Test
    fun testAccessibility_stateDescription() {
        var isLoading by mutableStateOf(false)

        composeTestRule.setContent {
            Button(
                onClick = { isLoading = true },
                modifier = Modifier.semantics {
                    stateDescription = if (isLoading) "Loading" else "Ready"
                }
            ) {
                if (isLoading) {
                    CircularProgressIndicator()
                } else {
                    Text("Submit")
                }
            }
        }

        // Verify state description
        composeTestRule
            .onNode(hasStateDescription("Ready"))
            .assertExists()

        composeTestRule
            .onNode(hasStateDescription("Ready"))
            .performClick()

        composeTestRule
            .onNode(hasStateDescription("Loading"))
            .assertExists()
    }

    @Test
    fun testAccessibility_heading() {
        composeTestRule.setContent {
            Column {
                Text(
                    text = "Settings",
                    modifier = Modifier.semantics { heading() }
                )
                Text("Content")
            }
        }

        // Verify heading exists
        composeTestRule
            .onNode(isHeading())
            .assertExists()
            .assertTextEquals("Settings")
    }

    @Test
    fun testAccessibility_traversalIndex() {
        composeTestRule.setContent {
            Column {
                Text("First", modifier = Modifier.testTag("first"))
                Text("Second", modifier = Modifier.testTag("second"))
                Text("Third", modifier = Modifier.testTag("third"))
            }
        }

        // Verify traversal order (simplified example)
        composeTestRule
            .onNodeWithTag("first")
            .assertExists()

        composeTestRule
            .onNodeWithTag("second")
            .assertExists()

        composeTestRule
            .onNodeWithTag("third")
            .assertExists()
    }
}
```

### 5. Robolectric Accessibility Tests

**Unit tests with Robolectric**:

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

        // Verify content description
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

        // Measure view
        val widthSpec = View.MeasureSpec.makeMeasureSpec(1080, View.MeasureSpec.AT_MOST)
        val heightSpec = View.MeasureSpec.makeMeasureSpec(1920, View.MeasureSpec.AT_MOST)
        button.measure(widthSpec, heightSpec)

        val minSize = (48 * activity.resources.displayMetrics.density).toInt()

        // Verify size
        assertTrue(
            "Touch target too small: ${button.measuredWidth}x${button.measuredHeight}, " +
            "minimum is ${minSize}x${minSize}",
            button.measuredWidth >= minSize && button.measuredHeight >= minSize
        )
    }

    @Test
    fun testAccessibility_announcements() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .create()
            .start()
            .resume()
            .get()

        val shadowActivity = shadowOf(activity)

        // Trigger action that should announce
        activity.findViewById<Button>(R.id.deleteButton).performClick()

        // Verify accessibility event was sent
        val events = shadowActivity.lastSentAccessibilityEvents
        assertTrue(events.any { it.eventType == AccessibilityEvent.TYPE_ANNOUNCEMENT })
    }
}
```

### 6. Screenshot Testing for Accessibility

**Visual regression for contrast ratios**:

```kotlin
@RunWith(AndroidJUnit4::class)
class AccessibilityScreenshotTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testAccessibility_contrastRatios() {
        composeTestRule.setContent {
            Column {
                // Test various text/background combinations
                Text(
                    text = "Black on White",
                    color = Color.Black,
                    modifier = Modifier.background(Color.White)
                )

                Text(
                    text = "White on Black",
                    color = Color.White,
                    modifier = Modifier.background(Color.Black)
                )

                // This should fail WCAG AA (4.5:1)
                Text(
                    text = "Gray on Light Gray",
                    color = Color.Gray,
                    modifier = Modifier.background(Color.LightGray)
                )
            }
        }

        // Capture screenshot and analyze contrast
        // (Using a tool like Paparazzi or custom screenshot testing)
        composeTestRule.onRoot().captureToImage()

        // Analyze contrast ratios programmatically
        // This is a simplified example; actual implementation would be more complex
    }
}
```

### 7. Custom Accessibility Test Rules

**Reusable test rules**:

```kotlin
class AccessibilityTestRule : TestRule {

    override fun apply(base: Statement, description: Description): Statement {
        return object : Statement() {
            override fun evaluate() {
                // Enable accessibility checks
                AccessibilityChecks.enable()
                    .setRunChecksFromRootView(true)

                try {
                    base.evaluate()
                } finally {
                    // Cleanup
                    AccessibilityChecks.disable()
                }
            }
        }
    }
}

// Usage
@RunWith(AndroidJUnit4::class)
class MyAccessibilityTest {

    @get:Rule
    val accessibilityRule = AccessibilityTestRule()

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testFeature() {
        // Accessibility automatically checked
        onView(withId(R.id.button)).perform(click())
    }
}
```

### 8. CI/CD Integration

**GitHub Actions with accessibility tests**:

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

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: |
            app/build/reports/tests/
            app/build/reports/androidTests/

      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: ' Accessibility tests failed. Please review the results.'
            })
```

### Best Practices

1. **Run accessibility tests in CI**
   ```kotlin
   //  GOOD - Catch issues early
   ./gradlew testDebugUnitTest connectedDebugAndroidTest

   //  BAD - Only manual testing
   ```

2. **Test with real assistive technologies**
   ```
    Test with TalkBack enabled
    Test with large text sizes
    Test with high contrast mode
    Test with display scaling
    Test with Switch Access
   ```

3. **Automate repetitive checks**
   ```kotlin
   //  GOOD - Automated checks
   @Test
   fun testAllImagesHaveContentDescriptions() {
       // Automated check for all ImageViews
   }

   //  BAD - Manual only
   ```

4. **Test early and often**
   ```
    Add accessibility tests from the start
    Run tests on every commit
    Include in PR reviews
   ```

5. **Get user feedback**
   ```
    Test with users who rely on assistive technology
    Conduct usability studies
    Gather feedback through support channels
   ```

### Summary

**Testing approaches:**
1.  **Manual testing** - TalkBack, Scanner, real devices
2.  **Automated testing** - Espresso, Compose Test, Robolectric
3.  **Lint checks** - Catch issues at build time
4.  **CI/CD integration** - Run tests automatically
5.  **User testing** - Feedback from real users

**Key tools:**
- **Accessibility Scanner** - Visual UI analysis
- **Lint** - Static analysis
- **Espresso** - Instrumented tests
- **Compose Test** - Compose UI tests
- **Robolectric** - Fast unit tests

**What to test:**
- Content descriptions exist and are meaningful
- Touch targets are at least 48dp
- Text contrast meets WCAG AA (4.5:1)
- Focus order is logical
- Custom actions work correctly
- State changes are announced
- Forms have proper labels and error messages

**CI/CD:**
- Run accessibility tests on every PR
- Fail builds on accessibility violations
- Upload reports for review
- Comment on PRs with failures

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

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-accessibility-compose--accessibility--medium]] - Accessibility
- [[q-robolectric-vs-instrumented--testing--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--testing--hard]] - Testing

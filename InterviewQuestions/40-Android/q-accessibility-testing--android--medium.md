---
id: android-036
title: Accessibility Testing / Тестирование доступности
aliases:
- Accessibility Testing
- Тестирование доступности
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
- c-accessibility
- q-accessibility-color-contrast--android--medium
- q-accessibility-compose--android--medium
- q-accessibility-talkback--android--medium
- q-compose-testing--android--medium
- q-custom-view-accessibility--android--medium
created: 2025-10-11
updated: 2025-11-10
tags:
- a11y
- android/testing-ui
- android/ui-accessibility
- difficulty/medium
- testing
anki_cards:
- slug: android-036-0-en
  language: en
  anki_id: 1768363328475
  synced_at: '2026-01-14T09:17:53.025866'
- slug: android-036-0-ru
  language: ru
  anki_id: 1768363328497
  synced_at: '2026-01-14T09:17:53.028124'
sources: []
---
# Вопрос (RU)
> Как тестировать доступность в Android-приложениях?

# Question (EN)
> How do you test accessibility in Android apps?

---

## Ответ (RU)

Тестирование доступности гарантирует работу приложения для людей с ограниченными возможностями. Android предоставляет инструменты для ручного и автоматизированного тестирования.

**Ручное тестирование с TalkBack:**
- Все интерактивные элементы доступны через свайп и фокусируются в логичном порядке
- `contentDescription` осмысленный для значимых элементов (не "Image", а "Фотография профиля пользователя"), декоративные изображения без смысла помечены `contentDescription = null`
- Проверка custom actions и live regions

**Accessibility Scanner:**
- Touch target минимум 48dp для интерактивных элементов
- Контраст цветов для текста не ниже 4.5:1 для обычного текста (WCAG AA)
- Читаемость шрифтов

**Автоматизированное тестирование Espresso:**

```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import androidx.test.rule.ActivityTestRule
import androidx.test.ext.truth.content.IntentSubject.assertThat
import com.google.android.apps.common.testing.accessibility.framework.integrations.espresso.AccessibilityChecks

@LargeTest
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @Test
    fun testAccessibility() {
        // ✅ Включить проверки для всех UI-действий (обычно один раз в test suite / @BeforeClass)
        AccessibilityChecks.enable()
            .setRunChecksFromRootView(true)

        onView(withId(R.id.submit)).perform(click())
        // Тест (или любой Espresso шаг) упадёт при проблемах доступности
    }

    @Test
    fun testContentDescription() {
        onView(withId(R.id.profile_image)).check { view, _ ->
            // ✅ Проверить осмысленное описание для значимого изображения
            assertThat(view.contentDescription?.toString()).isNotEmpty()
            // ❌ Избегать общих описаний
            assertThat(view.contentDescription?.toString()).isNotEqualTo("Image")
        }
    }
}
```

(В реальном проекте `AccessibilityChecks.enable()` следует вызывать один раз, например в `@BeforeClass`, так как он глобален для Espresso.)

**Тестирование Compose через семантику:**

```kotlin
@Test
fun testSemanticProperties() {
    composeTestRule.setContent {
        Button(onClick = { }) { Text("Submit") }
    }

    composeTestRule
        .onNodeWithText("Submit")
        .assertHasClickAction()
        .assertIsEnabled()
}

@Test
fun testStateDescription() {
    composeTestRule.setContent {
        var isChecked by remember { mutableStateOf(false) }

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
}
```

**Типичные ошибки:**

```kotlin
// ❌ Нет описания у значимого изображения (иконка несёт смысл)
Image(painterResource(R.drawable.icon), contentDescription = null)

// ❌ Touch target меньше 48dp для элемента, по которому нужно попадать касанием
IconButton(modifier = Modifier.size(24.dp), onClick = { }) {
    Icon(Icons.Default.Close, contentDescription = "Close")
}

// ❌ Недостаточный контраст текста по отношению к фону
Text(
    text = "Read more",
    color = Color.LightGray,
    modifier = Modifier.background(Color.White)
)
```

**Лучшие практики:**
- Тестируйте на реальных устройствах (эмуляторы неточны для TalkBack)
- Интегрируйте проверки (например, Espresso Accessibility Checks) в CI/CD
- Проверяйте разные настройки: масштаб шрифта, высокая контрастность, режимы доступности
- Используйте тесты семантики (role, label, state, `contentDescription`) вместо проверки деталей реализации (конкретных вью/иерархий)

## Answer (EN)

Accessibility testing ensures apps are usable by people with disabilities. Android provides tools for manual and automated testing.

**Manual Testing with TalkBack:**
- All interactive elements reachable via swipe with a logical focus order
- `contentDescription` is meaningful for important elements (not "Image", but "User profile photo"), decorative images with no meaning are marked with `contentDescription = null`
- Verify custom actions and live regions

**Accessibility Scanner:**
- Touch target minimum 48dp for interactive elements
- Color contrast for text at least 4.5:1 for normal text (WCAG AA)
- Font readability

**Automated Testing via Espresso:**

```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import com.google.android.apps.common.testing.accessibility.framework.integrations.espresso.AccessibilityChecks
// Use an assertion library such as Truth or JUnit assertions for checks

@LargeTest
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @Test
    fun testAccessibility() {
        // ✅ Enable accessibility checks for all UI actions (typically once per test suite / @BeforeClass)
        AccessibilityChecks.enable()
            .setRunChecksFromRootView(true)

        onView(withId(R.id.submit)).perform(click())
        // Any Espresso action will fail if accessibility issues are found
    }

    @Test
    fun testContentDescription() {
        onView(withId(R.id.profile_image)).check { view, _ ->
            // ✅ Verify meaningful description for a non-decorative image
            assertThat(view.contentDescription?.toString()).isNotEmpty()
            // ❌ Avoid generic descriptions
            assertThat(view.contentDescription?.toString()).isNotEqualTo("Image")
        }
    }
}
```

(In a real test suite, call `AccessibilityChecks.enable()` once, as it configures global Espresso behavior.)

**Compose Testing via Semantics:**

```kotlin
@Test
fun testSemanticProperties() {
    composeTestRule.setContent {
        Button(onClick = { }) { Text("Submit") }
    }

    composeTestRule
        .onNodeWithText("Submit")
        .assertHasClickAction()
        .assertIsEnabled()
}

@Test
fun testStateDescription() {
    composeTestRule.setContent {
        var isChecked by remember { mutableStateOf(false) }

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
}
```

**Common Issues:**

```kotlin
// ❌ Missing contentDescription for a meaningful image (icon carries meaning)
Image(painterResource(R.drawable.icon), contentDescription = null)

// ❌ Touch target smaller than 48dp for a tappable element
IconButton(modifier = Modifier.size(24.dp), onClick = { }) {
    Icon(Icons.Default.Close, contentDescription = "Close")
}

// ❌ Insufficient contrast between text and background
Text(
    text = "Read more",
    color = Color.LightGray,
    modifier = Modifier.background(Color.White)
)
```

**Best Practices:**
- Test on real devices (emulators can be inaccurate for TalkBack)
- Integrate checks (e.g., Espresso Accessibility Checks) into CI/CD
- Test different settings: font scale, high contrast text, accessibility modes
- Target semantic properties in tests (role, label, state, `contentDescription`) instead of relying on implementation details (exact view classes/structure)

---

## Дополнительные Вопросы (RU)

- Как `AccessibilityChecks.enable()` влияет на время выполнения тестов в CI-пайплайнах?
- Какие семантические свойства должны предоставлять кастомные компоненты Compose для совместимости с TalkBack?
- Как тестировать доступность для динамического контента, обновляемого через `StateFlow`?
- Какие стратегии использовать для тестирования доступности в мультимодульных проектах?
- Как сбалансировать покрытие тестами доступности и общее время выполнения тест-сьюта?

## Follow-ups

- How does `AccessibilityChecks.enable()` impact test execution time in CI pipelines?
- What semantic properties must custom Compose components expose for TalkBack compatibility?
- How do you test accessibility for dynamic content updating via `StateFlow`?
- What strategies handle accessibility testing across multi-module projects?
- How do you balance accessibility test coverage with test suite execution constraints?

## Ссылки (RU)

- [[c-accessibility]]
- https://developer.android.com/guide/topics/ui/accessibility/testing
- https://developer.android.com/training/testing/espresso/accessibility-checking

## References

- [[c-accessibility]]
- https://developer.android.com/guide/topics/ui/accessibility/testing
- https://developer.android.com/training/testing/espresso/accessibility-checking

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-testing-compose-ui--android--medium]] - основы тестирования Compose UI

### Связанные (того Же уровня)
- [[q-accessibility-compose--android--medium]] - реализация доступности
- [[q-accessibility-talkback--android--medium]] - интеграция TalkBack
- [[q-compose-testing--android--medium]] - паттерны тестирования Compose

### Продвинутые (сложнее)

## Related Questions

### Prerequisites (Easier)
- [[q-testing-compose-ui--android--medium]] - Compose UI testing basics

### Related (Same Level)
- [[q-accessibility-compose--android--medium]] - Accessibility implementation
- [[q-accessibility-talkback--android--medium]] - TalkBack integration
- [[q-compose-testing--android--medium]] - Compose testing patterns

### Advanced (Harder)

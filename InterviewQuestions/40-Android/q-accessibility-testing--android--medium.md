---
id: android-036
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
status: reviewed
moc: moc-android
related:
 - q-accessibility-compose--android--medium
 - q-accessibility-talkback--android--medium
created: 2025-10-11
updated: 2025-10-29
tags: [a11y, android/testing-ui, android/ui-accessibility, difficulty/medium, testing]
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
- Все интерактивные элементы доступны через свайп
- ContentDescription осмысленный (не "Image", а "User profile photo")
- Проверка custom actions и live regions

**Accessibility Scanner:**
- Touch target минимум 48dp
- Контраст цветов минимум 4.5:1 для текста
- Читаемость шрифтов

**Автоматизированное тестирование Espresso:**

```kotlin
@Test
fun testAccessibility() {
 // ✅ Включить проверки для всех UI-действий
 AccessibilityChecks.enable()

 onView(withId(R.id.submit)).perform(click())
 // Тест упадёт при проблемах доступности
}

@Test
fun testContentDescription() {
 onView(withId(R.id.profile_image)).check { view, _ ->
 // ✅ Проверить осмысленное описание
 assertThat(view.contentDescription).isNotEmpty()
 // ❌ Избегать общих описаний
 assertThat(view.contentDescription).isNotEqualTo("Image")
 }
}
```

**Тестирование Compose через семантику:**

```kotlin
@Test
fun testSemanticProperties() {
 composeTestRule.setContent {
 Button(onClick = { }) { Text("Отправить") }
 }

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
 stateDescription = if (isChecked) "Выбрано" else "Не выбрано"
 }
 )
 }

 composeTestRule
 .onNode(hasStateDescription("Не выбрано"))
 .assertExists()
}
```

**Типичные ошибки:**

```kotlin
// ❌ Отсутствует contentDescription
Image(painterResource(R.drawable.icon), contentDescription = null)

// ❌ Touch target меньше 48dp
IconButton(modifier = Modifier.size(24.dp), onClick = { }) {
 Icon(Icons.Default.Close, "Close")
}

// ❌ Недостаточный контраст
Text(
 text = "Read more",
 color = Color.LightGray,
 modifier = Modifier.background(Color.White)
)
```

**Лучшие практики:**
- Тестируйте на реальных устройствах (эмуляторы неточны для TalkBack)
- Интегрируйте проверки в CI/CD
- Проверяйте разные настройки: масштаб шрифта, высокую контрастность
- Используйте semantic testing вместо implementation details

## Answer (EN)

Accessibility testing ensures apps are usable by people with disabilities. Android provides tools for manual and automated testing.

**Manual Testing with TalkBack:**
- All interactive elements reachable via swipe
- ContentDescription meaningful (not "Image", but "User profile photo")
- Test custom actions and live regions

**Accessibility Scanner:**
- Touch target minimum 48dp
- Color contrast minimum 4.5:1 for text
- Font readability

**Automated Testing via Espresso:**

```kotlin
@Test
fun testAccessibility() {
 // ✅ Enable checks for all UI actions
 AccessibilityChecks.enable()

 onView(withId(R.id.submit)).perform(click())
 // Test fails if accessibility issues found
}

@Test
fun testContentDescription() {
 onView(withId(R.id.profile_image)).check { view, _ ->
 // ✅ Verify meaningful description
 assertThat(view.contentDescription).isNotEmpty()
 // ❌ Avoid generic descriptions
 assertThat(view.contentDescription).isNotEqualTo("Image")
 }
}
```

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
 Checkbox(
 checked = isChecked,
 onCheckedChange = { },
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
// ❌ Missing contentDescription
Image(painterResource(R.drawable.icon), contentDescription = null)

// ❌ Touch target smaller than 48dp
IconButton(modifier = Modifier.size(24.dp), onClick = { }) {
 Icon(Icons.Default.Close, "Close")
}

// ❌ Insufficient contrast
Text(
 text = "Read more",
 color = Color.LightGray,
 modifier = Modifier.background(Color.White)
)
```

**Best Practices:**
- Test on real devices (emulators inaccurate for TalkBack)
- Integrate checks into CI/CD
- Test different settings: font scale, high contrast
- Use semantic testing instead of implementation details

---

## Follow-ups

- How does AccessibilityChecks.enable() impact test execution time in CI pipelines?
- What semantic properties must custom Compose components expose for TalkBack compatibility?
- How do you test accessibility for dynamic content updating via `StateFlow`?
- What strategies handle accessibility testing across multi-module projects?
- How do you balance accessibility test coverage with test suite execution constraints?

## References

- [[c-accessibility]] - Accessibility fundamentals
- - Compose semantics system
- - Espresso testing framework
- https://developer.android.com/guide/topics/ui/accessibility/testing
- https://developer.android.com/training/testing/espresso/accessibility-checking

## Related Questions

### Prerequisites (Easier)
- [[q-testing-compose-ui--android--medium]] - Compose UI testing basics

### Related (Same Level)
- [[q-accessibility-compose--android--medium]] - Accessibility implementation
- [[q-accessibility-talkback--android--medium]] - TalkBack integration
- [[q-compose-testing--android--medium]] - Compose testing patterns

### Advanced (Harder)


---
id: android-044
title: Accessibility Text Scaling / Масштабирование текста для доступности
aliases: [Text Scaling Accessibility, Масштабирование текста]
topic: android
subtopics:
  - ui-accessibility
  - ui-theming
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
  - q-accessibility-testing--android--medium
  - q-accessibility-text-scaling--android--medium
  - q-how-to-break-text-by-screen-width--android--easy
created: 2025-10-11
updated: 2025-11-10
sources: []
tags: [android/ui-accessibility, android/ui-theming, difficulty/medium]
date created: Saturday, November 1st 2025, 1:24:36 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> Как обрабатывать масштабирование текста для доступности в Android?

# Question (EN)
> How do you handle text scaling for accessibility in Android?

---

## Ответ (RU)

Масштабирование текста позволяет пользователям настраивать размер текста на уровне системы. Рекомендации по доступности (например, WCAG и Android Accessibility) требуют, чтобы интерфейс корректно работал как минимум до 200% увеличения текста (без использования вспомогательных технологий); в Android системные настройки могут позволять и более высокие значения, которые также следует по возможности поддерживать.

**Основные правила:**

**1. Используйте масштабируемые единицы (`sp`)**

```kotlin
// ✅ Правильно - масштабируется с настройкой размера шрифта пользователя
Text(fontSize = 16.sp)
<TextView android:textSize="16sp" />

// ❌ Неправильно - не учитывает настройку размера шрифта
Text(fontSize = 16.dp)
<TextView android:textSize="16dp" />
```

**2. Используйте Material Type Scale**

Используйте предопределенные стили типографики (которые основаны на `sp`) вместо явных размеров: `MaterialTheme.typography.headlineLarge`, `bodyMedium`, или `?attr/textAppearanceHeadlineLarge` в XML, чтобы автоматически наследовать масштабирование шрифта и единый стиль.

**3. Избегайте фиксированных высот**

```kotlin
// ❌ Обрежет текст при масштабировании
Column(modifier = Modifier.height(48.dp)) {
    Text("Длинный текст")
}

// ✅ Позволяет контейнеру подстраиваться под содержимое
Column(modifier = Modifier.wrapContentHeight()) {
    Text("Длинный текст")
}
```

Ключевая идея — не задавать жесткую высоту там, где текст может расти.

**4. Адаптивные макеты для больших масштабов**

При больших значениях масштаба учитывайте `LocalDensity.current.fontScale` и адаптируйте макет: увеличивайте отступы, позволяйте перенос текста, упрощайте компоновку, при необходимости меняйте ориентацию или расположение элементов так, чтобы контент оставался читаемым без обрезки.

**5. Тестирование масштабирования**

```kotlin
@Preview(fontScale = 1.0f)
@Preview(fontScale = 2.0f)
@Composable
fun TextScalingPreview() {
    MyScreen()
}
```

**Основные ошибки:**
- Использование `dp` вместо `sp` для текста
- Фиксированные высоты контейнеров, из-за которых текст обрезается при увеличении
- Игнорирование минимальных размеров области касания (обычно не менее 48dp, задавать в `dp`, не в `sp`), особенно при увеличенном тексте
- Отсутствие тестирования при экстремальных значениях масштабирования

## Answer (EN)

Text scaling allows users to adjust text size system-wide. Accessibility guidance (e.g., WCAG and Android Accessibility) requires UIs to remain usable at least up to 200% text size (without assistive technologies). On Android, system settings may allow scaling beyond 200%; apps should handle these larger scales as well where practical.

**Key Principles:**

**1. Use Scalable Units (`sp`)**

```kotlin
// ✅ Correct - respects user font size settings
Text(fontSize = 16.sp)
<TextView android:textSize="16sp" />

// ❌ Wrong - ignores user font size settings
Text(fontSize = 16.dp)
<TextView android:textSize="16dp" />
```

**2. Use Material Type Scale**

Use predefined typography styles (which are based on `sp`) instead of hardcoded sizes: `MaterialTheme.typography.headlineLarge`, `bodyMedium`, or `?attr/textAppearanceHeadlineLarge` in XML so they inherit font scaling and stay consistent.

**3. Avoid Fixed Heights**

```kotlin
// ❌ Clips text when scaled
Column(modifier = Modifier.height(48.dp)) {
    Text("Long text")
}

// ✅ Allows the container to grow with content
Column(modifier = Modifier.wrapContentHeight()) {
    Text("Long text")
}
```

The key idea is to avoid strict fixed heights where text can grow.

**4. Adaptive Layouts for Large Scales**

At large font scales, read `LocalDensity.current.fontScale` and adapt layout accordingly: allow wrapping, adjust spacing, simplify layout, and, if needed, change orientation or arrangement so content remains readable and not clipped.

**5. Testing Text Scaling**

```kotlin
@Preview(fontScale = 1.0f)
@Preview(fontScale = 2.0f)
@Composable
fun TextScalingPreview() {
    MyScreen()
}
```

**Common Pitfalls:**
- Using `dp` instead of `sp` for text
- Fixed container heights that cause clipping when text is scaled
- Ignoring minimum touch target sizes (typically at least 48dp, specified in `dp`, not `sp`), especially when text becomes larger
- Not testing at extreme scale factors

---

## Дополнительные Вопросы (RU)

- В чем разница между масштабированием шрифта и масштабированием размера экрана (display size)?
- Как обрабатывать масштабирование текста в пользовательских `View`?
- Что происходит, когда масштабирование текста превышает 200%?
- Как сохранять минимальные размеры областей касания при масштабировании текста?
- Как тестировать масштабирование текста в автоматизированных тестах?

## Follow-ups

- What is the difference between font scaling and display size scaling?
- How do you handle text scaling in custom views?
- What happens when text scaling exceeds 200%?
- How do you maintain minimum touch targets when text scales?
- How do you test text scaling in automated tests?

## Ссылки (RU)

- Android Accessibility: https://developer.android.com/guide/topics/ui/accessibility/text-and-content
- Material Design Typography: https://m3.material.io/styles/typography/overview
- WCAG Guidelines: https://www.w3.org/WAI/WCAG21/quickref/#resize-text

## References

- Android Accessibility: https://developer.android.com/guide/topics/ui/accessibility/text-and-content
- Material Design Typography: https://m3.material.io/styles/typography/overview
- WCAG Guidelines: https://www.w3.org/WAI/WCAG21/quickref/#resize-text

## Related Questions

### Prerequisites / Concepts

- [[c-accessibility]]

### Related

- [[q-accessibility-compose--android--medium]] - Accessibility in Compose
- [[q-accessibility-testing--android--medium]] - Accessibility testing

### Advanced

```
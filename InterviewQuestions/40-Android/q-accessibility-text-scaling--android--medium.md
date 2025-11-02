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
  - q-accessibility-compose--android--medium
  - q-accessibility-testing--android--medium
created: 2025-10-11
updated: 2025-10-29
sources: []
tags: [android/ui-accessibility, android/ui-theming, difficulty/medium]
date created: Wednesday, October 29th 2025, 4:20:10 pm
date modified: Thursday, October 30th 2025, 11:12:49 am
---

# Вопрос (RU)
> Как обрабатывать масштабирование текста для доступности в Android?

# Question (EN)
> How do you handle text scaling for accessibility in Android?

---

## Ответ (RU)

Масштабирование текста позволяет пользователям настраивать размер текста на уровне системы. Приложения должны поддерживать масштабирование до 200% для соответствия требованиям доступности.

**Основные правила:**

**1. Используйте масштабируемые единицы (sp)**

```kotlin
// ✅ Правильно - масштабируется
Text(fontSize = 16.sp)
<TextView android:textSize="16sp" />

// ❌ Неправильно - не масштабируется
Text(fontSize = 16.dp)
<TextView android:textSize="16dp" />
```

**2. Используйте Material Type Scale**

Используйте предопределенные стили типографики вместо явных размеров: `MaterialTheme.typography.headlineLarge`, `bodyMedium`, или `?attr/textAppearanceHeadlineLarge` в XML.

**3. Избегайте фиксированных высот**

```kotlin
// ❌ Обрежет текст при масштабировании
Column(modifier = Modifier.height(48.dp)) {
    Text("Длинный текст")
}

// ✅ Расширится автоматически
Column(modifier = Modifier.wrapContentHeight()) {
    Text("Длинный текст")
}
```

**4. Адаптивные макеты для больших масштабов**

При экстремальных масштабах адаптируйте макет, проверяя `LocalDensity.current.fontScale` и переключаясь между вертикальной и горизонтальной ориентацией контента.

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
- Фиксированные высоты контейнеров
- Игнорирование минимальных размеров области касания (48dp)
- Отсутствие тестирования при экстремальных масштабах

## Answer (EN)

Text scaling allows users to adjust text size system-wide. Apps must support scaling up to 200% to meet accessibility guidelines.

**Key Principles:**

**1. Use Scalable Units (sp)**

```kotlin
// ✅ Correct - scales with user settings
Text(fontSize = 16.sp)
<TextView android:textSize="16sp" />

// ❌ Wrong - won't scale
Text(fontSize = 16.dp)
<TextView android:textSize="16dp" />
```

**2. Use Material Type Scale**

Use predefined typography styles instead of explicit sizes: `MaterialTheme.typography.headlineLarge`, `bodyMedium`, or `?attr/textAppearanceHeadlineLarge` in XML.

**3. Avoid Fixed Heights**

```kotlin
// ❌ Clips text when scaled
Column(modifier = Modifier.height(48.dp)) {
    Text("Long text")
}

// ✅ Expands automatically
Column(modifier = Modifier.wrapContentHeight()) {
    Text("Long text")
}
```

**4. Adaptive Layouts for Large Scales**

At extreme scales, adapt layout by checking `LocalDensity.current.fontScale` and switching between vertical and horizontal content orientation.

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
- Fixed container heights
- Ignoring minimum touch target sizes (48dp)
- Not testing at extreme scales

---

## Follow-ups

- What is the difference between font scaling and display size scaling?
- How do you handle text scaling in custom views?
- What happens when text scaling exceeds 200%?
- How do you maintain minimum touch targets when text scales?
- How do you test text scaling in automated tests?

## References

- Android Accessibility: https://developer.android.com/guide/topics/ui/accessibility/text-and-content
- Material Design Typography: https://m3.material.io/styles/typography/overview
- WCAG Guidelines: https://www.w3.org/WAI/WCAG21/quickref/#resize-text

## Related Questions

### Prerequisites
- [[q-compose-text-basics--android--easy]] - Basic text rendering in Compose
- [[q-material-theming--android--medium]] - Material Design theming

### Related
- [[q-accessibility-compose--android--medium]] - Accessibility in Compose
- [[q-accessibility-testing--android--medium]] - Accessibility testing
- [[q-responsive-layouts--android--medium]] - Responsive layout design

### Advanced
- [[q-custom-accessibility-services--android--hard]] - Custom accessibility services
- [[q-advanced-a11y-patterns--android--hard]] - Advanced accessibility patterns

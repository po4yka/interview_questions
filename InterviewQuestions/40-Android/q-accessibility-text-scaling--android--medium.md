---
id: 20251012-122755
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
updated: 2025-10-15
sources:
  - https://developer.android.com/guide/topics/ui/accessibility/text-and-content
  - https://m3.material.io/styles/typography/overview
tags: [android/ui-accessibility, android/ui-theming, difficulty/medium]
---
# Вопрос (RU)
> Как обрабатывать масштабирование текста для доступности в Android?

# Question (EN)
> How do you handle text scaling for accessibility in Android?

---

## Ответ (RU)

Масштабирование текста позволяет пользователям настраивать размер текста на уровне системы. Приложения должны поддерживать масштабирование до 200% (API 34+ до 320%) для соответствия требованиям доступности.

**Ключевые концепции:**

**1. Используйте масштабируемые единицы (SP)**

Всегда используйте `sp` для размеров текста:

```kotlin
// XML
<TextView
    android:textSize="16sp" /> <!-- ✅ Масштабируется -->
<TextView
    android:textSize="16dp" /> <!-- ❌ НЕ масштабируется -->

// Compose
Text(fontSize = 16.sp) // ✅ Автоматически масштабируется
```

**2. Используйте Material Type Scale**

```kotlin
// Compose
Text(style = MaterialTheme.typography.headlineLarge)
Text(style = MaterialTheme.typography.bodyMedium)

// XML
<TextView android:textAppearance="?attr/textAppearanceHeadlineLarge" />
```

**3. Избегайте фиксированных высот**

Используйте `wrap_content` или гибкие ограничения:

```kotlin
// ПЛОХО
Column(modifier = Modifier.height(48.dp)) { // ❌ Обрежет текст
    Text("Длинный текст")
}

// ХОРОШО
Column(modifier = Modifier.wrapContentHeight()) { // ✅ Расширяется
    Text("Длинный текст")
}

// XML
<TextView android:layout_height="wrap_content" /> <!-- ✅ Адаптивная -->
```

**4. Тестируйте с разными масштабами**

```kotlin
@Preview(fontScale = 1.0f)
@Preview(fontScale = 1.5f)
@Preview(fontScale = 2.0f)
@Composable
fun TextScalingPreview() {
    MyScreen()
}

// Настройки > Дисплей > Размер шрифта
```

**5. Поддерживайте минимальные области касания 48dp**

```kotlin
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp) // ✅ Минимальная область касания
) {
    Icon(Icons.Default.Favorite, "Избранное")
}
```

**6. Адаптивные макеты для экстремальных масштабов**

```kotlin
@Composable
fun AdaptiveLayout() {
    val fontScale = LocalDensity.current.fontScale
    if (fontScale > 1.5f) {
        Column { /* вертикальный макет */ }
    } else {
        Row { /* горизонтальный макет */ }
    }
}
```

**Лучшие практики:**

- Всегда используйте `sp` для текста (НИКОГДА `dp`)
- Используйте Material typography
- Тестируйте при 200% масштабе
- Избегайте фиксированных размеров
- Разрешайте перенос текста
- Сохраняйте области касания 48dp
- Тестируйте на реальных устройствах

**Частые ошибки:**

```kotlin
// ❌ ПЛОХО: Фиксированная высота
Box(modifier = Modifier.height(56.dp)) {
    Text("Обрежется при 200%")
}

// ✅ ХОРОШО: Гибкая высота
Box(modifier = Modifier.heightIn(min = 56.dp)) {
    Text("Расширится при необходимости")
}

// ❌ ПЛОХО: Использование dp
Text(fontSize = 16.dp)

// ✅ ХОРОШО: Использование sp
Text(fontSize = 16.sp)
```

**Чеклист тестирования:**

1. Включите максимальный размер шрифта в Настройках
2. Проверьте все экраны
3. Убедитесь, что текст читаем (не обрезан)
4. Проверьте интерактивные элементы
5. Убедитесь, что макеты не ломаются
6. Проверьте скроллинг
7. Тестируйте в портретной и альбомной ориентации

## Answer (EN)

Text scaling allows users to adjust text size system-wide. Apps must support scaling up to 200% (API 34+ up to 320%) to meet accessibility guidelines.

**Key Concepts:**

**1. Use Scalable Units (SP)**

Always use `sp` for text sizes:

```kotlin
// XML
<TextView
    android:textSize="16sp" /> <!-- ✅ Scales -->
<TextView
    android:textSize="16dp" /> <!-- ❌ Won't scale -->

// Compose
Text(fontSize = 16.sp) // ✅ Scales automatically
```

**2. Use Material Type Scale**

```kotlin
// Compose
Text(style = MaterialTheme.typography.headlineLarge)
Text(style = MaterialTheme.typography.bodyMedium)

// XML
<TextView android:textAppearance="?attr/textAppearanceHeadlineLarge" />
```

**3. Avoid Fixed Heights**

Use `wrap_content` or flexible constraints:

```kotlin
// BAD
Column(modifier = Modifier.height(48.dp)) { // ❌ Clips text
    Text("Long text")
}

// GOOD
Column(modifier = Modifier.wrapContentHeight()) { // ✅ Expands
    Text("Long text")
}

// XML
<TextView android:layout_height="wrap_content" /> <!-- ✅ Adaptive -->
```

**4. Test with Different Scales**

```kotlin
@Preview(fontScale = 1.0f)
@Preview(fontScale = 1.5f)
@Preview(fontScale = 2.0f)
@Composable
fun TextScalingPreview() {
    MyScreen()
}

// Settings > Display > Font size
```

**5. Maintain Minimum Touch Targets (48dp)**

```kotlin
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp) // ✅ Minimum touch target
) {
    Icon(Icons.Default.Favorite, "Favorite")
}
```

**6. Adaptive Layouts for Extreme Scales**

```kotlin
@Composable
fun AdaptiveLayout() {
    val fontScale = LocalDensity.current.fontScale
    if (fontScale > 1.5f) {
        Column { /* vertical layout */ }
    } else {
        Row { /* horizontal layout */ }
    }
}
```

**Best Practices:**

- Always use `sp` for text (NEVER `dp`)
- Use Material typography
- Test at 200% scale
- Avoid fixed dimensions
- Allow text wrapping
- Maintain 48dp touch targets
- Test on real devices

**Common Pitfalls:**

```kotlin
// ❌ BAD: Fixed height
Box(modifier = Modifier.height(56.dp)) {
    Text("Clips at 200%")
}

// ✅ GOOD: Flexible height
Box(modifier = Modifier.heightIn(min = 56.dp)) {
    Text("Expands as needed")
}

// ❌ BAD: Using dp
Text(fontSize = 16.dp)

// ✅ GOOD: Using sp
Text(fontSize = 16.sp)
```

**Testing Checklist:**

1. Enable largest font size in Settings
2. Check all screens
3. Verify text is readable (not clipped)
4. Check interactive elements
5. Ensure layouts don't break
6. Verify scrolling works
7. Test in portrait and landscape

---

## Follow-ups

- What's the difference between font scaling and display size scaling?
- How do you handle text scaling in custom views?
- What happens when text scaling exceeds 200%?

## Related Questions

- [[q-accessibility-compose--android--medium]] - Accessibility in Compose
- [[q-accessibility-testing--android--medium]] - Accessibility testing


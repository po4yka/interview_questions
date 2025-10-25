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
tags: [android/ui-accessibility, android/ui-theming, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:53:21 pm
---

# Question (EN)
> How do you handle text scaling for accessibility in Android?

# Вопрос (RU)
> Как обрабатывать масштабирование текста для доступности в Android?

---

## Answer (EN)

Text scaling (also called font scaling) allows users to adjust text size system-wide to improve readability. Apps must support text scaling up to 200% (API 34+ supports up to 320%) to meet accessibility guidelines. Proper text scaling implementation ensures layouts adapt gracefully without cutting off content or breaking UI.

**Key Concepts:**

**1. Use Scalable Units (SP)**

Always use `sp` (scale-independent pixels) for text sizes:

```kotlin
// View-based XML
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textSize="16sp" /> <!-- ✅ Scales with user preference -->

<!-- ❌ NEVER use dp for text -->
<TextView
    android:textSize="16dp" /> <!-- Will NOT scale -->

// Compose
Text(
    text = "Hello World",
    fontSize = 16.sp // ✅ Scales automatically
)
```

**2. Use Material Type Scale**

Use predefined text styles from Material Design:

```kotlin
// Compose - Material 3
Text(
    text = "Headline",
    style = MaterialTheme.typography.headlineLarge
)

Text(
    text = "Body text",
    style = MaterialTheme.typography.bodyMedium
)

// View-based XML - Material 3
<TextView
    android:text="Headline"
    android:textAppearance="?attr/textAppearanceHeadlineLarge" />

<TextView
    android:text="Body"
    android:textAppearance="?attr/textAppearanceBodyMedium" />
```

**3. Handle Layout Constraints**

Ensure layouts adapt to larger text:

```kotlin
// Compose - Flexible layouts
Column(
    modifier = Modifier.fillMaxWidth()
) {
    Text(
        text = longText,
        style = MaterialTheme.typography.bodyLarge,
        maxLines = Int.MAX_VALUE, // ✅ Allow text to wrap
        overflow = TextOverflow.Visible
    )
}

// View-based XML
<TextView
    android:layout_width="0dp"
    android:layout_height="wrap_content"
    android:layout_weight="1"
    android:maxLines="2147483647"
    android:ellipsize="none" />
```

**4. Avoid Fixed Heights**

Use `wrap_content` or flexible constraints:

```kotlin
// BAD - Fixed height clips large text
Column(
    modifier = Modifier.height(48.dp) // ❌ Will clip text at 200% scale
) {
    Text("Long text that might wrap")
}

// GOOD - Adaptive height
Column(
    modifier = Modifier
        .fillMaxWidth()
        .wrapContentHeight() // ✅ Expands for large text
) {
    Text("Long text that might wrap")
}

// View-based XML
<!-- BAD -->
<TextView
    android:layout_height="48dp" /> <!-- ❌ Fixed height -->

<!-- GOOD -->
<TextView
    android:layout_height="wrap_content" /> <!-- ✅ Adaptive -->
```

**5. Test with Different Scales**

Test your UI at various text scales:

```kotlin
// Compose Preview with different font scales
@Preview(fontScale = 1.0f)
@Preview(fontScale = 1.5f)
@Preview(fontScale = 2.0f)
@Composable
fun TextScalingPreview() {
    MyScreen()
}

// Manual testing on device
// Settings > Display > Font size (or Display size)
// Or use developer options to test extreme scales
```

**6. Use Minimum Touch Targets**

Ensure interactive elements remain accessible:

```kotlin
// Compose - Maintain minimum 48dp touch target
IconButton(
    onClick = { },
    modifier = Modifier
        .size(48.dp) // ✅ Minimum touch target
) {
    Icon(
        Icons.Default.Favorite,
        contentDescription = "Favorite",
        modifier = Modifier.size(24.dp) // Icon size can be smaller
    )
}

// Even with large text, touch target stays 48dp
Button(
    onClick = { },
    modifier = Modifier
        .defaultMinSize(minHeight = 48.dp) // ✅ Enforces minimum
) {
    Text("Click me", fontSize = 12.sp)
}
```

**7. Handle Multiline Text**

Allow text to wrap instead of truncating:

```kotlin
// Compose
Text(
    text = longDescription,
    maxLines = Int.MAX_VALUE, // ✅ No line limit
    overflow = TextOverflow.Visible,
    modifier = Modifier.fillMaxWidth()
)

// For single-line cases, consider making them multiline
Text(
    text = title,
    maxLines = 2, // Allow wrapping to 2 lines
    overflow = TextOverflow.Ellipsis
)

// View-based
<TextView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:maxLines="2147483647"
    android:ellipsize="none" />
```

**8. Responsive Typography**

Use NonScaledTextSize for special cases only:

```kotlin
// Most text should scale - use this RARELY
@Composable
fun NonScaledText(text: String) {
    // Only for decorative or non-essential text
    val density = LocalDensity.current
    Text(
        text = text,
        fontSize = with(density) { 16.dp.toSp() } // Won't scale with user preference
    )
}

// Better approach: Use Material typography that scales appropriately
Text(
    text = decorativeText,
    style = MaterialTheme.typography.labelSmall // Still scales but starts smaller
)
```

**9. Test Layouts Programmatically**

Test text scaling in UI tests:

```kotlin
@Test
fun testTextScaling() {
    composeTestRule.setContent {
        CompositionLocalProvider(
            LocalDensity provides Density(
                density = 1f,
                fontScale = 2.0f // Simulate 200% text scale
            )
        ) {
            MyScreen()
        }
    }

    // Verify layout doesn't break
    composeTestRule
        .onNodeWithText("Important button")
        .assertIsDisplayed()
        .assertHasClickAction()
}
```

**10. Handle Edge Cases**

Deal with extreme scaling gracefully:

```kotlin
// Compose - Adaptive layout based on font scale
@Composable
fun AdaptiveLayout() {
    val fontScale = LocalDensity.current.fontScale

    if (fontScale > 1.5f) {
        // Vertical layout for large text
        Column {
            Icon(Icons.Default.Star, "Rating")
            Text("4.5 stars")
        }
    } else {
        // Horizontal layout for normal text
        Row {
            Icon(Icons.Default.Star, "Rating")
            Text("4.5 stars")
        }
    }
}
```

**Best Practices:**

- **Always use sp for text**: Never use dp for font sizes
- **Use Material typography**: Predefined scales handle accessibility well
- **Test at 200% scale**: Minimum requirement for accessibility
- **Avoid fixed dimensions**: Use wrap_content and flexible constraints
- **Allow text wrapping**: Don't truncate important information
- **Maintain touch targets**: Keep minimum 48dp for interactive elements
- **Test on real devices**: Emulators may not accurately reflect text scaling
- **Consider line height**: Large text needs proportional line spacing

**Common Pitfalls:**

```kotlin
// ❌ BAD: Fixed heights clip text
Box(modifier = Modifier.height(56.dp)) {
    Text("This will clip at 200% scale")
}

// ✅ GOOD: Flexible height
Box(modifier = Modifier.heightIn(min = 56.dp)) {
    Text("This will expand as needed")
}

// ❌ BAD: Using dp for text
Text(text = "Wrong", fontSize = 16.dp)

// ✅ GOOD: Using sp for text
Text(text = "Correct", fontSize = 16.sp)

// ❌ BAD: Single line with ellipsis
Text(
    text = importantMessage,
    maxLines = 1,
    overflow = TextOverflow.Ellipsis // Hides content
)

// ✅ GOOD: Allow wrapping
Text(
    text = importantMessage,
    maxLines = 3,
    overflow = TextOverflow.Ellipsis // Still readable
)
```

**Testing Checklist:**

1. Enable largest font size in Settings
2. Navigate through all screens
3. Verify all text is readable (not clipped)
4. Check buttons and interactive elements are still usable
5. Ensure layouts don't overlap or break
6. Verify scrolling works for overflowing content
7. Test in both portrait and landscape orientations
8. Check error messages and dialogs

## Ответ (RU)

Масштабирование текста (также называемое масштабированием шрифта) позволяет пользователям настраивать размер текста на уровне системы для улучшения читаемости. Приложения должны поддерживать масштабирование текста до 200% (API 34+ поддерживает до 320%) для соответствия требованиям доступности. Правильная реализация масштабирования текста обеспечивает корректную адаптацию макетов без обрезания контента или нарушения UI.

**Ключевые концепции:**

**1. Используйте масштабируемые единицы (SP)**

Всегда используйте `sp` (scale-independent pixels) для размеров текста:

```kotlin
// На основе View - XML
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textSize="16sp" /> <!-- ✅ Масштабируется с настройками пользователя -->

<!-- ❌ НИКОГДА не используйте dp для текста -->
<TextView
    android:textSize="16dp" /> <!-- НЕ будет масштабироваться -->

// Compose
Text(
    text = "Привет мир",
    fontSize = 16.sp // ✅ Автоматически масштабируется
)
```

**2. Используйте Material Type Scale**

Используйте предопределённые стили текста из Material Design:

```kotlin
// Compose - Material 3
Text(
    text = "Заголовок",
    style = MaterialTheme.typography.headlineLarge
)

Text(
    text = "Основной текст",
    style = MaterialTheme.typography.bodyMedium
)
```

**3. Обрабатывайте ограничения макета**

Убедитесь, что макеты адаптируются к большому тексту:

```kotlin
// Compose - Гибкие макеты
Column(
    modifier = Modifier.fillMaxWidth()
) {
    Text(
        text = longText,
        style = MaterialTheme.typography.bodyLarge,
        maxLines = Int.MAX_VALUE, // ✅ Разрешить перенос текста
        overflow = TextOverflow.Visible
    )
}
```

**4. Избегайте фиксированных высот**

Используйте `wrap_content` или гибкие ограничения:

```kotlin
// ПЛОХО - Фиксированная высота обрезает большой текст
Column(
    modifier = Modifier.height(48.dp) // ❌ Обрежет текст при 200% масштабе
) {
    Text("Длинный текст с переносом")
}

// ХОРОШО - Адаптивная высота
Column(
    modifier = Modifier
        .fillMaxWidth()
        .wrapContentHeight() // ✅ Расширяется для большого текста
) {
    Text("Длинный текст с переносом")
}
```

**5. Тестируйте с разными масштабами**

Тестируйте UI при различных масштабах текста:

```kotlin
// Compose Preview с разными масштабами шрифта
@Preview(fontScale = 1.0f)
@Preview(fontScale = 1.5f)
@Preview(fontScale = 2.0f)
@Composable
fun TextScalingPreview() {
    MyScreen()
}

// Ручное тестирование на устройстве
// Настройки > Дисплей > Размер шрифта
```

**6. Поддерживайте минимальные области касания**

Убедитесь, что интерактивные элементы остаются доступными:

```kotlin
// Compose - Сохранение минимальной области касания 48dp
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp) // ✅ Минимальная область касания
) {
    Icon(
        Icons.Default.Favorite,
        contentDescription = "Избранное",
        modifier = Modifier.size(24.dp) // Размер иконки может быть меньше
    )
}
```

**Лучшие практики:**

- **Всегда используйте sp для текста**: Никогда не используйте dp для размеров шрифта
- **Используйте Material typography**: Предопределённые масштабы хорошо работают с доступностью
- **Тестируйте при 200% масштабе**: Минимальное требование для доступности
- **Избегайте фиксированных размеров**: Используйте wrap_content и гибкие ограничения
- **Разрешайте перенос текста**: Не обрезайте важную информацию
- **Поддерживайте области касания**: Сохраняйте минимум 48dp для интерактивных элементов
- **Тестируйте на реальных устройствах**: Эмуляторы могут неточно отражать масштабирование текста

---

## Follow-ups

- What's the difference between font scaling and display size scaling?
- How do you handle text scaling in custom views?
- What are the performance implications of adaptive layouts?
- How do you test text scaling in different screen orientations?
- What happens when text scaling exceeds 200%?

## References

- [Android Text Scaling Guide](https://developer.android.com/guide/topics/ui/accessibility/text-and-content)
- [Material Design Typography](https://m3.material.io/styles/typography/overview)
- [Compose Testing Documentation](https://developer.android.com/jetpack/compose/testing)
- [Accessibility Testing Guide](https://developer.android.com/guide/topics/ui/accessibility/testing)

## Related Questions

### Related (Medium)
- [[q-accessibility-compose--android--medium]] - Accessibility
- [[q-accessibility-testing--android--medium]] - Accessibility
- [[q-custom-view-accessibility--android--medium]] - Accessibility
- [[q-accessibility-color-contrast--android--medium]] - Accessibility
- [[q-accessibility-talkback--android--medium]] - Accessibility


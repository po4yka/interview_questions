---
id: 20251012-122751
title: Accessibility Color Contrast / Контрастность цветов для доступности
aliases: [Color Contrast, Контрастность цветов]
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
  - q-custom-view-accessibility--android--medium
created: 2025-10-11
updated: 2025-01-27
tags: [android/ui-accessibility, android/ui-theming, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Как обеспечить доступную контрастность цветов в Android-приложении согласно WCAG?

---

# Question (EN)
> How to ensure accessible color contrast in Android apps according to WCAG?

## Ответ (RU)

[[c-accessibility|Контрастность цвета]] — это отношение яркости между текстом и фоном. WCAG устанавливает минимальные требования: **4.5:1** для обычного текста (уровень AA) и **7:1** для AAA. Material Design автоматически обеспечивает достаточную контрастность через систему цветовых ролей.

### Требования WCAG

```kotlin
// WCAG AA (минимум):
// Обычный текст (< 18pt):  4.5:1
// Крупный текст (≥ 18pt):  3:1

// WCAG AAA (расширенный):
// Обычный текст:  7:1
// Крупный текст:  4.5:1

// Примеры:
// Черный на белом:    21:1  (отлично)
// #757575 на белом:   4.6:1 (проходит AA)
// #959595 на белом:   2.8:1 (не проходит)
```

### Material цветовые роли

```kotlin
@Composable
fun MaterialColorExample() {
    // ✅ Material автоматически гарантирует контраст
    Surface(color = MaterialTheme.colorScheme.primary) {
        Text(
            text = "Button",
            color = MaterialTheme.colorScheme.onPrimary // Гарантия 4.5:1
        )
    }
}

// Основные пары:
// primary / onPrimary
// surface / onSurface
// background / onBackground
// error / onError
```

### Типичные ошибки

**1. Светлый текст на светлом фоне:**

```kotlin
// ❌ Недостаточная контрастность (1.6:1)
Text(
    text = "Secondary",
    color = Color(0xFFCCCCCC),
    modifier = Modifier.background(Color.White)
)

// ✅ Достаточная контрастность (4.6:1)
Text(
    text = "Secondary",
    color = MaterialTheme.colorScheme.onSurfaceVariant,
    modifier = Modifier.background(MaterialTheme.colorScheme.surface)
)
```

**2. Использование только цвета для передачи информации:**

```kotlin
// ❌ Цветослепые пользователи не различат
Row {
    Text("Success", color = Color.Green)
    Text("Error", color = Color.Red)
}

// ✅ Иконки + цвет + текст
Row {
    Icon(Icons.Default.CheckCircle, null, tint = MaterialTheme.colorScheme.tertiary)
    Text("Success", color = MaterialTheme.colorScheme.tertiary)
}
Row {
    Icon(Icons.Default.Error, null, tint = MaterialTheme.colorScheme.error)
    Text("Error", color = MaterialTheme.colorScheme.error)
}
```

**3. Одинаковые цвета для светлой и темной темы:**

```kotlin
// ❌ В темной теме контраст нарушится
val textColor = Color(0xFF212121) // Темный текст

// ✅ Material адаптирует цвета под тему
Text(
    text = "Content",
    color = MaterialTheme.colorScheme.onBackground,
    modifier = Modifier.background(MaterialTheme.colorScheme.background)
)
```

### Тестирование

```kotlin
// Автоматическая проверка контраста
@Test
fun testColorContrast() {
    val foreground = Color(0xFF757575)
    val background = Color.White
    val ratio = ContrastChecker.contrastRatio(foreground, background)

    assertTrue("Контраст $ratio:1 не соответствует AA (4.5:1)", ratio >= 4.5)
}
```

**Инструменты:**
- **Accessibility Scanner** (Android app) — сканирует запущенное приложение
- **Android Studio** — цветовой пикер показывает контраст
- **WebAIM Contrast Checker** — онлайн-проверка

### Цветовая слепота

Около 8% мужчин и 0.5% женщин имеют дефицит цветового зрения. Не полагайтесь только на цвет:

```kotlin
// ✅ Форма + иконка + цвет
@Composable
fun StatusIndicator(isOnline: Boolean) {
    Row {
        Box(
            Modifier
                .size(16.dp)
                .background(
                    color = if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828),
                    shape = if (isOnline) CircleShape else RoundedCornerShape(2.dp)
                )
        )
        Icon(
            imageVector = if (isOnline) Icons.Default.CheckCircle else Icons.Default.Cancel,
            contentDescription = null
        )
        Text(if (isOnline) "Online" else "Offline")
    }
}
```

### Best Practices

1. **Используйте Material цветовые роли** — они гарантируют контраст
2. **Не полагайтесь только на цвет** — добавляйте иконки, формы, текст
3. **Тестируйте в темной теме** — используйте `@Preview(uiMode = UI_MODE_NIGHT_YES)`
4. **Автоматизируйте проверки** — добавьте тесты контраста в CI
5. **Проверяйте Accessibility Scanner** — регулярно сканируйте экраны

---

## Answer (EN)

[[c-accessibility|Color contrast]] is the luminance ratio between text and background. WCAG requires minimum **4.5:1** for normal text (level AA) and **7:1** for AAA. Material Design automatically ensures sufficient contrast through its color role system.

### WCAG Requirements

```kotlin
// WCAG AA (minimum):
// Normal text (< 18pt):  4.5:1
// Large text (≥ 18pt):   3:1

// WCAG AAA (enhanced):
// Normal text:  7:1
// Large text:   4.5:1

// Examples:
// Black on white:    21:1  (excellent)
// #757575 on white:  4.6:1 (passes AA)
// #959595 on white:  2.8:1 (fails)
```

### Material Color Roles

```kotlin
@Composable
fun MaterialColorExample() {
    // ✅ Material automatically guarantees contrast
    Surface(color = MaterialTheme.colorScheme.primary) {
        Text(
            text = "Button",
            color = MaterialTheme.colorScheme.onPrimary // Guaranteed 4.5:1
        )
    }
}

// Key pairs:
// primary / onPrimary
// surface / onSurface
// background / onBackground
// error / onError
```

### Common Violations

**1. Light text on light background:**

```kotlin
// ❌ Insufficient contrast (1.6:1)
Text(
    text = "Secondary",
    color = Color(0xFFCCCCCC),
    modifier = Modifier.background(Color.White)
)

// ✅ Sufficient contrast (4.6:1)
Text(
    text = "Secondary",
    color = MaterialTheme.colorScheme.onSurfaceVariant,
    modifier = Modifier.background(MaterialTheme.colorScheme.surface)
)
```

**2. Using color alone to convey information:**

```kotlin
// ❌ Color blind users cannot distinguish
Row {
    Text("Success", color = Color.Green)
    Text("Error", color = Color.Red)
}

// ✅ Icons + color + text
Row {
    Icon(Icons.Default.CheckCircle, null, tint = MaterialTheme.colorScheme.tertiary)
    Text("Success", color = MaterialTheme.colorScheme.tertiary)
}
Row {
    Icon(Icons.Default.Error, null, tint = MaterialTheme.colorScheme.error)
    Text("Error", color = MaterialTheme.colorScheme.error)
}
```

**3. Same colors for light and dark theme:**

```kotlin
// ❌ Dark theme will break contrast
val textColor = Color(0xFF212121) // Dark text

// ✅ Material adapts colors to theme
Text(
    text = "Content",
    color = MaterialTheme.colorScheme.onBackground,
    modifier = Modifier.background(MaterialTheme.colorScheme.background)
)
```

### Testing

```kotlin
// Automated contrast check
@Test
fun testColorContrast() {
    val foreground = Color(0xFF757575)
    val background = Color.White
    val ratio = ContrastChecker.contrastRatio(foreground, background)

    assertTrue("Contrast $ratio:1 does not meet AA (4.5:1)", ratio >= 4.5)
}
```

**Tools:**
- **Accessibility Scanner** (Android app) — scans running app
- **Android Studio** — color picker shows contrast ratio
- **WebAIM Contrast Checker** — online validation

### Color Blindness

About 8% of men and 0.5% of women have color vision deficiency. Don't rely on color alone:

```kotlin
// ✅ Shape + icon + color
@Composable
fun StatusIndicator(isOnline: Boolean) {
    Row {
        Box(
            Modifier
                .size(16.dp)
                .background(
                    color = if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828),
                    shape = if (isOnline) CircleShape else RoundedCornerShape(2.dp)
                )
        )
        Icon(
            imageVector = if (isOnline) Icons.Default.CheckCircle else Icons.Default.Cancel,
            contentDescription = null
        )
        Text(if (isOnline) "Online" else "Offline")
    }
}
```

### Best Practices

1. **Use Material color roles** — they guarantee contrast
2. **Don't rely on color alone** — add icons, shapes, text
3. **Test in dark theme** — use `@Preview(uiMode = UI_MODE_NIGHT_YES)`
4. **Automate checks** — add contrast tests to CI
5. **Run Accessibility Scanner** — regularly scan screens

---

## Follow-ups

- How do you implement automated contrast testing in CI/CD pipeline?
- What's the performance impact of color contrast calculations at runtime?
- How to handle contrast requirements for custom dynamic themes?
- What are the trade-offs between WCAG AA and AAA compliance?
- How to test color contrast with color blindness simulators?

## References

- [[c-accessibility]]
- [WCAG 2.1 Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Material Design Color System](https://m3.material.io/foundations/color)
- [Android Accessibility](https://developer.android.com/guide/topics/ui/accessibility)

## Related Questions

### Prerequisites (Easier)
- [[q-accessibility-compose--android--medium]] - Basic accessibility in Compose

### Related (Medium)
- [[q-accessibility-testing--android--medium]] - Accessibility testing approaches
- [[q-custom-view-accessibility--android--medium]] - Custom view accessibility

### Advanced (Harder)
- [[q-accessibility-talkback--android--medium]] - TalkBack implementation details

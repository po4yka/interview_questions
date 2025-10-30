---
id: 20251012-122751
title: Accessibility Color Contrast / Контрастность цветов для доступности
aliases: [Accessibility Color Contrast, Контрастность цветов для доступности]
topic: android
subtopics: [ui-accessibility, ui-theming]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-accessibility, q-accessibility-compose--android--medium, q-accessibility-testing--android--medium, q-custom-view-accessibility--android--medium]
created: 2025-10-11
updated: 2025-10-29
tags: [android/ui-accessibility, android/ui-theming, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Как обеспечить доступную контрастность цветов в Android-приложении согласно WCAG?

---

# Question (EN)
> How to ensure accessible color contrast in Android apps according to WCAG?

## Ответ (RU)

[[c-accessibility|Контрастность цвета]] — отношение яркости текста к фону. WCAG требует минимум **4.5:1** для обычного текста (AA) и **7:1** для AAA. Material Design гарантирует контраст через систему цветовых ролей.

### Требования WCAG и Material цветовые роли

**WCAG AA**: обычный текст < 18pt — 4.5:1, крупный ≥ 18pt — 3:1
**WCAG AAA**: обычный текст — 7:1, крупный — 4.5:1
**Примеры**: черный/белый 21:1 ✅, #757575/белый 4.6:1 ✅, #959595/белый 2.8:1 ❌

```kotlin
@Composable
fun MaterialColorExample() {
    // ✅ Material гарантирует контраст 4.5:1
    Surface(color = MaterialTheme.colorScheme.primary) {
        Text(text = "Button", color = MaterialTheme.colorScheme.onPrimary)
    }
}
// Основные пары: primary/onPrimary, surface/onSurface, background/onBackground
```

### Типичные ошибки

```kotlin
// ❌ 1. Недостаточная контрастность (1.6:1)
Text("Secondary", color = Color(0xFFCCCCCC), modifier = Modifier.background(Color.White))

// ❌ 2. Только цвет для передачи информации (недоступно для цветослепых)
Row {
    Text("Success", color = Color.Green)
    Text("Error", color = Color.Red)
}

// ❌ 3. Игнорирование темной темы
val textColor = Color(0xFF212121) // Темная тема нарушит контраст

// ✅ Правильный подход: контраст + иконки + адаптация к теме
Text(
    "Secondary",
    color = MaterialTheme.colorScheme.onSurfaceVariant, // Контраст 4.6:1
    modifier = Modifier.background(MaterialTheme.colorScheme.surface)
)
Row {
    Icon(Icons.Default.CheckCircle, null, tint = MaterialTheme.colorScheme.tertiary)
    Text("Success", color = MaterialTheme.colorScheme.tertiary)
}
```

### Цветовая слепота и тестирование

8% мужчин и 0.5% женщин имеют дефицит цветового зрения — не полагайтесь только на цвет:

```kotlin
// ✅ Форма + иконка + цвет для доступности
@Composable
fun StatusIndicator(isOnline: Boolean) {
    Row {
        Box(
            Modifier.size(16.dp).background(
                color = if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828),
                shape = if (isOnline) CircleShape else RoundedCornerShape(2.dp) // Разная форма
            )
        )
        Icon(if (isOnline) Icons.Default.CheckCircle else Icons.Default.Cancel, null)
        Text(if (isOnline) "Online" else "Offline")
    }
}

@Test
fun testColorContrast() {
    val ratio = ContrastChecker.contrastRatio(Color(0xFF757575), Color.White)
    assertTrue("Контраст $ratio:1 < 4.5:1", ratio >= 4.5)
}
```

**Инструменты**: Accessibility Scanner (Android), Android Studio (цветовой пикер), WebAIM Contrast Checker

**Best Practices**: Используйте Material цветовые роли, не полагайтесь только на цвет, тестируйте темную тему (`@Preview(uiMode = UI_MODE_NIGHT_YES)`), автоматизируйте проверки в CI

---

## Answer (EN)

[[c-accessibility|Color contrast]] is the luminance ratio between text and background. WCAG requires minimum **4.5:1** for normal text (AA) and **7:1** for AAA. Material Design guarantees contrast through its color role system.

### WCAG Requirements and Material Color Roles

**WCAG AA**: normal text < 18pt — 4.5:1, large ≥ 18pt — 3:1
**WCAG AAA**: normal text — 7:1, large — 4.5:1
**Examples**: black/white 21:1 ✅, #757575/white 4.6:1 ✅, #959595/white 2.8:1 ❌

```kotlin
@Composable
fun MaterialColorExample() {
    // ✅ Material guarantees 4.5:1 contrast
    Surface(color = MaterialTheme.colorScheme.primary) {
        Text(text = "Button", color = MaterialTheme.colorScheme.onPrimary)
    }
}
// Key pairs: primary/onPrimary, surface/onSurface, background/onBackground
```

### Common Violations

```kotlin
// ❌ 1. Insufficient contrast (1.6:1)
Text("Secondary", color = Color(0xFFCCCCCC), modifier = Modifier.background(Color.White))

// ❌ 2. Color alone for information (inaccessible for color blind users)
Row {
    Text("Success", color = Color.Green)
    Text("Error", color = Color.Red)
}

// ❌ 3. Ignoring dark theme
val textColor = Color(0xFF212121) // Dark theme breaks contrast

// ✅ Correct approach: contrast + icons + theme-adaptive
Text(
    "Secondary",
    color = MaterialTheme.colorScheme.onSurfaceVariant, // Contrast 4.6:1
    modifier = Modifier.background(MaterialTheme.colorScheme.surface)
)
Row {
    Icon(Icons.Default.CheckCircle, null, tint = MaterialTheme.colorScheme.tertiary)
    Text("Success", color = MaterialTheme.colorScheme.tertiary)
}
```

### Color Blindness and Testing

8% of men and 0.5% of women have color vision deficiency — don't rely on color alone:

```kotlin
// ✅ Shape + icon + color for accessibility
@Composable
fun StatusIndicator(isOnline: Boolean) {
    Row {
        Box(
            Modifier.size(16.dp).background(
                color = if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828),
                shape = if (isOnline) CircleShape else RoundedCornerShape(2.dp) // Different shapes
            )
        )
        Icon(if (isOnline) Icons.Default.CheckCircle else Icons.Default.Cancel, null)
        Text(if (isOnline) "Online" else "Offline")
    }
}

@Test
fun testColorContrast() {
    val ratio = ContrastChecker.contrastRatio(Color(0xFF757575), Color.White)
    assertTrue("Contrast $ratio:1 < 4.5:1", ratio >= 4.5)
}
```

**Tools**: Accessibility Scanner (Android), Android Studio (color picker), WebAIM Contrast Checker

**Best Practices**: Use Material color roles, don't rely on color alone, test dark theme (`@Preview(uiMode = UI_MODE_NIGHT_YES)`), automate contrast checks in CI

---

## Follow-ups

- How to implement automated contrast validation in CI/CD pipelines?
- What are the trade-offs between WCAG AA (4.5:1) and AAA (7:1) compliance?
- How do Material3 dynamic color schemes maintain contrast guarantees?
- How to handle contrast for user-customizable brand colors?
- What tools can simulate color blindness during development and testing?

## References

- [[c-accessibility]] - Core accessibility concepts
- WCAG Contrast Guidelines
- Material Design Color System
- Android Accessibility Guide

## Related Questions

### Prerequisites (Easier)
- [[q-accessibility-compose--android--medium]] - Accessibility basics in Compose

### Related (Medium)
- [[q-accessibility-testing--android--medium]] - Testing accessibility features
- [[q-custom-view-accessibility--android--medium]] - Custom view accessibility

### Advanced (Harder)
- Screen reader optimization and semantic labeling
- Dynamic theme systems with accessibility constraints

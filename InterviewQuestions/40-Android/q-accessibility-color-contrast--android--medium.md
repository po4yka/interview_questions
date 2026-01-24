---
id: android-039
title: Accessibility Color Contrast / Контрастность цветов для доступности
aliases:
- Accessibility Color Contrast
- Контрастность цветов для доступности
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
- q-accessibility-compose--android--medium
- q-accessibility-testing--android--medium
- q-custom-view-accessibility--android--medium
created: 2025-10-11
updated: 2025-10-29
tags:
- android/ui-accessibility
- android/ui-theming
- difficulty/medium
anki_cards:
- slug: android-039-0-en
  language: en
  anki_id: 1768363501896
  synced_at: '2026-01-23T16:45:05.506961'
- slug: android-039-0-ru
  language: ru
  anki_id: 1768363501921
  synced_at: '2026-01-23T16:45:05.508382'
sources: []
---
# Вопрос (RU)
> Как обеспечить доступную контрастность цветов в Android-приложении согласно WCAG?

---

# Question (EN)
> How to ensure accessible color contrast in Android apps according to WCAG?

## Ответ (RU)

[[c-accessibility|Контрастность цвета]] — отношение яркости текста к фону. WCAG рекомендует минимум **4.5:1** для обычного текста (уровень AA) и **7:1** для уровня AAA. Для крупного текста действуют послабления. В Material Design система цветовых ролей помогает достичь нужного контраста при корректном использовании (особенно при генерации через официальные инструменты и Dynamic Color), но не гарантирует его для произвольных кастомных палитр.

### Требования WCAG И Material Цветовые Роли

**WCAG AA** (упрощённо для интервью):
- обычный текст — 4.5:1
- крупный текст — 3:1 (в WCAG: ≥ 18pt normal или ≥ 14pt жирный, на экране обычно ≈ 24sp/18sp)

**WCAG AAA**:
- обычный текст — 7:1
- крупный текст — 4.5:1

**Примеры (иллюстративно):**
- чёрный/белый ≈ 21:1 ✅
- #757575/белый ≈ 4.6:1 ✅ (минимальный запас для обычного текста)
- #959595/белый ≈ 2.8:1 ❌ (ниже AA для обычного текста)

```kotlin
@Composable
fun MaterialColorExample() {
    // ✅ При использовании рекомендуемых ролей (Material 3 / Dynamic Color)
    // пары on* над * обычно подобраны с учётом WCAG AA для текста
    Surface(color = MaterialTheme.colorScheme.primary) {
        Text(text = "Button", color = MaterialTheme.colorScheme.onPrimary)
    }
}
// Основные пары ролей: primary/onPrimary, surface/onSurface, background/onBackground, и т.д.
// Фактический контраст зависит от конкретной палитры — при кастомных цветах проверяйте явно.
```

### Типичные Ошибки

```kotlin
// ❌ 1. Потенциально недостаточный контраст для текста на белом фоне
// (серый цвет выбран "на глаз", без проверки WCAG)
Text(
    text = "Secondary",
    color = Color(0xFF959595),
    modifier = Modifier.background(Color.White)
)

// ❌ 2. Только цвет для передачи информации (недоступно для пользователей с нарушениями цветового зрения)
Row {
    Text("Success", color = Color.Green)
    Text("Error", color = Color.Red)
}

// ❌ 3. Игнорирование темной темы: жёстко заданный тёмный цвет текста
val textColor = Color(0xFF212121) // В тёмной теме на тёмном фоне контраст может стать недостаточным

// ✅ Правильный подход: роли + иконки/текст + адаптация к теме
Text(
    text = "Secondary",
    color = MaterialTheme.colorScheme.onSurfaceVariant,
    modifier = Modifier.background(MaterialTheme.colorScheme.surface)
)
Row {
    Icon(
        imageVector = Icons.Default.CheckCircle,
        contentDescription = null,
        tint = MaterialTheme.colorScheme.tertiary
    )
    Text("Success", color = MaterialTheme.colorScheme.tertiary)
}
```

### Цветовая Слепота И Тестирование

Около 8% мужчин и 0.5% женщин имеют дефицит цветового зрения — нельзя полагаться только на цвет.

```kotlin
// ✅ Форма + иконка + цвет для доступности
@Composable
fun StatusIndicator(isOnline: Boolean) {
    Row {
        Box(
            Modifier
                .size(16.dp)
                .background(
                    color = if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828),
                    shape = if (isOnline) CircleShape else RoundedCornerShape(2.dp) // Разная форма
                )
        )
        Icon(
            imageVector = if (isOnline) Icons.Default.CheckCircle else Icons.Default.Cancel,
            contentDescription = null
        )
        Text(if (isOnline) "Online" else "Offline")
    }
}

@Test
fun testColorContrast() {
    val ratio = ContrastChecker.contrastRatio(Color(0xFF757575), Color.White)
    // Проверяем соответствие минимуму для обычного текста уровня AA (4.5:1)
    assertTrue("Контраст $ratio:1 < 4.5:1", ratio >= 4.5)
}
```

**Инструменты**: Accessibility Scanner (Android), Android Studio Color Picker (подсказки по контрасту), WebAIM Contrast Checker

**Best Practices**:
- используйте Material цветовые роли и Dynamic Color, но проверяйте кастомные палитры;
- не полагайтесь только на цвет для передачи состояния или ошибки;
- тестируйте светлую и тёмную темы (`@Preview(uiMode = UI_MODE_NIGHT_YES)`);
- автоматизируйте проверки контраста в CI.

---

## Answer (EN)

[[c-accessibility|Color contrast]] is the luminance ratio between text and background. WCAG recommends a minimum **4.5:1** for normal text (Level AA) and **7:1** for AAA. Large text has slightly relaxed requirements. Material Design’s color roles help you achieve sufficient contrast when used as intended (especially with official tools and Dynamic Color), but they do not guarantee contrast for arbitrary custom palettes.

### WCAG Requirements and Material Color Roles

**WCAG AA** (simplified for interview context):
- normal text — 4.5:1
- large text — 3:1 (WCAG: ≥ 18pt regular or ≥ 14pt bold; on screens this is roughly ≥ 24sp/18sp)

**WCAG AAA**:
- normal text — 7:1
- large text — 4.5:1

**Examples (illustrative):**
- black/white ≈ 21:1 ✅
- #757575/white ≈ 4.6:1 ✅ (meets AA for normal text)
- #959595/white ≈ 2.8:1 ❌ (fails AA for normal text)

```kotlin
@Composable
fun MaterialColorExample() {
    // ✅ When using recommended roles (Material 3 / Dynamic Color),
    // on* over * pairs are designed with WCAG AA in mind for typical text
    Surface(color = MaterialTheme.colorScheme.primary) {
        Text(text = "Button", color = MaterialTheme.colorScheme.onPrimary)
    }
}
// Key role pairs: primary/onPrimary, surface/onSurface, background/onBackground, etc.
// Actual contrast depends on the concrete palette — always validate custom colors.
```

### Common Violations

```kotlin
// ❌ 1. Potentially insufficient contrast on white background
// (gray chosen "by eye" without validating against WCAG)
Text(
    text = "Secondary",
    color = Color(0xFF959595),
    modifier = Modifier.background(Color.White)
)

// ❌ 2. Using color alone to convey meaning (inaccessible for users with color vision deficiency)
Row {
    Text("Success", color = Color.Green)
    Text("Error", color = Color.Red)
}

// ❌ 3. Ignoring dark theme: hardcoded dark text color
val textColor = Color(0xFF212121) // On dark theme backgrounds this may no longer meet contrast requirements

// ✅ Correct approach: roles + icons/text + theme-aware colors
Text(
    text = "Secondary",
    color = MaterialTheme.colorScheme.onSurfaceVariant,
    modifier = Modifier.background(MaterialTheme.colorScheme.surface)
)
Row {
    Icon(
        imageVector = Icons.Default.CheckCircle,
        contentDescription = null,
        tint = MaterialTheme.colorScheme.tertiary
    )
    Text("Success", color = MaterialTheme.colorScheme.tertiary)
}
```

### Color Blindness and Testing

About 8% of men and 0.5% of women have color vision deficiency — do not rely on color alone.

```kotlin
// ✅ Shape + icon + color for accessibility
@Composable
fun StatusIndicator(isOnline: Boolean) {
    Row {
        Box(
            Modifier
                .size(16.dp)
                .background(
                    color = if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828),
                    shape = if (isOnline) CircleShape else RoundedCornerShape(2.dp) // Different shapes
                )
        )
        Icon(
            imageVector = if (isOnline) Icons.Default.CheckCircle else Icons.Default.Cancel,
            contentDescription = null
        )
        Text(if (isOnline) "Online" else "Offline")
    }
}

@Test
fun testColorContrast() {
    val ratio = ContrastChecker.contrastRatio(Color(0xFF757575), Color.White)
    // Verify minimum AA requirement for normal text (4.5:1)
    assertTrue("Contrast $ratio:1 < 4.5:1", ratio >= 4.5)
}
```

**Tools**: Accessibility Scanner (Android), Android Studio Color Picker (contrast hints), WebAIM Contrast Checker

**Best Practices**:
- use Material color roles and Dynamic Color, but explicitly validate custom palettes;
- do not rely on color alone to represent state or errors;
- test both light and dark themes (`@Preview(uiMode = UI_MODE_NIGHT_YES)`);
- automate contrast checks in CI.

---

## Дополнительные Вопросы (RU)

- Как реализовать автоматизированную проверку контраста в CI/CD-конвейере?
- В чем компромиссы между соответствием WCAG AA (4.5:1) и AAA (7:1)?
- Как динамические цветовые схемы Material3 поддерживают гарантии контраста?
- Как обеспечивать контраст для настраиваемых брендовых цветов пользователя?
- Какие инструменты могут симулировать дальтонизм при разработке и тестировании?

## Follow-ups

- How to implement automated contrast validation in CI/CD pipelines?
- What are the trade-offs between WCAG AA (4.5:1) and AAA (7:1) compliance?
- How do Material3 dynamic color schemes maintain contrast guarantees?
- How to handle contrast for user-customizable brand colors?
- What tools can simulate color blindness during development and testing?

## Ссылки (RU)

- [[c-accessibility]] — Базовые концепции доступности
- WCAG Contrast Guidelines
- Material Design Color System
- Android Accessibility Guide

## References

- [[c-accessibility]] - Core accessibility concepts
- WCAG Contrast Guidelines
- Material Design Color System
- Android Accessibility Guide

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-accessibility-compose--android--medium]] - Основы доступности в Compose

### Связанные (средней сложности)
- [[q-accessibility-testing--android--medium]] - Тестирование возможностей доступности
- [[q-custom-view-accessibility--android--medium]] - Доступность для кастомных `View`

### Продвинутые (сложнее)
- Оптимизация для скринридеров и семантическая разметка
- Динамические системы тем с ограничениями доступности

## Related Questions

### Prerequisites (Easier)
- [[q-accessibility-compose--android--medium]] - Accessibility basics in Compose

### Related (Medium)
- [[q-accessibility-testing--android--medium]] - Testing accessibility features
- [[q-custom-view-accessibility--android--medium]] - Custom view accessibility

### Advanced (Harder)
- Screen reader optimization and semantic labeling
- Dynamic theme systems with accessibility constraints

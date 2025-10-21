---
id: 20251012-122755
title: Accessibility Text Scaling / Масштабирование текста для доступности
aliases: [Text Scaling Accessibility, Масштабирование текста]
topic: android
subtopics: [ui-accessibility, ui-theming]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
related:
  - q-accessibility-compose--accessibility--medium
  - q-accessibility-testing--accessibility--medium
created: 2025-10-11
updated: 2025-10-15
tags:
  - android/ui-accessibility
  - android/ui-theming
  - accessibility
  - text-scaling
  - font-size
  - dynamic-type
  - difficulty/medium
---
# Question (EN)
How do you support dynamic text sizing and display scaling for accessibility? What are sp units, text scaling factors, and how do you test your UI with different text sizes?

# Вопрос (RU)
Как поддерживать динамический размер текста и масштабирование дисплея для доступности? Что такое sp-единицы, коэффициенты масштабирования текста, и как тестировать UI с различными размерами текста?

---

## Answer (EN)

Text scaling allows users with visual impairments to increase text size for better readability. Android provides sp (scale-independent pixels) that scale with user's font size preference, text scaling factors from 0.85x to 2.0x, and display size that affects all UI elements.

#### SP vs DP Units

```kotlin
// GOOD - Text size in sp (scales with user preference)
Text(
    text = "Hello World",
    fontSize = 16.sp // Scales with accessibility settings
)

// BAD - Text size in dp (does NOT scale)
Text(
    text = "Hello World",
    fontSize = 16.dp // Fixed size, ignores user preferences
)

// GOOD - Non-text elements in dp
Box(
    modifier = Modifier.size(48.dp) // Touch target, doesn't scale
)

// BAD - Touch targets in sp
Box(
    modifier = Modifier.size(48.sp) // Will become huge at large text sizes
)
```

Rule of thumb: Text uses **sp**, layouts, icons, spacing use **dp**.

#### Text Scaling Levels

```
Scaling factors in Android:

Small:    0.85x  (85%)
Default:  1.00x  (100%)
Large:    1.15x  (115%)
Larger:   1.30x  (130%)
Largest:  1.50x  (150%)
Huge:     2.00x  (200%)  ← Target for testing
```

#### Adaptive Layouts for Text Scaling

**Problem: Text overflow at large sizes**:

```kotlin
// BAD - Fixed height truncates text
Row(modifier = Modifier.height(56.dp)) {
    Text("John Doe", fontSize = 16.sp, maxLines = 1)
}
```

**Solution: Remove fixed heights**:

```kotlin
// GOOD - Height adapts to content
Row(modifier = Modifier.padding(8.dp)) {
    Text("John Doe", fontSize = 16.sp) // No maxLines
}
```

**Solution: Use Column when needed**:

```kotlin
// GOOD - Switch to vertical layout at large scales
val fontScale = LocalDensity.current.fontScale
if (fontScale > 1.3f) {
    Column { Text("John Doe", fontSize = 16.sp) }
} else {
    Row { Text("John Doe", fontSize = 16.sp) }
}
```

#### Detecting Font Scale

```kotlin
@Composable
fun FontScaleAware() {
    val fontScale = LocalDensity.current.fontScale
    Text(text = when {
        fontScale >= 2.0f -> "Huge text (200%)"
        fontScale >= 1.5f -> "Largest text (150%)"
        else -> "Default text (100%)"
    })
}

// XML View
class MyView(context: Context) : View(context) {
    private val fontScale: Float
        get() = resources.configuration.fontScale
}
```

#### Material 3 Typography with Scaling

```kotlin
@Composable
fun MaterialTypographyExample() {
    Column {
        Text("Display Large", style = MaterialTheme.typography.displayLarge)
        Text("Headline Medium", style = MaterialTheme.typography.headlineMedium)
        Text("Body Large", style = MaterialTheme.typography.bodyLarge)
        Text("Body Small", style = MaterialTheme.typography.bodySmall)
    }
}
```

#### Testing with Different Text Sizes

**Manual testing**:

```
1. Settings → Display → Font size → Largest
2. Open app
3. Check: All text readable, no truncation, touch targets work
```

**Programmatic testing**:

```kotlin
@Test
fun testTextScaling() {
    composeTestRule.setContent {
        CompositionLocalProvider(
            LocalDensity provides Density(density = 1f, fontScale = 2.0f)
        ) {
            MyScreen()
        }
    }
    composeTestRule.onNodeWithText("Hello").assertIsDisplayed()
}
```

#### Common Text Scaling Issues

**1. Fixed heights cutting off text**:

```kotlin
// BAD
Card(modifier = Modifier.height(80.dp)) {
    Text("This text may get cut off")
}

// GOOD
Card(modifier = Modifier.wrapContentHeight()) {
    Text("This text will always be fully visible")
}
```

**2. maxLines causing truncation**:

```kotlin
// BAD - Text truncated at large sizes
Text("Important message", maxLines = 1, overflow = TextOverflow.Ellipsis)

// GOOD - Allow wrapping
Text("Important message") // No maxLines
```

**3. Icons not scaling with text**:

```kotlin
// BAD - Icon doesn't scale
Row {
    Icon(Icons.Default.Info, contentDescription = null, modifier = Modifier.size(24.dp))
    Text("Information", fontSize = 16.sp)
}

// GOOD - Icon scales with text
Row {
    Icon(Icons.Default.Info, contentDescription = null,
         modifier = Modifier.size(with(LocalDensity.current) { (16.sp * 1.5f).toDp() }))
    Text("Information", fontSize = 16.sp)
}
```

**4. Touch targets too close together**:

```kotlin
// BAD - Touch targets overlap at large text
Row {
    TextButton(onClick = {}) { Text("Cancel") }
    TextButton(onClick = {}) { Text("OK") }
}

// GOOD - Add spacing
Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
    TextButton(onClick = {}) { Text("Cancel") }
    TextButton(onClick = {}) { Text("OK") }
}
```

#### Display Size (Separate from Text Scaling)

Display size affects all UI elements:

```
Settings → Display → Display size

Small:     0.85x
Default:   1.00x
Large:     1.15x
Larger:    1.30x
Largest:   1.50x

Display size scales EVERYTHING:
- Layout sizes (dp values)
- Touch targets
- Images
- Padding
- Text (in addition to font scaling)
```

**Testing display size**:

```kotlin
@Test
fun testDisplaySize() {
    composeTestRule.setContent {
        CompositionLocalProvider(
            LocalDensity provides Density(density = 1.3f, fontScale = 1.0f)
        ) {
            MyScreen()
        }
    }
    composeTestRule.onNodeWithText("Submit").assertIsDisplayed()
}
```

#### Best Practices

1. Always use sp for text
2. Avoid fixed heights
3. Test at 200% scaling
4. Consider adaptive layouts
5. Use Material Typography

---

# Вопрос (RU)
Как поддерживать динамический размер текста и масштабирование дисплея для доступности? Что такое sp-единицы, коэффициенты масштабирования текста, и как тестировать UI с различными размерами текста?

## Ответ (RU)

Масштабирование текста позволяет пользователям с нарушениями зрения увеличивать размер текста для лучшей читаемости. Android предоставляет sp (scale-independent pixels), которые масштабируются с пользовательскими настройками размера шрифта, коэффициенты масштабирования текста от 0.85x до 2.0x, и размер дисплея, который влияет на все элементы UI.

#### SP vs DP единицы

```kotlin
// ХОРОШО - Размер текста в sp (масштабируется с пользовательскими настройками)
Text(
    text = "Привет мир",
    fontSize = 16.sp // Масштабируется с настройками доступности
)

// ПЛОХО - Размер текста в dp (НЕ масштабируется)
Text(
    text = "Привет мир",
    fontSize = 16.dp // Фиксированный размер, игнорирует пользовательские настройки
)

// ХОРОШО - Не-текстовые элементы в dp
Box(
    modifier = Modifier.size(48.dp) // Touch target, не масштабируется
)

// ПЛОХО - Touch targets в sp
Box(
    modifier = Modifier.size(48.sp) // Станет огромным при больших размерах текста
)
```

Правило: Текст использует **sp**, layouts, иконки, отступы используют **dp**.

#### Уровни масштабирования текста

```
Коэффициенты масштабирования в Android:

Маленький:    0.85x  (85%)
По умолчанию: 1.00x  (100%)
Большой:      1.15x  (115%)
Больше:       1.30x  (130%)
Самый большой: 1.50x  (150%)
Огромный:     2.00x  (200%)  ← Цель для тестирования
```

#### Адаптивные layouts для масштабирования текста

**Проблема: Переполнение текста при больших размерах**:

```kotlin
// ПЛОХО - Фиксированная высота обрезает текст
Row(modifier = Modifier.height(56.dp)) {
    Text("Иван Иванов", fontSize = 16.sp, maxLines = 1)
}
```

**Решение: Убрать фиксированные высоты**:

```kotlin
// ХОРОШО - Высота адаптируется к контенту
Row(modifier = Modifier.padding(8.dp)) {
    Text("Иван Иванов", fontSize = 16.sp) // Нет maxLines
}
```

**Решение: Использовать Column при необходимости**:

```kotlin
// ХОРОШО - Переключение на вертикальный layout при больших масштабах
val fontScale = LocalDensity.current.fontScale
if (fontScale > 1.3f) {
    Column { Text("Иван Иванов", fontSize = 16.sp) }
} else {
    Row { Text("Иван Иванов", fontSize = 16.sp) }
}
```

#### Определение масштаба шрифта

```kotlin
@Composable
fun FontScaleAware() {
    val fontScale = LocalDensity.current.fontScale
    Text(text = when {
        fontScale >= 2.0f -> "Огромный текст (200%)"
        fontScale >= 1.5f -> "Самый большой текст (150%)"
        else -> "Текст по умолчанию (100%)"
    })
}

// XML View
class MyView(context: Context) : View(context) {
    private val fontScale: Float
        get() = resources.configuration.fontScale
}
```

#### Material 3 Typography с масштабированием

```kotlin
@Composable
fun MaterialTypographyExample() {
    Column {
        Text("Display Large", style = MaterialTheme.typography.displayLarge)
        Text("Headline Medium", style = MaterialTheme.typography.headlineMedium)
        Text("Body Large", style = MaterialTheme.typography.bodyLarge)
        Text("Body Small", style = MaterialTheme.typography.bodySmall)
    }
}
```

#### Тестирование с разными размерами текста

**Ручное тестирование**:

```
1. Настройки → Дисплей → Размер шрифта → Самый большой
2. Открыть приложение
3. Проверить: Весь текст читаем, нет обрезания, touch targets работают
```

**Программное тестирование**:

```kotlin
@Test
fun testTextScaling() {
    composeTestRule.setContent {
        CompositionLocalProvider(
            LocalDensity provides Density(density = 1f, fontScale = 2.0f)
        ) {
            MyScreen()
        }
    }
    composeTestRule.onNodeWithText("Привет").assertIsDisplayed()
}
```

#### Распространённые проблемы масштабирования текста

**1. Фиксированные высоты обрезают текст**:

```kotlin
// ПЛОХО
Card(modifier = Modifier.height(80.dp)) {
    Text("Этот текст может обрезаться")
}

// ХОРОШО
Card(modifier = Modifier.wrapContentHeight()) {
    Text("Этот текст всегда будет полностью видим")
}
```

**2. maxLines вызывает усечение**:

```kotlin
// ПЛОХО - Текст усекается при больших размерах
Text("Важное сообщение", maxLines = 1, overflow = TextOverflow.Ellipsis)

// ХОРОШО - Позволить перенос
Text("Важное сообщение") // Нет maxLines
```

**3. Иконки не масштабируются с текстом**:

```kotlin
// ПЛОХО - Иконка не масштабируется
Row {
    Icon(Icons.Default.Info, contentDescription = null, modifier = Modifier.size(24.dp))
    Text("Информация", fontSize = 16.sp)
}

// ХОРОШО - Иконка масштабируется с текстом
Row {
    Icon(Icons.Default.Info, contentDescription = null,
         modifier = Modifier.size(with(LocalDensity.current) { (16.sp * 1.5f).toDp() }))
    Text("Информация", fontSize = 16.sp)
}
```

**4. Touch targets слишком близко друг к другу**:

```kotlin
// ПЛОХО - Touch targets перекрываются при большом тексте
Row {
    TextButton(onClick = {}) { Text("Отмена") }
    TextButton(onClick = {}) { Text("ОК") }
}

// ХОРОШО - Добавить отступы
Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
    TextButton(onClick = {}) { Text("Отмена") }
    TextButton(onClick = {}) { Text("ОК") }
}
```

#### Размер дисплея (отдельно от масштабирования текста)

Размер дисплея влияет на все элементы UI:

```
Настройки → Дисплей → Размер дисплея

Маленький:   0.85x
По умолчанию: 1.00x
Большой:     1.15x
Больше:      1.30x
Самый большой: 1.50x

Размер дисплея масштабирует ВСЁ:
- Размеры layout (dp значения)
- Touch targets
- Изображения
- Отступы
- Текст (в дополнение к font scaling)
```

**Тестирование размера дисплея**:

```kotlin
@Test
fun testDisplaySize() {
    composeTestRule.setContent {
        CompositionLocalProvider(
            LocalDensity provides Density(density = 1.3f, fontScale = 1.0f)
        ) {
            MyScreen()
        }
    }
    composeTestRule.onNodeWithText("Отправить").assertIsDisplayed()
}
```

#### Лучшие практики

1. Всегда использовать sp для текста
2. Избегать фиксированных высот
3. Тестировать на 200% масштабировании
4. Рассматривать адаптивные layouts
5. Использовать Material Typography

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
- [[q-accessibility-compose--accessibility--medium]] - Accessibility
- [[q-accessibility-testing--accessibility--medium]] - Accessibility
- [[q-custom-view-accessibility--custom-views--medium]] - Accessibility
- [[q-accessibility-color-contrast--accessibility--medium]] - Accessibility
- [[q-accessibility-talkback--accessibility--medium]] - Accessibility

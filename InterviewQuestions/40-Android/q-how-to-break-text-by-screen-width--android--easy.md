---
id: android-131
title: "How To Break Text By Screen Width / Как разбить текст по ширине экрана"
aliases: ["How To Break Text By Screen Width", "Как разбить текст по ширине экрана"]
topic: android
subtopics: [ui-graphics, ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/ui-graphics, android/ui-views, difficulty/easy]

---

# Вопрос (RU)

> Как разбить текст, зная ширину экрана (или контейнера) и параметры шрифта, а не фиксированное число символов?

# Question (EN)

> How to break text based on screen (or container) width and font parameters, rather than a fixed character count?

---

## Ответ (RU)

Используйте класс `Paint` и метод `breakText()` для определения количества символов, помещающихся в строку с учетом доступной ширины в пикселях и текущих настроек шрифта.

Важно понимать: разбиение происходит по измеренной ширине текста, а не по заранее заданному количеству символов. Разные символы имеют разную ширину.

### Основной Подход

```kotlin
val paint = Paint().apply { textSize = 48f }
val text = "Длинный текст для разбиения"
val maxWidth = 500f // ширина области рисования в пикселях

// ✅ breakText() возвращает количество символов, помещающихся в указанную ширину
val charsFit = paint.breakText(text, true, maxWidth, null)
val fittingText = text.substring(0, charsFit)
```

Этот пример разбивает строку на уровне символов и может обрезать слово посередине. Для пользовательского текста в реальном UI обычно дополнительно учитывают пробелы и перенос по словам.

### Разбиение На Несколько Строк

```kotlin
fun breakTextIntoLines(text: String, paint: Paint, maxWidth: Float): List<String> {
    val lines = mutableListOf<String>()
    var remaining = text

    while (remaining.isNotEmpty()) {
        val charsFit = paint.breakText(remaining, true, maxWidth, null)
        if (charsFit == 0) break // ❌ Ширина слишком мала для даже одного символа

        lines.add(remaining.substring(0, charsFit))
        remaining = remaining.substring(charsFit)
    }
    return lines
}
```

Этот упрощенный вариант также не учитывает перенос по словам. На собеседовании стоит упомянуть, что для продакшена нужно доработать алгоритм (поиск последних пробелов, обработка переносов строк, RTL и т.п.) или использовать готовые текстовые компоненты.

### В Кастомном `View`

```kotlin
class CustomTextView(context: Context, attrs: AttributeSet) : View(context, attrs) {
    private val paint = Paint().apply { textSize = 48f }
    private var text = ""
    private val lines = mutableListOf<String>()

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        lines.clear()
        var remaining = text

        // ✅ Пересчитываем разбиение при изменении размера
        while (remaining.isNotEmpty()) {
            val charsFit = paint.breakText(remaining, true, w.toFloat(), null)
            if (charsFit == 0) break
            lines.add(remaining.substring(0, charsFit))
            remaining = remaining.substring(charsFit)
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val fm = paint.fontMetrics
        val lineHeight = fm.bottom - fm.top
        var y = -fm.top // первая базовая линия

        lines.forEach { line ->
            canvas.drawText(line, 0f, y, paint)
            y += lineHeight + 8f
        }
    }
}
```

**Важно**:
- Метод `breakText()` учитывает настройки `Paint` (размер шрифта, `Typeface`, стиль), работая в пикселях.
- Косвенно это отражает плотность экрана через правильно заданный `textSize` (например, сконвертированный из `sp`), но сам метод не оперирует `dp/sp` напрямую.
- Показывайте в ответе понимание того, что разбиение должно быть основано на реальной ширине текста, а не просто на числе символов.
- Для сложного форматирования, переносов по словам, RTL и спанов чаще используют `StaticLayout`/`StaticLayout.Builder` и `TextPaint`.

---

## Answer (EN)

Use the `Paint` class and its `breakText()` method to determine how many characters fit into a line for a given width in pixels and the current font configuration.

Key idea: wrapping is based on measured text width, not on a fixed character count. Different characters have different widths.

### Basic Approach

```kotlin
val paint = Paint().apply { textSize = 48f }
val text = "Long text that needs to be broken"
val maxWidth = 500f // drawing area width in pixels

// ✅ breakText() returns the number of characters that fit within the given width
val charsFit = paint.breakText(text, true, maxWidth, null)
val fittingText = text.substring(0, charsFit)
```

This example breaks at the character level and may cut words in half. For real UI text you usually also respect word boundaries.

### Breaking into Multiple Lines

```kotlin
fun breakTextIntoLines(text: String, paint: Paint, maxWidth: Float): List<String> {
    val lines = mutableListOf<String>()
    var remaining = text

    while (remaining.isNotEmpty()) {
        val charsFit = paint.breakText(remaining, true, maxWidth, null)
        if (charsFit == 0) break // ❌ Width too small for even a single character

        lines.add(remaining.substring(0, charsFit))
        remaining = remaining.substring(charsFit)
    }
    return lines
}
```

This simplified version also ignores word boundaries. In an interview, mention that a production-ready solution should refine this (respect spaces, existing line breaks, RTL, etc.) or use higher-level text layout APIs.

### In Custom `View`

```kotlin
class CustomTextView(context: Context, attrs: AttributeSet) : View(context, attrs) {
    private val paint = Paint().apply { textSize = 48f }
    private var text = ""
    private val lines = mutableListOf<String>()

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        lines.clear()
        var remaining = text

        // ✅ Recalculate breaking on size change
        while (remaining.isNotEmpty()) {
            val charsFit = paint.breakText(remaining, true, w.toFloat(), null)
            if (charsFit == 0) break
            lines.add(remaining.substring(0, charsFit))
            remaining = remaining.substring(charsFit)
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val fm = paint.fontMetrics
        val lineHeight = fm.bottom - fm.top
        var y = -fm.top // first baseline

        lines.forEach { line ->
            canvas.drawText(line, 0f, y, paint)
            y += lineHeight + 8f
        }
    }
}
```

**Important**:
- `breakText()` respects the `Paint` configuration (textSize, typeface, style) and works in pixel units.
- Screen density is taken into account indirectly through how you configure `textSize` (e.g., converting from `sp`), not directly inside `breakText()`.
- Emphasize that line breaking should be based on actual measured width, not a naive "N characters per line".
- For complex layouts, word wrapping, spans, and bidirectional text, prefer `StaticLayout`/`StaticLayout.Builder` with `TextPaint`.

---

## Follow-ups

- What's the difference between `breakText()` and `measureText()` in `Paint`?
- How does `breakText()` handle RTL text and bidirectional scripts?
- When would you use `StaticLayout` instead of manual `breakText()` loops?

## References

- [[c-custom-views]] - Custom view implementation patterns
- https://developer.android.com/reference/android/graphics/Paint#breakText

## Related Questions

### Prerequisites
- Basic `Paint` and `Canvas` usage
- Custom view lifecycle

### Related
- Text measurement techniques
- Custom text rendering

### Advanced
- `StaticLayout` for complex text
- `TextPaint` and span handling

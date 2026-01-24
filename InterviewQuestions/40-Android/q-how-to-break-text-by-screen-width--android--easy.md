---
id: android-131
title: How To Break Text By Screen Width / Как разбить текст по ширине экрана
aliases:
- How To Break Text By Screen Width
- Как разбить текст по ширине экрана
topic: android
subtopics:
- ui-graphics
- ui-views
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-custom-views
- c-android-graphics
- c-canvas-drawing
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android
- android/ui-graphics
- android/ui-views
- difficulty/easy
anki_cards:
- slug: android-131-0-en
  language: en
  anki_id: 1768378630516
  synced_at: '2026-01-23T16:45:05.323956'
- slug: android-131-0-ru
  language: ru
  anki_id: 1768378630541
  synced_at: '2026-01-23T16:45:05.326112'
---
# Вопрос (RU)

> Как разбить текст, зная ширину экрана (или контейнера) и параметры шрифта, а не фиксированное число символов?

# Question (EN)

> How to break text based on screen (or container) width and font parameters, rather than a fixed character count?

---

## Ответ (RU)

Используйте класс `Paint` и метод `breakText()` для определения количества символов, помещающихся в строку с учетом доступной ширины в пикселях и текущих настроек шрифта.

Важно понимать: разбиение происходит по измеренной ширине текста, а не по заранее заданному количеству символов. Разные символы имеют разную ширину.

Также важно: `breakText()`/ручное разбиение — это низкоуровневый инструмент для кастомного рисования текста на `Canvas`. Для обычного UI (TextView/Compose) предпочтительно полагаться на встроенные механизмы переноса строк.

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
        if (charsFit == 0) break // ожидаемое поведение: ширина слишком мала даже для одного символа

        lines.add(remaining.substring(0, charsFit))
        remaining = remaining.substring(charsFit)
    }
    return lines
}
```

Этот упрощенный вариант:
- не учитывает перенос по словам;
- не учитывает уже существующие символы перевода строки;
- не поддерживает сложные сценарии (RTL, bidirectional, спаны, fallback-шрифты и т.п.).

На собеседовании стоит явно сказать, что это демонстрация принципа измерения ширины, а для продакшена алгоритм нужно доработать или использовать готовые текстовые компоненты / `StaticLayout`.

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
            if (charsFit == 0) break // ожидаемое поведение при слишком маленькой ширине
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
- Для сложного форматирования, переносов по словам, RTL и спанов используют `StaticLayout`/`StaticLayout.Builder` c `TextPaint` или более высокоуровневые компоненты.

---

## Answer (EN)

Use the `Paint` class and its `breakText()` method to determine how many characters fit into a line for a given width in pixels and the current font configuration.

Key idea: wrapping is based on measured text width, not on a fixed character count. Different characters have different widths.

Also important: `breakText()`/manual splitting is a low-level tool for custom text rendering on a `Canvas`. For regular app UI (`TextView`, Compose text), you usually rely on built-in line breaking instead of reimplementing it.

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
        if (charsFit == 0) break // expected behavior: width too small for even a single character

        lines.add(remaining.substring(0, charsFit))
        remaining = remaining.substring(charsFit)
    }
    return lines
}
```

This simplified version:
- does not respect word boundaries;
- ignores existing newline characters in the input;
- does not cover complex cases (RTL, bidirectional text, spans, fallback fonts, etc.).

In an interview, explicitly state this is a demonstration of width-based splitting; a production-ready solution should refine the algorithm or use higher-level text layout APIs / `StaticLayout`.

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
            if (charsFit == 0) break // expected behavior for an extremely narrow width
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
- `breakText()` respects the `Paint` configuration (textSize, typeface, style) and operates in pixels.
- Screen density is accounted for indirectly via how you set `textSize` (e.g., converting from `sp`); `breakText()` itself does not work in `dp/sp`.
- Emphasize that line breaking should be based on actual measured width, not a naive "N characters per line" approach.
- For complex layouts, word wrapping, spans, and bidirectional text, use `StaticLayout`/`StaticLayout.Builder` with `TextPaint` or higher-level components.

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

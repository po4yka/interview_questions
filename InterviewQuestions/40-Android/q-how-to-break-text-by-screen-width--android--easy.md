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
related: [c-custom-views, c-views]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, android/ui-graphics, android/ui-views, difficulty/easy]
---

# Вопрос (RU)

> Как разбить текст, зная, сколько символов помещается на экране?

# Question (EN)

> How to break text knowing how many characters fit on screen?

---

## Ответ (RU)

Используйте класс **`Paint`** и метод **breakText()** для определения количества символов, помещающихся в строку с учетом доступной ширины.

### Основной Подход

```kotlin
val paint = Paint().apply { textSize = 48f }
val text = "Длинный текст для разбиения"
val maxWidth = 500f

// ✅ breakText() возвращает количество символов, помещающихся в ширину
val charsFit = paint.breakText(text, true, maxWidth, null)
val fittingText = text.substring(0, charsFit)
```

### Разбиение На Несколько Строк

```kotlin
fun breakTextIntoLines(text: String, paint: Paint, maxWidth: Float): List<String> {
    val lines = mutableListOf<String>()
    var remaining = text

    while (remaining.isNotEmpty()) {
        val charsFit = paint.breakText(remaining, true, maxWidth, null)
        if (charsFit == 0) break // ❌ Ширина слишком мала

        lines.add(remaining.substring(0, charsFit))
        remaining = remaining.substring(charsFit)
    }
    return lines
}
```

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
        var y = paint.textSize
        lines.forEach { line ->
            canvas.drawText(line, 0f, y, paint)
            y += paint.textSize + 8
        }
    }
}
```

**Важно**: Метод breakText() учитывает размер шрифта, typeface и плотность экрана. Для корректной работы всегда используйте тот же объект `Paint`, который будет применяться для отрисовки. См. [[c-custom-views]] для деталей реализации.

---

## Answer (EN)

Use the **`Paint`** class and **breakText()** method to determine how many characters fit in a line based on available width.

### Basic Approach

```kotlin
val paint = Paint().apply { textSize = 48f }
val text = "Long text that needs to be broken"
val maxWidth = 500f

// ✅ breakText() returns the number of characters that fit
val charsFit = paint.breakText(text, true, maxWidth, null)
val fittingText = text.substring(0, charsFit)
```

### Breaking into Multiple Lines

```kotlin
fun breakTextIntoLines(text: String, paint: Paint, maxWidth: Float): List<String> {
    val lines = mutableListOf<String>()
    var remaining = text

    while (remaining.isNotEmpty()) {
        val charsFit = paint.breakText(remaining, true, maxWidth, null)
        if (charsFit == 0) break // ❌ Width too small

        lines.add(remaining.substring(0, charsFit))
        remaining = remaining.substring(charsFit)
    }
    return lines
}
```

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
        var y = paint.textSize
        lines.forEach { line ->
            canvas.drawText(line, 0f, y, paint)
            y += paint.textSize + 8
        }
    }
}
```

**Important**: The breakText() method accounts for font size, typeface, and screen density. Always use the same `Paint` object that will be used for drawing. See [[c-custom-views]] for implementation details.

---

## Follow-ups

- What's the difference between breakText() and measureText() in `Paint`?
- How does breakText() handle RTL text and bidirectional scripts?
- When would you use StaticLayout instead of manual breakText() loops?

## References

- [[c-custom-views]] - Custom view implementation patterns
- [[c-views]] - Android view system fundamentals
- https://developer.android.com/reference/android/graphics/`Paint`#breakText

## Related Questions

### Prerequisites
- Basic `Paint` and `Canvas` usage
- Custom view lifecycle

### Related
- Text measurement techniques
- Custom text rendering

### Advanced
- StaticLayout for complex text
- TextPaint and span handling

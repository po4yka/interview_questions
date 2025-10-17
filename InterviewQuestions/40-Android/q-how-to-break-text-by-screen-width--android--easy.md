---
id: "20251015082237262"
title: "How To Break Text By Screen Width / Как разбить текст по ширине экрана"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [android, android/text-rendering, android/ui, breakText, text-rendering, ui, difficulty/easy]
---

# Question (EN)

> How to break text knowing how many characters fit on screen?

# Вопрос (RU)

> Как разбить текст, зная, сколько символов помещается на экране?

---

## Answer (EN)

Use the **Paint** class and **breakText()** method to determine how many characters fit in a line based on available width.

### Using breakText()

```kotlin
val paint = Paint().apply {
    textSize = 48f
    typeface = Typeface.DEFAULT
}

val text = "This is a long text that needs to be broken"
val maxWidth = 500f // Available width

val measuredChars = paint.breakText(
    text,
    true,  // measureForwards
    maxWidth,
    null   // measuredWidth (optional)
)

val fittingText = text.substring(0, measuredChars)
```

### Breaking Text into Multiple Lines

```kotlin
fun breakTextIntoLines(text: String, paint: Paint, maxWidth: Float): List<String> {
    val lines = mutableListOf<String>()
    var remainingText = text

    while (remainingText.isNotEmpty()) {
        val charsFit = paint.breakText(
            remainingText,
            true,
            maxWidth,
            null
        )

        if (charsFit == 0) break

        val line = remainingText.substring(0, charsFit)
        lines.add(line)
        remainingText = remainingText.substring(charsFit)
    }

    return lines
}

// Usage
val paint = Paint().apply { textSize = 40f }
val lines = breakTextIntoLines("Long text here...", paint, 400f)
```

### In Custom View

```kotlin
class CustomTextView(context: Context, attrs: AttributeSet) : View(context, attrs) {
    private val paint = Paint().apply {
        textSize = 48f
        color = Color.BLACK
    }

    private var text = "This is a long text to be broken"
    private val lines = mutableListOf<String>()

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        lines.clear()

        var remaining = text
        while (remaining.isNotEmpty()) {
            val charsFit = paint.breakText(remaining, true, w.toFloat(), null)
            if (charsFit == 0) break

            lines.add(remaining.substring(0, charsFit))
            remaining = remaining.substring(charsFit)
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        var y = paint.textSize
        for (line in lines) {
            canvas.drawText(line, 0f, y, paint)
            y += paint.textSize + 8
        }
    }
}
```

---

## Ответ (RU)

Используйте класс Paint и метод breakText, чтобы определить, сколько символов помещается в строку. Это позволит разбивать текст в зависимости от ширины экрана и используемого шрифта.

---

## Follow-ups

-   How do you handle text breaking for different screen densities and font sizes?
-   What's the difference between breakText() and measureText() for text layout?
-   How can you implement custom text wrapping with hyphenation?

## References

-   `https://developer.android.com/reference/android/graphics/Paint` — Paint class documentation
-   `https://developer.android.com/guide/topics/ui/look-and-feel/themes` — Android themes and text
-   `https://developer.android.com/training/custom-views` — Custom views guide

## Related Questions

### Related (Easy)

-   [[q-text-measurement-android--android--easy]] - Text measurement
-   [[q-custom-view-text-rendering--android--easy]] - Custom text rendering

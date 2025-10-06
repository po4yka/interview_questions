---
topic: android
tags:
  - android
  - spannable
  - text-styling
  - ui
  - textview
  - difficulty/medium
difficulty: medium
---

# Spannable Text in Android / Spannable текст в Android

**English**: What is Spannable?

## Answer

**Spannable** is an interface for text to which **markup objects can be attached and detached**. It's used for **styling text** at runtime, allowing you to apply formatting to whole paragraphs or specific parts of text.

Spannable enables you to:
- 🎨 Change text color
- 👆 Make text clickable
- 📏 Scale text size
- 🎯 Draw custom bullet points
- 📐 Change line height
- **Bold, italic, underline** formatting
- Background colors
- Custom fonts and typefaces

**Applying Spans:**

When using spans, you will work with one of the following classes:

| Class | Text Mutable | Markup Mutable | Internal Structure | Use Case |
|-------|--------------|----------------|-------------------|----------|
| **SpannedString** | ❌ No | ❌ No | Linear array | Just reading, not setting |
| **SpannableString** | ❌ No | ✅ Yes | Linear array | Setting small number of spans (<~10) |
| **SpannableStringBuilder** | ✅ Yes | ✅ Yes | Interval tree | Setting text and spans, or many spans (>~10) |

**Which one to use?**
- Just reading (not setting text or spans)? → **SpannedString**
- Setting text and spans? → **SpannableStringBuilder**
- Setting a small number of spans (<~10)? → **SpannableString**
- Setting a larger number of spans (>~10)? → **SpannableStringBuilder**

**Basic Example:**

```kotlin
// Simple color span
val text = "Hello World"
val spannable = SpannableString(text)

// Make "World" red
val redColor = ForegroundColorSpan(Color.RED)
spannable.setSpan(
    redColor,
    6,  // start index
    11, // end index
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

textView.text = spannable
```

**Span Flags:**

| Flag | Description |
|------|-------------|
| `SPAN_EXCLUSIVE_EXCLUSIVE` | Don't include inserted text at start/end |
| `SPAN_INCLUSIVE_EXCLUSIVE` | Include text inserted at start |
| `SPAN_EXCLUSIVE_INCLUSIVE` | Include text inserted at end |
| `SPAN_INCLUSIVE_INCLUSIVE` | Include text inserted at both start and end |

**Framework Spans:**

The Android framework provides 20+ built-in spans in the `android.text.style` package.

**Appearance-Affecting Spans (Character Level):**

These spans change appearance without affecting layout:

```kotlin
val spannable = SpannableStringBuilder("This is a text with multiple styles")

// Foreground color (text color)
spannable.setSpan(
    ForegroundColorSpan(Color.RED),
    0, 4,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

// Background color
spannable.setSpan(
    BackgroundColorSpan(Color.YELLOW),
    10, 14,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

// Bold
spannable.setSpan(
    StyleSpan(Typeface.BOLD),
    20, 28,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

// Underline
spannable.setSpan(
    UnderlineSpan(),
    29, 35,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

textView.text = spannable
```

**Common Appearance Spans:**

```kotlin
// Strikethrough
StrikethroughSpan()

// Italic
StyleSpan(Typeface.ITALIC)

// Bold Italic
StyleSpan(Typeface.BOLD_ITALIC)

// Subscript (H₂O)
SubscriptSpan()

// Superscript (E=mc²)
SuperscriptSpan()

// Text color
ForegroundColorSpan(Color.BLUE)

// Background color
BackgroundColorSpan(Color.CYAN)

// Underline
UnderlineSpan()
```

**Metric-Affecting Spans (Layout Changes):**

These spans modify text metrics and require re-layout:

```kotlin
// Relative size (1.5x normal size)
spannable.setSpan(
    RelativeSizeSpan(1.5f),
    0, 5,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

// Absolute size (24sp)
spannable.setSpan(
    AbsoluteSizeSpan(24, true), // true = use sp
    10, 15,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

// Scale X (horizontal scaling)
spannable.setSpan(
    ScaleXSpan(2.0f),
    20, 25,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

// Custom typeface
spannable.setSpan(
    TypefaceSpan("monospace"),
    30, 40,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)
```

**Paragraph-Affecting Spans:**

These spans affect entire paragraphs and must be attached from the first character to the last character of a paragraph. On Android, paragraphs are defined by newline (`\n`) characters.

```kotlin
val text = "First line\nSecond line with quote\nThird line"
val spannable = SpannableString(text)

// Quote span (vertical line at start)
spannable.setSpan(
    QuoteSpan(Color.BLUE),
    11, 34, // Must span entire paragraph
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

// Bullet span
spannable.setSpan(
    BulletSpan(20, Color.RED),
    0, 10,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

// Alignment
spannable.setSpan(
    AlignmentSpan.Standard(Layout.Alignment.ALIGN_CENTER),
    11, 34,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)
```

**Clickable Spans:**

```kotlin
val spannable = SpannableStringBuilder("Click here to open website")

val clickableSpan = object : ClickableSpan() {
    override fun onClick(widget: View) {
        // Handle click
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://example.com"))
        widget.context.startActivity(intent)
    }

    override fun updateDrawState(ds: TextPaint) {
        super.updateDrawState(ds)
        ds.isUnderlineText = false // Remove underline
        ds.color = Color.BLUE
    }
}

spannable.setSpan(
    clickableSpan,
    6, 10, // "here"
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

textView.text = spannable
textView.movementMethod = LinkMovementMethod.getInstance()
```

**Image Spans:**

```kotlin
// Add an image inline with text
val spannable = SpannableStringBuilder("This is an icon  placeholder")

val drawable = ContextCompat.getDrawable(context, R.drawable.ic_star)
drawable?.setBounds(0, 0, drawable.intrinsicWidth, drawable.intrinsicHeight)

spannable.setSpan(
    ImageSpan(drawable, ImageSpan.ALIGN_BASELINE),
    15, 16, // Replace space with image
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

textView.text = spannable
```

**Custom Spans:**

Create your own custom spans:

```kotlin
// Custom span that draws a border around text
class BorderSpan(
    private val borderColor: Int,
    private val borderWidth: Float
) : ReplacementSpan() {

    override fun getSize(
        paint: Paint,
        text: CharSequence,
        start: Int,
        end: Int,
        fm: Paint.FontMetricsInt?
    ): Int {
        return paint.measureText(text, start, end).toInt() + borderWidth.toInt() * 2
    }

    override fun draw(
        canvas: Canvas,
        text: CharSequence,
        start: Int,
        end: Int,
        x: Float,
        top: Int,
        y: Int,
        bottom: Int,
        paint: Paint
    ) {
        val width = paint.measureText(text, start, end)

        // Draw border
        val borderPaint = Paint().apply {
            color = borderColor
            strokeWidth = borderWidth
            style = Paint.Style.STROKE
        }
        canvas.drawRect(
            x, top.toFloat(),
            x + width + borderWidth * 2, bottom.toFloat(),
            borderPaint
        )

        // Draw text
        canvas.drawText(text, start, end, x + borderWidth, y.toFloat(), paint)
    }
}

// Usage
spannable.setSpan(
    BorderSpan(Color.RED, 2f),
    0, 5,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)
```

**Building Complex Styled Text:**

```kotlin
fun buildStyledText(): SpannableStringBuilder {
    return SpannableStringBuilder().apply {
        // Title
        append("Title\n", StyleSpan(Typeface.BOLD), Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
        append("", RelativeSizeSpan(1.5f), Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)

        // Body
        append("This is ")

        // Bold word
        val start = length
        append("important")
        setSpan(StyleSpan(Typeface.BOLD), start, length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)

        append(" text with a ")

        // Link
        val linkStart = length
        append("clickable link")
        setSpan(
            object : ClickableSpan() {
                override fun onClick(widget: View) {
                    Toast.makeText(widget.context, "Link clicked!", Toast.LENGTH_SHORT).show()
                }
            },
            linkStart, length,
            Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
        )
    }
}

// Usage
textView.text = buildStyledText()
textView.movementMethod = LinkMovementMethod.getInstance()
```

**Extension Functions for Easier Usage:**

```kotlin
// Kotlin extension for easier span application
inline fun SpannableStringBuilder.span(
    what: Any,
    start: Int,
    end: Int,
    flags: Int = Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
) = apply {
    setSpan(what, start, end, flags)
}

inline fun SpannableStringBuilder.appendSpan(
    text: CharSequence,
    what: Any,
    flags: Int = Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
) = apply {
    val start = length
    append(text)
    setSpan(what, start, length, flags)
}

// Usage
val text = SpannableStringBuilder()
    .appendSpan("Bold ", StyleSpan(Typeface.BOLD))
    .appendSpan("Red ", ForegroundColorSpan(Color.RED))
    .appendSpan("Large", RelativeSizeSpan(1.5f))
```

**Real-World Example - Formatted Message:**

```kotlin
fun formatMessage(username: String, message: String, timestamp: Long): SpannableStringBuilder {
    return SpannableStringBuilder().apply {
        // Username in bold and blue
        appendSpan(username, ForegroundColorSpan(Color.BLUE))
        appendSpan(username, StyleSpan(Typeface.BOLD))

        append(" ")

        // Message in regular text
        append(message)

        append(" ")

        // Timestamp in small grey text
        val timeStart = length
        append(formatTime(timestamp))
        setSpan(RelativeSizeSpan(0.8f), timeStart, length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
        setSpan(ForegroundColorSpan(Color.GRAY), timeStart, length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
    }
}
```

**Performance Considerations:**

1. **Use SpannableString for static text** — faster than SpannableStringBuilder
2. **Avoid excessive spans** — each span adds overhead
3. **Reuse spans when possible** — don't create new instances unnecessarily
4. **Use SpannableStringBuilder for dynamic text** — efficient for multiple modifications
5. **Cache styled text** — don't recreate on every scroll in RecyclerView

**Summary:**

- **Spannable**: Interface for attaching markup to text
- **Classes**: SpannedString (immutable), SpannableString (spans mutable), SpannableStringBuilder (both mutable)
- **Appearance spans**: Change color, style without layout changes
- **Metric spans**: Change size, require re-layout
- **Paragraph spans**: Affect entire paragraphs (quotes, bullets, alignment)
- **Custom spans**: Create your own by extending base span classes
- **Use cases**: Formatted text, clickable links, inline images, syntax highlighting

**Sources:**
- [Android Spannable documentation](https://developer.android.com/reference/android/text/Spannable)
- [Spantastic text styling with Spans](https://medium.com/androiddevelopers/spantastic-text-styling-with-spans-17b0c16b4568)

## Ответ

**Spannable** — это интерфейс для текста, к которому можно **прикреплять и открепять объекты разметки**. Он используется для **стилизации текста** во время выполнения, позволяя применять форматирование к целым абзацам или конкретным частям текста.

Spannable позволяет:
- Изменять цвет текста
- Делать текст кликабельным
- Масштабировать размер текста
- Рисовать пользовательские маркеры
- Изменять высоту строки
- Форматирование жирным, курсивом, подчёркиванием
- Цвета фона
- Пользовательские шрифты

**Применение Spans:**

При использовании spans вы будете работать с одним из следующих классов:

| Класс | Текст изменяемый | Разметка изменяемая | Использование |
|-------|------------------|---------------------|---------------|
| **SpannedString** | ❌ Нет | ❌ Нет | Только чтение |
| **SpannableString** | ❌ Нет | ✅ Да | Небольшое количество spans (<~10) |
| **SpannableStringBuilder** | ✅ Да | ✅ Да | Установка текста и spans, или много spans (>~10) |

**Базовый пример:**

```kotlin
val text = "Hello World"
val spannable = SpannableString(text)

// Сделать "World" красным
spannable.setSpan(
    ForegroundColorSpan(Color.RED),
    6,  // начальный индекс
    11, // конечный индекс
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)

textView.text = spannable
```

**Флаги Span:**

- `SPAN_EXCLUSIVE_EXCLUSIVE` — не включать вставленный текст в начале/конце
- `SPAN_INCLUSIVE_EXCLUSIVE` — включать текст, вставленный в начале
- `SPAN_EXCLUSIVE_INCLUSIVE` — включать текст, вставленный в конце
- `SPAN_INCLUSIVE_INCLUSIVE` — включать текст, вставленный в начале и конце

**Категории Spans:**

**1. Appearance-affecting spans (влияющие на внешний вид):**

Изменяют внешний вид без влияния на layout:

```kotlin
// Цвет текста
ForegroundColorSpan(Color.RED)

// Цвет фона
BackgroundColorSpan(Color.YELLOW)

// Жирный
StyleSpan(Typeface.BOLD)

// Подчёркивание
UnderlineSpan()

// Зачёркивание
StrikethroughSpan()
```

**2. Metric-affecting spans (влияющие на метрики):**

Изменяют метрики текста и требуют пересчёта layout:

```kotlin
// Относительный размер (1.5x обычного)
RelativeSizeSpan(1.5f)

// Абсолютный размер (24sp)
AbsoluteSizeSpan(24, true)

// Масштабирование по горизонтали
ScaleXSpan(2.0f)

// Пользовательский шрифт
TypefaceSpan("monospace")
```

**3. Paragraph-affecting spans (влияющие на абзацы):**

Влияют на целые абзацы, должны применяться от первого до последнего символа абзаца:

```kotlin
// Цитата (вертикальная линия)
QuoteSpan(Color.BLUE)

// Маркер списка
BulletSpan(20, Color.RED)

// Выравнивание
AlignmentSpan.Standard(Layout.Alignment.ALIGN_CENTER)
```

**Кликабельные Spans:**

```kotlin
val clickableSpan = object : ClickableSpan() {
    override fun onClick(widget: View) {
        // Обработка клика
        Toast.makeText(widget.context, "Clicked!", Toast.LENGTH_SHORT).show()
    }

    override fun updateDrawState(ds: TextPaint) {
        super.updateDrawState(ds)
        ds.isUnderlineText = false
        ds.color = Color.BLUE
    }
}

spannable.setSpan(clickableSpan, 6, 10, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
textView.movementMethod = LinkMovementMethod.getInstance()
```

**Image Spans (встроенные изображения):**

```kotlin
val drawable = ContextCompat.getDrawable(context, R.drawable.ic_star)
drawable?.setBounds(0, 0, drawable.intrinsicWidth, drawable.intrinsicHeight)

spannable.setSpan(
    ImageSpan(drawable, ImageSpan.ALIGN_BASELINE),
    15, 16,
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)
```

**Вспомогательные функции-расширения:**

```kotlin
inline fun SpannableStringBuilder.appendSpan(
    text: CharSequence,
    what: Any,
    flags: Int = Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
) = apply {
    val start = length
    append(text)
    setSpan(what, start, length, flags)
}

// Использование
val text = SpannableStringBuilder()
    .appendSpan("Bold ", StyleSpan(Typeface.BOLD))
    .appendSpan("Red ", ForegroundColorSpan(Color.RED))
    .appendSpan("Large", RelativeSizeSpan(1.5f))
```

**Рекомендации по производительности:**

1. Используйте SpannableString для статического текста
2. Избегайте избыточных spans
3. Переиспользуйте spans когда возможно
4. Используйте SpannableStringBuilder для динамического текста
5. Кэшируйте стилизованный текст

**Резюме:**

Spannable — это интерфейс для прикрепления разметки к тексту. Существует три основных класса: SpannedString (неизменяемый), SpannableString (spans изменяемые), SpannableStringBuilder (оба изменяемые). Spans делятся на три категории: влияющие на внешний вид, метрики и абзацы. Используется для форматированного текста, кликабельных ссылок, встроенных изображений и подсветки синтаксиса.

---
id: android-109
title: Spannable Text Styling / Стилизация текста Spannable
aliases:
- Spannable Text Styling
- Стилизация текста Spannable
topic: android
subtopics:
- ui-views
- ui-widgets
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
created: 2025-10-13
updated: 2025-10-28
sources: []
tags:
- android/ui-views
- android/ui-widgets
- difficulty/medium
- spannable
- text-styling
moc: moc-android
related:
- c-android-components
- q-accessibility-text-scaling--android--medium
- q-custom-view-attributes--android--medium
- q-how-to-break-text-by-screen-width--android--easy
---

# Вопрос (RU)

Что такое Spannable и как его использовать для стилизации текста?

# Question (EN)

What is Spannable and how do you use it for text styling?

## Ответ (RU)

**Spannable** — интерфейс для текста, к которому можно прикреплять объекты разметки во время выполнения. Используется для динамической стилизации части текста или целых абзацев.

### Основные Классы

| Класс | Текст | Разметка | Использование |
|-------|-------|----------|---------------|
| **SpannedString** | Неизменяемый | Неизменяемая | Чтение |
| **SpannableString** | Неизменяемый | Изменяемая | <10 spans |
| **SpannableStringBuilder** | Изменяемый | Изменяемая | >10 spans |

### Базовый Пример

```kotlin
val text = SpannableString("Hello World")
text.setSpan(
    ForegroundColorSpan(Color.RED),
    6, 11,  // ✅ Индексы "World"
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)
textView.text = text
```

### Флаги Span

- `SPAN_EXCLUSIVE_EXCLUSIVE` — не включать вставленный текст
- `SPAN_INCLUSIVE_EXCLUSIVE` — включать текст в начале
- `SPAN_EXCLUSIVE_INCLUSIVE` — включать текст в конце
- `SPAN_INCLUSIVE_INCLUSIVE` — включать текст с обеих сторон

### Категории Spans

**1. Appearance spans** (изменяют внешний вид без перерасчёта layout):

```kotlin
ForegroundColorSpan(Color.RED)        // Цвет текста
BackgroundColorSpan(Color.YELLOW)     // Цвет фона
StyleSpan(Typeface.BOLD)              // Жирный
UnderlineSpan()                       // Подчёркивание
StrikethroughSpan()                   // Зачёркивание
```

**2. Metric spans** (требуют перерасчёта layout):

```kotlin
RelativeSizeSpan(1.5f)                // Относительный размер
AbsoluteSizeSpan(24, true)            // ✅ true = sp
ScaleXSpan(2.0f)                      // Масштабирование по X
TypefaceSpan("monospace")             // Моноширинный шрифт
```

**3. Paragraph spans** (применяются к целым абзацам):

```kotlin
QuoteSpan(Color.BLUE)                 // Вертикальная линия цитаты
BulletSpan(20, Color.RED)             // Маркер списка
AlignmentSpan.Standard(ALIGN_CENTER)  // Выравнивание
```

### Кликабельные Spans

```kotlin
val clickable = object : ClickableSpan() {
    override fun onClick(view: View) {
        Toast.makeText(view.context, "Clicked", LENGTH_SHORT).show()
    }

    override fun updateDrawState(ds: TextPaint) {
        super.updateDrawState(ds)
        ds.isUnderlineText = false  // ✅ Убрать подчёркивание
        ds.color = Color.BLUE
    }
}

spannable.setSpan(clickable, 0, 5, SPAN_EXCLUSIVE_EXCLUSIVE)
textView.movementMethod = LinkMovementMethod.getInstance()  // ✅ Обязательно
```

### Extension-функции

```kotlin
inline fun SpannableStringBuilder.appendSpan(
    text: CharSequence,
    what: Any,
    flags: Int = SPAN_EXCLUSIVE_EXCLUSIVE
) = apply {
    val start = length
    append(text)
    setSpan(what, start, length, flags)
}

// ✅ Использование
val styled = SpannableStringBuilder()
    .appendSpan("Bold ", StyleSpan(Typeface.BOLD))
    .appendSpan("Red ", ForegroundColorSpan(Color.RED))
    .appendSpan("Large", RelativeSizeSpan(1.5f))
```

### Производительность

1. **SpannableString** для статического текста — быстрее чем Builder
2. **SpannableStringBuilder** для динамического текста — эффективнее для множественных изменений
3. **Кэшировать** стилизованный текст в `RecyclerView`
4. **Избегать** избыточных spans — каждый добавляет overhead
5. **Переиспользовать** spans когда возможно

## Answer (EN)

**Spannable** is an interface for text to which markup objects can be attached at runtime. Used for dynamic styling of text portions or entire paragraphs.

### Core Classes

| Class | Text | Markup | Use Case |
|-------|------|--------|----------|
| **SpannedString** | Immutable | Immutable | Reading |
| **SpannableString** | Immutable | Mutable | <10 spans |
| **SpannableStringBuilder** | Mutable | Mutable | >10 spans |

### Basic Example

```kotlin
val text = SpannableString("Hello World")
text.setSpan(
    ForegroundColorSpan(Color.RED),
    6, 11,  // ✅ Indices for "World"
    Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
)
textView.text = text
```

### Span Flags

- `SPAN_EXCLUSIVE_EXCLUSIVE` — don't include inserted text
- `SPAN_INCLUSIVE_EXCLUSIVE` — include text inserted at start
- `SPAN_EXCLUSIVE_INCLUSIVE` — include text inserted at end
- `SPAN_INCLUSIVE_INCLUSIVE` — include text at both start and end

### Span Categories

**1. Appearance spans** (change appearance without layout recalculation):

```kotlin
ForegroundColorSpan(Color.RED)        // Text color
BackgroundColorSpan(Color.YELLOW)     // Background color
StyleSpan(Typeface.BOLD)              // Bold
UnderlineSpan()                       // Underline
StrikethroughSpan()                   // Strikethrough
```

**2. Metric spans** (require layout recalculation):

```kotlin
RelativeSizeSpan(1.5f)                // Relative size
AbsoluteSizeSpan(24, true)            // ✅ true = sp
ScaleXSpan(2.0f)                      // X-axis scaling
TypefaceSpan("monospace")             // Monospace font
```

**3. Paragraph spans** (apply to entire paragraphs):

```kotlin
QuoteSpan(Color.BLUE)                 // Quote vertical line
BulletSpan(20, Color.RED)             // Bullet point
AlignmentSpan.Standard(ALIGN_CENTER)  // Alignment
```

### Clickable Spans

```kotlin
val clickable = object : ClickableSpan() {
    override fun onClick(view: View) {
        Toast.makeText(view.context, "Clicked", LENGTH_SHORT).show()
    }

    override fun updateDrawState(ds: TextPaint) {
        super.updateDrawState(ds)
        ds.isUnderlineText = false  // ✅ Remove underline
        ds.color = Color.BLUE
    }
}

spannable.setSpan(clickable, 0, 5, SPAN_EXCLUSIVE_EXCLUSIVE)
textView.movementMethod = LinkMovementMethod.getInstance()  // ✅ Required
```

### Extension Functions

```kotlin
inline fun SpannableStringBuilder.appendSpan(
    text: CharSequence,
    what: Any,
    flags: Int = SPAN_EXCLUSIVE_EXCLUSIVE
) = apply {
    val start = length
    append(text)
    setSpan(what, start, length, flags)
}

// ✅ Usage
val styled = SpannableStringBuilder()
    .appendSpan("Bold ", StyleSpan(Typeface.BOLD))
    .appendSpan("Red ", ForegroundColorSpan(Color.RED))
    .appendSpan("Large", RelativeSizeSpan(1.5f))
```

### Performance Considerations

1. **SpannableString** for static text — faster than Builder
2. **SpannableStringBuilder** for dynamic text — efficient for multiple modifications
3. **Cache** styled text in `RecyclerView`
4. **Avoid** excessive spans — each adds overhead
5. **Reuse** spans when possible

## Follow-ups

- How do custom spans differ from framework spans?
- What's the performance impact of using many spans in a `RecyclerView`?
- When should you use SpannableStringBuilder vs SpannableString?
- How do paragraph spans handle text that doesn't end with newline?
- What are the trade-offs between Spannable vs HTML.fromHtml()?

## References

- [Android Spannable Documentation](https://developer.android.com/reference/android/text/Spannable)
- [Spantastic Text Styling with Spans](https://medium.com/androiddevelopers/spantastic-text-styling-with-spans-17b0c16b4568)
- [Text Spans Guide](https://developer.android.com/guide/topics/text/spans)

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]


### Prerequisites (Easier)
- [[q-view-fundamentals--android--easy]]
- [[q-how-to-break-text-by-screen-width--android--easy]]

### Related (Same Level)
- [[q-custom-view-attributes--android--medium]]
- [[q-accessibility-text-scaling--android--medium]]
- [[q-view-methods-and-their-purpose--android--medium]]

### Advanced (Harder)
- [[q-custom-viewgroup-layout--android--hard]]
- [[q-which-class-to-use-for-rendering-view-in-background-thread--android--hard]]

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
updated: 2025-11-11
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

> Что такое Spannable и как его использовать для стилизации текста?

# Question (EN)

> What is Spannable and how do you use it for text styling?

## Ответ (RU)

**Spannable** — интерфейс для текста, к которому можно прикреплять объекты разметки (spans) во время выполнения. Используется для динамической стилизации части текста или целых абзацев.

### Основные Классы

| Класс | Текст | Разметка | Использование |
|-------|-------|----------|---------------|
| **SpannedString** | Неизменяемый | Неизменяемая | Только чтение, заранее подготовленный текст со spans |
| **SpannableString** | Неизменяемый | Изменяемая | Небольшое количество spans, когда текст не меняется |
| **SpannableStringBuilder** | Изменяемый | Изменяемая | Частые изменения текста/диапазонов, сложная разметка |

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

- `SPAN_EXCLUSIVE_EXCLUSIVE` — не включать текст, вставленный на границах
- `SPAN_INCLUSIVE_EXCLUSIVE` — включать текст, вставленный в начале диапазона
- `SPAN_EXCLUSIVE_INCLUSIVE` — включать текст, вставленный в конце диапазона
- `SPAN_INCLUSIVE_INCLUSIVE` — включать текст, вставленный на обеих границах

### Категории Spans

**1. Appearance spans** (изменяют визуальное отображение текста; как правило не влияют на метрики шрифта, но всё равно могут приводить к перерисовке/перелэйауту при изменении):

```kotlin
ForegroundColorSpan(Color.RED)        // Цвет текста
BackgroundColorSpan(Color.YELLOW)     // Цвет фона
StyleSpan(Typeface.BOLD)              // Жирный
UnderlineSpan()                       // Подчёркивание
StrikethroughSpan()                   // Зачёркивание
```

**2. Metric spans** (влияют на метрики/размеры шрифта; требуют перерасчёта layout):

```kotlin
RelativeSizeSpan(1.5f)                // Относительный размер
AbsoluteSizeSpan(24, true)            // ✅ true = размер в sp; без true — в px
ScaleXSpan(2.0f)                      // Масштабирование по X
TypefaceSpan("monospace")             // Моноширинный шрифт (на новых API предпочтителен конструктор с Typeface)
```

**3. Paragraph spans** (применяются к целым абзацам, т.е. диапазону до символа перевода строки; корректное поведение ожидается, когда span покрывает весь абзац):

```kotlin
QuoteSpan(Color.BLUE)                 // Вертикальная линия цитаты
BulletSpan(20, Color.RED)            // Маркер списка
AlignmentSpan.Standard(ALIGN_CENTER)  // Выравнивание абзаца
```

### Кликабельные Spans

```kotlin
val spannable = SpannableString("Click me")

val clickable = object : ClickableSpan() {
    override fun onClick(view: View) {
        Toast.makeText(view.context, "Clicked", Toast.LENGTH_SHORT).show()
    }

    override fun updateDrawState(ds: TextPaint) {
        super.updateDrawState(ds)
        ds.isUnderlineText = false  // ✅ Убрать подчёркивание
        ds.color = Color.BLUE
    }
}

spannable.setSpan(clickable, 0, 5, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
textView.text = spannable
textView.movementMethod = LinkMovementMethod.getInstance()  // ✅ Обязательно для обработки кликов
```

### Extension-функции

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

// ✅ Использование
val styled = SpannableStringBuilder()
    .appendSpan("Bold ", StyleSpan(Typeface.BOLD))
    .appendSpan("Red ", ForegroundColorSpan(Color.RED))
    .appendSpan("Large", RelativeSizeSpan(1.5f))
```

### Производительность

1. **SpannableString** — хороший выбор для статического текста: текст неизменяем, можно добавить spans один раз.
2. **SpannableStringBuilder** — предпочтителен для динамического текста и множественных изменений.
3. **Кэшировать** стилизованный текст в RecyclerView.
4. **Избегать** избыточных spans — каждый добавляет overhead при layout/отрисовке.
5. **Осторожно переиспользовать** spans: безопасно для простых, stateless spans (например, цвет/стиль), но не для spans с внутренним состоянием, зависящим от диапазона или view.

## Answer (EN)

**Spannable** is an interface for text to which markup objects (spans) can be attached at runtime. It is used for dynamic styling of text portions or entire paragraphs.

### Core Classes

| Class | Text | Markup | Use Case |
|-------|------|--------|----------|
| **SpannedString** | Immutable | Immutable | Read-only, prebuilt text with spans |
| **SpannableString** | Immutable | Mutable | Small number of spans when text itself does not change |
| **SpannableStringBuilder** | Mutable | Mutable | Frequent edits / complex styling with many spans |

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

- `SPAN_EXCLUSIVE_EXCLUSIVE` — do not include text inserted at the span boundaries
- `SPAN_INCLUSIVE_EXCLUSIVE` — include text inserted at the start boundary
- `SPAN_EXCLUSIVE_INCLUSIVE` — include text inserted at the end boundary
- `SPAN_INCLUSIVE_INCLUSIVE` — include text inserted at both boundaries

### Span Categories

**1. Appearance spans** (change visual appearance; generally do not change font metrics, but updates can still trigger redraw/re-layout as needed):

```kotlin
ForegroundColorSpan(Color.RED)        // Text color
BackgroundColorSpan(Color.YELLOW)     // Background color
StyleSpan(Typeface.BOLD)              // Bold
UnderlineSpan()                       // Underline
StrikethroughSpan()                   // Strikethrough
```

**2. Metric spans** (affect font metrics/size; require layout recalculation):

```kotlin
RelativeSizeSpan(1.5f)                // Relative size
AbsoluteSizeSpan(24, true)            // ✅ true = size in sp; without true = px
ScaleXSpan(2.0f)                      // X-axis scaling
TypefaceSpan("monospace")             // Monospace font (for newer APIs, prefer constructor taking a Typeface)
```

**3. Paragraph spans** (apply to entire paragraphs, i.e., ranges delimited by newlines; correct behavior is expected when the span covers the whole paragraph):

```kotlin
QuoteSpan(Color.BLUE)                 // Quote vertical line
BulletSpan(20, Color.RED)            // Bullet point
AlignmentSpan.Standard(ALIGN_CENTER)  // Paragraph alignment
```

### Clickable Spans

```kotlin
val spannable = SpannableString("Click me")

val clickable = object : ClickableSpan() {
    override fun onClick(view: View) {
        Toast.makeText(view.context, "Clicked", Toast.LENGTH_SHORT).show()
    }

    override fun updateDrawState(ds: TextPaint) {
        super.updateDrawState(ds)
        ds.isUnderlineText = false  // ✅ Remove underline
        ds.color = Color.BLUE
    }
}

spannable.setSpan(clickable, 0, 5, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
textView.text = spannable
textView.movementMethod = LinkMovementMethod.getInstance()  // ✅ Required for click handling
```

### Extension Functions

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

// ✅ Usage
val styled = SpannableStringBuilder()
    .appendSpan("Bold ", StyleSpan(Typeface.BOLD))
    .appendSpan("Red ", ForegroundColorSpan(Color.RED))
    .appendSpan("Large", RelativeSizeSpan(1.5f))
```

### Performance Considerations

1. **SpannableString** is a good fit for static text: text is immutable; you set spans once.
2. **SpannableStringBuilder** is better for dynamic text and multiple modifications.
3. **Cache** styled text in RecyclerView.
4. **Avoid** excessive spans — each adds overhead during layout/draw.
5. **Reuse spans carefully**: safe for simple stateless spans (e.g., color/style), but avoid reusing spans that hold internal state or depend on a specific range/view.

## Дополнительные вопросы (RU)

- В чем отличие пользовательских (custom) spans от стандартных spans из фреймворка?
- Как использование большого количества spans влияет на производительность в RecyclerView?
- Когда следует использовать `SpannableStringBuilder` вместо `SpannableString`?
- Как абзацные spans обрабатывают текст, который не заканчивается символом новой строки?
- Каковы плюсы и минусы использования `Spannable` по сравнению с `Html.fromHtml()`?

## Follow-ups

- How do custom spans differ from framework spans?
- What's the performance impact of using many spans in a RecyclerView?
- When should you use SpannableStringBuilder vs SpannableString?
- How do paragraph spans handle text that doesn't end with newline?
- What are the trade-offs between Spannable vs HTML.fromHtml()?

## Ссылки (RU)

- [Документация Android Spannable](https://developer.android.com/reference/android/text/Spannable)
- [Spantastic Text Styling with Spans](https://medium.com/androiddevelopers/spantastic-text-styling-with-spans-17b0c16b4568)
- [Руководство по Text Spans](https://developer.android.com/guide/topics/text/spans)

## References

- [Android Spannable Documentation](https://developer.android.com/reference/android/text/Spannable)
- [Spantastic Text Styling with Spans](https://medium.com/androiddevelopers/spantastic-text-styling-with-spans-17b0c16b4568)
- [Text Spans Guide](https://developer.android.com/guide/topics/text/spans)

## Связанные вопросы (RU)

### Предпосылки / Концепции

- [[c-android-components]]

### Предпосылки (проще)

- [[q-view-fundamentals--android--easy]]
- [[q-how-to-break-text-by-screen-width--android--easy]]

### Связанные (такой же уровень)

- [[q-custom-view-attributes--android--medium]]
- [[q-accessibility-text-scaling--android--medium]]
- [[q-view-methods-and-their-purpose--android--medium]]

### Продвинутые (сложнее)

- [[q-custom-viewgroup-layout--android--hard]]
- [[q-which-class-to-use-for-rendering-view-in-background-thread--android--hard]]

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

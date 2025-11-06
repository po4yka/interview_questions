---
id: android-476
title: Custom View Attributes / Атрибуты Custom View
aliases: [Custom View Attributes, Атрибуты Custom View]
topic: android
subtopics:
  - ui-theming
  - ui-views
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-custom-views
  - q-custom-view-lifecycle--android--medium
created: 2025-10-21
updated: 2025-10-30
tags: [android/ui-theming, android/ui-views, difficulty/medium]
sources: []
---

# Вопрос (RU)
> Как работают кастомные атрибуты в Custom `View` и как их правильно объявлять и считывать?

# Question (EN)
> How do custom attributes work in Custom Views, and how to properly declare and read them?

---

## Ответ (RU)

**Кастомные XML-атрибуты** позволяют настраивать Custom `View` прямо в XML-разметке. Android использует **TypedArray** для типобезопасного чтения атрибутов с поддержкой стилей, тем и значений по умолчанию.

**Основные этапы**:
1. Объявить атрибуты в `res/values/attrs.xml`
2. Считать значения через `TypedArray` в конструкторе view
3. Обязательно вызвать `recycle()` для освобождения ресурсов

### Объявление Атрибутов

```xml
<!-- res/values/attrs.xml -->
<resources>
    <declare-styleable name="ProgressBar">
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <attr name="barHeight" format="dimension" />
    </declare-styleable>
</resources>
```

**Форматы атрибутов**:
- `color`, `dimension`, `string`, `boolean`, `integer`, `float`
- `reference` — ссылка на ресурс
- `enum` — набор именованных значений
- `flags` — битовая маска (можно комбинировать)

### Чтение Атрибутов

```kotlin
class ProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress: Float = 0f
    private var progressColor: Int = Color.BLUE

    init {
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.ProgressBar,
            defStyleAttr,
            0  // defStyleRes
        ).apply {
            try {
                // ✅ Всегда указывайте дефолтные значения
                progress = getFloat(R.styleable.ProgressBar_progress, 0f)
                progressColor = getColor(R.styleable.ProgressBar_progressColor, Color.BLUE)
            } finally {
                recycle()  // ✅ Обязательно освободите ресурсы
            }
        }
    }
}
```

**Параметры конструктора**:
- `attrs: AttributeSet?` — набор XML-атрибутов из layout
- `defStyleAttr: Int` — атрибут темы с дефолтным стилем (`R.attr.customProgressBarStyle`)
- `defStyleRes: Int` — ID стиля по умолчанию (`R.style.DefaultProgressBar`)

### Использование В XML

```xml
<ProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:progress="75"
    app:progressColor="@color/primary"
    app:barHeight="12dp" />
```

### Enum И Flags

```xml
<!-- Enum: выбор одного значения -->
<attr name="mode" format="enum">
    <enum name="linear" value="0" />
    <enum name="circular" value="1" />
</attr>

<!-- Flags: комбинация значений -->
<attr name="features" format="flags">
    <flag name="animate" value="0x01" />
    <flag name="showLabel" value="0x02" />
</attr>
```

```kotlin
// Чтение enum
val mode = getInt(R.styleable.ProgressBar_mode, 0)

// Чтение flags (битовая маска)
val features = getInt(R.styleable.ProgressBar_features, 0)
val shouldAnimate = (features and 0x01) != 0
```

### Почему recycle() Обязателен

`TypedArray` использует внутренний пул ресурсов. Без `recycle()` происходит утечка памяти, и пул исчерпывается, вызывая падения приложения.

```kotlin
// ❌ Утечка памяти
val a = context.obtainStyledAttributes(attrs, R.styleable.MyView, 0, 0)
val color = a.getColor(R.styleable.MyView_color, Color.RED)
// recycle() не вызван!

// ✅ Правильно с try-finally
context.obtainStyledAttributes(attrs, R.styleable.MyView, 0, 0).apply {
    try {
        // читаем атрибуты
    } finally {
        recycle()  // гарантированное освобождение
    }
}
```

## Answer (EN)

**Custom XML attributes** enable configuring Custom Views directly in XML layouts. Android uses **TypedArray** for type-safe attribute reading with support for styles, themes, and default values.

**Key steps**:
1. Declare attributes in `res/values/attrs.xml`
2. Read values via `TypedArray` in view constructor
3. Always call `recycle()` to release resources

### Declaring Attributes

```xml
<!-- res/values/attrs.xml -->
<resources>
    <declare-styleable name="ProgressBar">
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <attr name="barHeight" format="dimension" />
    </declare-styleable>
</resources>
```

**Attribute formats**:
- `color`, `dimension`, `string`, `boolean`, `integer`, `float`
- `reference` — resource reference
- `enum` — named value set
- `flags` — bit mask (combinable)

### Reading Attributes

```kotlin
class ProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress: Float = 0f
    private var progressColor: Int = Color.BLUE

    init {
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.ProgressBar,
            defStyleAttr,
            0  // defStyleRes
        ).apply {
            try {
                // ✅ Always provide default values
                progress = getFloat(R.styleable.ProgressBar_progress, 0f)
                progressColor = getColor(R.styleable.ProgressBar_progressColor, Color.BLUE)
            } finally {
                recycle()  // ✅ Must release resources
            }
        }
    }
}
```

**Constructor parameters**:
- `attrs: AttributeSet?` — XML attributes from layout
- `defStyleAttr: Int` — theme attribute with default style (`R.attr.customProgressBarStyle`)
- `defStyleRes: Int` — default style ID (`R.style.DefaultProgressBar`)

### XML Usage

```xml
<ProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:progress="75"
    app:progressColor="@color/primary"
    app:barHeight="12dp" />
```

### Enum and Flags

```xml
<!-- Enum: single value selection -->
<attr name="mode" format="enum">
    <enum name="linear" value="0" />
    <enum name="circular" value="1" />
</attr>

<!-- Flags: combinable values -->
<attr name="features" format="flags">
    <flag name="animate" value="0x01" />
    <flag name="showLabel" value="0x02" />
</attr>
```

```kotlin
// Reading enum
val mode = getInt(R.styleable.ProgressBar_mode, 0)

// Reading flags (bit mask)
val features = getInt(R.styleable.ProgressBar_features, 0)
val shouldAnimate = (features and 0x01) != 0
```

### Why recycle() is Mandatory

`TypedArray` uses an internal resource pool. Without `recycle()`, memory leaks occur and the pool depletes, causing app crashes.

```kotlin
// ❌ Memory leak
val a = context.obtainStyledAttributes(attrs, R.styleable.MyView, 0, 0)
val color = a.getColor(R.styleable.MyView_color, Color.RED)
// recycle() not called!

// ✅ Correct with try-finally
context.obtainStyledAttributes(attrs, R.styleable.MyView, 0, 0).apply {
    try {
        // read attributes
    } finally {
        recycle()  // guaranteed release
    }
}
```

---

## Follow-ups

- How does attribute resolution work through the style and theme hierarchy?
- What happens if you forget to call recycle() on TypedArray?
- When should you use defStyleAttr vs defStyleRes parameter?
- How to implement custom attribute validation for enum types?
- Can custom attributes reference theme attributes using `?attr/` syntax?

## References

- [[c-custom-views]]
- https://developer.android.com/develop/ui/views/layout/custom-views/create-view
- https://developer.android.com/develop/ui/views/theming/themes

## Related Questions

### Prerequisites
- [[q-custom-view-lifecycle--android--medium]] — Understanding view initialization lifecycle

### Related
- Custom view state persistence patterns

### Advanced
- Dynamic attribute updates during runtime
- Attribute interpolation for animations

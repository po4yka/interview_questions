---
id: 20251021-170000
title: Custom View Attributes / Атрибуты Custom View
aliases:
- Custom View Attributes
- Атрибуты Custom View
topic: android
subtopics:
- ui-views
- ui-theming
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- q-how-to-add-custom-attributes-to-custom-view--android--medium
- q-custom-view-lifecycle--android--medium
created: 2025-10-21
updated: 2025-10-21
tags:
- android/ui-views
- android/ui-theming
- difficulty/medium
source: https://developer.android.com/guide/topics/ui/themes
source_note: Official theming guide
---

# Вопрос (RU)
> Атрибуты Custom View?

# Question (EN)
> Custom View Attributes?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Custom Attributes Theory

**Custom XML attributes** allow configuring custom views directly in XML files, making them reusable and customizable. Android system uses **TypedArray** for reading attributes with support for styles, themes, and default values.

Based on [[c-custom-views]] and c-android-theming.

**Key principles**:
- **AttributeSet** contains all XML attributes
- **TypedArray** provides type-safe access to values
- **Style hierarchy** supports style inheritance
- **Default values** provide fallback values

### Attribute Types

| Type | Format | Usage |
|------|--------|-------|
| **color** | Color values | Background, text, border colors |
| **dimension** | Sizes (dp, sp, px) | Padding, sizes, thickness |
| **string** | String values | Text, descriptions |
| **boolean** | true/false | Enable/disable features |
| **float/integer** | Numeric values | Percentages, counters |
| **reference** | Resource references | Drawable, strings, colors |
| **enum** | Enumerated values | Styles, directions |
| **flags** | Bit mask | Flag combinations |

### Attribute Declaration in attrs.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <declare-styleable name="CustomProgressBar">
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <attr name="backgroundColor" format="color" />
        <attr name="showPercentage" format="boolean" />
        <attr name="barHeight" format="dimension" />
        <attr name="label" format="string" />
        <attr name="icon" format="reference" />

        <attr name="animationStyle" format="enum">
            <enum name="none" value="0" />
            <enum name="fade" value="1" />
            <enum name="slide" value="2" />
        </attr>

        <attr name="edges" format="flags">
            <flag name="left" value="0x01" />
            <flag name="top" value="0x02" />
            <flag name="right" value="0x04" />
            <flag name="bottom" value="0x08" />
        </attr>
    </declare-styleable>
</resources>
```

### Reading Attributes in Constructor

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0,
    defStyleRes: Int = 0
) : View(context, attrs, defStyleAttr, defStyleRes) {

    var progress = 0f
    var progressColor = Color.BLUE
    var backgroundColor = Color.LIGHT_GRAY
    var showPercentage = false
    var barHeight = 8.dpToPx()
    var label = ""
    var icon: Drawable? = null
    var animationStyle = AnimationStyle.NONE
    var edges = Edges.ALL

    init {
        // Read attributes from XML
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.CustomProgressBar,
            defStyleAttr,
            defStyleRes
        ).apply {
            try {
                progress = getFloat(R.styleable.CustomProgressBar_progress, 0f)
                progressColor = getColor(R.styleable.CustomProgressBar_progressColor, Color.BLUE)
                backgroundColor = getColor(R.styleable.CustomProgressBar_backgroundColor, Color.LIGHT_GRAY)
                showPercentage = getBoolean(R.styleable.CustomProgressBar_showPercentage, false)
                barHeight = getDimension(R.styleable.CustomProgressBar_barHeight, 8.dpToPx())
                label = getString(R.styleable.CustomProgressBar_label) ?: ""
                icon = getDrawable(R.styleable.CustomProgressBar_icon)
                animationStyle = AnimationStyle.values()[getInt(R.styleable.CustomProgressBar_animationStyle, 0)]
                edges = Edges.fromFlags(getInt(R.styleable.CustomProgressBar_edges, Edges.ALL.value))
            } finally {
                recycle() // Release resources
            }
        }
    }

    private fun Int.dpToPx(): Int =
        (this * Resources.getSystem().displayMetrics.density).toInt()

    enum class AnimationStyle { NONE, FADE, SLIDE }

    enum class Edges(val value: Int) {
        NONE(0),
        LEFT(0x01),
        TOP(0x02),
        RIGHT(0x04),
        BOTTOM(0x08),
        ALL(0x0F);

        companion object {
            fun fromFlags(flags: Int): Edges = values().find { it.value == flags } ?: ALL
        }
    }
}
```

### Styles and Themes Support

```xml
<!-- res/values/styles.xml -->
<style name="Widget.ProgressBar">
    <item name="progressColor">@color/primary</item>
    <item name="backgroundColor">@color/surface</item>
    <item name="barHeight">12dp</item>
    <item name="showPercentage">true</item>
</style>

<style name="Widget.ProgressBar.Small">
    <item name="barHeight">4dp</item>
    <item name="showPercentage">false</item>
</style>

<style name="Widget.ProgressBar.Large">
    <item name="barHeight">16dp</item>
    <item name="showPercentage">true</item>
</style>
```

### XML Usage

```xml
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:style="@style/Widget.ProgressBar"
    app:progress="75"
    app:label="Loading"
    app:animationStyle="fade"
    app:edges="left|right" />
```

### Best Practices

1. **Always use TypedArray** for reading attributes
2. **Don't forget recycle()** TypedArray to release resources
3. **Provide default values** for all attributes
4. **Use enum for limited value sets**
5. **Group related attributes** in one declare-styleable
6. **Support styles and themes** for reusability
7. **Document attributes** for other developers

### Pitfalls

- **Don't forget recycle()** TypedArray - can cause memory leaks
- **Handle null values properly** for optional attributes
- **Use correct attribute formats** for type safety
- **Check value boundaries** for enum and flags
- **Test with different styles** and themes

---

## Follow-ups

- How to create custom attribute groups?
- What are the performance implications of custom attributes?
- How to handle attribute inheritance in custom views?
- When to use reference vs direct values?

## References

- [Custom Views Guide](https://developer.android.com/guide/topics/ui/custom-components)
- [Themes and Styles Guide](https://developer.android.com/guide/topics/ui/themes)

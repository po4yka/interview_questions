---
id: "20251015082237326"
title: "Custom View Attributes / Атрибуты кастомных View"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - custom-views
  - xml-attributes
  - android-framework
  - theming
---
# Custom View Attributes

# Question (EN)
> How do you add custom XML attributes to a custom view? Explain attribute declaration in attrs.xml, reading attributes in the constructor, and supporting styles and themes.

# Вопрос (RU)
> Как добавить пользовательские XML атрибуты к пользовательскому view? Объясните объявление атрибутов в attrs.xml, чтение атрибутов в конструкторе и поддержку стилей и тем.

---

## Answer (EN)

**Custom XML attributes** allow you to configure your custom views directly in layout XML files, making them reusable and customizable. This is essential for creating production-ready custom views.

### Complete Custom Attribute Implementation

**Step 1: Declare attributes in res/values/attrs.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <declare-styleable name="ProgressBar">
        <!-- Simple attributes -->
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <attr name="backgroundColor" format="color" />
        <attr name="showPercentage" format="boolean" />

        <!-- Dimension attributes -->
        <attr name="barHeight" format="dimension" />
        <attr name="cornerRadius" format="dimension" />

        <!-- String attributes -->
        <attr name="label" format="string" />

        <!-- Reference attributes (to other resources) -->
        <attr name="icon" format="reference" />

        <!-- Enum attributes -->
        <attr name="animationStyle" format="enum">
            <enum name="none" value="0" />
            <enum name="fade" value="1" />
            <enum name="slide" value="2" />
        </attr>

        <!-- Flag attributes (multiple values) -->
        <attr name="edges" format="flags">
            <flag name="left" value="0x01" />
            <flag name="top" value="0x02" />
            <flag name="right" value="0x04" />
            <flag name="bottom" value="0x08" />
        </attr>

        <!-- Multiple formats -->
        <attr name="customPadding" format="dimension|reference" />
    </declare-styleable>
</resources>
```

**Step 2: Read attributes in custom view constructor**

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0,
    defStyleRes: Int = 0
) : View(context, attrs, defStyleAttr, defStyleRes) {

    // Default values
    var progress: Float = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            invalidate()
        }

    var progressColor: Int = Color.BLUE
        set(value) {
            field = value
            progressPaint.color = value
            invalidate()
        }

    var backgroundColor: Int = Color.LIGHT_GRAY
        set(value) {
            field = value
            backgroundPaint.color = value
            invalidate()
        }

    var showPercentage: Boolean = true
        set(value) {
            field = value
            invalidate()
        }

    var barHeight: Float = 50f
        set(value) {
            field = value
            requestLayout()
        }

    var cornerRadius: Float = 0f
        set(value) {
            field = value
            invalidate()
        }

    var label: String = ""
        set(value) {
            field = value
            invalidate()
        }

    var iconDrawable: Drawable? = null
        set(value) {
            field = value
            invalidate()
        }

    var animationStyle: AnimationStyle = AnimationStyle.NONE
    var edges: Int = 0

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }

    private val backgroundPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textAlign = Paint.Align.CENTER
        textSize = 18f.spToPx()
        color = Color.WHITE
    }

    init {
        // Read attributes
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.ProgressBar,
            defStyleAttr,
            defStyleRes
        ).apply {
            try {
                // Read attributes with defaults
                progress = getFloat(R.styleable.ProgressBar_progress, 0f)

                progressColor = getColor(
                    R.styleable.ProgressBar_progressColor,
                    Color.BLUE
                )

                backgroundColor = getColor(
                    R.styleable.ProgressBar_backgroundColor,
                    Color.LIGHT_GRAY
                )

                showPercentage = getBoolean(
                    R.styleable.ProgressBar_showPercentage,
                    true
                )

                barHeight = getDimension(
                    R.styleable.ProgressBar_barHeight,
                    50f.dpToPx()
                )

                cornerRadius = getDimension(
                    R.styleable.ProgressBar_cornerRadius,
                    0f
                )

                label = getString(R.styleable.ProgressBar_label) ?: ""

                iconDrawable = getDrawable(R.styleable.ProgressBar_icon)

                animationStyle = AnimationStyle.values()[
                    getInt(R.styleable.ProgressBar_animationStyle, 0)
                ]

                edges = getInt(R.styleable.ProgressBar_edges, 0)

            } finally {
                // IMPORTANT: Always recycle!
                recycle()
            }
        }

        // Apply read values to Paint objects
        progressPaint.color = progressColor
        backgroundPaint.color = backgroundColor
    }

    enum class AnimationStyle {
        NONE, FADE, SLIDE
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val width = width.toFloat()
        val height = barHeight

        // Draw background
        canvas.drawRoundRect(
            0f, 0f, width, height,
            cornerRadius, cornerRadius,
            backgroundPaint
        )

        // Draw progress
        val progressWidth = width * (progress / 100f)
        canvas.drawRoundRect(
            0f, 0f, progressWidth, height,
            cornerRadius, cornerRadius,
            progressPaint
        )

        // Draw percentage text
        if (showPercentage) {
            val text = "${progress.toInt()}%"
            canvas.drawText(
                text,
                width / 2f,
                height / 2f - (textPaint.descent() + textPaint.ascent()) / 2f,
                textPaint
            )
        }

        // Draw label if set
        if (label.isNotEmpty()) {
            canvas.drawText(
                label,
                width / 2f,
                height + 30f,
                textPaint
            )
        }
    }

    private fun Float.dpToPx(): Float =
        this * context.resources.displayMetrics.density

    private fun Float.spToPx(): Float =
        this * context.resources.displayMetrics.scaledDensity
}
```

**Step 3: Use in XML layout**

```xml
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:progress="75"
    app:progressColor="@color/blue"
    app:backgroundColor="@color/gray"
    app:showPercentage="true"
    app:barHeight="60dp"
    app:cornerRadius="8dp"
    app:label="Download Progress"
    app:icon="@drawable/ic_download"
    app:animationStyle="fade"
    app:edges="left|right" />
```

---

### Attribute Formats

**Available formats:**

| Format | Description | Example |
|--------|-------------|---------|
| `boolean` | true/false | `showLabel="true"` |
| `integer` | Integer number | `count="10"` |
| `float` | Floating point | `progress="75.5"` |
| `string` | Text | `label="Hello"` |
| `color` | Color value | `textColor="#FF0000"` |
| `dimension` | Size with unit | `textSize="16sp"` |
| `reference` | Reference to resource | `icon="@drawable/ic_star"` |
| `enum` | One value from set | `style="bold"` |
| `flags` | Multiple values | `edges="left\|right"` |
| `fraction` | Percentage | `weight="0.5"` |

**Multiple formats:**
```xml
<attr name="customValue" format="dimension|reference|fraction" />
```

---

### Supporting Styles

**Step 1: Define default style attribute in attrs.xml**

```xml
<resources>
    <!-- Define custom style attribute -->
    <attr name="customProgressBarStyle" format="reference" />

    <declare-styleable name="ProgressBar">
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <!-- ... other attributes ... -->
    </declare-styleable>
</resources>
```

**Step 2: Create style in styles.xml**

```xml
<resources>
    <!-- Default style for CustomProgressBar -->
    <style name="Widget.App.ProgressBar" parent="">
        <item name="progress">0</item>
        <item name="progressColor">@color/primary</item>
        <item name="backgroundColor">@color/surface</item>
        <item name="showPercentage">true</item>
        <item name="barHeight">50dp</item>
        <item name="cornerRadius">8dp</item>
        <item name="animationStyle">fade</item>
    </style>

    <!-- Success variant -->
    <style name="Widget.App.ProgressBar.Success">
        <item name="progressColor">@color/green</item>
        <item name="backgroundColor">@color/light_green</item>
    </style>

    <!-- Error variant -->
    <style name="Widget.App.ProgressBar.Error">
        <item name="progressColor">@color/red</item>
        <item name="backgroundColor">@color/light_red</item>
    </style>
</resources>
```

**Step 3: Set default style in theme**

```xml
<resources>
    <style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
        <!-- Set default style for CustomProgressBar -->
        <item name="customProgressBarStyle">@style/Widget.App.ProgressBar</item>
    </style>
</resources>
```

**Step 4: Use default style in constructor**

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = R.attr.customProgressBarStyle, // Use theme attribute
    defStyleRes: Int = R.style.Widget_App_ProgressBar  // Fallback
) : View(context, attrs, defStyleAttr, defStyleRes) {
    // ... constructor implementation ...
}
```

**Usage in XML:**

```xml
<!-- Uses default style from theme -->
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:progress="50" />

<!-- Applies custom style -->
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    style="@style/Widget.App.ProgressBar.Success"
    app:progress="100" />

<!-- XML attributes override style -->
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    style="@style/Widget.App.ProgressBar.Success"
    app:progress="75"
    app:progressColor="@color/blue" /> <!-- Overrides style color -->
```

---

### Attribute Priority

**Precedence (highest to lowest):**

1. **XML attribute** - Direct attribute in layout
2. **XML style** - `style="@style/..."` in layout
3. **defStyleAttr** - Theme attribute
4. **defStyleRes** - Default style resource
5. **Hard-coded default** - Fallback in code

**Example:**
```kotlin
context.theme.obtainStyledAttributes(
    attrs,
    R.styleable.ProgressBar,
    defStyleAttr,      // Priority 3: Theme attribute
    defStyleRes        // Priority 4: Default style
).apply {
    progress = getFloat(
        R.styleable.ProgressBar_progress,
        0f  // Priority 5: Hard-coded default
    )
    // Priority 1-2 from XML automatically applied
}
```

---

### Theme Integration

**Create theme-aware attributes:**

**attrs.xml:**
```xml
<resources>
    <!-- Define themeable colors -->
    <attr name="progressBarColor" format="color" />
    <attr name="progressBarBackground" format="color" />

    <declare-styleable name="ProgressBar">
        <attr name="progressColor" format="color" />
        <attr name="backgroundColor" format="color" />
    </declare-styleable>
</resources>
```

**themes.xml:**
```xml
<resources>
    <style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
        <!-- Light theme colors -->
        <item name="progressBarColor">@color/blue_500</item>
        <item name="progressBarBackground">@color/gray_200</item>
    </style>

    <style name="AppTheme.Dark" parent="AppTheme">
        <!-- Dark theme colors -->
        <item name="progressBarColor">@color/blue_300</item>
        <item name="progressBarBackground">@color/gray_800</item>
    </style>
</resources>
```

**Read from theme:**
```kotlin
init {
    context.theme.obtainStyledAttributes(
        attrs,
        R.styleable.ProgressBar,
        defStyleAttr,
        defStyleRes
    ).apply {
        try {
            // Try to read from XML/style
            progressColor = getColor(
                R.styleable.ProgressBar_progressColor,
                -1
            )

            // If not set, read from theme
            if (progressColor == -1) {
                progressColor = getThemeColor(R.attr.progressBarColor, Color.BLUE)
            }

        } finally {
            recycle()
        }
    }
}

private fun getThemeColor(attr: Int, defaultColor: Int): Int {
    val typedValue = TypedValue()
    return if (context.theme.resolveAttribute(attr, typedValue, true)) {
        typedValue.data
    } else {
        defaultColor
    }
}
```

---

### Advanced: Custom Attribute Types

**1. Fraction attributes (for percentages):**

```xml
<declare-styleable name="CustomView">
    <attr name="position" format="fraction" />
</declare-styleable>
```

```kotlin
init {
    context.theme.obtainStyledAttributes(attrs, R.styleable.CustomView).apply {
        val position = getFraction(
            R.styleable.CustomView_position,
            1, // Base (100% = 1)
            1, // Parent base
            0.5f // Default (50%)
        )
        // position = 0.0 to 1.0
        recycle()
    }
}
```

**XML:**
```xml
<com.example.ui.CustomView
    app:position="75%" />
```

**2. Array attributes:**

**arrays.xml:**
```xml
<resources>
    <array name="rainbow_colors">
        <item>@color/red</item>
        <item>@color/orange</item>
        <item>@color/yellow</item>
        <item>@color/green</item>
        <item>@color/blue</item>
        <item>@color/indigo</item>
        <item>@color/violet</item>
    </array>
</resources>
```

**attrs.xml:**
```xml
<declare-styleable name="RainbowView">
    <attr name="colors" format="reference" />
</declare-styleable>
```

```kotlin
init {
    context.theme.obtainStyledAttributes(attrs, R.styleable.RainbowView).apply {
        val colorsResId = getResourceId(R.styleable.RainbowView_colors, 0)
        if (colorsResId != 0) {
            val colorsArray = resources.obtainTypedArray(colorsResId)
            val colors = IntArray(colorsArray.length()) { i ->
                colorsArray.getColor(i, Color.BLACK)
            }
            colorsArray.recycle()
        }
        recycle()
    }
}
```

**XML:**
```xml
<com.example.ui.RainbowView
    app:colors="@array/rainbow_colors" />
```

---

### Validation and Error Handling

```kotlin
init {
    context.theme.obtainStyledAttributes(
        attrs,
        R.styleable.ProgressBar,
        defStyleAttr,
        defStyleRes
    ).apply {
        try {
            progress = getFloat(R.styleable.ProgressBar_progress, 0f)

            // Validate progress range
            if (progress < 0f || progress > 100f) {
                throw IllegalArgumentException(
                    "Progress must be between 0 and 100, got $progress"
                )
            }

            barHeight = getDimension(R.styleable.ProgressBar_barHeight, 50f.dpToPx())

            // Validate bar height
            if (barHeight <= 0f) {
                throw IllegalArgumentException(
                    "Bar height must be positive, got $barHeight"
                )
            }

            // Check for required attributes
            if (!hasValue(R.styleable.ProgressBar_progressColor)) {
                Log.w("ProgressBar", "progressColor not set, using default")
            }

        } finally {
            recycle()
        }
    }
}
```

---

### Testing Custom Attributes

```kotlin
@RunWith(AndroidJUnit4::class)
class CustomProgressBarTest {

    @Test
    fun testAttributeParsing() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        // Create AttributeSet from XML
        val parser = context.resources.getXml(R.layout.test_progress_bar)
        val attrs = Xml.asAttributeSet(parser)

        // Advance to start tag
        while (parser.eventType != XmlPullParser.START_TAG) {
            parser.next()
        }

        val progressBar = CustomProgressBar(context, attrs)

        assertEquals(75f, progressBar.progress, 0.01f)
        assertEquals(Color.BLUE, progressBar.progressColor)
        assertTrue(progressBar.showPercentage)
    }
}
```

---

### Best Practices

**1. Always recycle TypedArray**
```kotlin
//  DO
context.theme.obtainStyledAttributes(attrs, R.styleable.CustomView).apply {
    try {
        // Read attributes
    } finally {
        recycle() // IMPORTANT!
    }
}

//  DON'T forget to recycle
val a = context.theme.obtainStyledAttributes(attrs, R.styleable.CustomView)
// Read attributes
// Missing recycle() - memory leak!
```

**2. Provide defaults**
```kotlin
progress = getFloat(R.styleable.ProgressBar_progress, 0f) //  Has default
```

**3. Use meaningful names**
```kotlin
//  DO
<attr name="progressColor" format="color" />

//  DON'T
<attr name="color1" format="color" />
```

**4. Document attributes**
```xml
<resources>
    <declare-styleable name="ProgressBar">
        <!-- The current progress value (0-100) -->
        <attr name="progress" format="float" />

        <!-- The color of the progress bar -->
        <attr name="progressColor" format="color" />
    </declare-styleable>
</resources>
```

**5. Support RTL (Right-to-Left)**
```kotlin
if (layoutDirection == View.LAYOUT_DIRECTION_RTL) {
    // Mirror drawing for RTL languages
}
```

---

### Summary

**Creating custom attributes:**
1. Declare in `attrs.xml` with `<declare-styleable>`
2. Read in constructor with `obtainStyledAttributes()`
3. Always `recycle()` TypedArray
4. Provide default values

**Supporting styles:**
1. Define custom style attribute
2. Create styles in `styles.xml`
3. Set default in theme
4. Use in constructor parameters

**Attribute priority:**
1. XML attribute (highest)
2. XML style
3. defStyleAttr (theme)
4. defStyleRes (default style)
5. Hard-coded default (lowest)

**Best practices:**
- Always recycle TypedArray
- Provide sensible defaults
- Validate attribute values
- Support themes
- Document attributes

---

## Ответ (RU)

**Пользовательские XML атрибуты** позволяют конфигурировать ваши custom view прямо в layout XML файлах, делая их переиспользуемыми и настраиваемыми.

### Реализация пользовательских атрибутов

**Шаг 1: Объявить атрибуты в res/values/attrs.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <declare-styleable name="ProgressBar">
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <attr name="backgroundColor" format="color" />
        <attr name="showPercentage" format="boolean" />
        <attr name="barHeight" format="dimension" />

        <!-- Enum атрибуты -->
        <attr name="animationStyle" format="enum">
            <enum name="none" value="0" />
            <enum name="fade" value="1" />
            <enum name="slide" value="2" />
        </attr>

        <!-- Flag атрибуты (множественные значения) -->
        <attr name="edges" format="flags">
            <flag name="left" value="0x01" />
            <flag name="top" value="0x02" />
            <flag name="right" value="0x04" />
            <flag name="bottom" value="0x08" />
        </attr>
    </declare-styleable>
</resources>
```

**Шаг 2: Читать атрибуты в конструкторе**

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    var progress: Float = 0f
    var progressColor: Int = Color.BLUE
    var showPercentage: Boolean = true

    init {
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.ProgressBar,
            defStyleAttr,
            0
        ).apply {
            try {
                progress = getFloat(R.styleable.ProgressBar_progress, 0f)
                progressColor = getColor(R.styleable.ProgressBar_progressColor, Color.BLUE)
                showPercentage = getBoolean(R.styleable.ProgressBar_showPercentage, true)
            } finally {
                recycle() // ВАЖНО: всегда вызывать recycle()!
            }
        }
    }
}
```

**Шаг 3: Использовать в XML**

```xml
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:progress="75"
    app:progressColor="@color/blue"
    app:showPercentage="true"
    app:barHeight="60dp" />
```

### Форматы атрибутов

| Формат | Описание | Пример |
|--------|----------|--------|
| `boolean` | true/false | `showLabel="true"` |
| `integer` | Целое число | `count="10"` |
| `float` | Дробное число | `progress="75.5"` |
| `string` | Текст | `label="Hello"` |
| `color` | Цвет | `textColor="#FF0000"` |
| `dimension` | Размер с единицей | `textSize="16sp"` |
| `reference` | Ссылка на ресурс | `icon="@drawable/ic_star"` |
| `enum` | Одно значение из набора | `style="bold"` |
| `flags` | Множественные значения | `edges="left\|right"` |

### Приоритет атрибутов

1. **XML атрибут** (наивысший)
2. **XML style**
3. **defStyleAttr** (тема)
4. **defStyleRes** (стиль по умолчанию)
5. **Жестко заданное значение** (низший)

### Поддержка стилей и тем

**Шаг 1: Определить атрибут стиля по умолчанию в attrs.xml**

```xml
<resources>
    <!-- Определить custom атрибут стиля -->
    <attr name="customProgressBarStyle" format="reference" />

    <declare-styleable name="ProgressBar">
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <!-- ... другие атрибуты ... -->
    </declare-styleable>
</resources>
```

**Шаг 2: Создать стиль в styles.xml**

```xml
<resources>
    <!-- Стиль по умолчанию для CustomProgressBar -->
    <style name="Widget.App.ProgressBar" parent="">
        <item name="progress">0</item>
        <item name="progressColor">@color/primary</item>
        <item name="backgroundColor">@color/surface</item>
        <item name="showPercentage">true</item>
        <item name="barHeight">50dp</item>
    </style>

    <!-- Вариант Success -->
    <style name="Widget.App.ProgressBar.Success">
        <item name="progressColor">@color/green</item>
        <item name="backgroundColor">@color/light_green</item>
    </style>
</resources>
```

**Шаг 3: Установить стиль по умолчанию в теме**

```xml
<resources>
    <style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
        <!-- Установить стиль по умолчанию для CustomProgressBar -->
        <item name="customProgressBarStyle">@style/Widget.App.ProgressBar</item>
    </style>
</resources>
```

**Шаг 4: Использовать стиль по умолчанию в конструкторе**

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = R.attr.customProgressBarStyle, // Использовать атрибут темы
    defStyleRes: Int = R.style.Widget_App_ProgressBar  // Fallback
) : View(context, attrs, defStyleAttr, defStyleRes) {
    // ... реализация конструктора ...
}
```

**Использование в XML:**

```xml
<!-- Использует стиль по умолчанию из темы -->
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:progress="50" />

<!-- Применяет custom стиль -->
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    style="@style/Widget.App.ProgressBar.Success"
    app:progress="100" />

<!-- XML атрибуты переопределяют стиль -->
<com.example.ui.CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    style="@style/Widget.App.ProgressBar.Success"
    app:progress="75"
    app:progressColor="@color/blue" /> <!-- Переопределяет цвет стиля -->
```

### Приоритет атрибутов

**Приоритет (от высшего к низшему):**

1. **XML атрибут** - прямой атрибут в layout
2. **XML style** - `style="@style/..."` в layout
3. **defStyleAttr** - атрибут темы
4. **defStyleRes** - ресурс стиля по умолчанию
5. **Жестко заданное значение** - fallback в коде

**Пример:**
```kotlin
context.theme.obtainStyledAttributes(
    attrs,
    R.styleable.ProgressBar,
    defStyleAttr,      // Приоритет 3: атрибут темы
    defStyleRes        // Приоритет 4: стиль по умолчанию
).apply {
    progress = getFloat(
        R.styleable.ProgressBar_progress,
        0f  // Приоритет 5: жестко заданное значение
    )
    // Приоритет 1-2 из XML применяется автоматически
}
```

### Интеграция с темами

**Создать theme-aware атрибуты:**

**attrs.xml:**
```xml
<resources>
    <!-- Определить themeable цвета -->
    <attr name="progressBarColor" format="color" />
    <attr name="progressBarBackground" format="color" />

    <declare-styleable name="ProgressBar">
        <attr name="progressColor" format="color" />
        <attr name="backgroundColor" format="color" />
    </declare-styleable>
</resources>
```

**themes.xml:**
```xml
<resources>
    <style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
        <!-- Цвета светлой темы -->
        <item name="progressBarColor">@color/blue_500</item>
        <item name="progressBarBackground">@color/gray_200</item>
    </style>

    <style name="AppTheme.Dark" parent="AppTheme">
        <!-- Цвета темной темы -->
        <item name="progressBarColor">@color/blue_300</item>
        <item name="progressBarBackground">@color/gray_800</item>
    </style>
</resources>
```

**Читать из темы:**
```kotlin
init {
    context.theme.obtainStyledAttributes(
        attrs,
        R.styleable.ProgressBar,
        defStyleAttr,
        defStyleRes
    ).apply {
        try {
            // Попытка прочитать из XML/style
            progressColor = getColor(R.styleable.ProgressBar_progressColor, -1)

            // Если не установлено, читаем из темы
            if (progressColor == -1) {
                progressColor = getThemeColor(R.attr.progressBarColor, Color.BLUE)
            }

        } finally {
            recycle()
        }
    }
}

private fun getThemeColor(attr: Int, defaultColor: Int): Int {
    val typedValue = TypedValue()
    return if (context.theme.resolveAttribute(attr, typedValue, true)) {
        typedValue.data
    } else {
        defaultColor
    }
}
```

### Валидация и обработка ошибок

```kotlin
init {
    context.theme.obtainStyledAttributes(
        attrs,
        R.styleable.ProgressBar,
        defStyleAttr,
        defStyleRes
    ).apply {
        try {
            progress = getFloat(R.styleable.ProgressBar_progress, 0f)

            // Валидация диапазона progress
            if (progress < 0f || progress > 100f) {
                throw IllegalArgumentException(
                    "Progress должен быть между 0 и 100, получено $progress"
                )
            }

            barHeight = getDimension(R.styleable.ProgressBar_barHeight, 50f.dpToPx())

            // Валидация bar height
            if (barHeight <= 0f) {
                throw IllegalArgumentException(
                    "Bar height должна быть положительной, получено $barHeight"
                )
            }

            // Проверка обязательных атрибутов
            if (!hasValue(R.styleable.ProgressBar_progressColor)) {
                Log.w("ProgressBar", "progressColor не установлен, используется значение по умолчанию")
            }

        } finally {
            recycle()
        }
    }
}
```

### Ключевые правила

**1. Всегда освобождайте TypedArray**
```kotlin
// ПРАВИЛЬНО
context.theme.obtainStyledAttributes(attrs, R.styleable.CustomView).apply {
    try {
        // Чтение атрибутов
    } finally {
        recycle() // ВАЖНО!
    }
}

// НЕПРАВИЛЬНО - забыли recycle
val a = context.theme.obtainStyledAttributes(attrs, R.styleable.CustomView)
// Чтение атрибутов
// Отсутствует recycle() - утечка памяти!
```

**2. Предоставляйте значения по умолчанию**
```kotlin
progress = getFloat(R.styleable.ProgressBar_progress, 0f) // Имеет значение по умолчанию
```

**3. Используйте значимые имена**
```kotlin
// ПРАВИЛЬНО
<attr name="progressColor" format="color" />

// НЕПРАВИЛЬНО
<attr name="color1" format="color" />
```

**4. Документируйте атрибуты**
```xml
<resources>
    <declare-styleable name="ProgressBar">
        <!-- Текущее значение progress (0-100) -->
        <attr name="progress" format="float" />

        <!-- Цвет прогресс бара -->
        <attr name="progressColor" format="color" />
    </declare-styleable>
</resources>
```

**5. Поддерживайте RTL (Right-to-Left)**
```kotlin
if (layoutDirection == View.LAYOUT_DIRECTION_RTL) {
    // Зеркалирование отрисовки для RTL языков
}
```

**6. Валидируйте значения атрибутов**
- Проверяйте диапазоны (progress 0-100)
- Валидируйте размеры (положительные значения)
- Проверяйте обязательные атрибуты

**7. Используйте правильные форматы**
- dimension для размеров (dp, sp, px)
- color для цветов
- reference для ресурсов
- enum для ограниченного набора значений

**8. Поддерживайте темы**
- Читайте цвета из темы
- Поддерживайте светлую/темную темы
- Используйте тематические атрибуты

**9. Тестируйте атрибуты**
- Тестируйте значения по умолчанию
- Проверяйте валидацию
- Тестируйте с разными темами

**10. Оптимизируйте производительность**
- Предварительно вычисляйте значения в init
- Кешируйте преобразования (dp to px)
- Избегайте лишних вычислений в onDraw()

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View

---
id: android-347
title: "How To Add Custom Attributes To Custom View / Как добавить кастомные атрибуты к кастомным View"
aliases: [How To Add Custom Attributes To Custom View, Как добавить кастомные атрибуты к кастомным View]
topic: android
subtopics: [ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-app-security-best-practices--security--medium, q-how-to-display-two-identical-fragments-on-the-screen-at-the-same-time--android--easy, q-performance-optimization-android--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-views, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:40:05 pm
---

# Как Добавить Кастомные Атрибуты У Кастомного View?

## Answer (EN)
To add custom attributes to a Custom View, you need to: (1) create `attrs.xml` and describe attributes, (2) add them to styleable, (3) retrieve values in Custom View constructor, (4) use attributes in XML or Kotlin.

### 1. Define Attributes in attrs.xml

```xml
<!-- res/values/attrs.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <declare-styleable name="CircularProgressView">
        <!-- Progress value (0-100) -->
        <attr name="progress" format="integer" />

        <!-- Progress color -->
        <attr name="progressColor" format="color" />

        <!-- Background color -->
        <attr name="backgroundColor" format="color" />

        <!-- Progress width -->
        <attr name="progressWidth" format="dimension" />

        <!-- Text size -->
        <attr name="textSize" format="dimension" />

        <!-- Show percentage text -->
        <attr name="showPercentage" format="boolean" />

        <!-- Enum example -->
        <attr name="progressStyle" format="enum">
            <enum name="filled" value="0" />
            <enum name="outlined" value="1" />
        </attr>
    </declare-styleable>
</resources>
```

### 2. Create Custom View with Attributes

```kotlin
class CircularProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // Default values
    private var progress = 0
    private var progressColor = Color.BLUE
    private var bgColor = Color.LTGRAY
    private var progressWidth = 10f
    private var textSize = 14f
    private var showPercentage = true
    private var progressStyle = 0

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG)

    init {
        // Retrieve custom attributes
        attrs?.let {
            val typedArray = context.obtainStyledAttributes(
                it,
                R.styleable.CircularProgressView,
                defStyleAttr,
                0
            )

            try {
                progress = typedArray.getInt(
                    R.styleable.CircularProgressView_progress,
                    0
                )

                progressColor = typedArray.getColor(
                    R.styleable.CircularProgressView_progressColor,
                    Color.BLUE
                )

                bgColor = typedArray.getColor(
                    R.styleable.CircularProgressView_backgroundColor,
                    Color.LTGRAY
                )

                progressWidth = typedArray.getDimension(
                    R.styleable.CircularProgressView_progressWidth,
                    10f
                )

                textSize = typedArray.getDimension(
                    R.styleable.CircularProgressView_textSize,
                    14f * resources.displayMetrics.scaledDensity
                )

                showPercentage = typedArray.getBoolean(
                    R.styleable.CircularProgressView_showPercentage,
                    true
                )

                progressStyle = typedArray.getInt(
                    R.styleable.CircularProgressView_progressStyle,
                    0
                )

            } finally {
                // Always recycle TypedArray
                typedArray.recycle()
            }
        }

        setupPaints()
    }

    private fun setupPaints() {
        paint.strokeWidth = progressWidth
        paint.style = if (progressStyle == 0) Paint.Style.FILL else Paint.Style.STROKE

        textPaint.textSize = textSize
        textPaint.textAlign = Paint.Align.CENTER
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val centerX = width / 2f
        val centerY = height / 2f
        val radius = minOf(width, height) / 2f - progressWidth

        // Draw background circle
        paint.color = bgColor
        canvas.drawCircle(centerX, centerY, radius, paint)

        // Draw progress arc
        paint.color = progressColor
        val sweepAngle = (progress / 100f) * 360f
        canvas.drawArc(
            centerX - radius,
            centerY - radius,
            centerX + radius,
            centerY + radius,
            -90f,
            sweepAngle,
            progressStyle == 0,
            paint
        )

        // Draw percentage text
        if (showPercentage) {
            textPaint.color = Color.BLACK
            val text = "$progress%"
            val yPos = centerY - (textPaint.descent() + textPaint.ascent()) / 2
            canvas.drawText(text, centerX, yPos, textPaint)
        }
    }

    // Public setters
    fun setProgress(value: Int) {
        progress = value.coerceIn(0, 100)
        invalidate()
    }
}
```

### 3. Use in XML Layout

```xml
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center">

    <!-- Using custom attributes -->
    <com.example.CircularProgressView
        android:id="@+id/progressView"
        android:layout_width="200dp"
        android:layout_height="200dp"
        app:progress="75"
        app:progressColor="@color/purple_500"
        app:backgroundColor="@color/gray_200"
        app:progressWidth="12dp"
        app:textSize="24sp"
        app:showPercentage="true"
        app:progressStyle="filled" />

</LinearLayout>
```

### 4. Different Attribute Formats

```xml
<!-- res/values/attrs.xml -->
<resources>
    <declare-styleable name="CustomView">
        <!-- String -->
        <attr name="customText" format="string" />

        <!-- Integer -->
        <attr name="customCount" format="integer" />

        <!-- Float -->
        <attr name="customRatio" format="float" />

        <!-- Boolean -->
        <attr name="isEnabled" format="boolean" />

        <!-- Color -->
        <attr name="customColor" format="color" />

        <!-- Dimension (dp, sp, px) -->
        <attr name="customSize" format="dimension" />

        <!-- Reference (drawable, color, string resource) -->
        <attr name="customIcon" format="reference" />

        <!-- Enum -->
        <attr name="alignment" format="enum">
            <enum name="left" value="0" />
            <enum name="center" value="1" />
            <enum name="right" value="2" />
        </attr>

        <!-- Flags (can combine multiple) -->
        <attr name="gravity" format="flags">
            <flag name="top" value="0x01" />
            <flag name="bottom" value="0x02" />
            <flag name="left" value="0x04" />
            <flag name="right" value="0x08" />
        </attr>

        <!-- Multiple formats -->
        <attr name="customValue" format="integer|reference" />
    </declare-styleable>
</resources>
```

### 5. Reading Different Attribute Types

```kotlin
class AdvancedCustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    init {
        val ta = context.obtainStyledAttributes(attrs, R.styleable.CustomView)

        try {
            // String
            val text = ta.getString(R.styleable.CustomView_customText) ?: "Default"

            // Integer
            val count = ta.getInt(R.styleable.CustomView_customCount, 0)

            // Float
            val ratio = ta.getFloat(R.styleable.CustomView_customRatio, 1.0f)

            // Boolean
            val enabled = ta.getBoolean(R.styleable.CustomView_isEnabled, true)

            // Color
            val color = ta.getColor(R.styleable.CustomView_customColor, Color.BLACK)

            // Dimension (returns pixels)
            val size = ta.getDimension(R.styleable.CustomView_customSize, 0f)

            // Dimension (returns pixel offset for integers)
            val sizePixels = ta.getDimensionPixelSize(R.styleable.CustomView_customSize, 0)

            // Reference (drawable)
            val icon = ta.getDrawable(R.styleable.CustomView_customIcon)

            // Reference (resource ID)
            val iconResId = ta.getResourceId(R.styleable.CustomView_customIcon, 0)

            // Enum
            val alignment = ta.getInt(R.styleable.CustomView_alignment, 0)

            // Flags
            val gravity = ta.getInt(R.styleable.CustomView_gravity, 0)
            val hasTop = (gravity and 0x01) != 0
            val hasBottom = (gravity and 0x02) != 0

        } finally {
            ta.recycle()
        }
    }
}
```

### 6. Programmatic Usage

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val progressView = findViewById<CircularProgressView>(R.id.progressView)

        // Change attributes programmatically
        progressView.setProgress(85)

        // Animate progress
        ValueAnimator.ofInt(0, 100).apply {
            duration = 2000
            addUpdateListener { animation ->
                progressView.setProgress(animation.animatedValue as Int)
            }
            start()
        }
    }
}
```

### 7. Using Theme Attributes

```xml
<!-- Define in themes.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <item name="progressColor">@color/primary</item>
    <item name="backgroundColor">@color/surface</item>
</style>

<!-- Reference theme attribute in attrs.xml -->
<declare-styleable name="CircularProgressView">
    <attr name="progressColor" format="color" />
    <attr name="backgroundColor" format="color" />
</declare-styleable>

<!-- Use in custom view -->
<com.example.CircularProgressView
    android:layout_width="200dp"
    android:layout_height="200dp"
    app:progressColor="?attr/colorPrimary"
    app:backgroundColor="?attr/colorSurface" />
```

### 8. Reusing System Attributes

```xml
<!-- Reuse Android's built-in attributes -->
<declare-styleable name="CustomButton">
    <attr name="android:text" />
    <attr name="android:textColor" />
    <attr name="android:textSize" />
    <attr name="customIcon" format="reference" />
</declare-styleable>
```

```kotlin
class CustomButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : androidx.appcompat.widget.AppCompatButton(context, attrs) {

    init {
        val ta = context.obtainStyledAttributes(attrs, R.styleable.CustomButton)

        try {
            // Read Android's built-in attributes
            val text = ta.getString(R.styleable.CustomButton_android_text)
            val textColor = ta.getColor(
                R.styleable.CustomButton_android_textColor,
                Color.BLACK
            )

            // Read custom attribute
            val icon = ta.getDrawable(R.styleable.CustomButton_customIcon)

            // Apply
            this.text = text
            this.setTextColor(textColor)
            setCompoundDrawablesWithIntrinsicBounds(icon, null, null, null)

        } finally {
            ta.recycle()
        }
    }
}
```

### Best Practices

1. - **Always recycle TypedArray** with `typedArray.recycle()`
2. - **Provide default values** for all attributes
3. - **Use appropriate format** for each attribute type
4. - **Document attributes** with comments in attrs.xml
5. - **Group related attributes** in same styleable
6. - **Support theme attributes** for consistency
7. - **Validate attribute values** (e.g., progress 0-100)

---

# Как Добавить Кастомные Атрибуты У Кастомного view

## Ответ (RU)
Чтобы добавить кастомные атрибуты к Custom View, нужно: (1) создать `attrs.xml` и описать атрибуты, (2) добавить их в styleable, (3) получить значения в конструкторе Custom View, (4) использовать атрибуты в XML или Kotlin.

### 1. Определение Атрибутов В attrs.xml

```xml
<!-- res/values/attrs.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <declare-styleable name="CircularProgressView">
        <!-- Значение прогресса (0-100) -->
        <attr name="progress" format="integer" />

        <!-- Цвет прогресса -->
        <attr name="progressColor" format="color" />

        <!-- Цвет фона -->
        <attr name="backgroundColor" format="color" />

        <!-- Ширина прогресса -->
        <attr name="progressWidth" format="dimension" />

        <!-- Размер текста -->
        <attr name="textSize" format="dimension" />

        <!-- Показывать процентный текст -->
        <attr name="showPercentage" format="boolean" />

        <!-- Пример enum -->
        <attr name="progressStyle" format="enum">
            <enum name="filled" value="0" />
            <enum name="outlined" value="1" />
        </attr>
    </declare-styleable>
</resources>
```

### 2. Создание Custom View С Атрибутами

```kotlin
class CircularProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // Значения по умолчанию
    private var progress = 0
    private var progressColor = Color.BLUE
    private var bgColor = Color.LTGRAY
    private var progressWidth = 10f
    private var textSize = 14f
    private var showPercentage = true
    private var progressStyle = 0

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG)

    init {
        // Получение кастомных атрибутов
        attrs?.let {
            val typedArray = context.obtainStyledAttributes(
                it,
                R.styleable.CircularProgressView,
                defStyleAttr,
                0
            )

            try {
                progress = typedArray.getInt(
                    R.styleable.CircularProgressView_progress,
                    0
                )

                progressColor = typedArray.getColor(
                    R.styleable.CircularProgressView_progressColor,
                    Color.BLUE
                )

                bgColor = typedArray.getColor(
                    R.styleable.CircularProgressView_backgroundColor,
                    Color.LTGRAY
                )

                progressWidth = typedArray.getDimension(
                    R.styleable.CircularProgressView_progressWidth,
                    10f
                )

                textSize = typedArray.getDimension(
                    R.styleable.CircularProgressView_textSize,
                    14f * resources.displayMetrics.scaledDensity
                )

                showPercentage = typedArray.getBoolean(
                    R.styleable.CircularProgressView_showPercentage,
                    true
                )

                progressStyle = typedArray.getInt(
                    R.styleable.CircularProgressView_progressStyle,
                    0
                )

            } finally {
                // Всегда переработайте TypedArray
                typedArray.recycle()
            }
        }

        setupPaints()
    }

    private fun setupPaints() {
        paint.strokeWidth = progressWidth
        paint.style = if (progressStyle == 0) Paint.Style.FILL else Paint.Style.STROKE

        textPaint.textSize = textSize
        textPaint.textAlign = Paint.Align.CENTER
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val centerX = width / 2f
        val centerY = height / 2f
        val radius = minOf(width, height) / 2f - progressWidth

        // Рисуем фоновый круг
        paint.color = bgColor
        canvas.drawCircle(centerX, centerY, radius, paint)

        // Рисуем дугу прогресса
        paint.color = progressColor
        val sweepAngle = (progress / 100f) * 360f
        canvas.drawArc(
            centerX - radius,
            centerY - radius,
            centerX + radius,
            centerY + radius,
            -90f,
            sweepAngle,
            progressStyle == 0,
            paint
        )

        // Рисуем процентный текст
        if (showPercentage) {
            textPaint.color = Color.BLACK
            val text = "$progress%"
            val yPos = centerY - (textPaint.descent() + textPaint.ascent()) / 2
            canvas.drawText(text, centerX, yPos, textPaint)
        }
    }

    // Публичные сеттеры
    fun setProgress(value: Int) {
        progress = value.coerceIn(0, 100)
        invalidate()
    }
}
```

### 3. Использование В XML Layout

```xml
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center">

    <!-- Использование кастомных атрибутов -->
    <com.example.CircularProgressView
        android:id="@+id/progressView"
        android:layout_width="200dp"
        android:layout_height="200dp"
        app:progress="75"
        app:progressColor="@color/purple_500"
        app:backgroundColor="@color/gray_200"
        app:progressWidth="12dp"
        app:textSize="24sp"
        app:showPercentage="true"
        app:progressStyle="filled" />

</LinearLayout>
```

### 4. Различные Форматы Атрибутов

```xml
<!-- res/values/attrs.xml -->
<resources>
    <declare-styleable name="CustomView">
        <!-- String -->
        <attr name="customText" format="string" />

        <!-- Integer -->
        <attr name="customCount" format="integer" />

        <!-- Float -->
        <attr name="customRatio" format="float" />

        <!-- Boolean -->
        <attr name="isEnabled" format="boolean" />

        <!-- Color -->
        <attr name="customColor" format="color" />

        <!-- Dimension (dp, sp, px) -->
        <attr name="customSize" format="dimension" />

        <!-- Reference (drawable, color, string resource) -->
        <attr name="customIcon" format="reference" />

        <!-- Enum -->
        <attr name="alignment" format="enum">
            <enum name="left" value="0" />
            <enum name="center" value="1" />
            <enum name="right" value="2" />
        </attr>

        <!-- Flags (можно комбинировать несколько) -->
        <attr name="gravity" format="flags">
            <flag name="top" value="0x01" />
            <flag name="bottom" value="0x02" />
            <flag name="left" value="0x04" />
            <flag name="right" value="0x08" />
        </attr>

        <!-- Множественные форматы -->
        <attr name="customValue" format="integer|reference" />
    </declare-styleable>
</resources>
```

### 5. Чтение Различных Типов Атрибутов

```kotlin
class AdvancedCustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    init {
        val ta = context.obtainStyledAttributes(attrs, R.styleable.CustomView)

        try {
            // String
            val text = ta.getString(R.styleable.CustomView_customText) ?: "Default"

            // Integer
            val count = ta.getInt(R.styleable.CustomView_customCount, 0)

            // Float
            val ratio = ta.getFloat(R.styleable.CustomView_customRatio, 1.0f)

            // Boolean
            val enabled = ta.getBoolean(R.styleable.CustomView_isEnabled, true)

            // Color
            val color = ta.getColor(R.styleable.CustomView_customColor, Color.BLACK)

            // Dimension (возвращает пиксели)
            val size = ta.getDimension(R.styleable.CustomView_customSize, 0f)

            // Dimension (возвращает смещение в пикселях для целых чисел)
            val sizePixels = ta.getDimensionPixelSize(R.styleable.CustomView_customSize, 0)

            // Reference (drawable)
            val icon = ta.getDrawable(R.styleable.CustomView_customIcon)

            // Reference (resource ID)
            val iconResId = ta.getResourceId(R.styleable.CustomView_customIcon, 0)

            // Enum
            val alignment = ta.getInt(R.styleable.CustomView_alignment, 0)

            // Flags
            val gravity = ta.getInt(R.styleable.CustomView_gravity, 0)
            val hasTop = (gravity and 0x01) != 0
            val hasBottom = (gravity and 0x02) != 0

        } finally {
            ta.recycle()
        }
    }
}
```

### 6. Программное Использование

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val progressView = findViewById<CircularProgressView>(R.id.progressView)

        // Изменение атрибутов программно
        progressView.setProgress(85)

        // Анимация прогресса
        ValueAnimator.ofInt(0, 100).apply {
            duration = 2000
            addUpdateListener { animation ->
                progressView.setProgress(animation.animatedValue as Int)
            }
            start()
        }
    }
}
```

### 7. Использование Атрибутов Темы

```xml
<!-- Определение в themes.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.DayNight">
    <item name="progressColor">@color/primary</item>
    <item name="backgroundColor">@color/surface</item>
</style>

<!-- Ссылка на атрибут темы в attrs.xml -->
<declare-styleable name="CircularProgressView">
    <attr name="progressColor" format="color" />
    <attr name="backgroundColor" format="color" />
</declare-styleable>

<!-- Использование в custom view -->
<com.example.CircularProgressView
    android:layout_width="200dp"
    android:layout_height="200dp"
    app:progressColor="?attr/colorPrimary"
    app:backgroundColor="?attr/colorSurface" />
```

### 8. Переиспользование Системных Атрибутов

```xml
<!-- Переиспользование встроенных атрибутов Android -->
<declare-styleable name="CustomButton">
    <attr name="android:text" />
    <attr name="android:textColor" />
    <attr name="android:textSize" />
    <attr name="customIcon" format="reference" />
</declare-styleable>
```

```kotlin
class CustomButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : androidx.appcompat.widget.AppCompatButton(context, attrs) {

    init {
        val ta = context.obtainStyledAttributes(attrs, R.styleable.CustomButton)

        try {
            // Чтение встроенных атрибутов Android
            val text = ta.getString(R.styleable.CustomButton_android_text)
            val textColor = ta.getColor(
                R.styleable.CustomButton_android_textColor,
                Color.BLACK
            )

            // Чтение кастомного атрибута
            val icon = ta.getDrawable(R.styleable.CustomButton_customIcon)

            // Применение
            this.text = text
            this.setTextColor(textColor)
            setCompoundDrawablesWithIntrinsicBounds(icon, null, null, null)

        } finally {
            ta.recycle()
        }
    }
}
```

### Лучшие Практики

1. - **Всегда переработайте TypedArray** с помощью `typedArray.recycle()`
2. - **Предоставляйте значения по умолчанию** для всех атрибутов
3. - **Используйте подходящий формат** для каждого типа атрибута
4. - **Документируйте атрибуты** с помощью комментариев в attrs.xml
5. - **Группируйте связанные атрибуты** в одном styleable
6. - **Поддерживайте атрибуты темы** для согласованности
7. - **Валидируйте значения атрибутов** (например, прогресс 0-100)

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-testing-viewmodels-turbine--android--medium]] - View
- q-rxjava-pagination-recyclerview--android--medium - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - View

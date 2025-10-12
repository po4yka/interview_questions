---
tags:
  - programming-languages
difficulty: medium
status: draft
---

# Как добавить кастомные атрибуты у кастомного view?

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

# Как добавить кастомные атрибуты у кастомного view

## Ответ (RU)
Чтобы добавить кастомные атрибуты в Custom View нужно создать attrs.xml и описать атрибуты добавить их в styleable и получить в Custom View использовать атрибуты в XML или Kotlin

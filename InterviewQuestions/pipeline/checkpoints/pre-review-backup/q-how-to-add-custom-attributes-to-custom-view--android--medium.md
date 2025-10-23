---
id: 20251012-1227165
title: "How To Add Custom Attributes To Custom View / Как добавить кастомные атрибуты к кастомным View"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags:
  - android
moc: moc-android
related: [q-service-restrictions-why--android--medium, q-what-is-the-difference-between-fragmentmanager-and-fragmenttransaction--android--medium, q-presenter-notify-view--android--medium]
  - q-recyclerview-sethasfixedsize--android--easy
  - q-viewmodel-pattern--android--easy
  - q-what-is-known-about-methods-that-redraw-view--android--medium
  - q-testing-viewmodels-turbine--testing--medium
  - q-rxjava-pagination-recyclerview--android--medium
  - q-what-is-viewmodel--android--medium
  - q-how-to-create-list-like-recyclerview-in-compose--android--medium
  - q-compose-custom-layout--jetpack-compose--hard
---
# How to add custom attributes to custom view?

## EN (expanded)

To add custom attributes to a Custom View, you need to:
1. Define attributes in `attrs.xml`
2. Read attributes in the custom view constructor
3. Use attributes in XML layouts

### Step 1: Define Attributes in attrs.xml

Create or edit `res/values/attrs.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <declare-styleable name="CustomButton">
        <!-- String attribute -->
        <attr name="customText" format="string" />

        <!-- Color attribute -->
        <attr name="customTextColor" format="color" />

        <!-- Dimension attribute -->
        <attr name="customTextSize" format="dimension" />

        <!-- Boolean attribute -->
        <attr name="isRounded" format="boolean" />

        <!-- Integer attribute -->
        <attr name="cornerRadius" format="dimension" />

        <!-- Enum attribute -->
        <attr name="buttonStyle" format="enum">
            <enum name="primary" value="0" />
            <enum name="secondary" value="1" />
            <enum name="outlined" value="2" />
        </attr>

        <!-- Reference attribute (drawable, color, etc.) -->
        <attr name="customIcon" format="reference" />

        <!-- Multiple formats -->
        <attr name="customSize" format="dimension|fraction" />
    </declare-styleable>
</resources>
```

### Step 2: Read Attributes in Custom View

```kotlin
class CustomButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : AppCompatButton(context, attrs, defStyleAttr) {

    private var customText: String = ""
    private var customTextColor: Int = Color.BLACK
    private var customTextSize: Float = 16f
    private var isRounded: Boolean = false
    private var cornerRadius: Float = 0f
    private var buttonStyle: Int = 0
    private var customIcon: Drawable? = null

    init {
        // Read attributes
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.CustomButton,
            defStyleAttr,
            0
        ).apply {
            try {
                // Read string
                customText = getString(R.styleable.CustomButton_customText) ?: ""

                // Read color
                customTextColor = getColor(
                    R.styleable.CustomButton_customTextColor,
                    Color.BLACK
                )

                // Read dimension
                customTextSize = getDimension(
                    R.styleable.CustomButton_customTextSize,
                    16f
                )

                // Read boolean
                isRounded = getBoolean(
                    R.styleable.CustomButton_isRounded,
                    false
                )

                // Read dimension (corner radius)
                cornerRadius = getDimension(
                    R.styleable.CustomButton_cornerRadius,
                    0f
                )

                // Read enum
                buttonStyle = getInt(
                    R.styleable.CustomButton_buttonStyle,
                    0
                )

                // Read drawable reference
                customIcon = getDrawable(R.styleable.CustomButton_customIcon)

            } finally {
                recycle() // Important: recycle the TypedArray
            }
        }

        // Apply attributes
        applyAttributes()
    }

    private fun applyAttributes() {
        text = customText
        setTextColor(customTextColor)
        textSize = customTextSize

        if (isRounded) {
            background = createRoundedBackground()
        }

        customIcon?.let {
            setCompoundDrawablesWithIntrinsicBounds(it, null, null, null)
        }

        applyButtonStyle()
    }

    private fun createRoundedBackground(): Drawable {
        return GradientDrawable().apply {
            shape = GradientDrawable.RECTANGLE
            cornerRadii = floatArrayOf(
                cornerRadius, cornerRadius,
                cornerRadius, cornerRadius,
                cornerRadius, cornerRadius,
                cornerRadius, cornerRadius
            )
            setColor(Color.parseColor("#2196F3"))
        }
    }

    private fun applyButtonStyle() {
        when (buttonStyle) {
            0 -> applyPrimaryStyle()
            1 -> applySecondaryStyle()
            2 -> applyOutlinedStyle()
        }
    }

    private fun applyPrimaryStyle() {
        setBackgroundColor(Color.parseColor("#2196F3"))
        setTextColor(Color.WHITE)
    }

    private fun applySecondaryStyle() {
        setBackgroundColor(Color.parseColor("#E0E0E0"))
        setTextColor(Color.BLACK)
    }

    private fun applyOutlinedStyle() {
        background = GradientDrawable().apply {
            shape = GradientDrawable.RECTANGLE
            setStroke(2, Color.parseColor("#2196F3"))
            setColor(Color.TRANSPARENT)
        }
        setTextColor(Color.parseColor("#2196F3"))
    }
}
```

### Step 3: Use in XML Layout

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <!-- Using custom attributes -->
    <com.example.app.CustomButton
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:customText="Click Me"
        app:customTextColor="@color/white"
        app:customTextSize="18sp"
        app:isRounded="true"
        app:cornerRadius="8dp"
        app:buttonStyle="primary"
        app:customIcon="@drawable/ic_star" />

    <com.example.app.CustomButton
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        app:customText="Secondary"
        app:buttonStyle="secondary"
        app:isRounded="true"
        app:cornerRadius="12dp" />

    <com.example.app.CustomButton
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        app:customText="Outlined"
        app:buttonStyle="outlined"
        app:isRounded="true"
        app:cornerRadius="16dp" />

</LinearLayout>
```

### Complete Example: Custom CircleImageView

#### attrs.xml

```xml
<resources>
    <declare-styleable name="CircleImageView">
        <attr name="borderWidth" format="dimension" />
        <attr name="borderColor" format="color" />
        <attr name="imageSource" format="reference" />
    </declare-styleable>
</resources>
```

#### CircleImageView.kt

```kotlin
class CircleImageView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : AppCompatImageView(context, attrs, defStyleAttr) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val borderPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var borderWidth: Float = 0f
    private var borderColor: Int = Color.WHITE

    init {
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.CircleImageView,
            defStyleAttr,
            0
        ).apply {
            try {
                borderWidth = getDimension(
                    R.styleable.CircleImageView_borderWidth,
                    0f
                )

                borderColor = getColor(
                    R.styleable.CircleImageView_borderColor,
                    Color.WHITE
                )

                getResourceId(R.styleable.CircleImageView_imageSource, 0).let {
                    if (it != 0) setImageResource(it)
                }

            } finally {
                recycle()
            }
        }

        borderPaint.apply {
            style = Paint.Style.STROKE
            strokeWidth = borderWidth
            color = borderColor
        }

        scaleType = ScaleType.CENTER_CROP
    }

    override fun onDraw(canvas: Canvas) {
        val drawable = drawable ?: return

        val bitmap = drawableToBitmap(drawable)
        val circularBitmap = getCircularBitmap(bitmap)

        canvas.drawBitmap(circularBitmap, 0f, 0f, paint)

        // Draw border
        if (borderWidth > 0) {
            val radius = (width / 2f) - (borderWidth / 2f)
            canvas.drawCircle(
                width / 2f,
                height / 2f,
                radius,
                borderPaint
            )
        }
    }

    private fun drawableToBitmap(drawable: Drawable): Bitmap {
        if (drawable is BitmapDrawable) {
            return drawable.bitmap
        }

        val bitmap = Bitmap.createBitmap(
            width,
            height,
            Bitmap.Config.ARGB_8888
        )
        val canvas = Canvas(bitmap)
        drawable.setBounds(0, 0, width, height)
        drawable.draw(canvas)
        return bitmap
    }

    private fun getCircularBitmap(bitmap: Bitmap): Bitmap {
        val size = Math.min(width, height)
        val output = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(output)

        val paint = Paint(Paint.ANTI_ALIAS_FLAG)
        val rect = Rect(0, 0, size, size)

        canvas.drawCircle(
            size / 2f,
            size / 2f,
            size / 2f,
            paint
        )

        paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN)
        canvas.drawBitmap(bitmap, null, rect, paint)

        return output
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
        val size = Math.min(measuredWidth, measuredHeight)
        setMeasuredDimension(size, size)
    }
}
```

#### Usage in XML

```xml
<com.example.app.CircleImageView
    android:layout_width="120dp"
    android:layout_height="120dp"
    app:imageSource="@drawable/profile_photo"
    app:borderWidth="4dp"
    app:borderColor="@color/primary" />
```

### Attribute Formats

| Format | Description | Example |
|--------|-------------|---------|
| `string` | Text value | "Hello" |
| `color` | Color value | #FF0000 |
| `dimension` | Size value | 16dp, 24sp |
| `boolean` | True/false | true |
| `integer` | Whole number | 5 |
| `float` | Decimal number | 1.5 |
| `fraction` | Percentage | 50% |
| `enum` | Enumeration | primary/secondary |
| `flag` | Bit flags | left\|right |
| `reference` | Resource reference | @drawable/icon |

### Multiple Formats

```xml
<attr name="customSize" format="dimension|fraction" />
<attr name="customBackground" format="color|reference" />
```

### Programmatic Access

```kotlin
// Get custom attribute value at runtime
fun getCustomAttribute() {
    val typedValue = TypedValue()
    context.theme.resolveAttribute(
        R.attr.customAttribute,
        typedValue,
        true
    )
    val value = typedValue.data
}
```

### Setting Attributes Programmatically

```kotlin
// In custom view
fun setCustomText(text: String) {
    customText = text
    this.text = text
    invalidate() // Redraw if needed
}

fun setCustomTextColor(color: Int) {
    customTextColor = color
    setTextColor(color)
}
```

---

## RU (original)
Добавление кастомных атрибутов к custom view позволяет конфигурировать view через XML layout файлы.

**Шаг 1: Объявить атрибуты в attrs.xml:**

```xml
<!-- res/values/attrs.xml -->
<resources>
    <declare-styleable name="CustomButton">
        <attr name="buttonColor" format="color" />
        <attr name="buttonText" format="string" />
        <attr name="buttonSize" format="dimension" />
        <attr name="buttonStyle" format="enum">
            <enum name="normal" value="0" />
            <enum name="rounded" value="1" />
            <enum name="circular" value="2" />
        </attr>
        <attr name="isEnabled" format="boolean" />
    </declare-styleable>
</resources>
```

**Шаг 2: Использовать в Custom View:**

```kotlin
class CustomButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var buttonColor: Int = Color.BLUE
    private var buttonText: String = ""
    private var buttonSize: Float = 50f
    private var buttonStyle: Int = 0
    private var isButtonEnabled: Boolean = true

    init {
        // Получить атрибуты
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.CustomButton,
            0, 0
        ).apply {
            try {
                buttonColor = getColor(
                    R.styleable.CustomButton_buttonColor,
                    Color.BLUE
                )
                buttonText = getString(
                    R.styleable.CustomButton_buttonText
                ) ?: ""
                buttonSize = getDimension(
                    R.styleable.CustomButton_buttonSize,
                    50f
                )
                buttonStyle = getInt(
                    R.styleable.CustomButton_buttonStyle,
                    0
                )
                isButtonEnabled = getBoolean(
                    R.styleable.CustomButton_isEnabled,
                    true
                )
            } finally {
                recycle() // ВАЖНО: освободить ресурсы
            }
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Использовать атрибуты для рисования
        paint.color = buttonColor
        // ...
    }
}
```

**Шаг 3: Использовать в XML:**

```xml
<com.example.CustomButton
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:buttonColor="@color/red"
    app:buttonText="Click Me"
    app:buttonSize="24sp"
    app:buttonStyle="rounded"
    app:isEnabled="true" />
```

**Форматы атрибутов:**

- `color` - цвет
- `string` - текст
- `dimension` - размер (dp, sp, px)
- `integer` - целое число
- `float` - дробное число
- `boolean` - true/false
- `reference` - ссылка на ресурс (@drawable, @string и т.д.)
- `enum` - перечисление
- `flag` - флаги (можно комбинировать)

**Пример с flags:**

```xml
<attr name="textStyle" format="flag">
    <flag name="normal" value="0" />
    <flag name="bold" value="1" />
    <flag name="italic" value="2" />
</attr>

<!-- Использование -->
app:textStyle="bold|italic"
```

**Best Practices:**

1. ✅ Всегда вызывайте `recycle()` на TypedArray
2. ✅ Предоставляйте значения по умолчанию
3. ✅ Используйте `@JvmOverloads` для всех конструкторов
4. ✅ Группируйте связанные атрибуты в одном `declare-styleable`
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
- [[q-compose-custom-layout--android--hard]] - View

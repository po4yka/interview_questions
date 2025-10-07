---
topic: android
tags:
  - px
  - dp
  - sp
  - android
  - ui
  - measurement-units
difficulty: medium
status: draft
---

# What are px dp sp?

## Question (RU)

Что такое px dp sp

## Answer

Android uses three main measurement units for defining UI dimensions: **px** (pixels), **dp** (density-independent pixels), and **sp** (scale-independent pixels). Understanding these units is crucial for creating layouts that work across different screen sizes and densities.

### 1. px (Pixels)

Physical screen points - the actual pixels on the device screen.

```kotlin
// Setting dimensions in pixels (NOT recommended for most UI)
val textView = TextView(context).apply {
    layoutParams = LinearLayout.LayoutParams(
        200, // 200 pixels width
        100  // 100 pixels height
    )
}

// In XML
<TextView
    android:layout_width="200px"
    android:layout_height="100px" />
```

**Problems with px:**
- Looks different on different screen densities
- A 100px view appears much smaller on high-density screens
- Not recommended for UI dimensions

```kotlin
// Example showing px inconsistency
class PixelDemoActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val density = resources.displayMetrics.density
        Log.d("Density", "Screen density: $density")

        // 100px will look different on different devices
        // On mdpi (density=1.0): 100px = 100px
        // On hdpi (density=1.5): 100px = 67dp equivalent
        // On xhdpi (density=2.0): 100px = 50dp equivalent
        // On xxhdpi (density=3.0): 100px = 33dp equivalent
    }
}
```

### 2. dp (Density-Independent Pixels)

Abstract measurement unit that adapts to screen density. **Recommended for all UI sizes.**

```kotlin
// Setting dimensions in dp (RECOMMENDED)
val textView = TextView(context).apply {
    val widthInDp = 200
    val heightInDp = 100

    val widthInPx = (widthInDp * resources.displayMetrics.density).toInt()
    val heightInPx = (heightInDp * resources.displayMetrics.density).toInt()

    layoutParams = LinearLayout.LayoutParams(widthInPx, heightInPx)
}

// In XML (most common)
<TextView
    android:layout_width="200dp"
    android:layout_height="100dp" />
```

**Why use dp:**
- Consistent visual size across all devices
- 1dp = 1px on mdpi (160dpi) screens
- Automatically scales with screen density

```kotlin
// DP conversion utilities
fun Int.dpToPx(context: Context): Int {
    return (this * context.resources.displayMetrics.density).toInt()
}

fun Float.dpToPx(context: Context): Float {
    return this * context.resources.displayMetrics.density
}

fun Int.pxToDp(context: Context): Int {
    return (this / context.resources.displayMetrics.density).toInt()
}

// Usage
val marginInDp = 16
val marginInPx = marginInDp.dpToPx(context)

view.setPadding(16.dpToPx(context), 16.dpToPx(context), 16.dpToPx(context), 16.dpToPx(context))
```

### 3. sp (Scale-Independent Pixels)

Scalable pixels for text - accounts for user font settings. **Used only for text sizes.**

```kotlin
// Setting text size in sp (RECOMMENDED for text)
val textView = TextView(context).apply {
    setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
}

// In XML
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:textSize="16sp" />
```

**Why use sp for text:**
- Respects user's font size preferences
- Accessibility-friendly
- Scales with system font settings

```kotlin
// SP conversion utilities
fun Float.spToPx(context: Context): Float {
    return TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_SP,
        this,
        context.resources.displayMetrics
    )
}

// Example: User changes system font size
class FontSizeDemo : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val textView = TextView(this).apply {
            text = "Hello World"
            // If user sets font size to "Large" in system settings,
            // this text will automatically become larger
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
        }

        // DON'T use dp for text size!
        // This would ignore user preferences:
        // setTextSize(TypedValue.COMPLEX_UNIT_DIP, 16f) // WRONG!
    }
}
```

### Density Conversion Table

| Density | Scale | Example |
|---------|-------|---------|
| ldpi | 0.75x | 1dp = 0.75px |
| mdpi (baseline) | 1.0x | 1dp = 1px |
| hdpi | 1.5x | 1dp = 1.5px |
| xhdpi | 2.0x | 1dp = 2px |
| xxhdpi | 3.0x | 1dp = 3px |
| xxxhdpi | 4.0x | 1dp = 4px |

### Practical Examples

#### Example 1: Layout with Proper Units

```xml
<!-- Good example using dp and sp -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:padding="16dp"
    android:orientation="vertical">

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Title"
        android:textSize="24sp"
        android:layout_marginBottom="8dp" />

    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Description"
        android:textSize="14sp" />

    <Button
        android:layout_width="match_parent"
        android:layout_height="48dp"
        android:layout_marginTop="16dp"
        android:text="Click Me"
        android:textSize="16sp" />
</LinearLayout>
```

#### Example 2: Programmatic Dimension Handling

```kotlin
class DimensionUtils(private val context: Context) {

    private val displayMetrics = context.resources.displayMetrics

    // Convert dp to pixels
    fun dpToPx(dp: Int): Int {
        return (dp * displayMetrics.density).toInt()
    }

    fun dpToPx(dp: Float): Float {
        return dp * displayMetrics.density
    }

    // Convert pixels to dp
    fun pxToDp(px: Int): Int {
        return (px / displayMetrics.density).toInt()
    }

    // Convert sp to pixels
    fun spToPx(sp: Float): Float {
        return TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_SP,
            sp,
            displayMetrics
        )
    }

    // Get screen density info
    fun getDensityInfo(): String {
        return """
            Density: ${displayMetrics.density}
            DPI: ${displayMetrics.densityDpi}
            Scaled Density: ${displayMetrics.scaledDensity}
            Width: ${displayMetrics.widthPixels}px
            Height: ${displayMetrics.heightPixels}px
        """.trimIndent()
    }
}

// Usage
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val utils = DimensionUtils(this)

        val button = Button(this).apply {
            // Set margin in dp
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                utils.dpToPx(48) // 48dp height
            ).apply {
                setMargins(
                    utils.dpToPx(16), // left: 16dp
                    utils.dpToPx(8),  // top: 8dp
                    utils.dpToPx(16), // right: 16dp
                    utils.dpToPx(8)   // bottom: 8dp
                )
            }
            layoutParams = params

            // Set text size in sp
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
        }

        Log.d("Density", utils.getDensityInfo())
    }
}
```

#### Example 3: Extension Functions

```kotlin
// Extension functions for easy conversion
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt()

val Float.dp: Float
    get() = this * Resources.getSystem().displayMetrics.density

val Int.sp: Float
    get() = TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_SP,
        this.toFloat(),
        Resources.getSystem().displayMetrics
    )

// Usage - much cleaner!
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val view = View(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                100.dp,  // 100dp width
                50.dp    // 50dp height
            )
            setPadding(16.dp, 16.dp, 16.dp, 16.dp)
        }

        val textView = TextView(this).apply {
            setTextSize(TypedValue.COMPLEX_UNIT_PX, 16.sp) // 16sp
        }
    }
}
```

#### Example 4: Jetpack Compose

```kotlin
@Composable
fun DimensionsInCompose() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp) // dp in Compose
    ) {
        Text(
            text = "Title",
            fontSize = 24.sp, // sp for text size
            modifier = Modifier.padding(bottom = 8.dp)
        )

        Text(
            text = "Description",
            fontSize = 14.sp
        )

        Button(
            onClick = { },
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp) // dp for UI dimensions
                .padding(top = 16.dp)
        ) {
            Text(
                text = "Click Me",
                fontSize = 16.sp // sp for text
            )
        }
    }
}
```

### Best Practices

| Unit | Use For | Don't Use For |
|------|---------|---------------|
| **dp** | View dimensions, margins, padding, icon sizes | Text size |
| **sp** | Text size only | View dimensions |
| **px** | Rare cases (drawing, canvas) | Any UI elements |

### Common Mistakes to Avoid

```kotlin
// ❌ WRONG - Using px for UI
<TextView
    android:layout_width="200px"
    android:textSize="16px" />

// ❌ WRONG - Using dp for text size
<TextView
    android:textSize="16dp" />

// ❌ WRONG - Hardcoded pixels in code
textView.textSize = 16f // This is px, not sp!

// ✅ CORRECT - Using dp for layout, sp for text
<TextView
    android:layout_width="200dp"
    android:layout_height="50dp"
    android:padding="16dp"
    android:textSize="16sp" />

// ✅ CORRECT - Proper units in code
textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
```

### Summary

- **px** - Physical pixels, avoid for UI (looks different on different screens)
- **dp** - Density-independent pixels, use for all UI dimensions (consistent across devices)
- **sp** - Scale-independent pixels, use ONLY for text size (respects user font settings)
- Always use **dp** for layouts and **sp** for text to ensure proper scaling and accessibility

## Answer (RU)

px (пиксели) – физические точки экрана. dp (density-independent pixels) – абстрактная единица измерения, которая адаптируется под плотность экрана. sp (scale-independent pixels) – масштабируемые пиксели для текста. px не зависит от плотности экрана, dp адаптируется под плотность экрана для UI размеров, sp учитывает настройки шрифта пользователя и используется только для текста. Примеры использования в XML и Kotlin приведены.

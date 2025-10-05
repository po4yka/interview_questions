---
tags:
  - dp
  - density-independent pixels
  - easy_kotlin
  - android
  - ui
difficulty: easy
---

# Что такое dp?

**English**: What is dp?

## Answer

### Definition

**dp** stands for **density-independent pixels**. It's a virtual unit of measurement that ensures consistent visual size of UI elements across screens with different pixel densities.

### Why dp Matters

Android devices come in various screen sizes and pixel densities (DPI - dots per inch). Without density-independent units, a UI element sized in pixels would appear:
- Very small on high-density screens (e.g., 480 DPI)
- Very large on low-density screens (e.g., 120 DPI)

### How dp Works

The relationship between dp and physical pixels depends on screen density:

```
pixels = dp × (screen density / 160)
```

**Density buckets:**
- **ldpi** (low): ~120 DPI → 1dp = 0.75 pixels
- **mdpi** (medium): ~160 DPI → 1dp = 1 pixel (baseline)
- **hdpi** (high): ~240 DPI → 1dp = 1.5 pixels
- **xhdpi** (extra-high): ~320 DPI → 1dp = 2 pixels
- **xxhdpi**: ~480 DPI → 1dp = 3 pixels
- **xxxhdpi**: ~640 DPI → 1dp = 4 pixels

### Example

A button sized at **48dp × 48dp** will:
- Appear as 48×48 physical pixels on mdpi (160 DPI)
- Appear as 96×96 physical pixels on xhdpi (320 DPI)
- Appear as 144×144 physical pixels on xxhdpi (480 DPI)

But the **physical size** (in inches/millimeters) on the screen will be approximately the same across all devices.

### Using dp in XML

```xml
<Button
    android:id="@+id/myButton"
    android:layout_width="120dp"
    android:layout_height="48dp"
    android:padding="16dp"
    android:layout_margin="8dp"
    android:text="Click Me" />

<ImageView
    android:layout_width="64dp"
    android:layout_height="64dp"
    android:src="@drawable/icon" />
```

### Converting dp to Pixels in Code

```kotlin
fun dpToPx(dp: Float, context: Context): Int {
    val density = context.resources.displayMetrics.density
    return (dp * density).roundToInt()
}

fun pxToDp(px: Float, context: Context): Int {
    val density = context.resources.displayMetrics.density
    return (px / density).roundToInt()
}

// Usage
val widthInDp = 48f
val widthInPx = dpToPx(widthInDp, context)
```

### Extension Functions

```kotlin
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt()

val Float.dp: Float
    get() = this * Resources.getSystem().displayMetrics.density

// Usage
val size = 48.dp  // Converts 48dp to pixels
```

### Best Practices

1. **Always use dp** for layout dimensions, margins, padding, and UI element sizes
2. **Never use px** (pixels) directly in layouts - they won't scale
3. Use **sp** specifically for text sizes (it respects user font preferences)
4. Design for the **mdpi baseline** (160 DPI) where 1dp = 1px

### Common Sizes

```xml
<!-- Material Design common sizes in dp -->
<!-- Touch target minimum: 48dp × 48dp -->
<Button
    android:layout_width="wrap_content"
    android:layout_height="48dp"
    android:minWidth="88dp" />

<!-- Standard margins and padding -->
android:padding="16dp"     <!-- Standard padding -->
android:padding="8dp"      <!-- Small padding -->
android:padding="24dp"     <!-- Large padding -->

<!-- Icon sizes -->
android:layout_width="24dp"  <!-- Small icon -->
android:layout_width="48dp"  <!-- Standard icon -->
android:layout_width="64dp"  <!-- Large icon -->
```

### Why Use dp?

Using dp ensures:
- **Consistent UI** across devices with different screen densities
- **Proper scaling** on tablets, phones, and other form factors
- **Predictable layout** that matches your design specifications
- **Better user experience** with appropriately sized touch targets

## Ответ

dp означает density-independent pixels или пиксели не зависящие от плотности Это виртуальная единица измерения которая используется для обеспечения одинакового визуального размера элементов пользовательского интерфейса на экранах с различной плотностью пикселей Это важно поскольку устройства Android могут иметь различные размеры и разрешения экранов и использование dp помогает создать консистентный пользовательский интерфейс на всех этих устройствах


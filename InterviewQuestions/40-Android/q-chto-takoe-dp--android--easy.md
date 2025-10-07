---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# What is dp?

## EN (expanded)

### Definition

**dp** (Density-independent Pixels), also called **dip**, is a unit of measurement in Android used to create adaptive interfaces that look consistent across devices with different screen densities.

### Why dp Exists

Different devices have different screen pixel densities:

```
Low-end phone:    480 × 800 pixels, 4" screen  = 233 dpi
Mid-range phone:  1080 × 1920 pixels, 5" screen = 441 dpi
High-end phone:   1440 × 2560 pixels, 5.5" screen = 534 dpi
Tablet:           2048 × 1536 pixels, 10" screen = 264 dpi
```

**Problem**: If you use pixels (px), UI elements will be different physical sizes on different devices.

**Solution**: Use density-independent pixels (dp) that automatically scale.

### How dp Works

The conversion formula:

```
pixels = dp × (device dpi / 160)
```

**Example**: 100dp on different devices
- mdpi (160dpi): 100dp = 100px
- hdpi (240dpi): 100dp = 150px
- xhdpi (320dpi): 100dp = 200px
- xxhdpi (480dpi): 100dp = 300px

### Visual Comparison

```
┌─────────────────────────────────┐
│     Same Physical Size          │
├─────────────────────────────────┤
│ ldpi:   75px  (100dp)          │
│ mdpi:   100px (100dp)          │
│ hdpi:   150px (100dp)          │
│ xhdpi:  200px (100dp)          │
│ xxhdpi: 300px (100dp)          │
└─────────────────────────────────┘
```

### Density Buckets

Android defines standard density buckets:

| Density | DPI | Scale Factor | Folder |
|---------|-----|--------------|--------|
| ldpi | ~120dpi | 0.75 | drawable-ldpi |
| mdpi | ~160dpi | 1.0 (baseline) | drawable-mdpi |
| hdpi | ~240dpi | 1.5 | drawable-hdpi |
| xhdpi | ~320dpi | 2.0 | drawable-xhdpi |
| xxhdpi | ~480dpi | 3.0 | drawable-xxhdpi |
| xxxhdpi | ~640dpi | 4.0 | drawable-xxxhdpi |

### XML Usage

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:padding="16dp"
    android:orientation="vertical">

    <!-- Button with consistent size across devices -->
    <Button
        android:layout_width="200dp"
        android:layout_height="48dp"
        android:text="Submit" />

    <!-- Icon with standard size -->
    <ImageView
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:src="@drawable/ic_icon"
        android:layout_marginTop="8dp" />

    <!-- Divider -->
    <View
        android:layout_width="match_parent"
        android:layout_height="1dp"
        android:background="@color/divider"
        android:layout_marginVertical="16dp" />

</LinearLayout>
```

### Jetpack Compose Usage

```kotlin
@Composable
fun DpExample() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp) // Use .dp extension
    ) {
        // Button with consistent size
        Button(
            onClick = { },
            modifier = Modifier
                .width(200.dp)
                .height(48.dp)
        ) {
            Text("Submit")
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Icon with standard size
        Icon(
            imageVector = Icons.Default.Star,
            contentDescription = "Star",
            modifier = Modifier.size(24.dp)
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Divider
        Divider(
            thickness = 1.dp,
            color = Color.Gray
        )
    }
}
```

### Converting Between dp and px

#### In Code (View System)

```kotlin
// Get density
val density = resources.displayMetrics.density

// Convert dp to px
fun dpToPx(dp: Int): Int {
    return (dp * density).toInt()
}

// Convert px to dp
fun pxToDp(px: Int): Int {
    return (px / density).toInt()
}

// Usage
val buttonWidthPx = dpToPx(200) // 200dp → pixels
```

#### Extension Functions

```kotlin
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt()

val Int.px: Int
    get() = (this / Resources.getSystem().displayMetrics.density).toInt()

// Usage
val width = 100.dp  // 100dp converted to pixels
val dpValue = 150.px // 150px converted to dp
```

#### In Compose

```kotlin
@Composable
fun DpConversion() {
    val density = LocalDensity.current

    // Convert dp to px
    val widthPx = with(density) { 100.dp.toPx() }

    // Convert px to dp
    val widthDp = with(density) { 150.toDp() }
}
```

### Common dp Values

#### Material Design Spacing

```kotlin
// Margins and padding
4.dp   // Extra small spacing
8.dp   // Small spacing
12.dp  // Medium-small spacing
16.dp  // Standard spacing (most common)
24.dp  // Large spacing
32.dp  // Extra large spacing
48.dp  // XXL spacing
```

#### Component Sizes

```kotlin
// Touch target sizes
48.dp  // Minimum touch target (Material Design)
56.dp  // FAB size
64.dp  // Large touch target

// Icon sizes
16.dp  // Small icon
24.dp  // Standard icon
32.dp  // Large icon
48.dp  // Extra large icon

// Other
1.dp   // Thin divider
2.dp   // Medium divider
56.dp  // App bar height
72.dp  // List item height
```

### Practical Examples

#### Card Layout

```kotlin
@Composable
fun ProductCard() {
    Card(
        modifier = Modifier
            .width(160.dp)
            .padding(8.dp),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Image(
                painter = painterResource(R.drawable.product),
                contentDescription = null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(120.dp)
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Product Name",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = "$19.99",
                fontSize = 14.sp,
                color = Color.Gray
            )
        }
    }
}
```

#### Responsive Layout

```kotlin
@Composable
fun ResponsiveLayout() {
    val configuration = LocalConfiguration.current
    val screenWidthDp = configuration.screenWidthDp.dp

    // Adjust padding based on screen width
    val horizontalPadding = when {
        screenWidthDp < 360.dp -> 8.dp
        screenWidthDp < 600.dp -> 16.dp
        else -> 24.dp
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = horizontalPadding)
    ) {
        // Content
    }
}
```

### dp vs px vs sp

| Use Case | Unit | Example |
|----------|------|---------|
| Layout dimensions | dp | `width = 100.dp` |
| Margins/Padding | dp | `padding(16.dp)` |
| Border thickness | dp | `border(1.dp)` |
| Icon sizes | dp | `size(24.dp)` |
| **Text size** | **sp** | `fontSize = 16.sp` |
| Drawing (rare) | px | Canvas operations |

### Best Practices

1. **Always use dp** for layout dimensions
2. **Never use px** for UI elements (except rare canvas drawing)
3. **Use sp** for text sizes (not dp)
4. **Follow Material Design** guidelines for standard sizes
5. **Test on multiple densities** to ensure consistency
6. **Use consistent spacing** (multiples of 4dp or 8dp)

### Common Mistakes

```kotlin
// ❌ BAD: Using px
textView.layoutParams.width = 100 // This is px!

// ✅ GOOD: Using dp
val widthPx = (100 * density).toInt()
textView.layoutParams.width = widthPx
```

```xml
<!-- ❌ BAD: Inconsistent spacing -->
<View
    android:layout_margin="13dp" />

<!-- ✅ GOOD: Use multiples of 4dp or 8dp -->
<View
    android:layout_margin="12dp" />
```

### Screen Density Information

Get current screen density:

```kotlin
val displayMetrics = resources.displayMetrics

val density = displayMetrics.density        // Scale factor
val densityDpi = displayMetrics.densityDpi  // Actual DPI
val widthPixels = displayMetrics.widthPixels
val heightPixels = displayMetrics.heightPixels

// Calculate screen size in dp
val widthDp = widthPixels / density
val heightDp = heightPixels / density

Log.d("Screen", "Size: ${widthDp}dp × ${heightDp}dp")
Log.d("Screen", "Density: ${density}x ($densityDpi dpi)")
```

---

## RU (original)

Что такое dp

dp (Density-independent Pixels) это единица измерения в Android используемая для создания адаптивных интерфейсов Она масштабируется в зависимости от плотности экрана устройства обеспечивая одинаковый визуальный размер элементов на разных экранах

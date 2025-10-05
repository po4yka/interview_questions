---
id: "20251003141511"
title: "What are px, dp, and sp?"
slug: "chto-takoe-px-dp-sp"
topic: "android"
moc: "moc-android"
difficulty: "easy"
status: "draft"
tags:
  - android
  - ui
  - units
  - measurements
  - dp
  - sp
  - px
date: "2025-10-03"
source: "https://t.me/easy_kotlin/932"
---

# What are px, dp, and sp?

## EN (expanded)

Android uses three main unit types for UI measurements:

### 1. px (Pixels)

**Pixels** are physical screen points - the actual dots on the display.

**Characteristics:**
- Absolute unit
- Device-dependent
- Not recommended for UI design
- Different devices have different pixel densities

**Example:**
```xml
<!-- BAD: Don't use px -->
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Text"
    android:textSize="16px" />
```

**Problem with px:**
- 100px on a low-density screen looks large
- 100px on a high-density screen looks tiny
- UI appears different sizes on different devices

### 2. dp (Density-independent Pixels)

**dp** (also called **dip**) adapts to screen density for consistent physical size across devices.

**Characteristics:**
- Screen density-independent
- Recommended for all UI dimensions (margins, padding, sizes)
- 1dp = 1px on 160dpi screen (baseline)
- Automatically scales on other densities

**Calculation:**
```
px = dp × (dpi / 160)
```

**Example:**
```xml
<!-- GOOD: Use dp for dimensions -->
<View
    android:layout_width="100dp"
    android:layout_height="100dp"
    android:layout_margin="16dp" />
```

**Density Buckets:**
| Density | Scale | 100dp in pixels |
|---------|-------|----------------|
| ldpi | 0.75x | 75px |
| mdpi | 1.0x | 100px |
| hdpi | 1.5x | 150px |
| xhdpi | 2.0x | 200px |
| xxhdpi | 3.0x | 300px |
| xxxhdpi | 4.0x | 400px |

### 3. sp (Scalable Pixels)

**sp** is like dp but also accounts for user font size preferences.

**Characteristics:**
- Used exclusively for text sizes
- Respects user's font size settings
- Scales with screen density AND user preferences
- Essential for accessibility

**Example:**
```xml
<!-- GOOD: Use sp for text -->
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Hello World"
    android:textSize="16sp" />
```

**User Font Size Impact:**
```
Default: 16sp = 16px @ mdpi
Large text setting: 16sp = 19.2px @ mdpi (1.2x)
Huge text setting: 16sp = 24px @ mdpi (1.5x)
```

### Practical Examples

#### Layout with dp

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:padding="16dp"
    android:orientation="vertical">

    <ImageView
        android:layout_width="48dp"
        android:layout_height="48dp"
        android:src="@drawable/icon" />

    <View
        android:layout_width="match_parent"
        android:layout_height="1dp"
        android:background="@color/divider"
        android:layout_marginVertical="8dp" />

</LinearLayout>
```

#### Text with sp

```xml
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Title"
    android:textSize="24sp"
    android:layout_marginBottom="8dp" />

<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Body text"
    android:textSize="16sp" />
```

### In Jetpack Compose

```kotlin
@Composable
fun UnitsExample() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp) // Use .dp extension
    ) {
        // Text uses sp automatically
        Text(
            text = "Title",
            fontSize = 24.sp // Use .sp extension for text
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "Body",
            fontSize = 16.sp
        )

        Box(
            modifier = Modifier
                .size(48.dp) // Use dp for dimensions
                .background(Color.Blue)
        )
    }
}
```

### Converting Between Units

```kotlin
// In code (View system)
val density = resources.displayMetrics.density

// Convert dp to px
val widthPx = (100 * density).toInt() // 100dp → px

// Convert px to dp
val widthDp = (200 / density) // 200px → dp

// For sp (text)
val scaledDensity = resources.displayMetrics.scaledDensity
val textSizePx = (16 * scaledDensity) // 16sp → px
```

```kotlin
// Extension functions
val Int.dp: Int
    get() = (this * Resources.getSystem().displayMetrics.density).toInt()

val Int.sp: Int
    get() = (this * Resources.getSystem().displayMetrics.scaledDensity).toInt()

// Usage
val width = 100.dp
val textSize = 16.sp
```

### Common Mistakes

```kotlin
// ❌ BAD: Using px
textView.textSize = 16f // This is px!

// ✅ GOOD: Using sp
textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16f)
```

```kotlin
// ❌ BAD: Using dp for text
<TextView android:textSize="16dp" />

// ✅ GOOD: Using sp for text
<TextView android:textSize="16sp" />
```

```kotlin
// ❌ BAD: Using sp for dimensions
<View
    android:layout_width="100sp"
    android:layout_height="100sp" />

// ✅ GOOD: Using dp for dimensions
<View
    android:layout_width="100dp"
    android:layout_height="100dp" />
```

### Accessibility Considerations

```kotlin
@Composable
fun AccessibleText() {
    // sp automatically scales with user settings
    Text(
        text = "This text respects user font size preferences",
        fontSize = 16.sp // Will scale if user increases font size
    )
}
```

### Material Design Guidelines

**Common sizes:**
```kotlin
// Margins and padding
val spacing_xs = 4.dp
val spacing_s = 8.dp
val spacing_m = 16.dp
val spacing_l = 24.dp
val spacing_xl = 32.dp

// Text sizes
val text_xs = 12.sp
val text_s = 14.sp
val text_m = 16.sp
val text_l = 20.sp
val text_xl = 24.sp
val text_xxl = 34.sp

// Icon sizes
val icon_s = 16.dp
val icon_m = 24.dp
val icon_l = 32.dp
val icon_xl = 48.dp
```

### Best Practices

1. **Always use dp** for layout dimensions, margins, padding
2. **Always use sp** for text sizes
3. **Never use px** unless absolutely necessary (rare cases like drawing)
4. **Test on multiple devices** with different densities
5. **Test with different font sizes** in accessibility settings
6. **Use Material Design** spacing guidelines

### Quick Reference

| Unit | Use Case | Scales with Density | Scales with Font Settings |
|------|----------|-------------------|-------------------------|
| **px** | Avoid | ❌ No | ❌ No |
| **dp** | Dimensions | ✅ Yes | ❌ No |
| **sp** | Text size | ✅ Yes | ✅ Yes |

---

## RU (original)

Что такое px dp sp

px - физические точки экрана. dp - независимые от плотности пиксели адаптируются под плотность экрана. sp - масштабируемые пиксели учитывают настройки шрифта пользователя. Используются в Android для адаптации UI под разные устройства

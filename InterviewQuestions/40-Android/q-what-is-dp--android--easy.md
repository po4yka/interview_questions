---
id: 202510031411306
title: What is dp / Что такое dp
aliases: []

# Classification
topic: android
subtopics: [android, ui]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/84
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-dp
  - c-android-screen-density
  - c-android-dpi

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [dp, density-independent pixels, difficulty/easy, easy_kotlin, lang/ru]
---

# Question (EN)
> What is dp

# Вопрос (RU)
> Что такое dp

---

## Answer (EN)

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

## Ответ (RU)

dp означает density-independent pixels или пиксели не зависящие от плотности Это виртуальная единица измерения которая используется для обеспечения одинакового визуального размера элементов пользовательского интерфейса на экранах с различной плотностью пикселей Это важно поскольку устройства Android могут иметь различные размеры и разрешения экранов и использование dp помогает создать консистентный пользовательский интерфейс на всех этих устройствах

---

## Follow-ups
- How do you programmatically convert between dp and pixels in Android?
- What are the standard screen density buckets (ldpi, mdpi, hdpi, etc.)?
- When should you use px instead of dp?

## References
- [[c-android-dp]]
- [[c-android-screen-density]]
- [[c-android-dpi]]
- [[c-android-resources]]
- [[moc-android]]

## Related Questions
- [[q-what-is-the-difference-between-measurement-units-like-dp-and-sp--android--easy]]

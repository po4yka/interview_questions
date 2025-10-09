---
topic: android
tags:
  - android
  - fluent design system
  - human interface guidelines
  - material design
  - ui
difficulty: medium
status: reviewed
---

# С какими вариантами систем проектирования в Android работал

**English**: What design systems in Android have you worked with?

## Answer

In Android development, several design systems are commonly used to create consistent, polished user interfaces. Here are the main design systems:

### 1. Material Design (Google)

**Material Design** is the standard design system for Android, developed by Google. It's the most widely adopted system for Android applications due to its deep integration with the Android ecosystem.

#### Key Features:
- **Material Components** - Pre-built UI components
- **Motion and animation** guidelines
- **Color systems** with primary, secondary, and surface colors
- **Typography** scale and guidelines
- **Elevation and shadows** for depth
- **Shape theming** for customization

#### Implementation:

```kotlin
// build.gradle
dependencies {
    implementation 'com.google.android.material:material:1.9.0'
}
```

```xml
<!-- styles.xml - Material Theme -->
<style name="AppTheme" parent="Theme.Material3.DayNight">
    <item name="colorPrimary">@color/purple_500</item>
    <item name="colorPrimaryVariant">@color/purple_700</item>
    <item name="colorOnPrimary">@color/white</item>
    <item name="colorSecondary">@color/teal_200</item>
    <item name="colorSecondaryVariant">@color/teal_700</item>
    <item name="colorOnSecondary">@color/black</item>
</style>
```

```xml
<!-- Material Components in XML -->
<com.google.android.material.button.MaterialButton
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Material Button"
    app:cornerRadius="8dp"
    app:icon="@drawable/ic_check" />

<com.google.android.material.card.MaterialCardView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:cardElevation="4dp"
    app:cardCornerRadius="12dp">
    <!-- Card content -->
</com.google.android.material.card.MaterialCardView>

<com.google.android.material.textfield.TextInputLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:startIconDrawable="@drawable/ic_email">
    <com.google.android.material.textfield.TextInputEditText
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Email" />
</com.google.android.material.textfield.TextInputLayout>
```

#### Material Design 3 (Material You):

```kotlin
// Material 3 dynamic colors (Android 12+)
<style name="AppTheme" parent="Theme.Material3.DayNight">
    <item name="android:colorScheme">@android:color/system_accent1_500</item>
</style>
```

### 2. Fluent Design System (Microsoft)

**Fluent Design System** is Microsoft's design language, oriented toward creating intuitive interfaces. It can be adapted for Android through custom styling.

#### Key Features:
- **Light, depth, motion, material, scale** principles
- **Acrylic material** for translucent surfaces
- **Reveal highlight** for interactive elements
- **Connected animations** for smooth transitions

#### Adaptation for Android:

```xml
<!-- Fluent-inspired styling -->
<style name="FluentButtonStyle" parent="Widget.MaterialComponents.Button">
    <item name="cornerRadius">2dp</item>
    <item name="elevation">2dp</item>
    <item name="android:textAllCaps">false</item>
    <item name="android:letterSpacing">0</item>
</style>

<Button
    style="@style/FluentButtonStyle"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Fluent Button" />
```

```kotlin
// Implementing Fluent-like reveal effect
view.setOnTouchListener { v, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            val ripple = RippleDrawable(
                ColorStateList.valueOf(Color.parseColor("#33FFFFFF")),
                null,
                null
            )
            v.background = ripple
        }
    }
    false
}
```

### 3. Human Interface Guidelines (Apple)

**Human Interface Guidelines (HIG)** are Apple's design principles for iOS and macOS. While oriented toward iOS, these principles can be valuable for **cross-platform applications** to maintain consistency.

#### Key Principles:
- **Clarity** - Text legibility, icons, and visual elements
- **Deference** - Content takes precedence over UI
- **Depth** - Visual layers and realistic motion

#### Cross-platform considerations:

```kotlin
// Shared design tokens for cross-platform consistency
object DesignTokens {
    // iOS-inspired spacing
    const val SPACING_TINY = 4
    const val SPACING_SMALL = 8
    const val SPACING_MEDIUM = 16
    const val SPACING_LARGE = 24

    // iOS-inspired corner radius
    const val CORNER_RADIUS_SMALL = 8
    const val CORNER_RADIUS_MEDIUM = 12
    const val CORNER_RADIUS_LARGE = 16
}
```

### 4. Custom Design Systems

Many organizations create their own design systems based on Material Design or other frameworks:

```kotlin
// Custom design system example
object BrandDesignSystem {
    // Colors
    object Colors {
        val Primary = Color(0xFF1976D2)
        val Secondary = Color(0xFFFFC107)
        val Error = Color(0xFFD32F2F)
    }

    // Typography
    object Typography {
        val H1 = TextStyle(fontSize = 32.sp, fontWeight = FontWeight.Bold)
        val Body1 = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Normal)
    }

    // Spacing
    object Spacing {
        val Small = 8.dp
        val Medium = 16.dp
        val Large = 24.dp
    }
}
```

### Comparison

| Design System | Best For | Integration | Platform |
|--------------|----------|-------------|----------|
| **Material Design** | Android-first apps | Native Android support | Android, Web |
| **Fluent Design** | Microsoft ecosystem apps | Custom implementation | Windows, iOS, Android, Web |
| **HIG** | Cross-platform iOS/Android | Design principles only | iOS, macOS |
| **Custom** | Brand-specific needs | Full custom implementation | Any |

### Best Practices

1. **Material Design is recommended** for Android-native apps
2. Use **Material Components** library for consistency
3. Follow **accessibility guidelines** from your chosen system
4. Implement **dark theme** support
5. Use **design tokens** for maintainability
6. Consider **platform conventions** when choosing a system

## Ответ

В Android-разработке часто используются следующие системы проектирования: Material Design от Google, Fluent Design System от Microsoft и Human Interface Guidelines от Apple. Material Design является стандартным выбором благодаря интеграции с экосистемой Google и Android. Fluent Design System ориентирован на создание интуитивных интерфейсов и может быть адаптирован для Android через стилизацию. Принципы HIG, хотя ориентированы на iOS и macOS, могут быть полезны для кросс-платформенных приложений.


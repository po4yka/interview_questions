---
id: 20251012-122751
title: Accessibility Color Contrast / Контрастность цветов для доступности
aliases: [Color Contrast, Контрастность цветов]
topic: android
subtopics:
  - ui-accessibility
  - ui-theming
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-accessibility-compose--android--medium
  - q-material3-dynamic-color-theming--material-design--medium
created: 2025-10-11
updated: 2025-10-15
tags: [android/ui-accessibility, android/ui-theming, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:53:25 pm
---

# Вопрос (RU)
> Что такое Контрастность цветов для доступности?

---

# Question (EN)
> What is Accessibility Color Contrast?

## Answer (EN)
Color contrast is the difference in luminance between text and background colors. Proper [[c-accessibility|accessibility]] contrast ensures readability for users with low vision, color blindness, age-related vision changes, and outdoor viewing. WCAG provides standardized contrast requirements. Material Design color system helps ensure accessible color combinations.

#### WCAG Requirements

```
Level AA (Minimum):
  Normal text (< 18pt):      4.5:1
  Large text (≥ 18pt):       3:1

Level AAA (Enhanced):
  Normal text:               7:1
  Large text:                4.5:1

Examples:
  Black on White:     21:1   (Excellent)
  #757575 on White:    4.6:1   (Passes AA)
  #959595 on White:    2.8:1   (Fails AA)
```

#### Material 3 Color Roles

Use Material color pairs for guaranteed contrast:

```kotlin
@Composable
fun MaterialColorExample() {
    MaterialTheme {
        Surface(color = MaterialTheme.colorScheme.primary) {
            Text(
                text = "Primary button",
                color = MaterialTheme.colorScheme.onPrimary // Guaranteed contrast
            )
        }
    }
}
```

Material color pairs:
- primary / onPrimary
- secondary / onSecondary
- error / onError
- surface / onSurface
- background / onBackground

Each pair guarantees WCAG AA contrast (4.5:1).

#### Testing

Manual testing:
- WebAIM Contrast Checker
- Contrast Ratio
- Who Can Use

Automated testing:
```kotlin
@Test
fun testColorContrast() {
    val foreground = Color(0xFF757575)
    val background = Color.White
    val ratio = ContrastChecker.contrastRatio(foreground, background)

    assertTrue("Contrast ratio ${String.format("%.2f", ratio)}:1 does not meet WCAG AA (4.5:1)",
        ratio >= 4.5)
}
```

#### Common Violations

Gray text on light background:

```kotlin
//  BAD - Insufficient contrast
Text(
    text = "Secondary info",
    color = Color(0xFFCCCCCC), // Light gray
    modifier = Modifier.background(Color.White)
)
// Contrast: 1.6:1

//  GOOD - Sufficient contrast
Text(
    text = "Secondary info",
    color = Color(0xFF757575), // Medium gray
    modifier = Modifier.background(Color.White)
)
// Contrast: 4.6:1

//  BETTER - Use Material colors
Text(
    text = "Secondary info",
    color = MaterialTheme.colorScheme.onSurfaceVariant,
    modifier = Modifier.background(MaterialTheme.colorScheme.surface)
)
```

**2. Blue links on white background**:

```kotlin
//  BAD - Light blue, insufficient contrast
Text(
    text = "Click here",
    color = Color(0xFF4FC3F7), // Light blue
    modifier = Modifier
        .clickable { }
        .background(Color.White)
)
// Contrast: 2.9:1

//  GOOD - Darker blue
Text(
    text = "Click here",
    color = Color(0xFF0277BD), // Dark blue
    modifier = Modifier
        .clickable { }
        .background(Color.White)
)
// Contrast: 4.5:1

//  BETTER - Use Material colors
Text(
    text = "Click here",
    color = MaterialTheme.colorScheme.primary,
    modifier = Modifier
        .clickable { }
        .background(MaterialTheme.colorScheme.background)
)
```

**3. Status indicators relying only on color**:

```kotlin
//  BAD - Only color differentiation
Row {
    Text("Success", color = Color.Green)
    Text("Warning", color = Color.Yellow)
    Text("Error", color = Color.Red)
}
// Problems:
// 1. Color blind users can't distinguish
// 2. May not have sufficient contrast

//  GOOD - Add icons + sufficient contrast
Row {
    Row {
        Icon(Icons.Default.CheckCircle, null, tint = Color(0xFF2E7D32)) // Dark green
        Text("Success", color = Color(0xFF2E7D32))
    }
    Row {
        Icon(Icons.Default.Warning, null, tint = Color(0xFFF57C00)) // Dark orange
        Text("Warning", color = Color(0xFFF57C00))
    }
    Row {
        Icon(Icons.Default.Error, null, tint = Color(0xFFC62828)) // Dark red
        Text("Error", color = Color(0xFFC62828))
    }
}

//  BETTER - Use Material semantic colors
Row {
    Row {
        Icon(Icons.Default.CheckCircle, null, tint = MaterialTheme.colorScheme.tertiary)
        Text("Success", color = MaterialTheme.colorScheme.tertiary)
    }
    Row {
        Icon(Icons.Default.Error, null, tint = MaterialTheme.colorScheme.error)
        Text("Error", color = MaterialTheme.colorScheme.error)
    }
}
```

**4. Disabled states**:

```kotlin
//  BAD - Disabled text might not have contrast
Button(
    onClick = {},
    enabled = false,
    colors = ButtonDefaults.buttonColors(
        disabledContainerColor = Color.LightGray,
        disabledContentColor = Color.Gray
    )
) {
    Text("Disabled")
}
// May not meet 4.5:1 ratio

//  GOOD - Material provides accessible disabled states
Button(
    onClick = {},
    enabled = false
    // Material colors automatically ensure contrast
) {
    Text("Disabled")
}

// Note: WCAG allows lower contrast for disabled elements (no requirement)
// But best practice is to maintain readability
```

### Dark Theme Considerations

```kotlin
@Composable
fun DarkThemeContrast() {
    //  BAD - Same colors in both themes
    val textColor = Color.Black
    val backgroundColor = Color.White
    // Inverted in dark theme = poor contrast!

    //  GOOD - Different colors per theme
    val textColor = if (isSystemInDarkTheme()) {
        Color(0xFFE0E0E0) // Light gray for dark theme
    } else {
        Color(0xFF212121) // Dark gray for light theme
    }

    //  BETTER - Use Material dynamic colors
    Text(
        text = "Content",
        color = MaterialTheme.colorScheme.onBackground,
        modifier = Modifier.background(MaterialTheme.colorScheme.background)
    )
}

// Custom color scheme
val LightColorScheme = lightColorScheme(
    primary = Color(0xFF6200EE),
    onPrimary = Color.White, // Ensures contrast
    // ...
)

val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFBB86FC),
    onPrimary = Color.Black, // Ensures contrast
    // ...
)

@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme,
        content = content
    )
}
```

### Color Blindness Simulation

**Types of color blindness:**
```
Deuteranopia (red-green, most common):
  - Can't distinguish red from green
  - Affects ~5% of males, ~0.5% of females

Protanopia (red-green):
  - Similar to deuteranopia
  - Affects ~1% of males

Tritanopia (blue-yellow, rare):
  - Can't distinguish blue from yellow
  - Affects ~0.01% of population

Achromatopsia (complete):
  - No color vision (grayscale only)
  - Very rare (~0.003%)
```

**Testing for color blindness**:

```kotlin
// Simulator function (simplified)
object ColorBlindnessSimulator {

    fun simulateDeuteranopia(color: Color): Color {
        // Simplified deuteranopia simulation
        // Real implementation would use matrices
        return Color(
            red = 0.625f * color.red + 0.375f * color.green,
            green = 0.7f * color.red + 0.3f * color.green,
            blue = color.blue,
            alpha = color.alpha
        )
    }

    fun simulateProtanopia(color: Color): Color {
        return Color(
            red = 0.567f * color.red + 0.433f * color.green,
            green = 0.558f * color.red + 0.442f * color.green,
            blue = color.blue,
            alpha = color.alpha
        )
    }

    fun simulateTritanopia(color: Color): Color {
        return Color(
            red = color.red,
            green = 0.95f * color.green + 0.05f * color.blue,
            blue = 0.433f * color.green + 0.567f * color.blue,
            alpha = color.alpha
        )
    }

    fun simulateAchromatopsia(color: Color): Color {
        val gray = 0.299f * color.red + 0.587f * color.green + 0.114f * color.blue
        return Color(gray, gray, gray, color.alpha)
    }
}

@Preview
@Composable
fun ColorBlindnessPreview() {
    Column {
        // Original
        ColorSwatch(Color.Red, "Original Red")

        // Simulations
        ColorSwatch(
            ColorBlindnessSimulator.simulateDeuteranopia(Color.Red),
            "Deuteranopia"
        )
        ColorSwatch(
            ColorBlindnessSimulator.simulateProtanopia(Color.Red),
            "Protanopia"
        )
    }
}
```

**Design for color blindness:**

```kotlin
//  BAD - Only color to convey meaning
@Composable
fun BadStatus() {
    Row {
        Box(Modifier.size(16.dp).background(Color.Green))
        Text("Available")
    }
    Row {
        Box(Modifier.size(16.dp).background(Color.Red))
        Text("Offline")
    }
}
// Red and green look the same to color blind users!

//  GOOD - Use icons + color
@Composable
fun GoodStatus() {
    Row {
        Icon(Icons.Default.CheckCircle, null, tint = Color(0xFF2E7D32))
        Text("Available")
    }
    Row {
        Icon(Icons.Default.Cancel, null, tint = Color(0xFFC62828))
        Text("Offline")
    }
}

//  BETTER - Use patterns + icons + color
@Composable
fun BestStatus(isOnline: Boolean) {
    Row {
        Box(
            modifier = Modifier
                .size(16.dp)
                .background(
                    color = if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828),
                    shape = if (isOnline) CircleShape else RoundedCornerShape(2.dp)
                )
        )
        Icon(
            imageVector = if (isOnline) Icons.Default.CheckCircle else Icons.Default.Cancel,
            contentDescription = null,
            tint = if (isOnline) Color(0xFF2E7D32) else Color(0xFFC62828)
        )
        Text(if (isOnline) "Available" else "Offline")
    }
}
```

### Focus Indicators

```kotlin
//  GOOD - Visible focus indicator with sufficient contrast
@Composable
fun FocusableButton() {
    var isFocused by remember { mutableStateOf(false) }

    Button(
        onClick = {},
        modifier = Modifier
            .onFocusChanged { isFocused = it.isFocused }
            .border(
                width = if (isFocused) 3.dp else 0.dp,
                color = MaterialTheme.colorScheme.primary,
                shape = RoundedCornerShape(8.dp)
            )
    ) {
        Text("Focusable Button")
    }
}

// Focus indicator contrast must be at least 3:1 against adjacent colors
```

### Best Practices

1. **Use Material Color Roles**
   ```kotlin
   //  GOOD - Guaranteed contrast
   Text(
       text = "Content",
       color = MaterialTheme.colorScheme.onPrimary,
       modifier = Modifier.background(MaterialTheme.colorScheme.primary)
   )

   //  BAD - Manual colors without checking
   Text(
       text = "Content",
       color = Color.White,
       modifier = Modifier.background(Color(0xFFCCCCCC))
   )
   ```

2. **Test with Accessibility Scanner**
   ```
    Run Accessibility Scanner on every screen
    Fix all contrast violations
    Re-test after fixes
   ```

3. **Don't Rely on Color Alone**
   ```kotlin
   //  GOOD - Icons + text + color
   Row {
       Icon(Icons.Default.Error, null)
       Text("Error message", color = Color.Red)
   }

   //  BAD - Only color
   Text("Error message", color = Color.Red)
   ```

4. **Test in Dark Mode**
   ```kotlin
   //  GOOD - Test both themes
   @Preview(uiMode = Configuration.UI_MODE_NIGHT_YES)
   @Preview(uiMode = Configuration.UI_MODE_NIGHT_NO)
   @Composable
   fun MyScreenPreview() {
       AppTheme {
           MyScreen()
       }
   }
   ```

5. **Automate Contrast Checks**
   ```kotlin
   //  GOOD - Test contrast in CI
   @Test
   fun testAllColorPairsHaveSufficientContrast() {
       val colorPairs = listOf(
           Color.Black to Color.White,
           Color(0xFF757575) to Color.White,
           // ... all color pairs used in app
       )

       colorPairs.forEach { (fg, bg) ->
           val ratio = ContrastChecker.contrastRatio(fg, bg)
           assertTrue(
               "Insufficient contrast: $fg on $bg = ${String.format("%.2f", ratio)}:1",
               ratio >= 4.5
           )
       }
   }
   ```

### Tools for Checking Contrast

1. **Android Studio**:
   - Color picker shows contrast ratio
   - Warning for insufficient contrast

2. **Accessibility Scanner** (Android app):
   - Scans running app
   - Identifies contrast issues
   - Provides suggestions

3. **Online tools**:
   - WebAIM Contrast Checker
   - Contrast Ratio
   - Who Can Use

4. **Browser extensions**:
   - Axe DevTools
   - WAVE

### Summary

**WCAG requirements:**
- Normal text (< 18pt): 4.5:1 (AA), 7:1 (AAA)
- Large text (≥ 18pt): 3:1 (AA), 4.5:1 (AAA)
- Focus indicators: 3:1

**Key principles:**
- Use Material color roles (automatic contrast)
- Test with Accessibility Scanner
- Don't rely on color alone
- Test in dark mode
- Consider color blindness
- Automate contrast checks in CI

**Common violations:**
- Light gray on white
- Light blue links
- Status colors only (no icons)
- Same colors in both themes

**Solutions:**
- Use Material `colorScheme.onPrimary`, `onSurface`, etc.
- Add icons to color indicators
- Test with color blindness simulators
- Verify 4.5:1 ratio for all text

---

## Follow-ups

- What happens if you use custom colors without checking contrast?
- How does this issue affect users with different types of color blindness?
- What's the difference between WCAG AA and AAA requirements?
- How do you test contrast in automated UI tests?
- What tools can help detect contrast issues in CI/CD?

## References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design Color System](https://m3.material.io/foundations/color)
- [Android Accessibility Guidelines](https://developer.android.com/guide/topics/ui/accessibility)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

## Related Questions

### Related (Medium)
- [[q-accessibility-compose--android--medium]] - Accessibility
- [[q-accessibility-testing--android--medium]] - Accessibility
- [[q-custom-view-accessibility--android--medium]] - Accessibility
- [[q-accessibility-talkback--android--medium]] - Accessibility
- [[q-accessibility-text-scaling--android--medium]] - Accessibility

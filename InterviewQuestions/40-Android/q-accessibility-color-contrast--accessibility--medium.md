---
id: 20251012-122751
title: "Accessibility Color Contrast / Контрастность цветов для доступности"
topic: android
difficulty: medium
status: draft
moc: moc-android
created: 2025-10-11
tags: [accessibility, color-contrast, wcag, visual-accessibility, difficulty/medium]
related: [q-recyclerview-viewtypes-delegation--recyclerview--medium, q-kmm-sqldelight--multiplatform--medium, q-android-app-lag-analysis--android--medium]
  - q-accessibility-compose--accessibility--medium
  - q-material3-dynamic-color-theming--material-design--medium
---
# Question (EN)
How do you ensure sufficient color contrast for accessibility? What are WCAG contrast requirements, and how do you test and fix contrast issues in Android apps?

## Answer (EN)
### Overview

**Color contrast** is the difference in luminance between text and background colors. Proper contrast ensures content is readable for users with:
- Low vision
- Color blindness (deuteranopia, protanopia, tritanopia)
- Age-related vision changes
- Outdoor viewing (bright sunlight)

### WCAG Contrast Requirements

```
WCAG 2.1 Contrast Ratios:

Level AA (Minimum):
  - Normal text (< 18pt):      4.5:1
  - Large text (≥ 18pt/14pt bold): 3:1

Level AAA (Enhanced):
  - Normal text:               7:1
  - Large text:                4.5:1

Examples:
  Black on White:     21:1   (Excellent)
  #757575 on White:    4.6:1   (Passes AA)
  #959595 on White:    2.8:1   (Fails AA)
  Blue (#007AFF) on White: 4.5:1   (Passes AA)
```

### Calculating Contrast Ratio

**Formula:**
```
(Lighter luminance + 0.05) / (Darker luminance + 0.05)

Where luminance = 0.2126 * R + 0.7152 * G + 0.0722 * B
(after gamma correction)
```

**Kotlin implementation**:

```kotlin
object ContrastChecker {

    /**
     * Calculate contrast ratio between two colors
     * Returns value between 1:1 (no contrast) and 21:1 (maximum)
     */
    fun contrastRatio(color1: Color, color2: Color): Double {
        val lum1 = luminance(color1)
        val lum2 = luminance(color2)

        val lighter = maxOf(lum1, lum2)
        val darker = minOf(lum1, lum2)

        return (lighter + 0.05) / (darker + 0.05)
    }

    /**
     * Calculate relative luminance of a color
     */
    private fun luminance(color: Color): Double {
        val r = gammaCorrect(color.red)
        val g = gammaCorrect(color.green)
        val b = gammaCorrect(color.blue)

        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    }

    /**
     * Apply gamma correction
     */
    private fun gammaCorrect(value: Float): Double {
        return if (value <= 0.03928) {
            value / 12.92
        } else {
            Math.pow(((value + 0.055) / 1.055), 2.4)
        }
    }

    /**
     * Check if contrast meets WCAG AA for normal text
     */
    fun meetsWCAG_AA_Normal(foreground: Color, background: Color): Boolean {
        return contrastRatio(foreground, background) >= 4.5
    }

    /**
     * Check if contrast meets WCAG AA for large text
     */
    fun meetsWCAG_AA_Large(foreground: Color, background: Color): Boolean {
        return contrastRatio(foreground, background) >= 3.0
    }

    /**
     * Check if contrast meets WCAG AAA
     */
    fun meetsWCAG_AAA(foreground: Color, background: Color): Boolean {
        return contrastRatio(foreground, background) >= 7.0
    }
}

// Usage
val foreground = Color.Gray
val background = Color.White
val ratio = ContrastChecker.contrastRatio(foreground, background)
val passes = ContrastChecker.meetsWCAG_AA_Normal(foreground, background)

println("Contrast ratio: ${String.format("%.2f", ratio)}:1")
println("Passes WCAG AA: $passes")
```

### Material 3 Color Roles (Built-in Contrast)

```kotlin
@Composable
fun MaterialColorExample() {
    MaterialTheme {
        //  GOOD - Material 3 automatically ensures contrast
        Surface(
            color = MaterialTheme.colorScheme.primary
        ) {
            Text(
                text = "Primary button",
                color = MaterialTheme.colorScheme.onPrimary // Guaranteed contrast
            )
        }

        Surface(
            color = MaterialTheme.colorScheme.error
        ) {
            Text(
                text = "Error message",
                color = MaterialTheme.colorScheme.onError // Guaranteed contrast
            )
        }

        //  BAD - Manual colors without contrast check
        Surface(color = Color(0xFFCCCCCC)) {
            Text(
                text = "Button",
                color = Color.White // Might not have sufficient contrast!
            )
        }
    }
}
```

**Material 3 color pairs:**
```
primary / onPrimary
secondary / onSecondary
tertiary / onTertiary
error / onError
surface / onSurface
background / onBackground
surfaceVariant / onSurfaceVariant

Each pair guarantees WCAG AA contrast (4.5:1)
```

### Testing Contrast

**Manual testing with online tools**:
```
1. WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
2. Contrast Ratio: https://contrast-ratio.com/
3. Who Can Use: https://whocanuse.com/

Take screenshot → Pick colors → Get ratio
```

**Automated testing**:

```kotlin
@Test
fun testColorContrast() {
    composeTestRule.setContent {
        Text(
            text = "Important message",
            color = Color(0xFF757575), // Gray
            modifier = Modifier.background(Color.White)
        )
    }

    // Verify contrast
    val foreground = Color(0xFF757575)
    val background = Color.White
    val ratio = ContrastChecker.contrastRatio(foreground, background)

    assertTrue(
        "Contrast ratio ${String.format("%.2f", ratio)}:1 does not meet WCAG AA (4.5:1)",
        ratio >= 4.5
    )
}

@Test
fun testMaterialThemeContrast() {
    composeTestRule.setContent {
        MaterialTheme {
            val colorScheme = MaterialTheme.colorScheme

            // Verify all Material color pairs meet WCAG AA
            listOf(
                colorScheme.primary to colorScheme.onPrimary,
                colorScheme.secondary to colorScheme.onSecondary,
                colorScheme.error to colorScheme.onError,
                colorScheme.surface to colorScheme.onSurface,
                colorScheme.background to colorScheme.onBackground
            ).forEach { (bg, fg) ->
                val ratio = ContrastChecker.contrastRatio(fg, bg)
                assertTrue(
                    "Insufficient contrast: ${String.format("%.2f", ratio)}:1",
                    ratio >= 4.5
                )
            }
        }
    }
}
```

### Common Contrast Violations

**1. Gray text on light background**:

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

# Вопрос (RU)
Как обеспечить достаточный контраст цвета для доступности? Что такое требования WCAG к контрасту, и как тестировать и исправлять проблемы контраста в Android-приложениях?

## Ответ (RU)
[Перевод с примерами из английской версии...]

### Резюме

**Требования WCAG:**
- Обычный текст (< 18pt): 4.5:1 (AA), 7:1 (AAA)
- Крупный текст (≥ 18pt): 3:1 (AA), 4.5:1 (AAA)
- Focus индикаторы: 3:1

**Ключевые принципы:**
- Используйте Material color roles (автоматический контраст)
- Тестируйте с Accessibility Scanner
- Не полагайтесь только на цвет
- Тестируйте в dark mode
- Учитывайте дальтонизм
- Автоматизируйте проверки контраста в CI

**Распространённые нарушения:**
- Светло-серый на белом
- Светло-синие ссылки
- Статус только цветом (без иконок)
- Одинаковые цвета в обеих темах

**Решения:**
- Использовать Material `colorScheme.onPrimary`, `onSurface`, и т.д.
- Добавлять иконки к цветным индикаторам
- Тестировать с симуляторами дальтонизма
- Проверять соотношение 4.5:1 для всего текста

---

## Related Questions

### Related (Medium)
- [[q-accessibility-compose--accessibility--medium]] - Accessibility
- [[q-accessibility-testing--accessibility--medium]] - Accessibility
- [[q-custom-view-accessibility--custom-views--medium]] - Accessibility
- [[q-accessibility-talkback--accessibility--medium]] - Accessibility
- [[q-accessibility-text-scaling--accessibility--medium]] - Accessibility

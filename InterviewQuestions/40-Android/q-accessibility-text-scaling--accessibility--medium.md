---
tags:
  - android
  - accessibility
  - text-scaling
  - font-size
  - dynamic-type
difficulty: medium
status: draft
related:
  - q-accessibility-compose--accessibility--medium
  - q-accessibility-testing--accessibility--medium
created: 2025-10-11
---

# Question (EN)
How do you support dynamic text sizing and display scaling for accessibility? What are sp units, text scaling factors, and how do you test your UI with different text sizes?

## Answer (EN)
### Overview

**Text scaling** allows users with visual impairments to increase text size for better readability. Android provides:
- **sp (scale-independent pixels)** - Scales with user's font size preference
- **Text scaling factors** - 0.85x to 2.0x (or more)
- **Display size** - Separate from text scaling, affects all UI elements

### SP vs DP Units

```kotlin
//  GOOD - Text size in sp (scales with user preference)
Text(
    text = "Hello World",
    fontSize = 16.sp // Scales with accessibility settings
)

//  BAD - Text size in dp (does NOT scale)
Text(
    text = "Hello World",
    fontSize = 16.dp // Fixed size, ignores user preferences
)

//  GOOD - Non-text elements in dp
Box(
    modifier = Modifier.size(48.dp) // Touch target, doesn't scale
)

//  BAD - Touch targets in sp
Box(
    modifier = Modifier.size(48.sp) // Will become huge at large text sizes
)
```

**Rule of thumb:**
- Text: Use **sp**
- Layouts, icons, spacing: Use **dp**

### Text Scaling Levels

```
Scaling factors in Android:

Small:    0.85x  (85%)
Default:  1.00x  (100%)
Large:    1.15x  (115%)
Larger:   1.30x  (130%)
Largest:  1.50x  (150%)
Huge:     2.00x  (200%)  ← Target for testing
```

### Adaptive Layouts for Text Scaling

**Problem: Text overflow at large sizes**:

```kotlin
//  BAD - Text gets cut off
@Composable
fun BadProfile() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp) // Fixed height!
    ) {
        Image(
            painter = painterResource(R.drawable.profile),
            contentDescription = "Profile",
            modifier = Modifier.size(48.dp)
        )
        Column {
            Text(
                text = "John Doe",
                fontSize = 16.sp,
                maxLines = 1
            )
            Text(
                text = "Software Engineer",
                fontSize = 14.sp,
                maxLines = 1
            )
        }
    }
}
// At 200% text scaling, text gets truncated!
```

**Solution 1: Remove fixed heights**:

```kotlin
//  GOOD - Height adapts to content
@Composable
fun GoodProfile() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp), // No fixed height
        verticalAlignment = Alignment.CenterVertically
    ) {
        Image(
            painter = painterResource(R.drawable.profile),
            contentDescription = "Profile",
            modifier = Modifier.size(48.dp)
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(
                text = "John Doe",
                fontSize = 16.sp
                // No maxLines - allows wrapping
            )
            Text(
                text = "Software Engineer",
                fontSize = 14.sp
            )
        }
    }
}
```

**Solution 2: Use Column when needed**:

```kotlin
//  GOOD - Switch to vertical layout at large scales
@Composable
fun AdaptiveProfile() {
    val configuration = LocalConfiguration.current
    val fontScale = LocalDensity.current.fontScale

    if (fontScale > 1.3f) {
        // Vertical layout for large text
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Image(
                painter = painterResource(R.drawable.profile),
                contentDescription = "Profile",
                modifier = Modifier.size(64.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = "John Doe", fontSize = 16.sp)
            Text(text = "Software Engineer", fontSize = 14.sp)
        }
    } else {
        // Horizontal layout for normal text
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Image(
                painter = painterResource(R.drawable.profile),
                contentDescription = "Profile",
                modifier = Modifier.size(48.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(text = "John Doe", fontSize = 16.sp)
                Text(text = "Software Engineer", fontSize = 14.sp)
            }
        }
    }
}
```

### Detecting Font Scale

```kotlin
@Composable
fun FontScaleAware() {
    val density = LocalDensity.current
    val fontScale = density.fontScale

    Text(
        text = when {
            fontScale >= 2.0f -> "Huge text (200%)"
            fontScale >= 1.5f -> "Largest text (150%)"
            fontScale >= 1.3f -> "Larger text (130%)"
            fontScale >= 1.15f -> "Large text (115%)"
            fontScale <= 0.85f -> "Small text (85%)"
            else -> "Default text (100%)"
        }
    )
}

// XML View
class MyView(context: Context) : View(context) {
    private val fontScale: Float
        get() = resources.configuration.fontScale

    init {
        if (fontScale > 1.5f) {
            // Adapt layout for large text
        }
    }
}
```

### Material 3 Typography with Scaling

```kotlin
@Composable
fun MaterialTypographyExample() {
    // Material 3 typography automatically scales
    Column(modifier = Modifier.padding(16.dp)) {
        Text(
            text = "Display Large",
            style = MaterialTheme.typography.displayLarge
            // 57sp by default, scales with user preference
        )

        Text(
            text = "Headline Medium",
            style = MaterialTheme.typography.headlineMedium
            // 28sp by default
        )

        Text(
            text = "Body Large",
            style = MaterialTheme.typography.bodyLarge
            // 16sp by default
        )

        Text(
            text = "Body Small",
            style = MaterialTheme.typography.bodySmall
            // 12sp by default
        )
    }
}

// Custom theme with relative sizing
val CustomTypography = Typography(
    displayLarge = TextStyle(
        fontSize = 57.sp,
        lineHeight = 64.sp,
        letterSpacing = (-0.25).sp
    ),
    // Scale down proportionally
    bodyLarge = TextStyle(
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    )
)
```

### Testing with Different Text Sizes

**Manual testing**:

```
1. Go to Settings → Display → Font size
2. Set to "Largest" or "Huge"
3. Open your app
4. Verify:
    All text is readable
    No text is cut off
    Touch targets still work
    Layouts don't overlap
    Scrolling works properly
```

**Programmatic testing**:

```kotlin
@Test
fun testTextScaling() {
    composeTestRule.setContent {
        CompositionLocalProvider(
            LocalDensity provides Density(
                density = 1f,
                fontScale = 2.0f // 200% text scaling
            )
        ) {
            MyScreen()
        }
    }

    // Verify text is visible and readable
    composeTestRule
        .onNodeWithText("Hello")
        .assertIsDisplayed()
}

// Test multiple scales
@Test
fun testMultipleTextScales() {
    val scales = listOf(0.85f, 1.0f, 1.3f, 1.5f, 2.0f)

    scales.forEach { scale ->
        composeTestRule.setContent {
            CompositionLocalProvider(
                LocalDensity provides Density(
                    density = 1f,
                    fontScale = scale
                )
            ) {
                MyScreen()
            }
        }

        // Take screenshot for visual comparison
        composeTestRule.onRoot().captureToImage()

        // Verify key elements are still accessible
        composeTestRule
            .onNodeWithText("Submit")
            .assertIsDisplayed()
            .assertHasClickAction()
    }
}
```

**Robolectric testing**:

```kotlin
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P])
class TextScalingTest {

    @Test
    fun testViewWithLargeText() {
        // Set font scale
        val configuration = Configuration()
        configuration.fontScale = 2.0f

        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .create()
            .get()

        activity.resources.updateConfiguration(
            configuration,
            activity.resources.displayMetrics
        )

        // Measure views
        val textView = activity.findViewById<TextView>(R.id.title)
        textView.measure(
            View.MeasureSpec.makeMeasureSpec(1080, View.MeasureSpec.AT_MOST),
            View.MeasureSpec.makeMeasureSpec(0, View.MeasureSpec.UNSPECIFIED)
        )

        // Verify text is not cut off
        assertTrue(
            "Text height ${textView.measuredHeight} is too large",
            textView.measuredHeight < 200
        )
    }
}
```

### Common Text Scaling Issues

**1. Fixed heights cutting off text**:

```kotlin
//  BAD
Card(
    modifier = Modifier
        .fillMaxWidth()
        .height(80.dp) // Fixed height
) {
    Text("This text might get cut off at large scaling")
}

//  GOOD
Card(
    modifier = Modifier
        .fillMaxWidth()
        .wrapContentHeight() // Adapts to content
) {
    Text("This text will always be fully visible")
}
```

**2. maxLines causing truncation**:

```kotlin
//  BAD - Text truncated at large sizes
Text(
    text = "Important message that needs to be fully visible",
    maxLines = 1, // Only shows one line!
    overflow = TextOverflow.Ellipsis
)

//  GOOD - Allow wrapping
Text(
    text = "Important message that needs to be fully visible"
    // No maxLines - wraps naturally
)

//  ALSO GOOD - Use only when truncation is acceptable
Text(
    text = "Optional secondary info",
    maxLines = 2,
    overflow = TextOverflow.Ellipsis,
    modifier = Modifier.semantics {
        // Provide full text to accessibility
        contentDescription = "Optional secondary info (full text)"
    }
)
```

**3. Icons not scaling with text**:

```kotlin
//  BAD - Icon doesn't scale
Row {
    Icon(
        imageVector = Icons.Default.Info,
        contentDescription = null,
        modifier = Modifier.size(24.dp) // Fixed size
    )
    Text(
        text = "Information",
        fontSize = 16.sp // Scales
    )
}

//  GOOD - Icon scales with text
Row {
    Icon(
        imageVector = Icons.Default.Info,
        contentDescription = null,
        modifier = Modifier.size(with(LocalDensity.current) {
            (16.sp * 1.5f).toDp() // Scale with text
        })
    )
    Text(
        text = "Information",
        fontSize = 16.sp
    )
}

//  BETTER - Use LocalTextStyle
@Composable
fun ScalingIcon() {
    val textStyle = LocalTextStyle.current
    val iconSize = with(LocalDensity.current) {
        textStyle.fontSize.toDp() * 1.5f
    }

    Row {
        Icon(
            imageVector = Icons.Default.Info,
            contentDescription = null,
            modifier = Modifier.size(iconSize)
        )
        Text(
            text = "Information",
            style = textStyle
        )
    }
}
```

**4. Touch targets too close together**:

```kotlin
//  BAD - Touch targets overlap at large text
Row {
    TextButton(onClick = {}) { Text("Cancel") }
    TextButton(onClick = {}) { Text("OK") }
}

//  GOOD - Add spacing
Row(
    horizontalArrangement = Arrangement.spacedBy(16.dp)
) {
    TextButton(onClick = {}) { Text("Cancel") }
    TextButton(onClick = {}) { Text("OK") }
}

//  BETTER - Switch to Column at large scales
@Composable
fun AdaptiveButtons() {
    val fontScale = LocalDensity.current.fontScale

    if (fontScale > 1.3f) {
        Column(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(onClick = {}, modifier = Modifier.fillMaxWidth()) {
                Text("Cancel")
            }
            Button(onClick = {}, modifier = Modifier.fillMaxWidth()) {
                Text("OK")
            }
        }
    } else {
        Row(
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Button(onClick = {}) { Text("Cancel") }
            Button(onClick = {}) { Text("OK") }
        }
    }
}
```

### Display Size (Separate from Text Scaling)

**Display size affects all UI elements**:

```
Settings → Display → Display size

Small:   0.85x
Default: 1.00x
Large:   1.15x
Larger:  1.30x
Largest: 1.50x

Display size scales EVERYTHING:
- Layout dimensions (dp values)
- Touch targets
- Images
- Spacing
- Text (in addition to font scaling)
```

**Testing display size**:

```kotlin
@Test
fun testDisplaySize() {
    composeTestRule.setContent {
        CompositionLocalProvider(
            LocalDensity provides Density(
                density = 1.3f, // 130% display size
                fontScale = 1.0f
            )
        ) {
            MyScreen()
        }
    }

    // Verify layout still works
    composeTestRule
        .onNodeWithText("Submit")
        .assertIsDisplayed()
}
```

### Window Size Classes for Text Scaling

```kotlin
@Composable
fun ResponsiveLayout() {
    val windowSizeClass = calculateWindowSizeClass()
    val fontScale = LocalDensity.current.fontScale

    when {
        // Compact width + large text = vertical layout
        windowSizeClass.widthSizeClass == WindowWidthSizeClass.Compact && fontScale > 1.3f -> {
            CompactVerticalLayout()
        }
        // Medium width = flexible layout
        windowSizeClass.widthSizeClass == WindowWidthSizeClass.Medium -> {
            FlexibleLayout()
        }
        // Expanded width = multi-column
        else -> {
            ExpandedLayout()
        }
    }
}
```

### Best Practices

1. **Always use sp for text**
   ```kotlin
   //  GOOD
   fontSize = 16.sp

   //  BAD
   fontSize = 16.dp
   ```

2. **Avoid fixed heights**
   ```kotlin
   //  GOOD
   modifier = Modifier.wrapContentHeight()

   //  BAD
   modifier = Modifier.height(80.dp)
   ```

3. **Test at 200% scaling**
   ```
    Test every screen at 200% text scaling
    Verify no text is cut off
    Verify touch targets still work
    Verify layouts don't overlap
   ```

4. **Consider adaptive layouts**
   ```kotlin
   //  GOOD - Adapt to large text
   if (fontScale > 1.3f) {
       Column { /* Vertical layout */ }
   } else {
       Row { /* Horizontal layout */ }
   }
   ```

5. **Use Material Typography**
   ```kotlin
   //  GOOD - Consistent scaling
   Text(
       text = "Title",
       style = MaterialTheme.typography.titleLarge
   )
   ```

### Summary

**Key concepts:**
- **sp units** - Scale with user font size preference (use for text)
- **dp units** - Fixed size (use for layouts, icons, spacing)
- **Font scale** - 0.85x to 2.0x (target 200% for testing)
- **Display size** - Scales everything (separate from font scaling)

**Common issues:**
- Fixed heights cutting off text
- maxLines causing truncation
- Icons not scaling with text
- Touch targets too close at large sizes

**Solutions:**
- Use wrapContentHeight() instead of fixed heights
- Avoid maxLines for important text
- Scale icons with text size
- Add spacing or switch to vertical layouts
- Test at 200% font scaling

**Testing:**
- Manual: Settings → Display → Font size → Largest
- Automated: Set fontScale in tests
- Screenshot testing at multiple scales
- Verify accessibility in CI/CD

---

# Вопрос (RU)
Как поддерживать динамический размер текста и масштабирование дисплея для доступности? Что такое sp-единицы, коэффициенты масштабирования текста, и как тестировать UI с различными размерами текста?

## Ответ (RU)
[Перевод с примерами из английской версии...]

### Резюме

**Ключевые концепции:**
- **sp-единицы** — масштабируются с пользовательскими настройками размера шрифта (для текста)
- **dp-единицы** — фиксированный размер (для layouts, иконок, отступов)
- **Font scale** — 0.85x to 2.0x (тестировать на 200%)
- **Display size** — масштабирует всё (отдельно от font scaling)

**Распространённые проблемы:**
- Фиксированные высоты обрезают текст
- maxLines вызывает усечение
- Иконки не масштабируются с текстом
- Touch targets слишком близко при больших размерах

**Решения:**
- Использовать wrapContentHeight() вместо фиксированных высот
- Избегать maxLines для важного текста
- Масштабировать иконки с размером текста
- Добавлять spacing или переключаться на вертикальные layouts
- Тестировать на 200% font scaling

**Тестирование:**
- Ручное: Настройки → Дисплей → Размер шрифта → Самый большой
- Автоматизированное: Устанавливать fontScale в тестах
- Screenshot-тестирование на разных масштабах
- Проверять accessibility в CI/CD

---

## Related Questions

### Related (Medium)
- [[q-accessibility-compose--accessibility--medium]] - Accessibility
- [[q-accessibility-testing--accessibility--medium]] - Accessibility
- [[q-custom-view-accessibility--custom-views--medium]] - Accessibility
- [[q-accessibility-color-contrast--accessibility--medium]] - Accessibility
- [[q-accessibility-talkback--accessibility--medium]] - Accessibility

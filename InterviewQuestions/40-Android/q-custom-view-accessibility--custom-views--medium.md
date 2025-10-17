---
id: "20251015082238627"
title: "Custom View Accessibility / Доступность кастомных View"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: - custom-views
  - accessibility
  - a11y
  - inclusive-design
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
subtopics: [ui-views, ui-accessibility]
---
# Custom View Accessibility

# Question (EN)
> How do you make custom views accessible? Explain content descriptions, accessibility events, TalkBack support, and implementing AccessibilityNodeInfo for complex custom views.

# Вопрос (RU)
> Как сделать пользовательские view доступными? Объясните описания содержимого, события доступности, поддержку TalkBack и реализацию AccessibilityNodeInfo для сложных пользовательских view.

---

## Answer (EN)

**Accessibility** ensures your app is usable by everyone, including people with disabilities. Making custom views accessible is not just good practice—it's essential for inclusive design and required in many markets.

### Why Accessibility Matters

**Statistics:**
- 15% of world population has some form of disability
- Required by law in many countries (ADA, WCAG)
- Improves usability for everyone
- Better SEO/discoverability

---

### 1. Basic Accessibility - Content Descriptions

**Content description** provides text alternative for visual elements.

```kotlin
class IconButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    init {
        //  Set content description
        contentDescription = "Save button"

        // Or read from XML
        context.theme.obtainStyledAttributes(
            attrs,
            intArrayOf(android.R.attr.contentDescription),
            0, 0
        ).apply {
            contentDescription = getString(0)
            recycle()
        }
    }

    // Update dynamically
    fun setIcon(iconType: IconType) {
        contentDescription = when (iconType) {
            IconType.SAVE -> "Save"
            IconType.DELETE -> "Delete"
            IconType.EDIT -> "Edit"
        }
        invalidate()
    }
}
```

**XML usage:**
```xml
<com.example.ui.IconButton
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:contentDescription="@string/save_button" />
```

---

### 2. Focusable and Clickable

Make views focusable for keyboard/screen reader navigation.

```kotlin
class CustomButton : View {

    init {
        //  Make focusable
        isFocusable = true
        isClickable = true

        // Enable important for accessibility
        importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES

        // Set up click handling for accessibility
        setOnClickListener {
            performAction()
            announceForAccessibility("Action completed")
        }
    }

    override fun performClick(): Boolean {
        // Announce to TalkBack
        announceForAccessibility("Button clicked")
        return super.performClick()
    }
}
```

---

### 3. State Descriptions

Describe the current state for screen readers.

```kotlin
class ToggleSwitch @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    var isChecked: Boolean = false
        set(value) {
            field = value

            //  Update state description
            stateDescription = if (value) {
                "On"
            } else {
                "Off"
            }

            // Announce state change
            announceForAccessibility(
                if (value) "Switched on" else "Switched off"
            )

            invalidate()
        }

    init {
        // Initial state
        stateDescription = if (isChecked) "On" else "Off"
    }
}
```

---

### 4. Custom AccessibilityNodeInfo

For complex views, provide detailed accessibility information.

```kotlin
class CustomSlider @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    var value: Float = 50f
        set(newValue) {
            field = newValue.coerceIn(0f, 100f)
            invalidate()
        }

    var min: Float = 0f
    var max: Float = 100f

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        //  Set class name for TalkBack
        info.className = SeekBar::class.java.name

        //  Add range info for slider
        info.rangeInfo = AccessibilityNodeInfo.RangeInfo.obtain(
            AccessibilityNodeInfo.RangeInfo.RANGE_TYPE_FLOAT,
            min,
            max,
            value
        )

        //  Add actions
        info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD)
        info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_BACKWARD)

        //  Set content description with current value
        info.contentDescription = "Slider, ${value.toInt()} percent"
    }

    override fun performAccessibilityAction(action: Int, arguments: Bundle?): Boolean {
        when (action) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> {
                value = (value + 10f).coerceAtMost(max)
                announceForAccessibility("Increased to ${value.toInt()} percent")
                return true
            }

            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> {
                value = (value - 10f).coerceAtLeast(min)
                announceForAccessibility("Decreased to ${value.toInt()} percent")
                return true
            }
        }

        return super.performAccessibilityAction(action, arguments)
    }
}
```

---

### 5. Virtual View Hierarchy

For views with multiple interactive regions (like calendars, charts), expose virtual children.

```kotlin
class CalendarView : View {

    private val accessibilityHelper = CalendarAccessibilityHelper(this)

    init {
        ViewCompat.setAccessibilityDelegate(this, accessibilityHelper)
    }

    private inner class CalendarAccessibilityHelper(host: View) :
        ExploreByTouchHelper(host) {

        override fun getVirtualViewAt(x: Float, y: Float): Int {
            // Find which day cell was touched
            return findDayAt(x, y) ?: INVALID_ID
        }

        override fun getVisibleVirtualViews(virtualViewIds: MutableList<Int>) {
            // Add all visible day cells
            for (day in 1..31) {
                virtualViewIds.add(day)
            }
        }

        override fun onPopulateNodeForVirtualView(
            virtualViewId: Int,
            node: AccessibilityNodeInfoCompat
        ) {
            // Describe virtual day cell
            val day = virtualViewId
            node.contentDescription = "Day $day"
            node.addAction(AccessibilityNodeInfoCompat.ACTION_CLICK)

            // Set bounds for focus rectangle
            val bounds = getDayBounds(day)
            node.setBoundsInParent(bounds)
        }

        override fun onPerformActionForVirtualView(
            virtualViewId: Int,
            action: Int,
            arguments: Bundle?
        ): Boolean {
            when (action) {
                AccessibilityNodeInfoCompat.ACTION_CLICK -> {
                    selectDay(virtualViewId)
                    return true
                }
            }
            return false
        }
    }

    private fun findDayAt(x: Float, y: Float): Int? {
        // Implementation to find day at coordinates
        return null
    }

    private fun getDayBounds(day: Int): Rect {
        // Implementation to get day cell bounds
        return Rect()
    }

    private fun selectDay(day: Int) {
        // Handle day selection
        sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_CLICKED)
    }
}
```

---

### 6. Accessibility Events

Send events to inform assistive technologies of changes.

```kotlin
class ProgressIndicator : View {

    var progress: Int = 0
        set(value) {
            val oldValue = field
            field = value

            if (oldValue != value) {
                //  Send progress changed event
                sendAccessibilityEvent(
                    AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED
                )

                // Announce milestone
                if (value == 100) {
                    announceForAccessibility("Progress complete")
                }
            }

            invalidate()
        }

    override fun onInitializeAccessibilityEvent(event: AccessibilityEvent) {
        super.onInitializeAccessibilityEvent(event)

        // Add progress information to event
        event.itemCount = 100
        event.currentItemIndex = progress
    }

    override fun dispatchPopulateAccessibilityEvent(event: AccessibilityEvent): Boolean {
        // Populate event with text
        event.text.add("Progress: $progress percent")
        return true
    }
}
```

---

### 7. Touch Target Size

Ensure touch targets are large enough (minimum 48dp × 48dp).

```kotlin
class AccessibleButton : View {

    private val minTouchTargetSize = 48.dpToPx()

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)

        //  Ensure minimum touch target size
        val width = max(measuredWidth, minTouchTargetSize)
        val height = max(measuredHeight, minTouchTargetSize)

        setMeasuredDimension(width, height)
    }

    // Expand touch area if visual size is smaller
    override fun getHitRect(outRect: Rect) {
        super.getHitRect(outRect)

        val expansion = (minTouchTargetSize - width) / 2
        if (expansion > 0) {
            outRect.inset(-expansion, -expansion)
        }
    }

    private fun Int.dpToPx(): Int =
        (this * resources.displayMetrics.density).toInt()
}
```

---

### 8. Color Contrast

Ensure sufficient color contrast (WCAG AA: 4.5:1, AAA: 7:1).

```kotlin
class AccessibleTextView : View {

    private var textColor: Int = Color.BLACK
    private var backgroundColor: Int = Color.WHITE

    init {
        validateColorContrast()
    }

    private fun validateColorContrast() {
        val contrast = calculateContrastRatio(textColor, backgroundColor)

        if (contrast < 4.5f) {
            Log.w(
                "Accessibility",
                "Insufficient contrast ratio: $contrast (minimum: 4.5)"
            )

            // Optionally auto-adjust
            if (BuildConfig.DEBUG) {
                throw IllegalStateException(
                    "Color contrast too low: $contrast"
                )
            }
        }
    }

    private fun calculateContrastRatio(color1: Int, color2: Int): Float {
        val luminance1 = calculateLuminance(color1)
        val luminance2 = calculateLuminance(color2)

        val lighter = max(luminance1, luminance2)
        val darker = min(luminance1, luminance2)

        return (lighter + 0.05f) / (darker + 0.05f)
    }

    private fun calculateLuminance(color: Int): Float {
        val red = Color.red(color) / 255f
        val green = Color.green(color) / 255f
        val blue = Color.blue(color) / 255f

        val r = if (red <= 0.03928f) red / 12.92f else pow((red + 0.055f) / 1.055f, 2.4f)
        val g = if (green <= 0.03928f) green / 12.92f else pow((green + 0.055f) / 1.055f, 2.4f)
        val b = if (blue <= 0.03928f) blue / 12.92f else pow((blue + 0.055f) / 1.055f, 2.4f)

        return 0.2126f * r + 0.7152f * g + 0.0722f * b
    }
}
```

---

### 9. Complete Accessible Custom View Example

```kotlin
class AccessibleRatingBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    var rating: Int = 0
        set(value) {
            field = value.coerceIn(0, 5)

            //  Update state description
            stateDescription = "$rating out of 5 stars"

            //  Announce change
            announceForAccessibility("Rating changed to $rating stars")

            //  Send accessibility event
            sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SELECTED)

            invalidate()
        }

    var maxRating: Int = 5

    init {
        //  Make focusable and clickable
        isFocusable = true
        isClickable = true
        importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES

        //  Set initial content description
        contentDescription = "Rating bar"
        stateDescription = "$rating out of $maxRating stars"
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        //  Set class for TalkBack
        info.className = RatingBar::class.java.name

        //  Add range info
        info.rangeInfo = AccessibilityNodeInfo.RangeInfo.obtain(
            AccessibilityNodeInfo.RangeInfo.RANGE_TYPE_INT,
            0f,
            maxRating.toFloat(),
            rating.toFloat()
        )

        //  Add actions
        if (rating < maxRating) {
            info.addAction(
                AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD
            )
        }

        if (rating > 0) {
            info.addAction(
                AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_BACKWARD
            )
        }
    }

    override fun performAccessibilityAction(action: Int, arguments: Bundle?): Boolean {
        when (action) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> {
                if (rating < maxRating) {
                    rating++
                    return true
                }
            }

            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> {
                if (rating > 0) {
                    rating--
                    return true
                }
            }
        }

        return super.performAccessibilityAction(action, arguments)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val starSize = width / maxRating.toFloat()

        for (i in 0 until maxRating) {
            val filled = i < rating
            drawStar(canvas, i * starSize, 0f, starSize, filled)
        }
    }

    private fun drawStar(canvas: Canvas, x: Float, y: Float, size: Float, filled: Boolean) {
        // Draw star implementation
    }
}
```

---

### 10. Testing Accessibility

**Manual testing with TalkBack:**
1. Enable TalkBack: Settings → Accessibility → TalkBack
2. Navigate with swipes
3. Verify announcements are clear
4. Test all actions

**Automated testing:**
```kotlin
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testContentDescription() {
        onView(withId(R.id.custom_view))
            .check(matches(withContentDescription("Save button")))
    }

    @Test
    fun testClickable() {
        onView(withId(R.id.custom_view))
            .check(matches(isClickable()))
            .check(matches(isFocusable()))
    }

    @Test
    fun testAccessibilityActions() {
        val view = activityRule.scenario.onActivity { activity ->
            activity.findViewById<CustomSlider>(R.id.slider)
        }

        val info = AccessibilityNodeInfo.obtain(view)
        view.onInitializeAccessibilityNodeInfo(info)

        // Check actions are available
        assertTrue(info.actionList.any {
            it.id == AccessibilityNodeInfo.ACTION_SCROLL_FORWARD
        })
    }
}
```

**Accessibility Scanner:**
- Download Google Accessibility Scanner app
- Scan your app for issues
- Fix highlighted problems

---

### 11. Best Practices Checklist

**Content:**
-  Provide meaningful content descriptions
-  Keep descriptions concise (< 30 words)
-  Update descriptions when content changes
-  Don't include view type in description ("button" is redundant)

**Navigation:**
-  Make interactive elements focusable
-  Provide logical focus order
-  Support keyboard navigation
-  Ensure 48dp × 48dp minimum touch target

**State:**
-  Announce state changes
-  Use stateDescription for current state
-  Send appropriate accessibility events

**Actions:**
-  Expose custom actions via AccessibilityNodeInfo
-  Implement performAccessibilityAction()
-  Provide clear action labels

**Visual:**
-  4.5:1 minimum contrast ratio (WCAG AA)
-  Don't rely on color alone
-  Provide text alternatives for icons
-  Support dynamic text sizing

---

### 12. Common Mistakes

** Missing content description:**
```kotlin
// Bad - no description
val icon = IconView(context)
```

** With content description:**
```kotlin
val icon = IconView(context).apply {
    contentDescription = "Settings"
}
```

** Redundant information:**
```kotlin
contentDescription = "Save button button" // "button" is redundant
```

** Concise description:**
```kotlin
contentDescription = "Save"
```

** Not announcing changes:**
```kotlin
fun updateProgress(value: Int) {
    progress = value // Silent change
}
```

** Announcing changes:**
```kotlin
fun updateProgress(value: Int) {
    progress = value
    announceForAccessibility("Progress: $value percent")
}
```

---

### Summary

**Making custom views accessible:**
1. **Content descriptions** - Describe visual elements
2. **State descriptions** - Describe current state
3. **Accessibility events** - Announce changes
4. **AccessibilityNodeInfo** - Provide detailed info
5. **Touch targets** - Minimum 48dp × 48dp
6. **Color contrast** - Minimum 4.5:1 ratio
7. **Virtual hierarchy** - For complex views

**Key APIs:**
- `contentDescription` - Text alternative
- `stateDescription` - Current state
- `announceForAccessibility()` - TalkBack announcements
- `onInitializeAccessibilityNodeInfo()` - Detailed info
- `performAccessibilityAction()` - Handle actions

**Testing:**
- Manual with TalkBack
- Automated with Espresso
- Accessibility Scanner app
- Real users with disabilities

---

## Ответ (RU)

**Доступность** гарантирует, что ваше приложение можно использовать всем, включая людей с ограниченными возможностями.

### Основные концепции доступности

**1. Content Description (Описание содержимого)**

```kotlin
class IconButton : View {
    init {
        contentDescription = "Кнопка сохранения"
    }

    fun setIcon(type: IconType) {
        contentDescription = when (type) {
            IconType.SAVE -> "Сохранить"
            IconType.DELETE -> "Удалить"
            IconType.EDIT -> "Редактировать"
        }
    }
}
```

**2. State Description (Описание состояния)**

```kotlin
class ToggleSwitch : View {
    var isChecked: Boolean = false
        set(value) {
            field = value
            stateDescription = if (value) "Вкл" else "Выкл"
            announceForAccessibility(
                if (value) "Включено" else "Выключено"
            )
        }
}
```

**3. Custom AccessibilityNodeInfo**

```kotlin
override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
    super.onInitializeAccessibilityNodeInfo(info)

    // Класс для TalkBack
    info.className = SeekBar::class.java.name

    // Информация о диапазоне
    info.rangeInfo = AccessibilityNodeInfo.RangeInfo.obtain(
        AccessibilityNodeInfo.RangeInfo.RANGE_TYPE_FLOAT,
        0f, 100f, currentValue
    )

    // Добавить действия
    info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD)
    info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_BACKWARD)
}
```

### Checklist доступности

-  Предоставить осмысленные content descriptions
-  Сделать интерактивные элементы focusable
-  Объявлять изменения состояния
-  Минимальный размер касания 48dp × 48dp
-  Минимальный контраст 4.5:1
-  Поддержка клавиатурной навигации

### Тестирование

- Ручное тестирование с TalkBack
- Автоматизированное тестирование с Espresso
- Приложение Accessibility Scanner
- Реальные пользователи с ограниченными возможностями

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-accessibility-compose--accessibility--medium]] - Accessibility
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View
- [[q-what-is-viewmodel--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View

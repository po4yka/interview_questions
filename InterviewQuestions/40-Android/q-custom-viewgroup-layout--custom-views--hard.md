---
id: 20251017-104944
title: "Custom Viewgroup Layout / Layout кастомных ViewGroup"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: [views, viewgroup, layout, android-framework, difficulty/hard]
---
# Custom ViewGroup and Layout

# Question (EN)
> How do you create a custom ViewGroup? Explain the measurement and layout process. Implement a custom FlowLayout that arranges children in rows, wrapping to the next row when needed.

# Вопрос (RU)
> Как создать пользовательский ViewGroup? Объясните процесс измерения и компоновки. Реализуйте пользовательский FlowLayout, который располагает дочерние элементы в ряды, переносясь на следующий ряд при необходимости.

---

## Answer (EN)

Creating a **custom ViewGroup** is more complex than a simple custom View because you need to handle both your own measurement/layout AND the measurement/layout of all child views. This requires understanding the two-pass layout algorithm.

### ViewGroup Layout Process

```
Parent ViewGroup
    ↓
1. onMeasure() - Measure all children, then measure self
    ↓
2. onLayout() - Position all children based on measurements
    ↓
Children are measured and positioned
```

---

### Key Concepts

**1. Measure pass** (onMeasure):
- Parent measures each child with `child.measure()`
- Parent then measures itself based on children's sizes
- Must call `setMeasuredDimension()`

**2. Layout pass** (onLayout):
- Parent positions each child with `child.layout()`
- Children receive their position in parent coordinates

---

### Basic Custom ViewGroup Template

```kotlin
class BasicCustomLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Step 1: Measure all children
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility != GONE) {
                measureChild(child, widthMeasureSpec, heightMeasureSpec)
            }
        }

        // Step 2: Calculate own size based on children
        val desiredWidth = calculateDesiredWidth()
        val desiredHeight = calculateDesiredHeight()

        // Step 3: Resolve size and set
        setMeasuredDimension(
            resolveSize(desiredWidth, widthMeasureSpec),
            resolveSize(desiredHeight, heightMeasureSpec)
        )
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        // Position each child
        var currentX = paddingLeft
        var currentY = paddingTop

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility != GONE) {
                child.layout(
                    currentX,
                    currentY,
                    currentX + child.measuredWidth,
                    currentY + child.measuredHeight
                )
                currentX += child.measuredWidth
            }
        }
    }

    private fun calculateDesiredWidth(): Int {
        // Implementation depends on layout logic
        return 0
    }

    private fun calculateDesiredHeight(): Int {
        // Implementation depends on layout logic
        return 0
    }
}
```

---

### Complete FlowLayout Implementation

A **FlowLayout** arranges children in horizontal rows, wrapping to the next row when there's not enough space (like HTML flexbox with flex-wrap).

```kotlin
/**
 * FlowLayout - Arranges children in rows, wrapping when needed
 *
 * Features:
 * - Automatic row wrapping
 * - Horizontal and vertical spacing
 * - Support for margins
 * - Respects child visibility (GONE children are skipped)
 */
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    // Spacing between children
    var horizontalSpacing: Int = 0
        set(value) {
            field = value
            requestLayout()
        }

    var verticalSpacing: Int = 0
        set(value) {
            field = value
            requestLayout()
        }

    init {
        // Read custom attributes
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.FlowLayout,
            defStyleAttr,
            0
        ).apply {
            try {
                horizontalSpacing = getDimensionPixelSize(
                    R.styleable.FlowLayout_horizontalSpacing,
                    0
                )
                verticalSpacing = getDimensionPixelSize(
                    R.styleable.FlowLayout_verticalSpacing,
                    0
                )
            } finally {
                recycle()
            }
        }
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)
        val heightMode = MeasureSpec.getMode(heightMeasureSpec)
        val heightSize = MeasureSpec.getSize(heightMeasureSpec)

        // Calculate available width for children
        val availableWidth = if (widthMode == MeasureSpec.UNSPECIFIED) {
            Int.MAX_VALUE
        } else {
            widthSize - paddingLeft - paddingRight
        }

        var currentRowWidth = 0
        var currentRowHeight = 0
        var totalWidth = 0
        var totalHeight = 0

        // Measure each child and calculate total dimensions
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            // Measure child with available space
            measureChildWithMargins(
                child,
                widthMeasureSpec,
                0,
                heightMeasureSpec,
                totalHeight
            )

            val childWidth = child.measuredWidth + child.marginLeft + child.marginRight
            val childHeight = child.measuredHeight + child.marginTop + child.marginBottom

            // Check if we need to wrap to next row
            if (currentRowWidth + childWidth > availableWidth && currentRowWidth > 0) {
                // Start new row
                totalWidth = max(totalWidth, currentRowWidth - horizontalSpacing)
                totalHeight += currentRowHeight + verticalSpacing

                currentRowWidth = childWidth + horizontalSpacing
                currentRowHeight = childHeight
            } else {
                // Add to current row
                currentRowWidth += childWidth + horizontalSpacing
                currentRowHeight = max(currentRowHeight, childHeight)
            }
        }

        // Add final row
        totalWidth = max(totalWidth, currentRowWidth - horizontalSpacing)
        totalHeight += currentRowHeight

        // Add padding
        totalWidth += paddingLeft + paddingRight
        totalHeight += paddingTop + paddingBottom

        // Resolve final dimensions
        val finalWidth = when (widthMode) {
            MeasureSpec.EXACTLY -> widthSize
            MeasureSpec.AT_MOST -> min(totalWidth, widthSize)
            else -> totalWidth
        }

        val finalHeight = when (heightMode) {
            MeasureSpec.EXACTLY -> heightSize
            MeasureSpec.AT_MOST -> min(totalHeight, heightSize)
            else -> totalHeight
        }

        setMeasuredDimension(finalWidth, finalHeight)
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        val availableWidth = right - left - paddingLeft - paddingRight

        var currentX = paddingLeft
        var currentY = paddingTop
        var currentRowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val childWidth = child.measuredWidth
            val childHeight = child.measuredHeight
            val lp = child.layoutParams as MarginLayoutParams

            val totalChildWidth = childWidth + lp.leftMargin + lp.rightMargin

            // Check if we need to wrap
            if (currentX + totalChildWidth > paddingLeft + availableWidth && currentX > paddingLeft) {
                // Move to next row
                currentX = paddingLeft
                currentY += currentRowHeight + verticalSpacing
                currentRowHeight = 0
            }

            // Position child
            val childLeft = currentX + lp.leftMargin
            val childTop = currentY + lp.topMargin

            child.layout(
                childLeft,
                childTop,
                childLeft + childWidth,
                childTop + childHeight
            )

            // Update position for next child
            currentX += totalChildWidth + horizontalSpacing
            currentRowHeight = max(
                currentRowHeight,
                childHeight + lp.topMargin + lp.bottomMargin
            )
        }
    }

    // Support for margins
    override fun generateLayoutParams(attrs: AttributeSet?): LayoutParams {
        return MarginLayoutParams(context, attrs)
    }

    override fun generateDefaultLayoutParams(): LayoutParams {
        return MarginLayoutParams(
            LayoutParams.WRAP_CONTENT,
            LayoutParams.WRAP_CONTENT
        )
    }

    override fun generateLayoutParams(p: LayoutParams?): LayoutParams {
        return MarginLayoutParams(p)
    }

    override fun checkLayoutParams(p: LayoutParams?): Boolean {
        return p is MarginLayoutParams
    }
}
```

**attrs.xml:**
```xml
<resources>
    <declare-styleable name="FlowLayout">
        <attr name="horizontalSpacing" format="dimension" />
        <attr name="verticalSpacing" format="dimension" />
    </declare-styleable>
</resources>
```

---

### Usage Example

**XML:**
```xml
<com.example.ui.FlowLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:horizontalSpacing="8dp"
    app:verticalSpacing="8dp"
    android:padding="16dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Tag 1"
        android:background="@drawable/tag_background" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Tag 2"
        android:background="@drawable/tag_background" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Very Long Tag 3"
        android:background="@drawable/tag_background" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Tag 4"
        android:background="@drawable/tag_background" />
</com.example.ui.FlowLayout>
```

**Programmatic:**
```kotlin
val flowLayout = FlowLayout(context).apply {
    horizontalSpacing = 8.dpToPx()
    verticalSpacing = 8.dpToPx()
    layoutParams = LinearLayout.LayoutParams(
        LinearLayout.LayoutParams.MATCH_PARENT,
        LinearLayout.LayoutParams.WRAP_CONTENT
    )
}

// Add tags dynamically
val tags = listOf("Android", "Kotlin", "Jetpack Compose", "Coroutines", "Flow")
tags.forEach { tag ->
    val textView = TextView(context).apply {
        text = tag
        setBackgroundResource(R.drawable.tag_background)
        setPadding(16, 8, 16, 8)
    }
    flowLayout.addView(textView)
}
```

---

### Advanced: Custom LayoutParams

Add custom layout parameters for more control:

```kotlin
class FlowLayoutAdvanced @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    // Custom LayoutParams with gravity support
    class LayoutParams : MarginLayoutParams {
        var gravity: Int = Gravity.TOP or Gravity.START

        constructor(c: Context, attrs: AttributeSet?) : super(c, attrs) {
            val a = c.obtainStyledAttributes(attrs, R.styleable.FlowLayout_Layout)
            gravity = a.getInt(R.styleable.FlowLayout_Layout_android_layout_gravity, gravity)
            a.recycle()
        }

        constructor(width: Int, height: Int) : super(width, height)
        constructor(source: ViewGroup.LayoutParams) : super(source)
    }

    override fun generateLayoutParams(attrs: AttributeSet?): ViewGroup.LayoutParams {
        return LayoutParams(context, attrs)
    }

    override fun generateDefaultLayoutParams(): ViewGroup.LayoutParams {
        return LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)
    }

    override fun generateLayoutParams(p: ViewGroup.LayoutParams?): ViewGroup.LayoutParams {
        return LayoutParams(p)
    }

    override fun checkLayoutParams(p: ViewGroup.LayoutParams?): Boolean {
        return p is LayoutParams
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        // Use custom LayoutParams for positioning
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            val lp = child.layoutParams as LayoutParams

            // Apply gravity
            val childLeft = when (lp.gravity and Gravity.HORIZONTAL_GRAVITY_MASK) {
                Gravity.CENTER_HORIZONTAL -> (width - child.measuredWidth) / 2
                Gravity.END -> width - child.measuredWidth
                else -> 0
            }

            // Position child...
        }
    }
}
```

---

### Real-World Example: StaggeredLayout

A more complex layout that creates Pinterest-style staggered grid:

```kotlin
class StaggeredLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    var columnCount: Int = 2
        set(value) {
            field = value
            requestLayout()
        }

    var spacing: Int = 0
        set(value) {
            field = value
            requestLayout()
        }

    // Track height of each column
    private val columnHeights = IntArray(2)

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val width = MeasureSpec.getSize(widthMeasureSpec) - paddingLeft - paddingRight
        val columnWidth = (width - spacing * (columnCount - 1)) / columnCount

        // Reset column heights
        columnHeights.fill(0)

        // Measure each child
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            // Measure child with column width
            val childWidthSpec = MeasureSpec.makeMeasureSpec(
                columnWidth,
                MeasureSpec.EXACTLY
            )
            val childHeightSpec = MeasureSpec.makeMeasureSpec(
                0,
                MeasureSpec.UNSPECIFIED
            )

            child.measure(childWidthSpec, childHeightSpec)

            // Find shortest column
            val shortestColumn = columnHeights.indices.minByOrNull { columnHeights[it] } ?: 0

            // Add child height to column
            columnHeights[shortestColumn] += child.measuredHeight + spacing
        }

        // Total height is the tallest column
        val totalHeight = (columnHeights.maxOrNull() ?: 0) + paddingTop + paddingBottom

        setMeasuredDimension(
            MeasureSpec.getSize(widthMeasureSpec),
            resolveSize(totalHeight, heightMeasureSpec)
        )
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        val width = right - left - paddingLeft - paddingRight
        val columnWidth = (width - spacing * (columnCount - 1)) / columnCount

        // Reset column positions
        val columnPositions = IntArray(columnCount) { paddingTop }

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            // Find shortest column
            val shortestColumn = columnPositions.indices.minByOrNull { columnPositions[it] } ?: 0

            // Calculate child position
            val childLeft = paddingLeft + shortestColumn * (columnWidth + spacing)
            val childTop = columnPositions[shortestColumn]

            // Position child
            child.layout(
                childLeft,
                childTop,
                childLeft + columnWidth,
                childTop + child.measuredHeight
            )

            // Update column position
            columnPositions[shortestColumn] += child.measuredHeight + spacing
        }
    }
}
```

**Usage:**
```xml
<com.example.ui.StaggeredLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:columnCount="2"
    app:spacing="8dp">

    <ImageView
        android:layout_width="match_parent"
        android:layout_height="200dp"
        android:scaleType="centerCrop"
        android:src="@drawable/image1" />

    <ImageView
        android:layout_width="match_parent"
        android:layout_height="300dp"
        android:scaleType="centerCrop"
        android:src="@drawable/image2" />

    <!-- More images... -->
</com.example.ui.StaggeredLayout>
```

---

### Measurement Helper Methods

**Available helper methods:**

```kotlin
// 1. measureChild - Simple measurement
measureChild(child, widthMeasureSpec, heightMeasureSpec)

// 2. measureChildWithMargins - Respects margins
measureChildWithMargins(
    child,
    widthMeasureSpec, usedWidth,
    heightMeasureSpec, usedHeight
)

// 3. Manual measurement - Full control
val childWidthSpec = MeasureSpec.makeMeasureSpec(
    desiredWidth,
    MeasureSpec.EXACTLY
)
val childHeightSpec = MeasureSpec.makeMeasureSpec(
    desiredHeight,
    MeasureSpec.AT_MOST
)
child.measure(childWidthSpec, childHeightSpec)
```

**Comparison:**

| Method | Respects Padding | Respects Margins | Use Case |
|--------|-----------------|------------------|----------|
| `measureChild` |  Yes |  No | Simple layouts |
| `measureChildWithMargins` |  Yes |  Yes | Most layouts |
| Manual `measure()` |  No |  No | Full control |

---

### Best Practices

**1. Always measure children before self**
```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    //  Measure children first
    for (i in 0 until childCount) {
        measureChild(getChildAt(i), widthMeasureSpec, heightMeasureSpec)
    }

    // Then calculate own size based on children
    val width = calculateWidth()
    val height = calculateHeight()
    setMeasuredDimension(width, height)
}
```

**2. Skip GONE children**
```kotlin
for (i in 0 until childCount) {
    val child = getChildAt(i)
    if (child.visibility == GONE) continue //  Skip
    // Process child
}
```

**3. Use resolveSize for wrap_content/match_parent**
```kotlin
//  DO
setMeasuredDimension(
    resolveSize(desiredWidth, widthMeasureSpec),
    resolveSize(desiredHeight, heightMeasureSpec)
)

//  DON'T ignore measure spec
setMeasuredDimension(desiredWidth, desiredHeight)
```

**4. Support RTL layouts**
```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    val isRtl = layoutDirection == LAYOUT_DIRECTION_RTL

    for (i in 0 until childCount) {
        val child = getChildAt(i)

        val childLeft = if (isRtl) {
            width - currentX - child.measuredWidth
        } else {
            currentX
        }

        child.layout(childLeft, currentY, /* ... */)
    }
}
```

**5. Optimize for performance**
```kotlin
class OptimizedViewGroup : ViewGroup {
    // Cache to avoid repeated allocations
    private val childBounds = mutableListOf<Rect>()

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Clear and reuse list
        childBounds.clear()

        for (i in 0 until childCount) {
            // Measure and cache bounds
            val child = getChildAt(i)
            measureChild(child, widthMeasureSpec, heightMeasureSpec)

            val bounds = Rect(0, 0, child.measuredWidth, child.measuredHeight)
            childBounds.add(bounds)
        }

        setMeasuredDimension(/* ... */)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // Use cached bounds
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            val bounds = childBounds[i]
            child.layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
        }
    }
}
```

---

### Common Pitfalls

** Forgetting to call setMeasuredDimension()**
```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Measure children...
    // CRASH! Must call setMeasuredDimension()
}
```

** Not measuring children**
```kotlin
override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    val child = getChildAt(0)
    // child.measuredWidth is 0! Must call measure() in onMeasure()
    child.layout(0, 0, child.measuredWidth, child.measuredHeight)
}
```

** Calling requestLayout() in onLayout()**
```kotlin
override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    // ...
    requestLayout() // INFINITE LOOP!
}
```

---

### Testing Custom ViewGroup

```kotlin
@RunWith(AndroidJUnit4::class)
class FlowLayoutTest {

    @Test
    fun testMeasurement() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val flowLayout = FlowLayout(context)

        // Add children
        repeat(5) {
            val child = View(context).apply {
                layoutParams = ViewGroup.LayoutParams(100, 100)
            }
            flowLayout.addView(child)
        }

        // Measure with 300px width
        val widthSpec = MeasureSpec.makeMeasureSpec(300, MeasureSpec.EXACTLY)
        val heightSpec = MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)

        flowLayout.measure(widthSpec, heightSpec)

        // Should wrap to 2 rows (3 + 2 children)
        // Row 1: 300px, Row 2: 200px
        assertEquals(300, flowLayout.measuredWidth)
        assertTrue(flowLayout.measuredHeight >= 200)
    }

    @Test
    fun testLayout() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val flowLayout = FlowLayout(context).apply {
            horizontalSpacing = 10
        }

        val child1 = View(context).apply {
            layoutParams = ViewGroup.LayoutParams(100, 50)
        }
        val child2 = View(context).apply {
            layoutParams = ViewGroup.LayoutParams(100, 50)
        }

        flowLayout.addView(child1)
        flowLayout.addView(child2)

        flowLayout.measure(
            MeasureSpec.makeMeasureSpec(300, MeasureSpec.EXACTLY),
            MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)
        )
        flowLayout.layout(0, 0, 300, flowLayout.measuredHeight)

        // Check positions
        assertEquals(0, child1.left)
        assertEquals(110, child2.left) // 100 + 10 spacing
    }
}
```

---

### Summary

**Creating a custom ViewGroup:**

1. **Override onMeasure()**
   - Measure all children
   - Calculate own size
   - Call `setMeasuredDimension()`

2. **Override onLayout()**
   - Position all children with `child.layout()`
   - Use measured dimensions from onMeasure

3. **Support LayoutParams**
   - Override `generateLayoutParams()` methods
   - Support MarginLayoutParams or custom params

**Key rules:**
- Always measure children before self
- Always call `setMeasuredDimension()`
- Skip GONE children
- Use `resolveSize()` for wrap_content
- Support RTL layouts
- Cache calculations for performance

**Helper methods:**
- `measureChild()` - Simple measurement
- `measureChildWithMargins()` - Respects margins
- `resolveSize()` - Resolve final size from spec

---

## Ответ (RU)

Создание **пользовательского ViewGroup** сложнее, чем простого пользовательского View, потому что вам нужно обрабатывать как собственное измерение/расположение, так и измерение/расположение всех дочерних представлений. Это требует понимания двухпроходного алгоритма компоновки.

### Процесс компоновки ViewGroup

```
Родительский ViewGroup
    ↓
1. onMeasure() - Измерить всех дочерних элементов, затем измерить себя
    ↓
2. onLayout() - Расположить все дочерние элементы на основе измерений
    ↓
Дочерние элементы измерены и расположены
```

---

### Ключевые концепции

**1. Проход измерения** (onMeasure):
- Родитель измеряет каждый дочерний элемент с помощью `child.measure()`
- Затем родитель измеряет себя на основе размеров дочерних элементов
- Необходимо вызвать `setMeasuredDimension()`

**2. Проход компоновки** (onLayout):
- Родитель располагает каждый дочерний элемент с помощью `child.layout()`
- Дочерние элементы получают свою позицию в координатах родителя

---

### Базовый шаблон пользовательского ViewGroup

```kotlin
class BasicCustomLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Шаг 1: Измерить все дочерние элементы
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility != GONE) {
                measureChild(child, widthMeasureSpec, heightMeasureSpec)
            }
        }

        // Шаг 2: Рассчитать собственный размер на основе дочерних элементов
        val desiredWidth = calculateDesiredWidth()
        val desiredHeight = calculateDesiredHeight()

        // Шаг 3: Определить и установить размер
        setMeasuredDimension(
            resolveSize(desiredWidth, widthMeasureSpec),
            resolveSize(desiredHeight, heightMeasureSpec)
        )
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        // Расположить каждый дочерний элемент
        var currentX = paddingLeft
        var currentY = paddingTop

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility != GONE) {
                child.layout(
                    currentX,
                    currentY,
                    currentX + child.measuredWidth,
                    currentY + child.measuredHeight
                )
                currentX += child.measuredWidth
            }
        }
    }

    private fun calculateDesiredWidth(): Int {
        // Реализация зависит от логики компоновки
        return 0
    }

    private fun calculateDesiredHeight(): Int {
        // Реализация зависит от логики компоновки
        return 0
    }
}
```

---

### Полная реализация FlowLayout

**FlowLayout** располагает дочерние элементы в горизонтальные ряды, перенося их на следующий ряд, когда не хватает места (подобно flexbox в HTML с flex-wrap).

```kotlin
/**
 * FlowLayout - Располагает дочерние элементы в ряды, с переносом при необходимости
 *
 * Особенности:
 * - Автоматический перенос на новый ряд
 * - Горизонтальные и вертикальные отступы
 * - Поддержка margins
 * - Учитывает видимость дочерних элементов (пропускает GONE)
 */
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    // Отступы между дочерними элементами
    var horizontalSpacing: Int = 0
        set(value) {
            field = value
            requestLayout()
        }

    var verticalSpacing: Int = 0
        set(value) {
            field = value
            requestLayout()
        }

    init {
        // Чтение пользовательских атрибутов
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.FlowLayout,
            defStyleAttr,
            0
        ).apply {
            try {
                horizontalSpacing = getDimensionPixelSize(
                    R.styleable.FlowLayout_horizontalSpacing,
                    0
                )
                verticalSpacing = getDimensionPixelSize(
                    R.styleable.FlowLayout_verticalSpacing,
                    0
                )
            } finally {
                recycle()
            }
        }
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)
        val heightMode = MeasureSpec.getMode(heightMeasureSpec)
        val heightSize = MeasureSpec.getSize(heightMeasureSpec)

        // Рассчитать доступную ширину для дочерних элементов
        val availableWidth = if (widthMode == MeasureSpec.UNSPECIFIED) {
            Int.MAX_VALUE
        } else {
            widthSize - paddingLeft - paddingRight
        }

        var currentRowWidth = 0
        var currentRowHeight = 0
        var totalWidth = 0
        var totalHeight = 0

        // Измерить каждый дочерний элемент и рассчитать общие размеры
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            // Измерить дочерний элемент с доступным пространством
            measureChildWithMargins(
                child,
                widthMeasureSpec,
                0,
                heightMeasureSpec,
                totalHeight
            )

            val childWidth = child.measuredWidth + child.marginLeft + child.marginRight
            val childHeight = child.measuredHeight + child.marginTop + child.marginBottom

            // Проверить нужно ли переносить на следующий ряд
            if (currentRowWidth + childWidth > availableWidth && currentRowWidth > 0) {
                // Начать новый ряд
                totalWidth = max(totalWidth, currentRowWidth - horizontalSpacing)
                totalHeight += currentRowHeight + verticalSpacing

                currentRowWidth = childWidth + horizontalSpacing
                currentRowHeight = childHeight
            } else {
                // Добавить в текущий ряд
                currentRowWidth += childWidth + horizontalSpacing
                currentRowHeight = max(currentRowHeight, childHeight)
            }
        }

        // Добавить последний ряд
        totalWidth = max(totalWidth, currentRowWidth - horizontalSpacing)
        totalHeight += currentRowHeight

        // Добавить отступы (padding)
        totalWidth += paddingLeft + paddingRight
        totalHeight += paddingTop + paddingBottom

        // Разрешить финальные размеры
        val finalWidth = when (widthMode) {
            MeasureSpec.EXACTLY -> widthSize
            MeasureSpec.AT_MOST -> min(totalWidth, widthSize)
            else -> totalWidth
        }

        val finalHeight = when (heightMode) {
            MeasureSpec.EXACTLY -> heightSize
            MeasureSpec.AT_MOST -> min(totalHeight, heightSize)
            else -> totalHeight
        }

        setMeasuredDimension(finalWidth, finalHeight)
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        val availableWidth = right - left - paddingLeft - paddingRight

        var currentX = paddingLeft
        var currentY = paddingTop
        var currentRowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val childWidth = child.measuredWidth
            val childHeight = child.measuredHeight
            val lp = child.layoutParams as MarginLayoutParams

            val totalChildWidth = childWidth + lp.leftMargin + lp.rightMargin

            // Проверить нужен ли перенос
            if (currentX + totalChildWidth > paddingLeft + availableWidth && currentX > paddingLeft) {
                // Переместиться на следующий ряд
                currentX = paddingLeft
                currentY += currentRowHeight + verticalSpacing
                currentRowHeight = 0
            }

            // Расположить дочерний элемент
            val childLeft = currentX + lp.leftMargin
            val childTop = currentY + lp.topMargin

            child.layout(
                childLeft,
                childTop,
                childLeft + childWidth,
                childTop + childHeight
            )

            // Обновить позицию для следующего дочернего элемента
            currentX += totalChildWidth + horizontalSpacing
            currentRowHeight = max(
                currentRowHeight,
                childHeight + lp.topMargin + lp.bottomMargin
            )
        }
    }

    // Поддержка margins
    override fun generateLayoutParams(attrs: AttributeSet?): LayoutParams {
        return MarginLayoutParams(context, attrs)
    }

    override fun generateDefaultLayoutParams(): LayoutParams {
        return MarginLayoutParams(
            LayoutParams.WRAP_CONTENT,
            LayoutParams.WRAP_CONTENT
        )
    }

    override fun generateLayoutParams(p: LayoutParams?): LayoutParams {
        return MarginLayoutParams(p)
    }

    override fun checkLayoutParams(p: LayoutParams?): Boolean {
        return p is MarginLayoutParams
    }
}
```

**attrs.xml:**
```xml
<resources>
    <declare-styleable name="FlowLayout">
        <attr name="horizontalSpacing" format="dimension" />
        <attr name="verticalSpacing" format="dimension" />
    </declare-styleable>
</resources>
```

---

### Пример использования

**XML:**
```xml
<com.example.ui.FlowLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:horizontalSpacing="8dp"
    app:verticalSpacing="8dp"
    android:padding="16dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Тег 1"
        android:background="@drawable/tag_background" />
    <!-- ... -->
</com.example.ui.FlowLayout>
```

**Программно:**
```kotlin
// ... (код как в английской версии)
```

---

### Продвинутый уровень: Пользовательские LayoutParams

Добавьте пользовательские параметры компоновки для большего контроля:

```kotlin
class FlowLayoutAdvanced @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    // Пользовательские LayoutParams с поддержкой gravity
    class LayoutParams : MarginLayoutParams {
        var gravity: Int = Gravity.TOP or Gravity.START

        constructor(c: Context, attrs: AttributeSet?) : super(c, attrs) {
            val a = c.obtainStyledAttributes(attrs, R.styleable.FlowLayout_Layout)
            gravity = a.getInt(R.styleable.FlowLayout_Layout_android_layout_gravity, gravity)
            a.recycle()
        }

        constructor(width: Int, height: Int) : super(width, height)
        constructor(source: ViewGroup.LayoutParams) : super(source)
    }

    override fun generateLayoutParams(attrs: AttributeSet?): ViewGroup.LayoutParams {
        return LayoutParams(context, attrs)
    }

    override fun generateDefaultLayoutParams(): ViewGroup.LayoutParams {
        return LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)
    }

    override fun generateLayoutParams(p: ViewGroup.LayoutParams?): ViewGroup.LayoutParams {
        return LayoutParams(p)
    }

    override fun checkLayoutParams(p: ViewGroup.LayoutParams?): Boolean {
        return p is LayoutParams
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Реализация измерения
        setMeasuredDimension(0, 0)
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        // Использовать пользовательские LayoutParams для позиционирования
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            val lp = child.layoutParams as LayoutParams

            // Применить gravity
            val childLeft = when (lp.gravity and Gravity.HORIZONTAL_GRAVITY_MASK) {
                Gravity.CENTER_HORIZONTAL -> (width - child.measuredWidth) / 2
                Gravity.END -> width - child.measuredWidth
                else -> 0
            }

            // Расположить дочерний элемент...
        }
    }
}
```

---

### Реальный пример: StaggeredLayout

Более сложная компоновка, создающая сетку в стиле Pinterest:

```kotlin
class StaggeredLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    var columnCount: Int = 2
        set(value) {
            field = value
            requestLayout()
        }

    var spacing: Int = 0
        set(value) {
            field = value
            requestLayout()
        }

    // Отслеживание высоты каждого столбца
    private val columnHeights = IntArray(2)

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val width = MeasureSpec.getSize(widthMeasureSpec) - paddingLeft - paddingRight
        val columnWidth = (width - spacing * (columnCount - 1)) / columnCount

        // Сбросить высоты столбцов
        columnHeights.fill(0)

        // Измерить каждый дочерний элемент
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            // Измерить дочерний элемент с шириной столбца
            val childWidthSpec = MeasureSpec.makeMeasureSpec(
                columnWidth,
                MeasureSpec.EXACTLY
            )
            val childHeightSpec = MeasureSpec.makeMeasureSpec(
                0,
                MeasureSpec.UNSPECIFIED
            )

            child.measure(childWidthSpec, childHeightSpec)

            // Найти самый короткий столбец
            val shortestColumn = columnHeights.indices.minByOrNull { columnHeights[it] } ?: 0

            // Добавить высоту дочернего элемента к столбцу
            columnHeights[shortestColumn] += child.measuredHeight + spacing
        }

        // Общая высота - это самый высокий столбец
        val totalHeight = (columnHeights.maxOrNull() ?: 0) + paddingTop + paddingBottom

        setMeasuredDimension(
            MeasureSpec.getSize(widthMeasureSpec),
            resolveSize(totalHeight, heightMeasureSpec)
        )
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        val width = right - left - paddingLeft - paddingRight
        val columnWidth = (width - spacing * (columnCount - 1)) / columnCount

        // Сбросить позиции столбцов
        val columnPositions = IntArray(columnCount) { paddingTop }

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            // Найти самый короткий столбец
            val shortestColumn = columnPositions.indices.minByOrNull { columnPositions[it] } ?: 0

            // Вычислить позицию дочернего элемента
            val childLeft = paddingLeft + shortestColumn * (columnWidth + spacing)
            val childTop = columnPositions[shortestColumn]

            // Расположить дочерний элемент
            child.layout(
                childLeft,
                childTop,
                childLeft + columnWidth,
                childTop + child.measuredHeight
            )

            // Обновить позицию столбца
            columnPositions[shortestColumn] += child.measuredHeight + spacing
        }
    }
}
```

**Использование:**
```xml
<com.example.ui.StaggeredLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:columnCount="2"
    app:spacing="8dp">

    <ImageView
        android:layout_width="match_parent"
        android:layout_height="200dp"
        android:scaleType="centerCrop"
        android:src="@drawable/image1" />

    <ImageView
        android:layout_width="match_parent"
        android:layout_height="300dp"
        android:scaleType="centerCrop"
        android:src="@drawable/image2" />

    <!-- Больше изображений... -->
</com.example.ui.StaggeredLayout>
```

---

### Вспомогательные методы измерения

**Доступные вспомогательные методы:**

```kotlin
// 1. measureChild - Простое измерение
measureChild(child, widthMeasureSpec, heightMeasureSpec)

// 2. measureChildWithMargins - Учитывает margins
measureChildWithMargins(
    child,
    widthMeasureSpec, usedWidth,
    heightMeasureSpec, usedHeight
)

// 3. Ручное измерение - Полный контроль
val childWidthSpec = MeasureSpec.makeMeasureSpec(
    desiredWidth,
    MeasureSpec.EXACTLY
)
val childHeightSpec = MeasureSpec.makeMeasureSpec(
    desiredHeight,
    MeasureSpec.AT_MOST
)
child.measure(childWidthSpec, childHeightSpec)
```

**Сравнение:**

| Метод | Учитывает Padding | Учитывает Margins | Случай использования |
|--------|-----------------|------------------|----------|
| `measureChild` | Да | Нет | Простые компоновки |
| `measureChildWithMargins` | Да | Да | Большинство компоновок |
| Ручной `measure()` | Нет | Нет | Полный контроль |

---

### Лучшие практики

**1. Всегда измеряйте дочерние элементы перед родительским**
```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Сначала измерить дочерние элементы
    for (i in 0 until childCount) {
        measureChild(getChildAt(i), widthMeasureSpec, heightMeasureSpec)
    }

    // Затем рассчитать собственный размер на основе дочерних элементов
    val width = calculateWidth()
    val height = calculateHeight()
    setMeasuredDimension(width, height)
}
```

**2. Пропускайте дочерние элементы с видимостью GONE**
```kotlin
for (i in 0 until childCount) {
    val child = getChildAt(i)
    if (child.visibility == GONE) continue // Пропустить
    // Обработать дочерний элемент
}
```

**3. Используйте `resolveSize` для `wrap_content`/`match_parent`**
```kotlin
// ДЕЛАЙТЕ
setMeasuredDimension(
    resolveSize(desiredWidth, widthMeasureSpec),
    resolveSize(desiredHeight, heightMeasureSpec)
)

// НЕ ДЕЛАЙТЕ - игнорирование measure spec
setMeasuredDimension(desiredWidth, desiredHeight)
```

**4. Поддерживайте RTL-компоновки**
```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    val isRtl = layoutDirection == LAYOUT_DIRECTION_RTL

    for (i in 0 until childCount) {
        val child = getChildAt(i)

        val childLeft = if (isRtl) {
            width - currentX - child.measuredWidth
        } else {
            currentX
        }

        child.layout(childLeft, currentY, /* ... */)
    }
}
```

**5. Оптимизируйте производительность**
```kotlin
class OptimizedViewGroup : ViewGroup {
    // Кэш для избежания повторных выделений
    private val childBounds = mutableListOf<Rect>()

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Очистить и переиспользовать список
        childBounds.clear()

        for (i in 0 until childCount) {
            // Измерить и закэшировать границы
            val child = getChildAt(i)
            measureChild(child, widthMeasureSpec, heightMeasureSpec)

            val bounds = Rect(0, 0, child.measuredWidth, child.measuredHeight)
            childBounds.add(bounds)
        }

        setMeasuredDimension(/* ... */)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // Использовать закэшированные границы
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            val bounds = childBounds[i]
            child.layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
        }
    }
}
```

---

### Распространенные ошибки

**Забыли вызвать `setMeasuredDimension()`**
```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Измерить дочерние элементы...
    // КРАХ! Необходимо вызвать setMeasuredDimension()
}
```

**Не измерили дочерние элементы**
```kotlin
override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    val child = getChildAt(0)
    // child.measuredWidth равен 0! Необходимо вызвать measure() в onMeasure()
    child.layout(0, 0, child.measuredWidth, child.measuredHeight)
}
```

**Вызов `requestLayout()` в `onLayout()`**
```kotlin
override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    // ...
    requestLayout() // БЕСКОНЕЧНЫЙ ЦИКЛ!
}
```

---

### Тестирование пользовательского ViewGroup

```kotlin
@RunWith(AndroidJUnit4::class)
class FlowLayoutTest {

    @Test
    fun testMeasurement() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val flowLayout = FlowLayout(context)

        // Добавить дочерние элементы
        repeat(5) {
            val child = View(context).apply {
                layoutParams = ViewGroup.LayoutParams(100, 100)
            }
            flowLayout.addView(child)
        }

        // Измерить с шириной 300px
        val widthSpec = MeasureSpec.makeMeasureSpec(300, MeasureSpec.EXACTLY)
        val heightSpec = MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)

        flowLayout.measure(widthSpec, heightSpec)

        // Должен перенестись на 2 ряда (3 + 2 дочерних элемента)
        // Ряд 1: 300px, Ряд 2: 200px
        assertEquals(300, flowLayout.measuredWidth)
        assertTrue(flowLayout.measuredHeight >= 200)
    }

    @Test
    fun testLayout() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val flowLayout = FlowLayout(context).apply {
            horizontalSpacing = 10
        }

        val child1 = View(context).apply {
            layoutParams = ViewGroup.LayoutParams(100, 50)
        }
        val child2 = View(context).apply {
            layoutParams = ViewGroup.LayoutParams(100, 50)
        }

        flowLayout.addView(child1)
        flowLayout.addView(child2)

        flowLayout.measure(
            MeasureSpec.makeMeasureSpec(300, MeasureSpec.EXACTLY),
            MeasureSpec.makeMeasureSpec(0, MeasureSpec.UNSPECIFIED)
        )
        flowLayout.layout(0, 0, 300, flowLayout.measuredHeight)

        // Проверить позиции
        assertEquals(0, child1.left)
        assertEquals(110, child2.left) // 100 + 10 spacing
    }
}
```

---

### Резюме

**Создание пользовательского ViewGroup:**

1.  **Переопределите `onMeasure()`**
    *   Измерьте все дочерние элементы
    *   Рассчитайте собственный размер
    *   Вызовите `setMeasuredDimension()`
2.  **Переопределите `onLayout()`**
    *   Расположите все дочерние элементы с помощью `child.layout()`
    *   Используйте измеренные размеры из `onMeasure`
3.  **Поддерживайте `LayoutParams`**
    *   Переопределите методы `generateLayoutParams()`
    *   Поддерживайте `MarginLayoutParams` или пользовательские параметры

**Ключевые правила:**
- Всегда измеряйте дочерние элементы перед родительским
- Всегда вызывайте `setMeasuredDimension()`
- Пропускайте дочерние элементы с видимостью `GONE`
- Используйте `resolveSize()` для `wrap_content`
- Поддерживайте RTL-компоновки
- Кэшируйте вычисления для производительности

---

## Related Questions

### Prerequisites (Easier)
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View

### Related (Hard)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View

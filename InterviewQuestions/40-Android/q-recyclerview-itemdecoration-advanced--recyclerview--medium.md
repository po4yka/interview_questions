---
id: 20251017-114440
title: "Recyclerview Itemdecoration Advanced / Продвинутый ItemDecoration для RecyclerView"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: [itemdecoration, custom-drawing, ui, difficulty/medium]
moc: moc-android
related: [q-polling-implementation--android--medium, q-tasks-back-stack--android--medium, q-why-separate-ui-and-business-logic--android--easy]
  - q-recyclerview-sethasfixedsize--android--easy
  - q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy
  - q-rxjava-pagination-recyclerview--android--medium
  - q-how-to-create-list-like-recyclerview-in-compose--android--medium
  - q-recyclerview-itemdecoration-advanced--android--medium
  - q-how-animations-work-in-recyclerview--android--medium
  - q-recyclerview-async-list-differ--recyclerview--medium
---
# RecyclerView ItemDecoration Advanced

# Question (EN)
> How do you create custom ItemDecorations for RecyclerView? Explain the drawing phases (onDraw, onDrawOver), implementing dividers, sticky headers, and complex decorations with custom positioning.

# Вопрос (RU)
> Как создать пользовательские ItemDecorations для RecyclerView? Объясните фазы отрисовки (onDraw, onDrawOver), реализацию разделителей, sticky headers и сложных украшений с пользовательским позиционированием.

---

## Answer (EN)

**ItemDecoration** allows adding custom drawing and layout offsets to RecyclerView items without modifying the items themselves. It's perfect for dividers, spacing, sticky headers, and visual effects.

### ItemDecoration Phases

RecyclerView drawing occurs in 3 phases:

```
1. onDraw() - Draw UNDER items (background decorations)
2. Item views drawn
3. onDrawOver() - Draw OVER items (foreground decorations, sticky headers)
```

**Methods:**
- `onDraw()` - Draw decorations under items
- `onDrawOver()` - Draw decorations over items
- `getItemOffsets()` - Add spacing/padding around items

---

### Basic Divider ItemDecoration

```kotlin
class SimpleDividerDecoration(
    context: Context,
    private val dividerHeight: Int = 1.dpToPx(context)
) : RecyclerView.ItemDecoration() {

    private val paint = Paint().apply {
        color = Color.LTGRAY
        style = Paint.Style.FILL
    }

    // Add spacing for divider
    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        // Add bottom spacing to all items except last
        val position = parent.getChildAdapterPosition(view)
        if (position != parent.adapter?.itemCount?.minus(1)) {
            outRect.bottom = dividerHeight
        }
    }

    // Draw divider under items
    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft
        val right = parent.width - parent.paddingRight

        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val params = child.layoutParams as RecyclerView.LayoutParams

            val top = child.bottom + params.bottomMargin
            val bottom = top + dividerHeight

            canvas.drawRect(
                left.toFloat(),
                top.toFloat(),
                right.toFloat(),
                bottom.toFloat(),
                paint
            )
        }
    }

    private fun Int.dpToPx(context: Context): Int {
        return (this * context.resources.displayMetrics.density).toInt()
    }
}

// Usage
recyclerView.addItemDecoration(SimpleDividerDecoration(context))
```

---

### Advanced Divider with Insets

```kotlin
class InsetDividerDecoration(
    context: Context,
    private val insetStart: Int = 16.dpToPx(context),
    private val insetEnd: Int = 0,
    @ColorInt private val dividerColor: Int = Color.LTGRAY,
    private val dividerHeight: Int = 1.dpToPx(context)
) : RecyclerView.ItemDecoration() {

    private val paint = Paint().apply {
        color = dividerColor
        style = Paint.Style.FILL
    }

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val itemCount = state.itemCount

        // Add spacing except for last item
        if (position < itemCount - 1) {
            outRect.bottom = dividerHeight
        }
    }

    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft + insetStart
        val right = parent.width - parent.paddingRight - insetEnd

        for (i in 0 until parent.childCount - 1) { // Skip last item
            val child = parent.getChildAt(i)
            val params = child.layoutParams as RecyclerView.LayoutParams

            val top = child.bottom + params.bottomMargin
            val bottom = top + dividerHeight

            canvas.drawRect(
                left.toFloat(),
                top.toFloat(),
                right.toFloat(),
                bottom.toFloat(),
                paint
            )
        }
    }

    private fun Int.dpToPx(context: Context): Int {
        return (this * context.resources.displayMetrics.density).toInt()
    }
}
```

---

### Grid Spacing Decoration

```kotlin
class GridSpacingDecoration(
    private val spanCount: Int,
    private val spacing: Int,
    private val includeEdge: Boolean = true
) : RecyclerView.ItemDecoration() {

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val column = position % spanCount // Column index

        if (includeEdge) {
            // Spacing on all sides
            outRect.left = spacing - column * spacing / spanCount
            outRect.right = (column + 1) * spacing / spanCount

            if (position < spanCount) { // Top edge
                outRect.top = spacing
            }
            outRect.bottom = spacing
        } else {
            // Spacing between items only
            outRect.left = column * spacing / spanCount
            outRect.right = spacing - (column + 1) * spacing / spanCount

            if (position >= spanCount) {
                outRect.top = spacing
            }
        }
    }
}

// Usage
val spanCount = 3
val spacing = 16.dpToPx()
recyclerView.addItemDecoration(GridSpacingDecoration(spanCount, spacing, true))
```

---

### Sticky Header Decoration

```kotlin
interface StickyHeaderAdapter {
    fun isHeader(position: Int): Boolean
    fun getHeaderView(position: Int, parent: RecyclerView): View
}

class StickyHeaderDecoration(
    private val adapter: StickyHeaderAdapter
) : RecyclerView.ItemDecoration() {

    private var currentHeader: Pair<Int, View>? = null

    override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        super.onDrawOver(canvas, parent, state)

        val topChild = parent.getChildAt(0) ?: return
        val topChildPosition = parent.getChildAdapterPosition(topChild)
        if (topChildPosition == RecyclerView.NO_POSITION) return

        // Find current header position
        val headerPosition = findHeaderPosition(topChildPosition)
        if (headerPosition == RecyclerView.NO_POSITION) return

        // Get or create header view
        val headerView = getHeaderView(parent, headerPosition)

        // Calculate header position
        val contactPoint = headerView.bottom
        val childInContact = getChildInContact(parent, contactPoint)

        if (childInContact != null) {
            val childPosition = parent.getChildAdapterPosition(childInContact)
            if (adapter.isHeader(childPosition)) {
                // Push current header up
                moveHeader(canvas, headerView, childInContact)
                return
            }
        }

        // Draw header at top
        drawHeader(canvas, headerView)
    }

    private fun findHeaderPosition(fromPosition: Int): Int {
        var position = fromPosition
        while (position >= 0) {
            if (adapter.isHeader(position)) {
                return position
            }
            position--
        }
        return RecyclerView.NO_POSITION
    }

    private fun getHeaderView(parent: RecyclerView, position: Int): View {
        // Check cache
        if (currentHeader?.first == position) {
            return currentHeader!!.second
        }

        // Create new header view
        val headerView = adapter.getHeaderView(position, parent)

        // Measure header
        val widthSpec = View.MeasureSpec.makeMeasureSpec(
            parent.width,
            View.MeasureSpec.EXACTLY
        )
        val heightSpec = View.MeasureSpec.makeMeasureSpec(
            parent.height,
            View.MeasureSpec.UNSPECIFIED
        )

        val childWidth = ViewGroup.getChildMeasureSpec(
            widthSpec,
            parent.paddingLeft + parent.paddingRight,
            headerView.layoutParams.width
        )
        val childHeight = ViewGroup.getChildMeasureSpec(
            heightSpec,
            parent.paddingTop + parent.paddingBottom,
            headerView.layoutParams.height
        )

        headerView.measure(childWidth, childHeight)
        headerView.layout(0, 0, headerView.measuredWidth, headerView.measuredHeight)

        currentHeader = position to headerView
        return headerView
    }

    private fun drawHeader(canvas: Canvas, headerView: View) {
        canvas.save()
        canvas.translate(0f, 0f)
        headerView.draw(canvas)
        canvas.restore()
    }

    private fun moveHeader(canvas: Canvas, currentHeader: View, nextHeader: View) {
        canvas.save()
        val offset = nextHeader.top - currentHeader.height
        canvas.translate(0f, offset.toFloat())
        currentHeader.draw(canvas)
        canvas.restore()
    }

    private fun getChildInContact(parent: RecyclerView, contactPoint: Int): View? {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            if (child.bottom > contactPoint && child.top <= contactPoint) {
                return child
            }
        }
        return null
    }
}

// Implementation in adapter
class MyAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>(), StickyHeaderAdapter {

    override fun isHeader(position: Int): Boolean {
        // Your logic to determine if position is header
        return items[position] is HeaderItem
    }

    override fun getHeaderView(position: Int, parent: RecyclerView): View {
        val holder = onCreateViewHolder(parent, TYPE_HEADER)
        onBindViewHolder(holder, position)
        return holder.itemView
    }
}

// Usage
val decoration = StickyHeaderDecoration(adapter as StickyHeaderAdapter)
recyclerView.addItemDecoration(decoration)
```

---

### Section Divider with Label

```kotlin
class SectionDividerDecoration(
    context: Context,
    private val getSectionName: (position: Int) -> String?
) : RecyclerView.ItemDecoration() {

    private val dividerHeight = 40.dpToPx(context)
    private val dividerPaint = Paint().apply {
        color = Color.LTGRAY
        style = Paint.Style.FILL
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLACK
        textSize = 14.spToPx(context)
    }

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)

        // Add spacing if first item or section changed
        if (position == 0 || isNewSection(position, parent)) {
            outRect.top = dividerHeight
        }
    }

    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)

            if (position == 0 || isNewSection(position, parent)) {
                val sectionName = getSectionName(position) ?: continue

                // Draw section background
                val top = child.top - dividerHeight
                val bottom = child.top

                canvas.drawRect(
                    0f,
                    top.toFloat(),
                    parent.width.toFloat(),
                    bottom.toFloat(),
                    dividerPaint
                )

                // Draw section text
                val textY = top + dividerHeight / 2f + textPaint.textSize / 2f
                canvas.drawText(
                    sectionName,
                    16f,
                    textY,
                    textPaint
                )
            }
        }
    }

    private fun isNewSection(position: Int, parent: RecyclerView): Boolean {
        if (position == 0) return true

        val currentSection = getSectionName(position)
        val previousSection = getSectionName(position - 1)

        return currentSection != previousSection
    }

    private fun Int.dpToPx(context: Context): Int {
        return (this * context.resources.displayMetrics.density).toInt()
    }

    private fun Int.spToPx(context: Context): Float {
        return this * context.resources.displayMetrics.scaledDensity
    }
}

// Usage
val decoration = SectionDividerDecoration(context) { position ->
    // Return section name for position
    when {
        position < 5 -> "Section A"
        position < 10 -> "Section B"
        else -> "Section C"
    }
}
recyclerView.addItemDecoration(decoration)
```

---

### Highlight Selected Item Decoration

```kotlin
class SelectionDecoration(
    @ColorInt private val highlightColor: Int = Color.parseColor("#E3F2FD"),
    private val cornerRadius: Float = 8f
) : RecyclerView.ItemDecoration() {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = highlightColor
        style = Paint.Style.FILL
    }

    var selectedPosition: Int = RecyclerView.NO_POSITION
        set(value) {
            field = value
            // Request redraw
        }

    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        if (selectedPosition == RecyclerView.NO_POSITION) return

        // Find view at selected position
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)

            if (position == selectedPosition) {
                // Draw highlight behind item
                val left = child.left.toFloat()
                val top = child.top.toFloat()
                val right = child.right.toFloat()
                val bottom = child.bottom.toFloat()

                canvas.drawRoundRect(
                    left, top, right, bottom,
                    cornerRadius, cornerRadius,
                    paint
                )
                break
            }
        }
    }
}

// Usage
val decoration = SelectionDecoration()
recyclerView.addItemDecoration(decoration)

// Update selection
decoration.selectedPosition = 5
recyclerView.invalidateItemDecorations()
```

---

### Badge/Overlay Decoration

```kotlin
class BadgeDecoration(
    context: Context,
    private val hasBadge: (position: Int) -> Boolean,
    private val getBadgeText: (position: Int) -> String
) : RecyclerView.ItemDecoration() {

    private val badgeSize = 24.dpToPx(context)
    private val badgePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.RED
        style = Paint.Style.FILL
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.WHITE
        textSize = 12.spToPx(context)
        textAlign = Paint.Align.CENTER
    }

    override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)

            if (hasBadge(position)) {
                val badgeText = getBadgeText(position)

                // Draw badge at top-right corner
                val cx = child.right - badgeSize / 2f
                val cy = child.top + badgeSize / 2f

                canvas.drawCircle(cx, cy, badgeSize / 2f, badgePaint)

                // Draw text
                val textY = cy - (textPaint.descent() + textPaint.ascent()) / 2
                canvas.drawText(badgeText, cx, textY, textPaint)
            }
        }
    }

    private fun Int.dpToPx(context: Context): Int {
        return (this * context.resources.displayMetrics.density).toInt()
    }

    private fun Int.spToPx(context: Context): Float {
        return this * context.resources.displayMetrics.scaledDensity
    }
}

// Usage
val decoration = BadgeDecoration(
    context,
    hasBadge = { position -> unreadCounts[position] > 0 },
    getBadgeText = { position -> unreadCounts[position].toString() }
)
recyclerView.addItemDecoration(decoration)
```

---

### Performance Considerations

**1. Cache Paint objects**
```kotlin
//  DO - Create once
private val paint = Paint()

//  DON'T - Create in onDraw
override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
    val paint = Paint() // BAD - allocates every draw!
}
```

**2. Limit drawing operations**
```kotlin
//  DO - Only draw visible items
for (i in 0 until parent.childCount) {
    val child = parent.getChildAt(i)
    // Draw only for this child
}

//  DON'T - Loop through all items
for (position in 0 until adapter.itemCount) {
    // BAD - draws even non-visible items
}
```

**3. Use hardware acceleration**
```kotlin
// Set layer type for complex decorations
recyclerView.setLayerType(View.LAYER_TYPE_HARDWARE, null)
```

---

### Best Practices

**1. Use getItemOffsets for spacing**
```kotlin
//  DO - Use getItemOffsets for spacing
override fun getItemOffsets(outRect: Rect, ...) {
    outRect.bottom = spacing
}

//  DON'T - Add spacing in layout
```

**2. onDraw vs onDrawOver**
```kotlin
// Use onDraw for decorations UNDER items (dividers, backgrounds)
override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
    // Draw dividers
}

// Use onDrawOver for decorations OVER items (sticky headers, overlays)
override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
    // Draw sticky header
}
```

**3. Cache complex calculations**
```kotlin
private var cachedHeaderView: View? = null

override fun onDrawOver(...) {
    val headerView = cachedHeaderView ?: createHeaderView()
    // Use cached view
}
```

**4. Invalidate efficiently**
```kotlin
//  DO - Invalidate only decorations
recyclerView.invalidateItemDecorations()

//  DON'T - Invalidate entire RecyclerView
recyclerView.invalidate()
```

---

### Summary

**ItemDecoration phases:**
1. `onDraw()` - Draw under items
2. Item views drawn
3. `onDrawOver()` - Draw over items

**Key methods:**
- `getItemOffsets()` - Add spacing
- `onDraw()` - Draw backgrounds, dividers
- `onDrawOver()` - Draw overlays, sticky headers

**Common use cases:**
- Dividers (simple, inset, grid)
- Spacing (linear, grid)
- Sticky headers
- Section dividers with labels
- Highlights and badges

**Performance tips:**
- Cache Paint objects
- Only draw visible items
- Use hardware acceleration
- Invalidate efficiently

**Best practices:**
- Use getItemOffsets for spacing
- Choose correct drawing phase
- Cache complex calculations
- Test with different list sizes

---

## Ответ (RU)

**ItemDecoration** позволяет добавлять пользовательскую отрисовку и смещения layout к элементам RecyclerView без изменения самих элементов. Идеально подходит для разделителей, отступов, sticky headers и визуальных эффектов.

### Фазы ItemDecoration

RecyclerView отрисовка происходит в 3 фазах:

```
1. onDraw() - Рисовать ПОД элементами (фоновые украшения)
2. Элементы view отрисовываются
3. onDrawOver() - Рисовать НАД элементами (фронтальные украшения, sticky headers)
```

**Методы:**
- `onDraw()` - Рисовать украшения под элементами
- `onDrawOver()` - Рисовать украшения над элементами
- `getItemOffsets()` - Добавлять отступы/padding вокруг элементов

---

### Базовый разделитель ItemDecoration

```kotlin
class SimpleDividerDecoration(
    context: Context,
    private val dividerHeight: Int = 1.dpToPx(context)
) : RecyclerView.ItemDecoration() {

    private val paint = Paint().apply {
        color = Color.LTGRAY
        style = Paint.Style.FILL
    }

    // Добавить отступ для разделителя
    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        // Добавить нижний отступ ко всем элементам кроме последнего
        val position = parent.getChildAdapterPosition(view)
        if (position != parent.adapter?.itemCount?.minus(1)) {
            outRect.bottom = dividerHeight
        }
    }

    // Нарисовать разделитель под элементами
    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft
        val right = parent.width - parent.paddingRight

        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val params = child.layoutParams as RecyclerView.LayoutParams

            val top = child.bottom + params.bottomMargin
            val bottom = top + dividerHeight

            canvas.drawRect(
                left.toFloat(),
                top.toFloat(),
                right.toFloat(),
                bottom.toFloat(),
                paint
            )
        }
    }

    private fun Int.dpToPx(context: Context): Int {
        return (this * context.resources.displayMetrics.density).toInt()
    }
}

// Использование
recyclerView.addItemDecoration(SimpleDividerDecoration(context))
```

---

### Продвинутый разделитель с отступами

```kotlin
class InsetDividerDecoration(
    context: Context,
    private val insetStart: Int = 16.dpToPx(context),
    private val insetEnd: Int = 0,
    @ColorInt private val dividerColor: Int = Color.LTGRAY,
    private val dividerHeight: Int = 1.dpToPx(context)
) : RecyclerView.ItemDecoration() {

    private val paint = Paint().apply {
        color = dividerColor
        style = Paint.Style.FILL
    }

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val itemCount = state.itemCount

        // Добавить отступ кроме последнего элемента
        if (position < itemCount - 1) {
            outRect.bottom = dividerHeight
        }
    }

    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft + insetStart
        val right = parent.width - parent.paddingRight - insetEnd

        for (i in 0 until parent.childCount - 1) { // Пропустить последний элемент
            val child = parent.getChildAt(i)
            val params = child.layoutParams as RecyclerView.LayoutParams

            val top = child.bottom + params.bottomMargin
            val bottom = top + dividerHeight

            canvas.drawRect(
                left.toFloat(),
                top.toFloat(),
                right.toFloat(),
                bottom.toFloat(),
                paint
            )
        }
    }

    private fun Int.dpToPx(context: Context): Int {
        return (this * context.resources.displayMetrics.density).toInt()
    }
}
```

---

### Grid Spacing Decoration

```kotlin
class GridSpacingDecoration(
    private val spanCount: Int,
    private val spacing: Int,
    private val includeEdge: Boolean = true
) : RecyclerView.ItemDecoration() {

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val column = position % spanCount // Индекс колонки

        if (includeEdge) {
            // Отступы со всех сторон
            outRect.left = spacing - column * spacing / spanCount
            outRect.right = (column + 1) * spacing / spanCount

            if (position < spanCount) { // Верхний край
                outRect.top = spacing
            }
            outRect.bottom = spacing
        } else {
            // Отступы только между элементами
            outRect.left = column * spacing / spanCount
            outRect.right = spacing - (column + 1) * spacing / spanCount

            if (position >= spanCount) {
                outRect.top = spacing
            }
        }
    }
}

// Использование
val spanCount = 3
val spacing = 16.dpToPx()
recyclerView.addItemDecoration(GridSpacingDecoration(spanCount, spacing, true))
```

---

### Sticky Header Decoration

```kotlin
interface StickyHeaderAdapter {
    fun isHeader(position: Int): Boolean
    fun getHeaderView(position: Int, parent: RecyclerView): View
}

class StickyHeaderDecoration(
    private val adapter: StickyHeaderAdapter
) : RecyclerView.ItemDecoration() {

    private var currentHeader: Pair<Int, View>? = null

    override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        super.onDrawOver(canvas, parent, state)

        val topChild = parent.getChildAt(0) ?: return
        val topChildPosition = parent.getChildAdapterPosition(topChild)
        if (topChildPosition == RecyclerView.NO_POSITION) return

        // Найти текущую позицию заголовка
        val headerPosition = findHeaderPosition(topChildPosition)
        if (headerPosition == RecyclerView.NO_POSITION) return

        // Получить или создать header view
        val headerView = getHeaderView(parent, headerPosition)

        // Вычислить позицию заголовка
        val contactPoint = headerView.bottom
        val childInContact = getChildInContact(parent, contactPoint)

        if (childInContact != null) {
            val childPosition = parent.getChildAdapterPosition(childInContact)
            if (adapter.isHeader(childPosition)) {
                // Сдвинуть текущий заголовок вверх
                moveHeader(canvas, headerView, childInContact)
                return
            }
        }

        // Нарисовать заголовок вверху
        drawHeader(canvas, headerView)
    }

    private fun findHeaderPosition(fromPosition: Int): Int {
        var position = fromPosition
        while (position >= 0) {
            if (adapter.isHeader(position)) {
                return position
            }
            position--
        }
        return RecyclerView.NO_POSITION
    }

    private fun getHeaderView(parent: RecyclerView, position: Int): View {
        // Проверить кэш
        if (currentHeader?.first == position) {
            return currentHeader!!.second
        }

        // Создать новый header view
        val headerView = adapter.getHeaderView(position, parent)

        // Измерить header
        val widthSpec = View.MeasureSpec.makeMeasureSpec(
            parent.width,
            View.MeasureSpec.EXACTLY
        )
        val heightSpec = View.MeasureSpec.makeMeasureSpec(
            parent.height,
            View.MeasureSpec.UNSPECIFIED
        )

        val childWidth = ViewGroup.getChildMeasureSpec(
            widthSpec,
            parent.paddingLeft + parent.paddingRight,
            headerView.layoutParams.width
        )
        val childHeight = ViewGroup.getChildMeasureSpec(
            heightSpec,
            parent.paddingTop + parent.paddingBottom,
            headerView.layoutParams.height
        )

        headerView.measure(childWidth, childHeight)
        headerView.layout(0, 0, headerView.measuredWidth, headerView.measuredHeight)

        currentHeader = position to headerView
        return headerView
    }

    private fun drawHeader(canvas: Canvas, headerView: View) {
        canvas.save()
        canvas.translate(0f, 0f)
        headerView.draw(canvas)
        canvas.restore()
    }

    private fun moveHeader(canvas: Canvas, currentHeader: View, nextHeader: View) {
        canvas.save()
        val offset = nextHeader.top - currentHeader.height
        canvas.translate(0f, offset.toFloat())
        currentHeader.draw(canvas)
        canvas.restore()
    }

    private fun getChildInContact(parent: RecyclerView, contactPoint: Int): View? {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            if (child.bottom > contactPoint && child.top <= contactPoint) {
                return child
            }
        }
        return null
    }
}

// Реализация в адаптере
class MyAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>(), StickyHeaderAdapter {

    override fun isHeader(position: Int): Boolean {
        // Ваша логика для определения заголовка
        return items[position] is HeaderItem
    }

    override fun getHeaderView(position: Int, parent: RecyclerView): View {
        val holder = onCreateViewHolder(parent, TYPE_HEADER)
        onBindViewHolder(holder, position)
        return holder.itemView
    }
}

// Использование
val decoration = StickyHeaderDecoration(adapter as StickyHeaderAdapter)
recyclerView.addItemDecoration(decoration)
```

---

### Section Divider с меткой

```kotlin
class SectionDividerDecoration(
    context: Context,
    private val getSectionName: (position: Int) -> String?
) : RecyclerView.ItemDecoration() {

    private val dividerHeight = 40.dpToPx(context)
    private val dividerPaint = Paint().apply {
        color = Color.LTGRAY
        style = Paint.Style.FILL
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLACK
        textSize = 14.spToPx(context)
    }

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)

        // Добавить отступ если первый элемент или секция изменилась
        if (position == 0 || isNewSection(position, parent)) {
            outRect.top = dividerHeight
        }
    }

    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)

            if (position == 0 || isNewSection(position, parent)) {
                val sectionName = getSectionName(position) ?: continue

                // Нарисовать фон секции
                val top = child.top - dividerHeight
                val bottom = child.top

                canvas.drawRect(
                    0f,
                    top.toFloat(),
                    parent.width.toFloat(),
                    bottom.toFloat(),
                    dividerPaint
                )

                // Нарисовать текст секции
                val textY = top + dividerHeight / 2f + textPaint.textSize / 2f
                canvas.drawText(
                    sectionName,
                    16f,
                    textY,
                    textPaint
                )
            }
        }
    }

    private fun isNewSection(position: Int, parent: RecyclerView): Boolean {
        if (position == 0) return true

        val currentSection = getSectionName(position)
        val previousSection = getSectionName(position - 1)

        return currentSection != previousSection
    }

    private fun Int.dpToPx(context: Context): Int {
        return (this * context.resources.displayMetrics.density).toInt()
    }

    private fun Int.spToPx(context: Context): Float {
        return this * context.resources.displayMetrics.scaledDensity
    }
}

// Использование
val decoration = SectionDividerDecoration(context) { position ->
    // Вернуть имя секции для позиции
    when {
        position < 5 -> "Секция A"
        position < 10 -> "Секция B"
        else -> "Секция C"
    }
}
recyclerView.addItemDecoration(decoration)
```

---

### Соображения производительности

**1. Кэшировать Paint объекты**
```kotlin
//  ДЕЛАТЬ - Создать один раз
private val paint = Paint()

//  НЕ ДЕЛАТЬ - Создавать в onDraw
override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
    val paint = Paint() // ПЛОХО - аллокация при каждой отрисовке!
}
```

**2. Ограничить операции рисования**
```kotlin
//  ДЕЛАТЬ - Рисовать только видимые элементы
for (i in 0 until parent.childCount) {
    val child = parent.getChildAt(i)
    // Рисовать только для этого child
}

//  НЕ ДЕЛАТЬ - Цикл по всем элементам
for (position in 0 until adapter.itemCount) {
    // ПЛОХО - рисует даже невидимые элементы
}
```

**3. Использовать аппаратное ускорение**
```kotlin
// Установить layer type для сложных украшений
recyclerView.setLayerType(View.LAYER_TYPE_HARDWARE, null)
```

---

### Лучшие практики

**1. Используйте getItemOffsets для spacing**
```kotlin
//  ДЕЛАТЬ - Использовать getItemOffsets для spacing
override fun getItemOffsets(outRect: Rect, ...) {
    outRect.bottom = spacing
}

//  НЕ ДЕЛАТЬ - Добавлять spacing в layout
```

**2. onDraw vs onDrawOver**
```kotlin
// Использовать onDraw для украшений ПОД элементами (разделители, фоны)
override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
    // Рисовать разделители
}

// Использовать onDrawOver для украшений НАД элементами (sticky headers, оверлеи)
override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
    // Рисовать sticky header
}
```

**3. Кэшировать сложные вычисления**
```kotlin
private var cachedHeaderView: View? = null

override fun onDrawOver(...) {
    val headerView = cachedHeaderView ?: createHeaderView()
    // Использовать кэшированный view
}
```

**4. Эффективно invalidate**
```kotlin
//  ДЕЛАТЬ - Invalidate только украшения
recyclerView.invalidateItemDecorations()

//  НЕ ДЕЛАТЬ - Invalidate весь RecyclerView
recyclerView.invalidate()
```

---

### Резюме

**Фазы ItemDecoration:**
1. `onDraw()` - Рисовать под элементами
2. Элементы view отрисовываются
3. `onDrawOver()` - Рисовать над элементами

**Ключевые методы:**
- `getItemOffsets()` - Добавить spacing
- `onDraw()` - Рисовать фоны, разделители
- `onDrawOver()` - Рисовать оверлеи, sticky headers

**Распространённые случаи использования:**
- Разделители (простые, с отступами, для сетки)
- Spacing (linear, grid)
- Sticky headers
- Section dividers с метками
- Подсветка и значки

**Советы по производительности:**
- Кэшировать Paint объекты
- Рисовать только видимые элементы
- Использовать аппаратное ускорение
- Эффективно invalidate

**Лучшие практики:**
- Использовать getItemOffsets для spacing
- Выбрать правильную фазу рисования
- Кэшировать сложные вычисления
- Тестировать с разными размерами списков

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- [[q-rxjava-pagination-recyclerview--android--medium]] - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - View, Ui
- [[q-recyclerview-async-list-differ--recyclerview--medium]] - View, Ui

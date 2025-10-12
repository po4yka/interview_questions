---
topic: android
tags:
  - android
  - android/recyclerview
  - android/ui
  - itemdecoration
  - recyclerview
  - ui
difficulty: medium
status: draft
---

# Что позволяет делать ItemDecoration?

**English**: What does ItemDecoration allow you to do?

## Answer (EN)
**ItemDecoration** in RecyclerView allows adding visual decorations to list items such as margins, divider lines, borders, and any other visual elements that are not part of the item content itself.

### Key Capabilities

1. **Dividers**: Add separating lines between items
2. **Spacing**: Control margins and padding around items
3. **Borders**: Draw borders around items or groups
4. **Headers/Footers**: Draw custom headers or footers
5. **Overlays**: Add overlays or backgrounds
6. **Grid Spacing**: Manage spacing in grid layouts

### Basic ItemDecoration Methods

```kotlin
abstract class RecyclerView.ItemDecoration {
    // Draw decorations below items
    open fun onDraw(c: Canvas, parent: RecyclerView, state: State)

    // Draw decorations above items
    open fun onDrawOver(c: Canvas, parent: RecyclerView, state: State)

    // Define offset/spacing around items
    open fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: State
    )
}
```

### Simple Divider Implementation

```kotlin
class SimpleDividerDecoration(context: Context) : RecyclerView.ItemDecoration() {
    private val divider: Drawable = context.getDrawable(R.drawable.divider)!!

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft
        val right = parent.width - parent.paddingRight

        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val params = child.layoutParams as RecyclerView.LayoutParams

            val top = child.bottom + params.bottomMargin
            val bottom = top + divider.intrinsicHeight

            divider.setBounds(left, top, right, bottom)
            divider.draw(c)
        }
    }
}

// Usage
recyclerView.addItemDecoration(SimpleDividerDecoration(this))
```

### Using Built-in DividerItemDecoration

```kotlin
// Vertical divider
val dividerDecoration = DividerItemDecoration(
    this,
    DividerItemDecoration.VERTICAL
)
recyclerView.addItemDecoration(dividerDecoration)

// Custom divider drawable
dividerDecoration.setDrawable(
    ContextCompat.getDrawable(this, R.drawable.custom_divider)!!
)
```

### Item Spacing Decoration

```kotlin
class SpacingDecoration(private val spacing: Int) : RecyclerView.ItemDecoration() {
    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        outRect.left = spacing
        outRect.right = spacing
        outRect.bottom = spacing

        // Add top spacing only for first item
        if (parent.getChildAdapterPosition(view) == 0) {
            outRect.top = spacing
        }
    }
}

// Usage
val spacing = resources.getDimensionPixelSize(R.dimen.item_spacing)
recyclerView.addItemDecoration(SpacingDecoration(spacing))
```

### Grid Spacing Decoration

```kotlin
class GridSpacingDecoration(
    private val spanCount: Int,
    private val spacing: Int,
    private val includeEdge: Boolean
) : RecyclerView.ItemDecoration() {

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val column = position % spanCount

        if (includeEdge) {
            outRect.left = spacing - column * spacing / spanCount
            outRect.right = (column + 1) * spacing / spanCount

            if (position < spanCount) {
                outRect.top = spacing
            }
            outRect.bottom = spacing
        } else {
            outRect.left = column * spacing / spanCount
            outRect.right = spacing - (column + 1) * spacing / spanCount

            if (position >= spanCount) {
                outRect.top = spacing
            }
        }
    }
}

// Usage for 2-column grid
recyclerView.addItemDecoration(
    GridSpacingDecoration(
        spanCount = 2,
        spacing = 16.dpToPx(),
        includeEdge = true
    )
)
```

### Custom Border Decoration

```kotlin
class BorderDecoration(
    private val borderWidth: Int,
    private val borderColor: Int
) : RecyclerView.ItemDecoration() {

    private val paint = Paint().apply {
        style = Paint.Style.STROKE
        strokeWidth = borderWidth.toFloat()
        color = borderColor
    }

    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            c.drawRect(
                child.left.toFloat(),
                child.top.toFloat(),
                child.right.toFloat(),
                child.bottom.toFloat(),
                paint
            )
        }
    }

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        outRect.set(borderWidth, borderWidth, borderWidth, borderWidth)
    }
}

// Usage
recyclerView.addItemDecoration(
    BorderDecoration(
        borderWidth = 2.dpToPx(),
        borderColor = Color.GRAY
    )
)
```

### Section Header Decoration

```kotlin
class SectionHeaderDecoration(
    private val getSectionHeader: (position: Int) -> String?
) : RecyclerView.ItemDecoration() {

    private val headerPaint = Paint().apply {
        textSize = 40f
        color = Color.BLACK
        typeface = Typeface.DEFAULT_BOLD
    }

    private val backgroundPaint = Paint().apply {
        color = Color.LTGRAY
    }

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)

            if (position != RecyclerView.NO_POSITION) {
                val header = getSectionHeader(position)
                if (header != null) {
                    drawHeader(c, child, header)
                }
            }
        }
    }

    private fun drawHeader(c: Canvas, child: View, header: String) {
        val headerHeight = 80f
        c.drawRect(
            0f,
            child.top - headerHeight,
            child.parent.width.toFloat(),
            child.top.toFloat(),
            backgroundPaint
        )
        c.drawText(
            header,
            16f,
            child.top - 25f,
            headerPaint
        )
    }

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        if (getSectionHeader(position) != null) {
            outRect.top = 80
        }
    }
}

// Usage
recyclerView.addItemDecoration(
    SectionHeaderDecoration { position ->
        if (position % 5 == 0) "Section ${position / 5}" else null
    }
)
```

### Multiple Decorations

You can add multiple decorations to a single RecyclerView:

```kotlin
recyclerView.apply {
    addItemDecoration(SpacingDecoration(16.dpToPx()))
    addItemDecoration(DividerItemDecoration(context, DividerItemDecoration.VERTICAL))
    addItemDecoration(BorderDecoration(2.dpToPx(), Color.GRAY))
}
```

### Removing Decorations

```kotlin
// Remove specific decoration
recyclerView.removeItemDecoration(decoration)

// Remove by index
recyclerView.removeItemDecorationAt(0)

// Get decoration count
val count = recyclerView.itemDecorationCount
```

### Best Practices

1. **Reuse decorations** instead of creating new instances
2. **Cache paint objects** for better performance
3. **Consider item position** when calculating offsets
4. **Use getItemOffsets** for spacing, **onDraw** for visuals
5. **Test with different layouts** (linear, grid, etc.)

### Common Use Cases

- **Dividers between list items**
- **Grid item spacing**
- **Section headers in lists**
- **Custom borders or backgrounds**
- **Sticky headers**
- **Item shadows or overlays**

## Ответ (RU)
ItemDecoration в RecyclerView позволяет добавлять украшения к элементам списка такие как отступы разделительные линии рамки и любые другие визуальные элементы которые не являются частью содержимого элементов списка


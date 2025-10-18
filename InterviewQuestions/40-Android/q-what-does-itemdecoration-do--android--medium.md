---
id: 20251012-122711147
title: "What Does Itemdecoration Do / Что делает ItemDecoration"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-opengl-advanced-rendering--graphics--medium, q-retrofit-path-parameter--android--medium, q-what-can-be-done-through-composer--android--medium]
created: 2025-10-15
tags: [android/recyclerview, android/ui, itemdecoration, recyclerview, ui, difficulty/medium]
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

**ItemDecoration** в RecyclerView позволяет добавлять визуальные декорации к элементам списка, такие как отступы, разделительные линии, рамки и любые другие визуальные элементы, которые не являются частью содержимого самих элементов.

### Основные возможности ItemDecoration

1. **Разделители (Dividers)**: Добавление разделительных линий между элементами
2. **Отступы (Spacing)**: Управление отступами и padding вокруг элементов
3. **Рамки (Borders)**: Рисование рамок вокруг элементов или групп
4. **Заголовки/подвалы (Headers/Footers)**: Рисование кастомных заголовков или подвалов
5. **Наложения (Overlays)**: Добавление наложений или фонов
6. **Grid spacing**: Управление отступами в grid layout

### Основные методы ItemDecoration

```kotlin
abstract class RecyclerView.ItemDecoration {
    // Рисование декораций ПОД элементами
    open fun onDraw(c: Canvas, parent: RecyclerView, state: State)

    // Рисование декораций НАД элементами
    open fun onDrawOver(c: Canvas, parent: RecyclerView, state: State)

    // Определение отступов вокруг элементов
    open fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: State
    )
}
```

### Примеры использования

**1. Простой разделитель:**
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

// Использование
recyclerView.addItemDecoration(SimpleDividerDecoration(this))
```

**2. Встроенный DividerItemDecoration:**
```kotlin
// Вертикальный разделитель
val dividerDecoration = DividerItemDecoration(
    this,
    DividerItemDecoration.VERTICAL
)
recyclerView.addItemDecoration(dividerDecoration)

// Кастомный drawable для разделителя
dividerDecoration.setDrawable(
    ContextCompat.getDrawable(this, R.drawable.custom_divider)!!
)
```

**3. Отступы между элементами:**
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

        // Добавить отступ сверху только для первого элемента
        if (parent.getChildAdapterPosition(view) == 0) {
            outRect.top = spacing
        }
    }
}

// Использование
val spacing = resources.getDimensionPixelSize(R.dimen.item_spacing)
recyclerView.addItemDecoration(SpacingDecoration(spacing))
```

**4. Grid spacing decoration:**
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

// Использование для 2-колоночной сетки
recyclerView.addItemDecoration(
    GridSpacingDecoration(
        spanCount = 2,
        spacing = 16.dpToPx(),
        includeEdge = true
    )
)
```

**5. Кастомная рамка:**
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
```

### Множественные декорации

Можно добавлять несколько декораций к одному RecyclerView:

```kotlin
recyclerView.apply {
    addItemDecoration(SpacingDecoration(16.dpToPx()))
    addItemDecoration(DividerItemDecoration(context, DividerItemDecoration.VERTICAL))
    addItemDecoration(BorderDecoration(2.dpToPx(), Color.GRAY))
}
```

### Управление декорациями

```kotlin
// Удалить конкретную декорацию
recyclerView.removeItemDecoration(decoration)

// Удалить по индексу
recyclerView.removeItemDecorationAt(0)

// Получить количество декораций
val count = recyclerView.itemDecorationCount
```

### Лучшие практики

1. **Переиспользование декораций** вместо создания новых экземпляров
2. **Кеширование Paint объектов** для лучшей производительности
3. **Учет позиции элемента** при расчете отступов
4. **Использование getItemOffsets для spacing**, **onDraw для визуальных элементов**
5. **Тестирование с разными layouts** (linear, grid и т.д.)

### Распространенные случаи использования

- Разделители между элементами списка
- Отступы в grid элементах
- Заголовки секций в списках
- Кастомные рамки или фоны
- Sticky headers
- Тени или наложения на элементах

### Резюме

ItemDecoration предоставляет мощный механизм для добавления визуальных декораций к RecyclerView без изменения самих элементов списка. Это обеспечивает чистое разделение между содержимым элемента и его визуальным оформлением, делая код более поддерживаемым и переиспользуемым.

## Related Questions

- [[q-opengl-advanced-rendering--graphics--medium]]
- [[q-retrofit-path-parameter--android--medium]]
- [[q-what-can-be-done-through-composer--android--medium]]

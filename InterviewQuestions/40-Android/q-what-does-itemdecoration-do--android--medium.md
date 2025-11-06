---
id: android-309
title: What Does ItemDecoration Do / Что делает ItemDecoration
aliases:
- ItemDecoration
- Что делает ItemDecoration
topic: android
subtopics:
- ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-recyclerview
created: 2025-10-15
updated: 2025-10-28
sources: []
tags:
- android/ui-views
- difficulty/medium
- itemdecoration
- recyclerview
---

# Вопрос (RU)

> Что позволяет делать ItemDecoration в `RecyclerView`?

# Question (EN)

> What does ItemDecoration allow you to do in `RecyclerView`?

---

## Ответ (RU)

**ItemDecoration** — механизм для добавления визуальных декораций к элементам `RecyclerView` (разделители, отступы, рамки, заголовки) без изменения самих элементов или адаптера.

### Основные Методы

```kotlin
abstract class RecyclerView.ItemDecoration {
    // Рисование ПОД элементами
    open fun onDraw(c: Canvas, parent: RecyclerView, state: State)

    // Рисование НАД элементами
    open fun onDrawOver(c: Canvas, parent: RecyclerView, state: State)

    // Определение отступов/spacing
    open fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: State
    )
}
```

**Назначение методов**:
- `getItemOffsets` — создаёт пространство (padding) вокруг элементов
- `onDraw` — рисует под элементами (фон, разделители снизу)
- `onDrawOver` — рисует над элементами (overlay, sticky headers)

### Примеры Реализации

**1. Простой разделитель (встроенный)**

```kotlin
// ✅ Используйте встроенный DividerItemDecoration для простых случаев
val divider = DividerItemDecoration(context, DividerItemDecoration.VERTICAL)
divider.setDrawable(ContextCompat.getDrawable(context, R.drawable.divider)!!)
recyclerView.addItemDecoration(divider)
```

**2. Отступы между элементами**

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

        // ✅ Отступ сверху только для первого элемента
        if (parent.getChildAdapterPosition(view) == 0) {
            outRect.top = spacing
        }
    }
}
```

**3. Grid spacing (равные отступы)**

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
            // ✅ Компенсация для равных отступов с краями
            outRect.left = spacing - column * spacing / spanCount
            outRect.right = (column + 1) * spacing / spanCount
            if (position < spanCount) outRect.top = spacing
            outRect.bottom = spacing
        } else {
            // ❌ Без краёв — отступы неравномерные
            outRect.left = column * spacing / spanCount
            outRect.right = spacing - (column + 1) * spacing / spanCount
            if (position >= spanCount) outRect.top = spacing
        }
    }
}
```

**4. Кастомный разделитель с отрисовкой**

```kotlin
class CustomDivider(context: Context) : RecyclerView.ItemDecoration() {
    private val divider = context.getDrawable(R.drawable.divider)!!

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft
        val right = parent.width - parent.paddingRight

        for (i in 0 until parent.childCount - 1) { // ✅ Пропускаем последний
            val child = parent.getChildAt(i)
            val params = child.layoutParams as RecyclerView.LayoutParams
            val top = child.bottom + params.bottomMargin
            val bottom = top + divider.intrinsicHeight

            divider.setBounds(left, top, right, bottom)
            divider.draw(c)
        }
    }
}
```

**5. Заголовки секций**

```kotlin
class SectionHeaderDecoration(
    private val getSectionHeader: (Int) -> String?
) : RecyclerView.ItemDecoration() {
    private val headerPaint = Paint().apply {
        textSize = 40f
        color = Color.BLACK
        typeface = Typeface.DEFAULT_BOLD
    }

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        if (getSectionHeader(position) != null) {
            outRect.top = 80 // Место для заголовка
        }
    }

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)
            getSectionHeader(position)?.let { header ->
                c.drawText(header, 16f, child.top - 25f, headerPaint)
            }
        }
    }
}
```

### Лучшие Практики

1. **Кешируйте `Paint`/`Drawable`** — создавайте их в конструкторе, не в onDraw
2. **Переиспользуйте декорации** — создайте один экземпляр для всех `RecyclerView`
3. **Учитывайте LayoutManager** — проверяйте тип (Linear/Grid/Staggered)
4. **Не меняйте ViewHolder** — ItemDecoration изолирована от адаптера
5. **Множественные декорации** — можно комбинировать (порядок важен: первая рисуется снизу)

### Удаление Декораций

```kotlin
recyclerView.removeItemDecoration(decoration)     // Удалить конкретную
recyclerView.removeItemDecorationAt(0)            // По индексу
val count = recyclerView.itemDecorationCount      // Количество
```

---

## Answer (EN)

**ItemDecoration** is a mechanism for adding visual decorations to `RecyclerView` items (dividers, spacing, borders, headers) without modifying the items themselves or the adapter.

### Core Methods

```kotlin
abstract class RecyclerView.ItemDecoration {
    // Draw BELOW items
    open fun onDraw(c: Canvas, parent: RecyclerView, state: State)

    // Draw ABOVE items
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

**Method purposes**:
- `getItemOffsets` — creates space (padding) around items
- `onDraw` — draws below items (backgrounds, dividers underneath)
- `onDrawOver` — draws above items (overlays, sticky headers)

### Implementation Examples

**1. Simple Divider (Built-in)**

```kotlin
// ✅ Use built-in DividerItemDecoration for simple cases
val divider = DividerItemDecoration(context, DividerItemDecoration.VERTICAL)
divider.setDrawable(ContextCompat.getDrawable(context, R.drawable.divider)!!)
recyclerView.addItemDecoration(divider)
```

**2. Item Spacing**

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

        // ✅ Top spacing only for first item
        if (parent.getChildAdapterPosition(view) == 0) {
            outRect.top = spacing
        }
    }
}
```

**3. Grid Spacing (Equal Spacing)**

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
            // ✅ Compensation for equal spacing with edges
            outRect.left = spacing - column * spacing / spanCount
            outRect.right = (column + 1) * spacing / spanCount
            if (position < spanCount) outRect.top = spacing
            outRect.bottom = spacing
        } else {
            // ❌ Without edges — uneven spacing
            outRect.left = column * spacing / spanCount
            outRect.right = spacing - (column + 1) * spacing / spanCount
            if (position >= spanCount) outRect.top = spacing
        }
    }
}
```

**4. Custom Divider with Drawing**

```kotlin
class CustomDivider(context: Context) : RecyclerView.ItemDecoration() {
    private val divider = context.getDrawable(R.drawable.divider)!!

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft
        val right = parent.width - parent.paddingRight

        for (i in 0 until parent.childCount - 1) { // ✅ Skip last item
            val child = parent.getChildAt(i)
            val params = child.layoutParams as RecyclerView.LayoutParams
            val top = child.bottom + params.bottomMargin
            val bottom = top + divider.intrinsicHeight

            divider.setBounds(left, top, right, bottom)
            divider.draw(c)
        }
    }
}
```

**5. Section Headers**

```kotlin
class SectionHeaderDecoration(
    private val getSectionHeader: (Int) -> String?
) : RecyclerView.ItemDecoration() {
    private val headerPaint = Paint().apply {
        textSize = 40f
        color = Color.BLACK
        typeface = Typeface.DEFAULT_BOLD
    }

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        if (getSectionHeader(position) != null) {
            outRect.top = 80 // Space for header
        }
    }

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)
            getSectionHeader(position)?.let { header ->
                c.drawText(header, 16f, child.top - 25f, headerPaint)
            }
        }
    }
}
```

### Best Practices

1. **Cache `Paint`/`Drawable` objects** — create in constructor, not in onDraw
2. **Reuse decorations** — create one instance for all RecyclerViews
3. **Account for LayoutManager** — check type (Linear/Grid/Staggered)
4. **Don't modify ViewHolder** — ItemDecoration is isolated from adapter
5. **Multiple decorations** — can combine (order matters: first draws on bottom)

### Removing Decorations

```kotlin
recyclerView.removeItemDecoration(decoration)     // Remove specific
recyclerView.removeItemDecorationAt(0)            // By index
val count = recyclerView.itemDecorationCount      // Get count
```

---

## Follow-ups

1. What is the difference between `onDraw` and `onDrawOver`?
2. How do you create a sticky header using ItemDecoration?
3. How does ItemDecoration interact with `RecyclerView`'s item animator?
4. Can you modify item bounds in `getItemOffsets` dynamically based on scroll position?
5. How would you implement inset dividers (dividers that don't span full width)?

## References

- [`RecyclerView`.ItemDecoration Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/`RecyclerView`.ItemDecoration)
- [Android `Canvas` and Drawing Guide](https://developer.android.com/develop/ui/views/graphics/drawables)

## Related Questions

### Prerequisites / Concepts

- [[c-recyclerview]]


### Prerequisites
- `RecyclerView` basics (adapter, ViewHolder pattern)
- Understanding Android `Canvas` drawing

### Related
- `RecyclerView` ViewHolder lifecycle
- DiffUtil for efficient `RecyclerView` updates
- Custom LayoutManagers

### Advanced
- `RecyclerView` item animations with ItemDecoration
- Sticky headers implementation
- Performance optimization for complex decorations

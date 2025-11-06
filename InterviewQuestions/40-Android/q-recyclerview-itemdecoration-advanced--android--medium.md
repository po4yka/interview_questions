---
id: android-081
title: RecyclerView ItemDecoration Advanced / Продвинутый ItemDecoration для RecyclerView
aliases:
- RecyclerView ItemDecoration Advanced
- Продвинутый ItemDecoration для RecyclerView
topic: android
subtopics:
- ui-graphics
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
- c-itemdecoration
- q-recyclerview-basics--android--easy
created: 2025-10-13
updated: 2025-10-31
tags:
- android/ui-graphics
- android/ui-views
- custom-drawing
- difficulty/medium
- itemdecoration
- ui
sources:
- https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView.ItemDecoration
date created: Saturday, November 1st 2025, 1:04:10 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)
> Как создать пользовательские ItemDecorations для RecyclerView?

# Question (EN)
> How to create custom ItemDecorations for RecyclerView?

---

## Ответ (RU)

**Теория ItemDecoration:**
ItemDecoration позволяет добавлять пользовательскую отрисовку и отступы к элементам RecyclerView без изменения самих элементов. Идеально подходит для разделителей, отступов, sticky headers и визуальных эффектов.

**Фазы отрисовки:**
RecyclerView отрисовывается в 3 фазы:
1. `onDraw()` - отрисовка ПОД элементами (фоновые украшения)
2. Отрисовка элементов
3. `onDrawOver()` - отрисовка НАД элементами (передние украшения, sticky headers)

**Основные методы:**
- `onDraw()` - отрисовка украшений под элементами
- `onDrawOver()` - отрисовка украшений над элементами
- `getItemOffsets()` - добавление отступов вокруг элементов

```kotlin
// Базовый разделитель
class SimpleDividerDecoration(
    context: Context,
    private val dividerHeight: Int = 1.dpToPx(context)
) : RecyclerView.ItemDecoration() {

    private val paint = Paint().apply {
        color = Color.LTGRAY
        style = Paint.Style.FILL
    }

    // Добавление отступов для разделителя
    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        if (position != parent.adapter?.itemCount?.minus(1)) {
            outRect.bottom = dividerHeight
        }
    }

    // Отрисовка разделителя под элементами
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
}
```

**Sticky Header:**
```kotlin
class StickyHeaderDecoration : RecyclerView.ItemDecoration() {

    override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Отрисовка sticky header над элементами
        val topChild = parent.getChildAt(0) ?: return
        val topChildPosition = parent.getChildAdapterPosition(topChild)

        // Логика sticky header
        drawStickyHeader(canvas, parent, topChildPosition)
    }
}
```

**Использование:**
```kotlin
recyclerView.addItemDecoration(SimpleDividerDecoration(context))
recyclerView.addItemDecoration(StickyHeaderDecoration())
```

## Answer (EN)

**ItemDecoration Theory:**
ItemDecoration allows adding custom drawing and layout offsets to RecyclerView items without modifying the items themselves. Perfect for dividers, spacing, sticky headers, and visual effects.

**Drawing phases:**
RecyclerView drawing occurs in 3 phases:
1. `onDraw()` - Draw UNDER items (background decorations)
2. Item views drawn
3. `onDrawOver()` - Draw OVER items (foreground decorations, sticky headers)

**Main methods:**
- `onDraw()` - Draw decorations under items
- `onDrawOver()` - Draw decorations over items
- `getItemOffsets()` - Add spacing/padding around items

```kotlin
// Basic divider
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
}
```

**Sticky Header:**
```kotlin
class StickyHeaderDecoration : RecyclerView.ItemDecoration() {

    override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Draw sticky header over items
        val topChild = parent.getChildAt(0) ?: return
        val topChildPosition = parent.getChildAdapterPosition(topChild)

        // Sticky header logic
        drawStickyHeader(canvas, parent, topChildPosition)
    }
}
```

**Usage:**
```kotlin
recyclerView.addItemDecoration(SimpleDividerDecoration(context))
recyclerView.addItemDecoration(StickyHeaderDecoration())
```

---

## Follow-ups

- What's the difference between onDraw and onDrawOver?
- How do you optimize ItemDecoration performance?
- How do you handle ItemDecoration with different view types?


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Prerequisites / Concepts

- [[c-itemdecoration]]


### Prerequisites (Easier)
- [[q-recyclerview-basics--android--easy]] - RecyclerView basics
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-custom-drawing--android--medium]] - Custom drawing
- [[q-recyclerview-performance--android--medium]] - RecyclerView performance
- [[q-ui-customization--android--medium]] - UI customization

### Advanced (Harder)
- [[q-recyclerview-advanced--android--hard]] - RecyclerView advanced
- [[q-canvas-drawing-optimization--android--hard]] - Canvas optimization

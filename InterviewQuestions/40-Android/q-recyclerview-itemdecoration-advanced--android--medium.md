---
id: android-081
title: RecyclerView ItemDecoration Advanced / Продвинутый ItemDecoration для RecyclerView
aliases: [RecyclerView ItemDecoration Advanced, Продвинутый ItemDecoration для RecyclerView]
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
  - c-android-graphics
  - q-android-app-components--android--easy
  - q-camerax-advanced-pipeline--android--hard
  - q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy
  - q-recyclerview-diffutil-advanced--android--medium
created: 2025-10-13
updated: 2025-11-10
tags: [android/ui-graphics, android/ui-views, custom-drawing, difficulty/medium, itemdecoration, ui]
sources:
  - "https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView.ItemDecoration"
date created: Saturday, November 1st 2025, 1:04:10 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)
> Как создать пользовательские ItemDecorations для RecyclerView?

# Question (EN)
> How to create custom ItemDecorations for RecyclerView?

---

## Ответ (RU)

**Теория ItemDecoration:**
ItemDecoration позволяет добавлять пользовательскую отрисовку и отступы к элементам RecyclerView без изменения самих элементов. Подходит для разделителей, отступов, sticky headers и визуальных эффектов. См. также [[c-android-graphics]] для понимания основ отрисовки.

**Фазы отрисовки (хуки декораций):**
RecyclerView вызывает декорации вокруг собственной отрисовки элементов:
1. `onDraw()` — вызывается ДО отрисовки дочерних `View`, рисует ПОД элементами (фоновые украшения).
2. Отрисовка самих элементов.
3. `onDrawOver()` — вызывается ПОСЛЕ отрисовки элементов, рисует НАД элементами (передние украшения, sticky headers и т.п.).

**Основные методы:**
- `onDraw()` — отрисовка украшений под элементами.
- `onDrawOver()` — отрисовка украшений над элементами.
- `getItemOffsets()` — добавление отступов вокруг элементов (влияет на layout, но не рисует).

```kotlin
// Базовый разделитель (без разделителя после последнего элемента)
class SimpleDividerDecoration(
    context: Context,
    private val dividerHeight: Int = 1.dpToPx(context)
) : RecyclerView.ItemDecoration() {

    private val paint = Paint().apply {
        color = Color.LTGRAY
        style = Paint.Style.FILL
        isAntiAlias = false
    }

    // Добавление отступов для разделителя
    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val lastIndex = (parent.adapter?.itemCount ?: 0) - 1
        if (position != RecyclerView.NO_POSITION && position < lastIndex) {
            outRect.bottom = dividerHeight
        } else {
            outRect.set(0, 0, 0, 0)
        }
    }

    // Отрисовка разделителя под элементами (также без разделителя после последнего элемента)
    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft
        val right = parent.width - parent.paddingRight
        val adapter = parent.adapter ?: return
        val lastIndex = adapter.itemCount - 1

        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)
            if (position == RecyclerView.NO_POSITION || position >= lastIndex) continue

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

**Sticky Header (упрощённый пример):**
Ниже пример показывает, как использовать `onDrawOver` для закреплённого заголовка. Реальная реализация должна:
- уметь определить, какой заголовок относится к позиции (`topChildPosition`),
- создать/переиспользовать `View` заголовка и замерить его,
- нарисовать заголовок в `canvas` с учётом сдвига при прокрутке.

```kotlin
class StickyHeaderDecoration(
    private val getHeaderPositionForItem: (itemPosition: Int) -> Int,
    private val bindHeaderView: (header: View, headerPosition: Int) -> Unit,
    private val createHeaderView: (parent: RecyclerView) -> View
) : RecyclerView.ItemDecoration() {

    private var headerView: View? = null
    private var headerBounds = Rect()

    override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val topChild = parent.getChildAt(0) ?: return
        val topChildPosition = parent.getChildAdapterPosition(topChild)
        if (topChildPosition == RecyclerView.NO_POSITION) return

        val headerPosition = getHeaderPositionForItem(topChildPosition)
        if (headerPosition == RecyclerView.NO_POSITION) return

        val header = getHeaderView(parent, headerPosition)
        headerBounds.set(
            parent.paddingLeft,
            parent.paddingTop,
            parent.paddingLeft + header.measuredWidth,
            parent.paddingTop + header.measuredHeight
        )

        // Дополнительно можно сдвигать header вверх, если следующий header "наезжает".
        canvas.save()
        canvas.translate(headerBounds.left.toFloat(), headerBounds.top.toFloat())
        header.draw(canvas)
        canvas.restore()
    }

    private fun getHeaderView(parent: RecyclerView, headerPosition: Int): View {
        val header = headerView ?: createHeaderView(parent).also { headerView = it }
        bindHeaderView(header, headerPosition)

        // Убедиться, что header замерен перед отрисовкой
        val widthSpec = View.MeasureSpec.makeMeasureSpec(
            parent.measuredWidth - parent.paddingLeft - parent.paddingRight,
            View.MeasureSpec.EXACTLY
        )
        val heightSpec = View.MeasureSpec.makeMeasureSpec(
            0,
            View.MeasureSpec.UNSPECIFIED
        )
        header.measure(widthSpec, heightSpec)
        header.layout(0, 0, header.measuredWidth, header.measuredHeight)
        return header
    }
}
```

**Использование:**
```kotlin
recyclerView.addItemDecoration(SimpleDividerDecoration(context))

// Sticky header: реализация колбэков зависит от структуры адаптера/данных
recyclerView.addItemDecoration(
    StickyHeaderDecoration(
        getHeaderPositionForItem = { position -> /* вычислить позицию хедера */ -1 },
        bindHeaderView = { header, headerPosition -> /* привязать данные к header */ },
        createHeaderView = { parent -> /* создать View хедера */ View(parent.context) }
    )
)
```

## Answer (EN)

**ItemDecoration Theory:**
ItemDecoration allows adding custom drawing and layout offsets to RecyclerView items without modifying the item views themselves. It is commonly used for dividers, spacing, sticky headers, and visual effects. See also [[c-android-graphics]] for drawing fundamentals.

**Drawing phases (decoration hooks):**
RecyclerView calls decorations around its own item drawing:
1. `onDraw()` — called BEFORE child `View`s are drawn; draw UNDER items (background decorations).
2. Item views are drawn.
3. `onDrawOver()` — called AFTER item views are drawn; draw OVER items (foreground decorations, sticky headers, etc.).

**Main methods:**
- `onDraw()` — draw decorations under items.
- `onDrawOver()` — draw decorations over items.
- `getItemOffsets()` — add offsets around items (affects layout, does not draw).

```kotlin
// Basic divider (no divider after the last item)
class SimpleDividerDecoration(
    context: Context,
    private val dividerHeight: Int = 1.dpToPx(context)
) : RecyclerView.ItemDecoration() {

    private val paint = Paint().apply {
        color = Color.LTGRAY
        style = Paint.Style.FILL
        isAntiAlias = false
    }

    // Add spacing for divider
    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val lastIndex = (parent.adapter?.itemCount ?: 0) - 1
        if (position != RecyclerView.NO_POSITION && position < lastIndex) {
            outRect.bottom = dividerHeight
        } else {
            outRect.set(0, 0, 0, 0)
        }
    }

    // Draw divider under items (also skip after the last adapter item)
    override fun onDraw(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val left = parent.paddingLeft
        val right = parent.width - parent.paddingRight
        val adapter = parent.adapter ?: return
        val lastIndex = adapter.itemCount - 1

        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)
            if (position == RecyclerView.NO_POSITION || position >= lastIndex) continue

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

**Sticky Header (simplified example):**
The snippet below shows how to leverage `onDrawOver` for a pinned header. A full implementation should:
- determine which header corresponds to the current top item (`topChildPosition`),
- create/reuse and bind a header `View`,
- measure/layout the header and draw it on the canvas, optionally translating it when the next header pushes it.

```kotlin
class StickyHeaderDecoration(
    private val getHeaderPositionForItem: (itemPosition: Int) -> Int,
    private val bindHeaderView: (header: View, headerPosition: Int) -> Unit,
    private val createHeaderView: (parent: RecyclerView) -> View
) : RecyclerView.ItemDecoration() {

    private var headerView: View? = null
    private var headerBounds = Rect()

    override fun onDrawOver(canvas: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val topChild = parent.getChildAt(0) ?: return
        val topChildPosition = parent.getChildAdapterPosition(topChild)
        if (topChildPosition == RecyclerView.NO_POSITION) return

        val headerPosition = getHeaderPositionForItem(topChildPosition)
        if (headerPosition == RecyclerView.NO_POSITION) return

        val header = getHeaderView(parent, headerPosition)
        headerBounds.set(
            parent.paddingLeft,
            parent.paddingTop,
            parent.paddingLeft + header.measuredWidth,
            parent.paddingTop + header.measuredHeight
        )

        // Optionally adjust translation if the next header is about to overlap.
        canvas.save()
        canvas.translate(headerBounds.left.toFloat(), headerBounds.top.toFloat())
        header.draw(canvas)
        canvas.restore()
    }

    private fun getHeaderView(parent: RecyclerView, headerPosition: Int): View {
        val header = headerView ?: createHeaderView(parent).also { headerView = it }
        bindHeaderView(header, headerPosition)

        // Ensure header is measured before drawing
        val widthSpec = View.MeasureSpec.makeMeasureSpec(
            parent.measuredWidth - parent.paddingLeft - parent.paddingRight,
            View.MeasureSpec.EXACTLY
        )
        val heightSpec = View.MeasureSpec.makeMeasureSpec(
            0,
            View.MeasureSpec.UNSPECIFIED
        )
        header.measure(widthSpec, heightSpec)
        header.layout(0, 0, header.measuredWidth, header.measuredHeight)
        return header
    }
}
```

**Usage:**
```kotlin
recyclerView.addItemDecoration(SimpleDividerDecoration(context))

// Sticky header: callback implementations depend on adapter/data structure
recyclerView.addItemDecoration(
    StickyHeaderDecoration(
        getHeaderPositionForItem = { position -> /* compute header position */ -1 },
        bindHeaderView = { header, headerPosition -> /* bind data to header */ },
        createHeaderView = { parent -> /* create header View */ View(parent.context) }
    )
)
```

---

## Дополнительные Вопросы (RU)

- В чем разница между `onDraw` и `onDrawOver`?
- Как оптимизировать производительность `ItemDecoration`?
- Как обрабатывать `ItemDecoration` при разных типах элементов (`viewType`)?

## Follow-ups

- What's the difference between `onDraw` and `onDrawOver`?
- How do you optimize `ItemDecoration` performance?
- How do you handle `ItemDecoration` with different view types?

## Ссылки (RU)

- [Views](https://developer.android.com/develop/ui/views)
- [Документация Android](https://developer.android.com/docs)

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[q-android-app-components--android--easy]]

### Предпосылки (проще)
- [[q-android-app-components--android--easy]] - Базовые компоненты приложения

### Связанные (того Же уровня)
- [[q-canvas-drawing-optimization--android--hard]] - Оптимизация рисования на Canvas (сложнее, но по теме отрисовки)

## Related Questions

### Prerequisites / Concepts

- [[q-android-app-components--android--easy]]

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-canvas-drawing-optimization--android--hard]] - Canvas optimization (harder, but drawing-related)

---\
id: android-309
title: What Does ItemDecoration Do / Что делает ItemDecoration
aliases: [ItemDecoration, Что делает ItemDecoration]
topic: android
subtopics: [ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-ui-composition, c-android-view-system, c-recyclerview, q-android-app-components--android--easy, q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard, q-recyclerview-itemdecoration-advanced--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/ui-views, difficulty/medium, itemdecoration, recyclerview]
---\
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

    // Определение отступов/spacing (изменяет offsets элемента для layout, а не padding view)
    open fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: State
    )
}
```

**Назначение методов**:
- `getItemOffsets` — создаёт пространство вокруг элементов, изменяя offsets элемента до измерения/отрисовки (это не изменение `padding` view, а корректировка границ для layout).
- `onDraw` — рисует под элементами (фон, разделители), обычно для недиалоговых/неперекрывающих декораций.
- `onDrawOver` — рисует над элементами (overlay, sticky headers, эффекты, перекрывающие контент).

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
        val position = parent.getChildAdapterPosition(view)
        if (position == RecyclerView.NO_POSITION) return

        outRect.left = spacing
        outRect.right = spacing
        outRect.bottom = spacing

        // ✅ Отступ сверху только для первого элемента
        if (position == 0) {
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
        if (position == RecyclerView.NO_POSITION) return

        val column = position % spanCount

        if (includeEdge) {
            // ✅ Компенсация для равных отступов с краями
            outRect.left = spacing - column * spacing / spanCount
            outRect.right = (column + 1) * spacing / spanCount
            if (position < spanCount) outRect.top = spacing
            outRect.bottom = spacing
        } else {
            // ✅ Без краёв — визуально равномерные отступы между элементами, без внешних полей
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

    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
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
        if (position == RecyclerView.NO_POSITION) return

        // Ожидается, что getSectionHeader(position) != null только для элементов,
        // которые являются началом новой секции.
        if (getSectionHeader(position) != null) {
            outRect.top = 80 // Место для заголовка
        }
    }

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)
            if (position == RecyclerView.NO_POSITION) continue

            getSectionHeader(position)?.let { header ->
                c.drawText(header, 16f, child.top - 25f, headerPaint)
            }
        }
    }
}
```

### Лучшие Практики

1. **Кешируйте Paint/Drawable** — создавайте их в конструкторе, не в onDraw/onDrawOver.
2. **Переиспользуйте декорации аккуратно** — один ItemDecoration можно использовать повторно в пределах одного `RecyclerView` или для списков с одинаковой конфигурацией; не шарьте состояние между несвязанными списками, если оно зависит от их параметров.
3. **Учитывайте `LayoutManager`** — проверяйте тип (Linear/Grid/Staggered) при расчёте позиций и отступов.
4. **Не меняйте `ViewHolder` и бизнес-логику** — ItemDecoration предназначен для визуального оформления и не должен модифицировать содержимое `ViewHolder` или управлять данными.
5. **Множественные декорации** — можно комбинировать (порядок важен: первая добавленная рисуется снизу, последняя — сверху).

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

    // Define offset/spacing around items (adjusts item offsets for layout, not the view's padding)
    open fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: State
    )
}
```

**Method purposes**:
- `getItemOffsets` — creates space around items by adjusting item offsets before layout/drawing (this is not changing the view's `padding`, but its layout bounds).
- `onDraw` — draws below items (backgrounds, dividers), typically for non-overlay decorations.
- `onDrawOver` — draws above items (overlays, sticky headers, effects that may cover content).

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
        val position = parent.getChildAdapterPosition(view)
        if (position == RecyclerView.NO_POSITION) return

        outRect.left = spacing
        outRect.right = spacing
        outRect.bottom = spacing

        // ✅ Top spacing only for first item
        if (position == 0) {
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
        if (position == RecyclerView.NO_POSITION) return

        val column = position % spanCount

        if (includeEdge) {
            // ✅ Compensation for equal spacing with edges
            outRect.left = spacing - column * spacing / spanCount
            outRect.right = (column + 1) * spacing / spanCount
            if (position < spanCount) outRect.top = spacing
            outRect.bottom = spacing
        } else {
            // ✅ Without edges — visually equal spacing between items, no outer padding
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

    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
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
        if (position == RecyclerView.NO_POSITION) return

        // Expect getSectionHeader(position) != null only for items that start a new section.
        if (getSectionHeader(position) != null) {
            outRect.top = 80 // Space for header
        }
    }

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            val position = parent.getChildAdapterPosition(child)
            if (position == RecyclerView.NO_POSITION) continue

            getSectionHeader(position)?.let { header ->
                c.drawText(header, 16f, child.top - 25f, headerPaint)
            }
        }
    }
}
```

### Best Practices

1. **Cache Paint/Drawable objects** — create them in the constructor, not in onDraw/onDrawOver.
2. **Reuse decorations carefully** — you can reuse an ItemDecoration within a `RecyclerView` or across lists with matching configuration; avoid sharing stateful decorations across unrelated RecyclerViews.
3. **Account for `LayoutManager`** — check type (Linear/Grid/Staggered) when computing positions and offsets.
4. **Don't modify `ViewHolder` or business logic** — ItemDecoration is for visual concerns only; it should not alter `ViewHolder` contents or control data.
5. **Multiple decorations** — you can combine multiple decorations (order matters: the first added draws at the bottom, the last added on top).

### Removing Decorations

```kotlin
recyclerView.removeItemDecoration(decoration)     // Remove specific
recyclerView.removeItemDecorationAt(0)            // By index
val count = recyclerView.itemDecorationCount      // Get count
```

---

## Дополнительные Вопросы (RU)

1. В чем разница между `onDraw` и `onDrawOver`?
2. Как реализовать sticky header с помощью ItemDecoration?
3. Как ItemDecoration взаимодействует с аниматором элементов `RecyclerView`?
4. Можно ли динамически изменять отступы в `getItemOffsets` в зависимости от позиции прокрутки?
5. Как реализовать разделители-вставки (inset dividers), которые не занимают всю ширину?

## Follow-ups

1. What is the difference between `onDraw` and `onDrawOver`?
2. How do you create a sticky header using ItemDecoration?
3. How does ItemDecoration interact with `RecyclerView`'s item animator?
4. Can you modify item bounds in `getItemOffsets` dynamically based on scroll position?
5. How would you implement inset dividers (dividers that don't span full width)?

## Ссылки (RU)

- [Документация `RecyclerView`.ItemDecoration](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView.ItemDecoration)
- [Руководство по `Canvas` и рисованию в Android](https://developer.android.com/develop/ui/views/graphics/drawables)

## References

- [RecyclerView.ItemDecoration Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView.ItemDecoration)
- [Android `Canvas` and Drawing Guide](https://developer.android.com/develop/ui/views/graphics/drawables)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-recyclerview]]

### Предпосылки

- Базовое понимание `RecyclerView` (adapter, паттерн `ViewHolder`)
- Понимание рисования на `Canvas` в Android

### Связанные

- Жизненный цикл `ViewHolder` в `RecyclerView`
- Использование `DiffUtil` для эффективных обновлений `RecyclerView`
- Кастомные `LayoutManager`-ы

### Продвинутое

- Анимации элементов `RecyclerView` совместно с ItemDecoration
- Реализация sticky headers
- Оптимизация производительности для сложных декораций

## Related Questions

### Prerequisites / Concepts

- [[c-recyclerview]]

### Prerequisites

- `RecyclerView` basics (adapter, `ViewHolder` pattern)
- Understanding Android `Canvas` drawing

### Related

- `RecyclerView` `ViewHolder` lifecycle
- `DiffUtil` for efficient `RecyclerView` updates
- Custom LayoutManagers

### Advanced

- `RecyclerView` item animations with ItemDecoration
- Sticky headers implementation
- Performance optimization for complex decorations

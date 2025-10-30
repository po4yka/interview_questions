---
id: 20251020-200000
title: Custom ViewGroup Layout / Layout кастомных ViewGroup
aliases: ["Custom ViewGroup Layout", "Layout кастомных ViewGroup"]
topic: android
subtopics: [ui-views, ui-graphics]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-custom-drawable-implementation--android--medium, q-custom-view-attributes--android--medium, q-custom-view-lifecycle--android--medium]
created: 2025-10-20
updated: 2025-10-29
tags: [android/ui-views, android/ui-graphics, custom-views, layout, difficulty/hard]
sources: []
---
# Вопрос (RU)

> Как создать кастомный ViewGroup? Объясните процесс измерения и компоновки. Реализуйте FlowLayout, который располагает дочерние элементы в ряды с переносом.

# Question (EN)

> How do you create a custom ViewGroup? Explain the measurement and layout process. Implement a FlowLayout that arranges children in rows, wrapping to the next row when needed.

## Ответ (RU)

Создание кастомного ViewGroup требует понимания двухпроходного алгоритма: **измерение** (onMeasure) и **компоновка** (onLayout).

### Двухпроходный Алгоритм

**Проход 1: onMeasure**
- ViewGroup измеряет каждый дочерний элемент через `child.measure()`
- Рассчитывает собственный размер на основе размеров детей
- ОБЯЗАН вызвать `setMeasuredDimension(width, height)`

**Проход 2: onLayout**
- ViewGroup позиционирует каждый дочерний элемент через `child.layout(left, top, right, bottom)`
- Координаты задаются относительно родителя

### MeasureSpec Режимы

- `EXACTLY` — точный размер (`match_parent` или конкретное значение)
- `AT_MOST` — максимальный размер (`wrap_content`)
- `UNSPECIFIED` — без ограничений (редко)

### Реализация FlowLayout

```kotlin
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {

    var horizontalSpacing = 0
    var verticalSpacing = 0

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        val availableWidth = MeasureSpec.getSize(widthSpec) - paddingLeft - paddingRight

        var rowWidth = 0
        var rowHeight = 0
        var totalHeight = paddingTop + paddingBottom

        // ✅ Измеряем детей и считаем высоту
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            measureChildWithMargins(child, widthSpec, 0, heightSpec, 0)
            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            // Нужен ли перенос на новую строку?
            if (rowWidth + childWidth > availableWidth && rowWidth > 0) {
                totalHeight += rowHeight + verticalSpacing
                rowWidth = childWidth
                rowHeight = childHeight
            } else {
                rowWidth += childWidth + horizontalSpacing
                rowHeight = max(rowHeight, childHeight)
            }
        }
        totalHeight += rowHeight

        setMeasuredDimension(
            resolveSize(MeasureSpec.getSize(widthSpec), widthSpec),
            resolveSize(totalHeight, heightSpec)
        )
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        val availableWidth = right - left - paddingLeft - paddingRight
        var x = paddingLeft
        var y = paddingTop
        var rowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin

            // Перенос на новую строку
            if (x + childWidth > paddingLeft + availableWidth && x > paddingLeft) {
                x = paddingLeft
                y += rowHeight + verticalSpacing
                rowHeight = 0
            }

            // ✅ Позиционируем элемент
            child.layout(
                x + lp.leftMargin,
                y + lp.topMargin,
                x + lp.leftMargin + child.measuredWidth,
                y + lp.topMargin + child.measuredHeight
            )

            x += childWidth + horizontalSpacing
            rowHeight = max(rowHeight, child.measuredHeight + lp.topMargin + lp.bottomMargin)
        }
    }

    // ✅ Поддержка MarginLayoutParams
    override fun generateLayoutParams(attrs: AttributeSet?) = MarginLayoutParams(context, attrs)
    override fun generateDefaultLayoutParams() = MarginLayoutParams(WRAP_CONTENT, WRAP_CONTENT)
    override fun generateLayoutParams(p: LayoutParams?) = MarginLayoutParams(p)
    override fun checkLayoutParams(p: LayoutParams?) = p is MarginLayoutParams
}
```

### Критические Правила

**ОБЯЗАТЕЛЬНО:**
- Измерять дочерние элементы перед родителем
- Вызывать `setMeasuredDimension()` в конце `onMeasure()`
- Пропускать `GONE` элементы
- Учитывать padding родителя

**ЗАПРЕЩЕНО:**
- ❌ Вызывать `requestLayout()` внутри `onLayout()` (бесконечный цикл)
- ❌ Использовать `measuredWidth/Height` до вызова `measure()`
- ❌ Игнорировать `MeasureSpec` от родителя

### Оптимизации

**Кэширование:** Сохранить результаты `onMeasure()` для `onLayout()`:

```kotlin
private val childBounds = mutableListOf<Rect>()

override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    childBounds.clear()
    // Во время измерения сохраняем bounds
    for (i in 0 until childCount) {
        // ... измерение
        childBounds.add(Rect(left, top, right, bottom))
    }
    setMeasuredDimension(w, h)
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    // ✅ Используем сохранённые bounds
    for (i in 0 until childCount) {
        val bounds = childBounds[i]
        getChildAt(i).layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
    }
}
```

**RTL Support:** Используйте `ViewCompat.getLayoutDirection()` для поддержки RTL-раскладок.

## Answer (EN)

Creating a custom ViewGroup requires understanding the two-pass algorithm: **measure** (onMeasure) and **layout** (onLayout).

### Two-Pass Algorithm

**Pass 1: onMeasure**
- ViewGroup measures each child via `child.measure()`
- Calculates its own size based on children's sizes
- MUST call `setMeasuredDimension(width, height)`

**Pass 2: onLayout**
- ViewGroup positions each child via `child.layout(left, top, right, bottom)`
- Coordinates are relative to parent

### MeasureSpec Modes

- `EXACTLY` — exact size (`match_parent` or specific value)
- `AT_MOST` — maximum size (`wrap_content`)
- `UNSPECIFIED` — no constraints (rare)

### FlowLayout Implementation

```kotlin
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {

    var horizontalSpacing = 0
    var verticalSpacing = 0

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        val availableWidth = MeasureSpec.getSize(widthSpec) - paddingLeft - paddingRight

        var rowWidth = 0
        var rowHeight = 0
        var totalHeight = paddingTop + paddingBottom

        // ✅ Measure children and calculate height
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            measureChildWithMargins(child, widthSpec, 0, heightSpec, 0)
            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            // Do we need to wrap to next row?
            if (rowWidth + childWidth > availableWidth && rowWidth > 0) {
                totalHeight += rowHeight + verticalSpacing
                rowWidth = childWidth
                rowHeight = childHeight
            } else {
                rowWidth += childWidth + horizontalSpacing
                rowHeight = max(rowHeight, childHeight)
            }
        }
        totalHeight += rowHeight

        setMeasuredDimension(
            resolveSize(MeasureSpec.getSize(widthSpec), widthSpec),
            resolveSize(totalHeight, heightSpec)
        )
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        val availableWidth = right - left - paddingLeft - paddingRight
        var x = paddingLeft
        var y = paddingTop
        var rowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin

            // Wrap to next row
            if (x + childWidth > paddingLeft + availableWidth && x > paddingLeft) {
                x = paddingLeft
                y += rowHeight + verticalSpacing
                rowHeight = 0
            }

            // ✅ Position the child
            child.layout(
                x + lp.leftMargin,
                y + lp.topMargin,
                x + lp.leftMargin + child.measuredWidth,
                y + lp.topMargin + child.measuredHeight
            )

            x += childWidth + horizontalSpacing
            rowHeight = max(rowHeight, child.measuredHeight + lp.topMargin + lp.bottomMargin)
        }
    }

    // ✅ Support MarginLayoutParams
    override fun generateLayoutParams(attrs: AttributeSet?) = MarginLayoutParams(context, attrs)
    override fun generateDefaultLayoutParams() = MarginLayoutParams(WRAP_CONTENT, WRAP_CONTENT)
    override fun generateLayoutParams(p: LayoutParams?) = MarginLayoutParams(p)
    override fun checkLayoutParams(p: LayoutParams?) = p is MarginLayoutParams
}
```

### Critical Rules

**MUST:**
- Measure children before parent
- Call `setMeasuredDimension()` at end of `onMeasure()`
- Skip `GONE` children
- Account for parent's padding

**FORBIDDEN:**
- ❌ Call `requestLayout()` inside `onLayout()` (infinite loop)
- ❌ Use `measuredWidth/Height` before calling `measure()`
- ❌ Ignore `MeasureSpec` from parent

### Optimizations

**Caching:** Save `onMeasure()` results for `onLayout()`:

```kotlin
private val childBounds = mutableListOf<Rect>()

override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    childBounds.clear()
    // During measure, save bounds
    for (i in 0 until childCount) {
        // ... measurement
        childBounds.add(Rect(left, top, right, bottom))
    }
    setMeasuredDimension(w, h)
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    // ✅ Use cached bounds
    for (i in 0 until childCount) {
        val bounds = childBounds[i]
        getChildAt(i).layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
    }
}
```

**RTL Support:** Use `ViewCompat.getLayoutDirection()` for RTL layouts.

## Follow-ups

- How do you handle dynamic child addition/removal efficiently?
- What's the difference between `measureChild()` and `measureChildWithMargins()`?
- How do you implement custom LayoutParams with additional attributes?
- How would you optimize performance for 100+ children?
- How do you support RTL (right-to-left) layouts?

## References

- [[c-custom-views]]
- [[c-view-measurement]]
- [ViewGroup Documentation](https://developer.android.com/reference/android/view/ViewGroup)
- [Custom Views Tutorial](https://developer.android.com/guide/topics/ui/custom-components)

## Related Questions

### Prerequisites (Easier)

- [[q-custom-view-lifecycle--android--medium]] - Understanding View lifecycle
- [[q-custom-view-attributes--android--medium]] - Custom attributes basics

### Related (Same Level)

- [[q-custom-drawable-implementation--android--medium]] - Custom drawing
- [[q-constraint-layout-internals--android--hard]] - Complex layout system

### Advanced (Harder)

- [[q-view-performance-optimization--android--hard]] - Layout optimization
- [[q-async-layout-inflation--android--hard]] - Async inflation techniques

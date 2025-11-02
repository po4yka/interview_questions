---
id: android-454
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
updated: 2025-10-30
tags: [android/ui-views, android/ui-graphics, custom-views, layout, difficulty/hard]
sources: []
date created: Thursday, October 30th 2025, 12:03:04 pm
date modified: Thursday, October 30th 2025, 12:44:44 pm
---

# Вопрос (RU)

> Как создать кастомный ViewGroup? Объясните процесс измерения и компоновки. Реализуйте FlowLayout, который располагает дочерние элементы в ряды с переносом.

# Question (EN)

> How do you create a custom ViewGroup? Explain the measurement and layout process. Implement a FlowLayout that arranges children in rows, wrapping to the next row when needed.

## Ответ (RU)

Создание кастомного ViewGroup требует понимания двухпроходного алгоритма: **измерение** (onMeasure) и **компоновка** (onLayout).

### Двухпроходный Алгоритм

**Проход 1: onMeasure**
- Измеряет каждый дочерний элемент через `measureChild()` или `measureChildWithMargins()`
- Рассчитывает собственный размер на основе размеров детей и `MeasureSpec` от родителя
- ОБЯЗАН вызвать `setMeasuredDimension(width, height)`

**Проход 2: onLayout**
- Позиционирует каждый дочерний элемент через `child.layout(left, top, right, bottom)`
- Координаты относительно родителя; учитывает padding и margins

### MeasureSpec

`MeasureSpec` — 32-битное число: старшие 2 бита — режим, остальные 30 — размер.

- `EXACTLY` — точный размер (`match_parent` или конкретное значение `dp`)
- `AT_MOST` — максимальный размер (`wrap_content`)
- `UNSPECIFIED` — без ограничений (ScrollView, ListView)

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
- Измерять детей перед вызовом `setMeasuredDimension()`
- Вызывать `setMeasuredDimension()` в конце `onMeasure()`
- Пропускать `GONE` элементы (`child.visibility == GONE`)
- Учитывать padding родителя и margins детей

**ЗАПРЕЩЕНО:**
- ❌ Вызывать `requestLayout()` внутри `onLayout()` → бесконечный цикл
- ❌ Использовать `measuredWidth/Height` до вызова `measure()`
- ❌ Игнорировать `MeasureSpec` от родителя — нарушение контракта

### Оптимизации

**1. Кэширование bounds между onMeasure/onLayout:**

```kotlin
private val childBounds = mutableListOf<Rect>()

override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    childBounds.clear()
    for (i in 0 until childCount) {
        // Во время измерения сохраняем bounds
        childBounds.add(Rect(left, top, right, bottom))
    }
    setMeasuredDimension(w, h)
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    // ✅ Избегаем повторных вычислений
    childBounds.forEachIndexed { i, bounds ->
        getChildAt(i).layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
    }
}
```

**2. RTL Support:**

```kotlin
val isRtl = ViewCompat.getLayoutDirection(this) == ViewCompat.LAYOUT_DIRECTION_RTL
val startX = if (isRtl) width - paddingRight else paddingLeft
```

## Answer (EN)

Creating a custom ViewGroup requires understanding the two-pass algorithm: **measure** (onMeasure) and **layout** (onLayout).

### Two-Pass Algorithm

**Pass 1: onMeasure**
- Measures each child via `measureChild()` or `measureChildWithMargins()`
- Calculates its own size based on children's sizes and parent's `MeasureSpec`
- MUST call `setMeasuredDimension(width, height)`

**Pass 2: onLayout**
- Positions each child via `child.layout(left, top, right, bottom)`
- Coordinates relative to parent; accounts for padding and margins

### MeasureSpec

`MeasureSpec` is a 32-bit value: upper 2 bits = mode, lower 30 bits = size.

- `EXACTLY` — exact size (`match_parent` or specific `dp` value)
- `AT_MOST` — maximum size (`wrap_content`)
- `UNSPECIFIED` — no constraints (ScrollView, ListView)

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
- Measure children before calling `setMeasuredDimension()`
- Call `setMeasuredDimension()` at end of `onMeasure()`
- Skip `GONE` children (`child.visibility == GONE`)
- Account for parent's padding and child margins

**FORBIDDEN:**
- ❌ Call `requestLayout()` inside `onLayout()` → infinite loop
- ❌ Use `measuredWidth/Height` before calling `measure()`
- ❌ Ignore `MeasureSpec` from parent — contract violation

### Optimizations

**1. Cache bounds between onMeasure/onLayout:**

```kotlin
private val childBounds = mutableListOf<Rect>()

override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    childBounds.clear()
    for (i in 0 until childCount) {
        // Save bounds during measurement
        childBounds.add(Rect(left, top, right, bottom))
    }
    setMeasuredDimension(w, h)
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    // ✅ Avoid recalculation
    childBounds.forEachIndexed { i, bounds ->
        getChildAt(i).layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
    }
}
```

**2. RTL Support:**

```kotlin
val isRtl = ViewCompat.getLayoutDirection(this) == ViewCompat.LAYOUT_DIRECTION_RTL
val startX = if (isRtl) width - paddingRight else paddingLeft
```

## Follow-ups

- How would you handle dynamic child addition/removal without triggering full remeasurement?
- What's the difference between `measureChild()` and `measureChildWithMargins()`? When to use each?
- How would you implement baseline alignment across rows in FlowLayout?
- How would you optimize performance for 100+ children? Consider view recycling strategies.
- How does `requestLayout()` differ from `invalidate()`? When does each trigger measurement vs. drawing?

## References

- [ViewGroup Documentation](https://developer.android.com/reference/android/view/ViewGroup)
- [Custom Views Guide](https://developer.android.com/guide/topics/ui/custom-components)
- [View Measurement Process](https://developer.android.com/guide/topics/ui/how-android-draws)

## Related Questions

### Prerequisites

- [[q-custom-view-lifecycle--android--medium]] - View lifecycle and drawing order
- [[q-custom-view-attributes--android--medium]] - Custom XML attributes

### Related

- [[q-custom-drawable-implementation--android--medium]] - Custom drawing in Views
- Custom ConstraintLayout-like system - Layout constraint solving
- View performance optimization - Layout pass optimization

### Advanced

- Complex FlowLayout with baseline alignment
- AsyncLayoutInflater implementation - Background layout inflation
- RecyclerView layout manager internals

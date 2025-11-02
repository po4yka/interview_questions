---
id: android-454
title: Custom ViewGroup Layout / Layout кастомных ViewGroup
aliases: [Custom ViewGroup Layout, Layout кастомных ViewGroup]
topic: android
subtopics:
  - ui-graphics
  - ui-views
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-custom-drawable-implementation--android--medium
  - q-custom-view-attributes--android--medium
  - q-custom-view-lifecycle--android--medium
created: 2025-10-20
updated: 2025-11-02
tags: [android/ui-graphics, android/ui-views, custom-views, difficulty/hard, layout]
sources: []
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Sunday, November 2nd 2025, 5:28:27 pm
---

# Вопрос (RU)

> Как создать кастомный ViewGroup? Объясните процесс измерения и компоновки. Реализуйте FlowLayout, который располагает дочерние элементы в ряды с переносом.

# Question (EN)

> How do you create a custom ViewGroup? Explain the measurement and layout process. Implement a FlowLayout that arranges children in rows, wrapping to the next row when needed.

## Ответ (RU)

Создание кастомного `ViewGroup` требует понимания двухпроходного алгоритма: **измерение** (`onMeasure`) и **компоновка** (`onLayout`). Эти методы вызываются системой для определения размеров и позиций всех дочерних элементов.

### Двухпроходный Алгоритм

**Проход 1: `onMeasure`** — определение размеров:
- Измеряет каждый дочерний элемент через `measureChild()` или `measureChildWithMargins()`
- Рассчитывает собственный размер на основе размеров детей и `MeasureSpec` от родителя
- **ОБЯЗАН** вызвать `setMeasuredDimension(width, height)` — без этого View не отрисуется

**Проход 2: `onLayout`** — позиционирование:
- Позиционирует каждый дочерний элемент через `child.layout(left, top, right, bottom)`
- Координаты относительно родителя; учитывает `padding` родителя и `margins` детей

### MeasureSpec

`MeasureSpec` — 32-битное число, объединяющее режим (2 старших бита) и размер (30 младших бит). Режим определяет, как интерпретировать размер:

- **`EXACTLY`** — точный размер требуется (`match_parent` или конкретное значение в `dp`)
- **`AT_MOST`** — максимальный размер, можно меньше (`wrap_content`)
- **`UNSPECIFIED`** — без ограничений (используется в `ScrollView`, `ListView` для измерения контента)

### Реализация FlowLayout

```kotlin
class FlowLayout(context: Context, attrs: AttributeSet? = null) : ViewGroup(context, attrs) {
    var horizontalSpacing = 0
    var verticalSpacing = 0

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        val availableWidth = MeasureSpec.getSize(widthSpec) - paddingLeft - paddingRight
        var rowWidth = 0
        var rowHeight = 0
        var totalHeight = paddingTop + paddingBottom

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            measureChildWithMargins(child, widthSpec, 0, heightSpec, 0)
            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            if (rowWidth + childWidth > availableWidth && rowWidth > 0) {
                totalHeight += rowHeight + verticalSpacing
                rowWidth = childWidth
                rowHeight = childHeight
            } else {
                rowWidth += childWidth + horizontalSpacing
                rowHeight = max(rowHeight, childHeight)
            }
        }
        setMeasuredDimension(
            resolveSize(MeasureSpec.getSize(widthSpec), widthSpec),
            resolveSize(totalHeight + rowHeight, heightSpec)
        )
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        val availableWidth = r - l - paddingLeft - paddingRight
        var x = paddingLeft
        var y = paddingTop
        var rowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin

            if (x + childWidth > paddingLeft + availableWidth && x > paddingLeft) {
                x = paddingLeft
                y += rowHeight + verticalSpacing
                rowHeight = 0
            }

            child.layout(
                x + lp.leftMargin, y + lp.topMargin,
                x + lp.leftMargin + child.measuredWidth,
                y + lp.topMargin + child.measuredHeight
            )
            x += childWidth + horizontalSpacing
            rowHeight = max(rowHeight, child.measuredHeight + lp.topMargin + lp.bottomMargin)
        }
    }

    override fun generateLayoutParams(attrs: AttributeSet?) = MarginLayoutParams(context, attrs)
    override fun generateDefaultLayoutParams() = MarginLayoutParams(WRAP_CONTENT, WRAP_CONTENT)
    override fun generateLayoutParams(p: LayoutParams?) = MarginLayoutParams(p)
    override fun checkLayoutParams(p: LayoutParams?) = p is MarginLayoutParams
}
```

### Критические Правила

**ОБЯЗАТЕЛЬНО:**
- Измерять всех детей через `measureChild()` или `measureChildWithMargins()` перед расчетом собственного размера
- Вызывать `setMeasuredDimension()` в конце `onMeasure()` — без этого View не отрисуется
- Пропускать `GONE` элементы (`child.visibility == View.GONE`) — они не занимают место
- Учитывать `padding` родителя и `margins` детей при расчете размеров и позиций
- Использовать `resolveSize()` для учета `MeasureSpec` от родителя

**ЗАПРЕЩЕНО:**
- ❌ Вызывать `requestLayout()` внутри `onLayout()` → бесконечный цикл
- ❌ Использовать `measuredWidth`/`measuredHeight` до вызова `measure()` на дочернем элементе
- ❌ Игнорировать `MeasureSpec` от родителя — нарушение контракта измерения
- ❌ Позиционировать детей вне границ родителя (без учета `padding`)

### Оптимизации

**1. Кэширование bounds** между `onMeasure`/`onLayout` для избежания повторных вычислений:

```kotlin
private val childBounds = mutableListOf<Rect>()

override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    childBounds.clear()
    // Сохраняем вычисленные позиции во время измерения
    for (i in 0 until childCount) {
        childBounds.add(calculateChildBounds(i))
    }
    setMeasuredDimension(w, h)
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    childBounds.forEachIndexed { i, bounds ->
        getChildAt(i).layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
    }
}
```

**2. RTL Support** — учет направления письма для арабского/иврита:

```kotlin
val isRtl = ViewCompat.getLayoutDirection(this) == ViewCompat.LAYOUT_DIRECTION_RTL
val startX = if (isRtl) width - paddingRight else paddingLeft
```

## Answer (EN)

Creating a custom `ViewGroup` requires understanding the two-pass algorithm: **measure** (`onMeasure`) and **layout** (`onLayout`). These methods are called by the system to determine sizes and positions of all child views.

### Two-Pass Algorithm

**Pass 1: `onMeasure`** — size determination:
- Measures each child via `measureChild()` or `measureChildWithMargins()`
- Calculates its own size based on children's sizes and parent's `MeasureSpec`
- **MUST** call `setMeasuredDimension(width, height)` — without this, View won't render

**Pass 2: `onLayout`** — positioning:
- Positions each child via `child.layout(left, top, right, bottom)`
- Coordinates relative to parent; accounts for parent's `padding` and children's `margins`

### MeasureSpec

`MeasureSpec` is a 32-bit value combining mode (upper 2 bits) and size (lower 30 bits). The mode determines how to interpret the size:

- **`EXACTLY`** — exact size required (`match_parent` or specific `dp` value)
- **`AT_MOST`** — maximum size, can be smaller (`wrap_content`)
- **`UNSPECIFIED`** — no constraints (used in `ScrollView`, `ListView` for content measurement)

### FlowLayout Implementation

```kotlin
class FlowLayout(context: Context, attrs: AttributeSet? = null) : ViewGroup(context, attrs) {
    var horizontalSpacing = 0
    var verticalSpacing = 0

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        val availableWidth = MeasureSpec.getSize(widthSpec) - paddingLeft - paddingRight
        var rowWidth = 0
        var rowHeight = 0
        var totalHeight = paddingTop + paddingBottom

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            measureChildWithMargins(child, widthSpec, 0, heightSpec, 0)
            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            if (rowWidth + childWidth > availableWidth && rowWidth > 0) {
                totalHeight += rowHeight + verticalSpacing
                rowWidth = childWidth
                rowHeight = childHeight
            } else {
                rowWidth += childWidth + horizontalSpacing
                rowHeight = max(rowHeight, childHeight)
            }
        }
        setMeasuredDimension(
            resolveSize(MeasureSpec.getSize(widthSpec), widthSpec),
            resolveSize(totalHeight + rowHeight, heightSpec)
        )
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        val availableWidth = r - l - paddingLeft - paddingRight
        var x = paddingLeft
        var y = paddingTop
        var rowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams
            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin

            if (x + childWidth > paddingLeft + availableWidth && x > paddingLeft) {
                x = paddingLeft
                y += rowHeight + verticalSpacing
                rowHeight = 0
            }

            child.layout(
                x + lp.leftMargin, y + lp.topMargin,
                x + lp.leftMargin + child.measuredWidth,
                y + lp.topMargin + child.measuredHeight
            )
            x += childWidth + horizontalSpacing
            rowHeight = max(rowHeight, child.measuredHeight + lp.topMargin + lp.bottomMargin)
        }
    }

    override fun generateLayoutParams(attrs: AttributeSet?) = MarginLayoutParams(context, attrs)
    override fun generateDefaultLayoutParams() = MarginLayoutParams(WRAP_CONTENT, WRAP_CONTENT)
    override fun generateLayoutParams(p: LayoutParams?) = MarginLayoutParams(p)
    override fun checkLayoutParams(p: LayoutParams?) = p is MarginLayoutParams
}
```

### Critical Rules

**MUST:**
- Measure all children via `measureChild()` or `measureChildWithMargins()` before calculating own size
- Call `setMeasuredDimension()` at end of `onMeasure()` — without this, View won't render
- Skip `GONE` children (`child.visibility == View.GONE`) — they don't take space
- Account for parent's `padding` and children's `margins` when calculating sizes and positions
- Use `resolveSize()` to respect parent's `MeasureSpec`

**FORBIDDEN:**
- ❌ Call `requestLayout()` inside `onLayout()` → infinite loop
- ❌ Use `measuredWidth`/`measuredHeight` before calling `measure()` on child
- ❌ Ignore `MeasureSpec` from parent — measurement contract violation
- ❌ Position children outside parent bounds (without accounting for `padding`)

### Optimizations

**1. Cache bounds** between `onMeasure`/`onLayout` to avoid recalculation:

```kotlin
private val childBounds = mutableListOf<Rect>()

override fun onMeasure(widthSpec: Int, heightSpec: Int) {
    childBounds.clear()
    // Save calculated positions during measurement
    for (i in 0 until childCount) {
        childBounds.add(calculateChildBounds(i))
    }
    setMeasuredDimension(w, h)
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    childBounds.forEachIndexed { i, bounds ->
        getChildAt(i).layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
    }
}
```

**2. RTL Support** — account for right-to-left writing direction for Arabic/Hebrew:

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

### Prerequisites (Easier)
- [[q-custom-view-lifecycle--android--medium]] — View lifecycle and drawing order
- [[q-custom-view-attributes--android--medium]] — Custom XML attributes

### Related (Same Level)
- [[q-custom-drawable-implementation--android--medium]] — Custom drawing in Views
- Layout constraint solving systems
- Layout pass optimization techniques

### Advanced (Harder)
- Complex `FlowLayout` with baseline alignment
- `AsyncLayoutInflater` implementation — background layout inflation
- `RecyclerView` layout manager internals

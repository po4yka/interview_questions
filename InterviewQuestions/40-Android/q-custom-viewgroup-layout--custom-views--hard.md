---
id: 20251020-200000
title: Custom ViewGroup Layout / Layout кастомных ViewGroup
aliases:
  - Custom ViewGroup Layout
  - Layout кастомных ViewGroup
topic: android
subtopics:
  - ui-views
  - ui-layout
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-custom-view-lifecycle--custom-views--medium
  - q-custom-view-attributes--custom-views--medium
  - q-custom-drawable-implementation--custom-views--medium
created: 2025-10-20
updated: 2025-10-20
tags:
  - android/ui-views
  - android/ui-layout
  - custom-viewgroup
  - viewgroup
  - layout
  - measurement
  - difficulty/hard
source: https://developer.android.com/reference/android/view/ViewGroup
source_note: Official ViewGroup documentation
---

# Вопрос (RU)
> Как создать кастомный ViewGroup? Объясните процесс измерения и компоновки. Реализуйте кастомный FlowLayout, который располагает дочерние элементы в ряды, переносясь на следующий ряд при необходимости.

# Question (EN)
> How do you create a custom ViewGroup? Explain the measurement and layout process. Implement a custom FlowLayout that arranges children in rows, wrapping to the next row when needed.

## Ответ (RU)

Создание **кастомного ViewGroup** сложнее простого кастомного View, поскольку нужно управлять измерением и компоновкой как собственного элемента, так и всех дочерних элементов.

### Теория: Двухпроходный алгоритм компоновки

**1. Проход измерения (onMeasure)**
- Родитель измеряет каждый дочерний элемент через `child.measure()`
- Родитель рассчитывает собственный размер на основе размеров дочерних элементов
- Обязательно вызывается `setMeasuredDimension()`

**2. Проход компоновки (onLayout)**
- Родитель позиционирует каждый дочерний элемент через `child.layout()`
- Дочерние элементы получают свои координаты в системе родителя

### Ключевые концепции

**MeasureSpec** определяет требования к размеру:
- `EXACTLY` - точный размер (match_parent, конкретное значение)
- `AT_MOST` - максимальный размер (wrap_content)
- `UNSPECIFIED` - без ограничений (редко используется)

**LayoutParams** определяют параметры дочернего элемента:
- `MarginLayoutParams` - поддерживает margins
- Кастомные LayoutParams - для специфичных требований

### Базовая реализация FlowLayout

```kotlin
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    var horizontalSpacing: Int = 0
    var verticalSpacing: Int = 0

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)

        val availableWidth = if (widthMode == MeasureSpec.UNSPECIFIED) {
            Int.MAX_VALUE
        } else {
            widthSize - paddingLeft - paddingRight
        }

        var currentRowWidth = 0
        var currentRowHeight = 0
        var totalHeight = 0

        // Измеряем каждый дочерний элемент
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            measureChildWithMargins(child, widthMeasureSpec, 0, heightMeasureSpec, 0)

            val childWidth = child.measuredWidth + (child.layoutParams as? MarginLayoutParams)?.let {
                it.leftMargin + it.rightMargin
            } ?: 0

            val childHeight = child.measuredHeight + (child.layoutParams as? MarginLayoutParams)?.let {
                it.topMargin + it.bottomMargin
            } ?: 0

            // Проверяем нужен ли перенос
            if (currentRowWidth + childWidth > availableWidth && currentRowWidth > 0) {
                totalHeight += currentRowHeight + verticalSpacing
                currentRowWidth = childWidth
                currentRowHeight = childHeight
            } else {
                currentRowWidth += childWidth + horizontalSpacing
                currentRowHeight = max(currentRowHeight, childHeight)
            }
        }

        totalHeight += currentRowHeight + paddingTop + paddingBottom
        val finalWidth = resolveSize(widthSize, widthMeasureSpec)
        val finalHeight = resolveSize(totalHeight, heightMeasureSpec)

        setMeasuredDimension(finalWidth, finalHeight)
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        val availableWidth = right - left - paddingLeft - paddingRight
        var currentX = paddingLeft
        var currentY = paddingTop
        var currentRowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val childWidth = child.measuredWidth
            val childHeight = child.measuredHeight
            val lp = child.layoutParams as? MarginLayoutParams

            val totalChildWidth = childWidth + (lp?.leftMargin ?: 0) + (lp?.rightMargin ?: 0)

            // Проверяем нужен ли перенос
            if (currentX + totalChildWidth > paddingLeft + availableWidth && currentX > paddingLeft) {
                currentX = paddingLeft
                currentY += currentRowHeight + verticalSpacing
                currentRowHeight = 0
            }

            val childLeft = currentX + (lp?.leftMargin ?: 0)
            val childTop = currentY + (lp?.topMargin ?: 0)

            child.layout(
                childLeft,
                childTop,
                childLeft + childWidth,
                childTop + childHeight
            )

            currentX += totalChildWidth + horizontalSpacing
            currentRowHeight = max(currentRowHeight, childHeight + (lp?.topMargin ?: 0) + (lp?.bottomMargin ?: 0))
        }
    }

    // Поддержка MarginLayoutParams
    override fun generateLayoutParams(attrs: AttributeSet?): LayoutParams {
        return MarginLayoutParams(context, attrs)
    }

    override fun generateDefaultLayoutParams(): LayoutParams {
        return MarginLayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)
    }

    override fun generateLayoutParams(p: LayoutParams?): LayoutParams {
        return MarginLayoutParams(p)
    }

    override fun checkLayoutParams(p: LayoutParams?): Boolean {
        return p is MarginLayoutParams
    }
}
```

### Лучшие практики

**Измерение:**
- Всегда измеряйте дочерние элементы перед родительским
- Используйте `measureChildWithMargins()` для поддержки margins
- Пропускайте элементы с `visibility == GONE`
- Обязательно вызывайте `setMeasuredDimension()`

**Компоновка:**
- Используйте измеренные размеры из `onMeasure()`
- Учитывайте padding родителя
- Поддерживайте RTL-компоновки

**Производительность:**
- Кэшируйте вычисления между `onMeasure()` и `onLayout()`
- Избегайте создания объектов в циклах измерения/компоновки

### Распространенные ошибки

**Забыли `setMeasuredDimension()`** - приводит к краху
**Не измерили дочерние элементы** - `measuredWidth/Height` будут равны 0
**Вызов `requestLayout()` в `onLayout()`** - создает бесконечный цикл
**Игнорирование `MeasureSpec`** - нарушает контракт с родителем

## Answer (EN)

Creating a **custom ViewGroup** is more complex than a simple custom View because you need to handle measurement and layout for both your own element and all child elements.

### Theory: Two-Pass Layout Algorithm

**1. Measure Pass (onMeasure)**
- Parent measures each child via `child.measure()`
- Parent calculates its own size based on children's sizes
- Must call `setMeasuredDimension()`

**2. Layout Pass (onLayout)**
- Parent positions each child via `child.layout()`
- Children receive their coordinates in parent's coordinate system

### Key Concepts

**MeasureSpec** defines size requirements:
- `EXACTLY` - exact size (match_parent, specific value)
- `AT_MOST` - maximum size (wrap_content)
- `UNSPECIFIED` - no constraints (rarely used)

**LayoutParams** define child parameters:
- `MarginLayoutParams` - supports margins
- Custom LayoutParams - for specific requirements

### Basic FlowLayout Implementation

```kotlin
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    var horizontalSpacing: Int = 0
    var verticalSpacing: Int = 0

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)

        val availableWidth = if (widthMode == MeasureSpec.UNSPECIFIED) {
            Int.MAX_VALUE
        } else {
            widthSize - paddingLeft - paddingRight
        }

        var currentRowWidth = 0
        var currentRowHeight = 0
        var totalHeight = 0

        // Measure each child
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            measureChildWithMargins(child, widthMeasureSpec, 0, heightMeasureSpec, 0)

            val childWidth = child.measuredWidth + (child.layoutParams as? MarginLayoutParams)?.let {
                it.leftMargin + it.rightMargin
            } ?: 0

            val childHeight = child.measuredHeight + (child.layoutParams as? MarginLayoutParams)?.let {
                it.topMargin + it.bottomMargin
            } ?: 0

            // Check if wrapping is needed
            if (currentRowWidth + childWidth > availableWidth && currentRowWidth > 0) {
                totalHeight += currentRowHeight + verticalSpacing
                currentRowWidth = childWidth
                currentRowHeight = childHeight
            } else {
                currentRowWidth += childWidth + horizontalSpacing
                currentRowHeight = max(currentRowHeight, childHeight)
            }
        }

        totalHeight += currentRowHeight + paddingTop + paddingBottom
        val finalWidth = resolveSize(widthSize, widthMeasureSpec)
        val finalHeight = resolveSize(totalHeight, heightMeasureSpec)

        setMeasuredDimension(finalWidth, finalHeight)
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        val availableWidth = right - left - paddingLeft - paddingRight
        var currentX = paddingLeft
        var currentY = paddingTop
        var currentRowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val childWidth = child.measuredWidth
            val childHeight = child.measuredHeight
            val lp = child.layoutParams as? MarginLayoutParams

            val totalChildWidth = childWidth + (lp?.leftMargin ?: 0) + (lp?.rightMargin ?: 0)

            // Check if wrapping is needed
            if (currentX + totalChildWidth > paddingLeft + availableWidth && currentX > paddingLeft) {
                currentX = paddingLeft
                currentY += currentRowHeight + verticalSpacing
                currentRowHeight = 0
            }

            val childLeft = currentX + (lp?.leftMargin ?: 0)
            val childTop = currentY + (lp?.topMargin ?: 0)

            child.layout(
                childLeft,
                childTop,
                childLeft + childWidth,
                childTop + childHeight
            )

            currentX += totalChildWidth + horizontalSpacing
            currentRowHeight = max(currentRowHeight, childHeight + (lp?.topMargin ?: 0) + (lp?.bottomMargin ?: 0))
        }
    }

    // Support MarginLayoutParams
    override fun generateLayoutParams(attrs: AttributeSet?): LayoutParams {
        return MarginLayoutParams(context, attrs)
    }

    override fun generateDefaultLayoutParams(): LayoutParams {
        return MarginLayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)
    }

    override fun generateLayoutParams(p: LayoutParams?): LayoutParams {
        return MarginLayoutParams(p)
    }

    override fun checkLayoutParams(p: LayoutParams?): Boolean {
        return p is MarginLayoutParams
    }
}
```

### Best Practices

**Measurement:**
- Always measure children before parent
- Use `measureChildWithMargins()` for margin support
- Skip elements with `visibility == GONE`
- Must call `setMeasuredDimension()`

**Layout:**
- Use measured dimensions from `onMeasure()`
- Account for parent's padding
- Support RTL layouts

**Performance:**
- Cache calculations between `onMeasure()` and `onLayout()`
- Avoid object creation in measure/layout loops

### Common Pitfalls

**Forgot `setMeasuredDimension()`** - causes crash
**Didn't measure children** - `measuredWidth/Height` will be 0
**Calling `requestLayout()` in `onLayout()`** - creates infinite loop
**Ignoring `MeasureSpec`** - violates parent contract

## Follow-ups

- How to handle dynamic child addition/removal?
- What's the difference between `measureChild()` and `measureChildWithMargins()`?
- How to implement custom LayoutParams?
- How to optimize performance for large child counts?

## References

- [Android ViewGroup Documentation](https://developer.android.com/reference/android/view/ViewGroup)
- [Custom ViewGroup Tutorial](https://developer.android.com/guide/topics/ui/custom-components#custom-layout)

## Related Questions

### Prerequisites (Easier)
- [[q-custom-view-lifecycle--custom-views--medium]]

### Related (Same Level)
- [[q-custom-view-attributes--custom-views--medium]]
- [[q-custom-drawable-implementation--custom-views--medium]]

### Advanced (Harder)
- [[q-custom-view-animation--custom-views--medium]]

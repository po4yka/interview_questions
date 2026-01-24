---
id: android-454
title: Custom ViewGroup Layout / Layout кастомных ViewGroup
aliases:
- Custom ViewGroup Layout
- Layout кастомных ViewGroup
topic: android
subtopics:
- ui-views
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-custom-views
- q-compose-custom-animations--android--medium
- q-compose-custom-layout--android--hard
- q-custom-drawable-implementation--android--medium
- q-custom-view-attributes--android--medium
- q-custom-view-lifecycle--android--medium
- q-mlkit-custom-models--android--hard
created: 2025-10-20
updated: 2025-11-10
tags:
- android/ui-views
- custom-views
- difficulty/hard
- layout
sources: []
anki_cards:
- slug: android-454-0-en
  language: en
  anki_id: 1768366344675
  synced_at: '2026-01-23T16:45:06.021861'
- slug: android-454-0-ru
  language: ru
  anki_id: 1768366344700
  synced_at: '2026-01-23T16:45:06.023103'
---
# Вопрос (RU)

> Как создать кастомный `ViewGroup`? Объясните процесс измерения и компоновки. Реализуйте FlowLayout, который располагает дочерние элементы в ряды с переносом.

# Question (EN)

> How do you create a custom `ViewGroup`? Explain the measurement and layout process. Implement a FlowLayout that arranges children in rows, wrapping to the next row when needed.

## Ответ (RU)

Создание кастомного `ViewGroup` требует понимания двухпроходного алгоритма: **измерение** (`onMeasure`) и **компоновка** (`onLayout`). Эти методы вызываются системой для определения размеров и позиций всех дочерних элементов.

### Двухпроходный Алгоритм

**Проход 1: `onMeasure`** — определение размеров:
- Измеряет каждый дочерний элемент через `measureChild()` или `measureChildWithMargins()` с учетом `MeasureSpec`, полученного от родителя.
- Рассчитывает собственный размер на основе размеров детей, внутренних отступов (`padding`) и ограничений `MeasureSpec`.
- **ОБЯЗАН** вызвать `setMeasuredDimension(width, height)` — без этого `View` не будет корректно измерен и отрисован.

**Проход 2: `onLayout`** — позиционирование:
- Позиционирует каждый дочерний элемент через `child.layout(left, top, right, bottom)`.
- Координаты задаются относительно родителя; учитываются `padding` родителя и `margins` детей.

### MeasureSpec

`MeasureSpec` — 32-битное число, объединяющее режим (2 старших бита) и размер (30 младших бит). Режим определяет, как интерпретировать размер:

- **`EXACTLY`** — родитель требует точный размер (`match_parent` или конкретное значение в `dp`).
- **`AT_MOST`** — максимальный доступный размер, можно занять меньше (обычное поведение для `wrap_content`).
- **`UNSPECIFIED`** — родитель не накладывает ограничений (часто используется во вложенных прокручиваемых контейнерах для измерения контента).

### Реализация FlowLayout

Ниже пример упрощенной реализации `FlowLayout`, который уважает `MeasureSpec` и корректно раскладывает детей по строкам с переносом.

```kotlin
class FlowLayout(context: Context, attrs: AttributeSet? = null) : ViewGroup(context, attrs) {
    var horizontalSpacing = 0
    var verticalSpacing = 0

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)
        val heightMode = MeasureSpec.getMode(heightMeasureSpec)
        val heightSize = MeasureSpec.getSize(heightMeasureSpec)

        // При UNSPECIFIED ширина строки не ограничена родителем.
        val maxLineWidth = if (widthMode == MeasureSpec.UNSPECIFIED) Int.MAX_VALUE
                           else max(0, widthSize - paddingLeft - paddingRight)

        var rowWidth = 0
        var rowHeight = 0
        var maxWidth = 0
        var totalHeight = paddingTop + paddingBottom

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams

            // Учитываем маргины при измерении
            val childWidthMeasureSpec = getChildMeasureSpec(
                widthMeasureSpec,
                paddingLeft + paddingRight + lp.leftMargin + lp.rightMargin,
                lp.width
            )
            val childHeightMeasureSpec = getChildMeasureSpec(
                heightMeasureSpec,
                paddingTop + paddingBottom + lp.topMargin + lp.bottomMargin,
                lp.height
            )

            child.measure(childWidthMeasureSpec, childHeightMeasureSpec)

            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            // Если это не первый элемент в строке и он не помещается, переносим на следующую строку
            if (rowWidth > 0 && rowWidth + horizontalSpacing + childWidth > maxLineWidth && widthMode != MeasureSpec.UNSPECIFIED) {
                maxWidth = max(maxWidth, rowWidth)
                totalHeight += rowHeight + verticalSpacing
                rowWidth = childWidth
                rowHeight = childHeight
            } else {
                if (rowWidth > 0) {
                    rowWidth += horizontalSpacing
                }
                rowWidth += childWidth
                rowHeight = max(rowHeight, childHeight)
            }
        }

        if (rowWidth > 0) {
            maxWidth = max(maxWidth, rowWidth)
            totalHeight += rowHeight
        }

        // В случае UNSPECIFIED/AT_MOST ширина берётся по содержимому (с учётом padding)
        val measuredWidth = when (widthMode) {
            MeasureSpec.EXACTLY -> widthSize
            MeasureSpec.AT_MOST -> paddingLeft + paddingRight + min(maxWidth, maxLineWidth)
            MeasureSpec.UNSPECIFIED -> paddingLeft + paddingRight + maxWidth
            else -> paddingLeft + paddingRight + maxWidth
        }.coerceAtLeast(paddingLeft + paddingRight)

        val measuredHeight = when (heightMode) {
            MeasureSpec.EXACTLY -> heightSize
            MeasureSpec.AT_MOST -> min(totalHeight, heightSize)
            MeasureSpec.UNSPECIFIED -> totalHeight
            else -> totalHeight
        }.coerceAtLeast(paddingTop + paddingBottom)

        setMeasuredDimension(measuredWidth, measuredHeight)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        val width = r - l
        val maxLineWidth = max(0, width - paddingLeft - paddingRight)

        var x = paddingLeft
        var y = paddingTop
        var rowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams

            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            if (x > paddingLeft && x + childWidth > paddingLeft + maxLineWidth) {
                // перенос строки
                x = paddingLeft
                y += rowHeight + verticalSpacing
                rowHeight = 0
            }

            val left = x + lp.leftMargin
            val top = y + lp.topMargin
            val right = left + child.measuredWidth
            val bottom = top + child.measuredHeight

            child.layout(left, top, right, bottom)

            x += childWidth + horizontalSpacing
            rowHeight = max(rowHeight, childHeight)
        }
    }

    override fun generateLayoutParams(attrs: AttributeSet?): LayoutParams = MarginLayoutParams(context, attrs)

    override fun generateDefaultLayoutParams(): LayoutParams =
        MarginLayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)

    override fun generateLayoutParams(p: LayoutParams?): LayoutParams = when (p) {
        is MarginLayoutParams -> MarginLayoutParams(p)
        null -> MarginLayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)
        else -> MarginLayoutParams(p)
    }

    override fun checkLayoutParams(p: LayoutParams?): Boolean = p is MarginLayoutParams
}
```

Дополнительно (для полноты ответа на собеседовании): если отдельный ребёнок оказывается шире доступной строки (например, по `MeasureSpec`), его обычно размещают в отдельной строке и позволяют занять максимально возможную ширину в рамках переданного `MeasureSpec` (или обрезается/масштабируется самим дочерним `View` согласно его логике измерения).

### Критические Правила

**ОБЯЗАТЕЛЬНО:**
- Измерять всех детей через `measureChild()`, `measureChildWithMargins()` или `measure()` с корректными `getChildMeasureSpec()` до расчета собственного размера.
- Вызывать `setMeasuredDimension()` в конце `onMeasure()`.
- Пропускать `GONE` элементы (`child.visibility == View.GONE`) — они не занимают место.
- Учитывать `padding` родителя и `margins` детей при расчете размеров и позиций.
- Уважать `MeasureSpec` от родителя (можно использовать `resolveSize()` / `resolveSizeAndState()` как удобные хелперы).

**ЗАПРЕЩЕНО (в контексте обычного layout-контракта):**
- Вызывать `requestLayout()` внутри `onLayout()` → риск бесконечных перезапусков layout-процесса.
- Использовать `measuredWidth`/`measuredHeight` до вызова `measure()` на дочернем элементе.
- Игнорировать `MeasureSpec` от родителя — нарушение контракта измерения.
- Специально рассчитывать координаты так, чтобы дети выходили за границы родителя, если только это не контролируемый эффект с учётом возможного клиппинга/прокрутки.

### Оптимизации

**1. Кэширование позиций** между `onMeasure`/`onLayout` для избежания повторных вычислений (особенно при сложной геометрии). Важно: в `onMeasure()` можно вычислить предполагаемые `bounds`, но итоговая раскладка должна оставаться согласованной с измеренными размерами. В реальной реализации необходимо гарантировать совпадение количества записанных `bounds` с количеством видимых детей.

```kotlin
private val childBounds = mutableListOf<Rect>()

override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    childBounds.clear()
    // ... логика измерения, заполнение childBounds согласованными координатами ...
    setMeasuredDimension(calculatedWidth, calculatedHeight)
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    var index = 0
    for (i in 0 until childCount) {
        val child = getChildAt(i)
        if (child.visibility == GONE) continue
        val bounds = childBounds[index]
        child.layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
        index++
    }
}
```

**2. RTL Support** — учёт направления письма для арабского/иврита (при необходимости FlowLayout может зеркалировать расположение элементов):

```kotlin
val isRtl = ViewCompat.getLayoutDirection(this) == ViewCompat.LAYOUT_DIRECTION_RTL
val startX = if (isRtl) width - paddingRight else paddingLeft
```

## Answer (EN)

Creating a custom `ViewGroup` requires understanding the two-pass algorithm: **measure** (`onMeasure`) and **layout** (`onLayout`). These methods are called by the system to determine sizes and positions of all child views.

### Two-Pass Algorithm

**Pass 1: `onMeasure`** — size determination:
- Measure each child via `measureChild()`, `measureChildWithMargins()`, or `measure()` with appropriate `getChildMeasureSpec()` based on the parent's `MeasureSpec`.
- Compute the `ViewGroup`'s own size from children sizes, padding, and the constraints from the parent's `MeasureSpec`.
- **MUST** call `setMeasuredDimension(width, height)` — otherwise the view will not be properly measured/rendered.

**Pass 2: `onLayout`** — positioning:
- Position each child via `child.layout(left, top, right, bottom)`.
- Coordinates are relative to the parent; respect parent's `padding` and children's `margins`.

### MeasureSpec

`MeasureSpec` is a 32-bit value that combines mode (upper 2 bits) and size (lower 30 bits). The mode defines how to interpret the size:

- **`EXACTLY`** — parent specifies an exact size (`match_parent` or an explicit `dp` value).
- **`AT_MOST`** — maximum size available; the view should not exceed it (typical for `wrap_content`).
- **`UNSPECIFIED`** — no constraints from parent (often used inside scrollable containers to measure content).

### FlowLayout Implementation

Below is a simplified `FlowLayout` implementation that respects `MeasureSpec` and lays out children in rows with wrapping.

```kotlin
class FlowLayout(context: Context, attrs: AttributeSet? = null) : ViewGroup(context, attrs) {
    var horizontalSpacing = 0
    var verticalSpacing = 0

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)
        val heightMode = MeasureSpec.getMode(heightMeasureSpec)
        val heightSize = MeasureSpec.getSize(heightMeasureSpec)

        // When UNSPECIFIED, row width is not constrained by the parent.
        val maxLineWidth = if (widthMode == MeasureSpec.UNSPECIFIED) Int.MAX_VALUE
                           else max(0, widthSize - paddingLeft - paddingRight)

        var rowWidth = 0
        var rowHeight = 0
        var maxWidth = 0
        var totalHeight = paddingTop + paddingBottom

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams

            val childWidthMeasureSpec = getChildMeasureSpec(
                widthMeasureSpec,
                paddingLeft + paddingRight + lp.leftMargin + lp.rightMargin,
                lp.width
            )
            val childHeightMeasureSpec = getChildMeasureSpec(
                heightMeasureSpec,
                paddingTop + paddingBottom + lp.topMargin + lp.bottomMargin,
                lp.height
            )

            child.measure(childWidthMeasureSpec, childHeightMeasureSpec)

            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            // If not first in row and does not fit, wrap to next line (when width is constrained)
            if (rowWidth > 0 && rowWidth + horizontalSpacing + childWidth > maxLineWidth && widthMode != MeasureSpec.UNSPECIFIED) {
                maxWidth = max(maxWidth, rowWidth)
                totalHeight += rowHeight + verticalSpacing
                rowWidth = childWidth
                rowHeight = childHeight
            } else {
                if (rowWidth > 0) {
                    rowWidth += horizontalSpacing
                }
                rowWidth += childWidth
                rowHeight = max(rowHeight, childHeight)
            }
        }

        if (rowWidth > 0) {
            maxWidth = max(maxWidth, rowWidth)
            totalHeight += rowHeight
        }

        val measuredWidth = when (widthMode) {
            MeasureSpec.EXACTLY -> widthSize
            MeasureSpec.AT_MOST -> paddingLeft + paddingRight + min(maxWidth, maxLineWidth)
            MeasureSpec.UNSPECIFIED -> paddingLeft + paddingRight + maxWidth
            else -> paddingLeft + paddingRight + maxWidth
        }.coerceAtLeast(paddingLeft + paddingRight)

        val measuredHeight = when (heightMode) {
            MeasureSpec.EXACTLY -> heightSize
            MeasureSpec.AT_MOST -> min(totalHeight, heightSize)
            MeasureSpec.UNSPECIFIED -> totalHeight
            else -> totalHeight
        }.coerceAtLeast(paddingTop + paddingBottom)

        setMeasuredDimension(measuredWidth, measuredHeight)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        val width = r - l
        val maxLineWidth = max(0, width - paddingLeft - paddingRight)

        var x = paddingLeft
        var y = paddingTop
        var rowHeight = 0

        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue

            val lp = child.layoutParams as MarginLayoutParams

            val childWidth = child.measuredWidth + lp.leftMargin + lp.rightMargin
            val childHeight = child.measuredHeight + lp.topMargin + lp.bottomMargin

            if (x > paddingLeft && x + childWidth > paddingLeft + maxLineWidth) {
                // wrap to next line
                x = paddingLeft
                y += rowHeight + verticalSpacing
                rowHeight = 0
            }

            val left = x + lp.leftMargin
            val top = y + lp.topMargin
            val right = left + child.measuredWidth
            val bottom = top + child.measuredHeight

            child.layout(left, top, right, bottom)

            x += childWidth + horizontalSpacing
            rowHeight = max(rowHeight, childHeight)
        }
    }

    override fun generateLayoutParams(attrs: AttributeSet?): LayoutParams = MarginLayoutParams(context, attrs)

    override fun generateDefaultLayoutParams(): LayoutParams =
        MarginLayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)

    override fun generateLayoutParams(p: LayoutParams?): LayoutParams = when (p) {
        is MarginLayoutParams -> MarginLayoutParams(p)
        null -> MarginLayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)
        else -> MarginLayoutParams(p)
    }

    override fun checkLayoutParams(p: LayoutParams?): Boolean = p is MarginLayoutParams
}
```

Additionally (for interview completeness): if a single child becomes wider than the available line width according to its `MeasureSpec`, it is usually placed on its own line and allowed to take as much space as permitted by that `MeasureSpec` (or it may clip/scale itself based on its own measurement logic).

### Critical Rules

**MUST:**
- Measure all children via `measureChild()`, `measureChildWithMargins()`, or `measure()` with proper `getChildMeasureSpec()` before computing own size.
- `Call` `setMeasuredDimension()` at the end of `onMeasure()`.
- Skip `GONE` children (`child.visibility == View.GONE`) — they do not take space.
- Account for parent's `padding` and children's `margins` when calculating sizes and positions.
- Respect parent's `MeasureSpec`; `resolveSize()` / `resolveSizeAndState()` are recommended helpers.

**FORBIDDEN (within the normal layout contract context):**
- `Call` `requestLayout()` inside `onLayout()` → risk of repeated layout passes / infinite loops.
- Use `measuredWidth`/`measuredHeight` before calling `measure()` on the child.
- Ignore `MeasureSpec` from parent — violates the measurement contract.
- Intentionally compute child positions outside the parent's bounds unless you explicitly handle clipping/scrolling behavior.

### Optimizations

**1. Cache bounds** between `onMeasure` and `onLayout` to avoid recalculating complex geometry. Ensure cached bounds are consistent with measured sizes and are updated when children change. Also ensure the number of cached bounds matches the number of visible children.

```kotlin
private val childBounds = mutableListOf<Rect>()

override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    childBounds.clear()
    // ... measurement logic that fills childBounds ...
    setMeasuredDimension(calculatedWidth, calculatedHeight)
}

override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    var index = 0
    for (i in 0 until childCount) {
        val child = getChildAt(i)
        if (child.visibility == GONE) continue
        val bounds = childBounds[index]
        child.layout(bounds.left, bounds.top, bounds.right, bounds.bottom)
        index++
    }
}
```

**2. RTL Support** — account for right-to-left layout direction (FlowLayout may mirror item placement if desired):

```kotlin
val isRtl = ViewCompat.getLayoutDirection(this) == ViewCompat.LAYOUT_DIRECTION_RTL
val startX = if (isRtl) width - paddingRight else paddingLeft
```

## Дополнительные Вопросы (RU)

- Как обрабатывать динамическое добавление/удаление дочерних элементов без полного переизмерения?
- В чем разница между `measureChild()` и `measureChildWithMargins()` и когда использовать каждый?
- Как реализовать выравнивание по базовой линии между строками во `FlowLayout`?
- Как оптимизировать производительность для 100+ детей? Рассмотрите стратегии переиспользования представлений.
- Чем `requestLayout()` отличается от `invalidate()`? Когда каждый из них инициирует измерение vs. отрисовку?

## Follow-ups

- How would you handle dynamic child addition/removal without triggering full remeasurement?
- What's the difference between `measureChild()` and `measureChildWithMargins()`? When to use each?
- How would you implement baseline alignment across rows in FlowLayout?
- How would you optimize performance for 100+ children? Consider view recycling strategies.
- How does `requestLayout()` differ from `invalidate()`? When does each trigger measurement vs. drawing?

## Ссылки (RU)

- Документация `ViewGroup`: https://developer.android.com/reference/android/view/ViewGroup
- Руководство по кастомным `View`: https://developer.android.com/guide/topics/ui/custom-components
- Процесс измерения `View`: https://developer.android.com/guide/topics/ui/how-android-draws

## References

- `ViewGroup` Documentation: https://developer.android.com/reference/android/view/ViewGroup
- Custom Views Guide: https://developer.android.com/guide/topics/ui/custom-components
- `View` Measurement Process: https://developer.android.com/guide/topics/ui/how-android-draws

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-custom-views]]

### Предпосылки (Проще)

- [[q-custom-view-lifecycle--android--medium]] — Жизненный цикл и порядок отрисовки `View`
- [[q-custom-view-attributes--android--medium]] — Кастомные XML-атрибуты

### Связанные (Такой Же уровень)

- [[q-custom-drawable-implementation--android--medium]] — Кастомный рисунок во `View`
- Техники оптимизации layout-прохода

### Продвинутые (Сложнее)

- Более сложный `FlowLayout` с выравниванием по базовой линии
- Внутреннее устройство `AsyncLayoutInflater`
- Внутренняя работа `RecyclerView` `LayoutManager`

## Related Questions

### Prerequisites / Concepts

- [[c-custom-views]]

### Prerequisites (Easier)

- [[q-custom-view-lifecycle--android--medium]] — `View` lifecycle and drawing order
- [[q-custom-view-attributes--android--medium]] — Custom XML attributes

### Related (Same Level)

- [[q-custom-drawable-implementation--android--medium]] — Custom drawing in Views
- Layout pass optimization techniques

### Advanced (Harder)

- Complex `FlowLayout` with baseline alignment
- `AsyncLayoutInflater` implementation — background layout inflation
- `RecyclerView` layout manager internals

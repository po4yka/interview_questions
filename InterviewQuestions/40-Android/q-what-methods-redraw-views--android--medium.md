---
id: android-214
title: View Redraw Methods / Методы перерисовки View
aliases:
- View Redraw Methods
- Методы перерисовки View
topic: android
subtopics:
- lifecycle
- ui-views
question_kind: theory
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-view-system
- q-view-methods-and-their-purpose--android--medium
- q-what-is-a-view-and-what-is-responsible-for-its-visual-part--android--medium
- q-what-is-known-about-methods-that-redraw-view--android--medium
- q-what-layout-allows-overlapping-objects--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/lifecycle
- android/ui-views
- difficulty/medium
- drawing
- invalidate
- requestLayout
- view-rendering
anki_cards:
- slug: android-214-0-en
  language: en
  anki_id: 1768399145636
  synced_at: '2026-01-23T16:45:05.718197'
- slug: android-214-0-ru
  language: ru
  anki_id: 1768399145662
  synced_at: '2026-01-23T16:45:05.720128'
---
# Вопрос (RU)
> Методы перерисовки `View`

# Question (EN)
> `View` Redraw Methods

---

## Ответ (RU)

Android предоставляет несколько методов для запуска перерисовки `View` и пересчёта layout. Понимание того, когда и как использовать каждый метод, критично для эффективных обновлений UI. См. также [[c-android-view-system]].

### 1. invalidate()

Помечает `View` как требующую перерисовки. Фреймворк вызовет `onDraw()` (и `dispatchDraw()` для `ViewGroup`) при следующем проходе рисования. Используйте, когда меняется визуальное представление, но размер и позиционирование остаются теми же.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var color = Color.RED

    fun changeColor(newColor: Int) {
        color = newColor
        // Запланировать перерисовку в следующем кадре
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(color)
    }
}
```

#### Когда Использовать invalidate():
- Изменения цвета
- Обновления текста или содержимого `Drawable`
- Изменения состояния рисования
- Изменения видимости в рамках тех же границ
- Кадры анимации, не меняющие границы `View`

```kotlin
class AnimatedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0f
    private val rect = RectF(0f, 0f, 100f, 100f)
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    fun animateProgress(toProgress: Float) {
        val animator = ValueAnimator.ofFloat(progress, toProgress)
        animator.addUpdateListener { animation ->
            progress = animation.animatedValue as Float
            invalidate() // Перерисовать каждый кадр (по UI-потоку)
        }
        animator.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawArc(rect, 0f, 360f * progress, true, paint)
    }
}
```

### 2. requestLayout()

Запрашивает новый проход layout. Это приведёт к вызову `onMeasure()` и `onLayout()` (и у родителей по иерархии) при следующем layout-проходе. Используйте, когда размер или положение `View` могут измениться.

```kotlin
class ExpandableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    private var isExpanded = false

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()

    fun toggleExpansion() {
        isExpanded = !isExpanded
        // Запросить переизмерение и новый layout
        requestLayout()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val width = MeasureSpec.getSize(widthMeasureSpec)
        val height = if (isExpanded) 400.dp else 100.dp

        // При необходимости измерить детей
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            measureChild(child, widthMeasureSpec, MeasureSpec.makeMeasureSpec(height, MeasureSpec.AT_MOST))
        }

        setMeasuredDimension(width, height)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // Разместить детей в новых границах
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            child.layout(0, 0, width, height)
        }
    }
}
```

#### Когда Использовать requestLayout():
- Изменения размера
- Изменения margin/padding
- Изменения LayoutParams
- Добавление/удаление дочерних `View`
- Любые изменения, влияющие на измерение или позиционирование

```kotlin
class DynamicSizeView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    fun changeSize(newWidth: Int, newHeight: Int) {
        val params = layoutParams ?: return
        params.width = newWidth
        params.height = newHeight
        layoutParams = params
        // Явно запросить новый layout
        requestLayout()
    }

    fun changeSizeManually(newWidth: Int, newHeight: Int) {
        layoutParams = (layoutParams ?: return).apply {
            width = newWidth
            height = newHeight
        }
        requestLayout() // Пересчитать layout
        invalidate()    // Перерисовать
    }
}
```

### 3. postInvalidate()

Позволяет запланировать перерисовку из любого потока, публикуя запрос в UI-поток. Используйте, когда нужно обновить `View` из фонового потока.

```kotlin
class LoadingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var loadingProgress = 0
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    fun startLoading() {
        Thread {
            while (loadingProgress < 100) {
                Thread.sleep(100)
                loadingProgress += 10

                // invalidate() должен вызываться из UI-потока;
                // из фонового потока используем postInvalidate()
                postInvalidate()
            }
        }.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val widthProgress = width * loadingProgress / 100f
        canvas.drawRect(0f, 0f, widthProgress, height.toFloat(), paint)
    }
}
```

#### Сравнение: invalidate() Vs postInvalidate()

```kotlin
class ComparisonExample @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // Из UI-потока - используем invalidate()
    fun updateFromUIThread() {
        invalidate() // Безопасный прямой вызов
    }

    // Из фонового потока - используем postInvalidate()
    fun updateFromBackgroundThread() {
        Thread {
            // Фоновая работа
            processData()

            // Нельзя вызывать invalidate() напрямую из фонового потока
            postInvalidate() // Правильно - публикует в UI-поток

            // Альтернатива с post()
            post { invalidate() }
        }.start()
    }

    private fun processData() {
        // Фоновая обработка
    }
}
```

### 4. Дополнительные Методы, Связанные С Перерисовкой

#### forceLayout()
Помечает `View` как требующую layout на следующем проходе. Сам по себе не запускает немедленный layout; обычно используется вместе с `requestLayout()` или при родительском layout-проходе.

```kotlin
fun forceLayoutExample(view: View) {
    view.forceLayout()   // Пометить View для переразметки
    view.requestLayout() // Запросить у родителя запуск прохода layout
}
```

#### invalidateDrawable()
Вызывается, когда дочерний `Drawable` требует перерисовки; часто используется в кастомных `View`.

```kotlin
class DrawableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr), Drawable.Callback {

    private val drawable = ContextCompat.getDrawable(context, R.drawable.icon)

    init {
        drawable?.callback = this
    }

    override fun invalidateDrawable(who: Drawable) {
        // Перерисовать, когда Drawable изменился
        invalidate()
    }

    override fun scheduleDrawable(who: Drawable, what: Runnable, `when`: Long) {}

    override fun unscheduleDrawable(who: Drawable, what: Runnable) {}

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        drawable?.setBounds(0, 0, width, height)
        drawable?.draw(canvas)
    }
}
```

### 5. Практические Примеры

#### Сложное Обновление `View`

```kotlin
class ComplexView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var text = "Hello"
    private var textSizePx = 14f * resources.displayMetrics.scaledDensity

    fun updateText(newText: String) {
        text = newText
        invalidate() // Только визуальное изменение; предполагаем, что границы не меняются
    }

    fun updateTextSize(newSizeSp: Float) {
        textSizePx = newSizeSp * resources.displayMetrics.scaledDensity
        // Размер может измениться -> нужен layout + draw
        requestLayout()
        invalidate()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val paint = Paint().apply { textSize = textSizePx }
        val textWidth = paint.measureText(text)
        val textHeight = -paint.ascent() + paint.descent()
        setMeasuredDimension(textWidth.toInt(), textHeight.toInt())
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply {
            textSize = textSizePx
            color = Color.BLACK
        }
        val baseline = -paint.ascent()
        canvas.drawText(text, 0f, baseline, paint)
    }
}
```

#### Оптимизированные Обновления

```kotlin
class OptimizedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var needsLayout = false
    private var needsRedraw = false
    private var color: Int = Color.BLACK
    private var size: Int = 0

    fun batchUpdates(updates: () -> Unit) {
        // Собираем изменения
        updates()

        // Применяем один раз
        if (needsLayout) {
            requestLayout()
        }
        if (needsRedraw) {
            invalidate()
        }

        needsLayout = false
        needsRedraw = false
    }

    fun updateColor(newColor: Int) {
        // Только визуальное изменение
        if (color != newColor) {
            color = newColor
            needsRedraw = true
        }
    }

    fun updateSize(newSize: Int) {
        // Изменение, влияющее на layout
        if (size != newSize) {
            size = newSize
            needsLayout = true
            needsRedraw = true
        }
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desired = size
        val width = resolveSize(desired, widthMeasureSpec)
        val height = resolveSize(desired, heightMeasureSpec)
        setMeasuredDimension(width, height)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = this@OptimizedView.color }
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    }
}

// Использование
optimizedView.batchUpdates {
    updateColor(Color.RED)
    updateSize(100)
} // Один проход layout + invalidate
```

### Лучшие Практики

1. Используйте `invalidate()` для только визуальных изменений, не влияющих на layout.
2. Используйте `requestLayout()` при изменении размеров, положения или параметров, влияющих на измерение/размещение.
3. Используйте `postInvalidate()` (или `post { invalidate() }`) при обновлении из фоновых потоков.
4. Группируйте связанные обновления, чтобы избежать лишних проходов.
5. Избегайте частых вызовов в плотных циклах: `invalidate()` и `requestLayout()` могут быть дорогими операциями, особенно при большом дереве `View`.
6. По необходимости проверяйте `isAttachedToWindow` при асинхронных вызовах, чтобы избежать бесполезных обновлений.

```kotlin
fun View.safeInvalidate() {
    if (isAttachedToWindow) {
        invalidate()
    }
}
```

### Таблица Резюме

| Метод            | Поток        | Вызывает                         | Случай использования                          |
|------------------|-------------|----------------------------------|-----------------------------------------------|
| `invalidate()`    | UI-поток    | `onDraw()`                       | Только визуальные изменения                   |
| `requestLayout()` | UI-поток    | `onMeasure()`, `onLayout()`      | Изменения размера/позиции/layout              |
| `postInvalidate()`| Любой поток | `onDraw()` в UI-потоке           | Визуальные изменения из фонового потока       |
| `forceLayout()`   | UI-поток    | Помечает для layout (без немедл. прохода) | Принудительный пересчёт на следующем layout |

---

## Answer (EN)

Android provides several methods to trigger `View` redrawing and layout recalculation. Understanding when and how to use each method is crucial for efficient UI updates. See also [[c-android-view-system]].

### 1. invalidate()

Marks the `View` as needing to be redrawn. The framework will call `onDraw()` (and `dispatchDraw()` for `ViewGroup`s) during the next drawing pass. Use when the visual appearance changes but size and position remain the same.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var color = Color.RED

    fun changeColor(newColor: Int) {
        color = newColor
        // Trigger redraw on next frame
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(color)
    }
}
```

#### When to Use invalidate():
- Color changes
- Text or drawable content updates
- Drawing state changes
- Visibility changes in custom drawing (within the same bounds)
- Animation frames where bounds do not change

```kotlin
class AnimatedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0f
    private val rect = RectF(0f, 0f, 100f, 100f)
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    fun animateProgress(toProgress: Float) {
        val animator = ValueAnimator.ofFloat(progress, toProgress)
        animator.addUpdateListener { animation ->
            progress = animation.animatedValue as Float
            invalidate() // Schedule redraw for each frame on UI thread
        }
        animator.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawArc(rect, 0f, 360f * progress, true, paint)
    }
}
```

### 2. requestLayout()

Requests a new layout pass. This will cause `onMeasure()` and `onLayout()` (and for parents up the hierarchy) to be called on the next layout pass. Use when the `View`'s size or position might change.

```kotlin
class ExpandableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    private var isExpanded = false

    private val Int.dp: Int
        get() = (this * resources.displayMetrics.density).toInt()

    fun toggleExpansion() {
        isExpanded = !isExpanded
        // Trigger remeasure and relayout
        requestLayout()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val width = MeasureSpec.getSize(widthMeasureSpec)
        val height = if (isExpanded) 400.dp else 100.dp

        // Measure children if needed
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            measureChild(child, widthMeasureSpec, MeasureSpec.makeMeasureSpec(height, MeasureSpec.AT_MOST))
        }

        setMeasuredDimension(width, height)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // Position children within new bounds
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            child.layout(0, 0, width, height)
        }
    }
}
```

#### When to Use requestLayout():
- Size changes
- Margin/padding changes
- LayoutParams changes
- Adding/removing children
- Any changes that affect how parent or child views should be measured/positioned

```kotlin
class DynamicSizeView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    fun changeSize(newWidth: Int, newHeight: Int) {
        val params = layoutParams ?: return
        params.width = newWidth
        params.height = newHeight
        layoutParams = params
        // Explicitly ensure a layout pass
        requestLayout()
    }

    fun changeSizeManually(newWidth: Int, newHeight: Int) {
        layoutParams = (layoutParams ?: return).apply {
            width = newWidth
            height = newHeight
        }
        requestLayout() // Ensure layout is recalculated
        invalidate()    // Ensure it is redrawn
    }
}
```

### 3. postInvalidate()

Schedules a redraw from any thread by posting an invalidation request to the UI thread. Use this when you need to update the `View` from a background thread.

```kotlin
class LoadingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var loadingProgress = 0
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    fun startLoading() {
        Thread {
            while (loadingProgress < 100) {
                Thread.sleep(100)
                loadingProgress += 10

                // invalidate() must be called on UI thread;
                // from a background thread, use postInvalidate()
                postInvalidate()
            }
        }.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val widthProgress = width * loadingProgress / 100f
        canvas.drawRect(0f, 0f, widthProgress, height.toFloat(), paint)
    }
}
```

#### Comparison: invalidate() Vs postInvalidate()

```kotlin
class ComparisonExample @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // From UI thread - use invalidate()
    fun updateFromUIThread() {
        invalidate() // Safe, direct call on UI thread
    }

    // From background thread - use postInvalidate()
    fun updateFromBackgroundThread() {
        Thread {
            processData()

            // Do not call invalidate() directly from a background thread
            postInvalidate() // Correct - posts invalidation to UI thread

            // Alternative using post()
            post { invalidate() }
        }.start()
    }

    private fun processData() {
        // Background processing
    }
}
```

### 4. Additional Redraw-Related Methods

#### forceLayout()
Marks the `View` as needing layout during the next layout pass. It does not itself start a layout pass immediately; typically you combine it with `requestLayout()` (or rely on a parent-triggered layout pass).

```kotlin
fun forceLayoutExample(view: View) {
    view.forceLayout()   // Mark this view as needing layout
    view.requestLayout() // Ask the parent hierarchy to run a layout pass
}
```

#### invalidateDrawable()
Called when a child `Drawable` needs to be redrawn; often used in custom views.

```kotlin
class DrawableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr), Drawable.Callback {

    private val drawable = ContextCompat.getDrawable(context, R.drawable.icon)

    init {
        drawable?.callback = this
    }

    override fun invalidateDrawable(who: Drawable) {
        // Redraw when drawable changes
        invalidate()
    }

    override fun scheduleDrawable(who: Drawable, what: Runnable, `when`: Long) {}

    override fun unscheduleDrawable(who: Drawable, what: Runnable) {}

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        drawable?.setBounds(0, 0, width, height)
        drawable?.draw(canvas)
    }
}
```

### 5. Practical Examples

#### Complex `View` Update

```kotlin
class ComplexView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var text = "Hello"
    private var textSizePx = 14f * resources.displayMetrics.scaledDensity

    fun updateText(newText: String) {
        text = newText
        invalidate() // Only visual change; assumes bounds unchanged
    }

    fun updateTextSize(newSizeSp: Float) {
        textSizePx = newSizeSp * resources.displayMetrics.scaledDensity
        // Size might change, need measure + draw
        requestLayout()
        invalidate()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val paint = Paint().apply { textSize = textSizePx }
        val textWidth = paint.measureText(text)
        val textHeight = -paint.ascent() + paint.descent()
        setMeasuredDimension(textWidth.toInt(), textHeight.toInt())
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply {
            textSize = textSizePx
            color = Color.BLACK
        }
        val baseline = -paint.ascent()
        canvas.drawText(text, 0f, baseline, paint)
    }
}
```

#### Optimized Updates

```kotlin
class OptimizedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var needsLayout = false
    private var needsRedraw = false
    private var color: Int = Color.BLACK
    private var size: Int = 0

    fun batchUpdates(updates: () -> Unit) {
        // Collect changes
        updates()

        // Apply once
        if (needsLayout) {
            requestLayout()
        }
        if (needsRedraw) {
            invalidate()
        }

        needsLayout = false
        needsRedraw = false
    }

    fun updateColor(newColor: Int) {
        // Only visual change; mark for redraw
        if (color != newColor) {
            color = newColor
            needsRedraw = true
        }
    }

    fun updateSize(newSize: Int) {
        // Layout-related change
        if (size != newSize) {
            size = newSize
            needsLayout = true
            needsRedraw = true
        }
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desired = size
        val width = resolveSize(desired, widthMeasureSpec)
        val height = resolveSize(desired, heightMeasureSpec)
        setMeasuredDimension(width, height)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = this@OptimizedView.color }
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    }
}

// Usage
optimizedView.batchUpdates {
    updateColor(Color.RED)
    updateSize(100)
} // Single layout + invalidate call
```

### Best Practices

1. Use `invalidate()` for visual-only changes that don't affect layout.
2. Use `requestLayout()` when size, position, or LayoutParams-based properties may change.
3. Use `postInvalidate()` (or `post { invalidate() }`) when updating from a background thread.
4. Batch related updates where possible to avoid redundant passes.
5. Avoid unnecessary calls in tight loops: `invalidate()`/`requestLayout()` can be expensive, especially for large view hierarchies.
6. Optionally check attachment state (e.g., `isAttachedToWindow`) when invalidating from async callbacks to avoid unnecessary work.

```kotlin
fun View.safeInvalidate() {
    if (isAttachedToWindow) {
        invalidate()
    }
}
```

### Summary Table

| Method            | `Thread`        | Calls                            | Use Case                               |
|------------------|--------------|----------------------------------|----------------------------------------|
| `invalidate()`    | UI thread    | `onDraw()`                       | Visual changes only                    |
| `requestLayout()` | UI thread    | `onMeasure()`, `onLayout()`      | Size/position/layout changes           |
| `postInvalidate()`| Any thread   | `onDraw()` on UI thread          | Visual changes from background thread  |
| `forceLayout()`   | UI thread    | Marks for layout (no pass by itself) | Force remeasure on next layout pass |

---

## Follow-ups

- [[q-view-methods-and-their-purpose--android--medium]]
- How does excessive use of `requestLayout()` affect performance in complex view hierarchies?
- When would you combine `requestLayout()` and `invalidate()` in a single update, and why?
- How would you safely update a `View` from a coroutine running on a background dispatcher?
- What are potential pitfalls of calling `invalidate()`/`postInvalidate()` on a `View` that is not attached to window?

## References

- [`Views`](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`
- [[q-viewmodel-pattern--android--easy]] - `View`

### Related (Medium)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View`
- [[q-testing-viewmodels-turbine--android--medium]] - `View`
- [[q-what-is-viewmodel--android--medium]] - `View`
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - `View`

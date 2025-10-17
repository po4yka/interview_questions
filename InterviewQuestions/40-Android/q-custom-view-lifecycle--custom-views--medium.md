---
id: "20251015082237451"
title: "Custom View Lifecycle / Жизненный цикл кастомных View"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - custom-views
  - android-framework
  - lifecycle
  - performance
---
# Custom View Lifecycle

# Question (EN)
> Explain the lifecycle of a custom Android View. What methods are called and in what order? When should you perform initialization, measurement, layout, and drawing operations?

# Вопрос (RU)
> Объясните жизненный цикл пользовательского Android View. Какие методы вызываются и в каком порядке? Когда следует выполнять инициализацию, измерение, компоновку и отрисовку?

---

## Answer (EN)

Understanding the **Custom View lifecycle** is crucial for building efficient, performant custom UI components. The lifecycle consists of several key phases: construction, attachment, measurement, layout, drawing, and detachment.

### View Lifecycle Overview

```
Constructor → onAttachedToWindow → onMeasure → onLayout → onDraw → onDetachedFromWindow
     ↑              ↓                   ↑           ↑         ↑              ↓
     
                         (Can repeat multiple times)
```

---

### 1. Construction Phase

**Methods called:**
- Constructor(Context)
- Constructor(Context, AttributeSet)
- Constructor(Context, AttributeSet, int defStyleAttr)
- Constructor(Context, AttributeSet, int defStyleAttr, int defStyleRes)

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    //  DO: Read XML attributes here
    //  DO: Initialize Paint objects
    //  DO: Set up default values
    //  DON'T: Access view dimensions (they're 0)
    //  DON'T: Start animations or background work

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private val backgroundPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.LIGHT_GRAY
    }

    private var progress: Float = 0f

    init {
        // Read custom XML attributes
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.CustomProgressBar,
            defStyleAttr,
            0
        ).apply {
            try {
                progress = getFloat(R.styleable.CustomProgressBar_progress, 0f)
                progressPaint.color = getColor(
                    R.styleable.CustomProgressBar_progressColor,
                    Color.BLUE
                )
            } finally {
                recycle()
            }
        }

        // Enable drawing optimizations
        setWillNotDraw(false) // Important for views that draw
    }
}
```

**When to use:**
- Initialize Paint objects
- Read XML attributes
- Set default values
- Configure basic properties

**What NOT to do:**
- Don't access `width` or `height` (they're 0)
- Don't start animations
- Don't perform expensive operations

---

### 2. onAttachedToWindow()

Called when the view is attached to a window and becomes part of the view hierarchy.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    //  DO: Start animations
    //  DO: Register listeners
    //  DO: Start background tasks
    //  DO: Access ViewTreeObserver

    // Start animation when view is attached
    valueAnimator = ValueAnimator.ofFloat(0f, progress).apply {
        duration = 300
        addUpdateListener { animator ->
            animatedProgress = animator.animatedValue as Float
            invalidate() // Request redraw
        }
        start()
    }

    // Register global layout listener
    viewTreeObserver.addOnGlobalLayoutListener(layoutListener)

    Log.d("CustomView", "View attached to window")
}
```

**When to use:**
- Start animations
- Register broadcast receivers, listeners
- Subscribe to observables (Flow, LiveData)
- Access parent views
- Set up ViewTreeObserver callbacks

---

### 3. onMeasure()

Called to determine the size requirements of the view. Can be called multiple times.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    //  DO: Calculate desired dimensions
    //  DO: Consider padding
    //  DO: Respect measure spec modes
    //  DO: Call setMeasuredDimension()
    //  DON'T: Draw anything
    //  DON'T: Access child positions

    val desiredWidth = 200.dpToPx()
    val desiredHeight = 50.dpToPx()

    // Calculate width based on measure spec
    val width = when (MeasureSpec.getMode(widthMeasureSpec)) {
        MeasureSpec.EXACTLY -> {
            // Must be this size (match_parent or specific dp)
            MeasureSpec.getSize(widthMeasureSpec)
        }
        MeasureSpec.AT_MOST -> {
            // Can be up to this size (wrap_content with max)
            min(desiredWidth, MeasureSpec.getSize(widthMeasureSpec))
        }
        MeasureSpec.UNSPECIFIED -> {
            // Can be any size
            desiredWidth
        }
        else -> desiredWidth
    }

    // Calculate height similarly
    val height = when (MeasureSpec.getMode(heightMeasureSpec)) {
        MeasureSpec.EXACTLY -> MeasureSpec.getSize(heightMeasureSpec)
        MeasureSpec.AT_MOST -> min(desiredHeight, MeasureSpec.getSize(heightMeasureSpec))
        MeasureSpec.UNSPECIFIED -> desiredHeight
        else -> desiredHeight
    }

    // MUST call setMeasuredDimension()
    setMeasuredDimension(width, height)
}

private fun Int.dpToPx(): Int {
    return (this * resources.displayMetrics.density).toInt()
}
```

**MeasureSpec modes:**

| Mode | Description | XML Example |
|------|-------------|-------------|
| **EXACTLY** | View must be exact size | `android:layout_width="100dp"` |
| **AT_MOST** | View can be up to size | `android:layout_width="wrap_content"` |
| **UNSPECIFIED** | No constraints | Rare, used in ScrollView |

**When to use:**
- Calculate view dimensions
- Consider padding and margins
- Handle wrap_content properly
- Optimize for performance (cache calculations)

---

### 4. onSizeChanged()

Called when the view size changes (after onMeasure, before onLayout).

```kotlin
override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
    super.onSizeChanged(w, h, oldw, oldh)

    //  DO: Recalculate positions based on new size
    //  DO: Recreate bitmaps/shaders
    //  DO: Update Path objects
    //  DON'T: Call requestLayout() (infinite loop!)

    // Recreate gradient shader with new dimensions
    gradientShader = LinearGradient(
        0f, 0f, w.toFloat(), 0f,
        Color.BLUE, Color.GREEN,
        Shader.TileMode.CLAMP
    )
    progressPaint.shader = gradientShader

    // Recalculate bounds
    progressBounds.set(
        paddingLeft.toFloat(),
        paddingTop.toFloat(),
        (w - paddingRight).toFloat(),
        (h - paddingBottom).toFloat()
    )

    Log.d("CustomView", "Size changed: $w x $h (was $oldw x $oldh)")
}
```

**When to use:**
- Create size-dependent objects (Bitmap, Shader, Path)
- Recalculate layout bounds
- Update drawing regions
- Handle orientation changes

---

### 5. onLayout()

Called to assign positions to child views (for ViewGroups). Simple Views don't need to override this.

```kotlin
// For ViewGroup subclasses only
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    //  DO: Position child views
    //  DO: Call child.layout() for each child
    //  DON'T: Measure children (do in onMeasure)
    //  DON'T: Draw anything

    var currentX = paddingLeft
    val currentY = paddingTop

    for (i in 0 until childCount) {
        val child = getChildAt(i)
        if (child.visibility != GONE) {
            val childWidth = child.measuredWidth
            val childHeight = child.measuredHeight

            // Position child
            child.layout(
                currentX,
                currentY,
                currentX + childWidth,
                currentY + childHeight
            )

            currentX += childWidth + spacing
        }
    }
}
```

**When to use (ViewGroups only):**
- Position child views
- Implement custom layout logic
- Handle RTL (right-to-left) layouts

---

### 6. onDraw()

Called to render the view's content. This is where the magic happens!

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    //  DO: Draw view content
    //  DO: Use pre-allocated objects (Paint, Path, Rect)
    //  DON'T: Allocate objects (causes GC pressure)
    //  DON'T: Call requestLayout() or invalidate() directly
    //  DON'T: Perform heavy calculations

    val width = width.toFloat()
    val height = height.toFloat()

    // Draw background
    canvas.drawRect(0f, 0f, width, height, backgroundPaint)

    // Draw progress
    val progressWidth = width * (animatedProgress / 100f)
    canvas.drawRect(0f, 0f, progressWidth, height, progressPaint)

    // Draw text (optional)
    if (showText) {
        val text = "${animatedProgress.toInt()}%"
        val textX = width / 2f
        val textY = height / 2f - (textPaint.descent() + textPaint.ascent()) / 2f
        canvas.drawText(text, textX, textY, textPaint)
    }
}
```

**Performance tips:**
```kotlin
class OptimizedCustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    //  Pre-allocate objects
    private val paint = Paint()
    private val bounds = RectF()
    private val path = Path()

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        //  DON'T allocate in onDraw!
        // val paint = Paint() // BAD!
        // val bounds = RectF() // BAD!

        //  Reuse pre-allocated objects
        bounds.set(0f, 0f, width.toFloat(), height.toFloat())
        canvas.drawRect(bounds, paint)
    }
}
```

---

### 7. invalidate() vs requestLayout()

**invalidate()** - Request redraw (calls onDraw)
```kotlin
fun setProgress(progress: Float) {
    this.progress = progress
    invalidate() // Only redraw, no remeasure
}
```

**requestLayout()** - Request remeasure and redraw
```kotlin
fun setThickness(thickness: Int) {
    this.thickness = thickness
    requestLayout() // Remeasure, then redraw
}
```

**When to use:**
| Method | Use When | Performance | Triggers |
|--------|----------|-------------|----------|
| `invalidate()` | Visual change only | Fast | onDraw |
| `requestLayout()` | Size/position change | Slower | onMeasure → onLayout → onDraw |

---

### 8. onDetachedFromWindow()

Called when view is removed from window.

```kotlin
override fun onDetachedFromWindow() {
    //  DO: Cancel animations
    //  DO: Unregister listeners
    //  DO: Stop background work
    //  DO: Release resources

    valueAnimator?.cancel()
    viewTreeObserver.removeOnGlobalLayoutListener(layoutListener)

    // Cancel coroutines
    coroutineScope.cancel()

    Log.d("CustomView", "View detached from window")

    super.onDetachedFromWindow()
}
```

**When to use:**
- Clean up animations
- Unregister listeners/receivers
- Cancel background tasks
- Prevent memory leaks

---

### Complete Lifecycle Example

```kotlin
class CompleteCustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animator: ValueAnimator? = null

    init {
        Log.d("Lifecycle", "1. Constructor")
        paint.color = Color.BLUE
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        Log.d("Lifecycle", "2. onAttachedToWindow")

        animator = ValueAnimator.ofFloat(0f, 360f).apply {
            duration = 2000
            repeatCount = ValueAnimator.INFINITE
            addUpdateListener { invalidate() }
            start()
        }
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        Log.d("Lifecycle", "3. onMeasure")

        val size = 200.dpToPx()
        val width = resolveSize(size, widthMeasureSpec)
        val height = resolveSize(size, heightMeasureSpec)

        setMeasuredDimension(width, height)
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        Log.d("Lifecycle", "4. onSizeChanged: $w x $h")
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        super.onLayout(changed, left, top, right, bottom)
        Log.d("Lifecycle", "5. onLayout")
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        Log.d("Lifecycle", "6. onDraw")

        val cx = width / 2f
        val cy = height / 2f
        val radius = min(width, height) / 4f

        canvas.drawCircle(cx, cy, radius, paint)
    }

    override fun onDetachedFromWindow() {
        Log.d("Lifecycle", "7. onDetachedFromWindow")
        animator?.cancel()
        super.onDetachedFromWindow()
    }

    private fun Int.dpToPx(): Int =
        (this * resources.displayMetrics.density).toInt()
}
```

**Log output:**
```
1. Constructor
2. onAttachedToWindow
3. onMeasure
4. onSizeChanged: 200 x 200
5. onLayout
6. onDraw
6. onDraw (repeated with animation)
6. onDraw
...
7. onDetachedFromWindow
```

---

### Real-World Example: Custom Gauge View

```kotlin
class GaugeView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val arcPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 20f
        strokeCap = Paint.Cap.ROUND
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textAlign = Paint.Align.CENTER
        textSize = 48f
        color = Color.BLACK
    }

    private val arcBounds = RectF()
    private var value: Float = 0f
        set(newValue) {
            field = newValue.coerceIn(0f, 100f)
            invalidate() // Redraw with new value
        }

    private var sweepAngle: Float = 0f

    // 1. Constructor - Initialize paints and default values
    init {
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.GaugeView,
            defStyleAttr,
            0
        ).apply {
            try {
                value = getFloat(R.styleable.GaugeView_value, 0f)
                arcPaint.color = getColor(R.styleable.GaugeView_arcColor, Color.BLUE)
            } finally {
                recycle()
            }
        }
    }

    // 2. onAttachedToWindow - Start animation
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        animateToValue(value)
    }

    // 3. onMeasure - Calculate size
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desiredSize = 300.dpToPx()
        val width = resolveSize(desiredSize, widthMeasureSpec)
        val height = resolveSize(desiredSize, heightMeasureSpec)
        val size = min(width, height)
        setMeasuredDimension(size, size)
    }

    // 4. onSizeChanged - Update arc bounds
    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)

        val padding = 40f
        arcBounds.set(
            padding,
            padding,
            w - padding,
            h - padding
        )
    }

    // 5. onDraw - Render the gauge
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Draw background arc (gray)
        arcPaint.color = Color.LIGHT_GRAY
        canvas.drawArc(arcBounds, 135f, 270f, false, arcPaint)

        // Draw value arc (colored)
        arcPaint.color = Color.BLUE
        sweepAngle = (value / 100f) * 270f
        canvas.drawArc(arcBounds, 135f, sweepAngle, false, arcPaint)

        // Draw value text
        val text = "${value.toInt()}%"
        val textY = height / 2f - (textPaint.descent() + textPaint.ascent()) / 2f
        canvas.drawText(text, width / 2f, textY, textPaint)
    }

    // 6. onDetachedFromWindow - Clean up
    override fun onDetachedFromWindow() {
        animator?.cancel()
        super.onDetachedFromWindow()
    }

    // Public API
    fun setValue(newValue: Float, animate: Boolean = true) {
        if (animate) {
            animateToValue(newValue)
        } else {
            value = newValue
        }
    }

    private var animator: ValueAnimator? = null

    private fun animateToValue(target: Float) {
        animator?.cancel()
        animator = ValueAnimator.ofFloat(value, target).apply {
            duration = 500
            addUpdateListener { animation ->
                value = animation.animatedValue as Float
            }
            start()
        }
    }

    private fun Int.dpToPx(): Int =
        (this * resources.displayMetrics.density).toInt()
}
```

---

### Best Practices

**1. Constructor**
```kotlin
//  DO
init {
    paint.color = Color.BLUE
    paint.strokeWidth = 10f
}

//  DON'T
init {
    val w = width // 0!
    val h = height // 0!
}
```

**2. onMeasure**
```kotlin
//  DO
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val size = calculateDesiredSize()
    setMeasuredDimension(
        resolveSize(size, widthMeasureSpec),
        resolveSize(size, heightMeasureSpec)
    )
}

//  DON'T forget to call setMeasuredDimension
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Missing setMeasuredDimension() - CRASH!
}
```

**3. onDraw**
```kotlin
//  DO - Pre-allocate
private val paint = Paint()
override fun onDraw(canvas: Canvas) {
    canvas.drawCircle(x, y, radius, paint)
}

//  DON'T - Allocate in onDraw
override fun onDraw(canvas: Canvas) {
    val paint = Paint() // GC pressure!
    canvas.drawCircle(x, y, radius, paint)
}
```

**4. Cleanup**
```kotlin
//  DO
override fun onDetachedFromWindow() {
    animator?.cancel()
    listener?.unregister()
    super.onDetachedFromWindow()
}

//  DON'T forget cleanup
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    // Animator still running - leak!
}
```

---

### Summary

**View Lifecycle Order:**
1. **Constructor** - Initialize objects, read attributes
2. **onAttachedToWindow** - Start animations, register listeners
3. **onMeasure** - Calculate size requirements
4. **onSizeChanged** - Handle size changes, create size-dependent objects
5. **onLayout** - Position children (ViewGroups only)
6. **onDraw** - Render content
7. **onDetachedFromWindow** - Clean up resources

**Key Rules:**
- **Never allocate objects in onDraw()** - causes GC pressure
- **Always call setMeasuredDimension() in onMeasure()** - or crash
- **Use invalidate() for visual changes** - faster than requestLayout()
- **Clean up in onDetachedFromWindow()** - prevent memory leaks
- **Cache calculations** - don't recalculate in every onDraw()

---

## Ответ (RU)

Понимание **жизненного цикла пользовательского View** критически важно для создания эффективных, производительных пользовательских UI компонентов. Жизненный цикл состоит из нескольких ключевых фаз: конструирование, присоединение, измерение, компоновка, отрисовка и отсоединение.

### Обзор жизненного цикла View

```
Constructor → onAttachedToWindow → onMeasure → onLayout → onDraw → onDetachedFromWindow
     ↑              ↓                   ↑           ↑         ↑              ↓
     
                         (Может повторяться много раз)
```

### Основные методы жизненного цикла

**1. Constructor (Конструктор)**
- Инициализация Paint объектов
- Чтение XML атрибутов
- Установка значений по умолчанию
-  НЕ обращайтесь к width/height (они равны 0)

**2. onAttachedToWindow()**
- Запуск анимаций
- Регистрация слушателей
- Подписка на observable
- Доступ к родительским view

**3. onMeasure()**
- Расчет требований к размеру
- Учет padding и constraints
- Обязательно вызвать `setMeasuredDimension()`
- Может вызываться многократно

**4. onSizeChanged()**
- Пересоздание Bitmap/Shader
- Обновление Path объектов
- Пересчет границ рисования
-  НЕ вызывайте requestLayout() (бесконечный цикл!)

**5. onLayout()** (только для ViewGroup)
- Позиционирование дочерних view
- Вызов child.layout() для каждого ребенка

**6. onDraw()**
- Отрисовка содержимого view
-  НЕ выделяйте объекты (GC давление!)
-  Используйте предварительно выделенные объекты

**7. onDetachedFromWindow()**
- Отмена анимаций
- Отмена регистрации слушателей
- Остановка фоновой работы
- Освобождение ресурсов

### Пример полного жизненного цикла

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animator: ValueAnimator? = null

    // 1. Конструктор
    init {
        paint.color = Color.BLUE
    }

    // 2. Присоединение к окну
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        animator = ValueAnimator.ofFloat(0f, 100f).apply {
            duration = 1000
            addUpdateListener { invalidate() }
            start()
        }
    }

    // 3. Измерение
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val size = 200
        setMeasuredDimension(
            resolveSize(size, widthMeasureSpec),
            resolveSize(size, heightMeasureSpec)
        )
    }

    // 4. Изменение размера
    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        // Пересоздать shader с новыми размерами
    }

    // 5. Отрисовка
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    }

    // 6. Отсоединение
    override fun onDetachedFromWindow() {
        animator?.cancel()
        super.onDetachedFromWindow()
    }
}
```

### Ключевые правила

- **Никогда не выделяйте объекты в onDraw()** - вызывает GC pressure
- **Всегда вызывайте setMeasuredDimension() в onMeasure()** - иначе краш
- **Используйте invalidate() для визуальных изменений** - быстрее requestLayout()
- **Очищайте ресурсы в onDetachedFromWindow()** - предотвращение утечек памяти
- **Кэшируйте вычисления** - не пересчитывайте в каждом onDraw()

### invalidate() vs requestLayout()

| Метод | Когда использовать | Производительность | Триггерит |
|-------|-------------------|-------------------|-----------|
| `invalidate()` | Только визуальное изменение | Быстро | onDraw |
| `requestLayout()` | Изменение размера/позиции | Медленнее | onMeasure → onLayout → onDraw |

---

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Lifecycle, View

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - Lifecycle, View
- [[q-what-is-viewmodel--android--medium]] - Lifecycle, View
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - Lifecycle, View
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - Lifecycle, View
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - Lifecycle, View

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View

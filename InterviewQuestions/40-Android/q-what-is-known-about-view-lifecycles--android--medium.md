---
id: "20251015082237397"
title: "What Is Known About View Lifecycles / Что известно о жизненных циклах View"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - view
  - lifecycle
  - ui
---
# What is known about View lifecycles?

**Russian**: Что известно о жизненном цикле View?

## Answer (EN)
The View lifecycle in Android describes the sequence of method calls from view creation to destruction. Understanding this lifecycle is crucial for managing resources, handling configuration changes, and optimizing performance.

### View Lifecycle Stages

The view lifecycle consists of several key stages:

1. **Constructor** - View instance is created
2. **onAttachedToWindow()** - View is attached to a window
3. **onMeasure()** - View measures its size
4. **onLayout()** - View positions its children
5. **onDraw()** - View draws itself
6. **onDetachedFromWindow()** - View is detached from window

### 1. Constructor

The first step is creating a View instance through one of its constructors:

```kotlin
class CustomView : View {
    // Constructor called from code
    constructor(context: Context) : super(context) {
        init()
    }

    // Constructor called from XML with attributes
    constructor(context: Context, attrs: AttributeSet?) : super(context, attrs) {
        init(attrs)
    }

    // Constructor called from XML with attributes and style
    constructor(context: Context, attrs: AttributeSet?, defStyleAttr: Int)
        : super(context, attrs, defStyleAttr) {
        init(attrs, defStyleAttr)
    }

    private fun init(attrs: AttributeSet? = null, defStyleAttr: Int = 0) {
        // Initialize view properties
        // Parse custom attributes
        attrs?.let {
            val typedArray = context.obtainStyledAttributes(
                it, R.styleable.CustomView, defStyleAttr, 0
            )
            // Read attributes
            typedArray.recycle()
        }
    }
}
```

### 2. onAttachedToWindow()

Called when the view is attached to a window. This is where you should start animations, register listeners, or acquire resources.

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    // Start animations
    startAnimation()

    // Register listeners
    sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)

    // Start periodic updates
    handler.post(updateRunnable)

    Log.d("View", "View attached to window")
}
```

### 3. onMeasure()

Called to determine the size requirements for this view and all of its children. You should call `setMeasuredDimension()` to store the measured width and height.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    // Extract mode and size from MeasureSpec
    val widthMode = MeasureSpec.getMode(widthMeasureSpec)
    val widthSize = MeasureSpec.getSize(widthMeasureSpec)
    val heightMode = MeasureSpec.getMode(heightMeasureSpec)
    val heightSize = MeasureSpec.getSize(heightMeasureSpec)

    // Calculate desired dimensions
    val desiredWidth = 200.dpToPx()
    val desiredHeight = 200.dpToPx()

    // Determine final dimensions based on mode
    val width = when (widthMode) {
        MeasureSpec.EXACTLY -> widthSize  // Match parent or specific size
        MeasureSpec.AT_MOST -> min(desiredWidth, widthSize)  // Wrap content
        else -> desiredWidth  // Unspecified
    }

    val height = when (heightMode) {
        MeasureSpec.EXACTLY -> heightSize
        MeasureSpec.AT_MOST -> min(desiredHeight, heightSize)
        else -> desiredHeight
    }

    // MUST call this
    setMeasuredDimension(width, height)
}

private fun Int.dpToPx(): Int {
    return (this * resources.displayMetrics.density).toInt()
}
```

**MeasureSpec modes:**
- `EXACTLY` - Parent has determined exact size (match_parent or specific dp)
- `AT_MOST` - View can be as large as it wants up to specified size (wrap_content)
- `UNSPECIFIED` - View can be any size it wants

### 4. onLayout()

Called when the view should assign sizes and positions to its children. Custom ViewGroups override this to position children.

```kotlin
// For custom ViewGroup
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    var currentTop = paddingTop

    for (i in 0 until childCount) {
        val child = getChildAt(i)
        if (child.visibility != View.GONE) {
            val childWidth = child.measuredWidth
            val childHeight = child.measuredHeight

            // Position child
            child.layout(
                paddingLeft,
                currentTop,
                paddingLeft + childWidth,
                currentTop + childHeight
            )

            currentTop += childHeight
        }
    }
}
```

**For simple View (not ViewGroup):**

```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    super.onLayout(changed, left, top, right, bottom)

    // 'changed' indicates if view bounds have changed
    if (changed) {
        // Recalculate positions for internal drawing
        calculateDrawingBounds()
    }
}
```

### 5. onSizeChanged()

Called when the size of the view has changed. This is a good place to calculate coordinates for drawing.

```kotlin
override fun onSizeChanged(width: Int, height: Int, oldWidth: Int, oldHeight: Int) {
    super.onSizeChanged(width, height, oldWidth, oldHeight)

    // Recalculate drawing coordinates
    centerX = width / 2f
    centerY = height / 2f
    radius = min(width, height) / 2f * 0.8f

    Log.d("View", "Size changed: ${width}x${height}")
}
```

### 6. onDraw()

Called when the view should render its content. This is where all drawing happens.

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Draw background
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), backgroundPaint)

    // Draw circle
    canvas.drawCircle(centerX, centerY, radius, circlePaint)

    // Draw text
    canvas.drawText("Custom View", centerX, centerY, textPaint)
}
```

**Important:** `onDraw()` is called frequently. Avoid:
- Creating objects (causes GC)
- Complex calculations
- Allocating memory

### 7. onDetachedFromWindow()

Called when the view is detached from a window. This is where you should stop animations, unregister listeners, and release resources.

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()

    // Stop animations
    stopAnimation()

    // Unregister listeners
    sensorManager.unregisterListener(this)

    // Stop periodic updates
    handler.removeCallbacks(updateRunnable)

    // Release resources
    releaseResources()

    Log.d("View", "View detached from window")
}
```

### Complete Lifecycle Example

```kotlin
class LifecycleAwareView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    private var centerX = 0f
    private var centerY = 0f
    private var radius = 0f

    // 1. Constructor
    init {
        Log.d("Lifecycle", "Constructor called")
    }

    // 2. Attached to window
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        Log.d("Lifecycle", "onAttachedToWindow()")

        // Start resources
    }

    // 3. Measure
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        Log.d("Lifecycle", "onMeasure()")

        val size = 200.dpToPx()
        setMeasuredDimension(
            resolveSize(size, widthMeasureSpec),
            resolveSize(size, heightMeasureSpec)
        )
    }

    // 4. Size changed
    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        Log.d("Lifecycle", "onSizeChanged($w, $h)")

        centerX = w / 2f
        centerY = h / 2f
        radius = min(w, h) / 2f * 0.8f
    }

    // 5. Layout
    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        super.onLayout(changed, left, top, right, bottom)
        Log.d("Lifecycle", "onLayout($changed)")
    }

    // 6. Draw
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        Log.d("Lifecycle", "onDraw()")

        canvas.drawCircle(centerX, centerY, radius, paint)
    }

    // 7. Detached from window
    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        Log.d("Lifecycle", "onDetachedFromWindow()")

        // Clean up resources
    }

    private fun Int.dpToPx(): Int {
        return (this * resources.displayMetrics.density).toInt()
    }
}
```

### Invalidation and Layout Requests

#### requestLayout()

Triggers measure and layout passes. Call when view's size or position needs to change.

```kotlin
fun updateSize() {
    // Properties changed that affect size
    textSize = 24f

    // Request new measure and layout
    requestLayout()
}
```

#### invalidate()

Triggers only the draw pass. Call when view's appearance needs to update.

```kotlin
fun updateColor() {
    // Properties changed that affect appearance only
    paint.color = Color.RED

    // Request redraw
    invalidate()
}
```

**Difference:**
- `requestLayout()` → onMeasure() → onLayout() → onDraw()
- `invalidate()` → onDraw() only (faster)

### View State Restoration

Views can save and restore their state across configuration changes:

```kotlin
override fun onSaveInstanceState(): Parcelable {
    val superState = super.onSaveInstanceState()

    return Bundle().apply {
        putParcelable("super_state", superState)
        putInt("custom_value", customValue)
        putString("custom_text", customText)
    }
}

override fun onRestoreInstanceState(state: Parcelable?) {
    if (state is Bundle) {
        customValue = state.getInt("custom_value")
        customText = state.getString("custom_text")

        super.onRestoreInstanceState(state.getParcelable("super_state"))
    } else {
        super.onRestoreInstanceState(state)
    }
}
```

### Window Focus Changes

```kotlin
override fun onWindowFocusChanged(hasWindowFocus: Boolean) {
    super.onWindowFocusChanged(hasWindowFocus)

    if (hasWindowFocus) {
        // Window gained focus - resume animations
        resumeAnimations()
    } else {
        // Window lost focus - pause animations
        pauseAnimations()
    }
}
```

### Visibility Changes

```kotlin
override fun onVisibilityChanged(changedView: View, visibility: Int) {
    super.onVisibilityChanged(changedView, visibility)

    when (visibility) {
        View.VISIBLE -> {
            // View became visible
            startUpdates()
        }
        View.INVISIBLE, View.GONE -> {
            // View became invisible
            stopUpdates()
        }
    }
}
```

### Lifecycle Flow Diagram

```
Constructor
    ↓
onAttachedToWindow()
    ↓
onMeasure() ←
    ↓             
onLayout() ←   
    ↓            
onDraw() ←   
                 
requestLayout()   
invalidate()

Configuration Change
    ↓
onSaveInstanceState()
    ↓
onDetachedFromWindow()
    ↓
[View destroyed]
    ↓
[View recreated]
    ↓
Constructor
    ↓
onRestoreInstanceState()
    ↓
[Lifecycle continues]
```

### Best Practices

1. **Initialize in constructor** - Set up paint objects, default values
2. **Start resources in onAttachedToWindow()** - Animations, listeners
3. **Stop resources in onDetachedFromWindow()** - Prevent memory leaks
4. **Avoid allocations in onDraw()** - Pre-allocate objects
5. **Use requestLayout() for size changes** - Triggers proper measurement
6. **Use invalidate() for visual changes** - More efficient
7. **Save state** - Handle configuration changes gracefully
8. **Check isAttachedToWindow()** - Before starting animations

### Common Pitfalls

#### Memory Leaks

```kotlin
// BAD - Listener not unregistered
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    eventBus.register(this)  // Leak if not unregistered
}

// GOOD - Properly cleaned up
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    eventBus.register(this)
}

override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    eventBus.unregister(this)  // Clean up
}
```

#### Object Allocation in onDraw()

```kotlin
// BAD - Creates garbage
override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // New object every frame!
    canvas.drawCircle(x, y, radius, paint)
}

// GOOD - Reuse objects
private val paint = Paint()

override fun onDraw(canvas: Canvas) {
    canvas.drawCircle(x, y, radius, paint)
}
```

### Summary

**Key lifecycle methods:**
- **Constructor** - Initialize view
- **onAttachedToWindow()** - Start resources (animations, listeners)
- **onMeasure()** - Calculate size
- **onLayout()** - Position children
- **onDraw()** - Render content
- **onDetachedFromWindow()** - Release resources

**Important concepts:**
- `requestLayout()` for size/position changes
- `invalidate()` for visual changes only
- Save/restore state for configuration changes
- Clean up resources in onDetachedFromWindow()
- Avoid allocations in onDraw()

## Ответ (RU)
Жизненный цикл View в Android описывает последовательность вызовов методов от создания до уничтожения представления.

### Основные этапы жизненного цикла

1. **Constructor** - Создание экземпляра View
2. **onAttachedToWindow()** - View прикрепляется к окну
3. **onMeasure()** - Измерение размера View
4. **onLayout()** - Позиционирование дочерних элементов
5. **onDraw()** - Отрисовка View
6. **onDetachedFromWindow()** - View отсоединяется от окна

### Важные методы

**onAttachedToWindow()** - Запуск ресурсов:
```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    startAnimation()
    registerListeners()
}
```

**onMeasure()** - Определение размера:
```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val size = 200.dpToPx()
    setMeasuredDimension(size, size)
}
```

**onDraw()** - Отрисовка:
```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)
    canvas.drawCircle(centerX, centerY, radius, paint)
}
```

**onDetachedFromWindow()** - Освобождение ресурсов:
```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    stopAnimation()
    unregisterListeners()
}
```

### Методы обновления

- **requestLayout()** - для изменения размера/позиции (запускает onMeasure, onLayout, onDraw)
- **invalidate()** - только для визуальных изменений (запускает только onDraw)

### Лучшие практики

1. Инициализация в конструкторе
2. Запуск ресурсов в onAttachedToWindow()
3. Остановка ресурсов в onDetachedFromWindow()
4. Избегать создания объектов в onDraw()
5. Сохранение состояния для configuration changes


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

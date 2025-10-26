---
id: "20251025-120200"
title: "Custom Views / Пользовательские View"
aliases: ["Custom Views", "Custom View", "Android Custom Views", "Пользовательские View", "Кастомные View"]
summary: "Creating custom UI components in Android by extending View or ViewGroup classes to implement unique visual elements and interactions"
topic: "android"
subtopics: ["custom-views", "ui", "canvas", "drawing", "view-lifecycle"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["concept", "android", "custom-views", "ui", "canvas", "drawing", "view-lifecycle"]
---

# Custom Views / Пользовательские View

## Summary (EN)

Custom Views in Android are created by extending the View or ViewGroup classes to implement unique visual elements and interactions that aren't available in standard Android UI components. This involves overriding key methods like onDraw(), onMeasure(), and onLayout() to control how the view renders, sizes itself, and positions child views. Custom views are essential for creating complex, reusable UI components with custom drawing, animations, and user interactions.

## Краткое описание (RU)

Пользовательские View в Android создаются путем расширения классов View или ViewGroup для реализации уникальных визуальных элементов и взаимодействий, которые недоступны в стандартных компонентах Android UI. Это включает переопределение ключевых методов, таких как onDraw(), onMeasure() и onLayout(), для управления тем, как view отрисовывается, определяет свой размер и позиционирует дочерние view. Пользовательские view необходимы для создания сложных, переиспользуемых UI компонентов с кастомной отрисовкой, анимациями и взаимодействием с пользователем.

## Key Points (EN)

- Extend View for simple custom drawing or ViewGroup for container layouts
- Override onDraw() to perform custom drawing using Canvas and Paint
- Override onMeasure() to determine the view's size based on constraints
- Override onTouchEvent() to handle custom touch interactions
- Use invalidate() to trigger redraw and requestLayout() for size changes
- Custom attributes defined in attrs.xml allow XML configuration
- Hardware acceleration improves performance for most drawing operations

## Ключевые моменты (RU)

- Расширяйте View для простой отрисовки или ViewGroup для контейнерных layout'ов
- Переопределяйте onDraw() для выполнения кастомной отрисовки с помощью Canvas и Paint
- Переопределяйте onMeasure() для определения размера view на основе ограничений
- Переопределяйте onTouchEvent() для обработки пользовательских touch-взаимодействий
- Используйте invalidate() для перерисовки и requestLayout() для изменения размера
- Пользовательские атрибуты, определенные в attrs.xml, позволяют настройку через XML
- Аппаратное ускорение улучшает производительность для большинства операций отрисовки

## Creating a Basic Custom View

```kotlin
class CircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    private var circleColor: Int = Color.BLUE
    private var circleRadius: Float = 100f

    init {
        // Read custom attributes
        attrs?.let {
            val typedArray = context.obtainStyledAttributes(
                it, R.styleable.CircleView, 0, 0
            )
            circleColor = typedArray.getColor(
                R.styleable.CircleView_circleColor,
                Color.BLUE
            )
            circleRadius = typedArray.getDimension(
                R.styleable.CircleView_circleRadius,
                100f
            )
            typedArray.recycle()
        }
        paint.color = circleColor
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val centerX = width / 2f
        val centerY = height / 2f

        canvas.drawCircle(centerX, centerY, circleRadius, paint)
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desiredWidth = (circleRadius * 2).toInt() + paddingLeft + paddingRight
        val desiredHeight = (circleRadius * 2).toInt() + paddingTop + paddingBottom

        val measuredWidth = resolveSize(desiredWidth, widthMeasureSpec)
        val measuredHeight = resolveSize(desiredHeight, heightMeasureSpec)

        setMeasuredDimension(measuredWidth, measuredHeight)
    }

    // Public API
    fun setCircleColor(color: Int) {
        circleColor = color
        paint.color = color
        invalidate() // Trigger redraw
    }

    fun setCircleRadius(radius: Float) {
        circleRadius = radius
        requestLayout() // Trigger measure and layout
        invalidate()
    }
}
```

## Custom Attributes (attrs.xml)

```xml
<!-- res/values/attrs.xml -->
<resources>
    <declare-styleable name="CircleView">
        <attr name="circleColor" format="color" />
        <attr name="circleRadius" format="dimension" />
    </declare-styleable>
</resources>
```

## Using Custom View in XML

```xml
<com.example.myapp.CircleView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:circleColor="#FF5722"
    app:circleRadius="50dp" />
```

## Key Lifecycle Methods

### onMeasure()
Determines the size of the view.

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val widthMode = MeasureSpec.getMode(widthMeasureSpec)
    val widthSize = MeasureSpec.getSize(widthMeasureSpec)
    val heightMode = MeasureSpec.getMode(heightMeasureSpec)
    val heightSize = MeasureSpec.getSize(heightMeasureSpec)

    // Calculate desired dimensions
    val desiredWidth = 200 // Your calculation
    val desiredHeight = 200

    // Resolve based on mode
    val width = when (widthMode) {
        MeasureSpec.EXACTLY -> widthSize
        MeasureSpec.AT_MOST -> min(desiredWidth, widthSize)
        else -> desiredWidth
    }

    val height = when (heightMode) {
        MeasureSpec.EXACTLY -> heightSize
        MeasureSpec.AT_MOST -> min(desiredHeight, heightSize)
        else -> desiredHeight
    }

    setMeasuredDimension(width, height)
}
```

### onDraw()
Renders the view on the canvas.

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Draw shapes
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), backgroundPaint)
    canvas.drawCircle(centerX, centerY, radius, circlePaint)
    canvas.drawText("Text", x, y, textPaint)

    // Draw paths
    val path = Path().apply {
        moveTo(0f, 0f)
        lineTo(width.toFloat(), height.toFloat())
    }
    canvas.drawPath(path, pathPaint)
}
```

### onLayout()
For ViewGroup, positions child views.

```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    var currentTop = paddingTop

    for (i in 0 until childCount) {
        val child = getChildAt(i)
        if (child.visibility != GONE) {
            val childHeight = child.measuredHeight
            child.layout(
                paddingLeft,
                currentTop,
                paddingLeft + child.measuredWidth,
                currentTop + childHeight
            )
            currentTop += childHeight
        }
    }
}
```

### onTouchEvent()
Handles touch interactions.

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Start of touch
            touchStartX = event.x
            touchStartY = event.y
            return true
        }
        MotionEvent.ACTION_MOVE -> {
            // During touch movement
            currentX = event.x
            currentY = event.y
            invalidate()
            return true
        }
        MotionEvent.ACTION_UP -> {
            // End of touch
            performClick()
            return true
        }
    }
    return super.onTouchEvent(event)
}

override fun performClick(): Boolean {
    // Call listener
    return super.performClick()
}
```

## Advanced Example: Custom Progress Bar

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress: Float = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            invalidate()
        }

    private val backgroundPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.LTGRAY
        style = Paint.Style.FILL
    }

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    private val rectF = RectF()

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val cornerRadius = height / 2f

        // Draw background
        rectF.set(0f, 0f, width.toFloat(), height.toFloat())
        canvas.drawRoundRect(rectF, cornerRadius, cornerRadius, backgroundPaint)

        // Draw progress
        val progressWidth = width * (progress / 100f)
        rectF.set(0f, 0f, progressWidth, height.toFloat())
        canvas.drawRoundRect(rectF, cornerRadius, cornerRadius, progressPaint)
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desiredHeight = 40.dpToPx(context)
        val height = resolveSize(desiredHeight, heightMeasureSpec)
        val width = MeasureSpec.getSize(widthMeasureSpec)
        setMeasuredDimension(width, height)
    }

    fun setProgress(value: Float, animate: Boolean = false) {
        if (animate) {
            ValueAnimator.ofFloat(progress, value).apply {
                duration = 300
                addUpdateListener { progress = it.animatedValue as Float }
                start()
            }
        } else {
            progress = value
        }
    }
}

private fun Int.dpToPx(context: Context): Int {
    return (this * context.resources.displayMetrics.density).toInt()
}
```

## Use Cases

### When to Use

- **Custom charts and graphs**: Display data in unique visual formats
- **Custom controls**: Sliders, knobs, switches with unique behavior
- **Complex animations**: Frame-by-frame or property animations
- **Game UI elements**: Custom game controls and displays
- **Signature capture**: Drawing and capturing user input
- **Data visualization**: Heat maps, gauges, progress indicators
- **Performance-critical UI**: Optimized rendering for smooth animations

### When to Avoid

- **Standard UI components**: Use built-in views when possible
- **Jetpack Compose projects**: Use Compose Canvas instead
- **Simple styling changes**: Use themes, styles, or drawables
- **Complex layouts**: Use ConstraintLayout or other layout managers
- **Rapid prototyping**: Standard components are faster to implement

## Trade-offs

**Pros**:
- Complete control over appearance and behavior
- Optimal performance through custom drawing
- Reusable across projects and screens
- Can create unique, branded UI elements
- Direct access to Canvas for complex graphics
- Hardware-accelerated rendering support
- Full control over touch handling and gestures

**Cons**:
- Requires understanding of Canvas, Paint, and measurement
- More code to write and maintain than standard views
- Need to handle accessibility manually
- Potential performance issues if not optimized
- Testing custom views can be complex
- Must handle configuration changes properly
- Learning curve for developers unfamiliar with custom drawing

## Performance Optimization

```kotlin
class OptimizedCustomView(context: Context) : View(context) {

    // Reuse objects to avoid allocations in onDraw
    private val paint = Paint()
    private val rectF = RectF()
    private val path = Path()

    override fun onDraw(canvas: Canvas) {
        // Avoid allocations in onDraw
        // Reuse existing objects instead

        // Use canvas.save() and restore() instead of creating new Canvas
        val saveCount = canvas.save()
        try {
            // Drawing operations
        } finally {
            canvas.restoreToCount(saveCount)
        }
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Cache measurements when possible
        // Avoid complex calculations in onMeasure if not needed
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }

    // Invalidate only dirty regions
    fun updatePartial(rect: Rect) {
        invalidate(rect) // More efficient than invalidate()
    }
}
```

## Best Practices

- Reuse Paint, Path, and other objects; don't create them in onDraw()
- Call invalidate() only when necessary to trigger redraw
- Use hardware acceleration unless you need specific software-only features
- Implement proper measurement in onMeasure() respecting parent constraints
- Override performClick() when handling touch events for accessibility
- Provide custom attributes for XML configuration
- Document public API methods for other developers
- Consider state saving and restoration for configuration changes
- Use proper constructors to support XML inflation
- Implement accessibility features (content descriptions, etc.)

## Related Concepts

- [[c-canvas]]
- [[c-paint]]
- [[c-jetpack-compose]]
- [[c-view-lifecycle]]
- [[c-touch-events]]
- [[c-hardware-acceleration]]
- [[c-custom-viewgroup]]
- [[c-drawable]]

## References

- [Android Developer Guide: Custom View Components](https://developer.android.com/guide/topics/ui/custom-components)
- [Android Developer Guide: Canvas and Drawables](https://developer.android.com/guide/topics/graphics/2d-graphics)
- [Android Developer Training: Creating Custom Views](https://developer.android.com/training/custom-views)
- [Custom View Performance](https://developer.android.com/topic/performance/rendering)

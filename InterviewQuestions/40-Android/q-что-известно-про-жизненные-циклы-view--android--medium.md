---
id: 202510031417007
title: "What is known about View lifecycles"
question_ru: "Что известно про жизненные циклы View"
question_en: "Что известно про жизненные циклы View"
topic: android
moc: moc-android
status: draft
difficulty: medium
tags:
  - lifecycle
  - view
  - android/activity
  - android/fragments
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/89
---

# What is known about View lifecycles

## English Answer

Each widget (View) and ViewGroup has its own lifecycle, which is closely related to the lifecycle of the Activity or Fragment. Unlike Activity or Fragment, Views don't have built-in lifecycle callbacks, but they go through several distinct stages during their existence.

### View Lifecycle Stages

#### 1. Inflation
When a View is created from XML or programmatically:

```kotlin
// XML inflation
val view = layoutInflater.inflate(R.layout.my_layout, container, false)

// Programmatic creation
val textView = TextView(context).apply {
    text = "Hello"
    textSize = 16f
}
```

**Constructor called**:
```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    init {
        // Called during inflation
        // Initialize view state
    }
}
```

#### 2. Attachment to Window
When View is attached to the window and becomes part of the view hierarchy:

```kotlin
class CustomView(context: Context) : View(context) {

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // View is now part of window
        // Start animations, listeners, observers
        Log.d("Lifecycle", "View attached to window")
    }
}
```

#### 3. Layout (Measurement and Positioning)
System measures and positions the View:

```kotlin
class CustomView(context: Context) : View(context) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Determine the size of the view
        val desiredWidth = 100
        val desiredHeight = 100

        val width = resolveSize(desiredWidth, widthMeasureSpec)
        val height = resolveSize(desiredHeight, heightMeasureSpec)

        setMeasuredDimension(width, height)
        Log.d("Lifecycle", "View measured: $width x $height")
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        super.onLayout(changed, left, top, right, bottom)
        // Position child views (for ViewGroup)
        Log.d("Lifecycle", "View laid out")
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        // Size changed (rotation, layout change)
        Log.d("Lifecycle", "View size changed: $w x $h")
    }
}
```

#### 4. Drawing
View renders its content:

```kotlin
class CustomView(context: Context) : View(context) {

    private val paint = Paint().apply {
        color = Color.BLUE
        strokeWidth = 5f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Draw view content
        canvas.drawCircle(
            width / 2f,
            height / 2f,
            width / 3f,
            paint
        )
        Log.d("Lifecycle", "View drawn")
    }
}
```

#### 5. Updates
View is invalidated and redrawn:

```kotlin
class AnimatedView(context: Context) : View(context) {

    private var animationProgress = 0f

    fun startAnimation() {
        ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            addUpdateListener { animator ->
                animationProgress = animator.animatedValue as Float
                // Trigger redraw
                invalidate()
            }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Draw based on animation progress
        canvas.drawCircle(
            width * animationProgress,
            height / 2f,
            50f,
            paint
        )
    }
}
```

#### 6. Detachment from Window
When View is removed from window:

```kotlin
class CustomView(context: Context) : View(context) {

    private var observer: Observer? = null

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // Setup resources
        observer = Observer { data ->
            updateView(data)
        }
        viewModel.data.observeForever(observer!!)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // Cleanup resources
        observer?.let { viewModel.data.removeObserver(it) }
        observer = null
        Log.d("Lifecycle", "View detached from window")
    }
}
```

### View Lifecycle Diagram

```
Constructor
    ↓
onFinishInflate() (if from XML)
    ↓
onAttachedToWindow()
    ↓
onMeasure()
    ↓
onSizeChanged()
    ↓
onLayout()
    ↓
onDraw()
    ↓
[View is visible and interactive]
    ↓
invalidate() → onDraw() (updates)
    ↓
onDetachedFromWindow()
```

### Relationship with Activity/Fragment Lifecycle

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var customView: CustomView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // View constructors called during setContentView
        customView = findViewById(R.id.custom_view)
        // At this point: Constructor called, XML attributes parsed
    }

    override fun onStart() {
        super.onStart()
        // Views are being attached to window
        // onAttachedToWindow() will be called
    }

    override fun onResume() {
        super.onResume()
        // Views are fully visible and interactive
        // onMeasure(), onLayout(), onDraw() have been called
    }

    override fun onPause() {
        super.onPause()
        // Views still attached but Activity losing focus
    }

    override fun onStop() {
        super.onStop()
        // Views may be detached
        // onDetachedFromWindow() may be called
    }

    override fun onDestroy() {
        super.onDestroy()
        // Views are destroyed
        // Cleanup happens
    }
}
```

### Complete Custom View Example

```kotlin
class ProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0f
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animator: ValueAnimator? = null

    init {
        // 1. Construction phase
        Log.d("ViewLifecycle", "Constructor called")

        // Parse XML attributes
        context.theme.obtainStyledAttributes(
            attrs,
            R.styleable.ProgressView,
            0, 0
        ).apply {
            try {
                progress = getFloat(R.styleable.ProgressView_progress, 0f)
            } finally {
                recycle()
            }
        }
    }

    override fun onFinishInflate() {
        super.onFinishInflate()
        // 2. Inflation complete (only for views from XML)
        Log.d("ViewLifecycle", "onFinishInflate")
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        // 3. Attached to window
        Log.d("ViewLifecycle", "onAttachedToWindow")
        startAnimation()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // 4. Measure phase
        Log.d("ViewLifecycle", "onMeasure")

        val desiredWidth = 200.dpToPx()
        val desiredHeight = 200.dpToPx()

        val width = resolveSize(desiredWidth, widthMeasureSpec)
        val height = resolveSize(desiredHeight, heightMeasureSpec)

        setMeasuredDimension(width, height)
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        // 5. Size changed
        Log.d("ViewLifecycle", "onSizeChanged: $w x $h")
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        super.onLayout(changed, left, top, right, bottom)
        // 6. Layout phase
        Log.d("ViewLifecycle", "onLayout")
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // 7. Draw phase
        Log.d("ViewLifecycle", "onDraw")

        val centerX = width / 2f
        val centerY = height / 2f
        val radius = minOf(width, height) / 3f

        // Draw background circle
        paint.color = Color.LTGRAY
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = 20f
        canvas.drawCircle(centerX, centerY, radius, paint)

        // Draw progress arc
        paint.color = Color.BLUE
        val sweepAngle = 360f * progress
        canvas.drawArc(
            centerX - radius,
            centerY - radius,
            centerX + radius,
            centerY + radius,
            -90f,
            sweepAngle,
            false,
            paint
        )
    }

    private fun startAnimation() {
        animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 2000
            repeatCount = ValueAnimator.INFINITE
            addUpdateListener { animator ->
                progress = animator.animatedValue as Float
                invalidate() // Triggers onDraw()
            }
            start()
        }
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        // 8. Detached from window
        Log.d("ViewLifecycle", "onDetachedFromWindow")

        // Cleanup
        animator?.cancel()
        animator = null
    }

    private fun Int.dpToPx(): Int {
        return (this * resources.displayMetrics.density).toInt()
    }
}
```

### Important View Lifecycle Methods

| Method | Purpose | When Called |
|--------|---------|-------------|
| `Constructor` | Initialize view | During inflation |
| `onFinishInflate()` | Inflation complete | After XML parsing |
| `onAttachedToWindow()` | Attached to window | When added to view hierarchy |
| `onMeasure()` | Measure size | During layout pass |
| `onSizeChanged()` | Size changed | When dimensions change |
| `onLayout()` | Position children | After measurement |
| `onDraw()` | Render content | When view needs drawing |
| `invalidate()` | Request redraw | Manually or on state change |
| `requestLayout()` | Request re-layout | When size should change |
| `onDetachedFromWindow()` | Detached from window | When removed from hierarchy |

### Best Practices

1. **Setup resources in onAttachedToWindow()**, cleanup in onDetachedFromWindow()
2. **Don't allocate objects in onDraw()** - it's called frequently
3. **Use invalidate()** for visual updates, **requestLayout()** for size changes
4. **Cache paint objects and dimensions** to improve performance
5. **Override onSaveInstanceState/onRestoreInstanceState** to persist state across configuration changes

## Russian Answer

Каждый виджет (View) и ViewGroup имеет свой жизненный цикл, который тесно связан с жизненным циклом активности или фрагмента. У View нет встроенных коллбэков, как у Activity или Fragment, но они проходят через несколько этапов:

### Основные этапы

**Инфляция** (Inflation): Создание View из XML или программно через конструктор

**Прикрепление к окну** (Attachment): `onAttachedToWindow()` - View становится частью иерархии представлений

**Макетирование** (Layout): `onMeasure()`, `onLayout()` - определение размеров и позиции View

**Рисование** (Drawing): `onDraw()` - отрисовка содержимого View на экране

**Обновление** (Update): `invalidate()` вызывается для перерисовки, `requestLayout()` для пересчета размеров

**Отсоединение от окна** (Detachment): `onDetachedFromWindow()` - View удаляется из иерархии

Жизненный цикл View тесно связан с жизненным циклом Activity/Fragment - когда Activity создается, Views инфлируются и прикрепляются; когда Activity уничтожается, Views отсоединяются и уничтожаются.

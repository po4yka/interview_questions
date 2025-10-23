---
id: 20251021-180000
title: Custom View Lifecycle / Жизненный цикл Custom View
aliases:
- Custom View Lifecycle
- Жизненный цикл Custom View
topic: android
subtopics:
- ui-views
- lifecycle
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- ru
- en
status: reviewed
moc: moc-android
related:
- q-activity-lifecycle-methods--android--medium
- q-performance-optimization-android--android--medium
created: 2025-10-21
updated: 2025-10-21
tags:
- android/ui-views
- android/lifecycle
- difficulty/medium
source: https://developer.android.com/guide/topics/ui/custom-components
source_note: Official custom components guide
---

# Вопрос (RU)
> Жизненный цикл Custom View?

# Question (EN)
> Custom View Lifecycle?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### View Lifecycle Theory

**View Lifecycle** consists of several key phases, each with a specific purpose and timing. Understanding the lifecycle is critical for building efficient custom UI components.

See [[c-lifecycle]], [[c-custom-views]], and [[c-memory-management]] for in-depth understanding.

**Key principles**:
- **Phases execute sequentially** on first View creation
- **Some phases can repeat** on changes (measure, layout, draw)
- **Each phase has its responsibility** and limitations
- **Performance optimization** requires proper understanding of phases

### Main Lifecycle Phases

```
Constructor (once)
    ↓
onAttachedToWindow (once)
    ↓
onMeasure → onLayout → onDraw (can repeat)
    ↓           ↓         ↓
    └───────────┴─────────┘
                ↓
        onDetachedFromWindow (once)
```

### 1. Construction Phase

**Theory**: Constructor is called when View is created from XML or programmatically. This is the only time View receives Context and AttributeSet. All resources should be initialized here.

**Key principles**:
- **Single call** - constructor called only once
- **Resource initialization** - Paint objects, attributes, settings
- **No size access** - width/height not yet known
- **No animations** - View not yet attached to Window

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var progress = 0f

    init {
        // Read XML attributes
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

        setWillNotDraw(false) // Important for views that draw
    }
}
```

### 2. Attachment Phase

**Theory**: onAttachedToWindow() is called when View is added to hierarchy and receives Window. This is the place to start animations, register listeners, and initialize resources requiring Window.

**Key principles**:
- **Window access** - View now has access to Window
- **Start animations** - safe to begin animations
- **Register listeners** - subscribe to system events
- **Initialize resources** - create objects requiring Context

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()

    // Start animations
    startProgressAnimation()

    // Register listeners
    registerSystemListeners()

    // Initialize resources
    initializeResources()
}

private fun startProgressAnimation() {
    // Animation is safe here
}

private fun registerSystemListeners() {
    // Subscribe to system events
}

private fun initializeResources() {
    // Create resources requiring Window
}
```

### 3. Measurement Phase

**Theory**: onMeasure() determines View dimensions based on content and parent constraints. Called when View needs to determine its size. Can be called multiple times.

**Key principles**:
- **Determine dimensions** - View must calculate desired size
- **Respect constraints** - dimensions must match MeasureSpec
- **Call setMeasuredDimension()** - mandatory call at the end
- **Can repeat** - on layout changes

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val desiredWidth = 200 // Desired width
    val desiredHeight = 100 // Desired height

    val width = resolveSize(desiredWidth, widthMeasureSpec)
    val height = resolveSize(desiredHeight, heightMeasureSpec)

    setMeasuredDimension(width, height)
}

private fun resolveSize(desiredSize: Int, measureSpec: Int): Int {
    val specMode = MeasureSpec.getMode(measureSpec)
    val specSize = MeasureSpec.getSize(measureSpec)

    return when (specMode) {
        MeasureSpec.EXACTLY -> specSize
        MeasureSpec.AT_MOST -> min(desiredSize, specSize)
        MeasureSpec.UNSPECIFIED -> desiredSize
        else -> desiredSize
    }
}
```

### 4. Layout Phase

**Theory**: onLayout() is called after measurement to place View at given coordinates. Determines final position and size of View. Called when layout changes.

**Key principles**:
- **Place View** - determine final position
- **Sizes known** - width/height now available
- **Coordinates set** - left, top, right, bottom established
- **Can repeat** - on layout changes

```kotlin
override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
    super.onLayout(changed, left, top, right, bottom)

    if (changed) {
        // Layout changed - update internal components
        updateInternalLayout()

        // Recalculate cached values
        recalculateCachedValues()
    }
}

private fun updateInternalLayout() {
    // Update internal components based on new dimensions
}

private fun recalculateCachedValues() {
    // Recalculate cached values
}
```

### 5. Drawing Phase

**Theory**: onDraw() is called to draw View on Canvas. This is where actual content drawing happens. Can be called very frequently.

**Key principles**:
- **Actual drawing** - draw content on Canvas
- **Frequent calls** - can be called on every invalidate()
- **Optimization critical** - avoid object creation
- **Use caching** - precompute values

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Draw background
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), backgroundPaint)

    // Draw progress
    val progressWidth = width * (progress / 100f)
    canvas.drawRect(0f, 0f, progressWidth, height.toFloat(), progressPaint)

    // Draw text
    if (showPercentage) {
        val text = "${progress.toInt()}%"
        canvas.drawText(text, width / 2f, height / 2f, textPaint)
    }
}
```

### 6. Detachment Phase

**Theory**: onDetachedFromWindow() is called when View is removed from hierarchy. This is the place to clean up resources, cancel animations, and unsubscribe.

**Key principles**:
- **Clean up resources** - release all resources
- **Cancel animations** - stop all animations
- **Unsubscribe** - cancel listeners and callbacks
- **Prevent memory leaks** - critical for performance

```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()

    // Cancel animations
    cancelAnimations()

    // Unsubscribe
    unregisterSystemListeners()

    // Clean up resources
    cleanupResources()
}

private fun cancelAnimations() {
    // Cancel all animations
}

private fun unregisterSystemListeners() {
    // Cancel system event subscriptions
}

private fun cleanupResources() {
    // Clean up resources
}
```

### Best Practices

1. **Initialize resources in constructor** - Paint objects, attributes
2. **Start animations in onAttachedToWindow()** - safe for Window
3. **Optimize onDraw()** - avoid object creation
4. **Clean up resources in onDetachedFromWindow()** - prevent memory leaks
5. **Use caching** - precompute values
6. **Handle changes properly** - check changed parameters
7. **Test on weak devices** - verify performance

### Pitfalls

- **Don't create objects in onDraw()** - affects performance
- **Don't forget setMeasuredDimension()** - mandatory call in onMeasure()
- **Clean up resources properly** - prevent memory leaks
- **Don't start animations in constructor** - View not yet attached
- **Check changed parameters** - avoid unnecessary calculations

---

## Follow-ups

- How to handle configuration changes in custom views?
- What are the performance implications of each lifecycle phase?
- How to implement custom measurement logic?
- When to use onSizeChanged vs onLayout?

## References

- [Custom Components Guide](https://developer.android.com/guide/topics/ui/custom-components)
- [View Lifecycle Documentation](https://developer.android.com/reference/android/view/View)

---
tags:
  - programming-languages
  - android
difficulty: medium
---

# Что известно про методы, которые перерисовывают View?

## Answer

Android provides several methods to trigger View redrawing and layout recalculation. Understanding when and how to use each method is crucial for efficient UI updates.

### 1. invalidate()

Marks the View for redrawing by calling `onDraw()`. Use when visual appearance changes but size remains the same.

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var color = Color.RED

    fun changeColor(newColor: Int) {
        color = newColor
        // Trigger redraw - calls onDraw()
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(color)
    }
}
```

#### When to use invalidate():
- Color changes
- Text updates
- Drawing state changes
- Visibility changes in custom drawing
- Animation frames

```kotlin
class AnimatedView : View {
    private var progress = 0f

    fun animateProgress(toProgress: Float) {
        val animator = ValueAnimator.ofFloat(progress, toProgress)
        animator.addUpdateListener { animation ->
            progress = animation.animatedValue as Float
            invalidate() // Redraw each frame
        }
        animator.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Draw progress based on current value
        canvas.drawArc(rect, 0f, 360f * progress, true, paint)
    }
}
```

### 2. requestLayout()

Triggers recalculation of sizes and positioning by calling `onMeasure()` and `onLayout()`. Use when View dimensions change.

```kotlin
class ExpandableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {

    private var isExpanded = false

    fun toggleExpansion() {
        isExpanded = !isExpanded
        // Trigger remeasure and relayout
        requestLayout()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val height = if (isExpanded) 400.dp else 100.dp
        setMeasuredDimension(
            MeasureSpec.getSize(widthMeasureSpec),
            height
        )
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // Position children based on new size
        for (i in 0 until childCount) {
            getChildAt(i).layout(0, 0, width, height)
        }
    }
}
```

#### When to use requestLayout():
- Size changes
- Margin/padding changes
- LayoutParams changes
- Adding/removing children
- Orientation changes

```kotlin
class DynamicSizeView : View {

    fun changeSize(newWidth: Int, newHeight: Int) {
        val params = layoutParams
        params.width = newWidth
        params.height = newHeight
        layoutParams = params // Automatically calls requestLayout()
    }

    fun changeSizeManually(newWidth: Int, newHeight: Int) {
        // Manual approach
        layoutParams = layoutParams.apply {
            width = newWidth
            height = newHeight
        }
        requestLayout() // Ensure layout is recalculated
        invalidate()    // And redrawn
    }
}
```

### 3. postInvalidate()

Deferred redrawing from a non-UI thread. Thread-safe version of `invalidate()`.

```kotlin
class LoadingView : View {

    private var loadingProgress = 0

    fun startLoading() {
        Thread {
            while (loadingProgress < 100) {
                Thread.sleep(100)
                loadingProgress += 10

                // CANNOT call invalidate() from background thread
                // Must use postInvalidate()
                postInvalidate()
            }
        }.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawRect(0f, 0f, width * loadingProgress / 100f, height.toFloat(), paint)
    }
}
```

#### Comparison: invalidate() vs postInvalidate()

```kotlin
class ComparisonExample : View {

    // From UI thread - use invalidate()
    fun updateFromUIThread() {
        invalidate() // Safe, direct call
    }

    // From background thread - use postInvalidate()
    fun updateFromBackgroundThread() {
        Thread {
            // Do background work
            processData()

            // Wrong - will crash!
            // invalidate()

            // Correct - posts to UI thread
            postInvalidate()

            // Alternative using post()
            post { invalidate() }
        }.start()
    }

    private fun processData() {
        // Background processing
    }
}
```

### 4. Additional Redraw Methods

#### forceLayout()
Forces layout pass without immediate redraw:

```kotlin
fun forceLayoutExample() {
    val view = findViewById<View>(R.id.myView)
    view.forceLayout() // Mark for layout
    view.requestLayout() // Trigger layout pass
}
```

#### invalidateDrawable()
Invalidates a specific Drawable:

```kotlin
class CustomView : View {
    private val drawable = ContextCompat.getDrawable(context, R.drawable.icon)

    init {
        drawable?.callback = object : Drawable.Callback {
            override fun invalidateDrawable(who: Drawable) {
                invalidate() // Redraw when drawable changes
            }

            override fun scheduleDrawable(who: Drawable, what: Runnable, `when`: Long) {}
            override fun unscheduleDrawable(who: Drawable, what: Runnable) {}
        }
    }
}
```

### 5. Practical Examples

#### Complex View Update

```kotlin
class ComplexView : View {
    private var text = "Hello"
    private var textSize = 14f

    fun updateText(newText: String) {
        text = newText
        invalidate() // Only visual change, no size change
    }

    fun updateTextSize(newSize: Float) {
        textSize = newSize
        // Size might change, need both
        requestLayout()
        invalidate()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // Measure based on text size
        val paint = Paint().apply { textSize = this@ComplexView.textSize }
        val textWidth = paint.measureText(text)
        setMeasuredDimension(textWidth.toInt(), textSize.toInt())
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply {
            textSize = this@ComplexView.textSize
            color = Color.BLACK
        }
        canvas.drawText(text, 0f, textSize, paint)
    }
}
```

#### Optimized Updates

```kotlin
class OptimizedView : View {

    private var needsLayout = false
    private var needsRedraw = false

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

    fun updateColor(color: Int) {
        // Just visual change
        needsRedraw = true
    }

    fun updateSize(size: Int) {
        // Layout change
        needsLayout = true
        needsRedraw = true
    }
}

// Usage
optimizedView.batchUpdates {
    updateColor(Color.RED)
    updateSize(100)
} // Single layout and invalidate call
```

### Best Practices

1. **Use invalidate()** for visual-only changes
2. **Use requestLayout()** when size/position changes
3. **Use postInvalidate()** from background threads
4. **Batch updates** when possible to avoid multiple redraws
5. **Avoid calling in loops** - invalidate/requestLayout are expensive
6. **Check if attached** before calling these methods

```kotlin
fun safeInvalidate() {
    if (isAttachedToWindow) {
        invalidate()
    }
}
```

### Summary Table

| Method | Thread | Calls | Use Case |
|--------|--------|-------|----------|
| `invalidate()` | UI thread | `onDraw()` | Visual changes only |
| `requestLayout()` | UI thread | `onMeasure()`, `onLayout()` | Size/position changes |
| `postInvalidate()` | Any thread | `onDraw()` (on UI thread) | Visual changes from background |
| `forceLayout()` | UI thread | Marks for layout | Force layout recalculation |

---

# Что известно про методы, которые перерисовывают View?

## Ответ

invalidate() — помечает View на перерисовку (вызов onDraw). requestLayout() — вызывает перерасчёт размеров и размещения (onMeasure, onLayout). postInvalidate() — отложенная перерисовка из не-UI потока.

---
id: "20251015082237357"
title: "Custom View Animation / Анимация кастомных View"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - custom-views
  - animation
  - valueanimator
  - performance
---
# Custom View Animation

# Question (EN)
> How do you animate custom views? Compare different animation approaches (ValueAnimator, Property Animation, Canvas animation). Implement smooth animated transitions and handle animation lifecycle properly.

# Вопрос (RU)
> Как анимировать пользовательские view? Сравните различные подходы к анимации (ValueAnimator, Property Animation, Canvas animation). Реализуйте плавные анимированные переходы и правильно управляйте жизненным циклом анимации.

---

## Answer (EN)

**Animating custom views** brings them to life and improves user experience. Understanding different animation approaches and their performance characteristics is essential for smooth, responsive UIs.

### Animation Approaches Comparison

| Approach | Use Case | Performance | Complexity |
|----------|----------|-------------|------------|
| **ValueAnimator** | Animate custom properties | Excellent | Low |
| **Property Animation** | Animate View properties | Excellent | Very Low |
| **Canvas Animation** | Complex custom animations | Good | Medium |
| **Drawable Animation** | Frame-by-frame | Poor (high memory) | Low |

---

### 1. ValueAnimator - Most Flexible

**ValueAnimator** animates values over time. You manually apply animated values to your view.

```kotlin
class AnimatedProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var progress: Float = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            invalidate() // Redraw on value change
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var animator: ValueAnimator? = null

    fun setProgress(targetProgress: Float, animated: Boolean = true) {
        if (!animated) {
            progress = targetProgress
            return
        }

        // Cancel existing animation
        animator?.cancel()

        // Create new animation
        animator = ValueAnimator.ofFloat(progress, targetProgress).apply {
            duration = 500
            interpolator = DecelerateInterpolator()

            addUpdateListener { animation ->
                progress = animation.animatedValue as Float
            }

            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val progressWidth = width * (progress / 100f)
        canvas.drawRect(0f, 0f, progressWidth, height.toFloat(), paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel() // Clean up
    }
}
```

**Usage:**
```kotlin
progressBar.setProgress(75f, animated = true)
```

---

### 2. Property Animation with ViewPropertyAnimator

**ViewPropertyAnimator** animates built-in View properties (alpha, translation, scale, rotation).

```kotlin
class FadeInView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    init {
        alpha = 0f // Start invisible
    }

    fun show() {
        animate()
            .alpha(1f)
            .setDuration(300)
            .setInterpolator(AccelerateDecelerateInterpolator())
            .start()
    }

    fun hide() {
        animate()
            .alpha(0f)
            .setDuration(300)
            .withEndAction {
                visibility = GONE
            }
            .start()
    }

    fun pulse() {
        // Scale up and down
        animate()
            .scaleX(1.2f)
            .scaleY(1.2f)
            .setDuration(200)
            .withEndAction {
                animate()
                    .scaleX(1f)
                    .scaleY(1f)
                    .setDuration(200)
                    .start()
            }
            .start()
    }
}
```

**Chainable animations:**
```kotlin
view.animate()
    .alpha(0f)
    .translationX(100f)
    .rotation(360f)
    .setDuration(500)
    .withEndAction {
        // Next animation
        view.animate()
            .alpha(1f)
            .translationX(0f)
            .setDuration(500)
            .start()
    }
    .start()
```

---

### 3. Canvas Animation with Path

Animate drawing on canvas.

```kotlin
class AnimatedPathView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val path = Path()
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 5f
        color = Color.BLUE
    }

    private val pathMeasure = PathMeasure()
    private var pathLength = 0f
    private var animatedLength = 0f
    private var animator: ValueAnimator? = null

    fun setPath(newPath: Path, animate: Boolean = true) {
        path.reset()
        path.addPath(newPath)

        pathMeasure.setPath(path, false)
        pathLength = pathMeasure.length

        if (animate) {
            animatePath()
        } else {
            animatedLength = pathLength
            invalidate()
        }
    }

    private fun animatePath() {
        animator?.cancel()

        animator = ValueAnimator.ofFloat(0f, pathLength).apply {
            duration = 1000
            interpolator = DecelerateInterpolator()

            addUpdateListener { animation ->
                animatedLength = animation.animatedValue as Float
                invalidate()
            }

            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        if (animatedLength == 0f) return

        // Draw only animated portion of path
        val dst = Path()
        pathMeasure.getSegment(0f, animatedLength, dst, true)

        canvas.drawPath(dst, paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
    }
}
```

---

### 4. Color Animation

Animate between colors smoothly.

```kotlin
class ColorTransitionView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var currentColor: Int = Color.BLUE
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animator: ValueAnimator? = null

    fun animateToColor(targetColor: Int, duration: Long = 500) {
        animator?.cancel()

        animator = ValueAnimator.ofArgb(currentColor, targetColor).apply {
            this.duration = duration

            addUpdateListener { animation ->
                currentColor = animation.animatedValue as Int
                paint.color = currentColor
                invalidate()
            }

            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
    }
}
```

**Usage:**
```kotlin
view.animateToColor(Color.RED, duration = 300)
```

---

### 5. Multiple Properties Animation

Animate multiple properties simultaneously.

```kotlin
class CircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var radius: Float = 50f
    private var centerX: Float = 0f
    private var centerY: Float = 0f
    private var color: Int = Color.BLUE

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    fun animateToPosition(x: Float, y: Float, newRadius: Float, newColor: Int) {
        // Animate multiple properties together
        val radiusAnimator = ValueAnimator.ofFloat(radius, newRadius)
        val xAnimator = ValueAnimator.ofFloat(centerX, x)
        val yAnimator = ValueAnimator.ofFloat(centerY, y)
        val colorAnimator = ValueAnimator.ofArgb(color, newColor)

        val animatorSet = AnimatorSet().apply {
            duration = 500
            interpolator = OvershootInterpolator()

            addUpdateListener { animation ->
                radius = radiusAnimator.animatedValue as Float
                centerX = xAnimator.animatedValue as Float
                centerY = yAnimator.animatedValue as Float
                color = colorAnimator.animatedValue as Int
                paint.color = color
                invalidate()
            }

            playTogether(radiusAnimator, xAnimator, yAnimator, colorAnimator)
        }

        animatorSet.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawCircle(centerX, centerY, radius, paint)
    }
}
```

---

### 6. Spring Animation (Physics-Based)

Natural, physics-based animations using SpringAnimation.

```kotlin
class SpringView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var offsetX = 0f

    init {
        setOnClickListener {
            // Create spring animation
            val spring = SpringAnimation(this, DynamicAnimation.TRANSLATION_X, 0f).apply {
                spring = SpringForce(0f).apply {
                    dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
                    stiffness = SpringForce.STIFFNESS_LOW
                }
            }

            // Drag and release
            translationX = 200f
            spring.start()
        }
    }
}
```

**Benefits of spring animations:**
- Natural, physics-based motion
- Automatically interruptible
- No fixed duration needed

---

### 7. Real-World Example: Loading Spinner

```kotlin
class LoadingSpinner @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var rotation = 0f
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeWidth = 10f
        strokeCap = Paint.Cap.ROUND
    }

    private val animator = ValueAnimator.ofFloat(0f, 360f).apply {
        duration = 1000
        repeatCount = ValueAnimator.INFINITE
        interpolator = LinearInterpolator()

        addUpdateListener { animation ->
            rotation = animation.animatedValue as Float
            invalidate()
        }
    }

    var isAnimating: Boolean = false
        set(value) {
            field = value
            if (value) {
                animator.start()
            } else {
                animator.cancel()
            }
        }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        if (isAnimating) {
            animator.start()
        }
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator.cancel()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val cx = width / 2f
        val cy = height / 2f
        val radius = min(width, height) / 2f * 0.8f

        canvas.save()
        canvas.rotate(rotation, cx, cy)

        // Draw arc (incomplete circle for spinner effect)
        paint.color = Color.BLUE
        canvas.drawArc(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            0f, 270f, // 270° arc
            false, paint
        )

        canvas.restore()
    }
}
```

---

### 8. Wave Animation

```kotlin
class WaveView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val wavePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private val wavePath = Path()
    private var phase = 0f
    private val amplitude = 50f
    private val frequency = 2f

    private val animator = ValueAnimator.ofFloat(0f, 2 * PI.toFloat()).apply {
        duration = 2000
        repeatCount = ValueAnimator.INFINITE
        interpolator = LinearInterpolator()

        addUpdateListener { animation ->
            phase = animation.animatedValue as Float
            invalidate()
        }
    }

    var isAnimating: Boolean = false
        set(value) {
            field = value
            if (value) animator.start() else animator.cancel()
        }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        wavePath.reset()
        wavePath.moveTo(0f, height / 2f)

        // Create wave shape
        for (x in 0..width step 10) {
            val y = height / 2f +
                    amplitude * sin(frequency * x * PI / width + phase).toFloat()
            wavePath.lineTo(x.toFloat(), y)
        }

        wavePath.lineTo(width.toFloat(), height.toFloat())
        wavePath.lineTo(0f, height.toFloat())
        wavePath.close()

        canvas.drawPath(wavePath, wavePaint)
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        if (isAnimating) animator.start()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator.cancel()
    }
}
```

---

### 9. Interpolators Comparison

**Interpolators** control animation timing.

```kotlin
// Linear - Constant speed
animator.interpolator = LinearInterpolator()

// Accelerate - Starts slow, ends fast
animator.interpolator = AccelerateInterpolator()

// Decelerate - Starts fast, ends slow
animator.interpolator = DecelerateInterpolator()

// AccelerateDecelerate - Slow-fast-slow
animator.interpolator = AccelerateDecelerateInterpolator()

// Overshoot - Goes past target, then returns
animator.interpolator = OvershootInterpolator()

// Anticipate - Goes back first, then forward
animator.interpolator = AnticipateInterpolator()

// Bounce - Bounces at the end
animator.interpolator = BounceInterpolator()

// Custom - Create your own
animator.interpolator = object : Interpolator {
    override fun getInterpolation(input: Float): Float {
        return input * input // Quadratic
    }
}
```

**Visual comparison:**

| Interpolator | Motion | Use Case |
|--------------|--------|----------|
| Linear | Constant speed | Progress bars |
| Accelerate | Starts slow | Elements leaving screen |
| Decelerate | Ends slow | Elements entering screen |
| AccelerateDecelerate | Smooth | General animations |
| Overshoot | Bounces past | Attention-grabbing |
| Anticipate | Pull back first | Playful interactions |
| Bounce | Bounces at end | Playful, fun UI |

---

### 10. Animation Lifecycle Management

**Proper cleanup prevents memory leaks:**

```kotlin
class ProperAnimationView : View {

    private var animator: ValueAnimator? = null

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        //  Start animations when attached
        startAnimation()
    }

    override fun onDetachedFromWindow() {
        //  Cancel animations when detached
        animator?.cancel()
        animator = null
        super.onDetachedFromWindow()
    }

    override fun onVisibilityChanged(changedView: View, visibility: Int) {
        super.onVisibilityChanged(changedView, visibility)

        when (visibility) {
            VISIBLE -> {
                //  Resume animation when visible
                startAnimation()
            }
            INVISIBLE, GONE -> {
                //  Pause animation when invisible
                animator?.pause()
            }
        }
    }

    private fun startAnimation() {
        animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            repeatCount = ValueAnimator.INFINITE
            addUpdateListener {
                invalidate()
            }
            start()
        }
    }
}
```

---

### 11. Performance Optimization

**1. Use hardware layers during animation:**
```kotlin
fun animateWithHardwareLayer() {
    setLayerType(LAYER_TYPE_HARDWARE, null)

    animate()
        .alpha(0f)
        .rotation(360f)
        .setDuration(500)
        .withEndAction {
            setLayerType(LAYER_TYPE_NONE, null)
        }
        .start()
}
```

**2. Reduce invalidation area:**
```kotlin
override fun onDraw(canvas: Canvas) {
    // Instead of invalidate(), use:
    invalidate(left, top, right, bottom) // Only redraw changed region
}
```

**3. Use RenderEffect (API 31+):**
```kotlin
@RequiresApi(31)
fun applyBlurEffect() {
    setRenderEffect(
        RenderEffect.createBlurEffect(10f, 10f, Shader.TileMode.CLAMP)
    )
}
```

---

### 12. Testing Animations

```kotlin
@RunWith(AndroidJUnit4::class)
class AnimationTest {

    @Test
    fun testProgressAnimation() = runTest {
        val view = AnimatedProgressBar(ApplicationProvider.getApplicationContext())

        view.setProgress(50f, animated = false)
        assertEquals(50f, view.progress, 0.01f)

        // Test with animation
        view.setProgress(100f, animated = true)

        // Advance time
        advanceTimeBy(500)

        assertEquals(100f, view.progress, 0.01f)
    }
}
```

---

### Best Practices

**1. Always cancel animations in onDetachedFromWindow()**
```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    animator?.cancel() //  Prevent memory leaks
}
```

**2. Use appropriate interpolators**
```kotlin
//  DO - Natural motion
animator.interpolator = DecelerateInterpolator()

//  DON'T - Linear looks mechanical
animator.interpolator = LinearInterpolator()
```

**3. Enable hardware layers for complex animations**
```kotlin
setLayerType(LAYER_TYPE_HARDWARE, null) // During animation
setLayerType(LAYER_TYPE_NONE, null)      // After animation
```

**4. Pause animations when invisible**
```kotlin
override fun onVisibilityChanged(changedView: View, visibility: Int) {
    if (visibility != VISIBLE) {
        animator?.pause()
    }
}
```

**5. Use spring animations for natural motion**
```kotlin
SpringAnimation(view, DynamicAnimation.TRANSLATION_X).apply {
    spring = SpringForce().apply {
        dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
        stiffness = SpringForce.STIFFNESS_LOW
    }
}.start()
```

---

### Summary

**Animation approaches:**
- **ValueAnimator** - Most flexible, animate any value
- **ViewPropertyAnimator** - Simple, for View properties
- **Canvas Animation** - Complex custom animations
- **Spring Animation** - Natural, physics-based

**Key components:**
- Animator (ValueAnimator, ObjectAnimator)
- Interpolator (timing curve)
- Update listener (apply values)

**Lifecycle management:**
- Start in onAttachedToWindow()
- Cancel in onDetachedFromWindow()
- Pause when invisible
- Clean up resources

**Performance:**
- Use hardware layers
- Minimize invalidation area
- Choose appropriate interpolators
- Test on low-end devices

---

## Ответ (RU)

**Анимация пользовательских view** оживляет их и улучшает пользовательский опыт.

### Подходы к анимации

| Подход | Случай использования | Производительность |
|--------|---------------------|-------------------|
| **ValueAnimator** | Анимировать пользовательские свойства | Отлично |
| **Property Animation** | Анимировать свойства View | Отлично |
| **Canvas Animation** | Сложные пользовательские анимации | Хорошо |

### Пример: ValueAnimator

```kotlin
class AnimatedProgressBar : View {

    private var progress: Float = 0f
    private var animator: ValueAnimator? = null

    fun setProgress(target: Float, animated: Boolean = true) {
        animator?.cancel()

        animator = ValueAnimator.ofFloat(progress, target).apply {
            duration = 500
            interpolator = DecelerateInterpolator()

            addUpdateListener { animation ->
                progress = animation.animatedValue as Float
                invalidate()
            }

            start()
        }
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel() // Очистка
    }
}
```

### Интерполяторы

- **LinearInterpolator** - Постоянная скорость
- **AccelerateInterpolator** - Начинает медленно, заканчивает быстро
- **DecelerateInterpolator** - Начинает быстро, заканчивает медленно
- **OvershootInterpolator** - Проходит мимо цели, затем возвращается
- **BounceInterpolator** - Отскакивает в конце

### Управление жизненным циклом

```kotlin
override fun onAttachedToWindow() {
    super.onAttachedToWindow()
    startAnimation() //  Запуск при присоединении
}

override fun onDetachedFromWindow() {
    animator?.cancel() //  Отмена при отсоединении
    super.onDetachedFromWindow()
}
```

### Оптимизация производительности

- Используйте hardware layers во время анимации
- Минимизируйте область invalidation
- Выбирайте подходящие интерполяторы
- Тестируйте на слабых устройствах

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View

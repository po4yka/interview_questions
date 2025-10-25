---
id: 20251021-160000
title: Custom View Animation / Анимация Custom View
aliases: [Custom View Animation, Анимация Custom View]
topic: android
subtopics:
  - ui-animation
  - ui-views
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-canvas-drawing-optimization--android--hard
  - q-custom-view-lifecycle--android--medium
created: 2025-10-21
updated: 2025-10-21
tags: [android/ui-animation, android/ui-views, difficulty/medium]
source: https://developer.android.com/guide/topics/graphics/prop-animation
source_note: Official property animation guide
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:24 pm
---

# Вопрос (RU)
> Анимация Custom View?

# Question (EN)
> Custom View Animation?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Animation Approaches Comparison

| Approach | Use Case | Performance | Complexity |
|----------|----------|-------------|------------|
| **ValueAnimator** | Animate custom properties | Excellent | Low |
| **Property Animation** | Animate View properties | Excellent | Very Low |
| **Canvas Animation** | Complex custom animations | Good | Medium |
| **Drawable Animation** | Frame-by-frame | Poor (high memory) | Low |

### ValueAnimator - Most Flexible

**Theory**: ValueAnimator works on the principle of interpolating values between start and end points over a given time. Uses Choreographer for VSYNC synchronization, ensuring smooth 60 FPS performance. Internally manages temporal curves through Interpolator.

See c-android-animations and [[c-custom-views]] for in-depth understanding.

**Key principles**:
- **Interpolation**: Computing intermediate values between start and end
- **VSYNC synchronization**: Synchronization with screen refresh rate
- **Memory efficiency**: Doesn't create objects, only changes primitive values
- **Lifecycle awareness**: Requires manual cleanup when view is destroyed

```kotlin
class AnimatedProgressBar : View {
    private var progress = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            invalidate()
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var animator: ValueAnimator? = null

    fun setProgress(target: Float, animated: Boolean = true) {
        if (!animated) {
            progress = target
            return
        }

        animator?.cancel()
        animator = ValueAnimator.ofFloat(progress, target).apply {
            duration = 500
            interpolator = DecelerateInterpolator()
            addUpdateListener { progress = it.animatedValue as Float }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        val width = width * (progress / 100f)
        canvas.drawRect(0f, 0f, width, height.toFloat(), paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
    }
}
```

### Property Animation - For View Properties

**Theory**: Property Animation uses reflection to directly change View properties. ViewPropertyAnimator creates a chain of animations, combining them into a single AnimatorSet for optimization. ObjectAnimator works through PropertyValuesHolder for multiple properties.

**Key principles**:
- **Reflection-based**: Direct property changes through reflection
- **Hardware acceleration**: Uses GPU for transformations (scale, rotation, translation)
- **Chained animations**: Combining animations into a single set for synchronization
- **Automatic cleanup**: System automatically cancels animations when View is destroyed

```kotlin
class AnimatedButton : Button {

    fun animateScale() {
        animate()
            .scaleX(1.2f)
            .scaleY(1.2f)
            .setDuration(200)
            .setInterpolator(OvershootInterpolator())
            .withEndAction {
                animate().scaleX(1f).scaleY(1f).setDuration(200).start()
            }
            .start()
    }

    fun animateColor() {
        ObjectAnimator.ofArgb(this, "backgroundColor", Color.BLUE, Color.RED).apply {
            duration = 1000
            repeatCount = ObjectAnimator.INFINITE
            repeatMode = ObjectAnimator.REVERSE
            start()
        }
    }
}
```

### Canvas Animation - For Complex Animations

**Theory**: Canvas Animation works through mathematical functions to compute animated values. Uses trigonometric functions (sin, cos) to create smooth cycles. Each frame recalculates drawing parameters based on animation time.

**Key principles**:
- **Mathematical interpolation**: Using mathematical functions for smooth transitions
- **Frame-by-frame calculation**: Recalculating parameters on each frame
- **Trigonometric cycles**: Sin/cos for cyclical animations
- **Performance optimization**: Caching Paint objects and precomputing constants

```kotlin
class AnimatedCircleView : View {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var animationProgress = 0f
    private var animator: ValueAnimator? = null

    fun startAnimation() {
        animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 2000
            repeatCount = ValueAnimator.INFINITE
            repeatMode = ValueAnimator.REVERSE
            addUpdateListener {
                animationProgress = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        val centerX = width / 2f
        val centerY = height / 2f

        // Animated radius through linear interpolation
        val radius = (min(width, height) / 4f) * (0.5f + 0.5f * animationProgress)

        // Animated alpha through sine wave
        val alpha = (255 * (0.5f + 0.5f * sin(animationProgress * Math.PI))).toInt()
        paint.alpha = alpha

        canvas.drawCircle(centerX, centerY, radius, paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
    }
}
```

### Animation Lifecycle Management

**Theory**: Animation lifecycle should synchronize with View lifecycle. Android system automatically manages some aspects, but developers must explicitly cancel animations when View is destroyed to prevent memory leaks.

**Key principles**:
- **Lifecycle synchronization**: Animations should stop when View is destroyed
- **Visibility handling**: Pausing animations when View not visible to save resources
- **Memory leak prevention**: Explicit animation cancellation in onDetachedFromWindow()
- **State preservation**: Saving animation state during configuration changes

```kotlin
class LifecycleAwareAnimatedView : View {
    private val activeAnimators = mutableListOf<Animator>()

    fun startAnimation() {
        val animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            addUpdateListener { invalidate() }
        }

        activeAnimators.add(animator)
        animator.addListener(object : AnimatorListenerAdapter() {
            override fun onAnimationEnd(animation: Animator) {
                activeAnimators.remove(animation)
            }
        })
        animator.start()
    }

    override fun onVisibilityChanged(changedView: View, visibility: Int) {
        super.onVisibilityChanged(changedView, visibility)

        if (visibility != VISIBLE) {
            activeAnimators.forEach { it.pause() }
        } else {
            activeAnimators.forEach { it.resume() }
        }
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        activeAnimators.forEach { it.cancel() }
        activeAnimators.clear()
    }
}
```

### Interpolators and Their Usage

**Theory**: Interpolators define the temporal curve of animation, transforming linear time into non-linear values. Work on the principle of function f(t) where t ∈ [0,1] and f(t) ∈ [0,1]. Affect the perception of natural movement.

**Key principles**:
- **Time transformation**: Transforming linear time into non-linear values
- **Easing functions**: Mathematical functions for natural movement
- **Performance impact**: Interpolators are computed on each frame
- **Custom curves**: Ability to create custom temporal curves

```kotlin
// Linear animation - constant speed
animator.interpolator = LinearInterpolator()

// Slow down at the end - natural movement
animator.interpolator = DecelerateInterpolator()

// Speed up at the beginning - inertia effect
animator.interpolator = AccelerateInterpolator()

// Smooth acceleration and deceleration - S-curve
animator.interpolator = AccelerateDecelerateInterpolator()

// Elastic effect - overshoot target value
animator.interpolator = OvershootInterpolator()

// Bounce effect - physical bounce simulation
animator.interpolator = BounceInterpolator()

// Custom interpolator - sinusoidal curve
animator.interpolator = object : Interpolator {
    override fun getInterpolation(input: Float): Float {
        return sin(input * Math.PI / 2).toFloat()
    }
}
```

### Best Practices

1. **Always cancel animations** in onDetachedFromWindow()
2. **Use appropriate interpolators** for natural movement
3. **Limit concurrent animations** for performance
4. **Pause animations** when view not visible
5. **Cache Paint objects** - don't create in onDraw()
6. **Use invalidate()** instead of invalidate() for efficiency
7. **Test performance** on weak devices

### Pitfalls

- **Don't forget to cancel animations** - can cause memory leaks
- **Handle screen rotation properly** - animations may reset
- **Avoid animations in onDraw()** - affects performance
- **Don't create objects in animations** - use precomputed values
- **Check view state** before starting animations

---

## Follow-ups

- How to create complex path animations?
- What are the performance differences between animation approaches?
- How to handle animations during configuration changes?
- When to use ViewPropertyAnimator vs ValueAnimator?

## References

- [Property Animation Guide](https://developer.android.com/guide/topics/graphics/prop-animation)
- [Animation and Graphics Overview](https://developer.android.com/guide/topics/graphics)

## Related Questions

### Prerequisites (Easier)
- q-custom-view-implementation--android--medium

### Related (Same Level)
- q-canvas-drawing-android--android--medium
- q-view-lifecycle-android--android--medium

### Advanced (Harder)
- q-android-performance-optimization--android--hard

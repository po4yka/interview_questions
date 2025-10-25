---
id: 20251021-140000
title: Custom Drawable Implementation / Реализация Custom Drawable
aliases:
- Custom Drawable Implementation
- Реализация Custom Drawable
topic: android
subtopics:
- ui-views
- ui-graphics
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- q-canvas-drawing-optimization--android--hard
- q-custom-viewgroup-layout--android--hard
created: 2025-10-21
updated: 2025-10-21
tags:
- android/ui-views
- android/ui-graphics
- difficulty/medium
source: https://developer.android.com/reference/android/graphics/drawable/Drawable
source_note: Official Drawable documentation
---

# Вопрос (RU)
> Реализация Custom Drawable?

# Question (EN)
> Custom Drawable Implementation?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### What is Custom Drawable
- Lightweight, reusable graphics for multiple views
- More efficient than custom View for simple graphics without interaction
- Managed by Android system, no complex lifecycle needed

Related to concepts [[c-custom-views]], c-canvas-drawing, and [[c-lifecycle]].

### Drawable vs Custom View

| Feature | Drawable | Custom View |
|---------|----------|-------------|
| **Use case** | Simple graphics, icons | Interactive UI elements |
| **Performance** | Lightweight | Heavier (full View) |
| **Interaction** | No touch handling | Full touch support |
| **Lifecycle** | Simple | Complex (attach/detach) |
| **Reusability** | High | Lower |
| **State** | Limited | Full state management |

**Use Drawable when:**
- Non-interactive graphics
- Reusable across views
- Simple shapes/animations
- Background/foreground graphics

**Use Custom View when:**
- Need touch interaction
- Complex lifecycle
- Accessibility requirements
- Animation coordination

### Drawable Lifecycle
1. **Creation** - constructor or factory methods
2. **Bounds setting** - `setBounds()` defines drawing area
3. **Drawing** - `draw()` called by system
4. **State changes** - `setState()` for appearance updates
5. **Cleanup** - automatic memory management

### Key Methods to Override

**draw(canvas: Canvas)**
- Main drawing method
- Called by system for rendering

**setBounds()**
- Sets drawing area boundaries
- Defines where and how big to draw

**getOpacity()**
- Returns drawable transparency
- PixelFormat.OPAQUE, TRANSLUCENT, TRANSPARENT

**setAlpha(alpha: Int)**
- Sets alpha channel
- Affects transparency

**setColorFilter(colorFilter: ColorFilter?)**
- Applies color filter
- For tinting and color effects

### Minimal Implementation

```kotlin
class CircleDrawable : Drawable() {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    var color: Int
        get() = paint.color
        set(value) {
            paint.color = value
            invalidateSelf() // Request redraw
        }

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val centerX = bounds.centerX().toFloat()
        val centerY = bounds.centerY().toFloat()
        val radius = min(bounds.width(), bounds.height()) / 2f

        canvas.drawCircle(centerX, centerY, radius, paint)
    }

    override fun setAlpha(alpha: Int) {
        paint.alpha = alpha
        invalidateSelf()
    }

    override fun setColorFilter(colorFilter: ColorFilter?) {
        paint.colorFilter = colorFilter
        invalidateSelf()
    }

    @Deprecated("Deprecated in Java")
    override fun getOpacity(): Int = PixelFormat.TRANSLUCENT

    override fun getIntrinsicWidth(): Int = 48
    override fun getIntrinsicHeight(): Int = 48
}
```

### State Management

```kotlin
class StatefulDrawable : Drawable() {
    private val paint = Paint()
    private var isPressed = false

    override fun draw(canvas: Canvas) {
        paint.color = if (isPressed) Color.RED else Color.BLUE
        canvas.drawRect(bounds, paint)
    }

    override fun setState(stateSet: IntArray): Boolean {
        val wasPressed = isPressed
        isPressed = stateSet.contains(android.R.attr.state_pressed)

        if (wasPressed != isPressed) {
            invalidateSelf()
            return true
        }
        return false
    }

    override fun isStateful(): Boolean = true

    // ... other methods
}
```

### Animated Drawable

```kotlin
class AnimatedDrawable : Drawable() {
    private val paint = Paint()
    private var animationProgress = 0f

    override fun draw(canvas: Canvas) {
        val bounds = bounds
        val animatedRadius = bounds.width() * animationProgress / 2

        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            animatedRadius,
            paint
        )
    }

    fun startAnimation() {
        // Use ValueAnimator for animation
        ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            addUpdateListener { animator ->
                animationProgress = animator.animatedValue as Float
                invalidateSelf()
            }
            start()
        }
    }

    // ... other methods
}
```

### Best Practices

1. **Use Paint.ANTI_ALIAS_FLAG** for smooth edges
2. **Cache Paint objects** - don't create in draw()
3. **Call invalidateSelf()** when appearance changes
4. **Implement intrinsic sizes** for proper layout
5. **Handle states** through setState() for interactivity
6. **Avoid complex calculations** in draw() - precompute
7. **Use proper bounds** through bounds property

### Pitfalls

- **Don't create objects in draw()** - affects performance
- **Handle bounds correctly** - system may change them
- **Remember transparency** - implement getOpacity() correctly
- **Don't forget invalidateSelf()** on changes
- **Test on different sizes** - intrinsic sizes matter

---

## Follow-ups

- How to create compound drawables?
- When to use DrawableContainer vs custom Drawable?
- How to optimize Drawable performance?
- What are the differences between VectorDrawable and custom Drawable?

## References

- [Drawable Documentation](https://developer.android.com/reference/android/graphics/drawable/Drawable)
- [Custom Drawables Guide](https://developer.android.com/guide/topics/graphics/drawables)

## Related Questions

### Advanced (Harder)
- q-android-performance-optimization--android--hard

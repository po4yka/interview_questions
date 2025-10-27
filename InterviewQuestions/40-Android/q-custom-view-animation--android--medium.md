---
id: 20251021-160000
title: Custom View Animation / Анимация Custom View
aliases:
  - Custom View Animation
  - Анимация Custom View
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
sources:
  - https://developer.android.com/guide/topics/graphics/prop-animation
created: 2025-10-21
updated: 2025-10-27
tags:
  - android/ui-animation
  - android/ui-views
  - difficulty/medium
---
# Вопрос (RU)
> Как реализовать анимацию в Custom View?

# Question (EN)
> How to implement animation in Custom View?

---

## Ответ (RU)

### Сравнение подходов к анимации

| Подход | Назначение | Производительность | Сложность |
|--------|------------|-------------------|-----------|
| **ValueAnimator** | Анимация пользовательских свойств | Отличная | Низкая |
| **Property Animation** | Анимация свойств View | Отличная | Очень низкая |
| **Canvas Animation** | Сложные пользовательские анимации | Хорошая | Средняя |

### ValueAnimator - универсальный подход

**Принцип**: ValueAnimator интерполирует значения между начальной и конечной точкой за заданное время. Использует Choreographer для синхронизации с VSYNC (60 FPS). Не создает объекты в памяти, работает только с примитивами.

```kotlin
class AnimatedProgressBar : View {
    private var progress = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            invalidate() // ✅ Перерисовка только при изменении
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var animator: ValueAnimator? = null

    fun setProgress(target: Float, animated: Boolean = true) {
        animator?.cancel() // ✅ Отмена предыдущей анимации
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
        animator?.cancel() // ✅ Предотвращение утечек памяти
    }
}
```

### Property Animation - для стандартных свойств View

**Принцип**: Использует рефлексию для изменения свойств View. ViewPropertyAnimator оптимизирует цепочки анимаций. Поддерживает аппаратное ускорение для трансформаций (scale, rotation, translation).

```kotlin
class AnimatedButton : Button {
    fun animateScale() {
        animate()
            .scaleX(1.2f)
            .scaleY(1.2f)
            .setDuration(200)
            .setInterpolator(OvershootInterpolator()) // ✅ Естественное движение
            .withEndAction {
                animate().scaleX(1f).scaleY(1f).setDuration(200).start()
            }
            .start()
    }
}
```

### Canvas Animation - для сложной графики

**Принцип**: Использует математические функции для вычисления анимированных значений. Тригонометрия (sin, cos) для циклических анимаций.

```kotlin
class AnimatedCircleView : View {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animationProgress = 0f
    private var animator: ValueAnimator? = null

    fun startAnimation() {
        animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 2000
            repeatCount = ValueAnimator.INFINITE
            addUpdateListener {
                animationProgress = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        val radius = (min(width, height) / 4f) * (0.5f + 0.5f * animationProgress)
        val alpha = (255 * (0.5f + 0.5f * sin(animationProgress * Math.PI))).toInt()
        paint.alpha = alpha
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel() // ✅ Обязательная очистка
    }
}
```

### Управление жизненным циклом анимации

```kotlin
class LifecycleAwareAnimatedView : View {
    private val activeAnimators = mutableListOf<Animator>()

    fun startAnimation() {
        val animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    activeAnimators.remove(animation) // ✅ Автоочистка
                }
            })
        }
        activeAnimators.add(animator)
        animator.start()
    }

    override fun onVisibilityChanged(changedView: View, visibility: Int) {
        super.onVisibilityChanged(changedView, visibility)
        if (visibility != VISIBLE) {
            activeAnimators.forEach { it.pause() } // ✅ Экономия ресурсов
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

### Best Practices

1. **Всегда отменяйте анимации** в `onDetachedFromWindow()`
2. **Используйте подходящие интерполяторы**: DecelerateInterpolator для естественного замедления
3. **Кэшируйте Paint объекты** - не создавайте в `onDraw()`
4. **Приостанавливайте анимации** когда View невидим
5. **Ограничивайте количество одновременных анимаций** для производительности

### Типичные ошибки

- ❌ **Забывают отменять анимации** → утечки памяти
- ❌ **Создают объекты в onDraw()** → аллокации и GC паузы
- ❌ **Не учитывают поворот экрана** → анимации сбрасываются
- ❌ **Используют invalidate() вместо postInvalidateOnAnimation()** → пропуски кадров

## Answer (EN)

### Animation Approaches Comparison

| Approach | Use Case | Performance | Complexity |
|----------|----------|-------------|------------|
| **ValueAnimator** | Animate custom properties | Excellent | Low |
| **Property Animation** | Animate View properties | Excellent | Very Low |
| **Canvas Animation** | Complex custom animations | Good | Medium |

### ValueAnimator - Universal Approach

**Principle**: ValueAnimator interpolates values between start and end points over time. Uses Choreographer for VSYNC synchronization (60 FPS). Works with primitives only, no object allocations.

```kotlin
class AnimatedProgressBar : View {
    private var progress = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            invalidate() // ✅ Redraw only on change
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var animator: ValueAnimator? = null

    fun setProgress(target: Float, animated: Boolean = true) {
        animator?.cancel() // ✅ Cancel previous animation
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
        animator?.cancel() // ✅ Prevent memory leaks
    }
}
```

### Property Animation - For Standard View Properties

**Principle**: Uses reflection to change View properties. ViewPropertyAnimator optimizes animation chains. Hardware-accelerated for transformations (scale, rotation, translation).

```kotlin
class AnimatedButton : Button {
    fun animateScale() {
        animate()
            .scaleX(1.2f)
            .scaleY(1.2f)
            .setDuration(200)
            .setInterpolator(OvershootInterpolator()) // ✅ Natural movement
            .withEndAction {
                animate().scaleX(1f).scaleY(1f).setDuration(200).start()
            }
            .start()
    }
}
```

### Canvas Animation - For Complex Graphics

**Principle**: Uses mathematical functions to compute animated values. Trigonometry (sin, cos) for cyclical animations.

```kotlin
class AnimatedCircleView : View {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animationProgress = 0f
    private var animator: ValueAnimator? = null

    fun startAnimation() {
        animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 2000
            repeatCount = ValueAnimator.INFINITE
            addUpdateListener {
                animationProgress = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        val radius = (min(width, height) / 4f) * (0.5f + 0.5f * animationProgress)
        val alpha = (255 * (0.5f + 0.5f * sin(animationProgress * Math.PI))).toInt()
        paint.alpha = alpha
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel() // ✅ Required cleanup
    }
}
```

### Animation Lifecycle Management

```kotlin
class LifecycleAwareAnimatedView : View {
    private val activeAnimators = mutableListOf<Animator>()

    fun startAnimation() {
        val animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    activeAnimators.remove(animation) // ✅ Auto-cleanup
                }
            })
        }
        activeAnimators.add(animator)
        animator.start()
    }

    override fun onVisibilityChanged(changedView: View, visibility: Int) {
        super.onVisibilityChanged(changedView, visibility)
        if (visibility != VISIBLE) {
            activeAnimators.forEach { it.pause() } // ✅ Save resources
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

### Best Practices

1. **Always cancel animations** in `onDetachedFromWindow()`
2. **Use appropriate interpolators**: DecelerateInterpolator for natural deceleration
3. **Cache Paint objects** - don't create in `onDraw()`
4. **Pause animations** when View not visible
5. **Limit concurrent animations** for performance

### Common Mistakes

- ❌ **Forgetting to cancel animations** → memory leaks
- ❌ **Creating objects in onDraw()** → allocations and GC pauses
- ❌ **Not handling screen rotation** → animations reset
- ❌ **Using invalidate() instead of postInvalidateOnAnimation()** → frame drops

---

## Follow-ups

- How to create complex path animations using PathInterpolator?
- What are performance differences between ValueAnimator and ObjectAnimator?
- How to synchronize multiple animations?
- When to use Animator vs ViewPropertyAnimator?
- How to handle animation state during configuration changes?

## References

- [[q-custom-view-lifecycle--android--medium]]
- [[q-canvas-drawing-optimization--android--hard]]
- [Property Animation Guide](https://developer.android.com/guide/topics/graphics/prop-animation)

## Related Questions

### Prerequisites (Easier)
- [[q-custom-view-lifecycle--android--medium]] - Understanding View lifecycle for proper animation cleanup
- Custom View basics and onDraw() fundamentals

### Related (Same Level)
- [[q-canvas-drawing-optimization--android--hard]] - Canvas performance optimization
- Property animation system and Choreographer
- Interpolator types and custom implementations

### Advanced (Harder)
- Complex path animations with PathMeasure
- Animation synchronization across multiple Views
- Hardware-accelerated animation layers

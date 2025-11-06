---
id: android-481
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
status: reviewed
moc: moc-android
related:
- c-choreographer
- c-interpolator
- c-value-animator
- q-canvas-drawing-optimization--android--hard
- q-custom-view-lifecycle--android--medium
sources:
- https://developer.android.com/guide/topics/graphics/prop-animation
created: 2025-10-21
updated: 2025-10-30
tags:
- android/ui-animation
- android/ui-views
- difficulty/medium
---

# Вопрос (RU)
> Как реализовать анимацию в Custom `View`?

# Question (EN)
> How to implement animation in Custom `View`?

---

## Ответ (RU)

### Сравнение Подходов

| Подход | Назначение | Производительность | Управление |
|--------|------------|-------------------|------------|
| **`ValueAnimator`** | Анимация пользовательских свойств | Отличная (VSYNC, без аллокаций) | Полный контроль |
| **Property Animation** | Анимация стандартных свойств `View` | Отличная (Hardware-accelerated) | Простое |
| **`Canvas` Animation** | Сложная математическая графика | Хорошая | Требует математики |

### `ValueAnimator` - Универсальный Подход

**Принцип**: Интерполяция значений через Choreographer, синхронизация с VSYNC (60 FPS), работа только с примитивами.

```kotlin
class AnimatedProgressBar : View {
    private var progress = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            invalidate() // ✅ Перерисовка при изменении
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }
    private var animator: ValueAnimator? = null

    fun setProgress(target: Float) {
        animator?.cancel() // ✅ Отмена предыдущей
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
        animator?.cancel() // ✅ Предотвращение утечек
    }
}
```

### Property Animation - Для Стандартных Свойств

**Принцип**: ViewPropertyAnimator для цепочек анимаций, аппаратное ускорение трансформаций (scale, rotation, translation).

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
}
```

### `Canvas` Animation - Математическая Графика

**Принцип**: Тригонометрия (sin, cos) для циклических анимаций, математические функции для вычисления значений.

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

### Управление Жизненным Циклом

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

**✅ Обязательно:**
- Отменяйте анимации в `onDetachedFromWindow()`
- Кэшируйте `Paint` объекты - НЕ создавайте в `onDraw()`
- Приостанавливайте при `visibility != VISIBLE`

**❌ Ошибки:**
- Забывают отменять анимации → утечки памяти
- Создают объекты в `onDraw()` → GC паузы
- Используют `invalidate()` вместо `postInvalidateOnAnimation()` → пропуски кадров

## Answer (EN)

### Approach Comparison

| Approach | Use Case | Performance | Control |
|----------|----------|-------------|---------|
| **`ValueAnimator`** | Animate custom properties | Excellent (VSYNC, no allocations) | Full control |
| **Property Animation** | Animate standard `View` properties | Excellent (Hardware-accelerated) | Simple |
| **`Canvas` Animation** | Complex mathematical graphics | Good | Requires math |

### `ValueAnimator` - Universal Approach

**Principle**: Value interpolation via Choreographer, VSYNC synchronization (60 FPS), primitives only.

```kotlin
class AnimatedProgressBar : View {
    private var progress = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            invalidate() // ✅ Redraw on change
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }
    private var animator: ValueAnimator? = null

    fun setProgress(target: Float) {
        animator?.cancel() // ✅ Cancel previous
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
        animator?.cancel() // ✅ Prevent leaks
    }
}
```

### Property Animation - Standard Properties

**Principle**: ViewPropertyAnimator for animation chains, hardware acceleration for transformations (scale, rotation, translation).

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
}
```

### `Canvas` Animation - Mathematical Graphics

**Principle**: Trigonometry (sin, cos) for cyclical animations, mathematical functions for value computation.

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

### `Lifecycle` Management

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

**✅ Required:**
- Cancel animations in `onDetachedFromWindow()`
- Cache `Paint` objects - DON'T create in `onDraw()`
- Pause when `visibility != VISIBLE`

**❌ Mistakes:**
- Forgetting to cancel animations → memory leaks
- Creating objects in `onDraw()` → GC pauses
- Using `invalidate()` instead of `postInvalidateOnAnimation()` → frame drops

---

## Follow-ups

- Как создать сложные path-анимации с PathInterpolator?
- В чем разница производительности между `ValueAnimator` и `ObjectAnimator`?
- Как синхронизировать несколько анимаций (AnimatorSet)?
- Когда использовать postInvalidateOnAnimation() вместо invalidate()?
- Как сохранить состояние анимации при повороте экрана?

## References

- [Property Animation](https://developer.android.com/guide/topics/graphics/prop-animation)
- [Hardware Acceleration](https://developer.android.com/topic/performance/hardware-accel)

## Related Questions

### Prerequisites / Concepts

- [[c-choreographer]]
- [[c-interpolator]]
- [[c-value-animator]]


### Prerequisites (Easier)
- [[q-custom-view-lifecycle--android--medium]] - Жизненный цикл `View` для правильной очистки анимаций
- Custom `View` basics - onDraw() и основы рендеринга

### Related (Same Level)
- [[q-canvas-drawing-optimization--android--hard]] - Оптимизация `Canvas` для плавных анимаций
- Property Animation System - `ObjectAnimator` vs ViewPropertyAnimator
- Touch handling with animation - Gesture integration

### Advanced (Harder)
- `Path` animations with PathMeasure - Сложные траектории движения
- Spring animations - Physics-based motion (SpringAnimation, FlingAnimation)
- Coordinated animations - Transition API и Motion Layout

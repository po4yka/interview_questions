---
id: 20251021-160000
title: "Custom View Animation / Анимация Custom View"
aliases: [Custom View Animation, Анимация Custom View]
topic: android
subtopics: [ui-views, ui-animation]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-custom-view-implementation--android--medium, q-canvas-drawing-android--android--medium, q-view-lifecycle-android--android--medium]
created: 2025-10-21
updated: 2025-10-21
tags: [android/ui-views, android/ui-animation, animation, custom-views, valueanimator, performance, difficulty/medium]
source: https://developer.android.com/guide/topics/graphics/prop-animation
source_note: Official property animation guide
---

# Вопрос (RU)
> Как анимировать пользовательские view? Сравните различные подходы к анимации (ValueAnimator, Property Animation, Canvas animation). Реализуйте плавные анимированные переходы и правильно управляйте жизненным циклом анимации.

# Question (EN)
> How do you animate custom views? Compare different animation approaches (ValueAnimator, Property Animation, Canvas animation). Implement smooth animated transitions and handle animation lifecycle properly.

---

## Ответ (RU)

### Сравнение подходов к анимации

| Подход | Использование | Производительность | Сложность |
|--------|---------------|-------------------|-----------|
| **ValueAnimator** | Анимация пользовательских свойств | Отличная | Низкая |
| **Property Animation** | Анимация свойств View | Отличная | Очень низкая |
| **Canvas Animation** | Сложные пользовательские анимации | Хорошая | Средняя |
| **Drawable Animation** | Покадровая анимация | Плохая (высокая память) | Низкая |

### ValueAnimator - самый гибкий

**Теория**: ValueAnimator работает по принципу интерполяции значений между начальной и конечной точками за заданное время. Использует Choreographer для синхронизации с VSYNC, обеспечивая плавность 60 FPS. Внутренне управляет временными кривыми через Interpolator.

**Ключевые принципы**:
- **Интерполяция**: Вычисление промежуточных значений между start и end
- **VSYNC синхронизация**: Синхронизация с частотой обновления экрана
- **Memory efficiency**: Не создает объекты, только изменяет примитивные значения
- **Lifecycle awareness**: Требует ручной очистки при уничтожении view

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

### Property Animation - для свойств View

**Теория**: Property Animation использует рефлексию для прямого изменения свойств View. ViewPropertyAnimator создает цепочку анимаций, объединяя их в один AnimatorSet для оптимизации. ObjectAnimator работает через PropertyValuesHolder для множественных свойств.

**Ключевые принципы**:
- **Reflection-based**: Прямое изменение свойств через рефлексию
- **Hardware acceleration**: Использует GPU для трансформаций (scale, rotation, translation)
- **Chained animations**: Объединение анимаций в один набор для синхронизации
- **Automatic cleanup**: Система автоматически отменяет анимации при уничтожении View

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

### Canvas Animation - для сложных анимаций

**Теория**: Canvas Animation работает через математические функции для вычисления анимированных значений. Использует тригонометрические функции (sin, cos) для создания плавных циклов. Каждый кадр пересчитывает параметры рисования на основе времени анимации.

**Ключевые принципы**:
- **Mathematical interpolation**: Использование математических функций для плавных переходов
- **Frame-by-frame calculation**: Пересчет параметров на каждом кадре
- **Trigonometric cycles**: Sin/cos для циклических анимаций
- **Performance optimization**: Кэширование Paint объектов и предвычисление констант

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

        // Анимированный радиус через линейную интерполяцию
        val radius = (min(width, height) / 4f) * (0.5f + 0.5f * animationProgress)

        // Анимированный альфа через синусоиду
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

### Управление жизненным циклом анимации

**Теория**: Жизненный цикл анимации должен синхронизироваться с жизненным циклом View. Система Android автоматически управляет некоторыми аспектами, но разработчик должен явно отменять анимации при уничтожении View для предотвращения memory leaks.

**Ключевые принципы**:
- **Lifecycle synchronization**: Анимации должны останавливаться при уничтожении View
- **Visibility handling**: Приостановка анимаций когда View не видим для экономии ресурсов
- **Memory leak prevention**: Явная отмена анимаций в onDetachedFromWindow()
- **State preservation**: Сохранение состояния анимации при изменениях конфигурации

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

### Интерполяторы и их использование

**Теория**: Интерполяторы определяют временную кривую анимации, преобразуя линейное время в нелинейные значения. Работают по принципу функции f(t) где t ∈ [0,1] и f(t) ∈ [0,1]. Влияют на восприятие естественности движения.

**Ключевые принципы**:
- **Time transformation**: Преобразование линейного времени в нелинейные значения
- **Easing functions**: Математические функции для естественного движения
- **Performance impact**: Интерполяторы вычисляются на каждом кадре
- **Custom curves**: Возможность создания собственных временных кривых

```kotlin
// Линейная анимация - постоянная скорость
animator.interpolator = LinearInterpolator()

// Замедление в конце - естественное движение
animator.interpolator = DecelerateInterpolator()

// Ускорение в начале - эффект инерции
animator.interpolator = AccelerateInterpolator()

// Плавное ускорение и замедление - S-кривая
animator.interpolator = AccelerateDecelerateInterpolator()

// Эластичный эффект - превышение целевого значения
animator.interpolator = OvershootInterpolator()

// Отскок - имитация физического отскока
animator.interpolator = BounceInterpolator()

// Кастомный интерполятор - синусоидальная кривая
animator.interpolator = object : Interpolator {
    override fun getInterpolation(input: Float): Float {
        return sin(input * Math.PI / 2).toFloat()
    }
}
```

### Лучшие практики

1. **Всегда отменяйте анимации** в onDetachedFromWindow()
2. **Используйте подходящие интерполяторы** для естественного движения
3. **Ограничивайте количество одновременных анимаций** для производительности
4. **Приостанавливайте анимации** когда view не видим
5. **Кэшируйте Paint объекты** - не создавайте в onDraw()
6. **Используйте invalidate()** вместо invalidate() для эффективности
7. **Тестируйте производительность** на слабых устройствах

### Подводные камни

- **Не забывайте отменять анимации** - могут вызвать memory leaks
- **Правильно обрабатывайте поворот экрана** - анимации могут сброситься
- **Избегайте анимаций в onDraw()** - влияет на производительность
- **Не создавайте объекты в анимациях** - используйте предвычисленные значения
- **Проверяйте состояние view** перед запуском анимаций

---

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
- [[q-custom-view-implementation--android--medium]]

### Related (Same Level)
- [[q-canvas-drawing-android--android--medium]]
- [[q-view-lifecycle-android--android--medium]]

### Advanced (Harder)
- [[q-android-performance-optimization--android--hard]]

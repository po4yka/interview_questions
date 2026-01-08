---\
id: android-481
title: Custom View Animation / Анимация Custom View
aliases: [Custom View Animation, Анимация Custom View]
topic: android
subtopics: [ui-animation, ui-views]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-surfaces, q-canvas-drawing-optimization--android--hard, q-custom-view-accessibility--android--medium, q-custom-view-attributes--android--medium, q-custom-view-lifecycle--android--medium]
sources:
  - "https://developer.android.com/guide/topics/graphics/prop-animation"
created: 2025-10-21
updated: 2025-11-10
tags: [android/ui-animation, android/ui-views, difficulty/medium]

---\
# Вопрос (RU)
> Как реализовать анимацию в Custom `View`?

# Question (EN)
> How to implement animation in Custom `View`?

---

## Ответ (RU)

### Сравнение Подходов

| Подход | Назначение | Производительность | Управление |
|--------|------------|-------------------|------------|
| **ValueAnimator** | Анимация пользовательских свойств | Высокая (VSYNC-синхронизация, гибкий контроль) | Полный контроль |
| **Property Animation** | Анимация стандартных свойств `View` | Отличная (hardware-ускорение трансформаций) | Простое |
| **`Canvas` Animation** | Сложная математическая графика | Хорошая | Требует математики |

### ValueAnimator - Универсальный Подход

**Принцип**: Интерполяция значений через `Choreographer`, синхронизация с VSYNC, обновление состояний (часто примитивов) и вызов `invalidate()`/`postInvalidateOnAnimation()` для перерисовки.

```kotlin
class AnimatedProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            // Для вызовов с главного потока invalidate() корректен, для off-main — postInvalidateOnAnimation()
            invalidate()
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var animator: ValueAnimator? = null

    fun setProgress(target: Float) {
        animator?.cancel()
        animator = ValueAnimator.ofFloat(progress, target).apply {
            duration = 500
            interpolator = DecelerateInterpolator()
            addUpdateListener { progress = it.animatedValue as Float }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        val filledWidth = width * (progress / 100f)
        canvas.drawRect(0f, 0f, filledWidth, height.toFloat(), paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
    }
}
```

### Property Animation - Для Стандартных Свойств

**Принцип**: `ViewPropertyAnimator` для цепочек анимаций, аппаратное ускорение трансформаций (`alpha`, `translation`, `scale`, `rotation`).

```kotlin
class AnimatedButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = android.R.attr.buttonStyle
) : Button(context, attrs, defStyleAttr) {

    fun animateScale() {
        animate()
            .scaleX(1.2f)
            .scaleY(1.2f)
            .setDuration(200)
            .setInterpolator(OvershootInterpolator())
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

### Canvas Animation - Математическая Графика

**Принцип**: Тригонометрия (`sin`, `cos`) и другие функции для вычисления параметров анимации с ручной перерисовкой.

```kotlin
import kotlin.math.min
import kotlin.math.sin

class AnimatedCircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animationProgress = 0f
    private var animator: ValueAnimator? = null

    fun startAnimation() {
        animator?.cancel()
        animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 2000
            repeatCount = ValueAnimator.INFINITE
            repeatMode = ValueAnimator.RESTART
            addUpdateListener {
                animationProgress = it.animatedValue as Float
                // На главном потоке можно использовать invalidate(), для VSYNC-синхронизации предпочтителен postInvalidateOnAnimation()
                postInvalidateOnAnimation()
            }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        val baseRadius = min(width, height) / 4f
        val radius = baseRadius * (0.5f + 0.5f * animationProgress)
        val alpha = (255 * (0.5f + 0.5f * sin(animationProgress * Math.PI))).toInt()
        paint.alpha = alpha
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
    }
}
```

### Управление Жизненным Циклом

```kotlin
class LifecycleAwareAnimatedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val activeAnimators = mutableListOf<Animator>()

    fun startAnimation() {
        val animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    activeAnimators.remove(animation)
                }
            })
        }
        activeAnimators.add(animator)
        animator.start()
    }

    override fun onVisibilityChanged(changedView: View, visibility: Int) {
        super.onVisibilityChanged(changedView, visibility)
        if (visibility != VISIBLE) {
            activeAnimators.forEach { if (it.isStarted) it.pause() }
        } else {
            activeAnimators.forEach { if (it.isPaused) it.resume() }
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

**Обязательно:**
- Отменяйте анимации в `onDetachedFromWindow()`
- Кэшируйте `Paint` и другие объекты — не создавайте их в `onDraw()`
- Приостанавливайте анимации при `visibility != VISIBLE` или при уходе с экрана
- Для частых кадров / запуска не с главного потока используйте `postInvalidateOnAnimation()` для VSYNC-синхронизированной перерисовки

**Ошибки:**
- Забывают отменять анимации → утечки / лишняя работа в фоне
- Создают объекты в `onDraw()` → лишние GC-паузы
- Всегда вызывают только `invalidate()` для анимаций с фоновых потоков → возможны пропуски кадров и некорректная работа (нужен `postInvalidateOnAnimation()`)

---

## Answer (EN)

### Approach Comparison

| Approach | Use Case | Performance | Control |
|----------|----------|-------------|---------|
| **ValueAnimator** | Animate custom properties | High (VSYNC-synced, flexible) | Full control |
| **Property Animation** | Animate standard `View` properties | Excellent (hardware-accelerated transforms) | Simple |
| **`Canvas` Animation** | Complex mathematical graphics | Good | Requires math |

### ValueAnimator - Universal Approach

**Principle**: Interpolate values via `Choreographer`, sync to VSYNC, update state (often primitive-backed fields) and call `invalidate()`/`postInvalidateOnAnimation()` to redraw.

```kotlin
class AnimatedProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0f
        set(value) {
            field = value.coerceIn(0f, 100f)
            // For main-thread updates invalidate() is correct; for off-main use postInvalidateOnAnimation()
            invalidate()
        }

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    private var animator: ValueAnimator? = null

    fun setProgress(target: Float) {
        animator?.cancel()
        animator = ValueAnimator.ofFloat(progress, target).apply {
            duration = 500
            interpolator = DecelerateInterpolator()
            addUpdateListener { progress = it.animatedValue as Float }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        val filledWidth = width * (progress / 100f)
        canvas.drawRect(0f, 0f, filledWidth, height.toFloat(), paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
    }
}
```

### Property Animation - Standard Properties

**Principle**: Use `ViewPropertyAnimator` for chained animations, hardware-accelerated transforms (`alpha`, `translation`, `scale`, `rotation`).

```kotlin
class AnimatedButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = android.R.attr.buttonStyle
) : Button(context, attrs, defStyleAttr) {

    fun animateScale() {
        animate()
            .scaleX(1.2f)
            .scaleY(1.2f)
            .setDuration(200)
            .setInterpolator(OvershootInterpolator())
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

### Canvas Animation - Mathematical Graphics

**Principle**: Use trigonometry (`sin`, `cos`) and other math functions to compute animation parameters and manually invalidate the `View`.

```kotlin
import kotlin.math.min
import kotlin.math.sin

class AnimatedCircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var animationProgress = 0f
    private var animator: ValueAnimator? = null

    fun startAnimation() {
        animator?.cancel()
        animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 2000
            repeatCount = ValueAnimator.INFINITE
            repeatMode = ValueAnimator.RESTART
            addUpdateListener {
                animationProgress = it.animatedValue as Float
                // On the main thread invalidate() is fine; for VSYNC-aligned continuous animations prefer postInvalidateOnAnimation()
                postInvalidateOnAnimation()
            }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        val baseRadius = min(width, height) / 4f
        val radius = baseRadius * (0.5f + 0.5f * animationProgress)
        val alpha = (255 * (0.5f + 0.5f * sin(animationProgress * Math.PI))).toInt()
        paint.alpha = alpha
        canvas.drawCircle(width / 2f, height / 2f, radius, paint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        animator?.cancel()
    }
}
```

### Lifecycle Management

```kotlin
class LifecycleAwareAnimatedView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val activeAnimators = mutableListOf<Animator>()

    fun startAnimation() {
        val animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 1000
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    activeAnimators.remove(animation)
                }
            })
        }
        activeAnimators.add(animator)
        animator.start()
    }

    override fun onVisibilityChanged(changedView: View, visibility: Int) {
        super.onVisibilityChanged(changedView, visibility)
        if (visibility != VISIBLE) {
            activeAnimators.forEach { if (it.isStarted) it.pause() }
        } else {
            activeAnimators.forEach { if (it.isPaused) it.resume() }
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

**Required:**
- Cancel animations in `onDetachedFromWindow()`
- Cache `Paint` and other objects — don't create them in `onDraw()`
- Pause animations when `visibility != VISIBLE` or when the `View` goes off-screen
- For frequent frame updates / non-main-thread invalidation use `postInvalidateOnAnimation()` for VSYNC-synced redraw

**Mistakes:**
- Forgetting to cancel animations → leaks / unnecessary background work
- Creating objects in `onDraw()` → extra GC pauses
- Always using only `invalidate()` when invalidating from background threads → possible frame issues (use `postInvalidateOnAnimation()` instead)

---

## Дополнительные Вопросы (RU)

- Как создать сложные path-анимации с `PathInterpolator`?
- В чем разница производительности между `ValueAnimator` и `ObjectAnimator`?
- Как синхронизировать несколько анимаций (`AnimatorSet`)?
- Когда использовать `postInvalidateOnAnimation()` вместо `invalidate()`?
- Как сохранить состояние анимации при повороте экрана?

## Follow-ups (EN)

- How to create complex path animations with `PathInterpolator`?
- What is the performance difference between `ValueAnimator` and `ObjectAnimator`?
- How to synchronize multiple animations using `AnimatorSet`?
- When to use `postInvalidateOnAnimation()` instead of `invalidate()`?
- How to preserve animation state across configuration changes?

---

## Ссылки (RU)

- [Property Animation](https://developer.android.com/guide/topics/graphics/prop-animation)
- [Hardware Acceleration](https://developer.android.com/topic/performance/hardware-accel)

## References (EN)

- [Property Animation](https://developer.android.com/guide/topics/graphics/prop-animation)
- [Hardware Acceleration](https://developer.android.com/topic/performance/hardware-accel)

---

## Related Questions

### Prerequisites / Concepts

- [[c-android-surfaces]]

### Prerequisites (Easier)

- [[q-custom-view-lifecycle--android--medium]] - `View` lifecycle for proper animation cleanup / Жизненный цикл `View` для правильной очистки анимаций
- Custom `View` basics - onDraw() and rendering basics / Основы Custom `View` - `onDraw()` и базовый рендеринг

### Related (Same Level)

- [[q-canvas-drawing-optimization--android--hard]] - `Canvas` performance for smooth animations / Оптимизация `Canvas` для плавных анимаций
- Property Animation System - ObjectAnimator vs ViewPropertyAnimator / Система Property Animation - `ObjectAnimator` vs `ViewPropertyAnimator`
- Touch handling with animation - Gesture integration / Обработка касаний с анимациями - интеграция жестов

### Advanced (Harder)

- `Path` animations with `PathMeasure` - complex motion paths / `Path`-анимации с `PathMeasure` - сложные траектории
- Spring animations - physics-based motion (`SpringAnimation`, `FlingAnimation`) / Spring-анимации - физически правдоподобное движение (`SpringAnimation`, `FlingAnimation`)
- Coordinated animations - Transition API and Motion Layout / Координированные анимации - Transition API и Motion Layout

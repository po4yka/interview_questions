---\
id: android-478
title: Custom Drawable Implementation / Реализация Custom Drawable
aliases: [Custom Drawable Implementation, Реализация Custom Drawable]
topic: android
subtopics: [ui-graphics, ui-views]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views, q-canvas-drawing-optimization--android--hard, q-custom-view-accessibility--android--medium, q-custom-view-attributes--android--medium, q-custom-view-lifecycle--android--medium, q-custom-viewgroup-layout--android--hard]
created: 2025-10-21
updated: 2025-11-10
tags: [android/ui-graphics, android/ui-views, difficulty/medium]
sources: []

---\
# Вопрос (RU)
> Как реализовать Custom `Drawable` в Android?

# Question (EN)
> How to implement a Custom `Drawable` in Android?

---

## Ответ (RU)

### Что Такое Custom Drawable
Легковесный переиспользуемый графический примитив для отображения в нескольких `View`. Эффективнее кастомной `View` для простой неинтерактивной графики — не требует сложного жизненного цикла, управляется системой.

**Когда использовать `Drawable`**: неинтерактивная графика (иконки, фоны), переиспользование в разных `View`, простые формы и анимации.

**Когда использовать Custom `View`**: обработка касаний, сложный жизненный цикл, требования доступности, координация анимаций.

### Ключевые Методы

**draw(canvas: `Canvas`)** — основной метод отрисовки, вызывается системой.

**setBounds()** — устанавливает область рисования (координаты и размер).

**getOpacity()** — возвращает прозрачность (PixelFormat.OPAQUE/TRANSLUCENT/TRANSPARENT). В современных реализациях чаще используется для совместимости и оптимизаций, может игнорироваться рендерером.

**setAlpha(alpha: `Int`)** — устанавливает альфа-канал.

**setColorFilter(colorFilter: ColorFilter?)** — применяет цветовой фильтр для тонирования.

### Минимальная Реализация

```kotlin
class CircleDrawable : Drawable() {
    // ✅ Кэшируем Paint — создаем один раз
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    var color: Int
        get() = paint.color
        set(value) {
            paint.color = value
            invalidateSelf() // ✅ Запрос перерисовки
        }

    override fun draw(canvas: Canvas) {
        val radius = min(bounds.width(), bounds.height()) / 2f
        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            radius, paint
        )
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

**Критичные моменты**:
- `Paint` создается один раз, не в `draw()` — иначе аллокации на каждом фрейме
- `invalidateSelf()` запрашивает перерисовку при изменении состояния
- intrinsic размеры определяют дефолтные размеры для `wrap_content`

### Управление Состоянием

```kotlin
class StatefulDrawable : Drawable() {
    private val paint = Paint()
    private var isPressed = false

    override fun draw(canvas: Canvas) {
        // ✅ Выбор цвета по состоянию
        paint.color = if (isPressed) Color.RED else Color.BLUE
        canvas.drawRect(bounds, paint)
    }

    override fun setState(stateSet: IntArray): Boolean {
        val wasPressed = isPressed
        // Проверяем наличие стандартного флага "нажат" (state_pressed)
        isPressed = stateSet.any { it == android.R.attr.state_pressed }

        return if (wasPressed != isPressed) {
            invalidateSelf()
            true // Состояние изменилось, просим перерисовку
        } else {
            false
        }
    }

    override fun isStateful(): Boolean = true
}
```

**`setState()`** вызывается системой при изменении состояния `View` (pressed, focused, selected). Возвращайте `true` только если состояние реально изменилось — это триггерит перерисовку.

### Анимация

```kotlin
class PulsingDrawable : Drawable() {
    private val paint = Paint()
    private var scale = 1f
    private var animator: ValueAnimator? = null

    override fun draw(canvas: Canvas) {
        val radius = min(bounds.width(), bounds.height()) / 2f * scale
        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            radius, paint
        )
    }

    fun startAnimation() {
        if (animator?.isRunning == true) return

        animator = ValueAnimator.ofFloat(1f, 1.5f, 1f).apply {
            duration = 1000
            repeatCount = ValueAnimator.INFINITE
            addUpdateListener { valueAnimator ->
                scale = valueAnimator.animatedValue as Float
                invalidateSelf() // ✅ Перерисовка на каждом фрейме
            }
            start()
        }
    }

    fun stopAnimation() {
        animator?.cancel()
        animator = null
    }
}
```

### Лучшие Практики

1. Кэшируйте `Paint` — не создавайте в `draw()`, это аллокации на каждом фрейме.
2. Вызывайте `invalidateSelf()` при изменении внешнего вида.
3. Реализуйте intrinsic размеры для корректной работы с `wrap_content`.
4. Избегайте тяжелых вычислений в `draw()` — по возможности предварительно вычисляйте в `setBounds()`.
5. Правильно обрабатывайте `bounds` — система может их изменить.
6. Для анимаций управляйте жизненным циклом: останавливайте аниматоры, когда `Drawable` больше не используется, и учитывайте, что `Drawable` перерисовывается через свой `Callback` (например, `View`).

### Подводные Камни

- Аллокации в `draw()` — критично для производительности, вызывается каждый фрейм.
- Забытый `invalidateSelf()` — изменения не отрисуются.
- Игнорирование `bounds` — неверный размер/позиция.
- Неверный `getOpacity()` — влияет на оптимизацию рендеринга (хотя метод устаревший, лучше возвращать максимально корректное значение).
- Бесконтрольные анимации внутри `Drawable` — могут привести к утечкам и лишним перерисовкам; учитывайте `Callback` и жизненный цикл владельца.

## Answer (EN)

### What is Custom Drawable
Lightweight reusable graphic primitive for display in multiple `View`s. More efficient than Custom `View` for simple non-interactive graphics — no complex lifecycle needed, managed by the system.

**When to use `Drawable`**: non-interactive graphics (icons, backgrounds), reuse across `View`s, simple shapes and animations.

**When to use Custom `View`**: touch handling, complex lifecycle, accessibility requirements, animation coordination.

### Key Methods

**draw(canvas: `Canvas`)** — main drawing method called by the system.

**setBounds()** — sets drawing area (coordinates and size).

**getOpacity()** — returns transparency (`PixelFormat.OPAQUE/TRANSLUCENT/TRANSPARENT`). In modern rendering it is mostly used for compatibility/optimizations and may be ignored by the renderer.

**setAlpha(alpha: `Int`)** — sets alpha channel.

**setColorFilter(colorFilter: ColorFilter?)** — applies color filter for tinting.

### Minimal Implementation

```kotlin
class CircleDrawable : Drawable() {
    // ✅ Cache Paint — create once
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLUE
    }

    var color: Int
        get() = paint.color
        set(value) {
            paint.color = value
            invalidateSelf() // ✅ Request redraw
        }

    override fun draw(canvas: Canvas) {
        val radius = min(bounds.width(), bounds.height()) / 2f
        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            radius, paint
        )
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

**Critical points**:
- `Paint` created once, not in `draw()` — otherwise allocations every frame.
- `invalidateSelf()` requests redraw on appearance change.
- Intrinsic sizes define default dimensions for `wrap_content`.

### State Management

```kotlin
class StatefulDrawable : Drawable() {
    private val paint = Paint()
    private var isPressed = false

    override fun draw(canvas: Canvas) {
        // ✅ Select color by state
        paint.color = if (isPressed) Color.RED else Color.BLUE
        canvas.drawRect(bounds, paint)
    }

    override fun setState(stateSet: IntArray): Boolean {
        val wasPressed = isPressed
        // Check for standard "pressed" state flag (state_pressed)
        isPressed = stateSet.any { it == android.R.attr.state_pressed }

        return if (wasPressed != isPressed) {
            invalidateSelf()
            true // State changed, request redraw
        } else {
            false
        }
    }

    override fun isStateful(): Boolean = true
}
```

**`setState()`** is called by the system when `View` state changes (pressed, focused, selected). Return `true` only if state actually changed — this triggers redraw.

### Animation

```kotlin
class PulsingDrawable : Drawable() {
    private val paint = Paint()
    private var scale = 1f
    private var animator: ValueAnimator? = null

    override fun draw(canvas: Canvas) {
        val radius = min(bounds.width(), bounds.height()) / 2f * scale
        canvas.drawCircle(
            bounds.centerX().toFloat(),
            bounds.centerY().toFloat(),
            radius, paint
        )
    }

    fun startAnimation() {
        if (animator?.isRunning == true) return

        animator = ValueAnimator.ofFloat(1f, 1.5f, 1f).apply {
            duration = 1000
            repeatCount = ValueAnimator.INFINITE
            addUpdateListener { valueAnimator ->
                scale = valueAnimator.animatedValue as Float
                invalidateSelf() // ✅ Redraw every frame
            }
            start()
        }
    }

    fun stopAnimation() {
        animator?.cancel()
        animator = null
    }
}
```

### Best Practices

1. Cache `Paint` — don't create in `draw()`, causes allocations every frame.
2. `Call` `invalidateSelf()` when appearance changes.
3. Implement intrinsic sizes for correct `wrap_content` behavior.
4. Avoid heavy calculations in `draw()` — precompute in `setBounds()` when possible.
5. Handle `bounds` correctly — system may change them.
6. For animations, manage lifecycle: stop animators when the `Drawable` is no longer used, and remember that invalidation goes through its `Callback` (e.g., owning `View`).

### Pitfalls

- Allocations in `draw()` — critical for performance, called every frame.
- Forgot `invalidateSelf()` — changes won't render.
- Ignoring `bounds` — wrong size/position.
- Wrong `getOpacity()` — affects rendering optimization (even though deprecated, still better to return correct value).
- Uncontrolled animations inside `Drawable` — may cause leaks and unnecessary redraws; be aware of `Callback` and owner lifecycle.

---

## Дополнительные Вопросы (RU)

- Как реализовать составные `Drawable` с использованием `LayerDrawable` или `DrawableContainer`?
- Когда стоит использовать `VectorDrawable` вместо кастомного `Drawable` для масштабируемой графики?
- Как корректно обрабатывать размеры, независимые от плотности (dp), в кастомных `Drawable`?
- Каковы компромиссы по производительности между сложной логикой в `draw()` и кешированием в `Bitmap`?
- Как реализовать анимированные переходы состояния (аналог `StateListAnimator`)?

## Ссылки (RU)

- [[c-custom-views]] — паттерны реализации кастомных `View`.
- [[c-lifecycle]] — жизненный цикл Android-компонентов.
- [Drawable API Reference](https://developer.android.com/reference/android/graphics/drawable/Drawable)
- [Custom Drawables Guide](https://developer.android.com/develop/ui/views/graphics/drawables)

## Follow-ups

- How to implement compound drawables using LayerDrawable or DrawableContainer?
- When should you use VectorDrawable vs custom `Drawable` for scalable graphics?
- How to properly handle density-independent sizing in custom Drawables?
- What are performance trade-offs of complex `draw()` operations vs bitmap caching?
- How to implement animated state transitions (StateListAnimator equivalent)?

## References

- [[c-custom-views]] - Custom `View` implementation patterns
- [[c-lifecycle]] - Android component lifecycle
- [Drawable API Reference](https://developer.android.com/reference/android/graphics/drawable/Drawable)
- [Custom Drawables Guide](https://developer.android.com/develop/ui/views/graphics/drawables)

## Related Questions

### Расширенные Вопросы (RU)

- [[q-canvas-drawing-optimization--android--hard]] — техники оптимизации `Canvas`-отрисовки.
- [[q-custom-viewgroup-layout--android--hard]] — реализация кастомного `ViewGroup`.

### Advanced

- [[q-canvas-drawing-optimization--android--hard]] - Advanced `Canvas` optimization techniques
- [[q-custom-viewgroup-layout--android--hard]] - Custom `ViewGroup` implementation

---
id: android-378
title: Touch Event Handling Custom Views / Обработка касаний в пользовательских View
aliases:
- Touch Event Handling Custom Views
- Обработка касаний в пользовательских View
topic: android
subtopics:
- ui-state
- ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-state
- c-viewmodel
- q-custom-view-accessibility--android--medium
- q-custom-view-attributes--android--medium
- q-custom-view-lifecycle--android--medium
- q-modularization-patterns--android--hard
- q-what-does-itemdecoration-do--android--medium
created: 2025-10-15
updated: 2025-10-28
sources: []
tags:
- android/ui-state
- android/ui-views
- difficulty/medium
- gestures
- touch-events
- views
anki_cards:
- slug: android-378-0-ru
  language: ru
  anki_id: 1768420767340
  synced_at: '2026-01-14 23:59:27.345083'
- slug: android-378-0-en
  language: en
  anki_id: 1768420767314
  synced_at: '2026-01-14 23:59:27.319740'
---
# Вопрос (RU)
> Как обрабатывать события касания в пользовательских `View`? Объясните механизм диспетчеризации, разницу между `onTouchEvent()` и `onInterceptTouchEvent()`, и как реализовать пользовательские жесты.

# Question (EN)
> How do you handle touch events in custom views? Explain the touch event dispatch mechanism, the difference between `onTouchEvent()` and `onInterceptTouchEvent()`, and how to implement custom gestures.

---

## Ответ (RU)

### Механизм Диспетчеризации Событий

Android использует цепочку диспетчеризации касаний через активность и иерархию `View`:

```text
Activity.dispatchTouchEvent()
    ↓
Window / DecorView
    ↓
ViewGroup.dispatchTouchEvent()
    ↓
ViewGroup.onInterceptTouchEvent() → true? → ViewGroup.onTouchEvent()
    ↓ false
Child.dispatchTouchEvent()
    ↓
Child.onTouchEvent()
```

**Ключевые принципы:**
- Если `View` возвращает `true` на `ACTION_DOWN` (через `onTouchEvent()` или обработчик), система считает, что она хочет обрабатывать этот жест, и будет направлять ей последующие события того же жеста, пока родитель не перехватит или событие не будет отменено (`ACTION_CANCEL`).
- `onInterceptTouchEvent()` позволяет родительскому `ViewGroup` решать, отправлять ли события детям или перехватить их и обрабатывать самому. Решение обычно принимается начиная с `ACTION_DOWN` и может измениться на `MOVE` при выполнении условий (например, превышен `touchSlop`).
- Когда родитель начинает перехватывать уже идущий жест, дочерняя `View` получает `ACTION_CANCEL` и больше не будет получать события этого жеста.

### Базовая Обработка Касаний

```kotlin
class DraggableView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var lastX = 0f
    private var lastY = 0f
    private var isDragging = false

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                parent?.requestDisallowInterceptTouchEvent(true) // ✅ Запретить родителю перехватывать, пока обрабатываем жест
                // Возвращаем true, если хотим взять под контроль этот жест
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY
                if (dx != 0f || dy != 0f) {
                    isDragging = true
                }
                translationX += dx
                translationY += dy
                return true
            }

            MotionEvent.ACTION_UP -> {
                parent?.requestDisallowInterceptTouchEvent(false)
                if (!isDragging) {
                    // Обрабатываем как клик, только если фактически не было перетаскивания
                    performClick()
                }
                isDragging = false
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                parent?.requestDisallowInterceptTouchEvent(false)
                // Жест отменён, клик не вызываем
                isDragging = false
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }
}
```

### Использование `GestureDetector`

`GestureDetector` обрабатывает стандартные жесты: tap, double-tap, long-press, fling, scroll.

```kotlin
class GestureView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent): Boolean {
                // ✅ Должен вернуть true, чтобы получить последующие события для жестов
                return true
            }

            override fun onSingleTapUp(e: MotionEvent): Boolean {
                performClick()
                return true
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                // Обработка свайпа / флинга
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // ✅ Полагаться на GestureDetector; super вызываем только если он не обработал
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }
}
```

### Перехват Событий В `ViewGroup`

`onInterceptTouchEvent()` позволяет родителю перехватывать события до того, как они дойдут до детей:

```kotlin
class SwipeToDeleteLayout @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private var startX = 0f
    private var isSwiping = false

    private val touchSlop = ViewConfiguration.get(context).scaledTouchSlop

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                isSwiping = false
                // Не перехватываем сразу, дадим детям шанс
                return false
            }

            MotionEvent.ACTION_MOVE -> {
                val deltaX = event.x - startX
                if (kotlin.math.abs(deltaX) > touchSlop) {
                    // ✅ Начинаем перехватывать, как только понимаем, что это наш жест
                    isSwiping = true
                    return true
                }
            }

            MotionEvent.ACTION_CANCEL, MotionEvent.ACTION_UP -> {
                isSwiping = false
            }
        }
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_MOVE -> {
                if (isSwiping) {
                    translationX = event.x - startX
                    return true
                }
            }

            MotionEvent.ACTION_UP -> {
                if (isSwiping) {
                    if (kotlin.math.abs(translationX) > width / 2) {
                        animate().translationX(width.toFloat()).alpha(0f).start()
                    } else {
                        animate().translationX(0f).start()
                    }
                    isSwiping = false
                    return true
                }
            }

            MotionEvent.ACTION_CANCEL -> {
                if (isSwiping) {
                    animate().translationX(0f).start()
                    isSwiping = false
                    return true
                }
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Мультитач И `ScaleGestureDetector`

```kotlin
class ZoomableView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var scaleFactor = 1f

    private val scaleDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                scaleFactor = scaleFactor.coerceIn(0.5f, 3f) // ✅ Ограничить диапазон
                invalidate()
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Передаём все события детектору. Возвращаем true, если этот View всегда обрабатывает масштабирование.
        scaleDetector.onTouchEvent(event)
        return true
    }

    override fun onDraw(canvas: Canvas) {
        canvas.save()
        canvas.scale(scaleFactor, scaleFactor, width / 2f, height / 2f)
        // Рисование содержимого
        canvas.restore()
    }
}
```

### Отслеживание Скорости (`VelocityTracker`)

```kotlin
class FlingView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var velocityTracker: VelocityTracker? = null

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                if (velocityTracker == null) {
                    velocityTracker = VelocityTracker.obtain()
                } else {
                    velocityTracker?.clear()
                }
                velocityTracker?.addMovement(event)
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                velocityTracker?.addMovement(event)
                return true
            }

            MotionEvent.ACTION_UP -> {
                velocityTracker?.apply {
                    addMovement(event)
                    computeCurrentVelocity(1000) // px/sec
                    val velocityX = xVelocity

                    val vc = ViewConfiguration.get(context)
                    val minFlingVelocity = vc.scaledMinimumFlingVelocity

                    if (kotlin.math.abs(velocityX) > minFlingVelocity) {
                        startFlingAnimation(velocityX)
                    }

                    recycle()
                }
                velocityTracker = null
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                velocityTracker?.recycle()
                velocityTracker = null
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Лучшие Практики

1. Возвращайте `true` из `ACTION_DOWN`, когда `View` намерена обрабатывать жест — иначе система не закрепит за ней последующие события этого жеста.
2. Переопределяйте `performClick()` — для поддержки accessibility-сервисов и единообразной обработки кликов.
3. Обрабатывайте `ACTION_CANCEL` — родитель или система могут отменить жест (перехват, системный жест и т.п.).
4. Используйте `requestDisallowInterceptTouchEvent(true)` — когда дочернему `View` требуется эксклюзивный контроль над жестом (например, горизонтальный скролл внутри вертикального).
5. Корректно управляйте `VelocityTracker` — очищайте/рециклируйте при завершении/отмене жеста, избегайте утечек.
6. Предоставляйте тактильную обратную связь — `performHapticFeedback()` улучшает UX для важных действий.
7. Используйте `ViewConfiguration` — `scaledTouchSlop`, `scaledMinimumFlingVelocity` и т.п. для устойчивого поведения на разных устройствах.

---

## Answer (EN)

### Touch Event Dispatch Mechanism

Android uses a touch dispatch chain through the `Activity` and the `View` hierarchy:

```text
Activity.dispatchTouchEvent()
    ↓
Window / DecorView
    ↓
ViewGroup.dispatchTouchEvent()
    ↓
ViewGroup.onInterceptTouchEvent() → true? → ViewGroup.onTouchEvent()
    ↓ false
Child.dispatchTouchEvent()
    ↓
Child.onTouchEvent()
```

**Key Principles:**
- If a `View` returns `true` for `ACTION_DOWN` (via `onTouchEvent()` or a listener), the system treats it as interested in this gesture and will deliver subsequent events of that gesture to it, as long as the parent does not intercept and the gesture is not canceled (`ACTION_CANCEL`).
- `onInterceptTouchEvent()` allows a parent `ViewGroup` to decide whether to pass events to its children or intercept and handle them itself. The decision typically starts at `ACTION_DOWN` and may change on `MOVE` when movement exceeds certain thresholds (e.g., `touchSlop`).
- When a parent starts intercepting an ongoing gesture, the child receives `ACTION_CANCEL` and will no longer receive events for that gesture.

### Basic Touch Handling

```kotlin
class DraggableView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var lastX = 0f
    private var lastY = 0f
    private var isDragging = false

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                parent?.requestDisallowInterceptTouchEvent(true) // ✅ Ask parent not to intercept while handling this gesture
                // Return true if we intend to handle this gesture
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY
                if (dx != 0f || dy != 0f) {
                    isDragging = true
                }
                translationX += dx
                translationY += dy
                return true
            }

            MotionEvent.ACTION_UP -> {
                parent?.requestDisallowInterceptTouchEvent(false)
                if (!isDragging) {
                    // Treat as click only if there was effectively no drag
                    performClick()
                }
                isDragging = false
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                parent?.requestDisallowInterceptTouchEvent(false)
                // Gesture canceled; do not trigger click
                isDragging = false
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }
}
```

### Using `GestureDetector`

`GestureDetector` handles standard gestures: tap, double-tap, long-press, fling, scroll.

```kotlin
class GestureView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent): Boolean {
                // ✅ Must return true to receive further events for this gesture
                return true
            }

            override fun onSingleTapUp(e: MotionEvent): Boolean {
                performClick()
                return true
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                // Handle swipe / fling
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // ✅ Rely on GestureDetector; fall back to super only if it did not handle
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }
}
```

### Touch Interception in `ViewGroup`

`onInterceptTouchEvent()` allows a parent to intercept events before they reach children:

```kotlin
class SwipeToDeleteLayout @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private var startX = 0f
    private var isSwiping = false

    private val touchSlop = ViewConfiguration.get(context).scaledTouchSlop

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                isSwiping = false
                // Do not intercept immediately; let children try first
                return false
            }

            MotionEvent.ACTION_MOVE -> {
                val deltaX = event.x - startX
                if (kotlin.math.abs(deltaX) > touchSlop) {
                    // ✅ Start intercepting once we detect a horizontal swipe gesture
                    isSwiping = true
                    return true
                }
            }

            MotionEvent.ACTION_CANCEL, MotionEvent.ACTION_UP -> {
                isSwiping = false
            }
        }
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_MOVE -> {
                if (isSwiping) {
                    translationX = event.x - startX
                    return true
                }
            }

            MotionEvent.ACTION_UP -> {
                if (isSwiping) {
                    if (kotlin.math.abs(translationX) > width / 2) {
                        animate().translationX(width.toFloat()).alpha(0f).start()
                    } else {
                        animate().translationX(0f).start()
                    }
                    isSwiping = false
                    return true
                }
            }

            MotionEvent.ACTION_CANCEL -> {
                if (isSwiping) {
                    // Reset state when gesture is canceled
                    animate().translationX(0f).start()
                    isSwiping = false
                    return true
                }
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Multi-touch and `ScaleGestureDetector`

```kotlin
class ZoomableView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var scaleFactor = 1f

    private val scaleDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                scaleFactor = scaleFactor.coerceIn(0.5f, 3f) // ✅ Constrain range
                invalidate()
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Forward all events to the detector. Returning true means this View
        // consistently handles scaling gestures.
        scaleDetector.onTouchEvent(event)
        return true
    }

    override fun onDraw(canvas: Canvas) {
        canvas.save()
        canvas.scale(scaleFactor, scaleFactor, width / 2f, height / 2f)
        // Draw content
        canvas.restore()
    }
}
```

### Velocity Tracking

```kotlin
class FlingView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var velocityTracker: VelocityTracker? = null

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                if (velocityTracker == null) {
                    velocityTracker = VelocityTracker.obtain()
                } else {
                    velocityTracker?.clear()
                }
                velocityTracker?.addMovement(event)
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                velocityTracker?.addMovement(event)
                return true
            }

            MotionEvent.ACTION_UP -> {
                velocityTracker?.apply {
                    addMovement(event)
                    computeCurrentVelocity(1000) // px/sec
                    val velocityX = xVelocity

                    val vc = ViewConfiguration.get(context)
                    val minFlingVelocity = vc.scaledMinimumFlingVelocity

                    if (kotlin.math.abs(velocityX) > minFlingVelocity) {
                        startFlingAnimation(velocityX)
                    }

                    recycle()
                }
                velocityTracker = null
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                velocityTracker?.recycle()
                velocityTracker = null
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Best Practices

1. Return `true` from `ACTION_DOWN` when your `View` intends to handle the gesture — otherwise the system will not route subsequent events of that gesture to it.
2. Override `performClick()` — to support accessibility services and provide a single place for click behavior.
3. Handle `ACTION_CANCEL` — the parent or system (e.g., another gesture, window change) may cancel the gesture.
4. Use `requestDisallowInterceptTouchEvent(true)` — when a child needs exclusive control over a gesture (e.g., horizontal scroll inside a vertical parent).
5. Manage `VelocityTracker` correctly — clear/recycle on gesture end/cancel to avoid leaks and incorrect velocities.
6. Provide haptic feedback where appropriate — `performHapticFeedback()` can improve UX for critical interactions.
7. Use `ViewConfiguration` — `scaledTouchSlop`, `scaledMinimumFlingVelocity`, etc., for device-consistent gesture thresholds.

---

## Дополнительные Вопросы (RU)

- Как обрабатывать события касания во вложенных скроллируемых `View` (например, `RecyclerView` внутри `ScrollView`)?
- Как можно реализовать пользовательский жест pinch-to-zoom с поворотом?
- В чем разница между `actionMasked` и `action` в сценариях с мультитачем?
- Как избежать конфликтов обработки касаний между несколькими детекторами жестов?
- Как реализовать пользовательское определение свайпа от края, минимизируя конфликты с системными жестами?

## Follow-ups

- How do you handle touch events in nested scrollable views (e.g., `RecyclerView` inside ScrollView)?
- How would you implement a custom pinch-to-zoom with rotation gesture?
- What is the difference between `actionMasked` and `action` in multi-touch scenarios?
- How do you prevent touch event conflicts between multiple gesture detectors?
- How would you implement custom edge swipe detection while avoiding conflicts with system gestures?

## Ссылки (RU)

- [Документация по обработке касаний в Android](https://developer.android.com/develop/ui/views/touch-and-input/gestures)
- [Справка по `ViewConfiguration`](https://developer.android.com/reference/android/view/ViewConfiguration)
- [Справка по `MotionEvent`](https://developer.android.com/reference/android/view/MotionEvent)

## References

- [Android Touch Event Documentation](https://developer.android.com/develop/ui/views/touch-and-input/gestures)
- [ViewConfiguration Reference](https://developer.android.com/reference/android/view/ViewConfiguration)
- [MotionEvent Reference](https://developer.android.com/reference/android/view/MotionEvent)

## Связанные Вопросы (RU)

### Предпосылки / Концепты

- [[c-compose-state]]
- [[c-viewmodel]]

### Предпосылки (проще)

- [[q-recyclerview-sethasfixedsize--android--easy]] - Базовые концепции `View`
- [[q-viewmodel-pattern--android--easy]] - Паттерны слоя UI

### Похожие (того Же уровня)

- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - Инвалидация `View`
- [[q-what-does-itemdecoration-do--android--medium]] - Кастомный рисунок в `RecyclerView`

### Продвинутое (сложнее)

- [[q-compose-custom-layout--android--hard]] - Кастомные лейауты в Compose
- [[q-modularization-patterns--android--hard]] - Архитектура для крупных проектов

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-viewmodel]]

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Basic `View` concepts
- [[q-viewmodel-pattern--android--easy]] - UI layer patterns

### Related (Same Level)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View` invalidation
- [[q-what-does-itemdecoration-do--android--medium]] - Custom drawing in `RecyclerView`

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Custom layouts in Compose
- [[q-modularization-patterns--android--hard]] - Large-scale architecture

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
---

# Вопрос (RU)
> Как обрабатывать события касания в пользовательских `View`? Объясните механизм диспетчеризации, разницу между onTouchEvent() и onInterceptTouchEvent(), и как реализовать пользовательские жесты.

# Question (EN)
> How do you handle touch events in custom views? Explain the touch event dispatch mechanism, the difference between onTouchEvent() and onInterceptTouchEvent(), and how to implement custom gestures.

---

## Ответ (RU)

### Механизм Диспетчеризации Событий

Android использует трехэтапный механизм обработки касаний:

```
Activity.dispatchTouchEvent()
    ↓
ViewGroup.dispatchTouchEvent()
    ↓
ViewGroup.onInterceptTouchEvent() → true? → ViewGroup.onTouchEvent()
    ↓ false
Child.onTouchEvent()
```

**Ключевые принципы:**
- Если `View` возвращает `true` из `ACTION_DOWN`, она получит все последующие события
- `onInterceptTouchEvent()` позволяет родителю "украсть" события у детей
- `ACTION_CANCEL` отправляется, когда родитель перехватывает события

### Базовая Обработка Касаний

```kotlin
class DraggableView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var lastX = 0f
    private var lastY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                parent.requestDisallowInterceptTouchEvent(true) // ✅ Запретить родителю перехватывать
                return true // ✅ Обязательно вернуть true для получения последующих событий
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY
                translationX += dx
                translationY += dy
                return true
            }

            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                parent.requestDisallowInterceptTouchEvent(false)
                performClick() // ✅ Для доступности
                return true
            }
        }
        return super.onTouchEvent(event) // ❌ Если забыть return true в ACTION_DOWN
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }
}
```

### Использование GestureDetector

`GestureDetector` обрабатывает стандартные жесты: tap, double-tap, long-press, fling, scroll.

```kotlin
class GestureView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent) = true // ✅ Обязательно true

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
                // Обработка свайпа
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### Перехват Событий В `ViewGroup`

`onInterceptTouchEvent()` позволяет родителю перехватывать события:

```kotlin
class SwipeToDeleteLayout @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private var startX = 0f

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                return false // ✅ Не перехватывать, дать детям попробовать
            }

            MotionEvent.ACTION_MOVE -> {
                val deltaX = event.x - startX
                if (abs(deltaX) > touchSlop) { // ❌ Перехватить только при превышении порога
                    return true // Начать перехват
                }
            }
        }
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_MOVE -> {
                translationX = event.x - startX
                return true
            }
            MotionEvent.ACTION_UP -> {
                if (abs(translationX) > width / 2) {
                    animate().translationX(width.toFloat()).alpha(0f).start()
                } else {
                    animate().translationX(0f).start()
                }
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Мультитач И ScaleGestureDetector

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

### Отслеживание Скорости (VelocityTracker)

```kotlin
class FlingView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private val velocityTracker = VelocityTracker.obtain()

    override fun onTouchEvent(event: MotionEvent): Boolean {
        velocityTracker.addMovement(event) // ✅ Добавить движение

        when (event.action) {
            MotionEvent.ACTION_DOWN -> return true
            MotionEvent.ACTION_UP -> {
                velocityTracker.computeCurrentVelocity(1000) // px/sec
                val velocityX = velocityTracker.xVelocity

                if (abs(velocityX) > minFlingVelocity) {
                    startFlingAnimation(velocityX)
                }

                velocityTracker.clear() // ✅ Очистить для следующего жеста
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        velocityTracker.recycle() // ✅ Освободить ресурсы
    }
}
```

### Лучшие Практики

1. **Возвращайте true из ACTION_DOWN** — иначе не получите последующие события
2. **Переопределяйте performClick()** — для accessibility services
3. **Обрабатывайте ACTION_CANCEL** — родитель может отменить жест
4. **Используйте requestDisallowInterceptTouchEvent(true)** — когда нужен эксклюзивный контроль
5. **Освобождайте VelocityTracker** — вызывайте recycle() в onDetachedFromWindow()
6. **Предоставляйте тактильную обратную связь** — performHapticFeedback() для улучшения UX
7. **Проверяйте границы** — используйте ViewConfiguration.get(context).scaledTouchSlop

---

## Answer (EN)

### Touch Event Dispatch Mechanism

Android uses a three-stage touch handling mechanism:

```
Activity.dispatchTouchEvent()
    ↓
ViewGroup.dispatchTouchEvent()
    ↓
ViewGroup.onInterceptTouchEvent() → true? → ViewGroup.onTouchEvent()
    ↓ false
Child.onTouchEvent()
```

**Key Principles:**
- If a `View` returns `true` from `ACTION_DOWN`, it will receive all subsequent events
- `onInterceptTouchEvent()` allows parent to "steal" events from children
- `ACTION_CANCEL` is sent when parent intercepts events

### Basic Touch Handling

```kotlin
class DraggableView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private var lastX = 0f
    private var lastY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                parent.requestDisallowInterceptTouchEvent(true) // ✅ Prevent parent interception
                return true // ✅ Must return true to receive subsequent events
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY
                translationX += dx
                translationY += dy
                return true
            }

            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                parent.requestDisallowInterceptTouchEvent(false)
                performClick() // ✅ For accessibility
                return true
            }
        }
        return super.onTouchEvent(event) // ❌ If you forget to return true in ACTION_DOWN
    }

    override fun performClick(): Boolean {
        super.performClick()
        return true
    }
}
```

### Using GestureDetector

`GestureDetector` handles standard gestures: tap, double-tap, long-press, fling, scroll.

```kotlin
class GestureView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent) = true // ✅ Must return true

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
                // Handle swipe
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### Touch Interception in `ViewGroup`

`onInterceptTouchEvent()` allows parent to intercept events:

```kotlin
class SwipeToDeleteLayout @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private var startX = 0f

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                return false // ✅ Don't intercept, let children try first
            }

            MotionEvent.ACTION_MOVE -> {
                val deltaX = event.x - startX
                if (abs(deltaX) > touchSlop) { // ✅ Intercept only when threshold exceeded
                    return true // Start intercepting
                }
            }
        }
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_MOVE -> {
                translationX = event.x - startX
                return true
            }
            MotionEvent.ACTION_UP -> {
                if (abs(translationX) > width / 2) {
                    animate().translationX(width.toFloat()).alpha(0f).start()
                } else {
                    animate().translationX(0f).start()
                }
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Multi-touch and ScaleGestureDetector

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

    private val velocityTracker = VelocityTracker.obtain()

    override fun onTouchEvent(event: MotionEvent): Boolean {
        velocityTracker.addMovement(event) // ✅ Add movement

        when (event.action) {
            MotionEvent.ACTION_DOWN -> return true
            MotionEvent.ACTION_UP -> {
                velocityTracker.computeCurrentVelocity(1000) // px/sec
                val velocityX = velocityTracker.xVelocity

                if (abs(velocityX) > minFlingVelocity) {
                    startFlingAnimation(velocityX)
                }

                velocityTracker.clear() // ✅ Clear for next gesture
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        velocityTracker.recycle() // ✅ Release resources
    }
}
```

### Best Practices

1. **Return true from ACTION_DOWN** — or you won't receive subsequent events
2. **Override performClick()** — for accessibility services
3. **Handle ACTION_CANCEL** — parent may cancel gesture
4. **Use requestDisallowInterceptTouchEvent(true)** — when you need exclusive control
5. **Recycle VelocityTracker** — call recycle() in onDetachedFromWindow()
6. **Provide haptic feedback** — performHapticFeedback() improves UX
7. **Respect boundaries** — use ViewConfiguration.get(context).scaledTouchSlop

---

## Follow-ups

- How do you handle touch events in nested scrollable views (e.g., `RecyclerView` inside `ScrollView`)?
- How would you implement a custom pinch-to-zoom with rotation gesture?
- What is the difference between `actionMasked` and `action` in multi-touch scenarios?
- How do you prevent touch event conflicts between multiple gesture detectors?
- How would you implement custom edge swipe detection while avoiding conflicts with system gestures?

## References

- [Android Touch Event Documentation](https://developer.android.com/develop/ui/views/touch-and-input/gestures)
- [ViewConfiguration Reference](https://developer.android.com/reference/android/view/ViewConfiguration)
- [MotionEvent Reference](https://developer.android.com/reference/android/view/MotionEvent)

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

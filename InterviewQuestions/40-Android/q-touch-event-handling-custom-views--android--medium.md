---
id: 20251016-174833
title: "Touch Event Handling Custom Views"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-material3-motion-transitions--material-design--medium, q-what-does-itemdecoration-do--android--medium, q-modularization-patterns--android--hard]
created: 2025-10-15
tags: [views, touch-events, gestures, android-framework, difficulty/medium]
---
# Touch Event Handling in Custom Views

# Question (EN)
> How do you handle touch events in custom views? Explain the touch event dispatch mechanism, the difference between onTouchEvent() and onInterceptTouchEvent(), and how to implement custom gestures.

# Вопрос (RU)
> Как обрабатывать события касания в пользовательских view? Объясните механизм диспетчеризации событий касания, разницу между onTouchEvent() и onInterceptTouchEvent(), и как реализовать пользовательские жесты.

---

## Answer (EN)

Understanding **touch event handling** is essential for creating interactive custom views. The Android touch system is complex but powerful, allowing you to implement any gesture or interaction pattern.

### Touch Event Dispatch Flow

```
Activity.dispatchTouchEvent()
    ↓
ViewGroup.dispatchTouchEvent()
    ↓
ViewGroup.onInterceptTouchEvent() → true? → ViewGroup.onTouchEvent()
    ↓ false                                        ↓
Child.dispatchTouchEvent()                    consumed?
    ↓                                              ↓
Child.onTouchEvent()                          Return true/false
    ↓
consumed?
    ↓
Return true/false
```

---

### 1. Basic Touch Event Handling

**MotionEvent actions:**
- `ACTION_DOWN` - Touch starts
- `ACTION_MOVE` - Touch moves
- `ACTION_UP` - Touch ends
- `ACTION_CANCEL` - Touch cancelled (by parent)
- `ACTION_POINTER_DOWN/UP` - Multi-touch

```kotlin
class SimpleTouchView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var touchX = 0f
    private var touchY = 0f
    private val paint = Paint().apply {
        color = Color.RED
        style = Paint.Style.FILL
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Touch started
                touchX = event.x
                touchY = event.y
                Log.d("Touch", "DOWN at ($touchX, $touchY)")
                invalidate()
                return true // Consume event
            }

            MotionEvent.ACTION_MOVE -> {
                // Touch moved
                touchX = event.x
                touchY = event.y
                Log.d("Touch", "MOVE to ($touchX, $touchY)")
                invalidate()
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Touch ended
                Log.d("Touch", "UP at (${event.x}, ${event.y})")
                performClick() // Accessibility
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                // Touch cancelled by parent
                Log.d("Touch", "CANCEL")
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        super.performClick()
        // Handle click action
        return true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Draw circle at touch position
        canvas.drawCircle(touchX, touchY, 50f, paint)
    }
}
```

**Key points:**
- Return `true` to consume the event (continue receiving events)
- Return `false` to pass event to parent
- Must handle ACTION_DOWN to receive subsequent events
- Override performClick() for accessibility

---

### 2. Draggable View

Implement a view that can be dragged around.

```kotlin
class DraggableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var offsetX = 0f
    private var offsetY = 0f
    private var isDragging = false

    private val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Start dragging
                offsetX = event.x
                offsetY = event.y
                isDragging = true
                parent.requestDisallowInterceptTouchEvent(true) // Prevent parent from stealing
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                if (isDragging) {
                    // Calculate movement delta
                    val dx = event.x - offsetX
                    val dy = event.y - offsetY

                    // Move view
                    translationX += dx
                    translationY += dy

                    return true
                }
            }

            MotionEvent.ACTION_UP,
            MotionEvent.ACTION_CANCEL -> {
                isDragging = false
                parent.requestDisallowInterceptTouchEvent(false)
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawCircle(
            width / 2f,
            height / 2f,
            min(width, height) / 2f,
            paint
        )
    }
}
```

---

### 3. Custom Gesture: Swipe Detection

Detect left/right swipes manually.

```kotlin
class SwipeDetectorView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var startX = 0f
    private var startY = 0f
    private var startTime = 0L

    private val minSwipeDistance = 100 // dp
    private val maxSwipeTime = 500 // ms
    private val maxYDelta = 100 // dp (vertical tolerance)

    var onSwipeLeft: (() -> Unit)? = null
    var onSwipeRight: (() -> Unit)? = null

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                startY = event.y
                startTime = System.currentTimeMillis()
                return true
            }

            MotionEvent.ACTION_UP -> {
                val endX = event.x
                val endY = event.y
                val endTime = System.currentTimeMillis()

                val deltaX = endX - startX
                val deltaY = endY - startY
                val duration = endTime - startTime

                // Check if it's a swipe
                if (duration < maxSwipeTime &&
                    abs(deltaX) > minSwipeDistance.dpToPx() &&
                    abs(deltaY) < maxYDelta.dpToPx()
                ) {
                    if (deltaX > 0) {
                        onSwipeRight?.invoke()
                        Log.d("Gesture", "Swipe RIGHT")
                    } else {
                        onSwipeLeft?.invoke()
                        Log.d("Gesture", "Swipe LEFT")
                    }
                    return true
                }
            }
        }

        return super.onTouchEvent(event)
    }

    private fun Int.dpToPx(): Float =
        this * context.resources.displayMetrics.density
}
```

**Usage:**
```kotlin
swipeView.onSwipeLeft = {
    Toast.makeText(context, "Swiped Left!", Toast.LENGTH_SHORT).show()
}

swipeView.onSwipeRight = {
    Toast.makeText(context, "Swiped Right!", Toast.LENGTH_SHORT).show()
}
```

---

### 4. GestureDetector for Common Gestures

Use **GestureDetector** for standard gestures.

```kotlin
class GestureDemoView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureListener = object : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean {
            // Return true to indicate we want to handle gestures
            return true
        }

        override fun onSingleTapUp(e: MotionEvent): Boolean {
            Log.d("Gesture", "Single tap at (${e.x}, ${e.y})")
            performClick()
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            Log.d("Gesture", "Double tap")
            // Handle double tap
            return true
        }

        override fun onLongPress(e: MotionEvent) {
            Log.d("Gesture", "Long press")
            performLongClick()
        }

        override fun onFling(
            e1: MotionEvent?,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            Log.d("Gesture", "Fling with velocity ($velocityX, $velocityY)")
            return true
        }

        override fun onScroll(
            e1: MotionEvent?,
            e2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            Log.d("Gesture", "Scroll by ($distanceX, $distanceY)")
            return true
        }
    }

    private val gestureDetector = GestureDetector(context, gestureListener)

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Delegate to gesture detector
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

---

### 5. ScaleGestureDetector for Pinch-to-Zoom

```kotlin
class ZoomableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var scaleFactor = 1f
    private var focusX = 0f
    private var focusY = 0f

    private val scaleListener = object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
        override fun onScale(detector: ScaleGestureDetector): Boolean {
            scaleFactor *= detector.scaleFactor

            // Limit scale range
            scaleFactor = scaleFactor.coerceIn(0.5f, 3f)

            // Get focus point
            focusX = detector.focusX
            focusY = detector.focusY

            invalidate()
            return true
        }
    }

    private val scaleDetector = ScaleGestureDetector(context, scaleListener)

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleDetector.onTouchEvent(event)
        return true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        canvas.save()

        // Scale around focus point
        canvas.scale(scaleFactor, scaleFactor, focusX, focusY)

        // Draw content
        paint.color = Color.BLUE
        canvas.drawRect(100f, 100f, 300f, 300f, paint)

        canvas.restore()
    }
}
```

---

### 6. ViewGroup Touch Interception

**onInterceptTouchEvent()** allows parent to steal events from children.

```kotlin
class SwipeToDeleteLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private var startX = 0f
    private var intercepting = false

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                intercepting = false
                return false // Don't intercept yet
            }

            MotionEvent.ACTION_MOVE -> {
                val deltaX = event.x - startX

                // Intercept if horizontal swipe detected
                if (!intercepting && abs(deltaX) > 50) {
                    intercepting = true
                    return true // Start intercepting
                }
            }

            MotionEvent.ACTION_UP,
            MotionEvent.ACTION_CANCEL -> {
                intercepting = false
            }
        }

        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Handle swipe to delete
        when (event.action) {
            MotionEvent.ACTION_MOVE -> {
                translationX = event.x - startX
                return true
            }

            MotionEvent.ACTION_UP -> {
                if (abs(translationX) > width / 2) {
                    // Swipe threshold reached - delete
                    animate()
                        .translationX(width.toFloat())
                        .alpha(0f)
                        .setDuration(200)
                        .withEndAction {
                            visibility = GONE
                        }
                        .start()
                } else {
                    // Return to original position
                    animate()
                        .translationX(0f)
                        .setDuration(200)
                        .start()
                }
                return true
            }
        }

        return super.onTouchEvent(event)
    }
}
```

---

### 7. Multi-Touch Handling

Handle multiple simultaneous touches.

```kotlin
class MultiTouchView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val activePointers = mutableMapOf<Int, PointF>()
    private val paint = Paint().apply {
        style = Paint.Style.FILL
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                // First pointer down
                val pointerId = event.getPointerId(0)
                activePointers[pointerId] = PointF(event.x, event.y)
                invalidate()
                return true
            }

            MotionEvent.ACTION_POINTER_DOWN -> {
                // Additional pointer down
                val pointerIndex = event.actionIndex
                val pointerId = event.getPointerId(pointerIndex)
                activePointers[pointerId] = PointF(
                    event.getX(pointerIndex),
                    event.getY(pointerIndex)
                )
                invalidate()
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                // Update all active pointers
                for (i in 0 until event.pointerCount) {
                    val pointerId = event.getPointerId(i)
                    activePointers[pointerId] = PointF(
                        event.getX(i),
                        event.getY(i)
                    )
                }
                invalidate()
                return true
            }

            MotionEvent.ACTION_POINTER_UP -> {
                // One pointer released
                val pointerIndex = event.actionIndex
                val pointerId = event.getPointerId(pointerIndex)
                activePointers.remove(pointerId)
                invalidate()
                return true
            }

            MotionEvent.ACTION_UP,
            MotionEvent.ACTION_CANCEL -> {
                // All pointers released
                activePointers.clear()
                invalidate()
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Draw circle for each active pointer
        val colors = listOf(Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW, Color.MAGENTA)

        activePointers.entries.forEachIndexed { index, (_, point) ->
            paint.color = colors[index % colors.size]
            canvas.drawCircle(point.x, point.y, 50f, paint)
        }
    }
}
```

---

### 8. Velocity Tracking

Track touch velocity for fling gestures.

```kotlin
class FlingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val velocityTracker = VelocityTracker.obtain()
    private var positionX = 0f
    private var positionY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Add movement to tracker
        velocityTracker.addMovement(event)

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                positionX = event.x
                positionY = event.y
                invalidate()
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Compute velocity
                velocityTracker.computeCurrentVelocity(1000) // pixels per second

                val velocityX = velocityTracker.xVelocity
                val velocityY = velocityTracker.yVelocity

                Log.d("Velocity", "X: $velocityX px/s, Y: $velocityY px/s")

                // Start fling animation based on velocity
                if (abs(velocityX) > 1000) {
                    startFlingAnimation(velocityX, velocityY)
                }

                velocityTracker.clear()
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    private fun startFlingAnimation(velocityX: Float, velocityY: Float) {
        // Animate with deceleration
        animate()
            .translationXBy(velocityX / 2)
            .translationYBy(velocityY / 2)
            .setDuration(500)
            .setInterpolator(DecelerateInterpolator())
            .start()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        velocityTracker.recycle()
    }
}
```

---

### 9. Touch Feedback

Provide visual feedback for touch interactions.

```kotlin
class TouchFeedbackView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var isPressed = false
    private val normalPaint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    private val pressedPaint = Paint().apply {
        color = Color.DARK_GRAY
        style = Paint.Style.FILL
    }

    init {
        // Enable sound effects and haptic feedback
        isSoundEffectsEnabled = true
        isHapticFeedbackEnabled = true

        // Add ripple effect (Material Design)
        foreground = context.getDrawable(R.drawable.ripple)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                isPressed = true
                performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY)
                invalidate()
                return true
            }

            MotionEvent.ACTION_UP -> {
                isPressed = false
                playSoundEffect(SoundEffectConstants.CLICK)
                performClick()
                invalidate()
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                isPressed = false
                invalidate()
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        super.performClick()
        // Handle click
        return true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val paint = if (isPressed) pressedPaint else normalPaint

        canvas.drawRoundRect(
            0f, 0f, width.toFloat(), height.toFloat(),
            20f, 20f,
            paint
        )
    }
}
```

**ripple.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android"
    android:color="?attr/colorControlHighlight">
    <item android:id="@android:id/mask">
        <shape android:shape="rectangle">
            <solid android:color="#FFFFFF" />
            <corners android:radius="20dp" />
        </shape>
    </item>
</ripple>
```

---

### 10. Best Practices

**1. Return true from ACTION_DOWN to receive subsequent events**
```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> return true //  Important!
        // ...
    }
    return super.onTouchEvent(event)
}
```

**2. Override performClick() for accessibility**
```kotlin
override fun performClick(): Boolean {
    super.performClick()
    // Perform action
    return true
}
```

**3. Request parent not to intercept**
```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            parent.requestDisallowInterceptTouchEvent(true)
        }
    }
    return true
}
```

**4. Handle ACTION_CANCEL**
```kotlin
MotionEvent.ACTION_UP,
MotionEvent.ACTION_CANCEL -> {
    // Reset state
    isDragging = false
}
```

**5. Recycle VelocityTracker**
```kotlin
override fun onDetachedFromWindow() {
    super.onDetachedFromWindow()
    velocityTracker.recycle()
}
```

---

### Summary

**Touch event flow:**
1. `dispatchTouchEvent()` - Entry point
2. `onInterceptTouchEvent()` - Parent can steal events
3. `onTouchEvent()` - Handle events

**Key APIs:**
- `GestureDetector` - Standard gestures
- `ScaleGestureDetector` - Pinch-to-zoom
- `VelocityTracker` - Track velocity
- `MotionEvent` - Raw touch data

**Best practices:**
- Return true from ACTION_DOWN
- Override performClick()
- Handle ACTION_CANCEL
- Use requestDisallowInterceptTouchEvent()
- Provide visual/haptic feedback

---

## Ответ (RU)

Понимание **обработки событий касания** необходимо для создания интерактивных пользовательских представлений (custom views). Система обработки касаний в Android сложна, но мощна, и позволяет реализовать любой жест или паттерн взаимодействия.

### Поток диспетчеризации событий касания

```
Activity.dispatchTouchEvent()
    ↓
ViewGroup.dispatchTouchEvent()
    ↓
ViewGroup.onInterceptTouchEvent() → true? → ViewGroup.onTouchEvent()
    ↓ false                                        ↓
Child.dispatchTouchEvent()                    потреблено?
    ↓                                              ↓
Child.onTouchEvent()                          Вернуть true/false
    ↓
потреблено?
    ↓
Вернуть true/false
```

---

### 1. Базовая обработка событий касания

**Действия MotionEvent:**
- `ACTION_DOWN` - Касание началось
- `ACTION_MOVE` - Касание перемещается
- `ACTION_UP` - Касание завершилось
- `ACTION_CANCEL` - Касание отменено (родителем)
- `ACTION_POINTER_DOWN/UP` - Мультитач

```kotlin
class SimpleTouchView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var touchX = 0f
    private var touchY = 0f
    private val paint = Paint().apply {
        color = Color.RED
        style = Paint.Style.FILL
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Касание началось
                touchX = event.x
                touchY = event.y
                Log.d("Touch", "DOWN в ($touchX, $touchY)")
                invalidate()
                return true // Потребить событие
            }

            MotionEvent.ACTION_MOVE -> {
                // Касание переместилось
                touchX = event.x
                touchY = event.y
                Log.d("Touch", "MOVE в ($touchX, $touchY)")
                invalidate()
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Касание завершилось
                Log.d("Touch", "UP в (${event.x}, ${event.y})")
                performClick() // Доступность
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                // Касание отменено родителем
                Log.d("Touch", "CANCEL")
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        super.performClick()
        // Обработка действия клика
        return true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Рисование круга в месте касания
        canvas.drawCircle(touchX, touchY, 50f, paint)
    }
}
```

**Ключевые моменты:**
- Возвращайте `true`, чтобы потребить событие (и продолжать получать события)
- Возвращайте `false`, чтобы передать событие родителю
- Необходимо обработать `ACTION_DOWN`, чтобы получать последующие события
- Переопределяйте `performClick()` для доступности

---

### 2. Перетаскиваемое View

Реализуем view, которое можно перетаскивать.

```kotlin
class DraggableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var offsetX = 0f
    private var offsetY = 0f
    private var isDragging = false

    private val paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Начало перетаскивания
                offsetX = event.x
                offsetY = event.y
                isDragging = true
                parent.requestDisallowInterceptTouchEvent(true) // Запретить родителю перехватывать
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                if (isDragging) {
                    // Вычисление дельты перемещения
                    val dx = event.x - offsetX
                    val dy = event.y - offsetY

                    // Перемещение view
                    translationX += dx
                    translationY += dy

                    return true
                }
            }

            MotionEvent.ACTION_UP,
            MotionEvent.ACTION_CANCEL -> {
                isDragging = false
                parent.requestDisallowInterceptTouchEvent(false)
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawCircle(
            width / 2f,
            height / 2f,
            min(width, height) / 2f,
            paint
        )
    }
}
```

---

### 3. Пользовательский жест: определение свайпа

Определяем свайпы влево/вправо вручную.

```kotlin
class SwipeDetectorView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var startX = 0f
    private var startY = 0f
    private var startTime = 0L

    private val minSwipeDistance = 100 // dp
    private val maxSwipeTime = 500 // ms
    private val maxYDelta = 100 // dp (вертикальный допуск)

    var onSwipeLeft: (() -> Unit)? = null
    var onSwipeRight: (() -> Unit)? = null

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                startY = event.y
                startTime = System.currentTimeMillis()
                return true
            }

            MotionEvent.ACTION_UP -> {
                val endX = event.x
                val endY = event.y
                val endTime = System.currentTimeMillis()

                val deltaX = endX - startX
                val deltaY = endY - startY
                val duration = endTime - startTime

                // Проверяем, является ли это свайпом
                if (duration < maxSwipeTime &&
                    abs(deltaX) > minSwipeDistance.dpToPx() &&
                    abs(deltaY) < maxYDelta.dpToPx()
                ) {
                    if (deltaX > 0) {
                        onSwipeRight?.invoke()
                        Log.d("Gesture", "Свайп ВПРАВО")
                    } else {
                        onSwipeLeft?.invoke()
                        Log.d("Gesture", "Свайп ВЛЕВО")
                    }
                    return true
                }
            }
        }

        return super.onTouchEvent(event)
    }

    private fun Int.dpToPx(): Float =
        this * context.resources.displayMetrics.density
}
```

---

### 4. GestureDetector для стандартных жестов

Используйте **GestureDetector** для стандартных жестов.

```kotlin
class GestureDemoView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureListener = object : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean {
            // Возвращаем true, чтобы указать, что мы хотим обрабатывать жесты
            return true
        }

        override fun onSingleTapUp(e: MotionEvent): Boolean {
            Log.d("Gesture", "Одиночный тап в (${e.x}, ${e.y})")
            performClick()
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            Log.d("Gesture", "Двойной тап")
            // Обработка двойного тапа
            return true
        }

        override fun onLongPress(e: MotionEvent) {
            Log.d("Gesture", "Долгое нажатие")
            performLongClick()
        }

        override fun onFling(
            e1: MotionEvent?,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            Log.d("Gesture", "Fling со скоростью ($velocityX, $velocityY)")
            return true
        }

        override fun onScroll(
            e1: MotionEvent?,
            e2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            Log.d("Gesture", "Scroll на ($distanceX, $distanceY)")
            return true
        }
    }

    private val gestureDetector = GestureDetector(context, gestureListener)

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Делегируем детектору жестов
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

---

### 5. ScaleGestureDetector для масштабирования (Pinch-to-Zoom)

```kotlin
class ZoomableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var scaleFactor = 1f
    private var focusX = 0f
    private var focusY = 0f

    private val scaleListener = object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
        override fun onScale(detector: ScaleGestureDetector): Boolean {
            scaleFactor *= detector.scaleFactor

            // Ограничение диапазона масштабирования
            scaleFactor = scaleFactor.coerceIn(0.5f, 3f)

            // Получение точки фокуса
            focusX = detector.focusX
            focusY = detector.focusY

            invalidate()
            return true
        }
    }

    private val scaleDetector = ScaleGestureDetector(context, scaleListener)

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleDetector.onTouchEvent(event)
        return true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        canvas.save()

        // Масштабирование вокруг точки фокуса
        canvas.scale(scaleFactor, scaleFactor, focusX, focusY)

        // Рисование содержимого
        paint.color = Color.BLUE
        canvas.drawRect(100f, 100f, 300f, 300f, paint)

        canvas.restore()
    }
}
```

---

### 6. Перехват касаний в ViewGroup

**onInterceptTouchEvent()** позволяет родителю "украсть" события у дочерних элементов.

```kotlin
class SwipeToDeleteLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private var startX = 0f
    private var intercepting = false

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                intercepting = false
                return false // Пока не перехватывать
            }

            MotionEvent.ACTION_MOVE -> {
                val deltaX = event.x - startX

                // Перехватываем, если обнаружен горизонтальный свайп
                if (!intercepting && abs(deltaX) > 50) {
                    intercepting = true
                    return true // Начать перехват
                }
            }

            MotionEvent.ACTION_UP,
            MotionEvent.ACTION_CANCEL -> {
                intercepting = false
            }
        }

        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Обработка свайпа для удаления
        when (event.action) {
            MotionEvent.ACTION_MOVE -> {
                translationX = event.x - startX
                return true
            }

            MotionEvent.ACTION_UP -> {
                if (abs(translationX) > width / 2) {
                    // Порог свайпа достигнут - удаляем
                    animate()
                        .translationX(width.toFloat())
                        .alpha(0f)
                        .setDuration(200)
                        .withEndAction {
                            visibility = GONE
                        }
                        .start()
                } else {
                    // Возвращаемся в исходное положение
                    animate()
                        .translationX(0f)
                        .setDuration(200)
                        .start()
                }
                return true
            }
        }

        return super.onTouchEvent(event)
    }
}
```

---

### 7. Обработка мультитача

Обработка нескольких одновременных касаний.

```kotlin
class MultiTouchView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val activePointers = mutableMapOf<Int, PointF>()
    private val paint = Paint().apply {
        style = Paint.Style.FILL
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                // Первое касание
                val pointerId = event.getPointerId(0)
                activePointers[pointerId] = PointF(event.x, event.y)
                invalidate()
                return true
            }

            MotionEvent.ACTION_POINTER_DOWN -> {
                // Дополнительное касание
                val pointerIndex = event.actionIndex
                val pointerId = event.getPointerId(pointerIndex)
                activePointers[pointerId] = PointF(
                    event.getX(pointerIndex),
                    event.getY(pointerIndex)
                )
                invalidate()
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                // Обновление всех активных касаний
                for (i in 0 until event.pointerCount) {
                    val pointerId = event.getPointerId(i)
                    activePointers[pointerId] = PointF(
                        event.getX(i),
                        event.getY(i)
                    )
                }
                invalidate()
                return true
            }

            MotionEvent.ACTION_POINTER_UP -> {
                // Одно касание отпущено
                val pointerIndex = event.actionIndex
                val pointerId = event.getPointerId(pointerIndex)
                activePointers.remove(pointerId)
                invalidate()
                return true
            }

            MotionEvent.ACTION_UP,
            MotionEvent.ACTION_CANCEL -> {
                // Все касания отпущены
                activePointers.clear()
                invalidate()
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Рисование круга для каждого активного касания
        val colors = listOf(Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW, Color.MAGENTA)

        activePointers.entries.forEachIndexed { index, (_, point) ->
            paint.color = colors[index % colors.size]
            canvas.drawCircle(point.x, point.y, 50f, paint)
        }
    }
}
```

---

### 8. Отслеживание скорости (Velocity Tracking)

Отслеживание скорости касания для жестов броска (fling).

```kotlin
class FlingView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val velocityTracker = VelocityTracker.obtain()
    private var positionX = 0f
    private var positionY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Добавление движения в трекер
        velocityTracker.addMovement(event)

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                positionX = event.x
                positionY = event.y
                invalidate()
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Вычисление скорости
                velocityTracker.computeCurrentVelocity(1000) // пикселей в секунду

                val velocityX = velocityTracker.xVelocity
                val velocityY = velocityTracker.yVelocity

                Log.d("Velocity", "X: $velocityX px/s, Y: $velocityY px/s")

                // Запуск анимации броска на основе скорости
                if (abs(velocityX) > 1000) {
                    startFlingAnimation(velocityX, velocityY)
                }

                velocityTracker.clear()
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    private fun startFlingAnimation(velocityX: Float, velocityY: Float) {
        // Анимация с замедлением
        animate()
            .translationXBy(velocityX / 2)
            .translationYBy(velocityY / 2)
            .setDuration(500)
            .setInterpolator(DecelerateInterpolator())
            .start()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        velocityTracker.recycle()
    }
}
```

---

### 9. Обратная связь на касание

Предоставление визуальной обратной связи на касания.

```kotlin
class TouchFeedbackView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var isPressed = false
    private val normalPaint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.FILL
    }

    private val pressedPaint = Paint().apply {
        color = Color.DARK_GRAY
        style = Paint.Style.FILL
    }

    init {
        // Включение звуковых эффектов и тактильной обратной связи
        isSoundEffectsEnabled = true
        isHapticFeedbackEnabled = true

        // Добавление эффекта волны (Material Design)
        foreground = context.getDrawable(R.drawable.ripple)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                isPressed = true
                performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY)
                invalidate()
                return true
            }

            MotionEvent.ACTION_UP -> {
                isPressed = false
                playSoundEffect(SoundEffectConstants.CLICK)
                performClick()
                invalidate()
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                isPressed = false
                invalidate()
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        super.performClick()
        // Обработка клика
        return true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val paint = if (isPressed) pressedPaint else normalPaint

        canvas.drawRoundRect(
            0f, 0f, width.toFloat(), height.toFloat(),
            20f, 20f,
            paint
        )
    }
}
```

---

### Комбинирование GestureDetector и ScaleGestureDetector

Можно комбинировать разные детекторы жестов для сложных взаимодействий:

```kotlin
class ZoomableScrollView : View {
    private val gestureDetector = GestureDetector(context, gestureListener)
    private val scaleDetector = ScaleGestureDetector(context, scaleListener)

    override fun onTouchEvent(event: MotionEvent): Boolean {
        var handled = scaleDetector.onTouchEvent(event)
        handled = gestureDetector.onTouchEvent(event) || handled
        return handled || super.onTouchEvent(event)
    }
}
```

### ViewGroup и перехват событий

ViewGroup может перехватывать события у дочерних элементов через onInterceptTouchEvent():

**Как это работает**:
1. ACTION_DOWN приходит в ViewGroup
2. onInterceptTouchEvent() возвращает false - событие идет к child
3. При ACTION_MOVE если нужно перехватить - onInterceptTouchEvent() возвращает true
4. Child получает ACTION_CANCEL
5. Дальнейшие события обрабатывает ViewGroup

**Пример**: ScrollView перехватывает скроллинг, когда пользователь делает вертикальное движение, но пропускает горизонтальное к дочернему HorizontalScrollView.

### Координация с родителем

Используйте requestDisallowInterceptTouchEvent() чтобы запретить родителю перехватывать события:

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Запрещаем родителю перехватывать
            parent.requestDisallowInterceptTouchEvent(true)
            return true
        }
        MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
            // Разрешаем снова
            parent.requestDisallowInterceptTouchEvent(false)
        }
    }
    return true
}
```

### Производительность и оптимизация

**Избегайте аллокаций в onTouchEvent**: предварительно создавайте объекты, переиспользуйте массивы и коллекции.

**Batch обновления**: накапливайте изменения и применяйте за один раз вместо множественных invalidate().

**Оптимизация invalidate**: используйте invalidate(rect) для перерисовки только измененной области.

**Дебаунсинг**: для частых событий (MOVE) используйте throttling или debouncing.

### 10. Лучшие практики

**1. Возвращайте `true` из `ACTION_DOWN`** чтобы получать последующие события - это критично!

**2. Переопределяйте `performClick()`** для доступности - обязательно для screen readers.

**3. Запрашивайте у родителя не перехватывать** события с помощью `parent.requestDisallowInterceptTouchEvent(true)` когда нужен контроль.

**4. Обрабатывайте `ACTION_CANCEL`** чтобы корректно сбросить состояние - родитель может отменить жест.

**5. Освобождайте `VelocityTracker`** с помощью `recycle()` в onDetachedFromWindow().

**6. Предоставляйте тактильную и визуальную обратную связь** - используйте performHapticFeedback() и изменение состояния.

**7. Тестируйте на разных устройствах** - размеры экранов и плотность пикселей влияют на touch точность.

**8. Обрабатывайте мультитач корректно** - используйте actionMasked и getPointerId().

**9. Документируйте поведение жестов** - объясните пользователям что делают различные жесты.

**10. Соблюдайте Android Design Guidelines** - следуйте стандартным паттернам взаимодействия.

---

### Резюме

**Поток событий касания:**
1. `dispatchTouchEvent()` - точка входа
2. `onInterceptTouchEvent()` - родитель может "украсть" события
3. `onTouchEvent()` - обработка событий

**Ключевые API:**
- `GestureDetector` - стандартные жесты
- `ScaleGestureDetector` - масштабирование
- `VelocityTracker` - отслеживание скорости
- `MotionEvent` - сырые данные о касании

**Лучшие практики:**
- Возвращайте `true` из `ACTION_DOWN`
- Переопределяйте `performClick()`
- Обрабатывайте `ACTION_CANCEL`
- Используйте `requestDisallowInterceptTouchEvent()`
- Предоставляйте визуальную/тактильную обратную связь

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - View
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- q-rxjava-pagination-recyclerview--android--medium - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - View

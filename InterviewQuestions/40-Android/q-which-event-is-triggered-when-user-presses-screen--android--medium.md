---
id: 20251012-122711
title: "Which Event Is Triggered When User Presses Screen / Какое событие срабатывает когда пользователь нажимает на экран"
aliases: ["Touch Events in Android", "События касания в Android"]
topic: android
subtopics: [ui-views, ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-16kb-dex-page-size--android--medium, q-primitive-maps-android--android--medium, q-how-to-create-chat-lists-from-a-ui-perspective--android--hard]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags:
  - android
  - android/ui-views
  - android/ui-compose
  - touch-events
  - motion-event
  - gesture-detection
  - difficulty/medium
---
# Вопрос (RU)

Какое событие срабатывает когда пользователь нажимает на экран?

## Ответ (RU)

При нажатии пользователя на экран вызывается событие **ACTION_DOWN**. Это часть системы сенсорных событий, управляемой через `MotionEvent`. Обработка касаний — фундаментальная часть [[c-custom-views]] и взаимодействия с пользователем в Android.

### Основные действия MotionEvent

| Действие | Константа | Описание |
|----------|-----------|----------|
| **ACTION_DOWN** | 0 | Первое касание экрана |
| **ACTION_UP** | 1 | Последнее касание покидает экран |
| **ACTION_MOVE** | 2 | Перемещение указателя по экрану |
| **ACTION_CANCEL** | 3 | Текущий жест отменен |
| **ACTION_POINTER_DOWN** | 5 | Дополнительный указатель касается экрана |
| **ACTION_POINTER_UP** | 6 | Не основной указатель покидает экран |

### Базовая обработка касаний в View

```kotlin
class CustomView(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // ✅ Обработать начальное касание
                Log.d("Touch", "Экран нажат в точке (${event.x}, ${event.y})")
                return true  // Consume event для получения последующих событий
            }
            MotionEvent.ACTION_MOVE -> {
                Log.d("Touch", "Перемещение в точке (${event.x}, ${event.y})")
                return true
            }
            MotionEvent.ACTION_UP -> {
                Log.d("Touch", "Экран отпущен")
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Пример: Рисование по касанию

```kotlin
class DrawingView(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {

    private val paint = Paint().apply {
        color = Color.BLUE
        strokeWidth = 10f
        isAntiAlias = true
    }
    private val path = Path()

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                path.moveTo(event.x, event.y)  // ✅ Начало пути
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                path.lineTo(event.x, event.y)  // ✅ Продолжение линии
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP -> {
                // Завершение рисования
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawPath(path, paint)
    }
}
```

### Обработка мультикасаний

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    val action = event.actionMasked  // ✅ Используйте actionMasked для мультикасаний
    val pointerIndex = event.actionIndex
    val pointerId = event.getPointerId(pointerIndex)

    when (action) {
        MotionEvent.ACTION_DOWN -> {
            // Первый палец
            Log.d("Touch", "Первый указатель: $pointerId")
            return true
        }
        MotionEvent.ACTION_POINTER_DOWN -> {
            // Дополнительные пальцы (пинч, масштабирование)
            Log.d("Touch", "Указатель $pointerId, всего: ${event.pointerCount}")
            return true
        }
        MotionEvent.ACTION_MOVE -> {
            // Обработка всех активных указателей
            for (i in 0 until event.pointerCount) {
                val id = event.getPointerId(i)
                val x = event.getX(i)
                val y = event.getY(i)
                Log.d("Touch", "Указатель $id: ($x, $y)")
            }
            return true
        }
    }
    return super.onTouchEvent(event)
}
```

### Обработка касаний в Jetpack Compose

```kotlin
@Composable
fun TouchableBox() {
    var touchPosition by remember { mutableStateOf<Offset?>(null) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = { offset ->
                        // ✅ ACTION_DOWN
                        touchPosition = offset
                    },
                    onTap = { offset ->
                        // ✅ ACTION_DOWN + ACTION_UP (полный клик)
                        Log.d("Compose", "Тап в $offset")
                    }
                )
            }
    ) {
        touchPosition?.let { pos ->
            Canvas(modifier = Modifier.fillMaxSize()) {
                drawCircle(color = Color.Blue, radius = 50f, center = pos)
            }
        }
    }
}
```

### Свойства MotionEvent

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    // Координаты
    val x = event.x        // ✅ Относительно view
    val y = event.y
    val rawX = event.rawX  // ✅ Относительно экрана
    val rawY = event.rawY

    // Метаданные
    val pressure = event.pressure  // Сила нажатия
    val size = event.size          // Размер касания

    // ❌ Не используйте event.action напрямую для мультикасаний
    // ✅ Используйте event.actionMasked

    return true
}
```

### GestureDetector для сложных жестов

```kotlin
val gestureDetector = GestureDetector(context,
    object : GestureDetector.SimpleOnGestureListener() {

    override fun onDown(e: MotionEvent): Boolean = true

    override fun onSingleTapUp(e: MotionEvent): Boolean {
        // Одиночный клик
        return true
    }

    override fun onDoubleTap(e: MotionEvent): Boolean {
        // Двойной клик
        return true
    }

    override fun onLongPress(e: MotionEvent) {
        // Долгое нажатие
    }

    override fun onFling(
        e1: MotionEvent?,
        e2: MotionEvent,
        velocityX: Float,
        velocityY: Float
    ): Boolean {
        // Свайп с инерцией
        return true
    }
})

override fun onTouchEvent(event: MotionEvent): Boolean {
    return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
}
```

### Распространение событий (Touch Event Propagation)

```kotlin
class ParentView(context: Context) : ViewGroup(context) {

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        // ✅ Решить, перехватывать ли событие от дочерних элементов
        return when (ev.action) {
            MotionEvent.ACTION_DOWN -> false  // Пропустить к детям
            MotionEvent.ACTION_MOVE -> {
                // Перехватить для прокрутки
                shouldInterceptScroll()
            }
            else -> super.onInterceptTouchEvent(ev)
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Обработать, если перехвачено или дети не обработали
        return when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                Log.d("Parent", "Обработка касания")
                true
            }
            else -> super.onTouchEvent(event)
        }
    }
}
```

### Лучшие практики

1. **Возвращайте `true`** из `onTouchEvent()` для получения последующих событий (`MOVE`, `UP`)
2. **Используйте `actionMasked`** вместо `action` для корректной обработки мультикасаний
3. **Отслеживайте pointer ID** для стабильного трекинга пальцев при мультикасаниях
4. **Используйте `GestureDetector`** для стандартных жестов (tap, double-tap, fling)
5. **Учитывайте доступность** — обеспечьте альтернативы тач-управлению

---

# Question (EN)

Which event is triggered when user presses the screen?

## Answer (EN)

When a user presses the screen in Android, the **ACTION_DOWN** event is triggered. This is part of the touch event system managed through `MotionEvent`. Touch handling is a fundamental part of [[c-custom-views]] and user interaction in Android.

### Core MotionEvent Actions

| Action | Constant | Description |
|--------|----------|-------------|
| **ACTION_DOWN** | 0 | First pointer touches screen |
| **ACTION_UP** | 1 | Last pointer leaves screen |
| **ACTION_MOVE** | 2 | Pointer moves on screen |
| **ACTION_CANCEL** | 3 | Current gesture is cancelled |
| **ACTION_POINTER_DOWN** | 5 | Additional pointer touches screen |
| **ACTION_POINTER_UP** | 6 | Non-primary pointer leaves screen |

### Basic Touch Handling in View

```kotlin
class CustomView(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // ✅ Handle initial touch
                Log.d("Touch", "Screen pressed at (${event.x}, ${event.y})")
                return true  // Consume event to receive subsequent events
            }
            MotionEvent.ACTION_MOVE -> {
                Log.d("Touch", "Moving at (${event.x}, ${event.y})")
                return true
            }
            MotionEvent.ACTION_UP -> {
                Log.d("Touch", "Screen released")
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Example: Drawing on Touch

```kotlin
class DrawingView(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {

    private val paint = Paint().apply {
        color = Color.BLUE
        strokeWidth = 10f
        isAntiAlias = true
    }
    private val path = Path()

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                path.moveTo(event.x, event.y)  // ✅ Start path
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                path.lineTo(event.x, event.y)  // ✅ Continue line
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP -> {
                // Finish drawing
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawPath(path, paint)
    }
}
```

### Multi-Touch Handling

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    val action = event.actionMasked  // ✅ Use actionMasked for multi-touch
    val pointerIndex = event.actionIndex
    val pointerId = event.getPointerId(pointerIndex)

    when (action) {
        MotionEvent.ACTION_DOWN -> {
            // First finger
            Log.d("Touch", "First pointer: $pointerId")
            return true
        }
        MotionEvent.ACTION_POINTER_DOWN -> {
            // Additional fingers (pinch, zoom)
            Log.d("Touch", "Pointer $pointerId, total: ${event.pointerCount}")
            return true
        }
        MotionEvent.ACTION_MOVE -> {
            // Handle all active pointers
            for (i in 0 until event.pointerCount) {
                val id = event.getPointerId(i)
                val x = event.getX(i)
                val y = event.getY(i)
                Log.d("Touch", "Pointer $id: ($x, $y)")
            }
            return true
        }
    }
    return super.onTouchEvent(event)
}
```

### Touch Handling in Jetpack Compose

```kotlin
@Composable
fun TouchableBox() {
    var touchPosition by remember { mutableStateOf<Offset?>(null) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = { offset ->
                        // ✅ ACTION_DOWN
                        touchPosition = offset
                    },
                    onTap = { offset ->
                        // ✅ ACTION_DOWN + ACTION_UP (full click)
                        Log.d("Compose", "Tapped at $offset")
                    }
                )
            }
    ) {
        touchPosition?.let { pos ->
            Canvas(modifier = Modifier.fillMaxSize()) {
                drawCircle(color = Color.Blue, radius = 50f, center = pos)
            }
        }
    }
}
```

### MotionEvent Properties

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    // Coordinates
    val x = event.x        // ✅ Relative to view
    val y = event.y
    val rawX = event.rawX  // ✅ Relative to screen
    val rawY = event.rawY

    // Metadata
    val pressure = event.pressure  // Touch pressure
    val size = event.size          // Touch size

    // ❌ Don't use event.action directly for multi-touch
    // ✅ Use event.actionMasked

    return true
}
```

### GestureDetector for Complex Gestures

```kotlin
val gestureDetector = GestureDetector(context,
    object : GestureDetector.SimpleOnGestureListener() {

    override fun onDown(e: MotionEvent): Boolean = true

    override fun onSingleTapUp(e: MotionEvent): Boolean {
        // Single tap
        return true
    }

    override fun onDoubleTap(e: MotionEvent): Boolean {
        // Double tap
        return true
    }

    override fun onLongPress(e: MotionEvent) {
        // Long press
    }

    override fun onFling(
        e1: MotionEvent?,
        e2: MotionEvent,
        velocityX: Float,
        velocityY: Float
    ): Boolean {
        // Swipe with momentum
        return true
    }
})

override fun onTouchEvent(event: MotionEvent): Boolean {
    return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
}
```

### Touch Event Propagation

```kotlin
class ParentView(context: Context) : ViewGroup(context) {

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        // ✅ Decide whether to intercept touch from children
        return when (ev.action) {
            MotionEvent.ACTION_DOWN -> false  // Pass to children
            MotionEvent.ACTION_MOVE -> {
                // Intercept for scrolling
                shouldInterceptScroll()
            }
            else -> super.onInterceptTouchEvent(ev)
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Handle if intercepted or no child handled it
        return when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                Log.d("Parent", "Handling touch")
                true
            }
            else -> super.onTouchEvent(event)
        }
    }
}
```

### Best Practices

1. **Return `true`** from `onTouchEvent()` to receive subsequent events (`MOVE`, `UP`)
2. **Use `actionMasked`** instead of `action` for correct multi-touch handling
3. **Track pointer IDs** for stable finger tracking during multi-touch
4. **Use `GestureDetector`** for standard gestures (tap, double-tap, fling)
5. **Consider accessibility** — provide alternatives to touch controls

---

## Follow-ups

1. What's the difference between `event.action` and `event.actionMasked`?
2. How do you detect a swipe gesture vs. a scroll gesture?
3. What happens if `onTouchEvent()` returns `false` for `ACTION_DOWN`?
4. How does touch event propagation work in nested ViewGroups?
5. When should you use `GestureDetector` vs. raw `MotionEvent` handling?

## References

- [Android Developers: MotionEvent](https://developer.android.com/reference/android/view/MotionEvent)
- [Android Developers: Input Events](https://developer.android.com/develop/ui/views/touch-and-input/input-events)
- [Compose: Pointer Input](https://developer.android.com/jetpack/compose/touch-input)

## Related Questions

### Prerequisites (Easier)
- Understanding of View lifecycle in Android
- Basic knowledge of event handling patterns

### Related (Same Level)
- [[q-how-to-create-chat-lists-from-a-ui-perspective--android--hard]]
- Custom View drawing and invalidation
- Gesture recognition and touch feedback

### Advanced (Harder)
- Complex multi-touch gesture recognition (pinch-to-zoom, rotation)
- Touch event delegation in custom ViewGroups
- Performance optimization for high-frequency touch events
- Implementing custom drag-and-drop with touch events

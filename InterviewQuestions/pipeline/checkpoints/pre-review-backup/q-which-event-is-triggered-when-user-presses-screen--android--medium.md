---
id: 20251012-122711188
title: "Which Event Is Triggered When User Presses Screen / Какое событие срабатывает когда пользователь нажимает на экран"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-16kb-dex-page-size--android--medium, q-primitive-maps-android--android--medium, q-how-to-create-chat-lists-from-a-ui-perspective--android--hard]
created: 2025-10-15
tags:
  - android
---
# Which event is triggered when user presses the screen?

## EN (expanded)

When a user presses the screen in Android, the **ACTION_DOWN** event is triggered. This is part of the touch event system managed through `MotionEvent`.

### MotionEvent Actions

Android touch events have several action types:

| Action | Constant | Description |
|--------|----------|-------------|
| **ACTION_DOWN** | 0 | First pointer touches screen |
| **ACTION_UP** | 1 | Last pointer leaves screen |
| **ACTION_MOVE** | 2 | Pointer moves on screen |
| **ACTION_CANCEL** | 3 | Current gesture is cancelled |
| **ACTION_POINTER_DOWN** | 5 | Additional pointer touches screen |
| **ACTION_POINTER_UP** | 6 | Non-primary pointer leaves screen |

### Basic Touch Handling

```kotlin
class CustomView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // User pressed the screen
                Log.d("Touch", "Screen pressed at (${event.x}, ${event.y})")
                return true // Consume the event
            }
            MotionEvent.ACTION_MOVE -> {
                // User is moving finger
                Log.d("Touch", "Moving at (${event.x}, ${event.y})")
                return true
            }
            MotionEvent.ACTION_UP -> {
                // User released the screen
                Log.d("Touch", "Screen released")
                return true
            }
            MotionEvent.ACTION_CANCEL -> {
                // Touch event was cancelled
                Log.d("Touch", "Touch cancelled")
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Complete Touch Example

```kotlin
class DrawingView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private val paint = Paint().apply {
        color = Color.BLUE
        strokeWidth = 10f
        style = Paint.Style.STROKE
        isAntiAlias = true
    }

    private val path = Path()
    private var startX = 0f
    private var startY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val x = event.x
        val y = event.y

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // User pressed screen - start drawing
                startX = x
                startY = y
                path.moveTo(x, y)
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                // User dragging - continue drawing
                path.lineTo(x, y)
                invalidate() // Request redraw
                return true
            }

            MotionEvent.ACTION_UP -> {
                // User released - finish drawing
                path.lineTo(x, y)
                invalidate()
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                // Touch cancelled - reset
                path.reset()
                invalidate()
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

### Activity/Fragment Touch Handling

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                Log.d("Activity", "Screen touched")
                // Handle touch
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### View OnClickListener (Simplified Touch)

For simple clicks, use `OnClickListener`:

```kotlin
button.setOnClickListener {
    // Handles ACTION_DOWN + ACTION_UP automatically
    Toast.makeText(context, "Button clicked", Toast.LENGTH_SHORT).show()
}

// Or with touch feedback
button.setOnTouchListener { view, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            view.alpha = 0.5f
            true
        }
        MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
            view.alpha = 1f
            view.performClick() // Trigger click
            true
        }
        else -> false
    }
}
```

### Multi-Touch Handling

```kotlin
class MultiTouchView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val action = event.actionMasked
        val pointerIndex = event.actionIndex
        val pointerId = event.getPointerId(pointerIndex)

        when (action) {
            MotionEvent.ACTION_DOWN -> {
                // First finger down
                Log.d("Touch", "First pointer down: $pointerId")
                return true
            }

            MotionEvent.ACTION_POINTER_DOWN -> {
                // Additional finger down
                Log.d("Touch", "Pointer $pointerId down")
                Log.d("Touch", "Total pointers: ${event.pointerCount}")
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                // Any pointer moving
                for (i in 0 until event.pointerCount) {
                    val id = event.getPointerId(i)
                    val x = event.getX(i)
                    val y = event.getY(i)
                    Log.d("Touch", "Pointer $id at ($x, $y)")
                }
                return true
            }

            MotionEvent.ACTION_POINTER_UP -> {
                // Non-primary finger up
                Log.d("Touch", "Pointer $pointerId up")
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Last finger up
                Log.d("Touch", "Last pointer up")
                return true
            }
        }

        return super.onTouchEvent(event)
    }
}
```

### Touch Event Properties

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    // Position
    val x = event.x // Relative to view
    val y = event.y
    val rawX = event.rawX // Relative to screen
    val rawY = event.rawY

    // Time
    val eventTime = event.eventTime
    val downTime = event.downTime

    // Pressure and size
    val pressure = event.pressure
    val size = event.size

    // Action
    val action = event.action
    val actionMasked = event.actionMasked

    // Pointer info
    val pointerCount = event.pointerCount
    val pointerId = event.getPointerId(0)

    Log.d("Touch", "Position: ($x, $y)")
    Log.d("Touch", "Pressure: $pressure")
    Log.d("Touch", "Pointers: $pointerCount")

    return true
}
```

### Jetpack Compose Touch Handling

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
                        // ACTION_DOWN
                        Log.d("Compose", "Pressed at $offset")
                        touchPosition = offset
                    },
                    onTap = { offset ->
                        // ACTION_DOWN + ACTION_UP
                        Log.d("Compose", "Tapped at $offset")
                    }
                )
            }
    ) {
        touchPosition?.let { pos ->
            Canvas(modifier = Modifier.fillMaxSize()) {
                drawCircle(
                    color = Color.Blue,
                    radius = 50f,
                    center = pos
                )
            }
        }
    }
}

// Raw touch events
@Composable
fun RawTouchEvents() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                awaitPointerEventScope {
                    while (true) {
                        val event = awaitPointerEvent()

                        event.changes.forEach { change ->
                            when {
                                change.pressed -> {
                                    // ACTION_DOWN
                                    Log.d("Compose", "Down: ${change.position}")
                                }
                                change.previousPressed && !change.pressed -> {
                                    // ACTION_UP
                                    Log.d("Compose", "Up: ${change.position}")
                                }
                                else -> {
                                    // ACTION_MOVE
                                    Log.d("Compose", "Move: ${change.position}")
                                }
                            }
                        }
                    }
                }
            }
    )
}
```

### Touch Event Propagation

```kotlin
// Parent view
class ParentView(context: Context) : ViewGroup(context) {

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        // Decide whether to intercept touch events from children
        return when (ev.action) {
            MotionEvent.ACTION_DOWN -> {
                false // Don't intercept, let children handle
            }
            MotionEvent.ACTION_MOVE -> {
                // Intercept if needed (e.g., for scrolling)
                true
            }
            else -> super.onInterceptTouchEvent(ev)
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Handle touch if intercepted or no child handled it
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

1. **Return true** to consume events you handle
2. **Use ACTION_DOWN** to detect initial press
3. **Track pointer IDs** for multi-touch
4. **Use GestureDetector** for complex gestures
5. **Consider accessibility** - provide alternatives to touch

### Common Gestures

```kotlin
val gestureDetector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
    override fun onDown(e: MotionEvent): Boolean {
        // ACTION_DOWN
        return true
    }

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

    override fun onScroll(
        e1: MotionEvent?,
        e2: MotionEvent,
        distanceX: Float,
        distanceY: Float
    ): Boolean {
        // Scrolling
        return true
    }

    override fun onFling(
        e1: MotionEvent?,
        e2: MotionEvent,
        velocityX: Float,
        velocityY: Float
    ): Boolean {
        // Fling gesture
        return true
    }
})

override fun onTouchEvent(event: MotionEvent): Boolean {
    return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
}
```

---

## RU (original)

Какое событие вызывается при нажатии юзера по экрану

В Android при нажатии пользователя на экран вызывается событие **ACTION_DOWN**. Это часть системы сенсорных событий, управляемой через `MotionEvent`.

### Действия MotionEvent

Сенсорные события Android имеют несколько типов действий:

| Действие | Константа | Описание |
|--------|----------|-------------|
| **ACTION_DOWN** | 0 | Первое касание экрана |
| **ACTION_UP** | 1 | Последнее касание покидает экран |
| **ACTION_MOVE** | 2 | Перемещение указателя по экрану |
| **ACTION_CANCEL** | 3 | Текущий жест отменен |
| **ACTION_POINTER_DOWN** | 5 | Дополнительный указатель касается экрана |
| **ACTION_POINTER_UP** | 6 | Не основной указатель покидает экран |

### Базовая обработка касаний

```kotlin
class CustomView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Пользователь нажал на экран
                Log.d("Touch", "Экран нажат в точке (${event.x}, ${event.y})")
                return true // Обработать событие
            }
            MotionEvent.ACTION_MOVE -> {
                // Пользователь перемещает палец
                Log.d("Touch", "Перемещение в точке (${event.x}, ${event.y})")
                return true
            }
            MotionEvent.ACTION_UP -> {
                // Пользователь отпустил экран
                Log.d("Touch", "Экран отпущен")
                return true
            }
            MotionEvent.ACTION_CANCEL -> {
                // Событие касания отменено
                Log.d("Touch", "Касание отменено")
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### Полный пример обработки касаний

```kotlin
class DrawingView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private val paint = Paint().apply {
        color = Color.BLUE
        strokeWidth = 10f
        style = Paint.Style.STROKE
        isAntiAlias = true
    }

    private val path = Path()
    private var startX = 0f
    private var startY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val x = event.x
        val y = event.y

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Пользователь нажал экран - начать рисование
                startX = x
                startY = y
                path.moveTo(x, y)
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                // Пользователь перетаскивает - продолжить рисование
                path.lineTo(x, y)
                invalidate() // Запросить перерисовку
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Пользователь отпустил - завершить рисование
                path.lineTo(x, y)
                invalidate()
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                // Касание отменено - сбросить
                path.reset()
                invalidate()
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

### Обработка касаний в Activity/Fragment

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                Log.d("Activity", "Экран касается")
                // Обработать касание
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### View OnClickListener (упрощенное касание)

Для простых кликов используйте `OnClickListener`:

```kotlin
button.setOnClickListener {
    // Автоматически обрабатывает ACTION_DOWN + ACTION_UP
    Toast.makeText(context, "Кнопка нажата", Toast.LENGTH_SHORT).show()
}

// Или с обратной связью по касанию
button.setOnTouchListener { view, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            view.alpha = 0.5f
            true
        }
        MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
            view.alpha = 1f
            view.performClick() // Вызвать клик
            true
        }
        else -> false
    }
}
```

### Обработка мультикасаний

```kotlin
class MultiTouchView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val action = event.actionMasked
        val pointerIndex = event.actionIndex
        val pointerId = event.getPointerId(pointerIndex)

        when (action) {
            MotionEvent.ACTION_DOWN -> {
                // Первый палец опущен
                Log.d("Touch", "Первый указатель опущен: $pointerId")
                return true
            }

            MotionEvent.ACTION_POINTER_DOWN -> {
                // Дополнительный палец опущен
                Log.d("Touch", "Указатель $pointerId опущен")
                Log.d("Touch", "Всего указателей: ${event.pointerCount}")
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                // Любой указатель перемещается
                for (i in 0 until event.pointerCount) {
                    val id = event.getPointerId(i)
                    val x = event.getX(i)
                    val y = event.getY(i)
                    Log.d("Touch", "Указатель $id в позиции ($x, $y)")
                }
                return true
            }

            MotionEvent.ACTION_POINTER_UP -> {
                // Не основной палец поднят
                Log.d("Touch", "Указатель $pointerId поднят")
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Последний палец поднят
                Log.d("Touch", "Последний указатель поднят")
                return true
            }
        }

        return super.onTouchEvent(event)
    }
}
```

### Свойства событий касания

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    // Позиция
    val x = event.x // Относительно view
    val y = event.y
    val rawX = event.rawX // Относительно экрана
    val rawY = event.rawY

    // Время
    val eventTime = event.eventTime
    val downTime = event.downTime

    // Давление и размер
    val pressure = event.pressure
    val size = event.size

    // Действие
    val action = event.action
    val actionMasked = event.actionMasked

    // Информация об указателе
    val pointerCount = event.pointerCount
    val pointerId = event.getPointerId(0)

    Log.d("Touch", "Позиция: ($x, $y)")
    Log.d("Touch", "Давление: $pressure")
    Log.d("Touch", "Указателей: $pointerCount")

    return true
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
                        // ACTION_DOWN
                        Log.d("Compose", "Нажатие в $offset")
                        touchPosition = offset
                    },
                    onTap = { offset ->
                        // ACTION_DOWN + ACTION_UP
                        Log.d("Compose", "Тап в $offset")
                    }
                )
            }
    ) {
        touchPosition?.let { pos ->
            Canvas(modifier = Modifier.fillMaxSize()) {
                drawCircle(
                    color = Color.Blue,
                    radius = 50f,
                    center = pos
                )
            }
        }
    }
}

// Необработанные события касания
@Composable
fun RawTouchEvents() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                awaitPointerEventScope {
                    while (true) {
                        val event = awaitPointerEvent()

                        event.changes.forEach { change ->
                            when {
                                change.pressed -> {
                                    // ACTION_DOWN
                                    Log.d("Compose", "Опущен: ${change.position}")
                                }
                                change.previousPressed && !change.pressed -> {
                                    // ACTION_UP
                                    Log.d("Compose", "Поднят: ${change.position}")
                                }
                                else -> {
                                    // ACTION_MOVE
                                    Log.d("Compose", "Перемещение: ${change.position}")
                                }
                            }
                        }
                    }
                }
            }
    )
}
```

### Распространение событий касания

```kotlin
// Родительская view
class ParentView(context: Context) : ViewGroup(context) {

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        // Решить, перехватывать ли события касания от дочерних элементов
        return when (ev.action) {
            MotionEvent.ACTION_DOWN -> {
                false // Не перехватывать, позволить дочерним элементам обработать
            }
            MotionEvent.ACTION_MOVE -> {
                // Перехватить при необходимости (например, для прокрутки)
                true
            }
            else -> super.onInterceptTouchEvent(ev)
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Обработать касание, если перехвачено или ни один дочерний элемент не обработал
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

1. **Возвращайте true** для обработки событий
2. **Используйте ACTION_DOWN** для обнаружения начального нажатия
3. **Отслеживайте ID указателей** для мультикасаний
4. **Используйте GestureDetector** для сложных жестов
5. **Учитывайте доступность** - предоставляйте альтернативы касанию

### Распространенные жесты

```kotlin
val gestureDetector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
    override fun onDown(e: MotionEvent): Boolean {
        // ACTION_DOWN
        return true
    }

    override fun onSingleTapUp(e: MotionEvent): Boolean {
        // Одиночный тап
        return true
    }

    override fun onDoubleTap(e: MotionEvent): Boolean {
        // Двойной тап
        return true
    }

    override fun onLongPress(e: MotionEvent) {
        // Длительное нажатие
    }

    override fun onScroll(
        e1: MotionEvent?,
        e2: MotionEvent,
        distanceX: Float,
        distanceY: Float
    ): Boolean {
        // Прокрутка
        return true
    }

    override fun onFling(
        e1: MotionEvent?,
        e2: MotionEvent,
        velocityX: Float,
        velocityY: Float
    ): Boolean {
        // Жест свайпа
        return true
    }
})

override fun onTouchEvent(event: MotionEvent): Boolean {
    return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
}
```

## Related Questions

- [[q-16kb-dex-page-size--android--medium]]
- [[q-primitive-maps-android--android--medium]]
- [[q-how-to-create-chat-lists-from-a-ui-perspective--android--hard]]

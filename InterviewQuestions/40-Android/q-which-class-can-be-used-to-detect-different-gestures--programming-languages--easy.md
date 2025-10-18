---
id: 20251012-122711184
title: "Which Class Can Be Used To Detect Different Gestures / Какой класс можно использовать для обнаружения разных жестов"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-which-class-to-catch-gestures--android--easy, q-fragments-vs-activity--android--medium, q-material3-components--material-design--easy]
created: 2025-10-15
tags: [languages, android, difficulty/easy]
---
# Какой класс можно использовать что бы ловить разные жесты?

## Answer (EN)
To handle gestures in Android, use the **GestureDetector** class. It helps track standard gestures: single taps, swipes, long presses, double taps, flings, and scrolls.

### Basic GestureDetector Usage

```kotlin
class GestureActivity : AppCompatActivity() {

    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Create GestureDetector
        gestureDetector = GestureDetector(this, MyGestureListener())

        // Apply to view
        findViewById<View>(R.id.touchArea).setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
        }
    }

    private inner class MyGestureListener : GestureDetector.SimpleOnGestureListener() {

        override fun onSingleTapUp(e: MotionEvent): Boolean {
            Toast.makeText(this@GestureActivity, "Single Tap", Toast.LENGTH_SHORT).show()
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            Toast.makeText(this@GestureActivity, "Double Tap", Toast.LENGTH_SHORT).show()
            return true
        }

        override fun onLongPress(e: MotionEvent) {
            Toast.makeText(this@GestureActivity, "Long Press", Toast.LENGTH_SHORT).show()
        }

        override fun onFling(
            e1: MotionEvent,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            Toast.makeText(this@GestureActivity, "Fling", Toast.LENGTH_SHORT).show()
            return true
        }

        override fun onScroll(
            e1: MotionEvent,
            e2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            Toast.makeText(this@GestureActivity, "Scrolling", Toast.LENGTH_SHORT).show()
            return true
        }
    }
}
```

### All GestureDetector Methods

```kotlin
class CompleteGestureListener : GestureDetector.SimpleOnGestureListener() {

    // Called when user first touches screen
    override fun onDown(e: MotionEvent): Boolean {
        Log.d("Gesture", "onDown")
        return true // Must return true to process other gestures
    }

    // Called when user taps lightly and lifts finger
    override fun onSingleTapUp(e: MotionEvent): Boolean {
        Log.d("Gesture", "Single Tap Up")
        return true
    }

    // Called for confirmed single tap (not part of double tap)
    override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
        Log.d("Gesture", "Single Tap Confirmed")
        return true
    }

    // Called when user double taps
    override fun onDoubleTap(e: MotionEvent): Boolean {
        Log.d("Gesture", "Double Tap")
        return true
    }

    // Called for each event in double tap gesture
    override fun onDoubleTapEvent(e: MotionEvent): Boolean {
        Log.d("Gesture", "Double Tap Event")
        return true
    }

    // Called when user presses and holds
    override fun onLongPress(e: MotionEvent) {
        Log.d("Gesture", "Long Press")
    }

    // Called when user scrolls/drags
    override fun onScroll(
        e1: MotionEvent,
        e2: MotionEvent,
        distanceX: Float,
        distanceY: Float
    ): Boolean {
        Log.d("Gesture", "Scroll: dx=$distanceX, dy=$distanceY")
        return true
    }

    // Called for press-release with velocity
    override fun onFling(
        e1: MotionEvent,
        e2: MotionEvent,
        velocityX: Float,
        velocityY: Float
    ): Boolean {
        Log.d("Gesture", "Fling: vx=$velocityX, vy=$velocityY")
        return true
    }

    // Called for press without movement or release
    override fun onShowPress(e: MotionEvent) {
        Log.d("Gesture", "Show Press")
    }

    // Called during context click (usually right-click on mouse)
    override fun onContextClick(e: MotionEvent): Boolean {
        Log.d("Gesture", "Context Click")
        return true
    }
}
```

### Custom View with Gestures

```kotlin
class GestureView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureDetector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {

        override fun onDown(e: MotionEvent): Boolean = true

        override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
            // Handle single tap
            performClick()
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            // Handle double tap (e.g., zoom in)
            scaleX *= 1.5f
            scaleY *= 1.5f
            return true
        }

        override fun onLongPress(e: MotionEvent) {
            // Show context menu or selection
            performLongClick()
        }

        override fun onFling(
            e1: MotionEvent,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            // Determine fling direction
            if (abs(velocityX) > abs(velocityY)) {
                if (velocityX > 0) {
                    // Fling right
                } else {
                    // Fling left
                }
            }
            return true
        }
    })

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### Swipe Detection Example

```kotlin
class SwipeGestureListener(
    private val onSwipeLeft: () -> Unit = {},
    private val onSwipeRight: () -> Unit = {},
    private val onSwipeUp: () -> Unit = {},
    private val onSwipeDown: () -> Unit = {}
) : GestureDetector.SimpleOnGestureListener() {

    companion object {
        private const val SWIPE_THRESHOLD = 100
        private const val SWIPE_VELOCITY_THRESHOLD = 100
    }

    override fun onFling(
        e1: MotionEvent,
        e2: MotionEvent,
        velocityX: Float,
        velocityY: Float
    ): Boolean {
        val diffX = e2.x - e1.x
        val diffY = e2.y - e1.y

        if (abs(diffX) > abs(diffY)) {
            // Horizontal swipe
            if (abs(diffX) > SWIPE_THRESHOLD && abs(velocityX) > SWIPE_VELOCITY_THRESHOLD) {
                if (diffX > 0) {
                    onSwipeRight()
                } else {
                    onSwipeLeft()
                }
                return true
            }
        } else {
            // Vertical swipe
            if (abs(diffY) > SWIPE_THRESHOLD && abs(velocityY) > SWIPE_VELOCITY_THRESHOLD) {
                if (diffY > 0) {
                    onSwipeDown()
                } else {
                    onSwipeUp()
                }
                return true
            }
        }

        return false
    }
}

// Usage
val gestureDetector = GestureDetector(context, SwipeGestureListener(
    onSwipeLeft = { Toast.makeText(context, "Swiped Left", Toast.LENGTH_SHORT).show() },
    onSwipeRight = { Toast.makeText(context, "Swiped Right", Toast.LENGTH_SHORT).show() },
    onSwipeUp = { Toast.makeText(context, "Swiped Up", Toast.LENGTH_SHORT).show() },
    onSwipeDown = { Toast.makeText(context, "Swiped Down", Toast.LENGTH_SHORT).show() }
))
```

### ScaleGestureDetector for Pinch Zoom

```kotlin
class ZoomableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var scaleFactor = 1f

    private val scaleGestureDetector = ScaleGestureDetector(context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {

            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                scaleFactor = scaleFactor.coerceIn(0.1f, 5.0f) // Limit zoom

                scaleX = scaleFactor
                scaleY = scaleFactor

                return true
            }
        })

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleGestureDetector.onTouchEvent(event)
        return true
    }
}
```

### Jetpack Compose Gestures

```kotlin
@Composable
fun GestureExample() {
    var tapCount by remember { mutableStateOf(0) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = {
                        tapCount++
                    },
                    onDoubleTap = {
                        tapCount += 2
                    },
                    onLongPress = {
                        tapCount = 0
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        Text("Tap count: $tapCount")
    }
}

@Composable
fun SwipeExample() {
    var offsetX by remember { mutableStateOf(0f) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectDragGestures { change, dragAmount ->
                    change.consume()
                    offsetX += dragAmount.x
                }
            }
    ) {
        Box(
            modifier = Modifier
                .size(100.dp)
                .offset { IntOffset(offsetX.roundToInt(), 0) }
                .background(Color.Blue)
        )
    }
}
```

### Summary

- **GestureDetector** - Standard gesture recognition
- **ScaleGestureDetector** - Pinch zoom gestures
- **SimpleOnGestureListener** - Easy implementation
- Supports: tap, double tap, long press, fling, scroll
- Can combine multiple gesture detectors

---

# Какой класс можно использовать что бы ловить разные жесты?

## Ответ (RU)

Для обработки жестов в Android используйте класс **GestureDetector**. Он помогает отслеживать стандартные жесты: одиночные нажатия, свайпы, долгие нажатия, двойные касания, fling и прокрутку.

### Базовое использование GestureDetector

```kotlin
class GestureActivity : AppCompatActivity() {

    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Создание GestureDetector
        gestureDetector = GestureDetector(this, MyGestureListener())

        // Применение к view
        findViewById<View>(R.id.touchArea).setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
        }
    }

    private inner class MyGestureListener : GestureDetector.SimpleOnGestureListener() {

        override fun onSingleTapUp(e: MotionEvent): Boolean {
            Toast.makeText(this@GestureActivity, "Single Tap", Toast.LENGTH_SHORT).show()
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            Toast.makeText(this@GestureActivity, "Double Tap", Toast.LENGTH_SHORT).show()
            return true
        }

        override fun onLongPress(e: MotionEvent) {
            Toast.makeText(this@GestureActivity, "Long Press", Toast.LENGTH_SHORT).show()
        }

        override fun onFling(
            e1: MotionEvent,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            Toast.makeText(this@GestureActivity, "Fling", Toast.LENGTH_SHORT).show()
            return true
        }

        override fun onScroll(
            e1: MotionEvent,
            e2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            Toast.makeText(this@GestureActivity, "Scrolling", Toast.LENGTH_SHORT).show()
            return true
        }
    }
}
```

### Все методы GestureDetector

- **onDown** - вызывается когда пользователь касается экрана
- **onSingleTapUp** - одиночное касание с поднятием пальца
- **onSingleTapConfirmed** - подтвержденное одиночное касание (не часть двойного)
- **onDoubleTap** - двойное касание
- **onLongPress** - долгое нажатие
- **onScroll** - прокрутка/перетаскивание
- **onFling** - быстрое движение с отпусканием
- **onShowPress** - нажатие без движения
- **onContextClick** - контекстный клик

### Custom View с жестами

```kotlin
class GestureView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureDetector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {

        override fun onDown(e: MotionEvent): Boolean = true

        override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
            // Обработка одиночного касания
            performClick()
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            // Обработка двойного касания (например, увеличение)
            scaleX *= 1.5f
            scaleY *= 1.5f
            return true
        }

        override fun onLongPress(e: MotionEvent) {
            // Показать контекстное меню или выделение
            performLongClick()
        }

        override fun onFling(
            e1: MotionEvent,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            // Определить направление fling
            if (abs(velocityX) > abs(velocityY)) {
                if (velocityX > 0) {
                    // Fling вправо
                } else {
                    // Fling влево
                }
            }
            return true
        }
    })

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### ScaleGestureDetector для pinch zoom

```kotlin
class ZoomableView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var scaleFactor = 1f

    private val scaleGestureDetector = ScaleGestureDetector(context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {

            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                scaleFactor = scaleFactor.coerceIn(0.1f, 5.0f) // Ограничение масштаба

                scaleX = scaleFactor
                scaleY = scaleFactor

                return true
            }
        })

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleGestureDetector.onTouchEvent(event)
        return true
    }
}
```

### Jetpack Compose жесты

```kotlin
@Composable
fun GestureExample() {
    var tapCount by remember { mutableStateOf(0) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { tapCount++ },
                    onDoubleTap = { tapCount += 2 },
                    onLongPress = { tapCount = 0 }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        Text("Tap count: $tapCount")
    }
}
```

### Резюме

- **GestureDetector** - распознавание стандартных жестов
- **ScaleGestureDetector** - жесты pinch zoom
- **SimpleOnGestureListener** - простая реализация
- Поддерживает: tap, double tap, long press, fling, scroll
- Можно комбинировать несколько детекторов жестов

## Related Questions

- [[q-which-class-to-catch-gestures--android--easy]]
- [[q-fragments-vs-activity--android--medium]]
- [[q-material3-components--material-design--easy]]

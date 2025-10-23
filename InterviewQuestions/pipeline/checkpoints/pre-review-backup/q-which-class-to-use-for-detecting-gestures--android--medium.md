---
id: 20251012-122711186
title: "Which Class To Use For Detecting Gestures / Какой класс использовать для обнаружения жестов"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-how-to-write-recyclerview-cache-ahead--android--medium, q-dagger-field-injection--android--medium, q-what-are-services-for--android--easy]
created: 2025-10-15
tags: [gestures, ui, touch-events, difficulty/medium]
---
# Which class can be used to catch different gestures?

## EN (expanded)

The **GestureDetector** class is used to detect and handle common gestures in Android, including taps, double taps, long presses, scrolls, and flings.

### Basic GestureDetector Usage

```kotlin
class CustomView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {

            override fun onSingleTapUp(e: MotionEvent): Boolean {
                Log.d("Gesture", "Single tap")
                return true
            }

            override fun onDoubleTap(e: MotionEvent): Boolean {
                Log.d("Gesture", "Double tap")
                return true
            }

            override fun onLongPress(e: MotionEvent) {
                Log.d("Gesture", "Long press")
            }

            override fun onScroll(
                e1: MotionEvent?,
                e2: MotionEvent,
                distanceX: Float,
                distanceY: Float
            ): Boolean {
                Log.d("Gesture", "Scrolling: dx=$distanceX, dy=$distanceY")
                return true
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                Log.d("Gesture", "Fling: vx=$velocityX, vy=$velocityY")
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### Complete Example with All Gestures

```kotlin
class GestureView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private val paint = Paint().apply {
        color = Color.BLUE
        textSize = 48f
        textAlign = Paint.Align.CENTER
    }

    private var gestureText = "Touch the screen"

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {

            override fun onDown(e: MotionEvent): Boolean {
                // Required to return true to receive other events
                gestureText = "Down"
                invalidate()
                return true
            }

            override fun onSingleTapUp(e: MotionEvent): Boolean {
                gestureText = "Single Tap"
                invalidate()
                return true
            }

            override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
                gestureText = "Single Tap Confirmed"
                invalidate()
                return true
            }

            override fun onDoubleTap(e: MotionEvent): Boolean {
                gestureText = "Double Tap"
                invalidate()
                return true
            }

            override fun onDoubleTapEvent(e: MotionEvent): Boolean {
                gestureText = "Double Tap Event"
                invalidate()
                return true
            }

            override fun onLongPress(e: MotionEvent) {
                gestureText = "Long Press"
                invalidate()
            }

            override fun onScroll(
                e1: MotionEvent?,
                e2: MotionEvent,
                distanceX: Float,
                distanceY: Float
            ): Boolean {
                gestureText = "Scrolling"
                invalidate()
                return true
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                val direction = when {
                    abs(velocityX) > abs(velocityY) -> {
                        if (velocityX > 0) "Right" else "Left"
                    }
                    else -> {
                        if (velocityY > 0) "Down" else "Up"
                    }
                }
                gestureText = "Fling $direction"
                invalidate()
                return true
            }

            override fun onShowPress(e: MotionEvent) {
                gestureText = "Show Press"
                invalidate()
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(Color.WHITE)
        canvas.drawText(
            gestureText,
            width / 2f,
            height / 2f,
            paint
        )
    }
}
```

### Activity Example

```kotlin
class GestureActivity : AppCompatActivity() {

    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_gesture)

        gestureDetector = GestureDetector(this, GestureListener())
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }

    inner class GestureListener : GestureDetector.SimpleOnGestureListener() {

        override fun onDown(e: MotionEvent): Boolean {
            return true
        }

        override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
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
            e1: MotionEvent?,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            val diffY = e2.y - (e1?.y ?: 0f)
            val diffX = e2.x - (e1?.x ?: 0f)

            if (abs(diffX) > abs(diffY)) {
                if (abs(diffX) > 100 && abs(velocityX) > 100) {
                    if (diffX > 0) {
                        onSwipeRight()
                    } else {
                        onSwipeLeft()
                    }
                    return true
                }
            } else {
                if (abs(diffY) > 100 && abs(velocityY) > 100) {
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

    private fun onSwipeRight() {
        Toast.makeText(this, "Swipe Right", Toast.LENGTH_SHORT).show()
    }

    private fun onSwipeLeft() {
        Toast.makeText(this, "Swipe Left", Toast.LENGTH_SHORT).show()
    }

    private fun onSwipeUp() {
        Toast.makeText(this, "Swipe Up", Toast.LENGTH_SHORT).show()
    }

    private fun onSwipeDown() {
        Toast.makeText(this, "Swipe Down", Toast.LENGTH_SHORT).show()
    }
}
```

### ScaleGestureDetector (Pinch Zoom)

```kotlin
class ZoomableView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private var scaleFactor = 1f
    private val scaleGestureDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                scaleFactor = max(0.1f, min(scaleFactor, 5f))
                invalidate()
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleGestureDetector.onTouchEvent(event)
        return true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        canvas.save()
        canvas.scale(scaleFactor, scaleFactor, width / 2f, height / 2f)

        // Draw content
        val paint = Paint().apply {
            color = Color.BLUE
            style = Paint.Style.FILL
        }
        canvas.drawCircle(width / 2f, height / 2f, 100f, paint)

        canvas.restore()
    }
}
```

### Combined Gestures

```kotlin
class AdvancedGestureView(context: Context, attrs: AttributeSet? = null) :
    View(context, attrs) {

    private val gestureDetector = GestureDetector(context, GestureListener())
    private val scaleGestureDetector = ScaleGestureDetector(context, ScaleListener())

    private var posX = 0f
    private var posY = 0f
    private var scaleFactor = 1f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        var handled = scaleGestureDetector.onTouchEvent(event)
        handled = gestureDetector.onTouchEvent(event) || handled
        return handled || super.onTouchEvent(event)
    }

    inner class GestureListener : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent) = true

        override fun onScroll(
            e1: MotionEvent?,
            e2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            posX -= distanceX
            posY -= distanceY
            invalidate()
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            // Reset zoom on double tap
            scaleFactor = 1f
            posX = 0f
            posY = 0f
            invalidate()
            return true
        }
    }

    inner class ScaleListener : ScaleGestureDetector.SimpleOnScaleGestureListener() {
        override fun onScale(detector: ScaleGestureDetector): Boolean {
            scaleFactor *= detector.scaleFactor
            scaleFactor = max(0.1f, min(scaleFactor, 10f))
            invalidate()
            return true
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        canvas.save()
        canvas.translate(posX, posY)
        canvas.scale(scaleFactor, scaleFactor)

        // Draw content
        drawContent(canvas)

        canvas.restore()
    }

    private fun drawContent(canvas: Canvas) {
        val paint = Paint().apply {
            color = Color.RED
            style = Paint.Style.FILL
        }
        canvas.drawRect(0f, 0f, 200f, 200f, paint)
    }
}
```

### Jetpack Compose Gestures

```kotlin
@Composable
fun GestureExample() {
    var gestureText by remember { mutableStateOf("Touch the screen") }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = {
                        gestureText = "Tap"
                    },
                    onDoubleTap = {
                        gestureText = "Double Tap"
                    },
                    onLongPress = {
                        gestureText = "Long Press"
                    }
                )
            }
            .pointerInput(Unit) {
                detectDragGestures { change, dragAmount ->
                    gestureText = "Dragging"
                }
            },
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = gestureText,
            fontSize = 24.sp
        )
    }
}

// Transformable (scale, pan, rotate)
@Composable
fun TransformableBox() {
    var scale by remember { mutableStateOf(1f) }
    var offset by remember { mutableStateOf(Offset.Zero) }
    var rotation by remember { mutableStateOf(0f) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
                translationX = offset.x
                translationY = offset.y
                rotationZ = rotation
            }
            .transformable(
                state = rememberTransformableState { zoomChange, panChange, rotationChange ->
                    scale *= zoomChange
                    offset += panChange
                    rotation += rotationChange
                }
            )
    ) {
        Box(
            modifier = Modifier
                .size(100.dp)
                .background(Color.Blue)
                .align(Alignment.Center)
        )
    }
}
```

### Common Gestures Summary

| Gesture | Method | Description |
|---------|--------|-------------|
| **Single Tap** | `onSingleTapUp()` | Quick touch and release |
| **Double Tap** | `onDoubleTap()` | Two quick taps |
| **Long Press** | `onLongPress()` | Press and hold |
| **Scroll** | `onScroll()` | Drag finger |
| **Fling** | `onFling()` | Quick swipe |
| **Pinch** | `ScaleGestureDetector` | Two-finger zoom |

### Best Practices

1. **Always return true** from `onDown()` to receive other gesture events
2. **Use SimpleOnGestureListener** instead of full GestureDetector.OnGestureListener
3. **Combine detectors** for complex interactions (gesture + scale)
4. **Handle configuration changes** properly
5. **Test on real devices** - emulator gestures are limited

---

## RU (original)

Какой класс можно использовать что бы ловить разные жесты

Чтобы обрабатывать жесты в Android, используйте класс GestureDetector. Он помогает отслеживать стандартные жесты: одиночные нажатия, свайпы, долгие нажатия, двойные касания и т.д.

## Related Questions

- [[q-how-to-write-recyclerview-cache-ahead--android--medium]]
- [[q-dagger-field-injection--android--medium]]
- [[q-what-are-services-for--android--easy]]

---
id: android-176
title: "Which Class Can Be Used To Detect Different Gestures / Какой класс можно использовать для обнаружения разных жестов"
aliases: ["Which Class Can Be Used To Detect Different Gestures", "Какой класс можно использовать для обнаружения разных жестов"]
topic: android
subtopics: [ui-views, ui-widgets]
question_kind: android
difficulty: easy
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-fragments-vs-activity--android--medium, q-which-class-to-catch-gestures--android--easy]
sources: []
created: 2025-10-15
updated: 2025-01-27
tags: [android, android/ui-views, android/ui-widgets, difficulty/easy, gestures]
---

# Вопрос (RU)

> Какой класс можно использовать что бы ловить разные жесты?

# Question (EN)

> Which class can be used to detect different gestures?

---

## Ответ (RU)

Для обработки жестов в Android используйте класс **GestureDetector**. Он отслеживает стандартные жесты: tap, double tap, long press, fling, scroll.

### Базовое Использование

```kotlin
class GestureActivity : AppCompatActivity() {
    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        gestureDetector = GestureDetector(this, MyGestureListener())

        findViewById<View>(R.id.touchArea).setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event) // ✅ Делегирование обработки жестов
        }
    }

    private inner class MyGestureListener : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true // ✅ Обязательно для срабатывания других методов

        override fun onSingleTapUp(e: MotionEvent): Boolean {
            // Одиночное касание
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            // Двойное касание
            return true
        }

        override fun onLongPress(e: MotionEvent) {
            // Долгое нажатие
        }

        override fun onFling(
            e1: MotionEvent,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            // Быстрый свайп с отпусканием
            return true
        }
    }
}
```

### Определение Направления Свайпа

```kotlin
class SwipeGestureListener : GestureDetector.SimpleOnGestureListener() {
    companion object {
        private const val SWIPE_THRESHOLD = 100 // ✅ Минимальное расстояние
        private const val SWIPE_VELOCITY_THRESHOLD = 100 // ✅ Минимальная скорость
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
            // Горизонтальный свайп
            if (abs(diffX) > SWIPE_THRESHOLD && abs(velocityX) > SWIPE_VELOCITY_THRESHOLD) {
                if (diffX > 0) onSwipeRight() else onSwipeLeft()
                return true
            }
        } else {
            // Вертикальный свайп
            if (abs(diffY) > SWIPE_THRESHOLD && abs(velocityY) > SWIPE_VELOCITY_THRESHOLD) {
                if (diffY > 0) onSwipeDown() else onSwipeUp()
                return true
            }
        }
        return false
    }
}
```

### ScaleGestureDetector Для Pinch-zoom

```kotlin
class ZoomableView(context: Context) : View(context) {
    private var scaleFactor = 1f

    private val scaleGestureDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                scaleFactor = scaleFactor.coerceIn(0.1f, 5.0f) // ✅ Ограничение масштаба
                scaleX = scaleFactor
                scaleY = scaleFactor
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleGestureDetector.onTouchEvent(event)
        return true
    }
}
```

### Jetpack Compose

```kotlin
@Composable
fun GestureExample() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { /* tap */ },
                    onDoubleTap = { /* double tap */ },
                    onLongPress = { /* long press */ }
                )
            }
    )
}
```

**Основные классы:**
- **GestureDetector** — стандартные жесты (tap, fling, scroll)
- **ScaleGestureDetector** — pinch-zoom
- **SimpleOnGestureListener** — базовый класс с пустыми реализациями

## Answer (EN)

To handle gestures in Android, use the **GestureDetector** class. It tracks standard gestures: tap, double tap, long press, fling, scroll.

### Basic Usage

```kotlin
class GestureActivity : AppCompatActivity() {
    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        gestureDetector = GestureDetector(this, MyGestureListener())

        findViewById<View>(R.id.touchArea).setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event) // ✅ Delegate gesture handling
        }
    }

    private inner class MyGestureListener : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true // ✅ Required for other methods to trigger

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
            e1: MotionEvent,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            // Fast swipe with release
            return true
        }
    }
}
```

### Swipe Direction Detection

```kotlin
class SwipeGestureListener : GestureDetector.SimpleOnGestureListener() {
    companion object {
        private const val SWIPE_THRESHOLD = 100 // ✅ Minimum distance
        private const val SWIPE_VELOCITY_THRESHOLD = 100 // ✅ Minimum velocity
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
                if (diffX > 0) onSwipeRight() else onSwipeLeft()
                return true
            }
        } else {
            // Vertical swipe
            if (abs(diffY) > SWIPE_THRESHOLD && abs(velocityY) > SWIPE_VELOCITY_THRESHOLD) {
                if (diffY > 0) onSwipeDown() else onSwipeUp()
                return true
            }
        }
        return false
    }
}
```

### ScaleGestureDetector for Pinch-Zoom

```kotlin
class ZoomableView(context: Context) : View(context) {
    private var scaleFactor = 1f

    private val scaleGestureDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                scaleFactor = scaleFactor.coerceIn(0.1f, 5.0f) // ✅ Limit scale range
                scaleX = scaleFactor
                scaleY = scaleFactor
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleGestureDetector.onTouchEvent(event)
        return true
    }
}
```

### Jetpack Compose

```kotlin
@Composable
fun GestureExample() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { /* tap */ },
                    onDoubleTap = { /* double tap */ },
                    onLongPress = { /* long press */ }
                )
            }
    )
}
```

**Key Classes:**
- **GestureDetector** — standard gestures (tap, fling, scroll)
- **ScaleGestureDetector** — pinch-zoom
- **SimpleOnGestureListener** — base class with empty implementations

---

## Follow-ups

- How to combine multiple gesture detectors on the same `View`?
- What's the difference between `onSingleTapUp` and `onSingleTapConfirmed`?
- How to implement custom multi-touch gestures beyond pinch-zoom?
- How to handle gesture conflicts (e.g., scroll vs fling)?

## References

- [[c-custom-views]]
- [Android Developer: Handle Touch and Input](https://developer.android.com/develop/ui/views/touch-and-input)

## Related Questions

### Prerequisites
- [[q-which-class-to-catch-gestures--android--easy]] - Basic touch event handling

### Related
- [[q-fragments-vs-activity--android--medium]] - Component lifecycle context

### Advanced
- Custom multi-touch gesture recognizers
- Gesture conflict resolution strategies

---
id: 20251012-122711186
title: "Which Class To Use For Detecting Gestures / Какой класс использовать для обнаружения жестов"
aliases: ["Which Class To Use For Detecting Gestures", "Какой класс использовать для обнаружения жестов"]

# Classification
topic: android
subtopics: [ui-views, ui-state]
question_kind: android
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [q-how-to-write-recyclerview-cache-ahead--android--medium, q-dagger-field-injection--android--medium, q-what-are-services-for--android--easy]

# Timestamps
created: 2025-10-15
updated: 2025-10-29

# Tags (EN only; no leading #)
tags: [android/ui-views, android/ui-state, gestures, touch-events, difficulty/medium]
---

# Вопрос (RU)

> Какой класс можно использовать для обнаружения жестов в Android?

# Question (EN)

> Which class can be used to catch different gestures in Android?

---

## Ответ (RU)

Для обнаружения жестов в Android используется класс **GestureDetector**. Он распознаёт стандартные жесты: одиночные и двойные касания, длительные нажатия, прокрутку и свайпы (fling).

### Базовое использование

```kotlin
class CustomView(context: Context) : View(context) {

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {

            // ✅ onDown должен возвращать true для получения других событий
            override fun onDown(e: MotionEvent): Boolean = true

            override fun onSingleTapUp(e: MotionEvent): Boolean {
                // Обработка одиночного касания
                return true
            }

            override fun onLongPress(e: MotionEvent) {
                // Длительное нажатие
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                // Обработка свайпа по скорости и направлению
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### Обнаружение направления свайпа

```kotlin
override fun onFling(
    e1: MotionEvent?,
    e2: MotionEvent,
    velocityX: Float,
    velocityY: Float
): Boolean {
    val diffX = e2.x - (e1?.x ?: 0f)
    val diffY = e2.y - (e1?.y ?: 0f)

    // ✅ Проверка минимального смещения и скорости
    val threshold = 100
    val velocityThreshold = 100

    if (abs(diffX) > abs(diffY)) {
        if (abs(diffX) > threshold && abs(velocityX) > velocityThreshold) {
            if (diffX > 0) onSwipeRight() else onSwipeLeft()
            return true
        }
    } else {
        if (abs(diffY) > threshold && abs(velocityY) > velocityThreshold) {
            if (diffY > 0) onSwipeDown() else onSwipeUp()
            return true
        }
    }
    return false
}
```

### ScaleGestureDetector для жестов масштабирования

```kotlin
class ZoomableView(context: Context) : View(context) {

    private var scaleFactor = 1f

    private val scaleDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                // ✅ Ограничение диапазона масштабирования
                scaleFactor = scaleFactor.coerceIn(0.1f, 5f)
                invalidate()
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleDetector.onTouchEvent(event)
        return true
    }
}
```

### Jetpack Compose

В Compose используйте модификаторы:

```kotlin
@Composable
fun GestureExample() {
    var text by remember { mutableStateOf("Touch screen") }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { text = "Tap" },
                    onDoubleTap = { text = "Double Tap" },
                    onLongPress = { text = "Long Press" }
                )
            }
    ) {
        Text(text)
    }
}
```

### Основные методы SimpleOnGestureListener

| Метод | Описание |
|-------|----------|
| `onDown()` | Нажатие началось (должен вернуть true) |
| `onSingleTapUp()` | Одиночное касание |
| `onSingleTapConfirmed()` | Подтверждённое одиночное касание (не двойное) |
| `onDoubleTap()` | Двойное касание |
| `onLongPress()` | Длительное нажатие |
| `onScroll()` | Прокрутка/перетаскивание |
| `onFling()` | Быстрый свайп |

**Ключевые моменты**:
- `onDown()` должен возвращать `true`, иначе остальные события не поступят
- Используйте `SimpleOnGestureListener` вместо полного интерфейса
- Для масштабирования используйте отдельный `ScaleGestureDetector`
- Можно комбинировать несколько детекторов в одном View

---

## Answer (EN)

Android provides the **GestureDetector** class for detecting common gestures: single taps, double taps, long presses, scrolls, and flings.

### Basic Usage

```kotlin
class CustomView(context: Context) : View(context) {

    private val gestureDetector = GestureDetector(
        context,
        object : GestureDetector.SimpleOnGestureListener() {

            // ✅ onDown must return true to receive other events
            override fun onDown(e: MotionEvent): Boolean = true

            override fun onSingleTapUp(e: MotionEvent): Boolean {
                // Handle single tap
                return true
            }

            override fun onLongPress(e: MotionEvent) {
                // Handle long press
            }

            override fun onFling(
                e1: MotionEvent?,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                // Handle swipe based on velocity and direction
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### Detecting Swipe Direction

```kotlin
override fun onFling(
    e1: MotionEvent?,
    e2: MotionEvent,
    velocityX: Float,
    velocityY: Float
): Boolean {
    val diffX = e2.x - (e1?.x ?: 0f)
    val diffY = e2.y - (e1?.y ?: 0f)

    // ✅ Check minimum distance and velocity thresholds
    val threshold = 100
    val velocityThreshold = 100

    if (abs(diffX) > abs(diffY)) {
        if (abs(diffX) > threshold && abs(velocityX) > velocityThreshold) {
            if (diffX > 0) onSwipeRight() else onSwipeLeft()
            return true
        }
    } else {
        if (abs(diffY) > threshold && abs(velocityY) > velocityThreshold) {
            if (diffY > 0) onSwipeDown() else onSwipeUp()
            return true
        }
    }
    return false
}
```

### ScaleGestureDetector for Pinch Zoom

```kotlin
class ZoomableView(context: Context) : View(context) {

    private var scaleFactor = 1f

    private val scaleDetector = ScaleGestureDetector(
        context,
        object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                scaleFactor *= detector.scaleFactor
                // ✅ Constrain scale range
                scaleFactor = scaleFactor.coerceIn(0.1f, 5f)
                invalidate()
                return true
            }
        }
    )

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scaleDetector.onTouchEvent(event)
        return true
    }
}
```

### Jetpack Compose

In Compose, use modifier functions:

```kotlin
@Composable
fun GestureExample() {
    var text by remember { mutableStateOf("Touch screen") }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { text = "Tap" },
                    onDoubleTap = { text = "Double Tap" },
                    onLongPress = { text = "Long Press" }
                )
            }
    ) {
        Text(text)
    }
}
```

### Key SimpleOnGestureListener Methods

| Method | Description |
|--------|-------------|
| `onDown()` | Touch down event (must return true) |
| `onSingleTapUp()` | Single tap |
| `onSingleTapConfirmed()` | Confirmed single tap (not double) |
| `onDoubleTap()` | Double tap |
| `onLongPress()` | Long press |
| `onScroll()` | Scroll/drag |
| `onFling()` | Quick swipe |

**Key Points**:
- `onDown()` must return `true` or other events won't be received
- Use `SimpleOnGestureListener` instead of the full interface
- For pinch zoom, use separate `ScaleGestureDetector`
- Multiple detectors can be combined in one View

---

## Follow-ups

- How do you handle conflicting gestures (e.g., scroll vs. swipe)?
- What's the difference between `onSingleTapUp()` and `onSingleTapConfirmed()`?
- How would you implement custom multi-touch gestures?
- When should you use `MotionEvent` directly instead of `GestureDetector`?
- How do gesture detectors work with `RecyclerView` or `ViewPager`?

## References

- [Android Developers: Input Events](https://developer.android.com/develop/ui/views/touch-and-input/gestures)
- [GestureDetector API Reference](https://developer.android.com/reference/android/view/GestureDetector)
- [Compose Gestures](https://developer.android.com/jetpack/compose/touch-input)

## Related Questions

### Prerequisites (Easier)
- [[q-what-are-services-for--android--easy]] - Basic Android components understanding

### Related (Same Level)
- [[q-how-to-write-recyclerview-cache-ahead--android--medium]] - Touch handling in RecyclerView
- [[q-dagger-field-injection--android--medium]] - Dependency injection patterns

### Advanced (Harder)
- Custom multi-touch gesture implementation
- Gesture conflict resolution in complex UIs
- Performance optimization for gesture-heavy applications

---\
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
related: [c-custom-views, q-fragments-vs-activity--android--medium, q-which-class-to-catch-gestures--android--easy]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android, android/ui-views, android/ui-widgets, difficulty/easy, gestures]
anki_cards:
  - slug: android-176-0-en
    front: "Which class is used to detect gestures in Android?"
    back: |
      **GestureDetector** - for tap, double tap, long press, fling, scroll.
      **ScaleGestureDetector** - for pinch-zoom.

      ```kotlin
      val gestureDetector = GestureDetector(context,
          object : GestureDetector.SimpleOnGestureListener() {
              override fun onDown(e: MotionEvent) = true
              override fun onDoubleTap(e: MotionEvent) = true
              override fun onFling(...) = true
          })

      view.setOnTouchListener { _, event ->
          gestureDetector.onTouchEvent(event)
      }
      ```

      **Compose:** `Modifier.pointerInput { detectTapGestures(...) }`
    tags:
      - android_views
      - difficulty::easy
  - slug: android-176-0-ru
    front: "Какой класс используется для распознавания жестов в Android?"
    back: |
      **GestureDetector** - для tap, double tap, long press, fling, scroll.
      **ScaleGestureDetector** - для pinch-zoom.

      ```kotlin
      val gestureDetector = GestureDetector(context,
          object : GestureDetector.SimpleOnGestureListener() {
              override fun onDown(e: MotionEvent) = true
              override fun onDoubleTap(e: MotionEvent) = true
              override fun onFling(...) = true
          })

      view.setOnTouchListener { _, event ->
          gestureDetector.onTouchEvent(event)
      }
      ```

      **Compose:** `Modifier.pointerInput { detectTapGestures(...) }`
    tags:
      - android_views
      - difficulty::easy

---\
# Вопрос (RU)

> Какой класс можно использовать чтобы ловить разные жесты?

# Question (EN)

> Which class can be used to detect different gestures?

---

## Ответ (RU)

Для обработки стандартных жестов (tap, double tap, long press, scroll, fling и др.) в Android используйте класс **GestureDetector**.
Для жестов масштабирования (pinch-zoom) можно использовать отдельный класс **ScaleGestureDetector**.

`GestureDetector` вызывает соответствующие callback-и слушателя для типичных жестов: tap, double tap, long press, fling, scroll.

### Базовое Использование

```kotlin
class GestureActivity : AppCompatActivity() {
    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val listener = MyGestureListener()
        gestureDetector = GestureDetector(this, listener).apply {
            // ✅ Нужен для обработки double tap через onDoubleTap()
            setOnDoubleTapListener(listener)
        }

        findViewById<View>(R.id.touchArea).setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event) // ✅ Делегирование обработки жестов
        }
    }

    private inner class MyGestureListener : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true
        // ✅ onDown должен вернуть true, чтобы жесты на основе последующих событий (scroll, fling и др.) обрабатывались

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

    // Пример пользовательских обработчиков направлений (НЕ часть SDK)
    private fun onSwipeRight() { /* ... */ }
    private fun onSwipeLeft() { /* ... */ }
    private fun onSwipeUp() { /* ... */ }
    private fun onSwipeDown() { /* ... */ }
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
                // В Compose используются pointer input-детекторы (не GestureDetector из View API)
                detectTapGestures(
                    onTap = { /* tap */ },
                    onDoubleTap = { /* double tap */ },
                    onLongPress = { /* long press */ }
                )
            }
    )
}
```

**Основные классы (`View` API):**
- **GestureDetector** — стандартные жесты (tap, fling, scroll и др.)
- **ScaleGestureDetector** — pinch-zoom
- **GestureDetector.SimpleOnGestureListener** — базовый класс с пустыми реализациями

---

## Answer (EN)

To handle standard gestures (tap, double tap, long press, scroll, fling, etc.) in Android, use the **GestureDetector** class.
For scaling gestures (pinch-zoom), you can use the separate **ScaleGestureDetector** class.

`GestureDetector` invokes the appropriate callbacks on its listener for common gestures: tap, double tap, long press, fling, scroll.

### Basic Usage

```kotlin
class GestureActivity : AppCompatActivity() {
    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val listener = MyGestureListener()
        gestureDetector = GestureDetector(this, listener).apply {
            // ✅ Required for handling double-tap via onDoubleTap()
            setOnDoubleTapListener(listener)
        }

        findViewById<View>(R.id.touchArea).setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event) // ✅ Delegate gesture handling
        }
    }

    private inner class MyGestureListener : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true
        // ✅ onDown must return true so that subsequent gesture callbacks (scroll, fling, etc.) are triggered

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

    // Example custom handlers for directions (NOT part of the SDK)
    private fun onSwipeRight() { /* ... */ }
    private fun onSwipeLeft() { /* ... */ }
    private fun onSwipeUp() { /* ... */ }
    private fun onSwipeDown() { /* ... */ }
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
                // In Compose, pointer input detectors are used (not the View-based GestureDetector)
                detectTapGestures(
                    onTap = { /* tap */ },
                    onDoubleTap = { /* double tap */ },
                    onLongPress = { /* long press */ }
                )
            }
    )
}
```

**Key Classes (`View` API):**
- **GestureDetector** — standard gestures (tap, fling, scroll, etc.)
- **ScaleGestureDetector** — pinch-zoom
- **GestureDetector.SimpleOnGestureListener** — base class with empty implementations

---

## Дополнительные Вопросы (RU)

- Как комбинировать несколько детекторов жестов на одном `View`?
- В чем разница между `onSingleTapUp` и `onSingleTapConfirmed`?
- Как реализовать собственные мультитач-жесты, помимо pinch-zoom?
- Как обрабатывать конфликты жестов (например, scroll vs fling)?

## Follow-ups

- How to combine multiple gesture detectors on the same `View`?
- What's the difference between `onSingleTapUp` and `onSingleTapConfirmed`?
- How to implement custom multi-touch gestures beyond pinch-zoom?
- How to handle gesture conflicts (e.g., scroll vs fling)?

## Ссылки (RU)

- [[c-custom-views]]
- [Android Developer: Handle Touch and Input](https://developer.android.com/develop/ui/views/touch-and-input)

## References

- [[c-custom-views]]
- [Android Developer: Handle Touch and Input](https://developer.android.com/develop/ui/views/touch-and-input)

## Связанные Вопросы (RU)

### Необходимые Знания
- [[q-which-class-to-catch-gestures--android--easy]] - Базовая обработка touch-событий

### Связанные
- [[q-fragments-vs-activity--android--medium]] - Контекст жизненного цикла компонентов

### Продвинутое
- Кастомные мультитач-распознаватели жестов
- Стратегии разрешения конфликтов жестов

## Related Questions

### Prerequisites
- [[q-which-class-to-catch-gestures--android--easy]] - Basic touch event handling

### Related
- [[q-fragments-vs-activity--android--medium]] - `Component` lifecycle context

### Advanced
- Custom multi-touch gesture recognizers
- Gesture conflict resolution strategies

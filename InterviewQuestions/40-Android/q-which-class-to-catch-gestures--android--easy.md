---
id: "20251015082237290"
title: "Which Class To Catch Gestures / Какой класс для ловли жестов"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: - android
  - gesture-detector
  - gestures
  - ui
---

# Question (EN)

> Which class can be used to catch different gestures?

# Вопрос (RU)

> Какой класс можно использовать, чтобы ловить разные жесты?

---

## Answer (EN)

Use **GestureDetector** to handle standard gestures like taps, swipes, long presses, double taps, and flings.

### Basic Usage

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        gestureDetector = GestureDetector(this, MyGestureListener())

        view.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
        }
    }

    inner class MyGestureListener : GestureDetector.SimpleOnGestureListener() {
        override fun onSingleTapUp(e: MotionEvent): Boolean {
            // Handle tap
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            // Handle double tap
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
            // Handle swipe/fling
            return true
        }

        override fun onScroll(
            e1: MotionEvent?,
            e2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            // Handle scroll
            return true
        }
    }
}
```

### In Custom View

```kotlin
class GestureView(context: Context) : View(context) {
    private val gestureDetector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true

        override fun onFling(
            e1: MotionEvent?,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            if (abs(velocityX) > abs(velocityY)) {
                if (velocityX > 0) {
                    // Swipe right
                } else {
                    // Swipe left
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

## Ответ (RU)

---

## Follow-ups

-   How do you detect pinch-to-zoom and rotation gestures (ScaleGestureDetector)?
-   When should you use GestureDetector vs OnGestureListener vs Compose gestures?
-   How do you avoid gesture conflicts inside nested scrolling containers?

## References

-   `https://developer.android.com/reference/android/view/GestureDetector` — GestureDetector
-   `https://developer.android.com/reference/android/view/ScaleGestureDetector` — ScaleGestureDetector
-   `https://developer.android.com/jetpack/compose/gestures` — Compose gestures

## Related Questions

-   [[q-what-is-known-about-methods-that-redraw-view--android--medium]]
-   [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]
    Чтобы обрабатывать жесты в Android, используйте класс GestureDetector. Он помогает отслеживать стандартные жесты: одиночные нажатия, свайпы, долгие нажатия, двойные касания и т.д.

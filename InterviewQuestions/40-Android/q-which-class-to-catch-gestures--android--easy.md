---
id: 202510031419
title: Which class can be used to catch different gestures / Какой класс можно использовать что бы ловить разные жесты
aliases: []

# Classification
topic: android
subtopics: [android, ui, gestures]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/753
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-gestures
  - c-gesturedetector

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [GestureDetector, gestures, difficulty/easy, easy_kotlin, lang/ru, android/gestures, android/ui]
---

# Question (EN)
> Which class can be used to catch different gestures

# Вопрос (RU)
> Какой класс можно использовать что бы ловить разные жесты

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

Чтобы обрабатывать жесты в Android, используйте класс GestureDetector. Он помогает отслеживать стандартные жесты: одиночные нажатия, свайпы, долгие нажатия, двойные касания и т.д.

---

## Follow-ups
- How do you detect custom multi-touch gestures?
- What's the difference between GestureDetector and ScaleGestureDetector?
- How do you handle conflicting gestures in nested views?

## References
- [[c-android-gestures]]
- [[c-gesturedetector]]
- [[moc-android]]

## Related Questions
- [[q-which-event-on-screen-press--android--easy]]
- [[q-view-methods-and-their-purpose--android--medium]]

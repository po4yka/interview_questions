---
id: 202510031422
title: Which event is triggered when user presses on screen / Какое событие вызывается при нажатии юзера по экрану
aliases: []

# Classification
topic: android
subtopics: [android, ui, touch-events]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/802
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-touch-events
  - c-android-motionevent

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [event handling, touch events, difficulty/easy, easy_kotlin, lang/ru, android/touch-events, android/ui]
---

# Question (EN)
> Which event is triggered when user presses on screen

# Вопрос (RU)
> Какое событие вызывается при нажатии юзера по экрану

---

## Answer (EN)

When a user presses on the screen in Android, the **ACTION_DOWN** event is triggered via **MotionEvent**.

### Touch Event Sequence

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // User pressed the screen
            val x = event.x
            val y = event.y
            return true
        }
        MotionEvent.ACTION_MOVE -> {
            // User is moving finger while pressed
            return true
        }
        MotionEvent.ACTION_UP -> {
            // User released the screen
            return true
        }
        MotionEvent.ACTION_CANCEL -> {
            // Touch was cancelled
            return true
        }
    }
    return super.onTouchEvent(event)
}
```

### Complete Touch Events

| Event | Description |
|-------|-------------|
| ACTION_DOWN | Initial press |
| ACTION_MOVE | Finger moving while pressed |
| ACTION_UP | Finger lifted |
| ACTION_CANCEL | Touch cancelled by system |
| ACTION_POINTER_DOWN | Additional finger down (multi-touch) |
| ACTION_POINTER_UP | Additional finger up (multi-touch) |

### Example Usage

```kotlin
class TouchableView(context: Context) : View(context) {
    private var touchX = 0f
    private var touchY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                touchX = event.x
                touchY = event.y
                Log.d("Touch", "Press at ($touchX, $touchY)")
                invalidate()
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                touchX = event.x
                touchY = event.y
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP -> {
                Log.d("Touch", "Released at (${event.x}, ${event.y})")
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.RED }
        canvas.drawCircle(touchX, touchY, 50f, paint)
    }
}
```

### Setting Touch Listener

```kotlin
view.setOnTouchListener { v, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Handle press
            true
        }
        else -> false
    }
}
```

## Ответ (RU)

В Android при нажатии пользователя на экран вызывается событие ACTION_DOWN.

---

## Follow-ups
- How do you handle multi-touch events?
- What's the difference between onTouchEvent() and setOnTouchListener()?
- How does touch event propagation work in view hierarchy?

## References
- [[c-android-touch-events]]
- [[c-android-motionevent]]
- [[c-android-gestures]]
- [[moc-android]]

## Related Questions
- [[q-which-class-to-catch-gestures--android--easy]]
- [[q-view-methods-and-their-purpose--android--medium]]

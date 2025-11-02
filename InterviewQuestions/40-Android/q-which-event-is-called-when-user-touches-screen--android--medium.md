---
id: android-155
title: "Which Event Is Called When User Touches Screen / Какое событие вызывается когда пользователь касается экрана"
aliases: ["Touch Events", "События касания"]
topic: android
subtopics: [ui-views, ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-to-create-dynamic-screens-at-runtime--android--hard, q-how-to-create-chat-lists-from-a-ui-perspective--android--hard]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/ui-views, android/ui-compose, touch-events, ui, difficulty/medium]
date created: Monday, October 27th 2025, 4:02:54 pm
date modified: Thursday, October 30th 2025, 3:18:01 pm
---

# Вопрос (RU)

> Какое событие вызывается, когда пользователь касается экрана?

# Question (EN)

> Which event is called when the user touches the screen?

---

## Ответ (RU)

Когда пользователь касается экрана в Android, система вызывает цепочку методов обработки касаний. Основные события: **dispatchTouchEvent()** (распределение), **onInterceptTouchEvent()** (перехват для ViewGroup), **onTouchEvent()** (обработка), и **onClick()** (если настроен).

### Поток событий

```kotlin
// Activity.dispatchTouchEvent()
//   → ViewGroup.dispatchTouchEvent()
//     → ViewGroup.onInterceptTouchEvent() // ✅ Может перехватить для прокрутки
//       → View.onTouchEvent()
//         → View.OnClickListener.onClick()
```

### Основные методы

**dispatchTouchEvent()** — первый метод, распределяет событие:

```kotlin
override fun dispatchTouchEvent(event: MotionEvent): Boolean {
    // ✅ Можно перехватить перед обычной обработкой
    if (event.action == MotionEvent.ACTION_DOWN) {
        // Кастомная логика
    }
    return super.dispatchTouchEvent(event)
}
```

**onTouchEvent()** — основной метод обработки:

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            lastX = event.x; lastY = event.y
            return true // ✅ Потребляем событие
        }
        MotionEvent.ACTION_MOVE -> {
            translationX += event.x - lastX
            translationY += event.y - lastY
            return true
        }
        MotionEvent.ACTION_UP -> {
            performClick() // ✅ Важно для accessibility
            return true
        }
    }
    return super.onTouchEvent(event)
}
```

**onInterceptTouchEvent()** — перехват для ViewGroup:

```kotlin
override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
    return when (event.action) {
        MotionEvent.ACTION_MOVE -> shouldInterceptScroll(event) // ✅ Перехват при прокрутке
        else -> false // ❌ Не перехватываем DOWN - даем детям шанс
    }
}
```

### GestureDetector

Для обработки жестов (tap, double-tap, fling, scroll):

```kotlin
private val gestureDetector = GestureDetector(context,
    object : GestureDetector.SimpleOnGestureListener() {
        override fun onSingleTapUp(e: MotionEvent) = true // ✅ Tap
        override fun onDoubleTap(e: MotionEvent) = true   // ✅ Double tap
        override fun onLongPress(e: MotionEvent) {}       // ✅ Long press
        override fun onFling(e1: MotionEvent, e2: MotionEvent,
                            velocityX: Float, velocityY: Float) = true
    })

override fun onTouchEvent(event: MotionEvent): Boolean {
    return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
}
```

### Jetpack Compose

```kotlin
Box(modifier = Modifier.pointerInput(Unit) {
    detectTapGestures(
        onPress = { /* Нажато */ },
        onTap = { /* Tap */ },
        onDoubleTap = { /* Double tap */ },
        onLongPress = { /* Long press */ }
    )
})
```

### Последовательность для одиночного клика

```text
1. ACTION_DOWN → dispatchTouchEvent()
2. ACTION_DOWN → onTouchEvent()
3. ACTION_UP → dispatchTouchEvent()
4. ACTION_UP → onTouchEvent()
5. performClick()
6. onClick()
```

### Ключевые моменты

- Возвращайте `true` из onTouchEvent() для потребления события
- onClick() срабатывает только на ACTION_UP без движения
- ViewGroup может перехватить события детей через onInterceptTouchEvent()
- Всегда вызывайте performClick() при ACTION_UP для accessibility

## Answer (EN)

When a user touches the screen in Android, the system calls a chain of touch event methods. The main events are: **dispatchTouchEvent()** (distribution), **onInterceptTouchEvent()** (interception for ViewGroups), **onTouchEvent()** (handling), and **onClick()** (if configured).

### Event Flow

```kotlin
// Activity.dispatchTouchEvent()
//   → ViewGroup.dispatchTouchEvent()
//     → ViewGroup.onInterceptTouchEvent() // ✅ Can intercept for scrolling
//       → View.onTouchEvent()
//         → View.OnClickListener.onClick()
```

### Core Methods

**dispatchTouchEvent()** — first method called, distributes the event:

```kotlin
override fun dispatchTouchEvent(event: MotionEvent): Boolean {
    // ✅ Can intercept before normal handling
    if (event.action == MotionEvent.ACTION_DOWN) {
        // Custom logic
    }
    return super.dispatchTouchEvent(event)
}
```

**onTouchEvent()** — main touch handling method:

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            lastX = event.x; lastY = event.y
            return true // ✅ Consume event
        }
        MotionEvent.ACTION_MOVE -> {
            translationX += event.x - lastX
            translationY += event.y - lastY
            return true
        }
        MotionEvent.ACTION_UP -> {
            performClick() // ✅ Important for accessibility
            return true
        }
    }
    return super.onTouchEvent(event)
}
```

**onInterceptTouchEvent()** — interception for ViewGroups:

```kotlin
override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
    return when (event.action) {
        MotionEvent.ACTION_MOVE -> shouldInterceptScroll(event) // ✅ Intercept on scroll
        else -> false // ❌ Don't intercept DOWN - give children a chance
    }
}
```

### GestureDetector

For handling gestures (tap, double-tap, fling, scroll):

```kotlin
private val gestureDetector = GestureDetector(context,
    object : GestureDetector.SimpleOnGestureListener() {
        override fun onSingleTapUp(e: MotionEvent) = true // ✅ Tap
        override fun onDoubleTap(e: MotionEvent) = true   // ✅ Double tap
        override fun onLongPress(e: MotionEvent) {}       // ✅ Long press
        override fun onFling(e1: MotionEvent, e2: MotionEvent,
                            velocityX: Float, velocityY: Float) = true
    })

override fun onTouchEvent(event: MotionEvent): Boolean {
    return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
}
```

### Jetpack Compose

```kotlin
Box(modifier = Modifier.pointerInput(Unit) {
    detectTapGestures(
        onPress = { /* Pressed */ },
        onTap = { /* Tap */ },
        onDoubleTap = { /* Double tap */ },
        onLongPress = { /* Long press */ }
    )
})
```

### Event Sequence for Single Click

```text
1. ACTION_DOWN → dispatchTouchEvent()
2. ACTION_DOWN → onTouchEvent()
3. ACTION_UP → dispatchTouchEvent()
4. ACTION_UP → onTouchEvent()
5. performClick()
6. onClick()
```

### Key Points

- Return `true` from onTouchEvent() to consume the event
- onClick() only fires on ACTION_UP without movement
- ViewGroup can intercept child events via onInterceptTouchEvent()
- Always call performClick() on ACTION_UP for accessibility

## Follow-ups

- How does touch event propagation differ between View and ViewGroup?
- What happens when multiple views can handle the same touch event?
- How do you implement custom gesture detection for complex interactions?
- What is the difference between consuming an event and letting it propagate?
- How does Compose's pointer input system differ from View's touch events?

## References

- Android Developer Docs: Touch and input

## Related Questions

### Prerequisites
- Understanding View lifecycle and custom views

### Related
- [[q-how-to-create-dynamic-screens-at-runtime--android--hard]]
- [[q-how-to-create-chat-lists-from-a-ui-perspective--android--hard]]

### Advanced
- How to implement multi-touch gestures and pinch-to-zoom
- How to handle touch conflicts between nested scrollable views

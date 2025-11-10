---
id: android-155
title: Which Event Is Called When User Touches Screen / Какое событие вызывается когда пользователь касается экрана
aliases:
- Touch Events
- События касания
topic: android
subtopics:
- ui-compose
- ui-views
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-state
- c-jetpack-compose
- q-how-to-create-chat-lists-from-a-ui-perspective--android--hard
- q-how-to-create-dynamic-screens-at-runtime--android--hard
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/ui-compose
- android/ui-views
- difficulty/medium
- touch-events
- ui

---

# Вопрос (RU)

> Какое событие вызывается, когда пользователь касается экрана?

# Question (EN)

> Which event is called when the user touches the screen?

---

## Ответ (RU)

В Android не существует одного «магического» события для касания. Когда пользователь касается экрана, система формирует объект `MotionEvent` (например, `ACTION_DOWN`) и запускает цепочку методов обработки касаний. Ключевые точки в цепочке: **dispatchTouchEvent()** (распределение), **onInterceptTouchEvent()** (перехват для `ViewGroup`), **onTouchEvent()** (обработка), и, при выполнении условий клика, **performClick() / onClick()**.

### Поток Событий

```kotlin
// Activity.dispatchTouchEvent()
//   → ViewGroup.dispatchTouchEvent()
//     → ViewGroup.onInterceptTouchEvent() // ✅ Может перехватить, например, для прокрутки
//       → View.onTouchEvent()
//         → View.performClick()
//           → View.OnClickListener.onClick() // если клик распознан
```

### Основные Методы

**dispatchTouchEvent()** — первый метод в цепочке на каждом уровне (`Activity`, `ViewGroup`, `View`), распределяет событие дальше:

```kotlin
override fun dispatchTouchEvent(event: MotionEvent): Boolean {
    // ✅ Можно обработать или перехватить до стандартной логики
    if (event.action == MotionEvent.ACTION_DOWN) {
        // Кастомная логика
    }
    return super.dispatchTouchEvent(event)
}
```

**onTouchEvent()** — основной метод низкоуровневой обработки для конкретной `View`:

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            lastX = event.x; lastY = event.y
            return true // ✅ Потребляем последовательность событий
        }
        MotionEvent.ACTION_MOVE -> {
            translationX += event.x - lastX
            translationY += event.y - lastY
            return true
        }
        MotionEvent.ACTION_UP -> {
            // Вызываем performClick(), если жест действительно считается кликом
            performClick()
            return true
        }
    }
    return super.onTouchEvent(event)
}
```

**onInterceptTouchEvent()** — перехват для `ViewGroup`:

```kotlin
override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
    return when (event.action) {
        MotionEvent.ACTION_MOVE -> shouldInterceptScroll(event) // ✅ Частый случай: перехват при прокрутке
        // Обычно DOWN не перехватывают, чтобы дать детям шанс получить события,
        // но при необходимости его тоже можно перехватить.
        else -> false
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

### Последовательность Для Одиночного Клика (упрощенно)

```text
1. ACTION_DOWN → проходит через dispatchTouchEvent() (Activity → ViewGroup → View)
2. ACTION_DOWN → целевая View.onTouchEvent()
3. ACTION_UP → снова через dispatchTouchEvent() (Activity → ViewGroup → View)
4. ACTION_UP → целевая View.onTouchEvent()
5. View.performClick() вызывается, если жест распознан как клик
6. View.OnClickListener.onClick() вызывается из performClick()
```

### Ключевые Моменты

- Возвращайте `true` из `onTouchEvent()` (обычно на `ACTION_DOWN`), если `View` хочет обрабатывать дальнейшие события этого жеста.
- `onClick()` вызывается только если последовательность касаний распознана как клик (обычно `DOWN` → `UP` без значимого движения/отмены).
- `ViewGroup` может перехватывать события детей через `onInterceptTouchEvent()`; решение о перехвате зависит от жеста.
- Вызывайте `performClick()` при `ACTION_UP`, когда действие действительно соответствует клику — это важно для accessibility и единообразного поведения.

## Answer (EN)

In Android there is no single "magic" event for a touch. When the user touches the screen, the system creates a `MotionEvent` (e.g., `ACTION_DOWN`) and starts a touch event dispatch chain. The key points in this chain are: **dispatchTouchEvent()** (distribution), **onInterceptTouchEvent()** (interception for ViewGroups), **onTouchEvent()** (handling), and, when click conditions are met, **performClick() / onClick()**.

### Event `Flow`

```kotlin
// Activity.dispatchTouchEvent()
//   → ViewGroup.dispatchTouchEvent()
//     → ViewGroup.onInterceptTouchEvent() // ✅ Can intercept, e.g., for scrolling
//       → View.onTouchEvent()
//         → View.performClick()
//           → View.OnClickListener.onClick() // if click is recognized
```

### Core Methods

**dispatchTouchEvent()** — the first method in the chain at each level (`Activity`, `ViewGroup`, `View`); distributes the event further:

```kotlin
override fun dispatchTouchEvent(event: MotionEvent): Boolean {
    // ✅ Can handle or short-circuit before default behavior
    if (event.action == MotionEvent.ACTION_DOWN) {
        // Custom logic
    }
    return super.dispatchTouchEvent(event)
}
```

**onTouchEvent()** — the main low-level handling method for a specific `View`:

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            lastX = event.x; lastY = event.y
            return true // ✅ Consume the gesture sequence
        }
        MotionEvent.ACTION_MOVE -> {
            translationX += event.x - lastX
            translationY += event.y - lastY
            return true
        }
        MotionEvent.ACTION_UP -> {
            // Call performClick() when this sequence should be treated as a click
            performClick()
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
        MotionEvent.ACTION_MOVE -> shouldInterceptScroll(event) // ✅ Common: intercept when scrolling
        // Typically you don't intercept DOWN so children can receive events,
        // but you technically can if your layout needs it.
        else -> false
    }
}
```

### GestureDetector

For handling higher-level gestures (tap, double-tap, fling, scroll):

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

### Event Sequence for Single Click (simplified)

```text
1. ACTION_DOWN → goes through dispatchTouchEvent() (Activity → ViewGroup → View)
2. ACTION_DOWN → target View.onTouchEvent()
3. ACTION_UP → again through dispatchTouchEvent() (Activity → ViewGroup → View)
4. ACTION_UP → target View.onTouchEvent()
5. View.performClick() is called when the gesture is recognized as a click
6. View.OnClickListener.onClick() is invoked from performClick()
```

### Key Points

- Return `true` from `onTouchEvent()` (typically on `ACTION_DOWN`) if the `View` intends to handle the rest of the gesture.
- `onClick()` is fired only when the touch sequence is recognized as a click (usually `DOWN` → `UP` without significant movement/cancel).
- A `ViewGroup` may intercept child events via `onInterceptTouchEvent()`; interception behavior depends on the intended gesture handling.
- Call `performClick()` on `ACTION_UP` when the interaction should be treated as a click; this is important for accessibility and consistent behavior.

## Follow-ups

- How does touch event propagation differ between `View` and `ViewGroup`?
- What happens when multiple views can handle the same touch event?
- How do you implement custom gesture detection for complex interactions?
- What is the difference between consuming an event and letting it propagate?
- How does Compose's pointer input system differ from `View`'s touch events?

## References

- Android Developer Docs: Touch and input

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Prerequisites
- Understanding `View` lifecycle and custom views

### Related
- [[q-how-to-create-dynamic-screens-at-runtime--android--hard]]
- [[q-how-to-create-chat-lists-from-a-ui-perspective--android--hard]]

### Advanced
- How to implement multi-touch gestures and pinch-to-zoom
- How to handle touch conflicts between nested scrollable views

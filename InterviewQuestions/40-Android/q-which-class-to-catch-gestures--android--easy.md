---
id: android-149
title: Which Class To Catch Gestures / Какой класс для ловли жестов
aliases:
- Which Class To Catch Gestures
- Какой класс для ловли жестов
topic: android
subtopics:
- ui-views
- ui-widgets
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-components
- q-compose-side-effects-launchedeffect-disposableeffect--android--hard
- q-how-does-jetpack-compose-work--android--medium
created: 2025-10-15
updated: 2025-01-27
sources: []
tags:
- android/ui-views
- android/ui-widgets
- difficulty/easy
- gesture-detector
- gestures
- ui
---

# Вопрос (RU)

> Какой класс можно использовать, чтобы ловить разные жесты?

# Question (EN)

> Which class can be used to catch different gestures?

---

## Ответ (RU)

Используйте **GestureDetector** для обработки стандартных жестов: tap, swipe, long press, double tap, fling.

### Основное Использование

```kotlin
// ✅ Правильно: использовать SimpleOnGestureListener
gestureDetector = GestureDetector(context, object : SimpleOnGestureListener() {
    override fun onDown(e: MotionEvent): Boolean = true  // ✅ Обязательно вернуть true

    override fun onFling(
        e1: MotionEvent?,
        e2: MotionEvent,
        velocityX: Float,
        velocityY: Float
    ): Boolean {
        if (abs(velocityX) > abs(velocityY)) {
            // Горизонтальный свайп
            when {
                velocityX > 0 -> handleSwipeRight()
                else -> handleSwipeLeft()
            }
        }
        return true
    }
})

view.setOnTouchListener { _, event ->
    gestureDetector.onTouchEvent(event)  // ✅ Делегировать события
}
```

**Ключевые методы:**
- `onSingleTapUp()` — одиночное касание
- `onDoubleTap()` — двойное касание
- `onLongPress()` — долгое нажатие
- `onFling()` — быстрый свайп (получаете `velocityX/Y`)
- `onScroll()` — перетаскивание

**SimpleOnGestureListener** — adapter класс, позволяет переопределить только нужные методы вместо реализации всего интерфейса `OnGestureListener`.

### В Кастомных View

```kotlin
class GestureView(context: Context) : View(context) {
    private val gestureDetector = GestureDetector(context, GestureListener())

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // ✅ Правильно: делегировать и fallback на super
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }

    inner class GestureListener : SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true  // ✅ Критично
    }
}
```

### Дополнительные Детекторы

- **ScaleGestureDetector** — pinch-to-zoom (два пальца)
- **Compose gestures** — `Modifier.pointerInput { detectTapGestures() }`

### Best Practices

1. **Всегда возвращайте `true` из `onDown()`** — иначе последующие события не придут
2. **В Compose используйте Compose gesture APIs** — не создавайте `GestureDetector` вручную
3. **Для конфликтов в ScrollView** — используйте `requestDisallowInterceptTouchEvent()`

## Answer (EN)

Use **GestureDetector** to handle standard gestures: taps, swipes, long presses, double taps, and flings.

### Basic Usage

```kotlin
// ✅ Correct: use SimpleOnGestureListener
gestureDetector = GestureDetector(context, object : SimpleOnGestureListener() {
    override fun onDown(e: MotionEvent): Boolean = true  // ✅ Must return true

    override fun onFling(
        e1: MotionEvent?,
        e2: MotionEvent,
        velocityX: Float,
        velocityY: Float
    ): Boolean {
        if (abs(velocityX) > abs(velocityY)) {
            // Horizontal swipe
            when {
                velocityX > 0 -> handleSwipeRight()
                else -> handleSwipeLeft()
            }
        }
        return true
    }
})

view.setOnTouchListener { _, event ->
    gestureDetector.onTouchEvent(event)  // ✅ Delegate events
}
```

**Key methods:**
- `onSingleTapUp()` — single tap
- `onDoubleTap()` — double tap
- `onLongPress()` — long press
- `onFling()` — fast swipe (provides `velocityX/Y`)
- `onScroll()` — drag gesture

**SimpleOnGestureListener** is an adapter class that lets you override only the methods you need instead of implementing the full `OnGestureListener` interface.

### In Custom Views

```kotlin
class GestureView(context: Context) : View(context) {
    private val gestureDetector = GestureDetector(context, GestureListener())

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // ✅ Correct: delegate and fallback to super
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }

    inner class GestureListener : SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true  // ✅ Critical
    }
}
```

### Additional Detectors

- **ScaleGestureDetector** — pinch-to-zoom (two fingers)
- **Compose gestures** — `Modifier.pointerInput { detectTapGestures() }`

### Best Practices

1. **Always return `true` from `onDown()`** — otherwise subsequent events won't arrive
2. **In Compose, use Compose gesture APIs** — don't create `GestureDetector` manually
3. **For ScrollView conflicts** — use `requestDisallowInterceptTouchEvent()`


---

## Follow-ups

- How does `ScaleGestureDetector` work for pinch-to-zoom gestures?
- How do you resolve gesture conflicts in nested scrolling containers?
- What are the differences between `OnGestureListener` and `SimpleOnGestureListener`?
- How do Compose gesture APIs compare to View-based `GestureDetector`?

## References

- https://developer.android.com/reference/android/view/GestureDetector
- https://developer.android.com/jetpack/compose/gestures

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]


### Prerequisites
- Understanding MotionEvent and touch event handling basics

### Related
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]]
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]

### Advanced
- Multi-touch gesture handling (pinch, rotate)
- Custom gesture recognizers with `MotionEvent`
- Resolving gesture conflicts in complex layouts

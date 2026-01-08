---id: android-149
title: Which Class To Catch Gestures / Какой класс для ловли жестов
aliases: [Which Class To Catch Gestures, Какой класс для ловли жестов]
topic: android
subtopics: [ui-views, ui-widgets]
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
question_kind: android
moc: moc-android
related: [c-android-components, c-compose-recomposition, c-recomposition, c-wear-compose, q-compose-side-effects-launchedeffect-disposableeffect--android--hard, q-how-does-jetpack-compose-work--android--medium, q-which-class-can-be-used-to-detect-different-gestures--android--easy, q-which-class-to-use-for-detecting-gestures--android--medium, q-which-event-is-called-when-user-touches-screen--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/ui-views, android/ui-widgets, difficulty/easy, gesture-detector, gestures, ui]

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
import kotlin.math.abs

// ✅ Правильно: использовать SimpleOnGestureListener
gestureDetector = GestureDetector(context, object : SimpleOnGestureListener() {
    override fun onDown(e: MotionEvent): Boolean = true  // ✅ Обычно нужно вернуть true, если хотите обрабатывать дальнейшие жесты

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

    // Для обработки double tap также можно переопределить методы OnDoubleTapListener,
    // которые предоставляет SimpleOnGestureListener
    override fun onDoubleTap(e: MotionEvent): Boolean {
        handleDoubleTap()
        return true
    }
})

view.setOnTouchListener { _, event ->
    gestureDetector.onTouchEvent(event)  // ✅ Делегировать события
}
```

**Ключевые методы:**
- `onSingleTapUp()` — одиночное касание
- `onDoubleTap()` — двойное касание (через `OnDoubleTapListener` / `SimpleOnGestureListener`)
- `onLongPress()` — долгое нажатие
- `onFling()` — быстрый свайп (получаете `velocityX/Y`)
- `onScroll()` — перетаскивание

**SimpleOnGestureListener** — adapter-класс, позволяет переопределить только нужные методы вместо реализации всего интерфейса `OnGestureListener`.

### В Кастомных `View`

```kotlin
class GestureView(context: Context) : View(context) {
    private val gestureDetector = GestureDetector(context, GestureListener())

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // ✅ Правильно: делегировать и fallback на super
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }

    inner class GestureListener : SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true  // ✅ Обычно критично для получения последующих событий
    }
}
```

### Дополнительные Детекторы

- **ScaleGestureDetector** — pinch-to-zoom (два пальца)
- **Compose gestures** — `Modifier.pointerInput { detectTapGestures() }`

### Best Practices

1. **Обычно возвращайте `true` из `onDown()`**, если хотите получать `onScroll`, `onFling` и другие последующие события для этого жеста. Если вы сознательно не хотите обрабатывать последовательность, можно вернуть `false`.
2. **В Compose используйте Compose gesture APIs** — не создавайте `GestureDetector` вручную.
3. **Для конфликтов в ScrollView** — используйте `requestDisallowInterceptTouchEvent()`.
4. **Для double tap** — используйте `OnDoubleTapListener` или соответствующие методы `SimpleOnGestureListener`.

## Answer (EN)

Use **GestureDetector** to handle standard gestures: taps, swipes, long presses, double taps, and flings.

### Basic Usage

```kotlin
import kotlin.math.abs

// ✅ Correct: use SimpleOnGestureListener
gestureDetector = GestureDetector(context, object : SimpleOnGestureListener() {
    override fun onDown(e: MotionEvent): Boolean = true  // ✅ Typically must return true if you want to receive further gesture events

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

    // For double-tap handling you can also override OnDoubleTapListener methods
    // provided by SimpleOnGestureListener
    override fun onDoubleTap(e: MotionEvent): Boolean {
        handleDoubleTap()
        return true
    }
})

view.setOnTouchListener { _, event ->
    gestureDetector.onTouchEvent(event)  // ✅ Delegate events
}
```

**Key methods:**
- `onSingleTapUp()` — single tap
- `onDoubleTap()` — double tap (via `OnDoubleTapListener` / `SimpleOnGestureListener`)
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
        override fun onDown(e: MotionEvent): Boolean = true  // ✅ Usually critical to receive subsequent events
    }
}
```

### Additional Detectors

- **ScaleGestureDetector** — pinch-to-zoom (two fingers)
- **Compose gestures** — `Modifier.pointerInput { detectTapGestures() }`

### Best Practices

1. **Usually return `true` from `onDown()`** if you want to receive `onScroll`, `onFling`, and other subsequent events in that gesture sequence. If you intentionally don't want to handle the sequence, you may return `false`.
2. **In Compose, use Compose gesture APIs** — don't create `GestureDetector` manually.
3. **For ScrollView conflicts** — use `requestDisallowInterceptTouchEvent()`.
4. **For double tap** — use `OnDoubleTapListener` or the relevant `SimpleOnGestureListener` overrides.

---

## Дополнительные Вопросы (RU)

- Как работает `ScaleGestureDetector` для жестов pinch-to-zoom?
- Как решать конфликты жестов во вложенных скроллируемых контейнерах?
- В чем различия между `OnGestureListener` и `SimpleOnGestureListener`?
- Как жестовые API в Compose соотносятся с `GestureDetector` во `View`-основанном UI?

## Follow-ups

- How does `ScaleGestureDetector` work for pinch-to-zoom gestures?
- How do you resolve gesture conflicts in nested scrolling containers?
- What are the differences between `OnGestureListener` and `SimpleOnGestureListener`?
- How do Compose gesture APIs compare to `View`-based `GestureDetector`?

## Ссылки (RU)

- https://developer.android.com/reference/android/view/GestureDetector
- https://developer.android.com/jetpack/compose/gestures

## References

- https://developer.android.com/reference/android/view/GestureDetector
- https://developer.android.com/jetpack/compose/gestures

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-android-components]]

### Предпосылки

- Понимание `MotionEvent` и основ обработки touch-событий

### Связанные

- [[q-what-is-known-about-methods-that-redraw-view--android--medium]]
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]

### Продвинутое

- Обработка мультитач-жестов (pinch, rotate)
- Кастомные распознаватели жестов с использованием `MotionEvent`
- Разрешение конфликтов жестов в сложных layout-ах

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

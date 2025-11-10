---
id: android-256
title: "Which Event On Screen Press / Какое событие при нажатии на экран"
aliases: ["MotionEvent", "Touch Events", "Which Event On Screen Press", "Какое событие при нажатии на экран", "События касания"]
topic: android
subtopics: [ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views]
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-views, difficulty/easy, event-handling, motionevent, touch-events]

---

# Вопрос (RU)

> Какое событие вызывается при нажатии пользователя на экран в Android?

---

# Question (EN)

> Which event is triggered when a user presses on the screen in Android?

---

## Ответ (RU)

При первом нажатии на экран генерируется объект `MotionEvent` с действием `ACTION_DOWN`.

**Последовательность** (для одного касания): `ACTION_DOWN` → `ACTION_MOVE` → `ACTION_UP` (или `ACTION_CANCEL`).

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    return when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // ✅ Начальное касание: event.x, event.y
            // Верните true, если этот View хочет и дальше получать MOVE/UP для этого жеста
            true
        }
        MotionEvent.ACTION_MOVE -> true    // ✅ Движение (если DOWN был принят)
        MotionEvent.ACTION_UP -> true      // ✅ Отпускание
        MotionEvent.ACTION_CANCEL -> true  // ❌ Отменено системой
        else -> super.onTouchEvent(event)
    }
}

// ❌ WRONG (если вы хотите обработать событие в OnTouchListener)
// Возврат false означает, что вы НЕ потребляете событие,
// и последующие MOVE/UP могут не прийти этому слушателю.
view.setOnTouchListener { _, _ -> false }

// ✅ CORRECT (если цель — обработать DOWN и потребить последовательность)
view.setOnTouchListener { _, e ->
    if (e.action == MotionEvent.ACTION_DOWN) {
        // handle touch down
        true
    } else {
        true
    }
}
```

---

## Answer (EN)

On the initial press, a `MotionEvent` with action `ACTION_DOWN` is generated.

**Sequence** (for a single touch): `ACTION_DOWN` → `ACTION_MOVE` → `ACTION_UP` (or `ACTION_CANCEL`).

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    return when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // ✅ Initial touch: event.x, event.y
            // Return true if this View wants to keep receiving MOVE/UP for this gesture
            true
        }
        MotionEvent.ACTION_MOVE -> true   // ✅ Moving (if DOWN was accepted)
        MotionEvent.ACTION_UP -> true     // ✅ Release
        MotionEvent.ACTION_CANCEL -> true // ❌ Cancelled by system
        else -> super.onTouchEvent(event)
    }
}

// ❌ WRONG (if your goal is to handle the touch in the OnTouchListener)
// Returning false means you do NOT consume the event,
// and subsequent MOVE/UP may not be delivered to this listener.
view.setOnTouchListener { _, _ -> false }

// ✅ CORRECT (if the goal is to handle DOWN and consume the sequence)
view.setOnTouchListener { _, e ->
    if (e.action == MotionEvent.ACTION_DOWN) {
        // handle touch down
        true
    } else {
        true
    }
}
```

---

## Дополнительные вопросы (RU)

1. В чем разница между `onClick` и `onTouchEvent`?
2. Как обрабатывать мультитач (`ACTION_POINTER_DOWN`/`ACTION_POINTER_UP`)?
3. Когда происходит `ACTION_CANCEL` и как его корректно обрабатывать?
4. Как различать тап, долгий тап и скролл с помощью touch-событий или gesture detectors?
5. В чем разница между `event.x`/`event.y` (координаты во `View`) и `event.rawX`/`event.rawY` (координаты экрана)?

## Follow-ups

1. What's the difference between `onClick` and `onTouchEvent`?
2. How to handle multi-touch (`ACTION_POINTER_DOWN`/`ACTION_POINTER_UP`)?
3. When does `ACTION_CANCEL` occur, and how should you handle it?
4. How to distinguish tap vs long-press vs scroll using touch events or gesture detectors?
5. What's the difference between `event.x`/`event.y` (view coordinates) and `event.rawX`/`event.rawY` (screen coordinates)?

---

## Ссылки (RU)

- [[c-custom-views]] — Паттерны и обработка событий во кастомных `View`
- [Touch & Input](https://developer.android.com/develop/ui/views/touch-and-input/gestures) — Официальная документация по жестам и вводу

## References

- [[c-custom-views]] — Custom view patterns
- [Touch & Input](https://developer.android.com/develop/ui/views/touch-and-input/gestures) — Official docs

---

## Связанные вопросы (RU)

### Базовые знания
- [[c-custom-views]]

### Того же уровня
- [[q-custom-view-animation--android--medium]]
- [[q-list-elements-problems--android--medium]]


## Related Questions

### Prerequisites
- [[c-custom-views]]

### Same Level
- [[q-custom-view-animation--android--medium]]
- [[q-list-elements-problems--android--medium]]

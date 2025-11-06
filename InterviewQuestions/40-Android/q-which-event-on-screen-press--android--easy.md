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
related: [c-custom-views, c-gesture-detection, c-touch-events, c-view-lifecycle]
created: 2025-10-15
updated: 2025-10-30
tags: [android/ui-views, difficulty/easy, event-handling, motionevent, touch-events]

---

# Вопрос (RU)

> Какое событие вызывается при нажатии пользователя на экран в Android?

---

# Question (EN)

> Which event is triggered when a user presses on the screen in Android?

---

## Ответ (RU)

При нажатии на экран срабатывает **ACTION_DOWN** через **MotionEvent**.

**Последовательность**: ACTION_DOWN → ACTION_MOVE → ACTION_UP (или ACTION_CANCEL)

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    return when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // ✅ Касание: event.x, event.y
            true  // Обязательно true, иначе MOVE/UP не придут
        }
        MotionEvent.ACTION_MOVE -> true    // ✅ Движение
        MotionEvent.ACTION_UP -> true      // ✅ Отпускание
        MotionEvent.ACTION_CANCEL -> true  // ❌ Отменено системой
        else -> super.onTouchEvent(event)
    }
}

// ❌ WRONG
view.setOnTouchListener { _, _ -> false }

// ✅ CORRECT
view.setOnTouchListener { _, e -> e.action == MotionEvent.ACTION_DOWN }
```

---

## Answer (EN)

When the user presses the screen, **ACTION_DOWN** is triggered via **MotionEvent**.

**Sequence**: ACTION_DOWN → ACTION_MOVE → ACTION_UP (or ACTION_CANCEL)

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    return when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // ✅ Touch: event.x, event.y
            true  // Must return true or MOVE/UP won't arrive
        }
        MotionEvent.ACTION_MOVE -> true   // ✅ Moving
        MotionEvent.ACTION_UP -> true     // ✅ Released
        MotionEvent.ACTION_CANCEL -> true // ❌ Cancelled by system
        else -> super.onTouchEvent(event)
    }
}

// ❌ WRONG
view.setOnTouchListener { _, _ -> false }

// ✅ CORRECT
view.setOnTouchListener { _, e -> e.action == MotionEvent.ACTION_DOWN }
```

---

## Follow-ups

1. What's the difference between `onClick` and `onTouchEvent`?
2. How to handle multi-touch (ACTION_POINTER_DOWN/UP)?
3. When does ACTION_CANCEL occur?
4. How to distinguish tap vs long-press vs scroll?
5. What's the difference between `event.x` (view) and `event.rawX` (screen)?

## References

- [[c-view-lifecycle]] — `View` event dispatch mechanism
- [[c-custom-views]] — Custom view patterns
- [Touch & Input](https://developer.android.com/develop/ui/views/touch-and-input/gestures) — Official docs

## Related Questions

### Prerequisites
- [[c-view-lifecycle]]

### Same Level
- [[q-custom-view-animation--android--medium]]
- [[q-list-elements-problems--android--medium]]

### Advanced
- 

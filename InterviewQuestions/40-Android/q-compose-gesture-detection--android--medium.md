---
id: 20251012-122805
title: Compose Gesture Detection / Обработка жестов в Compose
aliases:
- Compose Gesture Detection
- Обработка жестов в Compose
topic: android
subtopics:
- ui-compose
- ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-animated-visibility-vs-content--android--medium
- q-compose-canvas-graphics--android--hard
- q-android-performance-measurement-tools--android--medium
created: 2025-10-11
updated: 2025-10-20
tags:
- android/ui-compose
- android/ui-views
- difficulty/medium
---

# Вопрос (RU)
> Обработка жестов в Compose?

# Question (EN)
> Compose Gesture Detection?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core concepts
- pointerInput: low‑level suspend handlers (detect* helpers)
- Modifiers: `clickable`, `combinedClickable`, `draggable`, `scrollable` for high‑level UX
- Nested scroll: coordinate scroll between parents/children
- Touch slop: thresholds to avoid accidental gesture starts

### Minimal patterns

Taps and long‑press:
```kotlin
Box(Modifier.pointerInput(Unit) {
  detectTapGestures(
    onLongPress = { /* show menu */ },
    onTap = { /* select */ }
  )
})
```

High‑level clickable (ripple, semantics):
```kotlin
Text("Open", Modifier.clickable(onClick = onOpen))
```

Drag with state:
```kotlin
@Composable
fun DraggableBox() {
  var offset by remember { mutableStateOf(Offset.Zero) }
  Box(Modifier.size(80.dp).offset { IntOffset(offset.x.toInt(), offset.y.toInt()) }
    .draggable(orientation = Orientation.Horizontal,
      state = rememberDraggableState { delta -> offset += Offset(delta, 0f) }))
}
```

Scrollable content:
```kotlin
val state = rememberScrollState()
Column(Modifier.verticalScroll(state)) { /* items */ }
```

Nested scroll (parent intercept sample):
```kotlin
val parent = remember {
  object : NestedScrollConnection {
    override fun onPreScroll(available: Offset, source: NestedScrollSource): Offset {
      // consume horizontal first; let child handle vertical
      return Offset(x = available.x, y = 0f)
    }
  }
}
Row(Modifier.nestedScroll(parent)) { /* child scrollables */ }
```

### Performance/UX tips
- Prefer high‑level modifiers (`clickable`, `scrollable`) for built‑in semantics/feedback
- Debounce heavy work; handle gesture callbacks on background when possible
- Avoid allocations inside gesture lambdas; hoist state via remember
- Respect touch slop; don’t block main thread; provide visual feedback (ripple)

## Follow-ups
- How to combine multiple gestures without conflict (e.g., tap vs drag)?
- When to use low‑level pointerInput vs high‑level modifiers?
- How to implement custom nested scroll behaviors?

## References
- [[c-algorithms]] - Gesture recognition and touch event processing
- https://developer.android.com/develop/ui/compose/gestures
- https://developer.android.com/develop/ui/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-animated-visibility-vs-content--android--medium]]

### Related (Same Level)
- [[q-compose-canvas-graphics--android--hard]]
- [[q-compose-compiler-plugin--android--hard]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]

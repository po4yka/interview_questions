---
id: 20251012-122805
title: Compose Gesture Detection / Обработка жестов в Compose
aliases: [Compose Gesture Detection, Обработка жестов в Compose]
topic: android
subtopics: [ui-compose, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-animated-visibility-vs-content--android--medium, q-compose-canvas-graphics--android--hard]
sources: []
created: 2025-10-11
updated: 2025-01-27
tags: [android/ui-compose, android/ui-views, difficulty/medium]
---
# Вопрос (RU)
> Обработка жестов в Compose?

# Question (EN)
> Compose Gesture Detection?

---

## Ответ (RU)

### Основные подходы

Compose предоставляет два уровня для работы с жестами:
- **Модификаторы высокого уровня** (`clickable`, `draggable`, `scrollable`) — встроенная поддержка семантики, ripple-эффектов и доступности
- **pointerInput** — низкоуровневый suspend-блок с detect*-хелперами для сложных сценариев

### Паттерны обработки жестов

Tap и LongPress:
```kotlin
Box(Modifier.pointerInput(Unit) {
  detectTapGestures(
    onLongPress = { /* ✅ контекстное меню */ },
    onTap = { /* ✅ выбор элемента */ }
  )
})
```

Кликабельный элемент:
```kotlin
// ✅ ripple, семантика и доступность из коробки
Text("Открыть", Modifier.clickable(onClick = onOpen))
```

Drag с состоянием:
```kotlin
@Composable
fun DraggableBox() {
  var offset by remember { mutableStateOf(Offset.Zero) }
  Box(
    Modifier
      .size(80.dp)
      .offset { IntOffset(offset.x.toInt(), offset.y.toInt()) }
      .draggable(
        orientation = Orientation.Horizontal,
        state = rememberDraggableState { delta ->
          offset += Offset(delta, 0f) // ✅ изменяем состояние
        }
      )
  )
}
```

Nested scroll:
```kotlin
val parent = remember {
  object : NestedScrollConnection {
    override fun onPreScroll(available: Offset, source: NestedScrollSource): Offset {
      // ✅ родитель перехватывает горизонтальный скролл
      return Offset(x = available.x, y = 0f)
    }
  }
}
Row(Modifier.nestedScroll(parent)) { /* дочерние scrollables */ }
```

### Рекомендации

- Используйте модификаторы высокого уровня для стандартных жестов
- Избегайте аллокаций внутри gesture lambdas — выносите состояние через remember
- Учитывайте touch slop для предотвращения случайных срабатываний
- Обеспечивайте визуальный feedback (ripple, animation)

## Answer (EN)

### Core Approaches

Compose provides two levels for gesture handling:
- **High-level modifiers** (`clickable`, `draggable`, `scrollable`) — built-in semantics, ripple effects, and accessibility
- **pointerInput** — low-level suspend block with detect* helpers for complex scenarios

### Gesture Handling Patterns

Tap and LongPress:
```kotlin
Box(Modifier.pointerInput(Unit) {
  detectTapGestures(
    onLongPress = { /* ✅ context menu */ },
    onTap = { /* ✅ item selection */ }
  )
})
```

Clickable element:
```kotlin
// ✅ ripple, semantics, and accessibility out of the box
Text("Open", Modifier.clickable(onClick = onOpen))
```

Drag with state:
```kotlin
@Composable
fun DraggableBox() {
  var offset by remember { mutableStateOf(Offset.Zero) }
  Box(
    Modifier
      .size(80.dp)
      .offset { IntOffset(offset.x.toInt(), offset.y.toInt()) }
      .draggable(
        orientation = Orientation.Horizontal,
        state = rememberDraggableState { delta ->
          offset += Offset(delta, 0f) // ✅ update state
        }
      )
  )
}
```

Nested scroll:
```kotlin
val parent = remember {
  object : NestedScrollConnection {
    override fun onPreScroll(available: Offset, source: NestedScrollSource): Offset {
      // ✅ parent intercepts horizontal scroll
      return Offset(x = available.x, y = 0f)
    }
  }
}
Row(Modifier.nestedScroll(parent)) { /* child scrollables */ }
```

### Best Practices

- Use high-level modifiers for standard gestures
- Avoid allocations inside gesture lambdas — hoist state via remember
- Account for touch slop to prevent accidental triggers
- Provide visual feedback (ripple, animation)

## Follow-ups
- How to prevent gesture conflicts when combining tap and drag detection?
- What are the performance implications of multiple pointerInput modifiers in the same chain?
- How to implement custom gesture recognition with AwaitPointerEventScope?
- When should you prefer transformable() over individual drag/scale/rotate modifiers?

## References
- https://developer.android.com/develop/ui/compose/gestures
- https://developer.android.com/develop/ui/compose/touch-input

## Related Questions

### Prerequisites (Easier)
- Compose modifier basics and ordering
- State hoisting in Compose

### Related (Same Level)
- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-canvas-graphics--android--hard]]

### Advanced (Harder)
- Custom layout implementation with gesture support
- Performance optimization for complex gesture chains

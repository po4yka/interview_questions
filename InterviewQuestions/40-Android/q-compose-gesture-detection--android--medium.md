---
id: 20251012-122805
title: Compose Gesture Detection / Обработка жестов в Compose
aliases: [Compose Gesture Detection, Обработка жестов в Compose]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-compose-modifiers, q-compose-side-effects--android--medium, q-compose-recomposition--android--hard]
sources: []
created: 2025-10-11
updated: 2025-10-30
tags: [android/ui-compose, android/ui-state, compose, gestures, difficulty/medium]
---

# Вопрос (RU)
> Как обрабатывать жесты в Jetpack Compose?

# Question (EN)
> How to handle gestures in Jetpack Compose?

---

## Ответ (RU)

### Уровни обработки жестов

Compose предоставляет два уровня API:

1. **High-level модификаторы** — встроенные жесты с семантикой и доступностью
2. **pointerInput** — низкоуровневый suspend-блок для кастомной логики

### Базовые модификаторы

```kotlin
// ✅ clickable: ripple, семантика, фокус из коробки
Text(
    "Открыть",
    modifier = Modifier.clickable { onItemClick() }
)

// ✅ draggable: однонаправленный drag с состоянием
var offsetX by remember { mutableStateOf(0f) }
Box(
    Modifier.draggable(
        orientation = Orientation.Horizontal,
        state = rememberDraggableState { delta ->
            offsetX += delta // обновляем offset при перетаскивании
        }
    )
)

// ✅ scrollable: обработка скролла без layout
val scrollState = rememberScrollState()
Column(Modifier.scrollable(scrollState, Orientation.Vertical)) {
    // контент
}
```

### pointerInput и detectTapGestures

Для сложных сценариев (long press, double tap):

```kotlin
Box(
    Modifier.pointerInput(Unit) {
        detectTapGestures(
            onTap = { offset -> /* ✅ обработка клика */ },
            onLongPress = { /* ✅ показ контекстного меню */ },
            onDoubleTap = { /* ✅ зум */ }
        )
    }
)
```

**Важно**: ключ `Unit` сохраняет корутину; если передать зависимость, pointerInput пересоздаётся.

### Drag с многомерным движением

```kotlin
var offset by remember { mutableStateOf(Offset.Zero) }
Box(
    Modifier
        .offset { IntOffset(offset.x.toInt(), offset.y.toInt()) }
        .pointerInput(Unit) {
            detectDragGestures { change, dragAmount ->
                change.consume() // ✅ предотвращаем всплытие
                offset += dragAmount
            }
        }
)
```

### Nested scroll для координации

Когда родитель и дочерний элемент оба scrollable, используйте `NestedScrollConnection`:

```kotlin
val nestedScrollConnection = remember {
    object : NestedScrollConnection {
        override fun onPreScroll(
            available: Offset,
            source: NestedScrollSource
        ): Offset {
            // ✅ родитель перехватывает до дочернего
            return if (available.y < 0) available else Offset.Zero
        }
    }
}
Column(Modifier.nestedScroll(nestedScrollConnection)) { /* ... */ }
```

### Best Practices

- Используйте high-level модификаторы (`clickable`, `draggable`) для стандартных жестов
- Избегайте аллокаций внутри pointerInput — выносите состояние через `remember`
- Учитывайте touch slop — система игнорирует движения < 8dp для предотвращения случайных срабатываний
- Вызывайте `change.consume()` в `detectDragGestures`, чтобы предотвратить всплытие события

## Answer (EN)

### Gesture Handling Levels

Compose provides two API levels:

1. **High-level modifiers** — built-in gestures with semantics and accessibility
2. **pointerInput** — low-level suspend block for custom logic

### Basic Modifiers

```kotlin
// ✅ clickable: ripple, semantics, focus out of the box
Text(
    "Open",
    modifier = Modifier.clickable { onItemClick() }
)

// ✅ draggable: unidirectional drag with state
var offsetX by remember { mutableStateOf(0f) }
Box(
    Modifier.draggable(
        orientation = Orientation.Horizontal,
        state = rememberDraggableState { delta ->
            offsetX += delta // update offset on drag
        }
    )
)

// ✅ scrollable: scroll handling without layout
val scrollState = rememberScrollState()
Column(Modifier.scrollable(scrollState, Orientation.Vertical)) {
    // content
}
```

### pointerInput and detectTapGestures

For complex scenarios (long press, double tap):

```kotlin
Box(
    Modifier.pointerInput(Unit) {
        detectTapGestures(
            onTap = { offset -> /* ✅ handle tap */ },
            onLongPress = { /* ✅ show context menu */ },
            onDoubleTap = { /* ✅ zoom */ }
        )
    }
)
```

**Important**: key `Unit` persists the coroutine; if you pass a dependency, pointerInput recreates.

### Drag with Multi-dimensional Movement

```kotlin
var offset by remember { mutableStateOf(Offset.Zero) }
Box(
    Modifier
        .offset { IntOffset(offset.x.toInt(), offset.y.toInt()) }
        .pointerInput(Unit) {
            detectDragGestures { change, dragAmount ->
                change.consume() // ✅ prevent event bubbling
                offset += dragAmount
            }
        }
)
```

### Nested Scroll for Coordination

When parent and child are both scrollable, use `NestedScrollConnection`:

```kotlin
val nestedScrollConnection = remember {
    object : NestedScrollConnection {
        override fun onPreScroll(
            available: Offset,
            source: NestedScrollSource
        ): Offset {
            // ✅ parent intercepts before child
            return if (available.y < 0) available else Offset.Zero
        }
    }
}
Column(Modifier.nestedScroll(nestedScrollConnection)) { /* ... */ }
```

### Best Practices

- Use high-level modifiers (`clickable`, `draggable`) for standard gestures
- Avoid allocations inside pointerInput — hoist state via `remember`
- Account for touch slop — system ignores movements < 8dp to prevent accidental triggers
- Call `change.consume()` in `detectDragGestures` to prevent event bubbling

## Follow-ups

- How to prevent gesture conflicts when combining tap and drag detection in the same composable?
- What is the role of `change.consume()` in custom gesture handling?
- How does `transformable` modifier work for multi-touch gestures (pinch, pan, rotate)?
- When to use `AwaitPointerEventScope` directly instead of detect* helpers?
- How does nested scroll cooperation affect performance in deeply nested lists?

## References

- [[c-compose-modifiers]]
- [[c-compose-state]]
- https://developer.android.com/develop/ui/compose/touch-input/pointer-input
- https://developer.android.com/develop/ui/compose/touch-input/gestures

## Related Questions

### Prerequisites (Easier)
- [[q-compose-modifiers-order--android--easy]]
- [[q-compose-state-hoisting--android--easy]]

### Related (Same Level)
- [[q-compose-side-effects--android--medium]]
- [[q-compose-recomposition--android--hard]]

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-performance-optimization--android--hard]]

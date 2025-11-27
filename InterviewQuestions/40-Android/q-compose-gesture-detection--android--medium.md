---
id: android-038
title: Compose Gesture Detection / Обработка жестов в Compose
aliases: [Compose Gesture Detection, Обработка жестов в Compose]
topic: android
subtopics:
  - ui-compose
  - ui-state
question_kind: android
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
  - q-compose-semantics--android--medium
  - q-mutable-state-compose--android--medium
  - q-recomposition-compose--android--medium
sources: []
created: 2025-10-11
updated: 2025-11-10
tags: [android/ui-compose, android/ui-state, compose, difficulty/medium, gestures]
date created: Saturday, November 1st 2025, 1:24:40 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---
# Вопрос (RU)
> Как обрабатывать жесты в Jetpack Compose?

# Question (EN)
> How to handle gestures in Jetpack Compose?

---

## Ответ (RU)

### Уровни Обработки Жестов

Compose предоставляет два уровня API:

1. **High-level модификаторы** — встроенные жесты с семантикой и поддержкой доступности
2. **pointerInput** — низкоуровневый suspend-блок для кастомной логики

### Базовые Модификаторы

```kotlin
// ✅ clickable: семантика, фокус, поддержка accessibility; визуальный эффект зависит от темы/indication
Text(
    "Открыть",
    modifier = Modifier.clickable { onItemClick() }
)

// ✅ draggable: однонаправленный drag с состоянием
var offsetX by remember { mutableStateOf(0f) }
Box(
    Modifier
        .offset { IntOffset(offsetX.toInt(), 0) } // применяем сдвиг
        .draggable(
            orientation = Orientation.Horizontal,
            state = rememberDraggableState { delta ->
                offsetX += delta // обновляем offset при перетаскивании
            }
        )
)

// ✅ verticalScroll: вертикальный скролл с ScrollState
val scrollState = rememberScrollState()
Column(
    modifier = Modifier.verticalScroll(scrollState)
) {
    // контент
}
```

### pointerInput И detectTapGestures

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

**Важно**: ключ в `pointerInput` определяет, когда блок будет перезапущен (корутина будет отменена и создана заново). При использовании `Unit` блок сохраняется, пока composable в композиции; при передаче зависимости `pointerInput` будет пересоздаваться при её изменении.

### Drag С Многомерным Движением

```kotlin
var offset by remember { mutableStateOf(Offset.Zero) }
Box(
    Modifier
        .offset { IntOffset(offset.x.toInt(), offset.y.toInt()) }
        .pointerInput(Unit) {
            detectDragGestures { change, dragAmount ->
                change.consume() // ✅ помечаем событие как использованное этим жестом (подавляем конкурентов)
                offset += dragAmount
            }
        }
)
```

### Nested Scroll Для Координации

Когда родитель и дочерний элемент оба scrollable, используйте `NestedScrollConnection`:

```kotlin
val nestedScrollConnection = remember {
    object : NestedScrollConnection {
        override fun onPreScroll(
            available: Offset,
            source: NestedScrollSource
        ): Offset {
            // ✅ пример: родитель перехватывает восходящий скролл
            return if (available.y < 0) available else Offset.Zero
        }
    }
}
Column(Modifier.nestedScroll(nestedScrollConnection)) { /* ... */ }
```

### Best Practices

- Используйте high-level модификаторы (`clickable`, `draggable`) для стандартных жестов
- Избегайте аллокаций внутри `pointerInput` — выносите состояние через `remember`
- Учитывайте touch slop — система игнорирует очень малые движения (порядка 8dp) для предотвращения случайных срабатываний
- Вызывайте `change.consume()` (или соответствующий consume-метод) в `detectDragGestures`, когда хотите пометить событие как обработанное данным жестом

## Answer (EN)

### Gesture Handling Levels

Compose provides two API levels:

1. **High-level modifiers** — built-in gestures with semantics and accessibility
2. **pointerInput** — low-level suspend block for custom logic

### Basic Modifiers

```kotlin
// ✅ clickable: semantics, focus, accessibility support; visual effect depends on theme/indication
Text(
    "Open",
    modifier = Modifier.clickable { onItemClick() }
)

// ✅ draggable: unidirectional drag with state
var offsetX by remember { mutableStateOf(0f) }
Box(
    Modifier
        .offset { IntOffset(offsetX.toInt(), 0) } // apply offset
        .draggable(
            orientation = Orientation.Horizontal,
            state = rememberDraggableState { delta ->
                offsetX += delta // update offset on drag
            }
        )
)

// ✅ verticalScroll: vertical scroll with ScrollState
val scrollState = rememberScrollState()
Column(
    modifier = Modifier.verticalScroll(scrollState)
) {
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

**Important**: the key passed to `pointerInput` controls when its block is restarted (coroutine cancelled and recreated). With `Unit`, it stays active as long as the composable is in the composition; with a changing dependency, `pointerInput` will be recreated whenever that dependency changes.

### Drag with Multi-dimensional Movement

```kotlin
var offset by remember { mutableStateOf(Offset.Zero) }
Box(
    Modifier
        .offset { IntOffset(offset.x.toInt(), offset.y.toInt()) }
        .pointerInput(Unit) {
            detectDragGestures { change, dragAmount ->
                change.consume() // ✅ mark event as used by this gesture (suppress competitors)
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
            // ✅ example: parent intercepts upward scroll
            return if (available.y < 0) available else Offset.Zero
        }
    }
}
Column(Modifier.nestedScroll(nestedScrollConnection)) { /* ... */ }
```

### Best Practices

- Use high-level modifiers (`clickable`, `draggable`) for standard gestures
- Avoid allocations inside `pointerInput` — hoist state via `remember`
- Account for touch slop — the system ignores very small movements (around 8dp) to prevent accidental triggers
- Call `change.consume()` (or appropriate consume method) in `detectDragGestures` when you want to mark the event as handled by that gesture

## Дополнительные Вопросы (RU)

- Как предотвратить конфликты жестов при комбинировании обработки нажатий и перетаскиваний в одном composable?
- Какова роль `change.consume()` в кастомной обработке жестов?
- Как работает модификатор `transformable` для мультитач-жестов (pinch, pan, rotate)?
- Когда стоит использовать `AwaitPointerEventScope` напрямую вместо detect* хелперов?
- Как кооперация nested scroll влияет на производительность в глубоко вложенных списках?

## Follow-ups

- How to prevent gesture conflicts when combining tap and drag detection in the same composable?
- What is the role of `change.consume()` in custom gesture handling?
- How does `transformable` modifier work for multi-touch gestures (pinch, pan, rotate)?
- When to use `AwaitPointerEventScope` directly instead of detect* helpers?
- How does nested scroll cooperation affect performance in deeply nested lists?

## Ссылки (RU)

- [[c-compose-state]]
- https://developer.android.com/develop/ui/compose/touch-input/pointer-input
- https://developer.android.com/develop/ui/compose/touch-input/gestures

## References

- [[c-compose-state]]
- https://developer.android.com/develop/ui/compose/touch-input/pointer-input
- https://developer.android.com/develop/ui/compose/touch-input/gestures

## Связанные Вопросы (RU)

### Предпосылки (проще)

### Связанные (средний уровень)

### Продвинутые (сложнее)
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-performance-optimization--android--hard]]

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]]
- [[q-compose-performance-optimization--android--hard]]

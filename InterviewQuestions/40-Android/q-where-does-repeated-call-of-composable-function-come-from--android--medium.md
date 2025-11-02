---
id: android-327
title: "Where Does Repeated Call Of Composable Function Come From / Откуда берется повторный вызов Composable функции"
aliases: ["Where Does Repeated Call Of Composable Function Come From", "Откуда берется повторный вызов Composable функции"]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-does-jetpackcompose-work--android--medium, q-compose-stability-skippability--android--hard, q-compose-performance-optimization--android--hard]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android, android/ui-compose, android/ui-state, compose, recomposition, difficulty/medium]
date created: Wednesday, October 29th 2025, 12:15:21 pm
date modified: Thursday, October 30th 2025, 3:18:08 pm
---

# Вопрос (RU)

> Откуда происходит повторный вызов composable функции?

# Question (EN)

> Where does the repeated call of a composable function come from?

---

## Ответ (RU)

Повторный вызов происходит из механизма **recomposition**. Compose автоматически вызывает функцию снова, если состояние, связанное с этой функцией, изменилось.

### Как работает Recomposition

```kotlin
@Composable
fun Counter() {
    // ✅ Изменение state запускает recomposition
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count") // Перерисовывается при изменении count

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Процесс**:
1. Compose отслеживает чтение `count`
2. При изменении помечает `Counter()` как недействительный
3. Перевызывает `Counter()` для обновления UI

### Источники Recomposition

```kotlin
@Composable
fun RecompositionSources(viewModel: MyViewModel) {
    // 1. State - локальное состояние
    var text by remember { mutableStateOf("") }

    // 2. Flow/StateFlow из ViewModel
    val uiState by viewModel.uiState.collectAsState()

    // 3. LiveData
    val data by viewModel.liveData.observeAsState()

    Column {
        Text(text)           // ✅ Перерисуется при изменении text
        Text(uiState.message) // ✅ Перерисуется при изменении uiState
        Text(data ?: "")      // ✅ Перерисуется при изменении data
    }
}
```

**Основные триггеры**:
- Изменения `mutableStateOf`
- Обновления `Flow/StateFlow` через `collectAsState()`
- Обновления `LiveData` через `observeAsState()`
- Recomposition родительского composable

### Оптимизация с derivedStateOf

```kotlin
@Composable
fun OptimizedRecomposition() {
    var count by remember { mutableStateOf(0) }

    // ❌ Без derivedStateOf - лишние recomposition
    val isEvenBad = count % 2 == 0

    // ✅ С derivedStateOf - перерисовка только при изменении результата
    val isEven by remember {
        derivedStateOf { count % 2 == 0 }
    }

    Column {
        Text("Count: $count")    // Recomposition на каждое изменение
        Text("Even: $isEven")    // Recomposition только при 0→1→2→3...
    }
}
```

---

## Answer (EN)

The repeated call comes from the **recomposition** mechanism. Compose automatically calls the function again if the state associated with this function has changed.

### How Recomposition Works

```kotlin
@Composable
fun Counter() {
    // ✅ State change triggers recomposition
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count") // Redrawn when count changes

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Process**:
1. Compose tracks reads of `count`
2. When changed, marks `Counter()` as invalid
3. Re-executes `Counter()` to update UI

### Recomposition Sources

```kotlin
@Composable
fun RecompositionSources(viewModel: MyViewModel) {
    // 1. State - local state
    var text by remember { mutableStateOf("") }

    // 2. Flow/StateFlow from ViewModel
    val uiState by viewModel.uiState.collectAsState()

    // 3. LiveData
    val data by viewModel.liveData.observeAsState()

    Column {
        Text(text)           // ✅ Recomposes when text changes
        Text(uiState.message) // ✅ Recomposes when uiState changes
        Text(data ?: "")      // ✅ Recomposes when data changes
    }
}
```

**Main Triggers**:
- Changes to `mutableStateOf`
- Updates to `Flow/StateFlow` via `collectAsState()`
- Updates to `LiveData` via `observeAsState()`
- Parent composable recomposition

### Optimizing with derivedStateOf

```kotlin
@Composable
fun OptimizedRecomposition() {
    var count by remember { mutableStateOf(0) }

    // ❌ Without derivedStateOf - unnecessary recomposition
    val isEvenBad = count % 2 == 0

    // ✅ With derivedStateOf - recomposition only when result changes
    val isEven by remember {
        derivedStateOf { count % 2 == 0 }
    }

    Column {
        Text("Count: $count")    // Recomposition on every change
        Text("Even: $isEven")    // Recomposition only at 0→1→2→3...
    }
}
```

---

## Follow-ups

1. How does Compose determine which specific composables to recompose (smart recomposition scope)?
2. What is the difference between `remember` and `rememberSaveable` in terms of recomposition?
3. How can you prevent unnecessary recompositions when passing lambdas as parameters?
4. What role does structural equality play in skipping recomposition?
5. How do snapshot state observers work internally to detect state changes?

## References

- https://developer.android.com/develop/ui/compose/lifecycle - Compose lifecycle
- https://developer.android.com/develop/ui/compose/performance - Performance best practices
- https://developer.android.com/develop/ui/compose/state - State and recomposition

## Related Questions

### Prerequisites (Easier)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose basics

### Related (Same Level)
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose architecture
- [[q-compose-modifier-order-performance--android--medium]] - Performance optimization
- [[q-compositionlocal-advanced--android--medium]] - State propagation

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability inference
- [[q-compose-performance-optimization--android--hard]] - Advanced optimization
- [[q-compose-custom-layout--android--hard]] - Custom layouts and recomposition

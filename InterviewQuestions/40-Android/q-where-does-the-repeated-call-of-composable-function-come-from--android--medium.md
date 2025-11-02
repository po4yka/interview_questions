---
id: android-422
title: "Where Does The Repeated Call Of Composable Function Come From / Откуда берется повторный вызов Composable функции"
aliases: ["Recomposition in Compose", "Where Does The Repeated Call Of Composable Function Come From", "Откуда берется повторный вызов Composable функции", "Рекомпозиция в Compose"]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-compose-stability-skippability--android--hard, q-how-does-jetpackcompose-work--android--medium]
created: 2025-10-15
updated: 2025-10-29
sources: []
tags: [android/ui-compose, android/ui-state, compose, difficulty/medium, jetpack-compose, recomposition]
date created: Wednesday, October 29th 2025, 12:15:30 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)

> Откуда происходит повторный вызов composable функции в Jetpack Compose?

# Question (EN)

> Where does the repeated call of composable function come from in Jetpack Compose?

---

## Ответ (RU)

Повторный вызов composable функции происходит из механизма **рекомпозиции (recomposition)**. Compose автоматически отслеживает чтение состояния внутри composable и помечает функцию как "невалидную" при изменении этого состояния, что запускает её повторное выполнение.

### Механизм Рекомпозиции

```kotlin
@Composable
fun Counter() {
    // ✅ State read triggers subscription
    var count by remember { mutableStateOf(0) }

    Column {
        // When count changes: Compose re-executes Counter()
        Text("Count: $count")
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

**Процесс**:
1. Compose отслеживает чтение `count` внутри `Text()`
2. При изменении `count` (клик кнопки) функция помечается невалидной
3. Compose планирует рекомпозицию на следующий фрейм
4. Функция `Counter()` выполняется снова, обновляя только изменённые части UI

### Источники Рекомпозиции

```kotlin
@Composable
fun TriggerSources(viewModel: MyViewModel) {
    // ✅ 1. Local state
    var text by remember { mutableStateOf("") }

    // ✅ 2. StateFlow/Flow
    val uiState by viewModel.uiState.collectAsState()

    // ✅ 3. LiveData (requires observeAsState)
    val data by viewModel.liveData.observeAsState()

    // Any read triggers subscription to that state
    Column {
        Text(text)
        Text(uiState.message)
    }
}
```

### Область Рекомпозиции (Scope)

Compose минимизирует рекомпозицию — перевыполняются только те composable, которые читают изменённое состояние:

```kotlin
@Composable
fun ScopedRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        // ✅ Recomposes when count changes
        Text("Count: $count")

        // ✅ Never recomposes (no state dependency)
        Text("Static text")

        Button(onClick = { count++ }) { Text("Click") }
    }
}
```

### Оптимизация: derivedStateOf

```kotlin
@Composable
fun OptimizedExample() {
    var count by remember { mutableStateOf(0) }

    // ✅ Recomposes only when parity changes (not on every count)
    val isEven by remember { derivedStateOf { count % 2 == 0 } }

    Column {
        Text("Count: $count")        // Recomposes every time
        Text("Is even: $isEven")     // Recomposes every 2nd time
    }
}
```

## Answer (EN)

The repeated call of a composable function comes from the **recomposition** mechanism. Compose automatically tracks state reads inside composables and marks the function as "invalid" when that state changes, triggering its re-execution.

### Recomposition Mechanism

```kotlin
@Composable
fun Counter() {
    // ✅ State read triggers subscription
    var count by remember { mutableStateOf(0) }

    Column {
        // When count changes: Compose re-executes Counter()
        Text("Count: $count")
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

**Process**:
1. Compose tracks the read of `count` inside `Text()`
2. When `count` changes (button click), the function is marked invalid
3. Compose schedules recomposition for the next frame
4. `Counter()` executes again, updating only changed UI parts

### Recomposition Trigger Sources

```kotlin
@Composable
fun TriggerSources(viewModel: MyViewModel) {
    // ✅ 1. Local state
    var text by remember { mutableStateOf("") }

    // ✅ 2. StateFlow/Flow
    val uiState by viewModel.uiState.collectAsState()

    // ✅ 3. LiveData (requires observeAsState)
    val data by viewModel.liveData.observeAsState()

    // Any read triggers subscription to that state
    Column {
        Text(text)
        Text(uiState.message)
    }
}
```

### Recomposition Scope

Compose minimizes recomposition — only composables that read the changed state are re-executed:

```kotlin
@Composable
fun ScopedRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        // ✅ Recomposes when count changes
        Text("Count: $count")

        // ✅ Never recomposes (no state dependency)
        Text("Static text")

        Button(onClick = { count++ }) { Text("Click") }
    }
}
```

### Optimization: derivedStateOf

```kotlin
@Composable
fun OptimizedExample() {
    var count by remember { mutableStateOf(0) }

    // ✅ Recomposes only when parity changes (not on every count)
    val isEven by remember { derivedStateOf { count % 2 == 0 } }

    Column {
        Text("Count: $count")        // Recomposes every time
        Text("Is even: $isEven")     // Recomposes every 2nd time
    }
}
```

---

## Follow-ups

- How does Compose determine which composables to recompose (smart recomposition)?
- What is the difference between `remember` and `rememberSaveable`?
- How does `derivedStateOf` reduce recomposition frequency?
- What are stable vs unstable types in the context of Compose skipping?
- How can you debug unnecessary recompositions in your app?

## References

- [[c-jetpack-compose]] - Core concepts of declarative UI
- [Compose Lifecycle Documentation](https://developer.android.com/jetpack/compose/lifecycle)
- [State and Recomposition](https://developer.android.com/jetpack/compose/state)
- [Performance Best Practices](https://developer.android.com/jetpack/compose/performance)

## Related Questions

### Prerequisites (Easier)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose fundamentals

### Related (Same Level)
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose architecture
- [[q-compose-modifier-order-performance--android--medium]] - Modifier system
- [[q-compositionlocal-advanced--android--medium]] - State propagation

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Skipping optimization
- [[q-compose-performance-optimization--android--hard]] - Advanced optimization
- [[q-compose-custom-layout--android--hard]] - Custom layout

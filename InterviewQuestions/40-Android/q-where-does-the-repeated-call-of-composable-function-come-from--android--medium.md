---
id: "20251015082238640"
title: "Where Does The Repeated Call Of Composable Function Come From / Откуда берется повторный вызов Composable функции"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [recomposition, android, ui, jetpack-compose, difficulty/medium]
---
# Where does the repeated call of composable function come from?

# Вопрос (RU)

Откуда происходит повторный вызов composable функции

## Answer (EN)
The repeated call comes from the **recomposition** mechanism. Compose automatically calls the function again if the state associated with this function has changed.

### How Recomposition Works

```kotlin
@Composable
fun Counter() {
    // State change triggers recomposition
    var count by remember { mutableStateOf(0) }

    Column {
        // This composable is called again when count changes
        Text("Count: $count")

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}

// When count changes from 0 to 1:
// 1. Compose detects state change
// 2. Marks Counter() as invalid
// 3. Re-executes Counter()
// 4. Only Text showing count is redrawn
```

### Recomposition Trigger Sources

1. **State Changes (mutableStateOf)**
2. **Flow/LiveData updates (collectAsState)**
3. **Parent recomposition**
4. **Configuration changes**

```kotlin
@Composable
fun RecompositionSources(viewModel: MyViewModel) {
    // 1. State change
    var text by remember { mutableStateOf("") }

    // 2. Flow/StateFlow
    val uiState by viewModel.uiState.collectAsState()

    // 3. LiveData
    val data by viewModel.liveData.observeAsState()

    // Any change triggers recomposition
    Column {
        Text(text)
        Text(uiState.message)
        Text(data?.toString() ?: "")
    }
}
```

### Recomposition Scope

```kotlin
@Composable
fun ScopedRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        // Only this Text recomposes when count changes
        Text("Count: $count")

        // This never recomposes (no state dependency)
        Text("Static text")

        Button(onClick = { count++ }) {
            // This recomposes only if we use count inside
            Text("Clicked") // Static - no recomposition
        }
    }
}
```

### Preventing Unnecessary Recomposition

```kotlin
@Composable
fun OptimizedRecomposition() {
    var count by remember { mutableStateOf(0) }

    // Use derivedStateOf to limit recomposition
    val isEven by remember {
        derivedStateOf { count % 2 == 0 }
    }

    Column {
        Text("Count: $count") // Recomposes on every change

        // Only recomposes when isEven changes (every 2 counts)
        Text("Is even: $isEven")

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

## Ответ (RU)

Повторный вызов происходит из механизма recomposition. Compose автоматически вызывает функцию снова, если состояние связанное с этой функцией изменилось

---

## Related Questions

### Related (Medium)
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Compose
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose
- [[q-accessibility-compose--accessibility--medium]] - Compose

### Advanced (Harder)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose
- [[q-compose-performance-optimization--android--hard]] - Compose

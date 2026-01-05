---
id: android-327
title: Where Does Repeated Call Of Composable Function Come From / Откуда берется
  повторный вызов Composable функции
aliases: [Where Does Repeated Call Of Composable Function Come From, Откуда берется повторный вызов Composable функции]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-jetpack-compose, c-viewmodel, q-compose-performance-optimization--android--hard, q-compose-stability-skippability--android--hard, q-how-dialog-differs-from-other-navigation--android--medium, q-how-does-jetpackcompose-work--android--medium, q-where-does-the-repeated-call-of-composable-function-come-from--android--medium, q-where-is-composition-created-for-calling-composable-function--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android, android/ui-compose, android/ui-state, compose, difficulty/medium, recomposition]
---
# Вопрос (RU)

> Откуда происходит повторный вызов composable функции?

# Question (EN)

> Where does the repeated call of a composable function come from?

---

## Ответ (RU)

Повторный вызов происходит из механизма **recomposition**. Compose автоматически вызывает функцию снова, когда отслеживаемое ею состояние изменилось.

### Как Работает Recomposition

```kotlin
@Composable
fun Counter() {
    // ✅ Изменение state запускает recomposition
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count") // Перечитывается при изменении count

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Процесс**:
1. Compose отслеживает чтения `count` в composable-функции.
2. При изменении состояния помечает соответствующую область композиции как недействительную.
3. Запускает recomposition и повторно вызывает нужные composable-функции для обновления UI.

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
        Text(text)            // ✅ Перерисуется при изменении text
        Text(uiState.message) // ✅ Перерисуется при изменении uiState
        Text(data ?: "")      // ✅ Перерисуется при изменении data
    }
}
```

**Основные триггеры**:
- Изменения `mutableStateOf`
- Обновления `Flow/StateFlow` через `collectAsState()`
- Обновления `LiveData` через `observeAsState()`
- Recomposition родительского composable (ребенок будет пересоздан в рамках его области)

### Оптимизация С `derivedStateOf`

```kotlin
@Composable
fun OptimizedRecomposition() {
    var count by remember { mutableStateOf(0) }

    // Прямой расчет: выполняется на каждый вызов composable
    val isEvenBad = count % 2 == 0

    // ✅ С derivedStateOf: значение пересчитывается при изменении count,
    // и recomposition зависимых мест будет запущена только если результат действительно изменился
    val isEven by remember {
        derivedStateOf { count % 2 == 0 }
    }

    Column {
        Text("Count: $count")    // Recomposition при каждом изменении count
        Text("Even (bad): $isEvenBad")
        Text("Even (good): $isEven")
    }
}
```

Важно: `derivedStateOf` не отменяет recomposition, вызванную изменением `count`. Оно помогает избежать лишних уведомлений и перерасчетов для производных значений, когда сам результат не меняется (по структурному равенству), и тем самым может сократить количество затронутых composable-элементов.

---

## Answer (EN)

The repeated call comes from the **recomposition** mechanism. Compose automatically calls the function again when the state it reads and depends on has changed.

### How Recomposition Works

```kotlin
@Composable
fun Counter() {
    // ✅ State change triggers recomposition
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count") // Re-read when count changes

        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

**Process**:
1. Compose tracks reads of `count` inside the composable.
2. When the state changes, it marks the corresponding composition scope as invalid.
3. It runs recomposition and re-executes the affected composables to update the UI.

### Recomposition Sources

```kotlin
@Composable
fun RecompositionSources(viewModel: MyViewModel) {
    // 1. Local state
    var text by remember { mutableStateOf("") }

    // 2. Flow/StateFlow from ViewModel
    val uiState by viewModel.uiState.collectAsState()

    // 3. LiveData
    val data by viewModel.liveData.observeAsState()

    Column {
        Text(text)            // ✅ Recomposes when text changes
        Text(uiState.message) // ✅ Recomposes when uiState changes
        Text(data ?: "")      // ✅ Recomposes when data changes
    }
}
```

**Main Triggers**:
- Changes to `mutableStateOf`
- Updates to `Flow/StateFlow` via `collectAsState()`
- Updates to `LiveData` via `observeAsState()`
- Parent composable recomposition (children in its scope will be recomposed as needed)

### Optimizing with `derivedStateOf`

```kotlin
@Composable
fun OptimizedRecomposition() {
    var count by remember { mutableStateOf(0) }

    // Direct computation: executed on every composable invocation
    val isEvenBad = count % 2 == 0

    // ✅ With derivedStateOf: the value is recomputed when count changes,
    // and dependents are only notified if the result actually changes
    val isEven by remember {
        derivedStateOf { count % 2 == 0 }
    }

    Column {
        Text("Count: $count")      // Recomposition on each count change
        Text("Even (bad): $isEvenBad")
        Text("Even (good): $isEven")
    }
}
```

Important: `derivedStateOf` does not prevent recomposition triggered by changes of `count` itself. It helps avoid extra invalidations and recompositions for dependents when the derived value remains equal (by structural equality), which can reduce the number of affected composables.

---

## Дополнительные Вопросы (RU)

1. Как Compose определяет, какие конкретные composable-функции нужно перерассчитать (механизм "умных" областей recomposition)?
2. В чем разница между `remember` и `rememberSaveable` с точки зрения recomposition?
3. Как избежать лишних recomposition при передаче лямбда-выражений как параметров?
4. Какую роль играет структурное равенство при пропуске recomposition?
5. Как внутренне работают наблюдатели snapshot-состояния для отслеживания изменений?

## Follow-ups

1. How does Compose determine which specific composables to recompose (smart recomposition scope)?
2. What is the difference between `remember` and `rememberSaveable` in terms of recomposition?
3. How can you prevent unnecessary recompositions when passing lambdas as parameters?
4. What role does structural equality play in skipping recomposition?
5. How do snapshot state observers work internally to detect state changes?

## Источники (RU)

- https://developer.android.com/develop/ui/compose/lifecycle - Жизненный цикл Compose
- https://developer.android.com/develop/ui/compose/performance - Рекомендации по производительности
- https://developer.android.com/develop/ui/compose/state - Состояние и recomposition

## References

- https://developer.android.com/develop/ui/compose/lifecycle - Compose lifecycle
- https://developer.android.com/develop/ui/compose/performance - Performance best practices
- https://developer.android.com/develop/ui/compose/state - State and recomposition

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]
- [[c-viewmodel]]

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

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
related: [c-compose-recomposition, q-how-does-jetpackcompose-work--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/ui-compose, android/ui-state, compose, difficulty/medium, jetpack-compose, recomposition]
date created: Saturday, November 1st 2025, 12:47:10 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Откуда происходит повторный вызов composable функции в Jetpack Compose?

# Question (EN)

> Where does the repeated call of composable function come from in Jetpack Compose?

---

## Ответ (RU)

Повторный вызов composable функции происходит из механизма **рекомпозиции (recomposition)**. Compose автоматически отслеживает чтение состояния внутри composable во время композиции и при изменении этого состояния помечает соответствующие участки дерева композиции как "невалидные", планируя их повторное выполнение.

### Механизм Рекомпозиции

```kotlin
@Composable
fun Counter() {
    // ✅ Чтение состояния регистрирует подписку на его изменения в текущей области композиции
    var count by remember { mutableStateOf(0) }

    Column {
        // При изменении count соответствующая часть композиции помечается для рекомпозиции
        Text("Count: $count")
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

**Процесс**:
1. При первой композиции Compose отслеживает чтение `count` внутри `Text("Count: $count")`.
2. При изменении `count` (клик по кнопке) эта область композиции помечается как невалидная.
3. Compose планирует рекомпозицию (обычно к следующему кадру).
4. Соответствующая часть UI выполняется заново; Compose старается переиспользовать неизменившиеся элементы и минимизировать объём работы.

### Источники Рекомпозиции

```kotlin
@Composable
fun TriggerSources(viewModel: MyViewModel) {
    // ✅ 1. Локальное состояние
    var text by remember { mutableStateOf("") }

    // ✅ 2. StateFlow/Flow (через collectAsState/collectAsStateWithLifecycle и т.п.)
    val uiState by viewModel.uiState.collectAsState()

    // ✅ 3. LiveData (через observeAsState)
    val data by viewModel.liveData.observeAsState()

    // Подписка на изменения возникает только для того состояния,
    // значения которого реально читаются в составе композиции.
    Column {
        Text(text)
        Text(uiState.message)
        // data также может участвовать в рекомпозиции, если будет прочитано в UI
    }
}
```

### Область Рекомпозиции (Recomposition Scope)

Compose минимизирует рекомпозицию — повторно выполняются только те composable или их части, которые зависят от изменившегося состояния в их области композиции.

```kotlin
@Composable
fun ScopedRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        // ✅ Рекомпозируется при изменении count
        Text("Count: $count")

        // ✅ Не рекомпозируется из-за изменения count,
        // так как не читает это состояние (может быть пересоздано по другим причинам)
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

    // ✅ Рекомпозиция потребителей isEven происходит только тогда,
    // когда меняется результат вычисления (четность), а не при каждом значении count,
    // если derivedStateOf используется корректно в нужной области.
    val isEven by remember { derivedStateOf { count % 2 == 0 } }

    Column {
        Text("Count: $count")        // Рекомпозируется при каждом изменении count
        Text("Is even: $isEven")     // Эффективно обновляется при изменении четности
    }
}
```

См. также: [[c-compose-recomposition]]

## Answer (EN)

The repeated call of a composable function comes from the **recomposition** mechanism. During composition, Compose tracks state reads inside composables; when that state changes, it marks the corresponding parts of the composition as invalid and schedules them for re-execution.

### Recomposition Mechanism

```kotlin
@Composable
fun Counter() {
    // ✅ Reading this state registers a subscription for changes in this composition scope
    var count by remember { mutableStateOf(0) }

    Column {
        // When count changes, the affected part of the composition is marked for recomposition
        Text("Count: $count")
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

**Process**:
1. On the initial composition, Compose tracks the read of `count` inside `Text("Count: $count")`.
2. When `count` changes (button click), that region of the composition is marked invalid.
3. Compose schedules recomposition (typically for the next frame).
4. The relevant UI is executed again; Compose tries to reuse unchanged nodes and minimize the work.

### Recomposition Trigger Sources

```kotlin
@Composable
fun TriggerSources(viewModel: MyViewModel) {
    // ✅ 1. Local state
    var text by remember { mutableStateOf("") }

    // ✅ 2. StateFlow/Flow via collectAsState/collectAsStateWithLifecycle, etc.
    val uiState by viewModel.uiState.collectAsState()

    // ✅ 3. LiveData via observeAsState
    val data by viewModel.liveData.observeAsState()

    // Subscription and recomposition are driven only by state values
    // that are actually read as part of the composition.
    Column {
        Text(text)
        Text(uiState.message)
        // data can also drive recomposition when read in the UI
    }
}
```

### Recomposition Scope

Compose minimizes recomposition — only composables or parts of them that depend on the changed state in their composition scope are re-executed.

```kotlin
@Composable
fun ScopedRecomposition() {
    var count by remember { mutableStateOf(0) }

    Column {
        // ✅ Recomposes when count changes
        Text("Count: $count")

        // ✅ Does not recompose because of count changes,
        // since it does not read that state (it may be recomposed for other reasons)
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

    // ✅ Consumers of isEven recompose only when the computed value changes
    // (parity), not on every intermediate count value, assuming derivedStateOf
    // is used in the correct scope.
    val isEven by remember { derivedStateOf { count % 2 == 0 } }

    Column {
        Text("Count: $count")        // Recomputes on every count change
        Text("Is even: $isEven")     // Efficiently updates when parity changes
    }
}
```

See also: [[c-compose-recomposition]]

---

## Дополнительные Вопросы (RU)

- Как Compose определяет, какие composable нужно рекомпозировать (механизм "умной" рекомпозиции)?
- В чем разница между `remember` и `rememberSaveable`?
- Как `derivedStateOf` помогает сократить частоту рекомпозиций?
- Что такое стабильные и нестабильные типы в контексте пропуска (skipping) в Compose?
- Как отлаживать и выявлять лишние рекомпозиции в приложении?

## Follow-ups

- How does Compose determine which composables to recompose (smart recomposition)?
- What is the difference between `remember` and `rememberSaveable`?
- How does `derivedStateOf` reduce recomposition frequency?
- What are stable vs unstable types in the context of Compose skipping?
- How can you debug unnecessary recompositions in your app?

## Ссылки (RU)

- "Compose Lifecycle Documentation" - документация по жизненному циклу Compose
- "State and Recomposition" - документация по состоянию и рекомпозиции
- "Performance Best Practices" - рекомендации по производительности в Compose

## References

- [Compose Lifecycle Documentation](https://developer.android.com/jetpack/compose/lifecycle)
- [State and Recomposition](https://developer.android.com/jetpack/compose/state)
- [Performance Best Practices](https://developer.android.com/jetpack/compose/performance)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Базовые принципы Compose

### Похожие (средний уровень)
- [[q-how-does-jetpackcompose-work--android--medium]] - Архитектура Compose
- [[q-compose-modifier-order-performance--android--medium]] - Система модификаторов

### Продвинутые (сложнее)
- [[q-compose-stability-skippability--android--hard]] - Оптимизация пропусков (skipping)
- [[q-compose-performance-optimization--android--hard]] - Продвинутая оптимизация
- [[q-compose-custom-layout--android--hard]] - Пользовательские Layout'ы

## Related Questions

### Prerequisites (Easier)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Compose fundamentals

### Related (Same Level)
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose architecture
- [[q-compose-modifier-order-performance--android--medium]] - Modifier system

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Skipping optimization
- [[q-compose-performance-optimization--android--hard]] - Advanced optimization
- [[q-compose-custom-layout--android--hard]] - Custom layout

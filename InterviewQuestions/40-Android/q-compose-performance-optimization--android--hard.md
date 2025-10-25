---
id: 20251020-200000
title: Compose Performance Optimization / Оптимизация производительности Compose
aliases:
- Compose Performance Optimization
- Оптимизация производительности Compose
topic: android
subtopics:
- ui-compose
- performance-memory
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-compose-compiler-plugin--android--hard
- q-compose-lazy-layout-optimization--android--hard
- q-android-performance-measurement-tools--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/ui-compose
- android/performance-memory
- difficulty/hard
source: https://developer.android.com/jetpack/compose/performance
source_note: Official Compose performance guide
---

# Вопрос (RU)
> Оптимизация производительности Compose?

# Question (EN)
> Compose Performance Optimization?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Principles

- Minimize recomposition scope (observe granular state, split UI).
- Prefer stable inputs (immutable/@Stable) and stable callbacks.
- Precompute/derive values with `remember`/`derivedStateOf`.
- Use keys and content types in lazy lists for reuse and diffing.
- Avoid allocations in hot paths; reuse shapes/brushes/painters.
- Measure and verify with tools; optimize only confirmed hotspots.
- Apply [[c-algorithms]] for efficient state management and [[c-data-structures]] for optimal data organization.

### Minimal patterns

Granular state observation

```kotlin
// Observe fields separately to limit recomposition
val title by vm.title.collectAsState()
val body by vm.body.collectAsState()
Header(title); Body(body)
```

Stable callbacks

```kotlin
// Avoid capturing changing state in lambdas
val onClick = remember { { vm.onClick() } }
Button(onClick) { Text("Go") }
// or method reference
Button(onClick = vm::onClick) { Text("Go") }
```

Immutable/@Stable models

```kotlin
@Immutable data class Product(val id: String, val name: String)
@Stable class UiState { var selected by mutableStateOf<String?>(null) }
```

Derived values

```kotlin
val listState = rememberLazyListState()
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```

Lazy reuse (keys, contentType)

```kotlin
LazyColumn {
  items(items = data, key = { it.id }, contentType = { it.type }) { item ->
    Row { Text(item.title) }
  }
}
```

Avoid recomposition propagation

```kotlin
// Do not pass frequently changing primitives down if not needed
var counter by remember { mutableStateOf(0) }
Button({ counter++ }) { Text("$counter") }
ExpensiveChild() // independent of counter
```

Remember expensive work

```kotlin
val formatted = remember(price) { priceFormatter.format(price) }
Text(formatted)
```

### Measurement and tooling

- Use Layout Inspector (Recomposition counts), Perfetto, tracing.
- Track jank and long frames; correlate with recomposition spikes.
- Verify skips with compiler metrics (Compose compiler reports).

## Follow-ups

- When to use `derivedStateOf` vs memoizing with `remember`?
- How to validate stability/skippability using compiler metrics?
- Strategies for large lazy lists (paging, prefetch, snapshots)?

## References

- [Compose Performance Guide](https://developer.android.com/jetpack/compose/performance)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)

## Related Questions

### Prerequisites (Easier)

- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)

- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-lazy-layout-optimization--android--hard]]

### Advanced (Harder)

- [[q-compose-custom-layout--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]

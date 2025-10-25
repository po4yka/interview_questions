---
id: 20251017-115547
title: Compose Lazy Layout Optimization / Оптимизация Lazy‑layout в Compose
aliases:
- Compose Lazy Layout Optimization
- Оптимизация Lazy‑layout в Compose
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
- q-android-performance-measurement-tools--android--medium
- q-compose-compiler-plugin--android--hard
- q-compose-custom-layout--android--hard
created: 2025-10-15
updated: 2025-10-20
tags:
- android/ui-compose
- android/performance-memory
- difficulty/hard
---

# Вопрос (RU)
> Оптимизация Lazy‑layout в Compose?

# Question (EN)
> Compose Lazy Layout Optimization?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core principles
- Stable keys: ensure identity across updates (`key = item.id`)
- Hoist state: keep per‑item state outside items or keyed by stable id
- Avoid capturing changing lambdas/state in item scope; use `rememberUpdatedState`
- Prefetch/layout: enable prefetch, use item placeholders/shimmer if needed
- Avoid nested scroll/layout thrash; constrain measure work; reuse shapes/brushes
- Leverages [[c-data-structures]] like hash maps for efficient item lookup and [[c-algorithms]] for scroll optimization

### Minimal patterns

Stable keys and no recomposition captures:
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->
    val onClick by rememberUpdatedState(newValue = { onItemClick(item.id) })
    Row(Modifier.clickable { onClick() }) { Text(item.title) }
  }
}
```

Hoist per‑row state by id:
```kotlin
@Composable
fun ListScreen(data: List<Item>) {
  val selection = remember { mutableStateMapOf<String, Boolean>() }
  LazyColumn { items(data, key = { it.id }) { item ->
    val selected = selection[item.id] == true
    Row(Modifier.toggleable(selected, onValueChange = { selection[item.id] = it })) {
      Text(item.title)
    }
  } }
}
```

Prefetching (paging integration):
```kotlin
val lazyState = rememberLazyListState()
LaunchedEffect(lazyState) {
  snapshotFlow { lazyState.layoutInfo.visibleItemsInfo.lastOrNull()?.index }
    .distinctUntilChanged()
    .collect { last -> if (last != null && last > data.size - 10) viewModel.loadMore() }
}
```

Avoid heavy recomposition in items:
```kotlin
@Composable
fun PriceTag(price: BigDecimal) {
  val formatted = remember(price) { priceFormatter.format(price) }
  Text(formatted) // precompute once per price change
}
```

### Measurement/perf tips
- Avoid costly intrinsics; provide fixed sizes where possible
- Reuse `Brush`, `Shape`, `Painter`; avoid recreating per item
- Use `mutableStateListOf`/snapshot state collections with stable keys
- Profile with Layout Inspector/Perfetto; monitor recomposition counts

## Follow-ups
- How to design item scopes to minimize captures and recompositions?
- When to use derivedStateOf in lazy items?
- How to measure item jank and tune prefetch/window sizes?

## References
- https://developer.android.com/develop/ui/compose/lists
- https://developer.android.com/develop/ui/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-animated-visibility-vs-content--android--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]

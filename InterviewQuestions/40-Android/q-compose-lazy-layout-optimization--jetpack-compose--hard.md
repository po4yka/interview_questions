---
id: 20251017-115547
title: Compose Lazy Layout Optimization / Оптимизация Lazy‑layout в Compose
aliases: [Compose Lazy Layout Optimization, Оптимизация Lazy‑layout в Compose]
topic: android
subtopics: [ui-compose, performance]
question_kind: android
difficulty: hard
status: reviewed
moc: moc-android
related: [q-android-performance-measurement-tools--android--medium, q-compose-compiler-plugin--jetpack-compose--hard, q-compose-custom-layout--jetpack-compose--hard]
created: 2025-10-15
updated: 2025-10-20
original_language: en
language_tags: [en, ru]
tags: [android/ui-compose, compose/lazy, performance, recomposition, keys, difficulty/hard]
---

# Question (EN)
> How do you optimize LazyColumn/LazyRow performance in Compose (keys, state hoisting, prefetching, item reuse, and avoiding recomposition)?

# Вопрос (RU)
> Как оптимизировать производительность LazyColumn/LazyRow в Compose (keys, подъём состояния, prefetching, переиспользование и избежание рекомпозиции)?

---

## Answer (EN)

### Core principles
- Stable keys: ensure identity across updates (`key = item.id`)
- Hoist state: keep per‑item state outside items or keyed by stable id
- Avoid capturing changing lambdas/state in item scope; use `rememberUpdatedState`
- Prefetch/layout: enable prefetch, use item placeholders/shimmer if needed
- Avoid nested scroll/layout thrash; constrain measure work; reuse shapes/brushes

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

## Ответ (RU)

### Базовые принципы
- Стабильные keys: идентичность элементов между обновлениями (`key = item.id`)
- Поднимайте состояние: храните per‑item состояние снаружи или по стабильному id
- Не захватывайте меняющиеся лямбды/состояние в item; `rememberUpdatedState`
- Prefetch/layout: включать префетч; плейсхолдеры/шиммер при необходимости
- Избегать вложенного скролла/джиттера измерений; переиспользовать shapes/brushes

### Минимальные паттерны

Стабильные keys и отсутствие захвата:
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->
    val onClick by rememberUpdatedState(newValue = { onItemClick(item.id) })
    Row(Modifier.clickable { onClick() }) { Text(item.title) }
  }
}
```

Подъём состояния по id:
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

Prefetch (интеграция с paging):
```kotlin
val lazyState = rememberLazyListState()
LaunchedEffect(lazyState) {
  snapshotFlow { lazyState.layoutInfo.visibleItemsInfo.lastOrNull()?.index }
    .distinctUntilChanged()
    .collect { last -> if (last != null && last > data.size - 10) viewModel.loadMore() }
}
```

Избежать тяжёлой рекомпозиции:
```kotlin
@Composable
fun PriceTag(price: BigDecimal) {
  val formatted = remember(price) { priceFormatter.format(price) }
  Text(formatted)
}
```

### Советы по измерению/перформансу
- Избегайте дорогих intrinsic; задавайте фиксированные размеры где можно
- Переиспользуйте `Brush`, `Shape`, `Painter`; не создавайте per‑item
- Используйте snapshot‑коллекции с стабильными ключами
- Профилируйте Layout Inspector/Perfetto; следите за количеством рекомпозиций

---

## Follow-ups
- How to design item scopes to minimize captures and recompositions?
- When to use derivedStateOf in lazy items?
- How to measure item jank and tune prefetch/window sizes?

## References
- https://developer.android.com/develop/ui/compose/lists
- https://developer.android.com/develop/ui/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-animated-visibility-vs-content--jetpack-compose--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--jetpack-compose--hard]]
- [[q-compose-custom-layout--jetpack-compose--hard]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]

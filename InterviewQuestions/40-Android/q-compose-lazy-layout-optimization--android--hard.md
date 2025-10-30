---
id: 20251017-115547
title: Compose Lazy Layout Optimization / Оптимизация Lazy‑layout в Compose
aliases: [Compose Lazy Layout Optimization, Оптимизация Lazy‑layout в Compose, LazyColumn optimization, LazyRow optimization, Оптимизация LazyColumn]
topic: android
subtopics: [ui-compose, performance-memory]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-performance-measurement-tools--android--medium
  - q-compose-compiler-plugin--android--hard
  - q-compose-custom-layout--android--hard
  - q-compose-performance-optimization--android--hard
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android/ui-compose, android/performance-memory, difficulty/hard]
date created: Thursday, October 30th 2025, 11:23:14 am
date modified: Thursday, October 30th 2025, 12:43:44 pm
---

# Вопрос (RU)
> Как оптимизировать производительность Lazy-layout (LazyColumn, LazyRow) в Jetpack Compose?

# Question (EN)
> How to optimize performance of Lazy layouts (LazyColumn, LazyRow) in Jetpack Compose?

---

## Ответ (RU)

### Критичные оптимизации

**1. Стабильные ключи**
Без ключей Compose пересоздаёт все элементы при изменении списка. Используйте `key = { item.id }` для правильного отслеживания элементов.

**2. Управление состоянием**
Храните состояние вне scope элемента — поднимайте наверх или используйте `mutableStateMapOf` для отслеживания множества элементов по ID.

**3. Стабильные callback'ы**
Применяйте `rememberUpdatedState` для callback'ов, чтобы избежать ненужных рекомпозиций при изменении лямбд.

**4. Кеширование вычислений**
Используйте `remember(key)` для дорогостоящих операций (форматирование, парсинг, расчёты).

### Паттерны оптимизации

**✅ Стабильные ключи и обновляемые callback'ы:**
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->
    // ✅ callback не вызывает рекомпозицию при изменении
    val onClick by rememberUpdatedState { onItemClick(item.id) }
    Row(Modifier.clickable { onClick() }) {
      Text(item.title)
    }
  }
}
```

**❌ Без ключей — элементы пересоздаются:**
```kotlin
LazyColumn {
  items(data) { item -> // ❌ нет key
    Row { Text(item.title) }
  }
}
```

**✅ Управление состоянием множества элементов:**
```kotlin
@Composable
fun SelectableList(data: List<Item>) {
  // ✅ состояние вне scope элемента
  val selection = remember { mutableStateMapOf<String, Boolean>() }
  LazyColumn {
    items(data, key = { it.id }) { item ->
      val selected = selection[item.id] == true
      Row(
        Modifier.toggleable(
          value = selected,
          onValueChange = { selection[item.id] = it }
        )
      ) {
        Text(item.title)
      }
    }
  }
}
```

**✅ Prefetching для пагинации:**
```kotlin
val lazyState = rememberLazyListState()
LaunchedEffect(lazyState) {
  snapshotFlow {
    lazyState.layoutInfo.visibleItemsInfo.lastOrNull()?.index
  }
    .distinctUntilChanged()
    .collect { lastVisible ->
      if (lastVisible != null && lastVisible > data.size - 10) {
        viewModel.loadMore()
      }
    }
}
```

**✅ Кеширование дорогостоящих вычислений:**
```kotlin
@Composable
fun PriceTag(price: BigDecimal) {
  // ✅ форматирование только при изменении price
  val formatted = remember(price) {
    priceFormatter.format(price)
  }
  Text(formatted)
}
```

### Дополнительные оптимизации

**Переиспользование объектов:**
- Создавайте `Brush`, `Shape`, `Painter` вне item scope через `remember`
- Избегайте создания новых объектов при каждой рекомпозиции

**Фиксированные размеры:**
- Используйте `Modifier.height()` где возможно для ускорения layout
- Избегайте intrinsic measurements внутри items

**Профилирование:**
- Layout Inspector — анализ иерархии и перерисовок
- Compose Compiler Metrics — подсчёт skippable composables
- Perfetto — измерение frame timing и jank

## Answer (EN)

### Critical Optimizations

**1. Stable Keys**
Without keys, Compose recreates all items when the list changes. Use `key = { item.id }` for proper item tracking.

**2. State Management**
Store state outside item scope — hoist it or use `mutableStateMapOf` to track multiple items by ID.

**3. Stable Callbacks**
Apply `rememberUpdatedState` for callbacks to avoid unnecessary recompositions when lambdas change.

**4. Computation Caching**
Use `remember(key)` for expensive operations (formatting, parsing, calculations).

### Optimization Patterns

**✅ Stable keys and updatable callbacks:**
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->
    // ✅ callback doesn't trigger recomposition on change
    val onClick by rememberUpdatedState { onItemClick(item.id) }
    Row(Modifier.clickable { onClick() }) {
      Text(item.title)
    }
  }
}
```

**❌ Without keys — items recreated:**
```kotlin
LazyColumn {
  items(data) { item -> // ❌ no key
    Row { Text(item.title) }
  }
}
```

**✅ Managing state for multiple items:**
```kotlin
@Composable
fun SelectableList(data: List<Item>) {
  // ✅ state outside item scope
  val selection = remember { mutableStateMapOf<String, Boolean>() }
  LazyColumn {
    items(data, key = { it.id }) { item ->
      val selected = selection[item.id] == true
      Row(
        Modifier.toggleable(
          value = selected,
          onValueChange = { selection[item.id] = it }
        )
      ) {
        Text(item.title)
      }
    }
  }
}
```

**✅ Prefetching for pagination:**
```kotlin
val lazyState = rememberLazyListState()
LaunchedEffect(lazyState) {
  snapshotFlow {
    lazyState.layoutInfo.visibleItemsInfo.lastOrNull()?.index
  }
    .distinctUntilChanged()
    .collect { lastVisible ->
      if (lastVisible != null && lastVisible > data.size - 10) {
        viewModel.loadMore()
      }
    }
}
```

**✅ Caching expensive computations:**
```kotlin
@Composable
fun PriceTag(price: BigDecimal) {
  // ✅ formatting only when price changes
  val formatted = remember(price) {
    priceFormatter.format(price)
  }
  Text(formatted)
}
```

### Additional Optimizations

**Object Reuse:**
- Create `Brush`, `Shape`, `Painter` outside item scope via `remember`
- Avoid creating new objects on every recomposition

**Fixed Sizes:**
- Use `Modifier.height()` where possible to speed up layout
- Avoid intrinsic measurements inside items

**Profiling:**
- Layout Inspector — hierarchy and redraw analysis
- Compose Compiler Metrics — count skippable composables
- Perfetto — measure frame timing and jank

---

## Follow-ups
- How to implement custom `LazyListPrefetchStrategy` for non-standard scroll patterns?
- When to use `derivedStateOf` vs `rememberUpdatedState` for lazy item state?
- How to debug and fix items causing layout thrashing in Perfetto?
- What are trade-offs between item keys and manual composition optimization?
- How to measure and optimize memory usage per item in large lists?

## References
- [[c-jetpack-compose]]
- [[c-memory-management]]
- [[c-recomposition]]
- https://developer.android.com/develop/ui/compose/lists
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/performance/stability

## Related Questions

### Prerequisites (Easier)
- [[q-compose-performance-optimization--android--hard]]
- [[q-compose-recomposition-basics--android--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]

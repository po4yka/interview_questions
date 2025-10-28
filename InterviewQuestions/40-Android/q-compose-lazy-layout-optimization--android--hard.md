---
id: 20251017-115547
title: Compose Lazy Layout Optimization / Оптимизация Lazy‑layout в Compose
aliases: [Compose Lazy Layout Optimization, Оптимизация Lazy‑layout в Compose, LazyColumn optimization, LazyRow optimization, Оптимизация LazyColumn]
topic: android
subtopics: [performance-memory, ui-compose]
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
updated: 2025-10-28
sources: []
tags: [android/performance-memory, android/ui-compose, difficulty/hard]
---
# Вопрос (RU)
> Как оптимизировать производительность Lazy-layout (LazyColumn, LazyRow) в Jetpack Compose?

# Question (EN)
> How to optimize performance of Lazy layouts (LazyColumn, LazyRow) in Jetpack Compose?

---

## Ответ (RU)

### Ключевые принципы оптимизации

**1. Стабильные ключи**
- Используйте уникальные стабильные ключи для элементов (`key = { item.id }`)
- [[c-jetpack-compose|Compose]] использует ключи для отслеживания изменений и предотвращения ненужных рекомпозиций
- Без ключей элементы пересоздаются при изменении списка

**2. Управление состоянием**
- Поднимайте состояние элементов наверх или храните по стабильному ID
- Используйте `mutableStateMapOf` для отслеживания состояния множества элементов
- Избегайте захвата изменяющихся лямбд в scope элемента

**3. Минимизация рекомпозиций**
- Применяйте `rememberUpdatedState` для обновляемых callback'ов
- Используйте `remember` для тяжелых вычислений
- Избегайте создания новых объектов при каждой рекомпозиции

**4. Prefetch и Layout**
- Включена по умолчанию, но можно настроить через `LazyListPrefetchStrategy`
- Используйте placeholder/shimmer для загружаемого контента
- Мониторьте видимые элементы для подгрузки данных

### Паттерны оптимизации

**✅ Стабильные ключи и оптимизированные callback'ы:**
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->
    val onClick by rememberUpdatedState { onItemClick(item.id) }
    Row(Modifier.clickable { onClick() }) {
      Text(item.title)
    }
  }
}
```

**❌ Без ключей - элементы пересоздаются:**
```kotlin
LazyColumn {
  items(data) { item -> // Без key
    Row { Text(item.title) }
  }
}
```

**✅ Управление состоянием множества элементов:**
```kotlin
@Composable
fun SelectableList(data: List<Item>) {
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

**✅ Кеширование тяжелых вычислений:**
```kotlin
@Composable
fun PriceTag(price: BigDecimal) {
  val formatted = remember(price) {
    priceFormatter.format(price)
  }
  Text(formatted)
}
```

**❌ Вычисления при каждой рекомпозиции:**
```kotlin
@Composable
fun PriceTag(price: BigDecimal) {
  Text(priceFormatter.format(price)) // Повторные вычисления
}
```

### Дополнительные оптимизации

**Переиспользование объектов:**
- Создавайте `Brush`, `Shape`, `Painter` вне item scope
- Используйте `remember` для объектов, общих для всех элементов

**Фиксированные размеры:**
- Указывайте `Modifier.height()` где возможно
- Избегайте сложных intrinsic measurements

**Профилирование:**
- Layout Inspector для анализа иерархии
- Compose Compiler Metrics для подсчета рекомпозиций
- Perfetto для измерения frame timing
- См. [[c-memory-management]] для глубокого анализа утечек памяти

## Answer (EN)

### Core Optimization Principles

**1. Stable Keys**
- Use unique stable keys for items (`key = { item.id }`)
- Compose uses keys to track changes and prevent unnecessary recompositions
- Without keys, items are recreated when list changes

**2. State Management**
- Hoist per-item state or store it by stable ID
- Use `mutableStateMapOf` to track state of multiple items
- Avoid capturing changing lambdas in item scope

**3. Minimize Recompositions**
- Apply `rememberUpdatedState` for updatable callbacks
- Use `remember` for expensive computations
- Avoid creating new objects on every recomposition

**4. Prefetch and Layout**
- Enabled by default, configurable via `LazyListPrefetchStrategy`
- Use placeholder/shimmer for loading content
- Monitor visible items to trigger data loading

### Optimization Patterns

**✅ Stable keys and optimized callbacks:**
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->
    val onClick by rememberUpdatedState { onItemClick(item.id) }
    Row(Modifier.clickable { onClick() }) {
      Text(item.title)
    }
  }
}
```

**❌ Without keys - items recreated:**
```kotlin
LazyColumn {
  items(data) { item -> // No key
    Row { Text(item.title) }
  }
}
```

**✅ Managing state for multiple items:**
```kotlin
@Composable
fun SelectableList(data: List<Item>) {
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
  val formatted = remember(price) {
    priceFormatter.format(price)
  }
  Text(formatted)
}
```

**❌ Computing on every recomposition:**
```kotlin
@Composable
fun PriceTag(price: BigDecimal) {
  Text(priceFormatter.format(price)) // Repeated computation
}
```

### Additional Optimizations

**Object Reuse:**
- Create `Brush`, `Shape`, `Painter` outside item scope
- Use `remember` for objects shared across items

**Fixed Sizes:**
- Specify `Modifier.height()` where possible
- Avoid complex intrinsic measurements

**Profiling:**
- Layout Inspector for hierarchy analysis
- Compose Compiler Metrics for recomposition counts
- Perfetto for frame timing measurement

---

## Follow-ups
- How to configure custom prefetch strategies for different scroll patterns?
- When should you use `derivedStateOf` vs `rememberUpdatedState` in lazy items?
- How to measure and analyze item-level jank using Perfetto traces?
- What are the trade-offs between `items()` with keys vs manual composition?

## References
- https://developer.android.com/develop/ui/compose/lists
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/performance/stability

## Related Questions

### Prerequisites (Easier)
- [[q-compose-performance-optimization--android--hard]]
- [[q-animated-visibility-vs-content--android--medium]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]

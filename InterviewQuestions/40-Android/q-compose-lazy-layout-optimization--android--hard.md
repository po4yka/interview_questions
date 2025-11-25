---
id: android-381
title: Compose Lazy Layout Optimization / Оптимизация Lazy‑layout в Compose
aliases: [Compose Lazy Layout Optimization, LazyColumn optimization, LazyRow optimization, Оптимизация Lazy‑layout в Compose, Оптимизация LazyColumn]
topic: android
subtopics:
  - performance-memory
  - ui-compose
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android
  - q-android-performance-measurement-tools--android--medium
  - q-compose-compiler-plugin--android--hard
  - q-compose-custom-layout--android--hard
  - q-compose-performance-optimization--android--hard
  - q-compose-stability-skippability--android--hard
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/performance-memory, android/ui-compose, difficulty/hard]

date created: Saturday, November 1st 2025, 1:04:33 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---

# Вопрос (RU)
> Как оптимизировать производительность Lazy-layout (LazyColumn, LazyRow) в Jetpack Compose?

# Question (EN)
> How to optimize performance of Lazy layouts (LazyColumn, LazyRow) in Jetpack Compose?

---

## Ответ (RU)

### Краткий Вариант
- Используйте стабильные ключи (`key`) для элементов.
- Храните состояние вне item composable (state hoisting, map по ID).
- Делайте callback'ы и эффекты стабильными (`rememberUpdatedState` для long-lived эффектов).
- Кешируйте дорогие вычисления через `remember`.
- Переиспользуйте объекты и избегайте ненужных intrinsic измерений.
- Профилируйте через Layout Inspector, Compose Compiler Metrics и Perfetto (см. [[c-android]]).

### Подробный Вариант

#### Критичные Оптимизации

**1. Стабильные ключи**
Без ключей LazyColumn/LazyRow полагаются на позиции элементов. При вставках/удалениях в середине списка это приводит к неправильному сопоставлению состояний и лишним перерисовкам. Используйте `key = { item.id }` (стабильный уникальный идентификатор) для корректного сопоставления элементов и сохранения состояния.

**2. Управление состоянием**
Храните состояние вне scope элемента (state hoisting) или централизованно (например, `mutableStateMapOf`) по ID, чтобы:
- не терять состояние при рециклинге/удалении composable;
- не пересоздавать состояние при скролле и переразмещении элементов.

**3. Стабильные callback'ы и эффекты**
Обеспечьте стабильность лямбд (например, через стабильные ссылки из `ViewModel`/hoisted state). `rememberUpdatedState` используйте там, где лямбда попадает во вложенные эффекты (`LaunchedEffect`, `DisposableEffect`, анимации), чтобы обновлять поведение без перезапуска эффекта. Не воспринимайте `rememberUpdatedState` как способ избежать самих рекомпозиций элемента, он лишь предотвращает использование устаревших значений внутри долгоживущих объектов.

**4. Кеширование вычислений**
Используйте `remember(key)` или мемоизацию для дорогостоящих операций (форматирование, парсинг, расчёты), чтобы они выполнялись только при изменении значимых входных данных.

#### Паттерны Оптимизации

**✅ Стабильные ключи и актуальные callback'ы:**
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->
    // ✅ onItemClick может меняться выше по иерархии,
    // но внутри, например, эффекта мы будем использовать актуальную версию
    val currentOnItemClick by rememberUpdatedState(onItemClick)
    Row(Modifier.clickable { currentOnItemClick(item.id) }) {
      Text(item.title)
    }
  }
}
```

**❌ Без ключей — риск неверного сопоставления состояния при изменении списка:**
```kotlin
LazyColumn {
  items(data) { item -> // ❌ нет key, опора только на позицию
    Row { Text(item.title) }
  }
}
```

**✅ Управление состоянием множества элементов:**
```kotlin
@Composable
fun SelectableList(data: List<Item>) {
  // ✅ состояние вне scope элемента, индексируем по стабильному ID
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
  snapshotFlow { lazyState.layoutInfo.visibleItemsInfo.lastOrNull()?.index }
    .distinctUntilChanged()
    .collect { lastVisible ->
      if (lastVisible != null && lastVisible > data.size - 10) {
        // loadMore должен быть идемпотентным/защищённым от повторных вызовов
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

#### Дополнительные Оптимизации

**Переиспользование объектов:**
- Создавайте `Brush`, `Shape`, `Painter` и другие неизменяемые объекты вне item scope через `remember` или на верхнем уровне.
- Избегайте создания новых объектов при каждой рекомпозиции без необходимости.

**Фиксированные размеры:**
- Где это семантически корректно, используйте явные размеры (`Modifier.height()`, `Modifier.size()`), чтобы упростить измерения.
- Избегайте intrinsic measurements внутри элементов, так как они дороже и могут негативно влиять на производительность.

**Профилирование:**
- Layout Inspector — анализ иерархии и перерисовок.
- Compose Compiler Metrics — оценка стабильности и skippability composable-функций.
- Perfetto — измерение frame timing и jank при скролле.

## Answer (EN)

### Short Version
- Use stable item `key`s.
- Hoist state and keep it keyed by ID, not tied to item lifetime.
- Make callbacks/effects stable (use `rememberUpdatedState` inside long-lived effects).
- Cache expensive work via `remember`.
- Reuse objects and avoid unnecessary intrinsic measurements.
- Profile with Layout Inspector, Compose Compiler Metrics, and Perfetto (see [[c-android]]).

### Detailed Version

#### Critical Optimizations

**1. Stable Keys**
Without keys, LazyColumn/LazyRow rely on item positions. When you insert/remove items in the middle, this can lead to incorrect state mapping and extra work. Use `key = { item.id }` (a stable unique ID) to keep item identity consistent and preserve state across updates.

**2. State Management**
Keep state outside the item scope (state hoisting) or in a centralized structure (e.g., `mutableStateMapOf`) keyed by ID to:
- avoid losing state when items are recycled/removed;
- avoid recreating state on scroll and item remeasure.

**3. Stable Callbacks and Effects**
Ensure callbacks are stable (e.g., provided from `ViewModel`/hoisted state). Use `rememberUpdatedState` in places where a lambda is captured by long-lived effects (`LaunchedEffect`, `DisposableEffect`, animations) so the effect sees the latest lambda without restarting. Do not treat `rememberUpdatedState` as a way to avoid recomposition of the item itself; it prevents stale values inside long-lived objects, not recomposition.

**4. Computation Caching**
Use `remember(key)` or memoization for expensive operations (formatting, parsing, calculations), so they only run when relevant inputs change.

#### Optimization Patterns

**✅ Stable keys and up-to-date callbacks:**
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->
    // ✅ onItemClick may change higher up; rememberUpdatedState keeps the latest
    val currentOnItemClick by rememberUpdatedState(onItemClick)
    Row(Modifier.clickable { currentOnItemClick(item.id) }) {
      Text(item.title)
    }
  }
}
```

**❌ Without keys — risk of incorrect state mapping when list changes:**
```kotlin
LazyColumn {
  items(data) { item -> // ❌ no key, identity based only on position
    Row { Text(item.title) }
  }
}
```

**✅ Managing state for multiple items:**
```kotlin
@Composable
fun SelectableList(data: List<Item>) {
  // ✅ state outside item scope, indexed by stable ID
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
  snapshotFlow { lazyState.layoutInfo.visibleItemsInfo.lastOrNull()?.index }
    .distinctUntilChanged()
    .collect { lastVisible ->
      if (lastVisible != null && lastVisible > data.size - 10) {
        // Ensure loadMore is idempotent/debounced to avoid duplicate requests
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

#### Additional Optimizations

**Object Reuse:**
- Create `Brush`, `Shape`, `Painter`, and other immutable objects outside the item scope via `remember` or higher-level composition.
- Avoid allocating new objects on every recomposition unless necessary.

**Fixed Sizes:**
- Where semantically correct, use explicit sizes (`Modifier.height()`, `Modifier.size()`) to simplify measurement and potentially speed up layout.
- Avoid intrinsic measurements inside items as they are relatively expensive and can hurt scrolling performance.

**Profiling:**
- Layout Inspector — inspect hierarchy and recomposition/redraw behavior.
- Compose Compiler Metrics — analyze stability and skippability of composables.
- Perfetto — measure frame timing and jank during scrolling.

---

## Follow-ups (RU)
- Как реализовать кастомный `LazyListPrefetchStrategy` для нестандартных сценариев скролла?
- Когда использовать `derivedStateOf` vs `rememberUpdatedState` для состояния элементов в `Lazy`-списках?
- Как отлаживать и устранять элементы, вызывающие layout thrashing, с помощью Perfetto?
- В чем компромиссы между использованием ключей элементов и ручной оптимизацией композиции?
- Как измерять и оптимизировать потребление памяти на элемент в очень больших списках?

## Follow-ups (EN)
- How to implement a custom `LazyListPrefetchStrategy` for non-standard scroll patterns?
- When to use `derivedStateOf` vs `rememberUpdatedState` for lazy item state?
- How to debug and fix items causing layout thrashing in Perfetto?
- What are trade-offs between item keys and manual composition optimization?
- How to measure and optimize memory usage per item in large lists?

## References (RU)
- https://developer.android.com/develop/ui/compose/lists
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/performance/stability

## References (EN)
- https://developer.android.com/develop/ui/compose/lists
- https://developer.android.com/develop/ui/compose/performance
- https://developer.android.com/develop/ui/compose/performance/stability

## Related Questions

### Prerequisites (Easier)
- [[q-compose-performance-optimization--android--hard]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-custom-layout--android--hard]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]]
- [[q-compose-slot-table-recomposition--android--hard]]

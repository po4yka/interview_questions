---
id: android-333
title: Compose Slot Table & Recomposition / Slot Table и рекомпозиция Compose
aliases: [Compose Slot Table and Recomposition, Slot Table и рекомпозиция]
topic: android
subtopics:
  - performance-rendering
  - ui-compose
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-compose-compiler-plugin--android--hard
  - q-compose-performance-optimization--android--hard
  - q-compose-stability-skippability--android--hard
created: 2025-10-15
updated: 2025-11-02
tags: [android/performance-rendering, android/ui-compose, difficulty/hard]
sources: []
---

# Вопрос (RU)
Как работают Slot Table и рекомпозиция в Jetpack Compose? Объясните механизм внутреннего представления и оптимизации перерисовки.

# Question (EN)
How do Slot Table and recomposition work in Jetpack Compose? Explain the internal representation mechanism and rendering optimization.

---

## Ответ (RU)

### Основная Идея
`Slot Table` — компактная линейная структура данных (`gap buffer`), хранящая UI-дерево композиции и оптимизирующая рекомпозицию через инвалидацию групп.

**Архитектура**:
- **Groups (группы)** — древовидная структура с ключами, арностью и флагами для быстрого пропуска неизменённых участков
- **Slots (слоты)** — хранилище для `remember`, state-объектов, ссылок на узлы (`LayoutNode`)
- **Anchors (якоря)** — позиционная идентичность для сохранения состояния при структурных изменениях

### Механизм Рекомпозиции

**Фаза инвалидации**:
1. Запись state → `snapshot` mutation → invalidation scope добавляется в очередь
2. `Composer` помечает затронутые группы по anchor-позициям
3. `Scheduler` планирует recompose на следующий frame

**Фаза рекомпозиции**:
```kotlin
// ✅ Пример: композиция с инвалидацией
@Composable
fun Counter(count: Int) {  // Group start
  Text("Count: $count")    // Slot: текстовый узел
}                          // Group end

// При изменении count:
// 1. Группа Counter инвалидирована
// 2. Composer пропускает стабильные соседние группы
// 3. Перевыполняется только лямбда Counter
// 4. Обновляется slot текстового узла
```

**Оптимизация: skippability** — компилятор генерирует ``if ($changed == 0) skip``, если параметры стабильны и не изменились.

### Критичные Паттерны

**Стабильные ключи для сохранения идентичности**:
```kotlin
LazyColumn {
  items(data, key = { it.id }) { item ->  // ✅ Group anchor привязан к id
    ItemRow(item)
  }
}
```

**`derivedStateOf` для снижения инвалидаций**:
```kotlin
val firstVisible by remember {
  derivedStateOf {  // ✅ Инвалидирует только при изменении результата
    listState.firstVisibleItemIndex > 0
  }
}
```

**`remember(deps)` для контроля пересоздания**:
```kotlin
val formatter = remember(locale) {  // ✅ Пересоздание только при смене locale
  DateTimeFormatter.ofPattern("dd MMM", locale)
}
```

### Производительность

**Сложность операций**:
- Чтение слота: O(1)
- Пропуск группы: O(1) по размеру группы
- Вставка/удаление группы: O(n) для gap buffer реорганизации

**Сравнение с `View`**:
- `View` hierarchy: глубокие деревья с `measure`/`layout` для всех дочерних
- `Slot Table`: плоская структура, локальная рекомпозиция без полного обхода

## Answer (EN)

### Core Idea
`Slot Table` is a compact linear data structure (`gap buffer`) storing the composition UI tree and optimizing recomposition through group invalidation.

**Architecture**:
- **Groups** — tree structure with keys, arity, flags enabling fast skipping of unchanged regions
- **Slots** — storage for `remember` values, state objects, node references (`LayoutNode`)
- **Anchors** — positional identity preserving state during structural changes

### Recomposition Mechanism

**Invalidation phase**:
1. State write → `snapshot` mutation → invalidation scope enqueued
2. `Composer` marks affected groups by anchor positions
3. `Scheduler` plans recompose for next frame

**Recomposition phase**:
```kotlin
// ✅ Example: composition with invalidation
@Composable
fun Counter(count: Int) {  // Group start
  Text("Count: $count")    // Slot: text node
}                          // Group end

// When count changes:
// 1. Counter group invalidated
// 2. Composer skips stable neighboring groups
// 3. Only Counter lambda re-executed
// 4. Text node slot updated
```

**Optimization: skippability** — compiler generates ``if ($changed == 0) skip`` when parameters are stable and unchanged.

### Critical Patterns

**Stable keys preserve identity**:
```kotlin
LazyColumn {
  items(data, key = { it.id }) { item ->  // ✅ Group anchor tied to id
    ItemRow(item)
  }
}
```

**`derivedStateOf` reduces invalidations**:
```kotlin
val firstVisible by remember {
  derivedStateOf {  // ✅ Invalidates only when result changes
    listState.firstVisibleItemIndex > 0
  }
}
```

**`remember(deps)` controls recreation**:
```kotlin
val formatter = remember(locale) {  // ✅ Recreates only on locale change
  DateTimeFormatter.ofPattern("dd MMM", locale)
}
```

### Performance

**Operation complexity**:
- Slot read: O(1)
- Group skip: O(1) in group size
- Group insert/delete: O(n) for gap buffer reorganization

**Comparison with `View`**:
- `View` hierarchy: deep trees with `measure`/`layout` for all children
- `Slot Table`: flat structure, local recomposition without full traversal

---

## Follow-ups
- How do anchors enable list item reordering without losing state?
- What causes parameter instability and how does it impact skippability?
- How does the Compose runtime detect which groups need recomposition?
- What's the memory overhead of Slot Table compared to `View` hierarchy?
- How does gap buffer reorganization affect performance during rapid list mutations?

## References
- [[c-compose-state]]
- [[c-compose-recomposition]]

## Related Questions

### Prerequisites (Easier)
- Understanding of Compose state management basics
- Basic knowledge of recomposition

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]] — How compiler generates slot table code
- [[q-compose-stability-skippability--android--hard]] — Stability inference details
- [[q-compose-performance-optimization--android--hard]] — Broader optimization strategies

### Advanced (Harder)
- Deep dive into gap buffer implementation
- Advanced recomposition debugging techniques

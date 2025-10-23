---
id: 20251012-122710
title: Compose Slot Table & Recomposition / Slot Table и рекомпозиция Compose
aliases:
- Compose Slot Table and Recomposition
- Slot Table и рекомпозиция
topic: android
subtopics:
- ui-compose
- internals
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
source: https://developer.android.com/jetpack/compose/mental-model
source_note: Official Compose mental model
status: reviewed
moc: moc-android
related:
- q-compose-compiler-plugin--jetpack-compose--hard
- q-compose-performance-optimization--android--hard
- q-compose-stability-skippability--jetpack-compose--hard
created: 2025-10-15
updated: 2025-10-20
tags:
- android/ui-compose
- compose/internals
- recomposition
- slot-table
- performance
- difficulty/hard
- android/internals
---# Вопрос (RU)
> Что такое Slot Table в Compose и как она обеспечивает эффективную рекомпозицию?

---

# Question (EN)
> What is the Slot Table in Compose and how does it enable efficient recomposition?

## Ответ (RU)

### Идея
- Slot Table — компактная линейная структура (похожа на gap‑buffer), фиксирующая группы и слоты compositon.
- Группы кодируют дерево (enter/exit), слоты хранят значения remember и ссылки на узлы.
- Рекомпозиция находит инвалидированные группы и исполняет только затронутые лямбды.

### Ключевые элементы
- Group: заголовок узла (key, arity, флаги), ограничивающий поддерево.
- Slot: хранилище для `remember`, состояния, узлов (layout/text и др.).
- Key/Anchor: позиционная идентичность для переживания перемещений (напр., keyed items).

### Минимальные паттерны (влияние на Slot Table)
Стабильные ключи в списках
```kotlin
LazyColumn { items(items = data, key = { it.id }) { item -> Row { Text(item.title) } } }
```
- Стабильные ключи сохраняют идентичность группы; предотвращают массовую инвалидацию при вставках.

remember пишет в слот
```kotlin
val formatter = remember(locale) { NumberFormat.getInstance(locale) }
```
- Запись один раз на ключ; слот переиспользуется, пока не изменится ключ/позиция.

derivedStateOf снижает инвалидации
```kotlin
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```
- Инвалидирует только при изменении результата.

Skippability и stability
- Стабильные параметры и модели `@Stable/@Immutable` позволяют помечать группы как skippable; компилятор разрешает пропуски.

### Процесс рекомпозиции (упрощённо)
1) Инвалидации ставятся в очередь (запись state, snapshot).
2) Composer обходит группы; если группа не инвалидирована → пропуск.
3) Если инвалидирована → выполняет лямбду; обновляет группы/слоты; фиксирует anchors.

---

## Answer (EN)

### Core idea
- Slot Table is a compact linear structure (gap‑buffer–like) recording composition groups and slots.
- Groups encode the tree (enter/exit group ops); slots store remembered values and node refs.
- Recomposition finds invalidated groups and re‑executes only affected lambdas.

### Key components
- Group: node header (key, arity, flags) delimiting a subtree.
- Slot: storage for `remember` values, state objects, nodes (layouts/text/etc.).
- Key/Anchor: positional identity to survive structural moves (e.g., keyed items).

### Minimal patterns (impact on Slot Table)
Stable keys in lazy lists
```kotlin
LazyColumn { items(items = data, key = { it.id }) { item -> Row { Text(item.title) } } }
```
- Stable keys preserve group identity; prevents mass invalidation on inserts.

remember stores into slots
```kotlin
val formatter = remember(locale) { NumberFormat.getInstance(locale) }
```
- Writes once per key; slot reused until key/position changes.

derivedStateOf avoids broad invalidations
```kotlin
val showFab by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }
```
- Invalidates only when derived result changes.

Skippability and stability
- Stable params and `@Stable/@Immutable` models let groups be marked skippable; compiler checks allow skipping recomposition.

### Recomposition flow (simplified)
1) Invalidations enqueued (state write, snapshot change) with anchors.
2) Composer traverses groups; if group not invalid → skip.
3) If invalid → execute lambda; update groups/slots; record anchors.

## Follow-ups
- How do anchors survive structural changes and support move operations?
- How does stability analysis interact with inline classes and collections?
- What pathologies cause wide invalidations (e.g., unstable params)?

## References
- https://developer.android.com/jetpack/compose/mental-model
- https://developer.android.com/jetpack/compose/performance

## Related Questions

### Prerequisites (Easier)
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-compose-compiler-plugin--android--hard]]
- [[q-compose-performance-optimization--android--hard]]

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]]


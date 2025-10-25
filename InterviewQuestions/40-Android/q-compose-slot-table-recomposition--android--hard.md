---
id: 20251012-122710
title: Compose Slot Table & Recomposition / Slot Table и рекомпозиция Compose
aliases: [Compose Slot Table and Recomposition, Slot Table и рекомпозиция]
topic: android
subtopics:
  - processes
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
  - q-compose-compiler-plugin--android--hard
  - q-compose-performance-optimization--android--hard
  - q-compose-stability-skippability--android--hard
created: 2025-10-15
updated: 2025-10-20
tags: [android/processes, android/ui-compose, difficulty/hard]
source: https://developer.android.com/jetpack/compose/mental-model
source_note: Official Compose mental model
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:30 pm
---

# Вопрос (RU)
> Slot Table и рекомпозиция Compose?

# Question (EN)
> Compose Slot Table & Recomposition?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Core Idea
- Slot Table is a compact linear structure (gap‑buffer–like) recording composition groups and slots.
- Groups encode the tree (enter/exit group ops); slots store remembered values and node refs.
- Recomposition finds invalidated groups and re‑executes only affected lambdas.
- Built using [[c-data-structures]] (similar to gap buffers and tree structures) for efficient storage and traversal.

### Key Components
- Group: node header (key, arity, flags) delimiting a subtree.
- Slot: storage for `remember` values, state objects, nodes (layouts/text/etc.).
- Key/Anchor: positional identity to survive structural moves (e.g., keyed items).

### Minimal Patterns (impact on Slot Table)
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

### Recomposition Flow (simplified)
1. Invalidations enqueued (state write, snapshot change) with anchors.
2. Composer traverses groups; if group not invalid → skip.
3. If invalid → execute lambda; update groups/slots; record anchors.

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

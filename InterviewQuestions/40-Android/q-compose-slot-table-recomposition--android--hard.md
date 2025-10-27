---
id: 20251012-122710
title: Compose Slot Table & Recomposition / Slot Table и рекомпозиция Compose
aliases: ["Compose Slot Table and Recomposition", "Slot Table и рекомпозиция"]
topic: android
subtopics: [processes, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-compiler-plugin--android--hard, q-compose-performance-optimization--android--hard, q-compose-stability-skippability--android--hard]
created: 2025-10-15
updated: 2025-10-27
tags: [android/processes, android/ui-compose, difficulty/hard]
sources: ["https://developer.android.com/jetpack/compose/mental-model"]
---

# Вопрос (RU)
Как работают Slot Table и рекомпозиция в Jetpack Compose? Объясните механизм внутреннего представления и оптимизации перерисовки.

# Question (EN)
How do Slot Table and recomposition work in Jetpack Compose? Explain the internal representation mechanism and rendering optimization.

---

## Ответ (RU)

### Основная идея
Slot Table — компактная линейная структура данных (подобна gap buffer), которая записывает группы композиции (groups) и слоты (slots) для эффективного хранения UI-дерева:

- **Groups** кодируют структуру дерева (операции входа/выхода из группы)
- **Slots** хранят запомненные значения (`remember`), state-объекты, ссылки на узлы (layout/text)
- **Recomposition** находит инвалидированные группы и перевыполняет только затронутые лямбды

### Ключевые компоненты

**Group (группа)** — заголовок узла с ключом, арностью и флагами, ограничивающий поддерево. Позволяет быстро пропустить неизменённые участки композиции.

**Slot (слот)** — хранилище для значений `remember`, state-объектов, узлов (TextView, Layout и т.д.).

**Key/Anchor** — позиционная идентичность для сохранения состояния при структурных изменениях (перемещение элементов в списке).

### Паттерны оптимизации

**Стабильные ключи в ленивых списках**
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->  // ✅ Сохраняет идентичность группы
    Text(item.title)
  }
}
```

**Использование remember для кэширования**
```kotlin
val formatter = remember(locale) { // ✅ Пересоздаётся только при смене locale
  NumberFormat.getInstance(locale)
}
```

**derivedStateOf для избирательной инвалидации**
```kotlin
val showFab by remember {
  derivedStateOf { listState.firstVisibleItemIndex > 0 }  // ✅ Инвалидирует только при изменении результата
}
```

**Skippability через стабильные типы**
- `@Stable`/`@Immutable` аннотации позволяют компилятору пропускать рекомпозицию групп со стабильными параметрами

### Процесс рекомпозиции
1. Инвалидации помещаются в очередь (запись state, изменение snapshot) с якорями
2. Composer обходит группы; если группа не инвалидирована → пропуск
3. Если инвалидирована → выполнение лямбды, обновление groups/slots, запись якорей

## Answer (EN)

### Core Idea
Slot Table is a compact linear data structure (gap-buffer-like) that records composition groups and slots for efficient UI tree storage:

- **Groups** encode tree structure (enter/exit group operations)
- **Slots** store remembered values (`remember`), state objects, node references (layout/text)
- **Recomposition** finds invalidated groups and re-executes only affected lambdas

### Key Components

**Group** — node header with key, arity, and flags delimiting a subtree. Enables fast skipping of unchanged composition regions.

**Slot** — storage for `remember` values, state objects, nodes (TextView, Layout, etc.).

**Key/Anchor** — positional identity to preserve state during structural changes (list item reordering).

### Optimization Patterns

**Stable keys in lazy lists**
```kotlin
LazyColumn {
  items(items = data, key = { it.id }) { item ->  // ✅ Preserves group identity
    Text(item.title)
  }
}
```

**Using remember for caching**
```kotlin
val formatter = remember(locale) { // ✅ Recreates only when locale changes
  NumberFormat.getInstance(locale)
}
```

**derivedStateOf for selective invalidation**
```kotlin
val showFab by remember {
  derivedStateOf { listState.firstVisibleItemIndex > 0 }  // ✅ Invalidates only when result changes
}
```

**Skippability via stable types**
- `@Stable`/`@Immutable` annotations allow compiler to skip recomposition of groups with stable parameters

### Recomposition Process
1. Invalidations enqueued (state write, snapshot change) with anchors
2. Composer traverses groups; if group not invalid → skip
3. If invalid → execute lambda, update groups/slots, record anchors

---

## Follow-ups
- How do anchors enable list item reordering without full recomposition?
- What causes unstable parameters and how does it impact slot table efficiency?
- How does the Compose runtime detect which groups need recomposition?
- What's the memory overhead of Slot Table compared to traditional View hierarchy?

## References
- [Compose Mental Model (Official)](https://developer.android.com/jetpack/compose/mental-model)
- [Compose Performance](https://developer.android.com/jetpack/compose/performance)
- [Thinking in Compose](https://developer.android.com/jetpack/compose/mental-model)

## Related Questions

### Prerequisites
- [[q-compose-state-management--android--medium]] — Understanding state before optimization
- [[q-compose-remember-vs-remember-saveable--android--medium]] — remember mechanism

### Related
- [[q-compose-compiler-plugin--android--hard]] — How compiler generates slot table code
- [[q-compose-performance-optimization--android--hard]] — Broader optimization strategies
- [[q-compose-stability-skippability--android--hard]] — Stability inference details

### Advanced
- [[q-compose-custom-layout-modifiers--android--hard]] — Low-level composition control
- [[q-compose-snapshot-system--android--hard]] — Snapshot isolation mechanics

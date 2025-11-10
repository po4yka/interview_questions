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
status: draft
moc: moc-android
related:
- c-compose-recomposition
- q-compose-compiler-plugin--android--hard
- q-compose-performance-optimization--android--hard
- q-compose-stability-skippability--android--hard
created: 2025-10-15
updated: 2025-11-10
tags: [android/performance-rendering, android/ui-compose, difficulty/hard]
sources: []

---

# Вопрос (RU)
> Как работают Slot Table и рекомпозиция в Jetpack Compose? Объясните механизм внутреннего представления и оптимизации перерисовки.

# Question (EN)
> How do Slot Table and recomposition work in Jetpack Compose? Explain the internal representation mechanism and rendering optimization.

---

## Ответ (RU)

### Краткий вариант
- `Slot Table` — линейная структура с группами и слотами, которая хранит структуру композиции.
- Рекомпозиция работает через инвалидацию затронутых групп и выборочное выполнение только нужных composable.
- Оптимизации достигаются за счет стабильности параметров, якорей и возможности быстро пропускать неизменённые группы.

### Подробный вариант

### Основная идея
`Slot Table` — компактная линейная структура данных (линейное представление с "gap"-областью), хранящая иерархию UI-дерева композиции и оптимизирующая рекомпозицию через инвалидацию групп.

**Архитектура**:
- **Groups (группы)** — древовидная структура с ключами, арностью и флагами, хранящаяся в линейном массиве и позволяющая быстро пропускать неизменённые участки по предвычисленным метаданным
- **Slots (слоты)** — хранилище для значений `remember`, state-объектов, ссылок на узлы (`LayoutNode`) и прочего связанного состояния
- **Anchors (якоря)** — позиционная идентичность для сохранения и переноса состояния при структурных изменениях

### Требования

- Функциональные:
  - Обеспечить локальную, инкрементальную рекомпозицию только изменившихся участков дерева.
  - Сохранить состояние (`remember`, state-объектов) при изменении структуры и порядка элементов.
  - Поддерживать декларативную модель Compose без ручного управления иерархией `View`.
- Нефункциональные:
  - Высокая производительность при частых изменениях состояния.
  - Минимизация аллокаций и пересозданий узлов.
  - Предсказуемое и детерминированное поведение рекомпозиции.

### Архитектура

- `Composer` управляет обходом дерева и работой со `Slot Table`.
- Группы и слоты представлены в линейном массиве с метаданными (размер группы, флаги, ключи).
- `Anchors` обеспечивают сопоставление логических групп с физическими позициями в `Slot Table` при вставках/удалениях.
- Планировщик Compose связывает инвалидации со слотами и группами и триггерит рекомпозицию в подходящий момент.

### Механизм рекомпозиции

**Фаза инвалидации**:
1. Запись в observable state → `snapshot`-мутация → в очередь добавляется scope/группа, зависящая от этого состояния.
2. `Composer` помечает затронутые группы по anchor-позициям и связанным scope.
3. Планировщик Compose (runtime) ставит задачу рекомпозиции на ближайший подходящий цикл обработки (часто с привязкой к следующему кадру UI).

**Фаза рекомпозиции**:
```kotlin
// ✅ Пример: композиция с инвалидацией
@Composable
fun Counter(count: Int) {  // Group start
  Text("Count: $count")    // Slot: текстовый узел
}                          // Group end

// При изменении состояния, от которого зависит count (или при передаче нового count сверху):
// 1. Инвалидируется соответствующий scope/группа
// 2. Composer пропускает стабильные соседние группы на основе метаданных Slot Table
// 3. Перевыполняется только лямбда Counter для затронутой группы
// 4. Обновляется slot текстового узла
```

**Оптимизация: skippability** — компилятор генерирует проверки вида `if ($changed == 0 && $default == 0) composer.skipToGroupEnd()` (упрощённо: `if ($changed == 0) skip`), если параметры стабильны и не изменились, что позволяет пропустить выполнение тела composable.

### Критичные паттерны

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
- Пропуск группы: O(1) за счёт информации о размере/смещении группы в Slot Table
- Вставка/удаление группы: O(n) из-за переразмещения и поддержания gap-области в линейной структуре

**Сравнение с `View`**:
- `View`-иерархия: явное древовидное представление с `measure`/`layout`/`draw`, часто с обходом значительных частей дерева.
- `Slot Table`: линейное представление иерархии с локальной рекомпозицией и возможностью быстро пропускать неизменённые группы без полного обхода всех узлов.

## Answer (EN)

### Short Version
- `Slot Table` is a linear structure of groups and slots that represents the composition tree.
- Recomposition works by invalidating affected groups and re-running only the necessary composables.
- Optimizations rely on stable parameters, anchors, and the ability to skip unchanged groups efficiently.

### Detailed Version

### Core Idea
`Slot Table` is a compact linear data structure (a linear representation with a gap-based region) that stores the composition UI hierarchy and optimizes recomposition through group invalidation.

**Architecture**:
- **Groups** — a tree-structured hierarchy with keys, arity, and flags, stored in a linear array, enabling fast skipping of unchanged regions via precomputed metadata
- **Slots** — storage for `remember` values, state objects, node references (`LayoutNode`), and other associated state
- **Anchors** — positional identity used to preserve and move state across structural changes

### Requirements

- Functional:
  - Enable local, incremental recomposition of only changed parts of the tree.
  - Preserve state (`remember`, state objects) across structural and ordering changes.
  - Support the declarative Compose model without manual `View` hierarchy manipulation.
- Non-functional:
  - High performance under frequent state updates.
  - Minimal allocations and node churn.
  - Predictable and deterministic recomposition behavior.

### Architecture

- The `Composer` orchestrates tree traversal and interacts with the `Slot Table`.
- Groups and slots live in a linear array with metadata (group size, flags, keys).
- `Anchors` map logical groups to physical positions in the `Slot Table` across insertions/deletions.
- The Compose runtime scheduler connects invalidations to groups/slots and triggers recomposition at appropriate times.

### Recomposition Mechanism

**Invalidation phase**:
1. Write to observable state → `snapshot` mutation → the corresponding scope/group that reads this state is enqueued for invalidation
2. The `Composer` marks affected groups by their anchors and associated scopes
3. The Compose runtime scheduler schedules recomposition work for the next suitable processing cycle (often aligned with the next UI frame, but not strictly guaranteed in all environments)

**Recomposition phase**:
```kotlin
// ✅ Example: composition with invalidation
@Composable
fun Counter(count: Int) {  // Group start
  Text("Count: $count")    // Slot: text node
}                          // Group end

// When the state driving `count` changes, or a new `count` is passed from above:
// 1. The corresponding scope/group is invalidated
// 2. The Composer skips stable neighboring groups using Slot Table metadata
// 3. Only the Counter lambda for the affected group is re-executed
// 4. The text node slot is updated
```

**Optimization: skippability** — the compiler generates checks like `if ($changed == 0 && $default == 0) composer.skipToGroupEnd()` (conceptually: `if ($changed == 0) skip`) when parameters are stable and unchanged, allowing the body of a composable to be skipped.

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
- Group skip: O(1) using stored group size/offset information in the Slot Table
- Group insert/delete: O(n) due to reorganization and maintenance of the gap region within the linear structure

**Comparison with `View`**:
- `View` hierarchy: explicit tree structure with `measure`/`layout`/`draw`, often traversing large portions of the tree
- `Slot Table`: linearized representation of the hierarchy with local recomposition and fast skipping of unchanged groups without traversing every node

---

## Дополнительные вопросы (Follow-ups, RU)
- Как якори помогают при перестановке элементов списка сохранять состояние?
- Что вызывает нестабильность параметров и как это влияет на skippability?
- Как рантайм Compose определяет, какие группы нуждаются в рекомпозиции?
- Каков накладной расход памяти Slot Table по сравнению с иерархией `View`?
- Как организация в стиле gap buffer влияет на производительность при частых изменениях списков?

## Ссылки (RU)
- [[c-compose-state]]
- [[c-compose-recomposition]]

## Связанные вопросы (RU)

### Предпосылки (проще)
- Понимание базового управления состоянием в Compose
- Базовые знания о рекомпозиции

### Связанные (тот же уровень)
- [[q-compose-compiler-plugin--android--hard]] — Как компилятор генерирует код для Slot Table
- [[q-compose-stability-skippability--android--hard]] — Детали вывода стабильности
- [[q-compose-performance-optimization--android--hard]] — Расширенные стратегии оптимизации

### Продвинутые (сложнее)
- Подробное изучение линейного хранения слотов и реализации на основе gap-буфера
- Продвинутые техники отладки рекомпозиции

---

## Follow-ups
- How do anchors enable list item reordering without losing state?
- What causes parameter instability and how does it impact skippability?
- How does the Compose runtime detect which groups need recomposition?
- What's the memory overhead of Slot Table compared to `View` hierarchy?
- How does gap buffer style reorganization affect performance during rapid list mutations?

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
- Deep dive into linear slot storage / gap-based implementation
- Advanced recomposition debugging techniques

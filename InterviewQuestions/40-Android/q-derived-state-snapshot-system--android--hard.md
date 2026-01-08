---
id: android-464
title: Derived State Snapshot System / Derived State и система Snapshot
aliases: [Derived State Snapshot System, Derived State и система Snapshot]
topic: android
subtopics: [performance-memory, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-jetpack-compose, c-memory-management, q-compose-performance-optimization--android--hard, q-compose-slot-table-recomposition--android--hard, q-compose-stability-skippability--android--hard, q-how-application-priority-is-determined-by-the-system--android--hard, q-sealed-classes-state-management--android--medium, q-when-can-the-system-restart-a-service--android--medium]
created: 2025-10-20
updated: 2025-11-02
tags: [android/performance-memory, android/ui-compose, derived-state, difficulty/hard, optimization, performance, snapshot, state]
sources:
  - https://developer.android.com/jetpack/compose/state
---
# Вопрос (RU)
> Объясните систему снимков (snapshot system) Compose. Как derivedStateOf оптимизирует перекомпозиции?

# Question (EN)
> Explain Compose's snapshot system. How does derivedStateOf optimize recompositions?

## Ответ (RU)

**Snapshot System** — механизм управления изменяемым состоянием в `Compose`, обеспечивающий изоляцию изменений, согласованность и атомарность применения. Концептуально похож на `MVCC` (Multi-Version Concurrency Control) для UI-состояния, но реализован специфично для Compose (глобальный снимок, вложенные snapshots, оптимистичные коммиты). Каждый `Snapshot` видит согласованную версию состояния; параллельные чтения и изменения возможны через snapshots, но корректность и отсутствие гонок зависят от правильного использования API.

**`derivedStateOf`** — оптимизирует recomposition, инвалидируясь только при изменении вычисленного результата (через `equals()`), а не при каждом изменении зависимостей, если они не меняют итоговое значение. Это предотвращает ненужные recomposition в потребителях этого значения.

### Архитектура Snapshot System

**Концептуальная модель (упрощённая, для интуиции, реальная реализация сложнее):**
```kotlin
// ✅ Упрощённая концепция Snapshot (аналогия, не реальный код runtime)
class Snapshot {
    private val modified = mutableMapOf<StateObject, Any?>()
    private val readSet = mutableSetOf<StateObject>()

    fun <T> read(state: StateObject): T {
        readSet += state  // отслеживание зависимостей
        return (modified[state] as T?) ?: state.currentValue as T
    }

    fun <T> write(state: StateObject, value: T) {
        modified[state] = value  // изолированное изменение в рамках snapshot
    }

    fun apply() {
        // атомарное применение (в реальности: оптимистичная попытка + проверка конфликтов)
        modified.forEach { (state, value) ->
            state.currentValue = value
        }
    }
}
```

**Ключевые механизмы (в реальной системе):**
- **Isolation**: каждый `Snapshot` читает собственную консистентную версию `state` — изменения не видны другим до успешного применения.
- **Tracking**: runtime автоматически отслеживает чтения/записи `SnapshotMutableState` и других snapshot-aware объектов — на основе этого строится invalidation для recomposition.
- **Atomicity**: успешный `apply` логически применяет все изменения разом.
- **Optimistic concurrency & conflict resolution**: конкурентные изменения приводят к проверке конфликтов; при конфликте commit может быть отклонён или повторён (например, `SnapshotApplyConflictException`).

### derivedStateOf: Оптимизация Через Мемоизацию

**Проблема:**
```kotlin
// ❌ Перекомпозиция и перерасчёт при каждом изменении items
@Composable
fun ListScreen(items: List<Item>) {
    val sorted = items.sortedBy { it.name }  // пересчёт при каждом recompose
    LazyColumn { items(sorted) { ... } }
}
```

**Решение (корректнее с snapshot-состоянием):**
```kotlin
// ✅ Пересчёт сортировки и invalidation только когда входные snapshot-состояния
// приводят к новому значению sorted (по equals())
@Composable
fun ListScreen(items: State<List<Item>>) {
    val sorted by remember {
        derivedStateOf { items.value.sortedBy { it.name } }
    }
    LazyColumn {
        items(sorted) { /* ... */ }
    }
}
```

Здесь `derivedStateOf`:
- отслеживает чтения `items.value` через snapshot system;
- лениво вычисляет сортировку при первом обращении после изменения;
- сравнивает новое значение с предыдущим через `equals()`; если список эквивалентен, потребители не инвалидируются.

Важно: `derivedStateOf` оптимизирует invalidation значения, основанного на snapshot-состоянии. Он не гарантирует отсутствие работы внутри `LazyColumn`, если ссылка или содержимое списка реально изменились.

**Механизм работы:**
1. **Dependency tracking**: при вычислении `block` внутри `derivedStateOf` runtime регистрирует обращения к snapshot-aware `State` — это зависимости.
2. **Lazy calculation**: новое значение вычисляется только при обращении к `.value` после того, как какая-то зависимость изменилась.
3. **Equality check ("structural equality")**: по умолчанию используется `equals()` результата; если он равен предыдущему значению, `derivedState` не помечается как изменённый.
4. **Conditional invalidation**: только если `equals()` возвращает `false`, все потребители `derivedState` инвалидируются и будут перерассчитаны/перекомпозированы.

### Практические Паттерны

**Complex filtering:**
```kotlin
@Composable
fun FilteredList(items: State<List<Item>>, filter: State<String>) {
    val filtered by remember {
        derivedStateOf {
            items.value.filter { it.matches(filter.value) }
        }
    }
    // ✅ Перекомпозиция потребителей filtered происходит только если
    // новый список (equals()) отличается от предыдущего.
}
```

**Aggregation:**
```kotlin
@Composable
fun CartSummary(cart: State<Cart>) {
    val totalPrice by remember {
        derivedStateOf {
            cart.value.items.sumOf { it.price }
        }
    }
    // ❗ Не создавайте derivedStateOf внутри часто повторяющихся участков (например, внутри items {}),
    // вместо этого выносите его в более высокий уровень или используйте локальные вычисления.
}
```

**Когда НЕ использовать:**
- Простые вычисления — накладные расходы `derivedStateOf` могут превышать выгоду (например, `val sum = a + b`).
- Побочные эффекты — внутри `derivedStateOf` не должно быть side effects; используйте `LaunchedEffect` и другие effect APIs.
- Suspend-функции — блок должен быть синхронным; для асинхронных операций используйте отдельные механизмы.
- Зависимости на мутируемые коллекции без snapshot-обёртки — Compose отслеживает чтения snapshot-aware `State`. Для корректного трекинга:
  - храни список в `State` (`mutableStateOf`, `SnapshotStateList` и т.п.);
  - предпочитайте стабильные/иммутабельные структуры, чтобы `equals()` и стабильность типов работали предсказуемо.

## Answer (EN)

The **Snapshot System** is Compose's mutable state management mechanism that provides isolation of changes, consistency, and atomic application of updates. It's conceptually similar to `MVCC` (Multi-Version Concurrency Control) for UI state, but implemented specifically for Compose (global snapshot, nested snapshots, optimistic commits). Each `Snapshot` observes a consistent view of state; concurrent reads and writes are enabled via snapshots, but correctness and race-freedom depend on using the snapshot APIs properly.

**`derivedStateOf`** optimizes recomposition by invalidating only when the computed result (based on `equals()`) changes, rather than on every dependency change that doesn't affect the final value. This reduces unnecessary recompositions for consumers of that value.

### Snapshot System Architecture

**Conceptual model (simplified; real implementation is more complex):**
```kotlin
// ✅ Simplified Snapshot concept (analogy, not actual runtime code)
class Snapshot {
    private val modified = mutableMapOf<StateObject, Any?>()
    private val readSet = mutableSetOf<StateObject>()

    fun <T> read(state: StateObject): T {
        readSet += state  // track dependency
        return (modified[state] as T?) ?: state.currentValue as T
    }

    fun <T> write(state: StateObject, value: T) {
        modified[state] = value  // isolated change within this snapshot
    }

    fun apply() {
        // atomic-like apply (in reality: optimistic commit with conflict checking)
        modified.forEach { (state, value) ->
            state.currentValue = value
        }
    }
}
```

**Key mechanisms (in the real system):**
- **Isolation**: each `Snapshot` reads its own consistent view of `state`; changes are not visible to others until successfully applied.
- **Tracking**: the runtime automatically tracks reads/writes of `SnapshotMutableState` and other snapshot-aware objects, and uses this to drive invalidation.
- **Atomicity**: a successful apply logically makes all the snapshot's updates visible at once.
- **Optimistic concurrency & conflict resolution**: concurrent modifications are handled via optimistic concurrency; conflicts can cause the commit to fail or be retried (e.g., `SnapshotApplyConflictException`).

### derivedStateOf: Optimization via Memoization

**Problem:**
```kotlin
// ❌ Recalculated on every recomposition when items changes
@Composable
fun ListScreen(items: List<Item>) {
    val sorted = items.sortedBy { it.name }
    LazyColumn { items(sorted) { ... } }
}
```

**Solution (more correct with snapshot state):**
```kotlin
// ✅ Sorting and invalidation only when the input snapshot state
// produces a new sorted value (by equals())
@Composable
fun ListScreen(items: State<List<Item>>) {
    val sorted by remember {
        derivedStateOf { items.value.sortedBy { it.name } }
    }
    LazyColumn {
        items(sorted) { /* ... */ }
    }
}
```

Here `derivedStateOf`:
- tracks reads of `items.value` via the snapshot system;
- lazily computes the sorted list when first accessed after a dependency change;
- compares the new result with the previous one using `equals()`; if equal, consumers are not invalidated.

Note: `derivedStateOf` optimizes invalidation of the derived value. It does not, by itself, prevent `LazyColumn` from doing its own work when the list reference/content actually changes.

**How it works:**
1. **Dependency tracking**: while evaluating the `derivedStateOf` block, the runtime records reads of snapshot-aware `State` objects.
2. **Lazy calculation**: the derived value is only recomputed on `.value` access after at least one dependency has changed.
3. **Equality check ("structural equality")**: by default uses `equals()` on the produced value; for custom types, implement `equals()/hashCode()` appropriately.
4. **Conditional invalidation**: only if `equals()` returns `false` is the `derivedState` marked as changed and its consumers invalidated for recomposition.

### Practical Patterns

**Complex filtering:**
```kotlin
@Composable
fun FilteredList(items: State<List<Item>>, filter: State<String>) {
    val filtered by remember {
        derivedStateOf {
            items.value.filter { it.matches(filter.value) }
        }
    }
    // ✅ Consumers of `filtered` recompose only when the new filtered list
    // is not equal to the previous one.
}
```

**Aggregation:**
```kotlin
@Composable
fun CartSummary(cart: State<Cart>) {
    val totalPrice by remember {
        derivedStateOf {
            cart.value.items.sumOf { it.price }
        }
    }
    // ❗ Avoid creating derivedStateOf inside frequently repeated scopes
    // (e.g., inside LazyColumn item lambdas); lift it or use direct local calculations.
}
```

**When NOT to use:**
- Simple calculations — `derivedStateOf` overhead outweighs benefits for trivial expressions (e.g., `val sum = a + b`).
- Side effects — do not perform side effects inside `derivedStateOf`; use `LaunchedEffect` and other effect APIs instead.
- Suspend functions — `derivedStateOf` blocks must be synchronous; use appropriate coroutine-based APIs for async work.
- Mutable collections as dependencies without snapshot state — Compose tracks reads of snapshot-aware `State` types. For correctness:
  - hold collections in `State` (`mutableStateOf`, `SnapshotStateList`, etc.);
  - prefer stable/immutable data structures so `equals()` and stability behave predictably.

## Follow-ups

- How does the `Snapshot` system handle concurrent writes from different threads?
- What's the performance overhead of `derivedStateOf` vs direct computation?
- When should you use `snapshotFlow` instead of `derivedStateOf`?
- How does the equality check work for custom data classes?
- What happens if `derivedStateOf` calculation throws an exception?
- How can immutable and stable collections improve `derivedStateOf` efficiency and correctness?

## References

- [Compose State Documentation](https://developer.android.com/jetpack/compose/state)
- MVCC-style snapshotting and optimistic concurrency concepts
- Memoization techniques in UI frameworks

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]
- [[c-compose-state]]
- [[c-jetpack-compose]]

### Prerequisites (Easier)
- Basic `Compose` state management (`mutableStateOf`, `remember`)
- Understanding `State` vs `MutableState` interfaces
- `Compose` recomposition basics

### Related (Same Level)
- [[q-compose-stability-skippability--android--hard]] — Stability inference and skippability
- [[q-compose-performance-optimization--android--hard]] — Performance optimization patterns
- `LaunchedEffect` vs `derivedStateOf` trade-offs

### Advanced (Harder)
- [[q-compose-slot-table-recomposition--android--hard]] — Slot table internals
- `Compose` compiler optimizations and code generation
- `Snapshot` system internals and thread-safety implementation

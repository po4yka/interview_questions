---
id: android-464
title: Derived State Snapshot System / Derived State и система Snapshot
aliases: [Derived State Snapshot System, Derived State и система Snapshot]
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
status: reviewed
moc: moc-android
related:
  - q-compose-performance-optimization--android--hard
  - q-compose-slot-table-recomposition--android--hard
  - q-compose-stability-skippability--android--hard
created: 2025-10-20
updated: 2025-11-02
tags: [android/performance-memory, android/ui-compose, compose, derived-state, difficulty/hard, optimization, performance, snapshot, state]
sources:
  - https://developer.android.com/jetpack/compose/state
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Sunday, November 2nd 2025, 7:43:20 pm
---

# Вопрос (RU)
> Объясните систему снимков (snapshot system) Compose. Как derivedStateOf оптимизирует перекомпозиции?

# Question (EN)
> Explain Compose's snapshot system. How does derivedStateOf optimize recompositions?

## Ответ (RU)

**Snapshot System** — механизм управления изменяемым состоянием в `Compose`, обеспечивающий изоляцию транзакций, thread-safety и атомарность изменений. Работает как `MVCC` (Multi-Version Concurrency Control) для UI state. Каждый `Snapshot` видит изолированную версию состояния, что позволяет безопасно выполнять параллельные чтения и записи.

**`derivedStateOf`** — оптимизирует recomposition, триггерясь только при изменении вычисленного результата (structural equality), а не промежуточных зависимостей. Это предотвращает ненужные recomposition при изменениях, не влияющих на финальный результат вычисления.

### Архитектура Snapshot System

**Концептуальная модель:**
```kotlin
// ✅ Упрощённая концепция Snapshot
class Snapshot {
    private val modified = mutableMapOf<StateObject, Any?>()
    private val readSet = mutableSetOf<StateObject>()

    fun <T> read(state: StateObject): T {
        readSet += state  // track dependency
        return modified[state] ?: state.currentValue
    }

    fun <T> write(state: StateObject, value: T) {
        modified[state] = value  // изолированное изменение
    }

    fun apply() {  // атомарный commit
        modified.forEach { (state, value) ->
            state.currentValue = value
        }
    }
}
```

**Ключевые механизмы:**
- **Isolation**: каждый `Snapshot` видит свою версию `state` — изменения изолированы до commit
- **Tracking**: автоматическое отслеживание read/write — `readSet` отслеживает зависимости для invalidation
- **Atomicity**: изменения применяются одновременно через `apply()` — all-or-nothing semantics
- **Conflict resolution**: обработка при параллельных записях — обнаружение конфликтов и предотвращение data races

### derivedStateOf: Оптимизация Через Memoization

**Проблема:**
```kotlin
// ❌ Перекомпозиция при любом изменении items
@Composable
fun ListScreen(items: List<Item>) {
    val sorted = items.sortedBy { it.name }  // пересчёт при каждом recompose
    LazyColumn { items(sorted) { ... } }
}
```

**Решение:**
```kotlin
// ✅ Recomposition только если результат сортировки изменился
@Composable
fun ListScreen(items: List<Item>) {
    val sorted = remember {
        derivedStateOf { items.sortedBy { it.name } }
    }
    LazyColumn { items(sorted.value) { ... } }  // structural equality check
}
```

**Механизм работы:**
1. **Dependency tracking**: автоматическое отслеживание читаемых `State` объектов — `Snapshot` регистрирует все прочитанные состояния
2. **Lazy calculation**: вычисление только при изменении зависимости — ленивое вычисление до первого обращения к `.value`
3. **Structural equality**: `equals()` сравнение старого и нового результата — предотвращает recomposition при идентичных результатах
4. **Conditional invalidation**: recomposition только если результат отличается — invalidation происходит только при неравенстве результатов

### Практические Паттерны

**Complex filtering:**
```kotlin
@Composable
fun FilteredList(items: State<List<Item>>, filter: State<String>) {
    val filtered = remember {
        derivedStateOf {
            items.value.filter { it.matches(filter.value) }
        }
    }
    // ✅ Recomposition только если отфильтрованный список изменился (structural equality)
}
```

**Aggregation:**
```kotlin
val totalPrice = remember {
    derivedStateOf {
        cart.items.sumOf { it.price }  // ❌ не создавайте в цикле!
    }
}
```

**Когда НЕ использовать:**
- Простые вычисления — overhead `derivedStateOf` превышает выгоду для быстрых операций (например, `val sum = a + b`)
- Side effects — используйте `LaunchedEffect` для побочных эффектов (navigation, logging, analytics)
- Suspend функции — нет поддержки coroutines внутри `derivedStateOf` (только синхронные вычисления)
- Изменяемые коллекции в зависимостях — используйте `ImmutableList` или `List.toImmutableList()` для корректного tracking

## Answer (EN)

**Snapshot System** is `Compose`'s mutable state management mechanism providing transaction isolation, thread-safety, and atomic changes. Works like `MVCC` (Multi-Version Concurrency Control) for UI state. Each `Snapshot` sees an isolated version of state, enabling safe concurrent reads and writes.

**`derivedStateOf`** optimizes recomposition by triggering only when the computed result changes (structural equality), not intermediate dependencies. This prevents unnecessary recomposition when changes don't affect the final computation result.

### Snapshot System Architecture

**Conceptual model:**
```kotlin
// ✅ Simplified Snapshot concept
class Snapshot {
    private val modified = mutableMapOf<StateObject, Any?>()
    private val readSet = mutableSetOf<StateObject>()

    fun <T> read(state: StateObject): T {
        readSet += state  // track dependency
        return modified[state] ?: state.currentValue
    }

    fun <T> write(state: StateObject, value: T) {
        modified[state] = value  // isolated change
    }

    fun apply() {  // atomic commit
        modified.forEach { (state, value) ->
            state.currentValue = value
        }
    }
}
```

**Key mechanisms:**
- **Isolation**: each `Snapshot` sees its own `state` version — changes isolated until commit
- **Tracking**: automatic read/write tracking — `readSet` tracks dependencies for invalidation
- **Atomicity**: changes applied simultaneously via `apply()` — all-or-nothing semantics
- **Conflict resolution**: handling concurrent writes — conflict detection and data race prevention

### derivedStateOf: Optimization via Memoization

**Problem:**
```kotlin
// ❌ Recomposition on any items change
@Composable
fun ListScreen(items: List<Item>) {
    val sorted = items.sortedBy { it.name }  // recalculated on every recompose
    LazyColumn { items(sorted) { ... } }
}
```

**Solution:**
```kotlin
// ✅ Recomposition only if sorted result changed
@Composable
fun ListScreen(items: List<Item>) {
    val sorted = remember {
        derivedStateOf { items.sortedBy { it.name } }
    }
    LazyColumn { items(sorted.value) { ... } }  // structural equality check
}
```

**How it works:**
1. **Dependency tracking**: automatically tracks read `State` objects — `Snapshot` registers all read states
2. **Lazy calculation**: computes only when dependencies change — lazy evaluation until first `.value` access
3. **Structural equality**: `equals()` comparison of old vs new result — prevents recomposition with identical results
4. **Conditional invalidation**: recomposition only if result differs — invalidation occurs only when results are unequal

### Practical Patterns

**Complex filtering:**
```kotlin
@Composable
fun FilteredList(items: State<List<Item>>, filter: State<String>) {
    val filtered = remember {
        derivedStateOf {
            items.value.filter { it.matches(filter.value) }
        }
    }
    // ✅ Recomposition only if filtered list changed (structural equality)
}
```

**Aggregation:**
```kotlin
val totalPrice = remember {
    derivedStateOf {
        cart.items.sumOf { it.price }  // ❌ don't create in loops!
    }
}
```

**When NOT to use:**
- Simple calculations — `derivedStateOf` overhead exceeds benefit for fast operations (e.g., `val sum = a + b`)
- Side effects — use `LaunchedEffect` for side effects (navigation, logging, analytics)
- Suspend functions — no coroutine support inside `derivedStateOf` (synchronous calculations only)
- Mutable collections in dependencies — use `ImmutableList` or `List.toImmutableList()` for correct tracking


## Follow-ups

- How does `Snapshot System` handle concurrent writes from different threads?
- What's the performance overhead of `derivedStateOf` vs direct computation?
- When should you use `snapshotFlow` instead of `derivedStateOf`?
- How does structural equality check work for custom data classes?
- What happens if `derivedStateOf` calculation throws an exception?
- How to optimize `derivedStateOf` with immutable collections?

## References

- [Compose State Documentation](https://developer.android.com/jetpack/compose/state)
- `MVCC` pattern and transaction isolation in UI frameworks
- Memoization optimization techniques

## Related Questions

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

---
id: android-464
title: Derived State Snapshot System / Derived State и система Snapshot
aliases: ["Derived State Snapshot System", "Derived State и система Snapshot"]
topic: android
subtopics: [performance-memory, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-performance-optimization--android--hard, q-compose-slot-table-recomposition--android--hard, q-compose-stability-skippability--android--hard]
created: 2025-10-20
updated: 2025-10-27
tags: [android/performance-memory, android/ui-compose, compose, derived-state, difficulty/hard, optimization, performance, snapshot, state]
sources: [https://developer.android.com/jetpack/compose/state]
date created: Monday, October 27th 2025, 10:27:49 pm
date modified: Wednesday, October 29th 2025, 5:07:37 pm
---

# Вопрос (RU)
> Объясните систему снимков (snapshot system) Compose. Как derivedStateOf оптимизирует перекомпозиции?

# Question (EN)
> Explain Compose's snapshot system. How does derivedStateOf optimize recompositions?

## Ответ (RU)

**Snapshot System** — это механизм управления изменяемым состоянием в Compose, обеспечивающий изоляцию транзакций, thread-safety и атомарность изменений. Работает как MVCC (Multi-Version Concurrency Control) для UI state.

**derivedStateOf** — оптимизирует recomposition, триггерясь только при изменении вычисленного результата, а не промежуточных зависимостей.

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
- **Isolation**: каждый snapshot видит свою версию state
- **Tracking**: автоматическое отслеживание read/write
- **Atomicity**: изменения применяются одновременно
- **Conflict resolution**: handling при параллельных записях

### derivedStateOf: Оптимизация через Memoization

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
1. **Dependency tracking**: автоматическое отслеживание читаемых State
2. **Lazy calculation**: вычисление только при изменении зависимости
3. **Structural equality**: `equals()` сравнение старого и нового результата
4. **Conditional invalidation**: recomposition только если результат отличается

### Практические паттерны

**Complex filtering:**
```kotlin
@Composable
fun FilteredList(items: State<List<Item>>, filter: State<String>) {
    val filtered = remember {
        derivedStateOf {
            items.value.filter { it.matches(filter.value) }
        }
    }
    // ✅ Recomposition только если отфильтрованный список изменился
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
- Простые вычисления (overhead > benefit)
- Side effects (используйте `LaunchedEffect`)
- Suspend функции (нет поддержки coroutines)

## Answer (EN)

**Snapshot System** is Compose's mutable state management mechanism providing transaction isolation, thread-safety, and atomic changes. Works like MVCC (Multi-Version Concurrency Control) for UI state.

**derivedStateOf** optimizes recomposition by triggering only when the computed result changes, not intermediate dependencies.

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
- **Isolation**: each snapshot sees its own state version
- **Tracking**: automatic read/write tracking
- **Atomicity**: changes applied simultaneously
- **Conflict resolution**: handling concurrent writes

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
1. **Dependency tracking**: automatically tracks read State objects
2. **Lazy calculation**: computes only when dependencies change
3. **Structural equality**: `equals()` comparison of old vs new result
4. **Conditional invalidation**: recomposition only if result differs

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
    // ✅ Recomposition only if filtered list changed
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
- Simple calculations (overhead > benefit)
- Side effects (use `LaunchedEffect`)
- Suspend functions (no coroutine support)


## Follow-ups

- How does Snapshot System handle concurrent writes from different threads?
- What's the performance overhead of derivedStateOf vs direct computation?
- When should you use snapshotFlow instead of derivedStateOf?
- How does structural equality check work for custom data classes?
- What happens if derivedStateOf calculation throws an exception?

## References

- Compose state management fundamentals (MVCC pattern, transaction isolation)
- Memoization optimization technique for expensive computations
- Official docs: https://developer.android.com/jetpack/compose/state
- State snapshots deep dive: https://dev.to/zachklipp/remember-mutablestateof-a-cheat-sheet-10ma

## Related Questions

### Prerequisites (Easier)
- Basic Compose state management (mutableStateOf, remember)
- Understanding State vs MutableState interfaces

### Related (Same Level)
- [[q-compose-stability-skippability--android--hard]] - Stability inference and skippability
- [[q-compose-performance-optimization--android--hard]] - Performance optimization patterns
- LaunchedEffect vs derivedStateOf trade-offs

### Advanced (Harder)
- [[q-compose-slot-table-recomposition--android--hard]] - Slot table internals
- Compose compiler optimizations and code generation

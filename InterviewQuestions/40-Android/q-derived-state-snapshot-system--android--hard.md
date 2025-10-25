---
id: 20251020-200000
title: Derived State Snapshot System / Derived State и система Snapshot
aliases:
- Derived State Snapshot System
- Derived State и система Snapshot
topic: android
subtopics:
- ui-compose
- performance-memory
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-compose-stability-skippability--android--hard
- q-compose-performance-optimization--android--hard
- q-compose-slot-table-recomposition--android--hard
created: 2025-10-20
updated: 2025-10-20
tags:
- android/ui-compose
- android/performance-memory
- compose
- state
- snapshot
- optimization
- derived-state
- performance
- difficulty/hard
source: https://developer.android.com/jetpack/compose/state
source_note: Android Compose State documentation
---

# Вопрос (RU)
> Объясните систему снимков (snapshot system) Compose. Как derivedStateOf оптимизирует перекомпозиции?

# Question (EN)
> Explain Compose's snapshot system. How does derivedStateOf optimize recompositions?

## Ответ (RU)

**Система Snapshot** - это основа Compose для управления изменяемым состоянием способом, который является наблюдаемым, потокобезопасным и обеспечивает эффективную перекомпозицию. Она предоставляет **изолированные, согласованные представления** состояния, которые изменяются атомарно.

**derivedStateOf** строится на этой системе для создания вычисляемого состояния, которое запускает перекомпозицию только тогда, когда вычисляемый результат действительно изменяется, а не когда изменяются промежуточные значения.

### Теория: Система Snapshot в Compose

**Основные концепции:**
- **Snapshot** - изолированное представление состояния
- **StateObject** - объект состояния с отслеживанием изменений
- **Snapshot Isolation** - изоляция изменений между снимками
- **Atomic Changes** - атомарные изменения состояния
- **Recomposition Optimization** - оптимизация перекомпозиции

**Принципы работы:**
- Каждый снимок предоставляет изолированное представление состояния
- Изменения невидимы для других снимков до применения
- Множественные снимки могут существовать одновременно
- Изменения применяются атомарно

### Система Snapshot

**Теоретические основы:**
Система Snapshot работает как транзакции базы данных для UI состояния. Она обеспечивает изоляцию, согласованность и атомарность изменений.

**Ключевые компоненты:**
- **Snapshot** - контейнер для изолированных изменений
- **StateObject** - базовый интерфейс для отслеживаемых состояний
- **Snapshot Isolation** - механизм изоляции между снимками
- **State Tracking** - отслеживание чтения и записи состояния

**Компактная реализация:**
```kotlin
class Snapshot {
    private val modified = mutableMapOf<StateObject, Any?>()
    private val readSet = mutableSetOf<StateObject>()

    fun <T> readState(state: StateObject): T {
        readSet.add(state)
        return modified[state] ?: state.currentValue
    }

    fun <T> writeState(state: StateObject, value: T) {
        modified[state] = value
    }

    fun apply() {
        modified.forEach { (state, value) -> state.currentValue = value }
    }
}
```

### derivedStateOf

**Теоретические основы:**
derivedStateOf создает вычисляемое состояние, которое оптимизирует перекомпозицию путем отслеживания только изменений результата вычисления.

**Принципы работы:**
- Отслеживает зависимости автоматически
- Вычисляет значение только при изменении зависимостей
- Запускает перекомпозицию только при изменении результата
- Оптимизирует производительность через мемоизацию

**Компактная реализация:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    var multiplier by remember { mutableStateOf(1) }

    val derivedCount = remember {
        derivedStateOf {
            count * multiplier
        }
    }

    Text(text = "Count: ${derivedCount.value}")
}
```

### Оптимизация перекомпозиции

**Теоретические принципы:**
derivedStateOf оптимизирует перекомпозицию путем отслеживания изменений результата вычисления, а не промежуточных значений.

**Механизм оптимизации:**
- Отслеживает зависимости через систему Snapshot
- Вычисляет значение только при изменении зависимостей
- Сравнивает результат с предыдущим значением
- Запускает перекомпозицию только при изменении результата

**Пример оптимизации:**
```kotlin
@Composable
fun OptimizedList(items: List<String>) {
    val sortedItems = remember {
        derivedStateOf {
            items.sorted()
        }
    }

    LazyColumn {
        items(sortedItems.value) { item ->
            Text(item)
        }
    }
}
```

### Сравнение с другими подходами

**Теоретическое сравнение:**

| Подход | Производительность | Сложность | Оптимизация |
|--------|-------------------|-----------|-------------|
| **mutableStateOf** | Базовая | Низкая | Нет |
| **remember** | Хорошая | Средняя | Частичная |
| **derivedStateOf** | Отличная | Средняя | Полная |
| **LaunchedEffect** | Хорошая | Высокая | Частичная |

**Выбор подхода:**
- **mutableStateOf** - для простого состояния
- **remember** - для вычисляемых значений
- **derivedStateOf** - для оптимизированных вычислений
- **LaunchedEffect** - для побочных эффектов

### Лучшие практики

**Теоретические принципы:**
- Используйте derivedStateOf для дорогих вычислений
- Избегайте создания derivedStateOf в цикле
- Используйте remember для создания derivedStateOf
- Обрабатывайте ошибки в вычислениях
- Тестируйте производительность

**Практические рекомендации:**
- Создавайте derivedStateOf в remember блоке
- Используйте для фильтрации и сортировки списков
- Применяйте для вычисления агрегированных значений
- Избегайте побочных эффектов в derivedStateOf
- Документируйте сложные вычисления

## Answer (EN)

The **Snapshot System** is Compose's foundation for managing mutable state in a way that's observable, thread-safe, and enables efficient recomposition. It provides **isolated, consistent views** of state that change atomically.

**derivedStateOf** builds on this system to create computed state that only triggers recomposition when the computed result actually changes, not when intermediate values change.

### Theory: Snapshot System in Compose

**Core Concepts:**
- **Snapshot** - isolated view of state
- **StateObject** - state object with change tracking
- **Snapshot Isolation** - isolation of changes between snapshots
- **Atomic Changes** - atomic state changes
- **Recomposition Optimization** - recomposition optimization

**Working Principles:**
- Each snapshot provides an isolated view of state
- Changes are invisible to other snapshots until applied
- Multiple snapshots can exist simultaneously
- Changes apply atomically

### Snapshot System

**Theoretical Foundations:**
The Snapshot System works like database transactions for UI state. It provides isolation, consistency, and atomicity of changes.

**Key Components:**
- **Snapshot** - container for isolated changes
- **StateObject** - base interface for tracked states
- **Snapshot Isolation** - isolation mechanism between snapshots
- **State Tracking** - tracking of state reading and writing

**Compact Implementation:**
```kotlin
class Snapshot {
    private val modified = mutableMapOf<StateObject, Any?>()
    private val readSet = mutableSetOf<StateObject>()

    fun <T> readState(state: StateObject): T {
        readSet.add(state)
        return modified[state] ?: state.currentValue
    }

    fun <T> writeState(state: StateObject, value: T) {
        modified[state] = value
    }

    fun apply() {
        modified.forEach { (state, value) -> state.currentValue = value }
    }
}
```

### derivedStateOf

**Theoretical Foundations:**
derivedStateOf creates computed state that optimizes recomposition by tracking only changes in the computation result.

**Working Principles:**
- Tracks dependencies automatically
- Computes value only when dependencies change
- Triggers recomposition only when result changes
- Optimizes performance through memoization

**Compact Implementation:**
```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    var multiplier by remember { mutableStateOf(1) }

    val derivedCount = remember {
        derivedStateOf {
            count * multiplier
        }
    }

    Text(text = "Count: ${derivedCount.value}")
}
```

### Recomposition Optimization

**Theoretical Principles:**
derivedStateOf optimizes recomposition by tracking changes in the computation result, not intermediate values.

**Optimization Mechanism:**
- Tracks dependencies through the Snapshot System
- Computes value only when dependencies change
- Compares result with previous value
- Triggers recomposition only when result changes

**Optimization Example:**
```kotlin
@Composable
fun OptimizedList(items: List<String>) {
    val sortedItems = remember {
        derivedStateOf {
            items.sorted()
        }
    }

    LazyColumn {
        items(sortedItems.value) { item ->
            Text(item)
        }
    }
}
```

### Comparison with Other Approaches

**Theoretical Comparison:**

| Approach | Performance | Complexity | Optimization |
|----------|-------------|------------|--------------|
| **mutableStateOf** | Basic | Low | None |
| **remember** | Good | Medium | Partial |
| **derivedStateOf** | Excellent | Medium | Full |
| **LaunchedEffect** | Good | High | Partial |

**Approach Selection:**
- **mutableStateOf** - for simple state
- **remember** - for computed values
- **derivedStateOf** - for optimized computations
- **LaunchedEffect** - for side effects

### Best Practices

**Theoretical Principles:**
- Use derivedStateOf for expensive computations
- Avoid creating derivedStateOf in loops
- Use remember for creating derivedStateOf
- Handle errors in computations
- Test performance

**Practical Recommendations:**
- Create derivedStateOf in remember block
- Use for filtering and sorting lists
- Apply for computing aggregated values
- Avoid side effects in derivedStateOf
- Document complex computations

**See also:** c-immutability, c-snapshot-isolation


## Follow-ups

- How does derivedStateOf differ from remember?
- What are the performance implications of using derivedStateOf?
- How do you debug snapshot system issues?

## Related Questions

### Related (Same Level)
- [[q-compose-stability-skippability--android--hard]]
- [[q-compose-performance-optimization--android--hard]]

### Advanced (Harder)
- [[q-compose-slot-table-recomposition--android--hard]]

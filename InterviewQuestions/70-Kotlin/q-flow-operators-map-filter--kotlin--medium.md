---
id: kotlin-074
title: "Flow Operators: map, filter, transform"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, filter, flow]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140018

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutinescope-vs-coroutinecontext--kotlin--medium, q-flow-operators--kotlin--medium, q-testing-flow-operators--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/medium, kotlin]
date created: Saturday, October 18th 2025, 12:37:18 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Вопрос (RU)
> Как использовать операторы Flow map, filter, transform? Объясните цепочки операторов и практические паттерны.

---

# Question (EN)
> How to use Flow operators map, filter, transform? Explain operator chaining and practical patterns.

## Ответ (RU)

Операторы Flow `map`, `filter` и `transform` являются фундаментальными инструментами для обработки потоков данных в Kotlin coroutines. Они позволяют трансформировать, фильтровать и манипулировать значениями, испускаемыми Flow, декларативным способом.

### Базовые Операторы

**map** - Трансформирует каждое испущенное значение:
```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { it * 2 }
 .collect { println(it) }  // Выводит: 2, 4, 6
```

**filter** - Фильтрует испускаемые значения на основе предиката:
```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
}.filter { it % 2 == 0 }
 .collect { println(it) }  // Выводит: 2, 4
```

**transform** - Универсальный оператор, который может испускать несколько значений:
```kotlin
flow {
    emit("A")
    emit("B")
}.transform { value ->
    emit("Start: $value")
    emit("End: $value")
}.collect { println(it) }
// Выводит: Start: A, End: A, Start: B, End: B
```

### Цепочки Операторов

Операторы можно объединять в цепочки для создания сложных конвейеров обработки данных:

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
    emit(5)
}.filter { it % 2 == 0 }      // Оставляем только четные числа
 .map { it * it }             // Возводим в квадрат
 .map { "Result: $it" }       // Преобразуем в строку
 .collect { println(it) }
// Выводит: Result: 4, Result: 16
```

### Практические Паттерны

**Паттерн 1: Конвейер трансформации данных**
```kotlin
userInputFlow
    .filter { it.isNotEmpty() }
    .map { it.trim() }
    .map { it.lowercase() }
    .collect { processInput(it) }
```

**Паттерн 2: Обработка ответов API**
```kotlin
apiFlow
    .map { response -> response.data }
    .filter { data -> data.isValid }
    .map { data -> data.toUiModel() }
    .collect { uiModel -> updateUI(uiModel) }
```

**Паттерн 3: Множественные испускания на одно входное значение**
```kotlin
searchQueryFlow
    .transform { query ->
        emit(LoadingState)
        try {
            val results = searchApi(query)
            emit(SuccessState(results))
        } catch (e: Exception) {
            emit(ErrorState(e))
        }
    }
    .collect { state -> updateState(state) }
```

**Паттерн 4: Условная трансформация**
```kotlin
dataFlow
    .transform { value ->
        if (value > 0) {
            emit(value)
            emit(value * 2)
        }
        // Отрицательные значения отбрасываются
    }
    .collect { println(it) }
```

### Соображения Производительности

- Операторы **выполняются последовательно** для каждого испускаемого значения
- **Промежуточные коллекции не создаются** (в отличие от операторов sequence)
- Операторы сохраняют семантику **backpressure** и **отмены**
- Цепочки операторов не создают накладных расходов на производительность

### Типичные Ошибки

1. **Suspend-операции в map**: Используйте `mapNotNull` или `transform`:
```kotlin
// Избегайте
flow.map { async { heavyOperation(it) }.await() }

// Предпочтительно
flow.transform {
    emit(heavyOperation(it))
}
```

2. **Побочные эффекты**: Держите операторы чистыми:
```kotlin
// Избегайте
flow.map {
    updateDatabase(it)  // Побочный эффект!
    it
}

// Предпочтительно
flow.onEach { updateDatabase(it) }
    .map { it }
```

---

## Answer (EN)

Flow operators `map`, `filter`, and `transform` are fundamental tools for processing data streams in Kotlin coroutines. They allow you to transform, filter, and manipulate Flow emissions in a declarative way.

### Basic Operators

**map** - Transforms each emitted value:
```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { it * 2 }
 .collect { println(it) }  // Prints: 2, 4, 6
```

**filter** - Filters emissions based on a predicate:
```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
}.filter { it % 2 == 0 }
 .collect { println(it) }  // Prints: 2, 4
```

**transform** - General-purpose operator that can emit multiple values:
```kotlin
flow {
    emit("A")
    emit("B")
}.transform { value ->
    emit("Start: $value")
    emit("End: $value")
}.collect { println(it) }
// Prints: Start: A, End: A, Start: B, End: B
```

### Operator Chaining

Operators can be chained to create complex data processing pipelines:

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
    emit(5)
}.filter { it % 2 == 0 }      // Keep only even numbers
 .map { it * it }             // Square each number
 .map { "Result: $it" }       // Convert to string
 .collect { println(it) }
// Prints: Result: 4, Result: 16
```

### Practical Patterns

**Pattern 1: Data transformation pipeline**
```kotlin
userInputFlow
    .filter { it.isNotEmpty() }
    .map { it.trim() }
    .map { it.lowercase() }
    .collect { processInput(it) }
```

**Pattern 2: API response processing**
```kotlin
apiFlow
    .map { response -> response.data }
    .filter { data -> data.isValid }
    .map { data -> data.toUiModel() }
    .collect { uiModel -> updateUI(uiModel) }
```

**Pattern 3: Multiple emissions per input**
```kotlin
searchQueryFlow
    .transform { query ->
        emit(LoadingState)
        try {
            val results = searchApi(query)
            emit(SuccessState(results))
        } catch (e: Exception) {
            emit(ErrorState(e))
        }
    }
    .collect { state -> updateState(state) }
```

**Pattern 4: Conditional transformation**
```kotlin
dataFlow
    .transform { value ->
        if (value > 0) {
            emit(value)
            emit(value * 2)
        }
        // Negative values are dropped
    }
    .collect { println(it) }
```

### Performance Considerations

- Operators are **executed sequentially** for each emission
- **No intermediate collections** are created (unlike sequence operators)
- Operators preserve **backpressure** and **cancellation** semantics
- Chaining multiple operators doesn't create performance overhead

### Common Pitfalls

1. **Suspending operations in map**: Use `mapNotNull` or `transform` instead:
```kotlin
// Avoid
flow.map { async { heavyOperation(it) }.await() }

// Prefer
flow.transform {
    emit(heavyOperation(it))
}
```

2. **Side effects**: Keep operators pure:
```kotlin
// Avoid
flow.map {
    updateDatabase(it)  // Side effect!
    it
}

// Prefer
flow.onEach { updateDatabase(it) }
    .map { it }
```

---

## Follow-ups

1. **Follow-up question 1**
2. **Follow-up question 2**

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators--kotlin--medium]] - Flow
- [[q-retry-operators-flow--kotlin--medium]] - Flow
- [[q-flow-time-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction


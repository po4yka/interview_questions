---
id: 20251012-140023
title: "Flow Performance Optimization / Оптимизация производительности Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, advanced, patterns]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140023

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-flow-backpressure--kotlin--hard, q-kotlin-enum-classes--kotlin--easy, q-kotlin-property-delegates--programming-languages--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, difficulty/medium]
---
# Question (EN)
> Kotlin Coroutines advanced topic 140023

# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140023

---

## Answer (EN)


Flow performance optimization focuses on efficient data processing, proper buffering, and avoiding unnecessary operations.

### Key Performance Techniques

**1. Buffering**
```kotlin
flow {
    repeat(100) {
        emit(it)
        delay(100)  // Slow producer
    }
}.buffer()  // Buffer emissions
 .collect {
     delay(300)  // Slow collector
 }
```

**2. Conflation**
```kotlin
flow {
    repeat(100) { emit(it) }
}.conflate()  // Drop intermediate values
 .collect { /* only latest */ }
```

**3. collectLatest**
```kotlin
flow.collectLatest { value ->
    // Cancel previous, process only latest
    processValue(value)
}
```

**4. Parallel Processing**
```kotlin
flow.map { item ->
    withContext(Dispatchers.Default) {
        processItem(item)
    }
}.collect()
```

**5. Channel Buffers**
```kotlin
flow.buffer(capacity = 64)
flow.buffer(Channel.UNLIMITED)
flow.buffer(Channel.CONFLATED)
```

### Benchmarking
```kotlin
measureTimeMillis {
    flow.collect { /* process */ }
}.also { println("Took ${it}ms") }
```

---
---

## Ответ (RU)


Оптимизация производительности Flow фокусируется на эффективной обработке данных, правильной буферизации и избежании ненужных операций.

### Ключевые техники производительности

**1. Буферизация**
```kotlin
flow {
    repeat(100) {
        emit(it)
        delay(100)  // Медленный производитель
    }
}.buffer()  // Буферизация испусканий
 .collect {
     delay(300)  // Медленный коллектор
 }
```

**2. Conflation**
```kotlin
flow {
    repeat(100) { emit(it) }
}.conflate()  // Отбрасывать промежуточные значения
 .collect { /* только последнее */ }
```

**3. collectLatest**
```kotlin
flow.collectLatest { value ->
    // Отменить предыдущее, обработать только последнее
    processValue(value)
}
```

**4. Параллельная обработка**
```kotlin
flow.map { item ->
    withContext(Dispatchers.Default) {
        processItem(item)
    }
}.collect()
```

**5. Буферы каналов**
```kotlin
flow.buffer(capacity = 64)
flow.buffer(Channel.UNLIMITED)
flow.buffer(Channel.CONFLATED)
```

### Бенчмаркинг
```kotlin
measureTimeMillis {
    flow.collect { /* process */ }
}.also { println("Took ${it}ms") }
```

---
---

## Follow-ups

1. **Follow-up question 1**
2. **Follow-up question 2**

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

---

## Related Questions

### Related (Hard)
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines
- [[q-dispatcher-performance--kotlin--hard]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines

### Prerequisites (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction


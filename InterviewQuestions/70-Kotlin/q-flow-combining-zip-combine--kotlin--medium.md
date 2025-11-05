---
id: kotlin-101
title: "Flow Combining: zip, combine, merge"
aliases: []

# Classification
topic: kotlin
subtopics: [advanced, coroutines, patterns]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140020

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-collections--kotlin--easy, q-kotlin-operator-overloading--kotlin--medium, q-testing-coroutine-timing-control--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [coroutines, difficulty/medium, kotlin]
date created: Sunday, October 12th 2025, 3:39:19 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140020

---

# Question (EN)
> Kotlin Coroutines advanced topic 140020

## Ответ (RU)


Операторы комбинирования Flow позволяют объединять несколько Flow различными способами: `zip` связывает испускания попарно, `combine` испускает при любом изменении, а `merge` чередует все испускания.

### Zip
Комбинирует два потока связывая их испускания:
```kotlin
val flow1 = flowOf(1, 2, 3)
val flow2 = flowOf("A", "B", "C", "D")

flow1.zip(flow2) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Вывод: 1A, 2B, 3C (D отброшен)
```

### Combine
Испускает когда ЛЮБОЙ поток испускает:
```kotlin
val numbers = flow {
    emit(1)
    delay(100)
    emit(2)
}
val letters = flow {
    emit("A")
    delay(150)
    emit("B")
}

numbers.combine(letters) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Вывод: 1A, 2A, 2B
```

### Merge
Объединяет несколько потоков в один:
```kotlin
val flow1 = flowOf(1, 2, 3).onEach { delay(100) }
val flow2 = flowOf(4, 5, 6).onEach { delay(150) }

merge(flow1, flow2).collect { println(it) }
// Вывод: 1, 4, 2, 3, 5, 6 (чередуются)
```

### Практические Примеры
```kotlin
// Комбинировать ввод пользователя с данными API
searchQuery.combine(apiResults) { query, results ->
    results.filter { it.matches(query) }
}

// Связать координаты с адресами
latLng.zip(addresses) { coords, address ->
    Location(coords, address)
}

// Объединить несколько источников данных
merge(cacheFlow, networkFlow, databaseFlow)
```

---
---

## Answer (EN)


Flow combining operators allow you to merge multiple Flows in different ways: `zip` pairs emissions, `combine` emits on any change, and `merge` interleaves all emissions.

### Zip
Combines two flows by pairing their emissions:
```kotlin
val flow1 = flowOf(1, 2, 3)
val flow2 = flowOf("A", "B", "C", "D")

flow1.zip(flow2) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Output: 1A, 2B, 3C (D is dropped)
```

### Combine
Emits whenever ANY flow emits:
```kotlin
val numbers = flow {
    emit(1)
    delay(100)
    emit(2)
}
val letters = flow {
    emit("A")
    delay(150)
    emit("B")
}

numbers.combine(letters) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Output: 1A, 2A, 2B
```

### Merge
Merges multiple flows into one:
```kotlin
val flow1 = flowOf(1, 2, 3).onEach { delay(100) }
val flow2 = flowOf(4, 5, 6).onEach { delay(150) }

merge(flow1, flow2).collect { println(it) }
// Output: 1, 4, 2, 3, 5, 6 (interleaved)
```

### Practical Examples
```kotlin
// Combine user input with API data
searchQuery.combine(apiResults) { query, results ->
    results.filter { it.matches(query) }
}

// Zip coordinates with addresses
latLng.zip(addresses) { coords, address ->
    Location(coords, address)
}

// Merge multiple data sources
merge(cacheFlow, networkFlow, databaseFlow)
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

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
- [[q-suspend-functions-basics--kotlin--easy]] - Coroutines
- [[q-coroutine-builders-basics--kotlin--easy]] - Coroutines
### Advanced (Harder)
- [[q-flow-performance--kotlin--hard]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow


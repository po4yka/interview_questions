---
id: kotlin-101
title: "Flow Combining: zip, combine, merge / Комбинирование Flow: zip, combine, merge"
aliases: []
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140020
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, q-kotlin-collections--kotlin--easy]
created: 2025-10-12
updated: 2025-11-11
tags: [coroutines, difficulty/medium, kotlin]

date created: Sunday, October 12th 2025, 3:39:19 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140020

# Question (EN)
> Kotlin `Coroutines` advanced topic 140020

## Ответ (RU)

Операторы комбинирования `Flow` позволяют объединять несколько `Flow` различными способами: `zip` связывает испускания попарно, `combine` после первого значения от каждого источника испускает при любом изменении, а `merge` просто пробрасывает все значения по мере их поступления без гарантированного порядка.

### Zip
Комбинирует два потока, связывая их испускания по индексам, пока оба источника могут выдать элемент:
```kotlin
val flow1 = flowOf(1, 2, 3)
val flow2 = flowOf("A", "B", "C", "D")

flow1.zip(flow2) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Вывод: 1A, 2B, 3C (D отброшен, так как flow1 завершился раньше)
```

### Combine
Испускает значение, когда ЛЮБОЙ поток испускает, но только после того, как каждый из потоков выдал хотя бы одно значение. Всегда использует последние значения из обоих потоков:
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
// Возможный вывод: 1A, 2A, 2B
```

### Merge
Объединяет несколько потоков в один, пробрасывая значения по мере их прихода. Порядок чередования не гарантируется и зависит от времён испускания:
```kotlin
val flow1 = flowOf(1, 2, 3).onEach { delay(100) }
val flow2 = flowOf(4, 5, 6).onEach { delay(150) }

merge(flow1, flow2).collect { println(it) }
// Пример возможного вывода: 1, 4, 2, 3, 5, 6 (фактический порядок может отличаться)
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

См. также: [[c-flow]], [[c-coroutines]]

## Answer (EN)

`Flow` combining operators allow you to merge multiple `Flow`s in different ways: `zip` pairs emissions index-wise, `combine` (after each source has emitted at least once) emits on any change using the latest values, and `merge` simply forwards all emissions as they arrive without guaranteeing order.

### Zip
Combines two flows by pairing their emissions by index, as long as both flows can provide an element:
```kotlin
val flow1 = flowOf(1, 2, 3)
val flow2 = flowOf("A", "B", "C", "D")

flow1.zip(flow2) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Output: 1A, 2B, 3C (D is dropped because flow1 completes earlier)
```

### Combine
Emits whenever ANY flow emits, but only after each flow has produced at least one value. It always uses the latest value from each flow:
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
// Possible output: 1A, 2A, 2B
```

### Merge
Merges multiple flows into one by forwarding values as they come. The interleaving order is not guaranteed and depends on emission timing:
```kotlin
val flow1 = flowOf(1, 2, 3).onEach { delay(100) }
val flow2 = flowOf(4, 5, 6).onEach { delay(150) }

merge(flow1, flow2).collect { println(it) }
// Example possible output: 1, 4, 2, 3, 5, 6 (actual order may vary)
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

See also: [[c-flow]], [[c-coroutines]]

## Дополнительные Вопросы (RU)

1. Объясните, как механизм backpressure и буферизация взаимодействуют с `zip`, `combine` и `merge` при работе с медленными и быстрыми источниками `Flow`.
2. Сравните `merge` с паттернами fan-in на основе каналов: когда в реальном приложении вы предпочтёте один подход другому?
3. Как вы будете выбирать между `Flow`, `LiveData`, `StateFlow` и `SharedFlow` для представления комбинированных потоков состояния UI?
4. Имея три `Flow` (ввод пользователя, кеш и сеть), спроектируйте цепочку операторов, обеспечивающую отзывчивый UI и минимизацию лишних сетевых вызовов.
5. Какие подводные камни возникают при комбинировании бесконечных или никогда не завершающихся `Flow`, и как их можно смягчить?

## Follow-ups

1. Explain how backpressure and buffering interact with `zip`, `combine`, and `merge` when working with slow and fast `Flow` sources.
2. Compare `merge` with channels-based fan-in patterns: when would you prefer one over the other in a real application?
3. How would you choose between `Flow`, `LiveData`, `StateFlow`, and `SharedFlow` for representing combined UI state streams?
4. Given three `Flow`s (user input, cache, and network), design an operator chain that provides responsive UI while minimizing wasted network calls.
5. What pitfalls can occur when combining infinite or never-completing `Flow`s, and how can you mitigate them?

## Ссылки (RU)

- [Документация по Kotlin `Coroutines`](https://kotlinlang.org/docs/coroutines-overview.html)

## References

- [Kotlin `Coroutines` Documentation](https://kotlinlang.org/docs/coroutines-overview.html)

## Связанные Вопросы (RU)

### Предварительная Подготовка (проще)
- [[q-what-is-coroutine--kotlin--easy]] - Корутины
- [[q-suspend-functions-basics--kotlin--easy]] - Базовые `suspend`-функции
- [[q-coroutine-builders-basics--kotlin--easy]] - Базовые билдеры корутин

### Продвинуто (сложнее)
- [[q-flow-performance--kotlin--hard]] - Производительность `Flow`
- [[q-select-expression-channels--kotlin--hard]] - `select` и каналы
- [[q-coroutine-profiling--kotlin--hard]] - Профилирование корутин
- [[q-flowon-operator-context-switching--kotlin--hard]] - Оператор `flowOn` и переключение контекстов
- [[q-flow-backpressure--kotlin--hard]] - Обработка backpressure в `Flow`
- [[q-flow-backpressure-strategies--kotlin--hard]] - Стратегии backpressure

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] - Введение в `Flow`

### Связанные (средний уровень)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold `Flow`
- [[q-cold-vs-hot-flows--kotlin--medium]] - Объяснение Cold vs Hot `Flow`
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` против `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Каналы против `Flow`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` против `StateFlow`

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - `Coroutines`
- [[q-suspend-functions-basics--kotlin--easy]] - Basic `suspend` functions
- [[q-coroutine-builders-basics--kotlin--easy]] - `Coroutine` builders

### Advanced (Harder)
- [[q-flow-performance--kotlin--hard]] - `Flow` performance
- [[q-select-expression-channels--kotlin--hard]] - `select` expression & channels
- [[q-coroutine-profiling--kotlin--hard]] - `Coroutine` profiling
- [[q-flowon-operator-context-switching--kotlin--hard]] - `flowOn` & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs `Flow`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`

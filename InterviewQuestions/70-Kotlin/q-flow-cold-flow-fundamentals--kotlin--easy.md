---
---
---\
id: kotlin-089
title: "Что делает Flow холодным потоком? / What makes Flow a cold stream?"
aliases: [Cold, Flow, Fundamentals]
topic: kotlin
subtopics: ["basics", "cold-streams", "coroutines"]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, q-flow-basics--kotlin--easy]
created: 2025-10-12
updated: 2025-11-09
tags: ["coroutines", "difficulty/easy", "kotlin"]
---\
# Вопрос (RU)

> Что делает `Flow` холодным потоком?

# Question (EN)

> What makes `Flow` a cold stream?

## Ответ (RU)

Ключевые свойства, делающие `Flow` холодным потоком:

1. Ленивое выполнение
- `Flow` не выполняется и не производит значения, пока у него нет хотя бы одного коллектора.
- Код внутри билдера `flow { ... }` и цепочки операторов выполняется только при вызове `collect`.

Пример:
```kotlin
val numbers = flow {
    println("Flow started")
    emit(1)
    emit(2)
    emit(3)
}

println("Before collect")

runBlocking {
    numbers.collect { value ->
        println("Collected $value")
    }
}

// Вывод:
// Before collect
// Flow started
// Collected 1
// Collected 2
// Collected 3
```
- "`Flow` started" выводится только при вызове `collect`, что показывает отсутствие жадного выполнения.

1. Выполнение заново для каждого коллектора
- Каждый новый коллектор запускает исходный `Flow` с начала.
- Эмиссии не разделяются автоматически между коллекторами.

Пример:
```kotlin
val coldFlow = flow {
    println("Producing values")
    emit(1)
    emit(2)
}

runBlocking {
    println("First collection")
    coldFlow.collect { println("First -> $it") }

    println("Second collection")
    coldFlow.collect { println("Second -> $it") }
}

// Вывод:
// First collection
// Producing values
// First -> 1
// First -> 2
// Second collection
// Producing values
// Second -> 1
// Second -> 2
```
- Строка "Producing values" появляется для каждого `collect`, подтверждая, что источник выполняется отдельно для каждого подписчика.

1. Декларативное описание потока
- `Flow` описывает, как производить значения, а не хранит сами значения.
- Пока `Flow` не собран, это только декларация и цепочка операторов.

1. Контекст выполнения
- По умолчанию `Flow` выполняется в контексте корутины коллектора, если не переопределён с помощью `flowOn` и других операторов.
- Это подчёркивает, что выполнение производителя привязано к акту коллекции.

1. Сравнение с «горячими» потоками (для интуиции)
- Горячие потоки (например, `SharedFlow`, `StateFlow`, внешние источники событий) производят значения независимо от наличия коллекторов.
- Холодный `Flow`: производство привязано к `collect`.
- Поэтому `Flow` удобен для одноразовых операций, сетевых запросов и последовательностей, которые должны быть полностью воспроизведены для каждого потребителя.

Практические выводы:
- Эффективное использование ресурсов: без коллектора вычисления не запускаются.
- Детерминированность для каждого коллектора: каждый видит полную последовательность значений с начала.
- Для совместного потребления эмиссий между несколькими коллекторами `Flow` нужно превратить в горячий поток (`shareIn`, `stateIn` или отдельный `SharedFlow`/`StateFlow`).

## Answer (EN)

Key properties that make `Flow` a cold stream:

1. Lazy execution
- A `Flow` does not run or produce values until it has at least one collector.
- The code inside the flow builder (`flow { ... }`) or operator chain executes only when `collect` is called.

Example:
```kotlin
val numbers = flow {
    println("Flow started")
    emit(1)
    emit(2)
    emit(3)
}

println("Before collect")

runBlocking {
    numbers.collect { value ->
        println("Collected $value")
    }
}

// Output:
// Before collect
// Flow started
// Collected 1
// Collected 2
// Collected 3
```
- "`Flow` started" is printed only when `collect` is invoked, showing that the `Flow` does not execute eagerly.

1. Per-collector execution
- Each new collector triggers the upstream `Flow` to run from the beginning.
- Emissions are not shared automatically between collectors.

Example:
```kotlin
val coldFlow = flow {
    println("Producing values")
    emit(1)
    emit(2)
}

runBlocking {
    println("First collection")
    coldFlow.collect { println("First -> $it") }

    println("Second collection")
    coldFlow.collect { println("Second -> $it") }
}

// Output:
// First collection
// Producing values
// First -> 1
// First -> 2
// Second collection
// Producing values
// Second -> 1
// Second -> 2
```
- The "Producing values" line appears for each collector, confirming that the source is re-executed per subscription.

1. Declarative description of the stream
- `Flow` represents a description of how to produce values, not the values themselves.
- Until collected, it is just a pipeline of operators.

1. Execution context
- By default, `Flow` runs in the coroutine context of the collector, unless modified with operators like `flowOn`.
- This reinforces that the producer's execution is tied to the act of collection.

1. Contrast with hot streams (for intuition)
- Hot streams (e.g., `SharedFlow`, `StateFlow`, external event sources) produce values independently of having collectors.
- Cold `Flow`: production is bound to collection.
- This distinction explains why `Flow` is suitable for one-off computations, network calls, and sequences of values tied to specific collectors.

Practical implications:
- Efficient resource usage: no work is done without collectors.
- Deterministic behavior per collector: each collector sees the full sequence from the start.
- To share emissions between multiple collectors, you must convert to a hot stream (e.g., `shareIn`, `stateIn`, or external `SharedFlow`/`StateFlow`).

---

## Дополнительные Вопросы (RU)

1. В чём различия между горячими потоками (`SharedFlow`, `StateFlow`) и холодным `Flow` с точки зрения жизненного цикла и подписчиков?
2. Как преобразовать холодный `Flow` в горячий поток с помощью `shareIn` или `stateIn`?
3. Какие типичные ошибки возникают при сборе `Flow` в Android (жизненный цикл, отмена)?
4. Как работает «backpressure» (контроль скорости) в `Flow` и его операторах?
5. В каких случаях следует предпочесть `Flow` вместо `suspend`-функций или `Sequence`?

## Follow-ups

1. How do hot flows (`SharedFlow`, `StateFlow`) differ from cold `Flow` in terms of lifecycle and subscribers?
2. How can you convert a cold `Flow` to a hot stream using `shareIn` or `stateIn`?
3. What are common pitfalls when collecting `Flow` in Android (lifecycle, cancellation)?
4. How does backpressure work with `Flow` and its operators?
5. When should you prefer `Flow` over `suspend` functions or sequences?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-flow]]
- Официальная документация "Kotlin Coroutines" по `Flow`
- Справочник по API `Flow` из kotlinx.coroutines

## References

- [[c-kotlin]]
- [[c-flow]]
- "Kotlin Coroutines" official documentation on `Flow`
- kotlinx.coroutines `Flow` API reference

## Связанные Вопросы (RU)

### Тот Же Уровень (Easy)
- [[q-flow-basics--kotlin--easy]] - основы и создание `Flow`

### Следующие Шаги (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - горячие vs холодные потоки
- [[q-cold-vs-hot-flows--kotlin--medium]] - различия холодных и горячих потоков
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - сравнение `Flow` и `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - каналы против `Flow`

### Продвинутый Уровень (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - тестирование операторов `Flow`
- [[q-flow-backpressure--kotlin--hard]] - управление потоком данных в `Flow`
- [[q-flow-testing-advanced--kotlin--hard]] - продвинутое тестирование `Flow`

### Предпосылки (Easier)
- [[q-flow-basics--kotlin--easy]] - основы `Flow`

### Похожие Вопросы (Same Level)
- [[q-catch-operator-flow--kotlin--medium]] - оператор `catch` в `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - операторы `map`/`filter` в `Flow`
- [[q-hot-cold-flows--kotlin--medium]] - горячие и холодные потоки
- [[q-channel-flow-comparison--kotlin--medium]] - сравнение каналов и `Flow`

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] - обзор основ `Flow`

## Related Questions

### Same Level (Easy)
- [[q-flow-basics--kotlin--easy]] - `Flow` basics and creation

### Next Steps (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs `Flow`

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Testing `Flow` operators
- [[q-flow-backpressure--kotlin--hard]] - Backpressure and flow control in `Flow`
- [[q-flow-testing-advanced--kotlin--hard]] - Advanced `Flow` testing

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - `Flow`

### Related (Same Level)
- [[q-catch-operator-flow--kotlin--medium]] - `catch` operator in `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - `map`/`filter` operators in `Flow`
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows overview
- [[q-channel-flow-comparison--kotlin--medium]] - Channels vs `Flow`

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

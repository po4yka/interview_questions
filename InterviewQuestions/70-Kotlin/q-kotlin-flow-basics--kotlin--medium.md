---
id: 20251005-222650
title: "Kotlin Flow Basics / Основы Flow в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, coroutines, async, reactive-streams]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, flow, coroutines, async, reactive-streams, difficulty/medium]
---
# Question (EN)
> What do you know about Flow in Kotlin?
# Вопрос (RU)
> Что вы знаете о Flow в Kotlin?

---

## Answer (EN)

In coroutines, a *flow* is a type that can emit multiple values sequentially, as opposed to *suspend functions* that return only a single value. For example, you can use a flow to receive live updates from a database.

Flows are built on top of coroutines and can provide multiple values. A flow is conceptually a *stream of data* that can be computed asynchronously. To represent the stream of values that are being asynchronously computed, we can use a `Flow<Int>` type:

```kotlin
fun simple(): Flow<Int> = flow { // flow builder
    for (i in 1..3) {
        delay(100) // pretend we are doing something useful here
        emit(i) // emit next value
    }
}

fun main() = runBlocking<Unit> {
    // Launch a concurrent coroutine to check if the main thread is blocked
    launch {
        for (k in 1..3) {
            println("I'm not blocked $k")
            delay(100)
        }
    }
    // Collect the flow
    simple().collect { value -> println(value) }
}
```

This code waits 100ms before printing each number without blocking the main thread. This is verified by printing "I'm not blocked" every 100ms from a separate coroutine that is running in the main thread:

```
I'm not blocked 1
1
I'm not blocked 2
2
I'm not blocked 3
3
```

A flow is very similar to an `Iterator` that produces a sequence of values, but it uses suspend functions to produce and consume values asynchronously. This means, for example, that the flow can safely make a network request to produce the next value without blocking the main thread.

There are three entities involved in streams of data:
- A **producer** produces data that is added to the stream. Thanks to coroutines, flows can also produce data asynchronously;
- **(Optional) Intermediaries** can modify each value emitted into the stream or the stream itself;
- A **consumer** consumes the values from the stream.

In Android, a *data source* or *repository* is typically a producer of UI data that has the `View` as the consumer that ultimately displays the data. Other times, the `View` layer is a producer of user input events and other layers of the hierarchy consume them. Layers in between the producer and consumer usually act as intermediaries that modify the stream of data to adjust it to the requirements of the following layer.

### Flow builders

There are the following basic ways to create a flow:
- [`flowOf(…)`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flow-of.html) functions to create a flow from a fixed set of values;
- [`asFlow()`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/kotlin.-function0/as-flow.html) extension functions on various types to convert them into flows;
- [`flow { … }`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/#) builder function to construct arbitrary flows from sequential calls to `emit` function;
- [`channelFlow { … }`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/channel-flow.html) builder function to construct arbitrary flows from potentially concurrent calls to the `send` function.
- [`MutableStateFlow`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-state-flow/index.html) and [`MutableSharedFlow()`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow/index.html) define the corresponding constructor functions to create a *hot* flow that can be directly updated.

### Flows are cold

Flows are *cold streams* similar to sequences — the code inside a flow builder does not run until the flow is collected. This becomes clear in the following example:

```kotlin
fun simple(): Flow<Int> = flow {
    println("Flow started")
    for (i in 1..3) {
        delay(100)
        emit(i)
    }
}

fun main() = runBlocking<Unit> {
    println("Calling simple function...")
    val flow = simple()
    println("Calling collect...")
    flow.collect { value -> println(value) }
    println("Calling collect again...")
    flow.collect { value -> println(value) }
}
```

Which prints:
```
Calling simple function...
Calling collect...
Flow started
1
2
3
Calling collect again...
Flow started
1
2
3
```

This is a key reason the `simple` function (which returns a flow) is not marked with `suspend` modifier. By itself, `simple()` call returns quickly and does not wait for anything. The flow starts every time it is collected, that is why we see "Flow started" when we call `collect` again.

*Intermediate operators* on the flow such as `map`, `filter`, `take`, `zip`, etc are functions that are applied to the *upstream* flow or flows and return a *downstream* flow where further operators can be applied to. Intermediate operations do not execute any code in the flow and are not suspending functions themselves. They only set up a chain of operations for future execution and quickly return. This is known as a *cold flow* property.

### Collecting from a flow

Use a *terminal operator* to trigger the flow to start listening for values. Terminal operators on the flow are either suspending functions such as `collect`, `single`, `reduce`, `toList`, etc. or `launchIn` operator that starts collection of the flow in the given scope. They are applied to the upstream flow and trigger execution of all operations. Execution of the flow is also called *collecting the flow* and is always performed in a suspending manner without actual blocking. Terminal operators complete normally or exceptionally depending on successful or failed execution of all the flow operations in the upstream. The most basic terminal operator is collect, for example:

```kotlin
try {
    flow.collect { value ->
        println("Received $value")
    }
} catch (e: Exception) {
    println("The flow has thrown an exception: $e")
}
```

By default, flows are *sequential* and all flow operations are executed sequentially in the same coroutine, with an exception for a few operations specifically designed to introduce concurrency into flow execution such as [buffer](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/buffer.html) and [flatMapMerge](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flat-map-merge.html).

## Ответ (RU)

В корутинах *flow* — это тип, который может последовательно выдавать несколько значений, в отличие от *suspend функций*, которые возвращают только одно значение. Например, вы можете использовать flow для получения живых обновлений из базы данных.

Flow построены поверх корутин и могут предоставлять несколько значений. Flow концептуально является *потоком данных*, который может вычисляться асинхронно. Чтобы представить поток значений, которые вычисляются асинхронно, мы можем использовать тип `Flow<Int>`:

```kotlin
fun simple(): Flow<Int> = flow { // билдер flow
    for (i in 1..3) {
        delay(100) // делаем вид, что здесь делаем что-то полезное
        emit(i) // выдаем следующее значение
    }
}

fun main() = runBlocking<Unit> {
    // Запускаем параллельную корутину чтобы проверить не блокируется ли главный поток
    launch {
        for (k in 1..3) {
            println("I'm not blocked $k")
            delay(100)
        }
    }
    // Собираем flow
    simple().collect { value -> println(value) }
}
```

Этот код ждет 100мс перед выводом каждого числа без блокировки главного потока. Это проверяется выводом "I'm not blocked" каждые 100мс из отдельной корутины, которая работает в главном потоке:

```
I'm not blocked 1
1
I'm not blocked 2
2
I'm not blocked 3
3
```

Flow очень похож на `Iterator`, который производит последовательность значений, но он использует suspend функции для асинхронного производства и потребления значений. Это означает, например, что flow может безопасно сделать сетевой запрос для производства следующего значения без блокировки главного потока.

В потоках данных участвуют три сущности:
- **Производитель** производит данные, которые добавляются в поток. Благодаря корутинам, flow также могут производить данные асинхронно;
- **(Опционально) Посредники** могут модифицировать каждое значение, выдаваемое в поток, или сам поток;
- **Потребитель** потребляет значения из потока.

В Android *источник данных* или *репозиторий* обычно является производителем UI данных, где `View` является потребителем, который в конечном итоге отображает данные. В другие времена слой `View` является производителем событий пользовательского ввода, а другие слои иерархии их потребляют. Слои между производителем и потребителем обычно действуют как посредники, которые модифицируют поток данных для адаптации к требованиям следующего слоя.

### Билдеры Flow

Существуют следующие основные способы создания flow:
- Функции [`flowOf(…)`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flow-of.html) для создания flow из фиксированного набора значений;
- Функции-расширения [`asFlow()`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/kotlin.-function0/as-flow.html) для различных типов для конвертации их в flow;
- Билдер-функция [`flow { … }`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/#) для построения произвольных flow из последовательных вызовов функции `emit`;
- Билдер-функция [`channelFlow { … }`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/channel-flow.html) для построения произвольных flow из потенциально параллельных вызовов функции `send`.
- [`MutableStateFlow`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-state-flow/index.html) и [`MutableSharedFlow()`](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow/index.html) определяют соответствующие функции-конструкторы для создания *горячего* flow, который может быть непосредственно обновлен.

### Flow являются холодными

Flow являются *холодными потоками*, похожими на последовательности — код внутри билдера flow не выполняется до тех пор, пока flow не будет собран. Это становится ясно из следующего примера:

```kotlin
fun simple(): Flow<Int> = flow {
    println("Flow started")
    for (i in 1..3) {
        delay(100)
        emit(i)
    }
}

fun main() = runBlocking<Unit> {
    println("Calling simple function...")
    val flow = simple()
    println("Calling collect...")
    flow.collect { value -> println(value) }
    println("Calling collect again...")
    flow.collect { value -> println(value) }
}
```

Что выводит:
```
Calling simple function...
Calling collect...
Flow started
1
2
3
Calling collect again...
Flow started
1
2
3
```

Это ключевая причина, по которой функция `simple` (которая возвращает flow) не помечена модификатором `suspend`. Сам по себе вызов `simple()` возвращается быстро и ничего не ждет. Flow запускается каждый раз, когда он собирается, поэтому мы видим "Flow started" когда вызываем `collect` снова.

*Промежуточные операторы* на flow, такие как `map`, `filter`, `take`, `zip` и т.д., являются функциями, которые применяются к *upstream* flow или flows и возвращают *downstream* flow, к которому могут быть применены дальнейшие операторы. Промежуточные операции не выполняют никакого кода в flow и не являются suspend функциями. Они только настраивают цепочку операций для будущего выполнения и быстро возвращаются. Это известно как свойство *холодного flow*.

### Сбор из flow

Используйте *терминальный оператор* для запуска flow и начала прослушивания значений. Терминальные операторы на flow являются либо suspend функциями, такими как `collect`, `single`, `reduce`, `toList` и т.д., либо оператором `launchIn`, который запускает сбор flow в заданной области видимости. Они применяются к upstream flow и запускают выполнение всех операций. Выполнение flow также называется *сбором flow* и всегда выполняется приостанавливающим образом без фактической блокировки. Терминальные операторы завершаются нормально или исключительно в зависимости от успешного или неудачного выполнения всех операций flow в upstream. Самым базовым терминальным оператором является collect, например:

```kotlin
try {
    flow.collect { value ->
        println("Received $value")
    }
} catch (e: Exception) {
    println("The flow has thrown an exception: $e")
}
```

По умолчанию flow являются *последовательными*, и все операции flow выполняются последовательно в одной корутине, за исключением нескольких операций, специально разработанных для внесения параллелизма в выполнение flow, таких как [buffer](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/buffer.html) и [flatMapMerge](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/flat-map-merge.html).

---

## References
- [Kotlin Flow Documentation](https://kotlinlang.org/docs/reference/coroutines/flow.html)
- [Android Flow Guide](https://developer.android.com/kotlin/flow)
- [Flow API Reference](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/)
- [Testing Kotlin flows on Android](https://developer.android.com/kotlin/flow/test)
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

## Related Questions

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - Flow basics and creation
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Cold flow fundamentals

### Flow Fundamentals (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - StateFlow & SharedFlow differences
- [[q-stateflow-sharedflow-android--kotlin--medium]] - StateFlow & SharedFlow in Android
- [[q-statein-sharein-flow--kotlin--medium]] - stateIn and shareIn operators

### Flow Operators (Medium)
- [[q-sharedflow-replay-buffer-config--kotlin--medium]] - SharedFlow replay & buffer config
- [[q-flow-operators--kotlin--medium]] - Flow operators overview
- [[q-flow-operators-map-filter--kotlin--medium]] - map, filter, transform operators
- [[q-flow-time-operators--kotlin--medium]] - debounce, sample, throttle
- [[q-debounce-throttle-flow--kotlin--medium]] - Debounce vs Throttle
- [[q-flatmap-variants-flow--kotlin--medium]] - flatMapConcat/Merge/Latest
- [[q-flow-combining-zip-combine--kotlin--medium]] - zip, combine, merge
- [[q-catch-operator-flow--kotlin--medium]] - catch operator
- [[q-flow-completion-oncompletion--kotlin--medium]] - onCompletion operator
- [[q-retry-operators-flow--kotlin--medium]] - retry & retryWhen

### Advanced Flow (Medium)
- [[q-retry-exponential-backoff-flow--kotlin--medium]] - Retry with backoff
- [[q-channelflow-callbackflow-flow--kotlin--medium]] - channelFlow vs callbackFlow
- [[q-flow-exception-handling--kotlin--medium]] - Exception handling in Flow
- [[q-instant-search-flow-operators--kotlin--medium]] - Instant search with Flow
- [[q-room-coroutines-flow--kotlin--medium]] - Room with Flow
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Testing hot Flows

### Advanced (Harder)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
- [[q-flow-operators-deep-dive--kotlin--hard]] - Deep dive into operators
- [[q-flow-performance--kotlin--hard]] - Performance optimization
- [[q-flow-testing-advanced--kotlin--hard]] - Advanced Flow testing
- [[q-testing-flow-operators--kotlin--hard]] - Testing Flow operators
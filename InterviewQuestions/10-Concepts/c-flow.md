---
id: concept-004
title: Kotlin Flow / Kotlin Flow
aliases: [Flow, Kotlin Flow, Cold Flow, Reactive Streams]
kind: concept
summary: Kotlin Flow is a cold asynchronous data stream that sequentially emits values and completes normally or with an exception. It's part of Kotlin Coroutines and provides a declarative way to work with asynchronous data sequences.
links: []
created: 2025-11-05
updated: 2025-11-05
tags: [concept, kotlin, coroutines, flow, reactive-programming]
---

# Summary (EN)

**Kotlin Flow** is a cold asynchronous stream that sequentially emits values over time. It's built on top of Kotlin Coroutines and provides a declarative, composable API for handling asynchronous data sequences.

**Key Characteristics**:

**1. Cold Stream**:
- Doesn't start producing values until collected
- Each collector gets its own independent stream
- Builder code runs separately for each collector

**2. Sequential Emission**:
- Values are emitted one at a time
- Next value is emitted only after previous one is processed
- Naturally handles backpressure (consumer-driven)

**3. Coroutine-based**:
- Uses `suspend` functions for emission and collection
- Automatically respects coroutine cancellation
- Integrates with structured concurrency

**4. Operators**:
- **Transformation**: `map`, `filter`, `transform`, `flatMapConcat`, `flatMapMerge`
- **Combination**: `zip`, `combine`, `merge`
- **Terminal**: `collect`, `toList`, `first`, `reduce`, `fold`
- **Context**: `flowOn` (switch dispatcher), `buffer` (control buffering)

**Basic Usage**:
```kotlin
// Create a flow
val numbersFlow = flow {
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

// Collect the flow
numbersFlow.collect { value ->
    println(value)
}
```

**Flow vs Other Abstractions**:
- **Flow vs Sequence**: Flow is async (suspend), Sequence is synchronous
- **Flow vs Channel**: Flow is cold, Channel is hot (always active)
- **Flow vs LiveData**: Flow is lifecycle-agnostic, LiveData is Android-specific
- **Flow vs RxJava**: Flow is simpler, coroutine-native, less ceremony

# Сводка (RU)

**Kotlin Flow** — это холодный асинхронный поток, последовательно испускающий значения со временем. Он построен на основе Kotlin Coroutines и предоставляет декларативный, композируемый API для работы с асинхронными последовательностями данных.

**Ключевые характеристики**:

**1. Холодный поток (Cold Stream)**:
- Не начинает производить значения до момента сбора (collect)
- Каждый подписчик получает собственный независимый поток
- Код билдера выполняется отдельно для каждого подписчика

**2. Последовательная эмиссия**:
- Значения испускаются по одному за раз
- Следующее значение испускается только после обработки предыдущего
- Естественная обработка backpressure (управляется потребителем)

**3. Основан на корутинах**:
- Использует `suspend`-функции для эмиссии и сбора
- Автоматически учитывает отмену корутин
- Интегрируется со структурированной конкурентностью

**4. Операторы**:
- **Трансформация**: `map`, `filter`, `transform`, `flatMapConcat`, `flatMapMerge`
- **Комбинирование**: `zip`, `combine`, `merge`
- **Терминальные**: `collect`, `toList`, `first`, `reduce`, `fold`
- **Контекст**: `flowOn` (переключить диспетчер), `buffer` (управлять буферизацией)

**Базовое использование**:
```kotlin
// Создать flow
val numbersFlow = flow {
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

// Собрать flow
numbersFlow.collect { value ->
    println(value)
}
```

**Flow в сравнении с другими абстракциями**:
- **Flow vs Sequence**: Flow асинхронный (suspend), Sequence синхронный
- **Flow vs Channel**: Flow холодный, Channel горячий (всегда активен)
- **Flow vs LiveData**: Flow не зависит от жизненного цикла, LiveData специфичен для Android
- **Flow vs RxJava**: Flow проще, встроен в корутины, меньше церемоний

## Use Cases / Trade-offs

**When to use Flow**:
- **Repository layer**: Emit database/network data updates reactively
- **UI state streams**: ViewModel exposes UI state as StateFlow
- **Real-time data**: Server-sent events, WebSocket messages, sensor data
- **Asynchronous pipelines**: Multi-stage data processing (fetch → transform → emit)

**Common patterns**:
- **StateFlow**: Hot flow that always has a value, replaces LiveData
- **SharedFlow**: Hot flow for events/broadcasts
- **channelFlow**: Bridge between callback-based APIs and Flow
- **callbackFlow**: Similar to channelFlow, better for Android lifecycle

**Advantages**:
- **Cold by default**: No resource consumption until collection
- **Backpressure**: Collector controls emission pace
- **Composability**: Chainable operators for declarative pipelines
- **Cancellation**: Automatic cleanup via structured concurrency

**Trade-offs**:
- **Cold flows restart**: Each collector triggers re-execution (use `shareIn`/`stateIn` if shared state needed)
- **Learning curve**: Operators, hot vs cold, buffering strategies
- **Debugging**: Asynchronous nature makes debugging harder (use `.onEach { println(it) }`)

**Performance considerations**:
- Use `buffer()` to decouple producer/consumer speeds
- Use `flowOn(Dispatchers.IO)` to offload work from main thread
- Use `conflate()` to skip intermediate values when consumer is slow

## References

- [Kotlin Flow Official Guide](https://kotlinlang.org/docs/flow.html)
- [Kotlin Coroutines Guide: Asynchronous Flow](https://kotlinlang.org/docs/coroutines-guide.html#asynchronous-flow)
- [Flow API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)
- [Android Developers: Flow in Android](https://developer.android.com/kotlin/flow)
- [Roman Elizarov on Flow Design](https://medium.com/@elizarov/cold-flows-hot-channels-d74769805f9)

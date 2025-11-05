---
id: lang-076
title: "What Is Flow / Что такое Flow"
aliases: [What Is Flow, Что такое Flow]
topic: programming-languages
subtopics: [coroutines, flow, reactive-programming]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-flow-flatmap-operator--programming-languages--easy, q-priorityqueue-vs-deque--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [coroutines, difficulty/medium, flow, kotlin, programming-languages]
date created: Saturday, October 4th 2025, 10:49:37 am
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# What is Flow in Kotlin?

# Question (EN)
> What is Flow in Kotlin?

# Вопрос (RU)
> Что такое Flow в Kotlin?

---

## Answer (EN)

**Flow** is an async data stream that works like List but lazily.

**Features:**
- Emits values sequentially - one by one
- Doesn't block thread - works with suspend functions
- Supports cancel() - can be stopped at any moment
- Allows working with infinite streams - useful for network requests, database, UI events

Flow is a cold asynchronous stream that emits values on demand and can be transformed using operators.

### Basic Concept

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Simple Flow
fun simpleFlow(): Flow<Int> = flow {
    println("Flow started")
    for (i in 1..3) {
        delay(100)
        emit(i)  // Emit value
    }
}

fun main() = runBlocking {
    println("Calling flow...")
    val myFlow = simpleFlow()  // Flow not started yet (cold)

    println("Collecting...")
    myFlow.collect { value ->  // Flow starts when collected
        println("Received: $value")
    }
}

// Output:
// Calling flow...
// Collecting...
// Flow started  <- Only starts when collected
// Received: 1
// Received: 2
// Received: 3
```

### Flow Vs List

```kotlin
// List: Eager evaluation (all values computed immediately)
fun getListOfNumbers(): List<Int> {
    println("Computing list...")
    return listOf(1, 2, 3, 4, 5)  // All computed at once
}

// Flow: Lazy evaluation (values computed on demand)
fun getFlowOfNumbers(): Flow<Int> = flow {
    println("Computing flow...")
    for (i in 1..5) {
        delay(100)  // Can use suspend functions
        emit(i)  // One at a time
    }
}

fun main() = runBlocking {
    // List example
    println("Getting list...")
    val list = getListOfNumbers()  // Computes all values immediately
    println("Processing list...")
    list.forEach { println(it) }

    println("\n---\n")

    // Flow example
    println("Getting flow...")
    val flow = getFlowOfNumbers()  // Nothing computed yet
    println("Processing flow...")
    flow.collect { println(it) }  // Values computed on demand
}
```

### Flow Characteristics

```kotlin
// 1. Cold stream - doesn't emit until collected
fun coldFlow(): Flow<Int> = flow {
    println("Started")  // Only printed when collected
    emit(1)
    emit(2)
}

fun demonstrateCold() = runBlocking {
    val flow = coldFlow()  // Created but not started
    println("Flow created")
    delay(1000)
    println("Now collecting")
    flow.collect { println(it) }  // Now it starts
}

// 2. Sequential emission
fun sequentialFlow() = flow {
    emit(1)
    println("First emitted")
    emit(2)
    println("Second emitted")
    emit(3)
    println("Third emitted")
}

// 3. Supports cancellation
fun cancellableFlow() = runBlocking {
    withTimeoutOrNull(500) {
        flow {
            repeat(10) { i ->
                delay(200)
                emit(i)
            }
        }.collect { println(it) }
    }
    println("Cancelled")
}
```

### Creating Flows

```kotlin
// 1. flow { } builder
fun flowBuilder(): Flow<Int> = flow {
    for (i in 1..3) {
        emit(i)
    }
}

// 2. flowOf() for fixed values
fun fixedFlow(): Flow<String> = flowOf("A", "B", "C")

// 3. asFlow() extension
fun fromCollection(): Flow<Int> = listOf(1, 2, 3).asFlow()

fun fromSequence(): Flow<Int> = (1..10).asSequence().asFlow()

// 4. channelFlow for concurrent emissions
fun concurrentFlow(): Flow<Int> = channelFlow {
    launch {
        delay(100)
        send(1)
    }
    launch {
        delay(50)
        send(2)
    }
}

// 5. Custom flow from callback
fun callbackToFlow(api: ApiService): Flow<Data> = flow {
    val data = suspendCancellableCoroutine<Data> { cont ->
        api.fetchData(object : Callback {
            override fun onSuccess(data: Data) {
                cont.resume(data)
            }
            override fun onError(error: Exception) {
                cont.resumeWithException(error)
            }
        })
    }
    emit(data)
}
```

### Flow Operators

```kotlin
// Transform operators
fun transformationExample() = runBlocking {
    flowOf(1, 2, 3, 4, 5)
        .map { it * 2 }           // Transform each value
        .filter { it > 5 }         // Filter values
        .take(2)                   // Take first 2
        .collect { println(it) }   // Output: 6, 8
}

// Intermediate operators (don't trigger collection)
fun intermediateOperators(): Flow<String> =
    flowOf(1, 2, 3, 4, 5)
        .map { it * 2 }            // Intermediate
        .filter { it % 4 == 0 }    // Intermediate
        .map { "Value: $it" }      // Intermediate

// Terminal operators (trigger collection)
suspend fun terminalOperators() {
    val flow = flowOf(1, 2, 3, 4, 5)

    // collect - collects all
    flow.collect { println(it) }

    // toList - collect to list
    val list = flow.toList()

    // first - get first value
    val first = flow.first()

    // reduce - accumulate values
    val sum = flow.reduce { acc, value -> acc + value }

    // fold - accumulate with initial value
    val total = flow.fold(0) { acc, value -> acc + value }
}
```

### Infinite Streams

```kotlin
// Infinite flow of numbers
fun infiniteNumbers(): Flow<Int> = flow {
    var i = 0
    while (true) {
        emit(i++)
        delay(100)
    }
}

// Infinite flow of events
fun eventStream(): Flow<Event> = flow {
    while (true) {
        val event = waitForEvent()  // Some suspend function
        emit(event)
    }
}

// Use with take() to limit
fun useInfiniteFlow() = runBlocking {
    infiniteNumbers()
        .take(5)  // Only take 5 values
        .collect { println(it) }
}
```

### Real-World Examples

```kotlin
// 1. Database queries
class UserRepository(private val dao: UserDao) {
    fun observeUsers(): Flow<List<User>> = dao.getAllUsers()
    // Room/SQLDelight automatically creates Flow
}

// 2. Network requests
class ApiService {
    fun getUpdates(): Flow<Update> = flow {
        while (true) {
            val update = fetchLatestUpdate()
            emit(update)
            delay(5000)  // Poll every 5 seconds
        }
    }
}

// 3. UI events
class SearchViewModel {
    private val _searchQuery = MutableStateFlow("")
    val searchResults: Flow<List<Result>> = _searchQuery
        .debounce(300)                    // Wait for user to stop typing
        .filter { it.length >= 3 }         // Min 3 characters
        .distinctUntilChanged()            // Ignore duplicates
        .flatMapLatest { query ->          // Cancel previous search
            searchRepository.search(query)
        }

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }
}

// 4. Location updates
class LocationService {
    fun observeLocation(): Flow<Location> = callbackFlow {
        val callback = object : LocationCallback() {
            override fun onLocationChanged(location: Location) {
                trySend(location)
            }
        }

        locationProvider.requestUpdates(callback)

        awaitClose {
            locationProvider.removeUpdates(callback)
        }
    }
}

// 5. File reading
fun readFileAsFlow(file: File): Flow<String> = flow {
    file.useLines { lines ->
        lines.forEach { line ->
            emit(line)
        }
    }
}
```

### Flow Cancellation

```kotlin
// Flow is cancellable
fun cancellationExample() = runBlocking {
    val job = launch {
        flow {
            repeat(10) { i ->
                println("Emitting $i")
                emit(i)
                delay(200)
            }
        }.collect { value ->
            println("Collected $value")
        }
    }

    delay(500)
    println("Cancelling...")
    job.cancel()  // Stops the flow
    println("Done")
}

// Output:
// Emitting 0
// Collected 0
// Emitting 1
// Collected 1
// Emitting 2
// Collected 2
// Cancelling...
// Done
```

### Exception Handling

```kotlin
// Handle exceptions in flow
fun flowWithErrors() = flow {
    emit(1)
    emit(2)
    throw RuntimeException("Error!")
    emit(3)  // Never reached
}

fun handleFlowErrors() = runBlocking {
    flowWithErrors()
        .catch { e ->
            println("Caught: ${e.message}")
            emit(-1)  // Emit fallback value
        }
        .collect { println("Value: $it") }
}

// Output:
// Value: 1
// Value: 2
// Caught: Error!
// Value: -1
```

### Context Preservation

```kotlin
// Flow preserves context
fun contextExample() = runBlocking {
    flow {
        println("Flow in: ${Thread.currentThread().name}")
        emit(1)
    }
    .map {
        println("Map in: ${Thread.currentThread().name}")
        it * 2
    }
    .collect {
        println("Collect in: ${Thread.currentThread().name}")
    }
}

// Switch context with flowOn
fun flowOnExample() = runBlocking {
    flow {
        println("Flow in: ${Thread.currentThread().name}")
        emit(1)
    }
    .flowOn(Dispatchers.IO)  // Upstream runs on IO
    .map {
        println("Map in: ${Thread.currentThread().name}")
        it * 2
    }
    .collect {
        println("Collect in: ${Thread.currentThread().name}")
    }
}
```

### Flow Vs Other Reactive Streams

```kotlin
// Flow vs RxJava Observable
// Flow: Cold, suspending, cancellable
// Observable: Hot/Cold, callback-based, disposable

// Flow vs LiveData
// Flow: General purpose, many operators, cold
// LiveData: Android-specific, lifecycle-aware, hot

// Flow vs Channel
// Flow: Cold, pull-based, single consumer
// Channel: Hot, push-based, multiple consumers

// Flow vs Sequence
// Flow: Async (suspend), for coroutines
// Sequence: Sync (blocking), for regular code
```

### Best Practices

```kotlin
class FlowBestPractices {
    // - DO: Use Flow for data streams
    fun getUserUpdates(): Flow<User> = flow {
        while (true) {
            emit(fetchUser())
            delay(1000)
        }
    }

    // - DO: Use operators for transformation
    fun processedData(): Flow<Result> =
        rawData()
            .map { transform(it) }
            .filter { it.isValid }

    // - DO: Handle errors with catch
    fun safeFlow(): Flow<Data> =
        dataSource()
            .catch { e ->
                emit(Data.Error(e))
            }

    // - DON'T: Block in flow builder
    fun badFlow(): Flow<Int> = flow {
        Thread.sleep(1000)  // BAD: Use delay
        emit(1)
    }

    // - DON'T: Create mutable shared state
    var counter = 0
    fun problematicFlow(): Flow<Int> = flow {
        emit(counter++)  // BAD: Not thread-safe
    }

    // - DO: Use StateFlow/SharedFlow for hot streams
    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state.asStateFlow()
}
```

### Summary

**Flow is ideal for:**
- Async data streams
- Reactive programming
- Database observables
- Network polling
- UI state management
- Event streams
- Sequential processing
- Cancellable operations

**Key advantages:**
- Cold (lazy) by default
- Built on coroutines
- Suspending operations
- Context preservation
- Structured concurrency
- Rich operator library

---


## Ответ (RU)

Это асинхронный поток данных, который работает как List, но лениво. Особенности: выдает значения последовательно – одно за другим не блокирует поток – работает с suspend-функциями поддерживает cancel() – может быть остановлен в любой момент позволяет работать с бесконечными потоками – полезно для сетевых запросов БД UI-событий

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-priorityqueue-vs-deque--programming-languages--easy]]
- [[q-flow-flatmap-operator--programming-languages--easy]]

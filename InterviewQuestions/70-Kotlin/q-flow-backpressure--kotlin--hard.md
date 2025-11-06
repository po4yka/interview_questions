---
id: kotlin-123
title: "Flow Backpressure / Противодавление в Flow"
aliases: ["Flow Backpressure, Противодавление в Flow"]

# Classification
topic: kotlin
subtopics:
  - backpressure
  - buffer
  - collectlatest
  - conflate
  - flow
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Flow backpressure handling

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-advanced-coroutine-patterns--kotlin--hard, q-channel-buffering-strategies--kotlin--hard, q-flow-basics--kotlin--easy]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [backpressure, buffer, collectlatest, conflate, difficulty/hard, flow, kotlin, performance]
---
# Вопрос (RU)
> Что такое противодавление в Kotlin Flow? Объясните операторы buffer(), conflate() и collectLatest() и когда использовать каждую стратегию.

---

# Question (EN)
> What is backpressure in Kotlin Flow? Explain buffer(), conflate(), and collectLatest() operators and when to use each strategy.

## Ответ (RU)

**Противодавление** (backpressure) возникает когда производитель создаёт значения быстрее, чем потребитель может их обработать. Kotlin Flow предоставляет несколько операторов для работы с противодавлением.

### buffer() - Параллельная Обработка

```kotlin
flow {
    repeat(3) {
        delay(100) // Производитель: 100мс
        emit(it)
    }
}
.buffer() // Производитель и потребитель работают параллельно
.collect {
    delay(300) // Потребитель: 300мс
}
// Время: ~1000мс вместо 1200мс
```

### conflate() - Только Последнее Значение

```kotlin
flow {
    repeat(10) {
        emit(it)
        delay(100)
    }
}
.conflate() // Пропускает промежуточные значения
.collect {
    delay(300) // Медленный потребитель
}
// Собирает только: 0, 3, 6, 9
```

### collectLatest() - Отмена И Перезапуск

```kotlin
searchQuery.collectLatest { query ->
    searchApi(query) // Отменяется если приходит новый query
}
```

### Выбор Стратегии

| Случай | Стратегия | Причина |
|--------|-----------|---------|
| Все значения важны | `buffer()` | Обработать каждое значение |
| Важно только последнее | `conflate()` | Обновления UI, сенсоры |
| Отменить предыдущую работу | `collectLatest()` | Поиск, автодополнение |

---

## Answer (EN)

**Backpressure** occurs when a producer emits values faster than a consumer can process them. Kotlin Flow provides several operators to handle backpressure: `buffer()`, `conflate()`, and `collectLatest()`.

### Understanding Backpressure

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

// Without buffer - producer waits for consumer
suspend fun withoutBuffer() {
    val time = measureTimeMillis {
        flow {
            repeat(3) {
                delay(100) // Producer takes 100ms
                emit(it)
                println("Emitted $it")
            }
        }.collect {
            delay(300) // Consumer takes 300ms
            println("Collected $it")
        }
    }
    println("Time: $time ms") // ~1200ms (100+300) * 3
}

// Output:
// Emitted 0
// Collected 0 (after 400ms total)
// Emitted 1
// Collected 1 (after 800ms total)
// Emitted 2
// Collected 2 (after 1200ms total)
```

### buffer() - Concurrent Processing

`buffer()` allows producer and consumer to run concurrently:

```kotlin
suspend fun withBuffer() {
    val time = measureTimeMillis {
        flow {
            repeat(3) {
                delay(100)
                emit(it)
                println("Emitted $it at ${System.currentTimeMillis()}")
            }
        }
        .buffer() // Producer and consumer run concurrently
        .collect {
            delay(300)
            println("Collected $it at ${System.currentTimeMillis()}")
        }
    }
    println("Time: $time ms") // ~1000ms (100*3 + 300*3 - overlapping)
}

// Output:
// Emitted 0 at 100ms
// Emitted 1 at 200ms
// Emitted 2 at 300ms
// Collected 0 at 400ms
// Collected 1 at 700ms
// Collected 2 at 1000ms
```

**Buffer with capacity:**

```kotlin
flow {
    repeat(10) {
        emit(it)
        println("Emitted $it")
    }
}
.buffer(capacity = 5) // Buffer up to 5 items
.collect {
    delay(100)
    println("Collected $it")
}

// If buffer is full, producer suspends until space is available
```

**Buffer strategies:**

```kotlin
// Default buffer
.buffer()

// Specific capacity
.buffer(capacity = 10)

// Unlimited buffer (use with caution!)
.buffer(capacity = Channel.UNLIMITED)

// Conflated buffer (keep only latest)
.buffer(capacity = Channel.CONFLATED)
```

### conflate() - Keep Latest Value

`conflate()` keeps only the most recent value when consumer is slow:

```kotlin
suspend fun withConflate() {
    flow {
        repeat(10) {
            emit(it)
            println("Emitted $it")
            delay(100)
        }
    }
    .conflate() // Drop intermediate values
    .collect {
        println("Collected $it")
        delay(300) // Slow consumer
    }
}

// Output:
// Emitted 0
// Collected 0
// Emitted 1
// Emitted 2
// Emitted 3
// Collected 3 (skipped 1 and 2)
// Emitted 4
// Emitted 5
// Emitted 6
// Collected 6 (skipped 4 and 5)
```

**Real-world example: Location updates**

```kotlin
data class Location(val lat: Double, val lng: Double, val timestamp: Long)

class LocationTracker {
    fun locationUpdates(): Flow<Location> = flow {
        while (true) {
            val location = getCurrentLocation()
            emit(location)
            delay(1000) // Update every second
        }
    }

    private fun getCurrentLocation() = Location(
        lat = Random.nextDouble(),
        lng = Random.nextDouble(),
        timestamp = System.currentTimeMillis()
    )
}

// UI consuming location updates
suspend fun trackLocation() {
    LocationTracker()
        .locationUpdates()
        .conflate() // Keep only latest location
        .collect { location ->
            // Update UI (might be slow)
            updateMapUI(location)
            delay(2000) // UI update takes 2 seconds
        }
}

// With conflate(), UI always shows the latest location
// without processing every intermediate update
```

### collectLatest() - Cancel and Restart

`collectLatest()` cancels previous collection when new value arrives:

```kotlin
suspend fun withCollectLatest() {
    flow {
        repeat(5) {
            emit(it)
            println("Emitted $it")
            delay(100)
        }
    }
    .collectLatest {
        println("Collecting $it")
        delay(300) // Long processing
        println("Collected $it") // May not print if cancelled
    }
}

// Output:
// Emitted 0
// Collecting 0
// Emitted 1
// Collecting 1 (cancels collection of 0)
// Emitted 2
// Collecting 2 (cancels collection of 1)
// Emitted 3
// Collecting 3 (cancels collection of 2)
// Emitted 4
// Collecting 4 (cancels collection of 3)
// Collected 4 (finally completes)
```

**Real-world example: Search**

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300) // Wait for user to stop typing
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .mapLatest { query -> // Similar to collectLatest
            searchApi(query) // Cancels previous search if new query arrives
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    private suspend fun searchApi(query: String): List<Result> {
        delay(500) // Simulate API call
        return listOf(Result(query))
    }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

// User types: "k" -> "ko" -> "kot" -> "kotl" -> "kotli" -> "kotlin"
// Only the last search ("kotlin") actually completes
// Previous searches are cancelled automatically
```

### Comparison of Strategies

```kotlin
// Test all three strategies
suspend fun compareStrategies() {
    println("=== Without backpressure handling ===")
    testStrategy(null)

    println("\n=== With buffer() ===")
    testStrategy("buffer")

    println("\n=== With conflate() ===")
    testStrategy("conflate")

    println("\n=== With collectLatest() ===")
    testStrategy("collectLatest")
}

suspend fun testStrategy(strategy: String?) {
    val flow = flow {
        repeat(5) {
            emit(it)
            println("Emitted $it")
            delay(100)
        }
    }

    val time = measureTimeMillis {
        when (strategy) {
            "buffer" -> flow.buffer().collect { processItem(it) }
            "conflate" -> flow.conflate().collect { processItem(it) }
            "collectLatest" -> flow.collectLatest { processItem(it) }
            else -> flow.collect { processItem(it) }
        }
    }

    println("Total time: $time ms\n")
}

suspend fun processItem(item: Int) {
    delay(300)
    println("Processed $item")
}
```

### Advanced Buffer Configuration

```kotlin
// Custom buffer with overflow strategy
flow<Int> {
    repeat(100) { emit(it) }
}
.buffer(
    capacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
.collect { /* process */ }

// Available strategies:
// - BufferOverflow.SUSPEND (default): suspend producer
// - BufferOverflow.DROP_OLDEST: drop oldest item
// - BufferOverflow.DROP_LATEST: drop newest item
```

**Custom buffering with Channel:**

```kotlin
fun <T> Flow<T>.customBuffer(size: Int): Flow<T> = channelFlow {
    val channel = Channel<T>(capacity = size)

    launch {
        collect { value ->
            channel.send(value)
        }
        channel.close()
    }

    for (value in channel) {
        send(value)
    }
}
```

### Real-World Examples

**Example 1: Network Request Batching**

```kotlin
data class AnalyticsEvent(val name: String, val timestamp: Long)

class AnalyticsManager {
    private val events = MutableSharedFlow<AnalyticsEvent>(
        extraBufferCapacity = 100,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    init {
        CoroutineScope(Dispatchers.IO).launch {
            events
                .buffer(capacity = 50)
                .chunked(10, timeout = 5000) // Batch 10 events or 5 seconds
                .collect { batch ->
                    sendToServer(batch)
                }
        }
    }

    fun logEvent(event: AnalyticsEvent) {
        events.tryEmit(event)
    }

    private suspend fun sendToServer(batch: List<AnalyticsEvent>) {
        println("Sending batch of ${batch.size} events")
        delay(200) // Simulate network call
    }
}

// Extension function for batching
fun <T> Flow<T>.chunked(size: Int, timeout: Long): Flow<List<T>> = flow {
    val batch = mutableListOf<T>()
    var lastEmitTime = System.currentTimeMillis()

    collect { value ->
        batch.add(value)
        val now = System.currentTimeMillis()

        if (batch.size >= size || (now - lastEmitTime) >= timeout) {
            emit(batch.toList())
            batch.clear()
            lastEmitTime = now
        }
    }

    if (batch.isNotEmpty()) {
        emit(batch)
    }
}
```

**Example 2: Real-time Data Processing**

```kotlin
data class SensorData(val value: Double, val timestamp: Long)

class SensorDataProcessor {
    fun processSensorData(sensorFlow: Flow<SensorData>): Flow<Double> {
        return sensorFlow
            .buffer(capacity = 20) // Buffer fast sensor readings
            .map { data ->
                // Heavy processing
                delay(50)
                data.value * 2
            }
            .scan(0.0) { accumulator, value ->
                // Running average
                (accumulator + value) / 2
            }
    }

    fun processLatestOnly(sensorFlow: Flow<SensorData>): Flow<Double> {
        return sensorFlow
            .conflate() // Only process latest reading
            .map { data ->
                delay(50) // Heavy processing
                data.value * 2
            }
    }
}
```

**Example 3: UI Updates**

```kotlin
class DataViewModel : ViewModel() {
    private val dataSource = DataSource()

    // Buffer: Process all updates
    val allUpdates: StateFlow<List<Item>> = dataSource.updates()
        .buffer(capacity = 50)
        .map { processUpdate(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    // Conflate: Show only latest
    val latestUpdate: StateFlow<Item?> = dataSource.updates()
        .conflate()
        .map { processUpdate(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = null
        )

    // CollectLatest: Cancel previous processing
    val searchResults: StateFlow<List<Result>> = searchQuery
        .debounce(300)
        .mapLatest { query ->
            if (query.isBlank()) emptyList()
            else searchApi(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )
}
```

### Performance Considerations

```kotlin
// Memory usage comparison
suspend fun memoryTest() {
    val largeFlow = flow {
        repeat(1_000_000) {
            emit(ByteArray(1024)) // 1KB per item
        }
    }

    // DANGEROUS: Unlimited buffer can cause OOM
    largeFlow
        .buffer(capacity = Channel.UNLIMITED) // Can use 1GB+ memory!
        .collect { delay(1) }

    // SAFE: Conflate keeps only 1 item
    largeFlow
        .conflate() // Uses ~1KB memory
        .collect { delay(1) }

    // SAFE: Limited buffer
    largeFlow
        .buffer(capacity = 100) // Uses ~100KB memory
        .collect { delay(1) }
}
```

### Choosing the Right Strategy

| Use Case | Strategy | Reason |
|----------|----------|---------|
| All values important | `buffer()` | Process every value, just concurrently |
| Only latest matters | `conflate()` | UI updates, sensor readings |
| Cancel previous work | `collectLatest()` | Search, auto-complete |
| Fast producer, slow consumer | `buffer()` | Decouple speeds |
| Show progress | `buffer()` | See all intermediate states |
| Show final state | `conflate()` | Skip intermediate states |

### Best Practices

#### DO:

```kotlin
// Use buffer for concurrent processing
flow { /* fast producer */ }
    .buffer()
    .collect { /* slow consumer */ }

// Use conflate for UI updates
locationFlow
    .conflate()
    .collect { updateUI(it) }

// Use collectLatest for cancellable work
searchQuery
    .collectLatest { query ->
        searchDatabase(query) // Cancelled if new query arrives
    }

// Limit buffer size
.buffer(capacity = 100) // Prevent OOM
```

#### DON'T:

```kotlin
// Don't use unlimited buffer without reason
.buffer(capacity = Channel.UNLIMITED) // Can cause OOM!

// Don't use conflate if all values are important
dataToSave.conflate() // Might lose data!

// Don't use buffer for simple cases
flow { emit(1) }.buffer().collect { /* process */ } // Overkill

// Don't forget backpressure handling for fast producers
fastSensor
    // .buffer() or .conflate() needed!
    .collect { slowProcessing(it) }
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Flow Backpressure](https://kotlinlang.org/docs/flow.html#buffering)
- [Flow Buffer](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/buffer.html)
- [Flow Conflate](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/conflate.html)

## Related Questions

### Related (Hard)
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-testing-advanced--kotlin--hard]] - Flow

### Prerequisites (Easier)
-  - Flow
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## MOC Links

- [[moc-kotlin]]

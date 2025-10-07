---
tags:
  - programming-languages
difficulty: medium
status: draft
---

# Back Pressure in Kotlin Flow

## Answer

**Back Pressure** is a data flow control mechanism that prevents consumer overload when the producer sends data too quickly.

Kotlin Flow and Reactive Streams have strategies for managing Back Pressure:

- **Buffer**: Accumulates data in memory
- **Drop**: Ignores excess elements
- **Latest**: Stores only the last element
- **Conflate**: Combines values to reduce load

Back Pressure is needed for stability and preventing memory leaks in async streams.

### The Problem: Fast Producer, Slow Consumer

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Problem: Producer emits faster than consumer can process
fun problematicFlow() = flow {
    repeat(100) { i ->
        println("Emitting $i")
        emit(i)
        delay(10)  // Producer emits every 10ms
    }
}

fun main() = runBlocking {
    problematicFlow().collect { value ->
        println("Collecting $value")
        delay(100)  // Consumer processes every 100ms
        // Producer is 10x faster than consumer!
    }
}

// Without backpressure handling:
// - Memory buildup
// - Potential OutOfMemoryError
// - Dropped data
// - System instability
```

### Strategy 1: buffer() - Accumulate Data

```kotlin
// Buffer allows producer to run ahead of consumer
fun bufferExample() = runBlocking {
    flow {
        repeat(10) { i ->
            println("Emit $i at ${System.currentTimeMillis()}")
            emit(i)
            delay(100)
        }
    }
    .buffer(capacity = 5)  // Buffer up to 5 elements
    .collect { value ->
        println("Collect $value at ${System.currentTimeMillis()}")
        delay(500)  // Slow consumer
    }
}

// With buffer:
// - Producer doesn't wait for consumer
// - Elements stored in buffer
// - Producer suspends when buffer is full
// - Consumer processes at own pace

// Buffer capacity strategies
val flow1 = flowOf(1, 2, 3)
    .buffer()  // Default buffer (64 elements)

val flow2 = flowOf(1, 2, 3)
    .buffer(10)  // Buffer 10 elements

val flow3 = flowOf(1, 2, 3)
    .buffer(Channel.UNLIMITED)  // Unlimited buffer (dangerous!)

val flow4 = flowOf(1, 2, 3)
    .buffer(Channel.RENDEZVOUS)  // No buffer, wait for consumer
```

### Strategy 2: conflate() - Keep Latest Only

```kotlin
// Conflate skips intermediate values, keeps only latest
fun conflateExample() = runBlocking {
    flow {
        repeat(10) { i ->
            println("Emit $i")
            emit(i)
            delay(100)
        }
    }
    .conflate()  // Drop intermediate values
    .collect { value ->
        println("Collect $value")
        delay(500)  // Slow consumer
    }
}

// Output example:
// Emit 0
// Collect 0
// Emit 1
// Emit 2
// Emit 3
// Emit 4
// Collect 4  <- Skipped 1, 2, 3
// Emit 5
// ...

// Use case: UI updates
fun locationUpdates(): Flow<Location> = flow {
    while (true) {
        emit(getCurrentLocation())
        delay(100)
    }
}
    .conflate()  // Only show latest location

// Use case: Stock prices
fun stockPrices(symbol: String): Flow<Double> = flow {
    while (true) {
        emit(fetchPrice(symbol))
        delay(50)
    }
}
    .conflate()  // Only latest price matters
```

### Strategy 3: collectLatest() - Cancel Previous Collection

```kotlin
// collectLatest cancels previous collection when new value arrives
fun collectLatestExample() = runBlocking {
    flow {
        repeat(5) { i ->
            println("Emit $i")
            emit(i)
            delay(100)
        }
    }
    .collectLatest { value ->
        println("Start collecting $value")
        delay(500)  // Slow processing
        println("Finish collecting $value")  // May not reach here
    }
}

// Output example:
// Emit 0
// Start collecting 0
// Emit 1
// Start collecting 1  <- Cancelled collection of 0
// Emit 2
// Start collecting 2  <- Cancelled collection of 1
// ...
// Finish collecting 4  <- Only last one completes

// Use case: Search queries
fun searchFlow(queries: Flow<String>): Flow<List<Result>> =
    queries.collectLatest { query ->
        // Cancel previous search when new query arrives
        performSearch(query)
    }

// Use case: Live data updates
fun dataUpdates(): Flow<Data> = dataSource
    .collectLatest { rawData ->
        // Cancel previous processing
        processData(rawData)
    }
```

### Strategy 4: Custom Buffer with Overflow

```kotlin
// Buffer with overflow handling
suspend fun bufferOverflowStrategies() {
    val source = flow {
        repeat(100) { emit(it) }
    }

    // SUSPEND (default): Suspend producer when buffer full
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.SUSPEND
    ).collect { /* slow consumer */ }

    // DROP_OLDEST: Drop oldest values when buffer full
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    ).collect { /* slow consumer */ }

    // DROP_LATEST: Drop newest values when buffer full
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.DROP_LATEST
    ).collect { /* slow consumer */ }
}

// Real example: Event logging
class EventLogger {
    private val events = MutableSharedFlow<Event>(
        replay = 0,
        extraBufferCapacity = 1000,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    fun logEvent(event: Event) {
        events.tryEmit(event)  // Won't suspend, drops oldest if full
    }

    fun observeEvents(): Flow<Event> = events
}
```

### Strategy 5: Sample / Throttle

```kotlin
// sample: Emit latest value at fixed intervals
fun sampleExample() = runBlocking {
    flow {
        repeat(100) { i ->
            emit(i)
            delay(10)  // Fast emission
        }
    }
    .sample(100)  // Sample every 100ms
    .collect { value ->
        println("Sampled: $value")
    }
}

// Output: Only values sampled at 100ms intervals
// Sampled: 9
// Sampled: 19
// Sampled: 29
// ...

// Custom sample implementation
fun <T> Flow<T>.sampleTime(periodMillis: Long): Flow<T> = flow {
    var lastEmission = 0L
    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmission >= periodMillis) {
            emit(value)
            lastEmission = currentTime
        }
    }
}

// Use case: Sensor data
fun sensorReadings(): Flow<SensorData> = flow {
    while (true) {
        emit(readSensor())
        delay(10)  // Read every 10ms
    }
}
    .sample(1000)  // Report every 1 second
```

### Strategy 6: Debounce

```kotlin
// debounce: Emit value only after quiet period
fun debounceExample() = runBlocking {
    flow {
        emit(1)
        delay(50)
        emit(2)
        delay(50)
        emit(3)
        delay(500)  // Quiet period
        emit(4)
    }
    .debounce(200)  // Wait 200ms of quiet
    .collect { value ->
        println("Debounced: $value")
    }
}

// Output:
// Debounced: 3  <- After quiet period
// Debounced: 4  <- Last value

// Use case: Search input
fun searchInput(textChanges: Flow<String>): Flow<List<Result>> =
    textChanges
        .debounce(300)  // Wait for user to stop typing
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            performSearch(query)
        }

// Use case: Auto-save
fun autoSave(contentChanges: Flow<String>): Flow<Unit> =
    contentChanges
        .debounce(2000)  // Save 2 seconds after last change
        .map { content -> saveToServer(content) }
```

### Comparing Strategies

```kotlin
suspend fun compareStrategies() = coroutineScope {
    val source = flow {
        repeat(10) { i ->
            println("Emit $i")
            emit(i)
            delay(100)
        }
    }

    println("=== No backpressure ===")
    source.collect {
        delay(500)
        println("Collect $it")
    }

    println("\n=== With buffer ===")
    source.buffer(3).collect {
        delay(500)
        println("Collect $it")
    }

    println("\n=== With conflate ===")
    source.conflate().collect {
        delay(500)
        println("Collect $it")
    }

    println("\n=== With collectLatest ===")
    source.collectLatest {
        println("Start $it")
        delay(500)
        println("End $it")
    }
}
```

### Real-World Example: Download Manager

```kotlin
class DownloadManager {
    // Fast download events, slow UI updates
    private val downloadProgress = MutableSharedFlow<DownloadProgress>(
        replay = 0,
        extraBufferCapacity = 100,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    fun observeProgress(): Flow<DownloadProgress> =
        downloadProgress
            .conflate()  // UI only needs latest progress
            .sample(100)  // Update UI max 10 times/second

    suspend fun download(url: String) {
        var bytesDownloaded = 0L
        val totalBytes = getContentLength(url)

        downloadStream(url).collect { chunk ->
            bytesDownloaded += chunk.size
            // Emit progress (may be faster than UI can handle)
            downloadProgress.emit(
                DownloadProgress(bytesDownloaded, totalBytes)
            )
        }
    }
}
```

### Memory-Safe Pattern

```kotlin
// Prevent OOM with bounded buffer
fun safePipeline(): Flow<ProcessedData> = flow {
    // Fast data source
    repeat(1_000_000) { emit(it) }
}
    .buffer(capacity = 100)  // Bounded buffer
    .map { data ->
        // CPU-intensive processing
        processData(data)
    }
    .buffer(capacity = 50)  // Another bounded buffer
    .map { intermediate ->
        // More processing
        transform(intermediate)
    }

// Without bounded buffers:
// - Unbounded memory growth
// - Potential OOM
// - System crash

// With bounded buffers:
// - Controlled memory usage
// - Producer suspends when buffer full
// - Stable system
```

### Best Practices

```kotlin
class BackPressureBestPractices {
    // ✅ DO: Use conflate for state updates
    fun userState(): Flow<UserState> =
        stateUpdates.conflate()

    // ✅ DO: Use buffer for throughput
    fun dataProcessing(): Flow<Result> =
        dataSource
            .buffer(100)
            .map { process(it) }

    // ✅ DO: Use debounce for user input
    fun searchQuery(input: Flow<String>): Flow<Results> =
        input.debounce(300)
            .flatMapLatest { query -> search(query) }

    // ✅ DO: Use sample for high-frequency events
    fun mousePosition(events: Flow<MouseEvent>): Flow<Position> =
        events.sample(16)  // ~60fps

    // ❌ DON'T: Use unlimited buffer
    fun dangerous(): Flow<Data> =
        source.buffer(Int.MAX_VALUE)  // Will cause OOM!

    // ❌ DON'T: Ignore backpressure entirely
    fun alsoProblematic(): Flow<Data> =
        fastSource  // No backpressure handling
}
```

### Summary Table

| Strategy | Behavior | Use Case | Memory Impact |
|----------|----------|----------|---------------|
| **buffer()** | Queue elements | High throughput | Medium (bounded) |
| **conflate()** | Keep latest | State updates | Low |
| **collectLatest()** | Cancel previous | Cancellable work | Low |
| **sample()** | Periodic emission | High-freq events | Low |
| **debounce()** | After quiet period | User input | Low |
| **DROP_OLDEST** | Drop old values | Event logging | Low (bounded) |
| **DROP_LATEST** | Drop new values | Rarely used | Low (bounded) |

---
## Вопрос (RU)

Что известно про Back Pressure?

## Ответ

Это механизм контроля потока данных, предотвращающий перегрузку потребителя если источник отправляет данные слишком быстро. В Kotlin Flow и Reactive Streams есть стратегии управления Back Pressure: Buffer – накапливает данные в памяти. Drop – игнорирует избыточные элементы. Latest – хранит только последний элемент. Conflate – объединяет значения для уменьшения нагрузки. Back Pressure нужен для стабильности и предотвращения утечек памяти в асинхронных потоках.

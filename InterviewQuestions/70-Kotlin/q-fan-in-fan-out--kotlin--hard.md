---
id: kotlin-092
title: "Fan-in Fan-out Pattern"
aliases: []

# Classification
topic: kotlin
subtopics:
  - channels
  - concurrency
  - coroutines
  - fan-in
  - fan-out
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Fan-in Fan-out patterns

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-actor-pattern--kotlin--hard, q-advanced-coroutine-patterns--kotlin--hard, q-channel-buffering-strategies--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [channels, coroutines, difficulty/hard, fan-in, fan-out, kotlin, load-balancing, parallel-processing]
date created: Sunday, October 12th 2025, 3:13:16 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Вопрос (RU)
> Что такое паттерны Fan-in и Fan-out в корутинах Kotlin? Объясните как распределять работу между несколькими воркерами и агрегировать результаты из множества источников.

---

# Question (EN)
> What are Fan-in and Fan-out patterns in Kotlin coroutines? Explain how to distribute work to multiple workers and aggregate results from multiple sources.

## Ответ (RU)

**Fan-out** распределяет работу от одного источника к нескольким потребителям (воркерам). **Fan-in** агрегирует результаты от множества производителей в одного потребителя.

### Паттерн Fan-out

Распределение работы между несколькими воркерами для параллельной обработки:

```kotlin
fun CoroutineScope.produceNumbers() = produce {
    var x = 1
    while (x <= 100) {
        send(x++)
        delay(10)
    }
}

suspend fun main() = coroutineScope {
    val numbers = produceNumbers()
    
    // Fan-out: 5 воркеров потребляют из одного канала
    repeat(5) { workerId ->
        launch {
            for (number in numbers) {
                println("Воркер $workerId обрабатывает $number")
                delay(100)
            }
        }
    }
}
```

### Паттерн Fan-in

Агрегация результатов от множества производителей:

```kotlin
fun CoroutineScope.fanIn(
    channels: List<ReceiveChannel<Int>>
): ReceiveChannel<Int> = produce {
    channels.forEach { channel ->
        launch {
            for (value in channel) {
                send(value)
            }
        }
    }
}
```

### Комбинированный Fan-out И Fan-in

```kotlin
class ImageProcessingPipeline(
    private val scope: CoroutineScope,
    private val processorCount: Int = 4
) {
    private val taskChannel = Channel<ImageTask>(capacity = 50)
    private val resultChannel = Channel<ProcessedImage>(capacity = 50)
    
    init {
        // Fan-out: Запуск нескольких процессоров
        repeat(processorCount) { processorId ->
            scope.launch {
                imageProcessor(processorId)
            }
        }
    }
}
```

### Лучшие Практики

#### ДЕЛАТЬ:

```kotlin
// Использовать fan-out для параллельной обработки
val workers = List(5) { processChannel(workerId = it, input) }

// Использовать fan-in для агрегации результатов
val merged = merge(channel1, channel2, channel3)

// Правильно закрывать каналы
channel.close()
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не создавать слишком много воркеров
repeat(1000) { /* воркер */ } // Слишком много!

// Не забывать о capacity канала
val channel = Channel<Int>() // Rendezvous может блокировать
```

---

## Answer (EN)

**Fan-out** distributes work from a single source to multiple consumers (workers). **Fan-in** aggregates results from multiple producers into a single consumer.

### Fan-out Pattern

Distributing work to multiple workers for parallel processing:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

fun CoroutineScope.produceNumbers() = produce {
    var x = 1
    while (x <= 100) {
        send(x++)
        delay(10)
    }
}

fun CoroutineScope.processNumbers(
    id: Int,
    channel: ReceiveChannel<Int>
) = launch {
    for (number in channel) {
        println("Worker $id processing $number")
        delay(100) // Simulate processing
    }
}

suspend fun main() = coroutineScope {
    val numbers = produceNumbers()
    
    // Fan-out: 5 workers consuming from single channel
    repeat(5) { workerId ->
        processNumbers(workerId, numbers)
    }
}
```

**Load Balancing Example:**

```kotlin
data class Task(val id: Int, val payload: String)
data class Result(val taskId: Int, val result: String, val workerId: Int)

class WorkerPool(private val scope: CoroutineScope, private val workerCount: Int) {
    private val taskChannel = Channel<Task>(capacity = 100)
    private val resultChannel = Channel<Result>(capacity = 100)
    
    init {
        repeat(workerCount) { workerId ->
            scope.launch {
                worker(workerId)
            }
        }
    }
    
    private suspend fun worker(workerId: Int) {
        for (task in taskChannel) {
            delay(100) // Simulate work
            val result = Result(
                taskId = task.id,
                result = task.payload.uppercase(),
                workerId = workerId
            )
            resultChannel.send(result)
            println("Worker $workerId completed task ${task.id}")
        }
    }
    
    suspend fun submitTask(task: Task) {
        taskChannel.send(task)
    }
    
    suspend fun getResult(): Result {
        return resultChannel.receive()
    }
    
    fun close() {
        taskChannel.close()
        resultChannel.close()
    }
}

suspend fun main() = coroutineScope {
    val pool = WorkerPool(this, workerCount = 3)
    
    // Submit 10 tasks
    launch {
        repeat(10) { i ->
            pool.submitTask(Task(i, "task_$i"))
        }
    }
    
    // Collect results
    repeat(10) {
        val result = pool.getResult()
        println("Got result: ${result.result} from worker ${result.workerId}")
    }
    
    pool.close()
}
```

### Fan-in Pattern

Aggregating results from multiple producers:

```kotlin
fun CoroutineScope.produceNumbersFrom(start: Int) = produce {
    var x = start
    repeat(5) {
        send(x++)
        delay(100)
    }
}

fun CoroutineScope.fanIn(
    channels: List<ReceiveChannel<Int>>
): ReceiveChannel<Int> = produce {
    channels.forEach { channel ->
        launch {
            for (value in channel) {
                send(value)
            }
        }
    }
}

suspend fun main() = coroutineScope {
    val producers = List(3) { produceNumbersFrom(it * 10) }
    val consumer = fanIn(producers)
    
    for (value in consumer) {
        println("Received: $value")
    }
}
```

**Real-World Fan-in: Log Aggregation**

```kotlin
data class LogEntry(val source: String, val message: String, val timestamp: Long)

class LogAggregator(private val scope: CoroutineScope) {
    private val aggregatedChannel = Channel<LogEntry>(capacity = 1000)
    
    fun createLogSource(sourceName: String): SendChannel<String> {
        val channel = Channel<String>(capacity = 100)
        
        scope.launch {
            for (message in channel) {
                val entry = LogEntry(
                    source = sourceName,
                    message = message,
                    timestamp = System.currentTimeMillis()
                )
                aggregatedChannel.send(entry)
            }
        }
        
        return channel
    }
    
    fun subscribe(): ReceiveChannel<LogEntry> = aggregatedChannel
}

suspend fun main() = coroutineScope {
    val aggregator = LogAggregator(this)
    
    // Create multiple log sources
    val apiLogger = aggregator.createLogSource("API")
    val dbLogger = aggregator.createLogSource("Database")
    val cacheLogger = aggregator.createLogSource("Cache")
    
    // Consume aggregated logs
    launch {
        for (log in aggregator.subscribe()) {
            println("[${log.source}] ${log.message} at ${log.timestamp}")
        }
    }
    
    // Send logs from different sources
    launch {
        apiLogger.send("Request received")
        delay(50)
        apiLogger.send("Response sent")
    }
    
    launch {
        dbLogger.send("Query executed")
        delay(30)
        dbLogger.send("Transaction committed")
    }
    
    launch {
        cacheLogger.send("Cache hit")
        delay(20)
        cacheLogger.send("Cache updated")
    }
    
    delay(500)
}
```

### Combined Fan-out and Fan-in

```kotlin
data class ImageTask(val id: Int, val url: String)
data class ProcessedImage(val id: Int, val data: ByteArray, val processorId: Int)

class ImageProcessingPipeline(
    private val scope: CoroutineScope,
    private val processorCount: Int = 4
) {
    private val taskChannel = Channel<ImageTask>(capacity = 50)
    private val resultChannel = Channel<ProcessedImage>(capacity = 50)
    
    init {
        // Fan-out: Launch multiple processors
        repeat(processorCount) { processorId ->
            scope.launch {
                imageProcessor(processorId)
            }
        }
    }
    
    private suspend fun imageProcessor(processorId: Int) {
        for (task in taskChannel) {
            // Simulate image processing
            delay(200)
            val processed = ProcessedImage(
                id = task.id,
                data = ByteArray(1024),
                processorId = processorId
            )
            resultChannel.send(processed)
            println("Processor $processorId completed image ${task.id}")
        }
    }
    
    suspend fun submitTask(task: ImageTask) {
        taskChannel.send(task)
    }
    
    fun results(): ReceiveChannel<ProcessedImage> = resultChannel
    
    fun close() {
        taskChannel.close()
    }
}

suspend fun main() = coroutineScope {
    val pipeline = ImageProcessingPipeline(this, processorCount = 3)
    
    // Submit tasks
    launch {
        repeat(10) { i ->
            pipeline.submitTask(ImageTask(i, "http://example.com/image$i.jpg"))
        }
        pipeline.close()
    }
    
    // Fan-in: Collect all results
    val results = mutableListOf<ProcessedImage>()
    for (result in pipeline.results()) {
        results.add(result)
        println("Collected result ${result.id} from processor ${result.processorId}")
    }
    
    println("Total results: ${results.size}")
}
```

### Advanced Fan-out: Work Stealing

```kotlin
class WorkStealingPool<T, R>(
    private val scope: CoroutineScope,
    private val workerCount: Int,
    private val processor: suspend (T) -> R
) {
    private val taskChannels = List(workerCount) { Channel<T>(capacity = 10) }
    private val resultChannel = Channel<R>(capacity = 100)
    private val taskCounter = AtomicInteger(0)
    
    init {
        repeat(workerCount) { workerId ->
            scope.launch {
                workStealingWorker(workerId)
            }
        }
    }
    
    private suspend fun workStealingWorker(workerId: Int) {
        val myChannel = taskChannels[workerId]
        
        while (!myChannel.isClosedForReceive || taskChannels.any { !it.isEmpty }) {
            // Try own queue first
            val task = myChannel.tryReceive().getOrNull()
            
            if (task != null) {
                val result = processor(task)
                resultChannel.send(result)
            } else {
                // Try stealing from other workers
                val stolenTask = stealTask(workerId)
                if (stolenTask != null) {
                    val result = processor(stolenTask)
                    resultChannel.send(result)
                } else {
                    delay(10) // Wait before retry
                }
            }
        }
    }
    
    private suspend fun stealTask(myId: Int): T? {
        for (i in taskChannels.indices) {
            if (i != myId) {
                val stolen = taskChannels[i].tryReceive().getOrNull()
                if (stolen != null) {
                    println("Worker $myId stole task from worker $i")
                    return stolen
                }
            }
        }
        return null
    }
    
    suspend fun submit(task: T) {
        val index = taskCounter.getAndIncrement() % workerCount
        taskChannels[index].send(task)
    }
    
    fun results(): ReceiveChannel<R> = resultChannel
    
    fun close() {
        taskChannels.forEach { it.close() }
    }
}

// Usage
suspend fun main() = coroutineScope {
    val pool = WorkStealingPool<Int, Int>(
        scope = this,
        workerCount = 3,
        processor = { number ->
            delay(100)
            number * 2
        }
    )
    
    launch {
        repeat(20) { i ->
            pool.submit(i)
        }
        pool.close()
    }
    
    for (result in pool.results()) {
        println("Result: $result")
    }
}
```

### Merge Multiple Channels (Fan-in Helper)

```kotlin
fun <T> CoroutineScope.merge(vararg channels: ReceiveChannel<T>): ReceiveChannel<T> = produce {
    channels.forEach { channel ->
        launch {
            for (item in channel) {
                send(item)
            }
        }
    }
}

// Alternative using select
fun <T> CoroutineScope.mergeWithSelect(vararg channels: ReceiveChannel<T>): ReceiveChannel<T> = produce {
    val channelList = channels.toMutableList()
    
    while (channelList.isNotEmpty()) {
        select<Unit> {
            channelList.forEach { channel ->
                channel.onReceiveCatching { result ->
                    result.getOrNull()?.let { send(it) }
                        ?: channelList.remove(channel)
                }
            }
        }
    }
}

suspend fun main() = coroutineScope {
    val channel1 = produce { repeat(5) { send("A$it"); delay(100) } }
    val channel2 = produce { repeat(5) { send("B$it"); delay(150) } }
    val channel3 = produce { repeat(5) { send("C$it"); delay(200) } }
    
    val merged = merge(channel1, channel2, channel3)
    
    for (value in merged) {
        println("Merged: $value")
    }
}
```

### Real-World Example: Web Scraper

```kotlin
data class UrlTask(val url: String)
data class ScrapedData(val url: String, val content: String, val scraperId: Int)

class WebScraperPool(
    private val scope: CoroutineScope,
    private val scraperCount: Int = 5
) {
    private val urlChannel = Channel<UrlTask>(capacity = 100)
    private val resultChannel = Channel<ScrapedData>(capacity = 100)
    
    init {
        repeat(scraperCount) { scraperId ->
            scope.launch {
                scraper(scraperId)
            }
        }
    }
    
    private suspend fun scraper(scraperId: Int) {
        for (task in urlChannel) {
            try {
                println("Scraper $scraperId fetching ${task.url}")
                delay(500) // Simulate HTTP request
                
                val content = "Content from ${task.url}"
                resultChannel.send(ScrapedData(task.url, content, scraperId))
            } catch (e: Exception) {
                println("Scraper $scraperId failed: ${e.message}")
            }
        }
    }
    
    suspend fun scrape(url: String) {
        urlChannel.send(UrlTask(url))
    }
    
    fun results(): ReceiveChannel<ScrapedData> = resultChannel
    
    fun close() {
        urlChannel.close()
    }
}

suspend fun main() = coroutineScope {
    val scraper = WebScraperPool(this, scraperCount = 3)
    
    // Submit URLs
    launch {
        val urls = List(15) { "https://example.com/page$it" }
        urls.forEach { scraper.scrape(it) }
        scraper.close()
    }
    
    // Collect results (fan-in)
    val results = mutableListOf<ScrapedData>()
    for (data in scraper.results()) {
        results.add(data)
        println("Collected: ${data.url} by scraper ${data.scraperId}")
    }
    
    println("Total scraped: ${results.size} pages")
}
```

### Best Practices

#### DO:

```kotlin
// Use fan-out for parallel processing
val workers = List(5) { processChannel(workerId = it, input) }

// Use fan-in for result aggregation
val merged = merge(channel1, channel2, channel3)

// Close channels properly
launch {
    submitTasks()
    channel.close() // Signal no more tasks
}

// Handle backpressure with buffered channels
val channel = Channel<Task>(capacity = 100)
```

#### DON'T:

```kotlin
// Don't create too many workers
repeat(1000) { /* worker */ } // Too many!

// Don't forget channel capacity
val channel = Channel<Int>() // Rendezvous can block

// Don't ignore exceptions in workers
launch {
    for (task in channel) {
        process(task) // Can throw!
    }
}
```

---

## References

- [Kotlin Channels Documentation](https://kotlinlang.org/docs/channels.html)
- [Fan-in Fan-out Pattern](https://kotlinlang.org/docs/channels.html#fan-out)
- [Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-channel-buffering-strategies--kotlin--hard]]
- [[q-structured-concurrency--kotlin--hard]]

## MOC Links

- [[moc-kotlin]]

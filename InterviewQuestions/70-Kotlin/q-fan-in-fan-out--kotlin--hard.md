---
'---id': kotlin-092
title: Fan-in Fan-out Pattern / Паттерн Fan-in Fan-out
topic: kotlin
subtopics:
- channels
- concurrency
- coroutines
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
source: internal
source_note: Comprehensive guide on Fan-in Fan-out patterns
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-stateflow
- q-actor-pattern--kotlin--hard
- q-advanced-coroutine-patterns--kotlin--hard
created: 2025-10-12
updated: 2025-11-11
aliases: []
tags:
- channels
- coroutines
- difficulty/hard
- fan-in
- fan-out
- kotlin
- load-balancing
- parallel-processing
anki_cards:
- slug: q-fan-in-fan-out--kotlin--hard-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-fan-in-fan-out--kotlin--hard-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> Что такое паттерны Fan-in и Fan-out в корутинах Kotlin? Объясните как распределять работу между несколькими воркерами и агрегировать результаты из множества источников.

# Question (EN)
> What are Fan-in and Fan-out patterns in Kotlin coroutines? Explain how to distribute work to multiple workers and aggregate results from multiple sources.

## Ответ (RU)

**Fan-out** распределяет работу от одного источника к нескольким потребителям (воркерам). **Fan-in** агрегирует результаты от множества производителей в одного потребителя.

См. также: [[c-coroutines]], [[c-flow]].

### Паттерн Fan-out

Распределение работы между несколькими воркерами для параллельной обработки с использованием одного входного канала:

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
        println("Воркер $id обрабатывает $number")
        delay(100)
    }
}

suspend fun main() = coroutineScope {
    val numbers = produceNumbers()
    
    // Fan-out: 5 воркеров потребляют из одного канала (load balancing через канал)
    repeat(5) { workerId ->
        processNumbers(workerId, numbers)
    }

    // produce { ... } завершится сам, что приведёт к закрытию numbers
    // и корректному завершению всех воркеров.
}
```

**Пример балансировки нагрузки (безопасное закрытие канала):**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class Task(val id: Int, val payload: String)
data class Result(val taskId: Int, val result: String, val workerId: Int)

class WorkerPool(private val scope: CoroutineScope, private val workerCount: Int) {
    private val taskChannel = Channel<Task>(capacity = 100)
    private val resultChannel = Channel<Result>(capacity = 100)
    private val workers: List<Job>

    init {
        workers = List(workerCount) { workerId ->
            scope.launch {
                worker(workerId)
            }
        }
    }
    
    private suspend fun worker(workerId: Int) {
        for (task in taskChannel) {
            delay(100) // эмуляция работы
            val result = Result(
                taskId = task.id,
                result = task.payload.uppercase(),
                workerId = workerId
            )
            resultChannel.send(result)
            println("Worker $workerId completed task ${task.id}")
        }
        // Выход при закрытом и исчерпанном taskChannel.
    }
    
    suspend fun submitTask(task: Task) {
        taskChannel.send(task)
    }

    fun results(): ReceiveChannel<Result> = resultChannel

    // Завершение: закрыть вход, дождаться воркеров, затем закрыть канал результатов
    suspend fun finish() {
        taskChannel.close()
        workers.forEach { it.join() }
        resultChannel.close()
    }
}
```

### Паттерн Fan-in

Агрегация результатов от множества производителей в один канал-приёмник. Канал, возвращаемый `fanIn`, автоматически будет закрыт, когда все исходные каналы завершатся и вспомогательные корутины дочитают их данные:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

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
```

Пример использования:

```kotlin
suspend fun main() = coroutineScope {
    val producers = List(3) { produceNumbersFrom(it * 10) }
    val consumer = fanIn(producers)

    for (value in consumer) {
        println("Received: $value")
    }
}
```

Примечание: канал `consumer` завершится, когда все исходные каналы завершатся, вспомогательные корутины закончат работу, и builder `produce` завершится, автоматически закрыв результирующий канал.

**Практический Fan-in: агрегация логов**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class LogEntry(val source: String, val message: String, val timestamp: Long)

class LogAggregator(private val scope: CoroutineScope) {
    private val aggregatedChannel = Channel<LogEntry>(capacity = 1000)
    private val sources = mutableListOf<SendChannel<String>>()
    private val jobs = mutableListOf<Job>()
    
    fun createLogSource(sourceName: String): SendChannel<String> {
        val channel = Channel<String>(capacity = 100)
        sources += channel
        
        val job = scope.launch {
            for (message in channel) {
                val entry = LogEntry(
                    source = sourceName,
                    message = message,
                    timestamp = System.currentTimeMillis()
                )
                aggregatedChannel.send(entry)
            }
        }
        jobs += job
        
        return channel
    }
    
    fun subscribe(): ReceiveChannel<LogEntry> = aggregatedChannel

    // Координированное завершение
    suspend fun close() {
        sources.forEach { it.close() }
        jobs.forEach { it.join() }
        aggregatedChannel.close()
    }
}
```

### Комбинированный Fan-out И Fan-in

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class ImageTask(val id: Int, val url: String)
data class ProcessedImage(val id: Int, val data: ByteArray, val processorId: Int)

class ImageProcessingPipeline(
    private val scope: CoroutineScope,
    private val processorCount: Int = 4
) {
    private val taskChannel = Channel<ImageTask>(capacity = 50)
    private val resultChannel = Channel<ProcessedImage>(capacity = 50)
    private val workers: List<Job>
    
    init {
        // Fan-out: запуск нескольких процессоров
        workers = List(processorCount) { processorId ->
            scope.launch {
                imageProcessor(processorId)
            }
        }
    }

    private suspend fun imageProcessor(processorId: Int) {
        for (task in taskChannel) {
            delay(200) // эмуляция обработки
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

    // Сигнал о завершении подачи задач
    fun closeInput() {
        taskChannel.close()
    }

    // Дождаться завершения воркеров и закрыть выходной канал
    suspend fun closeOutput() {
        workers.forEach { it.join() }
        resultChannel.close()
    }
}
```

### Продвинутый Fan-out: Work Stealing (упрощённый)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.util.concurrent.atomic.AtomicInteger

class WorkStealingPool<T, R>(
    private val scope: CoroutineScope,
    private val workerCount: Int,
    private val processor: suspend (T) -> R
) {
    private val taskChannels = List(workerCount) { Channel<T>(capacity = 10) }
    private val resultChannel = Channel<R>(capacity = 100)
    private val taskCounter = AtomicInteger(0)
    private val workers: List<Job>
    
    init {
        workers = List(workerCount) { workerId ->
            scope.launch { workStealingWorker(workerId) }
        }
    }
    
    private suspend fun workStealingWorker(workerId: Int) {
        val myChannel = taskChannels[workerId]
        while (true) {
            val task = myChannel.tryReceive().getOrNull() ?: stealTask(workerId)
            if (task != null) {
                val result = processor(task)
                resultChannel.send(result)
            } else {
                // Упрощённая логика завершения: возможны гонки, не для продакшена
                if (taskChannels.all { it.isClosedForReceive && it.isEmpty }) break
                delay(10)
            }
        }
    }
    
    private fun stealTask(myId: Int): T? {
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
    
    // Инициировать завершение: закрыть все taskChannels
    fun close() {
        taskChannels.forEach { it.close() }
    }
    
    // Дождаться воркеров и закрыть resultChannel
    suspend fun awaitCompletion() {
        workers.forEach { it.join() }
        resultChannel.close()
    }
}
```

### Объединение Нескольких Каналов (Fan-in helper)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.selects.select

fun <T> CoroutineScope.merge(vararg channels: ReceiveChannel<T>): ReceiveChannel<T> = produce {
    channels.forEach { channel ->
        launch {
            for (item in channel) {
                send(item)
            }
        }
    }
}

fun <T> CoroutineScope.mergeWithSelect(vararg channels: ReceiveChannel<T>): ReceiveChannel<T> = produce {
    val channelList = channels.toMutableList()
    
    while (channelList.isNotEmpty()) {
        select<Unit> {
            channelList.forEach { channel ->
                channel.onReceiveCatching { result ->
                    val value = result.getOrNull()
                    if (value != null) {
                        send(value)
                    } else {
                        // без изменения коллекции в момент итерации
                    }
                }
            }
        }
        // удалить закрытые каналы вне select, после итерации
        channelList.removeAll { it.isClosedForReceive }
    }
}
```

### Реальный Пример: Web Scraper

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class UrlTask(val url: String)
data class ScrapedData(val url: String, val content: String, val scraperId: Int)

class WebScraperPool(
    private val scope: CoroutineScope,
    private val scraperCount: Int = 5
) {
    private val urlChannel = Channel<UrlTask>(capacity = 100)
    private val resultChannel = Channel<ScrapedData>(capacity = 100)
    private val workers: List<Job>
    
    init {
        workers = List(scraperCount) { scraperId ->
            scope.launch {
                scraper(scraperId)
            }
        }
    }
    
    private suspend fun scraper(scraperId: Int) {
        for (task in urlChannel) {
            try {
                println("Scraper $scraperId fetching ${task.url}")
                delay(500)
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
    
    fun closeInput() {
        urlChannel.close()
    }
    
    suspend fun closeOutput() {
        workers.forEach { it.join() }
        resultChannel.close()
    }
}
```

### Лучшие Практики

#### ДЕЛАТЬ:

```kotlin
// Использовать fan-out для параллельной обработки (workerFn — определённый helper)
val workers = List(5) { workerId -> workerFn(workerId = workerId, input) }

// Использовать fan-in для агрегации результатов (merge определён как helper выше)
val merged = merge(channel1, channel2, channel3)

// Корректно закрывать каналы: сначала вход, после завершения воркеров — выход
launch {
    submitTasks()
    inputChannel.close()
}

// Использовать буферизованные каналы для управления backpressure
val channel = Channel<Task>(capacity = 100)
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не создавать чрезмерное количество воркеров
repeat(1000) { /* worker */ }

// Не игнорировать семантику capacity и блокировок
val channel = Channel<Int>() // rendezvous-канал может блокировать

// Не игнорировать исключения во воркерах
launch {
    try {
        for (task in channel) {
            process(task)
        }
    } catch (e: Throwable) {
        // обработать или пробросить
    }
}

// Не отправлять в закрытый канал
// send после close приведёт к ClosedSendChannelException
```

## Answer (EN)

**Fan-out** distributes work from a single source to multiple consumers (workers). **Fan-in** aggregates results from multiple producers into a single consumer.

See also: [[c-coroutines]], [[c-flow]].

### Fan-out Pattern

Distributing work to multiple workers for parallel processing using a single input channel:

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
    
    // Fan-out: 5 workers consuming from a single channel (load balancing via channel)
    repeat(5) { workerId ->
        processNumbers(workerId, numbers)
    }

    // The produce builder completes after sending all numbers, which closes `numbers`
    // and causes all workers' for-loops to finish.
}
```

**Load Balancing Example (safe channel closure):**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class Task(val id: Int, val payload: String)
data class Result(val taskId: Int, val result: String, val workerId: Int)

class WorkerPool(private val scope: CoroutineScope, private val workerCount: Int) {
    private val taskChannel = Channel<Task>(capacity = 100)
    private val resultChannel = Channel<Result>(capacity = 100)
    private val workers: List<Job>

    init {
        workers = List(workerCount) { workerId ->
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
        // Exits when taskChannel is closed and drained
    }
    
    suspend fun submitTask(task: Task) {
        taskChannel.send(task)
    }
    
    fun results(): ReceiveChannel<Result> = resultChannel

    // Signal no more tasks; wait workers; then close results so consumers can finish
    suspend fun finish() {
        taskChannel.close()
        workers.forEach { it.join() }
        resultChannel.close()
    }
}
```

### Fan-in Pattern

Aggregating results from multiple producers into a single channel. The channel returned by `fanIn` will be closed automatically when all source channels complete and the producer's body finishes:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

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

Note: `consumer` completes when all source channels complete, helper coroutines finish reading, and the `produce` builder completes, closing the resulting channel.

**Real-World Fan-in: Log Aggregation**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class LogEntry(val source: String, val message: String, val timestamp: Long)

class LogAggregator(private val scope: CoroutineScope) {
    private val aggregatedChannel = Channel<LogEntry>(capacity = 1000)
    private val sources = mutableListOf<SendChannel<String>>()
    private val jobs = mutableListOf<Job>()
    
    fun createLogSource(sourceName: String): SendChannel<String> {
        val channel = Channel<String>(capacity = 100)
        sources += channel
        
        val job = scope.launch {
            for (message in channel) {
                val entry = LogEntry(
                    source = sourceName,
                    message = message,
                    timestamp = System.currentTimeMillis()
                )
                aggregatedChannel.send(entry)
            }
        }
        jobs += job
        
        return channel
    }
    
    fun subscribe(): ReceiveChannel<LogEntry> = aggregatedChannel

    // Coordinated shutdown: close all sources, wait, then close aggregatedChannel
    suspend fun close() {
        sources.forEach { it.close() }
        jobs.forEach { it.join() }
        aggregatedChannel.close()
    }
}
```

### Combined Fan-out and Fan-in

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class ImageTask(val id: Int, val url: String)
data class ProcessedImage(val id: Int, val data: ByteArray, val processorId: Int)

class ImageProcessingPipeline(
    private val scope: CoroutineScope,
    private val processorCount: Int = 4
) {
    private val taskChannel = Channel<ImageTask>(capacity = 50)
    private val resultChannel = Channel<ProcessedImage>(capacity = 50)
    private val workers: List<Job>
    
    init {
        // Fan-out: Launch multiple processors
        workers = List(processorCount) { processorId ->
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
    
    // Signal that no more tasks will be submitted
    fun closeInput() {
        taskChannel.close()
    }
    
    // Wait for workers to finish and then close output so consumers can complete
    suspend fun closeOutput() {
        workers.forEach { it.join() }
        resultChannel.close()
    }
}
```

### Advanced Fan-out: Work Stealing (simplified)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.util.concurrent.atomic.AtomicInteger

class WorkStealingPool<T, R>(
    private val scope: CoroutineScope,
    private val workerCount: Int,
    private val processor: suspend (T) -> R
) {
    private val taskChannels = List(workerCount) { Channel<T>(capacity = 10) }
    private val resultChannel = Channel<R>(capacity = 100)
    private val taskCounter = AtomicInteger(0)
    private val workers: List<Job>
    
    init {
        workers = List(workerCount) { workerId ->
            scope.launch { workStealingWorker(workerId) }
        }
    }
    
    private suspend fun workStealingWorker(workerId: Int) {
        val myChannel = taskChannels[workerId]
        while (true) {
            val task = myChannel.tryReceive().getOrNull() ?: stealTask(workerId)
            if (task != null) {
                val result = processor(task)
                resultChannel.send(result)
            } else {
                // Simplified shutdown logic; races are possible, not production-grade
                if (taskChannels.all { it.isClosedForReceive && it.isEmpty }) break
                delay(10)
            }
        }
    }
    
    private fun stealTask(myId: Int): T? {
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
    
    // Initiate shutdown: close all task channels
    fun close() {
        taskChannels.forEach { it.close() }
    }
    
    // Wait workers and close resultChannel so consumers can finish
    suspend fun awaitCompletion() {
        workers.forEach { it.join() }
        resultChannel.close()
    }
}
```

### Merge Multiple Channels (Fan-in Helper)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.selects.select

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
                    val value = result.getOrNull()
                    if (value != null) {
                        send(value)
                    } else {
                        // do not mutate channelList here
                    }
                }
            }
        }
        // Safely remove closed channels after select iteration
        channelList.removeAll { it.isClosedForReceive }
    }
}
```

### Real-World Example: Web Scraper

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class UrlTask(val url: String)
data class ScrapedData(val url: String, val content: String, val scraperId: Int)

class WebScraperPool(
    private val scope: CoroutineScope,
    private val scraperCount: Int = 5
) {
    private val urlChannel = Channel<UrlTask>(capacity = 100)
    private val resultChannel = Channel<ScrapedData>(capacity = 100)
    private val workers: List<Job>
    
    init {
        workers = List(scraperCount) { scraperId ->
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
    
    fun closeInput() {
        urlChannel.close()
    }
    
    suspend fun closeOutput() {
        workers.forEach { it.join() }
        resultChannel.close()
    }
}
```

### Best Practices

#### DO:

```kotlin
// Use fan-out for parallel processing (workerFn is a user-defined helper)
val workers = List(5) { workerId -> workerFn(workerId = workerId, input) }

// Use fan-in for result aggregation (merge defined above)
val merged = merge(channel1, channel2, channel3)

// Close channels properly: close input when done producing, and close output after workers finish
launch {
    submitTasks()
    inputChannel.close() // Signal no more tasks
}

// Handle backpressure with buffered channels
val channel = Channel<Task>(capacity = 100)
```

#### DON'T:

```kotlin
// Don't create too many workers
repeat(1000) { /* worker */ } // Too many!

// Don't forget channel capacity and blocking semantics
val channel = Channel<Int>() // Rendezvous can block producers or consumers

// Don't ignore exceptions in workers
launch {
    try {
        for (task in channel) {
            process(task) // Can throw!
        }
    } catch (e: Throwable) {
        // handle or propagate
    }
}

// Don't send into a closed channel (will throw ClosedSendChannelException)
```

## Дополнительные Вопросы (RU)

- Чем это отличается от решений на Java без корутин?
- Когда вы бы использовали эти паттерны на практике?
- Каковы типичные ошибки и подводные камни при работе с каналами и fan-in/fan-out?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация по каналам Kotlin](https://kotlinlang.org/docs/channels.html)
- [Fan-in Fan-out Pattern](https://kotlinlang.org/docs/channels.html#fan-out)
- [Руководство по корутинам](https://kotlinlang.org/docs/coroutines-guide.html)

## References

- [Kotlin Channels Documentation](https://kotlinlang.org/docs/channels.html)
- [Fan-in Fan-out Pattern](https://kotlinlang.org/docs/channels.html#fan-out)
- [Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)

## Связанные Вопросы (RU)

- [[q-actor-pattern--kotlin--hard]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-channel-buffering-strategies--kotlin--hard]]
- [[q-structured-concurrency--kotlin--hard]]

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-channel-buffering-strategies--kotlin--hard]]
- [[q-structured-concurrency--kotlin--hard]]

## MOC Ссылки (RU)

- [[moc-kotlin]]

## MOC Links

- [[moc-kotlin]]

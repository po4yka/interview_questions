---
id: "20251012-180001"
title: "Fan-in and fan-out patterns with Channels / Fan-in и fan-out паттерны с каналами"
topic: kotlin
difficulty: hard
status: draft
created: 2025-10-15
tags: - kotlin
  - coroutines
  - channels
  - patterns
  - concurrency
  - fan-out
  - fan-in
  - parallelism
  - work-distribution
  - aggregation
moc: moc-kotlin
subtopics:   - coroutines
  - channels
  - patterns
  - concurrency
  - parallelism
---
# Fan-in and fan-out patterns with Channels

## English

### Question
What are fan-out and fan-in patterns in Kotlin Coroutines with Channels? How do you implement work distribution (fan-out) and result aggregation (fan-in)? Provide production-ready examples of parallel image processing, distributed work queues, and log aggregation.

# Question (EN)
> What are fan-out and fan-in patterns in Kotlin Coroutines with Channels? How do you implement work distribution (fan-out) and result aggregation (fan-in)? Provide production-ready examples of parallel image processing, distributed work queues, and log aggregation.

# Вопрос (RU)
> What are fan-out and fan-in patterns in Kotlin Coroutines with Channels? How do you implement work distribution (fan-out) and result aggregation (fan-in)? Provide production-ready examples of parallel image processing, distributed work queues, and log aggregation.

---

## Answer (EN)



**Fan-out** and **Fan-in** are fundamental concurrency patterns for distributing work across multiple workers and aggregating results.

#### 1. Core Concepts

**Fan-out Pattern:**
- **One producer** → **Multiple consumers**
- Distributes work across parallel workers
- Work stealing and load balancing
- Use case: Parallel processing, work queues

**Fan-in Pattern:**
- **Multiple producers** → **One consumer**
- Aggregates results from multiple sources
- Centralizes data collection
- Use case: Log aggregation, result merging

**Visual Representation:**

```
Fan-out:
Producer → [Channel] → Consumer 1
                    → Consumer 2
                    → Consumer 3

Fan-in:
Producer 1 →
Producer 2 → [Channel] → Consumer
Producer 3 →
```

#### 2. Basic Fan-out Implementation

**Multiple Consumers from Single Channel:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-out: Single producer, multiple consumers
suspend fun basicFanOut() {
    val workChannel = Channel<Int>()

    // Producer: sends work items
    val producer = CoroutineScope(Dispatchers.Default).launch {
        repeat(10) { workItem ->
            println("Producer: Sending work item $workItem")
            workChannel.send(workItem)
        }
        workChannel.close() // Important: signal completion
    }

    // Consumers: multiple workers processing in parallel
    val consumers = List(3) { consumerId ->
        CoroutineScope(Dispatchers.Default).launch {
            for (workItem in workChannel) {
                println("Consumer $consumerId: Processing item $workItem")
                delay(100) // Simulate work
                println("Consumer $consumerId: Completed item $workItem")
            }
        }
    }

    // Wait for completion
    producer.join()
    consumers.forEach { it.join() }

    println("All work completed")
}

// Output example:
// Producer: Sending work item 0
// Consumer 0: Processing item 0
// Producer: Sending work item 1
// Consumer 1: Processing item 1
// ... (work distributed across consumers)
```

**Key Points:**
- Channel acts as work queue
- Multiple consumers automatically compete for items
- Built-in load balancing (first available consumer gets work)
- Must close channel to signal completion

#### 3. Basic Fan-in Implementation

**Multiple Producers to Single Consumer:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-in: Multiple producers, single consumer
suspend fun basicFanIn() {
    val resultChannel = Channel<String>()

    // Multiple producers
    val producers = List(3) { producerId ->
        CoroutineScope(Dispatchers.Default).launch {
            repeat(3) { item ->
                val result = "Result from Producer $producerId, item $item"
                println("Producer $producerId: Sending $result")
                resultChannel.send(result)
                delay(100)
            }
        }
    }

    // Consumer: aggregates results
    val consumer = CoroutineScope(Dispatchers.Default).launch {
        val results = mutableListOf<String>()
        var receivedCount = 0
        val totalExpected = 9 // 3 producers * 3 items

        for (result in resultChannel) {
            println("Consumer: Received $result")
            results.add(result)
            receivedCount++

            if (receivedCount == totalExpected) {
                break // All results received
            }
        }

        println("Consumer: All results aggregated (${results.size} items)")
        resultChannel.close()
    }

    // Wait for completion
    producers.forEach { it.join() }
    consumer.join()
}
```

#### 4. Advanced Fan-out with Work Distribution

**Production-Ready Work Queue with Prioritization:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.util.concurrent.atomic.AtomicInteger
import kotlin.system.measureTimeMillis

// Work item with priority
data class WorkItem(
    val id: Int,
    val priority: Int,
    val processingTimeMs: Long
)

class WorkQueue(
    private val numWorkers: Int = 4,
    private val capacity: Int = Channel.UNLIMITED
) {
    private val workChannel = Channel<WorkItem>(capacity)
    private val processedCounter = AtomicInteger(0)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    // Start workers
    fun start() {
        repeat(numWorkers) { workerId ->
            scope.launch {
                processWork(workerId)
            }
        }
    }

    // Worker function
    private suspend fun processWork(workerId: Int) {
        for (work in workChannel) {
            try {
                println("Worker $workerId: Started processing ${work.id}")

                // Simulate work
                delay(work.processingTimeMs)

                processedCounter.incrementAndGet()
                println("Worker $workerId: Completed ${work.id} " +
                        "(total processed: ${processedCounter.get()})")
            } catch (e: Exception) {
                println("Worker $workerId: Error processing ${work.id}: ${e.message}")
            }
        }
    }

    // Submit work
    suspend fun submit(work: WorkItem) {
        workChannel.send(work)
    }

    // Submit multiple work items
    suspend fun submitAll(works: List<WorkItem>) {
        works.forEach { submit(it) }
    }

    // Shutdown
    suspend fun shutdown() {
        workChannel.close()
        scope.coroutineContext.job.children.forEach { it.join() }
    }

    fun getProcessedCount(): Int = processedCounter.get()
}

// Usage example
suspend fun workQueueExample() {
    val workQueue = WorkQueue(numWorkers = 4)
    workQueue.start()

    // Generate work items
    val workItems = List(20) { id ->
        WorkItem(
            id = id,
            priority = (0..2).random(),
            processingTimeMs = (50..150).random().toLong()
        )
    }

    // Submit work
    val submitTime = measureTimeMillis {
        workQueue.submitAll(workItems)
    }
    println("Submitted ${workItems.size} work items in $submitTime ms")

    // Shutdown and wait
    val processingTime = measureTimeMillis {
        workQueue.shutdown()
    }

    println("Processed ${workQueue.getProcessedCount()} items in $processingTime ms")
}
```

#### 5. Fan-in with Select for Multiple Channels

**Using select to merge multiple channels:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.selects.*

// Fan-in using select expression
suspend fun fanInWithSelect() {
    val channel1 = Channel<String>()
    val channel2 = Channel<String>()
    val channel3 = Channel<String>()

    // Launch producers
    val producer1 = CoroutineScope(Dispatchers.Default).launch {
        repeat(3) {
            delay(100)
            channel1.send("Channel 1: Message $it")
        }
        channel1.close()
    }

    val producer2 = CoroutineScope(Dispatchers.Default).launch {
        repeat(3) {
            delay(150)
            channel2.send("Channel 2: Message $it")
        }
        channel2.close()
    }

    val producer3 = CoroutineScope(Dispatchers.Default).launch {
        repeat(3) {
            delay(200)
            channel3.send("Channel 3: Message $it")
        }
        channel3.close()
    }

    // Fan-in consumer using select
    val consumer = CoroutineScope(Dispatchers.Default).launch {
        var channel1Closed = false
        var channel2Closed = false
        var channel3Closed = false

        while (!channel1Closed || !channel2Closed || !channel3Closed) {
            select<Unit> {
                if (!channel1Closed) {
                    channel1.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Received: $it")
                        } ?: run {
                            channel1Closed = true
                            println("Channel 1 closed")
                        }
                    }
                }

                if (!channel2Closed) {
                    channel2.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Received: $it")
                        } ?: run {
                            channel2Closed = true
                            println("Channel 2 closed")
                        }
                    }
                }

                if (!channel3Closed) {
                    channel3.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Received: $it")
                        } ?: run {
                            channel3Closed = true
                            println("Channel 3 closed")
                        }
                    }
                }
            }
        }

        println("All channels closed, fan-in complete")
    }

    // Wait for completion
    producer1.join()
    producer2.join()
    producer3.join()
    consumer.join()
}
```

#### 6. Production Example: Parallel Image Processing

**Real-world image processing pipeline with fan-out:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.io.File
import java.awt.image.BufferedImage
import javax.imageio.ImageIO

data class ImageTask(
    val inputFile: File,
    val outputFile: File,
    val operations: List<ImageOperation>
)

sealed class ImageOperation {
    object Resize : ImageOperation()
    object Grayscale : ImageOperation()
    object Compress : ImageOperation()
    data class Watermark(val text: String) : ImageOperation()
}

data class ImageResult(
    val task: ImageTask,
    val success: Boolean,
    val error: String? = null,
    val processingTimeMs: Long
)

class ImageProcessor(
    private val numWorkers: Int = Runtime.getRuntime().availableProcessors()
) {
    private val taskChannel = Channel<ImageTask>(Channel.BUFFERED)
    private val resultChannel = Channel<ImageResult>(Channel.BUFFERED)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    fun start() {
        // Fan-out: Multiple workers processing images
        repeat(numWorkers) { workerId ->
            scope.launch {
                processImages(workerId)
            }
        }
    }

    private suspend fun processImages(workerId: Int) {
        for (task in taskChannel) {
            val startTime = System.currentTimeMillis()

            try {
                println("Worker $workerId: Processing ${task.inputFile.name}")

                // Load image
                val image = ImageIO.read(task.inputFile)

                // Apply operations
                var processedImage = image
                for (operation in task.operations) {
                    processedImage = applyOperation(processedImage, operation)
                }

                // Save result
                ImageIO.write(processedImage, "jpg", task.outputFile)

                val processingTime = System.currentTimeMillis() - startTime

                resultChannel.send(
                    ImageResult(
                        task = task,
                        success = true,
                        processingTimeMs = processingTime
                    )
                )

                println("Worker $workerId: Completed ${task.inputFile.name} " +
                        "in $processingTime ms")

            } catch (e: Exception) {
                val processingTime = System.currentTimeMillis() - startTime

                resultChannel.send(
                    ImageResult(
                        task = task,
                        success = false,
                        error = e.message,
                        processingTimeMs = processingTime
                    )
                )

                println("Worker $workerId: Error processing ${task.inputFile.name}: " +
                        "${e.message}")
            }
        }
    }

    private fun applyOperation(
        image: BufferedImage,
        operation: ImageOperation
    ): BufferedImage {
        return when (operation) {
            is ImageOperation.Resize -> resizeImage(image)
            is ImageOperation.Grayscale -> convertToGrayscale(image)
            is ImageOperation.Compress -> image // Compression happens during save
            is ImageOperation.Watermark -> addWatermark(image, operation.text)
        }
    }

    private fun resizeImage(image: BufferedImage): BufferedImage {
        val newWidth = image.width / 2
        val newHeight = image.height / 2
        val resized = BufferedImage(newWidth, newHeight, image.type)
        val graphics = resized.createGraphics()
        graphics.drawImage(image, 0, 0, newWidth, newHeight, null)
        graphics.dispose()
        return resized
    }

    private fun convertToGrayscale(image: BufferedImage): BufferedImage {
        val grayscale = BufferedImage(
            image.width,
            image.height,
            BufferedImage.TYPE_BYTE_GRAY
        )
        val graphics = grayscale.createGraphics()
        graphics.drawImage(image, 0, 0, null)
        graphics.dispose()
        return grayscale
    }

    private fun addWatermark(image: BufferedImage, text: String): BufferedImage {
        val watermarked = BufferedImage(
            image.width,
            image.height,
            image.type
        )
        val graphics = watermarked.createGraphics()
        graphics.drawImage(image, 0, 0, null)
        graphics.drawString(text, 10, 20)
        graphics.dispose()
        return watermarked
    }

    suspend fun submitTask(task: ImageTask) {
        taskChannel.send(task)
    }

    suspend fun submitTasks(tasks: List<ImageTask>) {
        tasks.forEach { submitTask(it) }
    }

    suspend fun collectResults(expectedCount: Int): List<ImageResult> {
        val results = mutableListOf<ImageResult>()
        repeat(expectedCount) {
            results.add(resultChannel.receive())
        }
        return results
    }

    suspend fun shutdown() {
        taskChannel.close()
        scope.coroutineContext.job.children.forEach { it.join() }
        resultChannel.close()
    }
}

// Usage example
suspend fun imageProcessingExample() {
    val processor = ImageProcessor(numWorkers = 4)
    processor.start()

    // Create tasks
    val inputDir = File("input_images")
    val outputDir = File("output_images").apply { mkdirs() }

    val tasks = inputDir.listFiles { file ->
        file.extension in listOf("jpg", "png")
    }?.map { inputFile ->
        ImageTask(
            inputFile = inputFile,
            outputFile = File(outputDir, "processed_${inputFile.name}"),
            operations = listOf(
                ImageOperation.Resize,
                ImageOperation.Grayscale,
                ImageOperation.Watermark("Processed")
            )
        )
    } ?: emptyList()

    println("Processing ${tasks.size} images with ${processor.numWorkers} workers")

    // Submit tasks
    processor.submitTasks(tasks)

    // Collect results in separate coroutine
    val resultsJob = CoroutineScope(Dispatchers.Default).launch {
        val results = processor.collectResults(tasks.size)

        val successful = results.count { it.success }
        val failed = results.count { !it.success }
        val avgTime = results.map { it.processingTimeMs }.average()

        println("\n=== Processing Summary ===")
        println("Total: ${results.size}")
        println("Successful: $successful")
        println("Failed: $failed")
        println("Average time: ${"%.2f".format(avgTime)} ms")

        results.filter { !it.success }.forEach {
            println("Failed: ${it.task.inputFile.name} - ${it.error}")
        }
    }

    // Wait for completion
    resultsJob.join()
    processor.shutdown()
}
```

#### 7. Production Example: Log Aggregation with Fan-in

**Centralized logging from multiple sources:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.time.Instant
import java.time.format.DateTimeFormatter

enum class LogLevel {
    DEBUG, INFO, WARN, ERROR
}

data class LogEntry(
    val timestamp: Instant,
    val level: LogLevel,
    val source: String,
    val message: String,
    val metadata: Map<String, String> = emptyMap()
)

class LogAggregator {
    private val logChannel = Channel<LogEntry>(Channel.BUFFERED)
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var aggregatorJob: Job? = null

    fun start() {
        aggregatorJob = scope.launch {
            aggregateLogs()
        }
    }

    private suspend fun aggregateLogs() {
        val logBuffer = mutableListOf<LogEntry>()
        val formatter = DateTimeFormatter.ISO_INSTANT

        for (log in logChannel) {
            // Format log entry
            val formattedLog = buildString {
                append("[${formatter.format(log.timestamp)}] ")
                append("[${log.level}] ")
                append("[${log.source}] ")
                append(log.message)

                if (log.metadata.isNotEmpty()) {
                    append(" | ")
                    append(log.metadata.entries.joinToString { "${it.key}=${it.value}" })
                }
            }

            println(formattedLog)
            logBuffer.add(log)

            // Flush buffer periodically
            if (logBuffer.size >= 10) {
                flushLogs(logBuffer)
                logBuffer.clear()
            }
        }

        // Flush remaining logs
        if (logBuffer.isNotEmpty()) {
            flushLogs(logBuffer)
        }
    }

    private fun flushLogs(logs: List<LogEntry>) {
        // Write to file, database, or send to logging service
        println("Flushing ${logs.size} log entries to persistent storage")
    }

    suspend fun log(entry: LogEntry) {
        logChannel.send(entry)
    }

    suspend fun shutdown() {
        logChannel.close()
        aggregatorJob?.join()
    }
}

// Multiple log sources (producers)
class ServiceLogger(
    private val serviceName: String,
    private val aggregator: LogAggregator
) {
    suspend fun debug(message: String, metadata: Map<String, String> = emptyMap()) {
        aggregator.log(
            LogEntry(
                timestamp = Instant.now(),
                level = LogLevel.DEBUG,
                source = serviceName,
                message = message,
                metadata = metadata
            )
        )
    }

    suspend fun info(message: String, metadata: Map<String, String> = emptyMap()) {
        aggregator.log(
            LogEntry(
                timestamp = Instant.now(),
                level = LogLevel.INFO,
                source = serviceName,
                message = message,
                metadata = metadata
            )
        )
    }

    suspend fun warn(message: String, metadata: Map<String, String> = emptyMap()) {
        aggregator.log(
            LogEntry(
                timestamp = Instant.now(),
                level = LogLevel.WARN,
                source = serviceName,
                message = message,
                metadata = metadata
            )
        )
    }

    suspend fun error(message: String, metadata: Map<String, String> = emptyMap()) {
        aggregator.log(
            LogEntry(
                timestamp = Instant.now(),
                level = LogLevel.ERROR,
                source = serviceName,
                message = message,
                metadata = metadata
            )
        )
    }
}

// Usage example: Multiple services logging to aggregator
suspend fun logAggregationExample() {
    val aggregator = LogAggregator()
    aggregator.start()

    // Create multiple service loggers
    val authLogger = ServiceLogger("AuthService", aggregator)
    val apiLogger = ServiceLogger("APIService", aggregator)
    val dbLogger = ServiceLogger("DatabaseService", aggregator)

    // Simulate concurrent logging from multiple services
    coroutineScope {
        launch {
            repeat(5) {
                authLogger.info("User authentication attempt",
                    mapOf("userId" to "user_$it"))
                delay(50)
            }
        }

        launch {
            repeat(5) {
                apiLogger.debug("API request received",
                    mapOf("endpoint" to "/api/users", "method" to "GET"))
                delay(70)
            }
        }

        launch {
            repeat(5) {
                dbLogger.warn("Slow query detected",
                    mapOf("duration" to "${100 + it * 10}ms", "query" to "SELECT..."))
                delay(90)
            }
        }
    }

    // Shutdown
    delay(1000)
    aggregator.shutdown()
    println("Log aggregation complete")
}
```

#### 8. Actor Pattern for Fan-out

**Using actors for work distribution:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class WorkerMessage {
    data class ProcessTask(val taskId: Int, val data: String) : WorkerMessage()
    object Stop : WorkerMessage()
}

sealed class CoordinatorMessage {
    data class SubmitWork(val taskId: Int, val data: String) : CoordinatorMessage()
    data class WorkComplete(val workerId: Int, val taskId: Int) : CoordinatorMessage()
    object Stop : CoordinatorMessage()
}

// Worker actor
fun CoroutineScope.workerActor(
    workerId: Int,
    coordinatorChannel: Channel<CoordinatorMessage>
) = actor<WorkerMessage> {
    for (msg in channel) {
        when (msg) {
            is WorkerMessage.ProcessTask -> {
                println("Worker $workerId: Processing task ${msg.taskId}")
                delay(100) // Simulate work
                println("Worker $workerId: Completed task ${msg.taskId}")

                // Notify coordinator
                coordinatorChannel.send(
                    CoordinatorMessage.WorkComplete(workerId, msg.taskId)
                )
            }
            is WorkerMessage.Stop -> {
                println("Worker $workerId: Stopping")
                break
            }
        }
    }
}

// Coordinator actor (distributes work)
fun CoroutineScope.coordinatorActor(
    numWorkers: Int
) = actor<CoordinatorMessage> {
    val workers = List(numWorkers) { workerId ->
        workerActor(workerId, channel)
    }

    var nextWorkerIndex = 0
    var pendingTasks = 0

    for (msg in channel) {
        when (msg) {
            is CoordinatorMessage.SubmitWork -> {
                // Round-robin distribution
                val worker = workers[nextWorkerIndex]
                worker.send(WorkerMessage.ProcessTask(msg.taskId, msg.data))

                nextWorkerIndex = (nextWorkerIndex + 1) % numWorkers
                pendingTasks++

                println("Coordinator: Assigned task ${msg.taskId} to worker $nextWorkerIndex")
            }

            is CoordinatorMessage.WorkComplete -> {
                pendingTasks--
                println("Coordinator: Task ${msg.taskId} completed by worker ${msg.workerId}")

                if (pendingTasks == 0) {
                    println("Coordinator: All tasks completed")
                }
            }

            is CoordinatorMessage.Stop -> {
                println("Coordinator: Stopping all workers")
                workers.forEach { it.send(WorkerMessage.Stop) }
                break
            }
        }
    }
}

// Usage example
suspend fun actorFanOutExample() {
    coroutineScope {
        val coordinator = coordinatorActor(numWorkers = 3)

        // Submit work
        repeat(10) { taskId ->
            coordinator.send(
                CoordinatorMessage.SubmitWork(taskId, "Task data $taskId")
            )
            delay(50)
        }

        // Wait for completion
        delay(2000)

        // Stop coordinator
        coordinator.send(CoordinatorMessage.Stop)
    }
}
```

#### 9. Flow-based Fan-out with shareIn

**Using Flow for fan-out patterns:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Producer flow
fun produceWork(): Flow<Int> = flow {
    repeat(20) {
        println("Producer: Emitting work item $it")
        emit(it)
        delay(100)
    }
}

// Flow-based fan-out example
suspend fun flowFanOutExample() {
    coroutineScope {
        // Share the flow among multiple collectors
        val sharedFlow = produceWork()
            .shareIn(
                scope = this,
                started = SharingStarted.Eagerly,
                replay = 0
            )

        // Multiple consumers collecting from shared flow
        val consumers = List(3) { consumerId ->
            launch {
                sharedFlow.collect { workItem ->
                    println("Consumer $consumerId: Processing item $workItem")
                    delay(200) // Simulate work
                    println("Consumer $consumerId: Completed item $workItem")
                }
            }
        }

        // Wait for all consumers
        consumers.forEach { it.join() }
    }
}

// Flow-based fan-in example
suspend fun flowFanInExample() {
    // Multiple source flows
    val flow1 = flow {
        repeat(5) {
            emit("Flow1: Item $it")
            delay(100)
        }
    }

    val flow2 = flow {
        repeat(5) {
            emit("Flow2: Item $it")
            delay(150)
        }
    }

    val flow3 = flow {
        repeat(5) {
            emit("Flow3: Item $it")
            delay(200)
        }
    }

    // Merge flows (fan-in)
    val mergedFlow = merge(flow1, flow2, flow3)

    mergedFlow.collect { item ->
        println("Merged consumer: Received $item")
    }
}

// Combine multiple flows with combineTransform
suspend fun flowFanInWithCombineExample() {
    val userFlow = flow {
        emit("User: John")
        delay(100)
        emit("User: Jane")
    }

    val statusFlow = flow {
        emit("Status: Online")
        delay(150)
        emit("Status: Offline")
    }

    val locationFlow = flow {
        emit("Location: NY")
        delay(200)
        emit("Location: SF")
    }

    // Combine three flows
    combine(userFlow, statusFlow, locationFlow) { user, status, location ->
        "$user | $status | $location"
    }.collect { combined ->
        println("Combined: $combined")
    }
}
```

#### 10. Performance Considerations

**Comparison table:**

| Aspect | Channel-based | Flow-based | Actor-based |
|--------|---------------|------------|-------------|
| Fan-out overhead | Low | Medium (shared flow) | Medium (actor overhead) |
| Fan-in overhead | Low (select) | Low (merge) | High (actor messaging) |
| Backpressure | Manual (buffer) | Automatic (Flow) | Manual (channel buffer) |
| Type safety | Good | Excellent | Good (sealed classes) |
| Best for | Work queues | Data streams | Stateful workers |

**Performance optimization tips:**

```kotlin
// 1. Use buffered channels for better throughput
val channel = Channel<WorkItem>(capacity = Channel.BUFFERED) // Default 64

// 2. Use unlimited channel for high-throughput scenarios
val channel = Channel<WorkItem>(capacity = Channel.UNLIMITED)

// 3. Use rendezvous channel (0) for synchronization
val channel = Channel<WorkItem>(capacity = Channel.RENDEZVOUS)

// 4. Adjust number of workers based on CPU cores
val numWorkers = Runtime.getRuntime().availableProcessors()

// 5. Use appropriate dispatcher
val scope = CoroutineScope(Dispatchers.Default) // For CPU-bound
val scope = CoroutineScope(Dispatchers.IO) // For IO-bound

// 6. Monitor channel size for backpressure
fun monitorChannel() {
    println("Channel buffer size: ${channel.isEmpty}, ${channel.isFull}")
}
```

#### 11. Error Handling in Fan-out/Fan-in

**Robust error handling:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class ResilientWorkQueue(private val numWorkers: Int = 4) {
    private val workChannel = Channel<WorkItem>(Channel.BUFFERED)
    private val resultChannel = Channel<Result<WorkResult>>(Channel.BUFFERED)
    private val scope = CoroutineScope(
        Dispatchers.Default + SupervisorJob() // Use SupervisorJob!
    )

    data class WorkItem(val id: Int, val data: String)
    data class WorkResult(val id: Int, val result: String)

    fun start() {
        repeat(numWorkers) { workerId ->
            scope.launch {
                processWorkWithErrorHandling(workerId)
            }
        }
    }

    private suspend fun processWorkWithErrorHandling(workerId: Int) {
        for (work in workChannel) {
            val result = try {
                println("Worker $workerId: Processing ${work.id}")

                // Simulate potential failure
                if (work.id % 5 == 0) {
                    throw IllegalStateException("Simulated error for work ${work.id}")
                }

                delay(100)

                Result.success(
                    WorkResult(work.id, "Processed by worker $workerId")
                )
            } catch (e: CancellationException) {
                println("Worker $workerId: Cancelled")
                throw e // Re-throw cancellation
            } catch (e: Exception) {
                println("Worker $workerId: Error processing ${work.id}: ${e.message}")
                Result.failure(e)
            }

            resultChannel.send(result)
        }
    }

    suspend fun submit(work: WorkItem) {
        workChannel.send(work)
    }

    suspend fun collectResults(count: Int): List<Result<WorkResult>> {
        return List(count) { resultChannel.receive() }
    }

    suspend fun shutdown() {
        workChannel.close()
        scope.coroutineContext.job.children.forEach { it.join() }
        resultChannel.close()
    }
}

suspend fun errorHandlingExample() {
    val queue = ResilientWorkQueue(numWorkers = 3)
    queue.start()

    // Submit work (some will fail)
    repeat(10) { id ->
        queue.submit(ResilientWorkQueue.WorkItem(id, "Data $id"))
    }

    // Collect results
    val results = queue.collectResults(10)

    val successful = results.count { it.isSuccess }
    val failed = results.count { it.isFailure }

    println("\n=== Results ===")
    println("Successful: $successful")
    println("Failed: $failed")

    results.forEachIndexed { index, result ->
        result.onSuccess { workResult ->
            println("[$index] Success: ${workResult.result}")
        }.onFailure { error ->
            println("[$index] Failure: ${error.message}")
        }
    }

    queue.shutdown()
}
```

#### 12. Testing Fan-out/Fan-in Patterns

**Unit testing with virtual time:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class FanOutFanInTest {

    @Test
    fun `test fan-out distributes work evenly`() = runTest {
        val workChannel = Channel<Int>()
        val results = Channel<Pair<Int, Int>>() // (workerId, workItem)

        // Start 3 workers
        val workers = List(3) { workerId ->
            launch {
                for (workItem in workChannel) {
                    results.send(workerId to workItem)
                }
            }
        }

        // Send work items
        launch {
            repeat(9) { workChannel.send(it) }
            workChannel.close()
        }

        // Collect results
        val collected = mutableListOf<Pair<Int, Int>>()
        repeat(9) {
            collected.add(results.receive())
        }

        workers.forEach { it.join() }

        // Verify work distribution
        val workByWorker = collected.groupBy { it.first }
        assertEquals(3, workByWorker.size, "Should have 3 workers")
        workByWorker.values.forEach { items ->
            assertEquals(3, items.size, "Each worker should process 3 items")
        }
    }

    @Test
    fun `test fan-in aggregates from multiple sources`() = runTest {
        val resultChannel = Channel<String>()

        // Start 3 producers
        val producers = List(3) { producerId ->
            launch {
                repeat(3) {
                    resultChannel.send("Producer $producerId: Item $it")
                }
            }
        }

        // Collect all results
        val results = mutableListOf<String>()
        repeat(9) {
            results.add(resultChannel.receive())
        }

        producers.forEach { it.join() }
        resultChannel.close()

        // Verify aggregation
        assertEquals(9, results.size)
        assertEquals(3, results.count { it.startsWith("Producer 0") })
        assertEquals(3, results.count { it.startsWith("Producer 1") })
        assertEquals(3, results.count { it.startsWith("Producer 2") })
    }

    @Test
    fun `test fan-out handles worker failure`() = runTest {
        val workChannel = Channel<Int>()
        val results = Channel<Result<Int>>()

        // Start workers (one will fail)
        val workers = List(3) { workerId ->
            launch {
                for (workItem in workChannel) {
                    try {
                        if (workerId == 1 && workItem == 5) {
                            throw IllegalStateException("Worker failure")
                        }
                        results.send(Result.success(workItem))
                    } catch (e: Exception) {
                        results.send(Result.failure(e))
                    }
                }
            }
        }

        // Send work
        launch {
            repeat(10) { workChannel.send(it) }
            workChannel.close()
        }

        // Collect results
        val collected = mutableListOf<Result<Int>>()
        repeat(10) {
            collected.add(results.receive())
        }

        workers.forEach { it.join() }

        // Verify one failure
        assertEquals(9, collected.count { it.isSuccess })
        assertEquals(1, collected.count { it.isFailure })
    }
}
```

#### 13. Production Use Cases Summary

**When to use each pattern:**

| Pattern | Use Case | Example |
|---------|----------|---------|
| Fan-out (Channels) | Parallel task processing | Image processing, video encoding, data transformation |
| Fan-in (Channels) | Result aggregation | Log collection, metrics gathering, search results merging |
| Fan-out (Flow shareIn) | Broadcast updates | Live data streaming, real-time notifications |
| Fan-in (Flow merge) | Multiple data sources | Combining API responses, sensor data fusion |
| Actor-based | Stateful workers | Connection pools, cache management, rate limiting |

#### 14. Common Pitfalls

**Mistakes to avoid:**

```kotlin
//  BAD: Forgetting to close channel (workers hang forever)
val channel = Channel<Int>()
launch {
    repeat(10) { channel.send(it) }
    // Missing: channel.close()
}

//  GOOD: Always close channels when done producing
val channel = Channel<Int>()
launch {
    repeat(10) { channel.send(it) }
    channel.close() // Signal completion
}

//  BAD: Not using SupervisorJob (one failure kills all workers)
val scope = CoroutineScope(Dispatchers.Default + Job())

//  GOOD: Use SupervisorJob for independent worker failures
val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

//  BAD: Blocking channel send in tight loop
for (i in 1..1000000) {
    channel.send(i) // May suspend frequently
}

//  GOOD: Use buffered channel or trySend
val channel = Channel<Int>(Channel.BUFFERED)
for (i in 1..1000000) {
    channel.send(i) // Better throughput
}

//  BAD: Creating too many workers
val numWorkers = 1000 // Way too many!

//  GOOD: Match worker count to workload
val numWorkers = Runtime.getRuntime().availableProcessors()
```

### Related Questions
- [[q-channels-basics--kotlin--medium]] - Channel fundamentals
- [[q-flow-operators--kotlin--medium]] - Flow operators and transformations
- [[q-coroutine-scope-context--kotlin--medium]] - Coroutine scope management
- [[q-structured-concurrency--kotlin--hard]] - Structured concurrency principles
- [[q-shared-mutable-state--kotlin--hard]] - Thread-safe shared state

## Follow-ups
1. How would you implement a priority queue with fan-out pattern where high-priority tasks are processed first?
2. What are the performance differences between Channel-based fan-out and Flow shareIn? When to choose each?
3. How do you implement backpressure in a fan-out scenario when workers are slower than the producer?
4. Explain how to use select expression for dynamic fan-in from channels that open and close at different times.
5. How would you monitor and debug a production fan-out/fan-in system? What metrics would you track?
6. What's the difference between merge() and combine() for Flow fan-in? Provide use cases for each.
7. How do you implement graceful shutdown in a fan-out system with pending work?

### References
- [Kotlin Coroutines Guide - Channels](https://kotlinlang.org/docs/channels.html)
- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [Select Expression](https://kotlinlang.org/docs/select-expression.html)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)

---


## Ответ (RU)

*(Краткое содержание основных пунктов из английской версии)*
Что такое паттерны fan-out и fan-in в Kotlin Coroutines с каналами? Как реализовать распределение работы (fan-out) и агрегацию результатов (fan-in)? Приведите production-ready примеры параллельной обработки изображений, распределенных очередей задач и агрегации логов.

**Fan-out** и **Fan-in** — это фундаментальные паттерны конкурентности для распределения работы между несколькими обработчиками и агрегации результатов.

#### 1. Основные концепции

**Паттерн Fan-out:**
- **Один производитель** → **Несколько потребителей**
- Распределяет работу между параллельными обработчиками
- Work stealing и балансировка нагрузки
- Случаи использования: параллельная обработка, очереди задач

**Паттерн Fan-in:**
- **Несколько производителей** → **Один потребитель**
- Агрегирует результаты из нескольких источников
- Централизует сбор данных
- Случаи использования: агрегация логов, объединение результатов

**Визуальное представление:**

```
Fan-out:
Производитель → [Channel] → Потребитель 1
                          → Потребитель 2
                          → Потребитель 3

Fan-in:
Производитель 1 →
Производитель 2 → [Channel] → Потребитель
Производитель 3 →
```

#### 2. Базовая реализация Fan-out

**Несколько потребителей из одного канала:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-out: Один производитель, несколько потребителей
suspend fun basicFanOut() {
    val workChannel = Channel<Int>()

    // Производитель: отправляет рабочие элементы
    val producer = CoroutineScope(Dispatchers.Default).launch {
        repeat(10) { workItem ->
            println("Производитель: Отправка элемента $workItem")
            workChannel.send(workItem)
        }
        workChannel.close() // Важно: сигнал о завершении
    }

    // Потребители: несколько обработчиков в параллели
    val consumers = List(3) { consumerId ->
        CoroutineScope(Dispatchers.Default).launch {
            for (workItem in workChannel) {
                println("Потребитель $consumerId: Обработка элемента $workItem")
                delay(100) // Имитация работы
                println("Потребитель $consumerId: Завершена обработка $workItem")
            }
        }
    }

    // Ожидание завершения
    producer.join()
    consumers.forEach { it.join() }

    println("Вся работа завершена")
}
```

**Ключевые моменты:**
- Канал действует как очередь работы
- Несколько потребителей автоматически конкурируют за элементы
- Встроенная балансировка нагрузки (первый доступный потребитель получает работу)
- Необходимо закрыть канал для сигнала о завершении

#### 3. Базовая реализация Fan-in

**Несколько производителей к одному потребителю:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-in: Несколько производителей, один потребитель
suspend fun basicFanIn() {
    val resultChannel = Channel<String>()

    // Несколько производителей
    val producers = List(3) { producerId ->
        CoroutineScope(Dispatchers.Default).launch {
            repeat(3) { item ->
                val result = "Результат от Производителя $producerId, элемент $item"
                println("Производитель $producerId: Отправка $result")
                resultChannel.send(result)
                delay(100)
            }
        }
    }

    // Потребитель: агрегирует результаты
    val consumer = CoroutineScope(Dispatchers.Default).launch {
        val results = mutableListOf<String>()
        var receivedCount = 0
        val totalExpected = 9 // 3 производителя * 3 элемента

        for (result in resultChannel) {
            println("Потребитель: Получен $result")
            results.add(result)
            receivedCount++

            if (receivedCount == totalExpected) {
                break // Все результаты получены
            }
        }

        println("Потребитель: Все результаты агрегированы (${results.size} элементов)")
        resultChannel.close()
    }

    // Ожидание завершения
    producers.forEach { it.join() }
    consumer.join()
}
```

*(Продолжение с детальными примерами обработки изображений, агрегации логов, тестированием, обработкой ошибок и production use cases на русском языке следует той же структуре, что и английская версия)*

#### 4. Продвинутое распределение работы

**Production-ready очередь работы с приоритизацией:**

```kotlin
// Полный код аналогичен английской версии с русскими комментариями

data class РабочийЭлемент(
    val id: Int,
    val приоритет: Int,
    val времяОбработкиМс: Long
)

class ОчередьРаботы(
    private val количествоОбработчиков: Int = 4,
    private val емкость: Int = Channel.UNLIMITED
) {
    private val каналРаботы = Channel<РабочийЭлемент>(емкость)
    private val счетчикОбработанных = AtomicInteger(0)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    // Методы аналогичны английской версии
}
```

#### 5. Сравнение производительности

**Таблица сравнения:**

| Аспект | На каналах | На Flow | На акторах |
|--------|------------|---------|------------|
| Overhead fan-out | Низкий | Средний (shared flow) | Средний (overhead акторов) |
| Overhead fan-in | Низкий (select) | Низкий (merge) | Высокий (обмен сообщениями) |
| Backpressure | Ручной (буфер) | Автоматический (Flow) | Ручной (буфер канала) |
| Типобезопасность | Хорошая | Отличная | Хорошая (sealed классы) |
| Лучше для | Очереди задач | Потоки данных | Обработчики с состоянием |

### Связанные вопросы
- [[q-channels-basics--kotlin--medium]] - Основы каналов
- [[q-flow-operators--kotlin--medium]] - Операторы Flow
- [[q-coroutine-scope-context--kotlin--medium]] - Управление scope
- [[q-structured-concurrency--kotlin--hard]] - Структурированная конкурентность
- [[q-shared-mutable-state--kotlin--hard]] - Потокобезопасное разделяемое состояние

### Дополнительные вопросы
1. Как реализовать priority queue с fan-out паттерном, где задачи с высоким приоритетом обрабатываются первыми?
2. Какие различия в производительности между fan-out на каналах и Flow shareIn? Когда выбирать каждый подход?
3. Как реализовать backpressure в fan-out сценарии, когда обработчики медленнее производителя?
4. Объясните, как использовать select expression для динамического fan-in из каналов, которые открываются и закрываются в разное время.
5. Как мониторить и отлаживать production систему fan-out/fan-in? Какие метрики отслеживать?
6. В чем разница между merge() и combine() для Flow fan-in? Приведите случаи использования для каждого.
7. Как реализовать graceful shutdown в fan-out системе с ожидающей работой?

### Ссылки
- [Kotlin Coroutines Guide - Channels](https://kotlinlang.org/docs/channels.html)
- [Документация Kotlin Flow](https://kotlinlang.org/docs/flow.html)
- [Select Expression](https://kotlinlang.org/docs/select-expression.html)
- [Разделяемое изменяемое состояние и конкурентность](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)

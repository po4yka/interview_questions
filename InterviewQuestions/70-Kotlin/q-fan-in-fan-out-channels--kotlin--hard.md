---
id: kotlin-181
title: "Fan-in and fan-out patterns with Channels / Fan-in и fan-out паттерны с каналами"
aliases: ["Fan-in and fan-out with channels", "Kotlin channels fan-in fan-out"]
topic: kotlin
subtopics: [c-coroutines, c-flow, c-structured-concurrency]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-delegation-by-keyword--kotlin--medium, q-kotlin-nullable-string-declaration--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/hard]
---
# Вопрос (RU)
> Что такое паттерны fan-out и fan-in в Kotlin Coroutines с каналами? Как реализовать распределение работы (fan-out) и агрегацию результатов (fan-in)? Приведите production-примеры параллельной обработки изображений, распределенных очередей задач и агрегации логов.

# Question (EN)
> What are fan-out and fan-in patterns in Kotlin Coroutines with Channels? How do you implement work distribution (fan-out) and result aggregation (fan-in)? Provide production-ready examples of parallel image processing, distributed work queues, and log aggregation.

## Ответ (RU)

**Fan-out** и **Fan-in** — это фундаментальные паттерны конкурентности для распределения работы между несколькими обработчиками и агрегации результатов.

- Fan-out на каналах обычно означает конкурентное потребление из общего канала (очередь задач).
- Fan-out в режиме широковещания (например, `shareIn` / `SharedFlow`) отдает каждый элемент всем подписчикам — это другой паттерн; ниже явно разводим эти случаи.

#### 1. Основные концепции

**Паттерн Fan-out:**
- **Один производитель** → **Несколько потребителей**
- Несколько воркеров читают из одного канала и соревнуются за элементы
- Естественная балансировка нагрузки: первый свободный воркер забирает следующий элемент
- Сценарии: параллельная обработка, очереди задач

**Паттерн Fan-in:**
- **Несколько производителей** → **Один потребитель/агрегатор**
- Агрегирует результаты или события из множества источников в один канал/конвейер
- Сценарии: агрегация логов, метрик, объединение результатов

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

Используем структурированную конкурентность: не создаем глобальные scope внутри хелперов.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-out: один производитель, несколько потребителей
suspend fun basicFanOut(scope: CoroutineScope) {
    val workChannel = Channel<Int>()

    // Производитель: отправляет рабочие элементы
    val producer = scope.launch {
        repeat(10) { workItem ->
            println("Производитель: отправка элемента $workItem")
            workChannel.send(workItem)
        }
        workChannel.close() // сигнал о завершении
    }

    // Потребители: несколько воркеров в параллели
    val consumers = List(3) { consumerId ->
        scope.launch {
            for (workItem in workChannel) {
                println("Потребитель $consumerId: обработка элемента $workItem")
                delay(100) // имитация работы
                println("Потребитель $consumerId: завершена обработка $workItem")
            }
        }
    }

    producer.join()
    consumers.forEach { it.join() }

    println("Вся работа завершена")
}
```

Ключевые моменты:
- Канал выступает как очередь задач.
- Несколько потребителей конкурентно читают из одного канала.
- Канал нужно закрыть, когда производитель завершил отправку.

#### 3. Базовая реализация Fan-in

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-in: несколько производителей, один потребитель
suspend fun basicFanIn(scope: CoroutineScope) {
    val resultChannel = Channel<String>()

    // Несколько производителей
    val producers = List(3) { producerId ->
        scope.launch {
            repeat(3) { item ->
                val result = "Результат от производителя $producerId, элемент $item"
                println("Производитель $producerId: отправка $result")
                resultChannel.send(result)
                delay(100)
            }
        }
    }

    // Потребитель: агрегирует результаты
    val consumer = scope.launch {
        val results = mutableListOf<String>()

        for (result in resultChannel) {
            println("Потребитель: получен $result")
            results.add(result)
        }

        println("Потребитель: все результаты агрегированы (${results.size} элементов)")
    }

    producers.forEach { it.join() }
    resultChannel.close()
    consumer.join()
}
```

#### 4. Продвинутое распределение работы (Work Queue)

Скелет очереди задач в стиле production: структурированная конкурентность, явный lifecycle, корректное завершение.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.util.concurrent.atomic.AtomicInteger

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

    fun start() {
        repeat(количествоОбработчиков) { workerId ->
            scope.launch {
                for (work in каналРаботы) {
                    try {
                        println("Worker $workerId: start ${work.id}")
                        delay(work.времяОбработкиМс)
                        счетчикОбработанных.incrementAndGet()
                    } catch (e: CancellationException) {
                        throw e
                    } catch (e: Exception) {
                        // логирование ошибки
                    }
                }
            }
        }
    }

    suspend fun submit(work: РабочийЭлемент) {
        каналРаботы.send(work)
    }

    suspend fun shutdown() {
        каналРаботы.close()
        scope.coroutineContext[Job]?.join()
    }
}
```

#### 5. Fan-in с select для нескольких каналов

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.selects.*

// Fan-in с использованием select
suspend fun fanInWithSelectRu(scope: CoroutineScope) {
    val channel1 = Channel<String>()
    val channel2 = Channel<String>()
    val channel3 = Channel<String>()

    val producer1 = scope.launch {
        repeat(3) {
            delay(100)
            channel1.send("Канал 1: сообщение $it")
        }
        channel1.close()
    }

    val producer2 = scope.launch {
        repeat(3) {
            delay(150)
            channel2.send("Канал 2: сообщение $it")
        }
        channel2.close()
    }

    val producer3 = scope.launch {
        repeat(3) {
            delay(200)
            channel3.send("Канал 3: сообщение $it")
        }
        channel3.close()
    }

    val consumer = scope.launch {
        var c1Closed = false
        var c2Closed = false
        var c3Closed = false

        while (!c1Closed || !c2Closed || !c3Closed) {
            select<Unit> {
                if (!c1Closed) {
                    channel1.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Получено: $it")
                        } ?: run {
                            c1Closed = true
                            println("Канал 1 закрыт")
                        }
                    }
                }

                if (!c2Closed) {
                    channel2.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Получено: $it")
                        } ?: run {
                            c2Closed = true
                            println("Канал 2 закрыт")
                        }
                    }
                }

                if (!c3Closed) {
                    channel3.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Получено: $it")
                        } ?: run {
                            c3Closed = true
                            println("Канал 3 закрыт")
                        }
                    }
                }
            }
        }

        println("Все каналы закрыты, fan-in завершен")
    }

    producer1.join()
    producer2.join()
    producer3.join()
    consumer.join()
}
```

#### 6. Production-пример: параллельная обработка изображений

Структура: fan-out воркеров по `taskChannel` и fan-in результатов через `resultChannel`.

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
    val numWorkers: Int = Runtime.getRuntime().availableProcessors()
) {
    private val taskChannel = Channel<ImageTask>(Channel.BUFFERED)
    private val resultChannel = Channel<ImageResult>(Channel.BUFFERED)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    fun start() {
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
                println("Worker $workerId: обработка ${task.inputFile.name}")

                val image = ImageIO.read(task.inputFile)
                requireNotNull(image) { "Не удалось прочитать изображение: ${task.inputFile}" }

                var processedImage = image
                for (operation in task.operations) {
                    processedImage = applyOperation(processedImage, operation)
                }

                ImageIO.write(processedImage, "jpg", task.outputFile)

                val processingTime = System.currentTimeMillis() - startTime
                resultChannel.send(
                    ImageResult(task, success = true, processingTimeMs = processingTime)
                )
            } catch (e: Exception) {
                val processingTime = System.currentTimeMillis() - startTime
                resultChannel.send(
                    ImageResult(
                        task,
                        success = false,
                        error = e.message,
                        processingTimeMs = processingTime
                    )
                )
            }
        }
    }

    private fun applyOperation(
        image: BufferedImage,
        operation: ImageOperation
    ): BufferedImage = when (operation) {
        ImageOperation.Resize -> resizeImage(image)
        ImageOperation.Grayscale -> convertToGrayscale(image)
        ImageOperation.Compress -> image
        is ImageOperation.Watermark -> addWatermark(image, operation.text)
    }

    private fun resizeImage(image: BufferedImage): BufferedImage {
        val newWidth = maxOf(1, image.width / 2)
        val newHeight = maxOf(1, image.height / 2)
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
        val watermarked = BufferedImage(image.width, image.height, image.type)
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
        for (t in tasks) submitTask(t)
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
        scope.coroutineContext[Job]?.join()
        resultChannel.close()
    }
}
```

#### 7. Production-пример: агрегация логов (Fan-in)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.time.Instant
import java.time.format.DateTimeFormatter

enum class LogLevel { DEBUG, INFO, WARN, ERROR }

data class LogEntry(
    val timestamp: Instant,
    val level: LogLevel,
    val source: String,
    val message: String,
    val metadata: Map<String, String> = emptyMap()
)

class LogAggregator(
    capacity: Int = Channel.BUFFERED
) {
    private val logChannel = Channel<LogEntry>(capacity)
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

            if (logBuffer.size >= 10) {
                flushLogs(logBuffer)
                logBuffer.clear()
            }
        }

        if (logBuffer.isNotEmpty()) {
            flushLogs(logBuffer)
        }
    }

    private fun flushLogs(logs: List<LogEntry>) {
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
```

#### 8. Паттерн Actor для Fan-out

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

fun CoroutineScope.workerActor(
    workerId: Int,
    coordinatorChannel: SendChannel<CoordinatorMessage>
) = actor<WorkerMessage> {
    for (msg in channel) {
        when (msg) {
            is WorkerMessage.ProcessTask -> {
                println("Worker $workerId: processing task ${msg.taskId}")
                delay(100)
                println("Worker $workerId: completed task ${msg.taskId}")
                coordinatorChannel.send(
                    CoordinatorMessage.WorkComplete(workerId, msg.taskId)
                )
            }
            WorkerMessage.Stop -> {
                println("Worker $workerId: stopping")
                break
            }
        }
    }
}

fun CoroutineScope.coordinatorActor(
    numWorkers: Int
) = actor<CoordinatorMessage> {
    val workers = List(numWorkers) { workerId ->
        workerActor(workerId, this)
    }

    var nextWorkerIndex = 0
    var pendingTasks = 0

    for (msg in channel) {
        when (msg) {
            is CoordinatorMessage.SubmitWork -> {
                val worker = workers[nextWorkerIndex]
                worker.send(WorkerMessage.ProcessTask(msg.taskId, msg.data))
                nextWorkerIndex = (nextWorkerIndex + 1) % numWorkers
                pendingTasks++
            }

            is CoordinatorMessage.WorkComplete -> {
                pendingTasks--
                if (pendingTasks == 0) {
                    println("Coordinator: all tasks completed")
                }
            }

            CoordinatorMessage.Stop -> {
                workers.forEach { it.send(WorkerMessage.Stop) }
                break
            }
        }
    }
}
```

#### 9. Fan-out/Fan-in на основе Flow

- Fan-out (broadcast): `shareIn` чтобы каждый потребитель видел все элементы.
- Fan-in: `merge` для объединения нескольких `Flow` в один.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun produceWork(): Flow<Int> = flow {
    repeat(20) {
        println("Producer: emitting work item $it")
        emit(it)
        delay(100)
    }
}

suspend fun flowFanOutExampleRu() = coroutineScope {
    val sharedFlow = produceWork()
        .shareIn(
            scope = this,
            started = SharingStarted.Eagerly,
            replay = 0
        )

    val consumers = List(3) { consumerId ->
        launch {
            sharedFlow.collect { workItem ->
                println("Consumer $consumerId: processing item $workItem")
                delay(200)
                println("Consumer $consumerId: completed item $workItem")
            }
        }
    }

    consumers.forEach { it.join() }
}
```

#### 10. Производительность

```kotlin
val bufferedChannel = Channel<WorkItem>(capacity = Channel.BUFFERED)
val unlimitedChannel = Channel<WorkItem>(capacity = Channel.UNLIMITED)
val rendezvousChannel = Channel<WorkItem>(capacity = Channel.RENDEZVOUS)

val numWorkers = Runtime.getRuntime().availableProcessors()

val cpuScope = CoroutineScope(Dispatchers.Default)
val ioScope = CoroutineScope(Dispatchers.IO)

fun logChannelState(channel: Channel<*>) {
    println("Channel isEmpty=${channel.isEmpty}, isFull=${channel.isFull}")
}
```

#### 11. Обработка ошибок в Fan-out/Fan-in

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class ResilientWorkQueue(private val numWorkers: Int = 4) {
    data class WorkItem(val id: Int, val data: String)
    data class WorkResult(val id: Int, val result: String)

    private val workChannel = Channel<WorkItem>(Channel.BUFFERED)
    private val resultChannel = Channel<Result<WorkResult>>(Channel.BUFFERED)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

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
                println("Worker $workerId: processing ${work.id}")
                if (work.id % 5 == 0) {
                    throw IllegalStateException("Simulated error for work ${work.id}")
                }
                delay(100)
                Result.success(WorkResult(work.id, "Processed by worker $workerId"))
            } catch (e: CancellationException) {
                println("Worker $workerId: cancelled")
                throw e
            } catch (e: Exception) {
                println("Worker $workerId: error processing ${work.id}: ${e.message}")
                Result.failure(e)
            }
            resultChannel.send(result)
        }
    }

    suspend fun submit(work: WorkItem) {
        workChannel.send(work)
    }

    suspend fun collectResults(count: Int): List<Result<WorkResult>> =
        List(count) { resultChannel.receive() }

    suspend fun shutdown() {
        workChannel.close()
        scope.coroutineContext[Job]?.join()
        resultChannel.close()
    }
}
```

#### 12. Тестирование Fan-out/Fan-in

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.test.*
import kotlin.test.Test
import kotlin.test.assertEquals

class FanOutFanInTestRu {

    @Test
    fun `fan-out распределяет работу`() = runTest {
        val workChannel = Channel<Int>()
        val results = Channel<Pair<Int, Int>>()

        val workers = List(3) { workerId ->
            launch {
                for (workItem in workChannel) {
                    results.send(workerId to workItem)
                }
            }
        }

        launch {
            repeat(9) { workChannel.send(it) }
            workChannel.close()
        }

        val collected = mutableListOf<Pair<Int, Int>>()
        repeat(9) {
            collected.add(results.receive())
        }
        results.close()

        workers.forEach { it.join() }

        val workByWorker = collected.groupBy { it.first }
        assertEquals(3, workByWorker.size)
        workByWorker.values.forEach { items ->
            assertEquals(3, items.size)
        }
    }
}
```

#### 13. Итоги production use cases

- Fan-out (каналы, конкурентное потребление): очереди задач, параллельная обработка.
- Fan-in (каналы): агрегация логов, метрик, результатов.
- Fan-out (broadcast через `shareIn` / `SharedFlow`): рассылка обновлений всем подписчикам.
- Fan-in (`merge` для `Flow`): объединение нескольких асинхронных источников.
- Actor-подход: состояние и протоколы на воркерах.

#### 14. Частые ошибки

```kotlin
// ПЛОХО: забыли закрыть канал
val channel = Channel<Int>()
launch {
    repeat(10) { channel.send(it) }
    // нет channel.close()
}

// ХОРОШО: закрываем канал после окончания
val channel2 = Channel<Int>()
launch {
    repeat(10) { channel2.send(it) }
    channel2.close()
}

// ПЛОХО: Job вместо SupervisorJob для пула воркеров
val badScope = CoroutineScope(Dispatchers.Default + Job())

// ХОРОШО: SupervisorJob, чтобы сбой одного воркера не гасил всех
val goodScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
```

## Answer (EN)

Fan-out and fan-in in Kotlin Coroutines with channels follow the same ideas as in the RU section above and are used for scalable work distribution and result aggregation.

Below is an English mirror of the key production-style patterns and examples.

#### 1. Core concepts

**Fan-out:**
- One producer → multiple consumers.
- Multiple workers read competitively from a shared channel.
- Natural load balancing: whichever worker is free pulls the next item.
- Typical uses: parallel processing, task queues.

**Fan-in:**
- Multiple producers → single consumer/aggregator.
- Aggregates results or events from many sources into a single channel/pipeline.
- Typical uses: log aggregation, metrics, merging results.

Visual model:

```
Fan-out:
Producer → [Channel] → Worker 1
                     → Worker 2
                     → Worker 3

Fan-in:
Producer 1 →
Producer 2 → [Channel] → Aggregator
Producer 3 →
```

#### 2. Basic fan-out implementation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-out: one producer, multiple consumers
suspend fun basicFanOutEn(scope: CoroutineScope) {
    val workChannel = Channel<Int>()

    // Producer: sends work items
    val producer = scope.launch {
        repeat(10) { workItem ->
            println("Producer: sending item $workItem")
            workChannel.send(workItem)
        }
        workChannel.close() // completion signal
    }

    // Consumers: several workers in parallel
    val consumers = List(3) { consumerId ->
        scope.launch {
            for (workItem in workChannel) {
                println("Consumer $consumerId: processing item $workItem")
                delay(100)
                println("Consumer $consumerId: done $workItem")
            }
        }
    }

    producer.join()
    consumers.forEach { it.join() }

    println("All work completed")
}
```

Key points:
- Channel works as a work `Queue`.
- Multiple consumers read from the same channel concurrently.
- Always close the channel when the producer is done.

#### 3. Basic fan-in implementation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-in: multiple producers, single consumer
suspend fun basicFanInEn(scope: CoroutineScope) {
    val resultChannel = Channel<String>()

    // Multiple producers
    val producers = List(3) { producerId ->
        scope.launch {
            repeat(3) { item ->
                val result = "Result from producer $producerId, item $item"
                println("Producer $producerId: sending $result")
                resultChannel.send(result)
                delay(100)
            }
        }
    }

    // Consumer: aggregates results
    val consumer = scope.launch {
        val results = mutableListOf<String>()

        for (result in resultChannel) {
            println("Consumer: got $result")
            results.add(result)
        }

        println("Consumer: aggregated all results (${results.size} items)")
    }

    producers.forEach { it.join() }
    resultChannel.close()
    consumer.join()
}
```

#### 4. Advanced work queue (production-style)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.util.concurrent.atomic.AtomicInteger

data class WorkItemEn(
    val id: Int,
    val priority: Int,
    val processingTimeMs: Long
)

class WorkQueueEn(
    private val workerCount: Int = 4,
    private val capacity: Int = Channel.UNLIMITED
) {
    private val workChannel = Channel<WorkItemEn>(capacity)
    private val processedCounter = AtomicInteger(0)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    fun start() {
        repeat(workerCount) { workerId ->
            scope.launch {
                for (work in workChannel) {
                    try {
                        println("Worker $workerId: start ${work.id}")
                        delay(work.processingTimeMs)
                        processedCounter.incrementAndGet()
                    } catch (e: CancellationException) {
                        throw e
                    } catch (e: Exception) {
                        // log error
                    }
                }
            }
        }
    }

    suspend fun submit(work: WorkItemEn) {
        workChannel.send(work)
    }

    suspend fun shutdown() {
        workChannel.close()
        scope.coroutineContext[Job]?.join()
    }
}
```

#### 5. Fan-in with select over multiple channels

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.selects.*

// Fan-in using select
suspend fun fanInWithSelectEn(scope: CoroutineScope) {
    val channel1 = Channel<String>()
    val channel2 = Channel<String>()
    val channel3 = Channel<String>()

    val producer1 = scope.launch {
        repeat(3) {
            delay(100)
            channel1.send("Channel 1: message $it")
        }
        channel1.close()
    }

    val producer2 = scope.launch {
        repeat(3) {
            delay(150)
            channel2.send("Channel 2: message $it")
        }
        channel2.close()
    }

    val producer3 = scope.launch {
        repeat(3) {
            delay(200)
            channel3.send("Channel 3: message $it")
        }
        channel3.close()
    }

    val consumer = scope.launch {
        var c1Closed = false
        var c2Closed = false
        var c3Closed = false

        while (!c1Closed || !c2Closed || !c3Closed) {
            select<Unit> {
                if (!c1Closed) {
                    channel1.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Received: $it")
                        } ?: run {
                            c1Closed = true
                            println("Channel 1 closed")
                        }
                    }
                }

                if (!c2Closed) {
                    channel2.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Received: $it")
                        } ?: run {
                            c2Closed = true
                            println("Channel 2 closed")
                        }
                    }
                }

                if (!c3Closed) {
                    channel3.onReceiveCatching { result ->
                        result.getOrNull()?.let {
                            println("Received: $it")
                        } ?: run {
                            c3Closed = true
                            println("Channel 3 closed")
                        }
                    }
                }
            }
        }

        println("All channels closed, fan-in completed")
    }

    producer1.join()
    producer2.join()
    producer3.join()
    consumer.join()
}
```

#### 6. Production example: parallel image processing

Fan-out workers over a `taskChannel`, fan-in results via `resultChannel`.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.io.File
import java.awt.image.BufferedImage
import javax.imageio.ImageIO

data class ImageTaskEn(
    val inputFile: File,
    val outputFile: File,
    val operations: List<ImageOperationEn>
)

sealed class ImageOperationEn {
    object Resize : ImageOperationEn()
    object Grayscale : ImageOperationEn()
    object Compress : ImageOperationEn()
    data class Watermark(val text: String) : ImageOperationEn()
}

data class ImageResultEn(
    val task: ImageTaskEn,
    val success: Boolean,
    val error: String? = null,
    val processingTimeMs: Long
)

class ImageProcessorEn(
    val numWorkers: Int = Runtime.getRuntime().availableProcessors()
) {
    private val taskChannel = Channel<ImageTaskEn>(Channel.BUFFERED)
    private val resultChannel = Channel<ImageResultEn>(Channel.BUFFERED)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    fun start() {
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
                println("Worker $workerId: processing ${task.inputFile.name}")

                val image = ImageIO.read(task.inputFile)
                requireNotNull(image) { "Failed to read image: ${task.inputFile}" }

                var processedImage = image
                for (operation in task.operations) {
                    processedImage = applyOperation(processedImage, operation)
                }

                ImageIO.write(processedImage, "jpg", task.outputFile)

                val processingTime = System.currentTimeMillis() - startTime
                resultChannel.send(
                    ImageResultEn(task, success = true, processingTimeMs = processingTime)
                )
            } catch (e: Exception) {
                val processingTime = System.currentTimeMillis() - startTime
                resultChannel.send(
                    ImageResultEn(
                        task,
                        success = false,
                        error = e.message,
                        processingTimeMs = processingTime
                    )
                )
            }
        }
    }

    private fun applyOperation(
        image: BufferedImage,
        operation: ImageOperationEn
    ): BufferedImage = when (operation) {
        ImageOperationEn.Resize -> resizeImage(image)
        ImageOperationEn.Grayscale -> convertToGrayscale(image)
        ImageOperationEn.Compress -> image
        is ImageOperationEn.Watermark -> addWatermark(image, operation.text)
    }

    private fun resizeImage(image: BufferedImage): BufferedImage {
        val newWidth = maxOf(1, image.width / 2)
        val newHeight = maxOf(1, image.height / 2)
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
        val watermarked = BufferedImage(image.width, image.height, image.type)
        val graphics = watermarked.createGraphics()
        graphics.drawImage(image, 0, 0, null)
        graphics.drawString(text, 10, 20)
        graphics.dispose()
        return watermarked
    }

    suspend fun submitTask(task: ImageTaskEn) {
        taskChannel.send(task)
    }

    suspend fun submitTasks(tasks: List<ImageTaskEn>) {
        for (t in tasks) submitTask(t)
    }

    suspend fun collectResults(expectedCount: Int): List<ImageResultEn> {
        val results = mutableListOf<ImageResultEn>()
        repeat(expectedCount) {
            results.add(resultChannel.receive())
        }
        return results
    }

    suspend fun shutdown() {
        taskChannel.close()
        scope.coroutineContext[Job]?.join()
        resultChannel.close()
    }
}
```

#### 7. Production example: log aggregation (fan-in)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.time.Instant
import java.time.format.DateTimeFormatter

enum class LogLevelEn { DEBUG, INFO, WARN, ERROR }

data class LogEntryEn(
    val timestamp: Instant,
    val level: LogLevelEn,
    val source: String,
    val message: String,
    val metadata: Map<String, String> = emptyMap()
)

class LogAggregatorEn(
    capacity: Int = Channel.BUFFERED
) {
    private val logChannel = Channel<LogEntryEn>(capacity)
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var aggregatorJob: Job? = null

    fun start() {
        aggregatorJob = scope.launch {
            aggregateLogs()
        }
    }

    private suspend fun aggregateLogs() {
        val logBuffer = mutableListOf<LogEntryEn>()
        val formatter = DateTimeFormatter.ISO_INSTANT

        for (log in logChannel) {
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

            if (logBuffer.size >= 10) {
                flushLogs(logBuffer)
                logBuffer.clear()
            }
        }

        if (logBuffer.isNotEmpty()) {
            flushLogs(logBuffer)
        }
    }

    private fun flushLogs(logs: List<LogEntryEn>) {
        println("Flushing ${logs.size} log entries to persistent storage")
    }

    suspend fun log(entry: LogEntryEn) {
        logChannel.send(entry)
    }

    suspend fun shutdown() {
        logChannel.close()
        aggregatorJob?.join()
    }
}
```

#### 8. Actor pattern for fan-out/fan-in

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class WorkerMessageEn {
    data class ProcessTask(val taskId: Int, val data: String) : WorkerMessageEn()
    object Stop : WorkerMessageEn()
}

sealed class CoordinatorMessageEn {
    data class SubmitWork(val taskId: Int, val data: String) : CoordinatorMessageEn()
    data class WorkComplete(val workerId: Int, val taskId: Int) : CoordinatorMessageEn()
    object Stop : CoordinatorMessageEn()
}

fun CoroutineScope.workerActorEn(
    workerId: Int,
    coordinatorChannel: SendChannel<CoordinatorMessageEn>
) = actor<WorkerMessageEn> {
    for (msg in channel) {
        when (msg) {
            is WorkerMessageEn.ProcessTask -> {
                println("Worker $workerId: processing task ${msg.taskId}")
                delay(100)
                println("Worker $workerId: completed task ${msg.taskId}")
                coordinatorChannel.send(
                    CoordinatorMessageEn.WorkComplete(workerId, msg.taskId)
                )
            }
            WorkerMessageEn.Stop -> {
                println("Worker $workerId: stopping")
                break
            }
        }
    }
}

fun CoroutineScope.coordinatorActorEn(
    numWorkers: Int
) = actor<CoordinatorMessageEn> {
    val workers = List(numWorkers) { workerId ->
        workerActorEn(workerId, this)
    }

    var nextWorkerIndex = 0
    var pendingTasks = 0

    for (msg in channel) {
        when (msg) {
            is CoordinatorMessageEn.SubmitWork -> {
                val worker = workers[nextWorkerIndex]
                worker.send(WorkerMessageEn.ProcessTask(msg.taskId, msg.data))
                nextWorkerIndex = (nextWorkerIndex + 1) % numWorkers
                pendingTasks++
            }

            is CoordinatorMessageEn.WorkComplete -> {
                pendingTasks--
                if (pendingTasks == 0) {
                    println("Coordinator: all tasks completed")
                }
            }

            CoordinatorMessageEn.Stop -> {
                workers.forEach { it.send(WorkerMessageEn.Stop) }
                break
            }
        }
    }
}
```

#### 9. `Flow`-based fan-out/fan-in

- Broadcast fan-out: `shareIn` so each consumer sees all elements.
- Fan-in: `merge` to combine multiple `Flow` sources.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun produceWorkEn(): Flow<Int> = flow {
    repeat(20) {
        println("Producer: emitting work item $it")
        emit(it)
        delay(100)
    }
}

suspend fun flowFanOutExampleEn() = coroutineScope {
    val sharedFlow = produceWorkEn()
        .shareIn(
            scope = this,
            started = SharingStarted.Eagerly,
            replay = 0
        )

    val consumers = List(3) { consumerId ->
        launch {
            sharedFlow.collect { workItem ->
                println("Consumer $consumerId: processing item $workItem")
                delay(200)
                println("Consumer $consumerId: completed item $workItem")
            }
        }
    }

    consumers.forEach { it.join() }
}
```

#### 10. Performance considerations

```kotlin
val bufferedChannelEn = Channel<WorkItemEn>(capacity = Channel.BUFFERED)
val unlimitedChannelEn = Channel<WorkItemEn>(capacity = Channel.UNLIMITED)
val rendezvousChannelEn = Channel<WorkItemEn>(capacity = Channel.RENDEZVOUS)

val numWorkersEn = Runtime.getRuntime().availableProcessors()

val cpuScopeEn = CoroutineScope(Dispatchers.Default)
val ioScopeEn = CoroutineScope(Dispatchers.IO)

fun logChannelStateEn(channel: Channel<*>) {
    println("Channel isEmpty=${channel.isEmpty}, isFull=${channel.isFull}")
}
```

#### 11. Error handling in fan-out/fan-in

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class ResilientWorkQueueEn(private val numWorkers: Int = 4) {
    data class WorkItem(val id: Int, val data: String)
    data class WorkResult(val id: Int, val result: String)

    private val workChannel = Channel<WorkItem>(Channel.BUFFERED)
    private val resultChannel = Channel<Result<WorkResult>>(Channel.BUFFERED)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

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
                println("Worker $workerId: processing ${work.id}")
                if (work.id % 5 == 0) {
                    throw IllegalStateException("Simulated error for work ${work.id}")
                }
                delay(100)
                Result.success(WorkResult(work.id, "Processed by worker $workerId"))
            } catch (e: CancellationException) {
                println("Worker $workerId: cancelled")
                throw e
            } catch (e: Exception) {
                println("Worker $workerId: error processing ${work.id}: ${e.message}")
                Result.failure(e)
            }
            resultChannel.send(result)
        }
    }

    suspend fun submit(work: WorkItem) {
        workChannel.send(work)
    }

    suspend fun collectResults(count: Int): List<Result<WorkResult>> =
        List(count) { resultChannel.receive() }

    suspend fun shutdown() {
        workChannel.close()
        scope.coroutineContext[Job]?.join()
        resultChannel.close()
    }
}
```

#### 12. Testing fan-out/fan-in

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.test.*
import kotlin.test.Test
import kotlin.test.assertEquals

class FanOutFanInTestEn {

    @Test
    fun `fan-out distributes work across workers`() = runTest {
        val workChannel = Channel<Int>()
        val results = Channel<Pair<Int, Int>>()

        val workers = List(3) { workerId ->
            launch {
                for (workItem in workChannel) {
                    results.send(workerId to workItem)
                }
            }
        }

        launch {
            repeat(9) { workChannel.send(it) }
            workChannel.close()
        }

        val collected = mutableListOf<Pair<Int, Int>>()
        repeat(9) {
            collected.add(results.receive())
        }
        results.close()

        workers.forEach { it.join() }

        val workByWorker = collected.groupBy { it.first }
        assertEquals(3, workByWorker.size)
        workByWorker.values.forEach { items ->
            assertEquals(3, items.size)
        }
    }
}
```

#### 13. Production use-case summary

- Fan-out with channels (competitive consumption): task queues, parallel processing.
- Fan-in with channels: aggregation of logs, metrics, results.
- Broadcast fan-out with `shareIn` / `SharedFlow`: deliver each update to all subscribers.
- Fan-in with `merge` over `Flow`: combine several asynchronous sources.
- Actor-based design: encapsulate state and protocols per worker.

#### 14. Common pitfalls

```kotlin
// BAD: forgetting to close the channel
val channelEn = Channel<Int>()
launch {
    repeat(10) { channelEn.send(it) }
    // missing channelEn.close()
}

// GOOD: close after completing production
val channel2En = Channel<Int>()
launch {
    repeat(10) { channel2En.send(it) }
    channel2En.close()
}

// BAD: using Job instead of SupervisorJob for worker pool
val badScopeEn = CoroutineScope(Dispatchers.Default + Job())

// GOOD: SupervisorJob so one worker failure does not cancel all
val goodScopeEn = CoroutineScope(Dispatchers.Default + SupervisorJob())
```

## Follow-ups

### Дополнительные вопросы (RU)
1. Как реализовать priority queue с fan-out паттерном, где задачи с высоким приоритетом обрабатываются первыми?
2. Какие различия в производительности между fan-out на каналах и `shareIn` на `Flow`? Когда выбирать каждый подход?
3. Как реализовать backpressure в fan-out сценарии, когда обработчики медленнее производителя?
4. Как использовать `select` для динамического fan-in из каналов, которые открываются и закрываются в разное время?
5. Как мониторить и отлаживать production-систему fan-out/fan-in? Какие метрики отслеживать?
6. В чем разница между `merge()` и `combine()` для fan-in на `Flow`? Примеры использования.
7. Как организовать graceful shutdown в fan-out системе с ожидающей работой?

### Follow-up Questions (EN)
1. How would you implement a priority queue with fan-out, ensuring high-priority tasks are processed first?
2. What are the performance differences between channel-based fan-out and `shareIn`-based broadcast, and when would you choose each?
3. How do you implement backpressure when producers are faster than consumers in a fan-out scenario?
4. How can `select` be used for dynamic fan-in from channels that open and close at different times?
5. How do you monitor and debug a production fan-out/fan-in system? Which metrics are important?
6. What is the difference between `merge()` and `combine()` for `Flow` fan-in, and when to use each?
7. How do you implement graceful shutdown with in-flight work in a fan-out system?

## References

### Ссылки (RU)
- [[c-kotlin]]
- [[c-coroutines]]
- [[c-flow]]
- Руководство Kotlin Coroutines — Channels: https://kotlinlang.org/docs/channels.html
- Документация Kotlin `Flow`: https://kotlinlang.org/docs/flow.html
- Select expression: https://kotlinlang.org/docs/select-expression.html

### References (EN)
- [[c-kotlin]]
- [[c-coroutines]]
- [[c-flow]]
- Kotlin Coroutines Guide — Channels: https://kotlinlang.org/docs/channels.html
- Kotlin `Flow` documentation: https://kotlinlang.org/docs/flow.html
- Select expression: https://kotlinlang.org/docs/select-expression.html

## Related Questions
- [[q-actor-pattern--kotlin--hard]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-android-async-primitives--android--easy]]

---
'---id': kotlin-060
title: Channel Pipelines in Kotlin / Конвейеры каналов в Kotlin
aliases:
- Channel Pipelines in Kotlin
- Конвейеры каналов в Kotlin
topic: kotlin
subtopics:
- channels
- coroutines
- pipelines
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
source: internal
source_note: Created for vault completeness
status: draft
moc: moc-kotlin
related:
- c-coroutines
- c-kotlin
- c-kotlin-coroutines-basics
- c-stateflow
- q-flow-backpressure-strategies--kotlin--hard
- q-kotlin-channels--kotlin--medium
- q-produce-actor-builders--kotlin--medium
- q-structured-concurrency-kotlin--kotlin--medium
created: 2025-10-12
updated: 2025-11-09
tags:
- backpressure
- channels
- coroutines
- difficulty/hard
- fan-in
- fan-out
- kotlin
- pipelines
anki_cards:
- slug: q-channel-pipelines--kotlin--hard-0-en
  language: en
  difficulty: 0.7
  tags:
  - Kotlin
  - difficulty::hard
  - channels
  - coroutines
  - pipelines
- slug: q-channel-pipelines--kotlin--hard-0-ru
  language: ru
  difficulty: 0.7
  tags:
  - Kotlin
  - difficulty::hard
  - channels
  - coroutines
  - pipelines
---
# Вопрос (RU)
> Объясните конвейеры каналов в корутинах Kotlin. Как реализовать паттерны производитель-потребитель, fan-out, fan-in и стратегии буферизации? Приведите примеры реальных архитектур конвейеров.

---

# Question (EN)
> Explain channel pipelines in Kotlin coroutines. How do you implement producer-consumer patterns, fan-out, fan-in, and buffering strategies? Provide examples of real-world pipeline architectures.

## Ответ (RU)

Конвейеры каналов - это мощный паттерн для построения систем конкурентной обработки данных, где корутины производят, трансформируют и потребляют данные через серию соединенных каналов. Этот паттерн основан на фундаментальных принципах [[c-kotlin-coroutines-basics|корутин Kotlin]].

### Основные Концепции

Конвейер состоит из:
- **Производителей**: Корутины, генерирующие данные и отправляющие в каналы
- **Процессоров**: Корутины, получающие данные, трансформирующие и отправляющие на следующий этап
- **Потребителей**: Корутины, получающие и обрабатывающие финальные данные
- **Каналов**: Примитивы коммуникации, соединяющие этапы

```kotlin
// Базовая структура конвейера
Producer -> Channel -> Processor -> Channel -> Consumer
```

### Простой Пример Конвейера

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Этап 1: Производитель - генерирует числа
fun CoroutineScope.produceNumbers(): ReceiveChannel<Int> = produce {
    var x = 1
    while (isActive) { // уважать отмену родителя
        send(x++)  // Потенциально бесконечный поток
        delay(100)
    }
}

// Этап 2: Процессор - возводит числа в квадрат
fun CoroutineScope.squareNumbers(numbers: ReceiveChannel<Int>): ReceiveChannel<Int> = produce {
    for (x in numbers) {
        send(x * x)
    }
}

// Этап 3: Потребитель - выводит результаты
suspend fun consumeNumbers(squares: ReceiveChannel<Int>) {
    for (square in squares) {
        println("Результат: $square")
    }
}

// Построение и запуск конвейера
fun main() = runBlocking {
    val numbers = produceNumbers()
    val squares = squareNumbers(numbers)

    repeat(10) {
        println(squares.receive())
    }

    // Корректно останавливаем конвейер
    coroutineContext.cancelChildren()
}
```

### Многостадийный Конвейер С Обработкой Ошибок

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class RawData(val id: Int, val value: String)
data class ParsedData(val id: Int, val number: Int)
data class ProcessedData(val id: Int, val result: Int)

class DataPipeline(private val scope: CoroutineScope) {

    // Этап 1: Источник данных
    private fun produceRawData(): ReceiveChannel<RawData> = scope.produce(capacity = 10) {
        var id = 0
        while (isActive) {
            send(RawData(id++, "Value-${(0..100).random()}"))
            delay(50)
        }
    }

    // Этап 2: Парсер с обработкой ошибок
    private fun parseData(input: ReceiveChannel<RawData>): ReceiveChannel<ParsedData?> =
        scope.produce(capacity = 10) {
            for (raw in input) {
                try {
                    val number = raw.value.substringAfter("-").toInt()
                    send(ParsedData(raw.id, number))
                } catch (e: NumberFormatException) {
                    println("Ошибка парсинга для ${raw.id}: ${e.message}")
                    send(null)  // Маркер ошибки
                }
            }
        }

    // Этап 3: Фильтрация валидных данных
    private fun filterValid(input: ReceiveChannel<ParsedData?>): ReceiveChannel<ParsedData> =
        scope.produce(capacity = 10) {
            for (data in input) {
                if (data != null) {
                    send(data)
                }
            }
        }

    // Этап 4: Обработка данных (дорогая операция)
    private fun processData(input: ReceiveChannel<ParsedData>): ReceiveChannel<ProcessedData> =
        scope.produce(capacity = 5) {
            for (parsed in input) {
                delay(200)  // Эмуляция тяжелых вычислений
                val result = parsed.number * parsed.number
                send(ProcessedData(parsed.id, result))
            }
        }

    // Построение полного конвейера
    fun start(): ReceiveChannel<ProcessedData> {
        val raw = produceRawData()
        val parsed = parseData(raw)
        val filtered = filterValid(parsed)
        return processData(filtered)
    }
}

// Использование
fun main() = runBlocking {
    val pipeline = DataPipeline(this)
    val output = pipeline.start()

    // Потребляем результаты 5 секунд
    val job = launch {
        for (result in output) {
            println("Итоговый результат: ${result.id} -> ${result.result}")
        }
    }

    delay(5000)
    job.cancel() // отменяет конвейер через структурированную конкурентность
}
```

### Fan-Out: Множественные Потребители От Одного Канала

Fan-out распределяет работу от одного производителя нескольким потребителям для параллельной обработки.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class FanOutProcessor {

    fun CoroutineScope.produceJobs(): ReceiveChannel<Int> = produce(capacity = 100) {
        repeat(100) { jobId ->
            send(jobId)
        }
        // produce сам закроет канал по завершении блока
    }

    suspend fun worker(id: Int, jobs: ReceiveChannel<Int>) {
        for (job in jobs) {
            println("Работник $id обрабатывает задачу $job")
            delay(100)
            println("Работник $id завершил задачу $job")
        }
        println("Работник $id закончил")
    }

    fun runFanOut() = runBlocking {
        val jobs = produceJobs()

        // Запуск нескольких работников, использующих один канал
        val workers = List(5) { workerId ->
            launch { worker(workerId, jobs) }
        }

        workers.forEach { it.join() }
        println("Вся работа завершена")
    }
}
```

### Fan-Out С Балансировкой Нагрузки

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class LoadBalancedProcessor {

    data class Task(val id: Int, val complexity: Int)
    data class Result(val taskId: Int, val result: String, val workerId: Int)

    fun CoroutineScope.produceTasks(): ReceiveChannel<Task> = produce {
        repeat(50) { id ->
            val complexity = (1..5).random()
            send(Task(id, complexity))
        }
    }

    suspend fun worker(
        id: Int,
        tasks: ReceiveChannel<Task>,
        results: SendChannel<Result>
    ) {
        for (task in tasks) {
            val processingTime = task.complexity * 100L
            delay(processingTime)
            results.send(Result(task.id, "Обработано работником $id", id))
        }
    }

    fun run() = runBlocking {
        val tasks = produceTasks()
        val results = Channel<Result>(capacity = 50)

        // Пул работников
        val workers = List(4) { workerId ->
            launch { worker(workerId, tasks, results) }
        }

        // Сбор результатов
        val collector = launch {
            var completed = 0
            for (result in results) {
                println("Задача ${result.taskId}: ${result.result}")
                completed++
                if (completed == 50) break
            }
        }

        workers.forEach { it.join() }
        results.close()
        collector.join()
    }
}
```

### Fan-In: Множественные Производители В Один Канал

Fan-in объединяет вывод от нескольких производителей в один канал.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class FanInProcessor {

    fun CoroutineScope.dataSource(
        id: Int,
        output: SendChannel<String>
    ) = launch {
        repeat(5) { index ->
            delay(100L * id)  // Разная скорость
            output.send("Источник-$id: Сообщение-$index")
        }
    }

    fun runFanIn() = runBlocking {
        val channel = Channel<String>(capacity = 20)

        // Запуск нескольких производителей
        val producers = List(3) { sourceId ->
            dataSource(sourceId, channel)
        }

        producers.forEach { it.join() }
        channel.close()

        // Потребление объединенного потока
        for (message in channel) {
            println("Получено: $message")
        }
    }
}
```

### Fan-In С `PriorityQueue`

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class PriorityFanIn {

    data class PriorityMessage(val priority: Int, val content: String) : Comparable<PriorityMessage> {
        override fun compareTo(other: PriorityMessage) = other.priority.compareTo(priority)
    }

    fun CoroutineScope.prioritySource(
        id: Int,
        output: SendChannel<PriorityMessage>
    ) = launch {
        repeat(10) { index ->
            val priority = (1..5).random()
            delay((50..150).random().toLong())
            output.send(PriorityMessage(priority, "Источник-$id-Сообщение-$index"))
        }
    }

    fun run() = runBlocking {
        val rawChannel = Channel<PriorityMessage>(capacity = 50)

        // Запуск нескольких источников
        val sources = List(3) { sourceId ->
            prioritySource(sourceId, rawChannel)
        }

        // Потребитель, собирающий в очередь с приоритетом
        val priorityQueue = java.util.PriorityQueue<PriorityMessage>()
        val consumer = launch {
            for (message in rawChannel) {
                priorityQueue.offer(message)
            }
        }

        sources.forEach { it.join() }
        rawChannel.close()
        consumer.join()

        // Обработка по приоритету
        while (priorityQueue.isNotEmpty()) {
            val msg = priorityQueue.poll()
            println("Приоритет ${msg.priority}: ${msg.content}")
        }
    }
}
```

### Стратегии Буферизации

Различные конфигурации буфера влияют на поведение и производительность конвейера:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class BufferingStrategies {

    // 1. Rendezvous (без буфера) - строгая синхронизация
    fun rendezvousChannel() = runBlocking {
        val channel = Channel<Int>(capacity = Channel.RENDEZVOUS)

        launch {
            repeat(5) { i ->
                println("Отправка $i")
                channel.send(i)  // Приостанавливается пока получатель не готов
                println("Отправлено $i")
            }
            channel.close()
        }

        delay(1000)
        for (value in channel) {
            println("Получено $value")
            delay(300)
        }
    }

    // 2. Буферизованный канал - позволяет более асинхронное производство
    fun bufferedChannel() = runBlocking {
        val channel = Channel<Int>(capacity = 5)

        launch {
            repeat(10) { i ->
                println("Отправка $i")
                channel.send(i)  // Приостанавливается только когда буфер полон
                println("Отправлено $i")
            }
            channel.close()
        }

        delay(1000)  // Первые элементы могут быть отправлены до начала потребления
        for (value in channel) {
            println("Получено $value")
            delay(300)
        }
    }

    // 3. Неограниченный буфер - отправитель почти никогда не приостанавливается (риск OOM)
    fun unlimitedChannel() = runBlocking {
        val channel = Channel<Int>(capacity = Channel.UNLIMITED)

        launch {
            repeat(1000) { i ->
                channel.send(i)
            }
            channel.close()
        }

        delay(100)
        var count = 0
        for (value in channel) {
            count++
        }
        println("Получено $count элементов")
    }

    // 4. Conflated channel - хранит только последнее значение (медленный потребитель теряет промежуточные)
    fun conflatedChannel() = runBlocking {
        val channel = Channel<Int>(capacity = Channel.CONFLATED)

        launch {
            repeat(10) { i ->
                println("Отправка $i")
                channel.send(i)  // Перезаписывает предыдущее значение при переполнении
                delay(50)
            }
            channel.close()
        }

        delay(1000)
        for (value in channel) {
            // При медленном потребителе многие промежуточные значения будут отброшены
            println("Получено $value")
        }
    }
}
```

### Реальный Пример: Обработка Изображений

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.io.File
import java.awt.image.BufferedImage
import javax.imageio.ImageIO

class ImageProcessingPipeline(private val scope: CoroutineScope) {

    data class ImageTask(val file: File)
    data class LoadedImage(val file: File, val image: BufferedImage)
    data class ProcessedImage(val file: File, val image: BufferedImage)

    // Этап 1: Сканирование директории
    private fun scanImages(directory: File): ReceiveChannel<ImageTask> = scope.produce {
        directory.listFiles { file ->
            file.extension.lowercase() in listOf("jpg", "jpeg", "png")
        }?.forEach { file ->
            send(ImageTask(file))
        }
        // produce закроет канал по завершении
    }

    // Этап 2: Загрузка изображений (I/O bound - можно распараллелить)
    // Реализуем fan-out с общим выходным каналом и корректным завершением.
    private fun loadImages(
        tasks: ReceiveChannel<ImageTask>,
        parallelism: Int
    ): ReceiveChannel<LoadedImage> {
        val output = Channel<LoadedImage>(capacity = 10)

        val workers = List(parallelism) { workerId ->
            scope.launch {
                for (task in tasks) {
                    try {
                        val image = ImageIO.read(task.file)
                        output.send(LoadedImage(task.file, image))
                        println("Работник $workerId загрузил ${task.file.name}")
                    } catch (e: Exception) {
                        println("Не удалось загрузить ${task.file.name}: ${e.message}")
                    }
                }
            }
        }

        scope.launch {
            // Ждем завершения всех workers, затем закрываем выходной канал
            workers.forEach { it.join() }
            output.close()
        }

        return output
    }

    // Этап 3: Применение фильтров (CPU bound - ограничить параллелизм)
    private fun applyFilters(
        images: ReceiveChannel<LoadedImage>,
        parallelism: Int
    ): ReceiveChannel<ProcessedImage> {
        val output = Channel<ProcessedImage>(capacity = 5)

        val workers = List(parallelism) { workerId ->
            scope.launch {
                for (loaded in images) {
                    val processed = applyGrayscaleFilter(loaded.image)
                    output.send(ProcessedImage(loaded.file, processed))
                    println("Работник $workerId обработал ${loaded.file.name}")
                }
            }
        }

        scope.launch {
            // Ждем завершения всех workers, затем закрываем выходной канал
            workers.forEach { it.join() }
            output.close()
        }

        return output
    }

    private suspend fun applyGrayscaleFilter(image: BufferedImage): BufferedImage {
        // Заглушка для CPU-интенсивной операции; используем delay вместо Thread.sleep
        delay(100)
        return image
    }

    // Этап 4: Сохранение результатов (I/O bound)
    private fun saveImages(
        images: ReceiveChannel<ProcessedImage>,
        outputDir: File,
        parallelism: Int
    ) = scope.launch {
        outputDir.mkdirs()
        val workers = List(parallelism) { workerId ->
            launch {
                for (processed in images) {
                    val outputFile = File(outputDir, "processed_${processed.file.name}")
                    ImageIO.write(processed.image, "jpg", outputFile)
                    println("Работник $workerId сохранил ${outputFile.name}")
                }
            }
        }
        workers.forEach { it.join() }
    }

    // Построение и выполнение конвейера
    suspend fun process(inputDir: File, outputDir: File) {
        val tasks = scanImages(inputDir)
        val loaded = loadImages(tasks, parallelism = 4)  // I/O bound fan-out
        val processed = applyFilters(loaded, parallelism = 2)  // CPU bound fan-out

        saveImages(processed, outputDir, parallelism = 2).join()
        println("Конвейер завершен")
    }
}
```

### Реальный Пример: Конвейер ETL (Data ETL)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class ETLPipeline(private val scope: CoroutineScope) {

    data class RawRecord(val id: Long, val data: Map<String, String>)
    data class TransformedRecord(val id: Long, val normalized: Map<String, Any>)
    data class ValidatedRecord(val record: TransformedRecord, val valid: Boolean, val errors: List<String>)

    // Extract: чтение из источника данных
    private fun extract(): ReceiveChannel<RawRecord> = scope.produce(capacity = 100) {
        var id = 0L
        while (id < 10000 && isActive) {
            send(
                RawRecord(
                    id,
                    mapOf(
                        "name" to "User$id",
                        "age" to "${(18..80).random()}",
                        "email" to "user$id@example.com"
                    )
                )
            )
            id++
            if (id % 100 == 0L) delay(10)
        }
    }

    // Transform: нормализация и преобразование данных с корректным завершением
    private fun transform(
        input: ReceiveChannel<RawRecord>,
        parallelism: Int
    ): ReceiveChannel<TransformedRecord> {
        val output = Channel<TransformedRecord>(capacity = 100)
        val workerJobs = List(parallelism) {
            scope.launch {
                for (raw in input) {
                    val normalized = raw.data.mapValues { (key, value) ->
                        when (key) {
                            "age" -> value.toIntOrNull() ?: 0
                            "email" -> value.lowercase()
                            else -> value
                        }
                    }
                    output.send(TransformedRecord(raw.id, normalized))
                }
            }
        }

        scope.launch {
            workerJobs.forEach { it.join() }
            output.close()
        }

        return output
    }

    // Validate: проверка качества данных с корректным завершением
    private fun validate(
        input: ReceiveChannel<TransformedRecord>,
        parallelism: Int
    ): ReceiveChannel<ValidatedRecord> {
        val output = Channel<ValidatedRecord>(capacity = 100)
        val workerJobs = List(parallelism) {
            scope.launch {
                for (record in input) {
                    val errors = mutableListOf<String>()

                    val age = record.normalized["age"] as? Int
                    if (age == null || age < 0 || age > 150) {
                        errors.add("Некорректный возраст: $age")
                    }

                    val email = record.normalized["email"] as? String
                    if (email == null || !email.contains("@")) {
                        errors.add("Некорректный email: $email")
                    }

                    output.send(ValidatedRecord(record, errors.isEmpty(), errors))
                }
            }
        }

        scope.launch {
            workerJobs.forEach { it.join() }
            output.close()
        }

        return output
    }

    // Load: запись в целевую систему (с пакетированием)
    private fun load(
        input: ReceiveChannel<ValidatedRecord>,
        batchSize: Int
    ) = scope.launch {
        val batch = mutableListOf<ValidatedRecord>()
        var validCount = 0
        var invalidCount = 0

        for (validated in input) {
            if (validated.valid) {
                batch.add(validated)
                validCount++

                if (batch.size >= batchSize) {
                    writeBatch(batch)
                    batch.clear()
                }
            } else {
                invalidCount++
                println("Некорректная запись ${validated.record.id}: ${validated.errors}")
            }
        }

        if (batch.isNotEmpty()) {
            writeBatch(batch)
        }

        println("ETL завершен: $validCount валидных, $invalidCount невалидных записей")
    }

    private suspend fun writeBatch(batch: List<ValidatedRecord>) {
        delay(50)  // Имитация записи в базу
        println("Записан батч из ${batch.size} записей")
    }

    // Запуск полного конвейера
    suspend fun run() {
        val raw = extract()
        val transformed = transform(raw, parallelism = 4)
        val validated = validate(transformed, parallelism = 4)
        load(validated, batchSize = 100).join()
    }
}
```

### Управление Противодавлением (Backpressure)

Управление скоростью, когда производители быстрее потребителей:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.channels.BufferOverflow

class BackpressureExample {

    // Стратегия 1: Ограниченный буфер с приостановкой
    fun boundedBufferStrategy() = runBlocking {
        val channel = Channel<Int>(capacity = 10)

        val producer = launch {
            repeat(100) { i ->
                println("Производим $i")
                channel.send(i)  // Приостанавливается, когда буфер полон
                println("Произведено $i")
            }
            channel.close()
        }

        val consumer = launch {
            for (value in channel) {
                println("  Потребление $value")
                delay(100)  // Медленный потребитель
            }
        }

        joinAll(producer, consumer)
    }

    // Стратегия 2: Удаление самого старого (минимизация приостановки ценой потери данных)
    fun dropOldestStrategy() = runBlocking {
        val channel = Channel<Int>(
            capacity = 1,
            onBufferOverflow = BufferOverflow.DROP_OLDEST
        )

        val producer = launch {
            repeat(100) { i ->
                channel.send(i)
                delay(10)
            }
            channel.close()
        }

        val consumer = launch {
            for (value in channel) {
                println("Получено: $value")
                delay(100)
            }
        }

        joinAll(producer, consumer)
    }

    // Стратегия 3: Семплирование - обработка каждого N-го элемента
    fun samplingStrategy() = runBlocking {
        val channel = Channel<Int>(capacity = Channel.UNLIMITED)

        val producer = launch {
            repeat(1000) { i ->
                channel.send(i)
            }
            channel.close()
        }

        val consumer = launch {
            var count = 0
            for (value in channel) {
                count++
                if (count % 10 == 0) {  // Обрабатываем каждый 10-й элемент
                    println("Обработка: $value")
                    delay(50)
                }
            }
        }

        joinAll(producer, consumer)
    }
}
```

### Мониторинг Конвейера И Метрики

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class MonitoredPipeline(private val scope: CoroutineScope) {

    data class PipelineMetrics(
        var itemsProcessed: Long = 0,
        var itemsFailed: Long = 0,
        var totalProcessingTime: Long = 0,
        val startTime: Long = System.currentTimeMillis()
    ) {
        val averageProcessingTime: Long
            get() = if (itemsProcessed > 0) totalProcessingTime / itemsProcessed else 0

        val throughput: Double
            get() = itemsProcessed.toDouble() /
                ((System.currentTimeMillis() - startTime).coerceAtLeast(1) / 1000.0)

        fun printStats() {
            println(
                """
                Статистика конвейера:
                - Обработано элементов: $itemsProcessed
                - Ошибок: $itemsFailed
                - Среднее время: ${averageProcessingTime}мс
                - Пропускная способность: ${"%.2f".format(throughput)} эл/с
                - Время работы: ${(System.currentTimeMillis() - startTime) / 1000}с
                """.trimIndent()
            )
        }
    }

    private val metrics = PipelineMetrics()

    private fun produceWithMetrics(): ReceiveChannel<Int> = scope.produce {
        repeat(1000) { i ->
            send(i)
            delay(10)
        }
    }

    private fun processWithMetrics(
        input: ReceiveChannel<Int>
    ): ReceiveChannel<Int> = scope.produce {
        for (item in input) {
            val startTime = System.nanoTime()
            try {
                delay(50)  // Эмуляция обработки
                send(item * 2)

                metrics.itemsProcessed++
                metrics.totalProcessingTime += (System.nanoTime() - startTime) / 1_000_000
            } catch (e: Exception) {
                metrics.itemsFailed++
            }
        }
    }

    suspend fun run() {
        val input = produceWithMetrics()
        val output = processWithMetrics(input)

        // Периодический вывод статистики
        val monitor = scope.launch {
            while (isActive) {
                delay(1000)
                metrics.printStats()
            }
        }

        // Потребление результатов
        for (result in output) {
            // Обработка результата при необходимости
        }

        monitor.cancel()
        metrics.printStats()
    }
}
```

### Лучшие Практики

1. **Выбирайте подходящие размеры буфера**:
```kotlin
// Небольшой буфер для памятиёмких данных
val imageChannel = Channel<BufferedImage>(capacity = 5)

// Большой буфер для лёгких данных
val numberChannel = Channel<Int>(capacity = 1000)

// Rendezvous для строгой передачи
val syncChannel = Channel<String>(capacity = Channel.RENDEZVOUS)
```

2. **Правильно обрабатывайте отмену**:
```kotlin
fun CoroutineScope.robustProducer(): ReceiveChannel<Int> = produce {
    try {
        repeat(1000) { i ->
            send(i)
            if (!isActive) return@produce
        }
    } finally {
        println("Очистка производителя")
    }
}
```

3. **Используйте структурированную конкурентность**:
```kotlin
suspend fun reliablePipeline() = coroutineScope {
    val channel1 = produceData()
    val channel2 = processData(channel1)
    val channel3 = transformData(channel2)

    // Все корутины будут отменены, если какая-то упадёт
    consumeData(channel3)
}
```

4. **Мониторьте состояние каналов для диагностики** (но не полагайтесь на это для строгой корректности):
```kotlin
fun monitorChannelHealth(channel: Channel<Int>) {
    println("Channel isEmpty: ${channel.isEmpty}")
    println("Channel isFull: ${channel.isFull}")
}
```

5. **Реализуйте корректную обработку ошибок**:
```kotlin
fun CoroutineScope.safeProcessor(
    input: ReceiveChannel<Int>
): ReceiveChannel<Result<Int>> = produce {
    for (item in input) {
        try {
            val result = processItem(item)
            send(Result.success(result))
        } catch (e: Exception) {
            send(Result.failure(e))
        }
    }
}
```

### Распространенные Ошибки

1. **Неограниченные каналы, вызывающие OOM**:
```kotlin
// Плохо - может съесть всю память
val channel = Channel<Data>(capacity = Channel.UNLIMITED)

// Лучше - ограниченный буфер
val bounded = Channel<Data>(capacity = 100)
```

2. **Незакрытые каналы или несогласованное завершение стадий**:
```kotlin
// Плохо - потребитель может ждать бесконечно
fun producer(): ReceiveChannel<Int> = Channel<Int>().apply {
    GlobalScope.launch {
        send(1)
        // Забыли закрыть, нет структурированного родителя
    }
}

// Лучше - использовать builder produce в корректном scope
fun CoroutineScope.producer() = produce {
    send(1)
}  // Канал закроется по завершении блока
```

3. **Блокирующие операции внутри конвейера**:
```kotlin
// Плохо - блокирует поток корутины
fun processSync(item: Int): Int {
    Thread.sleep(100)
    return item * 2
}

// Хорошо - приостановка вместо блокировки
suspend fun processAsync(item: Int): Int {
    delay(100)
    return item * 2
}
```

---

## Answer (EN)

Channel pipelines are a powerful pattern for building concurrent data processing systems where coroutines produce, transform, and consume data through a series of connected channels. This pattern is built on the fundamental concepts of [[c-kotlin-coroutines-basics|Kotlin coroutines]] and enables efficient parallel processing, load distribution, and resource management.

### Core Concepts

A pipeline consists of:
- **Producers**: Coroutines that generate data and send it to channels
- **Processors**: Coroutines that receive data, transform it, and send to next stage
- **Consumers**: Coroutines that receive and process final data
- **Channels**: Communication primitives connecting stages

```kotlin
// Basic pipeline structure
Producer -> Channel -> Processor -> Channel -> Consumer
```

### Simple Pipeline Example

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Stage 1: Producer - generates numbers
fun CoroutineScope.produceNumbers(): ReceiveChannel<Int> = produce {
    var x = 1
    while (isActive) { // honor cancellation
        send(x++)  // Potentially infinite stream
        delay(100)  // Simulate work
    }
}

// Stage 2: Processor - squares numbers
fun CoroutineScope.squareNumbers(numbers: ReceiveChannel<Int>): ReceiveChannel<Int> = produce {
    for (x in numbers) {
        send(x * x)
    }
}

// Stage 3: Consumer - prints results
suspend fun consumeNumbers(squares: ReceiveChannel<Int>) {
    for (square in squares) {
        println("Result: $square")
    }
}

// Building and running the pipeline
fun main() = runBlocking {
    val numbers = produceNumbers()
    val squares = squareNumbers(numbers)

    // Process first 10 results
    repeat(10) {
        println(squares.receive())
    }

    // Cancel pipeline
    coroutineContext.cancelChildren()
}
```

### Multi-Stage Pipeline with Error Handling

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class RawData(val id: Int, val value: String)
data class ParsedData(val id: Int, val number: Int)
data class ProcessedData(val id: Int, val result: Int)

class DataPipeline(private val scope: CoroutineScope) {

    // Stage 1: Data source
    private fun produceRawData(): ReceiveChannel<RawData> = scope.produce(capacity = 10) {
        var id = 0
        while (isActive) {
            send(RawData(id++, "Value-${(0..100).random()}"))
            delay(50)
        }
    }

    // Stage 2: Parser with error handling
    private fun parseData(input: ReceiveChannel<RawData>): ReceiveChannel<ParsedData?> =
        scope.produce(capacity = 10) {
            for (raw in input) {
                try {
                    val number = raw.value.substringAfter("-").toInt()
                    send(ParsedData(raw.id, number))
                } catch (e: NumberFormatException) {
                    println("Parse error for ${raw.id}: ${e.message}")
                    send(null)  // Error marker
                }
            }
        }

    // Stage 3: Filter out errors
    private fun filterValid(input: ReceiveChannel<ParsedData?>): ReceiveChannel<ParsedData> =
        scope.produce(capacity = 10) {
            for (data in input) {
                if (data != null) {
                    send(data)
                }
            }
        }

    // Stage 4: Process data (expensive operation)
    private fun processData(input: ReceiveChannel<ParsedData>): ReceiveChannel<ProcessedData> =
        scope.produce(capacity = 5) {
            for (parsed in input) {
                delay(200)  // Simulate expensive computation
                val result = parsed.number * parsed.number
                send(ProcessedData(parsed.id, result))
            }
        }

    // Build complete pipeline
    fun start(): ReceiveChannel<ProcessedData> {
        val raw = produceRawData()
        val parsed = parseData(raw)
        val filtered = filterValid(parsed)
        return processData(filtered)
    }
}

// Usage
fun main() = runBlocking {
    val pipeline = DataPipeline(this)
    val output = pipeline.start()

    // Consume for 5 seconds
    val job = launch {
        for (result in output) {
            println("Final result: ${result.id} -> ${result.result}")
        }
    }

    delay(5000)
    job.cancel() // cancels the pipeline via structured concurrency
}
```

### Fan-Out: Multiple Consumers Processing from Single Channel

Fan-out distributes work from one producer to multiple consumers for parallel processing.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Fan-out pattern: Multiple workers consuming from one channel
class FanOutProcessor {

    fun CoroutineScope.produceJobs(): ReceiveChannel<Int> = produce(capacity = 100) {
        repeat(100) { jobId ->
            send(jobId)
        }
        // Channel is closed automatically when `produce` block completes
    }

    suspend fun worker(id: Int, jobs: ReceiveChannel<Int>) {
        for (job in jobs) {
            println("Worker $id processing job $job")
            delay(100)  // Simulate work
            println("Worker $id completed job $job")
        }
        println("Worker $id finished")
    }

    fun runFanOut() = runBlocking {
        val jobs = produceJobs()

        // Start multiple workers sharing the same channel
        val workers = List(5) { workerId ->
            launch { worker(workerId, jobs) }
        }

        workers.forEach { it.join() }
        println("All work completed")
    }
}
```

### Fan-Out with Load Balancing

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class LoadBalancedProcessor {

    data class Task(val id: Int, val complexity: Int)
    data class Result(val taskId: Int, val result: String, val workerId: Int)

    fun CoroutineScope.produceTasks(): ReceiveChannel<Task> = produce {
        repeat(50) { id ->
            val complexity = (1..5).random()
            send(Task(id, complexity))
        }
    }

    suspend fun worker(
        id: Int,
        tasks: ReceiveChannel<Task>,
        results: SendChannel<Result>
    ) {
        for (task in tasks) {
            val processingTime = task.complexity * 100L
            delay(processingTime)
            results.send(Result(task.id, "Processed by worker $id", id))
        }
    }

    fun run() = runBlocking {
        val tasks = produceTasks()
        val results = Channel<Result>(capacity = 50)

        // Start worker pool
        val workers = List(4) { workerId ->
            launch { worker(workerId, tasks, results) }
        }

        // Collect results
        val collector = launch {
            var completed = 0
            for (result in results) {
                println("Task ${result.taskId}: ${result.result}")
                completed++
                if (completed == 50) break
            }
        }

        workers.forEach { it.join() }
        results.close()
        collector.join()
    }
}
```

### Fan-In: Multiple Producers Sending to Single Channel

Fan-in combines output from multiple producers into a single channel.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class FanInProcessor {

    fun CoroutineScope.dataSource(
        id: Int,
        output: SendChannel<String>
    ) = launch {
        repeat(5) { index ->
            delay(100L * id)  // Different rates
            output.send("Source-$id: Message-$index")
        }
    }

    fun runFanIn() = runBlocking {
        val channel = Channel<String>(capacity = 20)

        // Start multiple producers
        val producers = List(3) { sourceId ->
            dataSource(sourceId, channel)
        }

        // Wait for all producers
        producers.forEach { it.join() }
        channel.close()

        // Consume merged stream
        for (message in channel) {
            println("Received: $message")
        }
    }
}
```

### Fan-In with `PriorityQueue`

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class PriorityFanIn {

    data class PriorityMessage(val priority: Int, val content: String) : Comparable<PriorityMessage> {
        override fun compareTo(other: PriorityMessage) = other.priority.compareTo(priority)
    }

    fun CoroutineScope.prioritySource(
        id: Int,
        output: SendChannel<PriorityMessage>
    ) = launch {
        repeat(10) { index ->
            val priority = (1..5).random()
            delay((50..150).random().toLong())
            output.send(PriorityMessage(priority, "Source-$id-Msg-$index"))
        }
    }

    fun run() = runBlocking {
        val rawChannel = Channel<PriorityMessage>(capacity = 50)

        // Start multiple sources
        val sources = List(3) { sourceId ->
            prioritySource(sourceId, rawChannel)
        }

        // Priority queue consumer
        val priorityQueue = java.util.PriorityQueue<PriorityMessage>()
        val consumer = launch {
            for (message in rawChannel) {
                priorityQueue.offer(message)
            }
        }

        sources.forEach { it.join() }
        rawChannel.close()
        consumer.join()

        // Process by priority
        while (priorityQueue.isNotEmpty()) {
            val msg = priorityQueue.poll()
            println("Priority ${msg.priority}: ${msg.content}")
        }
    }
}
```

### Buffering Strategies

Different buffer configurations affect pipeline behavior and performance:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class BufferingStrategies {

    // 1. Rendezvous (no buffer) - strict synchronization
    fun rendezvousChannel() = runBlocking {
        val channel = Channel<Int>(capacity = Channel.RENDEZVOUS)  // capacity = 0

        launch {
            repeat(5) { i ->
                println("Sending $i")
                channel.send(i)  // Suspends until receiver ready
                println("Sent $i")
            }
            channel.close()
        }

        delay(1000)  // Sender waits
        for (value in channel) {
            println("Received $value")
            delay(300)
        }
    }

    // 2. Buffered channel - allows more async production
    fun bufferedChannel() = runBlocking {
        val channel = Channel<Int>(capacity = 5)

        launch {
            repeat(10) { i ->
                println("Sending $i")
                channel.send(i)  // Suspends only when buffer full
                println("Sent $i")
            }
            channel.close()
        }

        delay(1000)  // First elements can be sent before consumer starts
        for (value in channel) {
            println("Received $value")
            delay(300)
        }
    }

    // 3. Unlimited buffer - sender almost never suspends (risk of OOM)
    fun unlimitedChannel() = runBlocking {
        val channel = Channel<Int>(capacity = Channel.UNLIMITED)

        launch {
            repeat(1000) { i ->
                channel.send(i)
            }
            channel.close()
        }

        delay(100)
        var count = 0
        for (value in channel) {
            count++
        }
        println("Received $count items")
    }

    // 4. Conflated channel - keeps only latest value when consumer is slow
    fun conflatedChannel() = runBlocking {
        val channel = Channel<Int>(capacity = Channel.CONFLATED)

        launch {
            repeat(10) { i ->
                println("Sending $i")
                channel.send(i)  // Overwrites previous value when needed
                delay(50)
            }
            channel.close()
        }

        delay(1000)  // Many intermediate values will be dropped for slow consumer
        for (value in channel) {
            println("Received $value")
        }
    }
}
```

### Real-World Pipeline: Image Processing

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import java.io.File
import java.awt.image.BufferedImage
import javax.imageio.ImageIO

class ImageProcessingPipeline(private val scope: CoroutineScope) {

    data class ImageTask(val file: File)
    data class LoadedImage(val file: File, val image: BufferedImage)
    data class ProcessedImage(val file: File, val image: BufferedImage)

    // Stage 1: Scan directory for images
    private fun scanImages(directory: File): ReceiveChannel<ImageTask> = scope.produce {
        directory.listFiles { file ->
            file.extension.lowercase() in listOf("jpg", "jpeg", "png")
        }?.forEach { file ->
            send(ImageTask(file))
        }
        // Channel closed when produce block completes
    }

    // Stage 2: Load images (I/O bound - fan-out with shared output channel)
    private fun loadImages(
        tasks: ReceiveChannel<ImageTask>,
        parallelism: Int
    ): ReceiveChannel<LoadedImage> {
        val output = Channel<LoadedImage>(capacity = 10)

        val workers = List(parallelism) { workerId ->
            scope.launch {
                for (task in tasks) {
                    try {
                        val image = ImageIO.read(task.file)
                        output.send(LoadedImage(task.file, image))
                        println("Worker $workerId loaded ${task.file.name}")
                    } catch (e: Exception) {
                        println("Failed to load ${task.file.name}: ${e.message}")
                    }
                }
            }
        }

        scope.launch {
            workers.forEach { it.join() }
            output.close()
        }

        return output
    }

    // Stage 3: Apply filters (CPU bound - fan-out with shared output channel)
    private fun applyFilters(
        images: ReceiveChannel<LoadedImage>,
        parallelism: Int
    ): ReceiveChannel<ProcessedImage> {
        val output = Channel<ProcessedImage>(capacity = 5)

        val workers = List(parallelism) { workerId ->
            scope.launch {
                for (loaded in images) {
                    val processed = applyGrayscaleFilter(loaded.image)
                    output.send(ProcessedImage(loaded.file, processed))
                    println("Worker $workerId processed ${loaded.file.name}")
                }
            }
        }

        scope.launch {
            workers.forEach { it.join() }
            output.close()
        }

        return output
    }

    private suspend fun applyGrayscaleFilter(image: BufferedImage): BufferedImage {
        // Simulate CPU-intensive work in a suspending way
        delay(100)
        return image  // Simplified
    }

    // Stage 4: Save results (I/O bound)
    private fun saveImages(
        images: ReceiveChannel<ProcessedImage>,
        outputDir: File,
        parallelism: Int
    ) = scope.launch {
        outputDir.mkdirs()
        val workers = List(parallelism) { workerId ->
            launch {
                for (processed in images) {
                    val outputFile = File(outputDir, "processed_${processed.file.name}")
                    ImageIO.write(processed.image, "jpg", outputFile)
                    println("Worker $workerId saved ${outputFile.name}")
                }
            }
        }
        workers.forEach { it.join() }
    }

    // Build and execute pipeline
    suspend fun process(inputDir: File, outputDir: File) {
        val tasks = scanImages(inputDir)
        val loaded = loadImages(tasks, parallelism = 4)
        val processed = applyFilters(loaded, parallelism = 2)

        saveImages(processed, outputDir, parallelism = 2).join()
        println("Pipeline completed")
    }
}

// Usage
fun main() = runBlocking {
    val pipeline = ImageProcessingPipeline(this)
    pipeline.process(
        inputDir = File("/path/to/images"),
        outputDir = File("/path/to/output")
    )
}
```

### Real-World Pipeline: Data ETL

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class ETLPipeline(private val scope: CoroutineScope) {

    data class RawRecord(val id: Long, val data: Map<String, String>)
    data class TransformedRecord(val id: Long, val normalized: Map<String, Any>)
    data class ValidatedRecord(val record: TransformedRecord, val valid: Boolean, val errors: List<String>)

    // Extract: Read from data source
    private fun extract(): ReceiveChannel<RawRecord> = scope.produce(capacity = 100) {
        var id = 0L
        while (id < 10000 && isActive) {
            send(
                RawRecord(
                    id,
                    mapOf(
                        "name" to "User$id",
                        "age" to "${(18..80).random()}",
                        "email" to "user$id@example.com"
                    )
                )
            )
            id++
            if (id % 100 == 0L) delay(10)  // Simulate batch fetching
        }
    }

    // Transform: Normalize and convert data with proper closing
    private fun transform(
        input: ReceiveChannel<RawRecord>,
        parallelism: Int
    ): ReceiveChannel<TransformedRecord> {
        val output = Channel<TransformedRecord>(capacity = 100)
        val workerJobs = List(parallelism) {
            scope.launch {
                for (raw in input) {
                    val normalized = raw.data.mapValues { (key, value) ->
                        when (key) {
                            "age" -> value.toIntOrNull() ?: 0
                            "email" -> value.lowercase()
                            else -> value
                        }
                    }
                    output.send(TransformedRecord(raw.id, normalized))
                }
            }
        }

        scope.launch {
            workerJobs.forEach { it.join() }
            output.close()
        }

        return output
    }

    // Validate: Check data quality with proper closing
    private fun validate(
        input: ReceiveChannel<TransformedRecord>,
        parallelism: Int
    ): ReceiveChannel<ValidatedRecord> {
        val output = Channel<ValidatedRecord>(capacity = 100)
        val workerJobs = List(parallelism) {
            scope.launch {
                for (record in input) {
                    val errors = mutableListOf<String>()

                    val age = record.normalized["age"] as? Int
                    if (age == null || age < 0 || age > 150) {
                        errors.add("Invalid age: $age")
                    }

                    val email = record.normalized["email"] as? String
                    if (email == null || !email.contains("@")) {
                        errors.add("Invalid email: $email")
                    }

                    output.send(ValidatedRecord(record, errors.isEmpty(), errors))
                }
            }
        }

        scope.launch {
            workerJobs.forEach { it.join() }
            output.close()
        }

        return output
    }

    // Load: Write to destination (with batching)
    private fun load(
        input: ReceiveChannel<ValidatedRecord>,
        batchSize: Int
    ) = scope.launch {
        val batch = mutableListOf<ValidatedRecord>()
        var validCount = 0
        var invalidCount = 0

        for (validated in input) {
            if (validated.valid) {
                batch.add(validated)
                validCount++

                if (batch.size >= batchSize) {
                    writeBatch(batch)
                    batch.clear()
                }
            } else {
                invalidCount++
                println("Invalid record ${validated.record.id}: ${validated.errors}")
            }
        }

        // Write remaining
        if (batch.isNotEmpty()) {
            writeBatch(batch)
        }

        println("ETL Complete: $validCount valid, $invalidCount invalid")
    }

    private suspend fun writeBatch(batch: List<ValidatedRecord>) {
        delay(50)  // Simulate database write
        println("Wrote batch of ${batch.size} records")
    }

    // Run complete pipeline
    suspend fun run() {
        val raw = extract()
        val transformed = transform(raw, parallelism = 4)
        val validated = validate(transformed, parallelism = 4)
        load(validated, batchSize = 100).join()
    }
}

// Usage with monitoring
fun main() = runBlocking {
    val startTime = System.currentTimeMillis()

    val pipeline = ETLPipeline(this)
    pipeline.run()

    val duration = System.currentTimeMillis() - startTime
    println("Pipeline completed in ${duration}ms")
}
```

### Backpressure Handling

Managing flow control when producers are faster than consumers:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.channels.BufferOverflow

class BackpressureExample {

    // Strategy 1: Bounded buffer with suspension
    fun boundedBufferStrategy() = runBlocking {
        val channel = Channel<Int>(capacity = 10)

        val producer = launch {
            repeat(100) { i ->
                println("Producing $i")
                channel.send(i)  // Suspends when buffer full
                println("Produced $i")
            }
            channel.close()
        }

        val consumer = launch {
            for (value in channel) {
                println("  Consuming $value")
                delay(100)  // Slow consumer
            }
        }

        joinAll(producer, consumer)
    }

    // Strategy 2: Drop oldest on overflow (minimize suspension at cost of loss)
    fun dropOldestStrategy() = runBlocking {
        val channel = Channel<Int>(
            capacity = 1,
            onBufferOverflow = BufferOverflow.DROP_OLDEST
        )

        val producer = launch {
            repeat(100) { i ->
                channel.send(i)
                delay(10)
            }
            channel.close()
        }

        val consumer = launch {
            for (value in channel) {
                println("Received: $value")  // Many values skipped
                delay(100)
            }
        }

        joinAll(producer, consumer)
    }

    // Strategy 3: Sampling - process every Nth item
    fun samplingStrategy() = runBlocking {
        val channel = Channel<Int>(capacity = Channel.UNLIMITED)

        val producer = launch {
            repeat(1000) { i ->
                channel.send(i)
            }
            channel.close()
        }

        val consumer = launch {
            var count = 0
            for (value in channel) {
                count++
                if (count % 10 == 0) {  // Process every 10th item
                    println("Processing: $value")
                    delay(50)
                }
            }
        }

        joinAll(producer, consumer)
    }
}
```

### Pipeline Monitoring and Metrics

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

class MonitoredPipeline(private val scope: CoroutineScope) {

    data class PipelineMetrics(
        var itemsProcessed: Long = 0,
        var itemsFailed: Long = 0,
        var totalProcessingTime: Long = 0,
        val startTime: Long = System.currentTimeMillis()
    ) {
        val averageProcessingTime: Long
            get() = if (itemsProcessed > 0) totalProcessingTime / itemsProcessed else 0

        val throughput: Double
            get() = itemsProcessed.toDouble() /
                ((System.currentTimeMillis() - startTime).coerceAtLeast(1) / 1000.0)

        fun printStats() {
            println(
                """
                Pipeline Statistics:
                - Items processed: $itemsProcessed
                - Items failed: $itemsFailed
                - Average time: ${averageProcessingTime}ms
                - Throughput: ${"%.2f".format(throughput)} items/sec
                - Uptime: ${(System.currentTimeMillis() - startTime) / 1000}s
                """.trimIndent()
            )
        }
    }

    private val metrics = PipelineMetrics()

    private fun produceWithMetrics(): ReceiveChannel<Int> = scope.produce {
        repeat(1000) { i ->
            send(i)
            delay(10)
        }
    }

    private fun processWithMetrics(
        input: ReceiveChannel<Int>
    ): ReceiveChannel<Int> = scope.produce {
        for (item in input) {
            val startTime = System.nanoTime()
            try {
                delay(50)  // Simulate processing
                send(item * 2)

                metrics.itemsProcessed++
                metrics.totalProcessingTime += (System.nanoTime() - startTime) / 1_000_000
            } catch (e: Exception) {
                metrics.itemsFailed++
            }
        }
    }

    suspend fun run() {
        val input = produceWithMetrics()
        val output = processWithMetrics(input)

        // Print stats periodically
        val monitor = scope.launch {
            while (isActive) {
                delay(1000)
                metrics.printStats()
            }
        }

        // Consume results
        for (result in output) {
            // Process result if needed
        }

        monitor.cancel()
        metrics.printStats()
    }
}
```

### Best Practices

1. **Choose appropriate buffer sizes**:
```kotlin
// Small buffer for memory-intensive data
val imageChannel = Channel<BufferedImage>(capacity = 5)

// Large buffer for lightweight data
val numberChannel = Channel<Int>(capacity = 1000)

// Rendezvous for strict hand-off
val syncChannel = Channel<String>(capacity = Channel.RENDEZVOUS)
```

2. **Handle cancellation properly**:
```kotlin
fun CoroutineScope.robustProducer(): ReceiveChannel<Int> = produce {
    try {
        repeat(1000) { i ->
            send(i)
            if (!isActive) return@produce
        }
    } finally {
        println("Producer cleanup")
    }
}
```

3. **Use structured concurrency**:
```kotlin
suspend fun reliablePipeline() = coroutineScope {
    val channel1 = produceData()
    val channel2 = processData(channel1)
    val channel3 = transformData(channel2)

    // All coroutines are cancelled if any fails
    consumeData(channel3)
}
```

4. **Monitor channel capacity/state carefully (for diagnostics, not strict correctness)**:
```kotlin
fun monitorChannelHealth(channel: Channel<Int>) {
    println("Channel isEmpty: ${channel.isEmpty}")
    println("Channel isFull: ${channel.isFull}")
}
```

5. **Implement proper error handling**:
```kotlin
fun CoroutineScope.safeProcessor(
    input: ReceiveChannel<Int>
): ReceiveChannel<Result<Int>> = produce {
    for (item in input) {
        try {
            val result = processItem(item)
            send(Result.success(result))
        } catch (e: Exception) {
            send(Result.failure(e))
        }
    }
}
```

### Common Pitfalls

1. **Unbounded channels causing OOM**:
```kotlin
// Bad - can consume all memory
val channel = Channel<Data>(capacity = Channel.UNLIMITED)

// Better - bounded buffer
val bounded = Channel<Data>(capacity = 100)
```

2. **Not closing channels or not completing stages**:
```kotlin
// Bad - consumer may wait forever
fun producer(): ReceiveChannel<Int> = Channel<Int>().apply {
    GlobalScope.launch {
        send(1)
        // Forgot to close, no structured parent
    }
}

// Better - use produce builder in a proper scope
fun CoroutineScope.producer() = produce {
    send(1)
}  // Channel is closed when block completes
```

3. **Blocking operations in pipeline**:
```kotlin
// Bad - blocks coroutine thread
fun processSync(item: Int): Int {
    Thread.sleep(100)
    return item * 2
}

// Good - suspending
suspend fun processAsync(item: Int): Int {
    delay(100)
    return item * 2
}
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия такого подхода от Java без корутин?
- Когда вы бы использовали такие конвейеры на практике?
- Какие распространенные подводные камни важно избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)
- [Kotlin Coroutines: Channels](https://kotlinlang.org/docs/channels.html)
- [Channel Pipelines](https://kotlinlang.org/docs/channels.html#pipelines)
- [Fan-out and Fan-in](https://kotlinlang.org/docs/channels.html#fan-out)

## References
- [Kotlin Coroutines: Channels](https://kotlinlang.org/docs/channels.html)
- [Channel Pipelines](https://kotlinlang.org/docs/channels.html#pipelines)
- [Fan-out and Fan-in](https://kotlinlang.org/docs/channels.html#fan-out)

## Похожие Вопросы (RU)
- [[q-kotlin-channels--kotlin--medium]]
- [[q-produce-actor-builders--kotlin--medium]]
- [[q-flow-backpressure-strategies--kotlin--hard]]
- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-kotlin-coroutines-introduction--kotlin--medium]]

## Related Questions
- [[q-kotlin-channels--kotlin--medium]]
- [[q-produce-actor-builders--kotlin--medium]]
- [[q-flow-backpressure-strategies--kotlin--hard]]
- [[q-structured-concurrency-kotlin--kotlin--medium]]
- [[q-kotlin-coroutines-introduction--kotlin--medium]]

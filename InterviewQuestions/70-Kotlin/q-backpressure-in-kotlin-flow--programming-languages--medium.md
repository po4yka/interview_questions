---
id: 20251006-backpressure-flow
title: "Back Pressure in Kotlin Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, backpressure, buffer, conflate, operators]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-flow-basics--kotlin--medium, q-debounce-throttle-flow--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-07

tags: [kotlin, flow, backpressure, buffer, conflate, operators, difficulty/medium]
---
# Question (EN)
> What is Back Pressure in Kotlin Flow? What strategies exist to handle it?
# Вопрос (RU)
> Что такое Back Pressure в Kotlin Flow? Какие стратегии существуют для его обработки?

## Answer (EN)
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
    // - DO: Use conflate for state updates
    fun userState(): Flow<UserState> =
        stateUpdates.conflate()

    // - DO: Use buffer for throughput
    fun dataProcessing(): Flow<Result> =
        dataSource
            .buffer(100)
            .map { process(it) }

    // - DO: Use debounce for user input
    fun searchQuery(input: Flow<String>): Flow<Results> =
        input.debounce(300)
            .flatMapLatest { query -> search(query) }

    // - DO: Use sample for high-frequency events
    fun mousePosition(events: Flow<MouseEvent>): Flow<Position> =
        events.sample(16)  // ~60fps

    // - DON'T: Use unlimited buffer
    fun dangerous(): Flow<Data> =
        source.buffer(Int.MAX_VALUE)  // Will cause OOM!

    // - DON'T: Ignore backpressure entirely
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

## Ответ (RU)

**Back Pressure** — это механизм контроля потока данных, который предотвращает перегрузку потребителя, когда производитель отправляет данные слишком быстро.

Kotlin Flow и Reactive Streams имеют стратегии для управления Back Pressure:

- **Buffer**: Накапливает данные в памяти
- **Drop**: Игнорирует избыточные элементы
- **Latest**: Хранит только последний элемент
- **Conflate**: Объединяет значения для уменьшения нагрузки

Back Pressure необходим для стабильности и предотвращения утечек памяти в асинхронных потоках.

### Проблема: Быстрый Производитель, Медленный Потребитель

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Проблема: Производитель испускает быстрее, чем потребитель может обработать
fun problematicFlow() = flow {
    repeat(100) { i ->
        println("Испускаю $i")
        emit(i)
        delay(10)  // Производитель испускает каждые 10мс
    }
}

fun main() = runBlocking {
    problematicFlow().collect { value ->
        println("Собираю $value")
        delay(100)  // Потребитель обрабатывает каждые 100мс
        // Производитель в 10 раз быстрее потребителя!
    }
}

// Без обработки backpressure:
// - Накопление в памяти
// - Потенциальный OutOfMemoryError
// - Потеря данных
// - Нестабильность системы
```

### Стратегия 1: buffer() - Накопление Данных

```kotlin
// Buffer позволяет производителю работать быстрее потребителя
fun bufferExample() = runBlocking {
    flow {
        repeat(10) { i ->
            println("Испускаю $i в ${System.currentTimeMillis()}")
            emit(i)
            delay(100)
        }
    }
    .buffer(capacity = 5)  // Буфер до 5 элементов
    .collect { value ->
        println("Собираю $value в ${System.currentTimeMillis()}")
        delay(500)  // Медленный потребитель
    }
}

// С буфером:
// - Производитель не ждет потребителя
// - Элементы хранятся в буфере
// - Производитель приостанавливается при заполнении буфера
// - Потребитель обрабатывает в своем темпе

// Стратегии емкости буфера
val flow1 = flowOf(1, 2, 3)
    .buffer()  // Буфер по умолчанию (64 элемента)

val flow2 = flowOf(1, 2, 3)
    .buffer(10)  // Буфер на 10 элементов

val flow3 = flowOf(1, 2, 3)
    .buffer(Channel.UNLIMITED)  // Неограниченный буфер (опасно!)

val flow4 = flowOf(1, 2, 3)
    .buffer(Channel.RENDEZVOUS)  // Без буфера, ждать потребителя
```

### Стратегия 2: conflate() - Только Последнее Значение

```kotlin
// Conflate пропускает промежуточные значения, сохраняет только последнее
fun conflateExample() = runBlocking {
    flow {
        repeat(10) { i ->
            println("Испускаю $i")
            emit(i)
            delay(100)
        }
    }
    .conflate()  // Отбрасываем промежуточные значения
    .collect { value ->
        println("Собираю $value")
        delay(500)  // Медленный потребитель
    }
}

// Пример вывода:
// Испускаю 0
// Собираю 0
// Испускаю 1
// Испускаю 2
// Испускаю 3
// Испускаю 4
// Собираю 4  <- Пропущены 1, 2, 3
// Испускаю 5
// ...

// Случай использования: Обновления UI
fun locationUpdates(): Flow<Location> = flow {
    while (true) {
        emit(getCurrentLocation())
        delay(100)
    }
}
    .conflate()  // Показываем только последнюю локацию

// Случай использования: Цены акций
fun stockPrices(symbol: String): Flow<Double> = flow {
    while (true) {
        emit(fetchPrice(symbol))
        delay(50)
    }
}
    .conflate()  // Важна только последняя цена
```

### Стратегия 3: collectLatest() - Отмена Предыдущего Сбора

```kotlin
// collectLatest отменяет предыдущий сбор при поступлении нового значения
fun collectLatestExample() = runBlocking {
    flow {
        repeat(5) { i ->
            println("Испускаю $i")
            emit(i)
            delay(100)
        }
    }
    .collectLatest { value ->
        println("Начинаю собирать $value")
        delay(500)  // Медленная обработка
        println("Заканчиваю собирать $value")  // Может не выполниться
    }
}

// Пример вывода:
// Испускаю 0
// Начинаю собирать 0
// Испускаю 1
// Начинаю собирать 1  <- Отменен сбор 0
// Испускаю 2
// Начинаю собирать 2  <- Отменен сбор 1
// ...
// Заканчиваю собирать 4  <- Только последний завершается

// Случай использования: Поисковые запросы
fun searchFlow(queries: Flow<String>): Flow<List<Result>> =
    queries.collectLatest { query ->
        // Отменяем предыдущий поиск при новом запросе
        performSearch(query)
    }

// Случай использования: Обновления данных в реальном времени
fun dataUpdates(): Flow<Data> = dataSource
    .collectLatest { rawData ->
        // Отменяем предыдущую обработку
        processData(rawData)
    }
```

### Стратегия 4: Буфер с Обработкой Переполнения

```kotlin
// Буфер с обработкой переполнения
suspend fun bufferOverflowStrategies() {
    val source = flow {
        repeat(100) { emit(it) }
    }

    // SUSPEND (по умолчанию): Приостанавливает производителя при заполнении
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.SUSPEND
    ).collect { /* медленный потребитель */ }

    // DROP_OLDEST: Отбрасывает старые значения при заполнении
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    ).collect { /* медленный потребитель */ }

    // DROP_LATEST: Отбрасывает новые значения при заполнении
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.DROP_LATEST
    ).collect { /* медленный потребитель */ }
}

// Реальный пример: Логирование событий
class EventLogger {
    private val events = MutableSharedFlow<Event>(
        replay = 0,
        extraBufferCapacity = 1000,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    fun logEvent(event: Event) {
        events.tryEmit(event)  // Не приостанавливается, отбрасывает старое при заполнении
    }

    fun observeEvents(): Flow<Event> = events
}
```

### Стратегия 5: Sample / Throttle

```kotlin
// sample: Испускает последнее значение через фиксированные интервалы
fun sampleExample() = runBlocking {
    flow {
        repeat(100) { i ->
            emit(i)
            delay(10)  // Быстрое испускание
        }
    }
    .sample(100)  // Сэмплирование каждые 100мс
    .collect { value ->
        println("Сэмплировано: $value")
    }
}

// Вывод: Только значения на интервалах 100мс
// Сэмплировано: 9
// Сэмплировано: 19
// Сэмплировано: 29
// ...

// Пользовательская реализация sample
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

// Случай использования: Данные сенсоров
fun sensorReadings(): Flow<SensorData> = flow {
    while (true) {
        emit(readSensor())
        delay(10)  // Чтение каждые 10мс
    }
}
    .sample(1000)  // Отчет каждую секунду
```

### Стратегия 6: Debounce

```kotlin
// debounce: Испускает значение только после периода тишины
fun debounceExample() = runBlocking {
    flow {
        emit(1)
        delay(50)
        emit(2)
        delay(50)
        emit(3)
        delay(500)  // Период тишины
        emit(4)
    }
    .debounce(200)  // Ждать 200мс тишины
    .collect { value ->
        println("Debounced: $value")
    }
}

// Вывод:
// Debounced: 3  <- После периода тишины
// Debounced: 4  <- Последнее значение

// Случай использования: Поисковый ввод
fun searchInput(textChanges: Flow<String>): Flow<List<Result>> =
    textChanges
        .debounce(300)  // Ждем, пока пользователь прекратит печатать
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            performSearch(query)
        }

// Случай использования: Автосохранение
fun autoSave(contentChanges: Flow<String>): Flow<Unit> =
    contentChanges
        .debounce(2000)  // Сохраняем через 2 секунды после последнего изменения
        .map { content -> saveToServer(content) }
```

### Сравнение Стратегий

```kotlin
suspend fun compareStrategies() = coroutineScope {
    val source = flow {
        repeat(10) { i ->
            println("Испускаю $i")
            emit(i)
            delay(100)
        }
    }

    println("=== Без backpressure ===")
    source.collect {
        delay(500)
        println("Собираю $it")
    }

    println("\n=== С buffer ===")
    source.buffer(3).collect {
        delay(500)
        println("Собираю $it")
    }

    println("\n=== С conflate ===")
    source.conflate().collect {
        delay(500)
        println("Собираю $it")
    }

    println("\n=== С collectLatest ===")
    source.collectLatest {
        println("Начало $it")
        delay(500)
        println("Конец $it")
    }
}
```

### Реальный Пример: Менеджер Загрузок

```kotlin
class DownloadManager {
    // Быстрые события загрузки, медленные обновления UI
    private val downloadProgress = MutableSharedFlow<DownloadProgress>(
        replay = 0,
        extraBufferCapacity = 100,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    fun observeProgress(): Flow<DownloadProgress> =
        downloadProgress
            .conflate()  // UI нужен только последний прогресс
            .sample(100)  // Обновлять UI макс. 10 раз/секунду

    suspend fun download(url: String) {
        var bytesDownloaded = 0L
        val totalBytes = getContentLength(url)

        downloadStream(url).collect { chunk ->
            bytesDownloaded += chunk.size
            // Испускаем прогресс (может быть быстрее чем UI может обработать)
            downloadProgress.emit(
                DownloadProgress(bytesDownloaded, totalBytes)
            )
        }
    }
}
```

### Безопасный для Памяти Паттерн

```kotlin
// Предотвращаем OOM с ограниченным буфером
fun safePipeline(): Flow<ProcessedData> = flow {
    // Быстрый источник данных
    repeat(1_000_000) { emit(it) }
}
    .buffer(capacity = 100)  // Ограниченный буфер
    .map { data ->
        // CPU-интенсивная обработка
        processData(data)
    }
    .buffer(capacity = 50)  // Еще один ограниченный буфер
    .map { intermediate ->
        // Дополнительная обработка
        transform(intermediate)
    }

// Без ограниченных буферов:
// - Неконтролируемый рост памяти
// - Потенциальный OOM
// - Сбой системы

// С ограниченными буферами:
// - Контролируемое использование памяти
// - Производитель приостанавливается при заполнении буфера
// - Стабильная система
```

### Лучшие Практики

```kotlin
class BackPressureBestPractices {
    // - ДЕЛАТЬ: Использовать conflate для обновлений состояния
    fun userState(): Flow<UserState> =
        stateUpdates.conflate()

    // - ДЕЛАТЬ: Использовать buffer для пропускной способности
    fun dataProcessing(): Flow<Result> =
        dataSource
            .buffer(100)
            .map { process(it) }

    // - ДЕЛАТЬ: Использовать debounce для ввода пользователя
    fun searchQuery(input: Flow<String>): Flow<Results> =
        input.debounce(300)
            .flatMapLatest { query -> search(query) }

    // - ДЕЛАТЬ: Использовать sample для высокочастотных событий
    fun mousePosition(events: Flow<MouseEvent>): Flow<Position> =
        events.sample(16)  // ~60fps

    // - НЕ ДЕЛАТЬ: Использовать неограниченный буфер
    fun dangerous(): Flow<Data> =
        source.buffer(Int.MAX_VALUE)  // Вызовет OOM!

    // - НЕ ДЕЛАТЬ: Полностью игнорировать backpressure
    fun alsoProblematic(): Flow<Data> =
        fastSource  // Нет обработки backpressure
}
```

### Таблица Сводки

| Стратегия | Поведение | Случай использования | Влияние на память |
|----------|----------|----------|---------------|
| **buffer()** | Очередь элементов | Высокая пропускная способность | Среднее (ограниченное) |
| **conflate()** | Сохранять последнее | Обновления состояния | Низкое |
| **collectLatest()** | Отменять предыдущее | Отменяемая работа | Низкое |
| **sample()** | Периодическое испускание | Высокочастотные события | Низкое |
| **debounce()** | После периода тишины | Ввод пользователя | Низкое |
| **DROP_OLDEST** | Отбрасывать старые | Логирование событий | Низкое (ограниченное) |
| **DROP_LATEST** | Отбрасывать новые | Редко используется | Низкое (ограниченное) |

**Резюме**: Back Pressure — критический механизм для управления асинхронными потоками данных в Kotlin Flow. Правильный выбор стратегии (buffer, conflate, collectLatest, sample, debounce) зависит от конкретного случая использования и обеспечивает стабильность системы и эффективное использование памяти.

---

## References

- [Flow - Kotlin Documentation](https://kotlinlang.org/docs/flow.html)
- [Buffering in Flows - Kotlin Blog](https://kotlinlang.org/docs/flow.html#buffering)
- [SharedFlow and StateFlow - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

---

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

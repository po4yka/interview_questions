---
id: kotlin-038
title: "Back Pressure в Kotlin Flow / Back Pressure in Kotlin Flow"
aliases: ["Back Pressure in Kotlin Flow", "Back Pressure в Kotlin Flow"]
topic: kotlin
subtopics: [backpressure, buffer, conflate]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, q-debounce-throttle-flow--kotlin--medium, q-kotlin-flow-basics--kotlin--medium]
created: 2025-10-06
updated: 2025-11-11
tags: [backpressure, buffer, conflate, difficulty/medium, flow, kotlin, operators]

---
# Вопрос (RU)
> Что такое Back Pressure в Kotlin `Flow`? Какие стратегии существуют для его обработки?

# Question (EN)
> What is Back Pressure in Kotlin `Flow`? What strategies exist to handle it?

## Ответ (RU)

**Back Pressure** — это контроль потока данных между производителем и потребителем, который предотвращает перегрузку потребителя, когда производитель испускает элементы быстрее, чем их можно обработать. В контексте Kotlin `Flow` это достигается в первую очередь за счет приостановки (suspension) производителя и настройки буферизации/отбрасывания элементов.

В Kotlin `Flow` используются следующие подходы для управления скоростью и объемом данных:

- **buffer() с onBufferOverflow**: накапливает данные в очереди и определяет поведение при переполнении
- **conflate()**: пропускает промежуточные значения, сохраняя только последние
- **collectLatest()/mapLatest()/flatMapLatest()**: отменяют обработку предыдущих значений при поступлении новых
- **sample()/debounce()**: формируют поток (throttling/shaping), ограничивая частоту событий

Back Pressure и управление скоростью нужны для стабильности, предсказуемого использования памяти и предотвращения утечек/OutOfMemory в асинхронных потоках.

См. также: [[c-flow]], [[c-kotlin]].

### Проблема: Быстрый Производитель, Медленный Потребитель

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Проблема: Производитель пытается испускать быстрее, чем потребитель может обработать
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

// В базовой реализации Flow без дополнительных операторов:
// - Производитель будет приостанавливаться, если потребитель не успевает (поддержка backpressure через suspension)
// - Проблемы возникают при неограниченной буферизации или неправильной стратегии работы с быстрыми источниками:
//   - Неконтролируемое накопление в памяти
//   - Потенциальный OutOfMemoryError
//   - Потеря данных (при политиках DROP_*)
//   - Нестабильность системы
```

### Стратегия 1: buffer() - Накопление Данных

```kotlin
// buffer позволяет производителю "обгонять" потребителя до заполнения буфера
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

// С buffer:
// - Производитель не ждет потребителя, пока есть свободное место в буфере
// - Элементы хранятся в буфере
// - При заполнении буфера производитель приостанавливается (при SUSPEND)
// - Потребитель обрабатывает в своем темпе

// Стратегии емкости буфера
val flow1 = flowOf(1, 2, 3)
    .buffer()  // Буфер по умолчанию (64 элемента)

val flow2 = flowOf(1, 2, 3)
    .buffer(10)  // Буфер на 10 элементов

val flow3 = flowOf(1, 2, 3)
    .buffer(Channel.UNLIMITED)  // Неограниченный буфер (рискованно: возможен рост памяти)

val flow4 = flowOf(1, 2, 3)
    .buffer(Channel.RENDEZVOUS)  // Без буфера: каждый emit ждет collect
```

### Стратегия 2: conflate() - Только Последнее Значение

```kotlin
// conflate пропускает промежуточные значения, сохраняет только последнее
fun conflateExample() = runBlocking {
    flow {
        repeat(10) { i ->
            println("Испускаю $i")
            emit(i)
            delay(100)
        }
    }
        .conflate()  // Отбрасываем накопившиеся промежуточные значения
        .collect { value ->
            println("Собираю $value")
            delay(500)  // Медленный потребитель
        }
}

// Пример вывода (может отличаться):
// Испускаю 0
// Собираю 0
// Испускаю 1
// Испускаю 2
// Испускаю 3
// Испускаю 4
// Собираю 4  <- Пропущены 1, 2, 3
// Испускаю 5
// ...

// Случай использования: обновления UI, где важен только последний стейт
fun locationUpdates(): Flow<Location> = flow {
    while (true) {
        emit(getCurrentLocation())
        delay(100)
    }
}
    .conflate()  // Показываем только последнюю локацию

// Случай использования: котировки
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
// collectLatest отменяет обработку предыдущего значения при поступлении нового
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
// Начинаю собирать 1  <- Сбор 0 отменен
// Испускаю 2
// Начинаю собирать 2  <- Сбор 1 отменен
// ...
// Заканчиваю собирать 4  <- Только последний завершается

// Случай использования: поисковые запросы (flatMapLatest/collectLatest в месте использования)
fun observeSearchResults(queries: Flow<String>): Flow<List<Result>> =
    queries
        .debounce(300)
        .flatMapLatest { query ->
            // При новом запросе отменяется предыдущий поиск
            performSearch(query)
        }

// Случай использования: обновления данных в реальном времени
fun observeProcessedData(): Flow<Data> =
    dataSource
        .flatMapLatest { rawData ->
            // При новом rawData отменяем предыдущую обработку
            processData(rawData)
        }
```

### Стратегия 4: Буфер С Обработкой Переполнения

```kotlin
// Буфер с обработкой переполнения
suspend fun bufferOverflowStrategies() {
    val source = flow {
        repeat(100) { emit(it) }
    }

    // SUSPEND (по умолчанию): приостанавливает производителя при заполнении
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.SUSPEND
    ).collect { /* медленный потребитель */ }

    // DROP_OLDEST: отбрасывает старые значения при заполнении
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    ).collect { /* медленный потребитель */ }

    // DROP_LATEST: отбрасывает новые значения при заполнении
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.DROP_LATEST
    ).collect { /* медленный потребитель */ }
}

// Реальный пример: логирование событий
class EventLogger {
    private val events = MutableSharedFlow<Event>(
        replay = 0,
        extraBufferCapacity = 1000,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    fun logEvent(event: Event) {
        // Не приостанавливается; при заполнении будут отбрасываться старые события
        events.tryEmit(event)
    }

    fun observeEvents(): Flow<Event> = events
}
```

### Стратегия 5: Sample / Throttle

```kotlin
// sample: испускает последнее значение с фиксированным интервалом
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

// Вывод: значения на интервалах ~100мс (конкретные числа зависят от тайминга)

// Пользовательская реализация sample (упрощенная)
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

// Случай использования: данные сенсоров
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
// debounce: испускает значение только после периода тишины
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

// Возможный вывод (зависит от точных таймингов):
// Debounced: 3
// Debounced: 4

// Случай использования: поисковый ввод
fun searchInput(textChanges: Flow<String>): Flow<List<Result>> =
    textChanges
        .debounce(300)  // Ждем, пока пользователь прекратит печатать
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            performSearch(query)
        }

// Случай использования: автосохранение
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

    println("=== Без дополнительных операторов ===")
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
    // Быстрые события загрузки, более медленные обновления UI
    private val downloadProgress = MutableSharedFlow<DownloadProgress>(
        replay = 0,
        extraBufferCapacity = 100,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    fun observeProgress(): Flow<DownloadProgress> =
        downloadProgress
            .conflate()  // UI нужен только последний прогресс
            .sample(100)  // Обновлять UI максимум 10 раз/секунду

    suspend fun download(url: String) {
        var bytesDownloaded = 0L
        val totalBytes = getContentLength(url)

        downloadStream(url).collect { chunk ->
            bytesDownloaded += chunk.size
            // Испускаем прогресс (может быть быстрее, чем UI может обработать)
            downloadProgress.emit(
                DownloadProgress(bytesDownloaded, totalBytes)
            )
        }
    }
}
```

### Безопасный Для Памяти Паттерн

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
// - Возможен неконтролируемый рост памяти при быстрой генерации данных
// - Потенциальный OOM
// - Сбой системы

// С ограниченными буферами:
// - Контролируемое использование памяти
// - Производитель приостанавливается при заполнении буфера
// - Более стабильная система
```

### Лучшие Практики

```kotlin
class BackPressureBestPractices {
    // - ДЕЛАТЬ: использовать conflate для обновлений состояния
    fun userState(): Flow<UserState> =
        stateUpdates.conflate()

    // - ДЕЛАТЬ: использовать buffer для повышения пропускной способности
    fun dataProcessing(): Flow<Result> =
        dataSource
            .buffer(100)
            .map { process(it) }

    // - ДЕЛАТЬ: использовать debounce для ввода пользователя
    fun searchQuery(input: Flow<String>): Flow<Results> =
        input.debounce(300)
            .flatMapLatest { query -> search(query) }

    // - ДЕЛАТЬ: использовать sample для высокочастотных событий
    fun mousePosition(events: Flow<MouseEvent>): Flow<Position> =
        events.sample(16)  // ~60fps

    // - НЕ ДЕЛАТЬ: использовать по-настоящему неограниченные буферы без необходимости
    fun dangerous(): Flow<Data> =
        source.buffer(Int.MAX_VALUE)  // Риск бесконтрольного роста памяти и OOM при высоком трафике

    // - НЕ ДЕЛАТЬ: игнорировать влияние скорости источника и потребителя
    fun alsoProblematic(): Flow<Data> =
        fastSource  // Нет явной стратегии управления нагрузкой
}
```

### Таблица Сводки

| Стратегия | Поведение | Случай использования | Влияние на память |
|----------|----------|----------|---------------|
| **buffer()** | Очередь элементов | Высокая пропускная способность | Среднее (ограниченное) |
| **conflate()** | Сохранять только последнее | Обновления состояния | Низкое |
| **collectLatest()** | Отменять предыдущую обработку | Отменяемая работа | Низкое |
| **sample()** | Периодическое испускание | Высокочастотные события | Низкое |
| **debounce()** | После периода тишины | Ввод пользователя | Низкое |
| **DROP_OLDEST** | Отбрасывать старые значения | Логирование событий | Низкое (ограниченное) |
| **DROP_LATEST** | Отбрасывать новые значения | Специфические сценарии | Низкое (ограниченное) |

**Резюме**: Back Pressure в Kotlin `Flow` реализуется через приостановку emit при отсутствии спроса и через операторы, управляющие буферизацией и частотой событий. Правильный выбор стратегии (buffer, conflate, collectLatest, sample, debounce и настройка onBufferOverflow) зависит от конкретного случая использования и обеспечивает стабильность системы и эффективное использование ресурсов.

---

## Answer (EN)
**Back Pressure** is flow control between producer and consumer that prevents the consumer from being overwhelmed when the producer emits faster than it can process. In Kotlin `Flow` this is primarily achieved via suspension of the producer and configurable buffering/element-dropping behavior.

Kotlin `Flow` provides several mechanisms to control rate and volume:

- **buffer() with onBufferOverflow**: queue elements and define behavior on overflow
- **conflate()**: skip intermediate values, keep only the latest
- **collectLatest()/mapLatest()/flatMapLatest()**: cancel ongoing work for previous values when new ones arrive
- **sample()/debounce()**: shape/limit emission frequency (throttling-like behavior)

These are important for stability, predictable memory usage, and avoiding leaks/OutOfMemory in async streams.

See also: [[c-flow]], [[c-kotlin]].

### The Problem: Fast Producer, Slow Consumer

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// Problem: producer tries to emit faster than consumer can process
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

// In plain Flow without extra buffering operators:
// - The producer will suspend when the consumer is not ready (backpressure via suspension)
// - Issues appear when using unbounded buffering or misconfigured strategies for fast sources:
//   - Uncontrolled memory accumulation
//   - Potential OutOfMemoryError
//   - Data loss (with DROP_* policies)
//   - System instability
```

### Strategy 1: buffer() - Accumulate Data

```kotlin
// buffer allows producer to run ahead of consumer up to buffer capacity
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
// - Producer does not wait for consumer while there is free space
// - Elements are stored in the buffer
// - Producer suspends when buffer is full (with SUSPEND behavior)
// - Consumer processes at its own pace

// Buffer capacity strategies
val flow1 = flowOf(1, 2, 3)
    .buffer()  // Default buffer (64 elements)

val flow2 = flowOf(1, 2, 3)
    .buffer(10)  // Buffer 10 elements

val flow3 = flowOf(1, 2, 3)
    .buffer(Channel.UNLIMITED)  // Unlimited buffer (risky: may grow and cause OOM)

val flow4 = flowOf(1, 2, 3)
    .buffer(Channel.RENDEZVOUS)  // No buffer: emit waits for collect
```

### Strategy 2: conflate() - Keep Latest Only

```kotlin
// conflate skips intermediate values, keeps only the latest
fun conflateExample() = runBlocking {
    flow {
        repeat(10) { i ->
            println("Emit $i")
            emit(i)
            delay(100)
        }
    }
        .conflate()  // Drop accumulated intermediate values
        .collect { value ->
            println("Collect $value")
            delay(500)  // Slow consumer
        }
}

// Example output (timing-dependent):
// Emit 0
// Collect 0
// Emit 1
// Emit 2
// Emit 3
// Emit 4
// Collect 4  <- Skipped 1, 2, 3
// Emit 5
// ...

// Use case: UI state updates, where only the latest value matters
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
// collectLatest cancels processing of the previous value when a new one arrives
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
            println("Finish collecting $value")  // May not be reached
        }
}

// Example output:
// Emit 0
// Start collecting 0
// Emit 1
// Start collecting 1  <- Cancelled collection of 0
// Emit 2
// Start collecting 2  <- Cancelled collection of 1
// ...
// Finish collecting 4  <- Only the last one completes

// Use case: search queries (use flatMapLatest/collectLatest where you consume the flow)
fun observeSearchResults(queries: Flow<String>): Flow<List<Result>> =
    queries
        .debounce(300)
        .flatMapLatest { query ->
            // New query cancels previous search
            performSearch(query)
        }

// Use case: live data updates
fun observeProcessedData(): Flow<Data> =
    dataSource
        .flatMapLatest { rawData ->
            // Cancel previous processing when new data arrives
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

    // SUSPEND (default): suspend producer when buffer is full
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.SUSPEND
    ).collect { /* slow consumer */ }

    // DROP_OLDEST: drop oldest values when buffer is full
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    ).collect { /* slow consumer */ }

    // DROP_LATEST: drop newest values when buffer is full
    source.buffer(
        capacity = 10,
        onBufferOverflow = BufferOverflow.DROP_LATEST
    ).collect { /* slow consumer */ }
}

// Real example: event logging
class EventLogger {
    private val events = MutableSharedFlow<Event>(
        replay = 0,
        extraBufferCapacity = 1000,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    fun logEvent(event: Event) {
        // Won't suspend; oldest events are dropped on overflow
        events.tryEmit(event)
    }

    fun observeEvents(): Flow<Event> = events
}
```

### Strategy 5: Sample / Throttle

```kotlin
// sample: emit the latest value at fixed intervals
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

// Output: only values observed at ~100ms intervals (exact indices depend on timing)

// Custom sample implementation (simplified)
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

// Use case: sensor data
fun sensorReadings(): Flow<SensorData> = flow {
    while (true) {
        emit(readSensor())
        delay(10)  // Read every 10ms
    }
}
    .sample(1000)  // Report every second
```

### Strategy 6: Debounce

```kotlin
// debounce: emit value only after a period of silence
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
        .debounce(200)  // Wait for 200ms of silence
        .collect { value ->
            println("Debounced: $value")
        }
}

// Possible output (timing-dependent):
// Debounced: 3
// Debounced: 4

// Use case: search input
fun searchInput(textChanges: Flow<String>): Flow<List<Result>> =
    textChanges
        .debounce(300)  // Wait for user to pause typing
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            performSearch(query)
        }

// Use case: auto-save
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

    println("=== No extra operators ===")
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
    // Fast download events, slower UI updates
    private val downloadProgress = MutableSharedFlow<DownloadProgress>(
        replay = 0,
        extraBufferCapacity = 100,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    fun observeProgress(): Flow<DownloadProgress> =
        downloadProgress
            .conflate()  // UI only needs the latest progress
            .sample(100)  // Update UI at most 10 times/second

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
// Prevent OOM with bounded buffers
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

// Without bounded buffers for fast sources:
// - Potentially unbounded memory growth
// - Possible OOM
// - System crash

// With bounded buffers:
// - Controlled memory usage
// - Producer suspends when buffer is full
// - More stable system
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

    // - DON'T: Use truly unbounded buffers without strong reasons
    fun dangerous(): Flow<Data> =
        source.buffer(Int.MAX_VALUE)  // Risk of uncontrolled growth and OOM under high load

    // - DON'T: Ignore the interaction between source and consumer speeds
    fun alsoProblematic(): Flow<Data> =
        fastSource  // No explicit load-management strategy
}
```

### Summary Table

| Strategy | Behavior | Use Case | Memory Impact |
|----------|----------|----------|---------------|
| **buffer()** | `Queue` elements | High throughput | Medium (bounded) |
| **conflate()** | Keep latest only | State updates | Low |
| **collectLatest()** | Cancel previous work | Cancellable work | Low |
| **sample()** | Periodic emission | High-frequency events | Low |
| **debounce()** | After quiet period | User input | Low |
| **DROP_OLDEST** | Drop old values | Event logging | Low (bounded) |
| **DROP_LATEST** | Drop new values | Specific scenarios | Low (bounded) |

---

## Дополнительные Вопросы (RU)

- Как Back Pressure в Kotlin `Flow` отличается от подходов в реактивных библиотеках на JVM?
- В каких реальных сценариях вы бы применили каждую из стратегий (`buffer`, `conflate`, `collectLatest`, `sample`, `debounce`)?
- Каковы типичные ошибки при работе с backpressure и буферами в `Flow`?

## Follow-ups

- What are the key differences between this and Java reactive approaches?
- When would you use each of these strategies (`buffer`, `conflate`, `collectLatest`, `sample`, `debounce`) in practice?
- What are common pitfalls to avoid when dealing with backpressure and buffers in `Flow`?

---

## Ссылки (RU)

- [`Flow` - документация Kotlin](https://kotlinlang.org/docs/flow.html)
- [Buffering in `Flows` - Kotlin Docs](https://kotlinlang.org/docs/flow.html#buffering)
- [`SharedFlow` и `StateFlow` - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

## References

- [`Flow` - Kotlin Documentation](https://kotlinlang.org/docs/flow.html)
- [Buffering in `Flows` - Kotlin Docs](https://kotlinlang.org/docs/flow.html#buffering)
- [`SharedFlow` and `StateFlow` - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

---

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Коррутины и операторы
- [[q-channel-flow-comparison--kotlin--medium]] - Коррутины
- [[q-flow-operators--kotlin--medium]] - `Flow`

### Продвинутый Уровень
- [[q-flow-backpressure-strategies--kotlin--hard]] - `Flow`
- [[q-flow-backpressure--kotlin--hard]] - `Flow`
- [[q-testing-flow-operators--kotlin--hard]] - Коррутины

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - `Flow`

### Advanced (Harder)
- [[q-flow-backpressure-strategies--kotlin--hard]] - `Flow`
- [[q-flow-backpressure--kotlin--hard]] - `Flow`
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

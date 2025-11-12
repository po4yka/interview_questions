---
id: kotlin-123
title: "Flow Backpressure / Противодавление в Flow"
aliases: ["Flow Backpressure", "Противодавление в Flow"]

# Classification
topic: kotlin
subtopics:
  - flow
  - buffer
  - backpressure
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
related: [c-flow, c-coroutines, q-advanced-coroutine-patterns--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [backpressure, buffer, collectlatest, conflate, difficulty/hard, flow, kotlin, performance]
---
# Вопрос (RU)
> Что такое противодавление в Kotlin `Flow`? Объясните операторы `buffer()`, `conflate()` и `collectLatest()` и когда использовать каждую стратегию.

---

# Question (EN)
> What is backpressure in Kotlin `Flow`? Explain `buffer()`, `conflate()`, and `collectLatest()` operators and when to use each strategy.

## Ответ (RU)

**Противодавление** (backpressure) возникает, когда производитель создаёт значения быстрее, чем потребитель может их обработать. В `Flow` это управляется кооперативно через приостановки: медленный потребитель замедляет быстрый источник. `Flow` предоставляет несколько операторов и настроек буферизации для управления стратегией этого несоответствия скоростей: `buffer()`, `conflate()`, `collectLatest()`, расширенные конфигурации `buffer` и использование `Channel`.

### Понимание Противодавления

Без специальных стратегий поведение по умолчанию такое: противодавление реализуется через приостановку производителя — `emit` приостанавливается, пока медленный потребитель не закончит обработку предыдущего элемента.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

// Без buffer/conflate/collectLatest - производитель ждёт потребителя
suspend fun withoutBuffer() {
    val time = measureTimeMillis {
        flow {
            repeat(3) {
                delay(100) // Производитель: 100 мс
                emit(it)
                println("Emitted $it")
            }
        }.collect {
            delay(300) // Потребитель: 300 мс
            println("Collected $it")
        }
    }
    println("Time: $time ms") // ~1200 мс: (100 + 300) * 3, без перекрытия
}
```

### buffer() — Параллельная обработка

`buffer()` позволяет производителю и потребителю выполняться конкурентно, частично развязывая их скорости, при этом при заполнении буфера по умолчанию используется стратегия `BufferOverflow.SUSPEND`.

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
        .buffer() // Производитель и потребитель могут работать конкурентно
        .collect {
            delay(300)
            println("Collected $it at ${System.currentTimeMillis()}")
        }
    }
    println("Time: $time ms") // Обычно около 900–1000 мс за счёт перекрытия
}
```

#### buffer с capacity

```kotlin
flow {
    repeat(10) {
        emit(it)
        println("Emitted $it")
    }
}
.buffer(capacity = 5) // До 5 элементов в буфере; при переполнении производитель приостанавливается
.collect {
    delay(100)
    println("Collected $it")
}
// Если буфер заполнен, производитель будет suspend до освобождения места (стратегия по умолчанию).
```

#### Стратегии буфера

```kotlin
// Буфер по умолчанию (DEFAULT_CAPACITY и BufferOverflow.SUSPEND)
.buffer()

// Явная емкость
.buffer(capacity = 10)

// Неограниченный буфер (использовать с крайней осторожностью)
.buffer(capacity = Channel.UNLIMITED)

// Эквивалент конфлирующего буфера (по сути хранит только последнее значение)
.buffer(capacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)
```

### conflate() — Только актуальное значение

`conflate()` пропускает промежуточные значения при медленном потребителе, сохраняя только самое новое значение. Фактически эквивалентно `buffer(capacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)`.

```kotlin
suspend fun withConflate() {
    flow {
        repeat(10) {
            emit(it)
            println("Emitted $it")
            delay(100)
        }
    }
    .conflate() // Пропуск промежуточных значений, если потребитель занят
    .collect {
        println("Collected $it")
        delay(300) // Медленный потребитель
    }
}
```

#### Реальный пример: Обновления локации

```kotlin
import kotlin.random.Random

data class Location(val lat: Double, val lng: Double, val timestamp: Long)

class LocationTracker {
    fun locationUpdates(): Flow<Location> = flow {
        while (true) {
            val location = getCurrentLocation()
            emit(location)
            delay(1000) // Обновление раз в секунду
        }
    }

    private fun getCurrentLocation() = Location(
        lat = Random.nextDouble(),
        lng = Random.nextDouble(),
        timestamp = System.currentTimeMillis()
    )
}

suspend fun trackLocation() {
    LocationTracker()
        .locationUpdates()
        .conflate() // Держим только последнюю локацию при медленном UI
        .collect { location ->
            updateMapUI(location)
            delay(2000) // Медленное обновление UI
        }
}

suspend fun updateMapUI(location: Location) { /* ... */ }
```

### collectLatest() — Отмена и перезапуск

`collectLatest()` отменяет выполнение тела коллекции для предыдущего значения при поступлении нового и начинает обработку заново для последнего. Элементы не теряются на входе, но незавершённая обработка старых значений может быть прервана.

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
        delay(300) // Долгая обработка
        println("Collected $it") // Может не вывестись, если была отмена
    }
}
```

#### Реальный пример: Поиск

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .mapLatest { query ->
            searchApi(query) // Отмена предыдущего запроса при новом query
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    private suspend fun searchApi(query: String): List<Result> {
        delay(500)
        return listOf(Result(query))
    }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

### Сравнение стратегий

```kotlin
suspend fun compareStrategies() {
    println("=== Default (suspending producer) ===")
    testStrategy(null)

    println("\n=== With buffer() ===")
    testStrategy("buffer")

    println("\n=== With conflate() ===")
    testStrategy("conflate")

    println("\n=== With collectLatest() ===")
    testStrategy("collectLatest")
}

suspend fun testStrategy(strategy: String?) {
    val upstream = flow {
        repeat(5) {
            emit(it)
            println("Emitted $it")
            delay(100)
        }
    }

    val time = measureTimeMillis {
        when (strategy) {
            "buffer" -> upstream.buffer().collect { processItem(it) }
            "conflate" -> upstream.conflate().collect { processItem(it) }
            "collectLatest" -> upstream.collectLatest { processItem(it) }
            else -> upstream.collect { processItem(it) }
        }
    }

    println("Total time: $time ms\n")
}

suspend fun processItem(item: Int) {
    delay(300)
    println("Processed $item")
}
```

### Продвинутая конфигурация buffer

```kotlin
flow<Int> {
    repeat(100) { emit(it) }
}
.buffer(
    capacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
.collect { /* обработка */ }

// Стратегии:
// - BufferOverflow.SUSPEND (по умолчанию): приостановить производителя при полном буфере
// - BufferOverflow.DROP_OLDEST: удалить самый старый элемент в буфере
// - BufferOverflow.DROP_LATEST: отбросить элемент, который пытаются эмиттить
```

### Кастомная буферизация через Channel

```kotlin
fun <T> Flow<T>.customBuffer(size: Int): Flow<T> = channelFlow {
    // channelFlow уже предоставляет канал-приёмник; просто перенаправляем значения
    collect { value ->
        send(value) // при превышении размера size отправитель будет приостановлен в соответствии с политикой
    }
}.buffer(size)
```

### Реальные примеры

#### Пример 1: Батчинг аналитики

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
                // Отдельный буфер потребителя для более редких отправок батчей;
                // не влияет на то, как tryEmit работает в SharedFlow
                .buffer(capacity = 50)
                .chunked(10, timeout = 5000)
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
        delay(200)
    }
}

fun <T> Flow<T>.chunked(size: Int, timeout: Long): Flow<List<T>> = flow {
    val batch = mutableListOf<T>()
    var lastEmitTime = 0L

    collect { value ->
        if (batch.isEmpty()) {
            lastEmitTime = System.currentTimeMillis()
        }

        batch.add(value)
        val now = System.currentTimeMillis()

        if (batch.size >= size || (now - lastEmitTime) >= timeout) {
            emit(batch.toList())
            batch.clear()
            lastEmitTime = 0L
        }
    }

    if (batch.isNotEmpty()) {
        emit(batch.toList())
    }
}
// Примечание: для продакшена лучше использовать монотонное время/таймауты корутин; здесь упрощённый пример.
```

#### Пример 2: Обработка данных сенсоров

```kotlin
data class SensorData(val value: Double, val timestamp: Long)

class SensorDataProcessor {
    fun processSensorData(sensorFlow: Flow<SensorData>): Flow<Double> {
        return sensorFlow
            .buffer(capacity = 20)
            .map { data ->
                delay(50)
                data.value * 2
            }
            .scan(0.0) { accumulator, value ->
                (accumulator + value) / 2
            }
    }

    fun processLatestOnly(sensorFlow: Flow<SensorData>): Flow<Double> {
        return sensorFlow
            .conflate()
            .map { data ->
                delay(50)
                data.value * 2
            }
    }
}
```

#### Пример 3: Обновления UI

```kotlin
class DataViewModel : ViewModel() {
    private val dataSource = DataSource()

    // buffer: обработать все обновления
    val allUpdates: StateFlow<List<Item>> = dataSource.updates()
        .buffer(capacity = 50)
        .map { processUpdate(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    // conflate: отображать только последнее
    val latestUpdate: StateFlow<Item?> = dataSource.updates()
        .conflate()
        .map { processUpdate(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = null
        )

    // collectLatest: отменять предыдущую обработку
    val searchResults: StateFlow<List<Result>> = searchQuery
        .debounce(300)
        .mapLatest { query ->
            if (query.isBlank()) emptyList() else searchApi(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    private fun processUpdate(item: Item): Item = item
    private suspend fun searchApi(query: String): List<Result> = emptyList()
}
```

### Производительность и выбор стратегии

| Сценарий | Стратегия | Причина |
|----------|-----------|---------|
| Все значения важны | `buffer()` | Обработать каждое значение, развязать скорости |
| Важно только последнее | `conflate()` | Обновления UI, сенсоры; пропуск устаревших значений |
| Нужно отменять предыдущую работу | `collectLatest()` | Поиск, автодополнение |
| Быстрый производитель, медленный потребитель | `buffer()` | Поглотить всплески, не блокируя сразу производителя |
| Нужен прогресс по шагам | `buffer()` | Не терять промежуточные состояния |
| Нужен только финальный/последний стейт | `conflate()` | Отброс промежуточных состояний |

### Рекомендуемые практики (Best Practices)

DO:

```kotlin
// Используйте buffer для конкурентной обработки
fastFlow
    .buffer()
    .collect { slowConsumer(it) }

// Используйте conflate для источников, где важен только последний стейт
locationFlow
    .conflate()
    .collect { updateUI(it) }

// Используйте collectLatest для отменяемой работы
searchQuery
    .collectLatest { query ->
        searchDatabase(query)
    }

// Ограничивайте размер буфера
flow
    .buffer(capacity = 100)
```

DON'T:

```kotlin
// Не используйте неограниченный буфер без крайней необходимости
flow.buffer(capacity = Channel.UNLIMITED)

// Не применяйте conflate к критичным данным, где важен каждый элемент
importantData.conflate()

// Не добавляйте buffer без причины к тривиальным потокам
flow { emit(1) }.buffer().collect { }

// Не игнорируйте стратегию противодавления при быстрых источниках
fastSensor
    .collect { slowProcessing(it) } // Рассмотрите buffer/conflate/collectLatest
```

---

## Answer (EN)

Backpressure occurs when a producer emits values faster than a consumer can process them. In Kotlin `Flow`, this is handled cooperatively via suspension: a slow collector naturally slows down the producer. `Flow` provides several operators and buffering configurations to choose different backpressure strategies: `buffer()`, `conflate()`, `collectLatest()`, advanced `buffer` options, and `Channel`-based buffering.

### Understanding Backpressure

Without special operators, the default behavior is that the producer is suspended: `emit` suspends until the slow consumer finishes processing the previous element.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

// Default: producer waits for consumer (no extra buffering/backpressure operator)
suspend fun withoutBuffer() {
    val time = measureTimeMillis {
        flow {
            repeat(3) {
                delay(100) // Producer: 100 ms
                emit(it)
                println("Emitted $it")
            }
        }.collect {
            delay(300) // Consumer: 300 ms
            println("Collected $it")
        }
    }
    println("Time: $time ms") // ~1200 ms: (100 + 300) * 3, no overlap
}
```

### buffer() — Parallelizing producer and consumer

`buffer()` lets the producer and consumer run concurrently, partially decoupling their speeds. By default it uses `BufferOverflow.SUSPEND` when the buffer is full.

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
        .buffer() // Producer and consumer can run concurrently
        .collect {
            delay(300)
            println("Collected $it at ${System.currentTimeMillis()}")
        }
    }
    println("Time: $time ms") // Usually about 900–1000 ms due to overlap
}
```

#### buffer with capacity

```kotlin
flow {
    repeat(10) {
        emit(it)
        println("Emitted $it")
    }
}
.buffer(capacity = 5) // Up to 5 elements stored; when full, producer suspends (default behavior)
.collect {
    delay(100)
    println("Collected $it")
}
// When the buffer is full, the producer suspends until there is free space.
```

#### Buffer strategies

```kotlin
// Default buffer (DEFAULT_CAPACITY and BufferOverflow.SUSPEND)
.buffer()

// Explicit capacity
.buffer(capacity = 10)

// Unlimited buffer (use with extreme caution)
.buffer(capacity = Channel.UNLIMITED)

// Conflation-like buffer (effectively keeps only the latest value)
.buffer(capacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)
```

### conflate() — Keep only the latest value

`conflate()` skips intermediate values when the consumer is slow and only delivers the most recent value once the collector is ready again. It is effectively equivalent to `buffer(capacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)`.

```kotlin
suspend fun withConflate() {
    flow {
        repeat(10) {
            emit(it)
            println("Emitted $it")
            delay(100)
        }
    }
    .conflate() // Skip intermediate values while consumer is busy
    .collect {
        println("Collected $it")
        delay(300) // Slow consumer
    }
}
```

#### Real-world example: Location updates

```kotlin
import kotlin.random.Random

data class Location(val lat: Double, val lng: Double, val timestamp: Long)

class LocationTracker {
    fun locationUpdates(): Flow<Location> = flow {
        while (true) {
            val location = getCurrentLocation()
            emit(location)
            delay(1000) // One update per second
        }
    }

    private fun getCurrentLocation() = Location(
        lat = Random.nextDouble(),
        lng = Random.nextDouble(),
        timestamp = System.currentTimeMillis()
    )
}

suspend fun trackLocation() {
    LocationTracker()
        .locationUpdates()
        .conflate() // Keep only the latest location for a slow UI
        .collect { location ->
            updateMapUI(location)
            delay(2000) // Slow UI update
        }
}

suspend fun updateMapUI(location: Location) { /* ... */ }
```

### collectLatest() — Cancel and restart on new value

`collectLatest()` cancels the body of the collector for the previous value when a new value is emitted and restarts processing for the newest value. Values are received, but ongoing work for older values can be cancelled.

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
        println("Collected $it") // May not print if cancelled by a newer value
    }
}
```

#### Real-world example: Search

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .mapLatest { query ->
            searchApi(query) // Previous request is cancelled on new query
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    private suspend fun searchApi(query: String): List<Result> {
        delay(500)
        return listOf(Result(query))
    }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

### Strategy Comparison

```kotlin
suspend fun compareStrategies() {
    println("=== Default (suspending producer) ===")
    testStrategy(null)

    println("\n=== With buffer() ===")
    testStrategy("buffer")

    println("\n=== With conflate() ===")
    testStrategy("conflate")

    println("\n=== With collectLatest() ===")
    testStrategy("collectLatest")
}

suspend fun testStrategy(strategy: String?) {
    val upstream = flow {
        repeat(5) {
            emit(it)
            println("Emitted $it")
            delay(100)
        }
    }

    val time = measureTimeMillis {
        when (strategy) {
            "buffer" -> upstream.buffer().collect { processItem(it) }
            "conflate" -> upstream.conflate().collect { processItem(it) }
            "collectLatest" -> upstream.collectLatest { processItem(it) }
            else -> upstream.collect { processItem(it) }
        }
    }

    println("Total time: $time ms\n")
}

suspend fun processItem(item: Int) {
    delay(300)
    println("Processed $item")
}
```

### Advanced buffer configuration

```kotlin
flow<Int> {
    repeat(100) { emit(it) }
}
.buffer(
    capacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
.collect { /* processing */ }

// Strategies:
// - BufferOverflow.SUSPEND (default): suspend producer when buffer is full
// - BufferOverflow.DROP_OLDEST: drop the oldest element in the buffer
// - BufferOverflow.DROP_LATEST: drop the element being emitted
```

### Custom buffering via Channel

```kotlin
fun <T> Flow<T>.customBuffer(size: Int): Flow<T> = channelFlow {
    // channelFlow already provides a channel; just forward values into it
    collect { value ->
        send(value)
    }
}.buffer(size)
```

### Real-world Examples

#### Example 1: Analytics batching

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
                // Downstream buffer for batching; does not change how tryEmit behaves on SharedFlow
                .buffer(capacity = 50)
                .chunked(10, timeout = 5000)
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
        delay(200)
    }
}

fun <T> Flow<T>.chunked(size: Int, timeout: Long): Flow<List<T>> = flow {
    val batch = mutableListOf<T>()
    var lastEmitTime = 0L

    collect { value ->
        if (batch.isEmpty()) {
            lastEmitTime = System.currentTimeMillis()
        }

        batch.add(value)
        val now = System.currentTimeMillis()

        if (batch.size >= size || (now - lastEmitTime) >= timeout) {
            emit(batch.toList())
            batch.clear()
            lastEmitTime = 0L
        }
    }

    if (batch.isNotEmpty()) {
        emit(batch.toList())
    }
}
// Note: for production code prefer monotonic time or coroutine timeouts; this is a simplified example.
```

#### Example 2: Sensor data processing

```kotlin
data class SensorData(val value: Double, val timestamp: Long)

class SensorDataProcessor {
    fun processSensorData(sensorFlow: Flow<SensorData>): Flow<Double> {
        return sensorFlow
            .buffer(capacity = 20)
            .map { data ->
                delay(50)
                data.value * 2
            }
            .scan(0.0) { accumulator, value ->
                (accumulator + value) / 2
            }
    }

    fun processLatestOnly(sensorFlow: Flow<SensorData>): Flow<Double> {
        return sensorFlow
            .conflate()
            .map { data ->
                delay(50)
                data.value * 2
            }
    }
}
```

#### Example 3: UI updates

```kotlin
class DataViewModel : ViewModel() {
    private val dataSource = DataSource()

    // buffer: handle all updates
    val allUpdates: StateFlow<List<Item>> = dataSource.updates()
        .buffer(capacity = 50)
        .map { processUpdate(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    // conflate: show only the latest
    val latestUpdate: StateFlow<Item?> = dataSource.updates()
        .conflate()
        .map { processUpdate(it) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = null
        )

    // collectLatest: cancel previous work
    val searchResults: StateFlow<List<Result>> = searchQuery
        .debounce(300)
        .mapLatest { query ->
            if (query.isBlank()) emptyList() else searchApi(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    private fun processUpdate(item: Item): Item = item
    private suspend fun searchApi(query: String): List<Result> = emptyList()
}
```

### Performance and Strategy Choice

- All values are important: use `buffer()` to process every value while decoupling producer and consumer.
- Only the latest value matters: use `conflate()` (e.g., UI or sensor updates).
- Need to cancel previous work when new data arrives: use `collectLatest()` (e.g., search/autocomplete).
- Fast producer, slow consumer: `buffer()` to absorb bursts instead of immediately blocking the producer.
- Need step-by-step progress tracking: `buffer()` so you do not lose intermediate states.
- Only final/latest state is needed: `conflate()` to drop intermediate states.

### Recommended Practices (Best Practices)

DO:

```kotlin
// Use buffer for concurrent producer/consumer
fastFlow
    .buffer()
    .collect { slowConsumer(it) }

// Use conflate when only the latest state matters
locationFlow
    .conflate()
    .collect { updateUI(it) }

// Use collectLatest for cancellable work
searchQuery
    .collectLatest { query ->
        searchDatabase(query)
    }

// Always bound your buffers (when possible)
flow
    .buffer(capacity = 100)
```

DON'T:

```kotlin
// Avoid unlimited buffer unless you truly know what you're doing
flow.buffer(capacity = Channel.UNLIMITED)

// Don't conflate critical streams where every element matters
importantData.conflate()

// Don't add buffer blindly to trivial flows
flow { emit(1) }.buffer().collect { }

// Don't ignore backpressure strategy for fast sources
fastSensor
    .collect { slowProcessing(it) } // Consider buffer/conflate/collectLatest
```

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия стратегий противодавления в `Flow` по сравнению с Java Reactive Streams?
- Когда на практике вы выберете `buffer()`, `conflate()` или `collectLatest()`?
- Какие типичные ошибки при использовании этих операторов вы бы назвали?

## Follow-ups

- What are the key differences between these strategies and Java Reactive Streams backpressure?
- When would you use each strategy (`buffer()`, `conflate()`, `collectLatest()`) in practice?
- What are common pitfalls to avoid when using these operators?

## Ссылки (RU)

- Официальная документация Kotlin Flow (буферизация и противодавление)
- [[c-flow]]

## References

- [Kotlin Flow Backpressure](https://kotlinlang.org/docs/flow.html#buffering)
- [Flow buffer](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/buffer.html)
- [Flow conflate](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/conflate.html)

## Связанные вопросы (RU)

### Сложные
- [[q-flow-backpressure-strategies--kotlin--hard]]
- [[q-testing-flow-operators--kotlin--hard]]
- [[q-flow-testing-advanced--kotlin--hard]]

### Базовые / Предпосылки
- [[q-flow-basics--kotlin--easy]]
- [[q-catch-operator-flow--kotlin--medium]]
- [[q-flow-operators-map-filter--kotlin--medium]]

## Related Questions

### Related (Hard)
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-testing-advanced--kotlin--hard]] - Flow

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - Flow
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

## MOC Связи (RU)

- [[moc-kotlin]]

## MOC Links

- [[moc-kotlin]]

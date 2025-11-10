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

**Противодавление** (backpressure) возникает, когда производитель создаёт значения быстрее, чем потребитель может их обработать. `Flow` предоставляет несколько операторов и настроек буферизации для управления этим несоответствием скоростей: `buffer()`, `conflate()`, `collectLatest()`, а также расширенные конфигурации `buffer` и использование `Channel`.

### Понимание Противодавления

Без специальных стратегий противодавление реализуется через приостановку производителя: эмиттер ждёт, пока медленный потребитель закончит обработку.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

// Без buffer - производитель ждёт потребителя
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

### buffer() — Параллельная Обработка

`buffer()` позволяет производителю и потребителю выполняться конкурентно, частично развязывая их скорости.

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
        .buffer() // Производитель и потребитель работают параллельно
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
// Если буфер заполнен, производитель будет suspend до освобождения места.
```

#### Стратегии буфера

```kotlin
// Буфер по умолчанию (дефолтная емкость и BufferOverflow.SUSPEND)
.buffer()

// Явная емкость
.buffer(capacity = 10)

// Неограниченный буфер (использовать с осторожностью)
.buffer(capacity = Channel.UNLIMITED)

// Конфлирующий буфер (хранит только последнее значение)
.buffer(capacity = Channel.CONFLATED)
```

### conflate() — Только Актуальное Значение

`conflate()` пропускает промежуточные значения при медленном потребителе, сохраняя только самое новое при возобновлении обработки.

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

### collectLatest() — Отмена и Перезапуск

`collectLatest()` отменяет выполнение блока коллекции для предыдущего значения при поступлении нового и начинает обработку заново для последнего.

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

### Сравнение Стратегий

```kotlin
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

### Продвинутая Конфигурация buffer

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
// - BufferOverflow.SUSPEND (по умолчанию): приостановить производителя
// - BufferOverflow.DROP_OLDEST: удалить старый элемент в буфере
// - BufferOverflow.DROP_LATEST: отбросить только что эмиттируемый элемент
```

### Кастомная буферизация через Channel

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

### Реальные Примеры

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

### Производительность и Выбор Стратегии

| Сценарий | Стратегия | Причина |
|----------|-----------|---------|
| Все значения важны | `buffer()` | Обработать каждое значение, развязать скорости |
| Важно только последнее | `conflate()` | Обновления UI, сенсоры; пропуск устаревших значений |
| Нужно отменять предыдущую работу | `collectLatest()` | Поиск, автодополнение |
| Быстрый производитель, медленный потребитель | `buffer()` | Поглотить всплески, не блокируя сразу производителя |
| Нужен прогресс по шагам | `buffer()` | Не терять промежуточные состояния |
| Нужен только финальный/последний стейт | `conflate()` | Отброс промежуточных состояний |

### Рекомендуемые Практики (Best Practices)

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

// Не игнорируйте противодавление при быстрых источниках
fastSensor
    .collect { slowProcessing(it) } // Рассмотрите buffer/conflate/collectLatest
```

---

## Answer (EN)

Backpressure occurs when a producer emits values faster than a consumer can process them. `Flow` provides several operators and buffering configurations to control this mismatch: `buffer()`, `conflate()`, `collectLatest()`, advanced `buffer` options, and `Channel`-based buffering. Below is the full detailed explanation mirroring the Russian section.

### Understanding Backpressure

Without any special operators, backpressure in `Flow` is handled by suspending the producer: the emitter waits until the slow collector finishes processing.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

// Without buffer - producer waits for consumer
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

`buffer()` lets producer and consumer run concurrently, partially decoupling their speeds.

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
        .buffer() // Producer and consumer run in parallel
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
.buffer(capacity = 5) // Up to 5 elements stored; producer suspends when buffer is full
.collect {
    delay(100)
    println("Collected $it")
}
// When the buffer is full, the producer suspends until there is free space.
```

#### Buffer strategies

```kotlin
// Default buffer (default capacity and BufferOverflow.SUSPEND)
.buffer()

// Explicit capacity
.buffer(capacity = 10)

// Unlimited buffer (use with care)
.buffer(capacity = Channel.UNLIMITED)

// Conflated buffer (keeps only the latest value)
.buffer(capacity = Channel.CONFLATED)
```

### conflate() — Keep only the latest value

`conflate()` skips intermediate values when the consumer is slow, delivering only the most recent value once the collector is ready again.

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

`collectLatest()` cancels the body of the collector for the previous value when a new value is emitted, and restarts for the newest value.

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
            searchApi(query) // Previous request is cancelled when query changes
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
- Fast producer, slow consumer: `buffer()` to absorb bursts without immediately blocking the producer.
- Need step-by-step progress tracking: `buffer()` so you do not lose intermediate states.
- Only final/latest state is needed: `conflate()`.

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

// Always bound your buffers
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

// Don't ignore backpressure for fast sources
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

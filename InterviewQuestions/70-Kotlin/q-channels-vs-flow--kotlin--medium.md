---
id: kotlin-058
title: "Channels vs Flow / Channels против Flow"
aliases: ["Channels vs Flow, Channels против Flow"]

# Classification
topic: kotlin
subtopics: [async, buffering, channels]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-channels--kotlin--medium, q-kotlin-flow-basics--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [async, buffering, channels, difficulty/medium, flow, kotlin]
---
# Вопрос (RU)
> Когда следует использовать Channels или Flow? Реализуйте буферизованный канал с различными стратегиями емкости и объясните их поведение.

---

# Question (EN)
> When should you use Channels vs Flow? Implement a buffered channel with different capacity strategies and explain their behavior.

## Ответ (RU)

Channels и Flows используются для асинхронных потоков данных, но служат разным целям.

### Ключевые Различия

| Характеристика | Channel | Flow |
|----------------|---------|------|
| **Тип** | Горячий (активный) | Холодный (ленивый) |
| **Выполнение** | Всегда активен | Активируется при сборе |
| **Буферизация** | Встроенный буфер | Нет буфера |
| **Несколько потребителей** | Один (по умолчанию) | Множество независимых |
| **Состояние** | Изменяемое | Неизменяемое |
| **Применение** | Producer-consumer, события | Трансформации данных |
| **Жизненный цикл** | Требует закрытия | Авто-закрытие |

### Стратегии Емкости Channel

#### 1. Rendezvous (по Умолчанию, Емкость = 0)

```kotlin
val channel = Channel<Int>() // или Channel<Int>(Channel.RENDEZVOUS)

/*
Поведение: Нет буфера
- send() приостанавливается пока не вызван receive()
- receive() приостанавливается пока не вызван send()
- Прямая передача между producer и consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>()

    launch {
        for (i in 1..3) {
            println("Отправка $i в ${System.currentTimeMillis()}")
            channel.send(i) // Приостанавливается до получения
            println("Отправлено $i")
        }
        channel.close()
    }

    delay(1000) // Даем отправителю подождать

    for (value in channel) {
        println("Получено $value в ${System.currentTimeMillis()}")
        delay(500)
    }
}

/*
Вывод:
Отправка 1 в 1000
(ожидание...)
Получено 1 в 2000
Отправлено 1
Отправка 2 в 2000
(ожидание...)
Получено 2 в 2500
*/
```

#### 2. Buffered (емкость = n)

```kotlin
val channel = Channel<Int>(capacity = 3)

/*
Поведение: Фиксированный размер буфера
- send() не приостанавливается пока буфер не заполнен
- receive() не приостанавливается пока есть значения
- Разделяет producer от consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>(capacity = 3)

    launch {
        for (i in 1..5) {
            println("Отправка $i")
            channel.send(i)
            println("Отправлено $i (без приостановки для первых 3)")
        }
        channel.close()
    }

    delay(2000) // Даем producer заполнить буфер

    for (value in channel) {
        println("Получено $value")
        delay(500)
    }
}

/*
Вывод:
Отправка 1
Отправлено 1 (без приостановки)
Отправка 2
Отправлено 2 (без приостановки)
Отправка 3
Отправлено 3 (без приостановки)
Отправка 4 (приостанавливается, буфер полон)
(ожидание 2 секунды...)
Получено 1
Отправлено 4
Отправка 5 (приостанавливается)
Получено 2
Отправлено 5
*/
```

#### 3. Unlimited (емкость = UNLIMITED)

```kotlin
val channel = Channel<Int>(Channel.UNLIMITED)

/*
Поведение: Неограниченный буфер
- send() никогда не приостанавливается
- Память растет безгранично
- Опасно если producer быстрее consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        repeat(1000000) { i ->
            channel.send(i) // Никогда не приостанавливается
            if (i % 100000 == 0) {
                println("Отправлено $i элементов")
            }
        }
        channel.close()
    }

    delay(100) // Producer отправляет все мгновенно

    var count = 0
    for (value in channel) {
        count++
        if (count % 100000 == 0) {
            println("Получено $count элементов")
        }
    }
    println("Всего получено: $count")
}

/*
Вывод:
Отправлено 0 элементов
Отправлено 100000 элементов
Отправлено 200000 элементов
... (все отправлено немедленно)
Получено 100000 элементов
Получено 200000 элементов
... (consumer опустошает буфер)
*/
```

#### 4. Conflated (емкость = CONFLATED)

```kotlin
val channel = Channel<Int>(Channel.CONFLATED)

/*
Поведение: Буфер размером 1, отбрасывает старые значения
- send() никогда не приостанавливается
- Хранится только последнее значение
- Старые значения отбрасываются
- Хорошо для обновлений состояния, где важно только последнее
*/

fun main() = runBlocking {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        for (i in 1..10) {
            println("Отправка $i")
            channel.send(i) // Никогда не приостанавливается
            delay(100)
        }
        channel.close()
    }

    delay(1000) // Даем отправителю отправить несколько значений

    for (value in channel) {
        println("Получено $value")
    }
}

/*
Вывод:
Отправка 1
Отправка 2
Отправка 3
...
Отправка 10
Получено 10 (только последнее значение!)
*/
```

### Когда Использовать Channels

1. **Горячие потоки** - Данные производятся независимо от потребителей
2. **Один producer, один consumer**
3. **Шины событий** - Разделенная коммуникация
4. **Пулы воркеров** - Распределение работы
5. **Реал-тайм данные** - Датчики, websockets

```kotlin
// Пример: Пул воркеров с каналами
class WorkerPool(private val workerCount: Int) {
    private val jobs = Channel<Job>(capacity = 100)
    private val results = Channel<Result>(capacity = 100)

    suspend fun start() = coroutineScope {
        repeat(workerCount) { workerId ->
            launch {
                for (job in jobs) {
                    val result = processJob(workerId, job)
                    results.send(result)
                }
            }
        }
    }

    suspend fun submitJob(job: Job) {
        jobs.send(job)
    }

    suspend fun getResult(): Result {
        return results.receive()
    }
}
```

### Когда Использовать Flow

1. **Холодные потоки** - Ленивые вычисления по требованию
2. **Трансформации данных** - map, filter, reduce
3. **Множество независимых коллекторов**
4. **Реактивные потоки** - Обновления UI, запросы к БД
5. **Композиция** - Сложные трансформационные конвейеры

```kotlin
// Пример: Трансформация данных с Flow
class UserRepository {
    fun getUserUpdates(userId: Int): Flow<User> = flow {
        while (true) {
            val user = fetchUser(userId)
            emit(user)
            delay(5000)
        }
    }
    .distinctUntilChanged()
    .map { user -> user.copy(name = user.name.uppercase()) }
    .catch { emit(User.DEFAULT) }
}

// Множественные коллекторы работают независимо
userRepository.getUserUpdates(123)
    .collect { user1 -> updateUI1(user1) }

userRepository.getUserUpdates(123)
    .collect { user2 -> updateUI2(user2) }
// Каждый коллектор получает независимый поток!
```

### Полный Пример: Все Типы Буферов

```kotlin
suspend fun demonstrateBufferTypes() {
    // Rendezvous - прямая передача
    println("=== RENDEZVOUS ===")
    val rendezvous = Channel<Int>(Channel.RENDEZVOUS)
    testChannel(rendezvous, "Rendezvous")

    // Buffered - фиксированная емкость
    println("\n=== BUFFERED (3) ===")
    val buffered = Channel<Int>(3)
    testChannel(buffered, "Buffered")

    // Unlimited - никогда не приостанавливается
    println("\n=== UNLIMITED ===")
    val unlimited = Channel<Int>(Channel.UNLIMITED)
    testChannel(unlimited, "Unlimited")

    // Conflated - хранит только последнее
    println("\n=== CONFLATED ===")
    val conflated = Channel<Int>(Channel.CONFLATED)
    testChannel(conflated, "Conflated")
}

suspend fun testChannel(channel: Channel<Int>, name: String) = coroutineScope {
    launch {
        repeat(5) { i ->
            println("[$name] Отправка $i")
            channel.send(i)
            println("[$name] Отправлено $i")
        }
        channel.close()
    }

    delay(500) // Даем producer поработать

    for (value in channel) {
        println("[$name] Получено $value")
        delay(200)
    }
}
```

### Реальный Пример: Шина Событий С Channels

```kotlin
sealed class AppEvent {
    data class UserLoggedIn(val userId: Int) : AppEvent()
    data class UserLoggedOut(val userId: Int) : AppEvent()
    data class MessageReceived(val message: String) : AppEvent()
}

class EventBus {
    private val events = Channel<AppEvent>(capacity = Channel.BUFFERED)

    suspend fun publish(event: AppEvent) {
        events.send(event)
    }

    fun subscribe(): ReceiveChannel<AppEvent> = events

    fun close() {
        events.close()
    }
}

// Использование
val eventBus = EventBus()

// Подписчик 1: Логирование
launch {
    for (event in eventBus.subscribe()) {
        logger.log("Событие: $event")
    }
}

// Подписчик 2: Аналитика
launch {
    for (event in eventBus.subscribe()) {
        when (event) {
            is AppEvent.UserLoggedIn -> trackLogin(event.userId)
            is AppEvent.UserLoggedOut -> trackLogout(event.userId)
            else -> {}
        }
    }
}

// Publisher
eventBus.publish(AppEvent.UserLoggedIn(123))
```

### Реальный Пример: Конвейер Данных С Flow

```kotlin
class DataPipeline {
    fun processStream(): Flow<ProcessedData> = fetchRawData()
        .buffer(capacity = 50) // Добавляем буферизацию
        .map { raw -> validate(raw) }
        .filter { it.isValid }
        .map { validated -> transform(validated) }
        .catch { exception ->
            logger.error("Ошибка конвейера", exception)
            emit(ProcessedData.ERROR)
        }
        .flowOn(Dispatchers.IO) // Выполнять на IO диспетчере

    private fun fetchRawData(): Flow<RawData> = flow {
        while (true) {
            val data = database.fetchNext()
            emit(data)
        }
    }
}

// Множественные независимые потребители
val pipeline = DataPipeline()

// UI коллектор
pipeline.processStream()
    .collect { data -> updateUI(data) }

// Коллектор хранилища
pipeline.processStream()
    .collect { data -> saveToCache(data) }
```

### Лучшие Практики

1. **Выбирайте на основе горячий vs холодный**:
   ```kotlin
   // Горячий: Channels для реал-тайм событий
   val sensorData = Channel<SensorReading>()

   // Холодный: Flow для данных по требованию
   val userData = flow { emit(fetchUser()) }
   ```

2. **Всегда закрывайте каналы**:
   ```kotlin
   val channel = Channel<Int>()
   try {
       channel.send(1)
   } finally {
       channel.close() // Предотвратить утечки
   }
   ```

3. **Используйте подходящую емкость**:
   ```kotlin
   // Быстрый producer, медленный consumer
   Channel<Int>(capacity = 100)

   // Обновления состояния
   Channel<State>(Channel.CONFLATED)

   // Синхронизированные операции
   Channel<Request>(Channel.RENDEZVOUS)
   ```

4. **Предпочитайте Flow для трансформаций**:
   ```kotlin
   //  Flow лучше для этого
   flow { emit(data) }
       .map { transform(it) }
       .filter { isValid(it) }

   //  Неудобно с каналами
   val ch1 = Channel<Data>()
   val ch2 = Channel<Transformed>()
   // Нужна ручная передача
   ```

### Распространенные Ошибки

1. **Забывание закрытия каналов**:
   ```kotlin
   //  Утечка
   val ch = Channel<Int>()
   ch.send(1)
   // Никогда не закрыт!

   //  Всегда закрывать
   try { ch.send(1) }
   finally { ch.close() }
   ```

2. **Небрежное использование UNLIMITED**:
   ```kotlin
   //  Риск OutOfMemoryError
   val ch = Channel<ByteArray>(Channel.UNLIMITED)
   repeat(1000000) { ch.send(ByteArray(1024)) }

   //  Используйте ограниченную емкость
   val ch = Channel<ByteArray>(100)
   ```

3. **Неправильный выбор для случая использования**:
   ```kotlin
   //  Channel для трансформации данных
   val ch = Channel<Int>()
   launch { for (i in ch) process(i) }

   //  Flow для трансформации данных
   flowOf(1,2,3).map { process(it) }.collect()
   ```

### Преобразование Между Channels И Flow

```kotlin
// Flow -> Channel (производит в канал)
fun <T> Flow<T>.produceIn(scope: CoroutineScope): ReceiveChannel<T> =
    scope.produce {
        collect { send(it) }
    }

// Channel -> Flow (потребляет из канала)
fun <T> ReceiveChannel<T>.consumeAsFlow(): Flow<T> = flow {
    for (value in this@consumeAsFlow) {
        emit(value)
    }
}

// Использование
val flow = flowOf(1, 2, 3, 4, 5)
val channel = flow.produceIn(GlobalScope)

val newFlow = channel.consumeAsFlow()
```

### Соображения Производительности

```kotlin
// Channel: Горячий, накладные расходы памяти на буфер
val channel = Channel<Int>(1000)
// Хранит 1000 элементов в памяти даже если нет потребителя

// Flow: Холодный, нет накладных расходов памяти до сбора
val flow = flow { emit(data) }
// Не используется память до вызова collect()

// Для одного потребителя, предпочитайте Flow
// Для нескольких потребителей с общим состоянием, используйте Channel
```

**Краткое содержание**: Channels - горячие, stateful примитивы коммуникации для producer-consumer паттернов, Flow - холодные функциональные реактивные потоки для трансформаций данных. Channels поддерживают буферизацию: RENDEZVOUS (без буфера), BUFFERED (фиксированный размер), UNLIMITED (безграничный), CONFLATED (только последнее). Используйте Channels для шин событий и пулов воркеров, Flows для реактивных потоков данных. Всегда закрывайте каналы. Выбирайте на основе требований горячий vs холодный и необходимости общего состояния.

---

## Answer (EN)

Channels and Flows are both used for asynchronous data streams, but they serve different purposes and have distinct characteristics.

### Key Differences

| Feature | Channel | Flow |
|---------|---------|------|
| **Type** | Hot (eager) | Cold (lazy) |
| **Execution** | Always active | Activates on collection |
| **Buffering** | Built-in buffer | No buffer (unless explicitly added) |
| **Backpressure** | Suspension | Suspension/operators |
| **Multiple consumers** | Single consumer (by default) | Multiple independent collectors |
| **State** | Mutable, stateful | Immutable, functional |
| **Use case** | Producer-consumer, events | Data transformations, reactive streams |
| **Lifecycle** | Manual close required | Auto-closed on completion |

### Channel Basics

Channels are hot streams for communication between coroutines - like a thread-safe queue.

```kotlin
// Basic channel usage
fun main() = runBlocking {
    val channel = Channel<Int>()

    // Producer
    launch {
        for (x in 1..5) {
            println("Sending $x")
            channel.send(x)
        }
        channel.close() // Must close manually
    }

    // Consumer
    launch {
        for (x in channel) {
            println("Received $x")
            delay(100)
        }
    }
}
```

### Channel Capacity Strategies

Channels support different buffering strategies via capacity parameter:

#### 1. Rendezvous (Default, Capacity = 0)

```kotlin
val channel = Channel<Int>() // or Channel<Int>(Channel.RENDEZVOUS)

/*
Behavior: No buffer
- send() suspends until receive() is called
- receive() suspends until send() is called
- Direct handoff between producer and consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>()

    launch {
        for (i in 1..3) {
            println("Sending $i at ${System.currentTimeMillis()}")
            channel.send(i) // Suspends until received
            println("Sent $i")
        }
        channel.close()
    }

    delay(1000) // Let sender wait

    for (value in channel) {
        println("Received $value at ${System.currentTimeMillis()}")
        delay(500)
    }
}

/*
Output:
Sending 1 at 1000
(waits...)
Received 1 at 2000
Sent 1
Sending 2 at 2000
(waits...)
Received 2 at 2500
*/
```

#### 2. Buffered (capacity = n)

```kotlin
val channel = Channel<Int>(capacity = 3)

/*
Behavior: Fixed size buffer
- send() doesn't suspend until buffer is full
- receive() doesn't suspend while buffer has values
- Decouples producer from consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>(capacity = 3)

    launch {
        for (i in 1..5) {
            println("Sending $i")
            channel.send(i)
            println("Sent $i (no suspend for first 3)")
        }
        channel.close()
    }

    delay(2000) // Let producer fill buffer

    for (value in channel) {
        println("Received $value")
        delay(500)
    }
}

/*
Output:
Sending 1
Sent 1 (no suspend)
Sending 2
Sent 2 (no suspend)
Sending 3
Sent 3 (no suspend)
Sending 4 (suspends, buffer full)
(waits 2 seconds...)
Received 1
Sent 4
Sending 5 (suspends)
Received 2
Sent 5
*/
```

#### 3. Unlimited (capacity = UNLIMITED)

```kotlin
val channel = Channel<Int>(Channel.UNLIMITED)

/*
Behavior: Unlimited buffer
- send() never suspends
- Memory grows unbounded
- Dangerous if producer faster than consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        repeat(1000000) { i ->
            channel.send(i) // Never suspends
            if (i % 100000 == 0) {
                println("Sent $i items")
            }
        }
        channel.close()
    }

    delay(100) // Producer sends all instantly

    var count = 0
    for (value in channel) {
        count++
        if (count % 100000 == 0) {
            println("Received $count items")
        }
    }
    println("Total received: $count")
}

/*
Output:
Sent 0 items
Sent 100000 items
Sent 200000 items
... (all sent immediately)
Received 100000 items
Received 200000 items
... (consumer drains buffer)
*/
```

#### 4. Conflated (capacity = CONFLATED)

```kotlin
val channel = Channel<Int>(Channel.CONFLATED)

/*
Behavior: Buffer size 1, drops old values
- send() never suspends
- Only most recent value kept
- Old values discarded
- Good for state updates where only latest matters
*/

fun main() = runBlocking {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        for (i in 1..10) {
            println("Sending $i")
            channel.send(i) // Never suspends
            delay(100)
        }
        channel.close()
    }

    delay(1000) // Let sender send multiple values

    for (value in channel) {
        println("Received $value")
    }
}

/*
Output:
Sending 1
Sending 2
Sending 3
...
Sending 10
Received 10 (only latest value!)
*/
```

### Complete Example: All Buffer Types

```kotlin
suspend fun demonstrateBufferTypes() {
    // Rendezvous - direct handoff
    println("=== RENDEZVOUS ===")
    val rendezvous = Channel<Int>(Channel.RENDEZVOUS)
    testChannel(rendezvous, "Rendezvous")

    // Buffered - fixed capacity
    println("\n=== BUFFERED (3) ===")
    val buffered = Channel<Int>(3)
    testChannel(buffered, "Buffered")

    // Unlimited - never suspends
    println("\n=== UNLIMITED ===")
    val unlimited = Channel<Int>(Channel.UNLIMITED)
    testChannel(unlimited, "Unlimited")

    // Conflated - keeps only latest
    println("\n=== CONFLATED ===")
    val conflated = Channel<Int>(Channel.CONFLATED)
    testChannel(conflated, "Conflated")
}

suspend fun testChannel(channel: Channel<Int>, name: String) = coroutineScope {
    launch {
        repeat(5) { i ->
            println("[$name] Sending $i")
            channel.send(i)
            println("[$name] Sent $i")
        }
        channel.close()
    }

    delay(500) // Let producer work

    for (value in channel) {
        println("[$name] Received $value")
        delay(200)
    }
}
```

### When to Use Channels Vs Flow

#### Use Channels When:

1. **Hot streams** - Data is produced regardless of consumers
2. **Single producer, single consumer**
3. **Event buses** - Decoupled communication
4. **Worker pools** - Distributing work
5. **Real-time data** - Sensor data, websockets

```kotlin
// Example: Worker pool with channels
class WorkerPool(private val workerCount: Int) {
    private val jobs = Channel<Job>(capacity = 100)
    private val results = Channel<Result>(capacity = 100)

    suspend fun start() = coroutineScope {
        // Start workers
        repeat(workerCount) { workerId ->
            launch {
                for (job in jobs) {
                    val result = processJob(workerId, job)
                    results.send(result)
                }
            }
        }
    }

    suspend fun submitJob(job: Job) {
        jobs.send(job)
    }

    suspend fun getResult(): Result {
        return results.receive()
    }

    fun close() {
        jobs.close()
        results.close()
    }
}
```

#### Use Flow When:

1. **Cold streams** - Lazy, on-demand computation
2. **Data transformations** - map, filter, reduce
3. **Multiple independent collectors**
4. **Reactive streams** - UI updates, database queries
5. **Composition** - Complex transformation pipelines

```kotlin
// Example: Data transformation with Flow
class UserRepository {
    fun getUserUpdates(userId: Int): Flow<User> = flow {
        while (true) {
            val user = fetchUser(userId)
            emit(user)
            delay(5000)
        }
    }
    .distinctUntilChanged() // Only emit when changed
    .map { user -> user.copy(name = user.name.uppercase()) }
    .catch { emit(User.DEFAULT) }
}

// Multiple collectors work independently
userRepository.getUserUpdates(123)
    .collect { user1 -> updateUI1(user1) }

userRepository.getUserUpdates(123)
    .collect { user2 -> updateUI2(user2) }
// Each collector gets independent stream!
```

### Converting Between Channels and Flow

```kotlin
// Flow -> Channel (produces to channel)
fun <T> Flow<T>.produceIn(scope: CoroutineScope): ReceiveChannel<T> =
    scope.produce {
        collect { send(it) }
    }

// Channel -> Flow (consumes from channel)
fun <T> ReceiveChannel<T>.consumeAsFlow(): Flow<T> = flow {
    for (value in this@consumeAsFlow) {
        emit(value)
    }
}

// Usage
val flow = flowOf(1, 2, 3, 4, 5)
val channel = flow.produceIn(GlobalScope)

val newFlow = channel.consumeAsFlow()
```

### Real-world Example: Event Bus with Channels

```kotlin
sealed class AppEvent {
    data class UserLoggedIn(val userId: Int) : AppEvent()
    data class UserLoggedOut(val userId: Int) : AppEvent()
    data class MessageReceived(val message: String) : AppEvent()
}

class EventBus {
    private val events = Channel<AppEvent>(capacity = Channel.BUFFERED)

    suspend fun publish(event: AppEvent) {
        events.send(event)
    }

    fun subscribe(): ReceiveChannel<AppEvent> = events

    fun close() {
        events.close()
    }
}

// Usage
val eventBus = EventBus()

// Subscriber 1: Logging
launch {
    for (event in eventBus.subscribe()) {
        logger.log("Event: $event")
    }
}

// Subscriber 2: Analytics
launch {
    for (event in eventBus.subscribe()) {
        when (event) {
            is AppEvent.UserLoggedIn -> trackLogin(event.userId)
            is AppEvent.UserLoggedOut -> trackLogout(event.userId)
            else -> {}
        }
    }
}

// Publisher
eventBus.publish(AppEvent.UserLoggedIn(123))
```

### Real-world Example: Data Pipeline with Flow

```kotlin
class DataPipeline {
    fun processStream(): Flow<ProcessedData> = fetchRawData()
        .buffer(capacity = 50) // Add buffering
        .map { raw -> validate(raw) }
        .filter { it.isValid }
        .map { validated -> transform(validated) }
        .catch { exception ->
            logger.error("Pipeline error", exception)
            emit(ProcessedData.ERROR)
        }
        .flowOn(Dispatchers.IO) // Run on IO dispatcher

    private fun fetchRawData(): Flow<RawData> = flow {
        while (true) {
            val data = database.fetchNext()
            emit(data)
        }
    }
}

// Multiple independent consumers
val pipeline = DataPipeline()

// UI collector
pipeline.processStream()
    .collect { data -> updateUI(data) }

// Storage collector
pipeline.processStream()
    .collect { data -> saveToCache(data) }
```

### Performance Considerations

```kotlin
// Channel: Hot, memory overhead for buffer
val channel = Channel<Int>(1000)
// Holds 1000 items in memory even if no consumer

// Flow: Cold, no memory overhead until collected
val flow = flow { emit(data) }
// No memory used until collect() called

// For single consumer, prefer Flow
// For multiple consumers with shared state, use Channel
```

### Best Practices

1. **Choose based on hot vs cold**:
   ```kotlin
   // Hot: Channels for real-time events
   val sensorData = Channel<SensorReading>()

   // Cold: Flow for on-demand data
   val userData = flow { emit(fetchUser()) }
   ```

2. **Always close channels**:
   ```kotlin
   val channel = Channel<Int>()
   try {
       channel.send(1)
   } finally {
       channel.close() // Prevent leaks
   }
   ```

3. **Use appropriate capacity**:
   ```kotlin
   // Fast producer, slow consumer
   Channel<Int>(capacity = 100) // Buffer

   // State updates
   Channel<State>(Channel.CONFLATED) // Latest only

   // Synchronized operations
   Channel<Request>(Channel.RENDEZVOUS) // Direct handoff
   ```

4. **Prefer Flow for transformations**:
   ```kotlin
   //  Flow is better for this
   flow { emit(data) }
       .map { transform(it) }
       .filter { isValid(it) }

   //  Awkward with channels
   val ch1 = Channel<Data>()
   val ch2 = Channel<Transformed>()
   // Manual piping needed
   ```

### Common Pitfalls

1. **Forgetting to close channels**:
   ```kotlin
   //  Leak
   val ch = Channel<Int>()
   ch.send(1)
   // Never closed!

   //  Always close
   val ch = Channel<Int>()
   try { ch.send(1) }
   finally { ch.close() }
   ```

2. **Using UNLIMITED carelessly**:
   ```kotlin
   //  OutOfMemoryError risk
   val ch = Channel<ByteArray>(Channel.UNLIMITED)
   repeat(1000000) { ch.send(ByteArray(1024)) }

   //  Use bounded capacity
   val ch = Channel<ByteArray>(100)
   ```

3. **Wrong choice for use case**:
   ```kotlin
   //  Channel for data transformation
   val ch = Channel<Int>()
   launch { for (i in ch) process(i) }

   //  Flow for data transformation
   flowOf(1,2,3).map { process(it) }.collect()
   ```

**English Summary**: Channels are hot, stateful communication primitives for producer-consumer patterns, while Flows are cold, functional reactive streams for data transformations. Channels support buffering with strategies: RENDEZVOUS (no buffer), BUFFERED (fixed size), UNLIMITED (unbounded), and CONFLATED (latest only). Use Channels for event buses and worker pools, Flows for reactive data streams. Always close channels to prevent leaks. Choose based on hot vs cold requirements and whether you need shared state.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [Channels - Kotlin Coroutines Guide](https://kotlinlang.org/docs/channels.html)
- [Flow - Kotlin Documentation](https://kotlinlang.org/docs/flow.html)
- [Channel capacity - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/)

## Related Questions

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - Flow
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Coroutines

### Related (Medium)
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - StateFlow & SharedFlow differences

### Advanced (Harder)
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies

---
id: kotlin-058
title: "Channels vs Flow / Channels против Flow"
aliases: ["Channels vs Flow", "Channels против Flow"]

# Classification
topic: kotlin
subtopics: [channels, coroutines, flow]
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
related: [c-coroutines, c-kotlin, q-kotlin-channels--kotlin--medium, q-kotlin-flow-basics--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-11-10

tags: [async, buffering, channels, difficulty/medium, flow, kotlin]
date created: Friday, October 17th 2025, 11:24:31 am
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---
# Вопрос (RU)
> Когда следует использовать Channels или `Flow`? Реализуйте буферизованный канал с различными стратегиями емкости и объясните их поведение.

---

# Question (EN)
> When should you use Channels vs `Flow`? Implement a buffered channel with different capacity strategies and explain their behavior.

## Ответ (RU)

Channels и `Flow` используются для асинхронных потоков данных, но служат разным целям.

### Ключевые Различия

| Характеристика | Channel | Flow |
|----------------|---------|------|
| **Тип** | Горячий (используется активными продюсерами/консюмерами) | Холодный (ленивый) |
| **Выполнение** | Используется активными корутинами, существующий канал может принимать данные в любой момент | Активируется при collect() |
| **Буферизация** | Встроенные стратегии емкости канала | Нет встроенного канального буфера по умолчанию (но есть buffer()/conflate() и операторные буферы) |
| **Обратное давление** | Приостановка send()/receive() в зависимости от емкости | Приостановка и операторы управляют скоростью и спросом |
| **Несколько потребителей** | Один потребитель по умолчанию; несколько конкурирующих потребителей разделяют элементы | Множество независимых коллекторов, каждый запускает источник заново |
| **Состояние** | Изменяемое, stateful коммуникация | Иммутабельный, декларативный pipeline значений |
| **Применение** | Producer-consumer, очереди задач, события между корутинами | Трансформации данных, реактивные потоки |
| **Жизненный цикл** | Требует явного закрытия (или завершения продюсеров) | Автоматически завершается при завершении источника |

### Основы Channel

Каналы — это горячий примитив коммуникации между корутинами, похожий на безопасную очередь.

```kotlin
// Базовое использование Channel
fun main() = runBlocking {
    val channel = Channel<Int>()

    // Продюсер
    launch {
        for (x in 1..5) {
            println("Отправка $x")
            channel.send(x)
        }
        channel.close() // Закрываем, когда закончили производить
    }

    // Консюмер
    launch {
        for (x in channel) {
            println("Получено $x")
            delay(100)
        }
    }
}
```

### Стратегии Емкости Channel

#### 1. Rendezvous (по Умолчанию, Емкость = 0)

```kotlin
val channel = Channel<Int>() // или Channel<Int>(Channel.RENDEZVOUS)

/*
Поведение: Нет буфера по емкости
- send() приостанавливается, пока соответствующий receive() не будет готов
- receive() приостанавливается, пока не будет выполнен send()
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
```

#### 2. Buffered (емкость = n)

```kotlin
val channel = Channel<Int>(capacity = 3)

/*
Поведение: Фиксированный размер буфера
- send() не приостанавливается, пока буфер не заполнен
- receive() не приостанавливается, пока в буфере есть значения
- Частично разделяет скорость producer и consumer
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
```

#### 3. Unlimited (емкость = UNLIMITED)

```kotlin
val channel = Channel<Int>(Channel.UNLIMITED)

/*
Поведение: Неограниченный буфер (по емкости в терминах API)
- send() не приостанавливается из-за заполнения буфера
- Память может расти безгранично
- Опасно, если producer существенно быстрее consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        repeat(1000000) { i ->
            channel.send(i)
            if (i % 100000 == 0) {
                println("Отправлено $i элементов")
            }
        }
        channel.close()
    }

    delay(100)

    var count = 0
    for (value in channel) {
        count++
        if (count % 100000 == 0) {
            println("Получено $count элементов")
        }
    }
    println("Всего получено: $count")
}
```

#### 4. Conflated (емкость = CONFLATED)

```kotlin
val channel = Channel<Int>(Channel.CONFLATED)

/*
Поведение: По сути буфер размером 1, старые значения заменяются новыми
- send() не приостанавливается из-за заполнения буфера
- Хранится только последнее значение
- Старые значения отбрасываются
- Подходит для обновлений состояния, где важно только последнее
*/

fun main() = runBlocking {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        for (i in 1..10) {
            println("Отправка $i")
            channel.send(i)
            delay(100)
        }
        channel.close()
    }

    delay(1000) // Даем отправителю отправить несколько значений

    for (value in channel) {
        println("Получено $value")
    }
}
```

### Когда Использовать Channels Vs Flow

#### Когда Использовать Channels

1. **Горячие потоки** — данные производятся независимо от того, есть ли текущие потребители
2. **Один producer, один consumer** или несколько конкурирующих consumers как очередь задач
3. **Очереди событий/работы** — разделенная коммуникация между корутинами
4. **Пулы воркеров** — распределение работы между конкурентами
5. **Реал-тайм данные** — датчики, websockets (один поток потребления или явный fan-out)

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

    fun close() {
        jobs.close()
        results.close()
    }
}
```

#### Когда Использовать Flow

1. **Холодные потоки** — ленивые вычисления по требованию
2. **Трансформации данных** — map, filter, reduce
3. **Множество независимых коллекторов**, каждый получает свой независимый запуск
4. **Реактивные потоки** — обновления UI, запросы к БД
5. **Композиция** — сложные трансформационные конвейеры

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
// Каждый collect запускает новый поток запросов
```

### Преобразование Между Channel И Flow

```kotlin
// Flow -> Channel (производим значения Flow в Channel)
fun <T> Flow<T>.produceIn(scope: CoroutineScope): ReceiveChannel<T> =
    scope.produce {
        collect { send(it) }
    }

// Channel -> Flow (потребляем значения Channel как Flow)
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

### Реальный Пример: Шина Событий С Channel (очередь, Не broadcast)

```kotlin
sealed class AppEvent {
    data class UserLoggedIn(val userId: Int) : AppEvent()
    data class UserLoggedOut(val userId: Int) : AppEvent()
    data class MessageReceived(val message: String) : AppEvent()
}

class EventBus {
    // Channel используется как очередь событий.
    // Потребители, читающие из одного ReceiveChannel, будут делить события между собой.
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

> Примечание: В этом примере подписчики конкурируют за события одного канала и не получают полную копию потока. Для broadcast-семантики лучше использовать `SharedFlow`/`StateFlow` или явный fan-out.

### Реальный Пример: Конвейер Данных С Flow

```kotlin
class DataPipeline {
    fun processStream(): Flow<ProcessedData> = fetchRawData()
        .buffer(capacity = 50) // Добавляем буферизацию между стадиями
        .map { raw -> validate(raw) }
        .filter { it.isValid }
        .map { validated -> transform(validated) }
        .catch { exception ->
            logger.error("Ошибка конвейера", exception)
            emit(ProcessedData.ERROR)
        }
        .flowOn(Dispatchers.IO)

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

### Соображения Производительности

```kotlin
// Channel: горячий примитив синхронизации/очередь с буфером
val channel = Channel<Int>(1000)
// Может удерживать до 1000 элементов в памяти, даже если потребитель временно отсутствует

// Flow: холодный, вычисления запускаются при collect()
val flow = flow { emit(data) }
// Память под элементы не используется до момента эмиссии и коллекции

// Для одного потребителя и декларативных трансформаций чаще предпочтителен Flow
// Для распределения работы между конкурентами (очередь задач) используйте Channel
```

### Лучшие Практики

1. **Выбирайте на основе горячий vs холодный**:
   ```kotlin
   // Горячий источник: Channel для реал-тайм событий (один/конкурирующие потребители)
   val sensorData = Channel<SensorReading>()

   // Холодный источник: Flow для данных по требованию
   val userData = flow { emit(fetchUser()) }
   ```

2. **Следите за жизненным циклом и закрытием каналов**:
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

   // Обновления состояния (важно только последнее)
   Channel<State>(Channel.CONFLATED)

   // Синхронизированные операции: прямая передача
   Channel<Request>(Channel.RENDEZVOUS)
   ```

4. **Предпочитайте Flow для трансформаций**:
   ```kotlin
   // Flow естественно подходит для цепочек операторов
   flow { emit(data) }
       .map { transform(it) }
       .filter { isValid(it) }

   // С каналами пришлось бы вручную строить pipeline
   val ch1 = Channel<Data>()
   val ch2 = Channel<Transformed>()
   ```

### Распространенные Ошибки

1. **Забывание закрытия каналов, управляемых вручную**:
   ```kotlin
   // Потенциальная утечка
   val ch = Channel<Int>()
   ch.send(1)
   // ch никогда не закрывается

   // Лучше явно закрывать, когда источник завершён
   val ch2 = Channel<Int>()
   try { ch2.send(1) }
   finally { ch2.close() }
   ```

2. **Небрежное использование UNLIMITED**:
   ```kotlin
   // Риск OutOfMemoryError
   val ch = Channel<ByteArray>(Channel.UNLIMITED)
   repeat(1000000) { ch.send(ByteArray(1024)) }

   // Используйте ограниченную емкость
   val bounded = Channel<ByteArray>(100)
   ```

3. **Неправильный выбор примитива**:
   ```kotlin
   // Использование Channel для чистых трансформаций усложняет код
   val ch = Channel<Int>()
   launch { for (i in ch) process(i) }

   // Для трансформаций удобнее Flow
   flowOf(1, 2, 3).map { process(it) }.collect()
   ```

**Краткое содержание**: Channel — горячий примитив коммуникации и очереди между корутинами для producer-consumer и распределения задач. Flow — холодный декларативный поток значений для трансформаций и реактивных сценариев. Каналы поддерживают стратегии емкости: RENDEZVOUS (без буфера по емкости), BUFFERED (фиксированный размер), UNLIMITED (без ограничений по емкости), CONFLATED (только последнее значение). Выбирайте на основе горячего vs холодного поведения и семантики очереди/трансформаций, аккуратно управляйте емкостью и жизненным циклом и явно закрывайте каналы, которые вы контролируете.

---

## Answer (EN)

Channels and `Flow`s are both used for asynchronous data streams, but they serve different purposes and have distinct characteristics.

### Key Differences

| Feature | Channel | Flow |
|---------|---------|------|
| **Type** | Hot-style primitive used by active producers/consumers | Cold (lazy) |
| **Execution** | Used by running coroutines; an existing channel can receive/send at any time | Starts work only when collected |
| **Buffering** | Built-in capacity strategies on the channel itself | No inherent channel buffer by default (but buffer()/conflate() and operators can add buffering) |
| **Backpressure** | Suspension on send/receive based on capacity | Suspension/flow operators coordinate demand |
| **Multiple consumers** | Single consumer by default; multiple consumers share work (competing receivers) | Multiple independent collectors, each re-runs the upstream |
| **State** | Mutable, stateful communication | Immutable, declarative pipeline |
| **Use case** | Producer-consumer queues, task distribution, inter-coroutine events | Data transformations, reactive streams, UI/data updates |
| **Lifecycle** | Needs explicit close (or producer completion helpers) | Auto-completes when upstream finishes |

### Channel Basics

Channels are hot-style primitives for communication between coroutines, similar to a coroutine-safe queue.

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
        channel.close() // Close when done producing
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

Channels support different buffering strategies via the capacity parameter:

#### 1. Rendezvous (Default, Capacity = 0)

```kotlin
val channel = Channel<Int>() // or Channel<Int>(Channel.RENDEZVOUS)

/*
Behavior: No capacity buffer
- send() suspends until a matching receive() is ready
- receive() suspends until send() is called
- Direct handoff between producer and consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>()

    launch {
        for (i in 1..3) {
            println("Sending $i at ${System.currentTimeMillis()}")
            channel.send(i)
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
```

#### 2. Buffered (capacity = n)

```kotlin
val channel = Channel<Int>(capacity = 3)

/*
Behavior: Fixed size buffer
- send() does not suspend until the buffer is full
- receive() does not suspend while the buffer has values
- Partially decouples producer and consumer speeds
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

    delay(2000) // Let producer fill the buffer

    for (value in channel) {
        println("Received $value")
        delay(500)
    }
}
```

#### 3. Unlimited (capacity = UNLIMITED)

```kotlin
val channel = Channel<Int>(Channel.UNLIMITED)

/*
Behavior: Unbounded buffer (by capacity setting)
- send() does not suspend due to buffer being full
- Memory usage can grow without bound
- Dangerous if producer is much faster than consumer
*/

fun main() = runBlocking {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        repeat(1000000) { i ->
            channel.send(i)
            if (i % 100000 == 0) {
                println("Sent $i items")
            }
        }
        channel.close()
    }

    delay(100)

    var count = 0
    for (value in channel) {
        count++
        if (count % 100000 == 0) {
            println("Received $count items")
        }
    }
    println("Total received: $count")
}
```

#### 4. Conflated (capacity = CONFLATED)

```kotlin
val channel = Channel<Int>(Channel.CONFLATED)

/*
Behavior: Effectively buffer size 1, keeps only latest
- send() does not suspend due to capacity
- Only the most recent value is retained
- Older values are dropped
- Good for state updates where only the latest matters
*/

fun main() = runBlocking {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        for (i in 1..10) {
            println("Sending $i")
            channel.send(i)
            delay(100)
        }
        channel.close()
    }

    delay(1000) // Let sender send multiple values

    for (value in channel) {
        println("Received $value")
    }
}
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

    // Unlimited - no suspension due to capacity
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

1. **Hot-style communication** - data is produced regardless of active collectors
2. **Single producer/single consumer**, or multiple competing consumers sharing a work queue
3. **Event/task queues** - decoupled communication between coroutines
4. **Worker pools** - distributing work across coroutines
5. **Real-time data** - sensors, websockets (with clear semantics: single consumer or explicit fan-out)

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

1. **Cold streams** - lazy, on-demand computations
2. **Data transformations** - map, filter, reduce, etc.
3. **Multiple independent collectors** - each gets its own execution
4. **Reactive streams** - UI updates, database queries
5. **Composition** - complex transformation pipelines

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
        .distinctUntilChanged() // Only emit on change
        .map { user -> user.copy(name = user.name.uppercase()) }
        .catch { emit(User.DEFAULT) }
}

// Multiple collectors work independently
userRepository.getUserUpdates(123)
    .collect { user1 -> updateUI1(user1) }

userRepository.getUserUpdates(123)
    .collect { user2 -> updateUI2(user2) }
// Each collect starts a new upstream sequence
```

### Converting Between Channels and Flow

```kotlin
// Flow -> Channel (produce Flow values into a Channel)
fun <T> Flow<T>.produceIn(scope: CoroutineScope): ReceiveChannel<T> =
    scope.produce {
        collect { send(it) }
    }

// Channel -> Flow (consume Channel values as a Flow)
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

### Real-world Example: Event Bus with Channel (work-sharing)

```kotlin
sealed class AppEvent {
    data class UserLoggedIn(val userId: Int) : AppEvent()
    data class UserLoggedOut(val userId: Int) : AppEvent()
    data class MessageReceived(val message: String) : AppEvent()
}

class EventBus {
    // Single Channel used as an event queue; subscribers compete for events.
    private val events = Channel<AppEvent>(capacity = Channel.BUFFERED)

    suspend fun publish(event: AppEvent) {
        events.send(event)
    }

    fun subscribe(): ReceiveChannel<AppEvent> = events

    fun close() {
        events.close()
    }
}

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

Note: In this example, subscribers share (compete for) events from a single channel. They do not each receive a full copy of the stream. For broadcast semantics in real apps, prefer `SharedFlow`/`StateFlow` or a dedicated fan-out mechanism.

### Real-world Example: Data Pipeline with Flow

```kotlin
class DataPipeline {
    fun processStream(): Flow<ProcessedData> = fetchRawData()
        .buffer(capacity = 50) // Add buffering between stages
        .map { raw -> validate(raw) }
        .filter { it.isValid }
        .map { validated -> transform(validated) }
        .catch { exception ->
            logger.error("Pipeline error", exception)
            emit(ProcessedData.ERROR)
        }
        .flowOn(Dispatchers.IO)

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
// Channel: hot-style synchronization/queue primitive with buffer
val channel = Channel<Int>(1000)
// Can hold up to 1000 items in memory even if consumer is temporarily absent

// Flow: cold, work starts on collection
val flow = flow { emit(data) }
// No data is produced until collect() is called

// For a single consumer and declarative transformations, prefer Flow
// For work queues and coordinating multiple workers, use Channel
```

### Best Practices

1. **Choose based on hot vs cold semantics**:
   ```kotlin
   // Hot-style: Channel for real-time events (single or competing consumers)
   val sensorData = Channel<SensorReading>()

   // Cold: Flow for on-demand data
   val userData = flow { emit(fetchUser()) }
   ```

2. **Manage channel lifecycle carefully**:
   ```kotlin
   val channel = Channel<Int>()
   try {
       channel.send(1)
   } finally {
       channel.close() // Prevent leaks for manually managed channels
   }
   ```

3. **Use appropriate capacity**:
   ```kotlin
   // Fast producer, slow consumer
   Channel<Int>(capacity = 100)

   // State updates (latest only matters)
   Channel<State>(Channel.CONFLATED)

   // Synchronized handoff
   Channel<Request>(Channel.RENDEZVOUS)
   ```

4. **Prefer Flow for transformations**:
   ```kotlin
   // Flow is a natural fit for pipelines
   flow { emit(data) }
       .map { transform(it) }
       .filter { isValid(it) }

   // With channels you'd need manual piping
   val ch1 = Channel<Data>()
   val ch2 = Channel<Transformed>()
   ```

### Common Pitfalls

1. **Forgetting to close channels you own**:
   ```kotlin
   // Potential leak
   val ch = Channel<Int>()
   ch.send(1)
   // Never closed

   // Better: close when done producing
   val ch2 = Channel<Int>()
   try { ch2.send(1) }
   finally { ch2.close() }
   ```

2. **Using UNLIMITED carelessly**:
   ```kotlin
   // OutOfMemoryError risk
   val ch = Channel<ByteArray>(Channel.UNLIMITED)
   repeat(1000000) { ch.send(ByteArray(1024)) }

   // Prefer bounded capacity
   val bounded = Channel<ByteArray>(100)
   ```

3. **Choosing the wrong primitive**:
   ```kotlin
   // Using Channel for pure data transformations
   val ch = Channel<Int>()
   launch { for (i in ch) process(i) }

   // Flow is a better fit here
   flowOf(1, 2, 3).map { process(it) }.collect()
   ```

**English Summary**: Channels are hot-style, stateful communication primitives and queues for producer-consumer and work distribution, while Flows are cold, declarative streams for data transformations and reactive patterns. Channels support capacity strategies: RENDEZVOUS (no capacity buffer), BUFFERED (fixed size), UNLIMITED (unbounded), and CONFLATED (latest only). Use Channels for task queues and inter-coroutine communication, and Flows for transformation pipelines and reactive data. Manage channel lifecycles carefully, choose capacities thoughtfully, and base your choice on hot vs cold semantics and queue vs transformation requirements.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [[c-kotlin]]
- [[c-coroutines]]
- [[c-flow]]
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
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs `LiveData`
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - `StateFlow` & `SharedFlow` differences

### Advanced (Harder)
- [[q-select-expression-channels--kotlin--hard]] - Coroutines
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies

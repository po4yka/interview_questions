---
anki_cards:
- slug: q-channel-flow-comparison--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-channel-flow-comparison--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: kotlin-085
title: "Channel vs Flow Comparison / Сравнение Channel и Flow"
aliases: ["Channel vs Flow Comparison", "Сравнение Channel и Flow"]
topic: kotlin
subtopics: [channels, coroutines]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Channel vs Flow Guide
status: draft
moc: moc-kotlin
related: [c-concurrency, c-stateflow, q-channels-basics-types--kotlin--medium, q-kotlin-flow-basics--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [channels, cold-stream, concurrency, coroutines, difficulty/medium, flow, hot-stream, kotlin]

---
# Вопрос (RU)
> В чем разница между `Channel` и `Flow`? Объясните горячие и холодные потоки, обработку backpressure и когда выбирать каждый подход.

# Question (EN)
> What's the difference between `Channel` and `Flow`? Explain hot vs cold streams, backpressure handling, and when to choose each approach.

---

## Ответ (RU)

Channel и `Flow` — это механизмы для работы с потоками значений в Kotlin Coroutines, но их семантика и области применения различаются.

- `Channel` — низкоуровневый примитив коммуникации между корутинами.
- `Flow` — высокоуровневый холодный асинхронный поток с операторами.

### Основное Различие: Горячий Vs Холодный (концептуально)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.flow.*

// CHANNEL: "горячий" по паттерну использования продьюсер - живет в своем scope
fun channelHotExample() = runBlocking {
    val channel = Channel<Int>()

    // Продьюсер стартует сразу в своей корутине
    launch {
        println("Producer started")
        for (i in 1..3) {
            println("Producing $i")
            channel.send(i) // Для rendezvous-канала send приостанавливается до receive
            delay(100)
        }
        channel.close()
    }

    delay(500) // Пауза перед началом потребления

    // Потребитель стартует позже
    println("Consumer starting...")
    for (value in channel) {
        println("Consumed $value")
    }
}

// FLOW: холодный поток — код выполняется для каждого коллектора отдельно
fun flowColdExample() = runBlocking {
    val flow = flow {
        println("Producer started")
        for (i in 1..3) {
            println("Producing $i")
            emit(i)
            delay(100)
        }
    }

    delay(500) // Пока нет collect — ничего не происходит

    println("Consumer starting...")
    flow.collect { value ->
        println("Consumed $value")
    }
}
```

Ключевая идея:
- Продьюсер на `Channel` обычно живет независимо от конкретных потребителей (горячий паттерн использования), а конкретная семантика (suspend, буфер) определяет, будут ли значения реально производиться заранее или продьюсер будет блокироваться.
- `Flow` по умолчанию холодный: collect запускает производство, для каждого коллектора выполняется свой экземпляр.

### Краткое Резюме Ключевых Различий

```kotlin
class ChannelVsFlowComparison(private val scope: CoroutineScope) {

    // 1. Семантика потребления: одиночное vs множественные коллектора
    suspend fun collectorDifference() = withContext(Dispatchers.Default) {
        // CHANNEL: значения потребляются один раз; несколько потребителей конкурируют
        val channel = Channel<Int>()

        scope.launch {
            repeat(5) { channel.send(it) }
            channel.close()
        }

        scope.launch {
            for (value in channel) {
                println("Consumer 1: $value")
            }
        }

        scope.launch {
            for (value in channel) {
                println("Consumer 2: $value")
            }
        }
        // Каждое значение получает ровно один потребитель.

        // FLOW: холодный; каждый коллектор получает полную последовательность
        val flow = flow {
            repeat(5) { emit(it) }
        }

        scope.launch {
            flow.collect { println("Collector 1: $it") }
        }

        scope.launch {
            flow.collect { println("Collector 2: $it") }
        }
        // Каждый коллектор видит все значения из своей независимой коллекции.
    }

    // 2. Жизненный цикл и тайминг
    suspend fun lifecycleDifference() = withContext(Dispatchers.Default) {
        // CHANNEL: живет в scope, независим от конкретного потребителя
        val channel = Channel<Int>()

        scope.launch {
            channel.send(1) // Приостанавливается, пока не будет получатель
            channel.send(2)
        }

        delay(1000)
        println(channel.receive()) // Возобновляет первый send

        // FLOW: выполнение только при collect
        val flow = flow {
            println("Flow builder executing")
            emit(1)
        }

        delay(1000) // Ничего не произойдет без collect
        flow.collect { println(it) }
    }

    // 3. Backpressure
    suspend fun backpressureDifference() = withContext(Dispatchers.Default) {
        // CHANNEL: backpressure через емкость и политику
        val channel = Channel<Int>(capacity = 10)

        scope.launch {
            repeat(100) {
                channel.send(it) // Приостанавливается при заполнении буфера
            }
            channel.close()
        }

        scope.launch {
            for (value in channel) {
                delay(100) // Медленный потребитель
                println(value)
            }
        }

        // FLOW: backpressure через приостановку
        val flow = flow {
            repeat(100) {
                emit(it) // Приостанавливается, если downstream медленный
            }
        }

        flow.collect {
            delay(100)
            println(it)
        }
    }
}
```

### Детализированное Сравнение (концептуально)

```kotlin
/**
 * CHANNEL vs FLOW Detailed Comparison
 *
 *  Тип потока:         Channel — горячий по паттерну использования (продьюсер в своем scope)
 *                      Flow — холодный по умолчанию
 *  Активация:          Channel — управляется продьюсером
 *                      Flow — при collect
 *  Коллекторы:         Channel — конкурирующие потребители (1 элемент -> 1 получатель)
 *                      Flow — каждый коллектор получает полную последовательность
 *  Шаринг:             Channel — one-to-one / fan-out конкуренцией
 *                      Flow — one-to-many через независимые коллекции
 *  Буферизация:        Channel — явная capacity/policy
 *                      Flow — операторы + внутренняя буферизация
 *  Backpressure:       Channel — приостановка send/receive, политика буфера
 *                      Flow — приостановка + buffer/conflate/debounce и др.
 *  Исключения:         Channel — try/catch вокруг send/receive
 *                      Flow — операторы (catch) + try/catch в collect
 *  Отмена:             Оба поддерживают структурированную отмену и зависят от scope
 *  Use-case:           Channel — коммуникация корутин, очереди, акторы
 *                      Flow — реактивные/трансформационные стримы данных
 */
```

### Практическая Демонстрация

```kotlin
class PracticalComparison(private val scope: CoroutineScope) {

    // Channel: EventBus / одноразовые события, конкурирующие потребители
    class EventBusWithChannel {
        private val events = Channel<Event>(Channel.UNLIMITED)

        sealed class Event {
            data class UserLoggedIn(val userId: String) : Event()
            data class MessageReceived(val message: String) : Event()
        }

        fun sendEvent(event: Event) {
            events.trySend(event)
        }

        // Предполагается запущенная корутина, которая вызывает observeEvents()
        suspend fun observeEvents() {
            for (event in events) {
                handleEvent(event)
            }
        }

        private fun handleEvent(event: Event) {
            println("Handling: $event")
        }
    }

    // Flow: репозиторий, реактивные обновления
    class UserRepositoryWithFlow {
        fun observeUser(userId: String): Flow<User> = flow {
            val user = fetchUserFromDb(userId)
            emit(user)

            val updates = listenToUserUpdates(userId)
            updates.collect { emit(it) }
        }

        private suspend fun fetchUserFromDb(userId: String): User {
            return User(userId, "Name")
        }

        private fun listenToUserUpdates(userId: String): Flow<User> {
            return flow { /* эмит обновлений */ }
        }

        data class User(val id: String, val name: String)
    }
}
```

### Когда Использовать Channel (подробно)

```kotlin
class WhenToUseChannel(private val scope: CoroutineScope) {

    // 1. Очередь заданий (producer-consumer)
    class JobQueue {
        private val jobs = Channel<Job>(capacity = 100)

        data class Job(val id: Int, val task: String)

        suspend fun worker(id: Int) {
            for (job in jobs) {
                println("Worker $id processing ${job.id}")
                processJob(job)
            }
        }

        fun submitJob(job: Job) {
            jobs.trySend(job)
        }

        private suspend fun processJob(job: Job) {
            delay(100)
        }
    }

    // 2. Актороподобный паттерн
    class ActorLikePattern {
        private val commands = Channel<Command>()
        private var state = 0

        sealed class Command {
            data class Increment(val value: Int) : Command()
            data class GetValue(val response: CompletableDeferred<Int>) : Command()
        }

        suspend fun processCommands() {
            for (cmd in commands) {
                when (cmd) {
                    is Command.Increment -> state += cmd.value
                    is Command.GetValue -> cmd.response.complete(state)
                }
            }
        }

        suspend fun increment(value: Int) {
            commands.send(Command.Increment(value))
        }

        suspend fun getValue(): Int {
            val response = CompletableDeferred<Int>()
            commands.send(Command.GetValue(response))
            return response.await()
        }
    }

    // 3. Fan-out / балансировка нагрузки
    suspend fun loadBalancing() = coroutineScope {
        val requests = Channel<Request>()

        data class Request(val id: Int)

        repeat(5) { workerId ->
            launch {
                for (request in requests) {
                    println("Worker $workerId handling ${request.id}")
                    delay(100)
                }
            }
        }

        repeat(20) {
            requests.send(Request(it))
        }
        requests.close()
    }

    // 4. Буферизированные конвейеры между компонентами
    class BufferedPipeline {
        private val input = Channel<Data>(capacity = 1000)
        private val output = Channel<ProcessedData>(capacity = 1000)

        data class Data(val raw: String)
        data class ProcessedData(val processed: String)

        suspend fun producer() {
            repeat(10000) {
                input.send(Data("Item $it"))
            }
            input.close()
        }

        suspend fun processor() {
            for (data in input) {
                val processed = process(data)
                output.send(processed)
            }
            output.close()
        }

        suspend fun consumer() {
            for (data in output) {
                save(data)
            }
        }

        private fun process(data: Data): ProcessedData =
            ProcessedData(data.raw.uppercase())

        private fun save(data: ProcessedData) {
            println("Saved: ${data.processed}")
        }
    }
}
```

### Когда Использовать Flow (подробно)

```kotlin
class WhenToUseFlow {

    // 1. Реактивные источники данных
    class UserRepository {
        private val database: Database = Database()

        fun observeUser(userId: String): Flow<User> = flow {
            val user = database.getUser(userId)
            emit(user)

            database.observeUserChanges(userId).collect { emit(it) }
        }.flowOn(Dispatchers.IO)

        data class User(val id: String, val name: String)

        class Database {
            fun getUser(id: String): User = User(id, "User $id")
            fun observeUserChanges(id: String): Flow<User> = flow { /* emit updates */ }
        }
    }

    // 2. Трансформационные конвейеры
    class DataPipeline {
        fun processData(input: Flow<Int>): Flow<String> = input
            .filter { it > 0 }
            .map { it * 2 }
            .take(10)
            .map { "Value: $it" }
            .flowOn(Dispatchers.Default)

        suspend fun example() {
            val source = flow {
                repeat(100) { emit(it) }
            }

            processData(source).collect { println(it) }
        }
    }

    // 3. Множественные подписчики к непрерывному источнику
    class SensorData {
        fun observeTemperature(): Flow<Double> = flow {
            while (true) {
                emit(readSensor())
                delay(1000)
            }
        }

        private fun readSensor(): Double = 20.0 + Math.random() * 10

        suspend fun example() = coroutineScope {
            val temperature = observeTemperature()

            launch {
                temperature.collect { temp -> updateUI(temp) }
            }

            launch {
                temperature.collect { temp -> logTemperature(temp) }
            }

            launch {
                temperature
                    .filter { it > 25 }
                    .collect { temp -> sendAlert(temp) }
            }
        }

        private fun updateUI(temp: Double) {}
        private fun logTemperature(temp: Double) {}
        private fun sendAlert(temp: Double) {}
    }

    // 4. Композиция операторов
    class ComplexTransformations {
        fun searchWithDebounce(queries: Flow<String>): Flow<List<Result>> = queries
            .debounce(300)
            .distinctUntilChanged()
            .filter { it.length >= 3 }
            .mapLatest { query -> searchApi(query) }
            .retry(3)
            .catch { emit(emptyList()) }

        data class Result(val title: String)

        private suspend fun searchApi(query: String): List<Result> {
            delay(500)
            return listOf(Result(query))
        }
    }
}
```

### Конвертация Между Channel И Flow

```kotlin
class ChannelFlowConversion(private val scope: CoroutineScope) {

    // Channel -> Flow
    fun channelToFlow() {
        val channel = Channel<Int>()

        val flow: Flow<Int> = channel.receiveAsFlow()

        val manualFlow: Flow<Int> = flow {
            for (value in channel) {
                emit(value)
            }
        }
    }

    // Flow -> Channel
    suspend fun flowToChannel() = coroutineScope {
        val flow = flow {
            repeat(10) { emit(it) }
        }

        val channel: ReceiveChannel<Int> = flow.produceIn(this)

        val manualChannel = Channel<Int>()
        launch {
            flow.collect { manualChannel.send(it) }
            manualChannel.close()
        }
    }

    // `SharedFlow`: горячий `Flow` с гибкими настройками
    class HotFlowExample(private val scope: CoroutineScope) {
        private val _events = MutableSharedFlow<Event>(extraBufferCapacity = 0)
        val events: SharedFlow<Event> = _events.asSharedFlow()

        sealed class Event {
            object Started : Event()
            data class Progress(val value: Int) : Event()
        }

        // Похоже на `Channel` (горячий, несколько коллекторов), но с API `Flow` и операторами.
        fun emitEvent(event: Event) {
            _events.tryEmit(event)
        }

        suspend fun example() = coroutineScope {
            launch {
                events.collect { println("Collector 1: $it") }
            }

            launch {
                events.collect { println("Collector 2: $it") }
            }

            emitEvent(Event.Started)
        }
    }
}
```

### Производительность

```kotlin
class PerformanceComparison(private val scope: CoroutineScope) {

    // Channel: эффективная передача сообщений, но итоговая производительность зависит от нагрузки и конфигурации
    suspend fun channelPerformance() = withContext(Dispatchers.Default) {
        val channel = Channel<Int>(Channel.UNLIMITED)

        val startTime = System.currentTimeMillis()

        scope.launch {
            repeat(1_000_000) { channel.send(it) }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Channel: $count items in $duration ms")
    }

    // Flow: подходит для конвейеров; operator fusion может снижать накладные расходы
    suspend fun flowPerformance() = withContext(Dispatchers.Default) {
        val flow = flow {
            repeat(1_000_000) { emit(it) }
        }

        val startTime = System.currentTimeMillis()

        val count = flow
            .filter { it % 2 == 0 }
            .map { it * 2 }
            .count()

        val duration = System.currentTimeMillis() - startTime
        println("Flow: $count items in $duration ms")
    }
}
```

### Частые Паттерны И Анти-паттерны

```kotlin
class Patterns {

    // GOOD: Channel для команд/акторов (нужна корутина-обработчик команд)
    class GoodChannelUsage {
        private val commands = Channel<Command>()

        sealed class Command {
            object Start : Command()
            object Stop : Command()
        }

        suspend fun sendCommand(cmd: Command) {
            commands.send(cmd)
        }
    }

    // BAD: общий Channel как источник для нескольких независимых наблюдателей
    class BadChannelUsage {
        private val data = Channel<Data>()

        data class Data(val value: Int)

        fun observeData(): ReceiveChannel<Data> = data
        // Коллекторы конкурируют; для "каждый получает все" лучше использовать `Flow`/`SharedFlow`.
    }

    // GOOD: Flow для реактивных данных
    class GoodFlowUsage {
        fun observeData(): Flow<Data> = flow {
            while (true) {
                emit(fetchData())
                delay(1000)
            }
        }

        data class Data(val value: Int)

        private fun fetchData(): Data = Data(0)
    }

    // BAD (часто): без аккуратной конфигурации использовать `SharedFlow` вместо Channel для одноразовых команд
    class BadFlowUsage {
        private val commands = MutableSharedFlow<Command>(extraBufferCapacity = 0)

        sealed class Command {
            object Save : Command()
        }

        // Без replay/buffer и явного жизненного цикла потребителя поздние подписчики могут пропустить событие.
        suspend fun sendCommand(cmd: Command) {
            commands.emit(cmd)
        }
    }
}
```

---

## Answer (EN)

Channel and `Flow` are both mechanisms for handling streams of values in Kotlin coroutines, but they have different semantics and use cases.

- `Channel` is a low-level concurrency primitive for communication between coroutines.
- `Flow` is a high-level cold asynchronous stream with operators.

### Core Difference: Hot Vs Cold (Conceptual)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.flow.*

// CHANNEL: Conceptually "hot-style" producer - lifetime independent from collectors
fun channelHotExampleEn() = runBlocking {
    val channel = Channel<Int>()

    // Producer starts immediately in its own coroutine
    launch {
        println("Producer started")
        for (i in 1..3) {
            println("Producing $i")
            channel.send(i) // Suspends until there is a receiver (for rendezvous channel)
            delay(100)
        }
        channel.close()
    }

    delay(500) // Delay before consuming

    // Consumer starts later
    println("Consumer starting...")
    for (value in channel) {
        println("Consumed $value")
    }
}

// FLOW: Cold Stream - producer code runs per collector
fun flowColdExampleEn() = runBlocking {
    val flow = flow {
        println("Producer started")
        for (i in 1..3) {
            println("Producing $i")
            emit(i)
            delay(100)
        }
    }

    delay(500) // `Flow` doesn't run yet

    // Production starts only when collected
    println("Consumer starting...")
    flow.collect { value ->
        println("Consumed $value")
    }
}
```

Key idea:
- Channel-based producers are typically started and run independently of who will consume ("hot-style" usage pattern),
  but send/receive semantics (suspension, buffering) define whether data can be produced ahead of consumers.
- `Flow` is cold by default: collection triggers execution, each collector runs the upstream block independently.

### Key Differences Summary

```kotlin
class ChannelVsFlowComparisonEn(private val scope: CoroutineScope) {

    // 1. Single vs Multiple collectors (consumption semantics)
    suspend fun collectorDifference() = withContext(Dispatchers.Default) {
        // CHANNEL: Values are consumed once per element; multiple consumers compete
        val channel = Channel<Int>()

        scope.launch {
            repeat(5) { channel.send(it) }
            channel.close()
        }

        // Two consumers compete for values from the same channel
        scope.launch {
            for (value in channel) {
                println("Consumer 1: $value")
            }
        }

        scope.launch {
            for (value in channel) {
                println("Consumer 2: $value")
            }
        }
        // Each value is received by exactly one consumer.

        // FLOW: Cold; each collector gets the full sequence (re-execution per collector)
        val flow = flow {
            repeat(5) { emit(it) }
        }

        scope.launch {
            flow.collect { println("Collector 1: $it") }
        }

        scope.launch {
            flow.collect { println("Collector 2: $it") }
        }
        // Each collector sees all emitted values from its own execution of the flow.
    }

    // 2. Lifecycle and timing
    suspend fun lifecycleDifference() = withContext(Dispatchers.Default) {
        // CHANNEL: Lifetime independent from specific consumers; behavior depends on capacity.
        val channel = Channel<Int>() // Rendezvous: send suspends until receive

        scope.launch {
            channel.send(1) // Suspends until someone receives
            channel.send(2)
        }

        delay(1000)

        // Consumer joins later; first receive will resume pending send
        println(channel.receive())

        // FLOW: Created per collection, no work until collected
        val flow = flow {
            println("Flow builder executing")
            emit(1)
        }

        delay(1000) // Nothing happens, `Flow` is cold

        // Execution starts here
        flow.collect { println(it) }
    }

    // 3. Backpressure handling
    suspend fun backpressureDifference() = withContext(Dispatchers.Default) {
        // CHANNEL: Backpressure via suspension & capacity policy
        val channel = Channel<Int>(capacity = 10)

        scope.launch {
            repeat(100) {
                channel.send(it) // Suspends when buffer is full according to capacity
            }
            channel.close()
        }

        scope.launch {
            for (value in channel) {
                delay(100) // Slow consumer
                println(value)
            }
        }

        // FLOW: Backpressure via suspension
        val flow = flow {
            repeat(100) {
                emit(it) // Suspends if downstream is slow
            }
        }

        flow.collect {
            delay(100) // Slow collector
            println(it)
        }
    }
}
```

### Detailed Comparison Table (Conceptual)

```kotlin
/**
 * CHANNEL vs FLOW Detailed Comparison
 *
 *  Feature              Channel                               Flow
 *
 *  Stream Type          Hot-style usage (by producer scope)   Cold by default
 *  Activation           Producer controlled                   On collection
 *  Collectors           Competing consumers (one receive      Multiple; each gets full sequence
 *                       per element per channel instance)     (new execution per collector)
 *  Value Sharing        One-to-one / fan-out via competition  One-to-many via independent collections
 *  Buffering            Explicit capacity & policy            Operators + internal buffering
 *  Backpressure         Suspension + capacity config          Suspension + operators
 *  Exception Handling   Try-catch around send/receive         Operators + try-catch in collectors
 *  Cancellation         Structured; tied to owning scope      Structured; tied to collector scope
 *  Lifecycle            Tied to scope owning channel          Tied to collector and upstream scope
 *  Use Case             Coroutines communication, pipelines   Reactive/transformational streams
 */
```

### Practical Demonstration

```kotlin
class PracticalComparisonEn(private val scope: CoroutineScope) {

    // Channel: Event bus / communication (one-time events, competing consumers, actors)
    class EventBusWithChannel {
        private val events = Channel<Event>(Channel.UNLIMITED)

        sealed class Event {
            data class UserLoggedIn(val userId: String) : Event()
            data class MessageReceived(val message: String) : Event()
        }

        fun sendEvent(event: Event) {
            events.trySend(event)
        }

        // Assumes a coroutine is running observeEvents()
        suspend fun observeEvents() {
            for (event in events) {
                handleEvent(event)
            }
        }

        private fun handleEvent(event: Event) {
            println("Handling: $event")
        }
    }

    // Flow: Data transformation / reactive streams
    class UserRepositoryWithFlow {
        fun observeUser(userId: String): Flow<User> = flow {
            // Fresh query each time (per collector)
            val user = fetchUserFromDb(userId)
            emit(user)

            // Listen for updates and emit further values
            val updates = listenToUserUpdates(userId)
            updates.collect { emit(it) }
        }

        private suspend fun fetchUserFromDb(userId: String): User {
            return User(userId, "Name")
        }

        private fun listenToUserUpdates(userId: String): Flow<User> {
            return flow { /* Emit updates from DB or other source */ }
        }

        data class User(val id: String, val name: String)
    }
}
```

### When to Use Channel

```kotlin
class WhenToUseChannelEn(private val scope: CoroutineScope) {

    // 1. Producer-Consumer Pattern
    class JobQueue {
        private val jobs = Channel<Job>(capacity = 100)

        data class Job(val id: Int, val task: String)

        // Multiple workers compete for jobs
        suspend fun worker(id: Int) {
            for (job in jobs) {
                println("Worker $id processing ${job.id}")
                processJob(job)
            }
        }

        fun submitJob(job: Job) {
            jobs.trySend(job)
        }

        private suspend fun processJob(job: Job) {
            delay(100)
        }
    }

    // 2. Communication Between Coroutines (actor-like)
    class ActorLikePattern {
        private val commands = Channel<Command>()
        private var state = 0

        sealed class Command {
            data class Increment(val value: Int) : Command()
            data class GetValue(val response: CompletableDeferred<Int>) : Command()
        }

        suspend fun processCommands() {
            for (cmd in commands) {
                when (cmd) {
                    is Command.Increment -> state += cmd.value
                    is Command.GetValue -> cmd.response.complete(state)
                }
            }
        }

        suspend fun increment(value: Int) {
            commands.send(Command.Increment(value))
        }

        suspend fun getValue(): Int {
            val response = CompletableDeferred<Int>()
            commands.send(Command.GetValue(response))
            return response.await()
        }
    }

    // 3. Fan-out Pattern (Load Balancing)
    suspend fun loadBalancing() = coroutineScope {
        val requests = Channel<Request>()

        data class Request(val id: Int)

        // Multiple workers share the load (competing consumers)
        repeat(5) { workerId ->
            launch {
                for (request in requests) {
                    println("Worker $workerId handling ${request.id}")
                    delay(100)
                }
            }
        }

        // Producer sends requests
        repeat(20) {
            requests.send(Request(it))
        }
        requests.close()
    }

    // 4. Buffering Between Components
    class BufferedPipeline {
        private val input = Channel<Data>(capacity = 1000)
        private val output = Channel<ProcessedData>(capacity = 1000)

        data class Data(val raw: String)
        data class ProcessedData(val processed: String)

        suspend fun producer() {
            repeat(10000) {
                input.send(Data("Item $it"))
            }
            input.close()
        }

        suspend fun processor() {
            for (data in input) {
                val processed = process(data)
                output.send(processed)
            }
            output.close()
        }

        suspend fun consumer() {
            for (data in output) {
                save(data)
            }
        }

        private fun process(data: Data): ProcessedData {
            return Data(data.raw.uppercase()).let { ProcessedData(it.raw) }
        }

        private fun save(data: ProcessedData) {
            println("Saved: ${data.processed}")
        }
    }
}
```

### When to Use Flow

```kotlin
class WhenToUseFlowEn {

    // 1. Reactive Data Sources
    class UserRepository {
        private val database: Database = Database()

        // Each collector triggers its own data sequence
        fun observeUser(userId: String): Flow<User> = flow {
            val user = database.getUser(userId)
            emit(user)

            database.observeUserChanges(userId).collect { emit(it) }
        }.flowOn(Dispatchers.IO)

        data class User(val id: String, val name: String)
        class Database {
            fun getUser(id: String): User = User(id, "User $id")
            fun observeUserChanges(id: String): Flow<User> = flow { /* emit updates */ }
        }
    }

    // 2. Transformation Pipelines
    class DataPipeline {
        fun processData(input: Flow<Int>): Flow<String> = input
            .filter { it > 0 }
            .map { it * 2 }
            .take(10)
            .map { "Value: $it" }
            .flowOn(Dispatchers.Default)

        // Usage
        suspend fun example() {
            val source = flow {
                repeat(100) { emit(it) }
            }

            processData(source).collect { println(it) }
        }
    }

    // 3. Multiple Subscribers to a continuous source
    class SensorData {
        // Each subscriber gets its own cold stream execution
        fun observeTemperature(): Flow<Double> = flow {
            while (true) {
                emit(readSensor())
                delay(1000)
            }
        }

        private fun readSensor(): Double = 20.0 + Math.random() * 10

        suspend fun example() = coroutineScope {
            val temperature = observeTemperature()

            // UI collector
            launch {
                temperature.collect { temp ->
                    updateUI(temp)
                }
            }

            // Logger collector
            launch {
                temperature.collect { temp ->
                    logTemperature(temp)
                }
            }

            // Alert collector
            launch {
                temperature
                    .filter { it > 25 }
                    .collect { temp ->
                        sendAlert(temp)
                    }
            }
        }

        private fun updateUI(temp: Double) {}
        private fun logTemperature(temp: Double) {}
        private fun sendAlert(temp: Double) {}
    }

    // 4. Composable Operators
    class ComplexTransformations {
        fun searchWithDebounce(queries: Flow<String>): Flow<List<Result>> = queries
            .debounce(300)
            .distinctUntilChanged()
            .filter { it.length >= 3 }
            .mapLatest { query -> searchApi(query) }
            .retry(3)
            .catch { emit(emptyList()) }

        data class Result(val title: String)

        private suspend fun searchApi(query: String): List<Result> {
            delay(500)
            return listOf(Result(query))
        }
    }
}
```

### Converting Between Channel and Flow

```kotlin
class ChannelFlowConversionEn(private val scope: CoroutineScope) {

    // Channel to Flow
    fun channelToFlow() {
        val channel = Channel<Int>()

        // Convert using receiveAsFlow (cold view over channel)
        val flow: Flow<Int> = channel.receiveAsFlow()

        // Or manually
        val manualFlow: Flow<Int> = flow {
            for (value in channel) {
                emit(value)
            }
        }
    }

    // Flow to Channel
    suspend fun flowToChannel() = coroutineScope {
        val flow = flow {
            repeat(10) { emit(it) }
        }

        // Using produceIn within a CoroutineScope
        val channel: ReceiveChannel<Int> = flow.produceIn(this)

        // Or manually
        val manualChannel = Channel<Int>()
        launch {
            flow.collect { manualChannel.send(it) }
            manualChannel.close()
        }
    }

    // `SharedFlow`: Hot `Flow` (hybrid semantics)
    class HotFlowExample(private val scope: CoroutineScope) {
        private val _events = MutableSharedFlow<Event>(extraBufferCapacity = 0)
        val events: SharedFlow<Event> = _events.asSharedFlow()

        sealed class Event {
            object Started : Event()
            data class Progress(val value: Int) : Event()
        }

        // Like `Channel`: hot, can have multiple collectors; no implicit replay unless configured.
        // Like `Flow`: supports operators, structured cancellation.
        fun emitEvent(event: Event) {
            _events.tryEmit(event)
        }

        suspend fun example() = coroutineScope {
            launch {
                events.collect { println("Collector 1: $it") }
            }

            launch {
                events.collect { println("Collector 2: $it") }
            }

            emitEvent(Event.Started)
        }
    }
}
```

### Performance Considerations

```kotlin
class PerformanceComparisonEn(private val scope: CoroutineScope) {

    // Channel: Suited for high-frequency communication, but actual performance is workload-dependent.
    suspend fun channelPerformance() = withContext(Dispatchers.Default) {
        val channel = Channel<Int>(Channel.UNLIMITED)

        val startTime = System.currentTimeMillis()

        scope.launch {
            repeat(1_000_000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Channel: $count items in $duration ms")
    }

    // Flow: Suited for pipelines; operator fusion may reduce overhead; performance depends on context.
    suspend fun flowPerformance() = withContext(Dispatchers.Default) {
        val flow = flow {
            repeat(1_000_000) {
                emit(it)
            }
        }

        val startTime = System.currentTimeMillis()

        val count = flow
            .filter { it % 2 == 0 }
            .map { it * 2 }
            .count()

        val duration = System.currentTimeMillis() - startTime
        println("Flow: $count items in $duration ms")
    }
}
```

### Common Patterns and Anti-patterns

```kotlin
class PatternsEn {

    //  GOOD: Use Channel for imperative communication / actors (with a consuming coroutine)
    class GoodChannelUsage {
        private val commands = Channel<Command>()

        sealed class Command {
            object Start : Command()
            object Stop : Command()
        }

        suspend fun sendCommand(cmd: Command) {
            commands.send(cmd)
        }
    }

    //  BAD: Using a single Channel as a data source for multiple independent observers
    class BadChannelUsage {
        private val data = Channel<Data>()

        data class Data(val value: Int)

        // Multiple consumers of the same ReceiveChannel will compete,
        // so this is not suitable for "every observer gets all values" semantics.
        fun observeData(): ReceiveChannel<Data> = data
        // For broadcast-style semantics, prefer `Flow`/`SharedFlow`.
    }

    //  GOOD: Use Flow for reactive streams
    class GoodFlowUsage {
        fun observeData(): Flow<Data> = flow {
            while (true) {
                emit(fetchData())
                delay(1000)
            }
        }

        data class Data(val value: Int)

        private fun fetchData(): Data = Data(0)
    }

    //  BAD (often): using `SharedFlow` naively for one-off commands instead of Channel
    class BadFlowUsage {
        private val commands = MutableSharedFlow<Command>(extraBufferCapacity = 0)

        sealed class Command {
            object Save : Command()
        }

        // Issue: `SharedFlow` is hot, and without replay/buffer and clear consumer lifecycle,
        // late collectors may miss events. For strict command/response, a Channel-based actor
        // or structured consumption is usually clearer.
        suspend fun sendCommand(cmd: Command) {
            commands.emit(cmd)
        }
    }
}
```

---

## Follow-ups

1. How does `SharedFlow` combine characteristics of `Channel` and `Flow`, and when is it preferable over each?
2. In which scenarios would you choose `StateFlow` over `SharedFlow` or `Channel` for exposing UI state from a `ViewModel`?
3. How can you implement and tune backpressure strategies using channel capacities and `Flow` operators like `buffer`, `conflate`, and `debounce`?
4. What are the trade-offs when converting between `Channel` and `Flow` using `receiveAsFlow` and `produceIn` in terms of semantics and performance?
5. How would you structure unit tests for `Channel`-based actors versus `Flow`-based pipelines (including use of Turbine and test dispatchers)?

## References

- [[c-concurrency]]
- Official Kotlin Coroutines documentation: "Channels" and "Flows" (see sections for `Channel`, `Flow`, `SharedFlow`, `StateFlow` on kotlinlang.org)

## Related Questions

- [[q-channels-basics-types--kotlin--medium]]
- [[q-kotlin-flow-basics--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]

## Дополнительные Вопросы (RU)
1. Как `SharedFlow` сочетает свойства `Channel` и `Flow`, и когда он предпочтительнее каждого из них?
2. В каких случаях стоит выбирать `StateFlow` вместо `SharedFlow` или `Channel` для экспонирования состояния UI из `ViewModel`?
3. Как реализовать и настроить стратегии backpressure с помощью емкости каналов и операторов `Flow` (`buffer`, `conflate`, `debounce`)?
4. Каковы семантические и производительные trade-off'ы при конвертации между `Channel` и `Flow` через `receiveAsFlow` и `produceIn`?
5. Как выстроить unit-тесты для акторов на основе `Channel` и конвейеров на основе `Flow` (включая использование Turbine и test dispatchers)?
## Связанные Вопросы (RU)
## Ссылки (RU)
- Официальная документация Kotlin Coroutines: "Channels" и "Flows" (смотрите разделы про `Channel`, `Flow`, `SharedFlow`, `StateFlow` на kotlinlang.org)
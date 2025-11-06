---
id: kotlin-065
title: "produce and actor Channel Builders / Билдеры каналов produce и actor"
aliases: ["produce and actor Channel Builders, Билдеры каналов produce и actor"]

# Classification
topic: kotlin
subtopics: [actor, channel-builders, channels]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Channel Builders Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-actor-pattern--kotlin--hard, q-channel-closing-completion--kotlin--medium, q-channels-basics-types--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [actor, builders, channels, coroutines, difficulty/medium, kotlin, produce]
---

# Question (EN)
> What are produce and actor channel builders? Explain their purpose, automatic resource management, and when to use each builder pattern.

# Вопрос (RU)
> Что такое билдеры каналов produce и actor? Объясните их назначение, автоматическое управление ресурсами и когда использовать каждый паттерн билдера.

---

## Answer (EN)

The `produce` and `actor` builders are high-level channel construction functions that simplify common coroutine patterns and provide automatic resource management.

### Produce: Producer Pattern Builder

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Basic produce usage
fun basicProduce() = runBlocking {
    val numbers = produce {
        for (i in 1..5) {
            send(i)
        }
        // Channel automatically closed after block completes
    }

    for (num in numbers) {
        println("Received: $num")
    }
    // Output: Received: 1, 2, 3, 4, 5
}

// Comparison: Manual channel vs produce
class ProduceComparison {

    //  Manual approach (more boilerplate)
    suspend fun manualChannel(): ReceiveChannel<Int> {
        val channel = Channel<Int>()

        launch {
            try {
                for (i in 1..5) {
                    channel.send(i)
                }
            } finally {
                channel.close()
            }
        }

        return channel
    }

    //  Using produce (cleaner, safer)
    fun withProduce() = produce {
        for (i in 1..5) {
            send(i)
        }
    }
}
```

### Produce Features and Benefits

```kotlin
class ProduceFeatures {

    // 1. Automatic channel creation and closing
    fun automaticManagement() = produce<Int> {
        try {
            for (i in 1..10) {
                send(i)
            }
            println("All sent successfully")
        } catch (e: Exception) {
            println("Error: ${e.message}")
        }
        // Channel automatically closed
    }

    // 2. Cancellation handling
    fun cancellationHandling() = runBlocking {
        val numbers = produce {
            var x = 1
            while (true) {
                send(x++)
                delay(100)
            }
        }

        // Take only first 5
        repeat(5) {
            println(numbers.receive())
        }

        numbers.cancel() // Cancels producer coroutine
    }

    // 3. Exception propagation
    fun exceptionPropagation() = runBlocking {
        val numbers = produce {
            for (i in 1..10) {
                if (i == 5) throw IllegalStateException("Error at $i")
                send(i)
            }
        }

        try {
            for (num in numbers) {
                println(num)
            }
        } catch (e: ClosedReceiveChannelException) {
            println("Channel closed due to: ${e.cause}")
        }
    }

    // 4. Capacity configuration
    fun withCapacity() = produce<Int>(capacity = Channel.BUFFERED) {
        repeat(100) {
            send(it)
            println("Sent $it")
        }
    }

    // 5. Dispatcher configuration
    fun withDispatcher() = produce<Int>(Dispatchers.IO) {
        // Runs on IO dispatcher
        repeat(10) {
            send(readFromDatabase(it))
        }
    }

    private fun readFromDatabase(id: Int): Int = id
}
```

### Produce Use Cases

```kotlin
class ProduceUseCases {

    // Use Case 1: Range generator
    fun rangeGenerator(start: Int, end: Int) = produce {
        for (i in start..end) {
            send(i)
        }
    }

    // Use Case 2: File reader
    fun readFileLines(file: File) = produce<String>(Dispatchers.IO) {
        file.bufferedReader().use { reader ->
            for (line in reader.lineSequence()) {
                send(line)
            }
        }
    }

    // Use Case 3: API pagination
    fun fetchAllPages(userId: String) = produce<Page> {
        var pageNumber = 1
        while (true) {
            val page = apiClient.fetchPage(userId, pageNumber)
            send(page)
            if (!page.hasNext) break
            pageNumber++
        }
    }

    // Use Case 4: Event stream
    fun observeEvents() = produce<Event> {
        val listener = object : EventListener {
            override fun onEvent(event: Event) {
                trySend(event)
            }
        }

        eventBus.register(listener)

        try {
            awaitClose { eventBus.unregister(listener) }
        } finally {
            eventBus.unregister(listener)
        }
    }

    data class Page(val data: List<String>, val hasNext: Boolean)
    data class Event(val type: String)
    interface EventListener {
        fun onEvent(event: Event)
    }
    object apiClient {
        fun fetchPage(userId: String, page: Int) = Page(emptyList(), false)
    }
    object eventBus {
        fun register(listener: EventListener) {}
        fun unregister(listener: EventListener) {}
    }
}
```

### Actor: Actor Pattern Builder

```kotlin
// Basic actor usage
sealed class CounterMsg {
    object Increment : CounterMsg()
    object Decrement : CounterMsg()
    data class GetValue(val response: CompletableDeferred<Int>) : CounterMsg()
}

fun counterActor() = actor<CounterMsg> {
    var counter = 0

    for (msg in channel) {
        when (msg) {
            is CounterMsg.Increment -> counter++
            is CounterMsg.Decrement -> counter--
            is CounterMsg.GetValue -> msg.response.complete(counter)
        }
    }
}

// Usage
fun actorExample() = runBlocking {
    val counter = counterActor()

    counter.send(CounterMsg.Increment)
    counter.send(CounterMsg.Increment)
    counter.send(CounterMsg.Decrement)

    val response = CompletableDeferred<Int>()
    counter.send(CounterMsg.GetValue(response))
    println("Counter value: ${response.await()}") // 1

    counter.close()
}

// Comparison: Manual actor vs builder
class ActorComparison {

    //  Manual approach
    suspend fun manualActor(): SendChannel<CounterMsg> {
        val channel = Channel<CounterMsg>()
        var counter = 0

        launch {
            for (msg in channel) {
                when (msg) {
                    is CounterMsg.Increment -> counter++
                    is CounterMsg.Decrement -> counter--
                    is CounterMsg.GetValue -> msg.response.complete(counter)
                }
            }
        }

        return channel
    }

    //  Using actor builder
    fun withActor() = actor<CounterMsg> {
        var counter = 0

        for (msg in channel) {
            when (msg) {
                is CounterMsg.Increment -> counter++
                is CounterMsg.Decrement -> counter--
                is CounterMsg.GetValue -> msg.response.complete(counter)
            }
        }
    }
}
```

### Actor Features and Benefits

```kotlin
class ActorFeatures {

    // 1. State encapsulation
    class BankAccount(initialBalance: Int) {
        sealed class Msg {
            data class Deposit(val amount: Int) : Msg()
            data class Withdraw(val amount: Int, val response: CompletableDeferred<Boolean>) : Msg()
            data class GetBalance(val response: CompletableDeferred<Int>) : Msg()
        }

        private val actor = CoroutineScope(Dispatchers.Default).actor<Msg> {
            var balance = initialBalance

            for (msg in channel) {
                when (msg) {
                    is Msg.Deposit -> {
                        balance += msg.amount
                        println("Deposited ${msg.amount}, balance: $balance")
                    }
                    is Msg.Withdraw -> {
                        val success = balance >= msg.amount
                        if (success) {
                            balance -= msg.amount
                            println("Withdrew ${msg.amount}, balance: $balance")
                        }
                        msg.response.complete(success)
                    }
                    is Msg.GetBalance -> {
                        msg.response.complete(balance)
                    }
                }
            }
        }

        suspend fun deposit(amount: Int) {
            actor.send(Msg.Deposit(amount))
        }

        suspend fun withdraw(amount: Int): Boolean {
            val response = CompletableDeferred<Boolean>()
            actor.send(Msg.Withdraw(amount, response))
            return response.await()
        }

        suspend fun getBalance(): Int {
            val response = CompletableDeferred<Int>()
            actor.send(Msg.GetBalance(response))
            return response.await()
        }

        fun close() {
            actor.close()
        }
    }

    // 2. Sequential message processing
    fun sequentialProcessing() = runBlocking {
        data class LogMsg(val level: String, val message: String)

        val logger = actor<LogMsg> {
            for (msg in channel) {
                // Messages processed one at a time, in order
                println("[${msg.level}] ${msg.message}")
                delay(100) // Simulate slow I/O
            }
        }

        // Send from multiple coroutines
        repeat(10) { i ->
            launch {
                logger.send(LogMsg("INFO", "Message $i"))
            }
        }

        delay(1500)
        logger.close()
    }

    // 3. Buffering configuration
    fun withBuffering() = actor<String>(capacity = 100) {
        for (msg in channel) {
            processMessage(msg)
        }
    }

    private suspend fun processMessage(msg: String) {
        delay(10)
    }
}
```

### Actor Use Cases

```kotlin
class ActorUseCases {

    // Use Case 1: Cache manager
    class CacheActor<K, V> {
        sealed class Msg<K, V> {
            data class Put<K, V>(val key: K, val value: V) : Msg<K, V>()
            data class Get<K, V>(val key: K, val response: CompletableDeferred<V?>) : Msg<K, V>()
            data class Remove<K, V>(val key: K) : Msg<K, V>()
        }

        private val actor = CoroutineScope(Dispatchers.Default).actor<Msg<K, V>> {
            val cache = mutableMapOf<K, V>()

            for (msg in channel) {
                when (msg) {
                    is Msg.Put -> cache[msg.key] = msg.value
                    is Msg.Get -> msg.response.complete(cache[msg.key])
                    is Msg.Remove -> cache.remove(msg.key)
                }
            }
        }

        suspend fun put(key: K, value: V) {
            actor.send(Msg.Put(key, value))
        }

        suspend fun get(key: K): V? {
            val response = CompletableDeferred<V?>()
            actor.send(Msg.Get(key, response))
            return response.await()
        }

        suspend fun remove(key: K) {
            actor.send(Msg.Remove(key))
        }
    }

    // Use Case 2: Rate limiter
    class RateLimiterActor(private val maxRequests: Int, private val periodMs: Long) {
        sealed class Msg {
            data class Request(val id: String, val response: CompletableDeferred<Boolean>) : Msg()
        }

        private val actor = CoroutineScope(Dispatchers.Default).actor<Msg> {
            val timestamps = mutableListOf<Long>()

            for (msg in channel) {
                when (msg) {
                    is Msg.Request -> {
                        val now = System.currentTimeMillis()

                        // Remove old timestamps
                        timestamps.removeAll { now - it > periodMs }

                        val allowed = timestamps.size < maxRequests
                        if (allowed) {
                            timestamps.add(now)
                        }

                        msg.response.complete(allowed)
                    }
                }
            }
        }

        suspend fun tryAcquire(id: String): Boolean {
            val response = CompletableDeferred<Boolean>()
            actor.send(Msg.Request(id, response))
            return response.await()
        }
    }

    // Use Case 3: Task queue
    class TaskQueueActor {
        sealed class Msg {
            data class AddTask(val task: suspend () -> Unit) : Msg()
            object ProcessNext : Msg()
        }

        private val actor = CoroutineScope(Dispatchers.Default).actor<Msg> {
            val queue = mutableListOf<suspend () -> Unit>()

            for (msg in channel) {
                when (msg) {
                    is Msg.AddTask -> queue.add(msg.task)
                    is Msg.ProcessNext -> {
                        if (queue.isNotEmpty()) {
                            val task = queue.removeAt(0)
                            task()
                        }
                    }
                }
            }
        }

        suspend fun addTask(task: suspend () -> Unit) {
            actor.send(Msg.AddTask(task))
        }

        suspend fun processNext() {
            actor.send(Msg.ProcessNext)
        }
    }
}
```

### Produce Vs Actor Comparison

```kotlin
/**
 * PRODUCE vs ACTOR
 *
 *
 *  Aspect            produce               actor
 *
 *  Purpose           Generate values       Process messages
 *  Direction         Outbound (send)       Inbound (receive)
 *  Return Type       ReceiveChannel        SendChannel
 *  Primary Use       Producer pattern      Actor pattern
 *  State             Usually stateless     Usually stateful
 *  Consumer          External              Internal
 *  Pattern           One-to-many           Many-to-one
 *
 */

class ProduceVsActorExamples {

    // PRODUCE: Generating sequence
    fun fibonacci() = produce {
        var a = 0
        var b = 1
        while (true) {
            send(a)
            val next = a + b
            a = b
            b = next
        }
    }

    // ACTOR: Processing requests
    fun requestProcessor() = actor<Request> {
        for (request in channel) {
            processRequest(request)
        }
    }

    data class Request(val id: Int)
    private suspend fun processRequest(request: Request) {}
}
```

### Advanced Patterns

```kotlin
class AdvancedPatterns {

    // Pipeline with produce
    fun pipeline() = runBlocking {
        val numbers = produce {
            for (i in 1..10) send(i)
        }

        val squares = produce {
            for (num in numbers) send(num * num)
        }

        val formatted = produce {
            for (sq in squares) send("Value: $sq")
        }

        for (result in formatted) {
            println(result)
        }
    }

    // Actor-based state machine
    class StateMachineActor {
        sealed class State {
            object Idle : State()
            object Running : State()
            object Paused : State()
        }

        sealed class Msg {
            object Start : Msg()
            object Pause : Msg()
            object Resume : Msg()
            object Stop : Msg()
            data class GetState(val response: CompletableDeferred<State>) : Msg()
        }

        private val actor = CoroutineScope(Dispatchers.Default).actor<Msg> {
            var state: State = State.Idle

            for (msg in channel) {
                state = when (msg) {
                    is Msg.Start -> State.Running
                    is Msg.Pause -> if (state is State.Running) State.Paused else state
                    is Msg.Resume -> if (state is State.Paused) State.Running else state
                    is Msg.Stop -> State.Idle
                    is Msg.GetState -> {
                        msg.response.complete(state)
                        state
                    }
                }
                println("State transition: $state")
            }
        }

        suspend fun start() = actor.send(Msg.Start)
        suspend fun pause() = actor.send(Msg.Pause)
        suspend fun resume() = actor.send(Msg.Resume)
        suspend fun stop() = actor.send(Msg.Stop)

        suspend fun getState(): State {
            val response = CompletableDeferred<State>()
            actor.send(Msg.GetState(response))
            return response.await()
        }
    }

    // Coordinated actors
    class CoordinatedActors {
        data class WorkItem(val id: Int, val data: String)

        val dispatcher = actor<WorkItem> {
            val workers = List(3) { createWorker(it) }
            var nextWorker = 0

            for (item in channel) {
                workers[nextWorker].send(item)
                nextWorker = (nextWorker + 1) % workers.size
            }

            workers.forEach { it.close() }
        }

        private fun CoroutineScope.createWorker(id: Int) = actor<WorkItem> {
            for (item in channel) {
                println("Worker $id processing ${item.id}")
                delay(100)
            }
        }
    }
}
```

### Testing Produce and Actor

```kotlin
class BuilderTests {

    @Test
    fun `test produce generates values`() = runTest {
        val numbers = produce {
            for (i in 1..5) send(i)
        }

        val values = mutableListOf<Int>()
        for (num in numbers) {
            values.add(num)
        }

        assertEquals(listOf(1, 2, 3, 4, 5), values)
    }

    @Test
    fun `test actor processes messages`() = runTest {
        val counter = actor<CounterMsg> {
            var count = 0
            for (msg in channel) {
                when (msg) {
                    is CounterMsg.Increment -> count++
                    is CounterMsg.GetValue -> msg.response.complete(count)
                    else -> {}
                }
            }
        }

        counter.send(CounterMsg.Increment)
        counter.send(CounterMsg.Increment)

        val response = CompletableDeferred<Int>()
        counter.send(CounterMsg.GetValue(response))

        assertEquals(2, response.await())
        counter.close()
    }

    @Test
    fun `test produce handles cancellation`() = runTest {
        val numbers = produce {
            var i = 0
            while (true) {
                send(i++)
                delay(100)
            }
        }

        repeat(3) {
            numbers.receive()
        }

        numbers.cancel()

        assertTrue(numbers.isClosedForReceive)
    }
}
```

---

## Ответ (RU)

Билдеры `produce` и `actor` - это высокоуровневые функции создания каналов, упрощающие общие паттерны корутин.

### Produce: Паттерн Производителя

```kotlin
val numbers = produce {
    for (i in 1..5) {
        send(i)
    }
    // Канал автоматически закрывается
}

for (num in numbers) {
    println(num)
}
```

**Преимущества produce**:
- Автоматическое создание и закрытие канала
- Обработка отмены
- Пропаганда исключений
- Настройка емкости и диспетчера

### Actor: Паттерн Актора

```kotlin
val counter = actor<CounterMsg> {
    var count = 0
    for (msg in channel) {
        when (msg) {
            is Increment -> count++
            is GetValue -> msg.response.complete(count)
        }
    }
}

counter.send(Increment)
```

**Преимущества actor**:
- Инкапсуляция состояния
- Последовательная обработка сообщений
- Потокобезопасность
- Паттерн "актор-модель"

### Когда Использовать

**produce**: Генерация последовательности значений, потоки данных
**actor**: Обработка запросов, управление состоянием, координация

---

## Follow-up Questions (Следующие вопросы)

1. **How do produce and actor handle exceptions?**
   - Exception propagation
   - Error recovery
   - Channel state after exception

2. **Can you compose multiple actors together?**
   - Actor hierarchies
   - Message routing
   - Coordination patterns

3. **How to test code using produce and actor?**
   - Testing patterns
   - Mocking actors
   - Verifying message flow

4. **What are the performance implications?**
   - Memory overhead
   - Message processing speed
   - Comparison with manual channels

5. **How to implement timeout in actor messages?**
   - Timeout strategies
   - Deadlock prevention
   - Response handling

---

## References (Ссылки)

### Official Documentation
- [produce Builder](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html)
- [actor Builder](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/actor.html)
- [Channels Guide](https://kotlinlang.org/docs/channels.html)

### Learning Resources
- "Kotlin Coroutines" by Marcin Moskała - Channel Builders
- [Actor Model in Kotlin](https://elizarov.medium.com/kotlin-coroutines-and-actor-model-5b88f908e352)

### Related Topics
- Actor Model
- Producer-Consumer Pattern
- CSP (Communicating Sequential Processes)

---

## Related Questions (Связанные вопросы)

- [[q-channels-basics-types--kotlin--medium]] - Channel fundamentals
- [[q-channel-closing-completion--kotlin--medium]] - Channel lifecycle
- [[q-actor-pattern--kotlin--hard]] - Advanced actor patterns
- [[q-channel-pipelines--kotlin--hard]] - Channel pipelines
- [[q-select-expression-channels--kotlin--hard]] - select with channels

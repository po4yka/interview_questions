---
id: kotlin-065
title: "produce and actor Channel Builders / Билдеры каналов produce и actor"
aliases: ["produce and actor Channel Builders", "Билдеры каналов produce и actor"]

# Classification
topic: kotlin
subtopics: [channels, coroutines, functions]
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
related: [c-coroutines, c-kotlin, q-actor-pattern--kotlin--hard, q-channel-closing-completion--kotlin--medium, q-channels-basics-types--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [actor, builders, channels, coroutines, difficulty/medium, kotlin, produce]
---
# Вопрос (RU)
> Что такое билдеры каналов `produce` и `actor`? Объясните их назначение, автоматическое управление ресурсами, особенности привязки к `CoroutineScope` и когда использовать каждый паттерн билдера.

# Question (EN)
> What are `produce` and `actor` channel builders? Explain their purpose, automatic resource management, scope-binding semantics, and when to use each builder pattern.

---

## Ответ (RU)

Билдеры `produce` и `actor` — это высокоуровневые функции (`CoroutineScope.produce` и `CoroutineScope.actor`) из `kotlinx.coroutines.channels`, которые упрощают типичные паттерны взаимодействия корутин через каналы и обеспечивают автоматическое управление ресурсами при использовании в рамках структурированной конкуренции.

Ключевая идея: каждый билдер определён как extension-функция на `CoroutineScope` и запускает корутину, привязанную к этому скоупу. Когда скоуп отменяется, соответствующая корутина и связанный канал также отменяются/закрываются. Это помогает избегать утечек и естественно встраивает продьюсеров и акторов в дерево структурированной конкуренции.

> См. также: [[c-kotlin]], [[c-coroutines]], [[c-structured-concurrency]] (если доступен в хранилище; в противном случае используйте документацию kotlinx.coroutines).

### Produce: Паттерн Производителя (Builder)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Базовый пример produce
fun basicProduceRu() = runBlocking {
    val numbers: ReceiveChannel<Int> = produce {
        for (i in 1..5) {
            send(i)
        }
        // Канал автоматически закрывается после успешного завершения блока
    }

    for (num in numbers) {
        println("Получено: $num")
    }
    // Вывод построчно:
    // Получено: 1
    // Получено: 2
    // ... до 5
}

// Сравнение: ручной канал vs produce
class ProduceComparisonRu {

    // Ручной подход (больше бойлерплейта)
    fun CoroutineScope.manualChannel(): ReceiveChannel<Int> {
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

    // Использование produce (чище и безопаснее в рамках скоупа)
    fun CoroutineScope.withProduce(): ReceiveChannel<Int> = produce {
        for (i in 1..5) {
            send(i)
        }
        // Канал закрывается, когда продьюсер-корутина завершается
    }
}
```

### Возможности И Преимущества Produce

```kotlin
class ProduceFeaturesRu {

    // 1. Автоматическое создание и закрытие канала в рамках скоупа
    fun CoroutineScope.automaticManagement(): ReceiveChannel<Int> = produce {
        try {
            for (i in 1..10) {
                send(i)
            }
            println("Все значения успешно отправлены")
        } catch (e: Exception) {
            println("Ошибка в продьюсере: ${e.message}")
        }
        // При нормальном завершении канал закрывается.
        // При ошибке исключение будет доставлено потребителю.
    }

    // 2. Обработка отмены
    fun cancellationHandling() = runBlocking {
        val numbers = produce {
            var x = 1
            while (true) {
                send(x++)
                delay(100)
            }
        }

        // Берём только первые 5
        repeat(5) {
            println(numbers.receive())
        }

        numbers.cancel() // Отменяет продьюсер и закрывает канал
    }

    // 3. Проброс исключений
    fun exceptionPropagation() = runBlocking {
        val numbers = produce {
            for (i in 1..10) {
                if (i == 5) throw IllegalStateException("Ошибка на $i")
                send(i)
            }
        }

        try {
            for (num in numbers) {
                println(num)
            }
        } catch (e: IllegalStateException) {
            println("Потребитель увидел ошибку: ${e.message}")
        }
    }

    // 4. Настройка capacity
    fun CoroutineScope.withCapacity(): ReceiveChannel<Int> = produce(capacity = Channel.BUFFERED) {
        repeat(100) {
            send(it)
            println("Отправлено $it")
        }
    }

    // 5. Настройка контекста/диспетчера
    fun CoroutineScope.withDispatcher(): ReceiveChannel<Int> = produce(context = Dispatchers.IO) {
        // Продьюсер работает на IO-диспетчере
        repeat(10) {
            send(readFromDatabase(it))
        }
    }

    private fun readFromDatabase(id: Int): Int = id
}
```

### Типичные Случаи Использования Produce

```kotlin
class ProduceUseCasesRu {

    // Use Case 1: Генератор диапазона
    fun CoroutineScope.rangeGenerator(start: Int, end: Int): ReceiveChannel<Int> = produce {
        for (i in start..end) {
            send(i)
        }
    }

    // Use Case 2: Чтение файла построчно
    fun CoroutineScope.readFileLines(file: java.io.File): ReceiveChannel<String> = produce(context = Dispatchers.IO) {
        file.bufferedReader().use { reader ->
            for (line in reader.lineSequence()) {
                send(line)
            }
        }
        // Канал закрывается после окончания чтения файла
    }

    // Use Case 3: Постраничная загрузка из API
    fun CoroutineScope.fetchAllPages(userId: String): ReceiveChannel<Page> = produce {
        var pageNumber = 1
        while (true) {
            val page = apiClient.fetchPage(userId, pageNumber)
            send(page)
            if (!page.hasNext) break
            pageNumber++
        }
    }

    data class Page(val data: List<String>, val hasNext: Boolean)

    object apiClient {
        fun fetchPage(userId: String, page: Int) = Page(emptyList(), hasNext = false)
    }
}
```

Примечание: для callback-источников событий с управляемым освобождением ресурсов чаще лучше подходят `callbackFlow` + `awaitClose`, чем `produce`.

### Actor: Паттерн Актора (Builder)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Сообщения
sealed class CounterMsgRu {
    object Increment : CounterMsgRu()
    object Decrement : CounterMsgRu()
    data class GetValue(val response: CompletableDeferred<Int>) : CounterMsgRu()
}

// actor-билдер вызывается на CoroutineScope
fun CoroutineScope.counterActorRu(): SendChannel<CounterMsgRu> = actor {
    var counter = 0

    for (msg in channel) {
        when (msg) {
            is CounterMsgRu.Increment -> counter++
            is CounterMsgRu.Decrement -> counter--
            is CounterMsgRu.GetValue -> msg.response.complete(counter)
        }
    }
}

// Использование
fun actorExampleRu() = runBlocking {
    val counter = counterActorRu() // скоуп runBlocking

    counter.send(CounterMsgRu.Increment)
    counter.send(CounterMsgRu.Increment)
    counter.send(CounterMsgRu.Decrement)

    val response = CompletableDeferred<Int>()
    counter.send(CounterMsgRu.GetValue(response))
    println("Значение счётчика: ${response.await()}") // 1

    counter.close() // После закрытия актор завершится после обработки очереди
}

// Сравнение: ручной актор vs actor-билдер
class ActorComparisonRu {

    // Ручной подход
    fun CoroutineScope.manualActor(): SendChannel<CounterMsgRu> {
        val channel = Channel<CounterMsgRu>()
        var counter = 0

        launch {
            for (msg in channel) {
                when (msg) {
                    is CounterMsgRu.Increment -> counter++
                    is CounterMsgRu.Decrement -> counter--
                    is CounterMsgRu.GetValue -> msg.response.complete(counter)
                }
            }
        }

        return channel
    }

    // Использование actor-билдера
    fun CoroutineScope.withActor(): SendChannel<CounterMsgRu> = actor {
        var counter = 0

        for (msg in channel) {
            when (msg) {
                is CounterMsgRu.Increment -> counter++
                is CounterMsgRu.Decrement -> counter--
                is CounterMsgRu.GetValue -> msg.response.complete(counter)
            }
        }
    }
}
```

### Возможности И Преимущества Actor

```kotlin
class ActorFeaturesRu {

    // 1. Инкапсуляция состояния (пример BankAccount)
    class BankAccount(initialBalance: Int) {
        sealed class Msg {
            data class Deposit(val amount: Int) : Msg()
            data class Withdraw(val amount: Int, val response: CompletableDeferred<Boolean>) : Msg()
            data class GetBalance(val response: CompletableDeferred<Int>) : Msg()
        }

        // Scope должен управляться жизненным циклом аккаунта
        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg> {
            var balance = initialBalance

            for (msg in channel) {
                when (msg) {
                    is Msg.Deposit -> {
                        balance += msg.amount
                        println("Пополнение ${msg.amount}, баланс: $balance")
                    }
                    is Msg.Withdraw -> {
                        val success = balance >= msg.amount
                        if (success) {
                            balance -= msg.amount
                            println("Снятие ${msg.amount}, баланс: $balance")
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
            scope.cancel()
        }
    }

    // 2. Последовательная обработка сообщений (пример логгера)
    fun sequentialProcessing() = runBlocking {
        data class LogMsg(val level: String, val message: String)

        val logger = actor<LogMsg> {
            for (msg in channel) {
                // Сообщения обрабатываются по одному, в порядке поступления
                println("[${msg.level}] ${msg.message}")
                delay(100) // эмуляция медленного I/O
            }
        }

        // Отправка из нескольких корутин
        repeat(10) { i ->
            launch {
                logger.send(LogMsg("INFO", "Сообщение $i"))
            }
        }

        delay(1500)
        logger.close()
    }

    // 3. Настройка буферизации
    fun CoroutineScope.withBuffering(): SendChannel<String> = actor(capacity = 100) {
        for (msg in channel) {
            processMessage(msg)
        }
    }

    private suspend fun processMessage(msg: String) {
        delay(10)
    }
}
```

### Типичные Случаи Использования Actor

```kotlin
class ActorUseCasesRu {

    // Use Case 1: Актор-кэш
    class CacheActor<K, V> {
        sealed class Msg<K, V> {
            data class Put<K, V>(val key: K, val value: V) : Msg<K, V>()
            data class Get<K, V>(val key: K, val response: CompletableDeferred<V?>) : Msg<K, V>()
            data class Remove<K, V>(val key: K) : Msg<K, V>()
        }

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg<K, V>> {
            val cache = mutableMapOf<K, V>()

            for (msg in channel) {
                when (msg) {
                    is Msg.Put<*, *> -> {
                        @Suppress("UNCHECKED_CAST")
                        cache[msg.key as K] = msg.value as V
                    }
                    is Msg.Get<*, *> -> {
                        @Suppress("UNCHECKED_CAST")
                        val typed = msg as Msg.Get<K, V>
                        typed.response.complete(cache[typed.key])
                    }
                    is Msg.Remove<*, *> -> {
                        @Suppress("UNCHECKED_CAST")
                        cache.remove(msg.key as K)
                    }
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

        fun close() {
            actor.close()
            scope.cancel()
        }
    }

    // Use Case 2: Rate limiter (токен-бакет)
    class RateLimiterActor(private val maxRequests: Int, private val periodMs: Long) {
        sealed class Msg {
            data class Request(val id: String, val response: CompletableDeferred<Boolean>) : Msg()
        }

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg> {
            val timestamps = mutableListOf<Long>()

            for (msg in channel) {
                when (msg) {
                    is Msg.Request -> {
                        val now = System.currentTimeMillis()

                        // Удаляем устаревшие отметки
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

        fun close() {
            actor.close()
            scope.cancel()
        }
    }

    // Use Case 3: Очередь задач
    class TaskQueueActor {
        sealed class Msg {
            data class AddTask(val task: suspend () -> Unit) : Msg()
            object ProcessNext : Msg()
        }

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg> {
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

        fun close() {
            actor.close()
            scope.cancel()
        }
    }
}
```

### Сравнение Produce И Actor

```kotlin
/**
 * PRODUCE vs ACTOR (обзор)
 *
 *  Aspect            produce                         actor
 *
 *  Purpose           Генерация значений              Обработка команд/сообщений
 *  Direction         Исходящий поток (producer -> consumer)
 *                    Входящий поток (клиенты -> actor)
 *  Return Type       ReceiveChannel                  SendChannel
 *  Primary Use       Producer-паттерн, пайплайны     Актор-модель, владение состоянием
 *  State             Обычно без состояния или внешнее Обычно инкапсулированное, изменяемое
 *  Consumer          Внешний код читает из канала    Внешний код шлёт в канал
 *  Pattern           Один → много потребителей       Многие отправители → один обработчик
 */

class ProduceVsActorExamplesRu {

    // PRODUCE: бесконечная последовательность Fibonacci
    fun CoroutineScope.fibonacci(): ReceiveChannel<Int> = produce {
        var a = 0
        var b = 1
        while (true) {
            send(a)
            val next = a + b
            a = b
            b = next
        }
    }

    // ACTOR: обработка запросов
    data class Request(val id: Int)

    fun CoroutineScope.requestProcessor(): SendChannel<Request> = actor {
        for (request in channel) {
            processRequest(request)
        }
    }

    private suspend fun processRequest(request: Request) {
        // обработка запроса
    }
}
```

### Продвинутые Паттерны

```kotlin
class AdvancedPatternsRu {

    // Простая pipeline-конструкция с produce (все в одном scope)
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
        // При завершении runBlocking все дочерние продьюсеры будут отменены.
    }

    // Актор как state machine
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

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg> {
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
                println("Переход состояния: $state")
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

        fun close() {
            actor.close()
            scope.cancel()
        }
    }

    // Координация нескольких акторов
    class CoordinatedActors {
        data class WorkItem(val id: Int, val data: String)

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        val dispatcher = scope.actor<WorkItem> {
            val workers = List(3) { createWorker(it) }
            var nextWorker = 0

            for (item in channel) {
                workers[nextWorker].send(item)
                nextWorker = (nextWorker + 1) % workers.size
            }

            workers.forEach { it.close() }
            scope.cancel()
        }

        private fun createWorker(id: Int) = scope.actor<WorkItem> {
            for (item in channel) {
                println("Worker $id обрабатывает ${item.id}")
                delay(100)
            }
        }
    }
}
```

### Тестирование Produce И Actor

```kotlin
import kotlinx.coroutines.test.runTest
import kotlin.test.*

class BuilderTestsRu {

    @Test
    fun `produce генерирует значения`() = runTest {
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
    fun `actor обрабатывает сообщения`() = runTest {
        sealed class Msg {
            object Increment : Msg()
            data class GetValue(val response: CompletableDeferred<Int>) : Msg()
        }

        val counter = actor<Msg> {
            var count = 0
            for (msg in channel) {
                when (msg) {
                    is Msg.Increment -> count++
                    is Msg.GetValue -> msg.response.complete(count)
                }
            }
        }

        counter.send(Msg.Increment)
        counter.send(Msg.Increment)

        val response = CompletableDeferred<Int>()
        counter.send(Msg.GetValue(response))

        assertEquals(2, response.await())
        counter.close()
    }

    @Test
    fun `produce корректно обрабатывает отмену`() = runTest {
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

### Когда Использовать (итог по-русски)

- `produce`:
  - когда нужен источник/поток данных (one-to-many, пайплайны, генераторы);
  - когда важен простой и безопасный lifecycle управления каналом.
- `actor`:
  - когда нужно потокобезопасно инкапсулировать изменяемое состояние;
  - когда много отправителей посылают команды/сообщения одному обработчику;
  - когда удобна актор-модель или state machine поверх сообщений.

Также важно вызывать эти билдеры на корректных скоупах (например, `coroutineScope`, `runBlocking`, `viewModelScope`, `lifecycleScope`) и не создавать "глобальные" скоупы без явного управления их жизненным циклом.

---

## Answer (EN)

The `produce` and `actor` builders are high-level channel construction functions (defined as extension functions on `CoroutineScope`) that simplify common coroutine patterns and provide automatic resource management when used in a structured concurrency context.

Note: These builders are part of `kotlinx.coroutines.channels`. They create coroutines bound to the scope on which they are called. When that scope is cancelled, the producer/actor and its channel are cancelled/closed accordingly.

### Produce: Producer Pattern Builder

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Basic produce usage
fun basicProduce() = runBlocking {
    val numbers: ReceiveChannel<Int> = produce {
        for (i in 1..5) {
            send(i)
        }
        // Channel automatically closed after this block completes successfully
    }

    for (num in numbers) {
        println("Received: $num")
    }
    // Output (line by line):
    // Received: 1
    // Received: 2
    // ... up to 5
}

// Comparison: Manual channel vs produce
class ProduceComparison {

    // Manual approach (more boilerplate)
    fun CoroutineScope.manualChannel(): ReceiveChannel<Int> {
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

    // Using produce (cleaner, safer in this scoped form)
    fun CoroutineScope.withProduce(): ReceiveChannel<Int> = produce {
        for (i in 1..5) {
            send(i)
        }
        // Channel closed when this producer coroutine completes
    }
}
```

### Produce Features and Benefits

```kotlin
class ProduceFeatures {

    // 1. Automatic channel creation and closing within scope
    fun CoroutineScope.automaticManagement(): ReceiveChannel<Int> = produce {
        try {
            for (i in 1..10) {
                send(i)
            }
            println("All sent successfully")
        } catch (e: Exception) {
            println("Error in producer: ${e.message}")
        }
        // On normal completion, channel is closed.
        // On failure, the exception is propagated to the consumer side.
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

        numbers.cancel() // Cancels producer coroutine and closes the channel
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
        } catch (e: IllegalStateException) {
            println("Consumer observed failure: ${e.message}")
        }
    }

    // 4. Capacity configuration
    fun CoroutineScope.withCapacity(): ReceiveChannel<Int> = produce(capacity = Channel.BUFFERED) {
        repeat(100) {
            send(it)
            println("Sent $it")
        }
    }

    // 5. Dispatcher / context configuration
    fun CoroutineScope.withDispatcher(): ReceiveChannel<Int> = produce(context = Dispatchers.IO) {
        // Producer coroutine runs on IO dispatcher
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
    fun CoroutineScope.rangeGenerator(start: Int, end: Int): ReceiveChannel<Int> = produce {
        for (i in start..end) {
            send(i)
        }
    }

    // Use Case 2: File reader
    fun CoroutineScope.readFileLines(file: java.io.File): ReceiveChannel<String> = produce(context = Dispatchers.IO) {
        file.bufferedReader().use { reader ->
            for (line in reader.lineSequence()) {
                send(line)
            }
        }
        // Channel closes when file reading is done
    }

    // Use Case 3: API pagination
    fun CoroutineScope.fetchAllPages(userId: String): ReceiveChannel<Page> = produce {
        var pageNumber = 1
        while (true) {
            val page = apiClient.fetchPage(userId, pageNumber)
            send(page)
            if (!page.hasNext) break
            pageNumber++
        }
    }

    data class Page(val data: List<String>, val hasNext: Boolean)

    object apiClient {
        fun fetchPage(userId: String, page: Int) = Page(emptyList(), hasNext = false)
    }
}
```

Note: For callback-based event sources with lifecycle-aware cleanup, prefer `callbackFlow` and `awaitClose` instead of `produce`.

### Actor: Actor Pattern Builder

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Messages
sealed class CounterMsg {
    object Increment : CounterMsg()
    object Decrement : CounterMsg()
    data class GetValue(val response: CompletableDeferred<Int>) : CounterMsg()
}

// Actor builder must be called on a CoroutineScope
fun CoroutineScope.counterActor(): SendChannel<CounterMsg> = actor {
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
    val counter = counterActor() // this refers to runBlocking's scope

    counter.send(CounterMsg.Increment)
    counter.send(CounterMsg.Increment)
    counter.send(CounterMsg.Decrement)

    val response = CompletableDeferred<Int>()
    counter.send(CounterMsg.GetValue(response))
    println("Counter value: ${response.await()}") // 1

    counter.close() // After closing, actor finishes when all messages are processed
}

// Comparison: Manual actor vs builder
class ActorComparison {

    // Manual approach
    fun CoroutineScope.manualActor(): SendChannel<CounterMsg> {
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

    // Using actor builder
    fun CoroutineScope.withActor(): SendChannel<CounterMsg> = actor {
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

        // Scope should be owned/managed by the account's lifecycle
        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg> {
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
            scope.cancel()
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
    fun CoroutineScope.withBuffering(): SendChannel<String> = actor(capacity = 100) {
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

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg<K, V>> {
            val cache = mutableMapOf<K, V>()

            for (msg in channel) {
                when (msg) {
                    is Msg.Put<*, *> -> {
                        @Suppress("UNCHECKED_CAST")
                        cache[msg.key as K] = msg.value as V
                    }
                    is Msg.Get<*, *> -> {
                        @Suppress("UNCHECKED_CAST")
                        val typed = msg as Msg.Get<K, V>
                        typed.response.complete(cache[typed.key])
                    }
                    is Msg.Remove<*, *> -> {
                        @Suppress("UNCHECKED_CAST")
                        cache.remove(msg.key as K)
                    }
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

        fun close() {
            actor.close()
            scope.cancel()
        }
    }

    // Use Case 2: Rate limiter (simple token bucket style)
    class RateLimiterActor(private val maxRequests: Int, private val periodMs: Long) {
        sealed class Msg {
            data class Request(val id: String, val response: CompletableDeferred<Boolean>) : Msg()
        }

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg> {
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

        fun close() {
            actor.close()
            scope.cancel()
        }
    }

    // Use Case 3: Task queue
    class TaskQueueActor {
        sealed class Msg {
            data class AddTask(val task: suspend () -> Unit) : Msg()
            object ProcessNext : Msg()
        }

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg> {
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

        fun close() {
            actor.close()
            scope.cancel()
        }
    }
}
```

### Produce Vs Actor Comparison

```kotlin
/**
 * PRODUCE vs ACTOR
 *
 *  Aspect            produce                        actor
 *
 *  Purpose           Generate values                Process commands/messages
 *  Direction         Outbound (producer -> consumer) Inbound (clients -> actor)
 *  Return Type       ReceiveChannel                 SendChannel
 *  Primary Use       Producer pattern, pipelines    Actor model, state ownership
 *  State             Usually stateless or external  Usually encapsulated, mutable
 *  Consumer          External reads from channel    External sends to channel
 *  Pattern           One-to-many consumers          Many-to-one sender(s)
 */

class ProduceVsActorExamples {

    // PRODUCE: Generating infinite sequence
    fun CoroutineScope.fibonacci(): ReceiveChannel<Int> = produce {
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
    data class Request(val id: Int)

    fun CoroutineScope.requestProcessor(): SendChannel<Request> = actor {
        for (request in channel) {
            processRequest(request)
        }
    }

    private suspend fun processRequest(request: Request) {
        // handle request
    }
}
```

### Advanced Patterns

```kotlin
class AdvancedPatterns {

    // Simple pipeline with produce (all within a scope)
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

        // When runBlocking completes, all child producers are cancelled if still running.
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

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        private val actor = scope.actor<Msg> {
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

        fun close() {
            actor.close()
            scope.cancel()
        }
    }

    // Coordinated actors
    class CoordinatedActors {
        data class WorkItem(val id: Int, val data: String)

        private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

        val dispatcher = scope.actor<WorkItem> {
            val workers = List(3) { createWorker(it) }
            var nextWorker = 0

            for (item in channel) {
                workers[nextWorker].send(item)
                nextWorker = (nextWorker + 1) % workers.size
            }

            workers.forEach { it.close() }
            scope.cancel()
        }

        private fun createWorker(id: Int) = scope.actor<WorkItem> {
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
import kotlinx.coroutines.test.runTest
import kotlin.test.*

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
        sealed class Msg {
            object Increment : Msg()
            data class GetValue(val response: CompletableDeferred<Int>) : Msg()
        }

        val counter = actor<Msg> {
            var count = 0
            for (msg in channel) {
                when (msg) {
                    is Msg.Increment -> count++
                    is Msg.GetValue -> msg.response.complete(count)
                }
            }
        }

        counter.send(Msg.Increment)
        counter.send(Msg.Increment)

        val response = CompletableDeferred<Int>()
        counter.send(Msg.GetValue(response))

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

## Дополнительные Вопросы (RU)

1. Как `produce` и `actor` обрабатывают исключения?
   - Проброс исключений от продьюсера/актора к потребителям/вызывающим сторонам
   - Стратегии восстановления
   - Состояние канала после ошибки или отмены

2. Можно ли компоновать несколько акторов вместе?
   - Иерархии акторов
   - Маршрутизация сообщений
   - Паттерны координации

3. Как тестировать код с `produce` и `actor`?
   - Использование `runTest` и тестовых скоупов
   - Тестовые реализации акторов
   - Проверка потока и порядка сообщений

4. Каковы последствия для производительности?
   - Памятные накладные расходы каналов и корутин
   - Пропускная способность обработки сообщений
   - Сравнение с ручными каналами / мьютексами

5. Как реализовать тайм-аут для сообщений актора?
   - `withTimeout` / `select`
   - Предотвращение дедлоков
   - Обработка ответов и fallback-сценарии

## Follow-ups (EN)

1. How do `produce` and `actor` handle exceptions?
   - Exception propagation from producer/actor to consumers/callers
   - Error recovery strategies
   - Channel state after failure or cancellation

2. Can you compose multiple actors together?
   - Actor hierarchies
   - Message routing
   - Coordination patterns

3. How to test code using `produce` and `actor`?
   - Using `runTest` and test scopes
   - Test implementations / mocks
   - Verifying message flow and ordering

4. What are the performance implications?
   - Memory overhead of channels and coroutines
   - Message processing throughput
   - Comparison with manual channels / mutexes

5. How to implement timeout in actor messages?
   - Timeout strategies with `withTimeout` / `select`
   - Deadlock prevention
   - Response handling and fallbacks

---

## References (EN/RU)

### Official Documentation
- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/produce.html
- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/actor.html
- https://kotlinlang.org/docs/channels.html

### Learning Resources
- "Kotlin Coroutines" by Marcin Moskała - Channel Builders
- https://elizarov.medium.com/kotlin-coroutines-and-actor-model-5b88f908e352

### Related Topics
- Actor Model
- Producer-Consumer Pattern
- CSP (Communicating Sequential Processes)

---

## Related Questions (Связанные вопросы)

- [[q-channels-basics-types--kotlin--medium]]
- [[q-channel-closing-completion--kotlin--medium]]
- [[q-actor-pattern--kotlin--hard]]
- [[q-channel-pipelines--kotlin--hard]]
- [[q-select-expression-channels--kotlin--hard]]

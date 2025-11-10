---
id: kotlin-066
title: "Actor Pattern with Coroutines / Паттерн Actor с корутинами"
aliases: ["Actor Pattern with Coroutines", "Паттерн Actor с корутинами"]

# Classification
topic: kotlin
subtopics:
  - channels
  - coroutines
  - state-management
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Actor pattern with Kotlin Coroutines

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-kotlin, q-advanced-coroutine-patterns--kotlin--hard, q-channel-buffering-strategies--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [actor, channels, concurrency, coroutines, difficulty/hard, kotlin, message-passing, state-encapsulation]
---
# Вопрос (RU)
> Что такое паттерн Actor в корутинах Kotlin? Объясните передачу сообщений через каналы, инкапсуляцию состояния и приведите реальные примеры акторов.

---

# Question (EN)
> What is the Actor pattern in Kotlin coroutines? Explain message passing with channels, state encapsulation, and provide real-world examples of actors.

## Ответ (RU)

Паттерн **Actor** - это модель параллелизма, где акторы являются изолированными единицами, которые обрабатывают сообщения последовательно, устраняя необходимость в явных блокировках и ручной синхронизации общего состояния. В Kotlin акторы обычно реализуются с использованием корутин и каналов ([[c-coroutines]]).

### Ключевые Концепции

1. **Actor**: Независимая сущность с приватным состоянием.
2. **Передача сообщений**: Коммуникация через каналы.
3. **Последовательная обработка**: Сообщения обрабатываются по одному в цикле.
4. **Инкапсуляция состояния**: Нет общего изменяемого состояния вне актора.
5. **Потокобезопасность**: Отсутствие гонок за счёт доступа к состоянию только из одного потока выполнения актора.
6. **Почтовый ящик**: Очередь сообщений (обычно `Channel`).

### Архитектура Модели Акторов

```

            Актор

       Приватное состояние
    (доступно только коду актора)



     Цикл обработки сообщений
     (обработка по одному)



        Почтовый ящик (Channel)



          Сообщения от
          внешних отправителей
```

### Базовая Реализация Актора

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Типы сообщений
sealed class CounterMsg
object IncCounter : CounterMsg()
object DecCounter : CounterMsg()
class GetCounter(val response: CompletableDeferred<Int>) : CounterMsg()

// Функция актора
fun CoroutineScope.counterActor() = actor<CounterMsg> {
    var counter = 0  // Приватное состояние

    for (msg in channel) {  // Обработка сообщений последовательно
        when (msg) {
            is IncCounter -> counter++
            is DecCounter -> counter--
            is GetCounter -> msg.response.complete(counter)
        }
    }
}

// Использование
suspend fun main() = coroutineScope {
    val counter = counterActor()

    // Отправка сообщений
    counter.send(IncCounter)
    counter.send(IncCounter)
    counter.send(IncCounter)
    counter.send(DecCounter)

    // Получение текущего значения
    val response = CompletableDeferred<Int>()
    counter.send(GetCounter(response))
    println("Счётчик: ${response.await()}")  // Счётчик: 2

    counter.close()
}
```

### Функция-строитель Actor

```kotlin
fun <T> CoroutineScope.actor(
    context: CoroutineContext = EmptyCoroutineContext,
    capacity: Int = 0,  // По умолчанию rendezvous-канал
    start: CoroutineStart = CoroutineStart.DEFAULT,
    onCompletion: CompletionHandler? = null,
    block: suspend ActorScope<T>.() -> Unit
): SendChannel<T>

// ActorScope предоставляет:
// - channel: ReceiveChannel<T> для получения сообщений
// - интерфейс SendChannel<T> для отправки сообщений
```

### Актор-счётчик с улучшенным API

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Типы сообщений
sealed class CounterMsg
object IncCounter : CounterMsg()
object DecCounter : CounterMsg()
class GetCounter(val response: CompletableDeferred<Int>) : CounterMsg()
class SetCounter(val value: Int) : CounterMsg()
object Reset : CounterMsg()

class CounterActor(scope: CoroutineScope) {
    private val actor = scope.actor<CounterMsg> {
        var counter = 0

        for (msg in channel) {
            when (msg) {
                is IncCounter -> counter++
                is DecCounter -> counter--
                is GetCounter -> msg.response.complete(counter)
                is SetCounter -> counter = msg.value
                is Reset -> counter = 0
            }
        }
    }

    suspend fun increment() = actor.send(IncCounter)
    suspend fun decrement() = actor.send(DecCounter)

    suspend fun get(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(GetCounter(response))
        return response.await()
    }

    suspend fun set(value: Int) = actor.send(SetCounter(value))
    suspend fun reset() = actor.send(Reset)

    fun close() = actor.close()
}
```

### Реальный пример: Актор банковского счёта

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class AccountMsg
class Deposit(val amount: Double, val response: CompletableDeferred<Result<Unit>>) : AccountMsg()
class Withdraw(val amount: Double, val response: CompletableDeferred<Result<Unit>>) : AccountMsg()
class GetBalance(val response: CompletableDeferred<Double>) : AccountMsg()
class Transfer(
    val toAccount: SendChannel<AccountMsg>,
    val amount: Double,
    val response: CompletableDeferred<Result<Unit>>
) : AccountMsg()

sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

class BankAccount(
    scope: CoroutineScope,
    private val accountId: String,
    initialBalance: Double = 0.0
) {
    internal val actor = scope.actor<AccountMsg> {
        var balance = initialBalance

        for (msg in channel) {
            when (msg) {
                is Deposit -> {
                    if (msg.amount <= 0) {
                        msg.response.complete(Result.Error("Неверная сумма"))
                    } else {
                        balance += msg.amount
                        println("[$accountId] Пополнение ${msg.amount}, Баланс: $balance")
                        msg.response.complete(Result.Success(Unit))
                    }
                }

                is Withdraw -> {
                    when {
                        msg.amount <= 0 -> {
                            msg.response.complete(Result.Error("Неверная сумма"))
                        }
                        balance < msg.amount -> {
                            msg.response.complete(Result.Error("Недостаточно средств"))
                        }
                        else -> {
                            balance -= msg.amount
                            println("[$accountId] Снятие ${msg.amount}, Баланс: $balance")
                            msg.response.complete(Result.Success(Unit))
                        }
                    }
                }

                is GetBalance -> {
                    msg.response.complete(balance)
                }

                is Transfer -> {
                    when {
                        msg.amount <= 0 -> {
                            msg.response.complete(Result.Error("Неверная сумма"))
                        }
                        balance < msg.amount -> {
                            msg.response.complete(Result.Error("Недостаточно средств"))
                        }
                        else -> {
                            // Списываем с этого счёта
                            balance -= msg.amount
                            println("[$accountId] Перевод ${msg.amount}, Баланс: $balance")

                            // Пытаемся зачислить на другой счёт
                            val depositResponse = CompletableDeferred<Result<Unit>>()
                            msg.toAccount.send(Deposit(msg.amount, depositResponse))

                            when (val result = depositResponse.await()) {
                                is Result.Success -> {
                                    msg.response.complete(Result.Success(Unit))
                                }
                                is Result.Error -> {
                                    // Откат при ошибке
                                    balance += msg.amount
                                    msg.response.complete(Result.Error("Перевод не выполнен: ${result.message}"))
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    suspend fun deposit(amount: Double): Result<Unit> {
        val response = CompletableDeferred<Result<Unit>>()
        actor.send(Deposit(amount, response))
        return response.await()
    }

    suspend fun withdraw(amount: Double): Result<Unit> {
        val response = CompletableDeferred<Result<Unit>>()
        actor.send(Withdraw(amount, response))
        return response.await()
    }

    suspend fun getBalance(): Double {
        val response = CompletableDeferred<Double>()
        actor.send(GetBalance(response))
        return response.await()
    }

    suspend fun transfer(toAccount: BankAccount, amount: Double): Result<Unit> {
        val response = CompletableDeferred<Result<Unit>>()
        actor.send(Transfer(toAccount.actor, amount, response))
        return response.await()
    }

    fun close() = actor.close()
}
```

### Актор кэша (Cache Actor)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class CacheMsg<K, V>
class Put<K, V>(val key: K, val value: V) : CacheMsg<K, V>()
class Get<K, V>(val key: K, val response: CompletableDeferred<V?>) : CacheMsg<K, V>()
class Remove<K, V>(val key: K) : CacheMsg<K, V>()
class Clear<K, V> : CacheMsg<K, V>()
class Size<K, V>(val response: CompletableDeferred<Int>) : CacheMsg<K, V>()

class CacheActor<K, V>(
    scope: CoroutineScope,
    private val maxSize: Int = 100
) {
    private val actor = scope.actor<CacheMsg<K, V>> {
        val cache = LinkedHashMap<K, V>(maxSize, 0.75f, true)

        for (msg in channel) {
            when (msg) {
                is Put -> {
                    if (cache.size >= maxSize && !cache.containsKey(msg.key)) {
                        val oldestKey = cache.keys.first()
                        cache.remove(oldestKey)
                    }
                    cache[msg.key] = msg.value
                }
                is Get -> {
                    msg.response.complete(cache[msg.key])
                }
                is Remove -> {
                    cache.remove(msg.key)
                }
                is Clear -> {
                    cache.clear()
                }
                is Size -> {
                    msg.response.complete(cache.size)
                }
            }
        }
    }

    suspend fun put(key: K, value: V) = actor.send(Put(key, value))

    suspend fun get(key: K): V? {
        val response = CompletableDeferred<V?>()
        actor.send(Get(key, response))
        return response.await()
    }

    suspend fun remove(key: K) = actor.send(Remove(key))
    suspend fun clear() = actor.send(Clear())

    suspend fun size(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(Size(response))
        return response.await()
    }

    fun close() = actor.close()
}
```

### Актор ограничения частоты (Rate Limiter Actor)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class RateLimiterMsg
class TryAcquire(val response: CompletableDeferred<Boolean>) : RateLimiterMsg()
class GetAvailable(val response: CompletableDeferred<Int>) : RateLimiterMsg()

class RateLimiterActor(
    scope: CoroutineScope,
    private val maxRequests: Int,
    private val windowMillis: Long
) {
    private val actor = scope.actor<RateLimiterMsg> {
        val requests = mutableListOf<Long>()

        for (msg in channel) {
            val now = System.currentTimeMillis()
            requests.removeIf { it < now - windowMillis }

            when (msg) {
                is TryAcquire -> {
                    if (requests.size < maxRequests) {
                        requests.add(now)
                        msg.response.complete(true)
                    } else {
                        msg.response.complete(false)
                    }
                }
                is GetAvailable -> {
                    msg.response.complete(maxRequests - requests.size)
                }
            }
        }
    }

    suspend fun tryAcquire(): Boolean {
        val response = CompletableDeferred<Boolean>()
        actor.send(TryAcquire(response))
        return response.await()
    }

    suspend fun getAvailable(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(GetAvailable(response))
        return response.await()
    }

    fun close() = actor.close()
}
```

### Актор очереди задач (Task Queue Actor)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class TaskQueueMsg
class EnqueueTask(val task: suspend () -> Unit) : TaskQueueMsg()
class GetQueueSize(val response: CompletableDeferred<Int>) : TaskQueueMsg()
object PauseQueue : TaskQueueMsg()
object ResumeQueue : TaskQueueMsg()

class TaskQueueActor(
    scope: CoroutineScope,
    private val concurrency: Int = 1
) {
    private val actor = scope.actor<TaskQueueMsg>(capacity = Channel.UNLIMITED) {
        val queue = mutableListOf<suspend () -> Unit>()
        var isPaused = false
        val activeJobs = mutableListOf<Job>()

        suspend fun processQueue() {
            while (!isPaused && queue.isNotEmpty() && activeJobs.size < concurrency) {
                val task = queue.removeAt(0)
                val job = launch {
                    try {
                        task()
                    } finally {
                        activeJobs.remove(this)
                        processQueue()
                    }
                }
                activeJobs.add(job)
            }
        }

        for (msg in channel) {
            when (msg) {
                is EnqueueTask -> {
                    queue.add(msg.task)
                    processQueue()
                }
                is GetQueueSize -> {
                    msg.response.complete(queue.size)
                }
                is PauseQueue -> {
                    isPaused = true
                }
                is ResumeQueue -> {
                    isPaused = false
                    processQueue()
                }
            }
        }
    }

    suspend fun enqueue(task: suspend () -> Unit) = actor.send(EnqueueTask(task))

    suspend fun getQueueSize(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(GetQueueSize(response))
        return response.await()
    }

    suspend fun pause() = actor.send(PauseQueue)
    suspend fun resume() = actor.send(ResumeQueue)

    fun close() = actor.close()
}
```

### Обработка ошибок в акторах

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class SafeAccountMsg
class SafeDeposit(
    val amount: Double,
    val response: CompletableDeferred<Result<Unit>>
) : SafeAccountMsg()

sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

class SafeBankAccount(scope: CoroutineScope) {
    private val actor = scope.actor<SafeAccountMsg> {
        var balance = 0.0

        try {
            for (msg in channel) {
                try {
                    when (msg) {
                        is SafeDeposit -> {
                            if (msg.amount < 0) {
                                throw IllegalArgumentException("Negative amount")
                            }
                            balance += msg.amount
                            msg.response.complete(Result.Success(Unit))
                        }
                    }
                } catch (e: Exception) {
                    when (msg) {
                        is SafeDeposit -> msg.response.complete(
                            Result.Error(e.message ?: "Unknown error")
                        )
                    }
                }
            }
        } catch (e: Exception) {
            println("Actor failed: ${e.message}")
        }
    }

    suspend fun deposit(amount: Double): Result<Unit> {
        val response = CompletableDeferred<Result<Unit>>()
        actor.send(SafeDeposit(amount, response))
        return response.await()
    }

    fun close() = actor.close()
}
```

### Сравнение Actor и Mutex

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.system.measureTimeMillis

// Подход с Mutex
class MutexCounter {
    private var counter = 0
    private val mutex = Mutex()

    suspend fun increment() {
        mutex.withLock {
            counter++
        }
    }

    suspend fun get(): Int = mutex.withLock { counter }
}

// Подход с Actor
sealed class CounterMsg
object IncCounter : CounterMsg()
class GetCounter(val response: CompletableDeferred<Int>) : CounterMsg()

class ActorCounter(scope: CoroutineScope) {
    private val actor = scope.actor<CounterMsg> {
        var counter = 0
        for (msg in channel) {
            when (msg) {
                is IncCounter -> counter++
                is GetCounter -> msg.response.complete(counter)
            }
        }
    }

    suspend fun increment() = actor.send(IncCounter)

    suspend fun get(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(GetCounter(response))
        return response.await()
    }
}

// Пример грубого сравнения производительности
suspend fun main() = coroutineScope {
    val mutexCounter = MutexCounter()
    val mutexTime = measureTimeMillis {
        repeat(10_000) {
            launch { mutexCounter.increment() }
        }
    }
    println("Mutex: $mutexTime ms")

    val actorCounter = ActorCounter(this)
    val actorTime = measureTimeMillis {
        repeat(10_000) {
            launch { actorCounter.increment() }
        }
    }
    println("Actor: $actorTime ms")
}
```

### Лучшие Практики

#### ДЕЛАТЬ:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Держать состояние актора приватным
class GoodActor(scope: CoroutineScope) {
    private var state = 0
    private val actor = scope.actor<Msg> { /* ... */ }
}

// Использовать sealed классы для сообщений
sealed class Msg
object Increment : Msg()
class GetValue(val response: CompletableDeferred<Int>) : Msg()

// Обрабатывать ошибки
private val actor = scope.actor<Msg> {
    try {
        for (msg in channel) {
            when (msg) {
                // ...
            }
        }
    } catch (e: Exception) {
        // логирование и обработка
    }
}

// Предоставлять чистый API
suspend fun increment() = actor.send(Increment)
```

#### НЕ ДЕЛАТЬ:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Не выставлять изменяемое состояние наружу
class BadActor(scope: CoroutineScope) {
    var state = 0  // Плохо
}

// Не использовать акторы для слишком простых задач
val mutex = Mutex()
var counter = 0
suspend fun simpleIncrement() = mutex.withLock { counter++ }

// Не забывать закрывать акторы
val actor = actor<Msg> { /* ... */ }
actor.close()

// Не блокировать поток внутри актора
private val blockingActor = scope.actor<Msg> {
    for (msg in channel) {
        // Thread.sleep(1000) // Плохо
        delay(1000)          // Хорошо
    }
}
```

### Когда Использовать Акторы

Используйте акторы когда:
- Нужно управлять изменяемым состоянием с конкурентным доступом.
- Обновления состояния сложные и требуют нескольких шагов.
- Нужно сохранять порядок операций.
- Хотите избежать явных блокировок.
- Строите событийно-ориентированные системы.

Не используйте акторы когда:
- Простые атомарные операции (используйте `AtomicInteger`).
- Операции в основном на чтение (используйте `StateFlow`).
- Нужны немедленные ответы (акторы имеют накладные расходы).
- Состояние неизменяемо.

---

## Answer (EN)

The **Actor pattern** is a concurrency model where actors are isolated units that process messages sequentially, avoiding explicit locks and manual synchronization of shared mutable state. In Kotlin, actors are typically implemented using coroutines and channels.

### Key Concepts

1. **Actor**: Independent entity with private state.
2. **Message passing**: Communication via channels.
3. **Sequential processing**: Messages processed one at a time in a loop.
4. **State encapsulation**: No shared mutable state outside the actor.
5. **Thread-safe**: No race conditions because only the actor logic accesses its state.
6. **Mailbox**: Queue of messages (commonly a `Channel`).

### Actor Model Architecture

```

            Actor

       Private State
    (only actor can access)



     Message Processing Loop
     (processes one at a time)



        Mailbox (Channel)



          Messages from
          external senders
```

### Basic Actor Implementation

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Message types
sealed class CounterMsg
object IncCounter : CounterMsg()
object DecCounter : CounterMsg()
class GetCounter(val response: CompletableDeferred<Int>) : CounterMsg()

// Actor function
fun CoroutineScope.counterActor() = actor<CounterMsg> {
    var counter = 0  // Private state

    for (msg in channel) {  // Process messages sequentially
        when (msg) {
            is IncCounter -> counter++
            is DecCounter -> counter--
            is GetCounter -> msg.response.complete(counter)
        }
    }
}

// Usage
suspend fun main() = coroutineScope {
    val counter = counterActor()

    // Send messages
    counter.send(IncCounter)
    counter.send(IncCounter)
    counter.send(IncCounter)
    counter.send(DecCounter)

    // Get current value
    val response = CompletableDeferred<Int>()
    counter.send(GetCounter(response))
    println("Counter: ${response.await()}")  // Counter: 2

    counter.close()
}
```

### Actor Builder Function

```kotlin
fun <T> CoroutineScope.actor(
    context: CoroutineContext = EmptyCoroutineContext,
    capacity: Int = 0,  // Rendezvous by default
    start: CoroutineStart = CoroutineStart.DEFAULT,
    onCompletion: CompletionHandler? = null,
    block: suspend ActorScope<T>.() -> Unit
): SendChannel<T>

// ActorScope provides:
// - channel: ReceiveChannel<T> for receiving messages
// - SendChannel<T> interface for sending messages
```

### Counter Actor with Better API

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Message types
sealed class CounterMsg
object IncCounter : CounterMsg()
object DecCounter : CounterMsg()
class GetCounter(val response: CompletableDeferred<Int>) : CounterMsg()
class SetCounter(val value: Int) : CounterMsg()
object Reset : CounterMsg()

class CounterActor(scope: CoroutineScope) {
    private val actor = scope.actor<CounterMsg> {
        var counter = 0

        for (msg in channel) {
            when (msg) {
                is IncCounter -> counter++
                is DecCounter -> counter--
                is GetCounter -> msg.response.complete(counter)
                is SetCounter -> counter = msg.value
                is Reset -> counter = 0
            }
        }
    }

    suspend fun increment() = actor.send(IncCounter)
    suspend fun decrement() = actor.send(DecCounter)

    suspend fun get(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(GetCounter(response))
        return response.await()
    }

    suspend fun set(value: Int) = actor.send(SetCounter(value))
    suspend fun reset() = actor.send(Reset)

    fun close() = actor.close()
}

// Usage
suspend fun main() = coroutineScope {
    val counter = CounterActor(this)

    repeat(100) {
        launch { counter.increment() }
    }

    delay(100)
    println("Counter: ${counter.get()}")  // Counter: 100 (thread-safe!)

    counter.close()
}
```

### Real-World Example: Bank Account Actor

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class AccountMsg
class Deposit(val amount: Double, val response: CompletableDeferred<Result<Unit>>) : AccountMsg()
class Withdraw(val amount: Double, val response: CompletableDeferred<Result<Unit>>) : AccountMsg()
class GetBalance(val response: CompletableDeferred<Double>) : AccountMsg()
class Transfer(
    val toAccount: SendChannel<AccountMsg>,
    val amount: Double,
    val response: CompletableDeferred<Result<Unit>>
) : AccountMsg()

sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

class BankAccount(
    scope: CoroutineScope,
    private val accountId: String,
    initialBalance: Double = 0.0
) {
    internal val actor = scope.actor<AccountMsg> {
        var balance = initialBalance

        for (msg in channel) {
            when (msg) {
                is Deposit -> {
                    if (msg.amount <= 0) {
                        msg.response.complete(Result.Error("Invalid amount"))
                    } else {
                        balance += msg.amount
                        println("[$accountId] Deposited ${msg.amount}, Balance: $balance")
                        msg.response.complete(Result.Success(Unit))
                    }
                }

                is Withdraw -> {
                    when {
                        msg.amount <= 0 -> {
                            msg.response.complete(Result.Error("Invalid amount"))
                        }
                        balance < msg.amount -> {
                            msg.response.complete(Result.Error("Insufficient funds"))
                        }
                        else -> {
                            balance -= msg.amount
                            println("[$accountId] Withdrew ${msg.amount}, Balance: $balance")
                            msg.response.complete(Result.Success(Unit))
                        }
                    }
                }

                is GetBalance -> {
                    msg.response.complete(balance)
                }

                is Transfer -> {
                    when {
                        msg.amount <= 0 -> {
                            msg.response.complete(Result.Error("Invalid amount"))
                        }
                        balance < msg.amount -> {
                            msg.response.complete(Result.Error("Insufficient funds"))
                        }
                        else -> {
                            balance -= msg.amount
                            println("[$accountId] Transfer out ${msg.amount}, Balance: $balance")

                            val depositResponse = CompletableDeferred<Result<Unit>>()
                            msg.toAccount.send(Deposit(msg.amount, depositResponse))

                            when (val result = depositResponse.await()) {
                                is Result.Success -> {
                                    msg.response.complete(Result.Success(Unit))
                                }
                                is Result.Error -> {
                                    balance += msg.amount
                                    msg.response.complete(Result.Error("Transfer failed: ${result.message}"))
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    suspend fun deposit(amount: Double): Result<Unit> {
        val response = CompletableDeferred<Result<Unit>>()
        actor.send(Deposit(amount, response))
        return response.await()
    }

    suspend fun withdraw(amount: Double): Result<Unit> {
        val response = CompletableDeferred<Result<Unit>>()
        actor.send(Withdraw(amount, response))
        return response.await()
    }

    suspend fun getBalance(): Double {
        val response = CompletableDeferred<Double>()
        actor.send(GetBalance(response))
        return response.await()
    }

    suspend fun transfer(toAccount: BankAccount, amount: Double): Result<Unit> {
        val response = CompletableDeferred<Result<Unit>>()
        actor.send(Transfer(toAccount.actor, amount, response))
        return response.await()
    }

    fun close() = actor.close()
}
```

### Cache Actor

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class CacheMsg<K, V>
class Put<K, V>(val key: K, val value: V) : CacheMsg<K, V>()
class Get<K, V>(val key: K, val response: CompletableDeferred<V?>) : CacheMsg<K, V>()
class Remove<K, V>(val key: K) : CacheMsg<K, V>()
class Clear<K, V> : CacheMsg<K, V>()
class Size<K, V>(val response: CompletableDeferred<Int>) : CacheMsg<K, V>()

class CacheActor<K, V>(
    scope: CoroutineScope,
    private val maxSize: Int = 100
) {
    private val actor = scope.actor<CacheMsg<K, V>> {
        val cache = LinkedHashMap<K, V>(maxSize, 0.75f, true)

        for (msg in channel) {
            when (msg) {
                is Put -> {
                    if (cache.size >= maxSize && !cache.containsKey(msg.key)) {
                        val oldestKey = cache.keys.first()
                        cache.remove(oldestKey)
                    }
                    cache[msg.key] = msg.value
                }

                is Get -> {
                    msg.response.complete(cache[msg.key])
                }

                is Remove -> {
                    cache.remove(msg.key)
                }

                is Clear -> {
                    cache.clear()
                }

                is Size -> {
                    msg.response.complete(cache.size)
                }
            }
        }
    }

    suspend fun put(key: K, value: V) = actor.send(Put(key, value))

    suspend fun get(key: K): V? {
        val response = CompletableDeferred<V?>()
        actor.send(Get(key, response))
        return response.await()
    }

    suspend fun remove(key: K) = actor.send(Remove(key))
    suspend fun clear() = actor.send(Clear())

    suspend fun size(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(Size(response))
        return response.await()
    }

    fun close() = actor.close()
}
```

### Rate Limiter Actor

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class RateLimiterMsg
class TryAcquire(val response: CompletableDeferred<Boolean>) : RateLimiterMsg()
class GetAvailable(val response: CompletableDeferred<Int>) : RateLimiterMsg()

class RateLimiterActor(
    scope: CoroutineScope,
    private val maxRequests: Int,
    private val windowMillis: Long
) {
    private val actor = scope.actor<RateLimiterMsg> {
        val requests = mutableListOf<Long>()

        for (msg in channel) {
            val now = System.currentTimeMillis()
            requests.removeIf { it < now - windowMillis }

            when (msg) {
                is TryAcquire -> {
                    if (requests.size < maxRequests) {
                        requests.add(now)
                        msg.response.complete(true)
                    } else {
                        msg.response.complete(false)
                    }
                }

                is GetAvailable -> {
                    msg.response.complete(maxRequests - requests.size)
                }
            }
        }
    }

    suspend fun tryAcquire(): Boolean {
        val response = CompletableDeferred<Boolean>()
        actor.send(TryAcquire(response))
        return response.await()
    }

    suspend fun getAvailable(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(GetAvailable(response))
        return response.await()
    }

    fun close() = actor.close()
}
```

### Task Queue Actor

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class TaskQueueMsg
class EnqueueTask(val task: suspend () -> Unit) : TaskQueueMsg()
class GetQueueSize(val response: CompletableDeferred<Int>) : TaskQueueMsg()
object PauseQueue : TaskQueueMsg()
object ResumeQueue : TaskQueueMsg()

class TaskQueueActor(
    scope: CoroutineScope,
    private val concurrency: Int = 1
) {
    private val actor = scope.actor<TaskQueueMsg>(capacity = Channel.UNLIMITED) {
        val queue = mutableListOf<suspend () -> Unit>()
        var isPaused = false
        val activeJobs = mutableListOf<Job>()

        suspend fun processQueue() {
            while (!isPaused && queue.isNotEmpty() && activeJobs.size < concurrency) {
                val task = queue.removeAt(0)
                val job = launch {
                    try {
                        task()
                    } finally {
                        activeJobs.remove(this)
                        processQueue()
                    }
                }
                activeJobs.add(job)
            }
        }

        for (msg in channel) {
            when (msg) {
                is EnqueueTask -> {
                    queue.add(msg.task)
                    processQueue()
                }

                is GetQueueSize -> {
                    msg.response.complete(queue.size)
                }

                is PauseQueue -> {
                    isPaused = true
                }

                is ResumeQueue -> {
                    isPaused = false
                    processQueue()
                }
            }
        }
    }

    suspend fun enqueue(task: suspend () -> Unit) = actor.send(EnqueueTask(task))

    suspend fun getQueueSize(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(GetQueueSize(response))
        return response.await()
    }

    suspend fun pause() = actor.send(PauseQueue)
    suspend fun resume() = actor.send(ResumeQueue)

    fun close() = actor.close()
}
```

### Error Handling in Actors

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class SafeAccountMsg
class SafeDeposit(
    val amount: Double,
    val response: CompletableDeferred<Result<Unit>>
) : SafeAccountMsg()

sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}

class SafeBankAccount(scope: CoroutineScope) {
    private val actor = scope.actor<SafeAccountMsg> {
        var balance = 0.0

        try {
            for (msg in channel) {
                try {
                    when (msg) {
                        is SafeDeposit -> {
                            if (msg.amount < 0) {
                                throw IllegalArgumentException("Negative amount")
                            }
                            balance += msg.amount
                            msg.response.complete(Result.Success(Unit))
                        }
                    }
                } catch (e: Exception) {
                    when (msg) {
                        is SafeDeposit -> msg.response.complete(
                            Result.Error(e.message ?: "Unknown error")
                        )
                    }
                }
            }
        } catch (e: Exception) {
            println("Actor failed: ${e.message}")
        }
    }

    suspend fun deposit(amount: Double): Result<Unit> {
        val response = CompletableDeferred<Result<Unit>>()
        actor.send(SafeDeposit(amount, response))
        return response.await()
    }

    fun close() = actor.close()
}
```

### Actor Vs Mutex Comparison

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.system.measureTimeMillis

// Using Mutex (traditional approach)
class MutexCounter {
    private var counter = 0
    private val mutex = Mutex()

    suspend fun increment() {
        mutex.withLock {
            counter++
        }
    }

    suspend fun get(): Int {
        return mutex.withLock {
            counter
        }
    }
}

// Using Actor (message passing)
sealed class CounterMsg
object IncCounter : CounterMsg()
class GetCounter(val response: CompletableDeferred<Int>) : CounterMsg()

class ActorCounter(scope: CoroutineScope) {
    private val actor = scope.actor<CounterMsg> {
        var counter = 0
        for (msg in channel) {
            when (msg) {
                is IncCounter -> counter++
                is GetCounter -> msg.response.complete(counter)
            }
        }
    }

    suspend fun increment() = actor.send(IncCounter)

    suspend fun get(): Int {
        val response = CompletableDeferred<Int>()
        actor.send(GetCounter(response))
        return response.await()
    }
}

// Performance comparison
suspend fun main() = coroutineScope {
    // Mutex approach
    val mutexCounter = MutexCounter()
    val mutexTime = measureTimeMillis {
        repeat(10_000) {
            launch { mutexCounter.increment() }
        }
    }
    println("Mutex: $mutexTime ms")

    // Actor approach
    val actorCounter = ActorCounter(this)
    val actorTime = measureTimeMillis {
        repeat(10_000) {
            launch { actorCounter.increment() }
        }
    }
    println("Actor: $actorTime ms")
}
```

### Best Practices

#### DO:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Keep actor state private
class GoodActor(scope: CoroutineScope) {
    private var state = 0  // Private, encapsulated
    private val actor = scope.actor<Msg> { /* ... */ }
}

// Use sealed classes for messages
sealed class Msg
object Increment : Msg()
class GetValue(val response: CompletableDeferred<Int>) : Msg()

// Handle errors gracefully
private val actor = scope.actor<Msg> {
    try {
        for (msg in channel) {
            when (msg) {
                // Handle message
            }
        }
    } catch (e: Exception) {
        // Log or handle actor failure
    }
}

// Provide clean API
suspend fun increment() = actor.send(Increment)
suspend fun getValue(): Int {
    val response = CompletableDeferred<Int>()
    actor.send(GetValue(response))
    return response.await()
}
```

#### DON'T:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Don't expose mutable state
class BadActor(scope: CoroutineScope) {
    var state = 0  // Bad: public mutable state!
}

// Don't use actors for simple tasks
val mutex = Mutex()
var counter = 0
suspend fun simpleIncrement() = mutex.withLock { counter++ }

// Don't forget to close actors
val actor = actor<Msg> { /* ... */ }
// ... use actor ...
actor.close()  // Always close!

// Don't block inside actor
private val blockingActor = scope.actor<Msg> {
    for (msg in channel) {
        // Thread.sleep would block; prefer suspending calls like delay
        // Thread.sleep(1000) // BAD
        delay(1000)          // GOOD (non-blocking)
    }
}
```

### When to Use Actors

Use actors when:
- Need to manage mutable state with concurrent access.
- State updates are complex and require multiple steps.
- Need to maintain ordering of operations.
- Want to avoid explicit locking.
- Building event-driven systems.

Don't use actors when:
- Simple atomic operations (use `AtomicInteger`).
- Read-heavy operations (use `StateFlow`).
- Need immediate responses (actors have overhead).
- State is immutable (use regular functions).

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия этого подхода от классической многопоточности в Java?
- Когда на практике вы бы выбрали акторы вместо других примитивов синхронизации?
- Каковы типичные ошибки при использовании акторов и как их избежать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Coroutines Actors](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html#actors)
- [Actor Model](https://en.wikipedia.org/wiki/Actor_model)
- [Kotlinx Coroutines Channels](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/)
- [Actor Pattern Guide](https://elizarov.medium.com/shared-mutable-state-and-concurrency-in-kotlin-f0f6b8c5c5d8)

## References

- [Kotlin Coroutines Actors](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html#actors)
- [Actor Model](https://en.wikipedia.org/wiki/Actor_model)
- [Kotlinx Coroutines Channels](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/)
- [Actor Pattern Guide](https://elizarov.medium.com/shared-mutable-state-and-concurrency-in-kotlin-f0f6b8c5c5d8)

## Связанные вопросы (RU)

- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-fan-in-fan-out--kotlin--hard]]
- [[q-channel-buffering-strategies--kotlin--hard]]
- [[q-structured-concurrency--kotlin--hard]]

## Related Questions

- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-fan-in-fan-out--kotlin--hard]]
- [[q-channel-buffering-strategies--kotlin--hard]]
- [[q-structured-concurrency--kotlin--hard]]

## MOC Ссылки (RU)

- [[moc-kotlin]]

## MOC Links

- [[moc-kotlin]]

---
id: lang-037
title: "Synchronized Blocks With Coroutines / Синхронизированные блоки с корутинами"
aliases: [Synchronized Blocks With Coroutines, Синхронизированные блоки с корутинами]
topic: kotlin
subtopics: [c-coroutines, c-kotlin, c-structured-concurrency]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-sealed-vs-enum-classes--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, kotlin, synchronization]
date created: Friday, October 31st 2025, 6:31:51 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---
# Вопрос (RU)
> Почему, как правило, не следует использовать `synchronized`-блоки с корутинами и когда это допустимо?

# Question (EN)
> Why should you generally avoid using synchronized blocks with coroutines, and when might it still be acceptable?

## Ответ (RU)

Основные причины (для корутинного кода и suspend-функций):

1. `synchronized` работает на уровне потоков, а не корутин: это мониторная блокировка потоков, а не кооперативный механизм приостановки.
2. `synchronized` блокирует поток. При большом числе корутин это приводит к простоям и потере преимуществ неблокирующей модели. В отличие от этого, `Mutex` позволяет ожидающим корутинам приостанавливаться, не занимая поток во время ожидания блокировки.
3. `synchronized` плохо сочетается с отменой и приостановкой: внутри `synchronized` нельзя вызывать suspend-функции, а если выполнять долгие блокирующие операции, отмена корутины не сможет их корректно прервать до выхода из критической секции.

При этом для коротких, быстрых, не приостанавливающихся секций (особенно в чисто блокирующем коде) `synchronized` остаётся корректным и может использоваться.

### Проблема С Synchronized

```kotlin
import kotlinx.coroutines.*

// ПЛОХО: использование synchronized с корутинами для защищённого доступа в suspend-контексте
class BadExample {
    private var counter = 0

    fun incrementWithSynchronized() = runBlocking {
        repeat(1000) {
            launch {
                synchronized(this@BadExample) {
                    counter++  // Блокирует поток, пока удерживается монитор
                }
            }
        }
    }
}

// Проблемы:
// 1. Блокирует потоки (ограничивает масштабируемость корутин)
// 2. Может приводить к истощению пула потоков при высокой нагрузке
// 3. Поощряет смешивание блокирующего стиля с корутинами вместо использования Mutex/конфайнмента
```

### Проблема 1: Блокировка Потоков

```kotlin
import kotlinx.coroutines.*

// synchronized блокирует целый поток
fun synchronizedBlocking() = runBlocking {
    val lock = Any()

    launch(Dispatchers.Default) {
        synchronized(lock) {
            println("Thread: ${'$'}{Thread.currentThread().name}")
            Thread.sleep(1000)  // Блокирует поток (здесь нельзя использовать delay)
            println("Done")
        }
    }

    launch(Dispatchers.Default) {
        synchronized(lock) {
            println("Waiting...")  // Если lock занят, поток этой корутины блокируется
        }
    }
}

// При тысячах корутин с synchronized можно быстро исчерпать доступные потоки.
```

### Проблема 2: Отмена И Приостановка

```kotlin
import kotlinx.coroutines.*

// synchronized + блокирующий код не кооперативны с отменой
fun cancellationProblem() = runBlocking {
    val job = launch {
        synchronized(this@runBlocking) {
            repeat(10) { i ->
                println("Iteration ${'$'}i")
                Thread.sleep(500)  // Блокирующий вызов: не проверяет отмену корутины
            }
        }
    }

    delay(1200)
    job.cancel()  // Запрос отмены
    println("Cancelled requested")
    // Но блокирующая работа внутри synchronized продолжится до завершения.
}
```

### Решение 1: Использовать Mutex (дружественный К Корутинам замок)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// ХОРОШО: использование Mutex
class GoodExample {
    private var counter = 0
    private val mutex = Mutex()

    suspend fun incrementWithMutex() = coroutineScope {
        repeat(1000) {
            launch {
                mutex.withLock {
                    counter++  // Если mutex занят, корутина приостанавливается, а не блокирует поток
                }
            }
        }
    }
}

// Преимущества:
// 1. Ожидающие корутины приостанавливаются вместо блокировки потоков
// 2. Потоки могут выполнять другие корутины, пока одни ждут Mutex
// 3. Работает с suspend-функциями и кооперативной отменой внутри критической секции
```

### Сравнение Mutex И Synchronized

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.system.measureTimeMillis

class Counter {
    private var count = 0
    private val mutex = Mutex()

    // synchronized: блокирует поток, пока удерживается монитор
    fun incrementSynchronized() {
        synchronized(this) {
            count++
        }
    }

    // Mutex: ожидающие корутины приостанавливаются; владелец всё ещё выполняется на потоке
    suspend fun incrementMutex() {
        mutex.withLock {
            count++
        }
    }
}

// Грубое сравнение поведения/производительности (только для иллюстрации)
fun comparePerformance() = runBlocking {
    val counter = Counter()

    // С synchronized
    val time1 = measureTimeMillis {
        repeat(10_000) {
            launch(Dispatchers.Default) {
                counter.incrementSynchronized()
            }
        }
    }
    println("synchronized: ${'$'}time1 ms")

    // С Mutex
    val time2 = measureTimeMillis {
        repeat(10_000) {
            launch(Dispatchers.Default) {
                counter.incrementMutex()
            }
        }
    }
    println("Mutex: ${'$'}time2 ms")
}
```

### Отмена С Mutex

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Критические секции на Mutex могут использовать suspend-функции и поддерживают кооперативную отмену
fun mutexCancellation() = runBlocking {
    val mutex = Mutex()

    val job = launch {
        mutex.withLock {
            repeat(10) { i ->
                println("Iteration ${'$'}i")
                delay(500)  // Проверяет отмену; при cancel корутина выйдет кооперативно
            }
        }
    }

    delay(1200)
    job.cancel()  // Корректно отменяется на следующей точке приостановки
    println("Cancelled requested")
}
```

### Решение 2: Атомарные Операции

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.atomic.AtomicInteger

// Для простых счётчиков используйте атомарные типы
class AtomicCounter {
    private val counter = AtomicInteger(0)

    fun increment() {
        counter.incrementAndGet()  // Потокобезопасно без явных блокировок
    }

    fun get(): Int = counter.get()
}

// Использование в корутинах
fun useAtomic() = runBlocking {
    val counter = AtomicCounter()

    repeat(10_000) {
        launch(Dispatchers.Default) {
            counter.increment()
        }
    }
}
```

### Решение 3: Конфайнмент На Один Поток

```kotlin
import kotlinx.coroutines.*

// Запуск всего доступа на одном потоке — синхронизация не нужна
// В реальном коде newSingleThreadContext нужно корректно закрывать, здесь — учебный пример.
val singleThreadContext = newSingleThreadContext("CounterThread")

class ConfinedCounter {
    private var counter = 0

    suspend fun increment() = withContext(singleThreadContext) {
        counter++  // Всегда на одном потоке, блокировки не требуются
    }

    suspend fun get(): Int = withContext(singleThreadContext) {
        counter
    }
}
```

### Реальный Пример: Разделяемый Ресурс

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// ПЛОХО: использование synchronized + runBlocking внутри API, блокирует вызывающего и смешивает стили.
// Для такой простой операции здесь вообще не нужны корутины.
class BadResourceManager {
    private val resources = mutableListOf<Resource>()

    fun addResource(resource: Resource) {
        synchronized(resources) {
            resources.add(resource)
        }
    }
}

// ХОРОШО: использование Mutex в suspend-функциях для корутинного API
class GoodResourceManager {
    private val resources = mutableListOf<Resource>()
    private val mutex = Mutex()

    suspend fun addResource(resource: Resource) {
        mutex.withLock {
            resources.add(resource)
        }
    }

    suspend fun getResources(): List<Resource> {
        return mutex.withLock {
            resources.toList()
        }
    }
}
```

### Сложная Синхронизация

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Несколько Mutex для более тонкой синхронизации (упрощённый пример, без детального анализа дедлоков)
class BankAccount {
    private var balance = 0.0
    private val balanceMutex = Mutex()

    private val transactions = mutableListOf<Transaction>()
    private val transactionsMutex = Mutex()

    suspend fun deposit(amount: Double) {
        balanceMutex.withLock {
            balance += amount
        }

        transactionsMutex.withLock {
            transactions.add(Transaction.Deposit(amount))
        }
    }

    suspend fun withdraw(amount: Double): Boolean {
        return balanceMutex.withLock {
            if (balance >= amount) {
                balance -= amount
                transactionsMutex.withLock {
                    transactions.add(Transaction.Withdrawal(amount))
                }
                true
            } else {
                false
            }
        }
    }
}
```

### Когда Synchronized Может Быть Допустим

```kotlin
// ВНИМАНИЕ: допустимо для быстрых, некорутинных, неблокирующих операций
class CacheManager {
    private val cache = mutableMapOf<String, String>()

    // ОК: быстрые, не приостанавливающиеся операции
    fun getCached(key: String): String? {
        synchronized(cache) {
            return cache[key]
        }
    }

    // ОК: быстрые, не приостанавливающиеся операции
    fun putCached(key: String, value: String) {
        synchronized(cache) {
            cache[key] = value
        }
    }

    // НЕ ОК: долгие или suspend-операции внутри synchronized
    suspend fun fetchAndCache(key: String): String {
        synchronized(cache) {  // ПЛОХО: нельзя вызывать suspend-функции или долго блокировать здесь
            // delay(1000)  // Не скомпилируется внутри synchronized
            val value = fetchFromNetwork(key) // Если блокирующий вызов — удерживает монитор; если suspend — не скомпилируется
            cache[key] = value
            return value
        }
    }
}
```

### Рекомендации По Использованию

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.atomic.AtomicInteger

class SynchronizationBestPractices {
    // ДЕЛАЙТЕ: используйте Mutex для синхронизации корутин
    private val mutex = Mutex()
    private var sharedState = 0

    suspend fun good1() {
        mutex.withLock {
            sharedState++
        }
    }

    // ДЕЛАЙТЕ: используйте атомарные типы для простых счётчиков
    private val atomicCounter = AtomicInteger(0)

    fun good2() {
        atomicCounter.incrementAndGet()
    }

    // ДЕЛАЙТЕ: используйте однопоточный диспетчер (в реальном коде правильно управляйте ресурсами)
    private val singleThread = newSingleThreadContext("MyThread")

    suspend fun good3() {
        withContext(singleThread) {
            // Весь доступ на одном потоке
            sharedState++
        }
    }

    // НЕ ДЕЛАЙТЕ: не используйте synchronized для обновления общего состояния из корутин, если ожидается масштабируемость
    fun bad1() = runBlocking {
        launch {
            synchronized(this@SynchronizationBestPractices) {  // ПЛОХО: блокирует поток
                sharedState++
            }
        }
    }

    // НЕ ДЕЛАЙТЕ: не вызывайте suspend-функции внутри synchronized
    suspend fun bad2() {
        synchronized(this) {  // ПЛОХО: нельзя вызывать suspend-функции или delay
            // delay(1000)  // Не скомпилируется
            sharedState++
        }
    }
}
```

### Влияние На Производительность

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Демонстрация влияния блокировки потоков (иллюстративно)
fun demonstrateThreadBlocking() = runBlocking {
    val availableThreads = Runtime.getRuntime().availableProcessors()
    println("Available threads: ${'$'}availableThreads")

    val lock = Any()

    // Многие корутины с synchronized
    repeat(1000) {
        launch(Dispatchers.Default) {
            synchronized(lock) {
                Thread.sleep(100)  // Блокирует поток
            }
        }
    }
    // При ограниченном числе потоков многие корутины будут заблокированы.

    val mutex = Mutex()

    // Многие корутины с Mutex
    repeat(1000) {
        launch(Dispatchers.Default) {
            mutex.withLock {
                delay(100)  // Приостанавливается, не блокируя поток во время ожидания
            }
        }
    }
    // Потоки могут эффективнее переключаться между корутинами.
}
```

### Сводная Таблица

| Характеристика | synchronized | Mutex |
|----------------|-------------|-------|
| Блокировка | Блокирует поток | Ожидающие корутины приостанавливаются |
| Отмена | Блокирующий код не кооперативен | Кооперативна при наличии точек приостановки |
| Производительность | Ухудшается при большом числе блокирующих корутин | Лучше масштабируется с большим числом корутин |
| Использование потоков | Удерживает поток на время блокировки | Освобождает поток во время ожидания |
| suspend-функции | Нельзя вызывать внутри | Полностью поддерживаются внутри |
| Основной кейс | Малые, быстрые, неблокирующие секции без suspend | Общий стейт и suspend-работа в корутинах |

## Answer (EN)

For coroutine-based and suspending code, there are three main reasons to avoid `synchronized` as the primary synchronization tool:

1. `synchronized` works at the thread/monitor level, not the coroutine level: it is a blocking monitor lock for threads, not a cooperative suspension mechanism.
2. `synchronized` blocks the underlying thread. With many coroutines this leads to thread starvation and defeats the scalability benefits of coroutines. In contrast, `Mutex` lets waiting coroutines suspend without occupying a thread while waiting for the lock.
3. `synchronized` does not work well with suspension/cancellation: you cannot call suspend functions inside `synchronized`, and if you perform long blocking work there, coroutine cancellation cannot safely interrupt it until the block exits.

However, for short, fast, non-suspending critical sections (especially in purely blocking code), `synchronized` remains correct and can be used.

### The Problem with `synchronized`

```kotlin
import kotlinx.coroutines.*

// BAD: Using synchronized with coroutines for protected access in a suspending-style context
class BadExample {
    private var counter = 0

    fun incrementWithSynchronized() = runBlocking {
        repeat(1000) {
            launch {
                synchronized(this@BadExample) {
                    counter++  // Locks monitor, blocks the thread while held
                }
            }
        }
    }
}

// Problems:
// 1. Blocks threads (limits coroutine scalability)
// 2. Can contribute to thread starvation under heavy load
// 3. Encourages mixing blocking style with coroutines instead of Mutex/confinement
```

### Issue 1: Thread Blocking

```kotlin
import kotlinx.coroutines.*

// synchronized blocks the entire thread
fun synchronizedBlocking() = runBlocking {
    val lock = Any()

    launch(Dispatchers.Default) {
        synchronized(lock) {
            println("Thread: ${'$'}{Thread.currentThread().name}")
            Thread.sleep(1000)  // Blocks thread while held (cannot use delay here)
            println("Done")
        }
    }

    launch(Dispatchers.Default) {
        synchronized(lock) {
            println("Waiting...")  // If lock is held, this coroutine's thread is blocked
        }
    }
}

// With thousands of coroutines using synchronized, you can exhaust the available threads.
```

### Issue 2: Cancellation and Suspension

```kotlin
import kotlinx.coroutines.*

// synchronized + blocking code is not cancellation-cooperative
fun cancellationProblem() = runBlocking {
    val job = launch {
        synchronized(this@runBlocking) {
            repeat(10) { i ->
                println("Iteration ${'$'}i")
                Thread.sleep(500)  // Blocking: does not check coroutine cancellation
            }
        }
    }

    delay(1200)
    job.cancel()  // Requests cancellation
    println("Cancelled requested")
    // But the blocking work inside synchronized continues until it finishes.
}
```

### Solution 1: Use Mutex (Coroutine-Friendly Lock)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// GOOD: Using Mutex
class GoodExample {
    private var counter = 0
    private val mutex = Mutex()

    suspend fun incrementWithMutex() = coroutineScope {
        repeat(1000) {
            launch {
                mutex.withLock {
                    counter++  // If lock is busy, this coroutine suspends instead of blocking a thread
                }
            }
        }
    }
}

// Benefits:
// 1. Waiting coroutines suspend instead of blocking threads
// 2. Threads can execute other coroutines while some are waiting for the Mutex
// 3. Works with suspend functions and cooperative cancellation inside the critical section
```

### Mutex Vs `synchronized` Comparison

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.system.measureTimeMillis

class Counter {
    private var count = 0
    private val mutex = Mutex()

    // synchronized: Blocks the thread while holding the monitor
    fun incrementSynchronized() {
        synchronized(this) {
            count++
        }
    }

    // Mutex: Waiting coroutines suspend; holder still runs on a thread
    suspend fun incrementMutex() {
        mutex.withLock {
            count++
        }
    }
}

// Rough performance / behavior comparison (illustrative only)
fun comparePerformance() = runBlocking {
    val counter = Counter()

    // With synchronized
    val time1 = measureTimeMillis {
        repeat(10_000) {
            launch(Dispatchers.Default) {
                counter.incrementSynchronized()
            }
        }
    }
    println("synchronized: ${'$'}time1 ms")

    // With Mutex
    val time2 = measureTimeMillis {
        repeat(10_000) {
            launch(Dispatchers.Default) {
                counter.incrementMutex()
            }
        }
    }
    println("Mutex: ${'$'}time2 ms")
}
```

### Cancellation with Mutex

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Mutex-based critical sections can use suspend functions and are cancellation-cooperative
fun mutexCancellation() = runBlocking {
    val mutex = Mutex()

    val job = launch {
        mutex.withLock {
            repeat(10) { i ->
                println("Iteration ${'$'}i")
                delay(500)  // Checks for cancellation; if job is cancelled, it will exit cooperatively
            }
        }
    }

    delay(1200)
    job.cancel()  // Cancels properly at next suspension point
    println("Cancelled requested")
}
```

### Solution 2: Atomic Operations

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.atomic.AtomicInteger

// For simple counters, use atomic types
class AtomicCounter {
    private val counter = AtomicInteger(0)

    fun increment() {
        counter.incrementAndGet()  // Thread-safe without explicit locks
    }

    fun get(): Int = counter.get()
}

// Use in coroutines
fun useAtomic() = runBlocking {
    val counter = AtomicCounter()

    repeat(10_000) {
        launch(Dispatchers.Default) {
            counter.increment()
        }
    }
}
```

### Solution 3: Single Thread Confinement

```kotlin
import kotlinx.coroutines.*

// Run all access on a single thread - no synchronization needed
// NOTE: newSingleThreadContext should be closed properly in real applications; this is a simplified example.
val singleThreadContext = newSingleThreadContext("CounterThread")

class ConfinedCounter {
    private var counter = 0

    suspend fun increment() = withContext(singleThreadContext) {
        counter++  // Always on same thread, no locking needed
    }

    suspend fun get(): Int = withContext(singleThreadContext) {
        counter
    }
}
```

### Real-World Example: Shared Resource

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// BAD: Using synchronized + runBlocking inside API, blocks the caller and mixes styles.
// For this simple operation coroutines are not needed at all.
class BadResourceManager {
    private val resources = mutableListOf<Resource>()

    fun addResource(resource: Resource) {
        synchronized(resources) {
            resources.add(resource)
        }
    }
}

// GOOD: Using Mutex in suspend functions for a coroutine-friendly API
class GoodResourceManager {
    private val resources = mutableListOf<Resource>()
    private val mutex = Mutex()

    suspend fun addResource(resource: Resource) {
        mutex.withLock {
            resources.add(resource)
        }
    }

    suspend fun getResources(): List<Resource> {
        return mutex.withLock {
            resources.toList()
        }
    }
}
```

### Complex Synchronization

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Multiple mutexes for fine-grained locking (simplified, without full deadlock analysis)
class BankAccount {
    private var balance = 0.0
    private val balanceMutex = Mutex()

    private val transactions = mutableListOf<Transaction>()
    private val transactionsMutex = Mutex()

    suspend fun deposit(amount: Double) {
        balanceMutex.withLock {
            balance += amount
        }

        transactionsMutex.withLock {
            transactions.add(Transaction.Deposit(amount))
        }
    }

    suspend fun withdraw(amount: Double): Boolean {
        return balanceMutex.withLock {
            if (balance >= amount) {
                balance -= amount
                transactionsMutex.withLock {
                    transactions.add(Transaction.Withdrawal(amount))
                }
                true
            } else {
                false
            }
        }
    }
}
```

### When `synchronized` Might Be Acceptable

```kotlin
// WARNING: Potentially OK if protecting quick, non-suspending, non-blocking code
class CacheManager {
    private val cache = mutableMapOf<String, String>()

    // OK: Quick, non-suspending operation
    fun getCached(key: String): String? {
        synchronized(cache) {
            return cache[key]
        }
    }

    // OK: Quick, non-suspending operation
    fun putCached(key: String, value: String) {
        synchronized(cache) {
            cache[key] = value
        }
    }

    // NOT OK: Long-running or suspending operation inside synchronized
    suspend fun fetchAndCache(key: String): String {
        synchronized(cache) {  // BAD: cannot call suspend functions or do long blocking work here
            // delay(1000)  // This would not compile inside synchronized
            val value = fetchFromNetwork(key) // If blocking, holds the monitor; if suspend, won't compile
            cache[key] = value
            return value
        }
    }
}
```

### Best Practices

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.atomic.AtomicInteger

class SynchronizationBestPractices {
    // DO: Use Mutex for coroutine synchronization
    private val mutex = Mutex()
    private var sharedState = 0

    suspend fun good1() {
        mutex.withLock {
            sharedState++
        }
    }

    // DO: Use atomic types for simple counters
    private val atomicCounter = AtomicInteger(0)

    fun good2() {
        atomicCounter.incrementAndGet()
    }

    // DO: Use single-threaded dispatcher (ensure proper resource management in real code)
    private val singleThread = newSingleThreadContext("MyThread")

    suspend fun good3() {
        withContext(singleThread) {
            // All access on same thread
            sharedState++
        }
    }

    // DON'T: Use synchronized for coroutine-based shared state updates when you rely on coroutine scalability
    fun bad1() = runBlocking {
        launch {
            synchronized(this@SynchronizationBestPractices) {  // BAD: blocks thread
                sharedState++
            }
        }
    }

    // DON'T: Call suspend functions from inside synchronized
    suspend fun bad2() {
        synchronized(this) {  // BAD: cannot call suspend functions or delay here
            // delay(1000)  // This would not compile
            sharedState++
        }
    }
}
```

### Performance Impact

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Demonstration of thread blocking impact (illustrative)
fun demonstrateThreadBlocking() = runBlocking {
    val availableThreads = Runtime.getRuntime().availableProcessors()
    println("Available threads: ${'$'}availableThreads")

    val lock = Any()

    // Launch many coroutines with synchronized
    repeat(1000) {
        launch(Dispatchers.Default) {
            synchronized(lock) {
                Thread.sleep(100)  // Blocks thread
            }
        }
    }
    // With a limited number of threads, many coroutines will be blocked waiting.

    val mutex = Mutex()

    // Launch many coroutines with Mutex
    repeat(1000) {
        launch(Dispatchers.Default) {
            mutex.withLock {
                delay(100)  // Suspends, doesn't block the thread while waiting
            }
        }
    }
    // Threads can switch between coroutines more efficiently.
}
```

### Summary Table

| Feature | synchronized | Mutex |
|---------|--------------|-------|
| Blocking | Blocks thread | Waiting coroutines suspend |
| Cancellation | Blocking code not cooperative | Cooperative with suspend points |
| Performance | Degrades with many blocking coroutines | Scales better with many coroutines |
| Thread usage | Holds thread while lock is held | Frees thread while waiting for lock |
| Suspend functions | Not allowed inside | Fully supported inside |
| Use case | Small, quick, non-suspending sections | Coroutine-based shared state and suspending work |

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия поведения `synchronized` и `Mutex` в контексте корутин?
- Когда использование `synchronized` все еще может быть оправдано в Kotlin-коде?
- Каковы типичные ошибки при смешивании блокирующего кода и корутин?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Связанные Вопросы (RU)

- [[q-sealed-vs-enum-classes--kotlin--medium]]

## Related Questions

- [[q-sealed-vs-enum-classes--kotlin--medium]]

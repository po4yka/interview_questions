---
tags:
  - programming-languages
difficulty: medium
---

# Why Not Use Synchronized Blocks with Coroutines?

## Answer

There are three main reasons:

1. **Different synchronization levels**: `synchronized` blocks work at thread level, not coroutine level - these are different mechanisms
2. **Thread blocking**: Blocking threads defeats the purpose of coroutines. Mutex works in async style without blocking threads
3. **Cancellation ignorance**: `synchronized` blocks don't account for coroutine cancellation - if coroutine is cancelled, the lock isn't released properly

### The Problem with synchronized

```kotlin
import kotlinx.coroutines.*

// ❌ BAD: Using synchronized with coroutines
class BadExample {
    private var counter = 0

    fun incrementWithSynchronized() = runBlocking {
        repeat(1000) {
            launch {
                synchronized(this@BadExample) {
                    counter++  // Blocks thread!
                }
            }
        }
    }
}

// Problems:
// 1. Blocks threads (defeats coroutine purpose)
// 2. Can cause thread starvation
// 3. Doesn't cooperate with cancellation
```

### Issue 1: Thread Blocking

```kotlin
// synchronized blocks the entire thread
fun synchronizedBlocking() = runBlocking {
    val lock = Any()

    launch(Dispatchers.Default) {
        synchronized(lock) {
            println("Thread: ${Thread.currentThread().name}")
            delay(1000)  // ❌ Blocks thread while waiting
            println("Done")
        }
    }

    launch(Dispatchers.Default) {
        synchronized(lock) {
            println("Waiting...")  // Blocked thread can't do other work
        }
    }
}

// With thousands of coroutines, you'll run out of threads!
```

### Issue 2: Cancellation Not Respected

```kotlin
// synchronized doesn't check cancellation
fun cancellationProblem() = runBlocking {
    val job = launch {
        synchronized(this@runBlocking) {
            repeat(10) { i ->
                println("Iteration $i")
                Thread.sleep(500)  // Blocking
                // No cancellation check!
            }
        }
    }

    delay(1200)
    job.cancel()  // Tries to cancel
    println("Cancelled")  // But synchronized keeps running!
}
```

### Solution 1: Use Mutex (Coroutine-Friendly Lock)

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// ✅ GOOD: Using Mutex
class GoodExample {
    private var counter = 0
    private val mutex = Mutex()

    suspend fun incrementWithMutex() = coroutineScope {
        repeat(1000) {
            launch {
                mutex.withLock {
                    counter++  // Suspends instead of blocking
                }
            }
        }
    }
}

// Benefits:
// 1. Suspends coroutine instead of blocking thread
// 2. Thread can execute other coroutines while waiting
// 3. Respects cancellation
```

### Mutex vs synchronized Comparison

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class Counter {
    private var count = 0
    private val mutex = Mutex()

    // ❌ synchronized: Blocks thread
    fun incrementSynchronized() {
        synchronized(this) {
            count++
        }
        // Thread is blocked while holding lock
    }

    // ✅ Mutex: Suspends coroutine
    suspend fun incrementMutex() {
        mutex.withLock {
            count++
        }
        // Thread is free while coroutine waits
    }
}

// Performance comparison
fun comparePerformance() = runBlocking {
    val counter = Counter()

    // With synchronized
    val time1 = measureTimeMillis {
        repeat(10_000) {
            launch {
                counter.incrementSynchronized()
            }
        }
    }
    println("synchronized: ${time1}ms")

    // With Mutex
    val time2 = measureTimeMillis {
        repeat(10_000) {
            launch {
                counter.incrementMutex()
            }
        }
    }
    println("Mutex: ${time2}ms")  // Usually faster
}
```

### Cancellation with Mutex

```kotlin
// Mutex respects cancellation
fun mutexCancellation() = runBlocking {
    val mutex = Mutex()

    val job = launch {
        mutex.withLock {
            repeat(10) { i ->
                println("Iteration $i")
                delay(500)  // Respects cancellation
            }
        }
    }

    delay(1200)
    job.cancel()  // ✅ Cancels properly
    println("Cancelled")
}
```

### Solution 2: Atomic Operations

```kotlin
import java.util.concurrent.atomic.AtomicInteger

// For simple counters, use atomic types
class AtomicCounter {
    private val counter = AtomicInteger(0)

    fun increment() {
        counter.incrementAndGet()  // Thread-safe without locks
    }

    fun get(): Int = counter.get()
}

// Use in coroutines
fun useAtomic() = runBlocking {
    val counter = AtomicCounter()

    repeat(10_000) {
        launch {
            counter.increment()  // No locking needed
        }
    }
}
```

### Solution 3: Single Thread Confinement

```kotlin
// Run all access on single thread - no synchronization needed
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
// ❌ BAD: Using synchronized
class BadResourceManager {
    private val resources = mutableListOf<Resource>()

    fun addResource(resource: Resource) = runBlocking {
        launch {
            synchronized(resources) {  // Blocks thread
                resources.add(resource)
            }
        }
    }
}

// ✅ GOOD: Using Mutex
class GoodResourceManager {
    private val resources = mutableListOf<Resource>()
    private val mutex = Mutex()

    suspend fun addResource(resource: Resource) {
        mutex.withLock {  // Suspends coroutine
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
// Multiple mutexes for fine-grained locking
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

### When synchronized Might Be Acceptable

```kotlin
// ⚠️ OK if: Protecting non-suspending code
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

    // ❌ NOT OK: Long-running or suspending operation
    suspend fun fetchAndCache(key: String): String {
        synchronized(cache) {  // BAD
            delay(1000)  // Can't use suspend functions in synchronized
            val value = fetchFromNetwork(key)
            cache[key] = value
            return value
        }
    }
}
```

### Best Practices

```kotlin
class SynchronizationBestPractices {
    // ✅ DO: Use Mutex for coroutine synchronization
    private val mutex = Mutex()
    private var sharedState = 0

    suspend fun good1() {
        mutex.withLock {
            sharedState++
        }
    }

    // ✅ DO: Use atomic types for simple counters
    private val atomicCounter = AtomicInteger(0)

    fun good2() {
        atomicCounter.incrementAndGet()
    }

    // ✅ DO: Use single-threaded dispatcher for confinement
    private val singleThread = newSingleThreadContext("MyThread")

    suspend fun good3() {
        withContext(singleThread) {
            // All access on same thread
            sharedState++
        }
    }

    // ❌ DON'T: Use synchronized in coroutines
    fun bad1() = runBlocking {
        launch {
            synchronized(this@SynchronizationBestPractices) {  // BAD
                sharedState++
            }
        }
    }

    // ❌ DON'T: Block threads in coroutines
    suspend fun bad2() {
        synchronized(this) {  // BAD
            delay(1000)  // Won't compile - can't call suspend in synchronized
        }
    }
}
```

### Performance Impact

```kotlin
// Demonstration of thread blocking impact
fun demonstrateThreadBlocking() = runBlocking {
    val availableThreads = Runtime.getRuntime().availableProcessors()
    println("Available threads: $availableThreads")

    val lock = Any()

    // Launch many coroutines with synchronized
    repeat(1000) {
        launch(Dispatchers.Default) {
            synchronized(lock) {
                Thread.sleep(100)  // Blocks thread
            }
        }
    }
    // With only a few threads, most coroutines wait for thread availability
    // = Poor performance

    val mutex = Mutex()

    // Launch many coroutines with Mutex
    repeat(1000) {
        launch(Dispatchers.Default) {
            mutex.withLock {
                delay(100)  // Suspends, doesn't block thread
            }
        }
    }
    // Threads can switch between coroutines
    // = Better performance
}
```

### Summary Table

| Feature | synchronized | Mutex |
|---------|--------------|-------|
| **Blocking** | Blocks thread | Suspends coroutine |
| **Cancellation** | Doesn't respect | Respects cancellation |
| **Performance** | Poor with many coroutines | Good |
| **Thread usage** | Holds thread | Releases thread |
| **Suspend functions** | Can't call | Can call |
| **Use case** | Quick non-suspend ops | Coroutine synchronization |

---
## Вопрос (RU)

Почему не рекомендуется использовать с корутинами synchronized блок и аналоги таких типов

## Ответ

1. synchronized блоки в Java/Kotlin работают на уровне потоков, а не корутин – это разные механизмы синхронизации.\", \"2. Блокировка потоков замедляет работу – Mutex работает в асинхронном стиле, не блокируя потоки.\", \"3. Глобальные synchronized блоки не учитывают отмену корутин – если корутина отменена, synchronized не освобощает ресурс

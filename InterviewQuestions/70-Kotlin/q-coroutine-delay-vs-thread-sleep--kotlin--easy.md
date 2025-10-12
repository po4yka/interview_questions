---
id: "20251012-150005"
title: "delay() vs Thread.sleep(): what's the difference?"
description: "Understanding the fundamental differences between suspending delay() and blocking Thread.sleep() in Kotlin coroutines, including thread usage and performance implications"
tags: ["kotlin", "coroutines", "delay", "threads", "suspending", "difficulty/easy"]
topic: "kotlin"
subtopics: ["coroutines", "delay", "threads", "suspending"]
moc: "moc-kotlin"
status: "draft"
date_created: "2025-10-12"
date_updated: "2025-10-12"
---

# delay() vs Thread.sleep(): what's the difference?

## English

### Problem Statement

Both `delay()` and `Thread.sleep()` pause execution for a specified time, but they work fundamentally differently. One suspends a coroutine without blocking the thread, while the other blocks the entire thread. What are the implications for performance, resource usage, and when should each be used?

### Solution

**`delay()`** is a **suspending function** that pauses a coroutine without blocking the underlying thread, allowing other coroutines to run. **`Thread.sleep()`** is a **blocking function** that blocks the entire thread, preventing any other work on that thread.

#### Basic Difference

```kotlin
import kotlinx.coroutines.*

fun basicDifference() = runBlocking {
    println("=== Thread.sleep() ===")
    println("Thread: ${Thread.currentThread().name}")

    // Thread.sleep blocks the thread
    Thread.sleep(1000)
    println("After Thread.sleep (thread was blocked)")

    println("\n=== delay() ===")
    println("Thread: ${Thread.currentThread().name}")

    // delay suspends the coroutine
    delay(1000)
    println("After delay (thread was NOT blocked)")
}
```

#### Thread Blocking vs Suspending

```kotlin
import kotlinx.coroutines.*

fun demonstrateThreadBlocking() = runBlocking {
    println("=== Thread.sleep blocks thread ===")

    val time1 = measureTimeMillis {
        launch {
            println("Coroutine 1 started on ${Thread.currentThread().name}")
            Thread.sleep(1000) // Blocks the thread!
            println("Coroutine 1 finished")
        }

        launch {
            println("Coroutine 2 started on ${Thread.currentThread().name}")
            Thread.sleep(1000) // Must wait for thread
            println("Coroutine 2 finished")
        }
    }
    println("Time with Thread.sleep: $time1 ms") // ~2000ms (sequential)

    println("\n=== delay suspends coroutine ===")

    val time2 = measureTimeMillis {
        launch {
            println("Coroutine 3 started on ${Thread.currentThread().name}")
            delay(1000) // Suspends, doesn't block thread
            println("Coroutine 3 finished")
        }

        launch {
            println("Coroutine 4 started on ${Thread.currentThread().name}")
            delay(1000) // Can run concurrently
            println("Coroutine 4 finished")
        }
    }
    println("Time with delay: $time2 ms") // ~1000ms (parallel)
}
```

#### Visualizing the Difference

```kotlin
import kotlinx.coroutines.*

fun visualizeTheorem() = runBlocking {
    println("=== Visual Demonstration ===")

    // With Thread.sleep: Thread is blocked
    println("\nWith Thread.sleep:")
    launch(Dispatchers.Default) {
        repeat(5) { i ->
            println("[$i] Before sleep on ${Thread.currentThread().name}")
            Thread.sleep(500)
            println("[$i] After sleep")
        }
    }

    delay(3000) // Wait for completion

    // With delay: Thread is free for other work
    println("\n\nWith delay:")
    repeat(5) {
        launch(Dispatchers.Default) {
            println("[$it] Before delay on ${Thread.currentThread().name}")
            delay(500)
            println("[$it] After delay on ${Thread.currentThread().name}")
        }
    }

    delay(1500) // All complete in ~500ms instead of 2500ms
}
```

#### Performance Impact

```kotlin
import kotlinx.coroutines.*

fun performanceComparison() = runBlocking {
    println("=== Performance Comparison ===")

    val coroutineCount = 100

    // Using Thread.sleep: Creates thread congestion
    val time1 = measureTimeMillis {
        val jobs = List(coroutineCount) {
            launch(Dispatchers.Default) {
                Thread.sleep(1000)
            }
        }
        jobs.forEach { it.join() }
    }
    println("$coroutineCount coroutines with Thread.sleep: $time1 ms")

    // Using delay: Efficient resource usage
    val time2 = measureTimeMillis {
        val jobs = List(coroutineCount) {
            launch(Dispatchers.Default) {
                delay(1000)
            }
        }
        jobs.forEach { it.join() }
    }
    println("$coroutineCount coroutines with delay: $time2 ms")

    // Thread.sleep is much slower because it blocks threads
}
```

#### Thread Pool Exhaustion

```kotlin
import kotlinx.coroutines.*

fun threadPoolExhaustion() {
    println("=== Thread Pool Exhaustion ===")

    // Bad: Using Thread.sleep exhausts thread pool
    runBlocking(Dispatchers.Default) {
        println("Available processors: ${Runtime.getRuntime().availableProcessors()}")

        val jobs = List(1000) { index ->
            launch {
                println("[$index] Started on ${Thread.currentThread().name}")
                Thread.sleep(5000) // Blocks thread for 5 seconds
                println("[$index] Finished")
            }
        }

        jobs.forEach { it.join() }
    }

    // Good: Using delay doesn't exhaust thread pool
    runBlocking(Dispatchers.Default) {
        val jobs = List(1000) { index ->
            launch {
                println("[$index] Started on ${Thread.currentThread().name}")
                delay(5000) // Suspends, thread can do other work
                println("[$index] Finished")
            }
        }

        jobs.forEach { it.join() }
    }
}
```

#### Cancellation Support

```kotlin
import kotlinx.coroutines.*

fun cancellationSupport() = runBlocking {
    println("=== Cancellation Support ===")

    // Thread.sleep is not cancellable
    val job1 = launch {
        try {
            println("Starting Thread.sleep")
            Thread.sleep(10000)
            println("Thread.sleep completed (this won't print)")
        } catch (e: Exception) {
            println("Caught: ${e::class.simpleName}")
        }
    }

    delay(1000)
    job1.cancel()
    println("Job1 cancelled: ${job1.isCancelled}")
    job1.join()

    // delay is cancellable
    val job2 = launch {
        try {
            println("Starting delay")
            delay(10000)
            println("delay completed (this won't print)")
        } catch (e: CancellationException) {
            println("delay was cancelled properly")
        }
    }

    delay(1000)
    job2.cancel()
    println("Job2 cancelled: ${job2.isCancelled}")
    job2.join()
}
```

#### Use Cases

```kotlin
import kotlinx.coroutines.*

// Use Case 1: Coroutine operations - use delay
suspend fun periodicTask() {
    while (true) {
        performTask()
        delay(1000) // Suspends, doesn't block
    }
}

// Use Case 2: Testing with delays
suspend fun testWithDelay() {
    val result = loadData()
    delay(100) // Give time for async operations
    verify(result)
}

// Use Case 3: Retry mechanism
suspend fun retryWithDelay(times: Int, delayTime: Long, block: suspend () -> Unit) {
    repeat(times) { attempt ->
        try {
            block()
            return
        } catch (e: Exception) {
            if (attempt < times - 1) {
                delay(delayTime) // Wait before retry
            }
        }
    }
}

// Use Case 4: Throttling
suspend fun throttledOperation(intervalMs: Long) {
    var lastExecutionTime = 0L

    fun canExecute(): Boolean {
        val currentTime = System.currentTimeMillis()
        return currentTime - lastExecutionTime >= intervalMs
    }

    if (!canExecute()) {
        val waitTime = intervalMs - (System.currentTimeMillis() - lastExecutionTime)
        delay(waitTime) // Use delay, not Thread.sleep
    }

    lastExecutionTime = System.currentTimeMillis()
    // Perform operation
}

// AVOID: Thread.sleep in coroutines
suspend fun badExample() {
    Thread.sleep(1000) // DON'T DO THIS in coroutines!
}

// Good: Use delay instead
suspend fun goodExample() {
    delay(1000) // Correct way
}

suspend fun performTask() {
    delay(100)
}

suspend fun loadData(): String {
    delay(100)
    return "data"
}

fun verify(result: String) {
    println("Verified: $result")
}
```

#### When Thread.sleep Might Be Acceptable

```kotlin
import kotlinx.coroutines.*

fun whenThreadSleepIsOk() {
    // 1. Non-coroutine code (rare in modern Kotlin)
    fun blockingFunction() {
        Thread.sleep(1000) // OK if not in coroutine context
    }

    // 2. Blocking test utilities (not recommended)
    fun simpleBlockingTest() {
        Thread.sleep(100)
        // Better to use runBlocking + delay
    }

    // 3. Main thread in simple scripts (before coroutines)
    fun oldStyleMain() {
        println("Start")
        Thread.sleep(1000)
        println("End")
    }

    // Better alternatives
    suspend fun modernMain() {
        println("Start")
        delay(1000)
        println("End")
    }
}
```

#### Real-World Examples

```kotlin
import kotlinx.coroutines.*

// Example 1: API rate limiting
class ApiClient {
    private var lastRequestTime = 0L
    private val minRequestInterval = 1000L // 1 second

    suspend fun makeRequest(url: String): String {
        val now = System.currentTimeMillis()
        val timeSinceLastRequest = now - lastRequestTime

        if (timeSinceLastRequest < minRequestInterval) {
            // Use delay, not Thread.sleep
            delay(minRequestInterval - timeSinceLastRequest)
        }

        lastRequestTime = System.currentTimeMillis()
        return performRequest(url)
    }

    private suspend fun performRequest(url: String): String {
        delay(500) // Simulate network request
        return "Response from $url"
    }
}

// Example 2: Polling mechanism
class DataPoller {
    suspend fun pollForData(intervalMs: Long = 5000) {
        while (true) {
            try {
                val data = fetchData()
                processData(data)
                delay(intervalMs) // Use delay for polling
            } catch (e: CancellationException) {
                println("Polling cancelled")
                throw e
            } catch (e: Exception) {
                println("Error: ${e.message}, retrying...")
                delay(intervalMs)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(200)
        return "data"
    }

    private fun processData(data: String) {
        println("Processed: $data")
    }
}

// Example 3: Timeout implementation
suspend fun <T> withCustomTimeout(timeMs: Long, block: suspend () -> T): T {
    return withTimeout(timeMs) {
        block()
    }
}

// Example 4: Delayed execution
class TaskScheduler {
    private val scope = CoroutineScope(Dispatchers.Default)

    fun scheduleTask(delayMs: Long, task: suspend () -> Unit): Job {
        return scope.launch {
            delay(delayMs) // Use delay for scheduling
            task()
        }
    }

    fun cancel() {
        scope.cancel()
    }
}

fun demonstrateRealWorld() = runBlocking {
    // API rate limiting
    val client = ApiClient()
    repeat(5) { index ->
        launch {
            val response = client.makeRequest("https://api.example.com/$index")
            println(response)
        }
    }

    delay(6000)

    // Polling
    val poller = DataPoller()
    val pollingJob = launch {
        poller.pollForData(1000)
    }

    delay(5000)
    pollingJob.cancel()

    // Scheduled tasks
    val scheduler = TaskScheduler()
    scheduler.scheduleTask(2000) {
        println("Scheduled task executed")
    }

    delay(3000)
    scheduler.cancel()
}
```

#### Testing Considerations

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class DelayVsSleepTest {
    // delay can be controlled in tests
    @Test
    fun testWithDelay() = runTest {
        var executed = false

        launch {
            delay(5000) // Virtual time
            executed = true
        }

        advanceTimeBy(5000) // Fast-forward time
        assertEquals(true, executed)
    }

    // Thread.sleep cannot be controlled
    @Test
    fun testWithSleep() = runTest {
        var executed = false

        launch {
            Thread.sleep(5000) // Real time! Test takes 5 seconds
            executed = true
        }

        // Cannot fast-forward Thread.sleep
        // Must actually wait 5 seconds
        delay(5000)
        assertEquals(true, executed)
    }

    // delay is much better for testing
    @Test
    fun testDelayAdvantage() = runTest {
        val startTime = currentTime

        delay(10000) // 10 seconds in virtual time
        advanceUntilIdle()

        val elapsedTime = currentTime - startTime
        // Test runs instantly, no real waiting
        println("Elapsed virtual time: $elapsedTime ms")
    }
}
```

#### Common Mistakes

```kotlin
import kotlinx.coroutines.*

fun commonMistakes() = runBlocking {
    // Mistake 1: Using Thread.sleep in coroutine
    launch {
        // BAD: Blocks the thread
        Thread.sleep(1000)
    }

    // Correct
    launch {
        // GOOD: Suspends the coroutine
        delay(1000)
    }

    // Mistake 2: Using Thread.sleep with withContext
    withContext(Dispatchers.IO) {
        // BAD: Blocks IO thread
        Thread.sleep(1000)
    }

    // Correct
    withContext(Dispatchers.IO) {
        // GOOD: Suspends, frees IO thread
        delay(1000)
    }

    // Mistake 3: Mixing blocking and suspending
    suspend fun mixedApproach() {
        delay(1000)
        Thread.sleep(1000) // BAD: Why block after suspending?
        delay(1000)
    }

    // Correct
    suspend fun consistentApproach() {
        delay(1000)
        delay(1000)
        delay(1000)
    }

    // Mistake 4: Using Thread.sleep for timeout
    launch {
        // BAD
        Thread.sleep(5000)
        cancel() // Manual timeout
    }

    // GOOD: Use withTimeout
    withTimeout(5000) {
        // Automatic cancellation
    }
}
```

### Quick Reference

```kotlin
// ✅ Use delay() when:
// - Inside coroutines
// - Need cancellation support
// - Want to avoid blocking threads
// - Writing tests (can be fast-forwarded)
// - Need efficient resource usage

suspend fun goodExample1() {
    delay(1000)
}

// ❌ Don't use Thread.sleep when:
// - Inside coroutines
// - Need cancellation
// - Care about performance
// - Writing testable code
// - Limited thread pool

suspend fun badExample1() {
    Thread.sleep(1000) // DON'T DO THIS
}

// ⚠️ Thread.sleep might be OK when:
// - Not in coroutine context
// - Simple blocking scripts
// - Legacy code (consider refactoring)

fun legacyCode() {
    Thread.sleep(1000) // OK if not in coroutine
}
```

### Best Practices

1. **Always use `delay()` in coroutines, never `Thread.sleep()`**
2. **Use `delay()` for any time-based waiting in suspending functions**
3. **`Thread.sleep()` should only be used in non-coroutine blocking code**
4. **Test coroutine code with `delay()` for fast testing**
5. **Check for `isActive` in long-running loops with `delay()`**

### Performance Summary

| Aspect | delay() | Thread.sleep() |
|--------|---------|----------------|
| Thread Usage | Suspends, frees thread | Blocks thread |
| Cancellable | Yes | No |
| Test Support | Fast-forward possible | Real time wait |
| Resource Efficient | Yes | No |
| Coroutine-friendly | Yes | No |
| Performance | High | Low (in coroutines) |

---

## Русский

### Описание проблемы

И `delay()`, и `Thread.sleep()` приостанавливают выполнение на указанное время, но работают они принципиально по-разному. Одна приостанавливает корутину без блокировки потока, в то время как другая блокирует весь поток. Каковы последствия для производительности, использования ресурсов, и когда следует использовать каждую из них?

### Решение

**`delay()`** - это **приостанавливающая функция**, которая останавливает корутину без блокировки базового потока, позволяя работать другим корутинам. **`Thread.sleep()`** - это **блокирующая функция**, которая блокирует весь поток, предотвращая любую другую работу на этом потоке.

[Полный перевод разделов...]

---

## Follow-up Questions

1. Can you use `delay()` outside of a coroutine context?
2. What happens if you call `Thread.sleep()` on the Main dispatcher in Android?
3. How does `delay()` work internally - does it create a timer?
4. Can `delay(0)` be useful, and what does it do?
5. What's the relationship between `delay()` and `yield()`?
6. How can you detect if `Thread.sleep()` is being used inappropriately in coroutines?
7. Is there ever a performance advantage to using `Thread.sleep()` in coroutines?
8. How does `delay()` handle very long delay times (hours/days)?

## References

- [Kotlin Coroutines Guide - Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [delay - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/delay.html)
- [Roman Elizarov - Blocking threads, suspending coroutines](https://medium.com/@elizarov/blocking-threads-suspending-coroutines-d33e11bf4761)
- [Android Developers - Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Related Questions

- [[q-coroutine-cancellation--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]
- [[q-suspending-functions--kotlin--medium]]
- [[q-coroutine-testing--kotlin--hard]]
- [[q-thread-blocking-vs-suspending--kotlin--medium]]

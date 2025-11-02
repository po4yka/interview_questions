---
id: kotlin-240
title: "delay() vs Thread.sleep(): what's the difference? / delay() против Thread.sleep()"
aliases: [delay vs Thread.sleep, delay против Thread.sleep]
topic: kotlin
difficulty: easy
original_language: en
language_tags: [en, ru]
question_kind: theory
status: draft
created: "2025-10-12"
updated: "2025-10-31"
tags: ["coroutines", "delay", "difficulty/easy", "kotlin", "suspending", "threads"]
description: "Understanding the fundamental differences between suspending delay() and blocking Thread.sleep() in Kotlin coroutines, including thread usage and performance implications"
moc: moc-kotlin
related: [q-array-vs-list-kotlin--kotlin--easy, q-kotlin-inline-functions--programming-languages--medium, q-kotlin-java-type-differences--programming-languages--medium]
subtopics: [coroutines, threading]
date created: Friday, October 31st 2025, 6:31:14 pm
date modified: Saturday, November 1st 2025, 5:43:27 pm
---

# delay() Vs Thread.sleep(): What's the Difference?

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

#### Thread Blocking Vs Suspending

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
//  Use delay() when:
// - Inside coroutines
// - Need cancellation support
// - Want to avoid blocking threads
// - Writing tests (can be fast-forwarded)
// - Need efficient resource usage

suspend fun goodExample1() {
    delay(1000)
}

//  Don't use Thread.sleep when:
// - Inside coroutines
// - Need cancellation
// - Care about performance
// - Writing testable code
// - Limited thread pool

suspend fun badExample1() {
    Thread.sleep(1000) // DON'T DO THIS
}

//  Thread.sleep might be OK when:
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

### Описание Проблемы

И `delay()`, и `Thread.sleep()` приостанавливают выполнение на указанное время, но работают они принципиально по-разному. Одна приостанавливает корутину без блокировки потока, в то время как другая блокирует весь поток. Каковы последствия для производительности, использования ресурсов, и когда следует использовать каждую из них?

### Решение

**`delay()`** - это **приостанавливающая функция (suspending function)**, которая останавливает корутину без блокировки базового потока, позволяя работать другим корутинам. **`Thread.sleep()`** - это **блокирующая функция**, которая блокирует весь поток, предотвращая любую другую работу на этом потоке.

#### Базовое Различие

```kotlin
import kotlinx.coroutines.*

fun basicDifference() = runBlocking {
    println("=== Thread.sleep() ===")
    println("Thread: ${Thread.currentThread().name}")

    // Thread.sleep блокирует поток
    Thread.sleep(1000)
    println("После Thread.sleep (поток был заблокирован)")

    println("\n=== delay() ===")
    println("Thread: ${Thread.currentThread().name}")

    // delay приостанавливает корутину
    delay(1000)
    println("После delay (поток НЕ был заблокирован)")
}
```

#### Блокировка Потока Vs Приостановка

```kotlin
import kotlinx.coroutines.*

fun demonstrateThreadBlocking() = runBlocking {
    println("=== Thread.sleep блокирует поток ===")

    val time1 = measureTimeMillis {
        launch {
            println("Корутина 1 запущена на ${Thread.currentThread().name}")
            Thread.sleep(1000) // Блокирует поток!
            println("Корутина 1 завершена")
        }

        launch {
            println("Корутина 2 запущена на ${Thread.currentThread().name}")
            Thread.sleep(1000) // Должна ждать поток
            println("Корутина 2 завершена")
        }
    }
    println("Время с Thread.sleep: $time1 ms") // ~2000ms (последовательно)

    println("\n=== delay приостанавливает корутину ===")

    val time2 = measureTimeMillis {
        launch {
            println("Корутина 3 запущена на ${Thread.currentThread().name}")
            delay(1000) // Приостанавливает, не блокирует поток
            println("Корутина 3 завершена")
        }

        launch {
            println("Корутина 4 запущена на ${Thread.currentThread().name}")
            delay(1000) // Может работать одновременно
            println("Корутина 4 завершена")
        }
    }
    println("Время с delay: $time2 ms") // ~1000ms (параллельно)
}
```

#### Визуализация Различий

```kotlin
import kotlinx.coroutines.*

fun visualizeTheorem() = runBlocking {
    println("=== Визуальная демонстрация ===")

    // С Thread.sleep: Поток заблокирован
    println("\nС Thread.sleep:")
    launch(Dispatchers.Default) {
        repeat(5) { i ->
            println("[$i] До sleep на ${Thread.currentThread().name}")
            Thread.sleep(500)
            println("[$i] После sleep")
        }
    }

    delay(3000) // Ждём завершения

    // С delay: Поток свободен для другой работы
    println("\n\nС delay:")
    repeat(5) {
        launch(Dispatchers.Default) {
            println("[$it] До delay на ${Thread.currentThread().name}")
            delay(500)
            println("[$it] После delay на ${Thread.currentThread().name}")
        }
    }

    delay(1500) // Всё завершится за ~500ms вместо 2500ms
}
```

#### Влияние На Производительность

```kotlin
import kotlinx.coroutines.*

fun performanceComparison() = runBlocking {
    println("=== Сравнение производительности ===")

    val coroutineCount = 100

    // Используя Thread.sleep: Создаёт перегрузку потоков
    val time1 = measureTimeMillis {
        val jobs = List(coroutineCount) {
            launch(Dispatchers.Default) {
                Thread.sleep(1000)
            }
        }
        jobs.forEach { it.join() }
    }
    println("$coroutineCount корутин с Thread.sleep: $time1 ms")

    // Используя delay: Эффективное использование ресурсов
    val time2 = measureTimeMillis {
        val jobs = List(coroutineCount) {
            launch(Dispatchers.Default) {
                delay(1000)
            }
        }
        jobs.forEach { it.join() }
    }
    println("$coroutineCount корутин с delay: $time2 ms")

    // Thread.sleep намного медленнее, так как блокирует потоки
}
```

#### Истощение Пула Потоков

```kotlin
import kotlinx.coroutines.*

fun threadPoolExhaustion() {
    println("=== Истощение пула потоков ===")

    // Плохо: Использование Thread.sleep истощает пул потоков
    runBlocking(Dispatchers.Default) {
        println("Доступно процессоров: ${Runtime.getRuntime().availableProcessors()}")

        val jobs = List(1000) { index ->
            launch {
                println("[$index] Запущена на ${Thread.currentThread().name}")
                Thread.sleep(5000) // Блокирует поток на 5 секунд
                println("[$index] Завершена")
            }
        }

        jobs.forEach { it.join() }
    }

    // Хорошо: Использование delay не истощает пул потоков
    runBlocking(Dispatchers.Default) {
        val jobs = List(1000) { index ->
            launch {
                println("[$index] Запущена на ${Thread.currentThread().name}")
                delay(5000) // Приостанавливает, поток может делать другую работу
                println("[$index] Завершена")
            }
        }

        jobs.forEach { it.join() }
    }
}
```

#### Поддержка Отмены

```kotlin
import kotlinx.coroutines.*

fun cancellationSupport() = runBlocking {
    println("=== Поддержка отмены ===")

    // Thread.sleep нельзя отменить
    val job1 = launch {
        try {
            println("Запуск Thread.sleep")
            Thread.sleep(10000)
            println("Thread.sleep завершён (это не напечатается)")
        } catch (e: Exception) {
            println("Поймано: ${e::class.simpleName}")
        }
    }

    delay(1000)
    job1.cancel()
    println("Job1 отменён: ${job1.isCancelled}")
    job1.join()

    // delay можно отменить
    val job2 = launch {
        try {
            println("Запуск delay")
            delay(10000)
            println("delay завершён (это не напечатается)")
        } catch (e: CancellationException) {
            println("delay был отменён корректно")
        }
    }

    delay(1000)
    job2.cancel()
    println("Job2 отменён: ${job2.isCancelled}")
    job2.join()
}
```

#### Примеры Использования

```kotlin
import kotlinx.coroutines.*

// Пример использования 1: Операции в корутинах - используйте delay
suspend fun periodicTask() {
    while (true) {
        performTask()
        delay(1000) // Приостанавливает, не блокирует
    }
}

// Пример использования 2: Тестирование с задержками
suspend fun testWithDelay() {
    val result = loadData()
    delay(100) // Даём время для асинхронных операций
    verify(result)
}

// Пример использования 3: Механизм повторных попыток
suspend fun retryWithDelay(times: Int, delayTime: Long, block: suspend () -> Unit) {
    repeat(times) { attempt ->
        try {
            block()
            return
        } catch (e: Exception) {
            if (attempt < times - 1) {
                delay(delayTime) // Ждём перед повторной попыткой
            }
        }
    }
}

// Пример использования 4: Throttling (ограничение частоты)
suspend fun throttledOperation(intervalMs: Long) {
    var lastExecutionTime = 0L

    fun canExecute(): Boolean {
        val currentTime = System.currentTimeMillis()
        return currentTime - lastExecutionTime >= intervalMs
    }

    if (!canExecute()) {
        val waitTime = intervalMs - (System.currentTimeMillis() - lastExecutionTime)
        delay(waitTime) // Используйте delay, не Thread.sleep
    }

    lastExecutionTime = System.currentTimeMillis()
    // Выполняем операцию
}

// ИЗБЕГАЙТЕ: Thread.sleep в корутинах
suspend fun badExample() {
    Thread.sleep(1000) // НЕ ДЕЛАЙТЕ ТАК в корутинах!
}

// Хорошо: Используйте delay вместо этого
suspend fun goodExample() {
    delay(1000) // Правильный способ
}

suspend fun performTask() {
    delay(100)
}

suspend fun loadData(): String {
    delay(100)
    return "data"
}

fun verify(result: String) {
    println("Проверено: $result")
}
```

#### Когда Thread.sleep Может Быть Допустим

```kotlin
import kotlinx.coroutines.*

fun whenThreadSleepIsOk() {
    // 1. Код вне корутин (редко в современном Kotlin)
    fun blockingFunction() {
        Thread.sleep(1000) // OK если не в контексте корутины
    }

    // 2. Блокирующие утилиты для тестов (не рекомендуется)
    fun simpleBlockingTest() {
        Thread.sleep(100)
        // Лучше использовать runBlocking + delay
    }

    // 3. Главный поток в простых скриптах (до корутин)
    fun oldStyleMain() {
        println("Start")
        Thread.sleep(1000)
        println("End")
    }

    // Лучшие альтернативы
    suspend fun modernMain() {
        println("Start")
        delay(1000)
        println("End")
    }
}
```

#### Реальные Примеры

```kotlin
import kotlinx.coroutines.*

// Пример 1: Ограничение частоты API запросов
class ApiClient {
    private var lastRequestTime = 0L
    private val minRequestInterval = 1000L // 1 секунда

    suspend fun makeRequest(url: String): String {
        val now = System.currentTimeMillis()
        val timeSinceLastRequest = now - lastRequestTime

        if (timeSinceLastRequest < minRequestInterval) {
            // Используйте delay, не Thread.sleep
            delay(minRequestInterval - timeSinceLastRequest)
        }

        lastRequestTime = System.currentTimeMillis()
        return performRequest(url)
    }

    private suspend fun performRequest(url: String): String {
        delay(500) // Имитация сетевого запроса
        return "Response from $url"
    }
}

// Пример 2: Механизм опроса (polling)
class DataPoller {
    suspend fun pollForData(intervalMs: Long = 5000) {
        while (true) {
            try {
                val data = fetchData()
                processData(data)
                delay(intervalMs) // Используйте delay для опроса
            } catch (e: CancellationException) {
                println("Опрос отменён")
                throw e
            } catch (e: Exception) {
                println("Ошибка: ${e.message}, повторная попытка...")
                delay(intervalMs)
            }
        }
    }

    private suspend fun fetchData(): String {
        delay(200)
        return "data"
    }

    private fun processData(data: String) {
        println("Обработано: $data")
    }
}

// Пример 3: Реализация timeout
suspend fun <T> withCustomTimeout(timeMs: Long, block: suspend () -> T): T {
    return withTimeout(timeMs) {
        block()
    }
}

// Пример 4: Отложенное выполнение
class TaskScheduler {
    private val scope = CoroutineScope(Dispatchers.Default)

    fun scheduleTask(delayMs: Long, task: suspend () -> Unit): Job {
        return scope.launch {
            delay(delayMs) // Используйте delay для планирования
            task()
        }
    }

    fun cancel() {
        scope.cancel()
    }
}

fun demonstrateRealWorld() = runBlocking {
    // Ограничение частоты API
    val client = ApiClient()
    repeat(5) { index ->
        launch {
            val response = client.makeRequest("https://api.example.com/$index")
            println(response)
        }
    }

    delay(6000)

    // Опрос
    val poller = DataPoller()
    val pollingJob = launch {
        poller.pollForData(1000)
    }

    delay(5000)
    pollingJob.cancel()

    // Запланированные задачи
    val scheduler = TaskScheduler()
    scheduler.scheduleTask(2000) {
        println("Запланированная задача выполнена")
    }

    delay(3000)
    scheduler.cancel()
}
```

#### Соображения По Тестированию

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class DelayVsSleepTest {
    // delay можно контролировать в тестах
    @Test
    fun testWithDelay() = runTest {
        var executed = false

        launch {
            delay(5000) // Виртуальное время
            executed = true
        }

        advanceTimeBy(5000) // Перемотка времени вперёд
        assertEquals(true, executed)
    }

    // Thread.sleep нельзя контролировать
    @Test
    fun testWithSleep() = runTest {
        var executed = false

        launch {
            Thread.sleep(5000) // Реальное время! Тест занимает 5 секунд
            executed = true
        }

        // Нельзя перемотать Thread.sleep
        // Нужно реально ждать 5 секунд
        delay(5000)
        assertEquals(true, executed)
    }

    // delay намного лучше для тестирования
    @Test
    fun testDelayAdvantage() = runTest {
        val startTime = currentTime

        delay(10000) // 10 секунд в виртуальном времени
        advanceUntilIdle()

        val elapsedTime = currentTime - startTime
        // Тест выполняется мгновенно, реального ожидания нет
        println("Прошло виртуального времени: $elapsedTime ms")
    }
}
```

#### Распространённые Ошибки

```kotlin
import kotlinx.coroutines.*

fun commonMistakes() = runBlocking {
    // Ошибка 1: Использование Thread.sleep в корутине
    launch {
        // ПЛОХО: Блокирует поток
        Thread.sleep(1000)
    }

    // Правильно
    launch {
        // ХОРОШО: Приостанавливает корутину
        delay(1000)
    }

    // Ошибка 2: Использование Thread.sleep с withContext
    withContext(Dispatchers.IO) {
        // ПЛОХО: Блокирует IO поток
        Thread.sleep(1000)
    }

    // Правильно
    withContext(Dispatchers.IO) {
        // ХОРОШО: Приостанавливает, освобождает IO поток
        delay(1000)
    }

    // Ошибка 3: Смешивание блокирующего и приостанавливающего подходов
    suspend fun mixedApproach() {
        delay(1000)
        Thread.sleep(1000) // ПЛОХО: Зачем блокировать после приостановки?
        delay(1000)
    }

    // Правильно
    suspend fun consistentApproach() {
        delay(1000)
        delay(1000)
        delay(1000)
    }

    // Ошибка 4: Использование Thread.sleep для timeout
    launch {
        // ПЛОХО
        Thread.sleep(5000)
        cancel() // Ручной timeout
    }

    // ХОРОШО: Используйте withTimeout
    withTimeout(5000) {
        // Автоматическая отмена
    }
}
```

### Краткая Справка

```kotlin
//  Используйте delay() когда:
// - Внутри корутин
// - Нужна поддержка отмены
// - Хотите избежать блокировки потоков
// - Пишете тесты (можно перематывать время)
// - Нужно эффективное использование ресурсов

suspend fun goodExample1() {
    delay(1000)
}

//  НЕ используйте Thread.sleep когда:
// - Внутри корутин
// - Нужна отмена
// - Важна производительность
// - Пишете тестируемый код
// - Ограниченный пул потоков

suspend fun badExample1() {
    Thread.sleep(1000) // НЕ ДЕЛАЙТЕ ТАК
}

//  Thread.sleep может быть OK когда:
// - Не в контексте корутины
// - Простые блокирующие скрипты
// - Легаси код (рассмотрите рефакторинг)

fun legacyCode() {
    Thread.sleep(1000) // OK если не в корутине
}
```

### Лучшие Практики

1. **Всегда используйте `delay()` в корутинах, никогда `Thread.sleep()`**
2. **Используйте `delay()` для любого временного ожидания в приостанавливающих функциях**
3. **`Thread.sleep()` следует использовать только в блокирующем коде вне корутин**
4. **Тестируйте код корутин с `delay()` для быстрого тестирования**
5. **Проверяйте `isActive` в долгоработающих циклах с `delay()`**

### Сводка По Производительности

| Аспект | delay() | Thread.sleep() |
|--------|---------|----------------|
| Использование потока | Приостанавливает, освобождает поток | Блокирует поток |
| Возможность отмены | Да | Нет |
| Поддержка тестирования | Возможна перемотка | Реальное ожидание |
| Эффективность ресурсов | Да | Нет |
| Совместимость с корутинами | Да | Нет |
| Производительность | Высокая | Низкая (в корутинах) |

---

## Follow-ups

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

### Same Level (Easy)
- [[q-what-is-coroutine--kotlin--easy]] - Basic coroutine concepts
- [[q-coroutine-builders-basics--kotlin--easy]] - launch, async, runBlocking
- [[q-coroutine-scope-basics--kotlin--easy]] - CoroutineScope fundamentals
- [[q-coroutines-threads-android-differences--kotlin--easy]] - Coroutines vs Threads on Android

### Next Steps (Medium)
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutine-dispatchers--kotlin--medium]] - Coroutine dispatchers overview
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs Context

### Advanced (Harder)
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines
- [[q-coroutine-memory-leaks--kotlin--hard]] - Coroutines

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines

### Related (Same Level)
- [[q-suspending-vs-blocking--kotlin--medium]] - Coroutines
- [[q-coroutine-virtual-time--kotlin--medium]] - Coroutines
- [[q-coroutine-context-explained--kotlin--medium]] - Coroutines
- [[q-coroutine-cancellation-cooperation--kotlin--medium]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction


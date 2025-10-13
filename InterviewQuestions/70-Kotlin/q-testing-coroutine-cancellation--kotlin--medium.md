---
id: 20251012-140004
title: "Testing Coroutine Cancellation Scenarios / Тестирование сценариев отмены корутин"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, testing, cancellation]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Coroutine Cancellation Testing Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-testing-coroutines-runtest--kotlin--medium, q-coroutine-cancellation-cooperation--kotlin--medium, q-coroutine-cancellation-mechanisms--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, testing, cancellation, difficulty/medium]
---
# Question (EN)
> How to test coroutine cancellation scenarios? Cover testing cooperative cancellation, timeout, ensureActive, CancellationException, and resource cleanup with NonCancellable.

# Вопрос (RU)
> Как тестировать сценарии отмены корутин? Покрыть тестирование кооперативной отмены, timeout, ensureActive, CancellationException и очистки ресурсов с NonCancellable.

---

## Answer (EN)

Testing cancellation is crucial for ensuring coroutines properly clean up resources and respond to cancellation requests. Kotlin coroutines use cooperative cancellation, which requires specific testing strategies.

### Basic Cancellation Testing

```kotlin
@Test
fun `coroutine can be cancelled`() = runTest {
    val job = launch {
        repeat(1000) {
            delay(100)
            println("Working $it")
        }
    }

    advanceTimeBy(250) // Let it run a bit
    assertTrue(job.isActive)

    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
    assertTrue(job.isCompleted)
}

@Test
fun `cancel stops execution`() = runTest {
    var counter = 0

    val job = launch {
        repeat(10) {
            delay(100)
            counter++
        }
    }

    advanceTimeBy(250)
    assertEquals(2, counter)

    job.cancel()
    advanceUntilIdle()

    // Counter doesn't reach 10
    assertTrue(counter < 10)
}
```

### Testing Cooperative Cancellation

Coroutines must cooperate with cancellation by checking `isActive` or calling suspending functions.

```kotlin
// Non-cooperative coroutine (BAD)
class NonCooperativeTask {
    suspend fun process(): Int {
        var result = 0
        repeat(1000000) {
            result += it // CPU-intensive, doesn't check cancellation
        }
        return result
    }
}

@Test
fun `non-cooperative coroutine doesn't cancel immediately`() = runTest {
    val task = NonCooperativeTask()
    var completed = false

    val job = launch {
        task.process()
        completed = true
    }

    advanceTimeBy(100)
    job.cancel()

    // Coroutine continues running!
    assertTrue(job.isActive) // Still processing
}

// Cooperative coroutine (GOOD)
class CooperativeTask {
    suspend fun process(): Int = coroutineScope {
        var result = 0
        repeat(1000000) {
            ensureActive() // Checks cancellation
            result += it
        }
        result
    }
}

@Test
fun `cooperative coroutine cancels immediately`() = runTest {
    val task = CooperativeTask()
    var completed = false

    val job = launch {
        try {
            task.process()
            completed = false
        } catch (e: CancellationException) {
            // Expected
        }
    }

    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
    assertFalse(completed)
}
```

### Testing ensureActive

```kotlin
class DataProcessor {
    suspend fun processLargeDataset(data: List<Int>): List<Int> = coroutineScope {
        val results = mutableListOf<Int>()

        for (item in data) {
            ensureActive() // Throws if cancelled
            results.add(processItem(item))
        }

        results
    }

    private fun processItem(item: Int): Int = item * 2
}

@Test
fun `ensureActive throws on cancellation`() = runTest {
    val processor = DataProcessor()
    val largeDataset = (1..10000).toList()

    val job = launch {
        try {
            processor.processLargeDataset(largeDataset)
            fail("Should have been cancelled")
        } catch (e: CancellationException) {
            // Expected
        }
    }

    advanceTimeBy(50)
    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
}

@Test
fun `ensureActive allows completion if not cancelled`() = runTest {
    val processor = DataProcessor()
    val dataset = (1..100).toList()

    val result = processor.processLargeDataset(dataset)

    assertEquals(100, result.size)
    assertEquals(dataset.map { it * 2 }, result)
}
```

### Testing isActive Check

```kotlin
class FileProcessor {
    suspend fun processFiles(files: List<File>): Int = coroutineScope {
        var processed = 0

        for (file in files) {
            if (!isActive) break // Check cancellation

            processFile(file)
            processed++
        }

        processed
    }

    private suspend fun processFile(file: File) {
        delay(100)
    }
}

@Test
fun `isActive check stops processing on cancellation`() = runTest {
    val processor = FileProcessor()
    val files = List(10) { File("file$it") }

    var result = 0

    val job = launch {
        result = processor.processFiles(files)
    }

    advanceTimeBy(350) // Process 3 files
    job.cancel()
    advanceUntilIdle()

    // Processed 3 files, stopped cleanly
    assertEquals(3, result)
}
```

### Testing CancellationException

```kotlin
@Test
fun `CancellationException is thrown on cancel`() = runTest {
    var exception: Throwable? = null

    val job = launch {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            exception = e
            throw e // Must rethrow!
        }
    }

    advanceTimeBy(500)
    job.cancel("Test cancellation", TestException())
    advanceUntilIdle()

    assertNotNull(exception)
    assertTrue(exception is CancellationException)
    assertEquals("Test cancellation", exception?.message)
}

class TestException : Exception("Test")

@Test
fun `don't suppress CancellationException`() = runTest {
    var finalized = false

    val job = launch {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            finalized = true
            throw e // MUST rethrow
        }
    }

    job.cancel()
    advanceUntilIdle()

    assertTrue(finalized)
    assertTrue(job.isCancelled)
}
```

### Testing Timeout

```kotlin
class SlowApi {
    suspend fun fetchData(): String {
        delay(5000) // Very slow
        return "data"
    }
}

@Test
fun `timeout cancels long-running operation`() = runTest {
    val api = SlowApi()

    val result = try {
        withTimeout(1000) {
            api.fetchData()
        }
    } catch (e: TimeoutCancellationException) {
        null
    }

    assertNull(result)
    assertEquals(1000, currentTime)
}

@Test
fun `timeout succeeds if completes in time`() = runTest {
    val api = object {
        suspend fun fetchData(): String {
            delay(500)
            return "data"
        }
    }

    val result = withTimeout(1000) {
        api.fetchData()
    }

    assertEquals("data", result)
    assertEquals(500, currentTime)
}

@Test
fun `withTimeoutOrNull returns null on timeout`() = runTest {
    val result = withTimeoutOrNull(1000) {
        delay(2000)
        "completed"
    }

    assertNull(result)
    assertEquals(1000, currentTime)
}

@Test
fun `withTimeoutOrNull returns value on success`() = runTest {
    val result = withTimeoutOrNull(1000) {
        delay(500)
        "completed"
    }

    assertEquals("completed", result)
    assertEquals(500, currentTime)
}
```

### Testing Resource Cleanup

```kotlin
class DatabaseConnection : Closeable {
    var closed = false
    var transactionActive = false

    fun beginTransaction() {
        transactionActive = true
    }

    fun commit() {
        transactionActive = false
    }

    override fun close() {
        closed = true
    }
}

class DatabaseService {
    suspend fun performTransaction(connection: DatabaseConnection) {
        try {
            connection.beginTransaction()
            delay(1000) // Simulate work
            connection.commit()
        } finally {
            connection.close()
        }
    }
}

@Test
fun `resources cleaned up on cancellation`() = runTest {
    val connection = DatabaseConnection()
    val service = DatabaseService()

    val job = launch {
        service.performTransaction(connection)
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    // Transaction was active but connection is closed
    assertTrue(connection.closed)
}

@Test
fun `use ensures resource cleanup`() = runTest {
    val connection = DatabaseConnection()

    val job = launch {
        connection.use {
            it.beginTransaction()
            delay(1000)
            it.commit()
        }
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    assertTrue(connection.closed)
}
```

### Testing NonCancellable

When cleanup must complete even after cancellation, use `withContext(NonCancellable)`.

```kotlin
class FileWriter {
    var fileOpen = false
    var bufferFlushed = false
    var fileClosed = false

    fun open() {
        fileOpen = true
    }

    suspend fun flush() {
        delay(100)
        bufferFlushed = true
    }

    suspend fun close() {
        delay(50)
        fileClosed = true
        fileOpen = false
    }
}

class FileService {
    suspend fun writeData(writer: FileWriter, data: String) {
        try {
            writer.open()
            delay(500) // Write data
        } finally {
            // Ensure cleanup completes even if cancelled
            withContext(NonCancellable) {
                writer.flush()
                writer.close()
            }
        }
    }
}

@Test
fun `NonCancellable allows cleanup to complete`() = runTest {
    val writer = FileWriter()
    val service = FileService()

    val job = launch {
        service.writeData(writer, "test data")
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    // Cleanup completed despite cancellation
    assertTrue(writer.bufferFlushed)
    assertTrue(writer.fileClosed)
    assertFalse(writer.fileOpen)
}

@Test
fun `cleanup with NonCancellable takes time`() = runTest {
    val writer = FileWriter()
    val service = FileService()

    val job = launch {
        service.writeData(writer, "test data")
    }

    advanceTimeBy(250)
    val cancelTime = currentTime
    job.cancel()
    advanceUntilIdle()
    val completeTime = currentTime

    // Cleanup took 150ms (flush 100ms + close 50ms)
    val cleanupTime = completeTime - cancelTime
    assertEquals(150, cleanupTime)
}
```

### Testing Child Cancellation

```kotlin
@Test
fun `cancelling parent cancels children`() = runTest {
    val child1Cancelled = CompletableDeferred<Unit>()
    val child2Cancelled = CompletableDeferred<Unit>()

    val parent = launch {
        launch {
            try {
                delay(Long.MAX_VALUE)
            } catch (e: CancellationException) {
                child1Cancelled.complete(Unit)
                throw e
            }
        }

        launch {
            try {
                delay(Long.MAX_VALUE)
            } catch (e: CancellationException) {
                child2Cancelled.complete(Unit)
                throw e
            }
        }

        delay(Long.MAX_VALUE)
    }

    advanceTimeBy(100)
    parent.cancel()
    advanceUntilIdle()

    assertTrue(child1Cancelled.isCompleted)
    assertTrue(child2Cancelled.isCompleted)
    assertTrue(parent.isCancelled)
}

@Test
fun `child failure doesn't cancel siblings with SupervisorJob`() = runTest {
    val child1Completed = CompletableDeferred<Unit>()
    val child2Completed = CompletableDeferred<Unit>()

    supervisorScope {
        launch {
            try {
                delay(500)
                child1Completed.complete(Unit)
            } catch (e: CancellationException) {
                // Shouldn't happen
            }
        }

        launch {
            delay(100)
            throw IllegalStateException("Child 2 failed")
        }

        launch {
            delay(500)
            child2Completed.complete(Unit)
        }
    }

    // Child 1 and 2 complete despite sibling failure
    assertTrue(child1Completed.isCompleted)
    assertTrue(child2Completed.isCompleted)
}
```

### Testing invokeOnCancellation

```kotlin
class ResourceManager {
    val releasedResources = mutableListOf<String>()

    suspend fun acquireResource(name: String) = suspendCancellableCoroutine<Unit> { continuation ->
        continuation.invokeOnCancellation {
            releasedResources.add(name)
        }
        continuation.resume(Unit)
    }
}

@Test
fun `invokeOnCancellation called on cancel`() = runTest {
    val manager = ResourceManager()

    val job = launch {
        manager.acquireResource("Resource1")
        delay(1000)
    }

    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()

    assertEquals(listOf("Resource1"), manager.releasedResources)
}

@Test
fun `invokeOnCancellation not called on completion`() = runTest {
    val manager = ResourceManager()

    val job = launch {
        manager.acquireResource("Resource1")
        delay(100)
    }

    advanceUntilIdle()

    // No cancellation, so invokeOnCancellation wasn't called
    assertTrue(manager.releasedResources.isEmpty())
}
```

### Testing Job.join and cancelAndJoin

```kotlin
@Test
fun `join waits for completion`() = runTest {
    var completed = false

    val job = launch {
        delay(500)
        completed = true
    }

    assertFalse(completed)

    job.join()

    assertTrue(completed)
    assertEquals(500, currentTime)
}

@Test
fun `cancelAndJoin cancels and waits`() = runTest {
    var cleanedUp = false

    val job = launch {
        try {
            delay(1000)
        } finally {
            withContext(NonCancellable) {
                delay(200)
                cleanedUp = true
            }
        }
    }

    advanceTimeBy(500)

    val cancelTime = currentTime
    job.cancelAndJoin()
    val joinTime = currentTime

    assertTrue(job.isCancelled)
    assertTrue(cleanedUp)
    assertEquals(200, joinTime - cancelTime) // Waited for cleanup
}
```

### Testing Structured Concurrency Cancellation

```kotlin
@Test
fun `coroutineScope cancels all children on failure`() = runTest {
    val task1Started = CompletableDeferred<Unit>()
    val task1Cancelled = CompletableDeferred<Unit>()
    val task2Started = CompletableDeferred<Unit>()
    val task2Cancelled = CompletableDeferred<Unit>()

    val result = try {
        coroutineScope {
            launch {
                task1Started.complete(Unit)
                try {
                    delay(Long.MAX_VALUE)
                } catch (e: CancellationException) {
                    task1Cancelled.complete(Unit)
                    throw e
                }
            }

            launch {
                task2Started.complete(Unit)
                delay(100)
                throw IllegalStateException("Task 2 failed")
            }

            delay(Long.MAX_VALUE)
        }
        "completed"
    } catch (e: IllegalStateException) {
        "failed"
    }

    assertEquals("failed", result)
    assertTrue(task1Started.isCompleted)
    assertTrue(task1Cancelled.isCompleted)
    assertTrue(task2Started.isCompleted)
}

@Test
fun `supervisorScope doesn't cancel siblings on failure`() = runTest {
    val task1Completed = CompletableDeferred<Unit>()
    val task2Failed = CompletableDeferred<Unit>()

    supervisorScope {
        launch {
            delay(500)
            task1Completed.complete(Unit)
        }

        launch {
            delay(100)
            task2Failed.complete(Unit)
            throw IllegalStateException("Task 2 failed")
        }
    }

    assertTrue(task1Completed.isCompleted)
    assertTrue(task2Failed.isCompleted)
}
```

### Testing Cancellation in Flow

```kotlin
@Test
fun `Flow collection can be cancelled`() = runTest {
    var emissionCount = 0

    val flow = flow {
        repeat(10) {
            emit(it)
            emissionCount++
            delay(100)
        }
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(350)
    job.cancel()
    advanceUntilIdle()

    // Only 3 emissions before cancellation
    assertEquals(3, emissionCount)
}

@Test
fun `Flow cancels upstream on collector cancellation`() = runTest {
    var upstreamCancelled = false

    val flow = flow {
        try {
            repeat(10) {
                emit(it)
                delay(100)
            }
        } catch (e: CancellationException) {
            upstreamCancelled = true
            throw e
        }
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(upstreamCancelled)
}

@Test
fun `onCompletion detects cancellation`() = runTest {
    var cancellationDetected = false
    var cause: Throwable? = null

    val flow = flow {
        repeat(10) {
            emit(it)
            delay(100)
        }
    }.onCompletion { throwable ->
        cause = throwable
        cancellationDetected = throwable is CancellationException
    }

    val job = launch {
        flow.collect { }
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(cancellationDetected)
    assertNotNull(cause)
}
```

### Best Practices

```kotlin
//  DO: Use ensureActive for CPU-intensive work
suspend fun processData(data: List<Int>) = coroutineScope {
    data.map { item ->
        ensureActive()
        processItem(item)
    }
}

//  DON'T: Ignore cancellation
suspend fun badProcess(data: List<Int>) {
    data.forEach { item ->
        // No cancellation check!
        processItem(item)
    }
}

//  DO: Use NonCancellable for cleanup
try {
    // Main work
} finally {
    withContext(NonCancellable) {
        cleanup()
    }
}

//  DON'T: Suppress CancellationException
try {
    delay(1000)
} catch (e: CancellationException) {
    // Don't catch and ignore!
}

//  DO: Rethrow CancellationException
try {
    delay(1000)
} catch (e: CancellationException) {
    cleanup()
    throw e // MUST rethrow
}

//  DO: Use use() for resources
resource.use {
    // Automatic cleanup on cancellation
}

//  DO: Test cancellation timing
@Test
fun test() = runTest {
    val job = launch { /* ... */ }
    advanceTimeBy(500)
    job.cancel()
    advanceUntilIdle()
    assertTrue(job.isCancelled)
}
```

### Summary

**Key concepts**:
- **Cooperative cancellation**: Coroutines must check `isActive` or call suspending functions
- **ensureActive()**: Throws CancellationException if cancelled
- **CancellationException**: Must be rethrown after cleanup
- **NonCancellable**: Context for cleanup that must complete
- **invokeOnCancellation**: Register cleanup callback

**Testing strategies**:
- Test that cancellation stops work promptly
- Test that resources are cleaned up properly
- Test that CancellationException is propagated
- Test timeout scenarios
- Test child cancellation in structured concurrency
- Use virtual time to control cancellation timing

**Common pitfalls**:
- Not checking cancellation in CPU-intensive loops
- Catching and suppressing CancellationException
- Not using NonCancellable for critical cleanup
- Forgetting to test resource cleanup on cancellation

---

## Ответ (RU)

Тестирование отмены критически важно для обеспечения правильной очистки ресурсов и ответа на запросы отмены.

### Базовое тестирование отмены

```kotlin
@Test
fun `корутина может быть отменена`() = runTest {
    val job = launch {
        repeat(1000) {
            delay(100)
        }
    }

    advanceTimeBy(250)
    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
}
```

### Тестирование кооперативной отмены

```kotlin
@Test
fun `ensureActive выбрасывает исключение при отмене`() = runTest {
    val job = launch {
        try {
            repeat(1000000) {
                ensureActive()
                // Обработка
            }
        } catch (e: CancellationException) {
            // Ожидается
        }
    }

    job.cancel()
    advanceUntilIdle()

    assertTrue(job.isCancelled)
}
```

### Лучшие практики

1. **Используйте ensureActive** для CPU-интенсивной работы
2. **Пробрасывайте CancellationException** после очистки
3. **Используйте NonCancellable** для критичной очистки
4. **Тестируйте очистку ресурсов** при отмене
5. **Используйте use()** для автоматической очистки

---

## Follow-ups

1. What happens if you don't rethrow CancellationException?
2. How does cancellation work with supervisorScope?
3. What is the difference between cancel() and cancelAndJoin()?
4. How to handle cancellation in custom suspending functions?
5. What are the performance implications of frequent ensureActive() calls?

---

## References

- [Cancellation and Timeouts - Kotlin Docs](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Cooperative Cancellation](https://kotlinlang.org/docs/cancellation-and-timeouts.html#cancellation-is-cooperative)
- [Testing Coroutines - Android Developers](https://developer.android.com/kotlin/coroutines/test)

---

## Related Questions

- [[q-coroutine-cancellation-cooperation--kotlin--medium]] - Cooperative cancellation explained
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]] - Cancellation mechanisms
- [[q-coroutine-resource-cleanup--kotlin--medium]] - Resource cleanup patterns
- [[q-testing-coroutines-runtest--kotlin--medium]] - runTest basics

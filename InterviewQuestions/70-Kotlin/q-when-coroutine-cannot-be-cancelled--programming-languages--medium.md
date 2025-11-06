---
id: lang-084
title: "When Coroutine Cannot Be Cancelled / Когда корутина не может быть отменена"
aliases: [When Coroutine Cannot Be Cancelled, Когда корутина не может быть отменена]
topic: programming-languages
subtopics: [cancellation, coroutines, lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-equals-hashcode-rules--programming-languages--medium, q-how-suspend-function-detects-suspension--programming-languages--hard, q-priorityqueue-vs-deque--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [cancellation, coroutines, difficulty/medium, kotlin, programming-languages]
---
# When Coroutine Cannot Be Cancelled?

# Вопрос (RU)
> Когда корутина не может быть отменена?

---

# Question (EN)
> When can a coroutine not be cancelled?

## Ответ (RU)

Да, есть три основных случая: 1. Блокирующий код – если внутри корутины используется блокирующая операция (Thread.sleep(), while(true) {}), она не реагирует на отмену. 2. Отмена родительской корутины не отменяет launch(NonCancellable) – если корутина запущена с NonCancellable, она игнорирует отмену. 3. Отмена не срабатывает, если корутина не проверяет isActive или yield() – долгие вычисления без точек приостановки не дадут корутине завершиться.

## Answer (EN)

Yes, there are three main cases when cancellation doesn't work:

1. **Blocking code**: If blocking operations are used inside coroutine (Thread.sleep(), while(true) {}), it doesn't react to cancellation
2. **NonCancellable context**: If coroutine is launched with NonCancellable, it ignores cancellation
3. **No cooperation**: Cancellation doesn't work if coroutine doesn't check isActive or yield() - long computations without suspension points won't allow coroutine to finish

### Case 1: Blocking Code

```kotlin
import kotlinx.coroutines.*

// - Cannot cancel - uses Thread.sleep (blocking)
fun blockingExample() = runBlocking {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Iteration $i")
                Thread.sleep(1000)  // Blocking call!
            }
        } finally {
            println("Finally block")
        }
    }

    delay(2500)
    println("Cancelling...")
    job.cancelAndJoin()  // Won't stop Thread.sleep
    println("Done")
}

// Output:
// Iteration 0
// Iteration 1
// Iteration 2  <- Tries to cancel here
// Iteration 3  <- But continues!
// Iteration 4  <- Still running!
// Finally block
// Done

// - SOLUTION: Use delay instead
fun cooperativeExample() = runBlocking {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Iteration $i")
                delay(1000)  // Suspension point - checks cancellation
            }
        } finally {
            println("Finally block")
        }
    }

    delay(2500)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}

// Output:
// Iteration 0
// Iteration 1
// Iteration 2
// Cancelling...
// Finally block  <- Cancelled successfully
// Done
```

### Case 2: NonCancellable Context

```kotlin
// - Cannot cancel - uses NonCancellable
fun nonCancellableExample() = runBlocking {
    val job = launch(NonCancellable) {
        repeat(5) { i ->
            println("Iteration $i")
            delay(1000)
        }
        println("Completed")
    }

    delay(2500)
    println("Trying to cancel...")
    job.cancel()  // Has no effect!
    job.join()
    println("Done")
}

// Output:
// Iteration 0
// Iteration 1
// Iteration 2
// Trying to cancel...
// Iteration 3  <- Ignores cancellation
// Iteration 4
// Completed
// Done

// Use case for NonCancellable: Cleanup operations
suspend fun performCleanup() {
    try {
        // Regular work
        doWork()
    } finally {
        // Ensure cleanup completes even if parent is cancelled
        withContext(NonCancellable) {
            saveState()  // Must complete
            closeResources()  // Must complete
        }
    }
}
```

### Case 3: No Cooperation - CPU-Intensive Loop

```kotlin
// - Cannot cancel - no suspension points or checks
fun cpuIntensiveNonCooperative() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {  // Long-running loop
            i++
            // No suspension point
            // No isActive check
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()  // Won't cancel - loop doesn't cooperate
    println("Done")
}

// - SOLUTION 1: Check isActive
fun cpuIntensiveCooperative1() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000 && isActive) {  // Check isActive
            i++
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}

// - SOLUTION 2: Call yield()
fun cpuIntensiveCooperative2() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {
            i++
            if (i % 1_000_000 == 0) {
                yield()  // Suspension point + cancellation check
            }
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}

// - SOLUTION 3: Use ensureActive()
fun cpuIntensiveCooperative3() = runBlocking {
    val job = launch {
        var i = 0
        while (i < 1_000_000_000) {
            i++
            if (i % 1_000_000 == 0) {
                ensureActive()  // Throws CancellationException if cancelled
            }
        }
        println("Completed: $i")
    }

    delay(100)
    println("Cancelling...")
    job.cancelAndJoin()
    println("Done")
}
```

### Case 4: Infinite Loop Without Checks

```kotlin
// - Cannot cancel - infinite loop with blocking
fun infiniteBlockingLoop() = runBlocking {
    val job = launch {
        while (true) {
            println("Working...")
            Thread.sleep(1000)  // Blocking!
        }
    }

    delay(3000)
    job.cancel()  // Won't work
}

// - SOLUTION: Use delay and isActive
fun infiniteCooperativeLoop() = runBlocking {
    val job = launch {
        while (isActive) {
            println("Working...")
            delay(1000)  // Suspending + checks cancellation
        }
    }

    delay(3000)
    job.cancel()
    println("Cancelled successfully")
}
```

### Case 5: Blocking I/O

```kotlin
// - Cannot cancel during blocking I/O
fun blockingIO() = runBlocking {
    val job = launch {
        val file = File("large_file.txt")
        file.readLines()  // Blocking read - cannot cancel mid-operation
        println("Read complete")
    }

    delay(100)
    job.cancel()  // File read continues
}

// - SOLUTION: Use interruptible I/O
fun interruptibleIO() = runBlocking {
    val job = launch(Dispatchers.IO) {
        withContext(Dispatchers.IO) {
            File("large_file.txt").useLines { lines ->
                lines.forEach { line ->
                    ensureActive()  // Check cancellation periodically
                    processLine(line)
                }
            }
        }
    }

    delay(100)
    job.cancelAndJoin()
}
```

### Cancellation Cooperation Patterns

```kotlin
// Pattern 1: isActive property
suspend fun cooperativeWork1() {
    while (isActive) {
        // Do work
        performTask()
    }
}

// Pattern 2: yield() function
suspend fun cooperativeWork2() {
    repeat(1000) {
        yield()  // Suspension point + cancellation check
        performTask()
    }
}

// Pattern 3: ensureActive() function
suspend fun cooperativeWork3() {
    repeat(1000) {
        ensureActive()  // Throws if cancelled
        performTask()
    }
}

// Pattern 4: delay() naturally checks
suspend fun cooperativeWork4() {
    repeat(1000) {
        delay(100)  // Checks cancellation automatically
        performTask()
    }
}

// Pattern 5: Cancellable suspend functions
suspend fun cooperativeWork5() {
    repeat(1000) {
        // Any suspend function from coroutines library checks cancellation
        withContext(Dispatchers.Default) {
            performTask()
        }
    }
}
```

### Real-World Example: Image Processing

```kotlin
// - Non-cooperative image processing
suspend fun processImagesNonCooperative(images: List<Bitmap>) {
    for (image in images) {
        // Long blocking operation
        val processed = processImage(image)  // Cannot cancel mid-processing
        saveImage(processed)
    }
}

// - Cooperative image processing
suspend fun processImagesCooperative(images: List<Bitmap>) {
    for (image in images) {
        ensureActive()  // Check before processing each image
        val processed = withContext(Dispatchers.Default) {
            processImage(image)
        }
        ensureActive()  // Check before saving
        saveImage(processed)
    }
}

// - Even better: Check during processing
suspend fun processImageCooperative(image: Bitmap): Bitmap {
    return withContext(Dispatchers.Default) {
        val width = image.width
        val height = image.height
        val result = Bitmap.createBitmap(width, height, image.config)

        for (y in 0 until height) {
            ensureActive()  // Check cancellation every row
            for (x in 0 until width) {
                result.setPixel(x, y, processPixel(image.getPixel(x, y)))
            }
        }
        result
    }
}
```

### Try-finally with Cancellation

```kotlin
// Cancellation throws CancellationException
suspend fun withCleanup() = coroutineScope {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Step $i")
                delay(1000)
            }
        } catch (e: CancellationException) {
            println("Caught cancellation")
            throw e  // Must rethrow!
        } finally {
            println("Cleanup")
        }
    }

    delay(2500)
    job.cancel()
}

// Output:
// Step 0
// Step 1
// Step 2
// Caught cancellation
// Cleanup
```

### NonCancellable for Critical Cleanup

```kotlin
suspend fun withCriticalCleanup() = coroutineScope {
    val job = launch {
        try {
            repeat(5) { i ->
                println("Working $i")
                delay(1000)
            }
        } finally {
            // Even if cancelled, complete cleanup
            withContext(NonCancellable) {
                println("Saving state...")
                delay(500)  // This delay won't be cancelled
                println("State saved")
            }
        }
    }

    delay(2500)
    job.cancelAndJoin()
    println("Job fully finished")
}

// Output:
// Working 0
// Working 1
// Working 2
// Saving state...
// State saved  <- Completed despite cancellation
// Job fully finished
```

### Testing Cancellation

```kotlin
class CancellationTest {
    @Test
    fun `cooperative coroutine cancels quickly`() = runTest {
        val job = launch {
            while (isActive) {
                yield()
            }
        }

        job.cancelAndJoin()
        // Test passes quickly
    }

    @Test(timeout = 5000)
    fun `non-cooperative coroutine may timeout`() = runTest {
        val job = launch {
            var i = 0
            while (i < Int.MAX_VALUE) {
                i++  // No cooperation
            }
        }

        job.cancel()
        job.join()  // May timeout!
    }
}
```

### Best Practices

```kotlin
class CancellationBestPractices {
    // - DO: Use delay instead of Thread.sleep
    suspend fun good1() {
        delay(1000)  // Checks cancellation
    }

    // - DON'T: Use blocking sleep
    suspend fun bad1() {
        Thread.sleep(1000)  // Ignores cancellation
    }

    // - DO: Check isActive in loops
    suspend fun good2() {
        while (isActive) {
            doWork()
        }
    }

    // - DON'T: Ignore cancellation in loops
    suspend fun bad2() {
        while (true) {  // Never checks cancellation
            doWork()
        }
    }

    // - DO: Call yield() in CPU-intensive work
    suspend fun good3() {
        repeat(1_000_000) { i ->
            if (i % 1000 == 0) yield()
            compute()
        }
    }

    // - DON'T: Long running without cooperation
    suspend fun bad3() {
        repeat(1_000_000) {
            compute()  // No cancellation checks
        }
    }

    // - DO: Use NonCancellable only for cleanup
    suspend fun good4() {
        try {
            doWork()
        } finally {
            withContext(NonCancellable) {
                cleanup()  // Must complete
            }
        }
    }

    // - DON'T: Use NonCancellable for regular work
    suspend fun bad4() {
        withContext(NonCancellable) {
            doWork()  // Cannot be cancelled!
        }
    }
}
```

### Summary

| Scenario | Cancellable? | Solution |
|----------|--------------|----------|
| `delay()` | - Yes | Built-in cooperation |
| `Thread.sleep()` | - No | Use `delay()` instead |
| `while(isActive)` | - Yes | Checks cancellation |
| `while(true)` | - No | Check `isActive` or call `yield()` |
| `NonCancellable` context | - No | By design (use only for cleanup) |
| CPU-intensive with `yield()` | - Yes | Cooperative |
| CPU-intensive without checks | - No | Add `yield()` or `ensureActive()` |
| Blocking I/O | - No | Use suspending I/O or add checks |

---


## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-how-suspend-function-detects-suspension--programming-languages--hard]]
- [[q-priorityqueue-vs-deque--programming-languages--easy]]
- [[q-equals-hashcode-rules--programming-languages--medium]]

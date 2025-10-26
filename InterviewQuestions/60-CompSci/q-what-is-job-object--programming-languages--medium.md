---
id: 20251012-1227111192
title: "What Is Job Object / Что такое объект Job"
topic: computer-science
difficulty: medium
status: draft
moc: moc-cs
related: [q-concurrency-fundamentals--computer-science--hard, q-data-structures-algorithms--computer-science--hard, q-decorator-pattern--design-patterns--medium]
created: 2025-10-15
tags: [programming-languages]
date created: Saturday, October 4th 2025, 10:55:52 am
date modified: Sunday, October 26th 2025, 1:39:59 pm
---

# What is the Job Object For?

# Question (EN)
> What is the Job Object for?

# Вопрос (RU)
> Для чего нужен объект Job?

---

## Answer (EN)

**Job** is an element for managing coroutine lifecycle. With it you can:

- **Cancel coroutine**: Stop execution
- **Track completion**: Wait for coroutine to finish
- **Combine with other tasks**: Manage parent-child relationships
- **Manage parent and child coroutines**: Structure concurrency

Job provides a handle to control and monitor coroutine execution.

### Basic Job Usage

```kotlin
import kotlinx.coroutines.*

fun basicJobExample() = runBlocking {
    val job: Job = launch {
        repeat(5) { i ->
            println("Working $i")
            delay(500)
        }
    }

    delay(1200)
    job.cancel()  // Cancel the coroutine
    println("Job cancelled")
}
```

### Creating a Job

```kotlin
// Job is returned from launch
val job1 = CoroutineScope(Dispatchers.Default).launch {
    // Work
}

// Create Job manually
val job2 = Job()
val scope = CoroutineScope(job2 + Dispatchers.Default)

// Job from async
val deferred = CoroutineScope(Dispatchers.Default).async {
    // Work
}
val job3: Job = deferred  // Deferred is a Job
```

### Cancelling with Job

```kotlin
fun cancellationExample() = runBlocking {
    val job = launch {
        try {
            repeat(10) { i ->
                println("Step $i")
                delay(500)
            }
        } finally {
            println("Cleanup")
        }
    }

    delay(1200)
    job.cancel()  // Cancel the job
    job.join()    // Wait for cancellation to complete

    // Or use cancelAndJoin() to combine both
    // job.cancelAndJoin()
}
```

### Waiting for Completion

```kotlin
fun joinExample() = runBlocking {
    val job = launch {
        delay(1000)
        println("Job done")
    }

    println("Waiting...")
    job.join()  // Wait for completion
    println("Job finished")
}

// Output:
// Waiting...
// Job done
// Job finished
```

### Job States

```kotlin
fun jobStates() = runBlocking {
    val job = launch {
        delay(1000)
    }

    println("isActive: ${job.isActive}")       // true
    println("isCompleted: ${job.isCompleted}") // false
    println("isCancelled: ${job.isCancelled}") // false

    job.cancel()

    println("isActive: ${job.isActive}")       // false
    println("isCompleted: ${job.isCompleted}") // true
    println("isCancelled: ${job.isCancelled}") // true
}
```

### Parent-Child Job Relationships

```kotlin
fun parentChildExample() = runBlocking {
    val parentJob = launch {
        val child1 = launch {
            delay(1000)
            println("Child 1 done")
        }

        val child2 = launch {
            delay(2000)
            println("Child 2 done")
        }

        println("Parent waiting for children")
    }

    parentJob.join()
    println("Parent done")  // Waits for all children
}

// Cancelling parent cancels all children
fun cancelParent() = runBlocking {
    val parent = launch {
        launch {
            repeat(10) { println("Child 1: $it"); delay(100) }
        }
        launch {
            repeat(10) { println("Child 2: $it"); delay(100) }
        }
    }

    delay(250)
    parent.cancel()  // Cancels both children
}
```

### SupervisorJob

```kotlin
// Regular Job: One child failure cancels all
fun regularJobFailure() = runBlocking {
    val job = Job()
    val scope = CoroutineScope(job)

    scope.launch {
        delay(100)
        throw Exception("Child 1 failed")
    }

    scope.launch {
        delay(200)
        println("Child 2")  // Won't print - cancelled by sibling failure
    }

    delay(500)
}

// SupervisorJob: Children fail independently
fun supervisorJobExample() = runBlocking {
    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(supervisorJob)

    scope.launch {
        delay(100)
        throw Exception("Child 1 failed")
    }

    scope.launch {
        delay(200)
        println("Child 2")  // Prints - not affected by sibling
    }

    delay(500)
}
```

### Job with CoroutineScope

```kotlin
class MyManager {
    private val job = Job()
    private val scope = CoroutineScope(job + Dispatchers.Default)

    fun startWork() {
        scope.launch {
            // Work is tied to job lifecycle
            performTask()
        }
    }

    fun stopWork() {
        job.cancel()  // Cancels all coroutines in scope
    }
}
```

### Combining Jobs

```kotlin
fun combiningJobs() = runBlocking {
    val job1 = launch { delay(1000); println("Job 1") }
    val job2 = launch { delay(2000); println("Job 2") }
    val job3 = launch { delay(3000); println("Job 3") }

    // Wait for all
    joinAll(job1, job2, job3)
    println("All jobs done")
}

// Cancel all jobs
fun cancelAllJobs() = runBlocking {
    val jobs = List(5) { i ->
        launch {
            repeat(10) { println("Job $i"); delay(200) }
        }
    }

    delay(500)
    jobs.forEach { it.cancel() }  // Cancel all
}
```

### Job Callbacks

```kotlin
fun jobCallbacks() = runBlocking {
    val job = launch {
        delay(1000)
        println("Job done")
    }

    job.invokeOnCompletion { exception ->
        if (exception != null) {
            println("Job failed: ${exception.message}")
        } else {
            println("Job completed successfully")
        }
    }

    job.join()
}

// Cancellation callback
fun cancellationCallback() = runBlocking {
    val job = launch {
        try {
            delay(1000)
        } finally {
            println("Cleanup")
        }
    }

    job.invokeOnCompletion {
        println("Job completed or cancelled")
    }

    delay(500)
    job.cancel()
}
```

### Real-World Example: Download Manager

```kotlin
class DownloadManager {
    private val downloads = mutableMapOf<String, Job>()

    fun startDownload(url: String, scope: CoroutineScope) {
        val job = scope.launch {
            try {
                downloadFile(url)
                println("Download complete: $url")
            } catch (e: CancellationException) {
                println("Download cancelled: $url")
                throw e
            } catch (e: Exception) {
                println("Download failed: $url")
            }
        }

        downloads[url] = job
    }

    fun cancelDownload(url: String) {
        downloads[url]?.cancel()
        downloads.remove(url)
    }

    fun cancelAll() {
        downloads.values.forEach { it.cancel() }
        downloads.clear()
    }

    fun isDownloading(url: String): Boolean {
        return downloads[url]?.isActive == true
    }
}
```

### Job Hierarchy

```kotlin
fun jobHierarchy() = runBlocking {
    val grandparent = Job()
    val parent = Job(grandparent)  // Child of grandparent
    val child = Job(parent)         // Child of parent

    // Cancelling grandparent cancels all descendants
    grandparent.cancel()

    println("Grandparent cancelled: ${grandparent.isCancelled}")  // true
    println("Parent cancelled: ${parent.isCancelled}")            // true
    println("Child cancelled: ${child.isCancelled}")              // true
}
```

### Best Practices

```kotlin
class JobBestPractices {
    // - DO: Store job for lifecycle management
    class GoodManager {
        private val job = SupervisorJob()
        private val scope = CoroutineScope(job + Dispatchers.Default)

        fun start() {
            scope.launch { work() }
        }

        fun stop() {
            job.cancel()
        }
    }

    // - DO: Use cancelAndJoin for clean shutdown
    suspend fun goodShutdown(job: Job) {
        job.cancelAndJoin()  // Cancel and wait
        println("Clean shutdown complete")
    }

    // - DON'T: Forget to clean up jobs
    class BadManager {
        fun start() {
            GlobalScope.launch {  // No way to cancel
                infiniteWork()
            }
        }
        // Memory leak!
    }

    // - DON'T: Ignore job completion
    fun badExample() = runBlocking {
        launch {
            // Long running work
        }
        // Doesn't wait - may exit before work completes
    }
}
```

### Summary

**Job provides:**
- **Lifecycle management**: Control coroutine execution
- **Cancellation**: Stop coroutines gracefully
- **Completion tracking**: Wait for coroutines to finish
- **Parent-child relationships**: Structure concurrency
- **Exception handling**: Manage failures

**Common operations:**
- `job.cancel()`: Cancel the job
- `job.join()`: Wait for completion
- `job.cancelAndJoin()`: Cancel and wait
- `job.isActive`: Check if running
- `job.invokeOnCompletion {}`: Add callback

---

## Ответ (RU)

Job — это элемент управления жизненным циклом корутины. С его помощью можно: отменять корутину; отслеживать завершение; объединять с другими задачами; управлять родительскими и дочерними корутинами.

## Related Questions

- [[q-concurrency-fundamentals--computer-science--hard]]
- [[q-data-structures-algorithms--computer-science--hard]]
- [[q-decorator-pattern--design-patterns--medium]]

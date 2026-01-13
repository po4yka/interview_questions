---
anki_cards:
- slug: q-what-is-job-object--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-what-is-job-object--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
## Answer (EN)

Job is a handle for managing coroutine lifecycle and part of the coroutine job hierarchy in Kotlin coroutines. With it you can:

- Cancel coroutine execution
- Track completion
- Coordinate related tasks (e.g., wait for a group of coroutines)
- Manage parent and child coroutines within structured concurrency

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
    job.cancel()  // Request cancellation
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

    println("isActive: ${job.isActive}")       // true (while coroutine is running)
    println("isCompleted: ${job.isCompleted}") // false
    println("isCancelled: ${job.isCancelled}") // false

    job.cancel()

    println("isActive: ${job.isActive}")       // false
    println("isCompleted: ${job.isCompleted}") // true (completed due to cancellation)
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
        // The parent coroutine will not complete until its children complete
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
    parent.cancel()  // Requests cancellation for parent and both children
}
```

### SupervisorJob

```kotlin
// Regular Job: One child failure cancels all children of that scope
fun regularJobFailure() = runBlocking {
    val job = Job()
    val scope = CoroutineScope(job)

    scope.launch {
        delay(100)
        throw Exception("Child 1 failed")
    }

    scope.launch {
        delay(200)
        println("Child 2")  // Won't print - cancelled due to sibling failure in regular Job
    }

    delay(500)
}

// SupervisorJob: Children fail independently; cancelling the supervisor still cancels all children
fun supervisorJobExample() = runBlocking {
    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(supervisorJob)

    scope.launch {
        delay(100)
        throw Exception("Child 1 failed")
    }

    scope.launch {
        delay(200)
        println("Child 2")  // Prints - not cancelled by sibling failure
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
    val parent = Job(grandparent)  // Child of grandparent (low-level, manual linkage)
    val child = Job(parent)        // Child of parent

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

    // - DON'T: Use GlobalScope for long-lived work you don't control
    class BadManager {
        fun start() {
            GlobalScope.launch {
                // Long running work not bound to any lifecycle
                infiniteWork()
            }
        }
        // Risk of work outliving the component and causing resource leaks
    }

    // - DON'T: Ignore job completion when you need a deterministic result
    fun badExample() = runBlocking {
        launch {
            // Long running work
        }
        // Doesn't wait - may exit before work completes
    }
}
```

### Summary

Job provides:
- `Lifecycle` management: control coroutine execution
- Cancellation: stop coroutines gracefully
- Completion tracking: wait for coroutines to finish
- Parent-child relationships: structure concurrency
- Exception handling: manage failures (through propagation rules and `invokeOnCompletion`)

Common operations:
- `job.cancel()`: Cancel the job
- `job.join()`: Wait for completion
- `job.cancelAndJoin()`: Cancel and wait
- `job.isActive`: Check if running
- `job.invokeOnCompletion {}`: Add callback

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия Job от Java-подходов к управлению потоками?
- Когда вы бы использовали Job на практике?
- Каковы распространенные ошибки и подводные камни при работе с Job?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- (см. другие вопросы по корутинам и структурированной конкуррентности в этом разделе)

## Related Questions

- (see other coroutine and structured concurrency questions in this section)

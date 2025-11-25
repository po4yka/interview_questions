---
id: lang-040
title: "What Is Job Object / Что такое объект Job"
aliases: [What Is Job Object, Что такое объект Job]
topic: kotlin
subtopics: [coroutines, lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, c-structured-concurrency]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/medium, job, kotlin]
date created: Saturday, November 1st 2025, 1:01:37 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---

# Вопрос (RU)
> Для чего нужен объект Job?

# Question (EN)
> What is the Job Object for?

## Ответ (RU)

Job — это дескриптор (handle) корутины и элемент иерархии задач в [[c-kotlin]] корутинах ([[c-coroutines]]). Он управляет жизненным циклом корутины и используется для:
- отмены выполнения корутины;
- ожидания завершения;
- координации группы связанных задач (ожидание нескольких корутин, агрегирование);
- управления родительскими и дочерними задачами в рамках структурированной конкуррентности.

Ниже — ключевые сценарии использования, соответствующие приведённым EN-примерам.

### Базовое Использование Job (Basic Job Usage)

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
    job.cancel()  // Отменяем корутину
    println("Job cancelled")
}
```

### Создание Job (Creating a Job)

```kotlin
// Job возвращается из launch
val job1 = CoroutineScope(Dispatchers.Default).launch {
    // Работа
}

// Явное создание Job
val job2 = Job()
val scope = CoroutineScope(job2 + Dispatchers.Default)

// Job из async
val deferred = CoroutineScope(Dispatchers.Default).async {
    // Работа
}
val job3: Job = deferred  // Deferred является Job
```

### Отмена С Помощью Job (Cancelling with Job)

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
    job.cancel()  // Запрашиваем отмену
    job.join()    // Ждем завершения отмены

    // Или cancelAndJoin(), чтобы совместить отмену и ожидание
    // job.cancelAndJoin()
}
```

### Ожидание Завершения (Waiting for Completion)

```kotlin
fun joinExample() = runBlocking {
    val job = launch {
        delay(1000)
        println("Job done")
    }

    println("Waiting...")
    job.join()  // Ждем завершения
    println("Job finished")
}

// Вывод:
// Waiting...
// Job done
// Job finished
```

### Состояния Job (Job States)

```kotlin
fun jobStates() = runBlocking {
    val job = launch {
        delay(1000)
    }

    println("isActive: ${job.isActive}")       // true (пока корутина выполняется)
    println("isCompleted: ${job.isCompleted}") // false
    println("isCancelled: ${job.isCancelled}") // false

    job.cancel()

    println("isActive: ${job.isActive}")       // false
    println("isCompleted: ${job.isCompleted}") // true (завершено через отмену)
    println("isCancelled: ${job.isCancelled}") // true
}
```

### Отношения родитель–потомок (Parent-Child Job Relationships)

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
        // Родительская корутина не завершится, пока не завершатся все дети
    }

    parentJob.join()
    println("Parent done")  // Ждем всех детей
}

// Отмена родителя отменяет всех детей
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
    parent.cancel()  // Отменяет родителя и обоих детей
}
```

### SupervisorJob

```kotlin
// Обычный Job: сбой одного дочернего отменяет всех детей этого scope
fun regularJobFailure() = runBlocking {
    val job = Job()
    val scope = CoroutineScope(job)

    scope.launch {
        delay(100)
        throw Exception("Child 1 failed")
    }

    scope.launch {
        delay(200)
        println("Child 2")  // Не будет напечатано — отменено из-за сбоя соседа
    }

    delay(500)
}

// SupervisorJob: дети независимы по сбоям; отмена супервизора по-прежнему гасит всех
fun supervisorJobExample() = runBlocking {
    val supervisorJob = SupervisorJob()
    val scope = CoroutineScope(supervisorJob)

    scope.launch {
        delay(100)
        throw Exception("Child 1 failed")
    }

    scope.launch {
        delay(200)
        println("Child 2")  // Будет напечатано — не отменяется из-за сбоя соседа
    }

    delay(500)
}
```

### Job И CoroutineScope (Job with CoroutineScope)

```kotlin
class MyManager {
    private val job = Job()
    private val scope = CoroutineScope(job + Dispatchers.Default)

    fun startWork() {
        scope.launch {
            // Работа привязана к жизненному циклу job
            performTask()
        }
    }

    fun stopWork() {
        job.cancel()  // Отменяет все корутины в scope
    }
}
```

### Комбинирование Job (Combining Jobs)

```kotlin
fun combiningJobs() = runBlocking {
    val job1 = launch { delay(1000); println("Job 1") }
    val job2 = launch { delay(2000); println("Job 2") }
    val job3 = launch { delay(3000); println("Job 3") }

    // Ждем все
    joinAll(job1, job2, job3)
    println("All jobs done")
}

// Отмена всех Job
fun cancelAllJobs() = runBlocking {
    val jobs = List(5) { i ->
        launch {
            repeat(10) { println("Job $i"); delay(200) }
        }
    }

    delay(500)
    jobs.forEach { it.cancel() }  // Отменяем все
}
```

### Колбэки Job И Обработка Исключений (Job Callbacks)

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

// Колбэк при отмене
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

### Реальный Пример: Менеджер Загрузок (Real-World Example: Download Manager)

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

### Иерархия Job (Job Hierarchy)

```kotlin
fun jobHierarchy() = runBlocking {
    val grandparent = Job()
    val parent = Job(grandparent)  // Ручная привязка дочернего Job к родителю
    val child = Job(parent)        // Дочерний по отношению к parent

    // Отмена grandparent отменяет всех потомков
    grandparent.cancel()

    println("Grandparent cancelled: ${grandparent.isCancelled}")  // true
    println("Parent cancelled: ${parent.isCancelled}")            // true
    println("Child cancelled: ${child.isCancelled}")              // true
}
```

### Рекомендации (Best Practices)

```kotlin
class JobBestPractices {
    // DO: хранить Job для управления жизненным циклом
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

    // DO: использовать cancelAndJoin для корректного завершения
    suspend fun goodShutdown(job: Job) {
        job.cancelAndJoin()  // Отмена и ожидание
        println("Clean shutdown complete")
    }

    // DON'T: использовать GlobalScope для долгоживущей работы без контроля
    class BadManager {
        fun start() {
            GlobalScope.launch {
                // Долгая работа, не привязанная к жизненному циклу компонента
                infiniteWork()
            }
        }
        // Риск утечек ресурсов и работы, переживающей компонент
    }

    // DON'T: игнорировать завершение, когда нужен детерминированный результат
    fun badExample() = runBlocking {
        launch {
            // Долгая работа
        }
        // Не ждет — выполнение может завершиться до окончания работы
    }
}
```

### Итог (Summary)

Job предоставляет:
- управление жизненным циклом корутин;
- контролируемую отмену;
- отслеживание завершения (`join`, `cancelAndJoin`);
- иерархию родитель–потомок и правила распространения отмены/исключений;
- возможность навесить колбэки `invokeOnCompletion`.

Часто используемые операции:
- `job.cancel()` — запросить отмену;
- `job.join()` — дождаться завершения;
- `job.cancelAndJoin()` — отменить и дождаться завершения;
- `job.isActive` — проверить, выполняется ли еще;
- `job.invokeOnCompletion {}` — выполнить действия по завершении/ошибке.

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
- Lifecycle management: control coroutine execution
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

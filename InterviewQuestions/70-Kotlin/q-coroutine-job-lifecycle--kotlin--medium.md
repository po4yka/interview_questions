---
id: kotlin-241
title: "What is a Job and its lifecycle in Kotlin coroutines? / Job и его жизненный цикл"
aliases: [Job Lifecycle, Job и его жизненный цикл]
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
question_kind: theory
status: draft
created: "2025-10-12"
updated: "2025-10-31"
tags: ["kotlin", "coroutines", "job", "lifecycle", "cancellation", "difficulty/medium"]
description: "A comprehensive guide to understanding Job and its lifecycle states in Kotlin coroutines, including parent-child relationships and cancellation mechanisms"
moc: moc-kotlin
related: [q-kotlin-properties--kotlin--easy, q-property-delegates--kotlin--medium, q-coroutine-context-explained--kotlin--medium]
subtopics: [coroutines, lifecycle]
---
# What is a Job and its lifecycle in Kotlin coroutines?

## English

### Problem Statement

Understanding the Job interface and its lifecycle is fundamental to working effectively with Kotlin coroutines. A Job represents a cancellable task with a lifecycle, and it's one of the key elements of CoroutineContext. What are the different states a Job can be in, and how do parent-child relationships work?

### Solution

A **Job** is a cancellable thing with a lifecycle that culminates in its completion. It's a core component of structured concurrency in Kotlin coroutines.

#### Job States

A Job goes through several states during its lifecycle:

```kotlin
import kotlinx.coroutines.*

fun demonstrateJobStates() = runBlocking {
    // State 1: NEW (optional, only for lazy coroutines)
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("Lazy job started")
        delay(1000)
    }

    println("Lazy job state: isActive=${lazyJob.isActive}, " +
            "isCompleted=${lazyJob.isCompleted}, " +
            "isCancelled=${lazyJob.isCancelled}") // false, false, false

    // State 2: ACTIVE (after start)
    lazyJob.start()
    println("After start: isActive=${lazyJob.isActive}, " +
            "isCompleted=${lazyJob.isCompleted}") // true, false

    // State 3: COMPLETING (when body finishes, waiting for children)
    val parentJob = launch {
        val childJob = launch {
            delay(2000)
            println("Child completed")
        }
        println("Parent body finished")
        // Parent is now COMPLETING, waiting for child
    }

    delay(100)
    println("Parent completing: isActive=${parentJob.isActive}, " +
            "isCompleted=${parentJob.isCompleted}") // true, false

    // State 4: COMPLETED
    parentJob.join()
    println("Parent completed: isActive=${parentJob.isActive}, " +
            "isCompleted=${parentJob.isCompleted}") // false, true

    // State 5: CANCELLING
    val cancellingJob = launch {
        try {
            delay(5000)
        } finally {
            println("Cleanup in finally")
            delay(500) // Can still suspend during cleanup
            println("Cleanup complete")
        }
    }

    delay(100)
    cancellingJob.cancel()
    println("After cancel: isActive=${cancellingJob.isActive}, " +
            "isCancelled=${cancellingJob.isCancelled}") // false, true

    // State 6: CANCELLED
    cancellingJob.join()
    println("Fully cancelled: isCompleted=${cancellingJob.isCompleted}") // true
}
```

#### Complete State Diagram

```kotlin
import kotlinx.coroutines.*

/**
 * Job State Transitions:
 *
 * NEW (lazy only)
 *   |
 *   v (start/join)
 * ACTIVE
 *   |
 *   v (body completes)
 * COMPLETING (waiting for children)
 *   |
 *   v (all children complete)
 * COMPLETED
 *
 * Any state can transition to:
 * CANCELLING (cancel called)
 *   |
 *   v (cleanup completes)
 * CANCELLED
 */

data class JobState(
    val isNew: Boolean,
    val isActive: Boolean,
    val isCompleting: Boolean,
    val isCompleted: Boolean,
    val isCancelled: Boolean
)

fun Job.getDetailedState(): String {
    return when {
        !isActive && !isCompleted && !isCancelled -> "NEW"
        isActive && !isCompleted && !isCancelled -> "ACTIVE or COMPLETING"
        !isActive && isCompleted && !isCancelled -> "COMPLETED"
        !isActive && isCancelled -> "CANCELLING or CANCELLED"
        else -> "UNKNOWN"
    }
}
```

#### Creating and Managing Jobs

```kotlin
import kotlinx.coroutines.*

fun jobCreationExamples() = runBlocking {
    // 1. Job from coroutine builder
    val job1 = launch {
        delay(1000)
        println("Job from launch")
    }

    // 2. Standalone Job
    val job2 = Job()
    launch(job2) {
        delay(1000)
        println("Job with explicit parent")
    }

    // 3. Job from CoroutineScope
    val scope = CoroutineScope(Dispatchers.Default)
    val job3 = scope.launch {
        delay(1000)
        println("Job from scope")
    }

    // 4. Getting current Job
    val job4 = launch {
        val currentJob = coroutineContext[Job]
        println("Current job: $currentJob")
    }

    // Wait for all
    joinAll(job1, job2, job3, job4)
    scope.cancel()
}
```

#### Parent-Child Relationships

```kotlin
import kotlinx.coroutines.*

fun parentChildRelationships() = runBlocking {
    println("=== Parent-Child Relationships ===")

    // 1. Automatic parent-child relationship
    val parent = launch {
        println("Parent started")

        val child1 = launch {
            delay(1000)
            println("Child 1 completed")
        }

        val child2 = launch {
            delay(1500)
            println("Child 2 completed")
        }

        println("Parent body finished, but waiting for children")
    }

    delay(500)
    println("Parent state: ${parent.isActive}, ${parent.isCompleted}")

    parent.join() // Waits for parent AND all children
    println("Parent and all children completed")

    // 2. Manual parent specification
    val manualParent = Job()

    launch(manualParent) {
        delay(500)
        println("Manual child 1")
    }

    launch(manualParent) {
        delay(1000)
        println("Manual child 2")
    }

    manualParent.children.forEach { child ->
        println("Child: $child")
    }

    manualParent.complete() // Complete the parent
    manualParent.join() // Wait for all children
}
```

#### Cancellation Propagation

```kotlin
import kotlinx.coroutines.*

fun cancellationPropagation() = runBlocking {
    println("=== Cancellation Propagation ===")

    // Parent cancellation cancels all children
    val parent = launch {
        val child1 = launch {
            try {
                delay(2000)
                println("Child 1 completed")
            } catch (e: CancellationException) {
                println("Child 1 cancelled")
            }
        }

        val child2 = launch {
            try {
                delay(3000)
                println("Child 2 completed")
            } catch (e: CancellationException) {
                println("Child 2 cancelled")
            }
        }

        delay(5000)
    }

    delay(500)
    parent.cancel() // Cancels parent and all children
    parent.join()

    println("\n=== Child Failure Cancels Parent ===")

    // Child failure cancels parent and siblings
    val parent2 = launch {
        launch {
            delay(500)
            throw RuntimeException("Child failed!")
        }

        launch {
            try {
                delay(2000)
                println("Sibling completed")
            } catch (e: CancellationException) {
                println("Sibling cancelled due to parent cancellation")
            }
        }

        try {
            delay(3000)
        } catch (e: CancellationException) {
            println("Parent cancelled due to child failure")
        }
    }

    delay(1000)
    println("Parent2 cancelled: ${parent2.isCancelled}")
}
```

#### Job Completion and Waiting

```kotlin
import kotlinx.coroutines.*

fun jobCompletionExamples() = runBlocking {
    // 1. join() - suspends until completion
    val job1 = launch {
        delay(1000)
        println("Job 1 completed")
    }
    job1.join() // Suspends until job1 completes

    // 2. joinAll() - wait for multiple jobs
    val jobs = List(5) { index ->
        launch {
            delay(1000L * index)
            println("Job $index completed")
        }
    }
    joinAll(*jobs.toTypedArray())

    // 3. Job.complete() - manual completion
    val manualJob = Job()
    launch(manualJob) {
        delay(500)
        println("Child completed")
    }
    manualJob.complete() // No new children can be attached
    manualJob.join() // Wait for existing children

    // 4. Job.completeExceptionally() - complete with exception
    val failingJob = Job()
    launch(failingJob) {
        try {
            delay(1000)
        } catch (e: CancellationException) {
            println("Cancelled due to exceptional completion")
        }
    }
    failingJob.completeExceptionally(RuntimeException("Failed"))

    // 5. invokeOnCompletion - callback on completion
    val job2 = launch {
        delay(1000)
        println("Job 2 work done")
    }

    job2.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Job completed successfully")
            is CancellationException -> println("Job was cancelled")
            else -> println("Job failed with $cause")
        }
    }

    job2.join()
}
```

#### Job Hierarchy and Inspection

```kotlin
import kotlinx.coroutines.*

fun jobHierarchyInspection() = runBlocking {
    val grandparent = launch {
        println("Grandparent: ${coroutineContext[Job]}")

        val parent = launch {
            println("Parent: ${coroutineContext[Job]}")
            println("Parent's parent: ${coroutineContext[Job]?.parent}")

            val child = launch {
                println("Child: ${coroutineContext[Job]}")
                println("Child's parent: ${coroutineContext[Job]?.parent}")

                delay(1000)
            }

            delay(500)
        }

        delay(100)

        // Inspect children
        val children = coroutineContext[Job]?.children?.toList()
        println("Grandparent has ${children?.size} children")

        delay(2000)
    }

    grandparent.join()
}
```

#### Practical Job Patterns

```kotlin
import kotlinx.coroutines.*

// Pattern 1: Timeout with Job
suspend fun <T> withTimeoutJob(timeMillis: Long, block: suspend () -> T): T {
    val job = Job()
    return try {
        coroutineScope {
            launch(job) {
                delay(timeMillis)
                job.cancel()
            }
            block()
        }
    } finally {
        job.cancel()
    }
}

// Pattern 2: Cancellable Resource
class CancellableResource {
    private val job = Job()

    fun doWork() {
        CoroutineScope(Dispatchers.Default + job).launch {
            while (isActive) {
                println("Working...")
                delay(500)
            }
        }
    }

    fun cancel() {
        job.cancel()
    }
}

// Pattern 3: Job as lifecycle manager
class ViewModel {
    private val viewModelJob = SupervisorJob()
    private val viewModelScope = CoroutineScope(Dispatchers.Main + viewModelJob)

    fun loadData() {
        viewModelScope.launch {
            // Load data
        }
    }

    fun onCleared() {
        viewModelJob.cancel()
    }
}

// Pattern 4: Joining with timeout
suspend fun Job.joinOrTimeout(timeoutMillis: Long): Boolean {
    return try {
        withTimeout(timeoutMillis) {
            join()
        }
        true
    } catch (e: TimeoutCancellationException) {
        false
    }
}

fun demonstrateJobPatterns() = runBlocking {
    // Using CancellableResource
    val resource = CancellableResource()
    resource.doWork()
    delay(2000)
    resource.cancel()

    // Using joinOrTimeout
    val longRunningJob = launch {
        delay(5000)
    }

    val completed = longRunningJob.joinOrTimeout(1000)
    println("Job completed in time: $completed")
    longRunningJob.cancel()
}
```

#### Job Exceptions and Error Handling

```kotlin
import kotlinx.coroutines.*

fun jobExceptionHandling() = runBlocking {
    // 1. Exception in job cancels it
    val failingJob = launch {
        throw RuntimeException("Job failed!")
    }

    delay(100)
    println("Failing job cancelled: ${failingJob.isCancelled}")

    // 2. CancellationException doesn't cancel parent
    val parent = launch {
        val child = launch {
            throw CancellationException("Explicit cancellation")
        }

        delay(1000)
        println("Parent survived child cancellation")
    }

    parent.join()

    // 3. Other exceptions cancel parent
    val parent2 = launch(SupervisorJob()) { // Use SupervisorJob to prevent crash
        launch {
            throw RuntimeException("This would cancel parent")
        }
    }

    delay(100)

    // 4. invokeOnCompletion distinguishes exceptions
    val job = launch {
        throw RuntimeException("Failed")
    }

    job.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Normal completion")
            is CancellationException -> println("Cancelled")
            else -> println("Failed with exception: $cause")
        }
    }

    delay(100)
}
```

#### Testing Job Lifecycle

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*

class JobLifecycleTest {
    @Test
    fun testJobStates() = runTest {
        val job = launch(start = CoroutineStart.LAZY) {
            delay(1000)
        }

        // NEW state
        assertFalse(job.isActive)
        assertFalse(job.isCompleted)

        // ACTIVE state
        job.start()
        assertTrue(job.isActive)
        assertFalse(job.isCompleted)

        // COMPLETED state
        job.join()
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
    }

    @Test
    fun testCancellation() = runTest {
        val job = launch {
            try {
                delay(10000)
            } finally {
                println("Cleanup")
            }
        }

        advanceTimeBy(100)
        job.cancel()

        assertTrue(job.isCancelled)
        job.join()
        assertTrue(job.isCompleted)
    }

    @Test
    fun testParentChildCancellation() = runTest {
        val parent = launch {
            launch {
                delay(10000)
            }
        }

        advanceTimeBy(100)
        parent.cancel()
        parent.join()

        assertTrue(parent.isCancelled)
    }
}
```

### Best Practices

1. **Don't create unnecessary Jobs**
   ```kotlin
   // Bad
   val job = Job()
   launch(job) { }

   // Good - let coroutine builder create it
   val job = launch { }
   ```

2. **Use invokeOnCompletion for cleanup**
   ```kotlin
   val job = launch {
       // work
   }

   job.invokeOnCompletion { cause ->
       // cleanup regardless of success or failure
   }
   ```

3. **Check isActive in loops**
   ```kotlin
   launch {
       while (isActive) {
           // work that can be cancelled
           doWork()
       }
   }
   ```

4. **Use SupervisorJob when appropriate**
   ```kotlin
   val scope = CoroutineScope(SupervisorJob())
   // Children don't cancel each other
   ```

5. **Don't swallow CancellationException**
   ```kotlin
   // Bad
   try {
       delay(1000)
   } catch (e: Exception) {
       // This catches CancellationException!
   }

   // Good
   try {
       delay(1000)
   } catch (e: CancellationException) {
       throw e // Re-throw
   } catch (e: Exception) {
       // Handle other exceptions
   }
   ```

### Common Pitfalls

1. **Forgetting about COMPLETING state**
   ```kotlin
   val job = launch {
       launch { delay(5000) }
       println("Parent finished") // But not COMPLETED yet!
   }
   // job is COMPLETING, not COMPLETED
   ```

2. **Not waiting for children**
   ```kotlin
   // Bad
   fun loadData() = runBlocking {
       launch { /* child work */ }
       // Returns before child completes!
   }

   // Good
   suspend fun loadData() = coroutineScope {
       launch { /* child work */ }
       // Waits for all children
   }
   ```

3. **Creating Job without attaching work**
   ```kotlin
   // This Job will never complete!
   val job = Job()
   // Need to call job.complete() manually
   ```

### Edge Cases

```kotlin
import kotlinx.coroutines.*

fun jobEdgeCases() = runBlocking {
    // 1. Empty job completes immediately
    val emptyJob = launch { }
    emptyJob.join() // Returns immediately

    // 2. Cancelled job before start
    val job = launch(start = CoroutineStart.LAZY) {
        println("Never executed")
    }
    job.cancel()
    // job is cancelled without ever being active

    // 3. Multiple invokeOnCompletion
    val job2 = launch { delay(100) }
    job2.invokeOnCompletion { println("First") }
    job2.invokeOnCompletion { println("Second") }
    // Both are called

    // 4. Join on completed job
    val job3 = launch { delay(100) }
    job3.join()
    job3.join() // Returns immediately

    // 5. Cancel completed job
    val job4 = launch { delay(100) }
    job4.join()
    job4.cancel() // No effect
}
```

---

## Русский

### Описание проблемы

Понимание интерфейса Job и его жизненного цикла является фундаментальным для эффективной работы с корутинами Kotlin. Job представляет отменяемую задачу с жизненным циклом, который завершается её выполнением. Это один из ключевых элементов CoroutineContext. Какие существуют состояния Job, и как работают отношения родитель-потомок?

### Решение

**Job** - это отменяемая сущность с жизненным циклом, который завершается её выполнением. Это основной компонент структурированного параллелизма в корутинах Kotlin.

#### Состояния Job

Job проходит через несколько состояний в течение своего жизненного цикла:

```kotlin
import kotlinx.coroutines.*

fun demonstrateJobStates() = runBlocking {
    // Состояние 1: NEW (опционально, только для ленивых корутин)
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("Ленивая задача запущена")
        delay(1000)
    }

    println("Состояние ленивой задачи: isActive=${lazyJob.isActive}, " +
            "isCompleted=${lazyJob.isCompleted}, " +
            "isCancelled=${lazyJob.isCancelled}") // false, false, false

    // Состояние 2: ACTIVE (после запуска)
    lazyJob.start()
    println("После запуска: isActive=${lazyJob.isActive}, " +
            "isCompleted=${lazyJob.isCompleted}") // true, false

    // Состояние 3: COMPLETING (когда тело завершилось, ожидание потомков)
    val parentJob = launch {
        val childJob = launch {
            delay(2000)
            println("Потомок завершён")
        }
        println("Тело родителя завершено")
        // Родитель теперь в COMPLETING, ожидает потомка
    }

    delay(100)
    println("Родитель завершается: isActive=${parentJob.isActive}, " +
            "isCompleted=${parentJob.isCompleted}") // true, false

    // Состояние 4: COMPLETED
    parentJob.join()
    println("Родитель завершён: isActive=${parentJob.isActive}, " +
            "isCompleted=${parentJob.isCompleted}") // false, true

    // Состояние 5: CANCELLING
    val cancellingJob = launch {
        try {
            delay(5000)
        } finally {
            println("Очистка в finally")
            delay(500) // Можно приостанавливаться во время очистки
            println("Очистка завершена")
        }
    }

    delay(100)
    cancellingJob.cancel()
    println("После отмены: isActive=${cancellingJob.isActive}, " +
            "isCancelled=${cancellingJob.isCancelled}") // false, true

    // Состояние 6: CANCELLED
    cancellingJob.join()
    println("Полностью отменена: isCompleted=${cancellingJob.isCompleted}") // true
}
```

#### Полная диаграмма состояний

```kotlin
import kotlinx.coroutines.*

/**
 * Переходы состояний Job:
 *
 * NEW (только для ленивых)
 *   |
 *   v (start/join)
 * ACTIVE
 *   |
 *   v (тело завершено)
 * COMPLETING (ожидание потомков)
 *   |
 *   v (все потомки завершены)
 * COMPLETED
 *
 * Из любого состояния можно перейти в:
 * CANCELLING (вызван cancel)
 *   |
 *   v (очистка завершена)
 * CANCELLED
 */

data class JobState(
    val isNew: Boolean,
    val isActive: Boolean,
    val isCompleting: Boolean,
    val isCompleted: Boolean,
    val isCancelled: Boolean
)

fun Job.getDetailedState(): String {
    return when {
        !isActive && !isCompleted && !isCancelled -> "NEW"
        isActive && !isCompleted && !isCancelled -> "ACTIVE или COMPLETING"
        !isActive && isCompleted && !isCancelled -> "COMPLETED"
        !isActive && isCancelled -> "CANCELLING или CANCELLED"
        else -> "UNKNOWN"
    }
}
```

[Продолжение следует с полным переводом всех разделов...]

### Лучшие практики

1. **Не создавайте ненужные Job**
2. **Используйте invokeOnCompletion для очистки**
3. **Проверяйте isActive в циклах**
4. **Используйте SupervisorJob когда уместно**
5. **Не перехватывайте CancellationException**

### Распространённые ошибки

1. Забывание о состоянии COMPLETING
2. Не ожидание завершения потомков
3. Создание Job без привязки работы

---

## Follow-ups

1. How does SupervisorJob differ from a regular Job in terms of child failure handling?
2. What happens to a Job when its parent is cancelled while it's in the COMPLETING state?
3. How can you prevent a coroutine from being cancelled during critical cleanup operations?
4. What's the difference between Job.cancel() and Job.cancelAndJoin()?
5. How do Job and Deferred relate to each other?
6. Can a Job transition from CANCELLED back to ACTIVE?
7. How does NonCancellable context affect Job lifecycle?
8. What's the impact of using Job() as a parent vs using coroutineScope for parent-child relationships?

## References

- [Kotlin Coroutines Guide - Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Job - kotlinx.coroutines API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-job/)
- [Roman Elizarov - Structured Concurrency](https://medium.com/@elizarov/structured-concurrency-722d765aa952)
- [Coroutines Guide - Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)

## Related Questions

- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]]
- [[q-coroutine-parent-child-relationship--kotlin--medium]]
- [[q-coroutine-context-elements--kotlin--hard]]
- [[q-coroutine-builders-comparison--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-cancellation--kotlin--medium]]

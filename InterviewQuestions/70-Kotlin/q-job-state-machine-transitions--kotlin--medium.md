---
id: kotlin-105
title: "Job state machine and state transitions / Job машина состояний и переходы"
aliases: [Job, Machine, State, Transitions]
topic: kotlin
subtopics: []
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-fan-in-fan-out--kotlin--hard, q-inline-function-limitations--kotlin--medium, q-list-set-map-differences--programming-languages--easy]
created: 2025-10-12
updated: 2025-10-12
tags: [difficulty/medium]
---

# Job State Machine and State Transitions / Job Машина Состояний И Переходы

## English

### Overview

The Kotlin coroutines `Job` is a state machine with 6 distinct states. Understanding these states, their transitions, and the behavior of `isActive`, `isCompleted`, and `isCancelled` properties is critical for mastering coroutine lifecycle management, debugging, and preventing common bugs.

This question explores the complete state machine, valid transitions, property behavior in each state, parent-child propagation rules, and how `join()` and `cancel()` interact with different states.

### The 6 Job States

A `Job` can be in one of the following states:

1. **New** (only for `CoroutineStart.LAZY`)
2. **Active** (normal execution)
3. **Completing** (body finished, waiting for children)
4. **Completed** (fully finished)
5. **Cancelling** (cancellation in progress, running finally blocks)
6. **Cancelled** (terminal cancelled state)

### State Properties Behavior

| State | isActive | isCompleted | isCancelled |
|-------|----------|-------------|-------------|
| **New** | false | false | false |
| **Active** | true | false | false |
| **Completing** | true | false | false |
| **Completed** | false | true | false |
| **Cancelling** | false | false | true |
| **Cancelled** | false | true | true |

### State Transition Diagram (Text-Based)

```

                           New      (LAZY only)
                        (initial)

                              start()


            Active
                      (executing)


                             body done


                      Completing
                     (wait kids)


                             all children
                             complete


                       Completed
                       (success)


           cancel()




                Cancelling
               (finally,
                wait kids)   children done


                       finally done


                 Cancelled
                (terminal)

```

### State 1: New (CoroutineStart.LAZY only)

The **New** state exists only for coroutines started with `CoroutineStart.LAZY`. The coroutine is created but not started yet.

**Properties:**
- `isActive = false`
- `isCompleted = false`
- `isCancelled = false`

**Transitions:**
- To **Active**: calling `start()` or `join()`
- To **Cancelling**: calling `cancel()` before starting

```kotlin
import kotlinx.coroutines.*

fun demonstrateNewState() = runBlocking {
    println("=== New State Demo ===")

    val job = launch(start = CoroutineStart.LAZY) {
        println("Coroutine body executing")
        delay(100)
    }

    // In New state
    println("After creation:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false
    println("  isCancelled: ${job.isCancelled}")   // false

    delay(50) // Wait a bit

    println("\nAfter 50ms (still not started):")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false

    // Transition to Active
    job.start()
    println("\nAfter start():")
    println("  isActive: ${job.isActive}")         // true
    println("  isCompleted: ${job.isCompleted}")   // false

    job.join()
    println("\nAfter completion:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
}
```

**Output:**
```
=== New State Demo ===
After creation:
  isActive: false
  isCompleted: false
  isCancelled: false

After 50ms (still not started):
  isActive: false
  isCompleted: false

After start():
  isActive: true
  isCompleted: false
Coroutine body executing

After completion:
  isActive: false
  isCompleted: true
```

### State 2: Active (Normal Execution)

The **Active** state means the coroutine is currently executing. This is the normal working state.

**Properties:**
- `isActive = true`
- `isCompleted = false`
- `isCancelled = false`

**Transitions:**
- To **Completing**: body finishes normally
- To **Cancelling**: `cancel()` called

```kotlin
import kotlinx.coroutines.*

fun demonstrateActiveState() = runBlocking {
    println("=== Active State Demo ===")

    val job = launch {
        println("Starting execution")
        println("  isActive: ${coroutineContext[Job]?.isActive}")       // true
        println("  isCompleted: ${coroutineContext[Job]?.isCompleted}") // false

        repeat(3) { i ->
            delay(100)
            println("Iteration $i - still active: ${coroutineContext[Job]?.isActive}")
        }

        println("Body finished")
    }

    delay(50)
    println("\nFrom parent scope:")
    println("  isActive: ${job.isActive}")         // true
    println("  isCompleted: ${job.isCompleted}")   // false

    job.join()
    println("\nAfter join:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
}
```

### State 3: Completing (Waiting for Children)

The **Completing** state occurs when the coroutine body has finished, but it still has active children. The parent waits for all children to complete before transitioning to **Completed**.

**Properties:**
- `isActive = true` (still considered active!)
- `isCompleted = false`
- `isCancelled = false`

**Key Insight:** `isActive` remains `true` during the Completing state because the job is not yet fully done.

```kotlin
import kotlinx.coroutines.*

fun demonstrateCompletingState() = runBlocking {
    println("=== Completing State Demo ===")

    val parentJob = launch {
        println("Parent body started")

        // Launch child coroutines
        launch {
            println("  Child 1 started")
            delay(200)
            println("  Child 1 finished")
        }

        launch {
            println("  Child 2 started")
            delay(400)
            println("  Child 2 finished")
        }

        println("Parent body finished (but children still running)")
        // Parent enters Completing state here
    }

    delay(250) // Parent body done, child 1 done, child 2 still running

    println("\nParent in Completing state:")
    println("  isActive: ${parentJob.isActive}")       // true (!)
    println("  isCompleted: ${parentJob.isCompleted}") // false
    println("  isCancelled: ${parentJob.isCancelled}") // false

    parentJob.join() // Wait for child 2 to finish

    println("\nAfter all children complete:")
    println("  isActive: ${parentJob.isActive}")       // false
    println("  isCompleted: ${parentJob.isCompleted}") // true
}
```

**Output:**
```
=== Completing State Demo ===
Parent body started
  Child 1 started
  Child 2 started
Parent body finished (but children still running)
  Child 1 finished

Parent in Completing state:
  isActive: true
  isCompleted: false
  isCancelled: false
  Child 2 finished

After all children complete:
  isActive: false
  isCompleted: true
```

### State 4: Completed (Success)

The **Completed** state is a terminal state indicating successful completion. The coroutine body finished, all children completed, and no cancellation occurred.

**Properties:**
- `isActive = false`
- `isCompleted = true`
- `isCancelled = false`

**Transitions:** None (terminal state)

```kotlin
import kotlinx.coroutines.*

fun demonstrateCompletedState() = runBlocking {
    println("=== Completed State Demo ===")

    val job = launch {
        println("Doing work...")
        delay(100)
        println("Work done!")
    }

    job.join()

    println("\nJob in Completed state:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // false

    // join() on completed job returns immediately
    println("\nCalling join() again...")
    job.join()
    println("join() returned immediately")

    // cancel() on completed job has no effect
    println("\nCalling cancel()...")
    job.cancel()
    println("cancel() had no effect (already completed)")
    println("  isCancelled: ${job.isCancelled}")   // false (still!)
}
```

### State 5: Cancelling (Running Finally Blocks)

The **Cancelling** state occurs when cancellation is in progress. The coroutine is running `finally` blocks, and waiting for children to be cancelled.

**Properties:**
- `isActive = false`
- `isCompleted = false`
- `isCancelled = true`

**Transitions:**
- To **Cancelled**: finally blocks done, children cancelled

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancellingState() = runBlocking {
    println("=== Cancelling State Demo ===")

    val job = launch {
        try {
            println("Starting work...")
            repeat(5) { i ->
                println("  Iteration $i")
                delay(100)
            }
        } finally {
            println("Finally block started")
            println("  isActive: ${coroutineContext[Job]?.isActive}")     // false
            println("  isCancelled: ${coroutineContext[Job]?.isCancelled}") // true

            // Cleanup work (non-suspending)
            println("  Cleaning up resources...")
            Thread.sleep(150) // Simulate cleanup
            println("  Cleanup done")

            println("Finally block finished")
        }
    }

    delay(250) // Let it run for a bit

    println("\nCancelling job...")
    job.cancel()

    // Job might briefly be in Cancelling state
    println("Job in Cancelling state:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false (!)
    println("  isCancelled: ${job.isCancelled}")   // true

    job.join() // Wait for cancellation to complete

    println("\nAfter cancellation complete:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // true
}
```

**Output:**
```
=== Cancelling State Demo ===
Starting work...
  Iteration 0
  Iteration 1
  Iteration 2

Cancelling job...
Job in Cancelling state:
  isActive: false
  isCompleted: false
  isCancelled: true
Finally block started
  isActive: false
  isCancelled: true
  Cleaning up resources...
  Cleanup done
Finally block finished

After cancellation complete:
  isActive: false
  isCompleted: true
  isCancelled: true
```

### State 6: Cancelled (Terminal Cancelled State)

The **Cancelled** state is a terminal state indicating cancellation completed. All finally blocks ran, all children cancelled.

**Properties:**
- `isActive = false`
- `isCompleted = true` (!)
- `isCancelled = true`

**Key Insight:** `isCompleted` is `true` in the Cancelled state because the job has finished (even though it was cancelled).

**Transitions:** None (terminal state)

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancelledState() = runBlocking {
    println("=== Cancelled State Demo ===")

    val job = launch {
        try {
            repeat(10) { i ->
                println("Working... $i")
                delay(100)
            }
        } finally {
            println("Cleanup in finally")
        }
    }

    delay(250)
    job.cancel()
    job.join()

    println("\nJob in Cancelled state:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true (!)
    println("  isCancelled: ${job.isCancelled}")   // true

    // Subsequent operations have no effect
    job.cancel() // No-op
    job.join()   // Returns immediately

    println("\nAfter additional cancel/join:")
    println("  isCompleted: ${job.isCompleted}")   // still true
    println("  isCancelled: ${job.isCancelled}")   // still true
}
```

### Parent-Child State Propagation Rules

Coroutine state propagation follows structured concurrency principles:

1. **Parent cancellation → Children cancellation**
   - When a parent is cancelled, all children are cancelled recursively
   - Children enter Cancelling state

2. **Child failure → Parent cancellation**
   - When a child fails with exception, parent is cancelled (by default)
   - Siblings are also cancelled
   - Use `SupervisorJob` to prevent this

3. **Parent waits for children**
   - Parent enters Completing state after body finishes
   - Transitions to Completed only when all children complete

```kotlin
import kotlinx.coroutines.*

fun demonstrateParentChildPropagation() = runBlocking {
    println("=== Parent-Child Propagation ===")

    val parent = launch {
        println("Parent started")

        val child1 = launch {
            try {
                println("  Child 1 started")
                delay(1000)
                println("  Child 1 finished")
            } finally {
                println("  Child 1 finally (cancelled: ${coroutineContext[Job]?.isCancelled})")
            }
        }

        val child2 = launch {
            try {
                println("  Child 2 started")
                delay(1000)
                println("  Child 2 finished")
            } finally {
                println("  Child 2 finally (cancelled: ${coroutineContext[Job]?.isCancelled})")
            }
        }

        println("Parent body finished (waiting for children)")
    }

    delay(200)
    println("\nCancelling parent...")
    parent.cancel()

    parent.join()

    println("\nAll jobs cancelled")
    println("Parent:")
    println("  isCompleted: ${parent.isCompleted}") // true
    println("  isCancelled: ${parent.isCancelled}") // true
}
```

**Output:**
```
=== Parent-Child Propagation ===
Parent started
  Child 1 started
  Child 2 started
Parent body finished (waiting for children)

Cancelling parent...
  Child 1 finally (cancelled: true)
  Child 2 finally (cancelled: true)

All jobs cancelled
Parent:
  isCompleted: true
  isCancelled: true
```

### join() Behavior in Each State

The `join()` function suspends until the job reaches a terminal state (Completed or Cancelled).

| State | join() Behavior |
|-------|-----------------|
| **New** | Starts the job (if LAZY), then suspends until complete |
| **Active** | Suspends until job completes or is cancelled |
| **Completing** | Suspends until all children complete |
| **Completed** | Returns immediately |
| **Cancelling** | Suspends until cancellation completes |
| **Cancelled** | Returns immediately |

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

fun demonstrateJoinBehavior() = runBlocking {
    println("=== join() Behavior Demo ===")

    // 1. join() on LAZY job starts it
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("Lazy job executing")
        delay(100)
    }

    println("1. join() on LAZY (New state) - starts and waits:")
    val time1 = measureTimeMillis {
        lazyJob.join()
    }
    println("   Took ${time1}ms\n")

    // 2. join() on Active job waits
    val activeJob = launch {
        delay(200)
    }

    delay(50)
    println("2. join() on Active job - waits for completion:")
    val time2 = measureTimeMillis {
        activeJob.join()
    }
    println("   Took ${time2}ms\n")

    // 3. join() on Completed job returns immediately
    val completedJob = launch {
        delay(100)
    }
    completedJob.join()

    println("3. join() on Completed job - immediate return:")
    val time3 = measureTimeMillis {
        completedJob.join()
    }
    println("   Took ${time3}ms\n")

    // 4. join() during Cancelling waits for cleanup
    val cancellingJob = launch {
        try {
            delay(10000)
        } finally {
            println("   Cleanup starting...")
            Thread.sleep(150)
            println("   Cleanup done")
        }
    }

    delay(50)
    cancellingJob.cancel()

    println("4. join() on Cancelling job - waits for finally:")
    val time4 = measureTimeMillis {
        cancellingJob.join()
    }
    println("   Took ${time4}ms")
}
```

### cancel() Behavior in Each State

The `cancel()` function requests cancellation of the job.

| State | cancel() Behavior |
|-------|-------------------|
| **New** | Immediately transitions to Cancelled (no execution) |
| **Active** | Transitions to Cancelling, runs finally blocks |
| **Completing** | Transitions to Cancelling, cancels remaining children |
| **Completed** | No effect (idempotent) |
| **Cancelling** | No effect (already cancelling) |
| **Cancelled** | No effect (idempotent) |

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancelBehavior() = runBlocking {
    println("=== cancel() Behavior Demo ===")

    // 1. cancel() on LAZY job (New state)
    println("1. cancel() on LAZY (New state):")
    val lazyJob = launch(start = CoroutineStart.LAZY) {
        println("   This should not print")
    }
    lazyJob.cancel()
    lazyJob.join()
    println("   Job cancelled without execution")
    println("   isCancelled: ${lazyJob.isCancelled}\n")

    // 2. cancel() on Active job
    println("2. cancel() on Active job:")
    val activeJob = launch {
        try {
            println("   Working...")
            delay(1000)
        } finally {
            println("   Finally block executed")
        }
    }
    delay(50)
    activeJob.cancel()
    activeJob.join()
    println("   Job cancelled and cleaned up\n")

    // 3. cancel() on Completed job
    println("3. cancel() on Completed job:")
    val completedJob = launch {
        delay(50)
    }
    completedJob.join()

    println("   Before cancel: isCancelled=${completedJob.isCancelled}")
    completedJob.cancel()
    println("   After cancel: isCancelled=${completedJob.isCancelled}")
    println("   (No effect - already completed)\n")

    // 4. cancel() multiple times
    println("4. Multiple cancel() calls:")
    val job = launch {
        delay(1000)
    }
    delay(50)

    job.cancel()
    println("   First cancel()")
    job.cancel()
    println("   Second cancel() - no effect")
    job.cancel()
    println("   Third cancel() - no effect")

    job.join()
    println("   All cancels completed")
}
```

### invokeOnCompletion for State Notifications

Use `invokeOnCompletion` to be notified when a job reaches a terminal state.

```kotlin
import kotlinx.coroutines.*

fun demonstrateInvokeOnCompletion() = runBlocking {
    println("=== invokeOnCompletion Demo ===")

    val job = launch {
        println("Job started")
        delay(200)
        println("Job finished")
    }

    // Register completion handler
    job.invokeOnCompletion { cause ->
        when (cause) {
            null -> println("Completed successfully")
            is CancellationException -> println("Cancelled: ${cause.message}")
            else -> println("Failed: ${cause.message}")
        }
    }

    delay(100)
    println("Job is active: ${job.isActive}")

    job.join()

    println("\n--- Cancellation Case ---")

    val cancelledJob = launch {
        try {
            delay(1000)
        } finally {
            println("Cleanup")
        }
    }

    cancelledJob.invokeOnCompletion { cause ->
        println("Completion handler: cause=$cause")
        println("  isCancelled: ${cancelledJob.isCancelled}")
        println("  isCompleted: ${cancelledJob.isCompleted}")
    }

    delay(50)
    cancelledJob.cancel("User requested cancellation")
    cancelledJob.join()
}
```

**Output:**
```
=== invokeOnCompletion Demo ===
Job started
Job is active: true
Job finished
Completed successfully

--- Cancellation Case ---
Cleanup
Completion handler: cause=kotlinx.coroutines.JobCancellationException: User requested cancellation
  isCancelled: true
  isCompleted: true
```

### Impossible State Transitions

Certain transitions are impossible in the Job state machine:

1. **Cannot go from Completed to Active** - terminal state
2. **Cannot go from Cancelled to Active** - terminal state
3. **Cannot go from Completing to New** - forward-only
4. **Cannot skip Cancelling** - must run finally blocks
5. **Cannot have Cancelled without Completing/Cancelling first**

```kotlin
import kotlinx.coroutines.*

fun demonstrateImpossibleTransitions() = runBlocking {
    println("=== Impossible Transitions Demo ===")

    // 1. Cannot restart completed job
    val completedJob = launch {
        delay(50)
    }
    completedJob.join()

    println("1. Completed job:")
    println("   isCompleted: ${completedJob.isCompleted}")

    // No way to restart or reactivate
    // completedJob.start() // Would have no effect

    delay(100)
    println("   Still completed: ${completedJob.isCompleted}")
    println("   Cannot transition back to Active\n")

    // 2. Cannot skip finally blocks
    var finallyExecuted = false
    val job = launch {
        try {
            delay(1000)
        } finally {
            finallyExecuted = true
            println("2. Finally executed during cancellation")
        }
    }

    delay(50)
    job.cancel()
    job.join()

    println("   finallyExecuted: $finallyExecuted")
    println("   Cancelling state is mandatory\n")

    // 3. Cannot have partial completion
    val parentJob = launch {
        launch {
            delay(100)
        }
        // Parent must wait for child
        println("3. Parent body done, but not completed yet")
    }

    delay(50)
    println("   Parent isCompleted: ${parentJob.isCompleted}") // false

    delay(100)
    println("   After child done, parent isCompleted: ${parentJob.isCompleted}") // true
}
```

### Real-World Example: State Logging

```kotlin
import kotlinx.coroutines.*

class StatefulJobMonitor {
    private var previousState: String = ""

    fun getState(job: Job): String {
        return when {
            !job.isActive && !job.isCompleted -> "New"
            job.isActive && !job.isCancelled && !job.isCompleted ->
                if (/* has children running */ false) "Completing" else "Active"
            !job.isActive && !job.isCompleted && job.isCancelled -> "Cancelling"
            job.isCompleted && !job.isCancelled -> "Completed"
            job.isCompleted && job.isCancelled -> "Cancelled"
            else -> "Unknown"
        }
    }

    fun logStateChange(job: Job, label: String) {
        val currentState = getState(job)
        if (currentState != previousState) {
            println("[$label] State: $previousState → $currentState")
            println("  isActive=${job.isActive}, isCompleted=${job.isCompleted}, isCancelled=${job.isCancelled}")
            previousState = currentState
        }
    }
}

fun demonstrateStateLogging() = runBlocking {
    println("=== State Logging Demo ===")

    val monitor = StatefulJobMonitor()

    val job = launch(start = CoroutineStart.LAZY) {
        monitor.logStateChange(coroutineContext[Job]!!, "Inside coroutine")

        try {
            repeat(3) { i ->
                delay(100)
                println("Iteration $i")
            }
        } finally {
            monitor.logStateChange(coroutineContext[Job]!!, "In finally")
        }
    }

    monitor.logStateChange(job, "After creation")

    delay(50)
    job.start()
    monitor.logStateChange(job, "After start")

    delay(150)
    monitor.logStateChange(job, "During execution")

    delay(200)
    monitor.logStateChange(job, "After completion")
}
```

### Real-World Example: Android ViewModel with State Tracking

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class DataViewModel {
    private val viewModelScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    private val _dataState = MutableStateFlow<DataState>(DataState.Idle)
    val dataState: StateFlow<DataState> = _dataState.asStateFlow()

    private var loadJob: Job? = null

    fun loadData() {
        // Cancel previous load if still running
        loadJob?.cancel()

        loadJob = viewModelScope.launch {
            _dataState.value = DataState.Loading

            try {
                val data = fetchDataFromNetwork()

                // Check if still active before updating state
                if (isActive) {
                    _dataState.value = DataState.Success(data)
                }
            } catch (e: CancellationException) {
                // Job was cancelled
                _dataState.value = DataState.Idle
                throw e // Rethrow to maintain cancellation
            } catch (e: Exception) {
                if (isActive) {
                    _dataState.value = DataState.Error(e.message ?: "Unknown error")
                }
            }
        }

        // Monitor job state
        loadJob?.invokeOnCompletion { cause ->
            println("Load job completed")
            println("  Cancelled: ${loadJob?.isCancelled}")
            println("  Cause: $cause")
        }
    }

    fun cancelLoad() {
        loadJob?.cancel("User cancelled")
    }

    fun getJobState(): String {
        val job = loadJob ?: return "No job"
        return when {
            job.isActive -> "Active"
            job.isCompleted && !job.isCancelled -> "Completed"
            job.isCompleted && job.isCancelled -> "Cancelled"
            else -> "Unknown"
        }
    }

    private suspend fun fetchDataFromNetwork(): String {
        delay(2000)
        return "Network data"
    }

    fun onCleared() {
        viewModelScope.cancel()
    }
}

sealed class DataState {
    object Idle : DataState()
    object Loading : DataState()
    data class Success(val data: String) : DataState()
    data class Error(val message: String) : DataState()
}

// Usage in Activity/Fragment
fun demonstrateViewModelStateTracking() = runBlocking {
    println("=== ViewModel State Tracking ===")

    val viewModel = DataViewModel()

    // Collect state
    val job = launch {
        viewModel.dataState.collect { state ->
            println("UI State: $state")
        }
    }

    println("Starting load...")
    viewModel.loadData()
    println("Job state: ${viewModel.getJobState()}")

    delay(500)
    println("\nCancelling load...")
    viewModel.cancelLoad()

    delay(100)
    println("Job state after cancel: ${viewModel.getJobState()}")

    job.cancel()
    viewModel.onCleared()
}
```

### Best Practices for State Checking

1. **Check `isActive` before suspending**
   ```kotlin
   suspend fun doWork() {
       if (!isActive) return

       // Expensive operation
       val result = heavyComputation()

       if (!isActive) return // Check again

       updateUI(result)
   }
   ```

2. **Use `ensureActive()` for better cancellation**
   ```kotlin
   suspend fun processItems(items: List<Item>) {
       for (item in items) {
           ensureActive() // Throws if cancelled
           processItem(item)
       }
   }
   ```

3. **Check completion before updating state**
   ```kotlin
   launch {
       val data = loadData()
       if (isActive) { // Only update if not cancelled
           _state.value = data
       }
   }
   ```

4. **Use `invokeOnCompletion` for cleanup**
   ```kotlin
   val job = launch {
       // Work
   }

   job.invokeOnCompletion { cause ->
       if (cause != null) {
           // Cleanup on failure/cancellation
       }
   }
   ```

5. **Don't rely on state in concurrent scenarios**
   ```kotlin
   // BAD: Race condition
   if (!job.isCompleted) {
       job.cancel()
   }

   // GOOD: cancel() is idempotent
   job.cancel()
   ```

6. **Wait for cancellation with `join()`**
   ```kotlin
   job.cancel()
   job.join() // Wait for finally blocks
   // Now safe to release resources
   ```

### Common Pitfalls

1. **Forgetting that `isCompleted=true` for cancelled jobs**
   ```kotlin
   // BAD
   if (job.isCompleted) {
       // Assumes success, but might be cancelled!
   }

   // GOOD
   if (job.isCompleted && !job.isCancelled) {
       // Truly successful
   }
   ```

2. **Not waiting for cancellation to complete**
   ```kotlin
   // BAD
   job.cancel()
   resource.release() // Finally might still be running!

   // GOOD
   job.cancel()
   job.join() // Wait for finally blocks
   resource.release()
   ```

3. **Assuming `isActive=false` means completed**
   ```kotlin
   // BAD
   if (!job.isActive) {
       // Could be New, Completing, Cancelling, or terminal
   }

   // GOOD
   if (job.isCompleted) {
       // Terminal state
   }
   ```

4. **Starting completed jobs**
   ```kotlin
   // BAD
   job.start() // No effect if already started/completed

   // GOOD
   if (job.isActive || !job.isCompleted) {
       job.start()
   }
   // Or better: just create a new job
   ```

### Performance Considerations

1. **State checks are O(1)** - cheap to call frequently
2. **`invokeOnCompletion` has overhead** - use sparingly
3. **Completing state adds latency** - parent waits for all children
4. **Cancelling state duration depends on finally blocks** - keep them short

### Testing Job States

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class JobStateTest {
    @Test
    fun testLazyJobStates() = runTest {
        val job = launch(start = CoroutineStart.LAZY) {
            delay(100)
        }

        // New state
        assertFalse(job.isActive)
        assertFalse(job.isCompleted)
        assertFalse(job.isCancelled)

        job.start()

        // Active state
        assertTrue(job.isActive)
        assertFalse(job.isCompleted)

        job.join()

        // Completed state
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
        assertFalse(job.isCancelled)
    }

    @Test
    fun testCancelledStates() = runTest {
        val job = launch {
            delay(1000)
        }

        // Active
        assertTrue(job.isActive)

        job.cancel()

        // Cancelling (might be brief)
        assertTrue(job.isCancelled)

        job.join()

        // Cancelled
        assertFalse(job.isActive)
        assertTrue(job.isCompleted)
        assertTrue(job.isCancelled)
    }

    @Test
    fun testCompletingState() = runTest {
        var parentInCompletingState = false

        val parent = launch {
            launch {
                delay(200)
            }
            // Parent body finishes here, enters Completing
            parentInCompletingState = parent.isActive && !parent.isCompleted
        }

        parent.join()
        assertTrue(parentInCompletingState)
    }
}
```

---

## Русский

### Обзор

Kotlin корутины `Job` — это конечный автомат с 6 различными состояниями. Понимание этих состояний, их переходов и поведения свойств `isActive`, `isCompleted` и `isCancelled` критически важно для управления жизненным циклом корутин, отладки и предотвращения распространённых ошибок.

Этот вопрос исследует полный конечный автомат, допустимые переходы, поведение свойств в каждом состоянии, правила распространения от родителя к потомкам, и как `join()` и `cancel()` взаимодействуют с различными состояниями.

### 6 Состояний Job

`Job` может находиться в одном из следующих состояний:

1. **New** (только для `CoroutineStart.LAZY`)
2. **Active** (нормальное выполнение)
3. **Completing** (тело завершено, ожидание потомков)
4. **Completed** (полностью завершено)
5. **Cancelling** (отмена в процессе, выполнение блоков finally)
6. **Cancelled** (терминальное отменённое состояние)

### Поведение Свойств Состояния

| Состояние | isActive | isCompleted | isCancelled |
|-----------|----------|-------------|-------------|
| **New** | false | false | false |
| **Active** | true | false | false |
| **Completing** | true | false | false |
| **Completed** | false | true | false |
| **Cancelling** | false | false | true |
| **Cancelled** | false | true | true |

### Диаграмма Переходов Состояний (текстовая)

```

                           New      (только LAZY)
                       (начальное)

                              start()


            Active
                     (выполнение)


                             тело завершено


                      Completing
                     (ожид. детей)


                             все дети
                             завершены


                       Completed
                        (успех)


           cancel()




                Cancelling
               (finally,
                ожид. детей) дети завершены


                       finally выполнен


                 Cancelled
               (терминальное)

```

### Состояние 1: New (только CoroutineStart.LAZY)

Состояние **New** существует только для корутин, запущенных с `CoroutineStart.LAZY`. Корутина создана, но ещё не запущена.

**Свойства:**
- `isActive = false`
- `isCompleted = false`
- `isCancelled = false`

**Переходы:**
- В **Active**: вызов `start()` или `join()`
- В **Cancelling**: вызов `cancel()` до запуска

```kotlin
import kotlinx.coroutines.*

fun demonstrateNewState() = runBlocking {
    println("=== Демонстрация состояния New ===")

    val job = launch(start = CoroutineStart.LAZY) {
        println("Выполнение тела корутины")
        delay(100)
    }

    // В состоянии New
    println("После создания:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false
    println("  isCancelled: ${job.isCancelled}")   // false

    delay(50) // Ждём немного

    println("\nЧерез 50мс (всё ещё не запущена):")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false

    // Переход в Active
    job.start()
    println("\nПосле start():")
    println("  isActive: ${job.isActive}")         // true
    println("  isCompleted: ${job.isCompleted}")   // false

    job.join()
    println("\nПосле завершения:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
}
```

### Состояние 2: Active (нормальное выполнение)

Состояние **Active** означает, что корутина в данный момент выполняется. Это нормальное рабочее состояние.

**Свойства:**
- `isActive = true`
- `isCompleted = false`
- `isCancelled = false`

**Переходы:**
- В **Completing**: тело завершается нормально
- В **Cancelling**: вызывается `cancel()`

### Состояние 3: Completing (ожидание потомков)

Состояние **Completing** возникает, когда тело корутины завершилось, но у неё всё ещё есть активные потомки. Родитель ждёт завершения всех потомков перед переходом в **Completed**.

**Свойства:**
- `isActive = true` (всё ещё считается активной!)
- `isCompleted = false`
- `isCancelled = false`

**Ключевой момент:** `isActive` остаётся `true` во время состояния Completing, потому что работа ещё не полностью завершена.

```kotlin
import kotlinx.coroutines.*

fun demonstrateCompletingState() = runBlocking {
    println("=== Демонстрация состояния Completing ===")

    val parentJob = launch {
        println("Тело родителя запущено")

        // Запускаем дочерние корутины
        launch {
            println("  Потомок 1 запущен")
            delay(200)
            println("  Потомок 1 завершён")
        }

        launch {
            println("  Потомок 2 запущен")
            delay(400)
            println("  Потомок 2 завершён")
        }

        println("Тело родителя завершено (но потомки ещё работают)")
        // Родитель переходит в состояние Completing здесь
    }

    delay(250) // Тело родителя выполнено, потомок 1 завершён, потомок 2 ещё работает

    println("\nРодитель в состоянии Completing:")
    println("  isActive: ${parentJob.isActive}")       // true (!)
    println("  isCompleted: ${parentJob.isCompleted}") // false
    println("  isCancelled: ${parentJob.isCancelled}") // false

    parentJob.join() // Ждём завершения потомка 2

    println("\nПосле завершения всех потомков:")
    println("  isActive: ${parentJob.isActive}")       // false
    println("  isCompleted: ${parentJob.isCompleted}") // true
}
```

### Состояние 4: Completed (успешное завершение)

Состояние **Completed** — терминальное состояние, указывающее на успешное завершение. Тело корутины завершилось, все потомки завершены, отмены не произошло.

**Свойства:**
- `isActive = false`
- `isCompleted = true`
- `isCancelled = false`

**Переходы:** Нет (терминальное состояние)

### Состояние 5: Cancelling (выполнение Блоков finally)

Состояние **Cancelling** возникает, когда отмена в процессе. Корутина выполняет блоки `finally` и ждёт отмены потомков.

**Свойства:**
- `isActive = false`
- `isCompleted = false`
- `isCancelled = true`

**Переходы:**
- В **Cancelled**: блоки finally выполнены, потомки отменены

```kotlin
import kotlinx.coroutines.*

fun demonstrateCancellingState() = runBlocking {
    println("=== Демонстрация состояния Cancelling ===")

    val job = launch {
        try {
            println("Начинаем работу...")
            repeat(5) { i ->
                println("  Итерация $i")
                delay(100)
            }
        } finally {
            println("Блок finally начался")
            println("  isActive: ${coroutineContext[Job]?.isActive}")     // false
            println("  isCancelled: ${coroutineContext[Job]?.isCancelled}") // true

            // Работа по очистке (без приостановки)
            println("  Очистка ресурсов...")
            Thread.sleep(150) // Имитация очистки
            println("  Очистка завершена")

            println("Блок finally завершён")
        }
    }

    delay(250) // Даём поработать немного

    println("\nОтменяем job...")
    job.cancel()

    // Job может ненадолго оказаться в состоянии Cancelling
    println("Job в состоянии Cancelling:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // false (!)
    println("  isCancelled: ${job.isCancelled}")   // true

    job.join() // Ждём завершения отмены

    println("\nПосле завершения отмены:")
    println("  isActive: ${job.isActive}")         // false
    println("  isCompleted: ${job.isCompleted}")   // true
    println("  isCancelled: ${job.isCancelled}")   // true
}
```

### Состояние 6: Cancelled (терминальное Отменённое состояние)

Состояние **Cancelled** — терминальное состояние, указывающее на завершённую отмену. Все блоки finally выполнены, все потомки отменены.

**Свойства:**
- `isActive = false`
- `isCompleted = true` (!)
- `isCancelled = true`

**Ключевой момент:** `isCompleted` равен `true` в состоянии Cancelled, потому что работа завершена (даже если была отменена).

**Переходы:** Нет (терминальное состояние)

### Правила Распространения Состояний Родитель-потомок

Распространение состояний корутин следует принципам структурной параллельности:

1. **Отмена родителя → отмена потомков**
   - Когда родитель отменяется, все потомки отменяются рекурсивно
   - Потомки переходят в состояние Cancelling

2. **Ошибка потомка → отмена родителя**
   - Когда потомок завершается с исключением, родитель отменяется (по умолчанию)
   - Братья и сёстры также отменяются
   - Используйте `SupervisorJob` для предотвращения этого

3. **Родитель ждёт потомков**
   - Родитель переходит в состояние Completing после завершения тела
   - Переходит в Completed только когда все потомки завершены

### Поведение join() В Каждом Состоянии

Функция `join()` приостанавливается до тех пор, пока job не достигнет терминального состояния (Completed или Cancelled).

| Состояние | Поведение join() |
|-----------|------------------|
| **New** | Запускает job (если LAZY), затем приостанавливается до завершения |
| **Active** | Приостанавливается до завершения или отмены job |
| **Completing** | Приостанавливается до завершения всех потомков |
| **Completed** | Возвращается немедленно |
| **Cancelling** | Приостанавливается до завершения отмены |
| **Cancelled** | Возвращается немедленно |

### Поведение cancel() В Каждом Состоянии

Функция `cancel()` запрашивает отмену job.

| Состояние | Поведение cancel() |
|-----------|---------------------|
| **New** | Немедленно переходит в Cancelled (без выполнения) |
| **Active** | Переходит в Cancelling, выполняет блоки finally |
| **Completing** | Переходит в Cancelling, отменяет оставшихся потомков |
| **Completed** | Без эффекта (идемпотентна) |
| **Cancelling** | Без эффекта (уже отменяется) |
| **Cancelled** | Без эффекта (идемпотентна) |

### Лучшие Практики Проверки Состояния

1. **Проверяйте `isActive` перед приостановкой**
2. **Используйте `ensureActive()` для лучшей отмены**
3. **Проверяйте завершение перед обновлением состояния**
4. **Используйте `invokeOnCompletion` для очистки**
5. **Не полагайтесь на состояние в конкурентных сценариях**
6. **Ждите завершения отмены с `join()`**

### Распространённые Ошибки

1. **Забывание, что `isCompleted=true` для отменённых jobs**
2. **Неожидание завершения отмены**
3. **Предположение, что `isActive=false` означает завершение**
4. **Запуск завершённых jobs**

### Соображения Производительности

1. **Проверки состояния имеют O(1)** - дёшево вызывать часто
2. **`invokeOnCompletion` имеет накладные расходы** - используйте экономно
3. **Состояние Completing добавляет задержку** - родитель ждёт всех потомков
4. **Длительность состояния Cancelling зависит от блоков finally** - делайте их короткими

---

## Follow-ups

1. What happens to child coroutines when parent transitions from Completing to Completed?
2. How does SupervisorJob affect state transitions between parent and children?
3. Can you cancel a job in the New state, and what happens to its properties?
4. Why is `isActive` true in the Completing state but false in Cancelling?
5. How does `cancelAndJoin()` differ from separate `cancel()` and `join()` calls?
6. What happens if an exception is thrown in a finally block during Cancelling state?
7. How do you test that a coroutine properly transitions through all expected states?

## References

- [Kotlin Coroutines Guide - Job](https://kotlinlang.org/docs/coroutines-guide.html)
- [Job Interface Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-job/)
- [Coroutine Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html)
- [Understanding Kotlin Coroutines Job Lifecycle](https://medium.com/androiddevelopers/coroutines-first-things-first-e6187bf3bb21)

## Related Questions

- [[q-structured-concurrency-violations--kotlin--hard|Structured concurrency violations]]

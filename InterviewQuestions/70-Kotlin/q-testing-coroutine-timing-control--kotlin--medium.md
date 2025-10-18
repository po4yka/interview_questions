---
topic: kotlin
id: "20251012-170008"
title: "Testing coroutine timing: advanceTimeBy vs advanceUntilIdle / Тестирование таймингов корутин"
subtopics:
  - coroutines
  - testing
  - timing
  - virtual-time
  - runtest
difficulty: medium
moc: moc-kotlin
related: [q-enum-class-advanced--kotlin--medium, q-lambdas-java-kotlin-syntax--programming-languages--medium, q-kotlin-constructor-types--programming-languages--medium]
status: draft
created: 2025-10-12
updated: 2025-10-12
tags:
  - kotlin
  - coroutines
  - testing
  - virtual-time
  - test-dispatcher
  - timing
  - deterministic
---

# Testing coroutine timing: advanceTimeBy vs advanceUntilIdle / Тестирование таймингов корутин

## English

### Overview

Testing time-dependent coroutine code without virtual time would require actual delays, making tests slow and non-deterministic. Kotlin coroutines provide virtual time control through `TestScope` and `TestDispatcher`, allowing instant execution of delayed operations and deterministic testing of timing-sensitive code.

Understanding `advanceTimeBy()`, `advanceUntilIdle()`, `runCurrent()`, and `currentTime` is essential for writing fast, reliable coroutine tests.

### Virtual Time Concept

Virtual time allows tests to "skip ahead" in time without actually waiting. A `delay(1000)` in test code executes instantly by advancing virtual time.

#### Real Time vs Virtual Time

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.system.measureTimeMillis
import kotlin.test.*

class VirtualTimeDemo {
    @Test
    fun realTimeTest() {
        val elapsed = measureTimeMillis {
            runBlocking {
                delay(1000) // Actually waits 1 second
            }
        }
        println("Real time test took: ${elapsed}ms") // ~1000ms
        assertTrue(elapsed >= 1000)
    }

    @Test
    fun virtualTimeTest() = runTest {
        val elapsed = measureTimeMillis {
            delay(1000) // Executes instantly in virtual time
        }
        println("Virtual time test took: ${elapsed}ms") // ~0ms
        assertTrue(elapsed < 100) // Very fast!

        println("Virtual time advanced: ${currentTime}ms") // 1000
    }
}
```

### TestScope and TestDispatcher

`runTest` creates a `TestScope` with a `TestDispatcher` that controls virtual time.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class TestScopeBasics {
    @Test
    fun testScopeExample() = runTest {
        // This is a TestScope
        println("Is TestScope: ${this is TestScope}") // true

        // currentTime starts at 0
        println("Initial time: $currentTime") // 0

        delay(100)
        println("After delay(100): $currentTime") // 100

        delay(500)
        println("After delay(500): $currentTime") // 600
    }

    @Test
    fun testDispatcherExample() = runTest {
        // TestDispatcher is the context
        val dispatcher = coroutineContext[CoroutineDispatcher]
        println("Dispatcher type: ${dispatcher?.javaClass?.simpleName}")
        // Output: StandardTestDispatcher
    }
}
```

### advanceTimeBy(delayMillis) - Precise Time Advancement

`advanceTimeBy(millis)` advances virtual time by exactly the specified amount and executes all tasks scheduled up to that time.

#### Basic Usage

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class AdvanceTimeByBasics {
    @Test
    fun basicAdvanceTimeBy() = runTest {
        var completed = false

        launch {
            delay(1000)
            completed = true
        }

        // Not yet completed
        assertFalse(completed)
        println("Time: $currentTime, completed: $completed") // 0, false

        // Advance 500ms - not enough
        advanceTimeBy(500)
        assertFalse(completed)
        println("Time: $currentTime, completed: $completed") // 500, false

        // Advance another 500ms - now completes
        advanceTimeBy(500)
        assertTrue(completed)
        println("Time: $currentTime, completed: $completed") // 1000, true
    }

    @Test
    fun multipleDelaysWithAdvanceTimeBy() = runTest {
        val results = mutableListOf<String>()

        launch {
            delay(100)
            results.add("Task A")
        }

        launch {
            delay(200)
            results.add("Task B")
        }

        launch {
            delay(300)
            results.add("Task C")
        }

        // Advance to 150ms - only A completes
        advanceTimeBy(150)
        assertEquals(listOf("Task A"), results)
        assertEquals(150, currentTime)

        // Advance to 250ms - B completes
        advanceTimeBy(100)
        assertEquals(listOf("Task A", "Task B"), results)
        assertEquals(250, currentTime)

        // Advance to 350ms - C completes
        advanceTimeBy(100)
        assertEquals(listOf("Task A", "Task B", "Task C"), results)
        assertEquals(350, currentTime)
    }
}
```

#### Precise Control Example

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class PreciseTimingControl {
    @Test
    fun testDebounce() = runTest {
        val events = mutableListOf<String>()

        // Simulated debounce function
        suspend fun debounceProcess(value: String) {
            delay(300) // Debounce delay
            events.add(value)
        }

        var debouncedJob: Job? = null

        fun submitEvent(value: String) {
            debouncedJob?.cancel()
            debouncedJob = this.backgroundScope.launch {
                debounceProcess(value)
            }
        }

        // Submit event 1
        submitEvent("Event1")
        advanceTimeBy(100) // Not enough to trigger
        assertTrue(events.isEmpty())

        // Submit event 2 (cancels event 1)
        submitEvent("Event2")
        advanceTimeBy(100)
        assertTrue(events.isEmpty())

        // Submit event 3 (cancels event 2)
        submitEvent("Event3")
        advanceTimeBy(300) // Enough for event 3
        assertEquals(listOf("Event3"), events)

        // Only the last event was processed (debounced)
    }

    @Test
    fun testRateLimiting() = runTest {
        val timestamps = mutableListOf<Long>()

        suspend fun rateLimitedOperation() {
            timestamps.add(currentTime)
            delay(1000) // Rate limit: 1 op per second
        }

        // Try to execute 3 times
        repeat(3) {
            rateLimitedOperation()
            advanceTimeBy(1000)
        }

        // Should execute at 0, 1000, 2000
        assertEquals(listOf(0L, 1000L, 2000L), timestamps)
    }
}
```

### advanceUntilIdle() - Run All Pending Work

`advanceUntilIdle()` advances time until there are no more pending tasks. It's like fast-forwarding to the end of all scheduled work.

#### Basic Usage

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class AdvanceUntilIdleBasics {
    @Test
    fun basicAdvanceUntilIdle() = runTest {
        val results = mutableListOf<String>()

        launch {
            delay(100)
            results.add("Task A")
        }

        launch {
            delay(500)
            results.add("Task B")
        }

        launch {
            delay(1000)
            results.add("Task C")
        }

        // Run all tasks instantly
        advanceUntilIdle()

        // All completed
        assertEquals(listOf("Task A", "Task B", "Task C"), results)
        assertEquals(1000, currentTime) // Advanced to latest delay
    }

    @Test
    fun chainedDelays() = runTest {
        val results = mutableListOf<Int>()

        launch {
            repeat(5) { i ->
                delay(100)
                results.add(i)
            }
        }

        // Execute all delays
        advanceUntilIdle()

        assertEquals(listOf(0, 1, 2, 3, 4), results)
        assertEquals(500, currentTime)
    }
}
```

#### Dynamic Work Example

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class DynamicWorkTesting {
    @Test
    fun testRecursiveScheduling() = runTest {
        val events = mutableListOf<String>()

        fun scheduleWork(depth: Int) {
            if (depth > 0) {
                backgroundScope.launch {
                    delay(100)
                    events.add("Depth $depth")
                    scheduleWork(depth - 1) // Schedule more work
                }
            }
        }

        scheduleWork(3)

        // advanceUntilIdle processes all dynamically scheduled work
        advanceUntilIdle()

        assertEquals(listOf("Depth 3", "Depth 2", "Depth 1"), events)
        assertEquals(300, currentTime)
    }

    @Test
    fun testProducerConsumerComplete() = runTest {
        val channel = Channel<Int>(capacity = 10)
        val received = mutableListOf<Int>()

        // Producer
        launch {
            repeat(5) { i ->
                delay(100)
                channel.send(i)
            }
            channel.close()
        }

        // Consumer
        launch {
            for (value in channel) {
                delay(50)
                received.add(value)
            }
        }

        // Run until both complete
        advanceUntilIdle()

        assertEquals(listOf(0, 1, 2, 3, 4), received)
    }
}
```

### runCurrent() - Execute Only Current Tasks

`runCurrent()` executes tasks scheduled at the current virtual time, without advancing time.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class RunCurrentBasics {
    @Test
    fun basicRunCurrent() = runTest {
        val results = mutableListOf<String>()

        launch {
            results.add("Immediate") // No delay
        }

        launch {
            delay(100)
            results.add("Delayed")
        }

        // Run immediate tasks only
        runCurrent()

        assertEquals(listOf("Immediate"), results)
        assertEquals(0, currentTime) // Time not advanced

        // Now advance time
        advanceTimeBy(100)
        assertEquals(listOf("Immediate", "Delayed"), results)
    }

    @Test
    fun multipleRunCurrentCalls() = runTest {
        val results = mutableListOf<String>()

        // Schedule at time 0 (immediate)
        launch {
            results.add("Task 1")
        }

        launch {
            results.add("Task 2")
        }

        // Execute immediate tasks
        runCurrent()
        assertEquals(listOf("Task 1", "Task 2"), results)

        // Schedule more at time 0
        launch {
            results.add("Task 3")
        }

        // Another runCurrent picks it up
        runCurrent()
        assertEquals(listOf("Task 1", "Task 2", "Task 3"), results)
        assertEquals(0, currentTime)
    }
}
```

### currentTime Property

`currentTime` returns the current virtual time in milliseconds.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class CurrentTimeUsage {
    @Test
    fun trackingTime() = runTest {
        assertEquals(0, currentTime)

        delay(100)
        assertEquals(100, currentTime)

        advanceTimeBy(500)
        assertEquals(600, currentTime)

        advanceUntilIdle()
        // Time is at the last scheduled task
    }

    @Test
    fun timestampingEvents() = runTest {
        data class Event(val name: String, val timestamp: Long)

        val events = mutableListOf<Event>()

        launch {
            delay(100)
            events.add(Event("Event 1", currentTime))

            delay(200)
            events.add(Event("Event 2", currentTime))

            delay(300)
            events.add(Event("Event 3", currentTime))
        }

        advanceUntilIdle()

        assertEquals(100, events[0].timestamp)
        assertEquals(300, events[1].timestamp)
        assertEquals(600, events[2].timestamp)
    }
}
```

### Testing delay() Operations

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class DelayTesting {
    @Test
    fun simpleDelay() = runTest {
        var executed = false

        launch {
            delay(1000)
            executed = true
        }

        assertFalse(executed)

        advanceTimeBy(999)
        assertFalse(executed) // Not yet

        advanceTimeBy(1)
        assertTrue(executed) // Now executed
    }

    @Test
    fun multipleDelaysInSequence() = runTest {
        val results = mutableListOf<Int>()

        launch {
            repeat(5) { i ->
                delay(100)
                results.add(i)
            }
        }

        // Test each delay individually
        repeat(5) { i ->
            advanceTimeBy(100)
            assertEquals(i + 1, results.size)
            assertEquals(i, results.last())
        }
    }

    @Test
    fun delayZero() = runTest {
        var executed = false

        launch {
            delay(0) // Yields to other coroutines
            executed = true
        }

        // delay(0) requires runCurrent or advanceTimeBy(0)
        assertFalse(executed)

        runCurrent()
        assertTrue(executed)
    }
}
```

### Testing withTimeout / withTimeoutOrNull

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class TimeoutTesting {
    @Test
    fun testWithTimeoutSuccess() = runTest {
        val result = withTimeout(1000) {
            delay(500)
            "Success"
        }

        assertEquals("Success", result)
        assertEquals(500, currentTime)
    }

    @Test
    fun testWithTimeoutFailure() = runTest {
        assertFailsWith<TimeoutCancellationException> {
            withTimeout(1000) {
                delay(2000)
                "Should not reach"
            }
        }

        assertEquals(1000, currentTime)
    }

    @Test
    fun testWithTimeoutOrNull() = runTest {
        val result1 = withTimeoutOrNull(1000) {
            delay(500)
            "Success"
        }
        assertEquals("Success", result1)

        val result2 = withTimeoutOrNull(1000) {
            delay(2000)
            "Should timeout"
        }
        assertNull(result2)
        assertEquals(1500, currentTime) // 500 + 1000
    }

    @Test
    fun testNetworkCallWithTimeout() = runTest {
        class NetworkClient {
            suspend fun fetchData(): String {
                delay(5000) // Slow network
                return "Data"
            }
        }

        val client = NetworkClient()

        val result = withTimeoutOrNull(3000) {
            client.fetchData()
        }

        assertNull(result) // Timed out
        assertEquals(3000, currentTime)
    }
}
```

### Testing Periodic Operations

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class PeriodicOperationsTesting {
    @Test
    fun testPolling() = runTest {
        var pollCount = 0

        val job = launch {
            while (isActive) {
                pollCount++
                delay(1000)
            }
        }

        // Advance through several polls
        repeat(5) {
            advanceTimeBy(1000)
        }

        assertEquals(5, pollCount)
        assertEquals(5000, currentTime)

        job.cancel()
    }

    @Test
    fun testTickerChannel() = runTest {
        val ticker = ticker(delayMillis = 1000, initialDelayMillis = 0)
        val ticks = mutableListOf<Long>()

        val job = launch {
            repeat(5) {
                ticker.receive()
                ticks.add(currentTime)
            }
        }

        advanceUntilIdle()

        assertEquals(listOf(0L, 1000L, 2000L, 3000L, 4000L), ticks)

        ticker.cancel()
        job.cancel()
    }

    @Test
    fun testRepeatingTask() = runTest {
        val executions = mutableListOf<Long>()

        suspend fun repeatingTask() {
            while (true) {
                executions.add(currentTime)
                delay(500)
            }
        }

        val job = launch {
            repeatingTask()
        }

        // Let it run for 2.5 seconds
        advanceTimeBy(2500)

        assertEquals(listOf(0L, 500L, 1000L, 1500L, 2000L), executions)

        job.cancel()
    }
}
```

### Testing Debounce/Throttle in Flow

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.*
import kotlin.test.*

class FlowTimingTesting {
    @Test
    fun testFlowDebounce() = runTest {
        val flow = flow {
            emit(1)
            delay(100)
            emit(2)
            delay(100)
            emit(3)
            delay(500) // Longer delay
            emit(4)
        }.debounce(200)

        val results = mutableListOf<Int>()

        launch {
            flow.collect { results.add(it) }
        }

        advanceUntilIdle()

        // Only 3 and 4 emitted (others debounced)
        assertEquals(listOf(3, 4), results)
    }

    @Test
    fun testFlowSample() = runTest {
        val flow = flow {
            repeat(10) { i ->
                emit(i)
                delay(100)
            }
        }.sample(250)

        val results = mutableListOf<Int>()

        launch {
            flow.collect { results.add(it) }
        }

        advanceUntilIdle()

        // Sampled every 250ms: 2, 4, 7, 9
        assertEquals(listOf(2, 4, 7, 9), results)
    }

    @Test
    fun testFlowDelay() = runTest {
        val flow = flow {
            emit(1)
            emit(2)
            emit(3)
        }.onEach { delay(100) }

        val timestamps = mutableListOf<Long>()

        launch {
            flow.collect {
                timestamps.add(currentTime)
            }
        }

        advanceUntilIdle()

        assertEquals(listOf(100L, 200L, 300L), timestamps)
    }
}
```

### Real-World Example: ViewModel Testing

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlinx.coroutines.flow.*
import kotlin.test.*

class UserProfileViewModel {
    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    suspend fun loadUserProfile(userId: String) {
        _uiState.value = UiState.Loading

        delay(1000) // Simulate network call

        if (userId.isNotEmpty()) {
            _uiState.value = UiState.Success(UserProfile(userId, "User $userId"))
        } else {
            _uiState.value = UiState.Error("Invalid user ID")
        }
    }

    suspend fun refreshWithRetry() {
        repeat(3) { attempt ->
            _uiState.value = UiState.Loading

            delay(2000) // Simulate network call

            // Simulate failure on first 2 attempts
            if (attempt < 2) {
                _uiState.value = UiState.Error("Network error")
                delay(1000) // Retry delay
            } else {
                _uiState.value = UiState.Success(UserProfile("123", "User"))
                return
            }
        }
    }
}

sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val profile: UserProfile) : UiState()
    data class Error(val message: String) : UiState()
}

data class UserProfile(val id: String, val name: String)

class UserProfileViewModelTest {
    @Test
    fun testLoadUserProfileSuccess() = runTest {
        val viewModel = UserProfileViewModel()

        // Initial state
        assertEquals(UiState.Idle, viewModel.uiState.value)

        // Start loading
        val job = launch {
            viewModel.loadUserProfile("123")
        }

        // Immediately becomes Loading
        advanceTimeBy(0)
        assertEquals(UiState.Loading, viewModel.uiState.value)

        // After 1000ms, should be Success
        advanceTimeBy(1000)
        val state = viewModel.uiState.value
        assertTrue(state is UiState.Success)
        assertEquals("123", state.profile.id)

        job.cancel()
    }

    @Test
    fun testLoadUserProfileError() = runTest {
        val viewModel = UserProfileViewModel()

        launch {
            viewModel.loadUserProfile("")
        }

        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UiState.Error)
        assertEquals("Invalid user ID", state.message)
    }

    @Test
    fun testRefreshWithRetry() = runTest {
        val viewModel = UserProfileViewModel()
        val states = mutableListOf<UiState>()

        // Collect all state changes
        val collectJob = launch {
            viewModel.uiState.collect { states.add(it) }
        }

        val refreshJob = launch {
            viewModel.refreshWithRetry()
        }

        advanceUntilIdle()

        // Expected sequence:
        // Idle -> Loading -> Error -> Loading -> Error -> Loading -> Success
        assertEquals(7, states.size)

        assertTrue(states[0] is UiState.Idle)
        assertTrue(states[1] is UiState.Loading)
        assertTrue(states[2] is UiState.Error)
        assertTrue(states[3] is UiState.Loading)
        assertTrue(states[4] is UiState.Error)
        assertTrue(states[5] is UiState.Loading)
        assertTrue(states[6] is UiState.Success)

        // Total time: (2000 + 1000) * 2 + 2000 = 8000ms
        assertEquals(8000, currentTime)

        collectJob.cancel()
        refreshJob.cancel()
    }

    @Test
    fun testStateFlowTimingWithCollect() = runTest {
        val viewModel = UserProfileViewModel()
        val stateTimestamps = mutableListOf<Pair<UiState, Long>>()

        val collectJob = backgroundScope.launch {
            viewModel.uiState.collect { state ->
                stateTimestamps.add(state to currentTime)
            }
        }

        launch {
            viewModel.loadUserProfile("user1")
        }

        advanceUntilIdle()

        // Verify timing
        assertEquals(3, stateTimestamps.size)
        assertEquals(0L, stateTimestamps[0].second) // Idle at 0
        assertEquals(0L, stateTimestamps[1].second) // Loading at 0
        assertEquals(1000L, stateTimestamps[2].second) // Success at 1000

        collectJob.cancel()
    }
}
```

### Testing Race Conditions Deterministically

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class RaceConditionTesting {
    @Test
    fun testConcurrentUpdates() = runTest {
        var counter = 0

        val jobs = List(10) {
            launch {
                delay(100) // All scheduled at same time
                counter++
            }
        }

        advanceTimeBy(100)

        // All 10 updates happened
        assertEquals(10, counter)

        jobs.forEach { it.cancel() }
    }

    @Test
    fun testFirstToComplete() = runTest {
        val results = mutableListOf<String>()

        coroutineScope {
            launch {
                delay(100)
                results.add("Task A")
            }

            launch {
                delay(50)
                results.add("Task B")
            }

            launch {
                delay(150)
                results.add("Task C")
            }
        }

        // Order is deterministic in virtual time
        assertEquals(listOf("Task B", "Task A", "Task C"), results)
    }

    @Test
    fun testSelectFirst() = runTest {
        suspend fun fetchFromServer1(): String {
            delay(200)
            return "Server 1"
        }

        suspend fun fetchFromServer2(): String {
            delay(100)
            return "Server 2"
        }

        val result = coroutineScope {
            val deferred1 = async { fetchFromServer1() }
            val deferred2 = async { fetchFromServer2() }

            // Wait for first to complete
            advanceTimeBy(100)

            if (deferred2.isCompleted) {
                deferred1.cancel()
                deferred2.await()
            } else {
                deferred2.cancel()
                deferred1.await()
            }
        }

        assertEquals("Server 2", result)
        assertEquals(100, currentTime)
    }
}
```

### Common Mistakes

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class CommonMistakes {
    @Test
    fun mistakeForgettingAdvanceUntilIdle() = runTest {
        var completed = false

        launch {
            delay(1000)
            completed = true
        }

        // MISTAKE: Forgot to advance time
        // assertFalse(completed) // Will fail!

        // FIX: Advance time
        advanceUntilIdle()
        assertTrue(completed)
    }

    @Test
    fun mistakeWrongTimingExpectation() = runTest {
        val results = mutableListOf<Int>()

        launch {
            delay(100)
            results.add(1)

            delay(100)
            results.add(2)
        }

        // MISTAKE: Expecting both after 100ms
        advanceTimeBy(100)
        // assertEquals(listOf(1, 2), results) // Will fail!

        // FIX: Need 200ms total
        assertEquals(listOf(1), results)
        advanceTimeBy(100)
        assertEquals(listOf(1, 2), results)
    }

    @Test
    fun mistakeNotUsingBackgroundScope() = runTest {
        // For fire-and-forget tasks, use backgroundScope

        var count = 0

        // PROBLEM: launch in test scope
        launch {
            while (true) {
                delay(1000)
                count++
            }
        }

        advanceTimeBy(3000)
        // advanceUntilIdle() // Would hang! Infinite loop

        // BETTER: Use backgroundScope for infinite loops
        backgroundScope.launch {
            while (true) {
                delay(1000)
                count++
            }
        }

        advanceTimeBy(3000)
        assertEquals(3, count) // Can advance without hanging
    }

    @Test
    fun mistakeAssumingImmediateExecution() = runTest {
        var value = 0

        launch {
            value = 1
        }

        // MISTAKE: Assuming immediate execution
        // assertEquals(1, value) // Might fail!

        // FIX: Run current tasks
        runCurrent()
        assertEquals(1, value)
    }
}
```

### Testing Immediate vs Delayed Execution

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.*

class ImmediateVsDelayedExecution {
    @Test
    fun testImmediateExecution() = runTest {
        var executed = false

        launch(start = CoroutineStart.UNDISPATCHED) {
            // Executes immediately
            executed = true
        }

        // Already executed, no need to advance time
        assertTrue(executed)
    }

    @Test
    fun testDelayedExecution() = runTest {
        var executed = false

        launch {
            executed = true
        }

        // Not yet executed
        assertFalse(executed)

        // Need to run current tasks
        runCurrent()
        assertTrue(executed)
    }

    @Test
    fun testMixedExecution() = runTest {
        val results = mutableListOf<String>()

        launch(start = CoroutineStart.UNDISPATCHED) {
            results.add("Immediate")
            delay(100)
            results.add("After delay")
        }

        // "Immediate" executed right away
        assertEquals(listOf("Immediate"), results)

        // Need to advance time for delay
        advanceTimeBy(100)
        assertEquals(listOf("Immediate", "After delay"), results)
    }
}
```

### Best Practices

1. **Use `runTest` for all coroutine tests**
   ```kotlin
   @Test
   fun myTest() = runTest {
       // Test code
   }
   ```

2. **Use `advanceUntilIdle()` for complete execution**
   ```kotlin
   @Test
   fun testComplete() = runTest {
       // Start operations
       launch { /* ... */ }

       // Run everything
       advanceUntilIdle()

       // Assert results
   }
   ```

3. **Use `advanceTimeBy()` for precise timing tests**
   ```kotlin
   @Test
   fun testTiming() = runTest {
       launch { delay(1000) }

       advanceTimeBy(500) // Half way
       // Assert intermediate state

       advanceTimeBy(500) // Complete
       // Assert final state
   }
   ```

4. **Use `runCurrent()` for immediate tasks**
   ```kotlin
   @Test
   fun testImmediate() = runTest {
       launch { /* immediate work */ }

       runCurrent()
       // Assert
   }
   ```

5. **Collect StateFlow/SharedFlow in `backgroundScope`**
   ```kotlin
   @Test
   fun testFlow() = runTest {
       backgroundScope.launch {
           flow.collect { /* ... */ }
       }

       advanceUntilIdle()
   }
   ```

6. **Test each timing scenario explicitly**
   ```kotlin
   @Test
   fun testRetry() = runTest {
       // Test immediate failure
       advanceTimeBy(0)
       // Assert

       // Test first retry
       advanceTimeBy(1000)
       // Assert

       // Test final state
       advanceUntilIdle()
       // Assert
   }
   ```

---

## Русский

### Обзор

Тестирование корутин с зависимостью от времени без виртуального времени потребовало бы реальных задержек, делая тесты медленными и недетерминированными. Kotlin корутины предоставляют контроль виртуального времени через `TestScope` и `TestDispatcher`, позволяя мгновенное выполнение отложенных операций и детерминированное тестирование чувствительного к времени кода.

### Концепция виртуального времени

Виртуальное время позволяет тестам "перепрыгивать" во времени без реального ожидания. `delay(1000)` в тестовом коде выполняется мгновенно путём продвижения виртуального времени.

### TestScope и TestDispatcher

`runTest` создаёт `TestScope` с `TestDispatcher`, который контролирует виртуальное время.

### advanceTimeBy(delayMillis) - Точное продвижение времени

`advanceTimeBy(millis)` продвигает виртуальное время ровно на указанное количество и выполняет все задачи, запланированные до этого времени.

### advanceUntilIdle() - Выполнить всю отложенную работу

`advanceUntilIdle()` продвигает время до тех пор, пока не останется отложенных задач. Это как перемотка вперёд до конца всей запланированной работы.

### runCurrent() - Выполнить только текущие задачи

`runCurrent()` выполняет задачи, запланированные на текущее виртуальное время, без продвижения времени.

### currentTime - Текущее виртуальное время

`currentTime` возвращает текущее виртуальное время в миллисекундах.

### Тестирование операций delay()

Виртуальное время позволяет тестировать `delay()` без реального ожидания.

### Тестирование withTimeout / withTimeoutOrNull

Тайм-ауты можно тестировать детерминированно с виртуальным временем.

### Тестирование периодических операций

Циклы с `delay()`, тикеры, опросы - всё тестируется быстро с виртуальным временем.

### Тестирование debounce/throttle в Flow

Flow операторы с временем (`debounce`, `sample`, `delay`) тестируются детерминированно.

### Лучшие практики

1. **Используйте `runTest` для всех тестов корутин**
2. **Используйте `advanceUntilIdle()` для полного выполнения**
3. **Используйте `advanceTimeBy()` для точных тестов таймингов**
4. **Используйте `runCurrent()` для немедленных задач**
5. **Собирайте StateFlow/SharedFlow в `backgroundScope`**
6. **Тестируйте каждый сценарий таймингов явно**

---

## Follow-ups

1. What's the difference between `advanceUntilIdle()` and `advanceTimeBy(Long.MAX_VALUE)`?
2. How do you test infinite loops with `delay()` without hanging the test?
3. When should you use `backgroundScope` vs the test scope in `runTest`?
4. How do you test that a coroutine is properly cancelled at a specific time?
5. What happens if you call `delay()` from outside a `TestScope`?
6. How do you test multiple coroutines with different timing running concurrently?
7. Can you test real-time code (without delays) with `runTest`, and what are the implications?

## References

- [Kotlin Coroutines Test Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [Testing Coroutines Guide](https://developer.android.com/kotlin/coroutines/test)
- [TestScope API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/kotlinx.coroutines.test/-test-scope/)
- [Virtual Time in Tests](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md)

## Related Questions

- [[q-coroutine-lifecycle-management--kotlin--medium|Coroutine lifecycle management]]
- [[q-flow-testing-strategies--kotlin--medium|Flow testing strategies]]
- [[q-job-state-machine-transitions--kotlin--medium|Job state machine and transitions]]
- [[q-structured-concurrency-violations--kotlin--hard|Structured concurrency violations]]

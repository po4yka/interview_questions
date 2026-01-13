---
anki_cards:
- slug: q-circuit-breaker-coroutines--kotlin--hard-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-circuit-breaker-coroutines--kotlin--hard-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-172
title: "Circuit breaker pattern with coroutines / Circuit breaker паттерн с корутинами"
aliases: [Circuit Breaker Pattern, Circuit breaker паттерн]
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-15
updated: 2025-11-09
tags: [circuit-breaker, coroutines, difficulty/hard, error-handling, kotlin, microservices, patterns, production, resilience]
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-advanced-coroutine-patterns--kotlin--hard]

---\
# Вопрос (RU)

> Как реализовать и использовать паттерн circuit breaker с использованием Kotlin coroutines в продакшене: состояния (Closed/Open/Half-Open), конфигурация порогов, потокобезопасность, мониторинг и интеграция с retry/timeout для разных сервисов?

# Question (EN)

> How do you implement and use the circuit breaker pattern with Kotlin coroutines in production: states (Closed/Open/Half-Open), threshold configuration, thread safety, monitoring, and integration with retry/timeout for different services?

## Ответ (RU)

Ниже приведено детальное объяснение и практические примеры реализации circuit breaker с корутинами, включая состояния, конфигурацию, потокобезопасность, мониторинг, интеграцию с retry/timeout и примеры для разных сервисов. Примеры кода демонстрационные; для реального продакшена потребуются дополнительные проверки и тестирование под нагрузкой.

## Answer (EN)

Below is a detailed explanation and practical implementation examples of a coroutine-based circuit breaker, covering states, configuration, thread safety, monitoring, integration with retry/timeout, and usage for different services. Code snippets are illustrative; a production-ready implementation requires additional validation and concurrency testing.

---

## Follow-ups

1. What is the difference between circuit breaker and retry pattern?
2. How would you choose `failureThreshold` and `resetTimeout` for different services?
3. How do you keep the implementation thread-safe under high concurrency with coroutines?
4. How would you expose circuit breaker metrics to your monitoring stack?
5. How do you test state transitions deterministically (including time-based)?

---

# Circuit Breaker Pattern with Coroutines

**English** | [Русский](#circuit-breaker-паттерн-с-корутинами)

---

## Table of Contents

- [Overview](#overview)
- [Pattern Definition and Motivation](#pattern-definition-and-motivation)
- [Three States Explained](#three-states-explained)
- [State Transition Diagram](#state-transition-diagram)
- [Failure Threshold Configuration](#failure-threshold-configuration)
- [Timeout and Recovery Period](#timeout-and-recovery-period)
- [Half-Open State Mechanism](#half-open-state-mechanism)
- [Full Implementation](#full-implementation)
- [Thread-Safe State Transitions](#thread-safe-state-transitions)
- [Complete API Client with Circuit Breaker](#complete-api-client-with-circuit-breaker)
- [Combining with Retry and Timeout](#combining-with-retry-and-timeout)
- [Monitoring Circuit Breaker State](#monitoring-circuit-breaker-state)
- [Multiple Circuit Breakers](#multiple-circuit-breakers)
- [Production Metrics](#production-metrics)
- [Testing with Simulated Failures](#testing-with-simulated-failures)
- [Resilience4j Comparison](#resilience4j-comparison)
- [Real Example: Payment `Service`](#real-example-payment-service)
- [Best Practices](#best-practices)
- [When NOT to Use](#when-not-to-use)
- [Common Pitfalls](#common-pitfalls)
- [Follow-up Questions](#follow-up-questions)
- [References](#references)
- [Related Questions](#related-questions)

---

## Overview

The Circuit Breaker pattern prevents an application from repeatedly trying to execute an operation that's likely to fail, allowing it to continue without waiting for the fault to be fixed or wasting CPU cycles.

Key benefits:
- Prevents cascading failures in distributed systems
- `Provides` fast failure detection and recovery
- Reduces load on failing services
- Improves system resilience and stability
- Enables graceful degradation

Also see: [[c-kotlin]], [[c-coroutines]].

---

## Pattern Definition and Motivation

### What is a Circuit Breaker?

The Circuit Breaker pattern is inspired by electrical circuit breakers that automatically stop the flow of electricity when a fault is detected.

```text
   Client       Circuit      Service
                         Breaker              (Backend)

                               Monitors failures
                               Controls access
                               Manages state

                           State
                          Machine
```

### Why Use Circuit Breaker?

Problem without circuit breaker:

```kotlin
// Without circuit breaker - keeps hammering failing service
class PaymentService(private val api: PaymentApi) {
    suspend fun processPayment(payment: Payment): Result<PaymentResponse> {
        return try {
            // Service is down, but we keep trying
            val response = api.processPayment(payment) // Takes 30 seconds to timeout
            Result.Success(response)
        } catch (e: Exception) {
            // Log error and return failure
            Result.Error(e)
        }
    }
}

// Multiple requests pile up, all waiting for timeout
// System becomes unresponsive
```

Solution with circuit breaker:

```kotlin
// With circuit breaker - fails fast when service is down
class PaymentService(
    private val api: PaymentApi,
    private val circuitBreaker: CircuitBreaker
) {
    suspend fun processPayment(payment: Payment): Result<PaymentResponse> {
        return circuitBreaker.execute {
            api.processPayment(payment)
        }
    }
}

// After threshold failures, circuit opens
// Subsequent requests fail immediately (no waiting)
// System remains responsive
```

---

## Three States Explained

NOTE: The snippets below illustrate behavior concepts. The complete, consistent implementation is shown in [Full Implementation](#full-implementation).

### State: Closed (Normal Operation)

```text
         CLOSED State
  (Normal Operation)

  • All requests pass through
  • Failures are counted
  • Success resets failure counter
  • When failures exceed threshold:
    → Transition to OPEN
```

Illustrative code example:

```kotlin
sealed class CircuitBreakerState {
    data class Closed(
        var failureCount: Int = 0,
        var lastFailureTime: Long? = null
    ) : CircuitBreakerState()
}
```

### State: Open (Failing)

```text
         OPEN State
  (Service is Down)

  • All requests fail immediately
  • No calls to backend service
  • Failure counter reached threshold
  • After timeout period:
    → Transition to HALF_OPEN
```

Illustrative code example:

```kotlin
sealed class CircuitBreakerState {
    data class Open(
        val openedAt: Long = System.currentTimeMillis()
    ) : CircuitBreakerState() {
        fun shouldAttemptReset(timeout: Long): Boolean {
            return System.currentTimeMillis() - openedAt >= timeout
        }
    }
}
```

### State: Half-Open (Testing)

```text
         HALF_OPEN State
  (Testing Recovery)

  • Limited requests pass through
  • Testing if service recovered
  • On success:
    → Transition to CLOSED
  • On failure:
    → Transition back to OPEN
```

Illustrative code example:

```kotlin
sealed class CircuitBreakerState {
    data class HalfOpen(
        var successCount: Int = 0,
        var failureCount: Int = 0
    ) : CircuitBreakerState()
}
```

---

## State Transition Diagram

```text
                       CLOSED
                      (Normal)

                            Failure threshold        Success threshold
                            exceeded                 in HALF_OPEN

                        OPEN
                      (Failing)

                            Timeout period
                            elapsed

                      HALF_OPEN
                      (Testing)

                            Failure

                        OPEN
                      (Failing)
```

State transitions:

1. CLOSED → OPEN: When failure count exceeds threshold
2. OPEN → HALF_OPEN: After timeout period elapses
3. HALF_OPEN → CLOSED: When test requests succeed
4. HALF_OPEN → OPEN: When test request fails

---

## Failure Threshold Configuration

### Basic Configuration

```kotlin
data class CircuitBreakerConfig(
    // Number of consecutive failures before opening circuit
    val failureThreshold: Int = 5,

    // Time window for counting failures (milliseconds)
    val failureTimeWindow: Long = 10_000, // 10 seconds

    // Time to wait before attempting reset (milliseconds)
    val resetTimeout: Long = 60_000, // 60 seconds

    // Number of successful calls needed to close from half-open
    val successThreshold: Int = 2,

    // Exceptions that should trigger circuit breaker
    val recordExceptions: List<Class<out Exception>> = listOf(
        IOException::class.java,
        TimeoutException::class.java
    ),

    // Exceptions that should NOT trigger circuit breaker
    val ignoreExceptions: List<Class<out Exception>> = listOf(
        IllegalArgumentException::class.java,
        ValidationException::class.java
    )
)
```

Note: the example combines "consecutive failures" and a time window. In a real implementation you should clarify whether you use consecutive failures, a sliding window, or both, and implement counters accordingly.

### Advanced Configuration with Sliding Window

```kotlin
data class AdvancedCircuitBreakerConfig(
    // Sliding window type: COUNT_BASED or TIME_BASED
    val slidingWindowType: SlidingWindowType = SlidingWindowType.COUNT_BASED,

    // Size of sliding window
    val slidingWindowSize: Int = 100, // Last 100 calls

    // Minimum number of calls before calculating failure rate
    val minimumNumberOfCalls: Int = 10,

    // Failure rate threshold (percentage)
    val failureRateThreshold: Float = 50f, // 50%

    // Slow call duration threshold (milliseconds)
    val slowCallDurationThreshold: Long = 1000,

    // Slow call rate threshold (percentage)
    val slowCallRateThreshold: Float = 100f,

    // Number of permitted calls in HALF_OPEN state
    val permittedNumberOfCallsInHalfOpenState: Int = 3,

    // Wait duration in OPEN state
    val waitDurationInOpenState: Long = 60_000
)

enum class SlidingWindowType {
    COUNT_BASED,  // Based on last N calls
    TIME_BASED    // Based on calls in last N seconds
}
```

### Example: Different Configurations for Different Services

```kotlin
object CircuitBreakerConfigs {
    // Critical service - fail fast
    val payment = CircuitBreakerConfig(
        failureThreshold = 3,
        failureTimeWindow = 5_000,
        resetTimeout = 30_000,
        successThreshold = 3
    )

    // Non-critical service - more tolerant
    val analytics = CircuitBreakerConfig(
        failureThreshold = 10,
        failureTimeWindow = 30_000,
        resetTimeout = 120_000,
        successThreshold = 1
    )

    // External third-party service - very tolerant
    val thirdParty = CircuitBreakerConfig(
        failureThreshold = 5,
        failureTimeWindow = 60_000,
        resetTimeout = 300_000, // 5 minutes
        successThreshold = 5
    )
}
```

---

## Timeout and Recovery Period

### Timeout Configuration

```kotlin
class CircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    // Timeout for OPEN → HALF_OPEN transition
    private fun shouldAttemptReset(openedAt: Long): Boolean {
        val elapsed = System.currentTimeMillis() - openedAt
        return elapsed >= config.resetTimeout
    }

    // Timeout for individual operations (delegates to full execute implementation)
    suspend fun <T> executeWithTimeout(
        timeoutMs: Long = 5000,
        operation: suspend () -> T
    ): T {
        return withTimeout(timeoutMs) {
            execute(operation)
        }
    }

    suspend fun <T> execute(operation: suspend () -> T): T {
        // Simplified example; see Full Implementation for state handling.
        return operation()
    }
}
```

### Recovery Period Strategies

The following strategies are conceptual examples for backoff policies; they are not wired into the full CircuitBreaker implementation above.

```kotlin
// Strategy 1: Fixed delay
class FixedDelayRecovery(
    private val delayMs: Long = 60_000
) : RecoveryStrategy {
    override fun getNextDelay(attempt: Int): Long = delayMs
}

// Strategy 2: Exponential backoff
class ExponentialBackoffRecovery(
    private val initialDelay: Long = 1000,
    private val maxDelay: Long = 300_000,
    private val multiplier: Double = 2.0
) : RecoveryStrategy {
    override fun getNextDelay(attempt: Int): Long {
        val delay = (initialDelay * multiplier.pow(attempt)).toLong()
        return delay.coerceAtMost(maxDelay)
    }
}

// Strategy 3: Jitter (randomization to prevent thundering herd)
class JitterRecovery(
    private val baseDelay: Long = 60_000,
    private val maxJitter: Long = 5000
) : RecoveryStrategy {
    override fun getNextDelay(attempt: Int): Long {
        val jitter = Random.nextLong(0, maxJitter)
        return baseDelay + jitter
    }
}

interface RecoveryStrategy {
    fun getNextDelay(attempt: Int): Long
}
```

---

## Half-Open State Mechanism

### Implementation (excerpt)

```kotlin
class CircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val halfOpenLock = Mutex()

    suspend fun <T> execute(operation: suspend () -> T): T {
        val currentState = state.get()

        return when (currentState) {
            is CircuitBreakerState.Closed -> executeInClosedState(operation, currentState)
            is CircuitBreakerState.Open -> executeInOpenState(operation, currentState)
            is CircuitBreakerState.HalfOpen -> executeInHalfOpenState(operation, currentState)
        }
    }

    private suspend fun <T> executeInHalfOpenState(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.HalfOpen
    ): T {
        // Ensure only limited concurrent requests in half-open
        return halfOpenLock.withLock {
            // Re-check state after acquiring the lock
            val latest = state.get()
            if (latest !is CircuitBreakerState.HalfOpen) {
                return execute(operation) // State changed, delegate
            }

            try {
                val result = operation()

                // Record success
                latest.successCount++

                // Check if we should close circuit
                if (latest.successCount >= config.successThreshold) {
                    val closed = CircuitBreakerState.Closed()
                    state.set(closed)
                    Log.i("CircuitBreaker", "Circuit closed after successful recovery")
                }

                result
            } catch (e: Exception) {
                // Record failure
                latest.failureCount++

                // Re-open circuit on any failure
                val open = CircuitBreakerState.Open()
                state.set(open)
                Log.w("CircuitBreaker", "Circuit re-opened after failure in half-open state")

                // In this illustrative snippet we wrap as CircuitBreakerOpenException;
                // in the full implementation below we rethrow the original exception.
                throw CircuitBreakerOpenException("Circuit breaker re-opened", e)
            }
        }
    }

    // executeInClosedState and executeInOpenState are implemented as in Full Implementation
}
```

To avoid confusion, pick one consistent behavior for Half-Open failures in your actual implementation (either wrap as CircuitBreakerOpenException or rethrow original) so callers can reliably distinguish open-circuit rejections.

### Test Request Strategy

```kotlin
// Strategy 1: Single test request
class SingleTestStrategy : HalfOpenStrategy {
    override suspend fun <T> test(operation: suspend () -> T): T {
        return operation() // Just one request
    }
}

// Strategy 2: Multiple test requests
class MultipleTestStrategy(
    private val testCount: Int = 3,
    private val successThreshold: Int = 2
) : HalfOpenStrategy {
    override suspend fun <T> test(operation: suspend () -> T): T {
        var successCount = 0
        var lastResult: T? = null

        repeat(testCount) { attempt ->
            try {
                lastResult = operation()
                successCount++

                if (successCount >= successThreshold) {
                    return lastResult!!
                }

                delay(100) // Small delay between tests
            } catch (e: Exception) {
                if (attempt == testCount - 1) {
                    throw e
                }
            }
        }

        throw Exception("Not enough successful test requests")
    }
}

interface HalfOpenStrategy {
    suspend fun <T> test(operation: suspend () -> T): T
}
```

---

## Full Implementation

### Complete Circuit Breaker Class

```kotlin
class CircuitBreaker(
    private val config: CircuitBreakerConfig = CircuitBreakerConfig()
) {
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val stateFlow = MutableStateFlow<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val mutex = Mutex()

    // Metrics
    private val totalCalls = AtomicLong(0)
    private val successfulCalls = AtomicLong(0)
    private val failedCalls = AtomicLong(0)
    private val rejectedCalls = AtomicLong(0)

    suspend fun <T> execute(operation: suspend () -> T): T {
        totalCalls.incrementAndGet()

        val currentState = state.get()

        return when (currentState) {
            is CircuitBreakerState.Closed -> {
                executeInClosedState(operation, currentState)
            }
            is CircuitBreakerState.Open -> {
                executeInOpenState(operation, currentState)
            }
            is CircuitBreakerState.HalfOpen -> {
                executeInHalfOpenState(operation, currentState)
            }
        }
    }

    private suspend fun <T> executeInClosedState(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.Closed
    ): T {
        return try {
            val result = operation()
            recordSuccess(currentState)
            result
        } catch (e: Exception) {
            if (shouldRecordException(e)) {
                recordFailure(currentState)
            }
            throw e
        }
    }

    private suspend fun <T> executeInOpenState(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.Open
    ): T {
        // Check if we should attempt reset
        if (currentState.shouldAttemptReset(config.resetTimeout)) {
            return transitionToHalfOpen(operation)
        }

        // Circuit is open, reject immediately
        rejectedCalls.incrementAndGet()
        throw CircuitBreakerOpenException(
            "Circuit breaker is OPEN. Service is unavailable."
        )
    }

    private suspend fun <T> executeInHalfOpenState(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.HalfOpen
    ): T = mutex.withLock {
        // Only one test execution at a time in this sample implementation
        try {
            val result = operation()
            recordHalfOpenSuccess(currentState)
            result
        } catch (e: Exception) {
            recordHalfOpenFailure()
            throw e
        }
    }

    private suspend fun <T> transitionToHalfOpen(operation: suspend () -> T): T {
        mutex.withLock {
            // Double-check state (may have changed)
            val currentState = state.get()
            if (currentState is CircuitBreakerState.Open &&
                currentState.shouldAttemptReset(config.resetTimeout)
            ) {
                val halfOpenState = CircuitBreakerState.HalfOpen()
                state.set(halfOpenState)
                stateFlow.value = halfOpenState
                Log.i("CircuitBreaker", "Transitioned to HALF_OPEN")
            }
        }

        return execute(operation)
    }

    private fun recordSuccess(currentState: CircuitBreakerState.Closed) {
        successfulCalls.incrementAndGet()
        currentState.failureCount = 0
        currentState.lastFailureTime = null
    }

    private fun recordFailure(currentState: CircuitBreakerState.Closed) {
        failedCalls.incrementAndGet()
        currentState.failureCount++
        currentState.lastFailureTime = System.currentTimeMillis()

        // Check if we should open circuit. This sample uses failureThreshold
        // together with failureTimeWindow for simplicity.
        if (shouldOpenCircuit(currentState)) {
            val openState = CircuitBreakerState.Open()
            state.set(openState)
            stateFlow.value = openState
            Log.w("CircuitBreaker", "Circuit OPENED after ${currentState.failureCount} failures")
        }
    }

    private fun recordHalfOpenSuccess(currentState: CircuitBreakerState.HalfOpen) {
        successfulCalls.incrementAndGet()
        currentState.successCount++

        // Check if we should close circuit
        if (currentState.successCount >= config.successThreshold) {
            val closedState = CircuitBreakerState.Closed()
            state.set(closedState)
            stateFlow.value = closedState
            Log.i("CircuitBreaker", "Circuit CLOSED after successful recovery")
        }
    }

    private fun recordHalfOpenFailure() {
        failedCalls.incrementAndGet()

        val openState = CircuitBreakerState.Open()
        state.set(openState)
        stateFlow.value = openState
        Log.w("CircuitBreaker", "Circuit re-OPENED after failure in HALF_OPEN")
    }

    private fun shouldOpenCircuit(currentState: CircuitBreakerState.Closed): Boolean {
        if (currentState.failureCount < config.failureThreshold) {
            return false
        }

        val lastFailure = currentState.lastFailureTime ?: return false
        val elapsed = System.currentTimeMillis() - lastFailure

        return elapsed <= config.failureTimeWindow
    }

    private fun shouldRecordException(e: Exception): Boolean {
        // Check if exception should be ignored
        if (config.ignoreExceptions.any { it.isInstance(e) }) {
            return false
        }

        // Check if exception should be recorded
        return config.recordExceptions.isEmpty() ||
            config.recordExceptions.any { it.isInstance(e) }
    }

    fun observeState(): StateFlow<CircuitBreakerState> = stateFlow.asStateFlow()

    fun getMetrics(): CircuitBreakerMetrics {
        val total = totalCalls.get()
        val success = successfulCalls.get()
        return CircuitBreakerMetrics(
            state = state.get(),
            totalCalls = total,
            successfulCalls = success,
            failedCalls = failedCalls.get(),
            rejectedCalls = rejectedCalls.get(),
            successRate = if (total > 0) {
                (success.toDouble() / total) * 100
            } else 0.0
        )
    }

    fun reset() {
        val closed = CircuitBreakerState.Closed()
        state.set(closed)
        stateFlow.value = closed
        totalCalls.set(0)
        successfulCalls.set(0)
        failedCalls.set(0)
        rejectedCalls.set(0)
    }
}

sealed class CircuitBreakerState {
    data class Closed(
        var failureCount: Int = 0,
        var lastFailureTime: Long? = null
    ) : CircuitBreakerState()

    data class Open(
        val openedAt: Long = System.currentTimeMillis()
    ) : CircuitBreakerState() {
        fun shouldAttemptReset(timeout: Long): Boolean {
            return System.currentTimeMillis() - openedAt >= timeout
        }
    }

    data class HalfOpen(
        var successCount: Int = 0,
        var failureCount: Int = 0
    ) : CircuitBreakerState()
}

data class CircuitBreakerMetrics(
    val state: CircuitBreakerState,
    val totalCalls: Long,
    val successfulCalls: Long,
    val failedCalls: Long,
    val rejectedCalls: Long,
    val successRate: Double
)

class CircuitBreakerOpenException(
    message: String,
    cause: Throwable? = null
) : Exception(message, cause)
```

Note: For true thread safety under high concurrency, consider making state transitions purely via compare-and-set on immutable state objects instead of mutating properties on data classes shared across coroutines.

---

## Thread-Safe State Transitions

### Using AtomicReference and Mutex (conceptual example)

```kotlin
class ThreadSafeCircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    // AtomicReference for lock-free reads
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())

    // Mutex for coordinated state transitions
    private val transitionMutex = Mutex()

    suspend fun <T> execute(operation: suspend () -> T): T {
        val currentState = state.get()
        return when (currentState) {
            is CircuitBreakerState.Closed -> executeInClosed(operation, currentState)
            is CircuitBreakerState.Open -> executeInOpen(operation, currentState)
            is CircuitBreakerState.HalfOpen -> executeInHalfOpen(operation, currentState)
        }
    }

    private suspend fun <T> executeInClosed(
        operation: suspend () -> T,
        current: CircuitBreakerState.Closed
    ): T {
        return try {
            val result = operation()
            // on success, reset counters
            current.failureCount = 0
            current.lastFailureTime = null
            result
        } catch (e: Exception) {
            current.failureCount++
            current.lastFailureTime = System.currentTimeMillis()
            if (current.failureCount >= config.failureThreshold) {
                val open = CircuitBreakerState.Open()
                if (state.compareAndSet(current, open)) {
                    // transitioned to OPEN
                }
            }
            throw e
        }
    }

    private suspend fun <T> executeInOpen(
        operation: suspend () -> T,
        current: CircuitBreakerState.Open
    ): T {
        if (current.shouldAttemptReset(config.resetTimeout)) {
            return transitionToHalfOpen(operation)
        }
        throw CircuitBreakerOpenException("Circuit is OPEN")
    }

    private suspend fun <T> executeInHalfOpen(
        operation: suspend () -> T,
        current: CircuitBreakerState.HalfOpen
    ): T = transitionMutex.withLock {
        try {
            val result = operation()
            current.successCount++
            if (current.successCount >= config.successThreshold) {
                state.compareAndSet(current, CircuitBreakerState.Closed())
            }
            result
        } catch (e: Exception) {
            state.compareAndSet(current, CircuitBreakerState.Open())
            throw e
        }
    }

    private suspend fun <T> transitionToHalfOpen(operation: suspend () -> T): T {
        transitionMutex.withLock {
            val current = state.get()
            if (current is CircuitBreakerState.Open &&
                current.shouldAttemptReset(config.resetTimeout)
            ) {
                state.compareAndSet(current, CircuitBreakerState.HalfOpen())
            }
        }
        return execute(operation)
    }
}
```

### CompareAndSet for State Updates

```kotlin
// Atomic state update with retry
private fun updateStateAtomically(
    state: AtomicReference<CircuitBreakerState>,
    expectedState: CircuitBreakerState,
    newState: CircuitBreakerState
): Boolean {
    return state.compareAndSet(expectedState, newState)
}

// Usage example
private fun openCircuit(
    state: AtomicReference<CircuitBreakerState>,
    currentState: CircuitBreakerState.Closed
) {
    val openState = CircuitBreakerState.Open()

    if (state.compareAndSet(currentState, openState)) {
        Log.i("CircuitBreaker", "Successfully transitioned to OPEN")
        // notifyStateChange(openState)
    } else {
        Log.w("CircuitBreaker", "State changed during transition, retry if needed")
    }
}
```

---

## Complete API Client with Circuit Breaker

### Retrofit API with Circuit Breaker Wrapper

```kotlin
interface PaymentApi {
    @POST("payments")
    suspend fun processPayment(@Body payment: PaymentRequest): PaymentResponse

    @GET("payments/{id}")
    suspend fun getPaymentStatus(@Path("id") paymentId: String): PaymentStatus
}

data class PaymentRequest(/* fields */)
data class PaymentResponse(/* fields */)
data class PaymentStatus(/* fields */)

sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()
}

class PaymentService(
    private val api: PaymentApi,
    private val circuitBreaker: CircuitBreaker
) {
    suspend fun processPayment(payment: PaymentRequest): Result<PaymentResponse> {
        return try {
            val response = circuitBreaker.execute {
                api.processPayment(payment)
            }
            Result.Success(response)
        } catch (e: CircuitBreakerOpenException) {
            // Circuit is open - fail fast
            Result.Error("Payment service is temporarily unavailable. Please try again later.", e)
        } catch (e: Exception) {
            Result.Error("Payment failed: ${e.message}", e)
        }
    }

    suspend fun getPaymentStatus(paymentId: String): Result<PaymentStatus> {
        return try {
            val status = circuitBreaker.execute {
                api.getPaymentStatus(paymentId)
            }
            Result.Success(status)
        } catch (e: CircuitBreakerOpenException) {
            // Try cache or local storage
            getCachedPaymentStatus(paymentId)
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error", e)
        }
    }

    private suspend fun getCachedPaymentStatus(paymentId: String): Result<PaymentStatus> {
        // Fallback to cached data (simplified example)
        return Result.Error("Service unavailable and no cached data")
    }
}
```

### Multiple Circuit Breakers for Different Services

```kotlin
class ApiClientFactory {
    private val paymentCircuitBreaker = CircuitBreaker(
        CircuitBreakerConfig(
            failureThreshold = 3,
            resetTimeout = 30_000,
            successThreshold = 2
        )
    )

    private val userCircuitBreaker = CircuitBreaker(
        CircuitBreakerConfig(
            failureThreshold = 5,
            resetTimeout = 60_000,
            successThreshold = 3
        )
    )

    private val analyticsCircuitBreaker = CircuitBreaker(
        CircuitBreakerConfig(
            failureThreshold = 10,
            resetTimeout = 120_000,
            successThreshold = 1
        )
    )

    fun createPaymentService(api: PaymentApi): PaymentService {
        return PaymentService(api, paymentCircuitBreaker)
    }

    fun createUserService(api: UserApi): UserService {
        return UserService(api, userCircuitBreaker)
    }

    fun createAnalyticsService(api: AnalyticsApi): AnalyticsService {
        return AnalyticsService(api, analyticsCircuitBreaker)
    }
}
```

---

## Combining with Retry and Timeout

### Circuit Breaker + Retry + Timeout

```kotlin
class ResilientApiClient(
    private val api: ApiService,
    private val circuitBreaker: CircuitBreaker,
    private val retryConfig: RetryConfig = RetryConfig()
) {
    suspend fun <T> executeWithResilience(
        operation: suspend () -> T
    ): Result<T> {
        return try {
            // Wrap in circuit breaker
            val result = circuitBreaker.execute {
                // Wrap in timeout
                withTimeout(retryConfig.timeoutMs) {
                    // Wrap in retry logic
                    retryWithBackoff(retryConfig) {
                        operation()
                    }
                }
            }
            Result.Success(result)
        } catch (e: CircuitBreakerOpenException) {
            Result.Error("Service unavailable (circuit open)", e)
        } catch (e: TimeoutCancellationException) {
            Result.Error("Request timeout", e)
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error", e)
        }
    }

    private suspend fun <T> retryWithBackoff(
        config: RetryConfig,
        operation: suspend () -> T
    ): T {
        var currentDelay = config.initialDelay
        var lastException: Exception? = null

        repeat(config.maxAttempts) { attempt ->
            try {
                return operation()
            } catch (e: Exception) {
                lastException = e

                if (attempt == config.maxAttempts - 1) {
                    throw e
                }

                Log.d("Retry", "Attempt ${attempt + 1} failed, retrying in ${currentDelay}ms")
                delay(currentDelay)
                currentDelay = (currentDelay * config.backoffMultiplier)
                    .toLong()
                    .coerceAtMost(config.maxDelay)
            }
        }

        throw lastException ?: Exception("Retry failed")
    }
}

data class RetryConfig(
    val maxAttempts: Int = 3,
    val initialDelay: Long = 1000,
    val maxDelay: Long = 10000,
    val backoffMultiplier: Double = 2.0,
    val timeoutMs: Long = 30000
)
```

### Composite Resilience Pattern (conceptual)

```kotlin
class CompositeResilienceStrategy(
    private val circuitBreaker: CircuitBreaker,
    private val rateLimiter: SimpleRateLimiter,
    private val bulkhead: Bulkhead
) {
    suspend fun <T> execute(operation: suspend () -> T): T {
        // 1. Check rate limiter first
        rateLimiter.acquire()

        // 2. Check bulkhead (concurrent request limit)
        return bulkhead.execute {
            // 3. Execute through circuit breaker
            circuitBreaker.execute {
                operation()
            }
        }
    }
}

// Simplified rate limiter: max N calls per time window.
// For production, avoid holding a mutex across delay loops as below;
// this is intentionally simplified for teaching purposes.
class SimpleRateLimiter(
    private val permitsPerSecond: Int
) {
    private val mutex = Mutex()
    private var availablePermits = permitsPerSecond
    private var lastRefillTime = System.currentTimeMillis()

    suspend fun acquire() {
        mutex.withLock {
            refillIfNeeded()
            while (availablePermits <= 0) {
                val waitTime = 50L
                delay(waitTime)
                refillIfNeeded()
            }
            availablePermits--
        }
    }

    private fun refillIfNeeded() {
        val now = System.currentTimeMillis()
        val elapsedSeconds = (now - lastRefillTime) / 1000
        if (elapsedSeconds > 0) {
            val permitsToAdd = (elapsedSeconds * permitsPerSecond).toInt()
            availablePermits = (availablePermits + permitsToAdd)
                .coerceAtMost(permitsPerSecond)
            lastRefillTime = now
        }
    }
}

// Bulkhead to limit concurrent requests
class Bulkhead(
    private val maxConcurrentCalls: Int
) {
    private val semaphore = kotlinx.coroutines.sync.Semaphore(maxConcurrentCalls)

    suspend fun <T> execute(operation: suspend () -> T): T {
        semaphore.acquire()
        try {
            return operation()
        } finally {
            semaphore.release()
        }
    }
}
```

---

## Monitoring Circuit Breaker State

### Real-Time State Monitoring

```kotlin
class CircuitBreakerMonitor(
    private val circuitBreaker: CircuitBreaker
) {
    fun monitorState(): Flow<CircuitBreakerState> {
        return circuitBreaker.observeState()
    }

    fun monitorMetrics(): Flow<CircuitBreakerMetrics> = flow {
        while (currentCoroutineContext().isActive) {
            emit(circuitBreaker.getMetrics())
            delay(1000) // Emit metrics every second
        }
    }

    suspend fun logStateChanges() {
        circuitBreaker.observeState().collect { state ->
            when (state) {
                is CircuitBreakerState.Closed -> {
                    Log.i("Monitor", "Circuit CLOSED - Service healthy")
                }
                is CircuitBreakerState.Open -> {
                    Log.w("Monitor", "Circuit OPEN - Service unhealthy")
                    // Trigger alert
                    sendAlert("Circuit breaker opened for service")
                }
                is CircuitBreakerState.HalfOpen -> {
                    Log.i("Monitor", "Circuit HALF_OPEN - Testing service recovery")
                }
            }
        }
    }

    private suspend fun sendAlert(message: String) {
        // Send to monitoring system (Datadog, New Relic, etc.)
    }
}
```

### Metrics Dashboard

```kotlin
@Composable
fun CircuitBreakerDashboard(monitor: CircuitBreakerMonitor) {
    val state by monitor.monitorState().collectAsState(initial = CircuitBreakerState.Closed())
    val metrics by monitor.monitorMetrics().collectAsState(
        initial = CircuitBreakerMetrics(
            state = CircuitBreakerState.Closed(),
            totalCalls = 0,
            successfulCalls = 0,
            failedCalls = 0,
            rejectedCalls = 0,
            successRate = 0.0
        )
    )

    Column(modifier = Modifier.padding(16.dp)) {
        // State indicator
        StateIndicator(state)

        Spacer(modifier = Modifier.height(16.dp))

        // Metrics
        MetricsCard(metrics)

        Spacer(modifier = Modifier.height(16.dp))

        // Success rate chart
        SuccessRateChart(metrics.successRate)
    }
}

@Composable
fun StateIndicator(state: CircuitBreakerState) {
    val (text, color) = when (state) {
        is CircuitBreakerState.Closed -> "CLOSED" to Color.Green
        is CircuitBreakerState.Open -> "OPEN" to Color.Red
        is CircuitBreakerState.HalfOpen -> "HALF-OPEN" to Color.Yellow
    }

    Card(
        backgroundColor = color.copy(alpha = 0.2f),
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(
            text = "Circuit Breaker: $text",
            modifier = Modifier.padding(16.dp),
            style = MaterialTheme.typography.h6,
            color = color
        )
    }
}
```

---

## Production Metrics

Key metrics to track in production:
- Number of calls, success/failure/rejected counts
- Success rate
- Time spent in each state (Closed/Open/Half-Open)
- Frequency of state transitions
- Per-service circuit breaker statistics

Use these metrics to:
- Tune `failureThreshold`, `failureTimeWindow`, `resetTimeout`, `successThreshold`
- Detect unstable downstream dependencies early
- Drive alerts when circuits stay OPEN too long

---

## Testing with Simulated Failures

Recommended approaches:
- Unit tests: inject a fake or stubbed dependency that consistently fails to trigger OPEN and HALF_OPEN transitions.
- Use virtual time or controllable clocks to test timeout and reset behavior.
- Integration tests: run against a test service that you can force to return errors/timeouts.
- Chaos testing: periodically inject failures in non-production/staging to validate behavior.

---

## Resilience4j Comparison

Resilience4j provides battle-tested implementations of circuit breaker, retry, bulkhead, and rate limiter.
Key comparison points for a custom coroutine-based implementation:
- Fine-tuned for your specific use cases and coroutine context.
- You control state model, metrics, and integration with your logging/monitoring.
- But you must carefully test: state transitions, race conditions, backpressure, and metrics.

When possible, prefer a well-tested library (like Resilience4j with Kotlin interop) for production unless you have specific constraints.

---

## Real Example: Payment Service

A typical payment flow:
- Wrap calls to external payment gateway with a circuit breaker.
- Configure aggressive thresholds (low `failureThreshold`, sensible `resetTimeout`).
- On OPEN:
  - Fail fast API calls.
  - Show clear message to user.
  - Optionally place payment into a "pending" queue.
- On HALF_OPEN:
  - Allow a few test charges.
  - If they succeed, close the circuit.
  - If they fail, re-open and alert on-call team.

This ensures:
- The rest of your system remains responsive.
- You do not overload a degraded payment provider.
- You have clear observability into payment stability.

---

## Best Practices

- Use separate circuit breakers per dependency (per endpoint or logical group), not a global one.
- Combine with retry, timeout, bulkhead, and rate limiting.
- Use metrics and logs to tune thresholds; avoid magic constants without data.
- Implement fallbacks where possible (cache, degraded responses).
- Ensure thread-safe, deterministic state transitions.

---

## When NOT to Use

- For cheap, idempotent operations where occasional retries are harmless.
- For purely in-process calls without network or IO boundaries.
- When underlying libraries already include robust resilience and adding another circuit breaker complicates behavior.

---

## Common Pitfalls

- Too low `failureThreshold` → frequent false openings.
- Ignoring `CircuitBreakerOpenException` without proper fallback.
- One global circuit breaker for very different operations.
- No monitoring or alerting on circuit breaker metrics.

---

## Follow-up Questions

1. What is the difference between circuit breaker and retry pattern?
2. How would you choose `failureThreshold` and `resetTimeout` for different services?
3. How do you keep the implementation thread-safe under high concurrency with coroutines?
4. How would you expose circuit breaker metrics to your monitoring stack?
5. How do you test state transitions deterministically (including time-based)?

---

## References

- Martin Fowler - Circuit Breaker: https://martinfowler.com/bliki/CircuitBreaker.html
- Resilience4j Documentation: https://resilience4j.readme.io/
- Microsoft - Circuit Breaker Pattern: https://learn.microsoft.com/azure/architecture/patterns/circuit-breaker

---

## Related Questions

- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-request-coalescing-deduplication--kotlin--hard]]
- [[q-actor-pattern--kotlin--hard]]

---

# Circuit Breaker Паттерн С Корутинами

[English](#circuit-breaker-pattern-with-coroutines) | **Русский**

---

## Содержание

- [Обзор](#обзор-ru)
- [Определение и мотивация паттерна](#определение-и-мотивация-паттерна)
- [Три состояния](#три-состояния)
- [Диаграмма переходов состояний](#диаграмма-переходов-состояний-ru)
- [Конфигурация порога ошибок](#конфигурация-порога-ошибок)
- [Тайм-ауты и период восстановления](#тайм-ауты-и-период-восстановления)
- [Механизм полуоткрытого состояния](#механизм-полуоткрытого-состояния)
- [Полная реализация](#полная-реализация-ru)
- [Потокобезопасные переходы состояний](#потокобезопасные-переходы-состояний)
- [Полный API клиент с Circuit Breaker](#полный-api-клиент-с-circuit-breaker)
- [Комбинирование с Retry и Timeout](#комбинирование-с-retry-и-timeout)
- [Мониторинг состояния Circuit Breaker](#мониторинг-состояния-circuit-breaker)
- [Несколько Circuit Breakers](#несколько-circuit-breakers)
- [Production метрики](#production-метрики-ru)
- [Тестирование с симуляцией сбоев](#тестирование-с-симуляцией-сбоев)
- [Сравнение с Resilience4j](#сравнение-с-resilience4j)
- [Реальный пример: Payment `Service`](#реальный-пример-payment-service)
- [Лучшие практики](#лучшие-практики-ru)
- [Когда НЕ использовать](#когда-не-использовать)
- [Распространённые ошибки](#распространённые-ошибки-ru)
- [Дополнительные вопросы](#дополнительные-вопросы-ru)
- [Ссылки](#ссылки-ru)
- [Связанные вопросы](#связанные-вопросы-ru)

---

## Обзор {#обзор-ru}

Паттерн circuit breaker предотвращает повторные попытки выполнения операции, которая с высокой вероятностью завершится неудачей, позволяя приложению продолжать работу без ожидания исправления ошибки и лишней траты ресурсов.

Ключевые преимущества:
- Предотвращает каскадные сбои в распределённых системах
- Обеспечивает быстрое обнаружение сбоев и восстановление
- Снижает нагрузку на неработающие сервисы
- Повышает устойчивость и стабильность системы
- Поддерживает плавную деградацию

См. также: [[c-kotlin]], [[c-coroutines]].

---

## Определение И Мотивация Паттерна

### Что Такое Circuit Breaker?

Паттерн circuit breaker вдохновлён электрическими автоматическими выключателями, которые автоматически останавливают ток при обнаружении неисправности.

### Зачем Использовать Circuit Breaker?

Проблема без circuit breaker:

```kotlin
// Без circuit breaker — продолжаем бомбить неработающий сервис
class PaymentService(private val api: PaymentApi) {
    suspend fun processPayment(payment: Payment): Result<PaymentResponse> {
        return try {
            // Сервис лежит, но мы продолжаем попытки
            val response = api.processPayment(payment) // Ждём 30 секунд до тайм-аута
            Result.Success(response)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

// Множество запросов накапливается, все ждут тайм-аута
// Система становится неотзывчивой
```

Решение с circuit breaker:

```kotlin
// С circuit breaker — быстрый отказ, когда сервис недоступен
class PaymentService(
    private val api: PaymentApi,
    private val circuitBreaker: CircuitBreaker
) {
    suspend fun processPayment(payment: Payment): Result<PaymentResponse> {
        return circuitBreaker.execute {
            api.processPayment(payment)
        }
    }
}

// После порога ошибок circuit открывается
// Новые запросы немедленно отклоняются (без ожидания)
// Система остаётся отзывчивой
```

---

## Три Состояния

(Фрагменты иллюстрируют поведение; полную реализацию см. в разделе «Полная реализация».)

### Состояние: Closed (закрыто, Нормальная работа)

```kotlin
sealed class CircuitBreakerState {
    data class Closed(
        var failureCount: Int = 0,
        var lastFailureTime: Long? = null
    ) : CircuitBreakerState()
}
```

Характеристики:
- Все запросы проходят
- Ошибки подсчитываются
- Успешный вызов сбрасывает счётчик ошибок
- При превышении порога → переход в OPEN

### Состояние: Open (открыто, Сервис Не работает)

```kotlin
sealed class CircuitBreakerState {
    data class Open(
        val openedAt: Long = System.currentTimeMillis()
    ) : CircuitBreakerState() {
        fun shouldAttemptReset(timeout: Long): Boolean {
            return System.currentTimeMillis() - openedAt >= timeout
        }
    }
}
```

Характеристики:
- Все запросы немедленно завершаются с ошибкой
- Нет вызовов к backend-сервису
- Порог ошибок достигнут
- После периода тайм-аута → переход в HALF_OPEN

### Состояние: Half-Open (полуоткрыто, тестирование)

```kotlin
sealed class CircuitBreakerState {
    data class HalfOpen(
        var successCount: Int = 0,
        var failureCount: Int = 0
    ) : CircuitBreakerState()
}
```

Характеристики:
- Ограниченное число запросов пропускается
- Проверяется восстановление сервиса
- При достаточном числе успешных вызовов → CLOSED
- При ошибке → обратно в OPEN

---

## Диаграмма Переходов Состояний {#диаграмма-переходов-состояний-ru}

1. CLOSED → OPEN: превышен порог ошибок.
2. OPEN → HALF_OPEN: истёк период тайм-аута.
3. HALF_OPEN → CLOSED: достаточно успешных тестовых запросов.
4. HALF_OPEN → OPEN: тестовый запрос завершился ошибкой.

---

## Конфигурация Порога Ошибок

### Базовая Конфигурация

```kotlin
data class CircuitBreakerConfig(
    // Количество последовательных ошибок перед открытием circuit
    val failureThreshold: Int = 5,

    // Временное окно для подсчёта ошибок (мс)
    val failureTimeWindow: Long = 10_000,

    // Время ожидания перед попыткой восстановления (мс)
    val resetTimeout: Long = 60_000,

    // Количество успешных вызовов для закрытия из half-open
    val successThreshold: Int = 2,

    // Исключения, которые должны триггерить circuit breaker
    val recordExceptions: List<Class<out Exception>> = listOf(
        IOException::class.java,
        TimeoutException::class.java
    ),

    // Исключения, которые НЕ должны триггерить circuit breaker
    val ignoreExceptions: List<Class<out Exception>> = listOf(
        IllegalArgumentException::class.java,
        ValidationException::class.java
    )
)
```

Примечание: пример одновременно упоминает «последовательные ошибки» и окно времени. В реальной реализации нужно явно выбрать модель (последовательные ошибки, скользящее окно и т.п.) и согласованно её реализовать.

### Продвинутая Конфигурация Со Sliding Window

```kotlin
data class AdvancedCircuitBreakerConfig(
    // Тип окна: по количеству вызовов или по времени
    val slidingWindowType: SlidingWindowType = SlidingWindowType.COUNT_BASED,

    // Размер окна
    val slidingWindowSize: Int = 100,

    // Минимальное число вызовов перед расчётом доли ошибок
    val minimumNumberOfCalls: Int = 10,

    // Порог доли ошибок (в процентах)
    val failureRateThreshold: Float = 50f,

    // Порог длительности медленного вызова (мс)
    val slowCallDurationThreshold: Long = 1000,

    // Порог доли медленных вызовов (в процентах)
    val slowCallRateThreshold: Float = 100f,

    // Количество разрешённых вызовов в HALF_OPEN
    val permittedNumberOfCallsInHalfOpenState: Int = 3,

    // Время ожидания в OPEN (мс)
    val waitDurationInOpenState: Long = 60_000
)

enum class SlidingWindowType {
    COUNT_BASED,
    TIME_BASED
}
```

### Разные Конфигурации Для Разных Сервисов

```kotlin
object CircuitBreakerConfigs {
    // Критичный сервис — быстрый отказ
    val payment = CircuitBreakerConfig(
        failureThreshold = 3,
        failureTimeWindow = 5_000,
        resetTimeout = 30_000,
        successThreshold = 3
    )

    // Некритичный сервис — больше допусков
    val analytics = CircuitBreakerConfig(
        failureThreshold = 10,
        failureTimeWindow = 30_000,
        resetTimeout = 120_000,
        successThreshold = 1
    )

    // Внешний сервис — ещё более толерантный
    val thirdParty = CircuitBreakerConfig(
        failureThreshold = 5,
        failureTimeWindow = 60_000,
        resetTimeout = 300_000,
        successThreshold = 5
    )
}
```

---

## Тайм-ауты И Период Восстановления

### Конфигурация Тайм-аута

```kotlin
class CircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    // Тайм-аут для перехода OPEN → HALF_OPEN
    private fun shouldAttemptReset(openedAt: Long): Boolean {
        val elapsed = System.currentTimeMillis() - openedAt
        return elapsed >= config.resetTimeout
    }

    // Тайм-аут для операций (делегирует в полную реализацию)
    suspend fun <T> executeWithTimeout(
        timeoutMs: Long = 5000,
        operation: suspend () -> T
    ): T {
        return withTimeout(timeoutMs) {
            execute(operation)
        }
    }

    suspend fun <T> execute(operation: suspend () -> T): T {
        // Упрощённый пример; за полной логикой см. «Полная реализация».
        return operation()
    }
}
```

### Стратегии Периода Восстановления

Примеры ниже концептуальные и не подключены напрямую к классу CircuitBreaker выше.

```kotlin
// Стратегия 1: фиксированная задержка
class FixedDelayRecovery(
    private val delayMs: Long = 60_000
) : RecoveryStrategy {
    override fun getNextDelay(attempt: Int): Long = delayMs
}

// Стратегия 2: экспоненциальная задержка
class ExponentialBackoffRecovery(
    private val initialDelay: Long = 1000,
    private val maxDelay: Long = 300_000,
    private val multiplier: Double = 2.0
) : RecoveryStrategy {
    override fun getNextDelay(attempt: Int): Long {
        val delay = (initialDelay * multiplier.pow(attempt)).toLong()
        return delay.coerceAtMost(maxDelay)
    }
}

// Стратегия 3: jitter (рандомизация)
class JitterRecovery(
    private val baseDelay: Long = 60_000,
    private val maxJitter: Long = 5000
) : RecoveryStrategy {
    override fun getNextDelay(attempt: Int): Long {
        val jitter = Random.nextLong(0, maxJitter)
        return baseDelay + jitter
    }
}

interface RecoveryStrategy {
    fun getNextDelay(attempt: Int): Long
}
```

---

## Механизм Полуоткрытого Состояния

### Реализация (фрагмент)

```kotlin
class CircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val halfOpenLock = Mutex()

    suspend fun <T> execute(operation: suspend () -> T): T {
        val currentState = state.get()
        return when (currentState) {
            is CircuitBreakerState.Closed -> executeInClosedState(operation, currentState)
            is CircuitBreakerState.Open -> executeInOpenState(operation, currentState)
            is CircuitBreakerState.HalfOpen -> executeInHalfOpenState(operation, currentState)
        }
    }

    private suspend fun <T> executeInHalfOpenState(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.HalfOpen
    ): T {
        return halfOpenLock.withLock {
            val latest = state.get()
            if (latest !is CircuitBreakerState.HalfOpen) {
                return execute(operation)
            }

            try {
                val result = operation()
                latest.successCount++

                if (latest.successCount >= config.successThreshold) {
                    val closed = CircuitBreakerState.Closed()
                    state.set(closed)
                    Log.i("CircuitBreaker", "Circuit closed after successful recovery")
                }

                result
            } catch (e: Exception) {
                latest.failureCount++
                val open = CircuitBreakerState.Open()
                state.set(open)
                Log.w("CircuitBreaker", "Circuit re-opened after failure in half-open state")
                // В этом фрагменте оборачиваем как CircuitBreakerOpenException;
                // в полной реализации ниже ошибка пробрасывается как есть.
                throw CircuitBreakerOpenException("Circuit breaker re-opened", e)
            }
        }
    }
}
```

Важно: в реальной реализации выберите единообразное поведение для ошибок в HALF_OPEN (либо всегда `CircuitBreakerOpenException`, либо оригинальное исключение), чтобы вызывающий код мог детерминированно их обрабатывать.

---

## Полная Реализация {#полная-реализация-ru}

### Полный Класс CircuitBreaker

```kotlin
class CircuitBreaker(
    private val config: CircuitBreakerConfig = CircuitBreakerConfig()
) {
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val stateFlow = MutableStateFlow<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val mutex = Mutex()

    // Метрики
    private val totalCalls = AtomicLong(0)
    private val successfulCalls = AtomicLong(0)
    private val failedCalls = AtomicLong(0)
    private val rejectedCalls = AtomicLong(0)

    suspend fun <T> execute(operation: suspend () -> T): T {
        totalCalls.incrementAndGet()

        val currentState = state.get()

        return when (currentState) {
            is CircuitBreakerState.Closed -> {
                executeInClosedState(operation, currentState)
            }
            is CircuitBreakerState.Open -> {
                executeInOpenState(operation, currentState)
            }
            is CircuitBreakerState.HalfOpen -> {
                executeInHalfOpenState(operation, currentState)
            }
        }
    }

    private suspend fun <T> executeInClosedState(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.Closed
    ): T {
        return try {
            val result = operation()
            recordSuccess(currentState)
            result
        } catch (e: Exception) {
            if (shouldRecordException(e)) {
                recordFailure(currentState)
            }
            throw e
        }
    }

    private suspend fun <T> executeInOpenState(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.Open
    ): T {
        if (currentState.shouldAttemptReset(config.resetTimeout)) {
            return transitionToHalfOpen(operation)
        }

        rejectedCalls.incrementAndGet()
        throw CircuitBreakerOpenException(
            "Circuit breaker is OPEN. Service is unavailable."
        )
    }

    private suspend fun <T> executeInHalfOpenState(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.HalfOpen
    ): T = mutex.withLock {
        try {
            val result = operation()
            recordHalfOpenSuccess(currentState)
            result
        } catch (e: Exception) {
            recordHalfOpenFailure()
            throw e
        }
    }

    private suspend fun <T> transitionToHalfOpen(operation: suspend () -> T): T {
        mutex.withLock {
            val currentState = state.get()
            if (currentState is CircuitBreakerState.Open &&
                currentState.shouldAttemptReset(config.resetTimeout)
            ) {
                val halfOpenState = CircuitBreakerState.HalfOpen()
                state.set(halfOpenState)
                stateFlow.value = halfOpenState
                Log.i("CircuitBreaker", "Transitioned to HALF_OPEN")
            }
        }

        return execute(operation)
    }

    private fun recordSuccess(currentState: CircuitBreakerState.Closed) {
        successfulCalls.incrementAndGet()
        currentState.failureCount = 0
        currentState.lastFailureTime = null
    }

    private fun recordFailure(currentState: CircuitBreakerState.Closed) {
        failedCalls.incrementAndGet()
        currentState.failureCount++
        currentState.lastFailureTime = System.currentTimeMillis()

        if (shouldOpenCircuit(currentState)) {
            val openState = CircuitBreakerState.Open()
            state.set(openState)
            stateFlow.value = openState
            Log.w("CircuitBreaker", "Circuit OPENED after ${currentState.failureCount} failures")
        }
    }

    private fun recordHalfOpenSuccess(currentState: CircuitBreakerState.HalfOpen) {
        successfulCalls.incrementAndGet()
        currentState.successCount++

        if (currentState.successCount >= config.successThreshold) {
            val closedState = CircuitBreakerState.Closed()
            state.set(closedState)
            stateFlow.value = closedState
            Log.i("CircuitBreaker", "Circuit CLOSED after successful recovery")
        }
    }

    private fun recordHalfOpenFailure() {
        failedCalls.incrementAndGet()

        val openState = CircuitBreakerState.Open()
        state.set(openState)
        stateFlow.value = openState
        Log.w("CircuitBreaker", "Circuit re-OPENED after failure in HALF_OPEN")
    }

    private fun shouldOpenCircuit(currentState: CircuitBreakerState.Closed): Boolean {
        if (currentState.failureCount < config.failureThreshold) {
            return false
        }

        val lastFailure = currentState.lastFailureTime ?: return false
        val elapsed = System.currentTimeMillis() - lastFailure

        return elapsed <= config.failureTimeWindow
    }

    private fun shouldRecordException(e: Exception): Boolean {
        if (config.ignoreExceptions.any { it.isInstance(e) }) {
            return false
        }

        return config.recordExceptions.isEmpty() ||
            config.recordExceptions.any { it.isInstance(e) }
    }

    fun observeState(): StateFlow<CircuitBreakerState> = stateFlow.asStateFlow()

    fun getMetrics(): CircuitBreakerMetrics {
        val total = totalCalls.get()
        val success = successfulCalls.get()
        return CircuitBreakerMetrics(
            state = state.get(),
            totalCalls = total,
            successfulCalls = success,
            failedCalls = failedCalls.get(),
            rejectedCalls = rejectedCalls.get(),
            successRate = if (total > 0) {
                (success.toDouble() / total) * 100
            } else 0.0
        )
    }

    fun reset() {
        val closed = CircuitBreakerState.Closed()
        state.set(closed)
        stateFlow.value = closed
        totalCalls.set(0)
        successfulCalls.set(0)
        failedCalls.set(0)
        rejectedCalls.set(0)
    }
}

data class CircuitBreakerMetrics(
    val state: CircuitBreakerState,
    val totalCalls: Long,
    val successfulCalls: Long,
    val failedCalls: Long,
    val rejectedCalls: Long,
    val successRate: Double
)

class CircuitBreakerOpenException(
    message: String,
    cause: Throwable? = null
) : Exception(message, cause)
```

Примечание: для настоящей потокобезопасности под высокой нагрузкой стоит использовать неизменяемые состояния и `compareAndSet` вместо мутации полей `failureCount`/`successCount` у разделяемых объектов.

---

## Потокобезопасные Переходы Состояний

### Использование AtomicReference И Mutex

```kotlin
class ThreadSafeCircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val transitionMutex = Mutex()

    suspend fun <T> execute(operation: suspend () -> T): T {
        val currentState = state.get()
        return when (currentState) {
            is CircuitBreakerState.Closed -> executeInClosed(operation, currentState)
            is CircuitBreakerState.Open -> executeInOpen(operation, currentState)
            is CircuitBreakerState.HalfOpen -> executeInHalfOpen(operation, currentState)
        }
    }

    private suspend fun <T> executeInClosed(
        operation: suspend () -> T,
        current: CircuitBreakerState.Closed
    ): T {
        return try {
            val result = operation()
            current.failureCount = 0
            current.lastFailureTime = null
            result
        } catch (e: Exception) {
            current.failureCount++
            current.lastFailureTime = System.currentTimeMillis()
            if (current.failureCount >= config.failureThreshold) {
                val open = CircuitBreakerState.Open()
                if (state.compareAndSet(current, open)) {
                    // переход в OPEN
                }
            }
            throw e
        }
    }

    private suspend fun <T> executeInOpen(
        operation: suspend () -> T,
        current: CircuitBreakerState.Open
    ): T {
        if (current.shouldAttemptReset(config.resetTimeout)) {
            return transitionToHalfOpen(operation)
        }
        throw CircuitBreakerOpenException("Circuit is OPEN")
    }

    private suspend fun <T> executeInHalfOpen(
        operation: suspend () -> T,
        current: CircuitBreakerState.HalfOpen
    ): T = transitionMutex.withLock {
        try {
            val result = operation()
            current.successCount++
            if (current.successCount >= config.successThreshold) {
                state.compareAndSet(current, CircuitBreakerState.Closed())
            }
            result
        } catch (e: Exception) {
            state.compareAndSet(current, CircuitBreakerState.Open())
            throw e
        }
    }

    private suspend fun <T> transitionToHalfOpen(operation: suspend () -> T): T {
        transitionMutex.withLock {
            val current = state.get()
            if (current is CircuitBreakerState.Open &&
                current.shouldAttemptReset(config.resetTimeout)
            ) {
                state.compareAndSet(current, CircuitBreakerState.HalfOpen())
            }
        }
        return execute(operation)
    }
}
```

---

## Полный API Клиент С Circuit Breaker

### Retrofit API С Обёрткой Circuit Breaker

```kotlin
interface PaymentApi {
    @POST("payments")
    suspend fun processPayment(@Body payment: PaymentRequest): PaymentResponse

    @GET("payments/{id}")
    suspend fun getPaymentStatus(@Path("id") paymentId: String): PaymentStatus
}

data class PaymentRequest(/* поля */)
data class PaymentResponse(/* поля */)
data class PaymentStatus(/* поля */)

sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()
}

class PaymentService(
    private val api: PaymentApi,
    private val circuitBreaker: CircuitBreaker
) {
    suspend fun processPayment(payment: PaymentRequest): Result<PaymentResponse> {
        return try {
            val response = circuitBreaker.execute {
                api.processPayment(payment)
            }
            Result.Success(response)
        } catch (e: CircuitBreakerOpenException) {
            Result.Error("Сервис платежей временно недоступен. Попробуйте позже.", e)
        } catch (e: Exception) {
            Result.Error("Платёж не прошёл: ${e.message}", e)
        }
    }

    suspend fun getPaymentStatus(paymentId: String): Result<PaymentStatus> {
        return try {
            val status = circuitBreaker.execute {
                api.getPaymentStatus(paymentId)
            }
            Result.Success(status)
        } catch (e: CircuitBreakerOpenException) {
            getCachedPaymentStatus(paymentId)
        } catch (e: Exception) {
            Result.Error(e.message ?: "Неизвестная ошибка", e)
        }
    }

    private suspend fun getCachedPaymentStatus(paymentId: String): Result<PaymentStatus> {
        return Result.Error("Сервис недоступен и нет кешированных данных")
    }
}
```

---

## Комбинирование С Retry И Timeout

### Circuit Breaker + Retry + Timeout (RU)

```kotlin
class ResilientApiClient(
    private val api: ApiService,
    private val circuitBreaker: CircuitBreaker,
    private val retryConfig: RetryConfig = RetryConfig()
) {
    suspend fun <T> executeWithResilience(
        operation: suspend () -> T
    ): Result<T> {
        return try {
            val result = circuitBreaker.execute {
                withTimeout(retryConfig.timeoutMs) {
                    retryWithBackoff(retryConfig) {
                        operation()
                    }
                }
            }
            Result.Success(result)
        } catch (e: CircuitBreakerOpenException) {
            Result.Error("Сервис недоступен (circuit открыт)", e)
        } catch (e: TimeoutCancellationException) {
            Result.Error("Тайм-аут запроса", e)
        } catch (e: Exception) {
            Result.Error(e.message ?: "Неизвестная ошибка", e)
        }
    }

    private suspend fun <T> retryWithBackoff(
        config: RetryConfig,
        operation: suspend () -> T
    ): T {
        var currentDelay = config.initialDelay
        var lastException: Exception? = null

        repeat(config.maxAttempts) { attempt ->
            try {
                return operation()
            } catch (e: Exception) {
                lastException = e

                if (attempt == config.maxAttempts - 1) {
                    throw e
                }

                Log.d("Retry", "Попытка ${attempt + 1} не удалась, повтор через ${currentDelay}мс")
                delay(currentDelay)
                currentDelay = (currentDelay * config.backoffMultiplier)
                    .toLong()
                    .coerceAtMost(config.maxDelay)
            }
        }

        throw lastException ?: Exception("Retry завершился неудачей")
    }
}
```

```kotlin
data class RetryConfig(
    val maxAttempts: Int = 3,
    val initialDelay: Long = 1000,
    val maxDelay: Long = 10000,
    val backoffMultiplier: Double = 2.0,
    val timeoutMs: Long = 30000
)
```

---

## Мониторинг Состояния Circuit Breaker

### Онлайн-мониторинг Состояния (RU)

```kotlin
class CircuitBreakerMonitor(
    private val circuitBreaker: CircuitBreaker
) {
    fun monitorState(): Flow<CircuitBreakerState> {
        return circuitBreaker.observeState()
    }

    fun monitorMetrics(): Flow<CircuitBreakerMetrics> = flow {
        while (currentCoroutineContext().isActive) {
            emit(circuitBreaker.getMetrics())
            delay(1000)
        }
    }

    suspend fun logStateChanges() {
        circuitBreaker.observeState().collect { state ->
            when (state) {
                is CircuitBreakerState.Closed -> {
                    Log.i("Monitor", "Circuit CLOSED - сервис здоров")
                }
                is CircuitBreakerState.Open -> {
                    Log.w("Monitor", "Circuit OPEN - проблемы с сервисом")
                    sendAlert("Circuit breaker открыт для сервиса")
                }
                is CircuitBreakerState.HalfOpen -> {
                    Log.i("Monitor", "Circuit HALF_OPEN - тестируем восстановление")
                }
            }
        }
    }

    private suspend fun sendAlert(message: String) {
        // Интеграция с системой мониторинга
    }
}
```

### Дэшборд Метрик (RU)

```kotlin
@Composable
fun CircuitBreakerDashboard(monitor: CircuitBreakerMonitor) {
    val state by monitor.monitorState().collectAsState(initial = CircuitBreakerState.Closed())
    val metrics by monitor.monitorMetrics().collectAsState(
        initial = CircuitBreakerMetrics(
            state = CircuitBreakerState.Closed(),
            totalCalls = 0,
            successfulCalls = 0,
            failedCalls = 0,
            rejectedCalls = 0,
            successRate = 0.0
        )
    )

    Column(modifier = Modifier.padding(16.dp)) {
        StateIndicator(state)
        Spacer(modifier = Modifier.height(16.dp))
        MetricsCard(metrics)
        Spacer(modifier = Modifier.height(16.dp))
        SuccessRateChart(metrics.successRate)
    }
}
```

---

## Production Метрики {#production-метрики-ru}

Рекомендуемые метрики:
- Общее число вызовов, успешных, неуспешных, отклонённых
- Доля успешных вызовов
- Время в состояниях Closed/Open/Half-Open
- Частота переходов состояний
- Отдельные метрики по каждому circuit breaker/сервису

Используйте метрики для настройки порогов (`failureThreshold`, `failureTimeWindow`, `resetTimeout`, `successThreshold`) и раннего обнаружения нестабильных зависимостей.

---

## Тестирование С Симуляцией Сбоев {#тестирование-с-симуляцией-сбоев}

Подходы:
- Unit-тесты с заглушками, которые всегда падают, чтобы проверить переход в OPEN и HALF_OPEN.
- Управляемое время (virtual time) для тестирования тайм-аутов и периодов восстановления.
- Интеграционные тесты против тестового сервиса с принудительными ошибками и тайм-аутами.
- Chaos-тестирование в стейджинге для проверки поведения под сбоями.

---

## Сравнение С Resilience4j {#сравнение-с-resilience4j}

Resilience4j предоставляет готовые реализации circuit breaker, retry, bulkhead и rate limiter.
Сравнение с собственной реализацией на корутинах:
- Своя реализация точнее учитывает контекст корутин и особенности проекта.
- Полный контроль над моделью состояний, метриками, логированием.
- Но требуется тщательное тестирование переходов состояний, гонок и метрик.

В продакшене при отсутствии особых требований стоит рассматривать использование проверенной библиотеки.

---

## Реальный Пример: Payment Service {#реальный-пример-payment-service}

Типичный сценарий:
- Оборачиваем вызовы внешнего платёжного провайдера в circuit breaker.
- Настраиваем агрессивные пороги (низкий `failureThreshold`, разумный `resetTimeout`).
- В состоянии OPEN:
  - Быстро отклоняем запросы.
  - Показываем пользователю понятное сообщение.
  - При необходимости отправляем транзакции в очередь "pending".
- В HALF_OPEN:
  - Разрешаем ограниченное число тестовых платежей.
  - При успехе — закрываем circuit.
  - При ошибках — снова открываем и шлём алерты.

Это защищает систему от перегрузки и даёт прозрачность состояния платёжного сервиса.

---

## Лучшие Практики {#лучшие-практики-ru}

- Отдельный circuit breaker на каждую внешнюю зависимость или группу похожих операций.
- Комбинация с retry, timeout, bulkhead и rate limiting.
- Настройка порогов на основе метрик.
- Наличие fallback-стратегий (кеш, деградация функциональности).
- Потокобезопасные и предсказуемые переходы состояний.

---

## Когда НЕ Использовать {#когда-не-использовать}

- Для дешёвых, идемпотентных операций, где повторы безопасны.
- Для локальных вызовов в пределах одного процесса.
- Когда сторонняя библиотека уже надёжно обрабатывает сбои и дополнительный circuit breaker усложняет поведение.

---

## Распространённые Ошибки {#распространённые-ошибки-ru}

- Слишком низкий порог ошибок → частые ложные срабатывания.
- Игнорирование `CircuitBreakerOpenException` без fallback.
- Один общий circuit breaker для разных по критичности операций.
- Отсутствие мониторинга и алертов по состояниям circuit breaker.

---

## Дополнительные Вопросы {#дополнительные-вопросы-ru}

1. В чём разница между circuit breaker и retry паттерном?
2. Как подобрать `failureThreshold` и `resetTimeout` для разных сервисов?
3. Как обеспечить потокобезопасность реализации под высокой нагрузкой с корутинами?
4. Как экспортировать метрики circuit breaker в систему мониторинга?
5. Как детерминированно тестировать переходы состояний, включая зависящие от времени?

---

## Ссылки {#ссылки-ru}

- Martin Fowler — Circuit Breaker: https://martinfowler.com/bliki/CircuitBreaker.html
- Resilience4j Documentation: https://resilience4j.readme.io/
- Microsoft — Circuit Breaker Pattern: https://learn.microsoft.com/azure/architecture/patterns/circuit-breaker

---

## Связанные Вопросы {#связанные-вопросы-ru}

- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-request-coalescing-deduplication--kotlin--hard]]
- [[q-actor-pattern--kotlin--hard]]

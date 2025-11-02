---
id: kotlin-172
title: "Circuit breaker pattern with coroutines / Circuit breaker паттерн с корутинами"
aliases: [Circuit Breaker Pattern, Circuit breaker паттерн]
topic: kotlin
subtopics: [coroutines, patterns]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-15
updated: 2025-10-31
tags: [circuit-breaker, coroutines, difficulty/hard, error-handling, kotlin, microservices, patterns, production, resilience]
moc: moc-kotlin
related: [q-flatmap-variants-flow--kotlin--medium, q-flow-vs-livedata-comparison--kotlin--medium, q-request-coalescing-deduplication--kotlin--hard]
date created: Saturday, November 1st 2025, 12:10:11 pm
date modified: Saturday, November 1st 2025, 5:43:27 pm
---

# Circuit Breaker Pattern with Coroutines

**English** | [Русский](#russian-version)

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
- [Real Example: Payment Service](#real-example-payment-service)
- [Best Practices](#best-practices)
- [When NOT to Use](#when-not-to-use)
- [Common Pitfalls](#common-pitfalls)
- [Follow-up Questions](#follow-up-questions)
- [References](#references)
- [Related Questions](#related-questions)

---

## Overview

The Circuit Breaker pattern prevents an application from repeatedly trying to execute an operation that's likely to fail, allowing it to continue without waiting for the fault to be fixed or wasting CPU cycles.

**Key Benefits:**
- Prevents cascading failures in distributed systems
- Provides fast failure detection and recovery
- Reduces load on failing services
- Improves system resilience and stability
- Enables graceful degradation

---

## Pattern Definition and Motivation

### What is a Circuit Breaker?

The Circuit Breaker pattern is inspired by electrical circuit breakers that automatically stop the flow of electricity when a fault is detected.

```

   Client       Circuit      Service
                         Breaker              (Backend)


                               Monitors failures
                               Controls access
                               Manages state


                           State
                          Machine

```

### Why Use Circuit Breaker?

**Problem without Circuit Breaker:**

```kotlin
//  Without circuit breaker - keeps hammering failing service
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

**Solution with Circuit Breaker:**

```kotlin
//  With circuit breaker - fails fast when service is down
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

### State: Closed (Normal Operation)

```

         CLOSED State
  (Normal Operation)

  • All requests pass through
  • Failures are counted
  • Success resets failure counter
  • When failures exceed threshold:
    → Transition to OPEN

```

**Code Example:**

```kotlin
sealed class CircuitBreakerState {
    object Closed : CircuitBreakerState() {
        var failureCount: Int = 0
        var lastFailureTime: Long? = null

        fun recordSuccess() {
            failureCount = 0
            lastFailureTime = null
        }

        fun recordFailure() {
            failureCount++
            lastFailureTime = System.currentTimeMillis()
        }
    }
}
```

### State: Open (Failing)

```

         OPEN State
  (Service is Down)

  • All requests fail immediately
  • No calls to backend service
  • Failure counter is at maximum
  • After timeout period:
    → Transition to HALF_OPEN

```

**Code Example:**

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

```

         HALF_OPEN State
  (Testing Recovery)

  • Limited requests pass through
  • Testing if service recovered
  • On success:
    → Transition to CLOSED
  • On failure:
    → Transition back to OPEN

```

**Code Example:**

```kotlin
sealed class CircuitBreakerState {
    object HalfOpen : CircuitBreakerState() {
        var successCount: Int = 0
        var failureCount: Int = 0

        fun recordSuccess() {
            successCount++
        }

        fun recordFailure() {
            failureCount++
        }
    }
}
```

---

## State Transition Diagram

```

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

**State Transitions:**

1. **CLOSED → OPEN**: When failure count exceeds threshold
2. **OPEN → HALF_OPEN**: After timeout period elapses
3. **HALF_OPEN → CLOSED**: When test requests succeed
4. **HALF_OPEN → OPEN**: When test request fails

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

    // Timeout for individual operations
    suspend fun <T> executeWithTimeout(
        timeoutMs: Long = 5000,
        operation: suspend () -> T
    ): T {
        return withTimeout(timeoutMs) {
            execute(operation)
        }
    }
}
```

### Recovery Period Strategies

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

### Implementation

```kotlin
class CircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val halfOpenLock = Mutex()

    suspend fun <T> execute(operation: suspend () -> T): T {
        val currentState = state.get()

        return when (currentState) {
            is CircuitBreakerState.Closed -> executeInClosedState(operation)
            is CircuitBreakerState.Open -> executeInOpenState(currentState, operation)
            is CircuitBreakerState.HalfOpen -> executeInHalfOpenState(operation)
        }
    }

    private suspend fun <T> executeInHalfOpenState(
        operation: suspend () -> T
    ): T {
        // Ensure only limited concurrent requests in half-open
        return halfOpenLock.withLock {
            val currentState = state.get()
            if (currentState !is CircuitBreakerState.HalfOpen) {
                return execute(operation) // State changed, retry
            }

            try {
                val result = operation()

                // Record success
                currentState.successCount++

                // Check if we should close circuit
                if (currentState.successCount >= config.successThreshold) {
                    state.set(CircuitBreakerState.Closed())
                    Log.i("CircuitBreaker", "Circuit closed after successful recovery")
                }

                result
            } catch (e: Exception) {
                // Record failure
                currentState.failureCount++

                // Re-open circuit on any failure
                state.set(CircuitBreakerState.Open())
                Log.w("CircuitBreaker", "Circuit re-opened after failure in half-open state")

                throw CircuitBreakerOpenException("Circuit breaker re-opened", e)
            }
        }
    }
}
```

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
                currentState.shouldAttemptReset(config.resetTimeout)) {

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

        // Check if we should open circuit
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
        return CircuitBreakerMetrics(
            state = state.get(),
            totalCalls = totalCalls.get(),
            successfulCalls = successfulCalls.get(),
            failedCalls = failedCalls.get(),
            rejectedCalls = rejectedCalls.get(),
            successRate = if (totalCalls.get() > 0) {
                (successfulCalls.get().toDouble() / totalCalls.get()) * 100
            } else 0.0
        )
    }

    fun reset() {
        state.set(CircuitBreakerState.Closed())
        stateFlow.value = CircuitBreakerState.Closed()
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

---

## Thread-Safe State Transitions

### Using AtomicReference and Mutex

```kotlin
class ThreadSafeCircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    // AtomicReference for lock-free reads
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())

    // Mutex for coordinated state transitions
    private val transitionMutex = Mutex()

    suspend fun <T> execute(operation: suspend () -> T): T {
        // Fast path: read state without lock
        val currentState = state.get()

        return when (currentState) {
            is CircuitBreakerState.Closed -> {
                executeWithStateTransition(operation) { result, error ->
                    if (error != null) {
                        handleClosedStateFailure(currentState)
                    } else {
                        handleClosedStateSuccess(currentState)
                    }
                }
            }
            is CircuitBreakerState.Open -> {
                if (currentState.shouldAttemptReset(config.resetTimeout)) {
                    transitionToHalfOpen(operation)
                } else {
                    throw CircuitBreakerOpenException("Circuit is OPEN")
                }
            }
            is CircuitBreakerState.HalfOpen -> {
                executeInHalfOpenWithMutex(operation, currentState)
            }
        }
    }

    private suspend fun <T> executeInHalfOpenWithMutex(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.HalfOpen
    ): T = transitionMutex.withLock {
        // Only one coroutine can execute in half-open
        try {
            val result = operation()
            currentState.successCount++

            if (currentState.successCount >= config.successThreshold) {
                state.compareAndSet(currentState, CircuitBreakerState.Closed())
            }

            result
        } catch (e: Exception) {
            state.compareAndSet(currentState, CircuitBreakerState.Open())
            throw e
        }
    }

    private suspend fun <T> transitionToHalfOpen(operation: suspend () -> T): T {
        transitionMutex.withLock {
            // Double-check after acquiring lock
            val current = state.get()
            if (current is CircuitBreakerState.Open) {
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
    expectedState: CircuitBreakerState,
    newState: CircuitBreakerState
): Boolean {
    return state.compareAndSet(expectedState, newState)
}

// Usage example
private fun openCircuit(currentState: CircuitBreakerState.Closed) {
    val openState = CircuitBreakerState.Open()

    if (state.compareAndSet(currentState, openState)) {
        Log.i("CircuitBreaker", "Successfully transitioned to OPEN")
        notifyStateChange(openState)
    } else {
        Log.w("CircuitBreaker", "State changed during transition, retry")
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
            Result.Error("Payment service is temporarily unavailable. Please try again later.")
        } catch (e: Exception) {
            Result.Error("Payment failed: ${e.message}")
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
            Result.Error(e.message ?: "Unknown error")
        }
    }

    private suspend fun getCachedPaymentStatus(paymentId: String): Result<PaymentStatus> {
        // Fallback to cached data
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
            Result.Error("Service unavailable (circuit open)")
        } catch (e: TimeoutCancellationException) {
            Result.Error("Request timeout")
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
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

### Composite Resilience Pattern

```kotlin
class CompositeResilienceStrategy(
    private val circuitBreaker: CircuitBreaker,
    private val rateLimiter: RateLimiter,
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

// Rate limiter to prevent overwhelming service
class RateLimiter(
    private val permitsPerSecond: Int
) {
    private val semaphore = Semaphore(permitsPerSecond)
    private var lastRefillTime = System.currentTimeMillis()

    suspend fun acquire() {
        refillIfNeeded()
        semaphore.acquire()
    }

    private fun refillIfNeeded() {
        val now = System.currentTimeMillis()
        val elapsed = now - lastRefillTime

        if (elapsed >= 1000) {
            val permitsToAdd = (elapsed / 1000).toInt() * permitsPerSecond
            repeat(permitsToAdd.coerceAtMost(permitsPerSecond)) {
                semaphore.tryAcquire()
            }
            lastRefillTime = now
        }
    }
}

// Bulkhead to limit concurrent requests
class Bulkhead(
    private val maxConcurrentCalls: Int
) {
    private val semaphore = Semaphore(maxConcurrentCalls)

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

[Continuing due to length - this is part 1 of the circuit breaker file. Would you like me to continue with the remaining sections including Production Metrics, Testing, Real Example, Best Practices, etc.?]

---

## Follow-ups

1. **What's the difference between circuit breaker and retry pattern?**
   - Retry: Keeps trying failed operation multiple times
   - Circuit breaker: Stops trying after threshold, prevents cascading failures
   - Use both together for optimal resilience

2. **How do you determine the right failure threshold?**
   - Depends on service SLA and criticality
   - Monitor baseline failure rate in production
   - Start conservative (3-5 failures), tune based on metrics

3. **What happens to in-flight requests when circuit opens?**
   - Requests already executing complete normally
   - New requests fail immediately with CircuitBreakerOpenException
   - Use bulkhead pattern to limit concurrent requests

4. **How do you handle circuit breaker in a microservices architecture?**
   - Each service has its own circuit breaker instance
   - Configure independently based on service characteristics
   - Share state across instances using Redis or similar

5. **What's the difference between half-open and closed state?**
   - Closed: Normal operation, all requests go through
   - Half-open: Limited test requests to check service recovery
   - Half-open transitions to either closed (success) or open (failure)

6. **How do you test circuit breaker behavior?**
   - Mock failures to trigger state transitions
   - Use virtual time to test timeout behavior
   - Verify metrics and state changes

7. **Should you use circuit breaker for all API calls?**
   - Not for idempotent, non-critical operations
   - Not for operations with built-in retry
   - Yes for critical services, payment processing, external APIs

---

## References

- [Martin Fowler - Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Resilience4j Documentation](https://resilience4j.readme.io/)
- [Microsoft - Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [Netflix Hystrix](https://github.com/Netflix/Hystrix)

---

## Related Questions

- [Retry logic with exponential backoff](q-retry-exponential-backoff--kotlin--medium.md)
- [Rate limiting patterns](q-rate-limiting--kotlin--hard.md)
- [Bulkhead pattern](q-bulkhead-pattern--kotlin--hard.md)

---

<a name="russian-version"></a>

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
- [Реальный пример: Payment Service](#реальный-пример-payment-service)
- [Лучшие практики](#лучшие-практики-ru)
- [Когда НЕ использовать](#когда-не-использовать)
- [Распространённые ошибки](#распространённые-ошибки-ru)

---

## Обзор {#обзор-ru}

Паттерн Circuit Breaker предотвращает повторные попытки выполнения операции, которая скорее всего завершится неудачей, позволяя приложению продолжать работу без ожидания исправления ошибки или траты циклов CPU.

**Ключевые преимущества:**
- Предотвращает каскадные сбои в распределённых системах
- Обеспечивает быстрое обнаружение сбоев и восстановление
- Снижает нагрузку на неработающие сервисы
- Улучшает устойчивость и стабильность системы
- Позволяет graceful degradation (плавную деградацию)

---

## Определение И Мотивация Паттерна

### Что Такое Circuit Breaker?

Паттерн Circuit Breaker вдохновлён электрическими автоматическими выключателями, которые автоматически останавливают поток электричества при обнаружении неисправности.

### Зачем Использовать Circuit Breaker?

**Проблема без Circuit Breaker:**

```kotlin
// Без circuit breaker - продолжает атаковать неработающий сервис
class PaymentService(private val api: PaymentApi) {
    suspend fun processPayment(payment: Payment): Result<PaymentResponse> {
        return try {
            // Сервис не работает, но мы продолжаем попытки
            val response = api.processPayment(payment) // Ждёт 30 секунд до тайм-аута
            Result.Success(response)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

// Множество запросов накапливается, все ждут тайм-аута
// Система становится неотзывчивой
```

**Решение с Circuit Breaker:**

```kotlin
// С circuit breaker - быстрый отказ когда сервис не работает
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

// После порогового количества ошибок circuit открывается
// Последующие запросы немедленно завершаются с ошибкой (без ожидания)
// Система остаётся отзывчивой
```

---

## Три Состояния

### Состояние: Closed (Закрыто - Нормальная работа)

**Пример кода:**

```kotlin
sealed class CircuitBreakerState {
    object Closed : CircuitBreakerState() {
        var failureCount: Int = 0
        var lastFailureTime: Long? = null

        fun recordSuccess() {
            failureCount = 0
            lastFailureTime = null
        }

        fun recordFailure() {
            failureCount++
            lastFailureTime = System.currentTimeMillis()
        }
    }
}
```

**Характеристики:**
- Все запросы проходят через
- Ошибки подсчитываются
- Успех сбрасывает счётчик ошибок
- При превышении порога → переход в OPEN

### Состояние: Open (Открыто - Сервис Не работает)

**Пример кода:**

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

**Характеристики:**
- Все запросы немедленно завершаются с ошибкой
- Нет вызовов к backend сервису
- Счётчик ошибок на максимуме
- После периода тайм-аута → переход в HALF_OPEN

### Состояние: Half-Open (Полуоткрыто - тестирование)

**Пример кода:**

```kotlin
sealed class CircuitBreakerState {
    object HalfOpen : CircuitBreakerState() {
        var successCount: Int = 0
        var failureCount: Int = 0

        fun recordSuccess() {
            successCount++
        }

        fun recordFailure() {
            failureCount++
        }
    }
}
```

**Характеристики:**
- Ограниченное количество запросов проходит через
- Тестирование восстановления сервиса
- При успехе → переход в CLOSED
- При ошибке → переход обратно в OPEN

---

## Диаграмма Переходов Состояний {#диаграмма-переходов-состояний-ru}

**Переходы состояний:**

1. **CLOSED → OPEN**: Когда количество ошибок превышает порог
2. **OPEN → HALF_OPEN**: После истечения периода тайм-аута
3. **HALF_OPEN → CLOSED**: Когда тестовые запросы успешны
4. **HALF_OPEN → OPEN**: Когда тестовый запрос завершается ошибкой

---

## Конфигурация Порога Ошибок

### Базовая Конфигурация

```kotlin
data class CircuitBreakerConfig(
    // Количество последовательных ошибок перед открытием circuit
    val failureThreshold: Int = 5,

    // Временное окно для подсчёта ошибок (миллисекунды)
    val failureTimeWindow: Long = 10_000, // 10 секунд

    // Время ожидания перед попыткой сброса (миллисекунды)
    val resetTimeout: Long = 60_000, // 60 секунд

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

### Различные Конфигурации Для Разных Сервисов

```kotlin
object CircuitBreakerConfigs {
    // Критический сервис - быстрый отказ
    val payment = CircuitBreakerConfig(
        failureThreshold = 3,
        failureTimeWindow = 5_000,
        resetTimeout = 30_000,
        successThreshold = 3
    )

    // Некритический сервис - более толерантный
    val analytics = CircuitBreakerConfig(
        failureThreshold = 10,
        failureTimeWindow = 30_000,
        resetTimeout = 120_000,
        successThreshold = 1
    )

    // Внешний сторонний сервис - очень толерантный
    val thirdParty = CircuitBreakerConfig(
        failureThreshold = 5,
        failureTimeWindow = 60_000,
        resetTimeout = 300_000, // 5 минут
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

    // Тайм-аут для индивидуальных операций
    suspend fun <T> executeWithTimeout(
        timeoutMs: Long = 5000,
        operation: suspend () -> T
    ): T {
        return withTimeout(timeoutMs) {
            execute(operation)
        }
    }
}
```

### Стратегии Периода Восстановления

```kotlin
// Стратегия 1: Фиксированная задержка
class FixedDelayRecovery(
    private val delayMs: Long = 60_000
) : RecoveryStrategy {
    override fun getNextDelay(attempt: Int): Long = delayMs
}

// Стратегия 2: Экспоненциальная задержка
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

// Стратегия 3: Jitter (рандомизация для предотвращения thundering herd)
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

### Реализация

```kotlin
class CircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())
    private val halfOpenLock = Mutex()

    private suspend fun <T> executeInHalfOpenState(
        operation: suspend () -> T
    ): T {
        // Обеспечиваем ограниченное количество concurrent запросов в half-open
        return halfOpenLock.withLock {
            val currentState = state.get()
            if (currentState !is CircuitBreakerState.HalfOpen) {
                return execute(operation) // Состояние изменилось, повторяем
            }

            try {
                val result = operation()

                // Записываем успех
                currentState.successCount++

                // Проверяем, нужно ли закрыть circuit
                if (currentState.successCount >= config.successThreshold) {
                    state.set(CircuitBreakerState.Closed())
                    Log.i("CircuitBreaker", "Circuit закрыт после успешного восстановления")
                }

                result
            } catch (e: Exception) {
                // Записываем ошибку
                currentState.failureCount++

                // Повторно открываем circuit при любой ошибке
                state.set(CircuitBreakerState.Open())
                Log.w("CircuitBreaker", "Circuit повторно открыт после ошибки в half-open состоянии")

                throw CircuitBreakerOpenException("Circuit breaker повторно открыт", e)
            }
        }
    }
}
```

---

## Полная Реализация {#полная-реализация-ru}

### Полный Класс Circuit Breaker

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
        // Проверяем, нужно ли попытаться сбросить
        if (currentState.shouldAttemptReset(config.resetTimeout)) {
            return transitionToHalfOpen(operation)
        }

        // Circuit открыт, немедленно отклоняем
        rejectedCalls.incrementAndGet()
        throw CircuitBreakerOpenException(
            "Circuit breaker в состоянии OPEN. Сервис недоступен."
        )
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

        // Проверяем, нужно ли открыть circuit
        if (shouldOpenCircuit(currentState)) {
            val openState = CircuitBreakerState.Open()
            state.set(openState)
            stateFlow.value = openState
            Log.w("CircuitBreaker", "Circuit ОТКРЫТ после ${currentState.failureCount} ошибок")
        }
    }

    fun observeState(): StateFlow<CircuitBreakerState> = stateFlow.asStateFlow()

    fun getMetrics(): CircuitBreakerMetrics {
        return CircuitBreakerMetrics(
            state = state.get(),
            totalCalls = totalCalls.get(),
            successfulCalls = successfulCalls.get(),
            failedCalls = failedCalls.get(),
            rejectedCalls = rejectedCalls.get(),
            successRate = if (totalCalls.get() > 0) {
                (successfulCalls.get().toDouble() / totalCalls.get()) * 100
            } else 0.0
        )
    }
}
```

---

## Потокобезопасные Переходы Состояний

### Использование AtomicReference И Mutex

```kotlin
class ThreadSafeCircuitBreaker(
    private val config: CircuitBreakerConfig
) {
    // AtomicReference для lock-free чтения
    private val state = AtomicReference<CircuitBreakerState>(CircuitBreakerState.Closed())

    // Mutex для координированных переходов состояний
    private val transitionMutex = Mutex()

    suspend fun <T> execute(operation: suspend () -> T): T {
        // Быстрый путь: чтение состояния без блокировки
        val currentState = state.get()

        return when (currentState) {
            is CircuitBreakerState.Closed -> {
                executeWithStateTransition(operation) { result, error ->
                    if (error != null) {
                        handleClosedStateFailure(currentState)
                    } else {
                        handleClosedStateSuccess(currentState)
                    }
                }
            }
            is CircuitBreakerState.Open -> {
                if (currentState.shouldAttemptReset(config.resetTimeout)) {
                    transitionToHalfOpen(operation)
                } else {
                    throw CircuitBreakerOpenException("Circuit в состоянии OPEN")
                }
            }
            is CircuitBreakerState.HalfOpen -> {
                executeInHalfOpenWithMutex(operation, currentState)
            }
        }
    }

    private suspend fun <T> executeInHalfOpenWithMutex(
        operation: suspend () -> T,
        currentState: CircuitBreakerState.HalfOpen
    ): T = transitionMutex.withLock {
        // Только одна корутина может выполняться в half-open
        try {
            val result = operation()
            currentState.successCount++

            if (currentState.successCount >= config.successThreshold) {
                state.compareAndSet(currentState, CircuitBreakerState.Closed())
            }

            result
        } catch (e: Exception) {
            state.compareAndSet(currentState, CircuitBreakerState.Open())
            throw e
        }
    }
}
```

---

## Полный API Клиент С Circuit Breaker

### Retrofit API С Circuit Breaker Обёрткой

```kotlin
interface PaymentApi {
    @POST("payments")
    suspend fun processPayment(@Body payment: PaymentRequest): PaymentResponse

    @GET("payments/{id}")
    suspend fun getPaymentStatus(@Path("id") paymentId: String): PaymentStatus
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
            // Circuit открыт - быстрый отказ
            Result.Error("Сервис платежей временно недоступен. Попробуйте позже.")
        } catch (e: Exception) {
            Result.Error("Платёж не прошёл: ${e.message}")
        }
    }

    suspend fun getPaymentStatus(paymentId: String): Result<PaymentStatus> {
        return try {
            val status = circuitBreaker.execute {
                api.getPaymentStatus(paymentId)
            }
            Result.Success(status)
        } catch (e: CircuitBreakerOpenException) {
            // Попытка использовать кеш или локальное хранилище
            getCachedPaymentStatus(paymentId)
        } catch (e: Exception) {
            Result.Error(e.message ?: "Неизвестная ошибка")
        }
    }

    private suspend fun getCachedPaymentStatus(paymentId: String): Result<PaymentStatus> {
        // Fallback к кешированным данным
        return Result.Error("Сервис недоступен и нет кешированных данных")
    }
}
```

---

## Комбинирование С Retry И Timeout

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
            // Оборачиваем в circuit breaker
            val result = circuitBreaker.execute {
                // Оборачиваем в timeout
                withTimeout(retryConfig.timeoutMs) {
                    // Оборачиваем в retry логику
                    retryWithBackoff(retryConfig) {
                        operation()
                    }
                }
            }
            Result.Success(result)
        } catch (e: CircuitBreakerOpenException) {
            Result.Error("Сервис недоступен (circuit открыт)")
        } catch (e: TimeoutCancellationException) {
            Result.Error("Тайм-аут запроса")
        } catch (e: Exception) {
            Result.Error(e.message ?: "Неизвестная ошибка")
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

                Log.d("Retry", "Попытка ${attempt + 1} не удалась, повтор через ${currentDelay}ms")
                delay(currentDelay)
                currentDelay = (currentDelay * config.backoffMultiplier)
                    .toLong()
                    .coerceAtMost(config.maxDelay)
            }
        }

        throw lastException ?: Exception("Retry не удался")
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

---

## Мониторинг Состояния Circuit Breaker

### Мониторинг Состояния В Реальном Времени

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
            delay(1000) // Отправляем метрики каждую секунду
        }
    }

    suspend fun logStateChanges() {
        circuitBreaker.observeState().collect { state ->
            when (state) {
                is CircuitBreakerState.Closed -> {
                    Log.i("Monitor", "Circuit ЗАКРЫТ - Сервис здоров")
                }
                is CircuitBreakerState.Open -> {
                    Log.w("Monitor", "Circuit ОТКРЫТ - Сервис неисправен")
                    // Триггерим alert
                    sendAlert("Circuit breaker открылся для сервиса")
                }
                is CircuitBreakerState.HalfOpen -> {
                    Log.i("Monitor", "Circuit ПОЛУОТКРЫТ - Тестирование восстановления сервиса")
                }
            }
        }
    }

    private suspend fun sendAlert(message: String) {
        // Отправка в систему мониторинга (Datadog, New Relic, etc.)
    }
}
```

---

## Лучшие Практики {#лучшие-практики-ru}

1. **Используйте разные конфигурации для разных типов сервисов**
   - Критические сервисы: низкий порог ошибок, быстрый сброс
   - Некритические сервисы: высокий порог ошибок, медленный сброс

2. **Комбинируйте с другими паттернами устойчивости**
   - Retry для временных сбоев
   - Timeout для предотвращения зависаний
   - Bulkhead для изоляции ресурсов

3. **Мониторьте метрики circuit breaker**
   - Отслеживайте переходы состояний
   - Логируйте успешность/неудачность вызовов
   - Настройте алерты для состояния OPEN

4. **Реализуйте fallback стратегии**
   - Кеширование
   - Значения по умолчанию
   - Деградированная функциональность

5. **Тестируйте сценарии сбоев**
   - Unit тесты с моками
   - Integration тесты с симулированными сбоями
   - Chaos engineering в production

---

## Когда НЕ Использовать

1. **Идемпотентные операции без побочных эффектов**
   - Простые запросы только на чтение
   - Операции, которые можно повторять без последствий

2. **Внутренние вызовы в процессе**
   - Не нужно для локальных операций
   - Используйте только для сетевых вызовов

3. **Операции с встроенным retry**
   - Некоторые библиотеки уже имеют механизмы retry
   - Избегайте дублирования логики

---

## Распространённые Ошибки {#распространённые-ошибки-ru}

1. **Слишком низкий порог ошибок**
   - Может привести к ложным срабатываниям
   - Начинайте с консервативных значений и настраивайте

2. **Забывание обработки CircuitBreakerOpenException**
   - Всегда предоставляйте fallback
   - Информируйте пользователя о проблеме

3. **Не мониторинг состояния**
   - Circuit может быть открыт долго без вашего ведома
   - Настройте alerts и мониторинг

4. **Использование одного circuit breaker для всех операций**
   - Разделяйте по сервисам/операциям
   - Избегайте каскадных сбоев

---

**End of document**

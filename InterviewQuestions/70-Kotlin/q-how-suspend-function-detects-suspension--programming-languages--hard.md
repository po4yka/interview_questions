---
id: lang-056
title: "How Suspend Function Detects Suspension / Как suspend функция определяет приостановку"
aliases: [How Suspend Function Detects Suspension, Как suspend функция определяет приостановку]
topic: programming-languages
subtopics: [concurrency, coroutines, kotlin]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [c-coroutines, c-kotlin-features, q-how-to-create-suspend-function--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [concurrency, coroutines, difficulty/hard, kotlin, programming-languages, suspension]
date created: Friday, October 31st 2025, 6:31:27 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# How Suspend Function Detects Suspension?

# Question (EN)
> How does a suspend function detect suspension?

# Вопрос (RU)
> Как suspend функция определяет приостановку?

---

## Answer (EN)

The function "learns" about suspension through:

1. **Continuation frame**: When another suspend function is called, the current one suspends its execution
2. **Coroutine dispatcher**: Suspension is possible when execution moves to another thread (withContext)
3. **COROUTINE_SUSPENDED marker**: Returning this special marker signals to Kotlin Runtime that execution is deferred

The suspend function doesn't actively "detect" suspension - rather, the Kotlin compiler transforms it into a state machine that can naturally suspend and resume.

### Understanding the Mechanism

```kotlin
// Source code
suspend fun example(): String {
    println("Step 1")
    delay(1000)  // Suspension point
    println("Step 2")
    return "Done"
}

// Conceptually transformed by compiler to:
fun example(continuation: Continuation<String>): Any? {
    val sm = continuation as? ExampleStateMachine
        ?: ExampleStateMachine(continuation)

    when (sm.label) {
        0 -> {
            println("Step 1")
            sm.label = 1
            val result = delay(1000, sm)  // Call delay

            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // Signal suspension
            }
            // If not suspended, fall through
        }
        1 -> {
            println("Step 2")
            return "Done"
        }
    }
    throw IllegalStateException()
}
```

### 1. COROUTINE_SUSPENDED Marker

```kotlin
// Internal Kotlin object
internal object COROUTINE_SUSPENDED

// When a suspend function suspends:
suspend fun fetchData(): String {
    delay(1000)  // This may return COROUTINE_SUSPENDED
    return "Data"
}

// Compiled version checks the return value:
fun fetchData(cont: Continuation<String>): Any? {
    val delayResult = delay(1000, cont)

    // Check if delay suspended
    if (delayResult === COROUTINE_SUSPENDED) {
        // Function is suspended - return marker
        return COROUTINE_SUSPENDED
    }

    // If not suspended, continue execution
    return "Data"
}
```

### 2. Continuation Frame

```kotlin
// The Continuation interface
interface Continuation<in T> {
    val context: CoroutineContext
    fun resumeWith(result: Result<T>)
}

// Each suspend function receives a Continuation
suspend fun step1(): String {
    // When this suspends, it stores its state in the continuation
    delay(100)
    return "Step 1 complete"
}

suspend fun step2(): String {
    delay(100)
    return "Step 2 complete"
}

suspend fun multiStep(): String {
    val result1 = step1()  // May suspend here
    val result2 = step2()  // May suspend here
    return "$result1, $result2"
}

// Compiled state machine preserves local variables
class MultiStepContinuation(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var result1: String? = null  // Preserved across suspensions

    override fun resumeWith(result: Result<Any?>) {
        // Resume execution from where it suspended
        multiStep(this)
    }

    override val context: CoroutineContext
        get() = completion.context
}
```

### 3. State Machine Labels

```kotlin
// Original suspend function
suspend fun complexOperation(): Int {
    val a = operation1()  // Suspension point 1
    val b = operation2()  // Suspension point 2
    val c = operation3()  // Suspension point 3
    return a + b + c
}

// Compiler generates state machine with labels
fun complexOperation(cont: Continuation<Int>): Any? {
    val sm = cont as ComplexOperationSM

    when (sm.label) {
        0 -> {
            sm.label = 1
            val result = operation1(sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.a = result as Int
            // Fall through to label 1
        }
        1 -> {
            sm.label = 2
            val result = operation2(sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.b = result as Int
            // Fall through to label 2
        }
        2 -> {
            sm.label = 3
            val result = operation3(sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.c = result as Int
            // Fall through to label 3
        }
        3 -> {
            return sm.a + sm.b + sm.c
        }
    }
    throw IllegalStateException()
}
```

### 4. How suspendCoroutine Works

```kotlin
// Low-level suspension using suspendCoroutine
suspend fun customSuspend(): String = suspendCoroutine { continuation ->
    // This lambda runs immediately
    // Suspension happens when you DON'T call continuation.resume immediately

    Thread {
        Thread.sleep(1000)
        // Resume later with result
        continuation.resume("Result")
    }.start()

    // Lambda ends WITHOUT calling resume
    // This causes COROUTINE_SUSPENDED to be returned
}

// Internal implementation (simplified)
inline suspend fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T = suspendCoroutineUninterceptedOrReturn { cont ->
    val safe = SafeContinuation(cont)
    block(safe)
    safe.getOrThrow()  // Returns COROUTINE_SUSPENDED if not resumed
}
```

### 5. Detecting Suspension at Runtime

```kotlin
import kotlin.coroutines.intrinsics.*

// You can check if a suspend function would suspend
suspend fun willThisSuspend(): Boolean {
    val result = suspendCoroutineUninterceptedOrReturn<String> { cont ->
        // If we return COROUTINE_SUSPENDED, function suspends
        COROUTINE_SUSPENDED
    }
    return true  // Never reached in this case
}

// Example: Check if delay would suspend
suspend fun checkDelaySuspension() {
    val startTime = System.currentTimeMillis()

    // delay always suspends (unless duration is 0 or negative)
    delay(100)

    val endTime = System.currentTimeMillis()
    println("Suspended for ${endTime - startTime}ms")
}

// Some operations might not suspend
suspend fun mightNotSuspend(value: Int): Int {
    if (value > 0) {
        // Doesn't suspend - returns immediately
        return value * 2
    } else {
        // Suspends
        delay(100)
        return 0
    }
}
```

### 6. Dispatcher and Thread Switching

```kotlin
suspend fun demonstrateDispatcherSwitch() {
    println("Thread: ${Thread.currentThread().name}")

    // withContext may cause suspension when switching threads
    withContext(Dispatchers.IO) {
        println("Thread: ${Thread.currentThread().name}")
        // Function suspends when entering withContext
        // Resumes on IO thread
    }

    println("Thread: ${Thread.currentThread().name}")
    // Suspends again when exiting withContext
    // Resumes on original thread
}

// withContext implementation (simplified)
suspend fun <T> withContext(
    context: CoroutineContext,
    block: suspend () -> T
): T = suspendCoroutine { cont ->
    // Switch to new context
    val newContinuation = cont.intercepted().context + context

    // Launch on new dispatcher
    newContinuation[ContinuationInterceptor]?.interceptContinuation(cont)
        ?.resumeWith(runCatching { block() })

    // This causes suspension - function will resume with block's result
}
```

### 7. Checking Suspension Points

```kotlin
suspend fun identifySuspensionPoints() {
    println("Not suspended")  // Regular code

    delay(100)  // SUSPENSION POINT 1
    // Execution may pause here, thread is released

    println("Resumed")

    withContext(Dispatchers.IO) {  // SUSPENSION POINT 2
        // Thread switch causes suspension
        println("On IO thread")
    }

    yield()  // SUSPENSION POINT 3
    // Voluntary suspension to allow other coroutines

    val data = async { fetchData() }.await()  // SUSPENSION POINT 4
    // Suspends until async completes

    println("All done: $data")
}

suspend fun fetchData(): String {
    delay(50)
    return "Data"
}
```

### 8. Internal Suspension Detection

```kotlin
// Using intrinsics to work with raw suspension
import kotlin.coroutines.intrinsics.suspendCoroutineUninterceptedOrReturn
import kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED

suspend fun rawSuspension(): String {
    return suspendCoroutineUninterceptedOrReturn { continuation ->
        // Return COROUTINE_SUSPENDED to suspend
        // Or return actual value to complete immediately

        val shouldSuspend = true

        if (shouldSuspend) {
            // Defer resumption
            Thread {
                Thread.sleep(1000)
                continuation.resumeWith(Result.success("Resumed"))
            }.start()

            COROUTINE_SUSPENDED  // Tells runtime: I'm suspended
        } else {
            "Immediate result"  // No suspension
        }
    }
}

// Testing suspension behavior
suspend fun testSuspension() {
    println("Before suspension")
    val result = rawSuspension()
    println("After suspension: $result")
}
```

### 9. Continuation Interception

```kotlin
// ContinuationInterceptor can observe suspensions
class LoggingInterceptor : ContinuationInterceptor {
    override val key = ContinuationInterceptor

    override fun <T> interceptContinuation(
        continuation: Continuation<T>
    ): Continuation<T> {
        return object : Continuation<T> {
            override val context = continuation.context

            override fun resumeWith(result: Result<T>) {
                println("Resuming continuation with result: $result")
                continuation.resumeWith(result)
            }
        }
    }
}

// Usage
suspend fun observeSuspension() = withContext(LoggingInterceptor()) {
    println("Before delay")
    delay(100)  // Suspension logged by interceptor
    println("After delay")
}
```

### 10. Practical Example: Suspension Tracking

```kotlin
// Track how many times a coroutine suspends
class SuspensionCounter {
    private var suspensionCount = 0

    suspend fun <T> trackSuspensions(
        block: suspend () -> T
    ): Pair<T, Int> {
        suspensionCount = 0

        val result = suspendCoroutineUninterceptedOrReturn<T> { cont ->
            val tracked = object : Continuation<T> {
                override val context = cont.context

                override fun resumeWith(result: Result<T>) {
                    suspensionCount++
                    cont.resumeWith(result)
                }
            }

            block.startCoroutine(tracked)
            COROUTINE_SUSPENDED
        }

        return result to suspensionCount
    }
}

// Usage
suspend fun example() {
    val counter = SuspensionCounter()

    val (result, count) = counter.trackSuspensions {
        delay(100)  // Suspension 1
        withContext(Dispatchers.IO) {  // Suspension 2
            delay(100)  // Suspension 3
        }
        "Done"
    }

    println("Result: $result, Suspended $count times")
}
```

### Key Points

1. **COROUTINE_SUSPENDED**: Special marker object returned when suspension occurs
2. **State Machine**: Compiler transforms suspend functions into state machines with labels
3. **Continuation**: Stores function state and allows resumption
4. **Automatic**: Developer doesn't manually detect suspension - compiler handles it
5. **Return Value**: Function returns `COROUTINE_SUSPENDED` to indicate suspension, or actual result if completed
6. **Thread Release**: When suspended, thread is freed for other work
7. **Resume**: Continuation.resumeWith() called to resume execution

### What Causes Suspension

```kotlin
// These cause suspension:
delay(1000)                           // Always suspends
withContext(Dispatchers.IO) { }       // Suspends for thread switch
yield()                               // Suspends to yield thread
async { }.await()                     // Suspends until result ready
mutex.lock()                          // May suspend if locked
channel.receive()                     // Suspends until data available
flow.collect { }                      // Suspends at each emission

// These DON'T cause suspension:
println("Hello")                      // Regular code
val x = 5 + 3                        // Regular computation
if (condition) { }                    // Regular control flow
```

---

## Ответ (RU)

Функция "узнает" о приостановке через: - Фрейм Continuation если вызвана другая suspend-функция текущая приостанавливает свое выполнение - Корутинный диспетчер приостановка возможна если выполнение ушло в другой поток withContext - Возвращение специального маркера COROUTINE_SUSPENDED сигнализирует Kotlin Runtime что выполнение отложено

## Related Questions

- [[q-visitor-pattern--design-patterns--hard]]
- [[q-how-system-knows-weakreference-can-be-cleared--programming-languages--medium]]
- [[q-chain-of-responsibility--design-patterns--medium]]

---
id: kotlin-122
title: "Continuation and CPS: how suspend functions work internally / Continuation и CPS: как работают suspend функции внутри"
topic: kotlin
difficulty: hard
status: draft
created: 2025-10-12
tags: [advanced, continuation, coroutines, cps, difficulty/hard, internals, kotlin, state-machine]
moc: moc-kotlin
related: [q-common-coroutine-mistakes--kotlin--medium, q-debugging-coroutines-techniques--kotlin--medium, q-kotlin-data-sealed-classes-combined--programming-languages--medium, q-kotlin-enum-classes--kotlin--easy, q-kotlin-scope-functions-advanced--kotlin--medium, q-suspend-cancellable-coroutine--kotlin--hard]
subtopics:
  - continuation
  - coroutines
  - cps
  - internals
  - state-machine
date created: Saturday, November 1st 2025, 12:10:31 pm
date modified: Saturday, November 1st 2025, 5:43:27 pm
---

# Question (EN)
> How does Kotlin transform suspend functions internally? What is Continuation, CPS transformation, and how do state machines work?

# Вопрос (RU)
> Как Kotlin трансформирует suspend функции внутри? Что такое Continuation, CPS трансформация, и как работают конечные автоматы?

---

## Answer (EN)

Understanding how `suspend` functions work internally is crucial for advanced coroutine usage, performance optimization, and debugging. Kotlin compiles suspend functions using **Continuation Passing Style (CPS)** and **state machines** under the hood. This transformation is transparent to developers but understanding it unlocks deeper insights.



### What is Continuation?

**Continuation** represents "the rest of the computation" - what should happen after a suspension point resumes.

```kotlin
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Convenience extensions:
fun <T> Continuation<T>.resume(value: T)
fun <T> Continuation<T>.resumeWithException(exception: Throwable)
```

**Key concept:** When a suspend function suspends, it passes a Continuation to the suspending operation. That operation later calls `resumeWith()` to continue execution.

### Continuation Passing Style (CPS)

**CPS transformation:** The compiler transforms every suspend function to accept an additional `Continuation` parameter.

**Before (source code):**

```kotlin
suspend fun getUserName(userId: String): String {
    val user = fetchUser(userId)
    return user.name
}
```

**After CPS transformation (conceptual):**

```kotlin
fun getUserName(userId: String, continuation: Continuation<String>): Any? {
    // Transformed to state machine (see below)
    val user = fetchUser(userId, continuation)
    if (user == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
    return user.name
}
```

**Key points:**
- Return type becomes `Any?` (can return result or `COROUTINE_SUSPENDED`)
- Continuation parameter added
- Function is no longer `suspend` (it's a regular function)

### State Machine Transformation

**The compiler transforms suspend functions into state machines** where each suspension point becomes a state.

**Example:**

```kotlin
suspend fun example() {
    println("Before delay 1")
    delay(1000)           // Suspension point 1
    println("After delay 1")
    delay(1000)           // Suspension point 2
    println("After delay 2")
}
```

**Conceptual transformation:**

```kotlin
fun example(continuation: Continuation<Unit>): Any? {
    val sm = continuation as? ExampleStateMachine
        ?: ExampleStateMachine(continuation)

    when (sm.label) {
        0 -> {
            println("Before delay 1")
            sm.label = 1
            if (delay(1000, sm) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED
            }
        }
        1 -> {
            println("After delay 1")
            sm.label = 2
            if (delay(1000, sm) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED
            }
        }
        2 -> {
            println("After delay 2")
            return Unit
        }
    }
}

class ExampleStateMachine(
    private val completion: Continuation<Unit>
) : Continuation<Unit> {
    var label = 0
    var result: Any? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Unit>) {
        this.result = result
        example(this) // Resume execution
    }
}
```

**Key concepts:**
- **label**: Current state (suspension point)
- **State machine class**: Stores state between suspensions
- **resumeWith**: Advances to next state when resumed

### Real Decompiled Example

Let's look at actual decompiled code:

**Original Kotlin:**

```kotlin
suspend fun fetchUserData(userId: String): UserData {
    val user = api.getUser(userId)
    val posts = api.getPosts(userId)
    return UserData(user, posts)
}
```

**Decompiled (simplified):**

```java
@Nullable
public static final Object fetchUserData(
    @NotNull String userId,
    @NotNull Continuation<UserData> $completion
) {
    Object $continuation;
    label27: {
        if ($completion instanceof FetchUserDataContinuation) {
            $continuation = (FetchUserDataContinuation) $completion;
            if ((($continuation.label & Integer.MIN_VALUE) != 0)) {
                $continuation.label -= Integer.MIN_VALUE;
                break label27;
            }
        }
        $continuation = new FetchUserDataContinuation($completion);
    }

    Object result = $continuation.result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch ($continuation.label) {
        case 0: {
            // Initial state
            ResultKt.throwOnFailure(result);
            $continuation.userId = userId;
            $continuation.label = 1;

            Object user = api.getUser(userId, $continuation);
            if (user == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            result = user;
            // Fall through to case 1
        }
        case 1: {
            // After getUser() resumed
            ResultKt.throwOnFailure(result);
            User user = (User) result;

            $continuation.user = user;
            $continuation.label = 2;

            Object posts = api.getPosts($continuation.userId, $continuation);
            if (posts == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            result = posts;
            // Fall through to case 2
        }
        case 2: {
            // After getPosts() resumed
            ResultKt.throwOnFailure(result);
            List<Post> posts = (List) result;
            User user = $continuation.user;

            return new UserData(user, posts);
        }
        default:
            throw new IllegalStateException("call to 'resume' before 'invoke'");
    }
}

// State machine class
static final class FetchUserDataContinuation extends ContinuationImpl {
    Object result;
    int label;
    String userId;
    User user;

    FetchUserDataContinuation(Continuation completion) {
        super(completion);
    }

    @Nullable
    public final Object invokeSuspend(@NotNull Object result) {
        this.result = result;
        this.label |= Integer.MIN_VALUE;
        return fetchUserData(null, this);
    }
}
```

**Observations:**
1. Function no longer has `suspend` modifier
2. Extra `Continuation` parameter added
3. Return type is `Object` (can be result or COROUTINE_SUSPENDED)
4. State machine with `switch` based on `label`
5. Local variables stored in continuation class fields
6. Each suspension point increments label

### suspendCoroutine and suspendCancellableCoroutine

**suspendCoroutine:** Low-level API to create custom suspending operations.

```kotlin
public suspend inline fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T {
    // Internal implementation details
    // Returns COROUTINE_SUSPENDED and stores continuation
}
```

**Usage example:**

```kotlin
suspend fun customDelay(timeMillis: Long) = suspendCoroutine<Unit> { cont ->
    // 'cont' is the continuation to resume later
    thread {
        Thread.sleep(timeMillis)
        cont.resume(Unit) // Resume coroutine
    }
}

// Usage
launch {
    println("Before custom delay")
    customDelay(1000)
    println("After custom delay")
}
```

**suspendCancellableCoroutine:** Cancellation-aware version:

```kotlin
suspend fun cancellableDelay(timeMillis: Long) = suspendCancellableCoroutine<Unit> { cont ->
    val timer = Timer()
    timer.schedule(timeMillis) {
        cont.resume(Unit)
    }

    // Handle cancellation
    cont.invokeOnCancellation {
        timer.cancel()
    }
}
```

### Continuation.resume And resumeWith

```kotlin
// Resume with success
continuation.resume(value)
// Equivalent to:
continuation.resumeWith(Result.success(value))

// Resume with exception
continuation.resumeWithException(exception)
// Equivalent to:
continuation.resumeWith(Result.failure(exception))
```

**Example: Manual continuation handling**

```kotlin
class ManualSuspender {
    private var continuation: Continuation<String>? = null

    suspend fun waitForValue(): String = suspendCoroutine { cont ->
        continuation = cont
    }

    fun provideValue(value: String) {
        continuation?.resume(value)
        continuation = null
    }
}

// Usage
val suspender = ManualSuspender()

launch {
    println("Waiting for value...")
    val value = suspender.waitForValue()
    println("Received: $value")
}

delay(1000)
suspender.provideValue("Hello!") // Resumes coroutine

// Output:
// Waiting for value...
// (1 second pause)
// Received: Hello!
```

### ContinuationInterceptor

**ContinuationInterceptor** is how dispatchers work - they intercept continuations to switch threads.

```kotlin
interface ContinuationInterceptor : CoroutineContext.Element {
    fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T>
}
```

**Example: Custom interceptor**

```kotlin
class LoggingInterceptor : ContinuationInterceptor {
    override val key = ContinuationInterceptor

    override fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T> {
        return LoggingContinuation(continuation)
    }

    private class LoggingContinuation<T>(
        private val continuation: Continuation<T>
    ) : Continuation<T> {
        override val context = continuation.context

        override fun resumeWith(result: Result<T>) {
            println("Resuming with: $result")
            continuation.resumeWith(result)
        }
    }
}

// Usage
runBlocking(LoggingInterceptor()) {
    println("Start")
    delay(100)
    println("After delay")
}

// Output:
// Start
// Resuming with: Success(kotlin.Unit)
// After delay
```

### How Dispatchers Intercept Continuations

**Dispatchers.Default implementation (simplified):**

```kotlin
object DefaultDispatcher : CoroutineDispatcher() {
    private val threadPool = Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors()
    )

    override fun dispatch(context: CoroutineContext, block: Runnable) {
        threadPool.execute(block)
    }

    override fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T> {
        return DispatchedContinuation(this, continuation)
    }
}

class DispatchedContinuation<T>(
    private val dispatcher: CoroutineDispatcher,
    private val continuation: Continuation<T>
) : Continuation<T> {
    override val context = continuation.context

    override fun resumeWith(result: Result<T>) {
        // Dispatch resume to appropriate thread
        dispatcher.dispatch(context, Runnable {
            continuation.resumeWith(result)
        })
    }
}
```

**What happens:**

1. Suspend function suspends, returns COROUTINE_SUSPENDED
2. Continuation is passed to suspending operation
3. Operation completes, calls `continuation.resumeWith()`
4. ContinuationInterceptor (dispatcher) intercepts
5. Dispatcher schedules resume on appropriate thread
6. State machine continues from next label

### Why Suspend Functions Can't Be Called from Regular Functions

**The problem:**

```kotlin
fun regularFunction() {
    getUserName("123") // ERROR: Suspend function 'getUserName' should be called only from a coroutine or another suspend function
}
```

**Why?** Suspend functions need a Continuation parameter, which only exists in coroutine context.

**Behind the scenes:**

```kotlin
// What you write:
suspend fun getUserName(userId: String): String

// What compiler sees:
fun getUserName(userId: String, continuation: Continuation<String>): Any?

// Regular function doesn't have continuation:
fun regularFunction() {
    getUserName("123", /* Where's the continuation? */)
}
```

**Solutions:**

```kotlin
// 1. Make caller suspend too
suspend fun callerFunction() {
    getUserName("123") // OK - compiler adds continuation
}

// 2. Launch coroutine
fun regularFunction() {
    GlobalScope.launch { // Creates continuation
        getUserName("123")
    }
}

// 3. Use runBlocking (blocks thread)
fun regularFunction() {
    runBlocking {
        getUserName("123")
    }
}
```

### Performance Implications

**State machine benefits:**

1. **No callback hell**: State machine handles flow
2. **Stack-less**: No thread stack allocation per coroutine
3. **Efficient**: Only continuation object allocated
4. **Reusable**: State machine object reused

**Cost:**

1. **Object allocation**: Continuation object created
2. **Switch overhead**: Label-based dispatch
3. **Field access**: Local variables become fields

**Benchmark:**

```kotlin
// Regular function: ~5ns
fun regularSum(a: Int, b: Int): Int {
    return a + b
}

// Suspend function: ~20ns (state machine overhead)
suspend fun suspendSum(a: Int, b: Int): Int {
    return a + b // No actual suspension
}

// Suspend with delay: ~100μs (actual suspension + dispatch)
suspend fun suspendSumWithDelay(a: Int, b: Int): Int {
    delay(1) // Actual suspension
    return a + b
}
```

**Optimization: Inline suspend functions**

```kotlin
// Generates state machine code at call site
inline suspend fun inlinedSum(a: Int, b: Int): Int {
    return a + b
}
// Performance: ~5ns (no state machine needed)
```

### Advanced: Implementing Custom Suspending Operations

**Example: Converting callback to suspend function**

```kotlin
// Callback-based API
interface ApiCallback {
    fun onSuccess(data: String)
    fun onError(error: Throwable)
}

fun fetchDataAsync(callback: ApiCallback) {
    thread {
        Thread.sleep(1000)
        callback.onSuccess("Data")
    }
}

// Convert to suspend function
suspend fun fetchData(): String = suspendCancellableCoroutine { cont ->
    fetchDataAsync(object : ApiCallback {
        override fun onSuccess(data: String) {
            cont.resume(data)
        }

        override fun onError(error: Throwable) {
            cont.resumeWithException(error)
        }
    })

    cont.invokeOnCancellation {
        // Cancel underlying operation if needed
    }
}

// Usage
launch {
    val data = fetchData() // Looks synchronous!
    println(data)
}
```

### State Machine with Multiple Variables

**Example:**

```kotlin
suspend fun complexFunction(x: Int): Int {
    val a = computeA(x)
    val b = computeB(a)
    val c = computeC(a, b)
    return c
}

// Transformed to:
class ComplexFunctionContinuation(completion: Continuation<Int>) : Continuation<Int> {
    var label = 0
    var result: Any? = null

    // Local variables become fields
    var x: Int = 0
    var a: Int = 0
    var b: Int = 0

    // ... resumeWith implementation
}
```

**Key insight:** All local variables that survive suspension points become fields in the continuation class.

### Exception Handling in State Machines

**Source:**

```kotlin
suspend fun withExceptionHandling() {
    try {
        val data = fetchData()
        processData(data)
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**Transformed (simplified):**

```kotlin
fun withExceptionHandling(cont: Continuation<Unit>): Any? {
    when (cont.label) {
        0 -> {
            cont.label = 1
            try {
                val data = fetchData(cont)
                if (data == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                cont.data = data
            } catch (e: Exception) {
                handleError(e)
                return Unit
            }
        }
        1 -> {
            try {
                processData(cont.data, cont)
                if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            } catch (e: Exception) {
                handleError(e)
            }
            return Unit
        }
    }
}
```

### Visualizing State Machine Execution

```
Initial call: label = 0
     ↓
[State 0] Call operation1()
     ↓
COROUTINE_SUSPENDED (return to caller)
     ↓
(Time passes, operation1 completes)
     ↓
continuation.resumeWith(result1)
     ↓
[State 1] Process result1, call operation2()
     ↓
COROUTINE_SUSPENDED (return to caller)
     ↓
(Time passes, operation2 completes)
     ↓
continuation.resumeWith(result2)
     ↓
[State 2] Process result2, return final result
     ↓
Complete
```

### Key Takeaways

1. **Continuation = "rest of computation"** - What happens after suspension
2. **CPS transformation** - Compiler adds Continuation parameter
3. **State machines** - Each suspension point = state (label)
4. **No callback hell** - State machine handles flow control
5. **Efficient** - No thread stack per coroutine
6. **ContinuationInterceptor** - How dispatchers switch threads
7. **suspendCoroutine/suspendCancellableCoroutine** - Build custom suspending ops
8. **Local variables → fields** - Survive suspension
9. **Can't call from regular functions** - Need continuation context
10. **Performance** - Small overhead for state machine, huge gain from not blocking

---

## Ответ (RU)

Понимание того, как `suspend` функции работают внутри, критично для продвинутого использования корутин, оптимизации производительности и отладки. Kotlin компилирует suspend функции используя **Continuation Passing Style (CPS)** и **конечные автоматы (state machines)** под капотом. Эта трансформация прозрачна для разработчиков, но её понимание открывает глубокие знания.



### Что Такое Continuation?

**Continuation** представляет "остаток вычисления" - что должно произойти после возобновления точки приостановки.

```kotlin
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}
```

**Ключевая концепция:** Когда suspend функция приостанавливается, она передает Continuation приостанавливающей операции. Эта операция позже вызывает `resumeWith()` для продолжения выполнения.

### Continuation Passing Style (CPS)

**CPS трансформация:** Компилятор преобразует каждую suspend функцию, добавляя дополнительный параметр `Continuation`.

**До (исходный код):**

```kotlin
suspend fun getUserName(userId: String): String {
    val user = fetchUser(userId)
    return user.name
}
```

**После CPS трансформации (концептуально):**

```kotlin
fun getUserName(userId: String, continuation: Continuation<String>): Any? {
    // Преобразовано в конечный автомат (см. ниже)
    val user = fetchUser(userId, continuation)
    if (user == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
    return user.name
}
```

### Ключевые Выводы

1. **Continuation = "остаток вычисления"** - Что происходит после приостановки
2. **CPS трансформация** - Компилятор добавляет параметр Continuation
3. **Конечные автоматы** - Каждая точка приостановки = состояние (label)
4. **Никакого callback hell** - Конечный автомат управляет потоком
5. **Эффективность** - Нет стека потока на корутину
6. **ContinuationInterceptor** - Как диспетчеры переключают потоки
7. **suspendCoroutine/suspendCancellableCoroutine** - Создание пользовательских приостанавливающих операций
8. **Локальные переменные → поля** - Выживают приостановку
9. **Нельзя вызвать из обычных функций** - Нужен контекст continuation
10. **Производительность** - Небольшие накладные расходы на конечный автомат, огромная выгода от неблокирования

---

## Follow-ups

1. How does the Kotlin compiler optimize state machines for suspend functions without suspension points?
2. Can you explain the difference between ContinuationImpl and BaseContinuationImpl?
3. How do inline suspend functions avoid state machine generation?
4. What happens to exception stack traces across multiple suspension points?
5. How does the compiler handle tail-call optimization in suspend functions?
6. Can you implement a custom ContinuationInterceptor for debugging?
7. How does the state machine handle loops with suspension points inside?

## References

- [Kotlin Coroutines Under the Hood](https://www.youtube.com/watch?v=YrrUCSi72E8)
- [Deep Dive into Coroutines on JVM](https://blog.jetbrains.com/kotlin/2021/04/coroutines-under-the-hood/)
- [KotlinConf 2017: Deep Dive into Coroutines](https://www.youtube.com/watch?v=_hfBv0a09Jc)
- [Continuation Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.coroutines/-continuation/)

## Related Questions

- [[q-suspend-cancellable-coroutine--kotlin--hard|Converting callbacks with suspendCancellableCoroutine]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging Kotlin coroutines]]
- [[q-common-coroutine-mistakes--kotlin--medium|Common coroutine mistakes]]

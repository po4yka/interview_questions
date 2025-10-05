---
id: 20251003142005
title: "Suspend Function Return Type After Compilation"
question_ru: "Какой будет возвращаемый тип у suspend-функции, которая возвращает String, после компиляции"
question_en: "What will be the return type of a suspend function that returns String after compilation"
answer_ru: "Возвращаемый тип становится Any, потому что функция может вернуть либо String, либо корутину в приостановленном состоянии"
answer_en: "The return type becomes Any because the function can return either String or a coroutine in suspended state."
tags:
  - coroutines
  - kotlin
  - async
  - difficulty-hard
  - easy_kotlin
  - lang/ru
  - suspend functions
topic: programming-languages
subtopics:
  - kotlin
  - coroutines
  - suspending-functions
difficulty: hard
question_kind: practical
moc: moc-kotlin
status: draft
source: https://t.me/easy_kotlin/876
---

# Suspend Function Return Type After Compilation

## Question (EN)

What will be the return type of a suspend function that returns String after compilation?

## Answer (EN)

The return type becomes **Any?** (or `Object` in JVM bytecode) because the function can return either the String value or a special marker **COROUTINE_SUSPENDED** to indicate that the coroutine is suspended.

Under the hood, the Kotlin compiler transforms suspend functions using the **Continuation-Passing Style (CPS)** transformation. The function signature changes significantly during compilation.

### Source Code

```kotlin
suspend fun fetchUserName(userId: Int): String {
    delay(100)
    return "User_$userId"
}
```

### After Compilation (Conceptual Decompiled Version)

```kotlin
// Simplified representation of what the compiler generates
fun fetchUserName(userId: Int, continuation: Continuation<String>): Any? {
    // State machine implementation
    val sm = continuation as? FetchUserNameStateMachine
        ?: FetchUserNameStateMachine(continuation)

    when (sm.label) {
        0 -> {
            sm.label = 1
            if (delay(100, sm) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED
            }
        }
        1 -> {
            return "User_$userId"
        }
    }
    throw IllegalStateException("Unexpected state")
}

// Return type is Any? because it can return:
// 1. COROUTINE_SUSPENDED (a special marker object)
// 2. The actual String result
// 3. null (in some cases)
```

### Understanding the Transformation

```kotlin
// Original suspend function
suspend fun getData(): String {
    delay(1000)
    return "Data"
}

// What the compiler actually generates (simplified):
fun getData(continuation: Continuation<String>): Any? {
    // Can return:
    // - COROUTINE_SUSPENDED: if the function suspends
    // - String: if the function completes immediately
    // - Exception: if an error occurs

    // ... state machine implementation ...
}
```

### COROUTINE_SUSPENDED Marker

```kotlin
// This is an internal Kotlin coroutine object
internal object COROUTINE_SUSPENDED

// The compiled function returns this when it suspends:
fun example(cont: Continuation<String>): Any? {
    // ... some logic ...

    if (needsToSuspend) {
        return COROUTINE_SUSPENDED  // Type is Any
    } else {
        return "Result"  // Type is String
    }

    // Return type must be Any? to accommodate both
}
```

### Real Example: State Machine

```kotlin
// Original code
suspend fun multiStepProcess(): String {
    val step1 = delay(100)           // Suspension point 1
    val step2 = fetchData()          // Suspension point 2
    return "Completed: $step2"
}

// Compiled version (highly simplified)
fun multiStepProcess(completion: Continuation<String>): Any? {
    val sm = completion as? MultiStepStateMachine
        ?: MultiStepStateMachine(completion)

    when (sm.label) {
        0 -> {
            sm.label = 1
            val result = delay(100, sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            // Fall through to label 1
        }
        1 -> {
            sm.label = 2
            val result = fetchData(sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.step2Result = result as String
            // Fall through to label 2
        }
        2 -> {
            return "Completed: ${sm.step2Result}"  // Returns String
        }
    }

    throw IllegalStateException()
}

// State machine to preserve local variables across suspensions
class MultiStepStateMachine(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var step2Result: String? = null

    override fun resumeWith(result: Result<Any?>) {
        multiStepProcess(this)
    }

    override val context: CoroutineContext
        get() = completion.context
}
```

### Verification with Decompiled Code

```kotlin
// Original Kotlin code
suspend fun simpleFunction(): String {
    delay(1000)
    return "Done"
}

// Actual decompiled Java bytecode (from IntelliJ)
public static final Object simpleFunction(Continuation $completion) {
    Object $continuation;
    label27: {
        if ($completion instanceof SimpleFunctionContinuation) {
            $continuation = (SimpleFunctionContinuation)$completion;
            if (((SimpleFunctionContinuation)$continuation).label >= Integer.MIN_VALUE) {
                ((SimpleFunctionContinuation)$continuation).label -= Integer.MIN_VALUE;
                break label27;
            }
        }
        $continuation = new SimpleFunctionContinuation($completion);
    }

    Object result = ((SimpleFunctionContinuation)$continuation).result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch(((SimpleFunctionContinuation)$continuation).label) {
        case 0:
            ResultKt.throwOnFailure(result);
            ((SimpleFunctionContinuation)$continuation).label = 1;
            if (DelayKt.delay(1000L, $continuation) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;  // Returns Object (COROUTINE_SUSPENDED)
            }
            break;
        case 1:
            ResultKt.throwOnFailure(result);
            break;
        default:
            throw new IllegalStateException("call to 'resume' before 'invoke'");
    }

    return "Done";  // Returns String

    // Return type is Object to support both COROUTINE_SUSPENDED and String
}
```

### Why Any? and not String?

```kotlin
// This wouldn't work with return type String:
fun fetchData(cont: Continuation<String>): String {
    if (suspended) {
        return COROUTINE_SUSPENDED  // ❌ ERROR: Type mismatch
    }
    return "Data"  // ✅ OK
}

// Must use Any? to allow both:
fun fetchData(cont: Continuation<String>): Any? {
    if (suspended) {
        return COROUTINE_SUSPENDED  // ✅ OK (Any)
    }
    return "Data"  // ✅ OK (String is subtype of Any)
}
```

### Continuation Interface

```kotlin
// The Continuation interface that's added as a parameter
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// So this:
suspend fun getName(): String

// Becomes this:
fun getName(continuation: Continuation<String>): Any?
```

### Example: Immediate Return vs Suspension

```kotlin
suspend fun smartFunction(needDelay: Boolean): String {
    if (needDelay) {
        delay(1000)  // May return COROUTINE_SUSPENDED
    }
    return "Result"  // Always returns String at the end
}

// Compiled behavior:
fun smartFunction(needDelay: Boolean, cont: Continuation<String>): Any? {
    if (needDelay) {
        // First call: returns COROUTINE_SUSPENDED
        // Resumed later after delay
    }
    // Eventually returns: "Result" (String)

    // Return type Any? covers both cases
}
```

### Testing the Return Type

```kotlin
// You can't access the compiled return type directly,
// but you can observe the behavior:

fun main() = runBlocking {
    // This suspend function returns String to the caller
    val result: String = fetchUserName(1)
    println(result)  // "User_1"

    // But internally, the compiled version returns Any?
    // and the coroutine machinery handles it
}

// The coroutine infrastructure checks:
val internalResult = fetchUserName(1, continuation)
when (internalResult) {
    COROUTINE_SUSPENDED -> {
        // Function suspended, will resume later
    }
    else -> {
        // Function completed immediately
        continuation.resumeWith(Result.success(internalResult as String))
    }
}
```

### Key Takeaways

1. **Original Signature**: `suspend fun foo(): String`
2. **Compiled Signature**: `fun foo(continuation: Continuation<String>): Any?`
3. **Return Type Reason**: Can return either `COROUTINE_SUSPENDED` or the actual `String` result
4. **Type Hierarchy**: `String` and `COROUTINE_SUSPENDED` share `Any?` as common supertype
5. **State Machine**: The function is transformed into a state machine that preserves state across suspension points

### Additional Transformation Details

```kotlin
// Suspend modifier adds:
// 1. Continuation parameter
// 2. State machine implementation
// 3. Return type change to Any?
// 4. Suspension point tracking

suspend fun original(x: Int): String
// ⬇️ Transformed to ⬇️
fun original(x: Int, $completion: Continuation<String>): Any?

// Generic pattern:
suspend fun <T> func(): T
// ⬇️ Becomes ⬇️
fun <T> func($completion: Continuation<T>): Any?
```

---

## Вопрос (RU)

Какой будет возвращаемый тип у suspend-функции, которая возвращает String, после компиляции

## Ответ (RU)

Возвращаемый тип становится Any, потому что функция может вернуть либо String, либо корутину в приостановленном состоянии

---
id: lang-062
title: "Suspend Function Suspension Mechanism / Механизм приостановки suspend функции"
aliases: [Suspend Function Suspension Mechanism, Механизм приостановки suspend функции]
topic: programming-languages
subtopics: [control-flow, coroutines, suspension]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-equals-hashcode-purpose--programming-languages--hard, q-extensions-concept--programming-languages--easy, q-list-vs-sequence--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [coroutines, difficulty/hard, kotlin, programming-languages, suspension]
date created: Saturday, October 4th 2025, 10:56:46 am
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Suspend Function Suspension Mechanism

# Question (EN)
> How does the suspension mechanism work in suspend functions?

# Вопрос (RU)
> Как работает механизм приостановки в suspend-функциях?

---

## Answer (EN)

When execution of a suspend function is suspended:

1. **Function state is saved** in a continuation object
2. **Current thread is released** for other work
3. Later, **execution resumes from the same place** as if nothing happened

This is implemented through:
- **State machine transformation** by the Kotlin compiler
- **Continuation-passing style (CPS)** transformation
- **Automatic code transformation** at compilation

### Continuation Object

```kotlin
// The Continuation interface that stores state
interface Continuation<in T> {
    val context: CoroutineContext
    fun resumeWith(result: Result<T>)
}

// Suspend function signature transformation
// From: suspend fun getData(): String
// To:   fun getData(continuation: Continuation<String>): Any?
```

### State Machine Example

```kotlin
// Original code you write:
suspend fun example(): String {
    val a = step1()  // Suspension point 1
    val b = step2()  // Suspension point 2
    return "$a $b"
}

// Compiler generates state machine:
fun example(continuation: Continuation<String>): Any? {
    val sm = continuation as? ExampleStateMachine
        ?: ExampleStateMachine(continuation)

    when (sm.label) {
        0 -> {
            sm.label = 1
            val result = step1(sm)
            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // Thread released here
            }
            sm.a = result
        }
        1 -> {
            sm.label = 2
            val result = step2(sm)
            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // Thread released here
            }
            sm.b = result
        }
        2 -> {
            return "${sm.a} ${sm.b}"
        }
    }
}

// State machine class stores local variables
class ExampleStateMachine(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var a: String? = null  // Local variable preserved
    var b: String? = null  // Local variable preserved

    override fun resumeWith(result: Result<Any?>) {
        example(this)  // Resume from where it suspended
    }

    override val context: CoroutineContext
        get() = completion.context
}
```

### How Suspension Works

```kotlin
// Step-by-step execution

// 1. Function starts
suspend fun fetchData(): String {
    println("Start")
    delay(1000)  // Suspension point
    println("Resume")
    return "Data"
}

// 2. Reaches delay - returns COROUTINE_SUSPENDED
//    - State saved: label = 1
//    - Thread released
//    - Coroutine scheduler notes to resume later

// 3. After 1000ms, scheduler calls:
continuation.resumeWith(Result.success(Unit))

// 4. Function resumes from label = 1
//    - Continues execution
//    - Returns "Data"
```

### Real Example with Local Variables

```kotlin
// Source code
suspend fun calculate(x: Int, y: Int): Int {
    val sum = x + y           // Regular code
    delay(100)                // Suspension point
    val doubled = sum * 2     // Regular code after resume
    delay(100)                // Another suspension
    return doubled + 10
}

// Compiled: Variables moved to state machine
class CalculateSM(val x: Int, val y: Int, val completion: Continuation<Int>) : Continuation<Any?> {
    var label = 0
    var sum: Int = 0      // Preserved across suspensions
    var doubled: Int = 0  // Preserved across suspensions

    override fun resumeWith(result: Result<Any?>) {
        calculate(x, y, this)
    }

    override val context: CoroutineContext get() = completion.context
}
```

### Thread Release Mechanism

```kotlin
fun demonstrateThreadRelease() = runBlocking {
    println("Thread: ${Thread.currentThread().name}")

    launch {
        println("Before delay: ${Thread.currentThread().name}")
        delay(1000)  // Thread released here
        println("After delay: ${Thread.currentThread().name}")  // May be different thread
    }

    // Thread can execute other coroutines during delay
    launch {
        println("Other coroutine: ${Thread.currentThread().name}")
    }
}
```

### Resumption Process

```kotlin
// When coroutine is ready to resume:
// 1. Scheduler finds the continuation
// 2. Calls continuation.resumeWith(result)
// 3. State machine jumps to saved label
// 4. Execution continues from that point

class DelayedContinuation(
    private val continuation: Continuation<Unit>,
    private val delayMs: Long
) {
    init {
        // Schedule resumption
        Timer().schedule(object : TimerTask() {
            override fun run() {
                continuation.resume(Unit)  // Resume here
            }
        }, delayMs)
    }
}
```

### Summary

**Suspension mechanism:**
1. **Compiler transformation**: Convert to state machine
2. **State preservation**: Save local variables in continuation
3. **Thread release**: Return COROUTINE_SUSPENDED
4. **Resumption**: Call continuation.resumeWith() to continue

**Key points:**
- No thread blocking during suspension
- State preserved automatically
- Transparent to developer
- Efficient resource usage

---


## Ответ (RU)

Когда выполнение suspend-функции приостанавливается состояние функции сохраняется в continuation-объекте а текущий поток освобождается Позже выполнение возобновляется с этого же места как будто ничего не происходило Это реализовано через стейт-машину и трансформацию кода компилятором Kotlin

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-list-vs-sequence--programming-languages--medium]]
- [[q-equals-hashcode-purpose--programming-languages--hard]]
- [[q-extensions-concept--programming-languages--easy]]

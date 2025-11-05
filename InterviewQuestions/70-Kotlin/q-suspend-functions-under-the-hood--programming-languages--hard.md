---
id: lang-089
title: "Suspend Functions Under The Hood / Suspend функции в подробностях"
aliases: [Suspend Functions Under The Hood, Suspend функции в подробностях]
topic: programming-languages
subtopics: [compiler, coroutines, implementation]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-suspend-function-return-type-after-compilation--programming-languages--hard, q-synchronized-blocks-with-coroutines--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [compiler, coroutines, difficulty/hard, kotlin, programming-languages]
date created: Saturday, October 4th 2025, 10:46:31 am
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Suspend Functions Under the Hood

# Question (EN)
> How do suspend functions work under the hood?

# Вопрос (RU)
> Как работают suspend-функции под капотом?

---

## Answer (EN)

Suspend functions in Kotlin pause execution without blocking the thread. Under the hood:

1. **Continuation-Passing Style (CPS)**: Suspend function is split into several parts (continuations)
2. **State Machine**: Compiler generates a state machine with suspension points as states
3. **Suspension**: Occurs when async code executes (e.g., delay, withContext)
4. **Resumption**: Continues from the stopping point when the result is ready

The Kotlin compiler transforms suspend functions into a state machine that can pause and resume execution.

### Compiler Transformation Overview

```kotlin
// Source code you write:
suspend fun fetchUserData(userId: Int): User {
    val profile = fetchProfile(userId)    // Suspension point 1
    val settings = fetchSettings(userId)  // Suspension point 2
    return User(profile, settings)
}

// What compiler generates (conceptual):
fun fetchUserData(
    userId: Int,
    continuation: Continuation<User>
): Any? {
    val sm = continuation as? FetchUserDataSM
        ?: FetchUserDataSM(userId, continuation)

    when (sm.label) {
        0 -> {
            sm.label = 1
            if (fetchProfile(userId, sm) == COROUTINE_SUSPENDED)
                return COROUTINE_SUSPENDED
            sm.profile = result
        }
        1 -> {
            sm.label = 2
            if (fetchSettings(userId, sm) == COROUTINE_SUSPENDED)
                return COROUTINE_SUSPENDED
            sm.settings = result
        }
        2 -> {
            return User(sm.profile, sm.settings)
        }
    }
}

// State machine class to preserve state
class FetchUserDataSM(
    val userId: Int,
    val completion: Continuation<User>
) : Continuation<Any?> {
    var label = 0
    var profile: Profile? = null
    var settings: Settings? = null

    override fun resumeWith(result: Result<Any?>) {
        fetchUserData(userId, this)
    }

    override val context: CoroutineContext
        get() = completion.context
}
```

### Simple Example: Transformation

```kotlin
// Original code
suspend fun simple(): String {
    delay(1000)
    return "Done"
}

// After compilation (simplified)
fun simple(continuation: Continuation<String>): Any? {
    val sm = continuation as? SimpleSM ?: SimpleSM(continuation)

    when (sm.label) {
        0 -> {
            sm.label = 1
            val delayResult = delay(1000, sm)
            if (delayResult == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED
            }
            // Fall through to label 1
        }
        1 -> {
            return "Done"
        }
    }
    throw IllegalStateException()
}

class SimpleSM(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0

    override fun resumeWith(result: Result<Any?>) {
        simple(this)
    }

    override val context: CoroutineContext
        get() = completion.context
}
```

### State Machine with Local Variables

```kotlin
// Original: Function with local variables
suspend fun calculate(x: Int, y: Int): Int {
    val sum = x + y             // Local variable
    delay(100)                  // Suspension point
    val product = sum * 2       // Another local variable
    delay(100)                  // Another suspension
    return product + x
}

// Compiled: Variables moved to state machine
fun calculate(
    x: Int,
    y: Int,
    continuation: Continuation<Int>
): Any? {
    val sm = continuation as? CalculateSM
        ?: CalculateSM(x, y, continuation)

    when (sm.label) {
        0 -> {
            sm.sum = x + y              // Store in SM
            sm.label = 1
            if (delay(100, sm) == COROUTINE_SUSPENDED)
                return COROUTINE_SUSPENDED
        }
        1 -> {
            sm.product = sm.sum * 2     // Access from SM
            sm.label = 2
            if (delay(100, sm) == COROUTINE_SUSPENDED)
                return COROUTINE_SUSPENDED
        }
        2 -> {
            return sm.product + sm.x    // Access from SM
        }
    }
}

class CalculateSM(
    val x: Int,
    val y: Int,
    val completion: Continuation<Int>
) : Continuation<Any?> {
    var label = 0
    var sum: Int = 0        // Local variables become fields
    var product: Int = 0

    override fun resumeWith(result: Result<Any?>) {
        calculate(x, y, this)
    }

    override val context: CoroutineContext
        get() = completion.context
}
```

### Continuation Interface

```kotlin
// Core interface for suspending functions
public interface Continuation<in T> {
    // Coroutine context
    public val context: CoroutineContext

    // Called to resume coroutine with result or exception
    public fun resumeWith(result: Result<T>)
}

// Extension functions
public inline fun <T> Continuation<T>.resume(value: T) {
    resumeWith(Result.success(value))
}

public inline fun <T> Continuation<T>.resumeWithException(exception: Throwable) {
    resumeWith(Result.failure(exception))
}
```

### How Suspension Works

```kotlin
// 1. Function call starts with label 0
suspend fun example(): String {
    println("Before suspension")
    delay(1000)  // Suspension point
    println("After suspension")
    return "Done"
}

// 2. Reaches delay, which returns COROUTINE_SUSPENDED
//    Function returns COROUTINE_SUSPENDED to caller
//    Thread is released for other work

// 3. After delay completes, scheduler calls:
continuation.resumeWith(Result.success(Unit))

// 4. Function resumes at label 1
//    Continues from where it left off
//    Returns "Done"
```

### Real Decompiled Example

```kotlin
// Original Kotlin code
suspend fun fetchData(): String {
    delay(1000)
    return "Data"
}

// Actual decompiled Java bytecode (simplified)
@Nullable
public static final Object fetchData(@NotNull Continuation $completion) {
    Object $continuation;
    label20: {
        if ($completion instanceof FetchDataContinuation) {
            $continuation = (FetchDataContinuation)$completion;
            if (((FetchDataContinuation)$continuation).label >= Integer.MIN_VALUE) {
                ((FetchDataContinuation)$continuation).label -= Integer.MIN_VALUE;
                break label20;
            }
        }
        $continuation = new FetchDataContinuation($completion);
    }

    Object $result = ((FetchDataContinuation)$continuation).result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch(((FetchDataContinuation)$continuation).label) {
        case 0:
            ResultKt.throwOnFailure($result);
            ((FetchDataContinuation)$continuation).label = 1;
            if (DelayKt.delay(1000L, (Continuation)$continuation) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            break;
        case 1:
            ResultKt.throwOnFailure($result);
            break;
        default:
            throw new IllegalStateException("call to 'resume' before 'invoke'");
    }

    return "Data";
}

static final class FetchDataContinuation extends ContinuationImpl {
    int label;
    Object result;

    FetchDataContinuation(Continuation $completion) {
        super($completion);
    }

    @Nullable
    public final Object invokeSuspend(@NotNull Object result) {
        this.result = result;
        this.label |= Integer.MIN_VALUE;
        return fetchData(this);
    }
}
```

### Exception Handling Transformation

```kotlin
// Original with try-catch
suspend fun safeFetch(): String {
    return try {
        delay(1000)
        fetchData()
    } catch (e: Exception) {
        "Error: ${e.message}"
    }
}

// Compiler adds exception handling to state machine
fun safeFetch(continuation: Continuation<String>): Any? {
    val sm = continuation as? SafeFetchSM ?: SafeFetchSM(continuation)

    try {
        when (sm.label) {
            0 -> {
                sm.label = 1
                if (delay(1000, sm) == COROUTINE_SUSPENDED)
                    return COROUTINE_SUSPENDED
            }
            1 -> {
                sm.label = 2
                if (fetchData(sm) == COROUTINE_SUSPENDED)
                    return COROUTINE_SUSPENDED
            }
            2 -> {
                return sm.result
            }
        }
    } catch (e: Exception) {
        return "Error: ${e.message}"
    }
}
```

### Nested Suspend Calls

```kotlin
// Original: Nested suspend calls
suspend fun outer(): String {
    val result1 = inner1()  // Calls another suspend function
    val result2 = inner2()
    return "$result1 $result2"
}

suspend fun inner1(): String {
    delay(100)
    return "First"
}

suspend fun inner2(): String {
    delay(100)
    return "Second"
}

// Each function has its own state machine
// Continuations are chained together
fun outer(cont: Continuation<String>): Any? {
    val sm = cont as? OuterSM ?: OuterSM(cont)

    when (sm.label) {
        0 -> {
            sm.label = 1
            // Create continuation for inner1 that resumes outer
            val innerCont = OuterToInner1Continuation(sm)
            val result = inner1(innerCont)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.result1 = result as String
        }
        1 -> {
            sm.label = 2
            val innerCont = OuterToInner2Continuation(sm)
            val result = inner2(innerCont)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.result2 = result as String
        }
        2 -> {
            return "${sm.result1} ${sm.result2}"
        }
    }
}
```

### suspendCoroutine Implementation

```kotlin
// Low-level primitive for creating suspend functions
public suspend inline fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T = suspendCoroutineUninterceptedOrReturn { cont: Continuation<T> ->
    val safe = SafeContinuation(cont.intercepted())
    block(safe)
    safe.getOrThrow()
}

// Usage example
suspend fun customDelay(time: Long): Unit = suspendCoroutine { continuation ->
    // Schedule resumption after delay
    Timer().schedule(object : TimerTask() {
        override fun run() {
            continuation.resume(Unit)
        }
    }, time)
    // Function suspends here because we don't call resume immediately
}

// Transformation
fun customDelay(time: Long, cont: Continuation<Unit>): Any? {
    Timer().schedule(object : TimerTask() {
        override fun run() {
            cont.resume(Unit)  // Resume later
        }
    }, time)
    return COROUTINE_SUSPENDED  // Signal suspension
}
```

### Performance Implications

```kotlin
// Each suspension point creates state machine overhead
suspend fun manySteps(): Int {
    delay(1)  // State 0 -> 1
    delay(1)  // State 1 -> 2
    delay(1)  // State 2 -> 3
    delay(1)  // State 3 -> 4
    delay(1)  // State 4 -> 5
    return 42
}
// Creates state machine with 6 states

// Fewer suspension points = less overhead
suspend fun optimized(): Int {
    delay(5)  // Only one state 0 -> 1
    return 42
}
// Creates state machine with 2 states
```

### Inline Suspend Functions

```kotlin
// inline suspend functions are optimized
suspend inline fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// After inlining, no extra state machine is created
suspend fun example() {
    val (data, time) = measureTime {
        fetchData()  // Only fetchData's state machine exists
    }
}
```

### Key Concepts Summary

1. **CPS Transformation**: Every `suspend fun foo(): T` becomes `fun foo(Continuation<T>): Any?`

2. **State Machine**: Function body split into states at suspension points

3. **Continuation**: Object that stores:
   - Current state (label)
   - Local variables
   - Reference to completion continuation

4. **COROUTINE_SUSPENDED**: Marker object indicating suspension

5. **No Thread Blocking**: When suspended, thread is released immediately

6. **Resumption**: `continuation.resumeWith()` called to continue execution

7. **Stack Unwinding**: Suspension unwinds the call stack; resumption rebuilds it

---


## Ответ (RU)

Suspend-функции в Kotlin приостанавливают выполнение без блокировки потока. Под капотом компилятор Kotlin преобразует suspend-функции в state machine (машину состояний), которая может приостанавливать и возобновлять выполнение.

### Основные Принципы Работы

1. **Continuation-Passing Style (CPS)**: Suspend-функция разбивается на несколько частей (continuations)
2. **State Machine**: Компилятор генерирует state machine с точками приостановки как состояниями
3. **Suspension**: Происходит когда выполняется асинхронный код (например, delay, withContext)
4. **Resumption**: Продолжает с точки остановки когда результат готов

### Преобразование Компилятором

```kotlin
// Исходный код:
suspend fun fetchUserData(userId: Int): User {
    val profile = fetchProfile(userId)    // Точка приостановки 1
    val settings = fetchSettings(userId)  // Точка приостановки 2
    return User(profile, settings)
}

// Что генерирует компилятор (концептуально):
fun fetchUserData(
    userId: Int,
    continuation: Continuation<User>
): Any? {
    val sm = continuation as? FetchUserDataSM
        ?: FetchUserDataSM(userId, continuation)

    when (sm.label) {
        0 -> {
            sm.label = 1
            if (fetchProfile(userId, sm) == COROUTINE_SUSPENDED)
                return COROUTINE_SUSPENDED
            sm.profile = result
        }
        1 -> {
            sm.label = 2
            if (fetchSettings(userId, sm) == COROUTINE_SUSPENDED)
                return COROUTINE_SUSPENDED
            sm.settings = result
        }
        2 -> {
            return User(sm.profile, sm.settings)
        }
    }
}
```

### Простой Пример Преобразования

```kotlin
// Оригинальный код
suspend fun simple(): String {
    delay(1000)
    return "Done"
}

// После компиляции (упрощенно)
fun simple(continuation: Continuation<String>): Any? {
    val sm = continuation as? SimpleSM ?: SimpleSM(continuation)

    when (sm.label) {
        0 -> {
            sm.label = 1
            val delayResult = delay(1000, sm)
            if (delayResult == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED
            }
        }
        1 -> {
            return "Done"
        }
    }
    throw IllegalStateException()
}
```

### State Machine С Локальными Переменными

```kotlin
// Оригинал: Функция с локальными переменными
suspend fun calculate(x: Int, y: Int): Int {
    val sum = x + y             // Локальная переменная
    delay(100)                  // Точка приостановки
    val product = sum * 2       // Другая локальная переменная
    delay(100)                  // Другая приостановка
    return product + x
}

// Скомпилировано: Переменные перемещены в state machine
fun calculate(
    x: Int,
    y: Int,
    continuation: Continuation<Int>
): Any? {
    val sm = continuation as? CalculateSM
        ?: CalculateSM(x, y, continuation)

    when (sm.label) {
        0 -> {
            sm.sum = x + y              // Сохранить в SM
            sm.label = 1
            if (delay(100, sm) == COROUTINE_SUSPENDED)
                return COROUTINE_SUSPENDED
        }
        1 -> {
            sm.product = sm.sum * 2     // Доступ из SM
            sm.label = 2
            if (delay(100, sm) == COROUTINE_SUSPENDED)
                return COROUTINE_SUSPENDED
        }
        2 -> {
            return sm.product + sm.x    // Доступ из SM
        }
    }
}
```

### Интерфейс Continuation

```kotlin
// Основной интерфейс для suspend-функций
public interface Continuation<in T> {
    // Контекст корутины
    public val context: CoroutineContext

    // Вызывается для возобновления корутины с результатом или исключением
    public fun resumeWith(result: Result<T>)
}

// Расширяющие функции
public inline fun <T> Continuation<T>.resume(value: T) {
    resumeWith(Result.success(value))
}

public inline fun <T> Continuation<T>.resumeWithException(exception: Throwable) {
    resumeWith(Result.failure(exception))
}
```

### Как Работает Приостановка

```kotlin
// 1. Вызов функции начинается с label 0
suspend fun example(): String {
    println("До приостановки")
    delay(1000)  // Точка приостановки
    println("После приостановки")
    return "Done"
}

// 2. Достигается delay, который возвращает COROUTINE_SUSPENDED
//    Функция возвращает COROUTINE_SUSPENDED вызывающему коду
//    Поток освобождается для другой работы

// 3. После завершения delay, планировщик вызывает:
continuation.resumeWith(Result.success(Unit))

// 4. Функция возобновляется с label 1
//    Продолжает с места остановки
//    Возвращает "Done"
```

### Вложенные Suspend Вызовы

```kotlin
// Оригинал: Вложенные suspend вызовы
suspend fun outer(): String {
    val result1 = inner1()  // Вызов другой suspend-функции
    val result2 = inner2()
    return "$result1 $result2"
}

suspend fun inner1(): String {
    delay(100)
    return "First"
}

suspend fun inner2(): String {
    delay(100)
    return "Second"
}

// Каждая функция имеет свой state machine
// Continuations связаны в цепочку
```

### Влияние На Производительность

```kotlin
// Каждая точка приостановки создает overhead state machine
suspend fun manySteps(): Int {
    delay(1)  // Состояние 0 -> 1
    delay(1)  // Состояние 1 -> 2
    delay(1)  // Состояние 2 -> 3
    delay(1)  // Состояние 3 -> 4
    delay(1)  // Состояние 4 -> 5
    return 42
}
// Создает state machine с 6 состояниями

// Меньше точек приостановки = меньше overhead
suspend fun optimized(): Int {
    delay(5)  // Только одно состояние 0 -> 1
    return 42
}
// Создает state machine с 2 состояниями
```

### Inline Suspend Функции

```kotlin
// inline suspend функции оптимизируются
suspend inline fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// После inlining дополнительный state machine не создается
suspend fun example() {
    val (data, time) = measureTime {
        fetchData()  // Существует только state machine fetchData
    }
}
```

### Ключевые Концепции

1. **CPS Transformation**: Каждая `suspend fun foo(): T` становится `fun foo(Continuation<T>): Any?`

2. **State Machine**: Тело функции разбивается на состояния в точках приостановки

3. **Continuation**: Объект, который хранит:
   - Текущее состояние (label)
   - Локальные переменные
   - Ссылку на completion continuation

4. **COROUTINE_SUSPENDED**: Объект-маркер, указывающий на приостановку

5. **Без блокировки потока**: При приостановке поток немедленно освобождается

6. **Resumption**: Вызывается `continuation.resumeWith()` для продолжения выполнения

7. **Stack Unwinding**: Приостановка разворачивает стек вызовов; возобновление восстанавливает его

**Резюме**: Suspend-функции в Kotlin преобразуются компилятором в state machine с использованием Continuation-Passing Style. Каждая точка приостановки (suspend вызов) разбивает функцию на состояния. При приостановке функция возвращает COROUTINE_SUSPENDED и освобождает поток. При возобновлении continuation.resumeWith() вызывается для продолжения с места остановки. Локальные переменные сохраняются в state machine классе. Этот механизм позволяет асинхронному коду выглядеть синхронным без блокировки потоков.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-suspend-function-return-type-after-compilation--programming-languages--hard]]
-
- [[q-synchronized-blocks-with-coroutines--programming-languages--medium]]

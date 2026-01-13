---
'---id': lang-056
title: How Suspend Function Detects Suspension / Как suspend функция определяет приостановку
aliases:
- How Suspend Function Detects Suspension
- Как suspend функция определяет приостановку
topic: kotlin
subtopics:
- coroutines
- functions
- types
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-coroutines
- c-kotlin
- c-stateflow
created: 2025-10-15
updated: 2025-11-11
tags:
- concurrency
- coroutines
- difficulty/hard
- kotlin
- suspension
anki_cards:
- slug: q-how-suspend-function-detects-suspension--kotlin--hard-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-how-suspend-function-detects-suspension--kotlin--hard-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> Как suspend функция определяет приостановку?

---

# Question (EN)
> How does a suspend function detect suspension?

## Ответ (RU)

Suspend-функция сама по себе ничего не "определяет". Компилятор Kotlin трансформирует её в:

- конечный автомат (state machine) с метками состояний;
- функцию, принимающую `Continuation`, в котором хранятся локальные переменные и текущая позиция;
- протокол, где вызовы других suspend-функций возвращают либо результат, либо специальный маркер `COROUTINE_SUSPENDED`.

Когда внутренняя suspend-функция возвращает `COROUTINE_SUSPENDED`, сгенерированный код внешней функции:

- сохраняет состояние (метку, локальные переменные) в continuation;
- немедленно возвращает `COROUTINE_SUSPENDED` вызывающему коду;
- передаёт управление рантайму/диспетчеру, который решает, когда и на каком потоке вызвать `resumeWith` у continuation.

То есть "обнаружение приостановки" — это проверка возвращаемого значения (`=== COROUTINE_SUSPENDED`) в сгенерированной машиной состояний функции, а не активное решение пользователем.

### Понимание Механизма

```kotlin
// Исходный код
suspend fun example(): String {
    println("Step 1")
    delay(1000)  // Потенциальная точка приостановки
    println("Step 2")
    return "Done"
}

// Концептуальная трансформация компилятором (упрощено; не буквальный код stdlib/composer)
fun example(continuation: Continuation<String>): Any? {
    val sm = continuation as? ExampleStateMachine
        ?: ExampleStateMachine(continuation)

    when (sm.label) {
        0 -> {
            println("Step 1")
            sm.label = 1
            val result = delay(1000, sm)  // Вызов suspend-функции в CPS-форме

            if (result === COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // Сигнал приостановки вызывающему коду
            }
            // Если не приостановилось (результат пришёл синхронно), двигаемся к следующему состоянию
        }
        1 -> {
            // Возобновление после delay
            println("Step 2")
            return "Done"
        }
    }
    throw IllegalStateException("Invalid state")
}
```

### 1. Маркер COROUTINE_SUSPENDED

```kotlin
// Внутренний маркер, используемый корутинными примитивами (концептуально)
internal object COROUTINE_SUSPENDED

// Когда suspend-функция может приостановиться:
suspend fun fetchData(): String {
    delay(1000)
    return "Data"
}

// Концептуально скомпилированная версия (упрощено)
fun fetchData(cont: Continuation<String>): Any? {
    val r = delay(1000, cont)

    if (r === COROUTINE_SUSPENDED) {
        // Сообщаем вызывающему коду о приостановке
        return COROUTINE_SUSPENDED
    }

    // Если результат пришёл синхронно, продолжаем обычно
    return "Data"
}
```

Ключевой момент: используется ссылочное сравнение (`===`), так как `COROUTINE_SUSPENDED` — это одиночный маркер.

### 2. Continuation И Кадр Состояния

```kotlin
// Интерфейс Continuation
interface Continuation<in T> {
    val context: CoroutineContext
    fun resumeWith(result: Result<T>)
}

// Пример: компилятор гарантирует сохранение локального состояния при приостановке
suspend fun multiStep(): String {
    val r1 = step1()  // Может приостановиться
    val r2 = step2()  // Может приостановиться
    return "${'$'}r1, ${'$'}r2"
}

// Концептуальный держатель состояния (схематично)
class MultiStepContinuation(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var r1: String? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        // Реальный сгенерированный код использует label и result
        // и вызывает multiStep(this) (или соответствующую функцию), чтобы продолжить выполнение.
        multiStep(this as Continuation<String>)
    }
}
```

Это иллюстрация; реальный код сложнее, но следует той же идее.

### 3. Метки Автомата Состояний

```kotlin
// Исходная suspend-функция
suspend fun complexOperation(): Int {
    val a = operation1()
    val b = operation2()
    val c = operation3()
    return a + b + c
}

// Упрощённый концептуальный автомат состояний (схематично)
fun complexOperation(cont: Continuation<Int>): Any? {
    val sm = cont as ComplexOperationSM

    when (sm.label) {
        0 -> {
            sm.label = 1
            val r = operation1(sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.a = r as Int
        }
        1 -> {
            sm.label = 2
            val r = operation2(sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.b = r as Int
        }
        2 -> {
            sm.label = 3
            val r = operation3(sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.c = r as Int
        }
        3 -> {
            return sm.a + sm.b + sm.c
        }
    }
    throw IllegalStateException("Invalid state")
}
```

(Нотация схематичная; в реальности используется тот же принцип: метки + проверки `COROUTINE_SUSPENDED`.)

### 4. Как Работает suspendCoroutine

```kotlin
import kotlin.coroutines.*
import kotlin.coroutines.intrinsics.*

// Низкоуровневая приостановка с помощью suspendCoroutine
suspend fun customSuspend(): String = suspendCoroutine { continuation ->
    // Этот лямбда-блок выполняется сразу в текущем контексте

    Thread {
        Thread.sleep(1000)
        // Позже возобновляем с результатом
        continuation.resume("Result")
    }.start()

    // Возврат из блока без немедленного resume
    // приводит к тому, что suspendCoroutine логически возвращает COROUTINE_SUSPENDED вызывающему коду.
}

// Приблизительная реализация (упрощено; детали зависят от версии stdlib)
inline suspend fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T = suspendCoroutineUninterceptedOrReturn { uCont ->
    val cont = uCont.intercepted()
    block(cont)
    COROUTINE_SUSPENDED  // Или немедленный результат, если завершено синхронно
}
```

На практике реализация использует дополнительную обёртку (например, `SafeContinuation` в некоторых версиях), которая возвращает либо значение, либо `COROUTINE_SUSPENDED` в зависимости от того, был ли вызван `resume` синхронно. Это деталь реализации; концептуальный протокол остаётся тем же.

### 5. Практический Взгляд: Может Приостановиться Vs Действительно Приостанавливается

Suspend-функция:

- может завершиться синхронно (без фактической приостановки);
- или может приостановиться, возвращая `COROUTINE_SUSPENDED` (из сгенерированного кода) и позже быть возобновлённой через `Continuation.resumeWith`.

Обычно не нужно пытаться "определять" в рантайме, была ли приостановка; о точках приостановки рассуждают статически по коду.

```kotlin
suspend fun mightNotSuspend(value: Int): Int {
    return if (value > 0) {
        value * 2           // Завершается синхронно
    } else {
        delay(100)          // Может приостановиться
        0
    }
}
```

### 6. Диспетчер И Переключение Потоков

```kotlin
import kotlinx.coroutines.*

suspend fun demonstrateDispatcherSwitch() = coroutineScope {
    println("Before withContext, thread: ${'$'}{Thread.currentThread().name}")

    withContext(Dispatchers.IO) {
        println("Inside IO, thread: ${'$'}{Thread.currentThread().name}")
        // Здесь withContext может приостановить выполнение при переключении контекста;
        // продолжение возобновляется на целевом диспетчере.
    }

    println("After withContext, thread: ${'$'}{Thread.currentThread().name}")
}
```

Важно: `withContext` реализован через низкоуровневые API continuation и диспетчера. Для этой темы главное: приостановка представлена через протокол `COROUTINE_SUSPENDED` и возобновление через `resumeWith` на нужном диспетчере.

### 7. Идентификация Точек Приостановки (концептуально)

```kotlin
import kotlinx.coroutines.*

suspend fun identifySuspensionPoints() = coroutineScope {
    println("Not suspended")

    delay(100)  // ТОЧКА ПРИОСТАНОВКИ: может вернуть COROUTINE_SUSPENDED
    println("Resumed after delay")

    withContext(Dispatchers.IO) {  // ТОЧКА ПРИОСТАНОВКИ: возможное переключение контекста
        println("On IO thread")
    }

    yield()  // ТОЧКА ПРИОСТАНОВКИ: кооперативная передача управления

    val data = async { fetchData() }.await()  // ТОЧКА ПРИОСТАНОВКИ: await
    println("All done: ${'$'}data")
}

suspend fun fetchData(): String {
    delay(50)
    return "Data"
}
```

Комментарии показывают, где компилятор вставляет проверки `COROUTINE_SUSPENDED` и управляет состоянием.

### 8. Внутренняя Приостановка Через Intrinsics

```kotlin
import kotlin.coroutines.Continuation
import kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED
import kotlin.coroutines.intrinsics.suspendCoroutineUninterceptedOrReturn

suspend fun rawSuspension(): String = suspendCoroutineUninterceptedOrReturn { cont ->
    val shouldSuspend = true

    if (shouldSuspend) {
        Thread {
            Thread.sleep(1000)
            cont.resumeWith(Result.success("Resumed"))
        }.start()
        COROUTINE_SUSPENDED  // Сигнализируем, что произошла приостановка
    } else {
        "Immediate result"  // Синхронное завершение; без приостановки
    }
}
```

Это показывает базовый протокол: вернуть значение для завершения или `COROUTINE_SUSPENDED` и позже вызвать `resumeWith`.

### 9. Перехват Continuation (для наблюдения)

```kotlin
import kotlin.coroutines.*

// ContinuationInterceptor может оборачивать возобновления; он не получает
// автоматический колбэк "на каждую приостановку", но позволяет наблюдать возобновления.
class LoggingInterceptor : ContinuationInterceptor {
    override val key: CoroutineContext.Key<*> = ContinuationInterceptor

    override fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T> {
        return object : Continuation<T> {
            override val context: CoroutineContext = continuation.context

            override fun resumeWith(result: Result<T>) {
                println("Resuming continuation with result: ${'$'}result")
                continuation.resumeWith(result)
            }
        }
    }
}

suspend fun observeSuspension() = withContext(LoggingInterceptor()) {
    println("Before delay")
    kotlinx.coroutines.delay(100)
    println("After delay")
}
```

Важно: так можно перехватывать возобновления; для точного подсчёта приостановок нужна более сложная логика.

### 10. Ключевые Моменты (сводка)

1. `COROUTINE_SUSPENDED` — специальный маркер, которым suspend-функции в CPS-форме сигнализируют приостановку.
2. Компилятор преобразует suspend-функции в автоматы состояний с метками и параметром `Continuation`.
3. `Continuation` хранит состояние и возобновляется через `resumeWith`, когда результат готов.
4. Разработчику обычно не нужно вручную сравнивать с `COROUTINE_SUSPENDED`; этим занимается сгенерированный код и билдеры корутин.
5. Приостановка освобождает текущий поток, позволяя выполнять другую работу.
6. На месте вызова "обнаружение" приостановки — это проверка, вернул ли вызываемый код `COROUTINE_SUSPENDED` (через `===`) и, при необходимости, сохранение состояния и проброс этого маркера выше.

### Что Концептуально Вызывает Приостановку

```kotlin
// Типичные API корутин, которые могут приостанавливать:

kotlinx.coroutines.delay(1000)
kotlinx.coroutines.withContext(Dispatchers.IO) { }
kotlinx.coroutines.yield()
async { }.await()
mutex.lock()
channel.receive()
flow.collect { }

// Обычные, не приостанавливающие операции:
println("Hello")
val x = 5 + 3
if (condition) { /* ... */ }
```

Эти примеры концептуальны: точное поведение (например, при delay(0)) может отличаться, но протокол приостановки всегда реализован через сгенерированный автомат состояний и механизм `COROUTINE_SUSPENDED`/`Continuation`.

## Answer (EN)

A suspend function does not actively "detect" suspension. The Kotlin compiler rewrites it into:

- a state machine with labels for each suspension point;
- a function that takes a `Continuation`, which stores local variables and the current position;
- a protocol where calls to other suspend functions return either a value or the special marker `COROUTINE_SUSPENDED`.

When an inner suspend call returns `COROUTINE_SUSPENDED`, the generated code of the caller:

- stores its state (label, locals) in the continuation;
- immediately returns `COROUTINE_SUSPENDED` to its caller;
- lets the runtime/dispatcher decide when and on which thread to invoke `resumeWith` on the continuation.

So "detecting suspension" is simply checking the returned value against `COROUTINE_SUSPENDED` inside the compiler-generated state machine, not something you implement manually.

### Understanding the Mechanism

```kotlin
// Source code
suspend fun example(): String {
    println("Step 1")
    delay(1000)  // Potential suspension point
    println("Step 2")
    return "Done"
}

// Conceptual compiler transformation (simplified; not exact production code)
fun example(continuation: Continuation<String>): Any? {
    val sm = continuation as? ExampleStateMachine
        ?: ExampleStateMachine(continuation)

    when (sm.label) {
        0 -> {
            println("Step 1")
            sm.label = 1
            val result = delay(1000, sm)  // Call suspend function in CPS form

            if (result === COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // Signal suspension to caller
            }
            // If not suspended (completed synchronously), proceed to the next-state logic
        }
        1 -> {
            // Resumed after delay
            println("Step 2")
            return "Done"
        }
    }
    throw IllegalStateException("Invalid state")
}
```

### 1. COROUTINE_SUSPENDED Marker

```kotlin
// Internal marker used by coroutine intrinsics (conceptual)
internal object COROUTINE_SUSPENDED

// When a suspend function may suspend:
suspend fun fetchData(): String {
    delay(1000)
    return "Data"
}

// Conceptually compiled version (simplified)
fun fetchData(cont: Continuation<String>): Any? {
    val r = delay(1000, cont)

    if (r === COROUTINE_SUSPENDED) {
        // Indicate to caller that execution is suspended
        return COROUTINE_SUSPENDED
    }

    // If resumed synchronously with a result, continue normally
    return "Data"
}
```

Key point: the check must use referential equality (`===`) because `COROUTINE_SUSPENDED` is a singleton marker.

### 2. Continuation Frame

```kotlin
// The Continuation interface
interface Continuation<in T> {
    val context: CoroutineContext
    fun resumeWith(result: Result<T>)
}

// Example: compiler ensures locals/state survive suspension
suspend fun multiStep(): String {
    val r1 = step1()  // May suspend
    val r2 = step2()  // May suspend
    return "${'$'}r1, ${'$'}r2"
}

// Conceptual state machine holder (schematic)
class MultiStepContinuation(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var r1: String? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        // In reality the compiler-generated code inspects label and result
        // and calls back into multiStep(this) (or its compiled body) to continue execution.
        multiStep(this as Continuation<String>)
    }
}
```

This is illustrative only; actual generated code is more complex but follows this pattern.

### 3. State Machine Labels

```kotlin
// Original suspend function
suspend fun complexOperation(): Int {
    val a = operation1()
    val b = operation2()
    val c = operation3()
    return a + b + c
}

// Simplified conceptual state machine (schematic)
fun complexOperation(cont: Continuation<Int>): Any? {
    val sm = cont as ComplexOperationSM

    when (sm.label) {
        0 -> {
            sm.label = 1
            val r = operation1(sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.a = r as Int
        }
        1 -> {
            sm.label = 2
            val r = operation2(sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.b = r as Int
        }
        2 -> {
            sm.label = 3
            val r = operation3(sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.c = r as Int
        }
        3 -> {
            return sm.a + sm.b + sm.c
        }
    }
    throw IllegalStateException("Invalid state")
}
```

(Notation is schematic; real code differs but uses the same idea: labels + `COROUTINE_SUSPENDED` checks.)

### 4. How suspendCoroutine Works

```kotlin
import kotlin.coroutines.*
import kotlin.coroutines.intrinsics.*

// Low-level suspension using suspendCoroutine
suspend fun customSuspend(): String = suspendCoroutine { continuation ->
    // This lambda runs immediately in the current context

    Thread {
        Thread.sleep(1000)
        // Resume later with result
        continuation.resume("Result")
    }.start()

    // Returning from this block without resuming immediately
    // means suspendCoroutine logically returns COROUTINE_SUSPENDED to its caller.
}

// Rough idea of implementation (simplified; concrete stdlib code may vary)
inline suspend fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T = suspendCoroutineUninterceptedOrReturn { uCont ->
    val cont = uCont.intercepted()
    block(cont)
    COROUTINE_SUSPENDED  // Or an immediate result if completed synchronously
}
```

In practice the implementation uses an extra wrapper (e.g. `SafeContinuation` in some versions) that returns either a value or `COROUTINE_SUSPENDED` depending on whether `resume` was called synchronously. This is an implementation detail; the conceptual protocol is stable.

### 5. Practical View: May Suspend Vs Does Suspend

A suspend function:

- may complete synchronously (no actual suspension);
- or may suspend by returning `COROUTINE_SUSPENDED` (from generated code) and later being resumed via `Continuation.resumeWith`.

You generally should not try to "detect" at runtime whether a call suspended; you reason about suspension points statically.

```kotlin
suspend fun mightNotSuspend(value: Int): Int {
    return if (value > 0) {
        value * 2           // completes synchronously
    } else {
        delay(100)          // may suspend
        0
    }
}
```

### 6. Dispatcher and Thread Switching

```kotlin
import kotlinx.coroutines.*

suspend fun demonstrateDispatcherSwitch() = coroutineScope {
    println("Before withContext, thread: ${'$'}{Thread.currentThread().name}")

    withContext(Dispatchers.IO) {
        println("Inside IO, thread: ${'$'}{Thread.currentThread().name}")
        // withContext may suspend when switching context; the continuation
        // is resumed on the target dispatcher.
    }

    println("After withContext, thread: ${'$'}{Thread.currentThread().name}")
}
```

Important: `withContext` is implemented using low-level continuation and dispatcher APIs. The key idea for this note: suspension is represented using the `COROUTINE_SUSPENDED` protocol and resumption via `resumeWith` on the appropriate dispatcher.

### 7. Identifying Suspension Points (Conceptually)

```kotlin
import kotlinx.coroutines.*

suspend fun identifySuspensionPoints() = coroutineScope {
    println("Not suspended")

    delay(100)  // SUSPENSION POINT: may return COROUTINE_SUSPENDED
    println("Resumed after delay")

    withContext(Dispatchers.IO) {  // SUSPENSION POINT: possible context switch
        println("On IO thread")
    }

    yield()  // SUSPENSION POINT: cooperative yielding

    val data = async { fetchData() }.await()  // SUSPENSION POINT: await
    println("All done: ${'$'}data")
}

suspend fun fetchData(): String {
    delay(50)
    return "Data"
}
```

These comments indicate where the compiler inserts checks for `COROUTINE_SUSPENDED` and manages state.

### 8. Internal Suspension with Intrinsics

```kotlin
import kotlin.coroutines.Continuation
import kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED
import kotlin.coroutines.intrinsics.suspendCoroutineUninterceptedOrReturn

suspend fun rawSuspension(): String = suspendCoroutineUninterceptedOrReturn { cont ->
    val shouldSuspend = true

    if (shouldSuspend) {
        Thread {
            Thread.sleep(1000)
            cont.resumeWith(Result.success("Resumed"))
        }.start()
        COROUTINE_SUSPENDED  // Signal that we suspended
    } else {
        "Immediate result"  // Complete synchronously; no suspension
    }
}
```

This shows the core protocol: return a value to complete, or `COROUTINE_SUSPENDED` and later call `resumeWith`.

### 9. Continuation Interception (Observation Only)

```kotlin
import kotlin.coroutines.*

// ContinuationInterceptor can wrap resumptions; it does not automatically
// get a callback "on each suspension", but can observe when continuations resume.
class LoggingInterceptor : ContinuationInterceptor {
    override val key: CoroutineContext.Key<*> = ContinuationInterceptor

    override fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T> {
        return object : Continuation<T> {
            override val context: CoroutineContext = continuation.context

            override fun resumeWith(result: Result<T>) {
                println("Resuming continuation with result: ${'$'}result")
                continuation.resumeWith(result)
            }
        }
    }
}

suspend fun observeSuspension() = withContext(LoggingInterceptor()) {
    println("Before delay")
    kotlinx.coroutines.delay(100)
    println("After delay")
}
```

Note: This illustrates that you can intercept resume events; it does not reliably count individual suspensions without more complex handling.

### 10. Key Points (Consolidated)

1. `COROUTINE_SUSPENDED` is a special marker used by the coroutine machinery; suspend functions compiled to CPS return it to indicate suspension.
2. The compiler transforms suspend functions into state machines with labels and a `Continuation` parameter.
3. `Continuation` holds state and is resumed with `resumeWith` once the result is ready.
4. Developers usually do not need to manually detect or compare with `COROUTINE_SUSPENDED`; this is handled by compiler-generated code and coroutine builders.
5. Suspension releases the current thread while the coroutine is waiting, allowing other work to run.
6. At a call site, "detecting" suspension means checking if the callee returned `COROUTINE_SUSPENDED` (using `===`) and, if so, propagating it and saving state.

### What Causes Suspension (Conceptually)

```kotlin
// Typical coroutine APIs that may suspend:

kotlinx.coroutines.delay(1000)
kotlinx.coroutines.withContext(Dispatchers.IO) { }
kotlinx.coroutines.yield()
async { }.await()
mutex.lock()
channel.receive()
flow.collect { }

// Non-suspending, regular operations:
println("Hello")
val x = 5 + 3
if (condition) { /* ... */ }
```

These examples are conceptual: exact behavior (e.g., whether delay actually suspends for 0ms) can vary, but the suspension protocol is always implemented via the compiler-generated state machine and the `COROUTINE_SUSPENDED`/`Continuation` mechanism.

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Related Questions

- [[q-how-to-create-suspend-function--kotlin--medium]]

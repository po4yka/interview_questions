---
id: lang-062
title: "Suspend Function Suspension Mechanism / Механизм приостановки suspend функции"
aliases: [Suspend Function Suspension Mechanism, Механизм приостановки suspend функции]
topic: kotlin
subtopics: [coroutines, suspension]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-list-vs-sequence--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/hard, kotlin, programming-languages, suspension]
date created: Friday, October 31st 2025, 6:31:50 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---

# Вопрос (RU)
> Как работает механизм приостановки в suspend-функциях?

# Question (EN)
> How does the suspension mechanism work in suspend functions?

## Ответ (RU)

Когда выполнение `suspend`-функции приостанавливается:

1. Её состояние (текущая позиция, локальные переменные, контекст) сохраняется во внутренней структуре — сгенерированном компилятором объекте state machine, который реализует или использует `Continuation` и связан с ним.
2. Текущий поток не обязан блокироваться: если используемая `suspend`-функция реализована неблокирующим образом (например, `delay`), поток освобождается и может быть использован для другой работы (при корректной реализации диспетчеров корутин). Если внутри `suspend`-функции вызывается обычная блокирующая операция, поток всё ещё будет блокироваться.
3. Позже выполнение возобновляется с точки приостановки так, как будто функция продолжила выполнение обычным образом, но фактический поток возобновления определяется диспетчером.

Это реализуется за счёт:
- трансформации `suspend`-функций компилятором Kotlin в конечный автомат (state machine);
- представления вызовов в стиле CPS (Continuation-Passing Style), когда под капотом добавляется скрытый параметр `Continuation`;
- использования специального маркера (например, `COROUTINE_SUSPENDED`) для сигнализации о приостановке и последующем возобновлении через вызов `continuation.resumeWith()`;
- того, что `suspend` — это compile-time контракт: фактическая асинхронность и неблокирующее поведение зависят от реализации вызываемых `suspend`-функций и используемых диспетчеров.

### Continuation-объект

```kotlin
// Интерфейс Continuation, который описывает продолжение и хранит контекст
interface Continuation<in T> {
    val context: CoroutineContext
    fun resumeWith(result: Result<T>)
}

// Концептуальная трансформация сигнатуры suspend-функции
// Было: suspend fun getData(): String
// Стало: fun getData(continuation: Continuation<String>): Any?
// (Фактически компилятор генерирует state machine-класс, который использует этот continuation.)
```

### Пример State Machine (иллюстративный)

```kotlin
// Исходный код:
suspend fun example(): String {
    val a = step1()  // Точка приостановки 1
    val b = step2()  // Точка приостановки 2
    return "$a $b"
}

// Упрощённый концептуальный state machine, генерируемый компилятором:
fun example(continuation: Continuation<String>): Any? {
    val sm = continuation as? ExampleStateMachine
        ?: ExampleStateMachine(continuation)

    when (sm.label) {
        0 -> {
            sm.label = 1
            val result = step1(sm)
            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // Поток здесь не блокируется для неблокирующей реализации
            }
            sm.a = result as String
            // Падение далее в when с обновлённой label
        }
        1 -> {
            sm.label = 2
            val result = step2(sm)
            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED
            }
            sm.b = result as String
        }
        2 -> {
            return "${'$'}{sm.a} ${'$'}{sm.b}"
        }
    }
}

// Класс state machine хранит локальные переменные и использует completion
class ExampleStateMachine(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var a: String? = null  // Локальная переменная сохраняется
    var b: String? = null  // Локальная переменная сохраняется

    override fun resumeWith(result: Result<Any?>) {
        // В реальной реализации сюда попадает result (значение или исключение),
        // и state machine обновляет своё состояние в зависимости от него.
        example(this)  // Возобновление с точки приостановки (упрощённо)
    }

    override val context: CoroutineContext
        get() = completion.context
}
```

### Как Работает Приостановка

```kotlin
// Пошаговое выполнение

// 1. Функция стартует
suspend fun fetchData(): String {
    println("Start")
    delay(1000)  // Точка приостановки
    println("Resume")
    return "Data"
}

// 2. Внутри delay вызывается suspend-функция, которая
//    при асинхронной реализации возвращает COROUTINE_SUSPENDED state machine-у:
//    - Сохраняется состояние: label = 1, локальные переменные
//    - Поток не блокируется; диспетчер может выполнять другие корутины на этом потоке

// 3. Через 1000 мс планировщик/таймер вызывает что-то вроде:
//    continuation.resumeWith(Result.success(Unit))

// 4. State machine возобновляет выполнение с label = 1
//    - Продолжает исполнение (может быть на том же или другом потоке в зависимости от диспетчера)
//    - В итоге возвращает "Data"
```

### Реальный Пример С Локальными Переменными (иллюстративный)

```kotlin
// Исходный код
suspend fun calculate(x: Int, y: Int): Int {
    val sum = x + y           // Обычный код
    delay(100)                // Точка приостановки
    val doubled = sum * 2     // Код после возобновления
    delay(100)                // Ещё одна приостановка
    return doubled + 10
}

// Концептуальная скомпилированная форма: переменные переносятся в state machine
class CalculateSM(
    val x: Int,
    val y: Int,
    val completion: Continuation<Int>
) : Continuation<Any?> {
    var label = 0
    var sum: Int = 0      // Сохраняется между приостановками
    var doubled: Int = 0  // Сохраняется между приостановками

    override fun resumeWith(result: Result<Any?>) {
        // В реальности здесь учитывался бы result (значение/исключение);
        // это иллюстрация механизма возобновления.
        calculate(x, y, this)
    }

    override val context: CoroutineContext get() = completion.context
}
```

### Механизм Освобождения Потока

```kotlin
fun demonstrateThreadRelease() = runBlocking {
    println("Thread: ${'$'}{Thread.currentThread().name}")

    launch {
        println("Before delay: ${'$'}{Thread.currentThread().name}")
        delay(1000)  // Неблокирующая приостановка; поток может быть освобождён
        println("After delay: ${'$'}{Thread.currentThread().name}")  // Может быть тот же или другой поток
    }

    // Тот же поток может выполнять другие корутины во время delay
    launch {
        println("Other coroutine: ${'$'}{Thread.currentThread().name}")
    }
}
```

### Процесс Возобновления

```kotlin
// Когда корутина готова к возобновлению:
// 1. Планировщик/колбэк получает сохранённый continuation/state machine.
// 2. Вызывает continuation.resumeWith(result).
// 3. State machine переходит к сохранённой метке (label).
// 4. Исполнение продолжается с нужного места, на потоке, выбранном диспетчером.

class DelayedContinuation(
    private val continuation: Continuation<Unit>,
    private val delayMs: Long
) {
    init {
        // Планирование возобновления (концептуальный пример)
        Timer().schedule(object : TimerTask() {
            override fun run() {
                continuation.resumeWith(Result.success(Unit))  // Корректное возобновление
            }
        }, delayMs)
    }
}
```

### Итог (RU)

Механизм приостановки концептуально:
1. Трансформация компилятором: `suspend`-функции превращаются в state machine с дополнительным параметром `Continuation`.
2. Сохранение состояния: локальные переменные и позиция исполнения хранятся в объекте state machine/continuation.
3. Неблокирующее поведение: при приостановке возвращается `COROUTINE_SUSPENDED`, и поток может быть освобождён, если реализация `suspend`-функции неблокирующая и используется корректный диспетчер.
4. Возобновление: внешний код/планировщик вызывает `continuation.resumeWith()`, и выполнение продолжается с сохранённого состояния на потоке, выбранном диспетчером.

Ключевые моменты:
- Поток не блокируется при корректной неблокирующей реализации точки приостановки.
- Состояние автоматически сохраняется сгенерированной компилятором инфраструктурой.
- Механизм в основном прозрачен для разработчика.
- Обеспечивает эффективное использование ресурсов и выразительный асинхронный код.
- Ключевой факт: `suspend` сам по себе не делает функцию асинхронной, он позволяет ей приостанавливаться в определённых точках.

## Answer (EN)

When execution of a suspend function is suspended:

1. The function state (current position, local variables, context) is captured in a compiler-generated state-machine object that implements or uses Continuation and is associated with it.
2. The current thread is not inherently blocked: if the suspending function at that point is implemented in a non-blocking way (e.g., `delay`), the thread is released and can run other work via coroutine dispatchers. If the suspend function performs a regular blocking call, that thread is still blocked.
3. Later, execution resumes from the exact suspension point as if the function had continued sequentially, but the actual thread used for resumption is determined by the dispatcher.

This is implemented through:
- state machine transformation by the Kotlin compiler;
- Continuation-passing style (CPS) transformation (a hidden Continuation parameter is added);
- use of a special marker (e.g., `COROUTINE_SUSPENDED`) to signal suspension and later resumption via `continuation.resumeWith()`;
- the fact that `suspend` is a compile-time contract: actual async/non-blocking behavior depends on the implementations of the suspending functions and dispatchers involved.

### Continuation Object

```kotlin
// The Continuation interface that describes a continuation and holds context
interface Continuation<in T> {
    val context: CoroutineContext
    fun resumeWith(result: Result<T>)
}

// Suspend function signature transformation (conceptual)
// From: suspend fun getData(): String
// To:   fun getData(continuation: Continuation<String>): Any?
// (In reality the compiler generates a state-machine class that uses this continuation.)
```

### State Machine Example (Illustrative)

```kotlin
// Original code you write:
suspend fun example(): String {
    val a = step1()  // Suspension point 1
    val b = step2()  // Suspension point 2
    return "$a $b"
}

// Conceptual compiler-generated state machine (simplified):
fun example(continuation: Continuation<String>): Any? {
    val sm = continuation as? ExampleStateMachine
        ?: ExampleStateMachine(continuation)

    when (sm.label) {
        0 -> {
            sm.label = 1
            val result = step1(sm)
            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // No thread is blocked for a non-blocking implementation
            }
            sm.a = result as String
            // Execution will continue with updated label
        }
        1 -> {
            sm.label = 2
            val result = step2(sm)
            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED
            }
            sm.b = result as String
        }
        2 -> {
            return "${'$'}{sm.a} ${'$'}{sm.b}"
        }
    }
}

// State machine class stores local variables and uses the completion continuation
class ExampleStateMachine(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var a: String? = null  // Local variable preserved
    var b: String? = null  // Local variable preserved

    override fun resumeWith(result: Result<Any?>) {
        // In a real implementation, `result` (value/exception) is inspected,
        // and the state machine updates its state accordingly.
        example(this)  // Resume from the suspension point (simplified)
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

// 2. At delay, the coroutine calls into a suspending function which,
//    for an asynchronous implementation, returns COROUTINE_SUSPENDED to the state machine:
//    - State is saved: label = 1, locals preserved
//    - No thread is blocked; the dispatcher can use the thread to run other coroutines

// 3. After 1000ms, the scheduler/timer calls something like:
//    continuation.resumeWith(Result.success(Unit))

// 4. The state machine resumes from label = 1
//    - Continues execution (possibly on the same or a different thread depending on dispatcher)
//    - Eventually returns "Data"
```

### Real Example with Local Variables (Illustrative)

```kotlin
// Source code
suspend fun calculate(x: Int, y: Int): Int {
    val sum = x + y           // Regular code
    delay(100)                // Suspension point
    val doubled = sum * 2     // Regular code after resume
    delay(100)                // Another suspension
    return doubled + 10
}

// Conceptual compiled form: variables moved into a state machine
class CalculateSM(
    val x: Int,
    val y: Int,
    val completion: Continuation<Int>
) : Continuation<Any?> {
    var label = 0
    var sum: Int = 0      // Preserved across suspensions
    var doubled: Int = 0  // Preserved across suspensions

    override fun resumeWith(result: Result<Any?>) {
        // Real implementation would inspect `result` (value/exception);
        // this is a simplified illustration of resumption.
        calculate(x, y, this)
    }

    override val context: CoroutineContext get() = completion.context
}
```

### Thread Release Mechanism

```kotlin
fun demonstrateThreadRelease() = runBlocking {
    println("Thread: ${'$'}{Thread.currentThread().name}")

    launch {
        println("Before delay: ${'$'}{Thread.currentThread().name}")
        delay(1000)  // Non-blocking suspension; the thread can be released
        println("After delay: ${'$'}{Thread.currentThread().name}")  // May be same or different thread
    }

    // The same underlying thread can execute other coroutines during delay
    launch {
        println("Other coroutine: ${'$'}{Thread.currentThread().name}")
    }
}
```

### Resumption Process

```kotlin
// When a coroutine is ready to resume:
// 1. The scheduler/callback retrieves the stored continuation/state machine.
// 2. Calls continuation.resumeWith(result).
// 3. The state machine jumps to the saved label.
// 4. Execution continues from that point, on a thread chosen by the dispatcher.

class DelayedContinuation(
    private val continuation: Continuation<Unit>,
    private val delayMs: Long
) {
    init {
        // Schedule resumption (conceptual example)
        Timer().schedule(object : TimerTask() {
            override fun run() {
                continuation.resumeWith(Result.success(Unit))  // Correct resume call
            }
        }, delayMs)
    }
}
```

### Summary

Suspension mechanism (conceptually):
1. Compiler transformation: suspend functions become a state machine with an extra Continuation parameter.
2. State preservation: local variables and execution position are stored in the state-machine/continuation object.
3. Non-blocking behavior: on suspension, `COROUTINE_SUSPENDED` is returned and the thread can be released if the suspending function is implemented in a non-blocking way and the dispatcher cooperates.
4. Resumption: external code/scheduler calls `continuation.resumeWith()`, and execution continues from the saved state on a dispatcher-selected thread.

Key points:
- No thread is inherently blocked during proper non-blocking suspension.
- State is preserved automatically by compiler-generated machinery.
- The mechanism is mostly transparent to the developer.
- Enables efficient resource usage and expressive async code.
- Crucially, `suspend` alone does not make code asynchronous; it enables well-defined suspension points.

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этого механизма от подхода в Java без `suspend`/корутин?
- Когда практически стоит использовать `suspend`-функции и корутины?
- Каковы распространённые подводные камни при работе с приостановкой?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-coroutines]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [[c-coroutines]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-list-vs-sequence--programming-languages--medium]]

## Related Questions

- [[q-list-vs-sequence--programming-languages--medium]]

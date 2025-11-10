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
related: [c-kotlin, c-coroutines, q-list-vs-sequence--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/hard, kotlin, programming-languages, suspension]
---
# Вопрос (RU)
> Как работает механизм приостановки в suspend-функциях?

# Question (EN)
> How does the suspension mechanism work in suspend functions?

## Ответ (RU)

Когда выполнение `suspend`-функции приостанавливается:

1. Её состояние (текущая позиция, локальные переменные, контекст) сохраняется во внутренней структуре, связанной с `Continuation`-объектом.
2. Текущий поток не блокируется и может быть использован для другой работы (при корректной реализации диспетчеров корутин).
3. Позже выполнение возобновляется с точки приостановки так, как будто функция продолжила выполнение обычным образом.

Это реализуется за счёт:
- трансформации `suspend`-функций компилятором Kotlin в конечный автомат (state machine);
- представления вызовов в стиле CPS (Continuation-Passing Style), когда под капотом добавляется скрытый параметр `Continuation`;
- использования специального маркера (например, `COROUTINE_SUSPENDED`) для сигнализации о приостановке и последующем возобновлении через вызов `continuation.resumeWith()`.

### Continuation-объект

```kotlin
// Интерфейс Continuation, который хранит контекст и завершение
interface Continuation<in T> {
    val context: CoroutineContext
    fun resumeWith(result: Result<T>)
}

// Концептуальная трансформация сигнатуры suspend-функции
// Было: suspend fun getData(): String
// Стало: fun getData(continuation: Continuation<String>): Any?
```

### Пример state machine (иллюстративный)

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
                return COROUTINE_SUSPENDED  // Поток здесь не блокируется
            }
            sm.a = result as String
        }
        1 -> {
            sm.label = 2
            val result = step2(sm)
            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // Поток здесь не блокируется
            }
            sm.b = result as String
        }
        2 -> {
            return "${'$'}{sm.a} ${'$'}{sm.b}"
        }
    }
}

// Класс state machine хранит локальные переменные и continuation
class ExampleStateMachine(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var a: String? = null  // Локальная переменная сохраняется
    var b: String? = null  // Локальная переменная сохраняется

    override fun resumeWith(result: Result<Any?>) {
        // В реальной реализации результат/исключения обрабатываются;
        // здесь упрощённый пример.
        example(this)  // Возобновление с точки приостановки
    }

    override val context: CoroutineContext
        get() = completion.context
}
```

### Как работает приостановка

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
//    возвращает COROUTINE_SUSPENDED state machine-у:
//    - Сохраняется состояние: label = 1, локальные переменные
//    - Поток не блокируется; диспетчер может выполнять другие корутины

// 3. Через 1000 мс планировщик/таймер вызывает:
//    continuation.resumeWith(Result.success(Unit))

// 4. State machine возобновляет выполнение с label = 1
//    - Продолжает исполнение
//    - В итоге возвращает "Data"
```

### Реальный пример с локальными переменными (иллюстративный)

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
        // В реальности здесь учитывался бы result.
        calculate(x, y, this)
    }

    override val context: CoroutineContext get() = completion.context
}
```

### Механизм освобождения потока

```kotlin
fun demonstrateThreadRelease() = runBlocking {
    println("Thread: ${'$'}{Thread.currentThread().name}")

    launch {
        println("Before delay: ${'$'}{Thread.currentThread().name}")
        delay(1000)  // Неблокирующая приостановка; поток не удерживается
        println("After delay: ${'$'}{Thread.currentThread().name}")  // Может быть тот же или другой поток
    }

    // Тот же поток может выполнять другие корутины во время delay
    launch {
        println("Other coroutine: ${'$'}{Thread.currentThread().name}")
    }
}
```

### Процесс возобновления

```kotlin
// Когда корутина готова к возобновлению:
// 1. Планировщик/колбэк получает сохранённый continuation.
// 2. Вызывает continuation.resumeWith(result).
// 3. State machine переходит к сохранённой метке (label).
// 4. Исполнение продолжается с нужного места.

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
2. Сохранение состояния: локальные переменные и позиция исполнения хранятся в объекте continuation/state machine.
3. Неблокирующее поведение: при приостановке возвращается `COROUTINE_SUSPENDED`, поток не блокируется (при корректной работе диспетчеров).
4. Возобновление: внешний код/планировщик вызывает `continuation.resumeWith()`, и выполнение продолжается с сохранённого состояния.

Ключевые моменты:
- Поток не блокируется при корректной реализации приостановки.
- Состояние автоматически сохраняется сгенерированной компилятором инфраструктурой.
- Механизм в основном прозрачен для разработчика.
- Обеспечивает эффективное использование ресурсов и выразительный асинхронный код.

## Answer (EN)

When execution of a suspend function is suspended:

1. The function state (current position, local variables, context) is captured in a Continuation object.
2. The current thread is not blocked and can be used for other work (with coroutine dispatchers implementing non-blocking suspension).
3. Later, execution resumes from the exact suspension point, as if the function had continued normally.

This is implemented through:
- state machine transformation by the Kotlin compiler;
- Continuation-passing style (CPS) transformation (a hidden Continuation parameter is added);
- use of a special marker (e.g., `COROUTINE_SUSPENDED`) to signal suspension and later resumption via `continuation.resumeWith()`.

### Continuation Object

```kotlin
// The Continuation interface that stores completion and context
interface Continuation<in T> {
    val context: CoroutineContext
    fun resumeWith(result: Result<T>)
}

// Suspend function signature transformation (conceptual)
// From: suspend fun getData(): String
// To:   fun getData(continuation: Continuation<String>): Any?
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
                return COROUTINE_SUSPENDED  // No thread is blocked here
            }
            sm.a = result as String
        }
        1 -> {
            sm.label = 2
            val result = step2(sm)
            if (result == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED  // No thread is blocked here
            }
            sm.b = result as String
        }
        2 -> {
            return "${'$'}{sm.a} ${'$'}{sm.b}"
        }
    }
}

// State machine class stores local variables and continuation
class ExampleStateMachine(
    val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var a: String? = null  // Local variable preserved
    var b: String? = null  // Local variable preserved

    override fun resumeWith(result: Result<Any?>) {
        // In a real implementation, `result` would be inspected to
        // propagate values/exceptions; this is simplified.
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

// 2. At delay, the coroutine calls into a suspending function that
//    returns COROUTINE_SUSPENDED to the state machine:
//    - State saved: label = 1, locals preserved
//    - No thread is blocked; dispatcher can run other coroutines

// 3. After 1000ms, the scheduler/timer calls:
//    continuation.resumeWith(Result.success(Unit))

// 4. State machine resumes from label = 1
//    - Continues execution
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

// Conceptual compiled form: variables moved to a state machine
class CalculateSM(
    val x: Int,
    val y: Int,
    val completion: Continuation<Int>
) : Continuation<Any?> {
    var label = 0
    var sum: Int = 0      // Preserved across suspensions
    var doubled: Int = 0  // Preserved across suspensions

    override fun resumeWith(result: Result<Any?>) {
        // Real implementation would use `result`.
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
        delay(1000)  // Non-blocking suspension; no thread is held waiting
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
// 1. The scheduler or callback finds the stored continuation.
// 2. Calls continuation.resumeWith(result).
// 3. The state machine jumps to the saved label.
// 4. Execution continues from that point.

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
2. State preservation: local variables and execution position are stored in the continuation/state machine.
3. Non-blocking behavior: on suspension, `COROUTINE_SUSPENDED` is returned, and no thread is blocked (with correct dispatcher implementation).
4. Resumption: external code/scheduler calls `continuation.resumeWith()`, and execution continues from the saved state.

Key points:
- No thread is inherently blocked during proper suspension.
- State is preserved automatically by compiler-generated machinery.
- The mechanism is mostly transparent to the developer.
- Enables efficient resource usage and expressive async code.

---

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

- [[q-list-vs-sequence--programming-languages--medium]]

## Related Questions

- [[q-list-vs-sequence--programming-languages--medium]]

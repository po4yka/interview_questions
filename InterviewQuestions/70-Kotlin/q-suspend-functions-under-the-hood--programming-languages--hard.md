---
id: lang-089
title: "Suspend Functions Under The Hood / Suspend функции в подробностях"
aliases: [Suspend Functions Under The Hood, Suspend функции в подробностях]
topic: kotlin
subtopics: [coroutines, compiler, implementation]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-suspend-function-return-type-after-compilation--programming-languages--hard, q-synchronized-blocks-with-coroutines--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [compiler, coroutines, difficulty/hard, kotlin]
---
# Вопрос (RU)
> Как работают suspend-функции под капотом?

# Question (EN)
> How do suspend functions work under the hood?

## Ответ (RU)

Suspend-функции в Kotlin позволяют приостанавливать выполнение без блокировки потока. Под капотом компилятор Kotlin преобразует suspend-функции в state machine (машину состояний) в стиле CPS (Continuation-Passing Style), которая может приостанавливать и возобновлять выполнение.

### Основные Принципы Работы

1. **Continuation-Passing Style (CPS)**: Каждая `suspend`-функция компилируется в обычную функцию, принимающую дополнительный параметр `Continuation<T>`, и возвращающую `Any?`, где `COROUTINE_SUSPENDED` сигнализирует о приостановке.
2. **State Machine**: Компилятор генерирует машину состояний, где каждая точка приостановки соответствует состоянию (`label`). Локальные переменные и прогресс выполнения сохраняются в специальном continuation-классе.
3. **Suspension**: При достижении точки приостановки (например, `delay`, другие `suspend`-функции) функция может вернуть `COROUTINE_SUSPENDED`, освободив текущий поток.
4. **Resumption**: Когда результат готов, вызывается `resumeWith` у соответствующего `Continuation`, и выполнение продолжается с сохранённого состояния.

### Преобразование Компилятором (Концептуально)

```kotlin
// Исходный код:
suspend fun fetchUserData(userId: Int): User {
    val profile = fetchProfile(userId)    // Точка приостановки 1
    val settings = fetchSettings(userId)  // Точка приостановки 2
    return User(profile, settings)
}

// Что делает компилятор (упрощенно и схематично):
fun fetchUserData(
    userId: Int,
    completion: Continuation<User>
): Any? {
    val sm = if (completion is FetchUserDataSM) completion
             else FetchUserDataSM(userId, completion)

    return sm.invokeSuspend(Unit)
}

// Сгенерированный (упрощенный) continuation/state-machine
class FetchUserDataSM(
    private val userId: Int,
    private val completion: Continuation<User>
) : Continuation<Any?> {
    var label = 0
    var profile: Profile? = null
    var settings: Settings? = null
    var result: Any? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        this.result = result.getOrThrow()
        val r = invokeSuspend(this.result)
        if (r != COROUTINE_SUSPENDED) {
            @Suppress("UNCHECKED_CAST")
            completion.resumeWith(Result.success(r as User))
        }
    }

    fun invokeSuspend(param: Any?): Any? {
        when (label) {
            0 -> {
                label = 1
                val r = fetchProfile(userId, this)
                if (r == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                profile = r as Profile
            }
            1 -> {
                label = 2
                val r = fetchSettings(userId, this)
                if (r == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                settings = r as Settings
            }
            2 -> {
                return User(profile!!, settings!!)
            }
        }
        return COROUTINE_SUSPENDED
    }
}
```

(В реальности используется базовый класс `ContinuationImpl`, битовые флаги для `label` и больше служебного кода; пример выше — концептуальная иллюстрация.)

### Простой Пример Преобразования

```kotlin
// Оригинальный код
suspend fun simple(): String {
    delay(1000)
    return "Done"
}

// После компиляции (упрощенно, концептуально)
fun simple(completion: Continuation<String>): Any? {
    val sm = if (completion is SimpleSM) completion else SimpleSM(completion)
    return sm.invokeSuspend(Unit)
}

class SimpleSM(
    private val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var result: Any? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        this.result = result.getOrThrow()
        val r = invokeSuspend(this.result)
        if (r != COROUTINE_SUSPENDED) {
            completion.resumeWith(Result.success(r as String))
        }
    }

    fun invokeSuspend(param: Any?): Any? = when (label) {
        0 -> {
            label = 1
            val r = delay(1000, this)
            if (r == COROUTINE_SUSPENDED) COROUTINE_SUSPENDED else {
                "Done"
            }
        }
        1 -> {
            "Done"
        }
        else -> throw IllegalStateException("call to 'resume' before 'invoke'")
    }
}
```

(Опять же, это схема: реальный байткод использует `ContinuationImpl.invokeSuspend`.)

### State Machine С Локальными Переменными

```kotlin
// Оригинал: функция с локальными переменными
suspend fun calculate(x: Int, y: Int): Int {
    val sum = x + y             // Локальная переменная
    delay(100)                  // Точка приостановки
    val product = sum * 2       // Другая локальная переменная
    delay(100)                  // Другая приостановка
    return product + x
}

// Скомпилировано (схематично): переменные сохраняются в continuation
fun calculate(
    x: Int,
    y: Int,
    completion: Continuation<Int>
): Any? {
    val sm = if (completion is CalculateSM) completion
             else CalculateSM(x, y, completion)
    return sm.invokeSuspend(Unit)
}

class CalculateSM(
    var x: Int,
    var y: Int,
    private val completion: Continuation<Int>
) : Continuation<Any?> {
    var label = 0
    var sum: Int = 0
    var product: Int = 0
    var result: Any? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        this.result = result.getOrThrow()
        val r = invokeSuspend(this.result)
        if (r != COROUTINE_SUSPENDED) {
            completion.resumeWith(Result.success(r as Int))
        }
    }

    fun invokeSuspend(param: Any?): Any? {
        when (label) {
            0 -> {
                sum = x + y
                label = 1
                if (delay(100, this) == COROUTINE_SUSPENDED)
                    return COROUTINE_SUSPENDED
            }
            1 -> {
                product = sum * 2
                label = 2
                if (delay(100, this) == COROUTINE_SUSPENDED)
                    return COROUTINE_SUSPENDED
            }
            2 -> {
                return product + x
            }
        }
        return COROUTINE_SUSPENDED
    }
}
```

### Интерфейс `Continuation`

```kotlin
// Основной интерфейс для suspend-функций
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Удобные вспомогательные функции
public inline fun <T> Continuation<T>.resume(value: T) {
    resumeWith(Result.success(value))
}

public inline fun <T> Continuation<T>.resumeWithException(exception: Throwable) {
    resumeWith(Result.failure(exception))
}
```

### Как Работает Приостановка

```kotlin
suspend fun example(): String {
    println("До приостановки")
    delay(1000)  // Точка приостановки
    println("После приостановки")
    return "Done"
}
```

- В сгенерированной функции при вызове `delay` вызывается другая `suspend`-функция.
- Если она возвращает `COROUTINE_SUSPENDED`, текущая функция немедленно возвращает `COROUTINE_SUSPENDED` вызывающему коду, поток освобождается.
- Позже, когда операция завершается, вызывается `resumeWith` на соответствующем `Continuation`.
- Машина состояний использует `label` и сохранённые поля, чтобы продолжить выполнение с нужного места.

### Вложенные Suspend Вызовы

```kotlin
// Оригинал
suspend fun outer(): String {
    val result1 = inner1()
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

// Каждая функция имеет свой state machine; continuations образуют цепочку.
```

Высокоуровневая идея: `outer` вызывает `inner1`, передавая continuation, который при возобновлении запишет результат в поля state machine `outer` и продолжит выполнение `outer` с соответствующим `label`. Аналогично для `inner2`. Таким образом, вложенные suspend-вызовы координируются через цепочку `Continuation` и машин состояний.

### Реальный Декомпилированный Пример (Упрощенный Шаблон)

```kotlin
// Оригинальный Kotlin
suspend fun fetchData(): String {
    delay(1000)
    return "Data"
}

// Типичный упрощенный декомпилированный вид (схематично)
@Nullable
public static final Object fetchData(@NotNull Continuation<? super String> completion) {
    if (completion instanceof FetchDataContinuation) {
        FetchDataContinuation c = (FetchDataContinuation) completion;
        if ((c.label & Integer.MIN_VALUE) != 0) {
            c.label -= Integer.MIN_VALUE;
            return fetchData(c);
        }
    }
    FetchDataContinuation c = new FetchDataContinuation(completion);
    Object result = c.result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch (c.label) {
        case 0: {
            ResultKt.throwOnFailure(result);
            c.label = 1;
            if (DelayKt.delay(1000L, c) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            break;
        }
        case 1: {
            ResultKt.throwOnFailure(result);
            break;
        }
        default:
            throw new IllegalStateException("call to 'resume' before 'invoke'");
    }

    return "Data";
}

static final class FetchDataContinuation extends ContinuationImpl {
    int label;
    Object result;

    FetchDataContinuation(Continuation<? super String> completion) {
        super(completion);
    }

    @Nullable
    public final Object invokeSuspend(@NotNull Object result) {
        this.result = result;
        this.label |= Integer.MIN_VALUE;
        return fetchData(this);
    }
}
```

### Трансформация Обработки Исключений (Концептуально)

```kotlin
// Оригинал с try-catch
suspend fun safeFetch(): String {
    return try {
        delay(1000)
        fetchData()
    } catch (e: Exception) {
        "Error: ${e.message}"
    }
}

// Концептуально: try/catch охватывает соответствующие части машины состояний.
// Реальный код использует Result/throwOnFailure и ловит исключения вокруг invokeSuspend,
// сохраняя их в result и обрабатывая в нужном состоянии.
```

### Реализация `suspendCoroutine` (Концептуально)

```kotlin
public suspend inline fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T = suspendCoroutineUninterceptedOrReturn { cont: Continuation<T> ->
    val safe = SafeContinuation(cont.intercepted())
    block(safe)
    safe.getOrThrow()
}

suspend fun customDelay(time: Long): Unit = suspendCoroutine { continuation ->
    Timer().schedule(object : TimerTask() {
        override fun run() {
            continuation.resume(Unit)
        }
    }, time)
}

// Пониженный (упрощенный) вид:
fun customDelay(time: Long, cont: Continuation<Unit>): Any? {
    Timer().schedule(object : TimerTask() {
        override fun run() {
            cont.resume(Unit)
        }
    }, time)
    return COROUTINE_SUSPENDED
}
```

### Влияние На Производительность

```kotlin
// Каждая точка приостановки добавляет состояния в машину состояний данной функции
suspend fun manySteps(): Int {
    delay(1)
    delay(1)
    delay(1)
    delay(1)
    delay(1)
    return 42
}
// Компилятор создаст state machine с несколькими состояниями для этой функции.

suspend fun optimized(): Int {
    delay(5)
    return 42
}
// Здесь state machine проще (меньше состояний) для этой функции.
```

Меньше точек приостановки в конкретной функции — проще её state machine и немного меньше накладных расходов, но общая стоимость также зависит от числа создаваемых корутин, логики внутри них и планировщика.

### Inline Suspend Функции

```kotlin
// inline suspend-функции позволяют заинлайнить оболочку
suspend inline fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// После inlining сама оболочка практически исчезает,
// но если block содержит точки приостановки,
// для него (его тела) всё равно будет сгенерирована соответствующая state machine.
suspend fun example() {
    val (data, time) = measureTime {
        fetchData()  // используется state machine suspend-вызовов внутри
    }
}
```

### Ключевые Концепции (RU)

1. CPS-трансформация: каждая `suspend fun foo(): T` компилируется в `fun foo(Continuation<T>): Any?` плюс сгенерированный continuation-класс.
2. State machine: тело функции разбивается на состояния в точках приостановки (`label`).
3. Continuation: хранит состояние, локальные переменные и ссылку на completion-`Continuation`.
4. `COROUTINE_SUSPENDED`: маркер, сигнализирующий о приостановке.
5. Без блокировки потока: при возврате `COROUTINE_SUSPENDED` поток можно использовать для другой работы.
6. Resumption: `resumeWith` продолжает выполнение с нужного состояния.
7. Stack unwinding: при приостановке стек вызовов обычных функций не удерживается; состояние корутины хранится в объектах на куче.

**Резюме**: Suspend-функции в Kotlin компилируются в код в стиле CPS с использованием машин состояний и `Continuation`. Каждая точка приостановки приводит к сохранению состояния в continuation-объекте и возможному возврату `COROUTINE_SUSPENDED`. Позже, через `resumeWith`, выполнение продолжается с сохранённого места без блокировки потоков.

## Answer (EN)

Suspend functions in Kotlin allow pausing execution without blocking the underlying thread. Under the hood, the Kotlin compiler lowers suspend functions to CPS-style code plus a state machine that tracks suspension points and local state.

1. **Continuation-Passing Style (CPS)**: Each `suspend` function is compiled to a function that takes an extra `Continuation<T>` parameter and returns `Any?`, where `COROUTINE_SUSPENDED` is used as a special marker.
2. **State Machine**: The compiler generates a state machine with a `label` field; each suspension point becomes a state. Locals and progress are stored in a generated continuation class.
3. **Suspension**: At a suspension point (e.g., `delay`, another `suspend` call), the function may return `COROUTINE_SUSPENDED`, releasing the thread.
4. **Resumption**: When the async operation completes, `resumeWith` is invoked on the captured `Continuation`, and execution continues from the saved state.

### Compiler Transformation Overview (Conceptual)

```kotlin
// Source code you write:
suspend fun fetchUserData(userId: Int): User {
    val profile = fetchProfile(userId)
    val settings = fetchSettings(userId)
    return User(profile, settings)
}

// Conceptual lowering:
fun fetchUserData(
    userId: Int,
    completion: Continuation<User>
): Any? {
    val sm = if (completion is FetchUserDataSM) completion
             else FetchUserDataSM(userId, completion)

    return sm.invokeSuspend(Unit)
}

class FetchUserDataSM(
    private val userId: Int,
    private val completion: Continuation<User>
) : Continuation<Any?> {
    var label = 0
    var profile: Profile? = null
    var settings: Settings? = null
    var result: Any? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        this.result = result.getOrThrow()
        val r = invokeSuspend(this.result)
        if (r != COROUTINE_SUSPENDED) {
            @Suppress("UNCHECKED_CAST")
            completion.resumeWith(Result.success(r as User))
        }
    }

    fun invokeSuspend(param: Any?): Any? {
        when (label) {
            0 -> {
                label = 1
                val r = fetchProfile(userId, this)
                if (r == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                profile = r as Profile
            }
            1 -> {
                label = 2
                val r = fetchSettings(userId, this)
                if (r == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                settings = r as Settings
            }
            2 -> {
                return User(profile!!, settings!!)
            }
        }
        return COROUTINE_SUSPENDED
    }
}
```

(Real code uses `ContinuationImpl`, bit-masked labels, and additional runtime helpers; this is intentionally simplified.)

### Simple Example: Transformation

```kotlin
// Original code
suspend fun simple(): String {
    delay(1000)
    return "Done"
}

// Simplified compiled shape
fun simple(completion: Continuation<String>): Any? {
    val sm = if (completion is SimpleSM) completion else SimpleSM(completion)
    return sm.invokeSuspend(Unit)
}

class SimpleSM(
    private val completion: Continuation<String>
) : Continuation<Any?> {
    var label = 0
    var result: Any? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        this.result = result.getOrThrow()
        val r = invokeSuspend(this.result)
        if (r != COROUTINE_SUSPENDED) {
            completion.resumeWith(Result.success(r as String))
        }
    }

    fun invokeSuspend(param: Any?): Any? = when (label) {
        0 -> {
            label = 1
            val r = delay(1000, this)
            if (r == COROUTINE_SUSPENDED) COROUTINE_SUSPENDED else {
                "Done"
            }
        }
        1 -> {
            "Done"
        }
        else -> throw IllegalStateException("call to 'resume' before 'invoke'")
    }
}
```

### State Machine with Local Variables

```kotlin
// Original: Function with local variables
suspend fun calculate(x: Int, y: Int): Int {
    val sum = x + y
    delay(100)
    val product = sum * 2
    delay(100)
    return product + x
}

fun calculate(
    x: Int,
    y: Int,
    completion: Continuation<Int>
): Any? {
    val sm = if (completion is CalculateSM) completion
             else CalculateSM(x, y, completion)
    return sm.invokeSuspend(Unit)
}

class CalculateSM(
    var x: Int,
    var y: Int,
    private val completion: Continuation<Int>
) : Continuation<Any?> {
    var label = 0
    var sum: Int = 0
    var product: Int = 0
    var result: Any? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        this.result = result.getOrThrow()
        val r = invokeSuspend(this.result)
        if (r != COROUTINE_SUSPENDED) {
            completion.resumeWith(Result.success(r as Int))
        }
    }

    fun invokeSuspend(param: Any?): Any? {
        when (label) {
            0 -> {
                sum = x + y
                label = 1
                if (delay(100, this) == COROUTINE_SUSPENDED)
                    return COROUTINE_SUSPENDED
            }
            1 -> {
                product = sum * 2
                label = 2
                if (delay(100, this) == COROUTINE_SUSPENDED)
                    return COROUTINE_SUSPENDED
            }
            2 -> {
                return product + x
            }
        }
        return COROUTINE_SUSPENDED
    }
}
```

### Continuation Interface

```kotlin
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

public inline fun <T> Continuation<T>.resume(value: T) {
    resumeWith(Result.success(value))
}

public inline fun <T> Continuation<T>.resumeWithException(exception: Throwable) {
    resumeWith(Result.failure(exception))
}
```

### How Suspension Works

```kotlin
suspend fun example(): String {
    println("Before suspension")
    delay(1000)
    println("After suspension")
    return "Done"
}
```

- The compiled function starts at `label = 0`.
- When it reaches `delay`, it calls another suspend function.
- If that call returns `COROUTINE_SUSPENDED`, it returns `COROUTINE_SUSPENDED` to its caller, and the thread is free.
- Later, the scheduler/dispatcher calls `resumeWith` on the stored `Continuation` with either success or failure.
- The state machine uses the `label` and stored locals to continue from where it left off.

### Real Decompiled Example (Corrected Pattern)

```kotlin
// Original Kotlin
suspend fun fetchData(): String {
    delay(1000)
    return "Data"
}

// Typical decompiled shape (simplified)
@Nullable
public static final Object fetchData(@NotNull Continuation<? super String> completion) {
    if (completion instanceof FetchDataContinuation) {
        FetchDataContinuation c = (FetchDataContinuation) completion;
        if ((c.label & Integer.MIN_VALUE) != 0) {
            c.label -= Integer.MIN_VALUE;
            return fetchData(c);
        }
    }
    FetchDataContinuation c = new FetchDataContinuation(completion);
    Object result = c.result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch (c.label) {
        case 0: {
            ResultKt.throwOnFailure(result);
            c.label = 1;
            if (DelayKt.delay(1000L, c) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            break;
        }
        case 1: {
            ResultKt.throwOnFailure(result);
            break;
        }
        default:
            throw new IllegalStateException("call to 'resume' before 'invoke'");
    }

    return "Data";
}

static final class FetchDataContinuation extends ContinuationImpl {
    int label;
    Object result;

    FetchDataContinuation(Continuation<? super String> completion) {
        super(completion);
    }

    @Nullable
    public final Object invokeSuspend(@NotNull Object result) {
        this.result = result;
        this.label |= Integer.MIN_VALUE;
        return fetchData(this);
    }
}
```

### Exception Handling Transformation (Conceptual)

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

// Conceptually: try/catch wraps the relevant parts of the state machine.
// Real code uses Result/throwOnFailure and catches exceptions around invokeSuspend,
// storing them in result and handling them in the appropriate state.
```

### Nested Suspend Calls (Conceptual)

```kotlin
suspend fun outer(): String {
    val result1 = inner1()
    val result2 = inner2()
    return "$result1 $result2"
}

// Each suspend function has its own state machine.
// The compiler wires continuations so that when inner1/inner2 resume,
// they feed their results back into outer's state machine and advance its label.
```

### suspendCoroutine Implementation (Conceptual)

```kotlin
public suspend inline fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T = suspendCoroutineUninterceptedOrReturn { cont: Continuation<T> ->
    val safe = SafeContinuation(cont.intercepted())
    block(safe)
    safe.getOrThrow()
}

suspend fun customDelay(time: Long): Unit = suspendCoroutine { continuation ->
    Timer().schedule(object : TimerTask() {
        override fun run() {
            continuation.resume(Unit)
        }
    }, time)
}

// Lowered shape (conceptual):
fun customDelay(time: Long, cont: Continuation<Unit>): Any? {
    Timer().schedule(object : TimerTask() {
        override fun run() {
            cont.resume(Unit)
        }
    }, time)
    return COROUTINE_SUSPENDED
}
```

### Performance Implications

```kotlin
suspend fun manySteps(): Int {
    delay(1)
    delay(1)
    delay(1)
    delay(1)
    delay(1)
    return 42
}

suspend fun optimized(): Int {
    delay(5)
    return 42
}
```

- Each suspension point in a given function contributes additional states and bookkeeping in that function's state machine.
- Fewer suspension points in the same function generally mean a simpler state machine and slightly lower overhead, but the main cost also comes from coroutine creation and scheduling, not only labels.

### Inline Suspend Functions

```kotlin
suspend inline fun <T> measureTime(
    block: suspend () -> T
): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// After inlining, the wrapper body is inlined at call site.
// Suspend lambdas that actually suspend still compile to state machines;
// inlining removes extra indirection rather than suspension itself.
suspend fun example() {
    val (data, time) = measureTime {
        fetchData()
    }
}
```

### Key Concepts Summary (EN)

1. CPS transformation: every `suspend fun foo(): T` is compiled to `fun foo(Continuation<T>): Any?` plus a generated continuation/state-machine.
2. State machine: the body is split into states at suspension points (`label`).
3. Continuation: stores current state, locals, and reference to completion continuation.
4. `COROUTINE_SUSPENDED`: marker object indicating suspension.
5. No thread blocking: on suspension, the function returns and the thread is free.
6. Resumption: `resumeWith` is used to continue from the saved state.
7. Stack unwinding: the JVM call stack is not kept for suspended calls; state lives in heap objects.

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

- [[q-suspend-function-return-type-after-compilation--programming-languages--hard]]
- [[q-synchronized-blocks-with-coroutines--programming-languages--medium]]

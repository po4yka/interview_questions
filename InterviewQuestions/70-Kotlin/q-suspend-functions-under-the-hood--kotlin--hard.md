---
'---id': lang-089
title: Suspend Functions Under The Hood / Suspend функции в подробностях
aliases:
- Suspend Functions Under The Hood
- Suspend функции в подробностях
topic: kotlin
subtopics:
- compiler
- coroutines
- implementation
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
- compiler
- coroutines
- difficulty/hard
- kotlin
anki_cards:
- slug: q-suspend-functions-under-the-hood--kotlin--hard-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-suspend-functions-under-the-hood--kotlin--hard-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> Как работают suspend-функции под капотом?

# Question (EN)
> How do suspend functions work under the hood?

## Ответ (RU)

Suspend-функции в Kotlin позволяют приостанавливать выполнение без блокировки потока. Под капотом компилятор Kotlin преобразует suspend-функции в код в стиле CPS (Continuation-Passing Style) и генерирует state machine (машину состояний), которая отслеживает точки приостановки и локальное состояние.

### Основные Принципы Работы

1. **Continuation-Passing Style (CPS)**: Каждая `suspend`-функция компилируется в обычную функцию, принимающую дополнительный параметр `Continuation<T>` и возвращающую `Any?`. Специальное значение `COROUTINE_SUSPENDED` используется как маркер приостановки.
2. **State Machine**: Компилятор генерирует машину состояний с полем `label`; каждая точка приостановки становится состоянием. Локальные переменные и прогресс выполнения сохраняются в сгенерированном continuation-классе.
3. **Suspension**: При достижении точки приостановки (например, `delay` или другая `suspend`-функция) функция может вернуть `COROUTINE_SUSPENDED`, позволяя освободить текущий поток.
4. **Resumption**: Когда асинхронная операция завершается, вызывается `resumeWith` у соответствующего `Continuation`, и выполнение продолжается с сохранённого состояния.

### Преобразование Компилятором (Концептуально)

Ниже — упрощённая иллюстрация того, что делает компилятор. Это не точный декомпилированный код, а схематический пример.

```kotlin
// Исходный код:
suspend fun fetchUserData(userId: Int): User {
    val profile = fetchProfile(userId)    // Точка приостановки 1
    val settings = fetchSettings(userId)  // Точка приостановки 2
    return User(profile, settings)
}

// Концептуально (упрощенно):
fun fetchUserData(
    userId: Int,
    completion: Continuation<User>
): Any? {
    val sm = if (completion is FetchUserDataSM) completion
             else FetchUserDataSM(userId, completion)

    return sm.invokeSuspend(Unit)
}

// Упрощённый continuation/state-machine (псевдокод)
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
        return when (label) {
            0 -> {
                label = 1
                val r = fetchProfile(userId, this)
                if (r == COROUTINE_SUSPENDED) COROUTINE_SUSPENDED else {
                    profile = r as Profile
                    // Падение вниз к следующему состоянию
                    label = 2
                    invokeSuspend(Unit)
                }
            }
            1 -> {
                // В реальном коде это состояние будет вызываться через resumeWith
                // после завершения fetchProfile.
                label = 2
                invokeSuspend(Unit)
            }
            2 -> {
                val r = fetchSettings(userId, this)
                label = 3
                if (r == COROUTINE_SUSPENDED) COROUTINE_SUSPENDED else {
                    settings = r as Settings
                    invokeSuspend(Unit)
                }
            }
            3 -> {
                User(profile!!, settings!!)
            }
            else -> throw IllegalStateException("call to 'resume' before 'invoke'")
        }
    }
}
```

(В реальности используется базовый класс `ContinuationImpl`, битовые флаги для `label`, проверка через `throwOnFailure` и больше служебного кода; пример выше — исключительно концептуальная иллюстрация.)

### Простой Пример Преобразования

```kotlin
// Оригинальный код
suspend fun simple(): String {
    delay(1000)
    return "Done"
}

// После компиляции (упрощенно, концептуально — псевдокод)
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
            if (r == COROUTINE_SUSPENDED) {
                COROUTINE_SUSPENDED
            } else {
                "Done"
            }
        }
        1 -> {
            // Возобновление после delay
            "Done"
        }
        else -> throw IllegalStateException("call to 'resume' before 'invoke'")
    }
}
```

(Снова: это схема, реальный байткод опирается на `ContinuationImpl.invokeSuspend`.)

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

// Скомпилировано (схематично, псевдокод): переменные сохраняются в continuation
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
        return when (label) {
            0 -> {
                sum = x + y
                label = 1
                if (delay(100, this) == COROUTINE_SUSPENDED)
                    COROUTINE_SUSPENDED
                else {
                    label = 2
                    invokeSuspend(Unit)
                }
            }
            1 -> {
                // Возобновление после первого delay
                label = 2
                invokeSuspend(Unit)
            }
            2 -> {
                product = sum * 2
                label = 3
                if (delay(100, this) == COROUTINE_SUSPENDED)
                    COROUTINE_SUSPENDED
                else {
                    product + x
                }
            }
            3 -> {
                // Возобновление после второго delay
                product + x
            }
            else -> throw IllegalStateException("call to 'resume' before 'invoke'")
        }
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

- В сгенерированной функции используется поле `label` для выбора следующего шага.
- При вызове `delay` вызывается другая `suspend`-функция.
- Если она возвращает `COROUTINE_SUSPENDED`, текущая функция сразу возвращает `COROUTINE_SUSPENDED` вызывающему коду, поток освобождается.
- Позже планировщик/диспетчер вызывает `resumeWith` на соответствующем `Continuation` с результатом или исключением.
- Машина состояний, используя `label` и сохранённые поля, продолжает выполнение с нужного места.

### Вложенные Suspend Вызовы (Концептуально)

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

Высокоуровневая идея: `outer` вызывает `inner1`, передавая continuation, который при возобновлении запишет результат в поля state machine `outer` и продвинет его `label`. Аналогично для `inner2`. Таким образом, вложенные suspend-вызовы координируются через цепочку `Continuation` и машин состояний.

### Реальный Декомпилированный Пример (Упрощенный Шаблон)

Ниже — типичный шаблон, к которому стремится реальный байткод (схематично, детали могут отличаться между версиями компилятора):

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

suspend fun optimized(): Int {
    delay(5)
    return 42
}
```

Меньше точек приостановки в конкретной функции — проще её state machine и немного меньше накладных расходов. Однако основная стоимость зависит также от числа создаваемых корутин, логики внутри них и планировщика, а не только от количества состояний.

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

// После inlining сама оболочка встраивается в место вызова.
// Если переданный block содержит точки приостановки, для его тела
// по-прежнему генерируется собственная state machine; inlining убирает
// лишний уровень вызова, но не отменяет механизм приостановки.
suspend fun example() {
    val (data, time) = measureTime {
        fetchData()  // используется state machine suspend-вызовов внутри
    }
}
```

### Ключевые Концепции (RU/EN Summary)

1. CPS-трансформация: каждая `suspend fun foo(): T` компилируется в `fun foo(Continuation<T>): Any?` плюс сгенерированный continuation/машину состояний.
2. State machine: тело функции разбивается на состояния в точках приостановки (`label`).
3. Continuation: хранит состояние, локальные переменные и ссылку на completion-`Continuation`.
4. `COROUTINE_SUSPENDED`: маркер, сигнализирующий о приостановке.
5. Без блокировки потока: при возврате `COROUTINE_SUSPENDED` поток можно использовать для другой работы.
6. Resumption: `resumeWith` продолжает выполнение с нужного состояния.
7. `Stack` unwinding: при приостановке стек вызовов обычных функций не удерживается; состояние корутины хранится в объектах на куче.

**Резюме**: Suspend-функции в Kotlin компилируются в CPS-код с использованием машин состояний и `Continuation`. Каждая точка приостановки приводит к сохранению состояния в continuation-объекте и возможному возврату `COROUTINE_SUSPENDED`. Позже, через `resumeWith`, выполнение продолжается с сохранённого места без блокировки потоков.

## Answer (EN)

Suspend functions in Kotlin allow pausing execution without blocking the underlying thread. Under the hood, the Kotlin compiler lowers suspend functions to CPS-style code plus a state machine that tracks suspension points and local state.

1. **Continuation-Passing Style (CPS)**: Each `suspend` function is compiled to a function that takes an extra `Continuation<T>` parameter and returns `Any?`. A special `COROUTINE_SUSPENDED` marker value is used to indicate suspension.
2. **State Machine**: The compiler generates a state machine driven by a `label` field; each suspension point becomes a state. Locals and progress are stored in a generated continuation class.
3. **Suspension**: At a suspension point (e.g., `delay`, another `suspend` call), the function may return `COROUTINE_SUSPENDED`, releasing the current thread.
4. **Resumption**: When the async operation completes, `resumeWith` is invoked on the stored `Continuation`, and execution continues from the saved state.

### Compiler Transformation Overview (Conceptual)

The following is a schematic illustration, not exact decompiled output.

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

// Simplified continuation/state-machine (pseudocode)
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
        return when (label) {
            0 -> {
                label = 1
                val r = fetchProfile(userId, this)
                if (r == COROUTINE_SUSPENDED) COROUTINE_SUSPENDED else {
                    profile = r as Profile
                    label = 2
                    invokeSuspend(Unit)
                }
            }
            1 -> {
                // Resume after fetchProfile
                label = 2
                invokeSuspend(Unit)
            }
            2 -> {
                val r = fetchSettings(userId, this)
                label = 3
                if (r == COROUTINE_SUSPENDED) COROUTINE_SUSPENDED else {
                    settings = r as Settings
                    invokeSuspend(Unit)
                }
            }
            3 -> {
                User(profile!!, settings!!)
            }
            else -> throw IllegalStateException("call to 'resume' before 'invoke'")
        }
    }
}
```

(Real code uses `ContinuationImpl`, bit-masked labels, Result/throwOnFailure utilities, and other helpers. This is intentionally simplified pseudocode.)

### Simple Example: Transformation

```kotlin
// Original code
suspend fun simple(): String {
    delay(1000)
    return "Done"
}

// Simplified compiled shape (pseudocode)
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
            if (r == COROUTINE_SUSPENDED) {
                COROUTINE_SUSPENDED
            } else {
                "Done"
            }
        }
        1 -> {
            // Resume after delay
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

// Conceptual lowered form: locals stored in continuation
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
        return when (label) {
            0 -> {
                sum = x + y
                label = 1
                if (delay(100, this) == COROUTINE_SUSPENDED)
                    COROUTINE_SUSPENDED
                else {
                    label = 2
                    invokeSuspend(Unit)
                }
            }
            1 -> {
                // Resume after first delay
                label = 2
                invokeSuspend(Unit)
            }
            2 -> {
                product = sum * 2
                label = 3
                if (delay(100, this) == COROUTINE_SUSPENDED)
                    COROUTINE_SUSPENDED
                else {
                    product + x
                }
            }
            3 -> {
                // Resume after second delay
                product + x
            }
            else -> throw IllegalStateException("call to 'resume' before 'invoke'")
        }
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

- The compiled function uses a `label`-driven state machine.
- At `delay`, it calls another suspend function.
- If that call returns `COROUTINE_SUSPENDED`, it immediately returns `COROUTINE_SUSPENDED` to its caller; the thread is free.
- Later, the dispatcher/scheduler calls `resumeWith` on the stored `Continuation`.
- The state machine uses `label` and stored locals to resume from where it left off.

### Nested Suspend Calls (Conceptual)

```kotlin
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

// Each suspend function has its own state machine.
// Continuations are wired so that when inner1/inner2 resume,
// their results are fed back into outer's state and its label advances.
```

### Real Decompiled Example (Schematic Pattern)

```kotlin
// Original Kotlin
suspend fun fetchData(): String {
    delay(1000)
    return "Data"
}

// Typical decompiled shape (simplified, schematic)
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

(Details such as constructor body are determined by the real compiler; pattern is what matters.)

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

// Conceptually: try/catch is represented as states spanning multiple suspension points.
// Real code uses Result/throwOnFailure and propagates exceptions via resumeWith,
// so they are observed in the appropriate state of the state machine.
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

- Each suspension point in a function contributes additional states and bookkeeping to that function's state machine.
- Fewer suspension points mean a slightly simpler state machine and lower per-call overhead, but the dominant costs often come from coroutine creation, scheduling, and the work done inside, not just the number of labels.

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

// After inlining, the wrapper body is inlined at the call site.
// Suspend lambdas that actually suspend still compile into their own state machines;
// inlining removes extra indirection but not the suspension mechanism itself.
suspend fun example() {
    val (data, time) = measureTime {
        fetchData()
    }
}
```

### Key Concepts Summary (EN)

1. CPS transformation: every `suspend fun foo(): T` is compiled to `fun foo(Continuation<T>): Any?` plus a generated continuation/state-machine class.
2. State machine: the body is split into states at suspension points (`label`).
3. Continuation: stores the current state, locals, and a reference to the completion continuation.
4. `COROUTINE_SUSPENDED`: marker object indicating suspension.
5. No thread blocking: on suspension, the function returns, and the thread is free.
6. Resumption: `resumeWith` is used to continue from the saved state.
7. `Stack` unwinding: suspended calls do not keep the JVM call stack; coroutine state lives in heap objects.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого механизма от подхода в Java без корутин?
- Когда на практике стоит учитывать детали работы suspend-функций под капотом?
- Какие распространенные ошибки и подводные камни связаны с использованием suspend-функций?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-coroutines]]

## Связанные Вопросы (RU)

- [[q-suspend-function-return-type-after-compilation--kotlin--hard]]
- [[q-synchronized-blocks-with-coroutines--kotlin--medium]]

## Related Questions

- [[q-suspend-function-return-type-after-compilation--kotlin--hard]]
- [[q-synchronized-blocks-with-coroutines--kotlin--medium]]

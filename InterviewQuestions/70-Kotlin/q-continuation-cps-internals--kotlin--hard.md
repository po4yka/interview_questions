---
anki_cards:
- slug: q-continuation-cps-internals--kotlin--hard-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-continuation-cps-internals--kotlin--hard-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: kotlin-122
title: "Continuation and CPS: how suspend functions work internally / Continuation и CPS: как работают suspend функции внутри"
topic: kotlin
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-11
tags: [advanced, continuation, coroutines, cps, difficulty/hard, internals, kotlin, state-machine]
aliases: ["Continuation and CPS internals in Kotlin", "Continuation и CPS: внутренняя работа suspend-функций"]
question_kind: theory
moc: moc-kotlin
related: [c-coroutines, c-kotlin, c-stateflow, q-common-coroutine-mistakes--kotlin--medium, q-debugging-coroutines-techniques--kotlin--medium, q-suspend-cancellable-coroutine--kotlin--hard]
subtopics: [continuation, coroutines, state-machine]

---
# Вопрос (RU)
> Как Kotlin трансформирует suspend функции внутри? Что такое Continuation, CPS трансформация, и как работают конечные автоматы?

---

# Question (EN)
> How does Kotlin transform suspend functions internally? What is Continuation, CPS transformation, and how do state machines work?

## Ответ (RU)

Понимание того, как `suspend` функции работают внутри, критично для продвинутого использования корутин, оптимизации производительности и отладки. Kotlin компилирует `suspend`-функции, используя под капотом **Continuation Passing Style (CPS)** и **конечные автоматы (state machines)**. Эта трансформация прозрачна для разработчиков, но её понимание помогает глубоко разобраться в поведении корутин.

См. также: [[c-kotlin]], [[c-coroutines]].

### Что Такое Continuation?

**Continuation** представляет "остаток вычисления" — что должно произойти после возобновления из точки приостановки.

```kotlin
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Удобные расширения стандартной библиотеки:
fun <T> Continuation<T>.resume(value: T)
fun <T> Continuation<T>.resumeWithException(exception: Throwable)
```

**Ключевая концепция:** Когда `suspend`-функция приостанавливается, она (через сгенерированный компилятором код) передаёт continuation приостанавливающей операции. Эта операция позже вызывает `resumeWith()` (или `resume`/`resumeWithException`) для продолжения выполнения.

### Continuation Passing Style (CPS)

**CPS-трансформация (упрощённо):** Компилятор преобразует каждую `suspend`-функцию в обычную функцию с дополнительным параметром `Continuation` и кодом конечного автомата.

**До (исходный код):**

```kotlin
suspend fun getUserName(userId: String): String {
    val user = fetchUser(userId)
    return user.name
}
```

**После CPS-трансформации (упрощённо и концептуально):**

```kotlin
fun getUserName(userId: String, completion: Continuation<String>): Any? {
    val sm = if (completion is GetUserNameStateMachine)
        completion
    else
        GetUserNameStateMachine(completion).also { it.userId = userId }

    return sm.invokeSuspend(Unit)
}

private class GetUserNameStateMachine(
    private val completion: Continuation<String>
) : ContinuationImpl(completion) {
    var label: Int = 0
    var userId: String = ""
    var user: User? = null

    override fun invokeSuspend(result: Any?): Any? {
        // Концептуальный, упрощённый пример
        when (label) {
            0 -> {
                label = 1
                val r = fetchUser(userId, this)
                if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                user = r as User
            }
            1 -> {
                // Возобновление после fetchUser
            }
        }
        completion.resumeWith(Result.success(user!!.name))
        return Unit
    }
}
```

Важно: приведённый код — схематичный. Реальный код компилятора сложнее, но идея та же:
- добавляется дополнительный параметр `Continuation`;
- возвращаемый тип становится `Any?`/`Object`, чтобы можно было вернуть как результат, так и `COROUTINE_SUSPENDED`;
- логика разворачивается в конечный автомат.

### Трансформация В Конечный Автомат (State Machine Transformation)

Компилятор преобразует `suspend`-функции в конечные автоматы, где каждая точка приостановки становится состоянием.

**Пример:**

```kotlin
suspend fun example() {
    println("Before delay 1")
    delay(1000)           // Точка приостановки 1
    println("After delay 1")
    delay(1000)           // Точка приостановки 2
    println("After delay 2")
}
```

**Концептуальная трансформация (упрощённо):**

```kotlin
fun example(completion: Continuation<Unit>): Any? {
    val sm = if (completion is ExampleStateMachine)
        completion
    else
        ExampleStateMachine(completion)

    return sm.invokeSuspend(Unit)
}

class ExampleStateMachine(
    private val completion: Continuation<Unit>
) : ContinuationImpl(completion) {
    var label = 0

    override fun invokeSuspend(result: Any?): Any? {
        when (label) {
            0 -> {
                println("Before delay 1")
                label = 1
                if (delay(1000, this) === COROUTINE_SUSPENDED) {
                    return COROUTINE_SUSPENDED
                }
            }
            1 -> {
                println("After delay 1")
                label = 2
                if (delay(1000, this) === COROUTINE_SUSPENDED) {
                    return COROUTINE_SUSPENDED
                }
            }
            2 -> {
                println("After delay 2")
                return Unit
            }
            else -> error("Invalid state")
        }
        return Unit
    }
}
```

Ключевые идеи:
- `label` хранит текущее состояние (индекс точки приостановки).
- Класс конечного автомата хранит состояние между приостановками.
- Методы `resumeWith` / `invokeSuspend` двигают выполнение вперёд при возобновлении.

### Реальный Декомпилированный Пример (Real Decompiled Example)

Ниже показан упрощённый, но структурно реалистичный пример декомпилированной `suspend`-функции:

```kotlin
suspend fun fetchUserData(userId: String): UserData {
    val user = api.getUser(userId)
    val posts = api.getPosts(userId)
    return UserData(user, posts)
}
```

**Упрощённый декомпилированный вариант (Java):**

```java
@Nullable
public static final Object fetchUserData(
    @NotNull String userId,
    @NotNull Continuation<? super UserData> $completion
) {
    FetchUserDataContinuation $cont;
    if ($completion instanceof FetchUserDataContinuation) {
        $cont = (FetchUserDataContinuation) $completion;
        if (($cont.label & Integer.MIN_VALUE) != 0) {
            $cont.label -= Integer.MIN_VALUE;
        }
    } else {
        $cont = new FetchUserDataContinuation($completion);
    }

    Object result = $cont.result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch ($cont.label) {
        case 0: {
            ResultKt.throwOnFailure(result);
            $cont.userId = userId;
            $cont.label = 1;

            Object user = api.getUser(userId, $cont);
            if (user == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            result = user;
        }
        case 1: {
            ResultKt.throwOnFailure(result);
            User user = (User) result;

            $cont.user = user;
            $cont.label = 2;

            Object posts = api.getPosts($cont.userId, $cont);
            if (posts == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            result = posts;
        }
        case 2: {
            ResultKt.throwOnFailure(result);
            @SuppressWarnings("unchecked")
            List<Post> posts = (List<Post>) result;
            User user = $cont.user;

            return new UserData(user, posts);
        }
        default:
            throw new IllegalStateException("call to 'resume' before 'invoke'");
    }
}

static final class FetchUserDataContinuation extends ContinuationImpl {
    Object result;
    int label;
    String userId;
    User user;

    FetchUserDataContinuation(Continuation<? super UserData> completion) {
        super(completion);
    }

    @Nullable
    public final Object invokeSuspend(@NotNull Object result) {
        this.result = result;
        this.label |= Integer.MIN_VALUE;
        return fetchUserData(this.userId, this);
    }
}
```

Основные наблюдения:
1. `suspend` в байткоде исчезает.
2. Добавляется дополнительный параметр `Continuation`.
3. Возвращаемый тип — `Object`, чтобы вернуть как результат, так и `COROUTINE_SUSPENDED`.
4. Логика автомата реализована через `label` и `switch`.
5. Локальные переменные, переживающие приостановку, становятся полями.
6. Каждая точка приостановки сопоставлена со значением `label`.

### suspendCoroutine И suspendCancellableCoroutine

`suspendCoroutine` — низкоуровневый API для создания пользовательских приостанавливающих операций.

```kotlin
public suspend inline fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T
```

Концептуально он:
- создаёт continuation и передаёт его в `block`;
- возвращает `COROUTINE_SUSPENDED` для сигнала о приостановке;
- продолжает выполнение, когда вызывается `resume`/`resumeWith`.

**Пример использования:**

```kotlin
suspend fun customDelay(timeMillis: Long) = suspendCoroutine<Unit> { cont ->
    thread {
        Thread.sleep(timeMillis)
        cont.resume(Unit) // Возобновляем корутину
    }
}

// Использование
launch {
    println("Before custom delay")
    customDelay(1000)
    println("After custom delay")
}
```

`suspendCancellableCoroutine` — вариант с поддержкой отмены:

```kotlin
suspend fun cancellableDelay(timeMillis: Long) = suspendCancellableCoroutine<Unit> { cont ->
    val timer = Timer()
    timer.schedule(object : TimerTask() {
        override fun run() {
            cont.resume(Unit)
        }
    }, timeMillis)

    cont.invokeOnCancellation {
        timer.cancel()
    }
}
```

### Continuation.resume И resumeWith

```kotlin
// Успешное возобновление
continuation.resume(value)
// Эквивалентно:
continuation.resumeWith(Result.success(value))

// Возобновление с исключением
continuation.resumeWithException(exception)
// Эквивалентно:
continuation.resumeWith(Result.failure(exception))
```

**Пример ручного управления continuation:**

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

// Использование
val suspender = ManualSuspender()

launch {
    println("Waiting for value...")
    val value = suspender.waitForValue()
    println("Received: $value")
}

delay(1000)
suspender.provideValue("Hello!")
```

### ContinuationInterceptor

`ContinuationInterceptor` — механизм, через который диспетчеры и другие компоненты могут перехватывать continuation и изменять, где и как он будет возобновлён.

```kotlin
interface ContinuationInterceptor : CoroutineContext.Element {
    fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T>
}
```

**Пример простого логирующего перехватчика:**

```kotlin
class LoggingInterceptor : ContinuationInterceptor {
    override val key: CoroutineContext.Key<*> = ContinuationInterceptor

    override fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T> {
        return LoggingContinuation(continuation)
    }

    private class LoggingContinuation<T>(
        private val continuation: Continuation<T>
    ) : Continuation<T> {
        override val context: CoroutineContext
            get() = continuation.context

        override fun resumeWith(result: Result<T>) {
            println("Resuming with: $result")
            continuation.resumeWith(result)
        }
    }
}

// Использование
runBlocking(LoggingInterceptor()) {
    println("Start")
    delay(100)
    println("After delay")
}
```

### Как Диспетчеры Перехватывают Continuation (How Dispatchers Intercept Continuations)

Концептуальный пример (упрощённо, не реальная реализация):

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
    override val context: CoroutineContext
        get() = continuation.context

    override fun resumeWith(result: Result<T>) {
        dispatcher.dispatch(context, Runnable {
            continuation.resumeWith(result)
        })
    }
}
```

Что происходит концептуально:
1. `suspend`-функция возвращает `COROUTINE_SUSPENDED`.
2. Continuation захватывается приостанавливающей операцией.
3. После завершения операции вызывается `continuation.resumeWith()`.
4. `ContinuationInterceptor` (например, диспетчер) может обернуть continuation.
5. Диспетчер планирует `resumeWith` на нужном потоке.
6. Конечный автомат продолжает выполнение с нужного `label`.

### Почему Suspend-функции Нельзя Вызывать Из Обычных Функций (Why Suspend Functions Can't Be Called from Regular Functions)

```kotlin
fun regularFunction() {
    getUserName("123") // ОШИБКА
}
```

`Suspend`-функции компилируются в функции с дополнительным параметром `Continuation` и специальным управлением потоком. Обычная функция не имеет continuation, который можно передать, поэтому не может вызывать `suspend` напрямую.

Концептуально:

```kotlin
suspend fun getUserName(userId: String): String
// становится
fun getUserName(userId: String, continuation: Continuation<String>): Any?

fun regularFunction() {
    // Здесь нечем передать continuation
    // getUserName("123", ???)
}
```

Правильные способы вызвать:

```kotlin
// 1. Сделать вызывающую функцию suspend
typealias UserId = String

suspend fun callerFunction() {
    getUserName("123")
}

// 2. Запустить корутину
fun regularFunction() {
    GlobalScope.launch {
        getUserName("123")
    }
}

// 3. Использовать runBlocking
fun blockingEntryPoint() {
    runBlocking {
        getUserName("123")
    }
}
```

### Производительность (Performance Implications)

Преимущества модели конечного автомата:

1. Нет "callback hell" — последовательный код трансформируется в неблокирующий автомат.
2. Стек-независимые корутины — не требуется отдельный стек потока на каждую корутину, состояние хранится в объекте continuation.
3. Обычно эффективно: накладные расходы — небольшой объект автомата и несколько обращений к полям.

Издержки:

1. Выделение объекта автомата/continuation.
2. Косвенные переходы через `label` (`when`/`switch`).
3. Локальные переменные, пересекающие точки приостановки, становятся полями.

Интуитивные примеры:

```kotlin
fun regularSum(a: Int, b: Int): Int = a + b

suspend fun suspendSum(a: Int, b: Int): Int = a + b // добавляется обвязка

suspend fun suspendSumWithDelay(a: Int, b: Int): Int {
    delay(1)
    return a + b
}
```

- Тривиальная `suspend`-функция имеет небольшой постоянный overhead.
- При реальной приостановке основная цена — планирование задач/потоков, а не логика автомата.

**Inline suspend-функции:**

```kotlin
inline suspend fun inlinedSum(a: Int, b: Int): Int = a + b
```

- Инлайнинг переносит тело в вызывающий контекст.
- Если нет точек приостановки, можно избежать лишних уровней автомата.
- Если они есть, автомат всё равно нужен, но на соответствующем уровне.

### Продвинутый Пример: Свои Приостанавливающие Операции (Advanced: Implementing Custom Suspending Operations)

**Обёртка над callback API с поддержкой отмены:**

```kotlin
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

suspend fun fetchData(): String = suspendCancellableCoroutine { cont ->
    fetchDataAsync(object : ApiCallback {
        override fun onSuccess(data: String) {
            if (cont.isActive) cont.resume(data)
        }

        override fun onError(error: Throwable) {
            if (cont.isActive) cont.resumeWithException(error)
        }
    })

    cont.invokeOnCancellation {
        // Отменить нижележащую операцию, если возможно
    }
}
```

### Конечный Автомат С Несколькими Переменными (State Machine with Multiple Variables)

```kotlin
suspend fun complexFunction(x: Int): Int {
    val a = computeA(x)
    val b = computeB(a)
    val c = computeC(a, b)
    return c
}
```

Концептуально компилятор генерирует continuation-класс, где переменные, "переживающие" приостановки, являются полями:

```kotlin
class ComplexFunctionContinuation(
    completion: Continuation<Int>
) : ContinuationImpl(completion) {
    var label = 0
    var result: Any? = null

    var x: Int = 0
    var a: Int = 0
    var b: Int = 0

    override fun invokeSuspend(result: Any?): Any? {
        // Логика автомата, использующая label, x, a, b
        return Unit
    }
}
```

Ключевой вывод: все значения, нужные после точки приостановки, хранятся в полях сгенерированного класса.

### Обработка Исключений В Конечных Автоматах (Exception Handling in State Machines)

Исходный код:

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

Концептуальное поведение (упрощённо):

```kotlin
class WithExceptionContinuation(
    completion: Continuation<Unit>
) : ContinuationImpl(completion) {
    var label = 0
    var data: String? = null

    override fun invokeSuspend(result: Any?): Any? {
        return try {
            when (label) {
                0 -> {
                    ResultKt.throwOnFailure(result)
                    label = 1
                    val r = fetchData(this)
                    if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                    data = r as String
                }
                1 -> {
                    ResultKt.throwOnFailure(result)
                    label = 2
                    val r = processData(data!!, this)
                    if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                }
            }
            Unit
        } catch (e: Exception) {
            handleError(e)
            Unit
        }
    }
}
```

Важно:
- Исключения до и после точек приостановки проходят через логику автомата.
- `Result` и `throwOnFailure` используются для переноса ошибок между шагами.

### Визуализация Выполнения Конечного Автомата (Visualizing State Machine Execution)

```text
Начальный вызов: label = 0
     ↓
[Состояние 0] Вызов operation1()
     ↓
COROUTINE_SUSPENDED (возврат вызывающему)
     ↓
(Проходит время, operation1 завершена)
     ↓
continuation.resumeWith(result1)
     ↓
[Состояние 1] Обработка result1, вызов operation2()
     ↓
COROUTINE_SUSPENDED
     ↓
(Проходит время, operation2 завершена)
     ↓
continuation.resumeWith(result2)
     ↓
[Состояние 2] Обработка result2, возврат финального результата
     ↓
Готово
```

### Основные Выводы (RU)

1. **Continuation = "остаток вычисления"** — что выполняется после возобновления.
2. **CPS-трансформация** — компилятор добавляет параметр `Continuation` и код конечного автомата.
3. **Конечные автоматы** — каждая точка приостановки соответствует состоянию (`label`).
4. **Без callback hell** — переходы между состояниями генерируются автоматически.
5. **Эффективность** — корутина не требует отдельного стека потока, состояние хранится в continuation-объекте.
6. **ContinuationInterceptor/Dispatchers** — определяют, где и как возобновляется выполнение.
7. **suspendCoroutine/suspendCancellableCoroutine** — низкоуровневые примитивы для своих приостанавливающих операций.
8. **Локальные переменные → поля** — значения, переживающие приостановки, сохраняются в полях.
9. **Нужен контекст корутины** — `suspend`-функции не вызываются как обычные.
10. **Производительность** — есть накладные расходы на автомат, но выигрыши от неблокирующего исполнения обычно выше.

---

## Answer (EN)

Understanding how `suspend` functions work internally is crucial for advanced coroutine usage, performance optimization, and debugging. Kotlin compiles suspend functions using **Continuation Passing Style (CPS)** and **state machines** under the hood. This transformation is transparent to developers but understanding it unlocks deeper insights.

See also: [[c-kotlin]], [[c-coroutines]].

### What is Continuation?

**Continuation** represents "the rest of the computation" — what should happen after a suspension point resumes.

```kotlin
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Convenience extensions in stdlib:
fun <T> Continuation<T>.resume(value: T)
fun <T> Continuation<T>.resumeWithException(exception: Throwable)
```

**Key concept:** When a suspend function suspends, the (compiler-generated) state machine passes a Continuation to the suspending operation. That operation later calls `resumeWith()` (or `resume`/`resumeWithException`) on it to continue execution.

### Continuation Passing Style (CPS)

**CPS transformation (conceptual):** The compiler transforms every suspend function into a regular function that:
- accepts an additional `Continuation` parameter;
- returns `Any?`/`Object` so it can return either the final result or a special `COROUTINE_SUSPENDED` marker;
- delegates control to a generated state machine.

**Before (source code):**

```kotlin
suspend fun getUserName(userId: String): String {
    val user = fetchUser(userId)
    return user.name
}
```

**After CPS transformation (high-level, conceptual, not exact compiler output):**

```kotlin
fun getUserName(userId: String, completion: Continuation<String>): Any? {
    val sm = if (completion is GetUserNameStateMachine)
        completion
    else
        GetUserNameStateMachine(completion).also { it.userId = userId }

    return sm.invokeSuspend(Unit)
}

private class GetUserNameStateMachine(
    private val completion: Continuation<String>
) : ContinuationImpl(completion) {
    var label: Int = 0
    var userId: String = ""
    var user: User? = null

    override fun invokeSuspend(result: Any?): Any? {
        // Conceptual, simplified
        when (label) {
            0 -> {
                label = 1
                val r = fetchUser(userId, this)
                if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                user = r as User
            }
            1 -> {
                // Resumed after fetchUser
            }
        }
        completion.resumeWith(Result.success(user!!.name))
        return Unit
    }
}
```

This is illustrative only; real generated bytecode/Java differs in structure and naming, but follows this model.

### State Machine Transformation

The compiler transforms suspend functions into state machines where each suspension point becomes a state.

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

**Conceptual transformation (simplified, not exact codegen):**

```kotlin
fun example(completion: Continuation<Unit>): Any? {
    val sm = if (completion is ExampleStateMachine)
        completion
    else
        ExampleStateMachine(completion)

    return sm.invokeSuspend(Unit)
}

class ExampleStateMachine(
    private val completion: Continuation<Unit>
) : ContinuationImpl(completion) {
    var label = 0

    override fun invokeSuspend(result: Any?): Any? {
        when (label) {
            0 -> {
                println("Before delay 1")
                label = 1
                if (delay(1000, this) === COROUTINE_SUSPENDED) {
                    return COROUTINE_SUSPENDED
                }
            }
            1 -> {
                println("After delay 1")
                label = 2
                if (delay(1000, this) === COROUTINE_SUSPENDED) {
                    return COROUTINE_SUSPENDED
                }
            }
            2 -> {
                println("After delay 2")
                return Unit
            }
            else -> error("Invalid state")
        }
        return Unit
    }
}
```

**Key concepts:**
- `label`: current state (suspension point index).
- State machine class: stores state between suspensions.
- `resumeWith`/`invokeSuspend`: called when the coroutine is resumed to advance execution.

### Real Decompiled Example

This reflects real patterns seen in decompiled Kotlin suspend functions (simplified for readability):

```kotlin
suspend fun fetchUserData(userId: String): UserData {
    val user = api.getUser(userId)
    val posts = api.getPosts(userId)
    return UserData(user, posts)
}
```

**Decompiled (simplified, but structurally valid):**

```java
@Nullable
public static final Object fetchUserData(
    @NotNull String userId,
    @NotNull Continuation<? super UserData> $completion
) {
    FetchUserDataContinuation $cont;
    if ($completion instanceof FetchUserDataContinuation) {
        $cont = (FetchUserDataContinuation) $completion;
        if (($cont.label & Integer.MIN_VALUE) != 0) {
            $cont.label -= Integer.MIN_VALUE;
        }
    } else {
        $cont = new FetchUserDataContinuation($completion);
    }

    Object result = $cont.result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch ($cont.label) {
        case 0: {
            ResultKt.throwOnFailure(result);
            $cont.userId = userId;
            $cont.label = 1;

            Object user = api.getUser(userId, $cont);
            if (user == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            result = user;
        }
        case 1: {
            ResultKt.throwOnFailure(result);
            User user = (User) result;

            $cont.user = user;
            $cont.label = 2;

            Object posts = api.getPosts($cont.userId, $cont);
            if (posts == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;
            }
            result = posts;
        }
        case 2: {
            ResultKt.throwOnFailure(result);
            @SuppressWarnings("unchecked")
            List<Post> posts = (List<Post>) result;
            User user = $cont.user;

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

    FetchUserDataContinuation(Continuation<? super UserData> completion) {
        super(completion);
    }

    @Nullable
    public final Object invokeSuspend(@NotNull Object result) {
        this.result = result;
        this.label |= Integer.MIN_VALUE;
        return fetchUserData(this.userId, this);
    }
}
```

**Observations:**
1. Suspend modifier is gone at bytecode level.
2. Extra `Continuation` parameter is added.
3. Return type is `Object` so it can be either `UserData` or `COROUTINE_SUSPENDED`.
4. State machine implemented via `label` and a `switch`.
5. Local variables persisted across suspensions become fields.
6. Each suspension point corresponds to a `label` value.

### suspendCoroutine and suspendCancellableCoroutine

`suspendCoroutine` is a low-level API to create custom suspending operations.

```kotlin
public suspend inline fun <T> suspendCoroutine(
    crossinline block: (Continuation<T>) -> Unit
): T
```

Conceptually, it:
- creates and passes a continuation to `block`;
- returns `COROUTINE_SUSPENDED` to signal suspension;
- resumes later when that continuation is invoked.

**Usage example:**

```kotlin
suspend fun customDelay(timeMillis: Long) = suspendCoroutine<Unit> { cont ->
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

`suspendCancellableCoroutine` is a cancellation-aware variant:

```kotlin
suspend fun cancellableDelay(timeMillis: Long) = suspendCancellableCoroutine<Unit> { cont ->
    val timer = Timer()
    timer.schedule(object : TimerTask() {
        override fun run() {
            cont.resume(Unit)
        }
    }, timeMillis)

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
suspender.provideValue("Hello!")
```

### ContinuationInterceptor

`ContinuationInterceptor` is how dispatchers and similar mechanisms intercept continuations to change how/where they resume.

```kotlin
interface ContinuationInterceptor : CoroutineContext.Element {
    fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T>
}
```

**Example: Custom interceptor (simplified):**

```kotlin
class LoggingInterceptor : ContinuationInterceptor {
    override val key: CoroutineContext.Key<*> = ContinuationInterceptor

    override fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T> {
        return LoggingContinuation(continuation)
    }

    private class LoggingContinuation<T>(
        private val continuation: Continuation<T>
    ) : Continuation<T> {
        override val context: CoroutineContext
            get() = continuation.context

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
```

### How Dispatchers Intercept Continuations

Conceptual (not real implementation):

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
    override val context: CoroutineContext
        get() = continuation.context

    override fun resumeWith(result: Result<T>) {
        dispatcher.dispatch(context, Runnable {
            continuation.resumeWith(result)
        })
    }
}
```

**What happens conceptually:**
1. Suspend function returns `COROUTINE_SUSPENDED`.
2. Continuation is captured by the suspending operation.
3. When the operation completes, it calls `continuation.resumeWith()`.
4. `ContinuationInterceptor` (e.g., dispatcher) may wrap the continuation.
5. Dispatcher schedules `resumeWith` on the appropriate thread.
6. State machine continues from the stored `label`.

### Why Suspend Functions Can't Be Called from Regular Functions

```kotlin
fun regularFunction() {
    getUserName("123") // ERROR
}
```

Suspend functions are compiled to functions with an extra `Continuation` parameter and special control flow. A plain function has no such continuation to pass, so it cannot call a suspend function directly.

Conceptually:

```kotlin
suspend fun getUserName(userId: String): String
// becomes
fun getUserName(userId: String, continuation: Continuation<String>): Any?

fun regularFunction() {
    // There's no continuation argument to provide here
    // getUserName("123", ???)
}
```

Valid ways to call:

```kotlin
// 1. Make caller suspend
typealias UserId = String

suspend fun callerFunction() {
    getUserName("123")
}

// 2. Launch a coroutine
fun regularFunction() {
    GlobalScope.launch {
        getUserName("123")
    }
}

// 3. Use runBlocking
fun blockingEntryPoint() {
    runBlocking {
        getUserName("123")
    }
}
```

### Performance Implications

**Benefits of the state machine model:**

1. No callback hell: sequential-looking code compiled to non-blocking state machine.
2. `Stack`-less coroutines: no dedicated OS thread stack per coroutine; state is in continuation object.
3. Generally efficient: main overhead is allocation of a small continuation/state-machine object and a few field reads/writes.

**Costs:**

1. Object allocation for continuation/state-machine.
2. Indirect jumps via `label` (`when`/`switch`).
3. Locals that cross suspension points become fields.

Rough intuition (not guarantees, environment-dependent):

```kotlin
fun regularSum(a: Int, b: Int): Int = a + b

suspend fun suspendSum(a: Int, b: Int): Int = a + b // extra machinery even without real suspension

suspend fun suspendSumWithDelay(a: Int, b: Int): Int {
    delay(1)
    return a + b
}
```

- A trivial suspend function has small constant overhead vs regular.
- A suspend function with real suspension is dominated by scheduler/timer/thread hops, not just state machine logic.

**Inline suspend functions:**

```kotlin
inline suspend fun inlinedSum(a: Int, b: Int): Int = a + b
```

- Inlining moves the suspend body into the caller.
- If there are no suspension points, this can avoid extra state machine layers.
- If there are suspension points, a state machine is still needed at the appropriate level; "inline" does not magically remove all state machines.

### Advanced: Implementing Custom Suspending Operations

**Convert callback API to suspend (with cancellation hook):**

```kotlin
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

suspend fun fetchData(): String = suspendCancellableCoroutine { cont ->
    fetchDataAsync(object : ApiCallback {
        override fun onSuccess(data: String) {
            if (cont.isActive) cont.resume(data)
        }

        override fun onError(error: Throwable) {
            if (cont.isActive) cont.resumeWithException(error)
        }
    })

    cont.invokeOnCancellation {
        // Cancel underlying operation if possible
    }
}
```

### State Machine with Multiple Variables

```kotlin
suspend fun complexFunction(x: Int): Int {
    val a = computeA(x)
    val b = computeB(a)
    val c = computeC(a, b)
    return c
}
```

Conceptually, the compiler generates a continuation class where locals that survive suspensions are fields:

```kotlin
class ComplexFunctionContinuation(
    completion: Continuation<Int>
) : ContinuationImpl(completion) {
    var label = 0
    var result: Any? = null

    var x: Int = 0
    var a: Int = 0
    var b: Int = 0

    override fun invokeSuspend(result: Any?): Any? {
        // state machine using label, x, a, b
        // (conceptual only)
        return Unit
    }
}
```

Key insight: all values needed after a suspension point are stored in fields of the generated continuation/state-machine.

### Exception Handling in State Machines

Source:

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

Conceptual behavior (simplified, not exact code):

```kotlin
class WithExceptionContinuation(
    completion: Continuation<Unit>
) : ContinuationImpl(completion) {
    var label = 0
    var data: String? = null

    override fun invokeSuspend(result: Any?): Any? {
        return try {
            when (label) {
                0 -> {
                    ResultKt.throwOnFailure(result)
                    label = 1
                    val r = fetchData(this)
                    if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                    data = r as String
                }
                1 -> {
                    ResultKt.throwOnFailure(result)
                    label = 2
                    val r = processData(data!!, this)
                    if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
                }
            }
            Unit
        } catch (e: Exception) {
            handleError(e)
            Unit
        }
    }
}
```

Important points:
- Exceptions thrown before or after suspension points are wrapped into the state machine logic.
- `Result` and `throwOnFailure` are used to propagate failures between suspension steps.

### Visualizing State Machine Execution

```kotlin
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

1. **Continuation = "rest of computation"** — what happens after suspension.
2. **CPS transformation** — compiler adds a `Continuation` parameter and uses it to model control flow.
3. **State machines** — each suspension point corresponds to a `label`/state.
4. **No callback hell** — the compiler generates the callback/state logic for you.
5. **Efficient model** — no OS thread per coroutine; state is stored in a small object.
6. **ContinuationInterceptor/Dispatchers** — customize where/how continuations resume.
7. **suspendCoroutine/suspendCancellableCoroutine** — low-level primitives to build custom suspending operations.
8. **Locals to fields** — variables that span suspensions become state machine fields.
9. **Suspend functions require a continuation context** — hence cannot be called like regular functions.
10. **Performance** — small but real overhead for the state machine; enormous benefit from asynchronous, non-blocking execution.

---

## Дополнительные Вопросы (Follow-ups, RU)

1. Как компилятор Kotlin оптимизирует конечные автоматы для `suspend`-функций без точек приостановки?
2. В чем разница между `ContinuationImpl` и `BaseContinuationImpl` во внутренней реализации корутин?
3. Как inline `suspend`-функции влияют на генерацию конечных автоматов?
4. Что происходит со стек-трейсом исключений при прохождении через несколько точек приостановки?
5. Как компилятор обрабатывает хвостоподобные (tail-call-like) паттерны в `suspend`-функциях?
6. Как реализовать собственный `ContinuationInterceptor` для логирования или отладки?
7. Как конечный автомат обрабатывает циклы с точками приостановки внутри?

## Follow-ups

1. How does the Kotlin compiler optimize state machines for suspend functions without suspension points?
2. Can you explain the difference between `ContinuationImpl` and `BaseContinuationImpl`?
3. How do inline suspend functions affect state machine generation?
4. What happens to exception stack traces across multiple suspension points?
5. How does the compiler handle tail-call-like patterns in suspend functions?
6. Can you implement a custom `ContinuationInterceptor` for debugging?
7. How does the state machine handle loops with suspension points inside?

## Ссылки (RU)

- [Kotlin Coroutines Under the Hood](https://www.youtube.com/watch?v=YrrUCSi72E8)
- [Deep Dive into Coroutines on JVM](https://blog.jetbrains.com/kotlin/2021/04/coroutines-under-the-hood/)
- [KotlinConf 2017: Deep Dive into Coroutines](https://www.youtube.com/watch?v=_hfBv0a09Jc)
- [Continuation Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.coroutines/-continuation/)

## References

- [Kotlin Coroutines Under the Hood](https://www.youtube.com/watch?v=YrrUCSi72E8)
- [Deep Dive into Coroutines on JVM](https://blog.jetbrains.com/kotlin/2021/04/coroutines-under-the-hood/)
- [KotlinConf 2017: Deep Dive into Coroutines](https://www.youtube.com/watch?v=_hfBv0a09Jc)
- [Continuation Documentation](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.coroutines/-continuation/)

## Связанные Вопросы (RU)

- [[q-suspend-cancellable-coroutine--kotlin--hard|Построение suspend API через suspendCancellableCoroutine]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Отладка корутин в Kotlin]]
- [[q-common-coroutine-mistakes--kotlin--medium|Типичные ошибки при работе с корутинами]]

## Related Questions

- [[q-suspend-cancellable-coroutine--kotlin--hard|Converting callbacks with suspendCancellableCoroutine]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging Kotlin coroutines]]
- [[q-common-coroutine-mistakes--kotlin--medium|Common coroutine mistakes]]

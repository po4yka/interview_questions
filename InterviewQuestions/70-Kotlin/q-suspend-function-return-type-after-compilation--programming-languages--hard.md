---
id: lang-023
title: "Suspend Function Return Type After Compilation / Тип возвращаемого значения suspend функции после компиляции"
aliases: [Suspend Function Return Type After Compilation, Тип возвращаемого значения suspend функции после компиляции]
topic: kotlin
subtopics: [coroutines, kotlin-coroutines-basics]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-coroutines, q-how-to-create-suspend-function--programming-languages--medium]
created: 2024-10-15
updated: 2025-11-09
tags: [coroutines, difficulty/hard, kotlin]
---
# Вопрос (RU)
> Каким становится тип возврата suspend-функции после компиляции?

---

# Question (EN)
> What is the return type of a suspend function after compilation?

## Ответ (RU)

На уровне байткода JVM сгенерированная функция имеет возвращаемый тип `Object` (в обобщённом виде `Any?` в Kotlin-терминах), потому что она должна иметь возможность вернуть либо специальный маркер `COROUTINE_SUSPENDED`, сигнализирующий приостановку, либо результат вычисления. Это деталь реализации компилятора Kotlin (в частности Kotlin/JVM), а не часть стабильного языкового контракта исходного `suspend` API.

Под капотом компилятор Kotlin преобразует `suspend`-функции, используя вариацию Continuation-Passing Style (`CPS`). Сигнатура функции значительно изменяется во время компиляции: к параметрам добавляется `Continuation`, а тело превращается в машину состояний.

См. также: [[c-kotlin]], [[c-coroutines]], [[c-kotlin-coroutines-basics]]

### Исходный Код

```kotlin
suspend fun fetchUserName(userId: Int): String {
    delay(100)
    return "User_$userId"
}
```

### После Компиляции (концептуальная декомпилированная версия)

```kotlin
// Упрощённое представление того, что генерирует компилятор (Kotlin/JVM)
fun fetchUserName(userId: Int, continuation: `Continuation<String>`): Any? {
    // Реализация машины состояний (упрощённо)
    val sm = continuation as? FetchUserNameStateMachine
        ?: FetchUserNameStateMachine(continuation)

    return when (sm.label) {
        0 -> {
            sm.label = 1
            val r = delay(100, sm)
            if (r === COROUTINE_SUSPENDED) {
                COROUTINE_SUSPENDED
            } else {
                // немедленно продолжаем
                "User_$userId"
            }
        }
        1 -> {
            // возобновление после приостановки
            "User_$userId"
        }
        else -> throw IllegalStateException("Unexpected state")
    }
}

// Возвращаемый тип Any? (Object в байткоде JVM), потому что функция:
// 1. Может вернуть COROUTINE_SUSPENDED (специальный объект-маркер)
// 2. Может вернуть фактический результат `String` при нормальном завершении
// Исключения не возвращаются значением: они пробрасываются или доставляются через resumeWith.
```

### Понимание трансформации

```kotlin
// Оригинальная suspend-функция
suspend fun getData(): String {
    delay(1000)
    return "Data"
}

// Что компилятор генерирует (упрощённо, для Kotlin/JVM):
fun getData(continuation: `Continuation<String>`): Any? {
    // Может вернуть:
    // - COROUTINE_SUSPENDED: если функция приостанавливается
    // - "Data" (`String`): если функция завершается без асинхронной приостановки
    // При ошибке будет выброшено исключение или вызвано continuation.resumeWith(Result.failure(e)).

    // ... реализация машины состояний ...
}
```

### Маркер COROUTINE_SUSPENDED

```kotlin
// Внутренний объект, используемый реализацией корутин
internal object COROUTINE_SUSPENDED

// Скомпилированная функция возвращает его при приостановке:
fun example(cont: `Continuation<String>`): Any? {
    // ... некоторая логика ...

    return if (needsToSuspend) {
        COROUTINE_SUSPENDED  // Тип Any
    } else {
        "Result"            // Тип `String`
    }

    // Возвращаемый тип должен быть Any?, чтобы вместить оба варианта.
}
```

### Реальный пример: машина состояний

```kotlin
// Оригинальный код
suspend fun multiStepProcess(): String {
    delay(100)                  // Точка приостановки 1
    val step2 = fetchData()     // Точка приостановки 2
    return "Completed: $step2"
}

// Сильно упрощённая форма скомпилированной версии
fun multiStepProcess(completion: `Continuation<String>`): Any? {
    val sm = completion as? MultiStepStateMachine
        ?: MultiStepStateMachine(completion)

    return when (sm.label) {
        0 -> {
            sm.label = 1
            val r = delay(100, sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            // продолжаем к следующему состоянию
            multiStepProcess(sm)
        }
        1 -> {
            sm.label = 2
            val r = fetchData(sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.step2Result = r as `String`
            multiStepProcess(sm)
        }
        2 -> {
            "Completed: ${sm.step2Result}"
        }
        else -> throw IllegalStateException()
    }
}

// Машина состояний для сохранения локальных переменных между приостановками
class MultiStepStateMachine(
    val completion: `Continuation<String>`
) : Continuation<Any?> {
    var label = 0
    var step2Result: String? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        // В реальном коде логика сложнее; здесь — упрощённая иллюстрация повторного входа
        multiStepProcess(this)
    }
}
```

### Проверка с декомпилированным кодом

```kotlin
// Оригинальный Kotlin-код
suspend fun simpleFunction(): String {
    delay(1000)
    return "Done"
}

// Типичный (упрощённый) декомпилированный Java-код для Kotlin/JVM
public static final Object simpleFunction(Continuation $completion) {
    SimpleFunctionContinuation $cont;
    if ($completion instanceof SimpleFunctionContinuation) {
        $cont = (SimpleFunctionContinuation) $completion;
    } else {
        $cont = new SimpleFunctionContinuation($completion);
    }

    Object result = $cont.result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch ($cont.label) {
        case 0: {
            ResultKt.throwOnFailure(result);
            $cont.label = 1;
            if (DelayKt.delay(1000L, $cont) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;  // Возвращает Object-маркер
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

    return "Done";  // Возвращает результат как Object
    // Возвращаемый тип Object объединяет COROUTINE_SUSPENDED и фактический результат.
}
```

### Почему Any?, а не String?

```kotlin
// Так работать не может:
fun fetchData(cont: `Continuation<String>`): String {
    if (suspended) {
        return COROUTINE_SUSPENDED  // ОШИБКА: несоответствие типов
    }
    return "Data"
}

// Необходимо использовать Any?, чтобы представить и маркер, и результат:
fun fetchData(cont: `Continuation<String>`): Any? {
    return if (suspended) {
        COROUTINE_SUSPENDED       // OK: Any
    } else {
        "Data"                   // OK: `String` — подтип Any
    }
}

// При этом контракт suspend-функции для вызывающего кода остаётся:
// suspend fun fetchData(): String
// Вызывающий видит и проверяет именно тип `String`; Any?/Object — внутренняя деталь реализации.
```

### Интерфейс Continuation

```kotlin
// Интерфейс Continuation, который фигурирует в скомпилированной сигнатуре
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// То есть это:
// suspend fun getName(): String
// на уровне байткода (упрощённо) становится:
// public static final Object getName(Continuation<? super String> continuation)

// В концептуальной форме для Kotlin:
fun getName(continuation: `Continuation<String>`): Any?
```

### Пример: немедленный возврат vs приостановка

```kotlin
suspend fun smartFunction(needDelay: Boolean): String {
    if (needDelay) {
        delay(1000)
    }
    return "Result"
}

// Упрощённое скомпилированное представление:
fun smartFunction(needDelay: Boolean, cont: `Continuation<String>`): Any? {
    // При первом вызове:
    // - либо сразу возвращает "Result" (как Object/Any?) при отсутствии приостановки,
    // - либо возвращает COROUTINE_SUSPENDED, если была приостановка.
    // После возобновления продолжит выполнение и в итоге вернёт результат.

    // Тип Any? охватывает оба возможных значения на этом уровне.
}
```

### Тестирование возвращаемого типа

```kotlin
// Нельзя напрямую полагаться на внутренний тип возврата (Any?/Object) при обычном вызове suspend-функции;
// с точки зрения вызывающего кода контракт остаётся тем, что объявлено в сигнатуре.

fun main() = runBlocking {
    val result: `String` = fetchUserName(1)
    println(result)  // "User_1"

    // Внутри реализация может работать через функцию вида
    // fun fetchUserName(userId: Int, cont: `Continuation<String>`): Any?
}

// Внутренняя инфраструктура корутин делает примерно следующее:
val internalResult = fetchUserName(1, continuation)
when (internalResult) {
    COROUTINE_SUSPENDED -> {
        // Функция приостановлена, продолжение сохранено
    }
    else -> {
        // Функция завершилась синхронно
        @Suppress("UNCHECKED_CAST")
        continuation.resumeWith(Result.success(internalResult as `String`))
    }
}
```

### Ключевые выводы

1. Оригинальная сигнатура: `suspend fun foo(): String`.
2. На уровне реализации Kotlin/JVM компилятор превращает её в форму вида: `fun foo(continuation: `Continuation<String>`): Any?` (в байткоде: `Object`).
3. Такой тип возврата нужен, чтобы через одно значение отличать `COROUTINE_SUSPENDED` от фактического результата.
4. Общий супертип для `String` и `COROUTINE_SUSPENDED` — `Any?` (на уровне байткода — `Object`).
5. Тело `suspend`-функции трансформируется в машину состояний, которая управляет переходами между точками приостановки.
6. Это — деталь реализации компилятора; с точки зрения пользователя контракт типа `suspend fun foo(): String` остаётся неизменным.

### Дополнительные детали трансформации

```kotlin
// Модификатор suspend приводит к тому, что компилятор:
// 1. Добавляет параметр `Continuation` в сгенерированную форму.
// 2. Строит машину состояний.
// 3. Использует возвращаемый тип Any?/Object для различения COROUTINE_SUSPENDED и результата.
// 4. Отслеживает точки приостановки.

suspend fun original(x: Int): String
// Примерно преобразуется в (Kotlin/JVM):
fun original(x: Int, completion: `Continuation<String>`): Any?

// Обобщённый паттерн:
suspend fun <T> func(): T
// Становится на уровне реализации:
fun <T> func(completion: Continuation<T>): Any?
```

## Answer (EN)

At the JVM bytecode level, the compiled suspend function has the return type `Object` (conceptually `Any?` in Kotlin) because it must be able to return either the special `COROUTINE_SUSPENDED` marker indicating suspension or the computed result. This is an implementation detail of the Kotlin compiler (specifically on Kotlin/JVM), not a stable part of the public `suspend` language contract.

Under the hood, the Kotlin compiler transforms suspend functions using a variant of Continuation-Passing Style (`CPS`). The function signature is rewritten to accept a `Continuation`, and the body is converted into a state machine.

See also: [[c-kotlin]], [[c-coroutines]], [[c-kotlin-coroutines-basics]]

### Source Code

```kotlin
suspend fun fetchUserName(userId: Int): String {
    delay(100)
    return "User_$userId"
}
```

### After Compilation (Conceptual Decompiled Version)

```kotlin
// Simplified representation of what the Kotlin/JVM compiler generates
fun fetchUserName(userId: Int, continuation: `Continuation<String>`): Any? {
    // State machine implementation (simplified)
    val sm = continuation as? FetchUserNameStateMachine
        ?: FetchUserNameStateMachine(continuation)

    return when (sm.label) {
        0 -> {
            sm.label = 1
            val r = delay(100, sm)
            if (r === COROUTINE_SUSPENDED) {
                COROUTINE_SUSPENDED
            } else {
                "User_$userId"
            }
        }
        1 -> {
            // Resumed after suspension
            "User_$userId"
        }
        else -> throw IllegalStateException("Unexpected state")
    }
}

// Return type is Any? (Object in JVM bytecode) because it may hold:
// 1. COROUTINE_SUSPENDED (special marker object)
// 2. The actual `String` result on normal completion
// Exceptions are not returned as values; they are thrown or delivered via resumeWith.
```

### Understanding the Transformation

```kotlin
// Original suspend function
suspend fun getData(): String {
    delay(1000)
    return "Data"
}

// What the compiler generates (simplified, Kotlin/JVM):
fun getData(continuation: `Continuation<String>`): Any? {
    // It can return:
    // - COROUTINE_SUSPENDED: if the function suspends
    // - "Data" (`String`): if it completes synchronously without suspension
    // On failure, an exception is thrown or continuation.resumeWith(Result.failure(e)) is invoked.

    // ... state machine implementation ...
}
```

### COROUTINE_SUSPENDED Marker

```kotlin
// Internal object used by coroutine implementation
internal object COROUTINE_SUSPENDED

// The compiled function returns this when it suspends:
fun example(cont: `Continuation<String>`): Any? {
    // ... some logic ...

    return if (needsToSuspend) {
        COROUTINE_SUSPENDED  // Type Any
    } else {
        "Result"            // Type `String`
    }

    // Return type must be Any? to accommodate both.
}
```

### Real Example: State Machine

```kotlin
// Original code
suspend fun multiStepProcess(): String {
    delay(100)                  // Suspension point 1
    val step2 = fetchData()     // Suspension point 2
    return "Completed: $step2"
}

// Highly simplified compiled form
fun multiStepProcess(completion: `Continuation<String>`): Any? {
    val sm = completion as? MultiStepStateMachine
        ?: MultiStepStateMachine(completion)

    return when (sm.label) {
        0 -> {
            sm.label = 1
            val r = delay(100, sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            // fall through by reinvoking with updated state
            multiStepProcess(sm)
        }
        1 -> {
            sm.label = 2
            val r = fetchData(sm)
            if (r === COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.step2Result = r as `String`
            multiStepProcess(sm)
        }
        2 -> {
            "Completed: ${sm.step2Result}"
        }
        else -> throw IllegalStateException()
    }
}

// State machine to preserve locals across suspensions
class MultiStepStateMachine(
    val completion: `Continuation<String>`
) : Continuation<Any?> {
    var label = 0
    var step2Result: String? = null

    override val context: CoroutineContext
        get() = completion.context

    override fun resumeWith(result: Result<Any?>) {
        // In real generated code, resumeWith drives the state machine; here it's simplified
        multiStepProcess(this)
    }
}
```

### Verification with Decompiled Code

```kotlin
// Original Kotlin code
suspend fun simpleFunction(): String {
    delay(1000)
    return "Done"
}

// Typical (simplified) decompiled Java for Kotlin/JVM
public static final Object simpleFunction(Continuation $completion) {
    SimpleFunctionContinuation $cont;
    if ($completion instanceof SimpleFunctionContinuation) {
        $cont = (SimpleFunctionContinuation) $completion;
    } else {
        $cont = new SimpleFunctionContinuation($completion);
    }

    Object result = $cont.result;
    Object COROUTINE_SUSPENDED = IntrinsicsKt.getCOROUTINE_SUSPENDED();

    switch ($cont.label) {
        case 0: {
            ResultKt.throwOnFailure(result);
            $cont.label = 1;
            if (DelayKt.delay(1000L, $cont) == COROUTINE_SUSPENDED) {
                return COROUTINE_SUSPENDED;  // Returns marker as Object
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

    return "Done";  // Returns result as Object
    // Return type Object supports both COROUTINE_SUSPENDED and the actual result.
}
```

### Why Any? and not String?

```kotlin
// This would not work with return type String:
fun fetchData(cont: `Continuation<String>`): String {
    if (suspended) {
        return COROUTINE_SUSPENDED  // ERROR: type mismatch
    }
    return "Data"
}

// Must use Any? so it can hold both marker and result:
fun fetchData(cont: `Continuation<String>`): Any? {
    return if (suspended) {
        COROUTINE_SUSPENDED       // OK (Any)
    } else {
        "Data"                   // OK (`String` is subtype of Any)
    }
}

// For callers, the suspend function's declared type remains:
// suspend fun fetchData(): String
// The Any?/Object return type is an internal implementation detail.
```

### Continuation Interface

```kotlin
// Continuation interface as used in the compiled signature
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// So this:
// suspend fun getName(): String
// is compiled (simplified, JVM) to:
// public static final Object getName(Continuation<? super String> continuation)

// Conceptual Kotlin form:
fun getName(continuation: `Continuation<String>`): Any?
```

### Example: Immediate Return vs Suspension

```kotlin
suspend fun smartFunction(needDelay: Boolean): String {
    if (needDelay) {
        delay(1000)
    }
    return "Result"
}

// Simplified compiled behavior:
fun smartFunction(needDelay: Boolean, cont: `Continuation<String>`): Any? {
    // On first call it may either:
    // - return "Result" immediately (as Any?) if no suspension occurs,
    // - or return COROUTINE_SUSPENDED if it suspends.
    // After resumption, it continues and eventually returns the result.

    // Any? covers both possibilities at this internal level.
}
```

### Testing the Return Type

```kotlin
// You cannot and should not rely on the internal Any?/Object return type
// when calling a suspend function normally; you see the declared suspend signature.

fun main() = runBlocking {
    val result: `String` = fetchUserName(1)
    println(result)  // "User_1"

    // Internally, an implementation-specific form like
    // fun fetchUserName(userId: Int, cont: `Continuation<String>`): Any?
    // is used by the coroutine machinery.
}

// Internally, coroutine infrastructure does something like:
val internalResult = fetchUserName(1, continuation)
when (internalResult) {
    COROUTINE_SUSPENDED -> {
        // Function suspended; continuation saved
    }
    else -> {
        // Function completed synchronously
        @Suppress("UNCHECKED_CAST")
        continuation.resumeWith(Result.success(internalResult as `String`))
    }
}
```

### Key Takeaways

1. Original signature: `suspend fun foo(): String`.
2. On Kotlin/JVM, the compiler rewrites it into an implementation form like: `fun foo(continuation: `Continuation<String>`): Any?` (bytecode return type `Object`).
3. This return type is needed so the implementation can use a single channel to indicate either `COROUTINE_SUSPENDED` or the actual result.
4. `String` and `COROUTINE_SUSPENDED` share `Any?` (`Object`) as a common supertype.
5. The suspend body is compiled into a state machine that manages suspension and resumption.
6. This is an implementation detail; at the source level the contract remains `suspend fun foo(): String`.

### Additional Transformation Details

```kotlin
// The suspend modifier causes the compiler to:
// 1. Add a `Continuation` parameter to the compiled form.
// 2. Generate a state machine.
// 3. Use Any?/Object as the compiled return type to distinguish COROUTINE_SUSPENDED from the result.
// 4. Track suspension points.

suspend fun original(x: Int): String
// Transformed (Kotlin/JVM, simplified) to:
fun original(x: Int, completion: `Continuation<String>`): Any?

// Generic pattern:
suspend fun <T> func(): T
// Becomes in the compiled form:
fun <T> func(completion: Continuation<T>): Any?
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-how-to-create-suspend-function--programming-languages--medium]]
- [[q-java-all-classes-inherit-from-object--programming-languages--easy]]
- [[q-what-is-garbage-in-gc--programming-languages--easy]]

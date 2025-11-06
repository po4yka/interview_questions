---
id: lang-023
title: "Suspend Function Return Type After Compilation / Тип возвращаемого значения suspend функции после компиляции"
aliases: [Suspend Function Return Type After Compilation, Тип возвращаемого значения suspend функции после компиляции]
topic: programming-languages
subtopics: [compilation, coroutines, type-system]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-how-to-create-suspend-function--programming-languages--medium, q-java-all-classes-inherit-from-object--programming-languages--easy, q-what-is-garbage-in-gc--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [compilation, coroutines, difficulty/hard, kotlin, programming-languages]
---
# Suspend Function Return Type After Compilation

# Вопрос (RU)
> Каким становится тип возврата suspend-функции после компиляции?

---

# Question (EN)
> What is the return type of a suspend function after compilation?

## Ответ (RU)

Возвращаемый тип становится **Any?** (или `Object` в JVM байткоде), потому что функция может вернуть либо значение String, либо специальный маркер **COROUTINE_SUSPENDED**, указывающий что корутина приостановлена.

Под капотом компилятор Kotlin преобразует suspend функции используя **трансформацию Continuation-Passing Style (CPS)**. Сигнатура функции значительно изменяется во время компиляции.

### Исходный Код

```kotlin
suspend fun fetchUserName(userId: Int): String {
    delay(100)
    return "User_$userId"
}
```

### После Компиляции (концептуальная Декомпилированная версия)

```kotlin
// Упрощенное представление того, что генерирует компилятор
fun fetchUserName(userId: Int, continuation: Continuation<String>): Any? {
    // Реализация машины состояний
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

// Возвращаемый тип Any?, потому что может вернуть:
// 1. COROUTINE_SUSPENDED (специальный объект-маркер)
// 2. Фактический результат String
// 3. null (в некоторых случаях)
```

### Понимание Трансформации

```kotlin
// Оригинальная suspend функция
suspend fun getData(): String {
    delay(1000)
    return "Data"
}

// Что фактически генерирует компилятор (упрощенно):
fun getData(continuation: Continuation<String>): Any? {
    // Может вернуть:
    // - COROUTINE_SUSPENDED: если функция приостанавливается
    // - String: если функция завершается немедленно
    // - Exception: если произошла ошибка

    // ... реализация машины состояний ...
}
```

### Маркер COROUTINE_SUSPENDED

```kotlin
// Это внутренний объект Kotlin coroutine
internal object COROUTINE_SUSPENDED

// Скомпилированная функция возвращает это при приостановке:
fun example(cont: Continuation<String>): Any? {
    // ... некоторая логика ...

    if (needsToSuspend) {
        return COROUTINE_SUSPENDED  // Тип Any
    } else {
        return "Result"  // Тип String
    }

    // Возвращаемый тип должен быть Any?, чтобы вместить оба варианта
}
```

### Реальный Пример: Машина Состояний

```kotlin
// Оригинальный код
suspend fun multiStepProcess(): String {
    val step1 = delay(100)           // Точка приостановки 1
    val step2 = fetchData()          // Точка приостановки 2
    return "Completed: $step2"
}

// Скомпилированная версия (сильно упрощенная)
fun multiStepProcess(completion: Continuation<String>): Any? {
    val sm = completion as? MultiStepStateMachine
        ?: MultiStepStateMachine(completion)

    when (sm.label) {
        0 -> {
            sm.label = 1
            val result = delay(100, sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            // Переход к label 1
        }
        1 -> {
            sm.label = 2
            val result = fetchData(sm)
            if (result == COROUTINE_SUSPENDED) return COROUTINE_SUSPENDED
            sm.step2Result = result as String
            // Переход к label 2
        }
        2 -> {
            return "Completed: ${sm.step2Result}"  // Возвращает String
        }
    }

    throw IllegalStateException()
}

// Машина состояний для сохранения локальных переменных между приостановками
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

### Проверка С Декомпилированным Кодом

```kotlin
// Оригинальный Kotlin код
suspend fun simpleFunction(): String {
    delay(1000)
    return "Done"
}

// Фактический декомпилированный Java байткод (из IntelliJ)
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
                return COROUTINE_SUSPENDED;  // Возвращает Object (COROUTINE_SUSPENDED)
            }
            break;
        case 1:
            ResultKt.throwOnFailure(result);
            break;
        default:
            throw new IllegalStateException("call to 'resume' before 'invoke'");
    }

    return "Done";  // Возвращает String

    // Возвращаемый тип Object для поддержки COROUTINE_SUSPENDED и String
}
```

### Почему Any?, А Не String?

```kotlin
// Это не сработает с возвращаемым типом String:
fun fetchData(cont: Continuation<String>): String {
    if (suspended) {
        return COROUTINE_SUSPENDED  // - ОШИБКА: Несоответствие типов
    }
    return "Data"  // - OK
}

// Необходимо использовать Any? для обоих вариантов:
fun fetchData(cont: Continuation<String>): Any? {
    if (suspended) {
        return COROUTINE_SUSPENDED  // - OK (Any)
    }
    return "Data"  // - OK (String - подтип Any)
}
```

### Интерфейс Continuation

```kotlin
// Интерфейс Continuation, который добавляется как параметр
public interface Continuation<in T> {
    public val context: CoroutineContext
    public fun resumeWith(result: Result<T>)
}

// Итак, это:
suspend fun getName(): String

// Становится этим:
fun getName(continuation: Continuation<String>): Any?
```

### Пример: Немедленный Возврат Vs Приостановка

```kotlin
suspend fun smartFunction(needDelay: Boolean): String {
    if (needDelay) {
        delay(1000)  // Может вернуть COROUTINE_SUSPENDED
    }
    return "Result"  // Всегда возвращает String в конце
}

// Скомпилированное поведение:
fun smartFunction(needDelay: Boolean, cont: Continuation<String>): Any? {
    if (needDelay) {
        // Первый вызов: возвращает COROUTINE_SUSPENDED
        // Возобновляется позже после delay
    }
    // В конце возвращает: "Result" (String)

    // Возвращаемый тип Any? охватывает оба случая
}
```

### Тестирование Возвращаемого Типа

```kotlin
// Вы не можете получить прямой доступ к скомпилированному возвращаемому типу,
// но можете наблюдать поведение:

fun main() = runBlocking {
    // Эта suspend функция возвращает String вызывающему коду
    val result: String = fetchUserName(1)
    println(result)  // "User_1"

    // Но внутри скомпилированная версия возвращает Any?
    // и machinery корутин обрабатывает это
}

// Инфраструктура корутин проверяет:
val internalResult = fetchUserName(1, continuation)
when (internalResult) {
    COROUTINE_SUSPENDED -> {
        // Функция приостановлена, возобновится позже
    }
    else -> {
        // Функция завершилась немедленно
        continuation.resumeWith(Result.success(internalResult as String))
    }
}
```

### Ключевые Выводы

1. **Оригинальная сигнатура**: `suspend fun foo(): String`
2. **Скомпилированная сигнатура**: `fun foo(continuation: Continuation<String>): Any?`
3. **Причина возвращаемого типа**: Может вернуть либо `COROUTINE_SUSPENDED`, либо фактический результат `String`
4. **Иерархия типов**: `String` и `COROUTINE_SUSPENDED` имеют `Any?` как общий супертип
5. **Машина состояний**: Функция преобразуется в машину состояний, которая сохраняет состояние между точками приостановки

### Дополнительные Детали Трансформации

```kotlin
// Модификатор suspend добавляет:
// 1. Параметр Continuation
// 2. Реализацию машины состояний
// 3. Изменение возвращаемого типа на Any?
// 4. Отслеживание точек приостановки

suspend fun original(x: Int): String
//  Преобразуется в
fun original(x: Int, $completion: Continuation<String>): Any?

// Общий паттерн:
suspend fun <T> func(): T
//  Становится
fun <T> func($completion: Continuation<T>): Any?
```

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
        return COROUTINE_SUSPENDED  // - ERROR: Type mismatch
    }
    return "Data"  // - OK
}

// Must use Any? to allow both:
fun fetchData(cont: Continuation<String>): Any? {
    if (suspended) {
        return COROUTINE_SUSPENDED  // - OK (Any)
    }
    return "Data"  // - OK (String is subtype of Any)
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

### Example: Immediate Return Vs Suspension

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
//  Transformed to
fun original(x: Int, $completion: Continuation<String>): Any?

// Generic pattern:
suspend fun <T> func(): T
//  Becomes
fun <T> func($completion: Continuation<T>): Any?
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
